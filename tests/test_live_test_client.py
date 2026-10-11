"""Offline trust scope, no-charge attestation and bounded client contracts."""

import ssl

import httpx
import pytest

from scripts import ci_live_modules as live
from scripts import live_test_client as client


def env():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": live.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "LIVE_SCENARIO": "mini-swe-sla",
        "BASE_URL": client.ENDPOINT,
        "MODE": "offline",
        "LIVE_TEST_CA": "caddy-ip",
        "LIVE_BILLING_MODE": "declared_free",
        "LIVE_ZERO_BILLING_ACK": "true",
        "LIVE_MAX_COST_USD": "0",
        "LIVE_USD_PER_MILLION_TOKENS": "0",
    }


def test_public_pinned_ca_keeps_hostname_and_certificate_verification():
    context = client.test_context(client.ENDPOINT, "caddy-ip")
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    assert "PRIVATE KEY" not in client.CA.read_text()


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://170.106.181.109:8317/v1",
        "https://170.106.181.109/v1",
        "https://example.test:8317/v1",
        client.ENDPOINT + "?other",
        client.ENDPOINT + "/models",
    ],
)
def test_private_ca_never_applies_to_other_destinations(endpoint):
    with pytest.raises(ValueError, match="endpoint"):
        client.test_context(endpoint, "caddy-ip")


def test_tampered_certificate_is_rejected_before_trust(tmp_path, monkeypatch):
    path = tmp_path / "ca.pem"
    path.write_text(client.CA.read_text().replace("MI", "MJ", 1))
    monkeypatch.setattr(client, "CA", path)
    with pytest.raises(ValueError, match="fingerprint"):
        client.test_context(client.ENDPOINT, "caddy-ip")


def test_free_mode_is_explicit_zero_and_still_bounded():
    config = live.configuration(env())
    assert config["max_cost_usd"] == config["usd_per_million_tokens"] == 0
    assert config["billing"]["attestation"] == client.ATTESTATION
    assert config["max_model_calls"] == 32 and config["max_output_tokens"] == 8192
    assert config["max_tokens_total"] == 4_000_000


@pytest.mark.parametrize(
    "key,value",
    [
        ("LIVE_ZERO_BILLING_ACK", "false"),
        ("LIVE_BILLING_MODE", "metered"),
        ("LIVE_BILLING_MODE", "unknown"),
        ("BASE_URL", "https://other.test/v1"),
        ("LIVE_MAX_COST_USD", "10"),
        ("LIVE_USD_PER_MILLION_TOKENS", "1"),
    ],
)
def test_free_mode_cannot_silently_replace_paid_budget(key, value):
    with pytest.raises(ValueError):
        live.configuration({**env(), key: value})


@pytest.mark.parametrize("status,success", [(200, True), (401, True), (403, False), (302, False)])
def test_probe_is_strict_unauthenticated_and_does_not_follow_redirects(
    monkeypatch, status, success
):
    requests = []

    def factory(**kwargs):
        assert kwargs["verify"].check_hostname
        assert kwargs["verify"].verify_mode == ssl.CERT_REQUIRED

        def handle(request):
            requests.append(request)
            assert "authorization" not in request.headers
            return httpx.Response(status, headers={"location": "https://other.test/v1"})

        return httpx.MockTransport(handle)

    monkeypatch.setattr(client.httpx, "HTTPTransport", factory)
    if success:
        assert client.probe({**env(), "API_KEY": "never-send-this"})["strict_tls"]
    else:
        with pytest.raises(ValueError):
            client.probe(env())
    assert len(requests) == 1


def test_scoped_transport_refuses_cross_host_and_authenticated_probe():
    transport = client.TestServiceTransport(client.ENDPOINT, "caddy-ip")
    try:
        for request in [
            httpx.Request("POST", "https://other.test/v1/chat/completions"),
            httpx.Request(
                "GET", client.ENDPOINT + "/models", headers={"Authorization": "not-real"}
            ),
        ]:
            with pytest.raises(ValueError, match="destination"):
                transport.handle_request(request)
        assert transport.calls == 0
    finally:
        transport.close()


@pytest.mark.parametrize(
    "ack,endpoint,cost,price,accepted",
    [
        (True, client.ENDPOINT, 0, 0, True),
        (False, client.ENDPOINT, 0, 0, False),
        (True, "https://other.test/v1", 0, 0, False),
        (True, client.ENDPOINT, 1, 0, False),
    ],
)
def test_platform_free_mode_needs_attested_exact_endpoint(
    settings, tmp_path, monkeypatch, ack, endpoint, cost, price, accepted
):
    from scripts.sla_fixture import design
    from workbench.coding import mini_swe
    from workbench.errors import UnsupportedScope
    from workbench.llm import ModelGateway

    settings = settings.model_copy(
        update={
            "mini_swe_enabled": True,
            "base_url": client.ENDPOINT,
            "model": "offline",
            "max_output_tokens": 8192,
            "mini_swe_billing_mode": "declared_free",
            "mini_swe_zero_billing_ack": ack,
            "mini_swe_zero_billing_endpoint": endpoint,
            "mini_swe_max_cost_usd": cost,
            "mini_swe_usd_per_million_tokens": price,
        }
    )
    monkeypatch.setattr(mini_swe, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(mini_swe, "_run", lambda *args: "offline-authority-checked")
    plan = design().implementation

    def invoke():
        return mini_swe.run_agent(
            settings,
            ModelGateway(settings, None),
            "offline",
            plan.tasks[0],
            plan,
            tmp_path,
            tmp_path / "worker",
            {},
        )

    if accepted:
        assert invoke() == "offline-authority-checked"
    else:
        with pytest.raises(UnsupportedScope):
            invoke()
