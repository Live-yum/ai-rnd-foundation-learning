"""Canonical note reminders preserve native audit events and transactional boundaries."""

import ast
import asyncio
import importlib.util
import os
import subprocess
import sys
from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    select,
)
from sqlalchemy import (
    event as sql_event,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from test_business_contracts import business_plan
from test_business_python import runtime_plan

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env


def load_template(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def notification_plan():
    raw = runtime_plan().model_dump()
    raw["business"]["notifications"] = [
        {"entity": "requests", "event": event, "recipient": recipient, **extra}
        for event, extra in [
            ("created", {}),
            ("assigned", {}),
            ("note_added", {}),
            ("transitioned", {"transition": "start"}),
            ("transitioned", {"transition": "resolve"}),
            ("due", {"due_field": "due_at"}),
        ]
        for recipient in (["creator"] if event == "created" else ["creator", "assignee"])
    ]
    return Plan.model_validate(raw)


@pytest.mark.parametrize("recipient", ["creator", "assignee"])
def test_note_notification_contract_accepts_declared_recipients(recipient):
    raw = business_plan()
    raw["business"]["notifications"].append(
        {"entity": "requests", "event": "note_added", "recipient": recipient}
    )
    plan = Plan.model_validate(raw)
    assert plan.business.notifications[-1].event == "note_added"
    assert Plan.model_validate_json(plan.model_dump_json()) == plan


@pytest.mark.parametrize("change", ["disabled", "transition", "due_field", "unassigned"])
def test_note_notification_contract_rejects_inapplicable_capabilities_and_selectors(change):
    raw = business_plan()
    rule = {"entity": "customers", "event": "note_added", "recipient": "creator"}
    raw["business"]["notifications"].append(rule)
    if change == "disabled":
        raw["business"]["resources"][0]["notes"] = False
    elif change == "unassigned":
        rule["recipient"] = "assignee"
    else:
        rule[change] = "resolve" if change == "transition" else "created_at"
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def extract_functions(path, names, namespace):
    nodes = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            node.returns = None
            for arg in node.args.args + node.args.kwonlyargs:
                arg.annotation = None
            node.args.defaults = [ast.Constant(None) for _ in node.args.defaults]
            nodes.append(node)
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, str(path), "exec"), namespace)


