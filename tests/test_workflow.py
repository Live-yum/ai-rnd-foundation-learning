import uuid

import pytest
from conftest import FixtureGateway, decision, new_run
from filelock import Timeout

from workbench.domain import CustomRule
from workbench.runtime import Runtime
from workbench.store import Conflict


def test_complete_default_flow(settings, store, plan):
    run = new_run(store)
    gateway = FixtureGateway(plan)
    with Runtime(settings, store, gateway) as worker:
        for stage in ("REQUIREMENTS", "DESIGN", "DELIVERY"):
            assert worker.tick()
            assert store.get_run(run)["status"] == "WAITING_" + stage
            decision(store, run)
        worker.tick()
    result = store.get_run(run)
    assert result["status"] == "READY", result
    assert result["result"]["cleanroom"]["passed"] is True
    assert result["result"]["cleanroom"]["restart"] is True
    assert gateway.calls == ["requirement:1", "plan:1"]  # CRUD never calls the coder.


def test_questions_revise_stale_gate_and_restart(settings, store, plan):
    run = new_run(store)
    gateway = FixtureGateway(plan, require_question=True)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        old = store.get_run(run)["pending"]
        assert old["stage"] == "clarification"
        with pytest.raises(Conflict):
            decision(store, run)
        decision(store, run, "answer", "个人用户")
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        assert store.get_run(run)["pending"]["stage"] == "requirements"
        with pytest.raises(Conflict):
            store.submit(
                run,
                {"gate_id": old["gate_id"], "action": "answer", "text": "again"},
                str(uuid.uuid4()),
            )
        decision(store, run, "revise", "明确只是个人 CRUD")
        worker.tick()
        decision(store, run, "reject")
        worker.tick()
    assert store.get_run(run)["status"] == "REJECTED"
    assert not (settings.data_dir / "runs" / run / "product").exists()


def test_crash_after_graph_progress_does_not_consume_next_gate(settings, store, plan, monkeypatch):
    run = new_run(store)
    gateway = FixtureGateway(plan)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        decision(store, run)
        original = store.finish
        monkeypatch.setattr(
            store, "finish", lambda *a, **kw: (_ for _ in ()).throw(SystemExit("crash"))
        )
        with pytest.raises(SystemExit):
            worker.tick()
        monkeypatch.setattr(store, "finish", original)
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        result = store.get_run(run)
        assert result["status"] == "WAITING_DESIGN"
        assert gateway.calls.count("plan:1") == 1
        decision(store, run, "reject")
        worker.tick()
    assert store.get_run(run)["status"] == "REJECTED"


def test_only_one_worker(settings, store, plan):
    with Runtime(settings, store, FixtureGateway(plan)), pytest.raises(Timeout):
        with Runtime(settings, store, FixtureGateway(plan)):
            pass


def test_rule_coding_repair_is_bounded(settings, store, plan):
    plan.custom_rules = [
        CustomRule(
            description="priority >= 0",
            entity="task",
            accept_examples=[{"title": "ok", "priority": 1, "done": False}],
            reject_examples=[{"title": "bad", "priority": -1, "done": False}],
        )
    ]
    gateway = FixtureGateway(plan, fail_first_code=True)
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        decision(store, run)
        worker.tick()
        decision(store, run)
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_DELIVERY", store.get_run(run)
        decision(store, run)
        worker.tick()
    assert store.get_run(run)["status"] == "READY"
    assert "coding:0" in gateway.calls and "coding:1" in gateway.calls
    assert "coding:2" not in gateway.calls


def test_tampered_delivery_not_released(settings, store, plan):
    run = new_run(store)
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
        decision(store, run)
        worker.tick()
        decision(store, run)
        worker.tick()
        (settings.data_dir / "runs" / run / "delivery.zip").write_bytes(b"tampered")
        decision(store, run)
        worker.tick()
    assert store.get_run(run)["status"] == "FAILED"
