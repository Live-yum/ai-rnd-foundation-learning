"""Query property references do not invent enabled application capabilities."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, explicit_legacy_field_constraints
from workbench.requirement_sources import analysis_source_conflicts


def query_case(text, section="features"):
    requirement = Requirement(
        summary="Record queries",
        users=["editor"],
        data_scope="shared",
        features=[],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="records", field=name, kind=kind)
            for name, kind in (("headline", "text"), ("priority", "enum"), ("event_on", "date"))
        ],
    )
    if section == "facts":
        requirement.facts = {"query_notes": text}
    else:
        setattr(requirement, section, [text])
    plan = Plan(
        title="Record queries",
        data_scope="shared",
        acceptance=["Manage records"],
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "headline", "kind": "text"},
                    {"name": "priority", "kind": "enum", "choices": ["a", "b"]},
                    {"name": "event_on", "kind": "date"},
                ],
            }
        ],
    )
    return requirement, plan


REFERENCES = [
    "保留用户字段；查询开关遵循字段的 searchable、filterable、date_range 声明。",
    "所有字段遵循 searchable、filterable、date_range 声明。",
    "searchable、filterable、date_range 仅按字段清单配置。",
    "searchable、filterable、date_range 默认为 false。",
    "未声明的 searchable、filterable、date_range 不启用。",
    "Query flags searchable, filterable and date_range follow the declared field definitions.",
    "All fields follow the declared flags searchable, filterable, and date_range.",
    "The attributes searchable/filterable/date_range default to false.",
    "The flags `searchable`, `filterable` and `date_range` remain disabled.",
    "不要启用以下查询开关 searchable、filterable、date_range。",
    "不启用查询开关 searchable、filterable、date_range。",
    "Do not enable the following query attributes searchable, filterable and date_range.",
]


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("text", REFERENCES)
def test_unbound_query_attribute_references_do_not_require_enabled_queries(text, section):
    requirement, plan = query_case(text, section)
    before = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert explicit_legacy_field_constraints(requirement) == []
    assert (requirement.model_dump(), plan.model_dump()) == before


@pytest.mark.parametrize(
    "text",
    [
        "所有字段开启 searchable、filterable、date_range 开关。",
        "开启所有字段的 searchable、filterable、date_range 开关。",
        "Enable query flags searchable, filterable and date_range.",
        "Query flags searchable, filterable and date_range are enabled.",
        "searchable、filterable、date_range 开关均应启用。",
        "启用以下查询开关 searchable、filterable、date_range。",
        "Enable the following query attributes searchable, filterable and date_range.",
        "Query flags searchable, filterable and date_range are true.",
        "需要关键词搜索、精确筛选和日期范围查询。",
    ],
)
def test_explicit_global_query_requirements_still_need_all_requested_capabilities(text):
    requirement, plan = query_case(text)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert {item["attribute"] for item in diagnostics} == {
        "searchable",
        "filterable",
        "date_range",
    }
    for field, attribute in zip(
        plan.entities[0].fields, ("searchable", "filterable", "date_range"), strict=True
    ):
        setattr(field, attribute, True)
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "attribute,index", [("searchable", 0), ("filterable", 1), ("date_range", 2)]
)
@pytest.mark.parametrize("expected", [True, False])
def test_explicit_named_boolean_assignments_are_never_metadata(attribute, index, expected):
    requirement, plan = query_case(REFERENCES[0])
    name = plan.entities[0].fields[index].name
    requirement.features.append(f"records.{name} {attribute}={str(expected).lower()}。")
    field = plan.entities[0].fields[index]
    setattr(field, attribute, expected)
    assert coverage_gaps(requirement, plan) == []
    setattr(field, attribute, not expected)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == attribute
        and item["expected"] is expected
        and item["targets"] == [{"entity": "records", "field": name}]
        for item in diagnostics
    )


@pytest.mark.parametrize(
    "text",
    [
        REFERENCES[0] + "records.event_on 日期范围筛选。",
        "查询开关遵循 searchable、filterable、date_range 声明，同时 records.event_on 开启 date_range。",
        "Query flags follow searchable, filterable and date_range declarations, "
        "and records.event_on enables date_range.",
        "records.headline（searchable），records.priority（filterable），records.event_on（date_range）",
    ],
)
def test_local_named_queries_survive_neighboring_attribute_references(text):
    requirement, plan = query_case(text)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "date_range"
        and item["targets"] == [{"entity": "records", "field": "event_on"}]
        for item in diagnostics
    )
    for field, attribute in zip(
        plan.entities[0].fields, ("searchable", "filterable", "date_range"), strict=True
    ):
        setattr(field, attribute, True)
    assert coverage_gaps(requirement, plan) == []


def test_reference_prose_cannot_erase_an_independent_typed_query_requirement():
    requirement, plan = query_case(REFERENCES[0])
    requirement.field_requirements[2].date_range = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert [(item["source"], item["attribute"], item["expected"]) for item in diagnostics] == [
        ({"section": "field_requirements", "index": 2}, "date_range", True)
    ]
    plan.entities[0].fields[2].date_range = True
    assert coverage_gaps(requirement, plan) == []


def test_reference_prose_cannot_authorize_a_query_under_original_source_closure():
    requirement, plan = query_case(REFERENCES[0])
    requirement.features.append("其他未声明的字段不增加查询条件。")
    original = "\n".join(requirement.features)
    assert coverage_gaps(requirement, plan) == []
    candidate = requirement.model_copy(deep=True)
    candidate.features.append("records.event_on 开启 date_range。")
    candidate.field_requirements[2].date_range = None
    diagnostics = analysis_source_conflicts(None, candidate, [original], cursor=1)
    assert any(
        item["target"] == {"entity": "records", "field": "event_on"}
        and item["attribute"] == "date_range"
        and {source["expected"] for source in item["sources"]} == {False, True}
        and any(source["origin"] == "user_input" for source in item["sources"])
        for item in diagnostics
    )
