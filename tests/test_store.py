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
        assert c.scalar(text("SELECT version_num FROM alembic_version")) == "0002"
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
    from workbench.errors import PausedLimit

    store.settings.max_model_calls = 2
    run = new_run(store)
    for _ in range(store.settings.max_model_calls):
        store.reserve_model_call(run)
    with pytest.raises(PausedLimit):
        store.reserve_model_call(run)


def test_run_pagination_and_project_history_are_independent(store):
    from workbench.store import Run

    older = store.create_project("older", "older-project")
    newer = store.create_project("newer", "newer-project")
    with store.tx() as session:
        session.add(
            Run(
                id="old-run",
                project_id=older["id"],
                template="python-basic",
                status="WAITING_EXTENSION_DELIVERY",
            )
        )
        session.flush()
        for index in range(105):
            session.add(
                Run(
                    id=f"new-{index:03}",
                    project_id=newer["id"],
                    template="python-basic",
                    status="READY",
                )
            )
    first = store.list_runs(limit=100)
    second = store.list_runs(limit=100, offset=100)
    assert len(first) == 100 and len(second) == 6
    assert not {row["id"] for row in first} & {row["id"] for row in second}
    assert store.list_runs(older["id"])[0]["id"] == "old-run"
    assert store.list_runs(statuses=["WAITING_EXTENSION_DELIVERY"])[0]["id"] == "old-run"


def test_model_capabilities_are_server_owned_even_for_saved_gates(store):
    run = new_run(store)
    gate = store.gate(run, "delivery", 1, {}, ["approve", "reject"])
    assert gate["needs_model"] == {"approve": False, "reject": False}
    from workbench.store import Run

    with store.tx() as session:
        record = session.get(Run, run)
        record.pending = {key: value for key, value in gate.items() if key != "needs_model"}
    assert store.get_run(run)["pending"]["needs_model"] == gate["needs_model"]
