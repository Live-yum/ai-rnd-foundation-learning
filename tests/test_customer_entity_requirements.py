"""Explicit closed inventories block extra fields before generation, with repair data."""

import pytest
from conftest import new_run
from pydantic import ValidationError

from scripts.ci_real_model import SafeFailure, require_customer_spec, safe_coverage_details
from workbench.domain import EntityRequirement, Plan, Requirement
from workbench.entity_requirements import entity_gaps
from workbench.flow import Workflow
from workbench.requirement_coverage import coverage_gaps, reconcile
from workbench.settings import ROOT


def customer_plan():
    return Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )


def inventory(plan, *, closed=True):
    return Requirement(
        summary="明确字段清单",
        users=["管理人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
        entity_requirements=[
            EntityRequirement(
                entity=e.name, fields=[f.name for f in e.fields], additional_fields=not closed
            )
            for e in plan.entities
        ],
    )


def test_default_open_and_legacy_gate_digest():
    item = EntityRequirement(entity="customers", fields=["name"])
    assert item.additional_fields is True
    requirement = Requirement(
        summary="字段", users=[], data_scope="shared", features=[], acceptance=[]
    )
    assert "entity_requirements" not in requirement.gate_dump()
    assert "additional_entities" not in requirement.gate_dump()
    assert not entity_gaps(requirement, customer_plan())


def test_extra_entities_block_only_explicit_closed_entity_inventory():
    plan = customer_plan()
    approved = inventory(plan)
    plan.entities.append(plan.entities[0].model_copy(update={"name": "optional_extra"}, deep=True))
    assert not entity_gaps(approved, plan)
    approved.additional_entities = False
    diagnostics = []
    assert entity_gaps(approved, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "entity_set"
    assert diagnostics[0]["targets"] == [{"entity": "optional_extra", "field": None}]


def test_closed_entity_inventory_survives_omission_and_requires_fresh_correction():
    old = inventory(customer_plan())
    old.additional_entities = False
    proposed = inventory(customer_plan())
    assert reconcile(old.gate_dump(), proposed, []).additional_entities is False
    quote = "将 additional_entities 改为 true，允许新实体"
    proposal = proposed.model_dump()
    proposal["changes"] = [
        {
            "section": "additional_entities",
            "key": "additional_entities",
            "replacement": True,
            "source_quote": quote,
        }
    ]
    corrected = Requirement.model_validate(proposal)
    assert reconcile(old.gate_dump(), corrected, [quote]).additional_entities is True
    assert reconcile(old.gate_dump(), corrected, []).additional_entities is False


@pytest.mark.parametrize(
    "data",
    [
        {"entity": "customers", "fields": []},
        {"entity": "customers", "fields": ["name", "name"]},
        {"entity": "customers", "fields": ["created at"]},
        {"entity": "customers", "fields": ["name"], "additional_fields": "false"},
        {"entity": "customers", "fields": ["name"], "additional_fields": 0},
    ],
)
def test_field_inventory_schema_rejects_ambiguous_values(data):
    with pytest.raises(ValidationError):
        EntityRequirement.model_validate(data)


def test_duplicate_entity_inventory_rejected():
    requirement = inventory(customer_plan()).model_dump()
    requirement["entity_requirements"].append(requirement["entity_requirements"][0])
    with pytest.raises(ValidationError):
        Requirement.model_validate(requirement)


@pytest.mark.parametrize("closed", [True, False])
@pytest.mark.parametrize("mutation", ["extra", "missing_field", "missing_entity"])
def test_exact_inventory_diagnostics_preserve_open_projects(closed, mutation):
    plan = customer_plan()
    approved = inventory(plan, closed=closed)
    target = plan.entities[0]
    if mutation == "extra":
        extra = target.fields[0].model_copy(
            update={"name": "optional_extension", "required": False}
        )
        target.fields.append(extra)
    elif mutation == "missing_field":
        target.fields.pop(0)
    else:
        plan.entities.pop(0)
    diagnostics = []
    gaps = entity_gaps(approved, plan, diagnostics=diagnostics)
    if mutation == "extra" and not closed:
        assert not gaps and not diagnostics
        return
    assert gaps and len(diagnostics) == 1
    item = diagnostics[0]
    assert item["source"] == {"section": "entity_requirements", "index": 0}
    assert item["attribute"] == "fields"
    assert item["additional_fields"] is not closed
    assert item["extra"] == (["optional_extension"] if mutation == "extra" else [])
    assert item["missing"] == (
        [] if mutation == "extra" else sorted(set(item["expected"]) - set(item["actual"]))
    )


def test_same_field_names_are_entity_scoped():
    plan = customer_plan()
    approved = inventory(plan)
    next(e for e in plan.entities if e.name == "tasks").fields = [
        f for f in next(e for e in plan.entities if e.name == "tasks").fields if f.name != "title"
    ]
    diagnostics = []
    assert entity_gaps(approved, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]


def test_approved_field_sets_survive_omission_and_model_reopening():
    old = inventory(customer_plan())
    omitted = old.model_copy(update={"entity_requirements": []}, deep=True)
    assert reconcile(old.model_dump(), omitted, []).entity_requirements == old.entity_requirements
    reopened = inventory(customer_plan(), closed=False)
    assert reconcile(old.model_dump(), reopened, []).entity_requirements == old.entity_requirements


@pytest.mark.parametrize(
    "attribute,replacement,quote",
    [
        ("additional_fields", True, "将 customers.additional_fields 改为 true，允许新增字段"),
        ("fields", ["name", "contact"], "将 customers.fields 改为 name 和 contact"),
    ],
)
def test_source_backed_exact_property_correction(attribute, replacement, quote):
    old = inventory(customer_plan())
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "entity_requirements",
            "key": "customers." + attribute,
            "replacement": replacement,
            "source_quote": quote,
        }
    ]
    revised = reconcile(old.model_dump(), Requirement.model_validate(proposed), [quote])
    assert getattr(revised.entity_requirements[0], attribute) == replacement
    assert revised.entity_requirements[1:] == old.entity_requirements[1:]
    assert (
        reconcile(old.model_dump(), Requirement.model_validate(proposed), []).entity_requirements
        == old.entity_requirements
    )


