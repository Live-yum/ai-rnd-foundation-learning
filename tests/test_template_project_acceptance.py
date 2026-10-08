"""Harness integrity and synthetic HTTP checks. None of these are live-model evidence."""

import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml

from scripts.ci_template_projects import (
    MAX_MODEL_CALLS,
    MAX_OUTPUT_TOKENS,
    REPOSITORY,
    BoundedTransport,
    ObservedGateway,
    acceptance_settings,
    aggregate,
    failure_events,
    trusted_event,
)
from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require_contract,
    require_scenario_checks,
    suite_cases,
)
from scripts.template_acceptance_runtime import check_json, resolve, run_scenario
from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.llm import ModelGateway
from workbench.model_protocol import OutputFailure


def fixture_plan(case):
    """Test-only metadata for exercising the harness; the live controller cannot import it."""
    data = copy.deepcopy(case.contract)
    data.update(title=case.title, acceptance=["Synthetic offline harness validation only"])
    data["entities"] = [
        {
            "name": entity,
            "description": entity,
            "fields": [{"name": name, **field} for name, field in fields.items()],
        }
        for entity, fields in data["entities"].items()
    ]
    if data.get("business"):
        for item in [*data["business"]["roles"], *data["business"]["metrics"]]:
            item["label"] = item["name"]
    return Plan.model_validate(data)


def test_three_explicit_scales_and_independent_contracts():
    cases = suite_cases()
    assert [len(case.contract["entities"]) for case in cases] == [1, 3, 6]
    assert [len(case.contract.get("business", {}).get("workflows", [])) for case in cases] == [
        0,
        1,
        4,
    ]
    assert [len(case.contract.get("business", {}).get("roles", [])) for case in cases] == [0, 3, 4]
    for case in cases:
        assert require_contract(case, fixture_plan(case).model_dump())
        assert set(case.expected_checks) == {block["id"] for block in case.scenario}
        for name, fields in case.contract["entities"].items():
            assert name in case.requirement
            assert all(field in case.requirement for field in fields)
        assert len(case.source_digest) == 64


@pytest.mark.parametrize("index", [0, 1, 2])
def test_each_scenario_over_real_generated_http_and_restart(tmp_path, index):
    case = suite_cases()[index]
    product = tmp_path / "product"
    generate_basic(fixture_plan(case), product)
    report = run_scenario(
        case, product, sys.executable, tmp_path / "scenario", tmp_path / "screens", browser=False
    )
    assert report["passed"] is True and report["restart"] is True
    assert report["browser"]["real_browser"] is False
    assert report["http_requests"] >= sum(len(block["requests"]) for block in case.scenario)
    require_scenario_checks(case, report["checks"])


@pytest.mark.parametrize("mutation", ["field", "entity", "permission", "metric", "query"])
def test_model_plan_cannot_drop_or_change_obligations(mutation):
    case = suite_cases()[2]
    plan = fixture_plan(case).model_dump()
    if mutation == "field":
        plan["entities"][0]["fields"][0]["max_length"] = 300
    elif mutation == "entity":
        plan["entities"][0]["fields"].append({"name": "unrequested", "kind": "text"})
    elif mutation == "permission":
        policy = next(p for p in plan["business"]["permissions"] if p["role"] == "auditor")
        policy["actions"].append("update")
    elif mutation == "query":
        plan["entities"][1]["fields"][2]["searchable"] = True
    else:
        plan["business"]["metrics"].pop()
    with pytest.raises(AcceptanceFailure, match="contract_mismatch"):
        require_contract(case, plan)


def test_json_assertions_preserve_numbers_booleans_counts_and_row_identity():
    refs = {"row": {"id": "x", "quantity": 12, "enabled": False}}
    assert resolve({"count": "${row.quantity}", "enabled": "${row.enabled}"}, refs) == {
        "count": 12,
        "enabled": False,
    }
    assert resolve("/api/orders/${row.id}", refs) == "/api/orders/x"
    check_json([{"id": "x"}], {"ids": ["x"]}, "unit-only")
    check_json(
        [{"name": "metric", "value": 5}],
        {"where": {"name": "metric"}, "one": True, "path": ["value"], "gte": 0},
        "unit-only",
    )
    for value, assertion in [
        (True, {"equals": 1}),
        ([], {"contains": {"id": "x"}}),
        ([{"id": "y"}], {"ids": ["x"]}),
        ([{"id": "x"}], {"count": 0}),
    ]:
        with pytest.raises(AcceptanceFailure):
            check_json(value, assertion, "unit-only")


