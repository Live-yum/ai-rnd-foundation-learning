"""Harness integrity and synthetic HTTP checks. None of these are live-model evidence."""

import copy
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml
from conftest import new_run

from scripts.ci_template_projects import (
    MAX_FEEDBACK_BYTES,
    MAX_MODEL_CALLS,
    MAX_OUTPUT_TOKENS,
    MAX_TRACE_BYTES,
    REPOSITORY,
    BoundedTransport,
    ObservedGateway,
    acceptance_settings,
    aggregate,
    diagnostic_facts,
    failure_events,
    feedback_snapshot,
    feedback_vocabulary,
    trusted_event,
)
from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require_contract,
    require_scenario_checks,
    suite_cases,
)
from scripts.template_acceptance_runtime import check_json, resolve, run_scenario
from workbench.business_capabilities import business_analysis_conflicts, business_gaps
from workbench.domain import Plan, Requirement, digest
from workbench.generator import generate_basic
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_protocol import OutputFailure
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_feedback
from workbench.store import Store


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


@pytest.mark.parametrize(
    "field,attribute,actual,expected",
    [
        ("started_on", "filterable", True, False),
        ("started_on", "date_range", False, True),
        ("started_on", "required", False, True),
        ("pages", "minimum", 2, 1),
        ("title", "max_length", 199, 200),
        ("author", "searchable", False, True),
        ("note", "kind", "boolean", "text"),
    ],
)
def test_contract_failure_identifies_the_exact_declared_field_attribute(
    field, attribute, actual, expected
):
    case = suite_cases()[0]
    plan = fixture_plan(case)
    next(item for item in plan.entities[0].fields if item.name == field).__setattr__(
        attribute, actual
    )
    with pytest.raises(AcceptanceFailure) as caught:
        require_contract(case, plan.model_dump())
    assert caught.value.code == "contract_mismatch"
    assert caught.value.path == f"books.{field}.{attribute}"
    assert caught.value.contract_difference == {
        "attribute": attribute,
        "expected": expected,
        "actual": actual,
    }


def test_contract_comparison_still_ignores_display_labels_and_enum_order():
    case = suite_cases()[0]
    plan = fixture_plan(case)
    plan.entities[0].description = "A model-authored display description"
    for field in plan.entities[0].fields:
        field.label = "A model-authored display label"
        field.choices.reverse()
    assert require_contract(case, plan.model_dump())


def test_contract_comparison_does_not_treat_missing_attributes_as_explicit_null():
    case = suite_cases()[0]
    contract = copy.deepcopy(case.contract)
    contract["entities"]["books"]["title"]["pattern"] = None
    with pytest.raises(AcceptanceFailure) as caught:
        require_contract(replace(case, contract=contract), fixture_plan(case).model_dump())
    assert caught.value.path == "books.title.pattern"
    assert caught.value.contract_difference == {
        "attribute": "pattern",
        "expected": None,
        "actual": {"type": "missing"},
    }


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


@pytest.mark.parametrize(
    "content,category",
    [
        ('{\n "title": "unit-only-key",\n "entities": ]}', "expected_value"),
        ('{"unit-only-key":1,"unit-only-key":2}', "duplicate_json_key"),
    ],
)
def test_json_provider_receipts_keep_only_static_categories_and_numbers(
    tmp_path, content, category
):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    transport.inner.close()
    transport.inner = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
        )
    )
    transport.run_id, transport.stage, transport.schema = "unit-only", "plan", Plan
    try:
        transport.handle_request(
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
        receipt = transport.receipts[0]
        assert receipt["schema_valid"] is False
        assert receipt["validation_code"] == "invalid_json"
        detail = receipt["json_diagnostics"][0]
        assert detail["category"] == category
        assert detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}
        assert "message" not in detail
        assert "unit-only-key" not in json.dumps(receipt)
    finally:
        transport.shutdown()


