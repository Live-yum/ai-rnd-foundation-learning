# tests/test_query_obligation_pairing.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recorded`（L23–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L25断言`d["approval_status"] == "unapproved"`；L26断言`d["execution_authorized"] is False`；L27断言`d["purpose"] == "offline_contract_validation_only"`。 调用`json.loads`、`(FIXTURES / "fastapi-unapproved-design.json").read_bytes`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L28的`Requirement.model_validate(d["requirement"]), Plan.model_validate(d["candidate_plan"])`。
- `test_recorded_failure_and_input_are_byte_exact`（L32–L39）：接收`name`、`digest`。 控制顺序：L33断言`hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest`；L35断言`summary["passed"] is False`；L36断言`summary["failure_details"]["coverage_block_count"] == 3`；L37断言`{d["code"] for d in summary["failure_details"]["coverage_sources"]} == { "uncovered_o…`。 调用`hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest`、`hashlib.sha256`、`(FIXTURES / name).read_bytes`、`json.loads`、`(FIXTURES / "fastapi-summary.json").read_bytes`、`pytest.mark.parametrize`、`HASHES.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_recorded_mixed_queries_do_not_override_typed_pairs`（L42–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L46断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L47断言`diagnostics == []`；L48断言`(requirement.model_dump(), plan.model_dump()) == before`；L49遍历`("name", "organization", "contact")`；L51断言`field.filterable is None`。 调用`recorded`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `typed_cases`（L54–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`recorded`、`enumerate`、`getattr`。 返回路径：L56的`[ (i, flag) for i, field in enumerate(requirement.field_requirements) for flag in FLAGS if…`。
- `test_every_explicit_typed_query_value_remains_binding`（L65–L78）：接收`index`、`flag`。 控制顺序：L72断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L73断言`any( d["source"] == {"section": "field_requirements", "index": index} and d["attribut…`。 调用`recorded`、`next`、`setattr`、`getattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`、`typed_cases`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `case`（L81–L117）：接收`text`、`typed`。 调用`Plan`、`Requirement`、`FieldRequirement`。 返回路径：L117的`requirement, plan`。
- `test_prefix_suffix_lists_and_clause_order_keep_independent_pairs`（L134–L144）：接收`text`、`typed`。 控制顺序：L136断言`coverage_gaps(requirement, plan) == []`；L137遍历`( ("short_text", "searchable"), ("long_text", "searchable"), ("pr…`；L144断言`coverage_gaps(requirement, changed)`。 调用`case`、`coverage_gaps`、`plan.model_copy`、`setattr`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_true_false_none_and_missing_typed_values_are_not_conflated`（L158–L177）：接收`typed`、`prose`、`actual`、`flag`、`operation`、`kind`。 控制顺序：L163按`typed != "absent"`分支；L169按`kind == "date"`分支；L175断言`bool(gaps) is not expected`；L176按`typed in (None, "absent") and actual is not prose`分支；L177断言`any(d["source"]["section"] == "features" for d in diagnostics)`。 调用`case`、`FieldRequirement`、`setattr`、`coverage_gaps`、`bool`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_another_typed_property_does_not_suppress_an_uncovered_query`（L180–L186）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L182断言`requirement.field_requirements[0].searchable is True`；L183断言`requirement.field_requirements[0].filterable is None`；L184断言`coverage_gaps(requirement, plan)`；L186断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_local_group_inherits_the_explicit_entity_without_fanning_out`（L196–L214）：接收`text`。 控制顺序：L199遍历`archive.fields`；L203断言`coverage_gaps(requirement, plan) == []`；L204遍历`(("short_text", "searchable"), ("priority", "filterable"))`；L208断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L209断言`any( d["attribute"] == flag and any(t == {"entity": "records", "field": name} for t i…`；L214断言`all(t["entity"] == "records" for d in diagnostics for t in d["targets"])`。 调用`case`、`plan.entities[0].model_copy`、`plan.entities.append`、`coverage_gaps`、`plan.model_copy`、`setattr`、`next`、`any`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_query_obligation_pairing.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L214。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8388`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_query_obligation_pairing.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "93339b3cae57095d95bd725e23a3ff966ceeb813086bbc4071e76f66be40cd91"} -->
````python
# tests/test_query_obligation_pairing.py
"""Field × query-property pairing, using typed facts before a legacy fallback.

The recorded candidate is unapproved and used only by pure validators.
"""

import hashlib
import json
from pathlib import Path

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps

FIXTURES = Path(__file__).parent / "fixtures/customer_design_diagnostics/d3ea684"
HASHES = {
    "fastapi-unapproved-design.json": "142534113f2fbf6a0f1dd6e1593279aac23ca2468ba733dab08cc85a9a6a9d4e",
    "fastapi-summary.json": "88434c888fb9a6dbe2f219f711163c2819ce72dce9c4ed6f1acaa33267f3ea76",
}
FLAGS = ("searchable", "filterable", "date_range")


def recorded():
    d = json.loads((FIXTURES / "fastapi-unapproved-design.json").read_bytes())
    assert d["approval_status"] == "unapproved"
    assert d["execution_authorized"] is False
    assert d["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(d["requirement"]), Plan.model_validate(d["candidate_plan"])


@pytest.mark.parametrize("name,digest", HASHES.items())
def test_recorded_failure_and_input_are_byte_exact(name, digest):
    assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest
    summary = json.loads((FIXTURES / "fastapi-summary.json").read_bytes())
    assert summary["passed"] is False
    assert summary["failure_details"]["coverage_block_count"] == 3
    assert {d["code"] for d in summary["failure_details"]["coverage_sources"]} == {
        "uncovered_operation"
    }


def test_exact_recorded_mixed_queries_do_not_override_typed_pairs():
    requirement, plan = recorded()
    before = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    for name in ("name", "organization", "contact"):
        field = next(f for f in requirement.field_requirements if f.field == name)
        assert field.filterable is None


def typed_cases():
    requirement, _ = recorded()
    return [
        (i, flag)
        for i, field in enumerate(requirement.field_requirements)
        for flag in FLAGS
        if getattr(field, flag) is not None
    ]


@pytest.mark.parametrize("index,flag", typed_cases())
def test_every_explicit_typed_query_value_remains_binding(index, flag):
    requirement, plan = recorded()
    expected = requirement.field_requirements[index]
    entity = next(e for e in plan.entities if e.name == expected.entity)
    field = next(f for f in entity.fields if f.name == expected.field)
    setattr(field, flag, not getattr(expected, flag))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["source"] == {"section": "field_requirements", "index": index}
        and d["attribute"] == flag
        and d["expected"] is getattr(expected, flag)
        for d in diagnostics
    )


def case(text, *, typed=True):
    plan = Plan(
        title="Record queries",
        data_scope="shared",
        acceptance=["Query records"],
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "short_text", "kind": "text", "searchable": True},
                    {"name": "long_text", "kind": "text", "searchable": True},
                    {
                        "name": "priority",
                        "kind": "enum",
                        "choices": ["low", "high"],
                        "filterable": True,
                    },
                ],
            }
        ],
    )
    requirement = Requirement(
        summary="Record queries",
        users=["staff"],
        data_scope="shared",
        features=[text],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="records", field="short_text", searchable=True),
            FieldRequirement(entity="records", field="long_text", searchable=True),
            FieldRequirement(entity="records", field="priority", searchable=False, filterable=True),
        ]
        if typed
        else [],
    )
    return requirement, plan


