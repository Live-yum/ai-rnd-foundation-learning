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
    require_news_spec,
    smoke,
    trusted_dispatch,
)
from scripts.news_fixture import news_spec
from workbench.domain import Plan
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
    assert receipt == {"passed": True, "http_status": 200, "actual_provider_request": True}


@pytest.mark.parametrize("body", [{}, {"choices": []}, {"choices": [{"message": {"content": ""}}]}])
def test_invalid_smoke_response_fails_closed(body):
    with pytest.raises(SafeFailure, match="invalid_smoke_response"):
        smoke(config(), httpx.MockTransport(lambda request: httpx.Response(200, json=body)))


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
        assert json.loads(requests[0].content)["max_tokens"] == 4096
        with pytest.raises(SafeFailure, match="model_substitution"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": "fallback"})
            )
        with pytest.raises(SafeFailure, match="request_scope"):
            transport.handle_request(
                httpx.Request(
                    "POST", "https://evil.example/chat/completions", json={"model": MODEL}
                )
            )
        transport.calls = 17
        with pytest.raises(SafeFailure, match="request_scope_or_budget"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": MODEL})
            )
    finally:
        transport.shutdown()


@pytest.mark.parametrize("mutation", ["search", "length", "isolation", "date", "category"])
def test_actual_model_plan_must_preserve_explicit_news_obligations(mutation):
    spec = Plan.model_validate(news_spec()).model_dump()
    require_news_spec(spec)
    if mutation == "isolation":
        spec["data_scope"] = "shared"
    elif mutation == "search":
        spec["entities"][0]["fields"][0]["searchable"] = False
    elif mutation == "length":
        spec["entities"][0]["fields"][1]["max_length"] = 200
    elif mutation == "date":
        spec["entities"][0]["fields"][2]["date_range"] = False
    else:
        spec["entities"][0]["fields"][3]["required"] = True
    with pytest.raises(SafeFailure, match="obligation"):
        require_news_spec(spec)


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
    assert [step["with"]["path"] for step in uploads] == ["reports/real-model/summary.json"]
    entry = yaml.load(
        (ROOT / ".github/workflows/native-probe.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert set(entry["jobs"]) == {"verify-bundles"}
    assert all(job.get("environment") != "rnd" for job in entry["jobs"].values())
    assert "push" not in entry["on"]


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
    for forbidden in ("test-only-secret", "private reasoning", "injected-private-field"):
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
