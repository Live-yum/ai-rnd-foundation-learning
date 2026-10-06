"""Authored policy/routing tests only; never a live sandbox or model attestation."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.capability_fixture import GOAL, fixture_baseline, make_plan
from scripts.extension_oracles import contest
from workbench.capability_contracts import HttpStep, scope_sources
from workbench.capability_policy import business_coverage, contract_errors, scope_policy
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest
from workbench.flow import Workflow
from workbench.orchestration import ExtensionDesign


def scope(text):
    return {"messages": [text], "source_digest": digest([text]), "sources": scope_sources([text])}


def original():
    data = json.loads(
        (Path(__file__).parent / "fixtures/contest_oracle/original_requirement.json").read_text()
    )
    return scope(data["requirement_text"])


def policy():
    return scope_policy(original(), Selection(template="fastapiadmin").model_dump())


def business_proof():
    return {
        "business_oracle": {
            "protocol": contest.CONTRACT_VERSION,
            "witnesses": {name: True for name in contest.SEMANTICS},
            "full_request_complete": False,
            "remaining_obligations": list(contest.REMAINING),
            "fresh_replay": True,
            "same_cluster": True,
            "distinct_database_oid": True,
        }
    }


def test_registered_original_keeps_all_35_units_even_after_bounded_success():
    current = original()
    assert len(current["sources"]) == 35
    selected = policy()
    assert selected["trusted_oracle"] == contest.CONTRACT_VERSION
    result = business_coverage(selected, business_proof())
    assert {g["source_id"] for g in result["obligations"]} == {s["id"] for s in current["sources"]}
    assert result["complete_source_ids"] == []
    assert result["full_request_complete"] is False
    assert len([g for g in result["obligations"] if g["status"] == "verified"]) == 4
    assert all(
        g["status"] == "remaining"
        for g in result["obligations"]
        if g["semantic"] == "original.full_source"
    )
    # Human IDs and planner text cannot select/deselect the registry.
    renamed = deepcopy(current)
    for row in renamed["sources"]:
        row["id"] = "renamed-" + row["id"]
    assert (
        scope_policy(renamed, selected["selection"])["trusted_oracle"] == contest.CONTRACT_VERSION
    )


@pytest.mark.parametrize(
    "key,value",
    [
        ("protocol", "health-only"),
        ("witnesses", {}),
        ("full_request_complete", True),
        ("remaining_obligations", []),
        ("fresh_replay", False),
        ("same_cluster", False),
        ("distinct_database_oid", False),
    ],
)
def test_oracle_missing_or_candidate_claimed_completion_fails_closed(key, value):
    proof = business_proof()
    proof["business_oracle"][key] = value
    with pytest.raises(CheckFailure):
        business_coverage(policy(), proof)


def test_generic_extensions_remain_available_but_health_ids_are_not_acceptance():
    current = scope(GOAL)
    plan = make_plan(
        {
            "source_units": current["sources"],
            "source_digest": current["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    assert contract_errors(plan) == []
    generic = scope_policy(current, plan.selection.model_dump())
    assert generic["trusted_oracle"] is None
    assert business_coverage(generic, {})["coverage_level"] == "reviewed-executable-contract"
    for scenario in plan.scenarios:
        scenario.steps = [HttpStep(path="/health", status=200, equals={"$.ok": True})]
        scenario.after_restart = scenario.steps
    errors = contract_errors(plan)
    assert any("健康" in error for error in errors)
    assert any("重启" in error for error in errors)


def aggregate_state(tmp_path):
    current = scope(GOAL)
    plan = make_plan(
        {
            "source_units": current["sources"],
            "source_digest": current["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    design = ExtensionDesign(baseline=fixture_baseline(), implementation=plan)
    product = tmp_path / "candidate"
    product.mkdir()
    (product / "app.py").write_text("# authored source, never executed\n")
    return design, {
        "run_id": "authored",
        "round": 1,
        "extension_product": str(product),
        "extension_completed": [{"task": t.id} for t in plan.tasks],
        "extension_policy": scope_policy(current, plan.selection.model_dump()),
        "extension_design": design.model_dump(),
        "extension_integration_attempt": 0,
    }


def test_workflow_routes_registered_oracle_and_requires_explicit_partial_scope(
    settings, store, tmp_path, monkeypatch
):
    design, state = aggregate_state(tmp_path)
    state["extension_policy"] = policy()
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)
    calls = []

    def verify(*args, **kwargs):
        calls.append(kwargs)
        return business_proof()

    monkeypatch.setattr("workbench.capability_sandbox.verify_capabilities", verify)
    # Routing simulation explicitly excludes the already separately tested real proof validator.
    monkeypatch.setattr("workbench.orchestration.require_evidence", lambda *a, **k: None)
    state.update(workflow.extension_aggregate(state))
    state["extension_scope"] = original()
    data = workflow.extension_scope_data(state, design)
    assert data["requires_explicit_review"] is True
    assert data["delivery_kind"] == "partial"
    assert data["full_request_complete"] is False
    from workbench.store import Conflict

    with pytest.raises(Conflict, match="人工审批"):
        workflow.extension_package(state)
    assert calls[0]["trusted_oracle"] == contest.CONTRACT_VERSION
    assert calls[0]["aggregate"] is True
    report = json.loads((settings.data_dir / "runs/authored/extension-coverage.json").read_text())
    assert len({g["source_id"] for g in report["obligations"]}) == 35
    assert not list((settings.data_dir / "runs/authored").glob("*.zip"))


def test_aggregate_failure_routes_bounded_repair_without_losing_candidate(
    settings, store, tmp_path, monkeypatch
):
    design, state = aggregate_state(tmp_path)
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)

    def failure(*args, **kwargs):
        raise CheckFailure("business assertion failed")

    monkeypatch.setattr("workbench.capability_sandbox.verify_capabilities", failure)
    before = manifest(Path(state["extension_product"]))
    state.update(workflow.extension_aggregate(state))
    assert workflow.extension_after_aggregate(state) == "extension_integration_repair"
    assert manifest(Path(state["extension_product"])) == before
    state["extension_integration_attempt"] = settings.max_repair_attempts
    with pytest.raises(UnsupportedScope, match="预算"):
        workflow.extension_after_aggregate(state)


@pytest.mark.parametrize("previously_complete", [False, True])
def test_scope_and_zip_preserve_review_conflicts_and_invalidate_old_approval(
    settings, store, tmp_path, monkeypatch, previously_complete
):
    import zipfile

    from workbench.store import Approval, Conflict

    design, state = aggregate_state(tmp_path)
    project = store.create_project("review disagreement", "review-disagreement")
    run = store.create_run(project["id"], {"requirement": "authored"}, "disagreement-run")["run_id"]
    state.update(
        run_id=run,
        extension_proof={"passed": True},
        extension_scope=scope(GOAL),
        model_review={
            "enabled": True,
            "uncovered_requirements": ["第一条原文中的人数约束未验证"],
            "observations": ["独立运行证明不能覆盖遗漏的子句"],
        },
    )
    root = settings.data_dir / "runs" / run
    root.mkdir(parents=True)
    base = {
        "coverage_level": "operator-reviewed-atomic-contracts",
        "full_request_complete": previously_complete,
        "complete_source_ids": ["source-0-0", "source-0-1"]
        if previously_complete
        else ["source-0-0"],
        "obligations": [
            {
                "goal_id": "full-a",
                "source_id": "source-0-0",
                "semantic": "original.full_source",
                "status": "verified",
            },
            {
                "goal_id": "full-b",
                "source_id": "source-0-1",
                "semantic": "original.full_source",
                "status": "verified" if previously_complete else "remaining",
            },
            {
                "goal_id": "atom-a",
                "source_id": "source-0-0",
                "semantic": "authored observed value",
                "status": "verified",
            },
        ],
    }
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)
    monkeypatch.setattr(workflow, "extension_coverage", lambda *args: deepcopy(base))
    data = workflow.extension_scope_data(state, design)
    assert data["model_review"] == state["model_review"]
    assert data["review_conflicts"] == state["model_review"]["uncovered_requirements"]
    assert data["requires_explicit_review"] is True
    assert data["delivery_kind"] == "partial" and data["full_request_complete"] is False
    assert data["coverage"]["complete_source_ids"] == []
    assert data["coverage"]["pre_review_complete_source_ids"] == base["complete_source_ids"]
    assert data["coverage"]["remaining_obligations"] == ["full-a", "full-b"]
    assert data["coverage"]["obligations"][-1]["status"] == "verified"
    gate = store.gate(run, "extension_scope", 1, data, ["approve"])
    with store.tx() as session:
        session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="local-operator"))
    monkeypatch.setattr("workbench.orchestration.require_evidence", lambda *a, **k: None)
    monkeypatch.setattr(
        "workbench.capability_sandbox.verify_capabilities", lambda *a, **k: {"passed": True}
    )
    monkeypatch.setattr(
        "workbench.capability_consumer.require_consumer_evidence", lambda *a, **k: None
    )
    packaged = workflow.extension_package(state)["delivery"]
    assert packaged["model_review"] == state["model_review"]
    assert packaged["review_conflicts"] == data["review_conflicts"]
    assert packaged["full_request_complete"] is False
    with zipfile.ZipFile(root / packaged["package"]) as archive:
        declared = json.loads(archive.read("RND-DELIVERY.json"))
    assert declared == data
    state["model_review"]["uncovered_requirements"].append("后来发现的另一个遗漏")
    with pytest.raises(Conflict, match="人工审批"):
        workflow.extension_package(state)