@pytest.mark.parametrize("typed", [True, False])
@pytest.mark.parametrize(
    "text",
    [
        "records: 关键词搜索覆盖 short_text/long_text，priority 精确筛选",
        "records: short_text/long_text 关键词搜索，priority 精确筛选",
        "records: 关键词搜索 short_text、long_text，精确筛选 priority",
        "records: search short_text, long_text, filter priority",
        "records: short_text, long_text search, priority filter",
        "records: priority filter, search short_text, long_text",
        "records: filter priority, short_text and long_text search",
        "records: short_text/long_text 搜索；priority 精确筛选",
    ],
)
def test_prefix_suffix_lists_and_clause_order_keep_independent_pairs(text, typed):
    requirement, plan = case(text, typed=typed)
    assert coverage_gaps(requirement, plan) == []
    for name, flag in (
        ("short_text", "searchable"),
        ("long_text", "searchable"),
        ("priority", "filterable"),
    ):
        changed = plan.model_copy(deep=True)
        setattr(next(f for f in changed.entities[0].fields if f.name == name), flag, False)
        assert coverage_gaps(requirement, changed)


@pytest.mark.parametrize("typed", [True, False, None, "absent"])
@pytest.mark.parametrize("prose", [True, False])
@pytest.mark.parametrize("actual", [True, False])
@pytest.mark.parametrize(
    "flag,operation,kind",
    [
        ("searchable", "搜索", "text"),
        ("filterable", "精确筛选", "text"),
        ("date_range", "日期范围查询", "date"),
    ],
)
def test_true_false_none_and_missing_typed_values_are_not_conflated(
    typed, prose, actual, flag, operation, kind
):
    text = "records: short_text " + ("必须" if prose else "禁止") + operation
    requirement, plan = case(text, typed=False)
    if typed != "absent":
        requirement.field_requirements = [
            FieldRequirement(entity="records", field="short_text", required=True, **{flag: typed})
        ]
    field = plan.entities[0].fields[0]
    field.kind = kind
    if kind == "date":
        field.searchable = False
    setattr(field, flag, actual)
    diagnostics = []
    gaps = coverage_gaps(requirement, plan, diagnostics=diagnostics)
    expected = actual is prose and (typed in (None, "absent") or typed is actual)
    assert bool(gaps) is not expected
    if typed in (None, "absent") and actual is not prose:
        assert any(d["source"]["section"] == "features" for d in diagnostics)


def test_another_typed_property_does_not_suppress_an_uncovered_query():
    requirement, plan = case("records: short_text 必须精确筛选")
    assert requirement.field_requirements[0].searchable is True
    assert requirement.field_requirements[0].filterable is None
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].filterable = True
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "text",
    [
        "records: search short_text, long_text, filter priority",
        "records: filter priority, short_text and long_text search",
    ],
)
def test_each_local_group_inherits_the_explicit_entity_without_fanning_out(text):
    requirement, plan = case(text, typed=False)
    archive = plan.entities[0].model_copy(deep=True, update={"name": "archive"})
    for field in archive.fields:
        field.searchable = False
        field.filterable = False
    plan.entities.append(archive)
    assert coverage_gaps(requirement, plan) == []
    for name, flag in (("short_text", "searchable"), ("priority", "filterable")):
        changed = plan.model_copy(deep=True)
        setattr(next(f for f in changed.entities[0].fields if f.name == name), flag, False)
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            d["attribute"] == flag
            and any(t == {"entity": "records", "field": name} for t in d["targets"])
            for d in diagnostics
        )
        assert all(t["entity"] == "records" for d in diagnostics for t in d["targets"])
````
