"""Offline connection probes: real adapter, mocked transport, no paid calls."""

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from workbench.model_connection import (
    ConnectionTestBusy,
    ConnectionTestRequest,
    ModelConnectionTester,
)
from workbench.model_settings import (
    ModelSettingsRepository,
    RevisionConflict,
    register_model_settings_routes,
)

SECRET = "dummy-connection-probe-secret-never-real"


@pytest.fixture
def configured(settings):
    repository = ModelSettingsRepository(settings)
    saved = repository.update(
        {
            "expected_revision": "0",
            "default": {
                "base_url": "https://provider.example/v1",
                "model": "saved-model",
                "api_key": SECRET,
                "max_output_tokens": 8000,
            },
            "stages": {"coding": {"model": "saved-coder"}},
        }
    )
    return repository, saved


def command(revision, stage="default", **extra):
    return ConnectionTestRequest(
        stage=stage,
        expected_revision=revision,
        request_id=str(uuid.uuid4()),
        confirm_cost=True,
        **extra,
    )


def completion(content='{"ok":true}', finish="stop"):
    return httpx.Response(
        200,
        json={
            "id": "test-probe",
            "object": "chat.completion",
            "created": 0,
            "model": "saved-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish,
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17},
        },
    )


def test_probe_uses_saved_effective_profile_one_bounded_call_and_no_project_data(
    settings, configured
):
    repository, saved = configured
    seen = []

    def handle(request):
        seen.append(request)
        return completion()

    tester = ModelConnectionTester(settings, httpx.MockTransport(handle))
    result = tester.test(command(saved["revision"], "coding"))
    assert result["ok"] and result["code"] == "connected"
    assert result["phase"] == "completed" and result["attempts"] == 1
    assert result["revision"] == saved["revision"] and result["stage"] == "coding"
    assert result["model"] == "saved-coder"
    assert result["usage"]["total_tokens"] == 17
    assert len(seen) == 1
    assert str(seen[0].url) == "https://provider.example/v1/chat/completions"
    assert seen[0].headers["authorization"] == "Bearer " + SECRET
    body = json.loads(seen[0].content)
    assert body["model"] == "saved-coder"
    assert body.get("max_tokens", body.get("max_completion_tokens")) == 128
    assert body["response_format"] == {"type": "json_object"}
    assert body["stream"] is False
    assert "project" not in json.dumps(body).lower()
    assert SECRET not in json.dumps(result)
    assert repository.public()["revision"] == saved["revision"]
    assert not (settings.data_dir / "workbench.db").exists()


def test_probe_keeps_one_snapshot_when_configuration_changes_during_call(settings, configured):
    repository, saved = configured

    def handle(request):
        repository.update(
            {"expected_revision": saved["revision"], "default": {"model": "next-model"}}
        )
        assert json.loads(request.content)["model"] == "saved-model"
        return completion()

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert result["ok"] and result["revision"] == saved["revision"]
    assert repository.public()["revision"] != result["revision"]


@pytest.mark.parametrize(
    "status,code,retryable",
    [
        (401, "authentication_failed", False),
        (403, "permission_denied", False),
        (404, "model_or_endpoint_not_found", False),
        (429, "rate_limited", True),
        (500, "http_500", True),
        (302, "http_302", False),
    ],
)
def test_http_failures_are_actionable_redacted_and_never_retried(
    settings, configured, status, code, retryable, caplog
):
    _, saved = configured
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            status,
            headers={"location": "https://unapproved.example/v1"},
            json={"error": {"message": SECRET}},
        )

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert not result["ok"] and result["code"] == code and result["phase"] == "request"
    assert result["retryable"] is retryable and result["http_status"] == status
    assert len(requests) == result["attempts"] == 1
    assert SECRET not in json.dumps(result) + caplog.text
    assert len(result["trace_id"]) == 32


