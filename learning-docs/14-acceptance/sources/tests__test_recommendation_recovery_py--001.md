# tests/test_recommendation_recovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.cli`、`workbench.domain`、`workbench.flow`、`workbench.llm`、`workbench.recommendation`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `news_requirement`（L29–L41）：接收`stale`。 调用`Requirement`、`news_plan`。 返回路径：L30的`Requirement( summary="游戏资讯的个人管理页面", users=["登录用户"], data_scope="per_user", features=["标题与正…`。
- `start_news`（L44–L50）：接收`store`、`smart`。 调用`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`。 返回路径：L46的`store.create_run( project["id"], {"requirement": "游戏资讯", "template": "python-basic", "inte…`。
- `test_limitations_are_advisory_but_unsupported_still_blocks`（L53–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L55断言`ready.ready`；L56断言`ready.limitations == LIMITATIONS`；L57断言`not ready.model_copy(update={"unsupported": ["用户明确要求自动采集"]}).ready`；L58断言`not ready.model_copy(update={"questions": [QUESTION]}).ready`。 调用`news_requirement`、`ready.model_copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_gate_digest_does_not_change_for_empty_optional_fields`（L61–L75）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L72断言`reconstructed.gate_dump() == old`；L73断言`digest({"requirement": old, "ready": True}) == digest( {"requirement": reconstructed.…`。 调用`requirement().model_dump`、`requirement`、`Requirement.model_validate`、`reconstructed.gate_dump`、`digest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_news_http_model_protocol_through_real_clean_delivery`（L79–L130）：接收`settings`、`store`、`initial_smart`。 控制顺序：L117断言`worker.tick()`；L118按`not initial_smart`分支；L119断言`store.get_run(run)["status"] == "WAITING_CLARIFICATION"`；L121断言`worker.tick()`；L123断言`state["status"] == "READY"`；L124断言`state["pending"] is None and state["error"] is None`；L125断言`state["options"]["database"] == "sqlite"`；L126断言`state["options"]["frontend"] == "simple-admin"`。后续分支沿下方源码相同行号继续阅读。 调用`SecretStr`、`start_news`、`ModelGateway`、`httpx.MockTransport`、`Runtime`、`worker.tick`、`store.get_run`、`store.set_automation`、`(settings.data_dir / "runs" / run / "delivery.zip").is_file`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_news_http_model_protocol_through_real_clean_delivery.handler`（L85–L112）：接收`request`。 控制顺序：L90按`"approved_requirement" in payload`分支；L92断言`approved["unsupported"] == []`；L93断言`approved["limitations"] == LIMITATIONS`；L94断言`approved["facts"]["分类是否必填"] == "否"`；L96按`not payload["autonomous"]`分支；L99断言`payload["original_request"] == "游戏资讯"`；L100断言`"禁止把 template_capabilities.not_supported" in instruction`；L101断言`"用户明确要求采集或公开访问时" in instruction`。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`seen.append`、`news_plan`、`news_requirement`、`httpx.Response`、`result.model_dump_json`。 返回路径：L107的`httpx.Response( 200, json={ "choices": [{"message": {"role": "assistant", "content": resul…`。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run`（L133–L180）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L161断言`blocked["status"] == "BLOCKED"`；L162断言`blocked["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS`；L163断言`"limitations" not in blocked["pending"]["data"]["requirement"]`；L178断言`state["status"] == "READY"`；L179断言`state["result"]["cleanroom"]["passed"] is True`；L180断言`len(store.messages(run)) == 1`。 调用`start_news`、`monkeypatch.context`、`patch.setattr`、`Runtime`、`Stale`、`news_plan`、`worker.tick`、`store.get_run`、`store.set_automation`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run.old_requirements`（L135–L147）：接收`state`。 控制顺序：L145按`outcome["decision"] in {"answer", "revise", "recommend"}`分支。 调用`dict`、`raw.pop`、`self.gate`。 返回路径：L147的`outcome`。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run.Stale`（L149–L153）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run.Stale.complete`（L150–L153）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L152断言`schema is Requirement`。 调用`self.calls.append`、`news_requirement`。 返回路径：L153的`news_requirement(stale=True)`。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run.Fixed`（L165–L171）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_existing_legacy_blocked_checkpoint_recovers_same_run.Fixed.complete`（L166–L171）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L167按`schema is Requirement`分支；L168断言`rid == run`；L169断言`payload["resolution_feedback"]["unsupported"] == LIMITATIONS`。 调用`news_requirement`、`super().complete`、`super`。 返回路径：L170的`news_requirement()`；L171的`super().complete(rid, key, instruction, payload, schema)`。
- `test_design_recommendation_receives_blockers_without_reanalysing_approved_scope`（L183–L206）：接收`settings`、`store`、`plan`。 控制顺序：L205断言`store.get_run(run)["status"] == "READY"`；L206断言`gateway.calls == ["recommend:1", "plan:1", "plan:2"]`。 调用`new_run`、`Repair`、`store.set_automation`、`Runtime`、`worker.tick`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_design_recommendation_receives_blockers_without_reanalysing_approved_scope.Repair`（L186–L198）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_design_recommendation_receives_blockers_without_reanalysing_approved_scope.Repair.complete`（L187–L198）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L188按`schema is Plan`分支；L190按`key == "plan:1"`分支；L192断言`payload["approved_requirement"]["data_scope"] == "per_user"`；L193断言`payload["previous_plan"]["data_scope"] == "shared"`；L194断言`payload["resolution_feedback"]["stage"] == "design"`；L195断言`any("数据归属" in x for x in payload["resolution_feedback"]["blocked"])`；L196断言`payload["runtime_constraints"]["coding_enabled"] is True`。 调用`self.calls.append`、`plan.model_copy`、`any`、`super().complete`、`super`。 返回路径：L191的`plan.model_copy(update={"data_scope": "shared"})`；L197的`plan`；L198的`super().complete(run, key, instruction, payload, schema)`。
- `test_explicit_unsupported_request_remains_blocked_with_actionable_report`（L210–L239）：接收`settings`、`store`、`plan`、`requested`。 控制顺序：L227断言`state["status"] == "BLOCKED"`；L228断言`requested in state["error"]`；L229断言`state["pending"]["can_approve"] is False`；L230断言`len(gateway.calls) == 3`；L236断言`report["reasons"] == [requested] and report["passed"] is False`；L237断言`not (settings.data_dir / "runs" / run / "delivery.zip").exists()`。 调用`store.create_project`、`store.create_run`、`Unsupported`、`Runtime`、`worker.tick`、`store.get_run`、`len`、`json.loads`、`(settings.data_dir / "runs" / run / "recommendation-blocked.json"…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_unsupported_request_remains_blocked_with_actionable_report.Unsupported`（L213–L217）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_explicit_unsupported_request_remains_blocked_with_actionable_report.Unsupported.complete`（L214–L217）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L216断言`schema is Requirement`。 调用`self.calls.append`、`requirement().model_copy`、`requirement`。 返回路径：L217的`requirement().model_copy(update={"unsupported": [requested]})`。
- `test_blocked_manual_and_retry_keep_saved_gate_and_clear_stale_error`（L242–L273）：接收`settings`、`store`、`plan`。 控制顺序：L252断言`state["status"] == "BLOCKED"`；L255断言`store.get_run(run)["pending"] is None`；L263断言`store.get_run(run)["status"] == "WAITING_CLARIFICATION"`；L264断言`pending_interrupt(worker.graph.get_state({"configurable": {"thread_id": run}}))[ "gat…`；L272断言`store.get_run(run)["status"] == "WAITING_REQUIREMENTS"`；L273断言`store.get_run(run)["error"] is None`。 调用`new_run`、`store.set_automation`、`Runtime`、`Unresolved`、`worker.tick`、`store.get_run`、`store.retry`、`pytest.raises`、`store.submit`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_blocked_manual_and_retry_keep_saved_gate_and_clear_stale_error.Unresolved`（L243–L245）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_blocked_manual_and_retry_keep_saved_gate_and_clear_stale_error.Unresolved.complete`（L244–L245）：接收`*args`。 调用`requirement`。 返回路径：L245的`requirement(["仍未决定"])`。
- `test_manual_switch_on_blocked_restores_visible_waiting_gate`（L276–L289）：接收`settings`、`store`、`plan`。 控制顺序：L288断言`state["status"] == "WAITING_CLARIFICATION"`；L289断言`state["pending"] == pending and state["error"] is None`。 调用`new_run`、`store.set_automation`、`Runtime`、`Unresolved`、`worker.tick`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manual_switch_on_blocked_restores_visible_waiting_gate.Unresolved`（L277–L279）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_manual_switch_on_blocked_restores_visible_waiting_gate.Unresolved.complete`（L278–L279）：接收`*args`。 调用`requirement`。 返回路径：L279的`requirement(["仍未决定"])`。
- `test_question_only_pause_is_not_misreported_as_unsupported_scope`（L292–L302）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L301断言`report["reasons"] == ["尚未自动决定：" + QUESTION]`；L302断言`report["recoverable"] and not report["can_approve"]`。 调用`blocked_report`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recovery_control_words_never_become_model_answers`（L306–L308）：接收`word`。 调用`pytest.raises`、`ResumeInput`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chat_run_can_operate_on_existing_blocked_gate`（L312–L361）：接收`monkeypatch`、`command`。 控制顺序：L345断言`result.exit_code == 0`；L346断言`LIMITATIONS[0] in result.output`；L348按`command == "退出"`分支；L349断言`writes == []`；L351断言`len(writes) == 1`；L352断言`writes[0][1].startswith(f"/runs/{run}/")`；L353按`command == "智能推荐"`分支；L354断言`writes[0][2] == {"enabled": True, "accepted": True}`。后续分支沿下方源码相同行号继续阅读。 调用`str`、`uuid.uuid4`、`monkeypatch.setattr`、`CliRunner().invoke`、`CliRunner`、`len`、`writes[0][1].startswith`、`writes[0][1].endswith`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chat_run_can_operate_on_existing_blocked_gate.client`（L327–L328）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`object`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_chat_run_can_operate_on_existing_blocked_gate.api_call`（L330–L340）：接收`c`、`method`、`path`、`body`。 控制顺序：L333按`method == "GET"`分支。 调用`calls.append`。 返回路径：L334的`{ "status": status, "error": "可恢复的阻塞", "pending": gate if status == "BLOCKED" else None, }`；L340的`{}`。
- `test_cache_binds_prompt_payload_and_schema_but_reuses_exact_replay`（L364–L395）：接收`settings`、`store`。 控制顺序：L385断言`len(sent) == 1`；L388断言`len(sent) == 3`；L389断言`store.get_run(run)["model_calls"] == 3`；L395断言`len(sent) == 4`。 调用`SecretStr`、`new_run`、`ModelGateway`、`httpx.MockTransport`、`gateway.complete`、`len`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cache_binds_prompt_payload_and_schema_but_reuses_exact_replay.handler`（L370–L379）：接收`request`。 调用`sent.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L372的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_cache_binds_prompt_payload_and_schema_but_reuses_exact_replay.ExtendedRequirement`（L391–L392）：继承`Requirement`。声明的数据项为`schema_revision_note`；类型约束/数据库列参数以完整定义为准。
- `test_smart_recovery_never_overrides_failed_independent_verification`（L398–L411）：接收`settings`、`store`、`plan`、`monkeypatch`。 控制顺序：L409断言`state["status"] == "FAILED"`；L410断言`"真实验收失败" in state["error"]`；L411断言`not (settings.data_dir / "runs" / run / "delivery.zip").exists()`。 调用`monkeypatch.setattr`、`new_run`、`store.set_automation`、`Runtime`、`FixtureGateway`、`worker.tick`、`store.get_run`、`(settings.data_dir / "runs" / run / "delivery.zip").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_recommendation_recovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L411。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16531`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_recommendation_recovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f58f0246ebcfb7cdd2706ebc9b3eeaba16195e7edc55a9398a210e2410ac9e84"} -->
````python
# tests/test_recommendation_recovery.py
"""Reported smart-news dead end: real graph/storage/product, explicit model fixtures."""

import json
import uuid
from contextlib import contextmanager

import httpx
import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from news_case import news_plan
from pydantic import SecretStr, ValidationError
from typer.testing import CliRunner

from workbench.cli import app
from workbench.domain import Plan, Requirement, ResumeInput, digest
from workbench.flow import Workflow
from workbench.llm import ModelGateway
from workbench.recommendation import blocked_report
from workbench.runtime import Runtime, pending_interrupt
from workbench.store import Conflict

LIMITATIONS = [
    "自动从外部网站采集游戏资讯不受当前模板支持",
    "面向无需登录的公众开放浏览不受当前模板支持",
]
QUESTION = "需要个人资讯管理页面，还是无需登录的公众资讯网站？"


def news_requirement(*, stale=False):
    return Requirement(
        summary="游戏资讯的个人管理页面",
        users=["登录用户"],
        data_scope="per_user",
        features=["标题与正文必填", "发布日期", "分类可选", "资讯增删改查", "关键词和组合筛选"],
        acceptance=news_plan().acceptance,
        questions=[QUESTION] if stale else [],
        unsupported=LIMITATIONS if stale else [],
        limitations=[] if stale else LIMITATIONS,
        recommendations=[] if stale else ["未要求采集或公众浏览，采用登录后个人录入管理"],
        facts={"标题长度上限": "250字符", "正文长度上限": "3000字符", "分类是否必填": "否"},
    )


def start_news(store, smart=False):
    project = store.create_project("游戏小助手", str(uuid.uuid4()))
    return store.create_run(
        project["id"],
        {"requirement": "游戏资讯", "template": "python-basic", "intelligent": smart},
        str(uuid.uuid4()),
    )["run_id"]


def test_limitations_are_advisory_but_unsupported_still_blocks():
    ready = news_requirement()
    assert ready.ready
    assert ready.limitations == LIMITATIONS
    assert not ready.model_copy(update={"unsupported": ["用户明确要求自动采集"]}).ready
    assert not ready.model_copy(update={"questions": [QUESTION]}).ready


def test_legacy_gate_digest_does_not_change_for_empty_optional_fields():
    old = requirement().model_dump(
        exclude={
            "limitations",
            "field_requirements",
            "entity_requirements",
            "additional_entities",
            "changes",
        }
    )
    reconstructed = Requirement.model_validate(old)
    assert reconstructed.gate_dump() == old
    assert digest({"requirement": old, "ready": True}) == digest(
        {"requirement": reconstructed.gate_dump(), "ready": reconstructed.ready}
    )


@pytest.mark.parametrize("initial_smart", [False, True])
def test_news_http_model_protocol_through_real_clean_delivery(settings, store, initial_smart):
    settings.base_url = "https://fixture.example/v1"
    settings.api_key = SecretStr("test-not-a-real-key")
    settings.model = "fixture"
    seen = []

    def handler(request):
        body = json.loads(request.content)
        payload = json.loads(body["messages"][1]["content"])
        instruction = body["messages"][0]["content"]
        seen.append(payload)
        if "approved_requirement" in payload:
            approved = payload["approved_requirement"]
            assert approved["unsupported"] == []
            assert approved["limitations"] == LIMITATIONS
            assert approved["facts"]["分类是否必填"] == "否"
            result = news_plan()
        elif not payload["autonomous"]:
            result = news_requirement(stale=True)
        else:
            assert payload["original_request"] == "游戏资讯"
            assert "禁止把 template_capabilities.not_supported" in instruction
            assert "用户明确要求采集或公开访问时" in instruction
            if not initial_smart:
                feedback = payload["resolution_feedback"]
                assert feedback["unsupported"] == LIMITATIONS
                assert feedback["questions"] == [QUESTION]
            result = news_requirement()
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"role": "assistant", "content": result.model_dump_json()}}]
            },
        )

    run = start_news(store, initial_smart)
    gateway = ModelGateway(settings, store, httpx.MockTransport(handler))
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        if not initial_smart:
            assert store.get_run(run)["status"] == "WAITING_CLARIFICATION"
            store.set_automation(run, True, "authorize-once")
            assert worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["pending"] is None and state["error"] is None
    assert state["options"]["database"] == "sqlite"
    assert state["options"]["frontend"] == "simple-admin"
    assert state["result"]["cleanroom"]["passed"] is True
    assert (settings.data_dir / "runs" / run / "delivery.zip").is_file()
    assert len(seen) == (2 if initial_smart else 3)
    assert [m["content"] for m in store.messages(run)] == ["游戏资讯"]


def test_existing_legacy_blocked_checkpoint_recovers_same_run(settings, store, monkeypatch):
    # This node writes the pre-fix requirement gate format and no resolution feedback.
    def old_requirements(self, state):
        raw = dict(state["requirement"])
        raw.pop("limitations", None)
        outcome = self.gate(
            state,
            "clarification",
            {"requirement": raw, "ready": False},
            ["answer", "reject"],
            False,
        )
        if outcome["decision"] in {"answer", "revise", "recommend"}:
            outcome["round"] = state["round"] + 1
        return outcome

    class Stale(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement
            return news_requirement(stale=True)

    run = start_news(store, True)
    with monkeypatch.context() as patch:
        patch.setattr(Workflow, "requirements", old_requirements)
        with Runtime(settings, store, Stale(news_plan())) as worker:
            worker.tick()
    blocked = store.get_run(run)
    assert blocked["status"] == "BLOCKED", blocked
    assert blocked["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS
    assert "limitations" not in blocked["pending"]["data"]["requirement"]

    class Fixed(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            if schema is Requirement:
                assert rid == run
                assert payload["resolution_feedback"]["unsupported"] == LIMITATIONS
                return news_requirement()
            return super().complete(rid, key, instruction, payload, schema)

    # Reload persistent worker/checkpoints and explicitly resume; never create a new run.
    store.set_automation(run, True, "resume-old-block")
    with Runtime(settings, store, Fixed(news_plan())) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["result"]["cleanroom"]["passed"] is True
    assert len(store.messages(run)) == 1


def test_design_recommendation_receives_blockers_without_reanalysing_approved_scope(
    settings, store, plan
):
    class Repair(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is Plan:
                self.calls.append(key)
                if key == "plan:1":
                    return plan.model_copy(update={"data_scope": "shared"})
                assert payload["approved_requirement"]["data_scope"] == "per_user"
                assert payload["previous_plan"]["data_scope"] == "shared"
                assert payload["resolution_feedback"]["stage"] == "design"
                assert any("数据归属" in x for x in payload["resolution_feedback"]["blocked"])
                assert payload["runtime_constraints"]["coding_enabled"] is True
                return plan
            return super().complete(run, key, instruction, payload, schema)

    run = new_run(store)
    gateway = Repair(plan)
    store.set_automation(run, True, "smart")
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "READY", store.get_run(run)
    assert gateway.calls == ["recommend:1", "plan:1", "plan:2"]


@pytest.mark.parametrize("requested", ["必须自动采集外部网站资讯", "必须向未登录公众开放浏览"])
def test_explicit_unsupported_request_remains_blocked_with_actionable_report(
    settings, store, plan, requested
):
    class Unsupported(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement
            return requirement().model_copy(update={"unsupported": [requested]})

    project = store.create_project("unsupported", "project")
    run = store.create_run(project["id"], {"requirement": requested, "intelligent": True}, "run")[
        "run_id"
    ]
    gateway = Unsupported(plan)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "BLOCKED", state
    assert requested in state["error"]
    assert state["pending"]["can_approve"] is False
    assert len(gateway.calls) == 3
    report = json.loads(
        (settings.data_dir / "runs" / run / "recommendation-blocked.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["reasons"] == [requested] and report["passed"] is False
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()
    with pytest.raises(Conflict):
        decision(store, run)


def test_blocked_manual_and_retry_keep_saved_gate_and_clear_stale_error(settings, store, plan):
    class Unresolved(FixtureGateway):
        def complete(self, *args):
            return requirement(["仍未决定"])

    run = new_run(store)
    store.set_automation(run, True, "smart")
    with Runtime(settings, store, Unresolved(plan)) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "BLOCKED"
    gate = state["pending"]
    store.retry(run, "retry")
    assert store.get_run(run)["pending"] is None
    with pytest.raises(Conflict):
        store.submit(
            run, {"gate_id": gate["gate_id"], "action": "answer", "text": "stale"}, "stale"
        )
    store.set_automation(run, False, "manual")
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_CLARIFICATION"
        assert (
            pending_interrupt(worker.graph.get_state({"configurable": {"thread_id": run}}))[
                "gate_id"
            ]
            == gate["gate_id"]
        )
        decision(store, run, "answer", "保留原需求，按模板支持的默认细节继续")
        worker.tick()
    assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
    assert store.get_run(run)["error"] is None


def test_manual_switch_on_blocked_restores_visible_waiting_gate(settings, store, plan):
    class Unresolved(FixtureGateway):
        def complete(self, *args):
            return requirement(["仍未决定"])

    run = new_run(store)
    store.set_automation(run, True, "smart")
    with Runtime(settings, store, Unresolved(plan)) as worker:
        worker.tick()
    pending = store.get_run(run)["pending"]
    store.set_automation(run, False, "manual")
    state = store.get_run(run)
    assert state["status"] == "WAITING_CLARIFICATION"
    assert state["pending"] == pending and state["error"] is None


def test_question_only_pause_is_not_misreported_as_unsupported_scope():
    report = blocked_report(
        {
            "stage": "clarification",
            "gate_id": "a" * 64,
            "data": {"requirement": {"questions": [QUESTION]}},
        },
        2,
    )
    assert report["reasons"] == ["尚未自动决定：" + QUESTION]
    assert report["recoverable"] and not report["can_approve"]


@pytest.mark.parametrize("word", ["手动", "manual", "重试", "retry", "退出", "quit", "exit"])
def test_recovery_control_words_never_become_model_answers(word):
    with pytest.raises(ValidationError, match="控制指令"):
        ResumeInput(gate_id="a" * 64, action="answer", text=word)


@pytest.mark.parametrize("command", ["智能推荐", "重试", "手动", "退出", "只需个人录入管理"])
def test_chat_run_can_operate_on_existing_blocked_gate(monkeypatch, command):
    import workbench.cli as cli

    run = str(uuid.uuid4())
    calls = []
    status = "BLOCKED"
    gate = {
        "stage": "clarification",
        "gate_id": "a" * 64,
        "can_approve": False,
        "actions": ["answer", "reject", "recommend"],
        "data": {"requirement": {"unsupported": LIMITATIONS}},
    }

    @contextmanager
    def client():
        yield object()

    def api_call(c, method, path, body=None):
        nonlocal status
        calls.append((method, path, body))
        if method == "GET":
            return {
                "status": status,
                "error": "可恢复的阻塞",
                "pending": gate if status == "BLOCKED" else None,
            }
        status = "READY"  # CLI boundary fixture only; actual product tested above.
        return {}

    monkeypatch.setattr(cli, "client", client)
    monkeypatch.setattr(cli, "api_call", api_call)
    result = CliRunner().invoke(app, ["chat", "--run", run], input=command + "\n")
    assert result.exit_code == 0, result.output
    assert LIMITATIONS[0] in result.output
    writes = [call for call in calls if call[0] == "POST"]
    if command == "退出":
        assert writes == []
    else:
        assert len(writes) == 1
        assert writes[0][1].startswith(f"/runs/{run}/")
        if command == "智能推荐":
            assert writes[0][2] == {"enabled": True, "accepted": True}
        elif command == "手动":
            assert writes[0][2] == {"enabled": False, "accepted": False}
        elif command == "重试":
            assert writes[0][1].endswith("/retry")
        else:
            assert writes[0][2]["text"] == command
    assert not any("/projects" in call[1] for call in calls)


def test_cache_binds_prompt_payload_and_schema_but_reuses_exact_replay(settings, store):
    settings.base_url = "https://fixture.example/v1"
    settings.api_key = SecretStr("not-a-real-key")
    settings.model = "fixture"
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": requirement().model_dump_json()}}
                ]
            },
        )

    run = new_run(store)
    gateway = ModelGateway(settings, store, httpx.MockTransport(handler))
    gateway.complete(run, "recommend:1", "old prompt", {}, Requirement)
    gateway.complete(run, "recommend:1", "old prompt", {}, Requirement)
    assert len(sent) == 1
    gateway.complete(run, "recommend:1", "fixed prompt", {}, Requirement)
    gateway.complete(run, "recommend:1", "fixed prompt", {"feedback": "new"}, Requirement)
    assert len(sent) == 3
    assert store.get_run(run)["model_calls"] == 3

    class ExtendedRequirement(Requirement):
        schema_revision_note: str = ""

    gateway.complete(run, "recommend:1", "fixed prompt", {"feedback": "new"}, ExtendedRequirement)
    assert len(sent) == 4


def test_smart_recovery_never_overrides_failed_independent_verification(
    settings, store, plan, monkeypatch
):
    monkeypatch.setattr(
        "workbench.flow.verify_basic", lambda *args: {"passed": False, "error": "真实验收失败"}
    )
    run = new_run(store)
    store.set_automation(run, True, "smart")
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "FAILED"
    assert "真实验收失败" in state["error"]
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()
````
