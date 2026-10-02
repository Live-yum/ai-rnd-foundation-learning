# tests/test_customer_entity_requirements.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_real_model`、`workbench.domain`、`workbench.entity_requirements`、`workbench.flow`、`workbench.requirement_coverage`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `customer_plan`（L15–L18）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`。 返回路径：L16的`Plan.model_validate_json( (ROOT / "examples/plans/customer-service.json").read_text(encodi…`。
- `inventory`（L21–L34）：接收`plan`、`closed`。 调用`Requirement`、`EntityRequirement`。 返回路径：L22的`Requirement( summary="明确字段清单", users=["管理人员"], data_scope="shared", features=[], acceptanc…`。
- `test_default_open_and_legacy_gate_digest`（L37–L45）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L39断言`item.additional_fields is True`；L43断言`"entity_requirements" not in requirement.gate_dump()`；L44断言`"additional_entities" not in requirement.gate_dump()`；L45断言`not entity_gaps(requirement, customer_plan())`。 调用`EntityRequirement`、`Requirement`、`requirement.gate_dump`、`entity_gaps`、`customer_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_entities_block_only_explicit_closed_entity_inventory`（L48–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52断言`not entity_gaps(approved, plan)`；L55断言`entity_gaps(approved, plan, diagnostics=diagnostics)`；L56断言`diagnostics[0]["code"] == "entity_set"`；L57断言`diagnostics[0]["targets"] == [{"entity": "optional_extra", "field": None}]`。 调用`customer_plan`、`inventory`、`plan.entities.append`、`plan.entities[0].model_copy`、`entity_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_closed_entity_inventory_survives_omission_and_requires_fresh_correction`（L60–L77）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L64断言`reconcile(old.gate_dump(), proposed, []).additional_entities is False`；L76断言`reconcile(old.gate_dump(), corrected, [quote]).additional_entities is True`；L77断言`reconcile(old.gate_dump(), corrected, []).additional_entities is False`。 调用`inventory`、`customer_plan`、`reconcile`、`old.gate_dump`、`proposed.model_dump`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_inventory_schema_rejects_ambiguous_values`（L90–L92）：接收`data`。 调用`pytest.raises`、`EntityRequirement.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_entity_inventory_rejected`（L95–L99）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`inventory(customer_plan()).model_dump`、`inventory`、`customer_plan`、`requirement["entity_requirements"].append`、`pytest.raises`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_inventory_diagnostics_preserve_open_projects`（L104–L130）：接收`closed`、`mutation`。 控制顺序：L108按`mutation == "extra"`分支；L113按`mutation == "missing_field"`分支；L119按`mutation == "extra" and not closed`分支；L120断言`not gaps and not diagnostics`；L122断言`gaps and len(diagnostics) == 1`；L124断言`item["source"] == {"section": "entity_requirements", "index": 0}`；L125断言`item["attribute"] == "fields"`；L126断言`item["additional_fields"] is not closed`。后续分支沿下方源码相同行号继续阅读。 调用`customer_plan`、`inventory`、`target.fields[0].model_copy`、`target.fields.append`、`target.fields.pop`、`plan.entities.pop`、`entity_gaps`、`len`、`sorted`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_same_field_names_are_entity_scoped`（L133–L141）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L140断言`entity_gaps(approved, plan, diagnostics=diagnostics)`；L141断言`diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]`。 调用`customer_plan`、`inventory`、`next`、`entity_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_field_sets_survive_omission_and_model_reopening`（L144–L149）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L147断言`reconcile(old.model_dump(), omitted, []).entity_requirements == old.entity_requiremen…`；L149断言`reconcile(old.model_dump(), reopened, []).entity_requirements == old.entity_requireme…`。 调用`inventory`、`customer_plan`、`old.model_copy`、`reconcile`、`old.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_backed_exact_property_correction`（L159–L176）：接收`attribute`、`replacement`、`quote`。 控制顺序：L171断言`getattr(revised.entity_requirements[0], attribute) == replacement`；L172断言`revised.entity_requirements[1:] == old.entity_requirements[1:]`；L173断言`reconcile(old.model_dump(), Requirement.model_validate(proposed), []).entity_requirem…`。 调用`inventory`、`customer_plan`、`old.model_dump`、`reconcile`、`Requirement.model_validate`、`getattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_model_extra_date_field_blocks_design_and_reaches_repair`（L179–L227）：接收`settings`、`store`。 控制顺序：L212断言`gates[0][1] is False`；L215断言`precise["extra"] == ["published_on"] and precise["missing"] == []`；L216断言`precise["targets"] == [{"entity": "customers", "field": "published_on"}]`；L218断言`seen[0]["previous_plan"] == bad.model_dump()`；L219断言`seen[0]["resolution_feedback"] == outcome["resolution_feedback"]`；L220断言`seen[0]["entity_obligations"][0]["additional_fields"] is False`；L221断言`not coverage_gaps(approved, Plan.model_validate(result["plan"]))`；L224断言`"published_on" in item["actual"] and "published_on" not in item["expected"]`。后续分支沿下方源码相同行号继续阅读。 调用`customer_plan`、`inventory`、`Plan.model_validate_json`、`( ROOT / "tests/fixtures/customer_design_diagnostics/10bd49e/pyth…`、`Workflow`、`Gateway`、`new_run`、`approved.model_dump`、`bad.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_model_extra_date_field_blocks_design_and_reaches_repair.Gateway`（L189–L194）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_actual_model_extra_date_field_blocks_design_and_reaches_repair.Gateway.complete`（L190–L194）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L192断言`schema is Plan`；L193断言`"entity_obligations" in instruction`。 调用`seen.append`、`valid.model_copy`。 返回路径：L194的`valid.model_copy(deep=True)`。
- `test_actual_model_extra_date_field_blocks_design_and_reaches_repair.gate`（L199–L201）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L201的`{"decision": "revise"}`。
- `test_canonical_customer_prompt_explicitly_closes_field_inventory`（L230–L235）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L234断言`"entity_requirements" in text and "additional_fields=false" in text`；L235断言`"穷尽且封闭" in text`。 调用`customer_request`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_entity_requirements.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L235。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9297`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_entity_requirements.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "09ce857347a2aae9a2c96f3ec812b549dbb3068ecdd01a3500370ab9632209ba"} -->
````python
# tests/test_customer_entity_requirements.py
"""Explicit closed inventories block extra fields before generation, with repair data."""

import pytest
from conftest import new_run
from pydantic import ValidationError

from scripts.ci_real_model import SafeFailure, require_customer_spec, safe_coverage_details
from workbench.domain import EntityRequirement, Plan, Requirement
from workbench.entity_requirements import entity_gaps
from workbench.flow import Workflow
from workbench.requirement_coverage import coverage_gaps, reconcile
from workbench.settings import ROOT


def customer_plan():
    return Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )


def inventory(plan, *, closed=True):
    return Requirement(
        summary="明确字段清单",
        users=["管理人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
        entity_requirements=[
            EntityRequirement(
                entity=e.name, fields=[f.name for f in e.fields], additional_fields=not closed
            )
            for e in plan.entities
        ],
    )


def test_default_open_and_legacy_gate_digest():
    item = EntityRequirement(entity="customers", fields=["name"])
    assert item.additional_fields is True
    requirement = Requirement(
        summary="字段", users=[], data_scope="shared", features=[], acceptance=[]
    )
    assert "entity_requirements" not in requirement.gate_dump()
    assert "additional_entities" not in requirement.gate_dump()
    assert not entity_gaps(requirement, customer_plan())


def test_extra_entities_block_only_explicit_closed_entity_inventory():
    plan = customer_plan()
    approved = inventory(plan)
    plan.entities.append(plan.entities[0].model_copy(update={"name": "optional_extra"}, deep=True))
    assert not entity_gaps(approved, plan)
    approved.additional_entities = False
    diagnostics = []
    assert entity_gaps(approved, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "entity_set"
    assert diagnostics[0]["targets"] == [{"entity": "optional_extra", "field": None}]


def test_closed_entity_inventory_survives_omission_and_requires_fresh_correction():
    old = inventory(customer_plan())
    old.additional_entities = False
    proposed = inventory(customer_plan())
    assert reconcile(old.gate_dump(), proposed, []).additional_entities is False
    quote = "将 additional_entities 改为 true，允许新实体"
    proposal = proposed.model_dump()
    proposal["changes"] = [
        {
            "section": "additional_entities",
            "key": "additional_entities",
            "replacement": True,
            "source_quote": quote,
        }
    ]
    corrected = Requirement.model_validate(proposal)
    assert reconcile(old.gate_dump(), corrected, [quote]).additional_entities is True
    assert reconcile(old.gate_dump(), corrected, []).additional_entities is False


@pytest.mark.parametrize(
    "data",
    [
        {"entity": "customers", "fields": []},
        {"entity": "customers", "fields": ["name", "name"]},
        {"entity": "customers", "fields": ["created at"]},
        {"entity": "customers", "fields": ["name"], "additional_fields": "false"},
        {"entity": "customers", "fields": ["name"], "additional_fields": 0},
    ],
)
def test_field_inventory_schema_rejects_ambiguous_values(data):
    with pytest.raises(ValidationError):
        EntityRequirement.model_validate(data)


def test_duplicate_entity_inventory_rejected():
    requirement = inventory(customer_plan()).model_dump()
    requirement["entity_requirements"].append(requirement["entity_requirements"][0])
    with pytest.raises(ValidationError):
        Requirement.model_validate(requirement)


@pytest.mark.parametrize("closed", [True, False])
@pytest.mark.parametrize("mutation", ["extra", "missing_field", "missing_entity"])
def test_exact_inventory_diagnostics_preserve_open_projects(closed, mutation):
    plan = customer_plan()
    approved = inventory(plan, closed=closed)
    target = plan.entities[0]
    if mutation == "extra":
        extra = target.fields[0].model_copy(
            update={"name": "optional_extension", "required": False}
        )
        target.fields.append(extra)
    elif mutation == "missing_field":
        target.fields.pop(0)
    else:
        plan.entities.pop(0)
    diagnostics = []
    gaps = entity_gaps(approved, plan, diagnostics=diagnostics)
    if mutation == "extra" and not closed:
        assert not gaps and not diagnostics
        return
    assert gaps and len(diagnostics) == 1
    item = diagnostics[0]
    assert item["source"] == {"section": "entity_requirements", "index": 0}
    assert item["attribute"] == "fields"
    assert item["additional_fields"] is not closed
    assert item["extra"] == (["optional_extension"] if mutation == "extra" else [])
    assert item["missing"] == (
        [] if mutation == "extra" else sorted(set(item["expected"]) - set(item["actual"]))
    )


def test_same_field_names_are_entity_scoped():
    plan = customer_plan()
    approved = inventory(plan)
    next(e for e in plan.entities if e.name == "tasks").fields = [
        f for f in next(e for e in plan.entities if e.name == "tasks").fields if f.name != "title"
    ]
    diagnostics = []
    assert entity_gaps(approved, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]


def test_approved_field_sets_survive_omission_and_model_reopening():
    old = inventory(customer_plan())
    omitted = old.model_copy(update={"entity_requirements": []}, deep=True)
    assert reconcile(old.model_dump(), omitted, []).entity_requirements == old.entity_requirements
    reopened = inventory(customer_plan(), closed=False)
    assert reconcile(old.model_dump(), reopened, []).entity_requirements == old.entity_requirements


@pytest.mark.parametrize(
    "attribute,replacement,quote",
    [
        ("additional_fields", True, "将 customers.additional_fields 改为 true，允许新增字段"),
        ("fields", ["name", "contact"], "将 customers.fields 改为 name 和 contact"),
    ],
)
def test_source_backed_exact_property_correction(attribute, replacement, quote):
    old = inventory(customer_plan())
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "entity_requirements",
            "key": "customers." + attribute,
            "replacement": replacement,
            "source_quote": quote,
        }
    ]
    revised = reconcile(old.model_dump(), Requirement.model_validate(proposed), [quote])
    assert getattr(revised.entity_requirements[0], attribute) == replacement
    assert revised.entity_requirements[1:] == old.entity_requirements[1:]
    assert (
        reconcile(old.model_dump(), Requirement.model_validate(proposed), []).entity_requirements
        == old.entity_requirements
    )


def test_actual_model_extra_date_field_blocks_design_and_reaches_repair(settings, store):
    valid = customer_plan()
    approved = inventory(valid)
    bad = Plan.model_validate_json(
        (
            ROOT / "tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json"
        ).read_text(encoding="utf-8")
    )
    seen = []

    class Gateway:
        def complete(self, run_id, key, instruction, payload, schema):
            seen.append(payload)
            assert schema is Plan
            assert "entity_obligations" in instruction
            return valid.model_copy(deep=True)

    flow = Workflow(settings, store, Gateway())
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((data, can_approve))
        return {"decision": "revise"}

    flow.gate = gate
    state = {
        "run_id": new_run(store),
        "round": 1,
        "template": "python-basic",
        "requirement": approved.model_dump(),
        "plan": bad.model_dump(),
    }
    outcome = flow.design(state)
    assert gates[0][1] is False
    diagnostics = outcome["resolution_feedback"]["coverage_diagnostics"]
    precise = next(d for d in diagnostics if d["code"] == "entity_field_set")
    assert precise["extra"] == ["published_on"] and precise["missing"] == []
    assert precise["targets"] == [{"entity": "customers", "field": "published_on"}]
    result = flow.plan({**state, **outcome})
    assert seen[0]["previous_plan"] == bad.model_dump()
    assert seen[0]["resolution_feedback"] == outcome["resolution_feedback"]
    assert seen[0]["entity_obligations"][0]["additional_fields"] is False
    assert not coverage_gaps(approved, Plan.model_validate(result["plan"]))
    exported = safe_coverage_details(approved.model_dump(), bad.model_dump())
    item = next(d for d in exported if d["code"] == "entity_field_set")
    assert "published_on" in item["actual"] and "published_on" not in item["expected"]
    with pytest.raises(SafeFailure) as caught:
        require_customer_spec(bad.model_dump())
    assert caught.value.guard_code == "fields_exact"


def test_canonical_customer_prompt_explicitly_closes_field_inventory():
    from scripts.ci_real_model import customer_request

    text = customer_request()
    assert "entity_requirements" in text and "additional_fields=false" in text
    assert "穷尽且封闭" in text
````
