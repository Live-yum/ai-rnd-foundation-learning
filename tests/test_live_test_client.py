"""Offline trust scope, no-charge attestation and bounded client contracts."""

import json
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


def labeled_env(tmp_path, *, mutation=None):
    head = "b" * 40
    event = {
        "action": "labeled",
        "label": {"name": "run-live-acceptance"},
        "pull_request": {
            "head": {"sha": head, "repo": {"full_name": live.REPOSITORY}},
            "base": {"repo": {"full_name": live.REPOSITORY}},
        },
    }
    values = {
        **env(),
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_SHA": "c" * 40,  # GitHub's merge ref differs from the checked-out PR head.
        "ACCEPTANCE_HEAD_SHA": head,
        "REVIEWED_SHA": head,
        "LIVE_TEST_CA": "system",
        "LIVE_BILLING_MODE": "metered",
        "LIVE_ZERO_BILLING_ACK": "false",
    }
    if mutation:
        mutation(values, event)
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event))
    values["GITHUB_EVENT_PATH"] = str(path)
    return values


def test_label_probe_binds_reviewed_same_repository_head_without_credentials(tmp_path, monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        assert request.method == "GET" and "authorization" not in request.headers
        return httpx.Response(401)

    def transport(**kwargs):
        assert kwargs["verify"].check_hostname
        assert kwargs["verify"].verify_mode == ssl.CERT_REQUIRED
        assert kwargs["retries"] == 0 and kwargs["trust_env"] is False
        return httpx.MockTransport(handle)

    monkeypatch.setattr(client.httpx, "HTTPTransport", transport)
    result = client.probe({**labeled_env(tmp_path), "API_KEY": "must-not-be-sent"})
    assert result["head_sha"] == "b" * 40
    assert result["authentication_sent"] is False and result["ca_mode"] == "system"
    assert len(requests) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        lambda e, p: e.update(GITHUB_EVENT_NAME="pull_request_target"),
        lambda e, p: e.update(GITHUB_RUN_ATTEMPT="2"),
        lambda e, p: e.update(GITHUB_REPOSITORY="untrusted/repo"),
        lambda e, p: e.update(ACCEPTANCE_HEAD_SHA="not-a-sha"),
        lambda e, p: e.update(REVIEWED_SHA="a" * 40),
        lambda e, p: p.update(action="synchronize"),
        lambda e, p: p["label"].update(name="unrelated"),
        lambda e, p: p["pull_request"]["head"]["repo"].update(full_name="fork/repo"),
        lambda e, p: p["pull_request"]["base"]["repo"].update(full_name="other/repo"),
        lambda e, p: p["pull_request"]["head"].update(sha="a" * 40),
        lambda e, p: p.update(pull_request={}),
    ],
)
def test_label_probe_rejects_unreviewed_event_before_network(tmp_path, monkeypatch, mutation):
    monkeypatch.setattr(
        client.httpx,
        "HTTPTransport",
        lambda **kwargs: pytest.fail("unreviewed event reached the network"),
    )
    with pytest.raises(ValueError):
        client.probe(labeled_env(tmp_path, mutation=mutation))


def test_label_workflow_defaults_do_not_grant_no_charge_or_custom_ca():
    import yaml

    workflow = yaml.safe_load(
        (live.ROOT / ".github/workflows/template-project-acceptance.yml").read_text()
    )
    job = workflow["jobs"]["all-three-projects"]
    assert "github.run_attempt == 1" in job["if"]
    assert "github.event_name == 'pull_request'" in job["if"]
    assert job["environment"] == "rnd"
    assert "github.event.pull_request.head.sha" in job["env"]["REVIEWED_SHA"]
    assert job["env"]["LIVE_BILLING_MODE"] == "${{ inputs.billing_mode || 'metered' }}"
    assert job["env"]["LIVE_TEST_CA"] == "${{ inputs.test_ca || 'system' }}"
    assert job["env"]["LIVE_ZERO_BILLING_ACK"] == "${{ inputs.confirm_no_charge || false }}"
    assert job["steps"][0]["with"]["persist-credentials"] is False
    assert "API_KEY" not in job["env"]


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
    monkeypatch.setattr(mini_swe, "_run", lambda *args: ("offline-authority-checked", {}))
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


@pytest.mark.parametrize("failure", [None, "headers", "body"])
def test_transport_timings_preserve_response_and_timeout_semantics(monkeypatch, failure):
    import json

    from workbench.coding.timing import http_trace_receipt, timing_receipts

    clock = [10.0]
    monkeypatch.setattr(
        client, "time", type("Clock", (), {"monotonic": staticmethod(lambda: clock[0])})
    )
    closed = []

    class Body(httpx.SyncByteStream):
        def __iter__(self):
            clock[0] += 2
            yield b"private-model-text"
            clock[0] += 3
            if failure == "body":
                raise httpx.ReadTimeout("private-server-detail")
            yield b"done"

        def close(self):
            closed.append(True)

    def request(req):
        assert req.extensions["timeout"]["read"] == 7
        clock[0] += 4
        if failure == "headers":
            raise httpx.ReadTimeout("private-server-detail")
        return httpx.Response(200, stream=Body())

    monkeypatch.setattr(client.httpx, "HTTPTransport", lambda **kw: httpx.MockTransport(request))
    transport = client.TestServiceTransport(client.ENDPOINT)
    with httpx.Client(transport=transport, timeout=7, trust_env=False) as http:
        if failure:
            with pytest.raises(httpx.ReadTimeout):
                http.post(client.ENDPOINT + "/chat/completions", content=b"private-request")
        else:
            assert (
                http.post(client.ENDPOINT + "/chat/completions", content=b"private-request").content
                == b"private-model-textdone"
            )
    assert transport.calls == 1 and transport.responses == (0 if failure == "headers" else 1)
    data = timing_receipts(transport.timings, attempts=True)
    assert data == [
        {
            "attempt": 1,
            "request_body_bytes": 15,
            "read_timeout_seconds": 7,
            "headers_seconds": None if failure == "headers" else 4,
            "elapsed_seconds": 4 if failure == "headers" else 9,
            "response_bytes": 0 if failure == "headers" else 18 if failure == "body" else 22,
            "http_trace": http_trace_receipt({"event_count": 0}),
        }
    ]
    assert bool(closed) is (failure != "headers")
    assert "private" not in json.dumps(data)


def test_timing_projection_rejects_non_numeric_data_and_limits_inventory():
    import json

    from workbench.coding.timing import ATTEMPT_FIELDS, TURN_FIELDS, timing_receipts

    for attempts, fields, limit in ((False, TURN_FIELDS, 8), (True, ATTEMPT_FIELDS, 32)):
        for poison in ("private-text", True, -1, float("nan"), float("inf"), 10**1000, {}, []):
            values = [{**dict.fromkeys(fields, poison), "raw": "private-key"}] * 40
            result = timing_receipts(values, attempts=attempts)
            assert len(result) == limit
            assert all(value is None for row in result for value in row.values())
            assert "private" not in json.dumps(result)