def github_env():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_EVENT_NAME": "pull_request",
        "ACCEPTANCE_HEAD_SHA": "a" * 40,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "2",
    }


def github_event():
    return {
        "action": "labeled",
        "label": {"name": "run-live-acceptance"},
        "pull_request": {
            "head": {"sha": "a" * 40, "repo": {"full_name": REPOSITORY}},
            "base": {"repo": {"full_name": REPOSITORY}},
        },
    }


def test_explicit_label_and_manual_dispatch_bind_exact_head_and_allow_rerun():
    env, event = github_env(), github_event()
    assert trusted_event(env, event)["head_sha"] == "a" * 40
    env.update(GITHUB_EVENT_NAME="workflow_dispatch", GITHUB_SHA="a" * 40)
    assert trusted_event(env, {})["event"] == "workflow_dispatch"


@pytest.mark.parametrize(
    "reason", ["fork", "wrong_label", "new_head", "synchronize", "pull_request_target", "local"]
)
def test_secret_scope_rejects_implicit_or_untrusted_events(reason):
    env, event = github_env(), github_event()
    if reason == "fork":
        event["pull_request"]["head"]["repo"]["full_name"] = "outside/fork"
    elif reason == "wrong_label":
        event["label"]["name"] = "bug"
    elif reason == "new_head":
        event["pull_request"]["head"]["sha"] = "b" * 40
    elif reason == "synchronize":
        event["action"] = "synchronize"
    elif reason == "pull_request_target":
        env["GITHUB_EVENT_NAME"] = reason
    else:
        env["GITHUB_ACTIONS"] = "false"
    with pytest.raises(AcceptanceFailure):
        trusted_event(env, event)


def configured_settings(tmp_path):
    return acceptance_settings(
        {
            "BASE_URL": "https://model.invalid/v1",
            "MODE": "unit-only-model",
            "API_KEY": "unit-only-key",
        },
        tmp_path,
    )


def test_live_suite_disables_optional_review_profile_as_well_as_flag(tmp_path):
    settings = configured_settings(tmp_path)
    assert settings.model_review is False
    assert settings.review_enabled is False
    assert settings.max_model_calls == MAX_MODEL_CALLS


def test_failure_events_keep_safe_structure_and_redact_before_bounding(tmp_path):
    settings = configured_settings(tmp_path)
    events = [
        {
            "id": 1,
            "kind": "assistant_failed",
            "data": {
                "stage": "planning",
                "code": "schema_validation",
                "response_id": "a" * 32,
                "content": "raw response must not be retained",
                "diagnostic": {
                    "attempt": 2,
                    "details": [
                        {
                            "type": "enum",
                            "path": ["unit-only-key"],
                            "constraints": {"enum": ["unit-only-key"]},
                            "message": "raw response must not be retained",
                        }
                    ],
                },
            },
        }
    ]
    store = SimpleNamespace(events=lambda run_id, after=0: events if after == 0 else [])
    retained = failure_events(store, "unit-only", settings)
    assert retained[0]["attempt"] == 2
    assert retained[0]["details"][0]["type"] == "enum"
    assert "unit-only-key" not in json.dumps(retained)
    assert "raw response" not in json.dumps(retained)


def test_schema_diagnostics_survive_failed_provider_responses_without_their_values(tmp_path):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    transport.inner.close()
    # Malformed content includes a secret-like value: only schema-owned paths survive.
    raw = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps({"title": "unit-only-key"})},
            }
        ],
        "usage": {"total_tokens": 7},
    }
    transport.inner = httpx.MockTransport(lambda request: httpx.Response(200, json=raw))
    transport.run_id, transport.stage, transport.schema = "unit-only", "plan", Plan
    try:
        response = transport.handle_request(
            httpx.Request(
                "POST",
                "https://model.invalid/v1/chat/completions",
                headers={"Authorization": "Bearer unit-only-key"},
                json={
                    "model": "unit-only-model",
                    "response_format": {"type": "json_object"},
                    "max_tokens": MAX_OUTPUT_TOKENS,
                },
            )
        )
        assert response.status_code == 200
        assert transport.receipts[0]["schema_valid"] is False
        assert transport.receipts[0]["validation_code"] == "schema_validation"
        assert "unit-only-key" not in json.dumps(transport.receipts)
        assert any(
            item["path"] == ["entities"] for item in transport.receipts[0]["schema_diagnostics"]
        )
    finally:
        transport.shutdown()


