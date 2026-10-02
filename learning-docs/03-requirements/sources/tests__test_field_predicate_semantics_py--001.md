# tests/test_field_predicate_semantics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`、`workbench.requirement_sources`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L15–L40）：接收`text`、`typed`。 调用`Requirement`、`FieldRequirement`、`Plan`。 返回路径：L40的`requirement, plan`。
- `test_bare_mentions_without_affirmative_predicate_do_not_create_fields`（L56–L60）：接收`text`、`typed`。 控制顺序：L59断言`coverage_gaps(requirement, plan) == []`；L60断言`(requirement.model_dump(), plan.model_dump()) == original`。 调用`case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_or_absent_typed_ledger_cannot_hide_positive_extra_field`（L76–L82）：接收`field`、`declaration`、`typed`。 控制顺序：L78断言`coverage_gaps(requirement, plan)`；L82断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`declaration.format`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_explicit_exclusions_remain_binding_in_open_inventory`（L94–L103）：接收`declaration`。 控制顺序：L99断言`coverage_gaps(requirement, plan) == []`；L102断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L103断言`any(d["code"] == "forbidden_field" for d in diagnostics)`。 调用`case`、`EntityRequirement`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_positive_extra_field_and_closed_catalog_are_not_silently_reconciled`（L106–L115）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L112断言`coverage_gaps(requirement, plan)`；L114断言`coverage_gaps(requirement, plan)`；L115断言`requirement.model_dump() == before`。 调用`case`、`EntityRequirement`、`requirement.model_dump`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_source_conflicts_remain_blocking`（L119–L122）：接收`text`。 控制顺序：L122断言`analysis_source_conflicts(None, requirement, [])`。 调用`case`、`analysis_source_conflicts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_user_scalar_conflict_is_still_checked`（L125–L129）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L129断言`any(s["origin"] == "user_input" for d in diagnostics for s in d["sources"])`。 调用`case`、`analysis_source_conflicts`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_declared_catalog_tail_preserves_arbitrary_field_after_descriptor`（L132–L136）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`coverage_gaps(requirement, plan)`；L136断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_existence_predicate_still_requires_its_named_field`（L148–L153）：接收`text`。 控制顺序：L150断言`coverage_gaps(requirement, plan)`；L153断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_fact_field_label_paths_do_not_become_entity_declarations`（L156–L163）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L161断言`coverage_gaps(requirement, plan) == []`；L163断言`coverage_gaps(requirement, plan)`。 调用`case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_field_predicate_semantics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L163。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6281`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_field_predicate_semantics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6fba4a2551d51c2f5f0e86d0e619f8e2e45f6726eb2148f8c85bde2f8eea6427"} -->
````python
# tests/test_field_predicate_semantics.py
"""A bare alias cannot create a field; explicit legacy contracts remain binding.

These are pure coverage/source checks, not executions of diagnostic candidates.
Raw user declarations omitted from every typed/narrative Requirement source are
not claimed to have general semantic completeness validation here.
"""

import pytest

from workbench.domain import EntityRequirement, FieldRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_source_conflicts


def case(text, *, typed=False):
    requirement = Requirement(
        summary="Records",
        users=["staff"],
        data_scope="shared",
        features=[text] if text else [],
        acceptance=[],
        field_requirements=[FieldRequirement(entity="records", field="title", required=True)]
        if typed
        else [],
    )
    plan = Plan(
        title="Records",
        data_scope="shared",
        acceptance=["Store records"],
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "title", "kind": "text", "required": True, "searchable": True},
                ],
            }
        ],
    )
    return requirement, plan


@pytest.mark.parametrize(
    "text",
    [
        "不存在 published_on 或任何额外业务字段，也无遗漏",
        "published_on 的说明",
        "关于 body 的说明",
        "不需要 published_on",
        "没有 published_on",
        "不含 published_on",
        "无需 published_on",
    ],
)
@pytest.mark.parametrize("typed", [False, True])
def test_bare_mentions_without_affirmative_predicate_do_not_create_fields(text, typed):
    requirement, plan = case(text, typed=typed)
    original = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == original


@pytest.mark.parametrize("field", ["published_on", "body", "external_ref", "custom_key"])
@pytest.mark.parametrize(
    "declaration",
    [
        "records: 字段 {field}",
        "records: 字段清单：{field}",
        "records: 必须包含 {field}",
        "records: 不得遗漏 {field}",
        "records.{field} 必填",
        "records: {field}（非必填）",
    ],
)
@pytest.mark.parametrize("typed", [False, True])
def test_partial_or_absent_typed_ledger_cannot_hide_positive_extra_field(field, declaration, typed):
    requirement, plan = case(declaration.format(field=field), typed=typed)
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(
        FieldSpec(name=field, kind="text", required="非必填" not in declaration)
    )
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "declaration",
    [
        "records: 不出现 external_ref",
        "records: 禁止添加 external_ref",
        "records: external_ref 字段不得出现",
        "records: do not include external_ref",
    ],
)
def test_existing_explicit_exclusions_remain_binding_in_open_inventory(declaration):
    requirement, plan = case(declaration)
    requirement.entity_requirements = [
        EntityRequirement(entity="records", fields=["title"], additional_fields=True)
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["code"] == "forbidden_field" for d in diagnostics)


def test_positive_extra_field_and_closed_catalog_are_not_silently_reconciled():
    requirement, plan = case("records: 必须包含 external_ref", typed=True)
    requirement.entity_requirements = [
        EntityRequirement(entity="records", fields=["title"], additional_fields=False)
    ]
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    assert coverage_gaps(requirement, plan)
    assert requirement.model_dump() == before


@pytest.mark.parametrize("text", ["records.title 最长120", "records: title 可选"])
def test_existing_source_conflicts_remain_blocking(text):
    requirement, _ = case(text, typed=True)
    requirement.field_requirements[0].max_length = 200
    assert analysis_source_conflicts(None, requirement, [])


def test_original_user_scalar_conflict_is_still_checked():
    requirement, _ = case("records.title 最长120", typed=True)
    requirement.field_requirements[0].max_length = 120
    diagnostics = analysis_source_conflicts(None, requirement, ["records.title 最长200"], cursor=1)
    assert any(s["origin"] == "user_input" for d in diagnostics for s in d["sources"])


def test_declared_catalog_tail_preserves_arbitrary_field_after_descriptor():
    requirement, plan = case("records: 字段清单：title（必填）、external_ref", typed=True)
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "text",
    [
        "records: published_on 必须存在",
        "records: 必须存在 published_on",
        "records: published_on must exist",
        "records: external_ref 必须存在",
    ],
)
def test_explicit_existence_predicate_still_requires_its_named_field(text):
    requirement, plan = case(text)
    assert coverage_gaps(requirement, plan)
    field = "external_ref" if "external_ref" in text else "published_on"
    plan.entities[0].fields.append(FieldSpec(name=field, kind="text"))
    assert coverage_gaps(requirement, plan) == []


def test_legacy_fact_field_label_paths_do_not_become_entity_declarations():
    requirement, plan = case("")
    plan.entities[0].fields[0].max_length = 250
    plan.entities[0].fields.append(FieldSpec(name="body", kind="text", max_length=3000))
    requirement.facts = {"标题长度上限": "250字符", "正文长度上限": "3000字符"}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 200
    assert coverage_gaps(requirement, plan)
````
