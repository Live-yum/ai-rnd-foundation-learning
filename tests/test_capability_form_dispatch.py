"""Bounded owned-native form protocol; no external CAPTCHA or account calls."""

import json
from urllib.parse import parse_qs

import httpx
import pytest
from pydantic import ValidationError

from workbench import capability_verification as verifier
from workbench.capability_contracts import AcceptanceScenario, HttpStep


@pytest.mark.parametrize("wait", [-1, 1001, True, "300"])
def test_wait_is_a_strict_small_nonnegative_integer(wait):
    with pytest.raises(ValidationError):
        HttpStep(path="/", status=200, wait_ms=wait)


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Type": "text/plain"},
        {"content-encoding": "gzip"},
        {"Transfer-Encoding": "chunked"},
    ],
)
def test_request_representation_headers_are_not_model_overrides(headers):
    with pytest.raises(ValidationError):
        HttpStep(path="/", status=200, headers=headers)


@pytest.mark.parametrize(
    "body",
    [None, [], {"x": 1}, {"x": "x" * 4097}, {str(i): "x" for i in range(21)}, {"x": "é" * 4096}],
)
def test_form_values_are_string_only_and_bounded(body):
    with pytest.raises(ValidationError):
        HttpStep(method="POST", path="/", status=200, body=body, body_encoding="form")


def test_form_dispatch_encodes_once_and_wait_uses_the_same_deadline(monkeypatch):
    now, seen = [10.0], []
    monkeypatch.setattr(verifier.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        verifier.time, "sleep", lambda seconds: now.__setitem__(0, now[0] + seconds)
    )

    def respond(request):
        seen.append((now[0], request))
        return httpx.Response(200, stream=httpx.ByteStream(b'{"ok":true}'))

    with httpx.Client(
        base_url="http://owned.invalid", transport=httpx.MockTransport(respond)
    ) as client:
        result = verifier.run_steps(
            client,
            [
                HttpStep(
                    method="POST",
                    path="/system/auth/login",
                    status=200,
                    wait_ms=300,
                    body_encoding="form",
                    body={"username": "synthetic+user", "captcha_key": "${challenge}"},
                    equals={"$.ok": True},
                )
            ],
            {"challenge": "a&b"},
            deadline=11.0,
        )
    assert result[0]["passed"] is True
    assert seen[0][0] == pytest.approx(10.3)
    request = seen[0][1]
    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert parse_qs(request.content.decode()) == {
        "username": ["synthetic+user"],
        "captcha_key": ["a&b"],
    }
    assert request.extensions["timeout"]["read"] <= 0.701


def test_wait_and_capture_expansion_cannot_consume_past_phase_budget(monkeypatch):
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 10.0)
    with httpx.Client(
        base_url="http://owned.invalid",
        transport=httpx.MockTransport(lambda request: pytest.fail("Must fail before network")),
    ) as client:
        step = HttpStep(
            method="POST",
            path="/",
            status=200,
            wait_ms=300,
            body_encoding="form",
            body={"x": "${value}"},
        )
        with pytest.raises(verifier.CheckFailure, match="期限"):
            verifier.run_steps(client, [step], {"value": "ok"}, deadline=10.2)
        step.wait_ms = 0
        with pytest.raises(verifier.CheckFailure, match="form"):
            verifier.run_steps(client, [step], {"value": "x" * 5000}, deadline=11)


def test_json_body_remains_json_and_never_uses_form(monkeypatch):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, stream=httpx.ByteStream(b"{}"))

    with httpx.Client(
        base_url="http://owned.invalid", transport=httpx.MockTransport(respond)
    ) as client:
        verifier.run_steps(
            client, [HttpStep(method="POST", path="/", status=200, body={"id": 7})], {}
        )
    assert json.loads(seen[0].content) == {"id": 7}
    assert seen[0].headers["content-type"] == "application/json"


def test_wait_budget_counts_all_scenarios_before_first_request(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_HTTP_PHASE_WAIT_MS", 1000)
    scenarios = [
        AcceptanceScenario(
            id=name,
            title=name,
            requirements=["r"],
            steps=[HttpStep(path="/", status=200, wait_ms=600)],
        )
        for name in ("one", "two")
    ]
    with httpx.Client(
        base_url="http://owned.invalid",
        transport=httpx.MockTransport(
            lambda request: pytest.fail("No request before aggregate budget validation")
        ),
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="等待总量"):
            verifier.run_scenarios(client, scenarios)
