"""Pure contract replay of recorded *unapproved* model diagnostics; never generation."""

import hashlib
import json
from copy import deepcopy

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

RECORDED = {
    "python-basic": "c168b09cfb9ad7a06c55f2e3fcd78ecba260dd78bc82793e2c8dff35b75ea9c8",
    "fastapiadmin": "09fead7bdd076d1f50dacab5574072c78ac15900aa6141f58e4d90e1d9a702c6",
    "yudao-vben": "387597908c075b12193585499482402359ba99afcc8c99cd173e17d93f806afe",
}


def recorded(template):
    payload = (
        ROOT / "tests/fixtures/customer_design_diagnostics" / (template + ".json")
    ).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == RECORDED[template]
    data = json.loads(payload)
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


def corrected_copy(template):
    requirement, candidate = recorded(template)
    value = deepcopy(candidate.model_dump())
    for policy in value["business"]["permissions"]:
        if policy["role"] in {"manager", "service"}:
            if policy["entity"] == "customers" and "read_metrics" not in policy["actions"]:
                policy["actions"].append("read_metrics")
            if (
                policy["entity"] in {"requests", "tasks"}
                and "read_history" not in policy["actions"]
            ):
                policy["actions"].append("read_history")
            if template == "yudao-vben" and policy["entity"] == "tasks":
                policy["actions"].remove("read_metrics")
    return requirement, Plan.model_validate(value)


@pytest.mark.parametrize("template", RECORDED)
def test_exact_recorded_candidates_remove_false_namespace_gaps_retain_real_omissions(template):
    requirement, plan = recorded(template)
    assert coverage_gaps(requirement, plan) == []
    diagnostics = []
    gaps = business_gaps(requirement, plan, diagnostics=diagnostics)
    if template == "fastapiadmin":
        assert gaps == diagnostics == []
    else:
        assert gaps
        assert any(d["code"] == "business_scope_mismatch" for d in diagnostics)
        assert any(
            d["source"]["path"] == "business.metrics.3.role_scope"
            for d in diagnostics
            if "path" in d["source"]
        )
    if template == "yudao-vben":
        history = [d for d in diagnostics if d["code"] == "business_missing_history_grant"]
        assert {(d["expected"]["role"], d["expected"]["entity"]) for d in history} == {
            (r, e) for r in ("manager", "service") for e in ("requests", "tasks")
        }


@pytest.mark.parametrize("template", RECORDED)
def test_exact_offline_copy_with_only_reported_obligations_repaired_passes(template):
    requirement, plan = corrected_copy(template)
    assert not coverage_gaps(requirement, plan)
    assert not business_gaps(requirement, plan)
    # Re-read the original: a local validation mutation is not an approved design.
    original_requirement, original = recorded(template)
    if template != "fastapiadmin":
        assert business_gaps(original_requirement, original)


@pytest.mark.parametrize("template", RECORDED)
@pytest.mark.parametrize(
    "mutation",
    ["scope", "write", "new_role", "relation", "metric", "workflow", "resolution_notice"],
)
def test_recorded_semantic_contract_mutations_remain_blocked(template, mutation):
    requirement, plan = corrected_copy(template)
    assert not business_gaps(requirement, plan)
    value = plan.model_dump()
    business = value["business"]
    if mutation == "scope":
        next(
            p
            for p in business["permissions"]
            if p["role"] == "service" and p["entity"] == "requests"
        )["scope"] = "all"
    elif mutation == "write":
        next(
            p
            for p in business["permissions"]
            if p["role"] == "employee" and p["entity"] == "customers"
        )["actions"].append("update")
    elif mutation == "new_role":
        business["roles"].append({"name": "observer", "label": "Unexpected observer"})
        business["permissions"].append(
            {"role": "observer", "entity": "customers", "actions": ["read"], "scope": "all"}
        )
    elif mutation == "relation":
        next(r for r in business["relations"] if r["field"] == "customer_id")["target_entity"] = (
            "tasks"
        )
    elif mutation == "metric":
        next(m for m in business["metrics"] if m["kind"] == "group_count")["group_by"] = "name"
    elif mutation == "workflow":
        business["workflows"][0]["transitions"][1]["set_timestamp"] = None
    else:
        business["notifications"] = [
            n
            for n in business["notifications"]
            if not (
                n["recipient"] == "creator"
                and n["event"] == "transitioned"
                and n["transition"] == "resolve"
            )
        ]
    mutated = Plan.model_validate(value)
    assert business_gaps(requirement, mutated)


CURRENT_HASHES = {
    "python-basic": "0ad2c86625dd7454bab688edf402c59b4a3d28ba3e4f5eb07f8c3b9747dfd8a5",
    "fastapiadmin": "3b03ca2f5b8b488bf958f4e685c398428b17e640d697bdcf284ddabfddc13099",
    "yudao-vben": "561b5bcabca92dff7d845c31ca33f2c3c221004bd195384cbca471e8db0fa72c",
}


@pytest.mark.parametrize("template", CURRENT_HASHES)
def test_second_recorded_contracts_preserve_all_typed_and_business_obligations(template):
    file = ROOT / "tests/fixtures/customer_design_diagnostics/2a4106f" / (template + ".json")
    raw = file.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CURRENT_HASHES[template]
    data = json.loads(raw)
    assert data["approval_status"] == "unapproved" and data["execution_authorized"] is False
    requirement = Requirement.model_validate(data["requirement"])
    candidate = Plan.model_validate(data["candidate_plan"])
    assert not coverage_gaps(requirement, candidate)
    assert not business_gaps(requirement, candidate)
    # These are pure validator regressions, not approval or generated runtime proof.
    for entity_name in ("requests", "tasks"):
        changed = candidate.model_copy(deep=True)
        entity = next(e for e in changed.entities if e.name == entity_name)
        next(f for f in entity.fields if f.name == "detail").max_length = 200
        assert coverage_gaps(requirement, changed)
    if template == "fastapiadmin":
        for entity in ("requests", "tasks"):
            for transition in ("start", "resolve"):
                changed = candidate.model_copy(deep=True)
                changed.business.notifications = [
                    n
                    for n in changed.business.notifications
                    if not (
                        n.entity == entity
                        and n.event == "transitioned"
                        and n.transition == transition
                        and n.recipient == "assignee"
                    )
                ]
                assert business_gaps(requirement, changed)
