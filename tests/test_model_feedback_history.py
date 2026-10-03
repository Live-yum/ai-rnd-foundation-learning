"""Provider failures and gate history remain actionable without exposing raw responses."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from workbench.domain import ModelReview
from workbench.llm import ModelFailure, ModelGateway
from workbench.store import Store


def test_failed_schema_has_safe_paths_trace_attempt_and_no_provider_values(store):
    run = new_run(store)
    store.settings.base_url = "https://api.openai.com/v1"
    store.settings.model = "offline"
    store.settings.api_key = SecretStr("secret-fixture-value")

    def handler(request):
        # Both arbitrary extra-field names and invalid values are private.
        return httpx.Response(
            200,
            json={
                "id": "fixture",
                "model": "offline",
                "object": "chat.completion",
                "created": 0,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(
                                {"summary": 123, "secret-fixture-value": "private-response-canary"}
                            ),
                        },
                    }
                ],
            },
        )

    gateway = ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True)
    with pytest.raises(ModelFailure):
        gateway.complete(run, "review:diagnostic", "JSON", {}, ModelReview)
    messages = store.transcript(run)["messages"]
    failed = [item for item in messages if item.get("validation") == "failed"]
    assert len(failed) == 2
    assert [item["diagnostic"]["attempt"] for item in failed] == [1, 2]
    for item in failed:
        assert item["content"] == ""
        diagnostic = item["diagnostic"]
        assert diagnostic["trace_id"] == item["response_id"]
        assert diagnostic["phase"] == "response_validation"
        assert diagnostic["retry_hint"]
        assert any(
            item["path"] == ["summary"] and item["type"] == "string_type"
            for item in diagnostic["details"]
        )
    safe = json.dumps(messages)
    assert "secret-fixture-value" not in safe
    assert "private-response-canary" not in safe
    assert not any(item.get("validation") == "validated" for item in messages)


def test_gate_questions_choices_gaps_and_exact_answer_survive_submit_failure_and_restart(store):
    run = new_run(store)
    gate = store.gate(
        run,
        "clarification",
        1,
        {
            "requirement": {
                "questions": ["参与者将通过哪种入口报名？"],
                "question_items": [
                    {
                        "id": "registration_scope",
                        "prompt": "参与者将通过哪种入口报名？",
                        "options": [{"id": "authenticated", "label": "登录后报名"}],
                    }
                ],
                "unsupported": ["模板不支持匿名公开报名页"],
            },
            "capability_conflicts": [
                {"message": "原始报名目标需要明确入口", "alternatives": ["已认证业务入口"]}
            ],
        },
        ["answer"],
        can_approve=False,
    )
    job = store.claim()
    store.finish(job, "WAITING_CLARIFICATION", pending=gate)
    answer = "参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录"
    payload = {"gate_id": gate["gate_id"], "action": "answer", "text": answer}
    first = store.submit(run, payload, "answer-once")
    assert store.submit(run, payload, "answer-once") == first
    job = store.claim()
    store.finish(job, "FAILED", error="结构化响应未通过校验")
    restored = Store(store.settings)
    try:
        messages = restored.transcript(run)["messages"]
        historical = [item for item in messages if item.get("validation") == "historical_gate"]
        assert len(historical) == 1
        text = historical[0]["content"]
        for expected in [
            "参与者将通过哪种入口报名？",
            "登录后报名",
            "模板不支持匿名公开报名页",
            "原始报名目标需要明确入口",
            "已认证业务入口",
        ]:
            assert expected in text
        assert sum(item["content"] == answer for item in messages) == 1
        assert messages.index(historical[0]) < next(
            index for index, item in enumerate(messages) if item["content"] == answer
        )
        assert restored.get_run(run)["pending"] is None
        assert "不代表当前仍未解决" in text
        assert (
            len(restored.messages(run)) == 2
        )  # Historical model questions never become human facts.
    finally:
        restored.engine.dispose()


def test_root_schema_failure_reports_only_allowlisted_validator_message():
    from pydantic import ValidationError

    from workbench.domain import Requirement
    from workbench.model_diagnostics import schema_diagnostics

    value = {
        "summary": "报名",
        "users": ["参赛者"],
        "data_scope": "per_user",
        "features": ["报名"],
        "acceptance": [],
        "questions": ["已回答的问题"],
        "question_items": [{"id": "scope", "prompt": "另一个问题", "kind": "text"}],
    }
    with pytest.raises(ValidationError) as error:
        Requirement.model_validate(value)
    details = schema_diagnostics(error.value, Requirement)
    assert details[0]["message"] == "结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题"
    assert details[0]["path"] == []
