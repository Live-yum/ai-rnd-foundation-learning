# tests/test_business_note_notifications.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `load_template`（L39–L43）：接收`name`、`filename`。 调用`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`。 返回路径：L43的`module`。
- `notification_plan`（L46–L60）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`runtime_plan().model_dump`、`runtime_plan`、`Plan.model_validate`。 返回路径：L60的`Plan.model_validate(raw)`。
- `test_note_notification_contract_accepts_declared_recipients`（L64–L71）：接收`recipient`。 控制顺序：L70断言`plan.business.notifications[-1].event == "note_added"`；L71断言`Plan.model_validate_json(plan.model_dump_json()) == plan`。 调用`business_plan`、`raw["business"]["notifications"].append`、`Plan.model_validate`、`Plan.model_validate_json`、`plan.model_dump_json`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_note_notification_contract_rejects_inapplicable_capabilities_and_selectors`（L75–L86）：接收`change`。 控制顺序：L79按`change == "disabled"`分支；L81按`change == "unassigned"`分支。 调用`business_plan`、`raw["business"]["notifications"].append`、`pytest.raises`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `extract_functions`（L89–L100）：接收`path`、`names`、`namespace`。 控制顺序：L91遍历`ast.parse(path.read_text(encoding="utf-8")).body`；L92按`isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names`分支；L95遍历`node.args.args + node.args.kwonlyargs`。 调用`ast.parse`、`path.read_text`、`isinstance`、`ast.Constant`、`nodes.append`、`ast.fix_missing_locations`、`ast.Module`、`exec`、`compile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent`（L104–L303）：接收`tmp_path`、`same_recipient`。 调用`dict`、`next`、`ast.parse`、`model.read_text`、`isinstance`、`exec`、`compile`、`ast.Module`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.Base`（L105–L106）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.User`（L108–L110）：继承`Base`。声明的数据项为`id`；类型约束/数据库列参数以完整定义为准。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.Request`（L112–L125）：继承`Base`。声明的数据项为`id`、`customer_id`、`assignee_id`、`request_state`、`resolved_at`、`due_at`、`created_id`、`created_time`、`updated_id`、`updated_time`、`is_deleted`、`deleted_time`；类型约束/数据库列参数以完整定义为准。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.actor`（L181–L182）：接收`db`、`auth`。 调用`str`。 返回路径：L182的`{"id": str(auth.user.id), "role": auth.role}`。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.auth`（L198–L199）：接收`identifier`、`role`。用本机Dex真实签发的JWT访问本机API创建密钥，不伪造token，也不向云身份服务注册账号。 调用`SimpleNamespace`。 返回路径：L199的`SimpleNamespace(user=SimpleNamespace(id=identifier), role=role)`。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.scenario`（L201–L301）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L245断言`list((await db.scalars(select(BusinessEvent))).all()) == []`；L246断言`(await db.get(Request, 7)).updated_time == original_time`；L256断言`denied.value.status_code == 404`；L269断言`[e.event for e in stored] == ["add_note"] + ["notification"] * ( 1 if same_recipient …`；L273断言`audit.payload["text"] == "Actual native note"`；L274断言`audit.payload["before"]["updated_at"] != audit.payload["after"]["updated_at"]`；L275断言`{e.recipient for e in stored[1:]} == {creator, assignee}`；L276断言`all(e.payload == {"event": "note_added"} for e in stored[1:])`。后续分支沿下方源码相同行号继续阅读。 调用`create_async_engine`、`async_sessionmaker`、`engine.begin`、`connection.run_sync`、`datetime`、`sessions`、`db.add_all`、`User`、`db.add`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_fastapi_note_reminders_are_atomic_scoped_and_idempotent.scenario.reject_notification`（L226–L228）：接收`mapper`、`connection`、`target`。 控制顺序：L227按`target.event == "notification"`分支；L228抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_note_dispatch_preserves_audit_transaction_recipient_and_read_guards`（L306–L322）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L309断言`"event(name,row,action,before,note)" in action`；L310断言`'case "add_note"->"note_added"' in action`；L311断言`"notify(name,row,notificationEvent,transition,audit)" in action`；L312断言`action.index("require(name,row,action)") < action.index( "event(name,row,action,befor…`；L315断言`"@Transactional(rollbackFor = Exception.class)" in source`；L316断言`'case "note_added"->"有新的备注"' in source`；L318断言`"ON CONFLICT(tenant_id,recipient_id,event_key) DO NOTHING" in mapper`；L319断言`"WHERE tenant_id=#{tenant} AND recipient_id=#{user}" in mapper`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / "templates/business/yudao/RndBusinessService.java").read_…`、`source.split("public Object action(", 1)[1].split`、`source.split`、`action.index`、`(ROOT / "templates/business/yudao/RndBusinessMapper.java").read_t…`、`(ROOT / "templates/business/fastapiadmin/index.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_notification_oracle_derives_every_recipient_and_deduplicates_one_source`（L325–L338）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L331断言`ledger.expected == { ("creator", "requests", "record", "note_added"): 1, ("assignee",…`；L336断言`ledger.expected["creator", "requests", "record", "note_added"] == 2`。 调用`load_template`、`notification_plan().model_dump`、`notification_plan`、`module.NotificationEvidence`、`ledger.event`、`pytest.raises`、`ledger.complete`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_notification_oracle_rejects_incomplete_or_misrouted_reminders`（L344–L372）：接收`corruption`。 控制顺序：L359按`corruption == "missing"`分支；L361按`corruption == "duplicated"`分支。 调用`load_template`、`module.NotificationEvidence`、`notification_plan().model_dump`、`notification_plan`、`ledger.event`、`ledger.inbox`、`deepcopy`、`notices.append`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_python_acceptance_requires_action_notifications_and_durable_reads`（L376–L424）：接收`tmp_path`、`fault`。 控制顺序：L387按`fault == "missing_note"`分支；L392按`fault == "missing_transition"`分支；L397按`fault == "read_reset"`分支；L399按`fault`分支；L400断言`text != source.read_text(encoding="utf-8")`；L415按`fault`分支；L416断言`result.returncode == 1 and evidence["passed"] is False`；L417断言`"notification" in evidence["message"].lower() or "read timestamp" in evidence["messag…`。后续分支沿下方源码相同行号继续阅读。 调用`generate_basic`、`notification_plan`、`source.read_text`、`text.replace`、`source.write_text`、`clean_env`、`os.environ.get`、`subprocess.run`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_python_notification_integrity_failure_rolls_back_whole_note`（L514–L549）：接收`tmp_path`、`failing_recipient`。 控制顺序：L539断言`initialized.returncode == 0`；L549断言`result.returncode == 0`。 调用`generate_basic`、`notification_plan`、`clean_env`、`os.environ.get`、`str`、`subprocess.run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_note_notifications.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L549。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22927`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_note_notifications.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e015a24f678599dc80bf22b857fcf9e4ce6ab7c3eb7c7b67fedd84f7887d3640"} -->
````python
# tests/test_business_note_notifications.py
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
````
