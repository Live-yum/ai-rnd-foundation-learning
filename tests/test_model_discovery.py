"""Offline catalog lookup: no inference, real credentials or provider requests."""

import json
import logging
import ssl

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from workbench.model_discovery import (
    MAX_DISCOVERY_BYTES,
    MAX_DISCOVERY_MODELS,
    MAX_MODEL_ID_LENGTH,
    DiscoveryInputError,
    ModelDiscoverer,
    ModelDiscoveryRequest,
)
from workbench.model_settings import (
    MAX_CONFIG_BYTES,
    ModelSettingsRepository,
    RevisionConflict,
    register_model_settings_routes,
)
from workbench.settings import STAGES

SECRET = "dummy-catalog-saved-key-never-real"
DRAFT_SECRET = "dummy-catalog-draft-key-never-real"


def command(revision="0", stage="default", **extra):
    return ModelDiscoveryRequest(expected_revision=revision, stage=stage, **extra)


def catalog(*models):
    return httpx.Response(
        200,
        json={
            "object": "list",
            "data": [{"id": model, "owned_by": SECRET} for model in models],
            "private_metadata": SECRET,
        },
    )


@pytest.fixture
def configured(settings):
    repository = ModelSettingsRepository(settings)
    saved = repository.update(
        {
            "expected_revision": "0",
            "default": {
                "base_url": "https://provider.example/v1",
                "model": "",
                "api_key": SECRET,
            },
        }
    )
    return repository, saved


@pytest.mark.parametrize("stage", ("default", *STAGES))
def test_catalog_reads_saved_or_inherited_endpoint_without_model_or_inference(
    settings, configured, stage, caplog
):
    repository, saved = configured
    original = repository.path.read_bytes()
    calls = []

    def handle(request):
        calls.append(request)
        return catalog("z-model", "a/model:v1", "z-model")

    result = ModelDiscoverer(settings, httpx.MockTransport(handle)).discover(
        command(saved["revision"], stage)
    )
    assert result["ok"] and result["models"] == ["z-model", "a/model:v1"]
    assert result["scope"] == "model_discovery" and result["code"] == "models_discovered"
    assert result["stage"] == stage and result["revision"] == saved["revision"]
    assert len(calls) == result["attempts"] == 1
    assert calls[0].method == "GET" and calls[0].content == b""
    assert str(calls[0].url) == "https://provider.example/v1/models"
    assert calls[0].headers["authorization"] == "Bearer " + SECRET
    assert calls[0].headers["accept-encoding"] == "identity"
    assert "endpoint" not in result and "private_metadata" not in result
    assert SECRET not in json.dumps(result) + caplog.text
    assert repository.path.read_bytes() == original
    assert not (settings.data_dir / "workbench.db").exists()


@pytest.mark.parametrize("stage", ("default", *STAGES))
def test_draft_can_discover_before_first_save_without_a_model(settings, stage):
    calls = []
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request) or catalog("new-model"))
    ).discover(
        command(
            stage=stage,
            profile={
                "base_url": "https://draft.example/custom/v1/",
                "api_key": DRAFT_SECRET,
                "model": "",
            },
        )
    )
    assert result["ok"] and result["models"] == ["new-model"]
    assert result["revision"] == "0"
    assert str(calls[0].url) == "https://draft.example/custom/v1/models"
    assert calls[0].headers["authorization"] == "Bearer " + DRAFT_SECRET
    assert not settings.data_dir.exists()
    assert DRAFT_SECRET not in settings.redaction_secrets()
    assert DRAFT_SECRET not in repr(command(profile={"api_key": DRAFT_SECRET}))


def test_saved_snapshot_survives_updates_during_catalog_fetch(settings, configured):
    repository, saved = configured

    def handle(request):
        repository.update(
            {
                "expected_revision": saved["revision"],
                "default": {"api_key": DRAFT_SECRET},
            }
        )
        assert request.headers["authorization"] == "Bearer " + SECRET
        return catalog("old-snapshot-model")

    result = ModelDiscoverer(settings, httpx.MockTransport(handle)).discover(
        command(saved["revision"])
    )
    assert result["ok"] and result["revision"] == saved["revision"]
    assert repository.public()["revision"] != result["revision"]


