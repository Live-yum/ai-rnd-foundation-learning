"""Batch submission is atomic, replayable, and uses ordinary isolated runs."""

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError
from sqlalchemy import func, select

from workbench.api import create_app
from workbench.domain import BatchInput
from workbench.store import Conflict, Event, Job, Message, Project, Request, Run


def batch():
    return {
        "items": [
            {"title": "个人书架", "requirement": "  记录读书进度\n", "intelligent": False},
            {"title": "采购协作", "requirement": "采购审批与收货", "intelligent": True},
            {
                "title": "设施维护",
                "requirement": "设备与工单",
                "template": "fastapiadmin",
                "selection": {
                    "template": "fastapiadmin",
                    "backend": "fastapiadmin",
                    "frontend": "fastapiadmin-vue",
                    "database": "postgresql",
                },
            },
        ]
    }


def test_batch_is_idempotent_and_keeps_independent_run_policies(store):
    payload = batch()
    result = store.create_batch(payload, "batch-once")
    assert store.create_batch(payload, "batch-once") == result
    assert len(result["items"]) == 3
    assert len({item["run_id"] for item in result["items"]}) == 3
    assert len({item["project_id"] for item in result["items"]}) == 3
    for source, item in zip(payload["items"], result["items"], strict=True):
        run = store.get_run(item["run_id"])
        assert item["status"] == run["status"] == "QUEUED"
        assert run["auto_mode"] is source.get("intelligent", False)
        assert store.messages(run["id"])[0]["content"] == source["requirement"]
        assert run["template"] == source.get("template", "python-basic")
    with store.tx() as session:
        assert session.scalar(select(func.count()).select_from(Job)) == 3
        assert session.scalar(select(func.count()).select_from(Event)) == 1
    payload["items"][0]["requirement"] = "变更需求"
    with pytest.raises(Conflict, match="Idempotency-Key"):
        store.create_batch(payload, "batch-once")


def test_batch_failure_rolls_back_every_item_and_allows_retry(store, monkeypatch):
    enqueue = store._enqueue_run
    calls = 0

    def interrupted(session, project_id, data):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated database failure")
        return enqueue(session, project_id, data)

    monkeypatch.setattr(store, "_enqueue_run", interrupted)
    with pytest.raises(RuntimeError):
        store.create_batch(batch(), "atomic-batch")
    with store.tx() as session:
        for table in (Project, Run, Message, Job, Event, Request):
            assert session.scalar(select(func.count()).select_from(table)) == 0
    monkeypatch.setattr(store, "_enqueue_run", enqueue)
    assert len(store.create_batch(batch(), "atomic-batch")["items"]) == 3


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{"title": "x", "requirement": "y"}] * 11,
        [{"title": "x", "requirement": "   "}],
        [{"title": "x", "requirement": "y", "intelligent": "true"}],
        [{"title": "x", "requirement": "y", "approved": True}],
        [
            {
                "title": "x",
                "requirement": "y",
                "selection": {"template": "python-basic", "frontend": "vben-antd"},
            }
        ],
    ],
)
def test_batch_validates_every_item_before_mutating(store, items):
    with pytest.raises(ValidationError):
        store.create_batch({"items": items}, "invalid-batch")
    assert store.list_projects() == []


def test_batch_accepts_ten_projects():
    assert len(BatchInput(items=[{"title": "x", "requirement": "y"}] * 10).items) == 10


def test_batch_api_auth_model_configuration_and_atomic_validation(settings):
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        headers = {"Idempotency-Key": "api-batch"}
        assert client.post("/batches", json=batch(), headers=headers).status_code == 401
        client.headers["Authorization"] = "Bearer " + app.state.token
        assert client.post("/batches", json=batch(), headers=headers).status_code == 503
        assert app.state.store.list_projects() == []
        settings.base_url = "https://model.example/v1"
        settings.model = "dummy-model"
        settings.api_key = SecretStr("dummy-batch-key")
        assert client.post("/batches", json=batch()).status_code == 422
        payload = batch()
        payload["items"][1]["role"] = "system"
        assert client.post("/batches", json=payload, headers=headers).status_code == 422
        assert app.state.store.list_projects() == []
        response = client.post("/batches", json=batch(), headers=headers)
        assert response.status_code == 202
        assert client.post("/batches", json=batch(), headers=headers).json() == response.json()
        assert len(client.get("/runs").json()) == 3
