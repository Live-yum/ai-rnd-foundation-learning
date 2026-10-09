"""Real API-only probes cover alternative workflow paths without weakening notifications."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env


def forked_plan():
    transitions = [
        {"name": "start", "from_states": ["queued"], "to_state": "review", "roles": ["operator"]},
        {
            "name": "accept",
            "from_states": ["review"],
            "to_state": "accepted",
            "roles": ["operator"],
        },
        {
            "name": "decline",
            "from_states": ["review"],
            "to_state": "rejected",
            "roles": ["operator"],
        },
        {
            "name": "reopen",
            "from_states": ["rejected"],
            "to_state": "review",
            "roles": ["operator"],
        },
    ]
    return Plan.model_validate(
        {
            "title": "Forked review workflow",
            "data_scope": "shared",
            "acceptance": [
                "Every declared transition and its recipient notifications are exercised"
            ],
            "entities": [
                {
                    "name": "reviews",
                    "description": "Reviews",
                    "fields": [
                        {"name": "title", "kind": "text", "max_length": 60},
                        {"name": "reviewer_id", "kind": "text", "required": False},
                        {
                            "name": "state",
                            "kind": "enum",
                            "choices": ["queued", "review", "accepted", "rejected"],
                        },
                        {"name": "due_at", "kind": "datetime", "required": False},
                    ],
                }
            ],
            "business": {
                "roles": [
                    {"name": "manager", "label": "Manager"},
                    {"name": "operator", "label": "Operator"},
                ],
                "bootstrap_role": "manager",
                "role_admin_roles": ["manager"],
                "registration": {"enabled": False, "default_role": "operator"},
                "resources": [
                    {"entity": "reviews", "assignee_field": "reviewer_id", "notes": False}
                ],
                "relations": [
                    {"entity": "reviews", "field": "reviewer_id", "target_entity": "$users"}
                ],
                "permissions": [
                    {
                        "role": "manager",
                        "entity": "reviews",
                        "scope": "all",
                        "actions": [
                            "create",
                            "read",
                            "update",
                            "archive",
                            "assign",
                            "read_history",
                            "read_audit",
                        ],
                    },
                    {
                        "role": "operator",
                        "entity": "reviews",
                        "scope": "assigned",
                        "actions": ["read", "transition", "read_history"],
                    },
                ],
                "workflows": [
                    {
                        "entity": "reviews",
                        "status_field": "state",
                        "initial": "queued",
                        "transitions": transitions,
                    }
                ],
                "notifications": [
                    {"entity": "reviews", "event": "assigned", "recipient": "assignee"},
                    {
                        "entity": "reviews",
                        "event": "due",
                        "recipient": "assignee",
                        "due_field": "due_at",
                    },
                    *[
                        {
                            "entity": "reviews",
                            "event": "transitioned",
                            "transition": transition["name"],
                            "recipient": recipient,
                        }
                        for transition in transitions
                        for recipient in ("creator", "assignee")
                    ],
                ],
                "metrics": [],
            },
        }
    )


def run_api_probe(tmp_path, plan, omit_transition_notification=False):
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    if omit_transition_notification:
        source = product / "business_runtime.py"
        original = source.read_text(encoding="utf-8")
        notify = 'notify(connection, entity, after, "transitioned", event_id, data.transition)'
        assert original.count(notify) == 1
        source.write_text(
            original.replace(notify, f'{notify} if data.transition != "decline" else None'),
            encoding="utf-8",
        )
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "verify.py",
            "--python",
            sys.executable,
            "--report",
            str(tmp_path / "verification.json"),
        ],
        cwd=product,
        env=clean_env(
            {"PATH": os.environ.get("PATH", ""), "TEMP": str(temporary), "TMP": str(temporary)}
        ),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=180,
    )
    assert result.stdout.strip(), result.stderr
    return result, json.loads(result.stdout.splitlines()[-1])


def test_api_probe_exercises_each_branch_and_notifies_both_recipients(tmp_path):
    result, report = run_api_probe(tmp_path, forked_plan())
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-transitions" in report["checks"]
    assert "business-notifications" in report["checks"]
    assert "process_restart_persistence" in report["checks"]
    assert report["browser"] == {"applicable": False, "reason": "api-only frontend"}
    assert report["http"] and report["restart"]


def test_api_probe_rejects_an_omitted_notification_on_the_alternative_branch(tmp_path):
    result, report = run_api_probe(tmp_path, forked_plan(), omit_transition_notification=True)
    assert result.returncode == 1 and report["passed"] is False, report
    assert report["message"] == "Missing, duplicated or unexpected declared notifications"


@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_api_probe_uses_each_branchs_existing_authorized_role(tmp_path, scope):
    raw = forked_plan().model_dump()
    business = raw["business"]
    business["roles"].append({"name": "specialist", "label": "Specialist"})
    operator = next(grant for grant in business["permissions"] if grant["role"] == "operator")
    operator["scope"] = scope
    if scope == "own":
        operator["actions"].append("create")
        business["resources"][0]["assignee_field"] = None
        business["relations"] = []
        for grant in business["permissions"]:
            grant["actions"] = [action for action in grant["actions"] if action != "assign"]
        business["notifications"] = [
            rule for rule in business["notifications"] if rule["recipient"] == "creator"
        ]
    business["permissions"].append({**operator, "role": "specialist"})
    for transition in business["workflows"][0]["transitions"]:
        if transition["name"] == "start":
            transition["roles"] = ["operator", "specialist"]
        elif transition["name"] in {"decline", "reopen"}:
            transition["roles"] = ["specialist"]
    result, report = run_api_probe(tmp_path, Plan.model_validate(raw))
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-notifications" in report["checks"] and report["restart"]


def test_large_source_contract_passes_independent_api_probe(tmp_path):
    from test_template_project_acceptance import fixture_plan

    from scripts.template_acceptance_cases import load_case, require_contract

    case = load_case("facilities-ops")
    plan = fixture_plan(case)
    assert require_contract(case, plan.model_dump())
    result, report = run_api_probe(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert report["entities"] == 6 and report["http"] and report["restart"]
    assert report["browser"] == {"applicable": False, "reason": "api-only frontend"}
    assert {
        "business-transitions",
        "business-relations",
        "business-scoped-metrics",
        "business-notifications",
    } <= set(report["checks"])


def test_api_probe_skips_transition_actor_who_is_not_an_eligible_assignee(tmp_path):
    raw = forked_plan().model_dump()
    business = raw["business"]
    for role in ["no_read", "specialist"]:
        business["roles"].append({"name": role, "label": role})
        business["permissions"].append(
            {
                "role": role,
                "entity": "reviews",
                "scope": "assigned",
                "actions": ["transition"] if role == "no_read" else ["read", "transition"],
            }
        )
    for transition in business["workflows"][0]["transitions"]:
        if transition["name"] == "start":
            transition["roles"] = ["operator", "no_read", "specialist"]
        elif transition["name"] in {"decline", "reopen"}:
            transition["roles"] = ["no_read", "specialist"]
    result, report = run_api_probe(tmp_path, Plan.model_validate(raw))
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-notifications" in report["checks"] and report["restart"]


@pytest.fixture
def verifier():
    path = Path(__file__).parents[1] / "templates/product/verify_business.py"
    spec = importlib.util.spec_from_file_location("branch_verifier", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_assignee_candidates_preserve_nullable_and_existing_runtime_qualifications(verifier):
    actors = {
        role: {"id": role + "-user", "role": role}
        for role in ["no_read", "owner", "reader", "handler"]
    }
    grants = {
        ("no_read", "reviews"): {"actions": ["transition"], "scope": "assigned"},
        ("owner", "reviews"): {"actions": ["read", "transition"], "scope": "own"},
        ("reader", "reviews"): {"actions": ["read"], "scope": "all"},
        ("handler", "reviews"): {"actions": ["read", "transition"], "scope": "assigned"},
    }
    assert verifier.workflow_assignee_candidates(actors, grants, "reviews", "handler-user") == [
        "handler-user",
        "reader-user",
        None,
    ]
    assert verifier.workflow_assignee_candidates(
        {"owner": actors["owner"]}, grants, "reviews", "no_read-user"
    ) == [None]


def test_transition_paths_accept_any_reachable_source_and_include_cycle_edges(verifier):
    workflow = forked_plan().business.workflows[0].model_dump()
    workflow["transitions"][1]["from_states"] = ["unreachable", "review"]
    paths = verifier.workflow_transition_paths(workflow)
    assert [step["name"] for step in paths["accept"]] == ["start", "accept"]
    assert [step["name"] for step in paths["reopen"]] == ["start", "decline", "reopen"]
    assert set(paths) == {"start", "accept", "decline", "reopen"}


@pytest.mark.parametrize("cycle_first", [False, True])
def test_branch_coverage_replays_required_prefixes_and_bounds_cycles(verifier, cycle_first):
    workflow = forked_plan().business.workflows[0].model_dump()
    if cycle_first:
        workflow["transitions"] = [workflow["transitions"][i] for i in [0, 2, 3, 1]]
    rows = [{"id": "base", "state": "queued"}]
    actions = []

    def create_branch(transition):
        row = {"id": "branch", "state": "queued"}
        rows.append(row)
        return row, verifier.workflow_transition_paths(workflow)[transition["name"]]

    def apply(row, transition, actor):
        assert row["state"] in transition["from_states"] and actor == "operator"
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    verifier.cover_workflow_branches(
        workflow, rows[0], create_branch, lambda row, transition: "operator", apply
    )
    assert {name for _, name in actions} == {"start", "accept", "decline", "reopen"}
    assert rows[0] == {"id": "base", "state": "accepted"}
    if cycle_first:
        assert len(actions) == 4 and len(rows) == 1
    else:
        assert actions == [
            ("base", "start"),
            ("base", "accept"),
            ("branch", "start"),
            ("branch", "decline"),
            ("branch", "reopen"),
        ]
        assert rows[1] == {"id": "branch", "state": "review"}


def test_unreachable_declared_transition_fails_before_any_side_effect(verifier):
    workflow = forked_plan().business.workflows[0].model_dump()
    workflow["transitions"][2]["from_states"] = ["never_reachable"]

    def unexpected(*args):
        pytest.fail("Unreachable graph must fail before creating or changing records")

    with pytest.raises(ValueError, match="no reachable source state"):
        verifier.cover_workflow_branches(
            workflow, {"state": "queued"}, unexpected, unexpected, unexpected
        )


@pytest.mark.parametrize("scope_field", ["created_by", "reviewer_id"])
def test_branch_actor_scope_is_rechecked_for_new_records(verifier, scope_field):
    workflow = forked_plan().business.workflows[0].model_dump()
    rows = [{"id": "base", "state": "queued", scope_field: "operator"}]
    actions = []

    def create_branch(transition):
        row = {"id": "branch", "state": "queued", scope_field: "another-user"}
        rows.append(row)
        return row, verifier.workflow_transition_paths(workflow)[transition["name"]]

    def actor_for(row, transition):
        return "operator" if row[scope_field] == "operator" else None

    def apply(row, transition, actor):
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    with pytest.raises(ValueError, match="no permitted transition actor"):
        verifier.cover_workflow_branches(workflow, rows[0], create_branch, actor_for, apply)
    assert actions == [("base", "start"), ("base", "accept")]
    assert rows[1] == {"id": "branch", "state": "queued", scope_field: "another-user"}


@pytest.mark.parametrize("reverse_prefix_order", [False, True])
def test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order(
    verifier, reverse_prefix_order
):
    transitions = [
        {"name": "a_start", "from_states": ["queued"], "to_state": "review", "roles": ["a"]},
        {"name": "b_finish", "from_states": ["review"], "to_state": "accepted", "roles": ["b"]},
        {"name": "b_start", "from_states": ["queued"], "to_state": "review", "roles": ["b"]},
    ]
    if reverse_prefix_order:
        transitions.reverse()
    workflow = {"status_field": "state", "initial": "queued", "transitions": transitions}
    rows = [
        {"id": "base", "state": "queued", "created_by": "a"},
        {"id": "secondary", "state": "queued", "created_by": "b"},
    ]
    actions = []

    def actor_for(row, transition):
        return row["created_by"] if row["created_by"] in transition["roles"] else None

    def apply(row, transition, actor):
        assert row["state"] in transition["from_states"] and row["created_by"] == actor
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    def unnecessary_create(transition):
        pytest.fail("An existing permitted owner record must be used before creating another")

    verifier.cover_workflow_branches(workflow, rows[0], unnecessary_create, actor_for, apply, rows)
    assert actions == [("base", "a_start"), ("secondary", "b_start"), ("secondary", "b_finish")]