@pytest.mark.parametrize("stage", ("default", "coding"))
@pytest.mark.parametrize("key", (None, "", SECRET))
@pytest.mark.parametrize("endpoint", ("https://other.example/v1", "https://provider.example/v2"))
def test_new_destination_never_reuses_saved_key(settings, configured, stage, key, endpoint):
    repository, saved = configured
    original = repository.path.read_bytes()
    calls = []
    profile = {"base_url": endpoint}
    if key is not None:
        profile["api_key"] = key
    discoverer = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request))
    )
    with pytest.raises(DiscoveryInputError, match="API Key"):
        discoverer.discover(command(saved["revision"], stage, profile=profile))
    assert not calls and repository.path.read_bytes() == original


def test_cannot_borrow_another_stages_key_for_a_new_endpoint(settings, configured):
    repository, saved = configured
    saved = repository.update(
        {
            "expected_revision": saved["revision"],
            "stages": {"coding": {"base_url": "https://coder.example", "api_key": DRAFT_SECRET}},
        }
    )
    with pytest.raises(DiscoveryInputError, match="API Key"):
        ModelDiscoverer(settings).discover(
            command(
                saved["revision"],
                "planning",
                profile={"base_url": "https://other.example", "api_key": DRAFT_SECRET},
            )
        )


def test_explicit_new_draft_key_is_used_without_saving(settings, configured):
    repository, saved = configured
    original = repository.path.read_bytes()
    calls = []
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request) or catalog("draft"))
    ).discover(
        command(
            saved["revision"],
            profile={"base_url": "https://new.example/v1", "api_key": DRAFT_SECRET},
        )
    )
    assert result["ok"] and calls[0].headers["authorization"] == "Bearer " + DRAFT_SECRET
    assert repository.path.read_bytes() == original


def test_stale_revision_rejected_before_draft_validation_or_network(settings, configured):
    calls = []
    with pytest.raises(RevisionConflict):
        ModelDiscoverer(
            settings, httpx.MockTransport(lambda request: calls.append(request))
        ).discover(command("stale", profile={"base_url": "https://other.example/v1"}))
    assert not calls


@pytest.mark.parametrize(
    "profile",
    [
        {"base_url": "http://remote.example/v1", "api_key": DRAFT_SECRET},
        {"base_url": "https://user:password@example.com/v1", "api_key": DRAFT_SECRET},
        {"base_url": "https://example.com/v1?secret=" + DRAFT_SECRET, "api_key": DRAFT_SECRET},
        {"base_url": "https://example.com/v1#fragment", "api_key": DRAFT_SECRET},
        {"base_url": "https://example.com/v1/chat/completions", "api_key": DRAFT_SECRET},
        {"base_url": "https://example.com/%72esponses", "api_key": DRAFT_SECRET},
        {"base_url": "https://example.com/v1", "api_key": "bad\nkey"},
        {"base_url": "https://example.com/v1", "api_key": "configured"},
        {
            "base_url": "https://example.com/v1",
            "api_key": DRAFT_SECRET,
            "allow_insecure_http": True,
        },
        {"base_url": "https://example.com/v1", "api_key": DRAFT_SECRET, "verify": False},
        {"model": 12},
        {"api_key": 12},
    ],
)
def test_invalid_drafts_cannot_weaken_endpoint_or_key_validation(settings, profile):
    calls = []
    with pytest.raises(DiscoveryInputError):
        ModelDiscoverer(
            settings, httpx.MockTransport(lambda request: calls.append(request))
        ).discover(command(profile=profile))
    assert not calls and not settings.data_dir.exists()


@pytest.mark.parametrize("host", ("127.0.0.1", "localhost", "[::1]"))
def test_existing_loopback_http_support_is_preserved(settings, host):
    calls = []
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(lambda request: calls.append(request) or catalog("local-model")),
    ).discover(command(profile={"base_url": f"http://{host}:11434/v1", "api_key": DRAFT_SECRET}))
    assert result["ok"] and str(calls[0].url) == f"http://{host}:11434/v1/models"


