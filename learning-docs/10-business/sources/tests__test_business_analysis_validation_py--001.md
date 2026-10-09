# tests/test_business_analysis_validation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.domain`、`workbench.flow`、`workbench.requirement_sources`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `candidate`（L17–L26）：接收`actions`。 调用`requirement`。 返回路径：L26的`result`。
- `test_malformed_business_facts_are_rejected_before_design_without_rewriting`（L34–L57）：接收`plan`、`actions`、`encoding`。 控制顺序：L38按`encoding == "json"`分支；L40按`encoding == "nested"`分支；L44断言`len(diagnostics) == 1`；L45断言`diagnostics[0]["code"] == "requirement_business_shape"`；L46断言`diagnostics[0]["target"] == {"entity": "task", "field": None}`；L47断言`diagnostics[0]["attribute"] == "permissions"`；L49断言`source["source"]["path"].endswith("business.permissions.0")`；L50断言`source["expected"]["actions"] == actions`。后续分支沿下方源码相同行号继续阅读。 调用`candidate`、`json.dumps`、`value.model_dump`、`business_analysis_conflicts`、`len`、`source["source"]["path"].endswith`、`business_gaps`、`analysis_feedback`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restrictions_share_the_same_known_action_grammar`（L61–L67）：接收`plan`、`key`。 控制顺序：L64断言`business_analysis_conflicts(value)`；L66断言`business_gaps(value, plan, diagnostics=diagnostics)`；L67断言`diagnostics[0]["code"] == "business_unsupported_shape"`。 调用`candidate`、`business_analysis_conflicts`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_known_aliases_and_partial_restrictions_remain_valid_and_unchanged`（L70–L79）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76断言`business_analysis_conflicts(value) == []`；L77断言`value.model_dump() == before`；L79断言`business_analysis_conflicts(value)`。 调用`candidate`、`descriptor.update`、`value.model_dump`、`business_analysis_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_personal_scope_cannot_approve_facts_that_require_a_shared_business_plan`（L93–L107）：接收`plan`、`domain`、`descriptor`。 控制顺序：L100断言`len(diagnostics) == 1`；L101断言`diagnostics[0]["code"] == "requirement_business_scope"`；L102断言`"per_user" in diagnostics[0]["sources"][0]["text"]`；L103断言`business_gaps(value, plan)`；L104断言`value.model_dump() == before`；L105遍历`("shared", "unknown")`；L107断言`business_analysis_conflicts(value) == []`。 调用`requirement`、`value.model_dump`、`business_analysis_conflicts`、`len`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_executable_partial_metadata_does_not_create_a_scope_conflict`（L110–L116）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L116断言`business_analysis_conflicts(value) == []`。 调用`requirement`、`business_analysis_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_retained_fact_provenance_requires_same_path_and_exact_typed_descriptor`（L119–L135）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L123断言`source["origin"] == "previous_requirement"`；L124断言`source["previous_source"] == source["source"]`；L125断言`source["user_sources"] == []`；L127断言`feedback[0]["sources"][0]["previous_source"] == source["source"]`；L130断言`source["origin"] == "model_analysis"`；L131断言`"previous_source" not in source`；L135断言`source["origin"] == "model_analysis"`。 调用`candidate`、`old.model_copy`、`business_analysis_conflicts`、`old.gate_dump`、`analysis_feedback`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_cannot_remove_previously_approved_invalid_facts_by_omission`（L138–L165）：接收`settings`、`store`、`plan`。 控制顺序：L158断言`state == before`；L159断言`result["requirement"] == old.gate_dump()`；L160断言`result["requirement_analysis_baseline"] == old.gate_dump()`；L161断言`result["requirement_source_count"] == 1`；L163断言`source["origin"] == "previous_requirement"`；L164断言`source["previous_source"]["path"] == "business.permissions.0"`；L165断言`result["requirement_ledger"][-1]["after"] == old.gate_dump()`。 调用`candidate`、`new_run`、`old.gate_dump`、`json.loads`、`json.dumps`、`Workflow(settings, store, Omitted(plan)).analyse`、`Workflow`、`Omitted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_cannot_remove_previously_approved_invalid_facts_by_omission.Omitted`（L143–L146）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_analysis_cannot_remove_previously_approved_invalid_facts_by_omission.Omitted.complete`（L144–L146）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L145断言`schema is Requirement`。 调用`requirement`。 返回路径：L146的`requirement()`。
- `test_shared_business_grammar_checks_other_domains_without_plan_or_field_guessing`（L168–L181）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L181断言`{item["attribute"] for item in diagnostics} == {"relations", "resources", "workflows"…`。 调用`requirement`、`business_analysis_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_personal_crud_and_display_metadata_do_not_invent_business_obligations`（L184–L195）：接收`plan`。 控制顺序：L193断言`business_analysis_conflicts(value) == []`；L194断言`business_gaps(value, plan) == []`；L195断言`value.model_dump() == before`。 调用`requirement`、`value.model_dump`、`business_analysis_conflicts`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_invalid_analysis_uses_existing_clarification_budget_before_plan`（L198–L233）：接收`settings`、`store`、`plan`。 控制顺序：L220断言`result["status"] == "BLOCKED"`；L221断言`result["pending"]["stage"] == "clarification"`；L222断言`result["pending"]["can_approve"] is False`；L223断言`gateway.calls == ["recommend:1", "recommend:2", "recommend:3"]`；L224断言`all(entry["after"] == {} for entry in state["requirement_ledger"])`；L225断言`all( entry["reconciled_candidate"]["facts"]["business"]["permissions"][0]["actions"][…`；L231断言`session.scalars(select(Approval)).all() == []`。 调用`new_run`、`store.set_automation`、`Invalid`、`Runtime`、`runtime.tick`、`runtime.graph.get_state`、`store.get_run`、`all`、`store.tx`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_invalid_analysis_uses_existing_clarification_budget_before_plan.Invalid`（L201–L211）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_autonomous_invalid_analysis_uses_existing_clarification_budget_before_plan.Invalid.complete`（L202–L211）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L204断言`schema is Requirement`；L205按`len(self.calls) > 1`分支；L206断言`payload["current_requirement"] == {}`；L207断言`payload["resolution_feedback"]["stage"] == "clarification"`；L209断言`feedback[0]["code"] == "requirement_business_shape"`；L210断言`"未知动作" in feedback[0]["sources"][0]["excerpt"]`。 调用`self.calls.append`、`len`、`candidate`。 返回路径：L211的`candidate(["create", "read", "purge"])`。
- `test_resume_can_correct_analysis_expression_without_losing_personal_crud`（L236–L272）：接收`settings`、`store`、`plan`。 控制顺序：L246断言`pending["stage"] == "clarification" and not pending["can_approve"]`；L265断言`result["status"] == "WAITING_REQUIREMENTS"`；L266断言`result["pending"]["can_approve"] is True`；L267断言`gateway.calls == ["requirement:2"]`；L268断言`state["requirement_analysis_diagnostics"] == []`；L269断言`"删除" in state["requirement"]["features"][0]`；L270断言`state["requirement"]["facts"] == {}`；L272断言`session.scalars(select(Approval)).all() == []`。 调用`new_run`、`Runtime`、`Invalid`、`runtime.tick`、`store.get_run`、`decision`、`Fixed`、`runtime.graph.get_state`、`store.tx`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resume_can_correct_analysis_expression_without_losing_personal_crud.Invalid`（L237–L240）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_resume_can_correct_analysis_expression_without_losing_personal_crud.Invalid.complete`（L238–L240）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L239断言`schema is Requirement`。 调用`candidate`。 返回路径：L240的`candidate(["create", "read", "purge"])`。
- `test_resume_can_correct_analysis_expression_without_losing_personal_crud.Fixed`（L249–L258）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_resume_can_correct_analysis_expression_without_losing_personal_crud.Fixed.complete`（L250–L258）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L252断言`schema is Requirement`；L253断言`payload["original_request"] == "个人任务 CRUD"`；L254断言`payload["current_requirement"] == {}`；L255断言`payload["resolution_feedback"]["analysis_diagnostics"]`。 调用`self.calls.append`、`requirement`。 返回路径：L258的`result`。

</details>

**创建路径：** `tests/test_business_analysis_validation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L272。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11601`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_analysis_validation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8620a2fb8232c0112ecccc8f4d56142b2885817d16e2ee513e77f69049727804"} -->
````python
# tests/test_business_analysis_validation.py
"""Malformed analysis facts return to clarification without weakening design guards."""

import json

import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from sqlalchemy import select

from workbench.business_capabilities import business_analysis_conflicts, business_gaps
from workbench.domain import Requirement
from workbench.flow import Workflow
from workbench.requirement_sources import analysis_feedback
from workbench.runtime import Runtime
from workbench.store import Approval, Conflict


def candidate(actions):
    result = requirement()
    result.facts = {
        "business": {
            "permissions": [
                {"role": "reader", "entity": "task", "actions": actions, "scope": "own"}
            ]
        }
    }
    return result


@pytest.mark.parametrize(
    "actions",
    [["create", "purge"], [], "read", ["read", "read"], ["view_history", "read_history"], [True]],
)
@pytest.mark.parametrize("encoding", ["native", "json", "nested"])
def test_malformed_business_facts_are_rejected_before_design_without_rewriting(
    plan, actions, encoding
):
    value = candidate(actions)
    if encoding == "json":
        value.facts["business"] = json.dumps(value.facts["business"])
    elif encoding == "nested":
        value.facts = {"confirmed": value.facts}
    before = value.model_dump()
    diagnostics = business_analysis_conflicts(value)
    assert len(diagnostics) == 1
    assert diagnostics[0]["code"] == "requirement_business_shape"
    assert diagnostics[0]["target"] == {"entity": "task", "field": None}
    assert diagnostics[0]["attribute"] == "permissions"
    source = diagnostics[0]["sources"][0]
    assert source["source"]["path"].endswith("business.permissions.0")
    assert source["expected"]["actions"] == actions
    assert value.model_dump() == before
    design_diagnostics = []
    assert business_gaps(value, plan, diagnostics=design_diagnostics)
    assert design_diagnostics[0]["code"] == "business_unsupported_shape"
    feedback = analysis_feedback(diagnostics)
    assert "actions" in feedback[0]["sources"][0]["excerpt"]
    assert feedback[0]["sources"][0]["expected"]["actions"] == actions


@pytest.mark.parametrize("key", ["only_actions", "denied_actions", "forbidden_actions"])
def test_restrictions_share_the_same_known_action_grammar(plan, key):
    value = candidate(["read"])
    value.facts["business"]["permissions"][0][key] = ["purge"]
    assert business_analysis_conflicts(value)
    diagnostics = []
    assert business_gaps(value, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "business_unsupported_shape"


def test_known_aliases_and_partial_restrictions_remain_valid_and_unchanged():
    value = candidate(["view_history"])
    value.data_scope = "shared"
    descriptor = value.facts["business"]["permissions"][0]
    descriptor.update(only_actions=["read_history"], read_only=True)
    before = value.model_dump()
    assert business_analysis_conflicts(value) == []
    assert value.model_dump() == before
    descriptor["read_only"] = "true"
    assert business_analysis_conflicts(value)


@pytest.mark.parametrize(
    "domain,descriptor",
    [
        ("permissions", {"role": "reader", "entity": "task", "actions": ["read"], "scope": "own"}),
        ("resources", {"entity": "task", "notes": True}),
        ("relations", {"entity": "task", "field": "parent", "target_entity": "other"}),
        ("workflows", {"entity": "task", "status_field": "state"}),
        ("metrics", {"entity": "task", "kind": "count"}),
        ("notifications", {"entity": "task", "event": "assigned", "recipient": "assignee"}),
    ],
)
def test_personal_scope_cannot_approve_facts_that_require_a_shared_business_plan(
    plan, domain, descriptor
):
    value = requirement()
    value.facts = {domain: [descriptor]}
    before = value.model_dump()
    diagnostics = business_analysis_conflicts(value)
    assert len(diagnostics) == 1
    assert diagnostics[0]["code"] == "requirement_business_scope"
    assert "per_user" in diagnostics[0]["sources"][0]["text"]
    assert business_gaps(value, plan)
    assert value.model_dump() == before
    for scope in ("shared", "unknown"):
        value.data_scope = scope
        assert business_analysis_conflicts(value) == []


def test_non_executable_partial_metadata_does_not_create_a_scope_conflict():
    value = requirement()
    value.facts = {
        "resources": [{"features": ["keyword_search"]}],
        "permissions": [{"only_actions": ["read"]}],
    }
    assert business_analysis_conflicts(value) == []


def test_retained_fact_provenance_requires_same_path_and_exact_typed_descriptor():
    old = candidate([True])
    value = old.model_copy(deep=True)
    source = business_analysis_conflicts(value, previous=old.gate_dump())[0]["sources"][0]
    assert source["origin"] == "previous_requirement"
    assert source["previous_source"] == source["source"]
    assert source["user_sources"] == []
    feedback = analysis_feedback(business_analysis_conflicts(value, previous=old.gate_dump()))
    assert feedback[0]["sources"][0]["previous_source"] == source["source"]
    value.facts["business"]["permissions"][0]["actions"] = [1]
    source = business_analysis_conflicts(value, previous=old.gate_dump())[0]["sources"][0]
    assert source["origin"] == "model_analysis"
    assert "previous_source" not in source
    value = old.model_copy(deep=True)
    value.facts = {"other": value.facts}
    source = business_analysis_conflicts(value, previous=old.gate_dump())[0]["sources"][0]
    assert source["origin"] == "model_analysis"


def test_analysis_cannot_remove_previously_approved_invalid_facts_by_omission(
    settings, store, plan
):
    old = candidate(["purge"])

    class Omitted(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            assert schema is Requirement
            return requirement()

    run = new_run(store)
    state = {
        "run_id": run,
        "template": "python-basic",
        "round": 2,
        "requirement": old.gate_dump(),
        "requirement_source_count": 1,
    }
    before = json.loads(json.dumps(state))
    result = Workflow(settings, store, Omitted(plan)).analyse(state)
    assert state == before
    assert result["requirement"] == old.gate_dump()
    assert result["requirement_analysis_baseline"] == old.gate_dump()
    assert result["requirement_source_count"] == 1
    source = result["requirement_analysis_diagnostics"][0]["sources"][0]
    assert source["origin"] == "previous_requirement"
    assert source["previous_source"]["path"] == "business.permissions.0"
    assert result["requirement_ledger"][-1]["after"] == old.gate_dump()


def test_shared_business_grammar_checks_other_domains_without_plan_or_field_guessing():
    value = requirement()
    value.facts = {
        "relations": [{"entity": "task", "from": "other", "target_entity": "accounts"}],
        "resources": [{"entity": "task", "audit": False, "audit_history": "append-only"}],
        "workflows": [
            {
                "entity": "task",
                "transitions": [{"name": "finish", "set": {"completed_at": "tomorrow"}}],
            }
        ],
    }
    diagnostics = business_analysis_conflicts(value)
    assert {item["attribute"] for item in diagnostics} == {"relations", "resources", "workflows"}


def test_personal_crud_and_display_metadata_do_not_invent_business_obligations(plan):
    value = requirement()
    value.features = ["登录用户可新增、查看、修改和删除自己的 task；不添加业务角色"]
    value.facts = {
        "ui": {"permissions": [{"role": "caption", "actions": ["purge"]}]},
        "fields": [{"name": "permissions", "kind": "text", "actions": ["purge"]}],
        "template_capabilities": {"permissions": [{"actions": ["purge"]}]},
    }
    before = value.model_dump()
    assert business_analysis_conflicts(value) == []
    assert business_gaps(value, plan) == []
    assert value.model_dump() == before


def test_autonomous_invalid_analysis_uses_existing_clarification_budget_before_plan(
    settings, store, plan
):
    class Invalid(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement, "Malformed facts must not be approved for Plan repair"
            if len(self.calls) > 1:
                assert payload["current_requirement"] == {}
                assert payload["resolution_feedback"]["stage"] == "clarification"
                feedback = payload["resolution_feedback"]["analysis_diagnostics"]
                assert feedback[0]["code"] == "requirement_business_shape"
                assert "未知动作" in feedback[0]["sources"][0]["excerpt"]
            return candidate(["create", "read", "purge"])

    run = new_run(store)
    store.set_automation(run, True, "smart")
    gateway = Invalid(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        state = runtime.graph.get_state({"configurable": {"thread_id": run}}).values
    result = store.get_run(run)
    assert result["status"] == "BLOCKED"
    assert result["pending"]["stage"] == "clarification"
    assert result["pending"]["can_approve"] is False
    assert gateway.calls == ["recommend:1", "recommend:2", "recommend:3"]
    assert all(entry["after"] == {} for entry in state["requirement_ledger"])
    assert all(
        entry["reconciled_candidate"]["facts"]["business"]["permissions"][0]["actions"][-1]
        == "purge"
        for entry in state["requirement_ledger"]
    )
    with store.tx() as session:
        assert session.scalars(select(Approval)).all() == []
    with pytest.raises(Conflict):
        decision(store, run)


def test_resume_can_correct_analysis_expression_without_losing_personal_crud(settings, store, plan):
    class Invalid(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            assert schema is Requirement
            return candidate(["create", "read", "purge"])

    run = new_run(store)
    with Runtime(settings, store, Invalid(plan)) as runtime:
        runtime.tick()
    pending = store.get_run(run)["pending"]
    assert pending["stage"] == "clarification" and not pending["can_approve"]
    decision(store, run, "answer", "按原文保留个人CRUD，修正分析中的虚构业务权限表达")

    class Fixed(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement
            assert payload["original_request"] == "个人任务 CRUD"
            assert payload["current_requirement"] == {}
            assert payload["resolution_feedback"]["analysis_diagnostics"]
            result = requirement()
            result.features = ["登录用户可新增、查看、修改和删除自己的 task"]
            return result

    gateway = Fixed(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        state = runtime.graph.get_state({"configurable": {"thread_id": run}}).values
    result = store.get_run(run)
    assert result["status"] == "WAITING_REQUIREMENTS"
    assert result["pending"]["can_approve"] is True
    assert gateway.calls == ["requirement:2"]
    assert state["requirement_analysis_diagnostics"] == []
    assert "删除" in state["requirement"]["features"][0]
    assert state["requirement"]["facts"] == {}
    with store.tx() as session:
        assert session.scalars(select(Approval)).all() == []
````