def test_autonomous_analysis_counts_as_requirement_without_relabeling_wire_receipt(
    tmp_path, monkeypatch
):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    gateway = ObservedGateway(settings, None, transport)
    # Test only the observation layer: there is no real-model receipt from this unit test.
    monkeypatch.setattr(ModelGateway, "complete", lambda *args, **kwargs: object())
    try:
        gateway.complete("unit-only", "recommend:1", "", {}, object)
        assert transport.stage == "recommend"
        assert gateway.traces == [
            {"run_id": "unit-only", "stage": "requirement", "validated": True}
        ]
    finally:
        transport.shutdown()


@pytest.mark.parametrize(
    "case", ["destination", "model", "token_budget", "call_budget", "authorization", "stream"]
)
def test_transport_bounds_actual_requests_before_dispatch(tmp_path, case):
    transport = BoundedTransport(configured_settings(tmp_path))
    transport.inner.close()
    calls = []
    transport.inner = httpx.MockTransport(
        lambda request: calls.append(request) or httpx.Response(200, json={})
    )
    transport.run_id, transport.stage = "unit-only", "plan"
    body = {
        "model": "unit-only-model",
        "response_format": {"type": "json_object"},
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "stream": False,
    }
    url, auth = "https://model.invalid/v1/chat/completions", "Bearer unit-only-key"
    if case == "destination":
        url = "https://outside.invalid/v1/chat/completions"
    elif case == "model":
        body["model"] = "different-model"
    elif case == "token_budget":
        body["max_completion_tokens"] += 1
    elif case == "call_budget":
        transport.calls["unit-only"] = MAX_MODEL_CALLS
    elif case == "authorization":
        auth = "wrong"
    else:
        body["stream"] = True
    with pytest.raises(OutputFailure):
        transport.handle_request(
            httpx.Request("POST", url, headers={"Authorization": auth}, json=body)
        )
    assert not calls
    transport.shutdown()


def success_receipts():
    """Fabricated metadata for negative aggregate tests only; never written as evidence."""
    return [
        {
            "case": case.identity,
            "source_digest": case.source_digest,
            "passed": True,
            "ready": True,
            "contract_preserved": True,
            "model_calls": 2,
            "provider_http_calls": 2,
            "completed_model_stages": ["requirement", "plan"],
            "cleanroom": {"passed": True, "real_browser": True},
            "scenario": {
                "passed": True,
                "restart": True,
                "checks": list(case.expected_checks),
                "browser": {"passed": True, "real_browser": True},
            },
        }
        for case in suite_cases()
    ]


@pytest.mark.parametrize(
    "reason",
    [
        "missing",
        "duplicate",
        "failure",
        "wrong_source",
        "no_browser",
        "missing_check",
        "no_model_plan",
        "fake_call_count",
        "over_budget",
    ],
)
def test_all_three_must_pass_with_real_calls_and_complete_evidence(reason):
    results = success_receipts()
    assert aggregate(suite_cases(), results)
    if reason == "missing":
        results.pop()
    elif reason == "duplicate":
        results[2] = copy.deepcopy(results[1])
    elif reason == "failure":
        results[2]["passed"] = False
    elif reason == "wrong_source":
        results[2]["source_digest"] = "f" * 64
    elif reason == "no_browser":
        results[2]["scenario"]["browser"]["real_browser"] = False
    elif reason == "missing_check":
        results[2]["scenario"]["checks"].pop()
    elif reason == "no_model_plan":
        results[2]["completed_model_stages"] = ["requirement"]
    elif reason == "fake_call_count":
        results[2]["provider_http_calls"] = 0
    else:
        results[2].update(model_calls=MAX_MODEL_CALLS + 1, provider_http_calls=MAX_MODEL_CALLS + 1)
    assert not aggregate(suite_cases(), results)


def test_workflow_uses_rnd_key_without_automatic_cost_trigger():
    root = Path(__file__).resolve().parents[1]
    raw = (root / ".github/workflows/template-project-acceptance.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(raw)
    events = workflow.get("on", workflow.get(True))
    assert set(events) == {"workflow_dispatch", "pull_request"}
    assert events["pull_request"]["types"] == ["labeled"]
    job = workflow["jobs"]["all-three-projects"]
    assert job["environment"] == "rnd"
    assert "run-live-acceptance" in job["if"]
    assert "head.repo.full_name == github.repository" in job["if"]
    secret_steps = [step for step in job["steps"] if "secrets." in json.dumps(step)]
    assert len(secret_steps) == 1
    assert secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"
    assert secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"
