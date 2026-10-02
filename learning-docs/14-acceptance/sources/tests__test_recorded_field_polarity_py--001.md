# tests/test_recorded_field_polarity.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`、`workbench.requirement_coverage`、`workbench.requirement_sources`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recorded_case`（L21–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23断言`envelope["format"] == "customer-design-diagnostic-v1"`；L24断言`envelope["approval_status"] == "unapproved"`；L25断言`envelope["execution_authorized"] is False`；L26断言`envelope["purpose"] == "offline_contract_validation_only"`。 调用`json.loads`、`(FIXTURES / "python-unapproved-design.json").read_bytes`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L27的`Requirement.model_validate(envelope["requirement"]), Plan.model_validate( envelope["candid…`。
- `test_recorded_inputs_are_unchanged_and_original_failure_remains_visible`（L33–L47）：接收`filename`、`expected`。 控制顺序：L34断言`hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest() == expected`；L36断言`summary["passed"] is False`；L37断言`summary["failure_code"] == "workflow_not_ready"`；L38断言`summary["run_identity"] == [ "36881018319", "1", "76ca70b2efedfc81e10637f3f93d58e1eca…`；L44断言`len(sources) == 1`；L45断言`sources[0]["code"] == "legacy_missing_field"`；L46断言`sources[0]["source"] == {"section": "acceptance", "index": 1, "clause": 3}`；L47断言`"不存在 published_on 或任何额外业务字段，也无遗漏" in sources[0]["source_excerpt"]`。 调用`hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest`、`hashlib.sha256`、`(FIXTURES / filename).read_bytes`、`json.loads`、`(FIXTURES / "python-summary.json").read_bytes`、`len`、`pytest.mark.parametrize`、`HASHES.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_unapproved_candidate_has_no_spurious_obligation_without_any_mutation`（L50–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L54断言`len(requirement.field_requirements) == 19`；L55断言`len(requirement.entity_requirements) == 3`；L56断言`requirement.additional_entities is False`；L57断言`all(not item.additional_fields for item in requirement.entity_requirements)`；L58断言`entity_gaps(requirement, plan) == []`；L59断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L60断言`diagnostics == []`；L61断言`analysis_source_conflicts(None, requirement, []) == []`。后续分支沿下方源码相同行号继续阅读。 调用`recorded_case`、`requirement.model_dump`、`plan.model_dump`、`len`、`all`、`entity_gaps`、`coverage_gaps`、`analysis_source_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_recorded_typed_field_remains_required_to_exist`（L66–L78）：接收`index`。 控制顺序：L72断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L73断言`any( item["code"] == "missing_or_ambiguous" and item["source"] == {"section": "field_…`；L78断言`entity_gaps(requirement, plan)`。 调用`recorded_case`、`next`、`coverage_gaps`、`any`、`entity_gaps`、`pytest.mark.parametrize`、`range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `mutation_cases`（L81–L88）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`recorded_case`、`enumerate`、`obligation.model_dump(exclude_none=True).items`、`obligation.model_dump`。 返回路径：L83的`[ (index, attribute) for index, obligation in enumerate(requirement.field_requirements) fo…`。
- `test_every_recorded_typed_constraint_stays_strict`（L92–L117）：接收`index`、`attribute`。 控制顺序：L98按`type(expected) is bool`分支；L100按`type(expected) is int`分支；L102按`attribute == "choices"`分支；L105断言`attribute == "kind"`；L109断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L110断言`any( item["code"] == "constraint_mismatch" and item["source"] == {"section": "field_r…`。 调用`recorded_case`、`next`、`getattr`、`type`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`、`mutation_cases`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_closed_catalog_cannot_be_reopened_by_narrative`（L122–L128）：接收`index`、`mutation`。 控制顺序：L124按`mutation == "extra_field"`分支；L128断言`entity_gaps(requirement, plan)`。 调用`recorded_case`、`plan.entities[index].fields.append`、`FieldSpec`、`plan.entities.pop`、`entity_gaps`、`pytest.mark.parametrize`、`range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_closed_entity_set_rejects_additional_entity`（L131–L134）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`entity_gaps(requirement, plan)`。 调用`recorded_case`、`plan.entities.append`、`plan.entities[0].model_copy`、`entity_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_inventory_absence_and_completeness_do_not_create_a_positive`（L149–L156）：接收`negative`、`completeness`。 控制顺序：L155断言`coverage_gaps(requirement, plan) == []`；L156断言`entity_gaps(requirement, plan) == []`。 调用`recorded_case`、`requirement.acceptance[1].rsplit`、`coverage_gaps`、`entity_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_recorded_field_polarity.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L156。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6485`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_recorded_field_polarity.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "35f82cf93d7bbf2434281791d625494d66887d465ea5477fb8380764d27eed92"} -->
````python
# tests/test_recorded_field_polarity.py
"""Pure validation of the recorded 76ca candidate, never approval or execution."""

import hashlib
import json
from pathlib import Path

import pytest

from workbench.domain import FieldSpec, Plan, Requirement
from workbench.entity_requirements import entity_gaps
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_source_conflicts

FIXTURES = Path(__file__).parent / "fixtures/customer_design_diagnostics/76ca70b"
HASHES = {
    "python-unapproved-design.json": "293da0b8cde09658f618ac76328eb1393b1d3eb79193456a419170adae1b4ecc",
    "python-summary.json": "3ada405998d4af9df24020c8eaff05ec428471ebb0caa0104757bb6758403ef9",
}


def recorded_case():
    envelope = json.loads((FIXTURES / "python-unapproved-design.json").read_bytes())
    assert envelope["format"] == "customer-design-diagnostic-v1"
    assert envelope["approval_status"] == "unapproved"
    assert envelope["execution_authorized"] is False
    assert envelope["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(envelope["requirement"]), Plan.model_validate(
        envelope["candidate_plan"]
    )


@pytest.mark.parametrize("filename,expected", HASHES.items())
def test_recorded_inputs_are_unchanged_and_original_failure_remains_visible(filename, expected):
    assert hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest() == expected
    summary = json.loads((FIXTURES / "python-summary.json").read_bytes())
    assert summary["passed"] is False
    assert summary["failure_code"] == "workflow_not_ready"
    assert summary["run_identity"] == [
        "36881018319",
        "1",
        "76ca70b2efedfc81e10637f3f93d58e1eca480c1",
    ]
    sources = summary["failure_details"]["coverage_sources"]
    assert len(sources) == 1
    assert sources[0]["code"] == "legacy_missing_field"
    assert sources[0]["source"] == {"section": "acceptance", "index": 1, "clause": 3}
    assert "不存在 published_on 或任何额外业务字段，也无遗漏" in sources[0]["source_excerpt"]


def test_exact_unapproved_candidate_has_no_spurious_obligation_without_any_mutation():
    requirement, plan = recorded_case()
    before = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert len(requirement.field_requirements) == 19
    assert len(requirement.entity_requirements) == 3
    assert requirement.additional_entities is False
    assert all(not item.additional_fields for item in requirement.entity_requirements)
    assert entity_gaps(requirement, plan) == []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert analysis_source_conflicts(None, requirement, []) == []
    assert (requirement.model_dump(), plan.model_dump()) == before


@pytest.mark.parametrize("index", range(19))
def test_every_recorded_typed_field_remains_required_to_exist(index):
    requirement, plan = recorded_case()
    obligation = requirement.field_requirements[index]
    entity = next(item for item in plan.entities if item.name == obligation.entity)
    entity.fields = [field for field in entity.fields if field.name != obligation.field]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "missing_or_ambiguous"
        and item["source"] == {"section": "field_requirements", "index": index}
        for item in diagnostics
    )
    assert entity_gaps(requirement, plan)


def mutation_cases():
    requirement, _ = recorded_case()
    return [
        (index, attribute)
        for index, obligation in enumerate(requirement.field_requirements)
        for attribute, value in obligation.model_dump(exclude_none=True).items()
        if attribute not in {"entity", "field"}
    ]


@pytest.mark.parametrize("index,attribute", mutation_cases())
def test_every_recorded_typed_constraint_stays_strict(index, attribute):
    requirement, plan = recorded_case()
    obligation = requirement.field_requirements[index]
    entity = next(item for item in plan.entities if item.name == obligation.entity)
    field = next(item for item in entity.fields if item.name == obligation.field)
    expected = getattr(obligation, attribute)
    if type(expected) is bool:
        replacement = not expected
    elif type(expected) is int:
        replacement = expected + 1
    elif attribute == "choices":
        replacement = expected + ["extra-synthetic-choice"]
    else:
        assert attribute == "kind"
        replacement = "text" if expected != "text" else "integer"
    setattr(field, attribute, replacement)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "constraint_mismatch"
        and item["source"] == {"section": "field_requirements", "index": index}
        and item["attribute"] == attribute
        and item["expected"] == expected
        and item["actual"] == replacement
        for item in diagnostics
    )


@pytest.mark.parametrize("index", range(3))
@pytest.mark.parametrize("mutation", ["extra_field", "missing_entity"])
def test_recorded_closed_catalog_cannot_be_reopened_by_narrative(index, mutation):
    requirement, plan = recorded_case()
    if mutation == "extra_field":
        plan.entities[index].fields.append(FieldSpec(name="published_on", kind="date"))
    else:
        plan.entities.pop(index)
    assert entity_gaps(requirement, plan)


def test_recorded_closed_entity_set_rejects_additional_entity():
    requirement, plan = recorded_case()
    plan.entities.append(plan.entities[0].model_copy(deep=True, update={"name": "extra"}))
    assert entity_gaps(requirement, plan)


@pytest.mark.parametrize(
    "negative",
    [
        "不存在 published_on",
        "不含 published_on",
        "不包含 published_on",
        "没有 published_on 字段",
        "禁止添加 published_on 字段",
        "published_on 字段不得存在",
    ],
)
@pytest.mark.parametrize("completeness", ["", "，也无遗漏", "，没有遗漏任何明确字段"])
def test_recorded_inventory_absence_and_completeness_do_not_create_a_positive(
    negative, completeness
):
    requirement, plan = recorded_case()
    heading = requirement.acceptance[1].rsplit("；", 1)[0]
    requirement.acceptance[1] = heading + "；" + negative + completeness + "。"
    assert coverage_gaps(requirement, plan) == []
    assert entity_gaps(requirement, plan) == []
````
