import uuid

import pytest
from conftest import FixtureGateway, new_run, requirement
from pydantic import ValidationError

from workbench.domain import ClarificationQuestion, Requirement, ResumeInput
from workbench.requirement_coverage import reconcile
from workbench.runtime import Runtime
from workbench.store import Conflict


def question(kind="single", **updates):
    return {
        "id": "audience",
        "prompt": "谁会使用第一版？",
        "kind": kind,
        "options": [
            {"id": "team", "label": "客服成员 + 团队主管", "description": "内部团队"},
            {"id": "personal", "label": "只有我自己", "description": ""},
        ]
        if kind != "text"
        else [],
        "required": True,
        "allow_other": True,
        **updates,
    }


def waiting(store, questions=None):
    run_id = new_run(store)
    job = store.claim()
    items = questions or [question()]
    req = requirement([item["prompt"] for item in items]).model_dump()
    req["question_items"] = items
    gate = store.gate(
        run_id,
        "clarification",
        1,
        {"requirement": req, "ready": False},
        ["answer", "reject", "recommend"],
        False,
    )
    store.finish(job, "WAITING_CLARIFICATION", pending=gate)
    return run_id, gate


def submission(gate, answers=None, **updates):
    return {
        "gate_id": gate["gate_id"],
        "version": gate["version"],
        "digest": gate["digest"],
        "action": "answer",
        "text": "保留原来已确定的审计功能",
        "answers": answers or [{"question_id": "audience", "option_ids": ["team"], "text": ""}],
        **updates,
    }


def test_selected_labels_custom_text_and_idempotence_are_durable(store):
    run_id, gate = waiting(store)
    body = submission(
        gate,
        [
            {
                "question_id": "audience",
                "option_ids": ["team"],
                "text": "主管只能查看自己团队 👋",
            }
        ],
    )
    key = str(uuid.uuid4())
    first = store.submit(run_id, body, key)
    assert store.submit(run_id, body, key) == first
    history = store.messages(run_id)
    assert len(history) == 2
    assert history[-1] == {
        "role": "user",
        "content": "谁会使用第一版？\n- 客服成员 + 团队主管\n补充：主管只能查看自己团队 👋\n其他补充：保留原来已确定的审计功能",
    }
    with pytest.raises(Conflict):
        store.submit(run_id, {**body, "text": "changed"}, key)
    assert len(store.messages(run_id)) == 2


@pytest.mark.parametrize("updates", [{"version": 2}, {"digest": "f" * 64}, {"gate_id": "a" * 64}])
def test_stale_identity_never_consumes_current_gate(store, updates):
    run_id, gate = waiting(store)
    with pytest.raises(Conflict):
        store.submit(run_id, submission(gate, **updates), str(uuid.uuid4()))
    assert store.get_run(run_id)["pending"] == gate
    assert len(store.messages(run_id)) == 1


@pytest.mark.parametrize(
    "answer",
    [
        {"question_id": "attacker", "option_ids": ["team"]},
        {"question_id": "audience", "option_ids": ["unknown"]},
        {"question_id": "audience", "option_ids": ["team", "personal"]},
        {"question_id": "audience", "option_ids": []},
    ],
)
def test_invalid_selections_do_not_queue_or_approve(store, answer):
    run_id, gate = waiting(store)
    with pytest.raises(Conflict):
        store.submit(run_id, submission(gate, [answer]), str(uuid.uuid4()))
    assert store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"
    assert len(store.messages(run_id)) == 1
    assert store.claim() is None


def test_multiselect_preserves_selected_labels_and_custom_answer(store):
    run_id, gate = waiting(store, [question("multiple")])
    store.submit(
        run_id,
        submission(
            gate,
            [
                {
                    "question_id": "audience",
                    "option_ids": ["team", "personal"],
                    "text": "分两期上线",
                }
            ],
        ),
        str(uuid.uuid4()),
    )
    assert (
        "- 客服成员 + 团队主管\n- 只有我自己\n补充：分两期上线"
        in store.messages(run_id)[-1]["content"]
    )


def test_text_only_answer_remains_supported_for_legacy_and_open_intent(store):
    run_id, gate = waiting(store)
    body = {"gate_id": gate["gate_id"], "action": "answer", "text": "我想要完全不同的第三种方案"}
    store.submit(run_id, body, str(uuid.uuid4()))
    assert store.messages(run_id)[-1]["content"] == body["text"]


def test_required_question_and_optional_question_rules(store):
    optional = question("text", id="extra", prompt="其他补充", required=False)
    run_id, gate = waiting(store, [question(), optional])
    store.submit(run_id, submission(gate), str(uuid.uuid4()))
    assert "其他补充\n" not in store.messages(run_id)[-1]["content"]


@pytest.mark.parametrize(
    "value",
    [
        {"kind": "single", "options": [{"id": "only", "label": "只有一个"}]},
        {"options": [{"id": "same", "label": "一"}, {"id": "same", "label": "二"}]},
        {"kind": "text"},
    ],
)
def test_malformed_question_is_not_a_valid_model_result(value):
    with pytest.raises(ValidationError):
        ClarificationQuestion.model_validate({**question(), **value})


def test_structured_question_must_match_real_blocking_question():
    data = requirement().model_dump()
    with pytest.raises(ValidationError):
        Requirement.model_validate({**data, "question_items": [question()]})
    req = Requirement.model_validate(
        {**data, "questions": [question()["prompt"]], "question_items": [question()]}
    )
    assert not req.ready
    assert req.gate_dump()["question_items"][0]["prompt"] == req.questions[0]
    assert "question_items" not in requirement().gate_dump()


def test_answers_cannot_be_control_action_or_forged_label():
    with pytest.raises(ValidationError):
        ResumeInput(
            gate_id="a" * 64,
            action="approve",
            approved=True,
            answers=[{"question_id": "audience", "option_ids": ["team"]}],
        )
    with pytest.raises(ValidationError):
        ResumeInput(
            gate_id="a" * 64,
            action="answer",
            answers=[
                {
                    "question_id": "audience",
                    "option_ids": ["team"],
                    "label": "替换服务端标签",
                }
            ],
        )


def test_answered_choices_do_not_drop_existing_explicit_scope():
    before = requirement().model_dump()
    before["features"] = ["审计", "工单分配"]
    before["facts"] = {"roles": ["成员", "主管"]}
    candidate = requirement()
    result = reconcile(before, candidate, ["谁会使用第一版？\n- 客服成员 + 团队主管"])
    assert {"审计", "工单分配"} <= set(result.features)
    assert result.facts["roles"] == ["成员", "主管"]


def test_stage_events_are_actual_serial_nodes_and_waiting_gate(settings, store, plan):
    run_id = new_run(store)
    with Runtime(settings, store, FixtureGateway(plan, require_question=True)) as worker:
        assert worker.tick()
    events = [event["data"] for event in store.events(run_id) if event["kind"] == "stage"]
    assert [(event["name"], event["phase"]) for event in events] == [
        ("analyse", "started"),
        ("analyse", "completed"),
        ("requirements", "started"),
        ("requirements", "waiting"),
    ]
    assert store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"


def test_partial_structured_questions_cannot_hide_another_blocking_question():
    data = requirement([question()["prompt"], "数据由谁访问？"]).model_dump()
    with pytest.raises(ValidationError):
        Requirement.model_validate({**data, "question_items": [question()]})
