# tests/test_keyword_query_binding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `query_case`（L18–L57）：接收`text`。 调用`Requirement`、`FieldRequirement`、`Plan`。 返回路径：L57的`requirement, plan`。
- `test_keyword_shorthand_keeps_exact_filters_on_their_own_fields`（L61–L67）：接收`text`。 控制顺序：L65断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L66断言`diagnostics == []`；L67断言`(requirement.model_dump(), plan.model_dump()) == original`。 调用`query_case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_keyword_shorthand_still_requires_every_named_query_field`（L80–L91）：接收`text`、`name`、`flag`。 控制顺序：L85断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L86断言`any( item["code"] == "uncovered_operation" and item["attribute"] == flag and {"entity…`。 调用`query_case`、`next`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_keyword_shorthand_does_not_override_an_explicit_false_filter`（L94–L102）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L98断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L99断言`[ (item["code"], item["source"]["section"], item["attribute"], item["expected"]) for …`。 调用`query_case`、`next`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_disabled_keyword_queries_remain_disabled`（L106–L120）：接收`keyword`。 控制顺序：L111断言`coverage_gaps(requirement, plan) == []`；L114断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L115断言`any( item["attribute"] == "searchable" and item["expected"] is False and item["target…`。 调用`query_case`、`next`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_keyword_descriptions_and_query_outputs_do_not_add_capabilities`（L132–L137）：接收`text`。 控制顺序：L134遍历`plan.entities[0].fields`；L137断言`coverage_gaps(requirement, plan) == []`。 调用`query_case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_keyword_query_binding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L137。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5004`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_keyword_query_binding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1758529fff8c03229690fd6cdb53c4047ee3b12e1ed83867299a19f9d5434512"} -->
````python
# tests/test_keyword_query_binding.py
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
````
