"""Keyword shorthand binds its own fields without borrowing exact-filter targets."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps

QUERIES = (
    "headline/writer 关键词及 category、status 精确筛选组合查询",
    "headline、writer 关键字与 category/status 精确筛选",
    "category/status 精确筛选与 headline/writer 关键词",
    "headline/writer 关键词查询，category/status 精确筛选",
    "headline/writer keyword query and category/status exact filtering",
    "headline/writer keywords and category/status exact filtering",
)


def query_case(text):
    requirement = Requirement(
        summary="文档查询",
        users=["reader"],
        data_scope="per_user",
        features=[],
        acceptance=[text],
        field_requirements=[
            FieldRequirement(entity="documents", field="writer", filterable=False),
            FieldRequirement(entity="documents", field="category", searchable=False),
        ],
    )
    plan = Plan(
        title="文档查询",
        data_scope="per_user",
        acceptance=[text],
        entities=[
            {
                "name": "documents",
                "description": "文档",
                "fields": [
                    {"name": "headline", "kind": "text", "searchable": True},
                    {"name": "writer", "kind": "text", "searchable": True},
                    {
                        "name": "category",
                        "kind": "enum",
                        "choices": ["a", "b"],
                        "filterable": True,
                    },
                    {
                        "name": "status",
                        "kind": "enum",
                        "choices": ["a", "b"],
                        "filterable": True,
                    },
                ],
            }
        ],
    )
    return requirement, plan


@pytest.mark.parametrize("text", QUERIES)
def test_keyword_shorthand_keeps_exact_filters_on_their_own_fields(text):
    requirement, plan = query_case(text)
    original = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert (requirement.model_dump(), plan.model_dump()) == original


@pytest.mark.parametrize("text", QUERIES)
@pytest.mark.parametrize(
    "name,flag",
    [
        ("headline", "searchable"),
        ("writer", "searchable"),
        ("category", "filterable"),
        ("status", "filterable"),
    ],
)
def test_keyword_shorthand_still_requires_every_named_query_field(text, name, flag):
    requirement, plan = query_case(text)
    field = next(field for field in plan.entities[0].fields if field.name == name)
    setattr(field, flag, False)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "uncovered_operation"
        and item["attribute"] == flag
        and {"entity": "documents", "field": name} in item["targets"]
        for item in diagnostics
    )


def test_keyword_shorthand_does_not_override_an_explicit_false_filter():
    requirement, plan = query_case(QUERIES[0])
    next(field for field in plan.entities[0].fields if field.name == "writer").filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert [
        (item["code"], item["source"]["section"], item["attribute"], item["expected"])
        for item in diagnostics
    ] == [("constraint_mismatch", "field_requirements", "filterable", False)]


@pytest.mark.parametrize("keyword", ["关键词查询", "关键字查询", "keyword query"])
def test_disabled_keyword_queries_remain_disabled(keyword):
    text = f"writer 禁止{keyword}，category/status 精确筛选"
    requirement, plan = query_case(text)
    writer = next(field for field in plan.entities[0].fields if field.name == "writer")
    writer.searchable = False
    assert coverage_gaps(requirement, plan) == []
    writer.searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "searchable"
        and item["expected"] is False
        and item["targets"] == [{"entity": "documents", "field": "writer"}]
        for item in diagnostics
    )


@pytest.mark.parametrize(
    "text",
    [
        "writer 的关键词查询结果中展示 category/status",
        "writer 的关键字查询结果中展示 category/status",
        "writer 标签说明包含关键词",
        "页面显示关键词",
    ],
)
def test_keyword_descriptions_and_query_outputs_do_not_add_capabilities(text):
    requirement, plan = query_case(text)
    for field in plan.entities[0].fields:
        field.searchable = False
        field.filterable = False
    assert coverage_gaps(requirement, plan) == []
