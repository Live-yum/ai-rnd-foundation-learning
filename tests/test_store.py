import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import new_run
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from workbench.store import Conflict, Message, Project, Store


def test_migration_and_foreign_key(store):
    with store.engine.connect() as c:
        assert c.scalar(text("PRAGMA foreign_keys")) == 1
        assert c.scalar(text("SELECT version_num FROM alembic_version")) == "0001"
    with pytest.raises(IntegrityError), store.tx() as s:
        s.add(Message(run_id=str(uuid.uuid4()), role="user", content="orphan"))


def test_rollback(store):
    with pytest.raises(RuntimeError), store.tx() as s:
        s.add(Project(title="rolled back"))
        raise RuntimeError("abort")
    assert store.list_projects() == []


def test_idempotency_and_conflict(store):
    first = store.create_project("same", "key")
    assert store.create_project("same", "key") == first
    with pytest.raises(Conflict):
        store.create_project("different", "key")
    assert len(store.list_projects()) == 1


def test_concurrent_duplicate_requests(store):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store.create_project("same", "thread-key"), range(4)))
    assert len({x["id"] for x in results}) == 1


def test_persistence(settings, store):
    run_id = new_run(store)
    other = Store(settings)
    try:
        assert other.get_run(run_id)["status"] == "QUEUED"
        assert other.messages(run_id)[0]["role"] == "user"
    finally:
        other.engine.dispose()


def test_step_reuses_receipt(store):
    run = new_run(store)
    calls = []

    def fn():
        calls.append(1)
        return {"answer": 42}

    assert store.step(run, "same", fn) == store.step(run, "same", fn)
    assert len(calls) == 1


def test_gate_cannot_bypass_approval(store):
    run = new_run(store)
    gate = store.gate(run, "design", 1, {"x": 1}, ["approve", "reject"])
    with pytest.raises(Conflict):
        store.check_decision(
            run, gate, {"gate_id": gate["gate_id"], "action": "approve", "approved": True}
        )


def test_model_budget(store):
    run = new_run(store)
    for _ in range(store.settings.max_model_calls):
        store.reserve_model_call(run)
    with pytest.raises(Conflict):
        store.reserve_model_call(run)
