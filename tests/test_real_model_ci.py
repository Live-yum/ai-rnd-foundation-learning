"""No paid calls here: test doubles only test the real-run harness' safety boundaries."""

import json

import httpx
import pytest

from scripts.ci_real_model import (
    ENDPOINT,
    MODEL,
    REFS,
    REPOSITORY,
    SMOKE_PAYLOAD,
    BoundedRealTransport,
    SafeFailure,
    configuration,
    require_customer_spec,
    smoke,
    trusted_dispatch,
)
from workbench.settings import ROOT


def config():
    return configuration({"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": "test-only-secret"})


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"BASE_URL": "https://evil.example", "MODE": MODEL, "API_KEY": "secret"},
        {"BASE_URL": ENDPOINT, "MODE": "fallback-model", "API_KEY": "secret"},
        {"BASE_URL": ENDPOINT, "MODE": MODEL},
        {"BASE_URL": ENDPOINT + "/v1", "MODE": MODEL, "API_KEY": "secret"},
    ],
)
def test_invalid_configuration_fails_before_provider_access(values):
    with pytest.raises(SafeFailure, match="configuration"):
        configuration(values)


def test_secret_not_in_config_representation():
    assert "test-only-secret" not in repr(config())


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_EVENT_NAME", "pull_request_target"),
        ("GITHUB_EVENT_NAME", "schedule"),
        ("GITHUB_REPOSITORY", "attacker/fork"),
        ("GITHUB_REF", "refs/heads/untrusted"),
    ],
)
def test_reject_untrusted_execution_context(key, value):
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": next(iter(REFS)),
    }
    env[key] = value
    with pytest.raises(SafeFailure, match="untrusted_dispatch"):
        trusted_dispatch(env)


@pytest.mark.parametrize("status", [301, 400, 401, 403, 404, 429, 500])
def test_smoke_provider_error_is_sanitized_and_never_retried(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"message": "test-only-secret raw provider data"}},
            headers={"location": "https://evil.example"},
        )

    with pytest.raises(SafeFailure) as caught:
        smoke(config(), httpx.MockTransport(handler))
    assert caught.value.status == status
    assert "test-only-secret" not in str(caught.value)
    assert len(calls) == 1
    assert str(calls[0].url) == ENDPOINT + "/chat/completions"
    assert json.loads(calls[0].content) == SMOKE_PAYLOAD


def test_successful_smoke_receipt_has_no_provider_content():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "OK test-only-secret"}}],
                "provider_private_field": "must not leave",
            },
        )
    )
    receipt = smoke(config(), transport)
    assert receipt == {
        "passed": True,
        "http_status": 200,
        "actual_provider_request": True,
    }


@pytest.mark.parametrize("body", [{}, {"choices": []}, {"choices": [{"message": {"content": ""}}]}])
def test_invalid_smoke_response_fails_closed(body):
    with pytest.raises(SafeFailure, match="invalid_smoke_response"):
        smoke(
            config(),
            httpx.MockTransport(lambda request: httpx.Response(200, json=body)),
        )


def test_transport_rejects_substitution_and_bounds_tokens_and_calls():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    requests = []
    transport.transport = httpx.MockTransport(
        lambda req: requests.append(req) or httpx.Response(200)
    )
    try:
        transport.handle_request(
            httpx.Request(
                "POST",
                ENDPOINT + "/chat/completions",
                headers={"Authorization": "Bearer test-only-secret"},
                json={"model": MODEL, "max_tokens": 90000},
            )
        )
        assert json.loads(requests[0].content)["max_tokens"] == 65536
        with pytest.raises(SafeFailure, match="model_substitution"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": "fallback"})
            )
        with pytest.raises(SafeFailure, match="request_scope"):
            transport.handle_request(
                httpx.Request(
                    "POST",
                    "https://evil.example/chat/completions",
                    json={"model": MODEL},
                )
            )
        transport.calls = 17
        with pytest.raises(SafeFailure, match="request_scope_or_budget"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": MODEL})
            )
    finally:
        transport.shutdown()


@pytest.mark.parametrize("mutation", ["roles", "metrics", "isolation", "workflow", "category"])
def test_actual_model_plan_must_preserve_explicit_customer_obligations(mutation):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    require_customer_spec(spec)
    if mutation == "isolation":
        spec["data_scope"] = "per_user"
    elif mutation == "roles":
        spec["business"]["registration"]["default_role"] = "manager"
    elif mutation == "metrics":
        spec["business"]["metrics"] = []
    elif mutation == "workflow":
        spec["business"]["workflows"] = []
    else:
        spec["entities"][0]["fields"][3]["choices"] = ["企业"]
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize(
    "name,change",
    [
        ("total", {"filters": [{"field": "request_state", "value": "resolved"}]}),
        ("resolved_total", {"filters": []}),
        (
            "resolved_total",
            {"filters": [{"field": "request_state", "op": "ne", "value": "resolved"}]},
        ),
        (
            "resolved_total",
            {"entity": "tasks", "filters": [{"field": "task_state", "value": "resolved"}]},
        ),
        (
            "resolved_total",
            {
                "filters": [
                    {"field": "request_state", "value": "resolved"},
                    {"field": "priority", "value": "紧急"},
                ]
            },
        ),
        ("resolution", {"start_field": "due_at"}),
        ("resolution", {"end_field": "due_at"}),
        ("resolution", {"filters": [{"field": "priority", "value": "紧急"}]}),
        ("customer_categories", {"entity": "requests", "group_by": "customer_id"}),
        ("customer_categories", {"group_by": "organization"}),
        ("customer_categories", {"filters": [{"field": "category", "value": "企业"}]}),
        ("daily", {"time_field": "due_at"}),
        ("daily", {"entity": "customers"}),
        ("daily", {"filters": [{"field": "request_state", "value": "resolved"}]}),
    ],
)
def test_customer_gate_requires_each_metric_meaning_not_just_four_kinds(name, change):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    next(metric for metric in spec["business"]["metrics"] if metric["name"] == name).update(change)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_customer_gate_accepts_provider_metric_names_extra_metrics_and_equivalent_resolution_filter():
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    for number, metric in enumerate(spec["business"]["metrics"]):
        metric["name"] = f"provider_metric_{number}"
        if metric["kind"] == "average_duration":
            metric["filters"] = []
        elif metric["filters"]:
            metric["filters"] = [{"field": "request_state", "op": "in", "value": ["resolved"]}]
    assert len(spec["business"]["metrics"]) > 5
    require_customer_spec(spec)


