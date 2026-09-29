import uuid

import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from sqlalchemy import select

from workbench.conversation import command_word
from workbench.domain import ModelReview, Requirement
from workbench.runtime import Runtime
from workbench.store import Approval, Conflict


@pytest.mark.parametrize("value", ["批准", "“批准”", '"批准"', "'批准'", "「批准」", " `批准` "])
def test_control_words_are_not_sent_as_user_answers(value):
    assert command_word(value) == "批准"


def test_intelligent_action_is_an_explicit_permission(store):
    run = new_run(store)
    with pytest.raises(Conflict):
        store.set_automation(run, True, "")
    assert not store.get_run(run)["auto_mode"]


def test_more_than_ten_manual_rounds_then_continue_same_run(settings, store, plan):
    class Questions(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is Requirement:
                self.calls.append(key)
                return requirement(["补充核心边界"] if len(self.calls) <= 13 else [])
            return super().complete(run, key, instruction, payload, schema)

    gateway = Questions(plan)
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        for index in range(13):
            worker.tick()
            assert store.get_run(run)["status"] == "WAITING_CLARIFICATION"
            decision(store, run, "answer", f"具体补充 {index}")
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
    assert len(store.messages(run)) == 14
    assert store.get_run(run)["error"] is None


@pytest.mark.parametrize("stage", ["clarification", "requirements", "design", "delivery"])
def test_smart_from_any_gate_finishes_without_another_user_input(settings, store, plan, stage):
    gateway = FixtureGateway(plan, require_question=stage == "clarification")
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        if stage in {"design", "delivery"}:
            decision(store, run)
            worker.tick()
        if stage == "delivery":
            decision(store, run)
            worker.tick()
        assert store.get_run(run)["pending"]["stage"] == stage
        store.set_automation(run, True, str(uuid.uuid4()))
    # Close/reopen to prove automation consent and the human interrupt persist.
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["auto_mode"] is True and state["pending"] is None
    assert state["result"]["cleanroom"]["passed"] is True
    with store.tx() as s:
        approvals = list(s.scalars(select(Approval)))
        assert any(x.actor == "delegated-ai" for x in approvals)
    # Recommend is not a fake user natural-language message.
    assert not any(m["content"] == "智能推荐" for m in store.messages(run))


def test_initial_smart_selection_is_retained(settings, store, plan):
    project = store.create_project("smart", "project")
    run = store.create_run(
        project["id"],
        {
            "requirement": "个人CRUD",
            "template": "python-basic",
            "selection": {
                "template": "python-basic",
                "backend": "fastapi",
                "frontend": "api-only",
                "database": "sqlite",
            },
            "intelligent": True,
        },
        "run",
    )["run_id"]
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["options"]["frontend"] == "api-only"


def test_smart_does_not_loop_or_hide_unsupported_requirements(settings, store, plan):
    class Unsupported(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            return requirement().model_copy(
                update={"questions": ["外部付费采集"], "unsupported": ["payment-system"]}
            )

    g = Unsupported(plan)
    run = new_run(store)
    store.set_automation(run, True, str(uuid.uuid4()))
    with Runtime(settings, store, g) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "BLOCKED"
    assert len(g.calls) <= 3
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()


def test_optional_positive_round_limit_pauses_and_resumes_without_loss(settings, store, plan):
    settings.max_rounds = 1
    g = FixtureGateway(plan, require_question=True)
    run = new_run(store)
    with Runtime(settings, store, g) as worker:
        worker.tick()
        decision(store, run, "answer", "最后明确的回答必须保留")
        worker.tick()
        assert store.get_run(run)["status"] == "PAUSED_LIMIT"
    settings.max_rounds = 0
    store.retry(run, "resume-same-run")
    with Runtime(settings, store, g) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
    assert store.messages(run)[-1]["content"] == "最后明确的回答必须保留"


def test_optional_review_model_does_not_replace_executable_tests(settings, store, plan):
    settings.model_review = True

    class Reviewer(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is ModelReview:
                assert payload["independent_evidence"]["passed"] is True
                self.calls.append(key)
                return ModelReview(
                    summary="审阅备注，不假装执行测试", observations=[], uncovered_requirements=[]
                )
            return super().complete(run, key, instruction, payload, schema)

    g = Reviewer(plan)
    run = new_run(store)
    store.set_automation(run, True, "consent")
    with Runtime(settings, store, g) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert any(key.startswith("review:") for key in g.calls)
    assert state["result"]["cleanroom"]["passed"]