def test_json_receipt_metadata_rejects_text_booleans_and_unbounded_numbers():
    details = diagnostic_facts(
        [
            {
                "type": "json_syntax",
                "category": "private-category-canary",
                "position": {"line": "private-location-canary", "column": True, "offset": -1},
                "lengths": {"characters": 2_000_001, "bytes": 37, "raw": "private-value-canary"},
                "message": "private-message-canary",
            }
        ]
    )
    assert details == [{"type": "json_syntax", "lengths": {"bytes": 37}}]
    assert "private-" not in json.dumps(details)


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
            {
                "run_id": "unit-only",
                "stage": "requirement",
                "logical_key": "recommend:1",
                "payload_sha256": digest({}),
                "feedback_sha256": digest({}),
                "resolution_feedback": {},
                "validated": True,
            }
        ]
    finally:
        transport.shutdown()


def test_real_gateway_preserves_design_feedback_before_terminal_json_failure(tmp_path):
    # Actual LangChain/ModelGateway/guard stack over an explicit mock HTTP provider;
    # these local receipts are never used as live-project acceptance evidence.
    case = suite_cases()[1]
    data = fixture_plan(case).model_dump()
    approved_grant = next(
        p
        for p in data["business"]["permissions"]
        if (p["role"], p["entity"]) == ("warehouse", "purchase_orders")
    )
    approved = Requirement(
        summary="Synthetic gateway diagnostic regression",
        users=["warehouse"],
        data_scope="shared",
        features=["Inventory"],
        acceptance=["Checks"],
        field_requirements=[{"entity": "items", "field": "stock", "minimum": 0}],
        facts={"business": {"permissions": [copy.deepcopy(approved_grant)]}},
    )
    approved_grant["actions"].remove("read_history")
    stock = next(
        f
        for e in data["entities"]
        if e["name"] == "items"
        for f in e["fields"]
        if f["name"] == "stock"
    )
    stock["minimum"] = -1
    candidate = Plan.model_validate(data)
    coverage, business = [], []
    reasons = coverage_gaps(approved, candidate, diagnostics=coverage)
    business_reasons = business_gaps(approved, candidate, diagnostics=business)
    assert coverage and business
    feedback = {
        "stage": "design",
        "round": 1,
        "blocked": reasons + business_reasons,
        "block_sources": ["requirement_coverage"] * len(reasons)
        + ["business_coverage"] * len(business_reasons),
        "coverage_diagnostics": coverage,
        "business_diagnostics": business,
    }
    settings = configured_settings(tmp_path)
    store = Store(settings)
    store.migrate()
    transport = BoundedTransport(settings)
    transport.inner.close()
    sent = []

    def provider(request):
        sent.append(json.loads(request.content))
        content = candidate.model_dump_json() if len(sent) <= 2 else '{"private-response-canary":]}'
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )

    transport.inner = httpx.MockTransport(provider)
    gateway = ObservedGateway(settings, store, transport, [case])
    run_id = new_run(store)
    payload = {
        "approved_requirement": approved.model_dump(),
        "resolution_feedback": {},
        "previous_plan": {},
    }
    try:
        assert (
            gateway.complete(run_id, "plan:1", "private-instruction-canary", payload, Plan)
            == candidate
        )
        payload.update(previous_plan=candidate.model_dump(), resolution_feedback=feedback)
        assert (
            gateway.complete(run_id, "plan:2", "private-instruction-canary", payload, Plan)
            == candidate
        )
        payload["resolution_feedback"] = {**feedback, "round": 2}
        with pytest.raises(ModelFailure):
            gateway.complete(run_id, "plan:3", "private-instruction-canary", payload, Plan)
        trace = gateway.receipt_trace(run_id)
        assert trace["omitted"] == 0
        assert [item["logical_key"] for item in trace["items"]] == ["plan:1", "plan:2", "plan:3"]
        assert [item["validated"] for item in trace["items"]] == [True, True, False]
        last = trace["items"][-1]
        assert last["payload_sha256"] == digest(payload)
        assert last["previous_plan_sha256"] == digest(candidate.model_dump())
        assert last["feedback_sha256"] == digest(payload["resolution_feedback"])
        assert trace["items"][1]["feedback_sha256"] != last["feedback_sha256"]
        shown = last["resolution_feedback"]
        assert shown["stage"] == "design" and shown["round"] == 2
        assert shown["block_sources"]["business_coverage"] == len(business_reasons)
        assert any(
            item.get("attribute") == "minimum" and item["expected"] == 0 and item["actual"] == -1
            for item in shown["coverage_diagnostics"]
        )
        assert any(
            item["source"]["domain"] == "permissions" for item in shown["business_diagnostics"]
        )
        assert [r["logical_key"] for r in transport.receipts] == [
            "plan:1",
            "plan:2",
            "plan:3",
            "plan:3",
        ]
        assert [r["schema_valid"] for r in transport.receipts] == [True, True, False, False]
        assert len(sent) == store.get_run(run_id)["model_calls"] == transport.calls[run_id] == 4
        assert json.loads(sent[2]["messages"][1]["content"]) == payload
        encoded = json.dumps(trace)
        assert "private-" not in encoded and "unit-only-key" not in encoded
        assert "blocked" not in shown and "previous_plan" not in last
    finally:
        transport.shutdown()
        store.engine.dispose()


