# tests/test_entity_field_fact_inventory.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L12–L56）：接收`typed`。 调用`Plan`、`Requirement`、`EntityRequirement`。 返回路径：L56的`requirement, plan`。
- `test_grouped_field_names_are_scoped_presence_obligations`（L61–L76）：接收`shape`、`typed`。 控制顺序：L64按`shape == "json"`分支；L66按`shape == "nested"`分支；L68按`shape == "resources"`分支；L75断言`coverage_gaps(requirement, plan) == []`；L76断言`requirement.model_dump() == original`。 调用`case`、`json.dumps`、`value["fields"].items`、`copy.deepcopy`、`requirement.model_dump`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_inventory_members_cannot_borrow_another_entity`（L80–L98）：接收`missing`。 控制顺序：L82按`missing == "entity"`分支；L86按`missing == "wrong_owner"`分支；L89断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L90断言`any( d["code"] == "structured_missing_field" and d["source"]["path"] == "arbitrary_le…`；L95断言`not any( d["code"] == "structured_missing_field" and d["source"]["path"].endswith("fi…`。 调用`case`、`plan.entities.pop`、`plan.entities[1].fields.append`、`FieldSpec`、`coverage_gaps`、`any`、`d["source"]["path"].endswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_grouped_descriptors_preserve_explicit_constraints`（L102–L121）：接收`declaration`。 控制顺序：L110断言`coverage_gaps(requirement, plan) == []`；L113断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L114断言`any( d["code"] == "constraint_mismatch" and d["targets"] == [{"entity": "alpha", "fie…`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_grouped_inventory_is_not_an_empty_success`（L125–L128）：接收`members`。 控制顺序：L128断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bare_enum_choices_keep_their_meaning_when_a_field_matches_an_entity_name`（L131–L141）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L137断言`coverage_gaps(requirement, plan) == []`；L140断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L141断言`any(d["attribute"] == "choices" for d in diagnostics)`。 调用`case`、`plan.entities[1].fields.append`、`FieldSpec`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_display_field_maps_do_not_become_inventory_obligations`（L144–L148）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L148断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`plan.entities.pop`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_entity_field_fact_inventory.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L148。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5370`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_entity_field_fact_inventory.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9d3ae63c0d2105c9f5c50df8adcdd087773f3427ff1a674e2f897a6c717affcf"} -->
````python
# tests/test_entity_field_fact_inventory.py
"""Entity-grouped field facts keep presence, scope and enum obligations distinct."""

import copy
import json

import pytest

from workbench.domain import EntityRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def case(*, typed=True):
    plan = Plan(
        title="Grouped field declarations",
        data_scope="per_user",
        entities=[
            {
                "name": "alpha",
                "description": "First resource",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80},
                    {"name": "category", "kind": "enum", "choices": ["first", "second"]},
                ],
            },
            {
                "name": "beta",
                "description": "Second resource",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80},
                    {"name": "note", "kind": "text", "required": False},
                ],
            },
        ],
        acceptance=["Declared fields remain present"],
    )
    requirement = Requirement(
        summary="Grouped field declarations",
        data_scope="per_user",
        users=[],
        features=[],
        acceptance=[],
        entity_requirements=[
            EntityRequirement(
                entity=e.name, fields=[f.name for f in e.fields], additional_fields=False
            )
            for e in plan.entities
        ]
        if typed
        else [],
        facts={
            "arbitrary_ledger": {
                "fields": {"alpha": ["title", "category"], "beta": ["title", "note"]}
            }
        },
    )
    return requirement, plan


@pytest.mark.parametrize("shape", ["native", "json", "nested", "resources"])
@pytest.mark.parametrize("typed", [True, False])
def test_grouped_field_names_are_scoped_presence_obligations(shape, typed):
    requirement, plan = case(typed=typed)
    value = requirement.facts["arbitrary_ledger"]
    if shape == "json":
        requirement.facts["arbitrary_ledger"] = json.dumps(value)
    elif shape == "nested":
        requirement.facts = {"wrapper": [{"details": json.dumps(value)}]}
    elif shape == "resources":
        requirement.facts = {
            "resources": [
                {"name": entity, "fields": fields} for entity, fields in value["fields"].items()
            ]
        }
    original = copy.deepcopy(requirement.model_dump())
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == original


@pytest.mark.parametrize("missing", ["field", "entity", "wrong_owner"])
def test_missing_inventory_members_cannot_borrow_another_entity(missing):
    requirement, plan = case()
    if missing == "entity":
        plan.entities.pop(0)
    else:
        plan.entities[0].fields = [f for f in plan.entities[0].fields if f.name != "title"]
        if missing == "wrong_owner":
            plan.entities[1].fields.append(FieldSpec(name="unrelated", kind="text"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["code"] == "structured_missing_field"
        and d["source"]["path"] == "arbitrary_ledger.fields.alpha.0"
        for d in diagnostics
    )
    assert not any(
        d["code"] == "structured_missing_field" and d["source"]["path"].endswith("fields.beta.0")
        for d in diagnostics
    )


@pytest.mark.parametrize("declaration", ["fields", "field_constraints"])
def test_grouped_descriptors_preserve_explicit_constraints(declaration):
    requirement, plan = case()
    requirement.facts = {
        declaration: {
            "alpha": {"title": {"required": True, "max_length": 80}},
            "beta": [{"field": "note", "required": False}],
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 81
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["code"] == "constraint_mismatch"
        and d["targets"] == [{"entity": "alpha", "field": "title"}]
        and d["attribute"] == "max_length"
        and d["expected"] == 80
        and d["actual"] == 81
        for d in diagnostics
    )


@pytest.mark.parametrize("members", [[], [None], [3], ["bad field"], [{"field": None}]])
def test_malformed_grouped_inventory_is_not_an_empty_success(members):
    requirement, plan = case()
    requirement.facts = {"fields": {"alpha": members}}
    assert coverage_gaps(requirement, plan)


def test_bare_enum_choices_keep_their_meaning_when_a_field_matches_an_entity_name():
    requirement, plan = case(typed=False)
    plan.entities[1].fields.append(
        FieldSpec(name="alpha", kind="enum", choices=["first", "second"])
    )
    requirement.facts = {"fields": {"alpha": ["first", "second"]}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[-1].choices = ["first", "third"]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["attribute"] == "choices" for d in diagnostics)


def test_display_field_maps_do_not_become_inventory_obligations():
    requirement, plan = case(typed=False)
    requirement.facts = {"presentation": requirement.facts}
    plan.entities.pop(0)
    assert coverage_gaps(requirement, plan) == []
````
