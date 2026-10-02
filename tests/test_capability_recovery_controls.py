"""A known scope decision cannot be delegated away by retrying the same gate."""

from contextlib import contextmanager

import pytest
from conftest import new_run, requirement
from typer.testing import CliRunner

from workbench import cli
from workbench.recommendation import blocked_report
from workbench.store import Conflict


def gate_data():
    return {
        "requirement": requirement(["请明确参与者入口与报名范围"]).gate_dump(),
        "ready": False,
        "blocked": ["参与者自行提交不能自动改为管理员录入"],
        "capability_conflicts": [
            {
                "code": "registration_scope_confirmation",
                "message": "参与者自行提交不能自动改为管理员录入",
                "alternatives": ["明确参与者登录后的操作", "明确仅需管理员维护"],
            }
        ],
    }


def test_known_scope_gate_keeps_identity_and_does_not_queue_recommendation(settings, store):
    run = new_run(store)
    job = store.claim()
    gate = store.gate(run, "clarification", 4, gate_data(), ["answer", "reject"], False)
    store.finish(job, "BLOCKED", pending=gate, error="需要范围选择")
    before = store.messages(run)
    for index in range(3):
        result = store.set_automation(run, True, f"repeat-smart-{index}")
        assert result["status"] == "BLOCKED"
        assert "未发起新的模型请求" in result["message"]
        assert store.claim() is None
        assert store.get_run(run)["pending"] == gate
        assert store.messages(run) == before
    with pytest.raises(Conflict, match="范围选择"):
        store.submit(
            run,
            {"gate_id": gate["gate_id"], "action": "recommend", "approved": True},
            "direct-recommend",
        )
    with pytest.raises(Conflict, match="范围选择"):
        store.retry(run, "repeat-retry")
    assert store.claim() is None
    answer = "保留参赛者自行提交的目标，需要登录后的参赛者入口，不要求匿名访问"
    store.submit(run, {"gate_id": gate["gate_id"], "action": "answer", "text": answer}, "scope")
    assert store.messages(run)[-1]["content"] == answer
    assert store.claim()["payload"]["gate_id"] == gate["gate_id"]


def test_scope_report_explains_paths_without_claiming_retry_can_fix_capabilities():
    report = blocked_report({"stage": "clarification", "gate_id": "a" * 64, "data": gate_data()}, 0)
    assert report["attempts"] == 0
    assert report["retry_without_changes"] is False
    assert report["alternatives"] == ["明确参与者登录后的操作", "明确仅需管理员维护"]
    assert not report["can_approve"]


def test_cli_does_not_resubmit_known_scope_for_smart_or_retry(monkeypatch):
    calls = []
    status = "BLOCKED"
    gate = {
        "stage": "clarification",
        "gate_id": "a" * 64,
        "can_approve": False,
        "actions": ["answer", "reject", "recommend"],
        "data": gate_data(),
    }

    @contextmanager
    def client():
        yield object()

    def api_call(client, method, path, body=None):
        nonlocal status
        calls.append((method, path, body))
        if method == "GET":
            return {"status": status, "error": "需要范围选择", "pending": gate}
        status = "READY"
        return {}

    monkeypatch.setattr(cli, "client", client)
    monkeypatch.setattr(cli, "api_call", api_call)
    answer = "保留自行报名，先讨论登录后的参赛者入口"
    result = CliRunner().invoke(
        cli.app, ["chat", "--run", "old-run"], input=f"智能推荐\n重试\n{answer}\n"
    )
    assert result.exit_code == 0, result.output
    assert "原始目标已保留" in result.output
    assert "未发送新的模型请求" in result.output
    writes = [call for call in calls if call[0] == "POST"]
    assert writes == [
        ("POST", "/runs/old-run/resume", {"gate_id": "a" * 64, "action": "answer", "text": answer})
    ]
