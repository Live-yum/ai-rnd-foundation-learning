"""Deterministic customer obligation feedback reaches the next planner unchanged."""

from conftest import new_run

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.flow import Workflow
from workbench.settings import ROOT


def test_required_priority_retry_receives_exact_typed_expected_and_actual(settings, store):
    approved = Requirement(
        summary="客户服务优先级必须填写",
        users=["服务人员"],
        data_scope="shared",
        features=[],
        acceptance=["服务请求的优先级必填"],
        field_requirements=[FieldRequirement(entity="requests", field="priority", required=True)],
    )
    valid = Plan.model_validate_json((ROOT / "examples/plans/customer-service.json").read_text())
    invalid = valid.model_copy(deep=True)
    next(
        field
        for entity in invalid.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "priority"
    ).required = False
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append(payload)
            assert schema is Plan and key == "plan:2"
            return valid.model_copy(deep=True)

    flow = Workflow(settings, store, CaptureGateway())
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((stage, data, can_approve))
        return {"decision": "revise"}

    flow.gate = gate
    state = {
        "run_id": new_run(store),
        "round": 1,
        "template": "python-basic",
        "requirement": approved.model_dump(),
        "plan": invalid.model_dump(),
    }
    outcome = flow.design(state)
    assert gates[0][0] == "design" and gates[0][2] is False
    feedback = outcome["resolution_feedback"]
    exact = next(
        d
        for d in feedback["coverage_diagnostics"]
        if d["source"]["section"] == "field_requirements"
    )
    assert exact["targets"] == [{"entity": "requests", "field": "priority"}]
    assert exact["attribute"] == "required"
    assert exact["expected"] is True and exact["actual"] is False
    flow.plan({**state, **outcome})
    assert seen[0]["resolution_feedback"] == feedback
    assert seen[0]["field_obligations"] == [
        {
            "id": "field_requirements/0",
            "target": {"entity": "requests", "field": "priority"},
            "expected": {"required": True},
        }
    ]
    assert seen[0]["approved_requirement"] == approved.model_dump()
    assert seen[0]["previous_plan"] == invalid.model_dump()


def test_planner_obligation_projection_preserves_scope_false_zero_and_unspecified(settings, store):
    approved = Requirement(
        summary="分实体字段约束",
        users=["服务人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="requests", field="title", required=True, max_length=200),
            FieldRequirement(
                entity="tasks",
                field="title",
                required=False,
                min_length=0,
                max_length=80,
                searchable=False,
            ),
        ],
    )
    plan = Plan.model_validate_json((ROOT / "examples/plans/customer-service.json").read_text())
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append(payload)
            assert "field_obligations" in instruction
            return plan

    flow = Workflow(settings, store, CaptureGateway())
    flow.plan({"run_id": new_run(store), "round": 1, "requirement": approved.model_dump()})
    assert seen[0]["field_obligations"] == [
        {
            "id": "field_requirements/0",
            "target": {"entity": "requests", "field": "title"},
            "expected": {"required": True, "max_length": 200},
        },
        {
            "id": "field_requirements/1",
            "target": {"entity": "tasks", "field": "title"},
            "expected": {"required": False, "min_length": 0, "max_length": 80, "searchable": False},
        },
    ]
    assert "filterable" not in seen[0]["field_obligations"][1]["expected"]
    assert seen[0]["approved_requirement"] == approved.model_dump()
