# tests/test_legacy_signup_recovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.domain`、`workbench.flow`、`workbench.requirement_intent`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `admin_requirement`（L28–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Requirement`。 返回路径：L29的`Requirement( summary="管理员维护竞赛报名记录", users=["管理员"], data_scope="shared", features=["后台录入和维护…`。
- `RecordingGateway`（L38–L49）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `RecordingGateway.__init__`（L39–L42）：接收`requirement`、`plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `RecordingGateway.complete`（L44–L49）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L46按`schema is Requirement`分支；L48断言`schema is Plan`。 调用`self.calls.append`、`self.requirement.model_copy`、`self.plan.model_copy`。 返回路径：L47的`self.requirement.model_copy(deep=True)`；L49的`self.plan.model_copy(deep=True)`。
- `approvals`（L52–L61）：接收`store`、`run`。 调用`store.tx`、`list`、`session.execute`、`select(Approval.gate_id, Approval.decision, Approval.actor) .join…`、`select(Approval.gate_id, Approval.decision, Approval.actor) .join`、`select`。 返回路径：L54的`list( session.execute( select(Approval.gate_id, Approval.decision, Approval.actor) .join(R…`。
- `create_legacy_failure`（L64–L121）：接收`settings`、`store`、`monkeypatch`、`plan`、`original`。 源码说明：Persist old automatic downgrade plus crash after requirements approval.。 控制顺序：L69按`not native`分支；L111断言`worker.tick()`；L113断言`snapshot.next == ("design",)`；L114断言`pending_interrupt(snapshot) is None`；L116断言`failed["status"] == "FAILED"`；L117断言`"ModuleNotFoundError" in failed["error"]`；L118断言`failed["pending"] is None`；L119断言`len(approvals(store, run)) == 1`。后续分支沿下方源码相同行号继续阅读。 调用`admin_requirement`、`requirement.model_copy`、`plan.model_copy`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`RecordingGateway`、`monkeypatch.context`等。 返回路径：L121的`run, gateway`。
- `create_legacy_failure.old_analyse`（L88–L90）：接收`state`。 调用`requirement.gate_dump`。 返回路径：L90的`{"requirement": requirement.gate_dump()}`。
- `create_legacy_failure.old_requirements`（L92–L99）：接收`state`。 调用`self.gate`。 返回路径：L93的`self.gate( state, "requirements", {"requirement": state["requirement"], "ready": True}, ["…`。
- `create_legacy_failure.broken_import`（L101–L102）：接收`state`。 控制顺序：L102抛异常，停止当前正常路径。 调用`ModuleNotFoundError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_old_failed_signup_reopens_guard_without_repeating_decisions`（L124–L154）：接收`settings`、`store`、`monkeypatch`、`plan`。 控制顺序：L131断言`worker.tick()`；L133断言`recovered["status"] == "BLOCKED"`；L135断言`gate["stage"] == "clarification" and gate["can_approve"] is False`；L137断言`conflicts[0]["source"]["quote"] == ORIGINAL`；L138断言`conflicts[0]["capability"] == "entrant-registration-entrypoint"`；L140断言`conflicts[0]["code"] == "registration_entrypoint_unresolved"`；L141断言`gate["data"]["requirement"]["unsupported"] == []`；L144遍历`range(3)`。后续分支沿下方源码相同行号继续阅读。 调用`create_legacy_failure`、`approvals`、`store.retry`、`Runtime`、`worker.tick`、`store.get_run`、`pytest.raises`、`decision`、`range`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_supported_scope_correction_resumes_same_failed_run`（L158–L197）：接收`settings`、`store`、`monkeypatch`、`plan`、`correction`。 控制顺序：L162按`correction == AUTHENTICATED_CORRECTION`分支；L173断言`worker.tick()`；L174断言`store.get_run(run)["status"] == "BLOCKED"`；L177断言`worker.tick()`；L179断言`corrected["status"] == "WAITING_REQUIREMENTS"`；L180断言`corrected["pending"]["can_approve"] is True`；L181断言`not corrected["pending"]["data"].get("capability_conflicts")`；L182断言`corrected["pending"]["data"]["requirement"]["unsupported"] == []`。后续分支沿下方源码相同行号继续阅读。 调用`create_legacy_failure`、`Requirement`、`approvals`、`store.retry`、`Runtime`、`worker.tick`、`store.get_run`、`store.set_automation`、`decision`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_auth_registration_is_not_public_competition_signup`（L200–L216）：接收`settings`、`store`、`monkeypatch`、`plan`。 控制顺序：L209断言`worker.tick()`；L211断言`state["status"] == "WAITING_DESIGN"`；L212断言`state["pending"]["can_approve"] is True`；L213断言`not state["pending"]["data"].get("capability_conflicts")`；L214断言`approvals(store, run) == original_approvals`；L215断言`[key for key, _ in gateway.calls] == ["plan:1"]`；L216断言`store.messages(run) == [{"role": "user", "content": original}]`。 调用`create_legacy_failure`、`approvals`、`store.set_automation`、`store.retry`、`Runtime`、`worker.tick`、`store.get_run`、`state["pending"]["data"].get`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_admin_option_plus_retained_entrant_flow_requires_clarification`（L226–L227）：接收`answer`。 控制顺序：L227断言`scope_conflicts([ORIGINAL, answer], Selection(template="fastapiadmin").capabilities()…`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_no_login_and_negated_withdrawal_cannot_become_auth_only`（L238–L240）：接收`human`。 控制顺序：L240断言`conflicts and any(conflict["unsupported"] for conflict in conflicts)`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supported_authenticated_employee_flow_and_anonymous_prohibition_do_not_block`（L252–L253）：接收`original`。 控制顺序：L253断言`scope_conflicts([original], Selection(template="fastapiadmin").capabilities()) == []`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_internal_employee_authenticated_submission_reaches_requirement_review`（L256–L279）：接收`settings`、`store`、`plan`。 控制顺序：L273断言`worker.tick()`；L275断言`current["status"] == "WAITING_REQUIREMENTS"`；L276断言`current["pending"]["can_approve"]`；L277断言`not current["pending"]["data"].get("analysis_diagnostics")`；L278断言`[key for key, _ in gateway.calls] == ["requirement:1"]`；L279断言`store.messages(run) == [{"role": "user", "content": original}]`。 调用`Requirement`、`RecordingGateway`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`Runtime`、`worker.tick`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_old_authenticated_design_gate_replays_then_requires_new_intent_review`（L282–L348）：接收`settings`、`store`、`monkeypatch`。 源码说明：New executable checks must not invalidate a persisted old gate digest.。 控制顺序：L320断言`worker.tick()`；L322断言`worker.tick()`；L324断言`old["stage"] == "design" and old["can_approve"]`；L326断言`not snapshot.values.get("requirement_intent_version")`；L329断言`len(accepted_before_resume) == 2`；L331断言`worker.tick()`；L333断言`current["status"] == "WAITING_REQUIREMENTS"`；L334断言`current["pending"]["gate_id"] != old["gate_id"]`。后续分支沿下方源码相同行号继续阅读。 调用`Requirement`、`Plan.model_validate`、`RecordingGateway`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`monkeypatch.setattr`、`monkeypatch.context`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_ready_gate_does_not_gain_scope_approval_from_delegation`（L353–L412）：接收`settings`、`store`、`monkeypatch`、`plan`、`stage`、`interrupted_auto_start`。 源码说明：Both an explicit smart command and recovered automatic loop stay unapproved.。 控制顺序：L387按`interrupted_auto_start`分支；L389断言`job["payload"]["action"] == "start"`；L394断言`worker.tick()`；L395断言`store.get_run(run)["status"] == "WAITING_" + stage.upper()`；L397断言`old["stage"] == stage and old["can_approve"] is True`；L398断言`approvals(store, run) == []`；L399按`not interrupted_auto_start`分支；L402断言`worker.tick()`。后续分支沿下方源码相同行号继续阅读。 调用`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`plan.model_copy`、`RecordingGateway`、`admin_requirement`、`monkeypatch.context`、`legacy.setattr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_legacy_signup_recovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L412。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18610`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_legacy_signup_recovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d8f4b1ccd35bdbca5a99846096392afeebb233c1acbfdc0f10bdd8c204f0ba7e"} -->
````python
# tests/test_legacy_signup_recovery.py
"""Independent regression for pre-upgrade FAILED design checkpoints.

These tests write a real SQLite Store and LangGraph checkpoint with the old
node behavior, reload the worker, then use the normal persisted resume protocol.
Model responses are local fixtures; no native services or paid calls are used.
"""

import uuid

import pytest
from conftest import decision
from sqlalchemy import select

from workbench.catalog import Selection
from workbench.domain import Plan, Requirement
from workbench.flow import Workflow
from workbench.requirement_intent import scope_conflicts
from workbench.runtime import Runtime, pending_interrupt
from workbench.store import Approval, Conflict, Revision

ORIGINAL = "大学生计算机设计大赛报名网站"
CORRECTION = "取消参赛者自行提交报名，改为仅管理员录入和维护报名记录"
AUTHENTICATED_CORRECTION = (
    "参赛者注册登录后自行提交报名、仅管理本人报名，采用现有业务界面，不需要匿名提交或独立公开门户"
)


def admin_requirement():
    return Requirement(
        summary="管理员维护竞赛报名记录",
        users=["管理员"],
        data_scope="shared",
        features=["后台录入和维护报名记录"],
        acceptance=["管理员可维护报名记录"],
    )


class RecordingGateway:
    def __init__(self, requirement, plan):
        self.requirement = requirement
        self.plan = plan
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append((key, payload))
        if schema is Requirement:
            return self.requirement.model_copy(deep=True)
        assert schema is Plan
        return self.plan.model_copy(deep=True)


def approvals(store, run):
    with store.tx() as session:
        return list(
            session.execute(
                select(Approval.gate_id, Approval.decision, Approval.actor)
                .join(Revision, Revision.gate_id == Approval.gate_id)
                .where(Revision.run_id == run)
                .order_by(Approval.gate_id)
            )
        )


def create_legacy_failure(settings, store, monkeypatch, plan, *, original=ORIGINAL):
    """Persist old automatic downgrade plus crash after requirements approval."""
    native = original == ORIGINAL
    selected = "fastapiadmin" if native else "python-basic"
    requirement = admin_requirement()
    if not native:
        requirement = requirement.model_copy(
            update={
                "summary": "个人任务管理",
                "users": ["注册用户"],
                "data_scope": "per_user",
                "features": ["CRUD"],
                "acceptance": ["CRUD 和两用户隔离"],
            }
        )
    plan = plan.model_copy(update={"data_scope": requirement.data_scope})
    project = store.create_project("legacy import recovery", str(uuid.uuid4()))
    run = store.create_run(
        project["id"],
        {"requirement": original, "template": selected, "intelligent": True},
        str(uuid.uuid4()),
    )["run_id"]
    gateway = RecordingGateway(requirement, plan)

    def old_analyse(self, state):
        # Old checkpoint has no capability/source-cursor fields.
        return {"requirement": requirement.gate_dump()}

    def old_requirements(self, state):
        return self.gate(
            state,
            "requirements",
            {"requirement": state["requirement"], "ready": True},
            ["approve", "revise", "reject"],
            True,
        )

    def broken_import(self, state):
        raise ModuleNotFoundError("No module named 'psycopg'", name="psycopg")

    with monkeypatch.context() as legacy:
        legacy.setattr(Workflow, "analyse", old_analyse)
        legacy.setattr(Workflow, "requirements", old_requirements)
        legacy.setattr(Workflow, "source_context", lambda *_: {"code_context": {}})
        legacy.setattr(Workflow, "design", broken_import)
        legacy.setattr(Workflow, "capability_recovery", lambda *a, **kw: None, raising=False)
        with Runtime(settings, store, gateway) as worker:
            assert worker.tick()
            snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
            assert snapshot.next == ("design",)
            assert pending_interrupt(snapshot) is None
    failed = store.get_run(run)
    assert failed["status"] == "FAILED", failed
    assert "ModuleNotFoundError" in failed["error"]
    assert failed["pending"] is None
    assert len(approvals(store, run)) == 1
    assert [key for key, _ in gateway.calls] == ["plan:1"]
    return run, gateway


def test_old_failed_signup_reopens_guard_without_repeating_decisions(
    settings, store, monkeypatch, plan
):
    run, gateway = create_legacy_failure(settings, store, monkeypatch, plan)
    original_approvals = approvals(store, run)
    store.retry(run, "resume-old-import-failure")
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        recovered = store.get_run(run)
        assert recovered["status"] == "BLOCKED", recovered
        gate = recovered["pending"]
        assert gate["stage"] == "clarification" and gate["can_approve"] is False
        conflicts = gate["data"]["capability_conflicts"]
        assert conflicts[0]["source"]["quote"] == ORIGINAL
        assert conflicts[0]["capability"] == "entrant-registration-entrypoint"
        # The short original goal does not itself demand anonymous access.
        assert conflicts[0]["code"] == "registration_entrypoint_unresolved"
        assert gate["data"]["requirement"]["unsupported"] == []
        with pytest.raises(Conflict):
            decision(store, run, "approve")
        for index in range(3):
            store.set_automation(run, True, f"repeat-smart-{index}")
            worker.tick()
            current = store.get_run(run)
            assert current["status"] == "BLOCKED", current
            assert current["pending"]["can_approve"] is False
            assert current["pending"]["data"]["capability_conflicts"] == conflicts
    assert approvals(store, run) == original_approvals
    assert [key for key, _ in gateway.calls] == ["plan:1"]
    assert store.messages(run) == [{"role": "user", "content": ORIGINAL}]
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()


@pytest.mark.parametrize("correction", [CORRECTION, AUTHENTICATED_CORRECTION])
def test_explicit_supported_scope_correction_resumes_same_failed_run(
    settings, store, monkeypatch, plan, correction
):
    run, gateway = create_legacy_failure(settings, store, monkeypatch, plan)
    if correction == AUTHENTICATED_CORRECTION:
        gateway.requirement = Requirement(
            summary=ORIGINAL,
            users=["参赛者", "管理员"],
            data_scope="shared",
            features=["参赛者注册登录后在现有业务界面自行提交报名，仅管理本人报名记录"],
            acceptance=["参赛者仅可创建和维护本人报名，不能维护其他参赛者的报名"],
        )
    original_approvals = approvals(store, run)
    store.retry(run, "restore-scope-gate")
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        assert store.get_run(run)["status"] == "BLOCKED"
        store.set_automation(run, False, "review-corrected-scope")
        decision(store, run, "answer", correction)
        assert worker.tick()
        corrected = store.get_run(run)
        assert corrected["status"] == "WAITING_REQUIREMENTS", corrected
        assert corrected["pending"]["can_approve"] is True
        assert not corrected["pending"]["data"].get("capability_conflicts")
        assert corrected["pending"]["data"]["requirement"]["unsupported"] == []
        if correction == AUTHENTICATED_CORRECTION:
            assert corrected["pending"]["data"]["requirement"]["summary"] == ORIGINAL
            assert any(
                "自行提交报名" in feature
                for feature in corrected["pending"]["data"]["requirement"]["features"]
            )
    assert approvals(store, run) == original_approvals
    assert len(gateway.calls) == 2
    payload = gateway.calls[-1][1]
    assert payload["original_request"] == ORIGINAL
    assert payload["fresh_user_corrections"] == [correction]
    assert store.messages(run) == [
        {"role": "user", "content": ORIGINAL},
        {"role": "user", "content": correction},
    ]


def test_legacy_auth_registration_is_not_public_competition_signup(
    settings, store, monkeypatch, plan
):
    original = "内部个人任务管理，用户注册账号并登录后管理自己的任务"
    run, gateway = create_legacy_failure(settings, store, monkeypatch, plan, original=original)
    original_approvals = approvals(store, run)
    store.set_automation(run, False, "manual-retry")
    store.retry(run, "resume-auth-only-failure")
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        state = store.get_run(run)
        assert state["status"] == "WAITING_DESIGN", state
        assert state["pending"]["can_approve"] is True
        assert not state["pending"]["data"].get("capability_conflicts")
    assert approvals(store, run) == original_approvals
    assert [key for key, _ in gateway.calls] == ["plan:1"]
    assert store.messages(run) == [{"role": "user", "content": original}]


@pytest.mark.parametrize(
    "answer",
    [
        CORRECTION + "\n其他补充：也允许游客无需登录提交报名",
        CORRECTION + "\n其他补充：但保留参赛者注册登录后自行提交报名",
    ],
)
def test_admin_option_plus_retained_entrant_flow_requires_clarification(answer):
    assert scope_conflicts([ORIGINAL, answer], Selection(template="fastapiadmin").capabilities())


@pytest.mark.parametrize(
    "human",
    [
        [ORIGINAL + "，参赛者不需要登录即可提交报名"],
        [ORIGINAL + "，参赛者无需登录即可提交报名"],
        [ORIGINAL + "，必须支持匿名报名", "不要取消匿名报名，参赛者登录后自行提交报名"],
    ],
)
def test_explicit_no_login_and_negated_withdrawal_cannot_become_auth_only(human):
    conflicts = scope_conflicts(human, Selection(template="fastapiadmin").capabilities())
    assert conflicts and any(conflict["unsupported"] for conflict in conflicts)


@pytest.mark.parametrize(
    "original",
    [
        "内部员工登录后自行提交报销申请，只管理本人的申请",
        "内部员工注册登录后自行提交活动报名，仅管理本人报名记录",
        ORIGINAL + "，禁止匿名报名，参赛者登录后自行提交报名",
        ORIGINAL + "，不允许未登录用户提交报名，参赛者登录后自行提交报名",
    ],
)
def test_supported_authenticated_employee_flow_and_anonymous_prohibition_do_not_block(original):
    assert scope_conflicts([original], Selection(template="fastapiadmin").capabilities()) == []


def test_internal_employee_authenticated_submission_reaches_requirement_review(
    settings, store, plan
):
    original = "内部员工注册登录后自行提交活动报名，仅管理本人报名记录"
    requirement = Requirement(
        summary=original,
        users=["员工"],
        data_scope="shared",
        features=[original],
        acceptance=["员工只能维护本人活动报名"],
    )
    gateway = RecordingGateway(requirement, plan)
    project = store.create_project("employee entrypoint", str(uuid.uuid4()))
    run = store.create_run(
        project["id"], {"requirement": original, "template": "fastapiadmin"}, str(uuid.uuid4())
    )["run_id"]
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        current = store.get_run(run)
        assert current["status"] == "WAITING_REQUIREMENTS", current
        assert current["pending"]["can_approve"]
        assert not current["pending"]["data"].get("analysis_diagnostics")
    assert [key for key, _ in gateway.calls] == ["requirement:1"]
    assert store.messages(run) == [{"role": "user", "content": original}]


def test_old_authenticated_design_gate_replays_then_requires_new_intent_review(
    settings, store, monkeypatch
):
    """New executable checks must not invalidate a persisted old gate digest."""
    original = "参赛者注册登录后自行提交报名，仅可维护本人报名记录"
    requirement = Requirement(
        summary="竞赛报名网站",
        users=["参赛者", "管理员"],
        data_scope="shared",
        features=["参赛者登录后自行提交报名"],
        acceptance=["参赛者仅可维护本人报名记录"],
    )
    # This old design omitted the executable entrant-role grants. The new
    # checks must reject it after replay, without accepting its old approval.
    plan = Plan.model_validate(
        {
            "title": "竞赛报名网站",
            "data_scope": "shared",
            "entities": [
                {
                    "name": "registration",
                    "description": "报名记录",
                    "fields": [{"name": "title", "kind": "text", "max_length": 200}],
                }
            ],
            "acceptance": requirement.acceptance,
        }
    )
    gateway = RecordingGateway(requirement, plan)
    project = store.create_project("old authenticated gate", str(uuid.uuid4()))
    run = store.create_run(
        project["id"], {"requirement": original, "template": "fastapiadmin"}, str(uuid.uuid4())
    )["run_id"]
    monkeypatch.setattr(Workflow, "source_context", lambda *_: {"code_context": {}})
    with monkeypatch.context() as legacy:
        legacy.setattr(Workflow, "analyse", lambda *_: {"requirement": requirement.gate_dump()})
        legacy.setattr(Workflow, "capability_recovery", lambda *a, **kw: None)
        with Runtime(settings, store, gateway) as worker:
            assert worker.tick()
            decision(store, run, "approve")
            assert worker.tick()
            old = store.get_run(run)["pending"]
            assert old["stage"] == "design" and old["can_approve"]
            snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
            assert not snapshot.values.get("requirement_intent_version")
    decision(store, run, "approve")
    accepted_before_resume = approvals(store, run)
    assert len(accepted_before_resume) == 2
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        current = store.get_run(run)
        assert current["status"] == "WAITING_REQUIREMENTS", current
        assert current["pending"]["gate_id"] != old["gate_id"]
        assert current["pending"]["version"] > old["version"]
        assert approvals(store, run) == accepted_before_resume
        snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
        assert snapshot.values["requirement_intent_version"] == 1
        assert snapshot.values["plan"] == {}
        assert [key for key, _ in gateway.calls] == ["plan:1", "requirement:2"]
        decision(store, run, "approve")
        assert worker.tick()
        current = store.get_run(run)
        assert current["status"] == "WAITING_DESIGN", current
        assert current["pending"]["can_approve"] is False
        assert "registration_entrypoint" in current["pending"]["data"]["block_sources"]
    assert store.messages(run) == [{"role": "user", "content": original}]
    assert not (settings.data_dir / "runs" / run / "product").exists()


@pytest.mark.parametrize("stage", ["requirements", "design"])
@pytest.mark.parametrize("interrupted_auto_start", [False, True])
def test_legacy_ready_gate_does_not_gain_scope_approval_from_delegation(
    settings, store, monkeypatch, plan, stage, interrupted_auto_start
):
    """Both an explicit smart command and recovered automatic loop stay unapproved."""
    project = store.create_project("legacy unapproved gate", str(uuid.uuid4()))
    run = store.create_run(
        project["id"],
        {
            "requirement": ORIGINAL,
            "template": "fastapiadmin",
            "intelligent": interrupted_auto_start,
        },
        str(uuid.uuid4()),
    )["run_id"]
    legacy_plan = plan.model_copy(update={"data_scope": "shared"})
    gateway = RecordingGateway(admin_requirement(), legacy_plan)
    config = {"configurable": {"thread_id": run}}
    with monkeypatch.context() as legacy:
        legacy.setattr(Workflow, "capability_recovery", lambda *a, **kw: None)
        with Runtime(settings, store, gateway) as worker:
            # Seed the pre-upgrade checkpoint immediately before the old ready
            # node. Its ready flag is legacy model evidence, never a user decision.
            worker.graph.update_state(
                config,
                {
                    "run_id": run,
                    "template": "fastapiadmin",
                    "round": 1,
                    "attempt": 0,
                    "requirement": admin_requirement().gate_dump(),
                    "plan": legacy_plan.model_dump(),
                },
                as_node="analyse" if stage == "requirements" else "plan",
            )
            if interrupted_auto_start:
                job = store.claim()
                assert job["payload"]["action"] == "start"
                worker.graph.invoke(None, config)
                # Simulate process death after the durable interrupt but before
                # Store.finish. Recovery must not auto-approve its narrowed scope.
            else:
                assert worker.tick()
                assert store.get_run(run)["status"] == "WAITING_" + stage.upper()
            old = pending_interrupt(worker.graph.get_state(config))
            assert old["stage"] == stage and old["can_approve"] is True
            assert approvals(store, run) == []
    if not interrupted_auto_start:
        store.set_automation(run, True, "enable-smart-at-legacy-gate")
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        current = store.get_run(run)
        assert current["status"] == "BLOCKED", current
        assert current["pending"]["stage"] == "clarification"
        assert current["pending"]["gate_id"] != old["gate_id"]
        assert current["pending"]["can_approve"] is False
        assert current["pending"]["data"]["capability_conflicts"]
    assert approvals(store, run) == []
    assert gateway.calls == []
    assert store.messages(run) == [{"role": "user", "content": ORIGINAL}]
    assert not (settings.data_dir / "runs" / run / "product").exists()
````