def test_explicit_operator_insecure_http_policy_is_preserved(settings):
    settings.allow_insecure_model_http = True
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: catalog("local"))
    ).discover(
        command(profile={"base_url": "http://lan.example:11434/v1", "api_key": DRAFT_SECRET})
    )
    assert result["ok"]


def test_transport_keeps_tls_verification_no_proxy_no_redirects(settings, configured, monkeypatch):
    _, saved = configured
    real_client, options = httpx.Client, []

    def client(**kwargs):
        options.append(kwargs.copy())
        return real_client(**kwargs)

    monkeypatch.setattr("workbench.model_discovery.httpx.Client", client)
    monkeypatch.setenv("HTTPS_PROXY", "http://unapproved.example:8080")
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: catalog("model"))
    ).discover(command(saved["revision"]))
    assert result["ok"] and len(options) == 1
    assert options[0]["verify"] is True
    assert options[0]["trust_env"] is False and options[0]["follow_redirects"] is False
    assert options[0]["timeout"] <= 20


def test_untrusted_protocol_fields_cannot_echo_secrets_in_httpx_logs(settings, configured, caplog):
    caplog.set_level(logging.INFO, logger="httpx")
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"data": [{"id": "safe"}]},
                extensions={"reason_phrase": SECRET.encode(), "http_version": SECRET.encode()},
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["ok"] and SECRET not in caplog.text + json.dumps(result)


def test_default_transport_explicitly_disables_retries_and_keeps_tls(
    settings, configured, monkeypatch
):
    options = []

    def transport(**kwargs):
        options.append(kwargs)
        return httpx.MockTransport(lambda request: catalog("model"))

    monkeypatch.setattr("workbench.model_discovery.httpx.HTTPTransport", transport)
    result = ModelDiscoverer(settings).discover(command(configured[1]["revision"]))
    assert result["ok"] and options == [{"verify": True, "trust_env": False, "retries": 0}]


@pytest.mark.parametrize(
    "status,code",
    [
        (301, "http_error"),
        (302, "http_error"),
        (307, "http_error"),
        (401, "authentication_failed"),
        (403, "permission_denied"),
        (404, "discovery_unsupported"),
        (405, "discovery_unsupported"),
        (429, "rate_limited"),
        (500, "http_error"),
    ],
)
def test_upstream_error_body_never_exposed_redirected_or_retried(
    settings, configured, status, code, caplog
):
    calls = []
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: (
                calls.append(request)
                or httpx.Response(
                    status,
                    headers={"location": "https://unapproved.example", "x-secret": SECRET},
                    json={"error": {"message": SECRET}},
                )
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert not result["ok"] and result["code"] == code
    assert result["http_status"] == status and result["models"] == []
    assert len(calls) == result["attempts"] == 1
    assert SECRET not in json.dumps(result) + caplog.text


@pytest.mark.parametrize(
    "payload",
    [
        [],
        None,
        {},
        {"data": {}},
        {"data": ["model"]},
        {"data": [{}]},
        {"data": [{"id": 10}]},
        {"data": [{"id": ""}]},
        {"data": [{"id": " padded "}]},
        {"data": [{"id": "model\nname"}]},
        {"data": [{"id": "model\u202ename"}]},
        {"data": [{"id": "\ud800"}]},
        {"data": [{"id": "a" * (MAX_MODEL_ID_LENGTH + 1)}]},
        {"data": [{"id": "echo-" + SECRET}]},
        {"data": [{"id": "echo-" + DRAFT_SECRET}]},
    ],
)
def test_malformed_or_secret_echoed_ids_are_not_offered(settings, configured, payload, caplog):
    # json.dumps safely encodes intentionally malformed surrogate strings.
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=json.dumps(payload))
    )
    result = ModelDiscoverer(settings, transport).discover(
        command(configured[1]["revision"], profile={"api_key": DRAFT_SECRET})
    )
    assert not result["ok"] and result["code"] == "invalid_response" and result["models"] == []
    assert SECRET not in json.dumps(result) + caplog.text
    assert DRAFT_SECRET not in json.dumps(result) + caplog.text


@pytest.mark.parametrize("content", (b"not JSON", b"\xff", b"[" * 2000 + b"]" * 2000))
def test_invalid_json_is_a_fixed_error(settings, configured, content):
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: httpx.Response(200, content=content))
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "invalid_response"


