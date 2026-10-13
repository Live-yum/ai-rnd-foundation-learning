"""Offline regressions for billing evidence and persisted connection diagnostics."""

import json
import ssl
import sys
from types import SimpleNamespace

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from scripts import ci_template_projects as acceptance
from scripts import live_test_client as client
from workbench.domain import Requirement
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_diagnostics import failure_diagnostic


@pytest.fixture
def acceptance_main(tmp_path, monkeypatch):
    """Exercise the real CLI authority/billing path without starting a model suite."""
    event = tmp_path / "event.json"
    event.write_text("{}", encoding="utf-8")
    environment = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": acceptance.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_EVENT_PATH": str(event),
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "ACCEPTANCE_HEAD_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "BASE_URL": client.ENDPOINT,
        "LIVE_TEST_CA": "system",
        "LIVE_BILLING_MODE": "declared_free",
        "LIVE_ZERO_BILLING_ACK": "true",
    }
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", ["ci_template_projects"])
    monkeypatch.setattr(acceptance, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(
        acceptance.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout="a" * 40)
    )
    monkeypatch.setattr(acceptance, "acceptance_settings", lambda *args: object())
    calls = []

    def offline_suite(settings, directory, binding, **kwargs):
        calls.append(kwargs)
        return {"passed": False, "real_model": False, "run_identity": binding}

    monkeypatch.setattr(acceptance, "run_suite", offline_suite)

    def invoke():
        with pytest.raises(SystemExit) as caught:
            acceptance.main()
        assert caught.value.code == 1  # The offline substitute never claims live success.
        report = json.loads((acceptance.REPORTS / "summary.json").read_text(encoding="utf-8"))
        assert report["passed"] is False and report["real_model"] is False
        return calls, report

    return invoke


@pytest.mark.parametrize("ca_mode", ["system", "caddy-ip"])
def test_declared_free_billing_reaches_suite_independently_of_ca(
    acceptance_main, monkeypatch, ca_mode
):
    monkeypatch.setenv("LIVE_TEST_CA", ca_mode)
    calls, report = acceptance_main()
    assert len(calls) == 1 and "controller_failure" not in report
    assert calls[0] == {
        "ca_mode": ca_mode,
        "billing": {
            "mode": "declared_free",
            "attestation": client.ATTESTATION,
            "endpoint": client.ENDPOINT,
            "source": "user_declaration_not_provider_invoice",
            "maximum_cost_usd": 0,
        },
    }


@pytest.mark.parametrize("ca_mode", ["system", "caddy-ip"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("LIVE_ZERO_BILLING_ACK", "false"),
        ("LIVE_ZERO_BILLING_ACK", ""),
        ("BASE_URL", "https://other.test/v1"),
    ],
)
def test_declared_free_billing_remains_bound_to_confirmation_and_endpoint(
    acceptance_main, monkeypatch, ca_mode, key, value
):
    monkeypatch.setenv("LIVE_TEST_CA", ca_mode)
    monkeypatch.setenv(key, value)
    calls, report = acceptance_main()
    assert calls == []
    assert report["controller_failure"]["error_type"] == "ValueError"


def test_system_ca_metered_mode_keeps_existing_unspecified_billing(acceptance_main, monkeypatch):
    monkeypatch.setenv("LIVE_BILLING_MODE", "metered")
    monkeypatch.setenv("BASE_URL", "https://other.test/v1")
    monkeypatch.delenv("LIVE_ZERO_BILLING_ACK")
    calls, report = acceptance_main()
    assert calls == [{"ca_mode": "system", "billing": None}]
    assert "controller_failure" not in report


def test_private_ca_still_requires_explicit_declared_free_mode(acceptance_main, monkeypatch):
    monkeypatch.setenv("LIVE_TEST_CA", "caddy-ip")
    monkeypatch.setenv("LIVE_BILLING_MODE", "metered")
    calls, report = acceptance_main()
    assert calls == []
    assert report["controller_failure"]["error_type"] == "ValueError"


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    "kind,code,hint",
    [
        ("proxy", "proxy_connection_failed", "代理访问策略"),
        ("certificate", "tls_certificate_verification_failed", "不能关闭校验"),
        ("proxy_certificate", "tls_certificate_verification_failed", "不能关闭校验"),
    ],
)
def test_gateway_persists_provider_phase_and_safe_connection_guidance(
    store, kind, code, hint, streaming
):
    calls = []
    secret = "private-provider-error-canary"
    store.settings.base_url = "https://example.test/v1"
    store.settings.model = "test-model"
    store.settings.api_key = SecretStr(secret)

    def handler(request):
        calls.append(request)
        if kind == "proxy":
            raise httpx.ProxyError("403 " + secret, request=request)
        try:
            raise ssl.SSLCertVerificationError(1, secret)
        except ssl.SSLCertVerificationError as cause:
            if kind == "proxy_certificate":
                raise httpx.ProxyError(secret, request=request) from cause
            raise httpx.ConnectError(secret, request=request) from cause

    gateway = ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=streaming)
    run = new_run(store)
    with pytest.raises(ModelFailure) as caught:
        gateway.complete(run, "requirement:1", "offline test", {}, Requirement)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    failures = [
        event
        for event in store.events(run)
        if event["kind"] in {"model_failure", "assistant_failed"}
    ]
    assert len(failures) == (2 if streaming else 1)
    for event in failures:
        diagnostic = event["data"]["diagnostic"]
        assert diagnostic["code"] == code
        assert diagnostic["phase"] == "provider_request"
        assert hint in diagnostic["retry_hint"]
        assert "Schema" not in diagnostic["retry_hint"]
    assert secret not in str(caught.value) + json.dumps(failures)


@pytest.mark.parametrize(
    "code,phase",
    [
        ("transport_error", "provider_request"),
        ("http_401", "provider_request"),
        ("http_429", "provider_request"),
        ("invalid_json", "response_validation"),
        ("native_schema_violation", "response_validation"),
    ],
)
def test_existing_failure_phases_are_unchanged(code, phase):
    assert failure_diagnostic(code, trace_id="offline-trace")["phase"] == phase
