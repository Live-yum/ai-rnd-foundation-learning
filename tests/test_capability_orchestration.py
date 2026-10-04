"""Authored routing fixtures, never evidence of real model/sandbox acceptance."""

from pathlib import Path

import pytest

from scripts.capability_fixture import APP, GOAL, CapabilityFixture, fixture_baseline, make_plan
from workbench.capability_contracts import CapabilityEdits, custom_requested
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest
from workbench.orchestration import ExtensionDesign
from workbench.runtime import Runtime


class Gateway:
    def __init__(self, *, permission_changes=None):
        self.calls = []
        self.permission_changes = permission_changes or []
        self.coder = CapabilityFixture()

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append((key, schema.__name__))
        if schema is ExtensionDesign:
            return ExtensionDesign(
                baseline=fixture_baseline(),
                implementation=make_plan(payload),
                permission_changes=self.permission_changes,
            )
        assert schema is CapabilityEdits
        return self.coder.complete(
            run_id,
            key,
            instruction,
            {
                **payload,
                "file_manifest": {name: row["sha256"] for name, row in payload["context"].items()},
            },
            schema,
        )


def create(store, request=GOAL):
    project = store.create_project("extension fixture", "project")
    return store.create_run(project["id"], {"requirement": request, "intelligent": True}, "run")[
        "run_id"
    ]


def test_explicit_extension_reaches_code_and_preserves_candidate_on_missing_sandbox(
    settings, store, monkeypatch
):
    import workbench.capability_sandbox as sandbox

    calls = []

    def unavailable(product, *args, **kwargs):
        calls.append(str(product))
        raise UnsupportedScope("fixture: isolated execution unavailable")

    monkeypatch.setattr(sandbox, "verify_capabilities", unavailable)
    run = create(store)
    gateway = Gateway()
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        first = store.get_run(run)
        assert first["status"] == "BLOCKED", first
        assert first["pending"] is None
        assert [schema for _, schema in gateway.calls] == ["ExtensionDesign", "CapabilityEdits"]
        candidate = Path(calls[0])
        assert (candidate / "app.py").read_text() == APP
        before = manifest(candidate)
        store.retry(run, "retry-existing-candidate")
        runtime.tick()
        assert len(gateway.calls) == 2, "Retry must resume verification, not pay to regenerate"
        assert calls == [str(candidate), str(candidate)]
        assert manifest(candidate) == before
        assert not list((settings.data_dir / "runs" / run).glob("*delivery.zip"))


def test_permission_changes_cannot_be_auto_approved_or_recommended(settings, store):
    from workbench.store import Conflict

    run = create(store)
    gateway = Gateway(permission_changes=["新增团队管理员跨记录授权"])
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    saved = store.get_run(run)
    assert saved["status"] == "WAITING_EXTENSION_DESIGN"
    assert len(gateway.calls) == 1
    gate = saved["pending"]
    with pytest.raises(Conflict, match="人工审阅"):
        store.submit(
            run, {"gate_id": gate["gate_id"], "action": "recommend", "approved": True}, "no-bypass"
        )


def test_source_coverage_cannot_discard_contest_requirements(settings, store):
    request = "竞赛报名；队伍人数限制和邀请；跨校报名；随机分配评委；加权评分和盲审；教师确认；并发唯一编号；邮件SMS和云文件。全部自己实现"

    class DropsSource(Gateway):
        def complete(self, run_id, key, instruction, payload, schema):
            result = super().complete(run_id, key, instruction, payload, schema)
            result.implementation.tasks[0].requirements = ["invented-source"]
            return result

    run = create(store, request)
    gateway = DropsSource()
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    saved = store.get_run(run)
    assert saved["status"] == "BLOCKED"
    assert not any(schema == "CapabilityEdits" for _, schema in gateway.calls)
    data = saved["pending"]["data"]
    assert "加权评分和盲审" in "".join(row["text"] for row in data["source_units"])
    assert any("来源" in error for error in data["blocked"])


def test_custom_route_requires_human_intent_and_honors_later_cancellation():
    assert custom_requested(["模板不支持跨记录规则", "全部自己实现"])
    assert not custom_requested(["全部自己实现", "不要自定义实现，仅使用模板"])
    assert not custom_requested(["竞赛报名网站"])


def test_automation_endpoint_cannot_consume_explicit_extension_gate(settings, store):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from workbench.api import create_app
    from workbench.store import Conflict

    settings.base_url = "https://model.example.test/v1"
    settings.model = "authored-test-model"
    settings.api_key = SecretStr("dummy-test-only-key")
    run = create(store)
    with Runtime(settings, store, Gateway(permission_changes=["扩大数据访问权限"])) as runtime:
        runtime.tick()
    gate = store.get_run(run)["pending"]
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/automation",
            json={"enabled": True, "accepted": True},
            headers={"Idempotency-Key": "explicit-still-required"},
        )
        assert response.status_code == 202
        assert store.get_run(run)["pending"] == gate
        for change in ({"version": gate["version"] + 1}, {"digest": "0" * 64}):
            response = client.post(
                f"/runs/{run}/resume",
                json={"gate_id": gate["gate_id"], "action": "approve", "approved": True, **change},
                headers={"Idempotency-Key": "stale-" + next(iter(change))},
            )
            assert response.status_code == 409
        body = {
            "gate_id": gate["gate_id"],
            "action": "approve",
            "approved": True,
            "version": gate["version"],
            "digest": gate["digest"],
        }
        first = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "current-approval"}
        )
        assert first.status_code == 202
        replay = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "current-approval"}
        )
        assert replay.json() == first.json()
    with pytest.raises(Conflict):
        store.auto_approve(run, gate)