@pytest.mark.parametrize(
    "exception,code", [(httpx.ReadTimeout, "timeout"), (httpx.ConnectError, "connection_failed")]
)
def test_transport_errors_do_not_echo_exception_text(settings, configured, exception, code):
    _, saved = configured
    calls = []

    def handle(request):
        calls.append(request)
        raise exception(SECRET, request=request)

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert result["code"] == code and result["retryable"]
    assert len(calls) == 1 and SECRET not in json.dumps(result)


@pytest.mark.parametrize(
    "content,finish,code",
    [
        (SECRET, "stop", "invalid_response"),
        ('{"ok":false}', "stop", "invalid_response"),
        ('{"ok":true}', "length", "truncated"),
        ("", "stop", "empty_content"),
    ],
)
def test_invalid_model_output_is_not_reported_as_connected(
    settings, configured, content, finish, code
):
    _, saved = configured
    result = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: completion(content, finish))
    ).test(command(saved["revision"]))
    assert not result["ok"] and result["phase"] == "validation" and result["code"] == code
    assert SECRET not in json.dumps(result)


def test_duplicate_request_is_cached_and_stale_configuration_cannot_call(settings, configured):
    _, saved = configured
    calls = []
    tester = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: calls.append(request) or completion())
    )
    request = command(saved["revision"])
    first = tester.test(request)
    assert tester.test(request) == first and len(calls) == 1
    with pytest.raises(RevisionConflict):
        tester.test(request.model_copy(update={"stage": "coding"}))
    with pytest.raises(RevisionConflict):
        tester.test(command("stale"))
    assert len(calls) == 1


def test_concurrent_probe_is_blocked_before_second_model_call(settings, configured):
    _, saved = configured
    started, release = threading.Event(), threading.Event()

    def handle(request):
        started.set()
        assert release.wait(5)
        return completion()

    tester = ModelConnectionTester(settings, httpx.MockTransport(handle))
    with ThreadPoolExecutor(max_workers=1) as executor:
        running = executor.submit(tester.test, command(saved["revision"]))
        try:
            assert started.wait(5)
            with pytest.raises(ConnectionTestBusy):
                tester.test(command(saved["revision"]))
            # Independent service instances must share the same file lock.
            with pytest.raises(ConnectionTestBusy):
                ModelConnectionTester(settings).test(command(saved["revision"]))
        finally:
            release.set()
        assert running.result()["ok"]


def test_missing_configuration_never_uses_network(settings):
    def unexpected(request):
        raise AssertionError("No network permitted")

    result = ModelConnectionTester(settings, httpx.MockTransport(unexpected)).test(command("0"))
    assert result["code"] == "invalid_configuration" and result["attempts"] == 0


def test_test_route_requires_auth_origin_saved_revision_and_explicit_cost_confirmation(
    settings, configured, monkeypatch
):
    _, saved = configured
    calls = []
    tester = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: calls.append(request) or completion())
    )
    monkeypatch.setattr("workbench.model_connection.ModelConnectionTester", lambda settings: tester)
    app = FastAPI()

    def auth(request: Request):
        if request.headers.get("authorization") != "Bearer local-test-token":
            raise HTTPException(401)

    register_model_settings_routes(app, settings, auth)
    body = command(saved["revision"]).model_dump()
    with TestClient(app) as client:
        assert client.post("/settings/models/test", json=body).status_code == 401
        client.headers["authorization"] = "Bearer local-test-token"
        assert (
            client.post(
                "/settings/models/test", json=body, headers={"origin": "https://evil.example"}
            ).status_code
            == 403
        )
        for invalid in (
            {**body, "confirm_cost": False},
            {**body, "stage": SECRET},
            {**body, "api_key": SECRET},
        ):
            response = client.post("/settings/models/test", json=invalid)
            assert response.status_code == 422 and SECRET not in response.text
        assert (
            client.post(
                "/settings/models/test", json={**body, "expected_revision": "stale"}
            ).status_code
            == 409
        )
        assert not calls
        response = client.post("/settings/models/test", json=body)
        assert response.status_code == 200 and response.json()["ok"]
        assert response.headers["cache-control"] == "no-store"
        assert client.post("/settings/models/test", json=body).json() == response.json()
        assert len(calls) == 1 and SECRET not in response.text