def test_planning_diagnostic_projection_hides_unknown_keys_and_values_before_bounding(tmp_path):
    settings = configured_settings(tmp_path)
    secret = "unit-only-key"
    diagnostic = {
        "code": "business_scope_mismatch",
        "source": {
            "section": "facts",
            "domain": "permissions",
            "path": "business.private_identifier.permissions.0",
        },
        "expected": {
            "any_of": [
                [
                    {
                        "role": "technician",
                        "entity": "work_orders",
                        "action": "read_metrics",
                        "scope": "assigned",
                    }
                ]
            ]
        },
        "actual": [
            {
                "role": "technician",
                "entity": "work_orders",
                "actions": ["read", "read_metrics"],
                "scope": "all",
                "label": "private-label-canary",
                "api_key": secret,
                "content": "private-body-canary",
            }
        ],
    }
    feedback = {
        "stage": "design",
        "round": 2,
        "blocked": ["private-block-canary " + secret],
        "block_sources": ["business_coverage"],
        "business_diagnostics": [
            diagnostic,
            {
                "code": "business_unsupported_shape",
                "source": {
                    "section": "facts",
                    "domain": "policy",
                    "path": "business.registration.enabled",
                },
                "expected": {"enabled": True},
                "actual": {"enabled": False, "value": "private_identifier"},
            },
        ],
        "coverage_diagnostics": [
            {
                "code": "constraint_mismatch",
                "source": {"section": "field_requirements", "index": 0},
                "targets": [{"entity": "items", "field": "stock"}],
                "attribute": "pattern",
                "expected": "private-regex-canary",
                "actual": secret,
            }
        ],
        "analysis_diagnostics": [
            {
                "code": "requirement_business_shape",
                "target": {"entity": "books", "field": None},
                "sources": [
                    {
                        "source": {"section": "facts", "path": "business.private_identifier"},
                        "expected": {"entity": "books"},
                        "origin": "previous_requirement",
                        "previous_source": {
                            "section": "user_messages",
                            "index": 0,
                            "path": "private_identifier.permissions",
                            "text": "private-source-canary",
                        },
                        "excerpt": "private-excerpt-canary",
                    },
                    {
                        "source": {"section": "user_messages", "index": 1},
                        "expected": "private-input-canary",
                        "origin": "user_input",
                    },
                    {"source": {}, "expected": None, "origin": "private-origin-canary"},
                ],
            }
        ],
        "prompt": "private-prompt-canary",
        "previous_plan": {"title": "private-plan-canary"},
    }
    original = copy.deepcopy(feedback)
    shown = feedback_snapshot(feedback, settings, feedback_vocabulary(suite_cases()))
    assert feedback == original
    assert shown["business_diagnostics"][0]["source"]["path"] == "business.<key>.permissions.0"
    assert shown["business_diagnostics"][0]["expected"] == diagnostic["expected"]
    assert shown["business_diagnostics"][0]["actual"][0]["scope"] == "all"
    assert shown["business_diagnostics"][1]["expected"] == {"enabled": True}
    assert shown["business_diagnostics"][1]["actual"]["enabled"] is False
    assert shown["coverage_diagnostics"][0]["actual"]["characters"] == len("[redacted]")
    sources = shown["analysis_diagnostics"][0]["sources"]
    assert [record["origin"] for record in sources] == [
        "previous_requirement",
        "user_input",
        "unknown",
    ]
    assert sources[0]["previous_source"] == {
        "section": "user_messages",
        "index": 0,
        "path": "<key>.permissions",
    }
    assert sources[1]["source"] == {"section": "user_messages", "index": 1}
    encoded = json.dumps(shown)
    assert "private" not in encoded and secret not in encoded
    assert all(name not in encoded for name in ("api_key", "previous_plan", "prompt", "label"))


