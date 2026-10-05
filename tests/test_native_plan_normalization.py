"""Replay the nine-field registration recommendation without live project data."""

from copy import deepcopy

import pytest
from test_business_contracts import business_plan

from workbench.domain import Plan, Requirement
from workbench.native_modules import validate_plan
from workbench.native_plan_normalization import normalize_native_plan, source_plan
from workbench.requirement_coverage import coverage_gaps

NAMES = [
    "applicant_name",
    "student_id",
    "school",
    "phone",
    "email",
    "category",
    "project_name",
    "project_description",
    "status",
]


def registration():
    return Plan.model_validate(
        {
            "title": "Registration",
            "data_scope": "shared",
            "acceptance": ["CRUD"],
            "entities": [
                {
                    "name": "registration",
                    "description": "报名",
                    "fields": [{"name": name, "kind": "text", "required": False} for name in NAMES],
                }
            ],
        }
    )


def approved():
    return Requirement.model_validate(
        {
            "summary": "报名",
            "users": ["管理员"],
            "data_scope": "shared",
            "features": ["CRUD"],
            "acceptance": ["CRUD"],
            "field_requirements": [
                {"entity": "registration", "field": name, "required": False} for name in NAMES
            ],
            "entity_requirements": [
                {"entity": "registration", "fields": NAMES, "additional_fields": False}
            ],
            "additional_entities": False,
        }
    )


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_nine_field_replay_maps_audit_collision_without_inventing_required_fields(template):
    plan, requirement = registration(), approved()
    snapshot = (plan.model_dump(), requirement.model_dump())
    with pytest.raises(ValueError, match="Field conflicts with native framework audit columns"):
        validate_plan(plan)
    normalized, report = normalize_native_plan(plan, requirement, template)
    validate_plan(normalized)
    assert [field.name for field in normalized.entities[0].fields] == [
        *NAMES[:-1],
        "registration_status",
    ]
    assert all(not field.required for field in normalized.entities[0].fields)
    assert coverage_gaps(requirement, normalized, native_normalization=report) == []
    assert (plan.model_dump(), requirement.model_dump()) == snapshot
    assert source_plan(normalized, report) == plan
    assert normalize_native_plan(plan, requirement, template) == (normalized, report)
    assert normalize_native_plan(normalized, requirement, template, prior_normalization=report) == (
        normalized,
        report,
    )
    assert normalize_native_plan(normalized, requirement, template)[0] == normalized


def test_collision_safe_names_and_constraint_drift_stays_blocked():
    data = registration().model_dump()
    data["entities"][0]["fields"].append({"name": "registration_status", "kind": "text"})
    requirement = approved().model_copy(deep=True)
    requirement.entity_requirements[0].additional_fields = True
    normalized, report = normalize_native_plan(data, requirement, "fastapiadmin")
    assert normalized.entities[0].fields[-2].name == "registration_status_2"
    normalized.entities[0].fields[-2].required = True
    diagnostics = []
    assert coverage_gaps(
        requirement, normalized, native_normalization=report, diagnostics=diagnostics
    )
    assert any(
        item.get("attribute") == "required" and item["source"]["index"] == 8 for item in diagnostics
    )


def test_rule_example_keys_change_but_example_values_and_labels_never_do():
    data = registration().model_dump()
    data["entities"][0]["fields"][-1]["label"] = "status"
    data["custom_rules"] = [
        {
            "entity": "registration",
            "description": "status must be allowed",
            "accept_examples": [{"status": "status"}],
            "reject_examples": [{"status": "no"}],
        }
    ]
    normalized, report = normalize_native_plan(data, approved(), "fastapiadmin")
    assert normalized.custom_rules[0].accept_examples == [{"registration_status": "status"}]
    assert normalized.custom_rules[0].description == "registration_status must be allowed"
    assert normalized.entities[0].fields[-1].label == "status"
    assert source_plan(normalized, report) == Plan.model_validate(data)


def test_business_references_are_remapped_without_changing_values_or_permissions():
    data = business_plan()
    # Fixture replacement changes a real workflow, its predicates and refs.
    replacements = {
        "request_state": "status",
        "resolved_at": "updated_time",
        "due_at": "deleted_time",
        "assignee_id": "created_id",
        "customer_id": "uuid",
    }

    def rename(value):
        if isinstance(value, dict):
            return {key: rename(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rename(item) for item in value]
        return replacements.get(value, value) if isinstance(value, str) else value

    original = Plan.model_validate(rename(data))
    normalized, report = normalize_native_plan(original, approved(), "fastapiadmin")
    assert normalized.business.workflows[0].status_field == "requests_status"
    assert normalized.business.workflows[0].transitions[-1].set_timestamp == "requests_updated_time"
    assert normalized.business.notifications[-1].due_field == "requests_deleted_time"
    assert normalized.business.resources[-1].assignee_field == "requests_created_id"
    assert normalized.business.relations[0].field == "requests_uuid"
    assert normalized.business.metrics[1].filters[0].field == "requests_status"
    assert normalized.business.metrics[2].group_by == "requests_uuid"
    assert normalized.business.permissions == original.business.permissions
    assert source_plan(normalized, report) == original
    validate_plan(normalized)


def test_python_template_unchanged_and_invalid_mapping_rejected():
    plan = registration()
    normalized, report = normalize_native_plan(plan, approved(), "python-basic")
    assert normalized == plan
    assert report["field_mappings"] == []
    normalized, report = normalize_native_plan(plan, approved(), "fastapiadmin")
    invalid = deepcopy(report)
    invalid["field_mappings"][0]["source_field"] = "applicant_name"
    with pytest.raises(ValueError, match="映射无效"):
        source_plan(normalized, invalid)


def test_replanning_with_prior_mapping_accepts_source_names_and_detects_missing_field():
    plan, requirement = registration(), approved()
    normalized, report = normalize_native_plan(plan, requirement, "fastapiadmin")
    assert normalize_native_plan(plan, requirement, "fastapiadmin", prior_normalization=report) == (
        normalized,
        report,
    )
    omitted = plan.model_dump()
    omitted["entities"][0]["fields"].pop()
    next_plan, next_report = normalize_native_plan(
        omitted, requirement, "fastapiadmin", prior_normalization=report
    )
    assert coverage_gaps(requirement, next_plan, native_normalization=next_report)


def test_long_names_stay_within_identifier_limit_with_deterministic_suffix():
    data = registration().model_dump()
    data["entities"][0]["name"] = "registration_archive"
    data["entities"][0]["fields"] = [
        {"name": "updated_time", "kind": "text", "required": False},
        {"name": "registration_archive_updated_time", "kind": "text", "required": False},
    ]
    plan, report = normalize_native_plan(data, approved(), "fastapiadmin")
    assert plan.entities[0].fields[0].name == "registration_archive_updated_time_2"
    validate_plan(plan)
    assert source_plan(plan, report) == Plan.model_validate(data)
