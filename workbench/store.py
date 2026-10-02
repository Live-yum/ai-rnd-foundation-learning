"""Short SQLAlchemy transactions; no model/tool calls inside a database transaction."""

import json
import secrets
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from alembic import command
from alembic.config import Config
from filelock import FileLock
from sqlalchemy import (
    JSON,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    select,
    text,
    update,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from workbench.domain import ResumeInput, RunInput, digest
from workbench.errors import PausedLimit
from workbench.settings import ROOT, Settings


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def uid():
    return str(uuid.uuid4())


class Conflict(ValueError):
    pass


class Missing(LookupError):
    pass


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    template: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(50), default="QUEUED")
    pending: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_calls: Mapped[int] = mapped_column(default=0)
    options: Mapped[dict] = mapped_column(JSON, default=dict)
    auto_mode: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    updated_at: Mapped[str] = mapped_column(String(40), default=now, onupdate=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED", index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Request(Base):
    __tablename__ = "requests"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSON)


class Revision(Base):
    __tablename__ = "revisions"
    gate_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    digest: Mapped[str] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Approval(Base):
    __tablename__ = "approvals"
    gate_id: Mapped[str] = mapped_column(ForeignKey("revisions.gate_id"), primary_key=True)
    decision: Mapped[bool] = mapped_column()
    actor: Mapped[str] = mapped_column(String(40), default="local-operator")
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Step(Base):
    __tablename__ = "steps"
    __table_args__ = (UniqueConstraint("run_id", "name", name="uq_steps_run_name"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    kind: Mapped[str] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.prepare()
        args = (
            {"check_same_thread": False, "autocommit": False}
            if settings.db_url.startswith("sqlite:")
            else {}
        )
        self.engine = create_engine(settings.db_url, connect_args=args, pool_pre_ping=True)
        if self.engine.dialect.name == "sqlite":

            @event.listens_for(self.engine, "connect")
            def configure(connection, _):
                old = connection.autocommit
                connection.autocommit = True
                try:
                    with _cursor(connection) as cursor:
                        cursor.execute("PRAGMA foreign_keys=ON")
                        cursor.execute("PRAGMA busy_timeout=10000")
                        cursor.execute("PRAGMA journal_mode=WAL")
                finally:
                    connection.autocommit = old

        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def migrate(self):
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "migrations"))
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")

    def token(self):
        path = self.settings.data_dir / "access-token"
        if not path.exists():
            try:
                with path.open("x", encoding="utf-8") as f:
                    f.write(secrets.token_urlsafe(32))
                path.chmod(0o600)
            except FileExistsError:
                pass
        return path.read_text(encoding="utf-8").strip()

    @contextmanager
    def tx(self):
        with self.sessions.begin() as session:
            yield session

    def request(self, key, payload, operation):
        # Serialise local API mutations. PostgreSQL additionally uses a short DB lock.
        with FileLock(str(self.settings.data_dir / "requests.lock"), timeout=30):
            return self._request(key, payload, operation)

    def _request(self, key, payload, operation):
        if not key or len(key) > 100:
            raise Conflict("Idempotency-Key 必填且长度不超过 100")
        fingerprint = digest(payload)
        with self.tx() as session:
            if self.engine.dialect.name == "postgresql":
                session.execute(text("SELECT pg_advisory_xact_lock(728194601)"))
            previous = session.get(Request, key)
            if previous:
                if previous.fingerprint != fingerprint:
                    raise Conflict("相同 Idempotency-Key 不能用于不同请求")
                return previous.response
            response = operation(session)
            session.add(Request(key=key, fingerprint=fingerprint, response=response))
            return response

    def create_project(self, title, key):
        def operation(session):
            project = Project(title=title)
            session.add(project)
            session.flush()
            return {"id": project.id, "title": project.title}

        return self.request(key, {"operation": "create-project", "title": title}, operation)

    def create_run(self, project_id, data, key):
        data = RunInput.model_validate(data).model_dump()

        def operation(session):
            if not session.get(Project, project_id):
                raise Missing("项目不存在")
            run = Run(
                project_id=project_id,
                template=data["template"],
                options=data["selection"],
                auto_mode=data["intelligent"],
            )
            session.add(run)
            session.flush()
            session.add(Message(run_id=run.id, role="user", content=data["requirement"]))
            session.add(Job(run_id=run.id, payload={"action": "start"}))
            if run.auto_mode:
                session.add(
                    Event(
                        run_id=run.id,
                        kind="delegation",
                        data={
                            "enabled": True,
                            "actor": "local-operator",
                            "scope": "choose missing details and approve subsequent design/delivery; never bypass tests",
                        },
                    )
                )
            return {"run_id": run.id, "status": "QUEUED"}

        return self.request(
            key, {"operation": "create-run", "project": project_id, **data}, operation
        )

    def submit(self, run_id, data, key):
        data = ResumeInput.model_validate(data).model_dump()

        def operation(session):
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            pending = run.pending
            if not pending or pending["gate_id"] != data["gate_id"]:
                raise Conflict("审批/回答版本已变化，请重新读取运行状态")
            if data["action"] not in pending["actions"] and data["action"] != "recommend":
                raise Conflict("当前阶段不接受这个动作")
            if data["action"] == "approve" and not pending.get("can_approve", False):
                raise Conflict("存在未支持项或先决条件尚未满足，不能批准")
            if data["action"] == "recommend":
                run.auto_mode = True
                session.add(
                    Event(
                        run_id=run_id,
                        kind="delegation",
                        data={
                            "enabled": True,
                            "actor": "local-operator",
                            "gate_id": pending["gate_id"],
                        },
                    )
                )
            if data["action"] in {"answer", "revise"}:
                session.add(Message(run_id=run_id, role="user", content=data["text"]))
            if data["action"] in {"approve", "reject"}:
                session.add(Approval(gate_id=pending["gate_id"], decision=data["approved"]))
            job = Job(run_id=run_id, payload=dict(data))
            session.add(job)
            session.flush()
            run.pending = None
            run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "job_id": job.id, "status": "QUEUED"}

        return self.request(key, {"operation": "submit", "run_id": run_id, **data}, operation)

    def retry(self, run_id, key):
        def operation(session):
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            if run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}:
                raise Conflict("只有 FAILED、BLOCKED 或 PAUSED_LIMIT 状态可以重试")
            session.add(Job(run_id=run_id, payload={"action": "retry"}))
            # The graph owns the saved interrupt. Hide the stale Store copy
            # while queued so a second request cannot consume it concurrently.
            run.pending = None
            run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "status": run.status}

        return self.request(key, {"operation": "retry", "run_id": run_id}, operation)

    def get_run(self, run_id):
        with self.tx() as session:
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            return {c.name: getattr(run, c.name) for c in Run.__table__.columns}

    def messages(self, run_id):
        with self.tx() as session:
            rows = session.scalars(
                select(Message).where(Message.run_id == run_id).order_by(Message.id)
            )
            return [{"role": row.role, "content": row.content} for row in rows]

    def step(self, run_id, name, fn):
        with self.tx() as session:
            old = session.scalar(select(Step).where(Step.run_id == run_id, Step.name == name))
            if old:
                return old.data
        result = fn()
        result = json.loads(json.dumps(result, ensure_ascii=False))
        with self.tx() as session:
            session.add(Step(run_id=run_id, name=name, data=result))
            session.add(Event(run_id=run_id, kind="step", data={"name": name}))
        return result

    def reserve_model_call(self, run_id):
        with self.tx() as session:
            statement = update(Run).where(Run.id == run_id)
            if self.settings.max_model_calls:
                statement = statement.where(Run.model_calls < self.settings.max_model_calls)
            changed = session.execute(statement.values(model_calls=Run.model_calls + 1)).rowcount
            if changed != 1:
                raise PausedLimit(
                    "已到达你配置的模型预算；回答已保存。调整 MAX_MODEL_CALLS 后重试同一运行，无需重建。"
                )

    def set_automation(self, run_id, enabled, key):
        def operation(session):
            run = session.get(Run, run_id)
            if run is None:
                raise Missing("运行不存在")
            if run.status in {"READY", "SOURCE_READY", "REJECTED"}:
                raise Conflict("已结束运行不能更改自动决策授权")
            run.auto_mode = enabled
            session.add(
                Event(
                    run_id=run_id,
                    kind="delegation",
                    data={
                        "enabled": enabled,
                        "actor": "local-operator",
                        "scope": "remaining decisions; cannot bypass tests",
                    },
                )
            )
            if enabled and run.pending:
                session.add(
                    Job(
                        run_id=run_id,
                        payload={
                            "action": "recommend",
                            "gate_id": run.pending["gate_id"],
                            "approved": True,
                        },
                    )
                )
                run.pending = None
                run.status, run.error = "QUEUED", None
            elif not enabled and run.status == "BLOCKED" and run.pending:
                run.status = "WAITING_" + run.pending["stage"].upper()
                run.error = None
            elif enabled and run.status in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}:
                session.add(Job(run_id=run_id, payload={"action": "retry"}))
                run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "auto_mode": enabled, "status": run.status}

        return self.request(
            key, {"operation": "automation", "run_id": run_id, "enabled": enabled}, operation
        )

    def auto_approve(self, run_id, gate):
        with self.tx() as session:
            run = session.get(Run, run_id)
            if not run or not run.auto_mode or not gate["can_approve"]:
                raise Conflict("没有有效智能推荐授权，或存在不能自动通过的阻塞项")
            current = session.get(Approval, gate["gate_id"])
            if current and not current.decision:
                raise Conflict("已拒绝的版本不能被智能推荐重新批准")
            if not current:
                session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="delegated-ai"))
                session.add(
                    Event(
                        run_id=run_id,
                        kind="auto-decision",
                        data={
                            "gate_id": gate["gate_id"],
                            "stage": gate["stage"],
                            "digest": gate["digest"],
                        },
                    )
                )

    def record_event(self, run_id, kind, data):
        with self.tx() as session:
            session.add(Event(run_id=run_id, kind=kind, data=data))

    def model_records(self, run_id):
        self.get_run(run_id)
        with self.tx() as session:
            rows = session.scalars(
                select(Step)
                .where(Step.run_id == run_id, Step.name.like("model:%"))
                .order_by(Step.id)
            )
            records = [
                {
                    "step": r.name,
                    "stage": r.data.get("stage", "legacy"),
                    "model": r.data.get("model"),
                    "endpoint": r.data.get("endpoint"),
                    "usage": r.data.get("usage"),
                    "provider": r.data.get("provider", "legacy"),
                    "output_mode": r.data.get("output_mode", "legacy"),
                    "format_reason": r.data.get("format_reason", "legacy"),
                    "contract_version": r.data.get("contract_version", 0),
                    "structured_output": r.data.get("structured_output", "legacy"),
                    "finish_reason": r.data.get("finish_reason", "unknown"),
                    "status": "validated" if r.data.get("contract_version") else "legacy",
                    "created_at": r.created_at,
                }
                for r in rows
            ]
            failures = session.scalars(
                select(Event)
                .where(Event.run_id == run_id, Event.kind == "model_failure")
                .order_by(Event.id)
            )
            records.extend({**r.data, "created_at": r.created_at} for r in failures)
            return sorted(records, key=lambda item: item["created_at"])

    def gate(self, run_id, stage, version, data, actions, can_approve=True):
        content_digest = digest(data)
        gate_id = digest([run_id, stage, version, content_digest])
        with self.tx() as session:
            if not session.get(Revision, gate_id):
                session.add(
                    Revision(
                        gate_id=gate_id,
                        run_id=run_id,
                        stage=stage,
                        digest=content_digest,
                        data=data,
                    )
                )
        return {
            "gate_id": gate_id,
            "stage": stage,
            "version": version,
            "digest": content_digest,
            "data": data,
            "actions": actions,
            "can_approve": can_approve,
        }

    def check_decision(self, run_id, gate, value):
        if not isinstance(value, dict):
            raise Conflict("工作流恢复需要结构化输入")
        if value.get("gate_id") != gate["gate_id"] or (
            value.get("action") not in gate["actions"] and value.get("action") != "recommend"
        ):
            raise Conflict("工作流恢复凭据与等待点不一致")
        if value["action"] == "recommend":
            if value.get("approved") is not True or not self.get_run(run_id)["auto_mode"]:
                raise Conflict("没有有效的智能推荐授权")
        if value["action"] == "approve" and not gate.get("can_approve", False):
            raise Conflict("不能批准被阻塞的版本")
        if value["action"] in {"approve", "reject"}:
            if value.get("approved") is not (value["action"] == "approve"):
                raise Conflict("审批必须使用匹配的布尔值")
            with self.tx() as session:
                revision = session.get(Revision, gate["gate_id"])
                approval = session.get(Approval, gate["gate_id"])
                if not revision or revision.run_id != run_id or not approval:
                    raise Conflict("缺少人工审批记录")
                if approval.decision is not (value["action"] == "approve"):
                    raise Conflict("审批决定不一致")

    def claim(self):
        with self.tx() as session:
            job = session.scalar(
                select(Job).where(Job.status == "QUEUED").order_by(Job.created_at).limit(1)
            )
            if job is None:
                return None
            changed = session.execute(
                update(Job).where(Job.id == job.id, Job.status == "QUEUED").values(status="RUNNING")
            ).rowcount
            if changed != 1:
                return None
            run = session.get(Run, job.run_id)
            run.status = "RUNNING"
            return {"id": job.id, "run_id": job.run_id, "payload": job.payload}

    def recover(self):
        with self.tx() as session:
            session.execute(update(Job).where(Job.status == "RUNNING").values(status="QUEUED"))

    def finish(self, job, status, pending=None, result=None, error=None):
        with self.tx() as session:
            session.get(Job, job["id"]).status = "FAILED" if error else "DONE"
            run = session.get(Run, job["run_id"])
            run.status, run.pending, run.error = status, pending, error
            if result is not None:
                run.result = result
            session.add(
                Event(run_id=run.id, kind="status", data={"status": status, "error": error})
            )

    def events(self, run_id, after=0):
        self.get_run(run_id)
        with self.tx() as session:
            rows = session.scalars(
                select(Event)
                .where(Event.run_id == run_id, Event.id > after)
                .order_by(Event.id)
                .limit(200)
            )
            return [
                {"id": r.id, "kind": r.kind, "data": r.data, "created_at": r.created_at}
                for r in rows
            ]

    def list_projects(self):
        with self.tx() as session:
            return [
                {"id": p.id, "title": p.title, "created_at": p.created_at}
                for p in session.scalars(
                    select(Project).order_by(Project.created_at.desc()).limit(100)
                )
            ]

    def list_runs(self, project_id=None):
        with self.tx() as session:
            statement = select(Run).order_by(Run.created_at.desc()).limit(100)
            if project_id is not None:
                if not session.get(Project, project_id):
                    raise Missing("项目不存在")
                statement = statement.where(Run.project_id == project_id)
            return [
                {
                    "id": r.id,
                    "project_id": r.project_id,
                    "status": r.status,
                    "template": r.template,
                    "options": r.options,
                    "auto_mode": r.auto_mode,
                    "updated_at": r.updated_at,
                }
                for r in session.scalars(statement)
            ]

    def latest_revision(self, run_id, stage):
        with self.tx() as session:
            row = session.scalar(
                select(Revision)
                .where(Revision.run_id == run_id, Revision.stage == stage)
                .order_by(Revision.created_at.desc())
                .limit(1)
            )
            return row.data if row else None


@contextmanager
def _cursor(connection):
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