@pytest.mark.parametrize(
    "action,code",
    [
        ("private-action-canary", "requirement_business_shape"),
        ("read", "requirement_business_scope"),
    ],
)
def test_real_gateway_retains_safe_analysis_feedback_when_recommendation_retry_fails(
    tmp_path, action, code
):
    analysis = Requirement(
        summary="private-analysis-canary",
        users=[],
        data_scope="per_user",
        features=[],
        acceptance=[],
        facts={
            "private_fact_namespace": {
                "business": {
                    "permissions": [
                        {
                            "role": "private-role-canary",
                            "entity": "books",
                            "actions": [action],
                            "scope": "own",
                        }
                    ]
                }
            }
        },
    )
    issues = business_analysis_conflicts(analysis)
    assert len(issues) == 1 and issues[0]["code"] == code
    feedback = {
        "stage": "clarification",
        "round": 1,
        "blocked": [issues[0]["message"]],
        "analysis_diagnostics": analysis_feedback(issues),
    }
    settings = configured_settings(tmp_path)
    store = Store(settings)
    store.migrate()
    transport = BoundedTransport(settings)
    transport.inner.close()
    sent = []

    def provider(request):
        sent.append(json.loads(request.content))
        content = analysis.model_dump_json() if len(sent) == 1 else '{"private-response-canary":]}'
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )

    transport.inner = httpx.MockTransport(provider)
    gateway = ObservedGateway(settings, store, transport)
    run_id = new_run(store)
    try:
        gateway.complete(run_id, "recommend:1", "private-instruction-canary", {}, Requirement)
        payload = {"resolution_feedback": feedback, "current_requirement": {}}
        with pytest.raises(ModelFailure):
            gateway.complete(
                run_id, "recommend:2", "private-instruction-canary", payload, Requirement
            )
        trace = gateway.receipt_trace(run_id)
        assert [r["logical_key"] for r in trace["items"]] == ["recommend:1", "recommend:2"]
        last = trace["items"][-1]
        assert last["validated"] is False
        assert last["feedback_sha256"] == digest(feedback)
        assert last["payload_sha256"] == digest(payload)
        shown = last["resolution_feedback"]
        assert shown["stage"] == "clarification" and shown["round"] == 1
        assert shown["analysis_diagnostics_count"] == 1
        assert shown["analysis_diagnostics_omitted"] == 0
        diagnostic = shown["analysis_diagnostics"][0]
        assert diagnostic["code"] == code
        assert diagnostic["target"] == {"entity": "books", "field": None}
        assert diagnostic["attribute"] == "permissions"
        source = diagnostic["sources"][0]
        assert source["source"] == {
            "section": "facts",
            "path": "<key>.business.permissions.0",
            "domain": "permissions",
        }
        assert source["origin"] == "model_analysis"
        assert source["expected"]["scope"] == "own"
        assert source["expected"]["role"] == {"type": "string", "characters": 19}
        assert source["expected"]["actions"] == (
            ["read"] if action == "read" else [{"type": "string", "characters": len(action)}]
        )
        assert [r["logical_key"] for r in transport.receipts] == [
            "recommend:1",
            "recommend:2",
            "recommend:2",
        ]
        assert len(sent) == transport.calls[run_id] == store.get_run(run_id)["model_calls"] == 3
        assert "private" not in json.dumps(trace) and "unit-only-key" not in json.dumps(trace)
        assert all(
            key not in source for key in ("text", "excerpt", "user_sources", "previous_source")
        )
    finally:
        transport.shutdown()
        store.engine.dispose()