class Chunks(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks, self.count, self.closed = chunks, 0, False

    def __iter__(self):
        for chunk in self.chunks:
            self.count += 1
            yield chunk

    def close(self):
        self.closed = True


@pytest.mark.parametrize("advertised", (True, False))
def test_response_bytes_bounded_before_parsing(settings, configured, advertised):
    stream = Chunks([b"x" * (MAX_DISCOVERY_BYTES + 1), b"unread"])
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                headers={"content-length": str(MAX_DISCOVERY_BYTES + 1)} if advertised else {},
                stream=stream,
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "response_too_large"
    assert stream.count == (0 if advertised else 1) and stream.closed


def test_model_count_bounded_before_returning_any_ids(settings, configured):
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: catalog(
                *("m" + str(index) for index in range(MAX_DISCOVERY_MODELS + 1))
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "response_too_large" and result["models"] == []


def test_compression_rejected_without_reading_or_expanding_body(settings, configured):
    stream = Chunks([b"not-read"])
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                headers={"content-encoding": "gzip"},
                stream=stream,
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "invalid_response" and stream.count == 0 and stream.closed


@pytest.mark.parametrize("length", ("-1", "not-a-number", "9" * 5000))
def test_malformed_content_length_is_rejected_without_body_read(settings, configured, length):
    stream = Chunks([b"not-read"])
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                headers={"content-length": length},
                stream=stream,
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "invalid_response" and stream.count == 0 and stream.closed


def test_model_id_and_count_at_limits_are_accepted(settings, configured):
    models = [str(index).zfill(MAX_MODEL_ID_LENGTH) for index in range(MAX_DISCOVERY_MODELS)]
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: catalog(*models))
    ).discover(command(configured[1]["revision"]))
    assert result["ok"] and result["models"] == models


def test_discovery_total_read_deadline_stops_a_slow_stream(settings, configured, monkeypatch):
    times = iter((0, 21))
    monkeypatch.setattr("workbench.model_discovery.time.monotonic", lambda: next(times))
    stream = Chunks([b'{"data":', b"[]}"])
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                stream=stream,
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "timeout" and stream.count == 1 and stream.closed


def test_error_status_body_is_never_read(settings, configured):
    stream = Chunks([SECRET.encode()])
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(
                401,
                stream=stream,
            )
        ),
    ).discover(command(configured[1]["revision"]))
    assert result["code"] == "authentication_failed" and stream.count == 0 and stream.closed


def test_empty_catalog_succeeds_without_implying_model_compatibility(settings, configured):
    result = ModelDiscoverer(settings, httpx.MockTransport(lambda request: catalog())).discover(
        command(configured[1]["revision"])
    )
    assert result["ok"] and result["models"] == [] and "手动填写" in result["message"]


@pytest.mark.parametrize(
    "kind,code",
    [
        ("timeout", "timeout"),
        ("connection", "connection_failed"),
        ("proxy", "proxy_connection_failed"),
        ("tls", "tls_certificate_verification_failed"),
        ("unexpected", "internal_error"),
    ],
)
def test_transport_errors_are_typed_fixed_and_never_retried(
    settings, configured, kind, code, caplog
):
    calls = []

    def handle(request):
        calls.append(request)
        if kind == "tls":
            try:
                raise ssl.SSLCertVerificationError(1, SECRET)
            except ssl.SSLCertVerificationError as cause:
                raise httpx.ConnectError(SECRET) from cause
        raise {
            "timeout": httpx.ReadTimeout,
            "connection": httpx.ConnectError,
            "proxy": httpx.ProxyError,
            "unexpected": RuntimeError,
        }[kind](SECRET)

    result = ModelDiscoverer(settings, httpx.MockTransport(handle)).discover(
        command(configured[1]["revision"])
    )
    assert result["code"] == code and len(calls) == 1
    assert SECRET not in json.dumps(result) + caplog.text


def test_missing_configuration_does_not_request_anything(settings):
    calls = []
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request))
    ).discover(command())
    assert result["code"] == "invalid_configuration" and result["attempts"] == 0 and not calls


