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
