"""Explicit query closure constrains source intent, never planner defaults."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, explicit_legacy_field_constraints
from workbench.requirement_sources import analysis_source_conflicts

CLOSURES = (
    "其他未声明的字段不增加查询条件。",
    "未列出的字段不得添加查询参数。",
    "未声明的 searchable、filterable、date_range 均为 false。",
    "Do not add query conditions for other undeclared fields.",
    "Unlisted fields must not have query controls.",
    "Unspecified searchable, filterable and date_range are false.",
)
DECLARATIONS = (
    "documents: headline/writer 关键词搜索；documents.category 精确筛选；"
    "documents.event_on 起止日期均包含边界。"
)


def query_case(closure=CLOSURES[0], *, declarations=DECLARATIONS):
    requirement = Requirement(
        summary="Document catalogue",
        users=["editor"],
        data_scope="per_user",
        features=[declarations, closure] if closure else [declarations],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="documents", field=name, kind=kind)
            for name, kind in (
                ("headline", "text"),
                ("writer", "text"),
                ("category", "enum"),
                ("event_on", "date"),
                ("archived_on", "date"),
                ("note", "text"),
            )
        ],
    )
    plan = Plan(
        title="Document catalogue",
        data_scope="per_user",
        acceptance=["Manage documents"],
        entities=[
            {
                "name": "documents",
                "description": "Documents",
                "fields": [
                    {"name": "headline", "kind": "text", "searchable": True},
                    {"name": "writer", "kind": "text", "searchable": True},
                    {
                        "name": "category",
                        "kind": "enum",
                        "choices": ["a", "b"],
                        "filterable": True,
                    },
                    {"name": "event_on", "kind": "date", "date_range": True},
                    {"name": "archived_on", "kind": "date"},
                    {"name": "note", "kind": "text"},
                ],
            }
        ],
    )
    return requirement, plan


@pytest.mark.parametrize("closure", CLOSURES)
@pytest.mark.parametrize(
    "name,attribute",
    [
        ("writer", "filterable"),
        ("event_on", "filterable"),
        ("note", "searchable"),
        ("archived_on", "date_range"),
    ],
)
def test_closed_queries_reject_each_extra_capability_without_typed_false(closure, name, attribute):
    requirement, plan = query_case(closure)
    before = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    assert all(getattr(field, attribute) is None for field in requirement.field_requirements)
    field = next(field for field in plan.entities[0].fields if field.name == name)
    setattr(field, attribute, True)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "constraint_mismatch"
        and item["source"]["section"] == "features"
        and item["source"]["index"] == 1
        and item["targets"] == [{"entity": "documents", "field": name}]
        and item["attribute"] == attribute
        and item["expected"] is False
        and item["actual"] is True
        for item in diagnostics
    )


@pytest.mark.parametrize(
    "closure",
    ["", "其他未声明的字段可以增加查询条件。", "其他未声明的字段无需增加查询条件。"],
)
def test_open_requests_do_not_invent_false_query_obligations(closure):
    requirement, plan = query_case(closure)
    plan.entities[0].fields[1].filterable = True
    plan.entities[0].fields[3].filterable = True
    plan.entities[0].fields[-1].searchable = True
    assert coverage_gaps(requirement, plan) == []
    assert not any(
        item["attribute"] in {"searchable", "filterable", "date_range"}
        and item["expected"] is False
        for item in explicit_legacy_field_constraints(requirement)
    )


@pytest.mark.parametrize(
    "declaration",
    [
        "documents.event_on 日期范围筛选和精确筛选",
        "documents.event_on date range filter and exact filter",
    ],
)
@pytest.mark.parametrize("missing", ["filterable", "date_range"])
def test_explicit_range_and_exact_filter_remain_independent(declaration, missing):
    requirement, plan = query_case(declarations=DECLARATIONS + declaration)
    field = plan.entities[0].fields[3]
    field.filterable = True
    assert coverage_gaps(requirement, plan) == []
    setattr(field, missing, False)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["attribute"] == missing and item["expected"] is True for item in diagnostics)


@pytest.mark.parametrize("retain_closure", [True, False])
def test_candidate_true_cannot_authorize_itself_against_original_query_closure(retain_closure):
    requirement, _ = query_case()
    original = "\n".join(requirement.features)
    candidate = requirement.model_copy(deep=True)
    if not retain_closure:
        candidate.features.pop()
    candidate.field_requirements[3].filterable = True
    before = candidate.model_dump()
    diagnostics = analysis_source_conflicts(None, candidate, [original], cursor=1)
    assert any(
        item["code"] == "requirement_source_conflict"
        and item["target"] == {"entity": "documents", "field": "event_on"}
        and item["attribute"] == "filterable"
        and {source["expected"] for source in item["sources"]} == {False, True}
        and any(source["origin"] == "user_input" for source in item["sources"])
        for item in diagnostics
    )
    assert candidate.model_dump() == before


def test_original_explicit_exact_and_range_authorizes_both_candidate_flags():
    requirement, _ = query_case(declarations=DECLARATIONS + "documents.event_on 精确筛选。")
    requirement.field_requirements[3].filterable = True
    requirement.field_requirements[3].date_range = True
    assert (
        analysis_source_conflicts(None, requirement, ["\n".join(requirement.features)], cursor=1)
        == []
    )


def test_candidate_prose_cannot_authorize_a_query_while_its_typed_flag_is_none():
    requirement, plan = query_case()
    original = "\n".join(requirement.features)
    candidate = requirement.model_copy(deep=True)
    candidate.features.append("documents.event_on 精确筛选。")
    assert candidate.field_requirements[3].filterable is None
    plan.entities[0].fields[3].filterable = True
    # The added sentence describes this candidate Plan, but cannot establish
    # authority to change the original closed source before design approval.
    assert coverage_gaps(candidate, plan) == []
    before = candidate.model_dump()
    diagnostics = analysis_source_conflicts(None, candidate, [original], cursor=1)
    assert any(
        item["target"] == {"entity": "documents", "field": "event_on"}
        and item["attribute"] == "filterable"
        and {source["expected"] for source in item["sources"]} == {False, True}
        and any(source["origin"] == "user_input" for source in item["sources"])
        for item in diagnostics
    )
    assert candidate.model_dump() == before


def test_query_closure_stays_on_its_entity_when_field_names_repeat():
    requirement, plan = query_case()
    requirement.field_requirements.extend(
        field.model_copy(update={"entity": "archive"})
        for field in list(requirement.field_requirements)
    )
    plan.entities.append(plan.entities[0].model_copy(deep=True, update={"name": "archive"}))
    requirement.features = [
        DECLARATIONS + "documents: " + CLOSURES[0],
        "archive.event_on 精确筛选；archive.writer 精确筛选。",
    ]
    plan.entities[1].fields[1].filterable = True
    plan.entities[1].fields[3].filterable = True
    assert coverage_gaps(requirement, plan) == []
    for field in requirement.field_requirements:
        if field.entity == "archive" and field.field == "event_on":
            field.filterable = True
    assert (
        analysis_source_conflicts(None, requirement, ["\n".join(requirement.features)], cursor=1)
        == []
    )
    plan.entities[0].fields[3].filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert [(item["targets"], item["attribute"]) for item in diagnostics] == [
        ([{"entity": "documents", "field": "event_on"}], "filterable")
    ]


def test_closing_one_named_query_flag_does_not_close_other_capabilities():
    requirement, plan = query_case("未声明的 filterable 均为 false。")
    plan.entities[0].fields[-1].searchable = True
    plan.entities[0].fields[4].date_range = True
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = True
    assert coverage_gaps(requirement, plan)


def test_original_markdown_field_rows_use_the_existing_descriptor_binding():
    requirement, plan = query_case(
        CLOSURES[2],
        declarations="\n".join(
            [
                "| Entity | Field | Constraints |",
                "| --- | --- | --- |",
                "| documents | headline | text；必填；关键词搜索 |",
                "| documents | writer | text；必填；关键词搜索 |",
                "| documents | category | enum；必填；精确筛选 |",
                "| documents | event_on | date；必填；包含首尾的日期范围 |",
            ]
        ),
    )
    assert coverage_gaps(requirement, plan) == []
    requirement.field_requirements[0].searchable = True
    requirement.field_requirements[1].searchable = True
    requirement.field_requirements[2].filterable = True
    requirement.field_requirements[3].date_range = True
    original = "\n".join(requirement.features)
    assert analysis_source_conflicts(None, requirement, [original], cursor=1) == []
    requirement.field_requirements[3].filterable = True
    assert any(
        item["attribute"] == "filterable"
        for item in analysis_source_conflicts(None, requirement, [original], cursor=1)
    )


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_analysis_projection_and_coverage_share_closed_query_provenance(section):
    requirement, plan = query_case()
    closure = requirement.features.pop()
    if section == "facts":
        requirement.facts = {"query_policy": closure}
    else:
        getattr(requirement, section).append(closure)
    projected = explicit_legacy_field_constraints(requirement)
    obligation = next(
        item
        for item in projected
        if item["field"] == "event_on" and item["attribute"] == "filterable"
    )
    plan.entities[0].fields[3].filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"] == obligation["source"] and item["expected"] is obligation["expected"]
        for item in diagnostics
    )