def test_discovery_route_auth_origin_revision_body_validation_and_no_store(
    settings, configured, monkeypatch
):
    calls = []
    discoverer = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request) or catalog("m1"))
    )
    monkeypatch.setattr("workbench.model_discovery.ModelDiscoverer", lambda settings: discoverer)
    app = FastAPI()

    def auth(request: Request):
        if request.headers.get("authorization") != "Bearer local-test-token":
            raise HTTPException(401)

    register_model_settings_routes(app, settings, auth)
    body = command(configured[1]["revision"]).model_dump()
    path = "/settings/models/discover"
    with TestClient(app) as client:
        assert client.post(path, json=body).status_code == 401
        client.headers["authorization"] = "Bearer local-test-token"
        for headers in ({"origin": "https://evil.example"}, {"sec-fetch-site": "cross-site"}):
            assert client.post(path, json=body, headers=headers).status_code == 403
        for invalid in (
            {**body, "expected_revision": ""},
            {**body, "stage": SECRET},
            {**body, "profile": {"api_key": SECRET, "unknown": SECRET}},
            {**body, "api_key": SECRET},
            {**body, "profile": [SECRET]},
            {**body, "profile": {"base_url": "https://new.example/v1"}},
        ):
            response = client.post(path, json=invalid)
            assert response.status_code == 422 and SECRET not in response.text
        assert client.post(path, json={**body, "expected_revision": "stale"}).status_code == 409
        assert (
            client.post(path, content="{}", headers={"content-type": "text/plain"}).status_code
            == 415
        )
        assert (
            client.post(
                path, content="broken", headers={"content-type": "application/json"}
            ).status_code
            == 422
        )
        assert (
            client.post(
                path,
                content="x" * (MAX_CONFIG_BYTES + 1),
                headers={"content-type": "application/json"},
            ).status_code
            == 413
        )
        assert not calls
        response = client.post(path, json=body, headers={"origin": "http://testserver"})
        assert response.status_code == 200 and response.json()["models"] == ["m1"]
        assert response.headers["cache-control"] == "no-store"
        assert len(calls) == 1 and SECRET not in response.text


@pytest.mark.parametrize("draft", (False, True))
@pytest.mark.parametrize("malformed", (False, True))
def test_real_protocol_stack_does_not_log_provider_secrets(
    settings, configured, caplog, draft, malformed
):
    """Exercise httpcore itself; MockTransport skips its pre-response debug logs."""
    import httpcore
    from httpcore._backends.mock import MockBackend

    caplog.set_level(logging.DEBUG, logger="httpcore")
    secret = DRAFT_SECRET if draft else SECRET
    raw = (
        b"HTTP/1.1 invalid-" + secret.encode() + b"\r\n\r\n"
        if malformed
        else b"HTTP/1.1 200 "
        + secret.encode()
        + b"\r\nX-Provider-Echo: "
        + secret.encode()
        + b'\r\nContent-Length: 11\r\n\r\n{"data":[]}'
    )
    transport = httpx.HTTPTransport(verify=True, trust_env=False, retries=0)
    transport._pool = httpcore.ConnectionPool(network_backend=MockBackend([raw]))
    result = ModelDiscoverer(settings, transport).discover(
        command(configured[1]["revision"], **({"profile": {"api_key": secret}} if draft else {}))
    )
    assert result["ok"] is not malformed
    assert secret not in caplog.text + json.dumps(result)
    assert "receive_response_headers." in caplog.text


