# tests/test_customer_plan_feedback.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.flow`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `windows_fixture_encoding_default`（L14–L23）：接收`monkeypatch`。 源码说明：Exercise Windows' legacy locale on Linux unless the fixture is explicit UTF-8.。 调用`monkeypatch.setattr`、`pytest.fixture`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `windows_fixture_encoding_default.read_text`（L18–L21）：接收`path`、`encoding`、`errors`、`newline`。 控制顺序：L19按`path.name == "customer-service.json" and encoding is None`分支。 调用`original`。 返回路径：L21的`original(path, encoding=encoding, errors=errors, newline=newline)`。
- `test_required_priority_retry_receives_exact_typed_expected_and_actual`（L26–L90）：接收`settings`、`store`。 控制顺序：L70断言`gates[0][0] == "design" and gates[0][2] is False`；L77断言`exact["targets"] == [{"entity": "requests", "field": "priority"}]`；L78断言`exact["attribute"] == "required"`；L79断言`exact["expected"] is True and exact["actual"] is False`；L81断言`seen[0]["resolution_feedback"] == feedback`；L82断言`seen[0]["field_obligations"] == [ { "id": "field_requirements/0", "target": {"entity"…`；L89断言`seen[0]["approved_requirement"] == approved.model_dump()`；L90断言`seen[0]["previous_plan"] == invalid.model_dump()`。 调用`Requirement`、`FieldRequirement`、`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`valid.model_copy`、`next`、`Workflow`、`CaptureGateway`、`new_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_priority_retry_receives_exact_typed_expected_and_actual.CaptureGateway`（L48–L52）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_required_priority_retry_receives_exact_typed_expected_and_actual.CaptureGateway.complete`（L49–L52）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L51断言`schema is Plan and key == "plan:2"`。 调用`seen.append`、`valid.model_copy`。 返回路径：L52的`valid.model_copy(deep=True)`。
- `test_required_priority_retry_receives_exact_typed_expected_and_actual.gate`（L57–L59）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L59的`{"decision": "revise"}`。
- `test_planner_obligation_projection_preserves_scope_false_zero_and_unspecified`（L93–L138）：接收`settings`、`store`。 控制顺序：L125断言`seen[0]["field_obligations"] == [ { "id": "field_requirements/0", "target": {"entity"…`；L137断言`"filterable" not in seen[0]["field_obligations"][1]["expected"]`；L138断言`seen[0]["approved_requirement"] == approved.model_dump()`。 调用`Requirement`、`FieldRequirement`、`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Workflow`、`CaptureGateway`、`flow.plan`、`new_run`、`approved.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_planner_obligation_projection_preserves_scope_false_zero_and_unspecified.CaptureGateway`（L117–L121）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_planner_obligation_projection_preserves_scope_false_zero_and_unspecified.CaptureGateway.complete`（L118–L121）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L120断言`"field_obligations" in instruction`。 调用`seen.append`。 返回路径：L121的`plan`。
- `test_analysis_receives_actual_business_schema_without_rewriting_approved_facts`（L141–L192）：接收`settings`、`store`。 控制顺序：L176断言`"business_contract_schema" in instruction`；L177断言`payload["business_contract_schema"] == BusinessSpec.model_json_schema()`；L178断言`payload["business_contract_schema"]["$defs"]["PermissionSpec"]["properties"]["actions…`；L192断言`outcome["requirement"]["facts"] == approved.facts`。 调用`Requirement`、`Workflow`、`CaptureGateway`、`flow.analyse`、`new_run`、`approved.gate_dump`、`BusinessSpec.model_json_schema`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_receives_actual_business_schema_without_rewriting_approved_facts.CaptureGateway`（L160–L164）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_analysis_receives_actual_business_schema_without_rewriting_approved_facts.CaptureGateway.complete`（L161–L164）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L163断言`schema is Requirement`。 调用`seen.append`、`approved.model_copy`。 返回路径：L164的`approved.model_copy(deep=True)`。
- `test_actual_recorded_business_gap_reaches_planner_with_exact_scope_and_action`（L195–L249）：接收`settings`、`store`。 控制顺序：L230断言`gates[0][0] == "design" and gates[0][2] is False`；L237断言`diagnostic["expected"] == [ {"role": role, "entity": "customers", "action": "read_met…`；L241断言`all( "read_metrics" not in p["actions"] for p in diagnostic["actual"] if p["role"] in…`；L247断言`seen[0]["resolution_feedback"] == feedback`；L248断言`seen[0]["approved_requirement"] == approved.gate_dump()`；L249断言`seen[0]["previous_plan"] == candidate.model_dump()`。 调用`json.loads`、`(ROOT / "tests/fixtures/customer_design_diagnostics/python-basic.…`、`Requirement.model_validate`、`Plan.model_validate`、`Workflow`、`CaptureGateway`、`new_run`、`approved.gate_dump`、`candidate.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_recorded_business_gap_reaches_planner_with_exact_scope_and_action.CaptureGateway`（L207–L212）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_actual_recorded_business_gap_reaches_planner_with_exact_scope_and_action.CaptureGateway.complete`（L208–L212）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L210断言`schema is Plan`；L211断言`"business_diagnostics" in instruction`。 调用`seen.append`、`candidate.model_copy`。 返回路径：L212的`candidate.model_copy(deep=True)`。
- `test_actual_recorded_business_gap_reaches_planner_with_exact_scope_and_action.gate`（L217–L219）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L219的`{"decision": "revise"}`。

</details>

**创建路径：** `tests/test_customer_plan_feedback.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L249。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8549`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_plan_feedback.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ba638b493205444b3671f68f0b198013ff37bede32da37756d905cd2a4d5886e"} -->
````python
# tests/test_customer_plan_feedback.py
"""Deterministic customer obligation feedback reaches the next planner unchanged."""

from pathlib import Path

import pytest
from conftest import new_run

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.flow import Workflow
from workbench.settings import ROOT


@pytest.fixture(autouse=True)
def windows_fixture_encoding_default(monkeypatch):
    """Exercise Windows' legacy locale on Linux unless the fixture is explicit UTF-8."""
    original = Path.read_text

    def read_text(path, encoding=None, errors=None, newline=None):
        if path.name == "customer-service.json" and encoding is None:
            encoding = "cp1252"
        return original(path, encoding=encoding, errors=errors, newline=newline)

    monkeypatch.setattr(Path, "read_text", read_text)


def test_required_priority_retry_receives_exact_typed_expected_and_actual(settings, store):
    approved = Requirement(
        summary="客户服务优先级必须填写",
        users=["服务人员"],
        data_scope="shared",
        features=[],
        acceptance=["服务请求的优先级必填"],
        field_requirements=[FieldRequirement(entity="requests", field="priority", required=True)],
    )
    valid = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    invalid = valid.model_copy(deep=True)
    next(
        field
        for entity in invalid.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "priority"
    ).required = False
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append(payload)
            assert schema is Plan and key == "plan:2"
            return valid.model_copy(deep=True)

    flow = Workflow(settings, store, CaptureGateway())
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((stage, data, can_approve))
        return {"decision": "revise"}

    flow.gate = gate
    state = {
        "run_id": new_run(store),
        "round": 1,
        "template": "python-basic",
        "requirement": approved.model_dump(),
        "plan": invalid.model_dump(),
    }
    outcome = flow.design(state)
    assert gates[0][0] == "design" and gates[0][2] is False
    feedback = outcome["resolution_feedback"]
    exact = next(
        d
        for d in feedback["coverage_diagnostics"]
        if d["source"]["section"] == "field_requirements"
    )
    assert exact["targets"] == [{"entity": "requests", "field": "priority"}]
    assert exact["attribute"] == "required"
    assert exact["expected"] is True and exact["actual"] is False
    flow.plan({**state, **outcome})
    assert seen[0]["resolution_feedback"] == feedback
    assert seen[0]["field_obligations"] == [
        {
            "id": "field_requirements/0",
            "target": {"entity": "requests", "field": "priority"},
            "expected": {"required": True},
        }
    ]
    assert seen[0]["approved_requirement"] == approved.model_dump()
    assert seen[0]["previous_plan"] == invalid.model_dump()


def test_planner_obligation_projection_preserves_scope_false_zero_and_unspecified(settings, store):
    approved = Requirement(
        summary="分实体字段约束",
        users=["服务人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="requests", field="title", required=True, max_length=200),
            FieldRequirement(
                entity="tasks",
                field="title",
                required=False,
                min_length=0,
                max_length=80,
                searchable=False,
            ),
        ],
    )
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append(payload)
            assert "field_obligations" in instruction
            return plan

    flow = Workflow(settings, store, CaptureGateway())
    flow.plan({"run_id": new_run(store), "round": 1, "requirement": approved.model_dump()})
    assert seen[0]["field_obligations"] == [
        {
            "id": "field_requirements/0",
            "target": {"entity": "requests", "field": "title"},
            "expected": {"required": True, "max_length": 200},
        },
        {
            "id": "field_requirements/1",
            "target": {"entity": "tasks", "field": "title"},
            "expected": {"required": False, "min_length": 0, "max_length": 80, "searchable": False},
        },
    ]
    assert "filterable" not in seen[0]["field_obligations"][1]["expected"]
    assert seen[0]["approved_requirement"] == approved.model_dump()


def test_analysis_receives_actual_business_schema_without_rewriting_approved_facts(settings, store):
    from workbench.business_contracts import BusinessSpec

    approved = Requirement(
        summary="保留结构化业务需求",
        users=["服务人员"],
        data_scope="shared",
        facts={
            "business": {
                "permissions": [
                    {"role": "service", "entity": "customers", "actions": ["read"], "scope": "all"}
                ]
            }
        },
        features=[],
        acceptance=[],
    )
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append((instruction, payload))
            assert schema is Requirement
            return approved.model_copy(deep=True)

    flow = Workflow(settings, store, CaptureGateway())
    outcome = flow.analyse(
        {
            "run_id": new_run(store),
            "round": 1,
            "template": "python-basic",
            "requirement": approved.gate_dump(),
        }
    )
    instruction, payload = seen[0]
    assert "business_contract_schema" in instruction
    assert payload["business_contract_schema"] == BusinessSpec.model_json_schema()
    assert payload["business_contract_schema"]["$defs"]["PermissionSpec"]["properties"]["actions"][
        "items"
    ]["enum"] == [
        "create",
        "read",
        "update",
        "archive",
        "assign",
        "transition",
        "add_note",
        "read_history",
        "read_audit",
        "read_metrics",
    ]
    assert outcome["requirement"]["facts"] == approved.facts


def test_actual_recorded_business_gap_reaches_planner_with_exact_scope_and_action(settings, store):
    import json

    recorded = json.loads(
        (ROOT / "tests/fixtures/customer_design_diagnostics/python-basic.json").read_text(
            encoding="utf-8"
        )
    )
    approved = Requirement.model_validate(recorded["requirement"])
    candidate = Plan.model_validate(recorded["candidate_plan"])
    seen = []

    class CaptureGateway:
        def complete(self, run, key, instruction, payload, schema):
            seen.append(payload)
            assert schema is Plan
            assert "business_diagnostics" in instruction
            return candidate.model_copy(deep=True)

    flow = Workflow(settings, store, CaptureGateway())
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((stage, data, can_approve))
        return {"decision": "revise"}

    flow.gate = gate
    state = {
        "run_id": new_run(store),
        "round": 1,
        "template": "python-basic",
        "requirement": approved.gate_dump(),
        "plan": candidate.model_dump(),
    }
    outcome = flow.design(state)
    assert gates[0][0] == "design" and gates[0][2] is False
    feedback = outcome["resolution_feedback"]
    diagnostic = next(
        d
        for d in feedback["business_diagnostics"]
        if d["source"]["path"] == "business.metrics.3.role_scope"
    )
    assert diagnostic["expected"] == [
        {"role": role, "entity": "customers", "action": "read_metrics", "scope": "all"}
        for role in ("manager", "service")
    ]
    assert all(
        "read_metrics" not in p["actions"]
        for p in diagnostic["actual"]
        if p["role"] in {"manager", "service"}
    )
    flow.plan({**state, **outcome})
    assert seen[0]["resolution_feedback"] == feedback
    assert seen[0]["approved_requirement"] == approved.gate_dump()
    assert seen[0]["previous_plan"] == candidate.model_dump()
````