@pytest.mark.parametrize("entity", ["requests", "tasks"])
@pytest.mark.parametrize(
    "event,transition",
    [
        ("assigned", None),
        ("note_added", None),
        ("transitioned", "start"),
        ("transitioned", "resolve"),
        ("due", None),
    ],
)
def test_customer_gate_requires_every_requested_reminder(entity, event, transition):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    spec["business"]["notifications"] = [
        notice
        for notice in spec["business"]["notifications"]
        if (notice["entity"], notice["event"], notice["transition"]) != (entity, event, transition)
    ]
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_customer_gate_only_pins_the_explicit_resolution_recipient():
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    for notice in spec["business"]["notifications"]:
        if (notice["entity"], notice["transition"]) != ("requests", "resolve"):
            notice["recipient"] = "creator" if notice["recipient"] == "assignee" else "assignee"
    require_customer_spec(spec)
    for notice in spec["business"]["notifications"]:
        if (notice["entity"], notice["transition"]) == ("requests", "resolve"):
            notice["recipient"] = "assignee"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role", ["service", "employee"])
@pytest.mark.parametrize("action", ["create", "update", "archive", "add_note", "read_audit"])
def test_customer_query_access_never_implies_customer_write_or_audit_permissions(role, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    next(
        grant
        for grant in spec["business"]["permissions"]
        if grant["role"] == role and grant["entity"] == "customers"
    )["actions"].append(action)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role", ["service", "employee"])
def test_customer_role_administration_is_manager_only(role):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    spec["business"]["role_admin_roles"].append(role)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role,scope", [("service", "assigned"), ("employee", "own")])
def test_customer_collaboration_tasks_are_created_only_by_managers(role, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        (
            grant
            for grant in spec["business"]["permissions"]
            if grant["role"] == role and grant["entity"] == "tasks"
        ),
        None,
    )
    if permission is None:
        spec["business"]["permissions"].append(
            {"role": role, "entity": "tasks", "actions": ["read", "create"], "scope": scope}
        )
    else:
        permission["actions"].append("create")
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize(
    "role,entity,action",
    [
        ("manager", "customers", action)
        for action in ("create", "read", "update", "archive", "read_audit")
    ]
    + [
        ("manager", entity, action)
        for entity in ("requests", "tasks")
        for action in (
            "create",
            "read",
            "update",
            "archive",
            "add_note",
            "read_history",
            "read_audit",
            "assign",
            "transition",
        )
    ]
    + [
        ("service", entity, action)
        for entity in ("requests", "tasks")
        for action in ("read", "update", "add_note", "transition", "read_history", "read_audit")
    ]
    + [("employee", "requests", action) for action in ("create", "read")],
)
def test_customer_gate_rejects_each_explicit_role_action_omission(role, entity, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        grant
        for grant in spec["business"]["permissions"]
        if (grant["role"], grant["entity"]) == (role, entity)
    )
    permission["actions"].remove(action)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("entity", ["customers", "requests", "tasks"])
@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_customer_managers_require_all_record_scope(entity, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        grant
        for grant in spec["business"]["permissions"]
        if grant["role"] == "manager" and grant["entity"] == entity
    )
    permission["scope"] = scope
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role,scope", [("service", "assigned"), ("employee", "own")])
def test_customer_collaboration_task_assignment_is_manager_only(role, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        (
            grant
            for grant in spec["business"]["permissions"]
            if grant["role"] == role and grant["entity"] == "tasks"
        ),
        None,
    )
    if permission is None:
        spec["business"]["permissions"].append(
            {"role": role, "entity": "tasks", "actions": ["read", "assign"], "scope": scope}
        )
    else:
        permission["actions"].append("assign")
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_workflow_is_manual_environment_scoped_and_artifact_allowlisted():
    import yaml

    doc = yaml.load(
        (ROOT / ".github/workflows/real-model.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert set(doc["on"]) == {"workflow_dispatch"}
    job = doc["jobs"]["real-model"]
    assert job["environment"] == "rnd"
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert REPOSITORY in job["if"]
    secret_steps = [step for step in job["steps"] if "API_KEY" in step.get("env", {})]
    assert len(secret_steps) == 2
    assert secret_steps[0]["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"
    assert secret_steps[0]["env"]["BASE_URL"] == "${{ vars.BASE_URL }}"
    assert secret_steps[0]["env"]["MODE"] == "${{ vars.MODE }}"
    uploads = [
        step for step in job["steps"] if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert [step["with"]["path"] for step in uploads] == [
        "reports/real-model/summary.json",
        "reports/real-model/screenshots/*.png",
    ]
    entry = yaml.load(
        (ROOT / ".github/workflows/native-probe.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert set(entry["on"]) == {"workflow_dispatch", "pull_request"}
    inputs = entry["on"]["workflow_dispatch"]["inputs"]
    assert inputs["real_model"]["type"] == "boolean"
    assert inputs["real_model"]["default"] == "false"
    assert inputs["real_model"]["required"] == "false"
    assert inputs["expected_sha"]["type"] == "string"
    assert inputs["expected_sha"]["default"] == ""
    assert set(entry["jobs"]) == {"verify-bundles", "real-model"}
    assert entry["jobs"]["verify-bundles"].get("environment") != "rnd"
    paid = entry["jobs"]["real-model"]
    assert paid["environment"] == "rnd"
    assert "uses" not in paid
    assert "github.event_name == 'workflow_dispatch'" in paid["if"]
    assert "inputs.real_model == true" in paid["if"]
    assert f"github.repository == '{REPOSITORY}'" in paid["if"]
    for ref in REFS:
        assert f"github.ref == '{ref}'" in paid["if"]
    assert "API_KEY" not in entry.get("env", {})
    assert "API_KEY" not in paid.get("env", {})
    guard = paid["steps"][0]
    assert guard["shell"] == "bash"
    assert guard["env"] == {"EXPECTED_SHA": "${{ inputs.expected_sha }}"}
    assert "set -euo pipefail" in guard["run"]
    assert '[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]' in guard["run"]
    assert 'test "$EXPECTED_SHA" = "$GITHUB_SHA"' in guard["run"]
    checkout = paid["steps"][1]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert checkout["with"]["persist-credentials"] == "false"
    paid_secret_steps = [step for step in paid["steps"] if "API_KEY" in step.get("env", {})]
    assert len(paid_secret_steps) == 2
    for step in paid_secret_steps:
        assert step["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"
        assert step["env"]["BASE_URL"] == "${{ vars.BASE_URL }}"
        assert step["env"]["MODE"] == "${{ vars.MODE }}"
    assert [step["run"] for step in paid_secret_steps] == [
        "uv run python -m scripts.ci_real_model --phase smoke",
        "uv run python -m scripts.ci_real_model --phase full --template ${{ matrix.template }}",
    ]
    paid_uploads = [
        step for step in paid["steps"] if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert [step["with"]["path"] for step in paid_uploads] == [
        "reports/real-model/summary.json",
        "reports/real-model/approved-plan-replay.json",
        "reports/real-model/unapproved-design-contract.json",
        "reports/real-model/screenshots/*.png",
    ]
    assert paid_uploads[1]["if"] == "failure()"
    assert paid_uploads[1]["with"]["retention-days"] == "7"
    assert paid_uploads[2]["if"] == "failure()"
    assert paid_uploads[2]["with"]["retention-days"] == "7"


def test_all_profiles_use_authorized_configuration_despite_hostile_ambient_overrides(
    tmp_path, monkeypatch
):
    from scripts.ci_real_model import acceptance_settings
    from workbench.settings import STAGES

    monkeypatch.setenv("PLANNING_BASE_URL", "https://evil.example")
    monkeypatch.setenv("CODING_MODE", "silent-fallback")
    settings = acceptance_settings(config(), tmp_path)
    settings.require_model()
    for stage in STAGES:
        profile = settings.model_for(stage)
        assert profile.base_url == ENDPOINT and profile.model == MODEL
        assert profile.api_key.get_secret_value() == "test-only-secret"
    assert settings.max_model_calls == 16
    assert settings.install_products is True
    assert settings.model_review is True


def test_full_run_requires_matching_same_run_successful_smoke(tmp_path):
    from scripts.ci_real_model import verified_smoke_receipt

    path = tmp_path / "summary.json"
    env = {"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "a" * 40}
    with pytest.raises(SafeFailure, match="matching_successful_smoke"):
        verified_smoke_receipt(path, config(), env)
    receipt = {
        "passed": True,
        "acceptance_scope": "smoke_only",
        "model": MODEL,
        "endpoint": ENDPOINT,
        "run_identity": ["1", "2", "a" * 40],
        "actual_http_calls": 1,
        "provider_statuses": [200],
        "smoke": {"passed": True, "http_status": 200, "actual_provider_request": True},
    }
    path.write_text(json.dumps(receipt), encoding="utf-8")
    assert verified_smoke_receipt(path, config(), env)["passed"] is True
    env["GITHUB_SHA"] = "b" * 40
    with pytest.raises(SafeFailure, match="matching_successful_smoke"):
        verified_smoke_receipt(path, config(), env)


def test_exact_user_smoke_payload_preserved_by_real_transport():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    requests = []
    transport.transport = httpx.MockTransport(
        lambda req: requests.append(req) or httpx.Response(200)
    )
    try:
        transport.handle_request(
            httpx.Request(
                "POST",
                ENDPOINT + "/chat/completions",
                headers={"Authorization": "Bearer test-only-secret"},
                json=SMOKE_PAYLOAD,
            )
        )
        assert json.loads(requests[0].content) == SMOKE_PAYLOAD
        assert "max_tokens" not in json.loads(requests[0].content)
        with pytest.raises(SafeFailure, match="unexpected_authorization"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json=SMOKE_PAYLOAD)
            )
    finally:
        transport.shutdown()


def test_actual_actions_empty_secret_mapping_identifies_only_field_presence():
    # The failed Actions job provided correct vars and an empty API_KEY binding.
    env = {"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": ""}
    with pytest.raises(SafeFailure) as caught:
        configuration(env)
    assert caught.value.code == "missing_configuration_API_KEY"
    assert caught.value.details == {
        "BASE_URL_present": True,
        "MODE_present": True,
        "API_KEY_present": False,
        "BASE_URL_matches_authorized_destination": True,
        "MODE_matches_authorized_model": True,
    }
    assert ENDPOINT not in json.dumps(caught.value.details)
    assert MODEL not in json.dumps(caught.value.details)


@pytest.mark.parametrize("value", [None, 1, True, [], {}])
def test_non_string_mode_reports_field_name_not_value(value):
    with pytest.raises(SafeFailure) as caught:
        configuration({"BASE_URL": ENDPOINT, "MODE": value, "API_KEY": "test-only-secret"})
    assert caught.value.code == "invalid_configuration_type_MODE"
    assert "test-only-secret" not in str(caught.value)


def test_string_actions_values_and_exact_secret_mapping_are_accepted():
    cfg = configuration({"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": "test-only-secret"})
    assert cfg.model == MODEL and cfg.base_url == ENDPOINT
    assert cfg.key.get_secret_value() == "test-only-secret"


@pytest.mark.parametrize("ref", sorted(REFS))
def test_only_explicit_manual_runs_on_authorized_branches_can_use_provider(tmp_path, ref):
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": ref,
    }
    trusted_dispatch(env)
    # The former iteration marker cannot re-enable automatic paid calls.
    path = tmp_path / "event.json"
    path.write_text(
        json.dumps(
            {
                "head_commit": {
                    "message": "test: run authorized real-model validation iteration",
                    "id": "a" * 40,
                },
                "after": "a" * 40,
                "repository": {"full_name": REPOSITORY},
            }
        ),
        encoding="utf-8",
    )
    env.update(GITHUB_EVENT_NAME="push", GITHUB_SHA="a" * 40, GITHUB_EVENT_PATH=str(path))
    with pytest.raises(SafeFailure, match="untrusted_dispatch"):
        trusted_dispatch(env)


def test_provider_diagnostics_emit_only_schema_codes_counts_and_flags():
    from scripts.ci_real_model import response_receipt
    from workbench.domain import Requirement

    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({"injected-private-field": "test-only-secret"}),
                        "reasoning_content": "private reasoning must never leave",
                    },
                }
            ],
            "usage": {"total_tokens": 42, "secret": "test-only-secret"},
        }
    ).encode()
    receipt = response_receipt(200, raw, "requirement", Requirement)
    assert receipt["schema_valid"] is False
    assert receipt["schema_error_types"] == ["extra_forbidden", "missing"]
    assert receipt["usage"] == {"total_tokens": 42}
    encoded = json.dumps(receipt)
    for forbidden in (
        "test-only-secret",
        "private reasoning",
        "injected-private-field",
    ):
        assert forbidden not in encoded


def test_buffered_diagnostic_transport_preserves_client_response_and_secret_privacy():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    body = {
        "choices": [{"finish_reason": "stop", "message": {"content": "OK"}}],
        "usage": {"total_tokens": 10},
    }
    transport.transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    try:
        assert smoke(config(), transport)["passed"] is True
        assert transport.receipts[0]["finish_reason"] == "stop"
        assert transport.receipts[0]["usage"] == {"total_tokens": 10}
        assert "test-only-secret" not in json.dumps(transport.receipts)
    finally:
        transport.shutdown()


def test_customer_prompt_is_prose_not_precomputed_plan():
    from scripts.ci_real_model import customer_request

    request = customer_request()
    assert "客户服务管理系统" in request
    assert "不是模型响应" in request
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    require_customer_spec(plan)
    plan["business"]["metrics"] = []
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(plan)


def test_paid_matrix_covers_three_native_ui_families():
    import yaml

    for name in ("native-probe.yml", "real-model.yml"):
        doc = yaml.load(
            (ROOT / ".github/workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader
        )
        job = doc["jobs"]["real-model"]
        assert {row["template"] for row in job["strategy"]["matrix"]["include"]} == {
            "python-basic",
            "fastapiadmin",
            "yudao-vben",
        }
        assert "feat/customer-service-acceptance" in job["if"]
        assert not any(
            "API_KEY" in step.get("env", {}) for step in job["steps"] if step.get("uses")
        )


def test_requirement_snapshot_preserves_entity_mapping_without_text():
    from scripts.ci_real_model import contract_snapshot

    result = contract_snapshot(
        {
            "field_requirements": [
                {"entity": "requests", "field": "title", "required": True},
                {"entity": "tasks", "field": "title", "required": False},
            ],
            "features": ["test-only-secret"],
        },
        requirement=True,
    )
    assert [item["entity"] for item in result] == ["requests", "tasks"]
    assert "test-only-secret" not in json.dumps(result)


def test_safe_coverage_diagnostics_include_source_and_no_raw_prose_or_choices():
    from scripts.ci_real_model import safe_coverage_details
    from workbench.domain import Plan, Requirement

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    requirement = Requirement(
        summary="test-only-secret",
        users=["test-only-secret"],
        features=["customers：category必须可搜索 test-only-secret"],
        acceptance=[],
        data_scope="shared",
        facts={"customers": {"category": {"choices": ["test-only-secret"]}}},
    )
    result = safe_coverage_details(requirement.model_dump(), plan.model_dump())
    assert any(item["source"]["section"] == "features" for item in result)
    assert any(
        item["source"]["encoding"] == "structured"
        for item in result
        if item["source"]["section"] == "facts"
    )
    assert any(item["targets"] == [{"entity": "customers", "field": "category"}] for item in result)
    assert any(item.get("expected_count") == 1 for item in result)
    assert "test-only-secret" not in json.dumps(result)


def test_native_label_failure_is_exact_finite_code_with_no_description_export():
    from scripts.ci_real_model import safe_native_plan_details

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["entities"][0]["description"] = "客户管理，test-only-secret"
    result = safe_native_plan_details(plan)
    assert result["code"] == "native_label_contract"
    assert result["entity_labels"][0]["allowed_characters"] is False
    assert result["entity_labels"][0]["single_line"] is True
    assert "test-only-secret" not in json.dumps(result)


def test_every_native_plan_validation_message_has_a_finite_safe_code():
    import ast
    import inspect

    from scripts.ci_real_model import DESIGN_REASON_CODES
    from workbench.native_delivery import runtime_config
    from workbench.native_modules import validate_plan

    for function in (validate_plan, runtime_config):
        tree = ast.parse(inspect.getsource(function))
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                assert isinstance(node.exc.args[0], ast.Constant)
                assert node.exc.args[0].value in DESIGN_REASON_CODES


def test_workflow_diagnostics_separate_model_coverage_and_native_origins():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_workflow_details
    from workbench.domain import Plan, Requirement
    from workbench.requirement_coverage import coverage_gaps

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["unsupported"] = ["模板日期范围能力不支持 test-only-secret"]
    requirement = Requirement(
        summary="test-only-secret",
        users=["客服"],
        data_scope="shared",
        features=["customers：category可搜索 test-only-secret"],
        acceptance=[],
    )
    coverage = coverage_gaps(requirement, Plan.model_validate(plan))

    class Store:
        def get_run(self, run_id):
            return {
                "status": "BLOCKED",
                "template": "python-basic",
                "model_calls": 4,
                "pending": {
                    "stage": "design",
                    "data": {
                        "blocked": [*plan["unsupported"], *coverage],
                        "block_sources": [
                            "planner_unsupported",
                            *["requirement_coverage"] * len(coverage),
                        ],
                    },
                },
            }

        def latest_revision(self, run_id, stage):
            return (
                {"requirement": requirement.model_dump()}
                if stage == "requirements"
                else {"plan": plan}
            )

    result = safe_workflow_details(
        Store(), "run", [], text_budget=DiagnosticTextBudget(secrets=("test-only-secret",))
    )
    assert result["coverage_diagnostics"][0]["codes"] == ["planner_unsupported"]
    assert result["coverage_diagnostics"][0]["origin"] == "planner_unsupported"
    assert result["coverage_diagnostics"][1]["origin"] == "requirement_coverage"
    assert result["unsupported_diagnostics"][0]["topics"] == ["date_range", "capability"]
    assert "test-only-secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "value,secret",
    [
        ("API_KEY=credential_canary", "credential_canary"),
        ('{"password": "password_canary"}', "password_canary"),
        ("诊断：密码：password_canary", "password_canary"),
        ("request failed Authorization: Bearer header_canary", "header_canary"),
        ('metadata "Cookie": "session=cookie_canary"', "cookie_canary"),
        ("postgresql+psycopg://alice:url_canary@127.0.0.1/private", "url_canary"),
        ("https://example.invalid/?access_token=query_canary", "query_canary"),
        ("Bearer bearer_canary", "bearer_canary"),
        ("sk-testcredentialcanary123", "sk-testcredentialcanary123"),
        ("github_pat_credentialcanary123", "github_pat_credentialcanary123"),
        ("eyJhbGciOiJIUzI1NiJ9.credentialcanary.signature", "credentialcanary"),
    ],
)
def test_validation_excerpt_scrubs_credentials_headers_tokens_and_url_userinfo(value, secret):
    from scripts.ci_real_model import DiagnosticTextBudget

    result = DiagnosticTextBudget().excerpt(value)
    assert secret not in result
    assert "REDACTED" in result


def test_exact_key_redaction_precedes_truncation_and_total_budget_is_shared():
    from scripts.ci_real_model import DiagnosticTextBudget

    secret = "exact-key-canary-private"
    budget = DiagnosticTextBudget(secrets=(secret,))
    first = budget.excerpt("x" * 595 + secret)
    assert "exact" not in first and len(first) <= 600
    rest = budget.excerpts(["y" * 1000] * 20)
    assert len(first) + sum(map(len, rest)) == 6000
    assert all(len(item) <= 600 for item in rest)
    assert budget.excerpt("more") == ""


def test_safe_coverage_excerpt_is_selected_and_redacted_without_full_requirement():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_coverage_details
    from workbench.domain import Requirement

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    requirement = Requirement(
        summary="private summary not selected",
        users=["not selected"],
        data_scope="shared",
        features=["customers：name 必须支持精确筛选，opaque-private-canary"],
        acceptance=["unrelated unselected wording"],
    )
    result = safe_coverage_details(
        requirement.model_dump(),
        plan,
        text_budget=DiagnosticTextBudget(secrets=("opaque-private-canary",)),
    )
    rendered = json.dumps(result, ensure_ascii=False)
    assert "必须支持精确筛选" in rendered
    assert "opaque-private-canary" not in rendered
    assert "private summary" not in rendered and "unrelated unselected" not in rendered


def test_review_gap_diagnostics_preserve_blocking_count_and_omit_other_model_text():
    from scripts.ci_real_model import DiagnosticTextBudget, completed_stage_details
    from workbench.domain import ModelReview

    review = ModelReview(
        summary="raw private provider summary",
        observations=["raw private provider observation"],
        uncovered_requirements=["客户历史请求未验证，opaque-private-canary"],
    )
    result = completed_stage_details(
        review, DiagnosticTextBudget(secrets=("opaque-private-canary",))
    )
    assert result["uncovered_requirements_count"] == 1
    assert "客户历史请求未验证" in result["uncovered_requirement_excerpts"][0]
    encoded = json.dumps(result, ensure_ascii=False)
    assert "opaque-private-canary" not in encoded and "raw private provider" not in encoded
    assert review.uncovered_requirements == ["客户历史请求未验证，opaque-private-canary"]


def test_runtime_diagnostics_keep_exact_failure_stage_and_safe_headline(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    (tmp_path / "progress.json").write_text(
        json.dumps(
            {
                "template": "fastapiadmin",
                "stage": "customer-service-http",
                "environment": "private environment not selected",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "failure.log").write_text(
        "AssertionError at business_probe.py:271 (customer_service_acceptance): "
        "Native API failed: POST /business/requests/create HTTP 422 exact-key-canary\n"
        "unselected subprocess log and provider response\nAuthorization: Bearer second-secret\n",
        encoding="utf-8",
    )
    result = safe_runtime_details(
        "AssertionError：business_probe.py:271（customer_service_acceptance），请检查本次运行报告",
        tmp_path,
        DiagnosticTextBudget(secrets=("exact-key-canary",)),
    )
    assert "business_probe.py:271" in result["error_excerpt"]
    assert result["native_stage"] == "customer-service-http"
    assert result["native_template"] == "fastapiadmin"
    assert result["native_exception"] == {
        "exception_type": "AssertionError",
        "file": "business_probe.py",
        "function": "customer_service_acceptance",
        "line": 271,
        "message_excerpt": "Native API failed: POST /business/requests/create HTTP 422 [REDACTED]",
    }
    encoded = json.dumps(result)
    for value in ("exact-key-canary", "second-secret", "unselected", "private environment"):
        assert value not in encoded


@pytest.mark.parametrize(
    "stage,headline",
    [
        ("arbitrary model text", "raw provider response\n"),
        (["customer-service-http"], "Authorization: Bearer secret\n"),
        ("customer-service-http", "A" * 65537 + "\n"),
        ("customer-service-http", "AssertionError at /private/path.py:2 (f): secret\n"),
    ],
    # Pytest exports the node ID as PYTEST_CURRENT_TEST; never put the 64-KiB
    # hostile payload there (Windows environment values are limited to 32767).
    ids=["unknown-stage", "non-string-stage", "oversized-headline", "private-path"],
)
def test_runtime_diagnostics_reject_unrecognized_report_values(tmp_path, stage, headline):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    (tmp_path / "progress.json").write_text(json.dumps({"stage": stage}), encoding="utf-8")
    (tmp_path / "failure.log").write_text(headline, encoding="utf-8")
    result = safe_runtime_details("", tmp_path, DiagnosticTextBudget())
    assert "native_exception" not in result
    assert result.get("native_stage") == (
        "customer-service-http" if stage == "customer-service-http" else None
    )


def test_runtime_diagnostics_reject_symlinked_files_and_report_directory(tmp_path, monkeypatch):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "progress.json").write_text('{"stage":"customer-service-http"}', encoding="utf-8")
    (outside / "failure.log").write_text(
        "AssertionError at hidden.py:1 (hidden): private canary\n", encoding="utf-8"
    )
    reports = tmp_path / "reports"
    reports.mkdir()
    linked_directory = tmp_path / "linked"
    linked_paths = {reports / "progress.json", reports / "failure.log", linked_directory}
    try:
        for name in ("progress.json", "failure.log"):
            (reports / name).symlink_to(outside / name)
        linked_directory.symlink_to(outside, target_is_directory=True)
    except OSError:
        # Windows can deny unprivileged symlink creation. Still exercise the
        # same rejection branch instead of silently skipping the safety check.
        original = type(reports).is_symlink
        monkeypatch.setattr(
            type(reports), "is_symlink", lambda path: path in linked_paths or original(path)
        )
    for path in (reports, linked_directory, linked_directory / "nested"):
        assert safe_runtime_details("", path, DiagnosticTextBudget()) == {}


def test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_workflow_details

    class Store:
        def get_run(self, run_id):
            return {
                "status": "FAILED",
                "template": "fastapiadmin",
                "error": "RuntimeError：native_modules.py:23（generate_modules），请检查本次运行报告",
            }

        def latest_revision(self, run_id, stage):
            return {}

    budget = DiagnosticTextBudget(limit=40)
    result = safe_workflow_details(Store(), "run", [], text_budget=budget)
    assert result["terminal_state"] == "FAILED"
    assert result["runtime_diagnostics"]["error_excerpt"].startswith(
        "RuntimeError：native_modules.py"
    )
    assert len(result["runtime_diagnostics"]["error_excerpt"]) == 40
    assert budget.remaining == 0


def test_native_progress_allowlist_covers_real_literal_stages():
    import ast
    import inspect

    from scripts.ci_real_model import NATIVE_PROGRESS_STAGES
    from workbench.native_lab import run_acceptance

    tree = ast.parse(inspect.getsource(run_acceptance))
    stages = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "stage"
    }
    assert stages == NATIVE_PROGRESS_STAGES


def test_native_exception_headline_redaction_precedes_truncation_and_ignores_log(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    secret = "private-exact-credential-canary"
    (tmp_path / "failure.log").write_text(
        "ValueError at native_modules.py:8 (generate_modules): "
        + "x" * 595
        + secret
        + "\nsubprocess private output",
        encoding="utf-8",
    )
    budget = DiagnosticTextBudget(secrets=(secret,))
    result = safe_runtime_details("", tmp_path, budget)
    message = result["native_exception"]["message_excerpt"]
    assert len(message) == 600
    assert "private" not in json.dumps(result)
    assert message.endswith("[REDA")


def test_approved_plan_replay_preserves_exact_normalized_customer_contract(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan
    from workbench.domain import Plan

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    reports = tmp_path / "native-evidence"
    reports.mkdir()
    (reports / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    (reports / "raw-provider-response.json").write_text("unselected secret", encoding="utf-8")
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    budget = DiagnosticTextBudget(secrets=("test-only-secret",), limit=0)
    result = preserve_approved_customer_plan(reports, destination, budget)
    assert result["status"] == "saved" and result["exact_normalized_plan"] is True
    assert result["file"] == destination.name
    assert result["bytes"] == len(destination.read_bytes())
    assert (
        json.loads(destination.read_text(encoding="utf-8"))
        == Plan.model_validate(plan).model_dump()
    )
    assert list(destination.parent.iterdir()) == [destination]
    assert "unselected secret" not in destination.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "secret_text",
    [
        "test-only-secret",
        "password=credential_canary",
        "Authorization: Bearer header_canary",
        "https://alice:credential_canary@example.invalid",
        "API_KEY=credential_canary",
        "sk-credentialcanary12345",
        'metadata {"password": "credential_canary"}',
    ],
)
def test_approved_plan_replay_rejects_credentials_before_persistence(tmp_path, secret_text):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["acceptance"].append(secret_text)
    (tmp_path / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    result = preserve_approved_customer_plan(
        tmp_path, destination, DiagnosticTextBudget(secrets=("test-only-secret",))
    )
    assert result == {"status": "secret_scan_rejected"}
    assert not destination.exists()
    assert secret_text not in json.dumps(result)


def test_approved_plan_replay_rejects_unknown_schema_and_does_not_read_other_files(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    budget = DiagnosticTextBudget()
    (tmp_path / "design.json").write_text('{"secret": "unapproved plan"}', encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, budget) == {
        "status": "unavailable"
    }
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["provider_headers"] = "private provider data"
    (tmp_path / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, budget) == {
        "status": "invalid_schema"
    }
    assert not destination.exists()


def test_approved_plan_replay_size_is_bounded_on_read_and_normalized_write(tmp_path):
    from scripts.ci_real_model import (
        MAX_REPLAY_PLAN_BYTES,
        DiagnosticTextBudget,
        preserve_approved_customer_plan,
    )

    source = tmp_path / "approved-spec.json"
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    source.write_bytes(b" " * (MAX_REPLAY_PLAN_BYTES + 1))
    assert preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == {
        "status": "size_limit"
    }
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["acceptance"] = ["中文" * 1000] * 21
    compact = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    assert len(compact.encode("utf-8")) > MAX_REPLAY_PLAN_BYTES
    source.write_text(compact, encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == {
        "status": "size_limit"
    }
    assert not destination.exists()


def test_approved_plan_replay_rejects_linked_input(tmp_path, monkeypatch):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    real = tmp_path / "actual.json"
    real.write_bytes((ROOT / "examples/plans/customer-service.json").read_bytes())
    reports = tmp_path / "reports"
    reports.mkdir()
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    try:
        (reports / "approved-spec.json").symlink_to(real)
    except OSError:
        original = type(reports).is_symlink
        monkeypatch.setattr(
            type(reports),
            "is_symlink",
            lambda path: path == reports / "approved-spec.json" or original(path),
        )
    assert preserve_approved_customer_plan(reports, destination, DiagnosticTextBudget()) == {
        "status": "unsafe_path"
    }
    assert not destination.exists()


def test_failed_native_harness_preserves_replay_before_private_cleanup(tmp_path, monkeypatch):
    import tempfile
    from pathlib import Path
    from types import SimpleNamespace

    import uvicorn

    from scripts import ci_real_model
    from workbench import api
    from workbench import settings as settings_module
    from workbench.filesystem import write_json

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    public_root = tmp_path / "public"
    public_root.mkdir()
    monkeypatch.setattr(settings_module, "ROOT", public_root)
    monkeypatch.setattr(ci_real_model, "customer_request", lambda: "Synthetic customer request")

    class Store:
        def get_run(self, run_id):
            assert run_id == "test-run"
            return {
                "status": "FAILED",
                "template": "fastapiadmin",
                "error": "AssertionError：business_probe.py:123（customer_service_acceptance）",
            }

        def latest_revision(self, run_id, stage):
            return {"plan": plan} if stage == "design" else {}

    application = SimpleNamespace(state=SimpleNamespace(token="test-auth", store=Store()))
    monkeypatch.setattr(api, "create_app", lambda *args, **kwargs: application)
    monkeypatch.setattr(uvicorn, "Config", lambda *args, **kwargs: None)
    server = SimpleNamespace(started=True, run=lambda: None, should_exit=False)
    monkeypatch.setattr(uvicorn, "Server", lambda *args: server)

    with tempfile.TemporaryDirectory(dir=tmp_path) as private:
        directory = Path(private)

        def failed_browser(command, **kwargs):
            write_json(directory / "browser-result.json", {"run_id": "test-run"})
            reports = directory / "private-platform/runs/test-run/native-evidence"
            write_json(reports / "approved-spec.json", plan)
            write_json(reports / "progress.json", {"stage": "customer-service-http"})
            (reports / "failure.log").write_text(
                "AssertionError at business_probe.py:123 (customer_service_acceptance): "
                "Native API failed: POST /business/tasks/create HTTP 422 test-only-secret\n"
                "raw log must remain private",
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=1)

        monkeypatch.setattr(ci_real_model.subprocess, "run", failed_browser)
        with pytest.raises(SafeFailure, match="workflow_not_ready") as caught:
            ci_real_model.run_acceptance(
                config(), SimpleNamespace(statuses=[200]), directory, "fastapiadmin"
            )
        details = caught.value.details
        assert details["terminal_state"] == "FAILED"
        assert details["runtime_diagnostics"]["native_stage"] == "customer-service-http"
        assert "HTTP 422" in details["runtime_diagnostics"]["native_exception"]["message_excerpt"]
        assert details["approved_plan_replay"]["status"] == "saved"
        assert "test-only-secret" not in json.dumps(details)
        assert "raw log" not in json.dumps(details)
    assert not directory.exists()
    replay = public_root / "reports/real-model/approved-plan-replay.json"
    assert json.loads(replay.read_text(encoding="utf-8"))["business"] == plan["business"]
    assert list(replay.parent.iterdir()) == [replay]


def test_schema_root_validation_reason_is_bounded_redacted_without_input():
    from pydantic import BaseModel, model_validator

    from scripts.ci_real_model import DiagnosticTextBudget, response_receipt

    class Contract(BaseModel):
        value: str

        @model_validator(mode="after")
        def validate_contract(self):
            raise ValueError("Known transition required; exact-private-canary " + "x" * 2000)

    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({"value": "provider-input-never-exported"}),
                        "reasoning_content": "reasoning-never-exported",
                    },
                }
            ]
        }
    ).encode()
    budget = DiagnosticTextBudget(secrets=("exact-private-canary",), limit=800)
    first = response_receipt(200, raw, "plan", Contract, text_budget=budget)
    second = response_receipt(200, raw, "plan", Contract, text_budget=budget)
    assert first["schema_errors"][0]["field_path"] == []
    assert first["schema_errors"][0]["message"].startswith("Value error, Known transition required")
    assert len(first["schema_errors"][0]["message"]) == 600
    assert len(second["schema_errors"][0]["message"]) == 200
    encoded = json.dumps([first, second])
    for forbidden in (
        "exact-private-canary",
        "provider-input-never-exported",
        "reasoning-never-exported",
    ):
        assert forbidden not in encoded
    assert "[REDACTED]" in encoded


@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_customer_employee_task_scope_binds_approved_requirement(scope):
    from copy import deepcopy

    from workbench.domain import Requirement

    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permissions = spec["business"]["permissions"]
    permissions[:] = [p for p in permissions if (p["role"], p["entity"]) != ("employee", "tasks")]
    permissions.append({"role": "employee", "entity": "tasks", "actions": ["read"], "scope": scope})
    approved = Requirement(
        summary="已确认角色合同",
        users=["普通员工"],
        data_scope="shared",
        features=[],
        acceptance=[],
        facts={"business": deepcopy(spec["business"])},
    )
    require_customer_spec(spec, approved_requirement=approved.model_dump())
    permissions[-1]["scope"] = "assigned" if scope == "own" else "own"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec, approved_requirement=approved.model_dump())
    permissions[-1]["scope"] = "all"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("scope", ["own", "assigned"])
@pytest.mark.parametrize(
    "action", ["create", "update", "archive", "add_note", "assign", "transition", "read_metrics"]
)
def test_customer_employee_tasks_remain_read_only_under_each_allowed_scope(scope, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permissions = spec["business"]["permissions"]
    permissions[:] = [p for p in permissions if (p["role"], p["entity"]) != ("employee", "tasks")]
    permissions.append(
        {"role": "employee", "entity": "tasks", "actions": ["read", action], "scope": scope}
    )
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)