def test_catalog_trace_is_request_local_and_preserves_unrelated_debug_logs(
    settings, configured, caplog
):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    import httpcore
    from httpcore._backends.mock import MockBackend

    caplog.set_level(logging.DEBUG, logger="httpcore")
    barrier = Barrier(2)

    class SynchronizedBackend(MockBackend):
        def connect_tcp(self, *args, **kwargs):
            barrier.wait(timeout=5)
            return super().connect_tcp(*args, **kwargs)

    def transport(marker):
        result = httpx.HTTPTransport(verify=True, trust_env=False, retries=0)
        result._pool = httpcore.ConnectionPool(
            network_backend=SynchronizedBackend(
                [
                    b"HTTP/1.1 200 OK\r\nX-Marker: "
                    + marker.encode()
                    + b'\r\nContent-Length: 11\r\n\r\n{"data":[]}'
                ]
            )
        )
        return result

    def unrelated():
        with httpx.Client(transport=transport("unrelated-debug-preserved")) as client:
            return client.get("https://unrelated.example").status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        other = executor.submit(unrelated)
        result = ModelDiscoverer(settings, transport(SECRET)).discover(
            command(configured[1]["revision"])
        )
        assert other.result(timeout=5) == 200 and result["ok"]
    assert SECRET not in caplog.text
    assert "unrelated-debug-preserved" in caplog.text
    assert "http_status=200" in caplog.text


@pytest.mark.parametrize("draft", (False, True))
def test_short_symbol_key_allows_public_hostname_and_embedded_model_word(settings, draft):
    profile = {"base_url": "https://api.example/v1", "api_key": "api"}
    if draft:
        request = command(profile=profile)
    else:
        saved = ModelSettingsRepository(settings).update(
            {"expected_revision": "0", "default": profile}
        )
        request = command(saved["revision"])
    calls = []
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(
            lambda request: calls.append(request) or catalog("rapid-model", "capital-v2")
        ),
    ).discover(request)
    assert result["ok"] and result["models"] == ["rapid-model", "capital-v2"]
    assert len(calls) == 1
    assert calls[0].headers["authorization"] == "Bearer api"
    assert str(calls[0].url) == "https://api.example/v1/models"


@pytest.mark.parametrize(
    "model",
    ["api", "echo-api", "api/model", "model_api", "%61pi", "%2561pi", "&#97;pi", "%26%2397%3Bpi"],
)
def test_short_symbol_exact_delimited_and_encoded_echoes_are_rejected(settings, model):
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: catalog(model))
    ).discover(command(profile={"base_url": "https://api.example/v1", "api_key": "api"}))
    assert result["code"] == "invalid_response" and result["models"] == []


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://api.example/api",
        "https://api.example/echo-api",
        "https://api.example/%61pi",
        "https://api.example/%2561pi",
        "https://api.example/%25252561pi",
        "https://echo-api.example/v1",
        "https://%61pi.example/v1",
        "https://%2561pi.example/v1",
    ],
)
def test_short_symbol_path_or_decorated_hostname_echo_is_rejected(settings, endpoint):
    calls = []
    result = ModelDiscoverer(
        settings, httpx.MockTransport(lambda request: calls.append(request))
    ).discover(command(profile={"base_url": endpoint, "api_key": "api"}))
    assert result["code"] == "invalid_configuration" and not calls


@pytest.mark.parametrize("secret", ["A1b2C3d4E5f6G7h8", "sk-ab", SECRET, "key%61"])
@pytest.mark.parametrize("encoding", ["raw", "percent", "double", "html"])
@pytest.mark.parametrize("target", ["model", "path", "hostname"])
def test_structured_or_long_credentials_remain_blocked_inside_larger_values(
    settings, secret, encoding, target, caplog
):
    caplog.set_level(logging.DEBUG)

    def encode(value):
        return "".join(f"%{byte:02X}" for byte in value.encode())

    encoded = {
        "raw": secret,
        "percent": encode(secret),
        "double": encode(encode(secret)),
        "html": "".join(f"&#{ord(char)};" for char in secret),
    }[encoding]
    endpoint = (
        f"https://x{encoded}x.example/v1"
        if target == "hostname"
        else f"https://provider.example/x{encoded}x"
        if target == "path"
        else "https://provider.example/v1"
    )
    if target in {"path", "hostname"} and encoding == "html":
        endpoint = endpoint.replace("#", "%23")
    calls = []
    result = ModelDiscoverer(
        settings,
        httpx.MockTransport(lambda request: calls.append(request) or catalog("x" + encoded + "x")),
    ).discover(command(profile={"base_url": endpoint, "api_key": secret}))
    assert result["models"] == []
    assert result["code"] == ("invalid_response" if target == "model" else "invalid_configuration")
    assert len(calls) == (1 if target == "model" else 0)
    assert secret not in caplog.text + json.dumps(result)