def test_actual_model_extra_date_field_blocks_design_and_reaches_repair(settings, store):
    valid = customer_plan()
    approved = inventory(valid)
    bad = Plan.model_validate_json(
        (
            ROOT / "tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json"
        ).read_text(encoding="utf-8")
    )
    seen = []

    class Gateway:
        def complete(self, run_id, key, instruction, payload, schema):
            seen.append(payload)
            assert schema is Plan
            assert "entity_obligations" in instruction
            return valid.model_copy(deep=True)

    flow = Workflow(settings, store, Gateway())
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((data, can_approve))
        return {"decision": "revise"}

    flow.gate = gate
    state = {
        "run_id": new_run(store),
        "round": 1,
        "template": "python-basic",
        "requirement": approved.model_dump(),
        "plan": bad.model_dump(),
    }
    outcome = flow.design(state)
    assert gates[0][1] is False
    diagnostics = outcome["resolution_feedback"]["coverage_diagnostics"]
    precise = next(d for d in diagnostics if d["code"] == "entity_field_set")
    assert precise["extra"] == ["published_on"] and precise["missing"] == []
    assert precise["targets"] == [{"entity": "customers", "field": "published_on"}]
    result = flow.plan({**state, **outcome})
    assert seen[0]["previous_plan"] == bad.model_dump()
    assert seen[0]["resolution_feedback"] == outcome["resolution_feedback"]
    assert seen[0]["entity_obligations"][0]["additional_fields"] is False
    assert not coverage_gaps(approved, Plan.model_validate(result["plan"]))
    exported = safe_coverage_details(approved.model_dump(), bad.model_dump())
    item = next(d for d in exported if d["code"] == "entity_field_set")
    assert "published_on" in item["actual"] and "published_on" not in item["expected"]
    with pytest.raises(SafeFailure) as caught:
        require_customer_spec(bad.model_dump())
    assert caught.value.guard_code == "fields_exact"


def test_canonical_customer_prompt_explicitly_closes_field_inventory():
    from scripts.ci_real_model import customer_request

    text = customer_request()
    assert "entity_requirements" in text and "additional_fields=false" in text
    assert "穷尽且封闭" in text