@pytest.mark.parametrize("same_recipient", [False, True])
def test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent(tmp_path, same_recipient):
    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "sys_user"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

    class Request(Base):
        __tablename__ = "requests"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        customer_id: Mapped[str] = mapped_column(String)
        assignee_id: Mapped[int] = mapped_column(Integer)
        request_state: Mapped[str] = mapped_column(String)
        resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
        due_at: Mapped[datetime | None] = mapped_column(DateTime)
        created_id: Mapped[int] = mapped_column(Integer)
        created_time: Mapped[datetime] = mapped_column(DateTime)
        updated_id: Mapped[int] = mapped_column(Integer)
        updated_time: Mapped[datetime] = mapped_column(DateTime)
        is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
        deleted_time: Mapped[datetime | None] = mapped_column(DateTime)

    model_scope = dict(
        MappedBase=Base,
        Mapped=Mapped,
        mapped_column=mapped_column,
        CONFIG={"namespace": "note_test"},
        Integer=Integer,
        String=String,
        ForeignKey=ForeignKey,
        JSON=JSON,
        DateTime=DateTime,
        datetime=datetime,
        UTC=UTC,
    )
    model = ROOT / "templates/business/fastapiadmin/model.py"
    event_class = next(
        node for node in ast.parse(model.read_text()).body if isinstance(node, ast.ClassDef)
    )
    exec(compile(ast.Module(body=[event_class], type_ignores=[]), str(model), "exec"), model_scope)
    BusinessEvent = model_scope["BusinessEvent"]
    plan = notification_plan().model_dump()
    plan["business"]["notifications"] = [
        n for n in plan["business"]["notifications"] if n["event"] == "note_added"
    ]
    policy = load_template("note_policy", "templates/business/common/policy.py")
    scope = dict(
        SPEC=plan["business"],
        ENTITIES={e["name"]: e for e in plan["entities"]},
        POLICY=policy.Policy(plan),
        PolicyError=policy.PolicyError,
        MODELS={"requests": Request},
        HTTPException=HTTPException,
        select=select,
        BusinessEvent=BusinessEvent,
        datetime=datetime,
        UTC=UTC,
        date=__import__("datetime").date,
    )
    extract_functions(
        ROOT / "templates/business/fastapiadmin/runtime.py",
        {
            "fail",
            "identifier",
            "serialize",
            "grant",
            "scope",
            "record",
            "record_title",
            "event",
            "mutate",
        },
        scope,
    )
    rt = SimpleNamespace(**scope)

    async def actor(db, auth):
        return {"id": str(auth.user.id), "role": auth.role}

    rt.actor = actor
    controller = dict(
        rt=rt,
        select=select,
        UserModel=User,
        BusinessEvent=BusinessEvent,
        datetime=datetime,
        UTC=UTC,
        SuccessResponse=lambda **kw: kw["data"],
    )
    extract_functions(
        ROOT / "templates/business/fastapiadmin/controller.py", {"inbox", "read_notice"}, controller
    )

    def auth(identifier, role):
        return SimpleNamespace(user=SimpleNamespace(id=identifier), role=role)

    async def scenario():
        engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'native.db'}")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
            creator, assignee = 1, 1 if same_recipient else 2
            original_time = datetime(2020, 1, 1)
            async with sessions() as db:
                db.add_all(User(id=i) for i in [1, 2, 3])
                db.add(
                    Request(
                        id=7,
                        customer_id="9",
                        assignee_id=assignee,
                        request_state="active",
                        created_id=creator,
                        created_time=original_time,
                        updated_id=creator,
                        updated_time=original_time,
                    )
                )
                await db.commit()

            # Inject a notification write failure: the note/audit/row mutation must roll back.
            def reject_notification(mapper, connection, target):
                if target.event == "notification":
                    raise RuntimeError("synthetic reminder storage failure")

            sql_event.listen(BusinessEvent, "before_insert", reject_notification)
            try:
                async with sessions() as db:
                    with pytest.raises(RuntimeError, match="synthetic reminder storage failure"):
                        await rt.mutate(
                            db,
                            {"id": "1", "role": "manager"},
                            "requests",
                            7,
                            "add_note",
                            {"text": "Must roll back"},
                        )
            finally:
                sql_event.remove(BusinessEvent, "before_insert", reject_notification)
            async with sessions() as db:
                assert list((await db.scalars(select(BusinessEvent))).all()) == []
                assert (await db.get(Request, 7)).updated_time == original_time
                with pytest.raises(HTTPException) as denied:
                    await rt.mutate(
                        db,
                        {"id": "3", "role": "employee"},
                        "requests",
                        7,
                        "add_note",
                        {"text": "Denied"},
                    )
                assert denied.value.status_code == 404
                await rt.mutate(
                    db,
                    {"id": "1", "role": "manager"},
                    "requests",
                    7,
                    "add_note",
                    {"text": "Actual native note"},
                )
            async with sessions() as db:
                stored = list(
                    (await db.scalars(select(BusinessEvent).order_by(BusinessEvent.id))).all()
                )
                assert [e.event for e in stored] == ["add_note"] + ["notification"] * (
                    1 if same_recipient else 2
                )
                audit = stored[0]
                assert audit.payload["text"] == "Actual native note"
                assert audit.payload["before"]["updated_at"] != audit.payload["after"]["updated_at"]
                assert {e.recipient for e in stored[1:]} == {creator, assignee}
                assert all(e.payload == {"event": "note_added"} for e in stored[1:])
                assert all(e.source_key == f"{audit.id}:{e.recipient}" for e in stored[1:])
            for recipient in {creator, assignee}:
                who = auth(recipient, "manager" if recipient == creator else "service")
                async with sessions() as db:
                    notices = await controller["inbox"](who, db)
                    assert len(notices) == 1 and notices[0]["event"] == "note_added"
                    assert notices == await controller["inbox"](who, db)
                    with pytest.raises(HTTPException) as denied:
                        await controller["read_notice"](notices[0]["id"], auth(3, "employee"), db)
                    assert denied.value.status_code == 404
                    await controller["read_notice"](notices[0]["id"], who, db)
                    first_read = (await db.get(BusinessEvent, int(notices[0]["id"]))).read_at
                    await controller["read_notice"](notices[0]["id"], who, db)
                    assert (
                        await db.get(BusinessEvent, int(notices[0]["id"]))
                    ).read_at == first_read
                async with sessions() as db:
                    assert (await controller["inbox"](who, db))[0]["read"] is True
            async with sessions() as db:
                assert await controller["inbox"](auth(3, "employee"), db) == []
                assert len((await db.scalars(select(BusinessEvent))).all()) == 2 + (
                    not same_recipient
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_yudao_note_dispatch_preserves_audit_transaction_recipient_and_read_guards():
    source = (ROOT / "templates/business/yudao/RndBusinessService.java").read_text(encoding="utf-8")
    action = source.split("public Object action(", 1)[1].split("public Object related(", 1)[0]
    assert "event(name,row,action,before,note)" in action
    assert 'case "add_note"->"note_added"' in action
    assert "notify(name,row,notificationEvent,transition,audit)" in action
    assert action.index("require(name,row,action)") < action.index(
        "event(name,row,action,before,note)"
    )
    assert "@Transactional(rollbackFor = Exception.class)" in source
    assert 'case "note_added"->"有新的备注"' in source
    mapper = (ROOT / "templates/business/yudao/RndBusinessMapper.java").read_text(encoding="utf-8")
    assert "ON CONFLICT(tenant_id,recipient_id,event_key) DO NOTHING" in mapper
    assert "WHERE tenant_id=#{tenant} AND recipient_id=#{user}" in mapper
    assert "read_at=COALESCE(read_at,CURRENT_TIMESTAMP)" in mapper
    page = (ROOT / "templates/business/fastapiadmin/index.vue").read_text(encoding="utf-8")
    assert "note_added: '添加备注'" in page


def test_notification_oracle_derives_every_recipient_and_deduplicates_one_source():
    module = load_template("note_verifier", "templates/product/verify_business.py")
    plan = notification_plan().model_dump()
    ledger = module.NotificationEvidence(plan["business"])
    row = {"id": "record", "created_by": "creator", "assignee_id": "assignee"}
    ledger.event("requests", row, "note_added")
    assert ledger.expected == {
        ("creator", "requests", "record", "note_added"): 1,
        ("assignee", "requests", "record", "note_added"): 1,
    }
    ledger.event("requests", {**row, "assignee_id": "creator"}, "note_added")
    assert ledger.expected["creator", "requests", "record", "note_added"] == 2
    with pytest.raises(ValueError, match="not exercised"):
        ledger.complete()


@pytest.mark.parametrize(
    "corruption", ["missing", "duplicated", "recipient", "event", "record", "timestamp"]
)
def test_notification_oracle_rejects_incomplete_or_misrouted_reminders(corruption):
    module = load_template("note_verifier_negative", "templates/product/verify_business.py")
    ledger = module.NotificationEvidence(notification_plan().model_dump()["business"])
    row = {"id": "record", "created_by": "creator", "assignee_id": "assignee"}
    ledger.event("requests", row, "note_added")
    notice = {
        "id": "notice",
        "recipient_id": "creator",
        "entity": "requests",
        "record_id": "record",
        "event": "note_added",
        "created_at": "2026-01-01T00:00:00Z",
    }
    ledger.inbox({"id": "creator"}, [notice])
    notices = [deepcopy(notice)]
    if corruption == "missing":
        notices = []
    elif corruption == "duplicated":
        notices.append({**notice, "id": "duplicate"})
    else:
        field = {
            "recipient": "recipient_id",
            "event": "event",
            "record": "record_id",
            "timestamp": "created_at",
        }[corruption]
        notices[0][field] = "wrong" if corruption != "timestamp" else None
    with pytest.raises(ValueError):
        ledger.inbox({"id": "creator"}, notices)


@pytest.mark.parametrize("fault", [None, "missing_note", "missing_transition", "read_reset"])
def test_generated_python_acceptance_requires_action_notifications_and_durable_reads(
    tmp_path, fault
):
    product = tmp_path / "product"
    generate_basic(
        notification_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    source = product / "business_runtime.py"
    text = source.read_text(encoding="utf-8")
    if fault == "missing_note":
        text = text.replace(
            'notify(connection, entity, row, "note_added", eid)',
            "pass  # omitted notification fault",
        )
    elif fault == "missing_transition":
        text = text.replace(
            'notify(connection, entity, after, "transitioned", event_id, data.transition)',
            "pass  # omitted notification fault",
        )
    elif fault == "read_reset":
        text = text.replace('timestamp = row["read_at"] or utc()', "timestamp = utc()")
    if fault:
        assert text != source.read_text(encoding="utf-8")
        source.write_text(text, encoding="utf-8")
    env = clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"})
    result = subprocess.run(
        [sys.executable, "verify.py", "--python", sys.executable],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
    )
    import json

    evidence = json.loads(result.stdout.splitlines()[-1])
    if fault:
        assert result.returncode == 1 and evidence["passed"] is False, result.stdout + result.stderr
        assert (
            "notification" in evidence["message"].lower()
            or "read timestamp" in evidence["message"].lower()
        ), evidence
    else:
        assert result.returncode == 0 and evidence["passed"] is True, result.stdout + result.stderr
        assert "business-notifications" in evidence["checks"]
        assert "process_restart_persistence" in evidence["checks"]


NOTE_ATOMICITY_SCENARIO = r"""
import getpass
import inspect
import json
import sys

from fastapi.testclient import TestClient
from sqlalchemy import select, text

import manage

getpass.getpass = lambda _: "Example-Test-Password-123"
manage.bootstrap_admin("admin")
from app import app
from schema import engine, metadata

with TestClient(app, raise_server_exceptions=False) as client:
    login = client.post("/auth/login", json={"username": "admin", "password": "Example-Test-Password-123"})
    assert login.status_code == 200, login.text
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}

    def post(path, data, status=200):
        response = client.post(path, headers=headers, json=data)
        assert response.status_code == status, response.text
        return response.json()

    admin = client.get("/business/me", headers=headers).json()
    service = post("/business/users", {"username": "service", "password": "Example-Test-Password-123", "role": "service"}, 201)
    customer = post("/api/customers", {"name": "Atomic customer"}, 201)
    row = post("/api/requests", {"customer_id": customer["id"]}, 201)
    row = post(f"/api/requests/{row['id']}/assign", {"user_id": service["id"]})
    blocked = admin["id"] if sys.argv[1] == "creator" else service["id"]
    tables = metadata.tables
    notes, audit, notices = (tables[name] for name in ("business_notes", "business_audit", "business_notifications"))

    def snapshots():
        with engine.connect() as connection:
            return {
                "notes": [dict(r) for r in connection.execute(select(notes).where(notes.c.record_id == row["id"])).mappings()],
                "audit": [dict(r) for r in connection.execute(select(audit).where(audit.c.record_id == row["id"], audit.c.action == "note_added")).mappings()],
                "notifications": [dict(r) for r in connection.execute(select(notices).where(notices.c.record_id == row["id"], notices.c.event == "note_added")).mappings()],
            }

    before = snapshots()
    assert before == {"notes": [], "audit": [], "notifications": []}
    with engine.begin() as connection:
        connection.execute(text(f"CREATE TRIGGER fail_note_reminder BEFORE INSERT ON business_notifications WHEN NEW.event = 'note_added' AND NEW.recipient_id = '{blocked}' BEGIN SELECT RAISE(ABORT, 'synthetic notification constraint failure'); END"))
    failed = client.post(f"/api/requests/{row['id']}/notes", headers=headers, json={"body": "Must roll back"})
    assert failed.status_code == 500, failed.text
    assert snapshots() == before, snapshots()
    with engine.begin() as connection:
        connection.execute(text("DROP TRIGGER fail_note_reminder"))
    note = post(f"/api/requests/{row['id']}/notes", {"body": "Confirmed atomic note"}, 201)
    stored = snapshots()
    assert len(stored["notes"]) == len(stored["audit"]) == 1, stored
    assert len(stored["notifications"]) == 2, stored
    assert {n["recipient_id"] for n in stored["notifications"]} == {admin["id"], service["id"]}
    assert stored["audit"][0]["action"] == "note_added"
    assert json.loads(stored["audit"][0]["after_json"]) == note

    # Model an exact duplicate becoming visible between precheck and insertion.
    # A real unique-key violation must remain harmless after its savepoint rollback.
    endpoint = next(route.endpoint for route in app.routes if getattr(route, "path", "") == "/api/{entity}/{identity}/notes" and "POST" in getattr(route, "methods", set()))
    notify = inspect.getclosurevars(endpoint).nonlocals["notify"]

    class StalePrecheck:
        def __init__(self, connection):
            self.connection = connection
            self.calls = 0
        def scalar(self, statement):
            self.calls += 1
            return None if self.calls == 1 else self.connection.scalar(statement)
        def execute(self, statement):
            return self.connection.execute(statement)
        def begin_nested(self):
            return self.connection.begin_nested()

    with engine.begin() as connection:
        raced = StalePrecheck(connection)
        notify(raced, "requests", row, "note_added", stored["audit"][0]["id"])
        assert raced.calls >= 3
    assert snapshots() == stored
print(json.dumps({"passed": True, "atomic_rollback": True, "exact_duplicate_preserved": True}))
"""


@pytest.mark.parametrize("failing_recipient", ["creator", "assignee"])
def test_generated_python_notification_integrity_failure_rolls_back_whole_note(
    tmp_path, failing_recipient
):
    product = tmp_path / "product"
    generate_basic(
        notification_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
        }
    )
    initialized = subprocess.run(
        [sys.executable, "manage.py", "init"],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=60,
    )
    assert initialized.returncode == 0, initialized.stdout + initialized.stderr
    result = subprocess.run(
        [sys.executable, "-c", NOTE_ATOMICITY_SCENARIO, failing_recipient],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
