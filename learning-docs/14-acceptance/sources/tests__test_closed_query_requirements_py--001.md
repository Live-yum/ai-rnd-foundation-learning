# tests/test_closed_query_requirements.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`、`workbench.requirement_sources`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `query_case`（L23–L66）：接收`closure`、`declarations`。 调用`Requirement`、`FieldRequirement`、`Plan`。 返回路径：L66的`requirement, plan`。
- `test_closed_queries_reject_each_extra_capability_without_typed_false`（L79–L98）：接收`closure`、`name`、`attribute`。 控制顺序：L82断言`coverage_gaps(requirement, plan) == []`；L83断言`(requirement.model_dump(), plan.model_dump()) == before`；L84断言`all(getattr(field, attribute) is None for field in requirement.field_requirements)`；L88断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L89断言`any( item["code"] == "constraint_mismatch" and item["source"]["section"] == "features…`。 调用`query_case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`all`、`getattr`、`next`、`setattr`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_open_requests_do_not_invent_false_query_obligations`（L105–L115）：接收`closure`。 控制顺序：L110断言`coverage_gaps(requirement, plan) == []`；L111断言`not any( item["attribute"] in {"searchable", "filterable", "date_range"} and item["ex…`。 调用`query_case`、`coverage_gaps`、`any`、`explicit_legacy_field_constraints`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_range_and_exact_filter_remain_independent`（L126–L134）：接收`declaration`、`missing`。 控制顺序：L130断言`coverage_gaps(requirement, plan) == []`；L133断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L134断言`any(item["attribute"] == missing and item["expected"] is True for item in diagnostics…`。 调用`query_case`、`coverage_gaps`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_true_cannot_authorize_itself_against_original_query_closure`（L138–L155）：接收`retain_closure`。 控制顺序：L142按`not retain_closure`分支；L147断言`any( item["code"] == "requirement_source_conflict" and item["target"] == {"entity": "…`；L155断言`candidate.model_dump() == before`。 调用`query_case`、`"\n".join`、`requirement.model_copy`、`candidate.features.pop`、`candidate.model_dump`、`analysis_source_conflicts`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_explicit_exact_and_range_authorizes_both_candidate_flags`（L158–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L162断言`analysis_source_conflicts(None, requirement, ["\n".join(requirement.features)], curso…`。 调用`query_case`、`analysis_source_conflicts`、`"\n".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_prose_cannot_authorize_a_query_while_its_typed_flag_is_none`（L168–L187）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L173断言`candidate.field_requirements[3].filterable is None`；L177断言`coverage_gaps(candidate, plan) == []`；L180断言`any( item["target"] == {"entity": "documents", "field": "event_on"} and item["attribu…`；L187断言`candidate.model_dump() == before`。 调用`query_case`、`"\n".join`、`requirement.model_copy`、`candidate.features.append`、`coverage_gaps`、`candidate.model_dump`、`analysis_source_conflicts`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_closure_stays_on_its_entity_when_field_names_repeat`（L190–L216）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L203断言`coverage_gaps(requirement, plan) == []`；L204遍历`requirement.field_requirements`；L205按`field.entity == "archive" and field.field == "event_on"`分支；L207断言`analysis_source_conflicts(None, requirement, ["\n".join(requirement.features)], curso…`；L213断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L214断言`[(item["targets"], item["attribute"]) for item in diagnostics] == [ ([{"entity": "doc…`。 调用`query_case`、`requirement.field_requirements.extend`、`field.model_copy`、`list`、`plan.entities.append`、`plan.entities[0].model_copy`、`coverage_gaps`、`analysis_source_conflicts`、`"\n".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_closing_one_named_query_flag_does_not_close_other_capabilities`（L219–L225）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L223断言`coverage_gaps(requirement, plan) == []`；L225断言`coverage_gaps(requirement, plan)`。 调用`query_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_markdown_field_rows_use_the_existing_descriptor_binding`（L228–L253）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L242断言`coverage_gaps(requirement, plan) == []`；L248断言`analysis_source_conflicts(None, requirement, [original], cursor=1) == []`；L250断言`any( item["attribute"] == "filterable" for item in analysis_source_conflicts(None, re…`。 调用`query_case`、`"\n".join`、`coverage_gaps`、`analysis_source_conflicts`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_projection_and_coverage_share_closed_query_provenance`（L257–L276）：接收`section`。 控制顺序：L260按`section == "facts"`分支；L272断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L273断言`any( item["source"] == obligation["source"] and item["expected"] is obligation["expec…`。 调用`query_case`、`requirement.features.pop`、`getattr(requirement, section).append`、`getattr`、`explicit_legacy_field_constraints`、`next`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_closed_query_requirements.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L276。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11379`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_closed_query_requirements.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2d6c006b4326afba57ec434c5b7fe2a549fca88b8511f2d066c34410e66d5357"} -->
````python
# tests/test_closed_query_requirements.py
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
````
