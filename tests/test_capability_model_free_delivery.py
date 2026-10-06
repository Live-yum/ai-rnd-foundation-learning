"""Final retained-candidate approvals require no model, but no planning is waived."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from workbench.api import create_app
from workbench.runtime import Runtime
from workbench.store import Job, Run


def waiting_run(store, stage):
    project = store.create_project("offline approval", "project-" + stage)
    run = store.create_run(
        project["id"], {"requirement": "测试资料保存；全部自己实现"}, "run-" + stage
    )["run_id"]
    gate = store.gate(run, stage, 1, {"requires_explicit_review": True}, ["approve", "reject"])
    with store.tx() as session:
        record = session.get(Run, run)
        record.pending = gate
        record.status = "WAITING_" + stage.upper()
    return run, gate


@pytest.mark.parametrize(
    "stage", ["delivery", "extension_scope", "extension_delivery", "extension_design"]
)
def test_api_allows_only_exact_model_free_approval_and_its_idempotent_replay(
    settings, store, stage
):
    assert settings.models_ready() is False
    run, gate = waiting_run(store, stage)
    body = {
        "action": "approve",
        "approved": True,
        "gate_id": gate["gate_id"],
        "version": gate["version"],
        "digest": gate["digest"],
    }
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "offline-approval"}
        )
        if stage == "extension_design":
            assert response.status_code == 503
            assert store.claim(only_rejections=True, include_model_free=True) is None
            return
        assert response.status_code == 202, response.text
        replay = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "offline-approval"}
        )
        assert replay.status_code == 202
        assert replay.json() == response.json()
    job = store.claim(only_rejections=True, include_model_free=True)
    assert job["id"] == response.json()["job_id"]
    assert job["payload"]["action"] == "approve"
    assert store.claim(only_rejections=True, include_model_free=True) is None


def test_model_free_admission_uses_persisted_same_run_gate_not_payload_stage(store):
    run, gate = waiting_run(store, "extension_scope")
    other, _ = waiting_run(store, "extension_design")
    body = {"action": "approve", "approved": True, "gate_id": gate["gate_id"]}
    assert store.is_model_free_approval(run, body)
    assert not store.is_model_free_approval(other, body)
    assert not store.is_model_free_approval(run, {**body, "approved": False})
    assert not store.is_model_free_approval(run, {**body, "action": "recommend"})
    with store.tx() as session:
        session.add(Job(run_id=other, payload=body))
    assert store.claim(only_rejections=True, include_model_free=True) is None


@pytest.mark.parametrize("stage", ["delivery", "extension_scope", "extension_delivery"])
def test_worker_resumes_saved_final_approval_without_model_calls(
    settings, store, monkeypatch, stage
):
    run, gate = waiting_run(store, stage)
    reply = store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "worker-offline-approval",
    )
    gateway = Mock()
    gateway.complete.side_effect = AssertionError("no model call is authorized by final approval")
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    waiting = SimpleNamespace(
        values={"run_id": run},
        next=("extension_scope",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value=gate)])],
    )
    completed = SimpleNamespace(
        values={"status": "SOURCE_READY", "delivery": {}, "last_job_id": reply["job_id"]},
        next=(),
        tasks=[],
    )
    runtime.graph = Mock()
    runtime.graph.get_state.side_effect = [waiting, completed]
    assert runtime.tick() is True
    runtime.graph.invoke.assert_called_once()
    gateway.complete.assert_not_called()
    assert store.get_run(run)["status"] == "SOURCE_READY"


def test_worker_missing_checkpoint_cannot_turn_approval_into_model_work(
    settings, store, monkeypatch
):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "missing-checkpoint",
    )
    gateway = Mock()
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    runtime.graph = Mock()
    runtime.graph.get_state.return_value = SimpleNamespace(values={}, next=(), tasks=[])
    assert runtime.tick() is True
    runtime.graph.invoke.assert_not_called()
    gateway.complete.assert_not_called()
    assert store.get_run(run)["status"] == "FAILED"


@pytest.mark.parametrize("next_node", ["extension_package", "extension_code", "waiting_scope"])
def test_offline_transient_package_retry_stays_bound_to_model_free_checkpoint(
    settings, store, monkeypatch, next_node
):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "scope-before-failure",
    )
    failed = store.claim(only_rejections=True, include_model_free=True)
    store.record_event(run, "stage", {"name": "extension_package", "phase": "failed"})
    store.finish(failed, "FAILED", error="authored transient cleanroom outage")
    assert store.get_run(run)["model_free_retry"] is True
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/retry", headers={"Idempotency-Key": "offline-package-retry"}
        )
        assert response.status_code == 202
        replay = client.post(
            f"/runs/{run}/retry", headers={"Idempotency-Key": "offline-package-retry"}
        )
        assert replay.status_code == 202
        assert replay.json() == response.json()
    gateway = Mock()
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    resume = SimpleNamespace(
        values={"run_id": run, "last_job_id": failed["id"]}, next=(next_node,), tasks=[]
    )
    if next_node == "waiting_scope":
        resume.next = ("extension_scope",)
        resume.tasks = [SimpleNamespace(interrupts=[SimpleNamespace(value=gate)])]
    completed = SimpleNamespace(
        values={"status": "SOURCE_READY", "delivery": {}}, next=(), tasks=[]
    )
    runtime.graph = Mock()
    runtime.graph.get_state.side_effect = [resume, completed]
    assert runtime.tick() is True
    gateway.complete.assert_not_called()
    if next_node == "extension_package":
        runtime.graph.invoke.assert_called_once()
        assert runtime.graph.invoke.call_args.args[0] is None
        assert store.get_run(run)["status"] == "SOURCE_READY"
    else:
        runtime.graph.invoke.assert_not_called()
        assert store.get_run(run)["status"] == "FAILED"


def test_failed_scope_approval_is_not_misclassified_as_package_retry(settings, store):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "scope-failed-before-return",
    )
    failed = store.claim(only_rejections=True, include_model_free=True)
    store.record_event(run, "stage", {"name": "extension_scope", "phase": "failed"})
    store.finish(failed, "FAILED", error="authored stale scope rejection")
    assert store.get_run(run)["model_free_retry"] is False
    assert store.is_model_free_retry(run) is False
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(f"/runs/{run}/retry", headers={"Idempotency-Key": "not-package"})
        assert response.status_code == 503