def test_planning_diagnostics_and_terminal_trace_have_explicit_byte_and_count_bounds(
    tmp_path, monkeypatch
):
    settings = configured_settings(tmp_path)
    vocabulary = feedback_vocabulary(suite_cases())
    large = {
        "stage": "design",
        "round": 2,
        "blocked": ["private-free-text" for _ in range(100)],
        "block_sources": ["business_coverage"] * 100,
        "business_diagnostics": [
            {
                "code": "business_unsupported_shape",
                "source": {
                    "section": "facts",
                    "domain": "permissions",
                    "path": ".".join(["private_identifier"] * 100),
                },
                "expected": [
                    {
                        "role": "technician",
                        "entity": "work_orders",
                        "actions": ["read_metrics"] * 13,
                        "scope": "assigned",
                    }
                ]
                * 13,
                "actual": None,
            }
        ]
        * 13,
    }
    bounded = feedback_snapshot(large, settings, vocabulary)
    assert len(json.dumps(bounded, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES
    assert bounded["business_diagnostics_count"] == 13
    assert bounded["business_diagnostics_omitted"] > 0
    assert bounded["blocked_count"] == 100 and bounded["block_sources"] == {
        "business_coverage": 100
    }
    assert "private" not in json.dumps(bounded)
    analysis = feedback_snapshot(
        {
            "stage": "clarification",
            "analysis_diagnostics": [
                {
                    "code": "requirement_business_shape",
                    "target": {"entity": "books", "field": None},
                    "attribute": "permissions",
                    "sources": [
                        {
                            "source": {
                                "section": "facts",
                                "path": "private.business.permissions.0",
                            },
                            "expected": {"entity": "books", "actions": ["read"], "scope": "own"},
                            "origin": "model_analysis",
                            "excerpt": "private-analysis-canary",
                        }
                    ]
                    * 6,
                }
            ]
            * 13,
        },
        settings,
        vocabulary,
    )
    assert len(json.dumps(analysis, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES
    assert analysis["analysis_diagnostics_count"] == 13
    assert analysis["analysis_diagnostics_omitted"] > 0
    first = analysis["analysis_diagnostics"][0]
    assert first["sources_count"] == 6 and first["sources_omitted"] == 2
    assert len(first["sources"]) == 4
    assert "private" not in json.dumps(analysis)
    transport = BoundedTransport(settings)
    gateway = ObservedGateway(settings, None, transport)
    monkeypatch.setattr(ModelGateway, "complete", lambda *args, **kwargs: object())
    try:
        trace_feedback = {**large, "business_diagnostics": large["business_diagnostics"][:1]}
        for index in range(30):
            gateway.complete(
                "unit-only", f"plan:{index}", "", {"resolution_feedback": trace_feedback}, object
            )
        gateway.traces[-1]["validated"] = False
        trace = gateway.receipt_trace("unit-only")
        assert len(json.dumps(trace, ensure_ascii=False).encode()) <= MAX_TRACE_BYTES
        assert 0 < len(trace["items"]) < MAX_MODEL_CALLS + 1
        assert trace["omitted"] == 30 - len(trace["items"])
        assert trace["items"][-1]["logical_key"] == "plan:29"
        assert trace["items"][-1]["validated"] is False
        assert not transport.receipts
    finally:
        transport.shutdown()


@pytest.mark.parametrize("failure_kind", ["workflow", "contract"])
def test_complete_offline_terminal_receipts_never_export_workflow_error_text(
    tmp_path, monkeypatch, capsys, failure_kind
):
    from scripts import ci_template_projects as suite

    settings = configured_settings(tmp_path)
    error = "private_fact_namespace.permissions.0: private-excerpt-canary unit-only-key"
    internal_errors = []

    class FailedWorker:
        """Inject a terminal failure into the real Store; no model or browser runs."""

        def __init__(self, settings, store, gateway):
            self.store = store

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def tick(self):
            job = self.store.claim()
            if job is None:
                return False
            if failure_kind == "workflow":
                self.store.finish(job, "BLOCKED", error=error)
            else:
                self.store.finish(job, "READY", result={})
            internal_errors.append(self.store.get_run(job["run_id"])["error"])
            return True

    reports = tmp_path / "reports"
    monkeypatch.setattr(suite, "Runtime", FailedWorker)
    monkeypatch.setattr(suite, "REPORTS", reports)
    if failure_kind == "contract":

        def reject_offline_candidate(case, *args):
            """Exercise the real oracle, without generating or accepting a product."""
            plan = fixture_plan(case)
            plan.title, plan.acceptance = error, [error]
            field = plan.entities[0].fields[0]
            field.label = error
            if case.identity == "reading-shelf":
                category = next(item for item in plan.entities[0].fields if item.name == "category")
                category.choices = [f"{error} {index} {'x' * 100}" for index in range(50)]
            else:
                field.max_length += 1
            return require_contract(case, plan.model_dump())

        monkeypatch.setattr(suite, "verify_delivery", reject_offline_candidate)
    report = suite.run_suite(settings, tmp_path, {"offline_guard": True})
    assert internal_errors == [error if failure_kind == "workflow" else None] * 3
    assert report["passed"] is False and report["real_model"] is False
    assert report["actual_model_calls"] == 0 and len(report["cases"]) == 3
    for receipt in report["cases"]:
        assert receipt["passed"] is False
        if failure_kind == "workflow":
            assert receipt["workflow_status"] == "BLOCKED"
            assert receipt["failure"]["workflow_error"] == {
                "code": "workflow_not_ready",
                "status": "BLOCKED",
                "sha256": hashlib.sha256(error.encode()).hexdigest(),
                "characters": len(error),
            }
        else:
            assert receipt["workflow_status"] == "READY"
            assert receipt["failure"]["code"] == "contract_mismatch"
            difference = receipt["failure"]["contract_difference"]
            assert len(json.dumps(difference).encode()) < 500
            if receipt["case"] == "reading-shelf":
                assert receipt["failure"]["path"] == "books.category.choices"
                assert difference["attribute"] == "choices"
                assert difference["expected"]["items"] == 3
                assert difference["actual"]["items"] == 50
                assert set(difference["actual"]) == {"type", "items", "sha256"}
            else:
                assert difference["attribute"] == "max_length"
                assert difference["actual"] == difference["expected"] + 1
    output = capsys.readouterr().out
    emitted = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert emitted == report["cases"]
    for text in [
        output,
        json.dumps(report),
        *(path.read_text() for path in reports.glob("*.json")),
    ]:
        assert all(
            canary not in text
            for canary in ("private_fact_namespace", "private-excerpt-canary", "unit-only-key")
        )


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
