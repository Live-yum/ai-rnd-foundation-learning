"""Pure validation of the recorded 76ca candidate, never approval or execution."""

import hashlib
import json
from pathlib import Path

import pytest

from workbench.domain import FieldSpec, Plan, Requirement
from workbench.entity_requirements import entity_gaps
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_source_conflicts

FIXTURES = Path(__file__).parent / "fixtures/customer_design_diagnostics/76ca70b"
HASHES = {
    "python-unapproved-design.json": "293da0b8cde09658f618ac76328eb1393b1d3eb79193456a419170adae1b4ecc",
    "python-summary.json": "3ada405998d4af9df24020c8eaff05ec428471ebb0caa0104757bb6758403ef9",
}


def recorded_case():
    envelope = json.loads((FIXTURES / "python-unapproved-design.json").read_bytes())
    assert envelope["format"] == "customer-design-diagnostic-v1"
    assert envelope["approval_status"] == "unapproved"
    assert envelope["execution_authorized"] is False
    assert envelope["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(envelope["requirement"]), Plan.model_validate(
        envelope["candidate_plan"]
    )


@pytest.mark.parametrize("filename,expected", HASHES.items())
def test_recorded_inputs_are_unchanged_and_original_failure_remains_visible(filename, expected):
    assert hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest() == expected
    summary = json.loads((FIXTURES / "python-summary.json").read_bytes())
    assert summary["passed"] is False
    assert summary["failure_code"] == "workflow_not_ready"
    assert summary["run_identity"] == [
        "36881018319",
        "1",
        "76ca70b2efedfc81e10637f3f93d58e1eca480c1",
    ]
    sources = summary["failure_details"]["coverage_sources"]
    assert len(sources) == 1
    assert sources[0]["code"] == "legacy_missing_field"
    assert sources[0]["source"] == {"section": "acceptance", "index": 1, "clause": 3}
    assert "不存在 published_on 或任何额外业务字段，也无遗漏" in sources[0]["source_excerpt"]


def test_exact_unapproved_candidate_has_no_spurious_obligation_without_any_mutation():
    requirement, plan = recorded_case()
    before = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert len(requirement.field_requirements) == 19
    assert len(requirement.entity_requirements) == 3
    assert requirement.additional_entities is False
    assert all(not item.additional_fields for item in requirement.entity_requirements)
    assert entity_gaps(requirement, plan) == []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert analysis_source_conflicts(None, requirement, []) == []
    assert (requirement.model_dump(), plan.model_dump()) == before


@pytest.mark.parametrize("index", range(19))
def test_every_recorded_typed_field_remains_required_to_exist(index):
    requirement, plan = recorded_case()
    obligation = requirement.field_requirements[index]
    entity = next(item for item in plan.entities if item.name == obligation.entity)
    entity.fields = [field for field in entity.fields if field.name != obligation.field]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "missing_or_ambiguous"
        and item["source"] == {"section": "field_requirements", "index": index}
        for item in diagnostics
    )
    assert entity_gaps(requirement, plan)


def mutation_cases():
    requirement, _ = recorded_case()
    return [
        (index, attribute)
        for index, obligation in enumerate(requirement.field_requirements)
        for attribute, value in obligation.model_dump(exclude_none=True).items()
        if attribute not in {"entity", "field"}
    ]


@pytest.mark.parametrize("index,attribute", mutation_cases())
def test_every_recorded_typed_constraint_stays_strict(index, attribute):
    requirement, plan = recorded_case()
    obligation = requirement.field_requirements[index]
    entity = next(item for item in plan.entities if item.name == obligation.entity)
    field = next(item for item in entity.fields if item.name == obligation.field)
    expected = getattr(obligation, attribute)
    if type(expected) is bool:
        replacement = not expected
    elif type(expected) is int:
        replacement = expected + 1
    elif attribute == "choices":
        replacement = expected + ["extra-synthetic-choice"]
    else:
        assert attribute == "kind"
        replacement = "text" if expected != "text" else "integer"
    setattr(field, attribute, replacement)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "constraint_mismatch"
        and item["source"] == {"section": "field_requirements", "index": index}
        and item["attribute"] == attribute
        and item["expected"] == expected
        and item["actual"] == replacement
        for item in diagnostics
    )


@pytest.mark.parametrize("index", range(3))
@pytest.mark.parametrize("mutation", ["extra_field", "missing_entity"])
def test_recorded_closed_catalog_cannot_be_reopened_by_narrative(index, mutation):
    requirement, plan = recorded_case()
    if mutation == "extra_field":
        plan.entities[index].fields.append(FieldSpec(name="published_on", kind="date"))
    else:
        plan.entities.pop(index)
    assert entity_gaps(requirement, plan)


def test_recorded_closed_entity_set_rejects_additional_entity():
    requirement, plan = recorded_case()
    plan.entities.append(plan.entities[0].model_copy(deep=True, update={"name": "extra"}))
    assert entity_gaps(requirement, plan)


@pytest.mark.parametrize(
    "negative",
    [
        "不存在 published_on",
        "不含 published_on",
        "不包含 published_on",
        "没有 published_on 字段",
        "禁止添加 published_on 字段",
        "published_on 字段不得存在",
    ],
)
@pytest.mark.parametrize("completeness", ["", "，也无遗漏", "，没有遗漏任何明确字段"])
def test_recorded_inventory_absence_and_completeness_do_not_create_a_positive(
    negative, completeness
):
    requirement, plan = recorded_case()
    heading = requirement.acceptance[1].rsplit("；", 1)[0]
    requirement.acceptance[1] = heading + "；" + negative + completeness + "。"
    assert coverage_gaps(requirement, plan) == []
    assert entity_gaps(requirement, plan) == []
