# tests/test_query_attribute_references.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`、`workbench.requirement_sources`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `query_case`（L10–L42）：接收`text`、`section`。 控制顺序：L22按`section == "facts"`分支。 调用`Requirement`、`FieldRequirement`、`setattr`、`Plan`。 返回路径：L42的`requirement, plan`。
- `test_unbound_query_attribute_references_do_not_require_enabled_queries`（L63–L70）：接收`text`、`section`。 控制顺序：L67断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L68断言`diagnostics == []`；L69断言`explicit_legacy_field_constraints(requirement) == []`；L70断言`(requirement.model_dump(), plan.model_dump()) == before`。 调用`query_case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`explicit_legacy_field_constraints`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_global_query_requirements_still_need_all_requested_capabilities`（L87–L100）：接收`text`。 控制顺序：L90断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L91断言`{item["attribute"] for item in diagnostics} == { "searchable", "filterable", "date_ra…`；L96遍历`zip( plan.entities[0].fields, ("searchable", "filterable", "date_…`；L100断言`coverage_gaps(requirement, plan) == []`。 调用`query_case`、`coverage_gaps`、`zip`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_named_boolean_assignments_are_never_metadata`（L107–L122）：接收`attribute`、`index`、`expected`。 控制顺序：L113断言`coverage_gaps(requirement, plan) == []`；L116断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L117断言`any( item["attribute"] == attribute and item["expected"] is expected and item["target…`。 调用`query_case`、`requirement.features.append`、`str(expected).lower`、`str`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_named_queries_survive_neighboring_attribute_references`（L135–L148）：接收`text`。 控制顺序：L138断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L139断言`any( item["attribute"] == "date_range" and item["targets"] == [{"entity": "records", …`；L144遍历`zip( plan.entities[0].fields, ("searchable", "filterable", "date_…`；L148断言`coverage_gaps(requirement, plan) == []`。 调用`query_case`、`coverage_gaps`、`any`、`zip`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reference_prose_cannot_erase_an_independent_typed_query_requirement`（L151–L160）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L155断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L156断言`[(item["source"], item["attribute"], item["expected"]) for item in diagnostics] == [ …`；L160断言`coverage_gaps(requirement, plan) == []`。 调用`query_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reference_prose_cannot_authorize_a_query_under_original_source_closure`（L163–L178）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L167断言`coverage_gaps(requirement, plan) == []`；L172断言`any( item["target"] == {"entity": "records", "field": "event_on"} and item["attribute…`。 调用`query_case`、`requirement.features.append`、`"\n".join`、`coverage_gaps`、`requirement.model_copy`、`candidate.features.append`、`analysis_source_conflicts`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_query_attribute_references.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L178。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7712`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_query_attribute_references.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1abbe0b3df99368efab6877fb9719083b544102893c16df810eb0906271e71a2"} -->
````python
# tests/test_query_attribute_references.py
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
````
