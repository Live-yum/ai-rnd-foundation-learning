# workbench/store.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：持久化项目、会话、任务、版本、审批和证据。** SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run建立运行和首条消息；任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。

**对应关系：** api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `now`（L31–L32）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`datetime.now(timezone.utc).isoformat`、`datetime.now`。 返回路径：L32的`datetime.now(timezone.utc).isoformat(timespec="microseconds")`。
- `uid`（L35–L36）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`str`、`uuid.uuid4`。 返回路径：L36的`str(uuid.uuid4())`。
- `Conflict`（L39–L40）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Missing`（L43–L44）：继承`LookupError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Base`（L47–L48）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Project`（L51–L55）：继承`Base`。声明的数据项为`id`、`title`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Run`（L58–L71）：继承`Base`。声明的数据项为`id`、`project_id`、`template`、`status`、`pending`、`result`、`error`、`model_calls`、`options`、`auto_mode`、`created_at`、`updated_at`；类型约束/数据库列参数以完整定义为准。
- `Message`（L74–L80）：继承`Base`。声明的数据项为`id`、`run_id`、`role`、`content`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Job`（L83–L89）：继承`Base`。声明的数据项为`id`、`run_id`、`payload`、`status`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Request`（L92–L96）：继承`Base`。声明的数据项为`key`、`fingerprint`、`response`；类型约束/数据库列参数以完整定义为准。
- `Revision`（L99–L106）：继承`Base`。声明的数据项为`gate_id`、`run_id`、`stage`、`digest`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Approval`（L109–L114）：继承`Base`。声明的数据项为`gate_id`、`decision`、`actor`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Step`（L117–L124）：继承`Base`。声明的数据项为`id`、`run_id`、`name`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Event`（L127–L133）：继承`Base`。声明的数据项为`id`、`run_id`、`kind`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Store`（L136–L575）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Store.__init__`（L137–L160）：接收`settings`。 控制顺序：L146按`self.engine.dialect.name == "sqlite"`分支。 调用`settings.prepare`、`settings.db_url.startswith`、`create_engine`、`sessionmaker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.__init__.configure`（L149–L158）：接收`connection`、`_`。 调用`_cursor`、`cursor.execute`、`event.listens_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.migrate`（L162–L167）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Config`、`str`、`config.set_main_option`、`self.engine.begin`、`command.upgrade`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.token`（L169–L178）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L171按`not path.exists()`分支。 调用`path.exists`、`path.open`、`f.write`、`secrets.token_urlsafe`、`path.chmod`、`path.read_text(encoding="utf-8").strip`、`path.read_text`。 返回路径：L178的`path.read_text(encoding="utf-8").strip()`。
- `Store.tx`（L181–L183）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.sessions.begin`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Store.request`（L185–L188）：接收`key`、`payload`、`operation`。 调用`FileLock`、`str`、`self._request`。 返回路径：L188的`self._request(key, payload, operation)`。
- `Store._request`（L190–L204）：接收`key`、`payload`、`operation`。 控制顺序：L191按`not key or len(key) > 100`分支；L192抛异常，停止当前正常路径；L195按`self.engine.dialect.name == "postgresql"`分支；L198按`previous`分支；L199按`previous.fingerprint != fingerprint`分支；L200抛异常，停止当前正常路径。 调用`len`、`Conflict`、`digest`、`self.tx`、`session.execute`、`text`、`session.get`、`operation`、`session.add`等。 返回路径：L201的`previous.response`；L204的`response`。
- `Store.create_project`（L206–L213）：接收`title`、`key`。 调用`self.request`。 返回路径：L213的`self.request(key, {"operation": "create-project", "title": title}, operation)`。
- `Store.create_project.operation`（L207–L211）：接收`session`。 调用`Project`、`session.add`、`session.flush`。 返回路径：L211的`{"id": project.id, "title": project.title}`。
- `Store.create_run`（L215–L247）：接收`project_id`、`data`、`key`。 调用`RunInput.model_validate(data).model_dump`、`RunInput.model_validate`、`self.request`。 返回路径：L245的`self.request( key, {"operation": "create-run", "project": project_id, **data}, operation )`。
- `Store.create_run.operation`（L218–L243）：接收`session`。 控制顺序：L219按`not session.get(Project, project_id)`分支；L220抛异常，停止当前正常路径；L231按`run.auto_mode`分支。 调用`session.get`、`Missing`、`Run`、`session.add`、`session.flush`、`Message`、`Job`、`Event`。 返回路径：L243的`{"run_id": run.id, "status": "QUEUED"}`。
- `Store.submit`（L249–L287）：接收`run_id`、`data`、`key`。 调用`ResumeInput.model_validate(data).model_dump`、`ResumeInput.model_validate`、`self.request`。 返回路径：L287的`self.request(key, {"operation": "submit", "run_id": run_id, **data}, operation)`。
- `Store.submit.operation`（L252–L285）：接收`session`。 控制顺序：L254按`not run`分支；L255抛异常，停止当前正常路径；L257按`not pending or pending["gate_id"] != data["gate_id"]`分支；L258抛异常，停止当前正常路径；L259按`data["action"] not in pending["actions"] and data["action"] != "recommend"`分支；L260抛异常，停止当前正常路径；L261按`data["action"] == "approve" and not pending.get("can_approve", False)`分支；L262抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`session.get`、`Missing`、`Conflict`、`pending.get`、`session.add`、`Event`、`Message`、`Approval`、`Job`等。 返回路径：L285的`{"run_id": run_id, "job_id": job.id, "status": "QUEUED"}`。
- `Store.retry`（L289–L303）：接收`run_id`、`key`。 调用`self.request`。 返回路径：L303的`self.request(key, {"operation": "retry", "run_id": run_id}, operation)`。
- `Store.retry.operation`（L290–L301）：接收`session`。 控制顺序：L292按`not run`分支；L293抛异常，停止当前正常路径；L294按`run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支；L295抛异常，停止当前正常路径。 调用`session.get`、`Missing`、`Conflict`、`session.add`、`Job`。 返回路径：L301的`{"run_id": run_id, "status": run.status}`。
- `Store.get_run`（L305–L310）：接收`run_id`。 控制顺序：L308按`not run`分支；L309抛异常，停止当前正常路径。 调用`self.tx`、`session.get`、`Missing`、`getattr`。 返回路径：L310的`{c.name: getattr(run, c.name) for c in Run.__table__.columns}`。
- `Store.messages`（L312–L317）：接收`run_id`。 调用`self.tx`、`session.scalars`、`select(Message).where(Message.run_id == run_id).order_by`、`select(Message).where`、`select`。 返回路径：L317的`[{"role": row.role, "content": row.content} for row in rows]`。
- `Store.step`（L319–L329）：接收`run_id`、`name`、`fn`。 控制顺序：L322按`old`分支。 调用`self.tx`、`session.scalar`、`select(Step).where`、`select`、`fn`、`json.loads`、`json.dumps`、`session.add`、`Step`等。 返回路径：L323的`old.data`；L329的`result`。
- `Store.reserve_model_call`（L331–L340）：接收`run_id`。 控制顺序：L334按`self.settings.max_model_calls`分支；L337按`changed != 1`分支；L338抛异常，停止当前正常路径。 调用`self.tx`、`update(Run).where`、`update`、`statement.where`、`session.execute`、`statement.values`、`PausedLimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.set_automation`（L342–L384）：接收`run_id`、`enabled`、`key`。 调用`self.request`。 返回路径：L382的`self.request( key, {"operation": "automation", "run_id": run_id, "enabled": enabled}, oper…`。
- `Store.set_automation.operation`（L343–L380）：接收`session`。 控制顺序：L345按`run is None`分支；L346抛异常，停止当前正常路径；L347按`run.status in {"READY", "SOURCE_READY", "REJECTED"}`分支；L348抛异常，停止当前正常路径；L361按`enabled and run.pending`分支；L374按`not enabled and run.status == "BLOCKED" and run.pending`分支；L377按`enabled and run.status in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支。 调用`session.get`、`Missing`、`Conflict`、`session.add`、`Event`、`Job`、`run.pending["stage"].upper`。 返回路径：L380的`{"run_id": run_id, "auto_mode": enabled, "status": run.status}`。
- `Store.auto_approve`（L386–L406）：接收`run_id`、`gate`。 控制顺序：L389按`not run or not run.auto_mode or not gate["can_approve"]`分支；L390抛异常，停止当前正常路径；L392按`current and not current.decision`分支；L393抛异常，停止当前正常路径；L394按`not current`分支。 调用`self.tx`、`session.get`、`Conflict`、`session.add`、`Approval`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.record_event`（L408–L410）：接收`run_id`、`kind`、`data`。 调用`self.tx`、`session.add`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.model_records`（L412–L444）：接收`run_id`。 调用`self.get_run`、`self.tx`、`session.scalars`、`select(Step) .where(Step.run_id == run_id, Step.name.like("model:…`、`select(Step) .where`、`select`、`Step.name.like`、`r.data.get`、`select(Event) .where(Event.run_id == run_id, Event.kind == "model…`等。 返回路径：L444的`sorted(records, key=lambda item: item["created_at"])`。
- `Store.gate`（L446–L468）：接收`run_id`、`stage`、`version`、`data`、`actions`、`can_approve`。 控制顺序：L450按`not session.get(Revision, gate_id)`分支。 调用`digest`、`self.tx`、`session.get`、`session.add`、`Revision`。 返回路径：L460的`{ "gate_id": gate_id, "stage": stage, "version": version, "digest": content_digest, "data"…`。
- `Store.check_decision`（L470–L491）：接收`run_id`、`gate`、`value`。 控制顺序：L471按`not isinstance(value, dict)`分支；L472抛异常，停止当前正常路径；L473按`value.get("gate_id") != gate["gate_id"] or ( value.get("action") not in gate["actions…`分支；L476抛异常，停止当前正常路径；L477按`value["action"] == "recommend"`分支；L478按`value.get("approved") is not True or not self.get_run(run_id)["auto_mode"]`分支；L479抛异常，停止当前正常路径；L480按`value["action"] == "approve" and not gate.get("can_approve", False)`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`Conflict`、`value.get`、`self.get_run`、`gate.get`、`self.tx`、`session.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.claim`（L493–L507）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L498按`job is None`分支；L503按`changed != 1`分支。 调用`self.tx`、`session.scalar`、`select(Job).where(Job.status == "QUEUED").order_by(Job.created_at…`、`select(Job).where(Job.status == "QUEUED").order_by`、`select(Job).where`、`select`、`session.execute`、`update(Job).where(Job.id == job.id, Job.status == "QUEUED").value…`、`update(Job).where`等。 返回路径：L499的`None`；L504的`None`；L507的`{"id": job.id, "run_id": job.run_id, "payload": job.payload}`。
- `Store.recover`（L509–L511）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.tx`、`session.execute`、`update(Job).where(Job.status == "RUNNING").values`、`update(Job).where`、`update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.finish`（L513–L522）：接收`job`、`status`、`pending`、`result`、`error`。 控制顺序：L518按`result is not None`分支。 调用`self.tx`、`session.get`、`session.add`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.events`（L524–L536）：接收`run_id`、`after`。 调用`self.get_run`、`self.tx`、`session.scalars`、`select(Event) .where(Event.run_id == run_id, Event.id > after) .o…`、`select(Event) .where`、`select`。 返回路径：L533的`[ {"id": r.id, "kind": r.kind, "data": r.data, "created_at": r.created_at} for r in rows ]`。
- `Store.list_projects`（L538–L545）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.tx`、`session.scalars`、`select(Project).order_by(Project.created_at.desc()).limit`、`select(Project).order_by`、`select`、`Project.created_at.desc`。 返回路径：L540的`[ {"id": p.id, "title": p.title, "created_at": p.created_at} for p in session.scalars( sel…`。
- `Store.list_runs`（L547–L565）：接收`project_id`。 控制顺序：L550按`project_id is not None`分支；L551按`not session.get(Project, project_id)`分支；L552抛异常，停止当前正常路径。 调用`self.tx`、`select(Run).order_by(Run.created_at.desc()).limit`、`select(Run).order_by`、`select`、`Run.created_at.desc`、`session.get`、`Missing`、`statement.where`、`session.scalars`。 返回路径：L554的`[ { "id": r.id, "project_id": r.project_id, "status": r.status, "template": r.template, "o…`。
- `Store.latest_revision`（L567–L575）：接收`run_id`、`stage`。 调用`self.tx`、`session.scalar`、`select(Revision) .where(Revision.run_id == run_id, Revision.stage…`、`select(Revision) .where`、`select`、`Revision.created_at.desc`。 返回路径：L575的`row.data if row else None`。
- `_cursor`（L579–L584）：接收`connection`。 调用`connection.cursor`、`cursor.close`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/store.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L584。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`23801`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/store.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9e3bdf350928eb79ebac0a3904f1d6fa911578c679a6786c1e8287b3a46cc54b"} -->
````python
# workbench/store.py
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
````
