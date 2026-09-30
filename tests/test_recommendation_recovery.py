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
    old = requirement().model_dump(exclude={"limitations"})
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
            200, json={"choices": [{"message": {"content": result.model_dump_json()}}]}
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
            200, json={"choices": [{"message": {"content": requirement().model_dump_json()}}]}
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
