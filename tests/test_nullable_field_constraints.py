"""Nullable prose preserves required flags without reversing non-null prohibitions."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, explicit_legacy_field_constraints


@pytest.mark.parametrize(
    "phrase,required",
    [("可空", False), ("不可空", True), ("不得为空", True), ("可选", False), ("必填", True)],
)
def test_nullable_and_nonnullable_field_prose_stays_strict(phrase, required):
    text = f"documents 的 comment {phrase}；最大长度600"
    requirement = Requirement(
        summary="文档备注",
        users=["reader"],
        data_scope="per_user",
        features=[text],
        acceptance=[],
        field_requirements=[FieldRequirement(entity="documents", field="comment", kind="text")],
    )
    plan = Plan(
        title="文档备注",
        data_scope="per_user",
        acceptance=["Offline source constraint check"],
        entities=[
            {
                "name": "documents",
                "description": "文档",
                "fields": [
                    {"name": "comment", "kind": "text", "required": required, "max_length": 600},
                    {"name": "headline", "kind": "text", "required": True},
                ],
            }
        ],
    )
    assert coverage_gaps(requirement, plan) == []
    source_constraints = explicit_legacy_field_constraints(requirement)
    assert [
        (item["entity"], item["field"], item["expected"])
        for item in source_constraints
        if item["attribute"] == "required"
    ] == [("documents", "comment", required)]
    plan.entities[0].fields[0].required = not required
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    mismatches = [item for item in diagnostics if item["attribute"] == "required"]
    assert len(mismatches) == 1
    assert mismatches[0]["targets"] == [{"entity": "documents", "field": "comment"}]
    assert mismatches[0]["expected"] is required
    assert mismatches[0]["actual"] is not required
