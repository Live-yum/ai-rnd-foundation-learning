"""Synthetic data-only checks for bounded retained captures and substitutions."""

import json

import httpx
import pytest

from workbench import capability_verification as verifier
from workbench.capability_contracts import AcceptanceScenario, HttpStep


def client_for(values, seen):
    values = iter(values)

    def respond(request):
        seen.append(request)
        body = json.dumps(next(values)).encode()
        return httpx.Response(200, stream=httpx.ByteStream(body))

    return httpx.Client(base_url="http://candidate.invalid", transport=httpx.MockTransport(respond))


@pytest.mark.parametrize("text", ["x" * 16384, "é" * 8192])
def test_capture_single_value_exact_byte_limit_and_overflow(text):
    assert verifier.capture_scalar_size(text) == verifier.MAX_CAPTURE_VALUE_BYTES
    with pytest.raises(verifier.CheckFailure, match="单值预算"):
        verifier.capture_scalar_size(text + "x")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), [], {}, None])
def test_capture_rejects_nonfinite_or_nonscalar_values(value):
    with pytest.raises(verifier.CheckFailure):
        verifier.capture_scalar_size(value)


def test_oversize_response_capture_is_never_retained():
    variables, seen = {}, []
    step = HttpStep(path="/", status=200, captures={"token": "$.token"})
    with client_for([{"token": "secret" * 3000}], seen) as client:
        with pytest.raises(verifier.CheckFailure, match="单值预算") as raised:
            verifier.run_steps(client, [step], variables)
    assert variables == {}
    assert "secret" not in str(raised.value)


def test_capture_boundary_overwrite_credit_and_reuse_across_http_steps(monkeypatch):
    variables, seen = {}, []
    value = "x" * verifier.MAX_CAPTURE_VALUE_BYTES
    exact_budget = 128 + verifier.CaptureBudget.entry_size("token", value)
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", exact_budget)
    steps = [
        HttpStep(path="/first", status=200, captures={"token": "$.token"}),
        HttpStep(
            method="POST",
            path="/second",
            status=200,
            body={"echo": "${token}"},
            captures={"token": "$.token"},
        ),
        HttpStep(path="/${token}", status=200, captures={"small": "$.small"}),
    ]
    with client_for([{"token": value}, {"token": "short"}, {"small": True}], seen) as client:
        receipts = verifier.run_steps(client, steps, variables)
    assert len(receipts) == 3
    assert json.loads(seen[1].content) == {"echo": value}
    assert seen[2].url.path == "/short"
    assert variables == {"token": "short", "small": True}


def test_state_limit_counts_scenarios_together_without_storing_overflow(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", 2048)
    saved, seen = {}, []
    scenarios = [
        AcceptanceScenario(
            id=name,
            title="Synthetic",
            requirements=["r"],
            steps=[HttpStep(path="/", status=200, captures={"token": "$.token"})],
        )
        for name in ("first", "second")
    ]
    with client_for([{"token": "x" * 1000}, {"token": "y" * 1000}], seen) as client:
        with pytest.raises(verifier.CheckFailure, match="总预算"):
            verifier.run_scenarios(client, scenarios, saved=saved)
    assert len(seen) == 2
    assert saved["first"]["token"] == "x" * 1000
    assert "token" not in saved["second"]
    assert verifier.CaptureBudget(saved).used <= 2048


def test_same_variable_replacement_does_not_accumulate_historical_size(monkeypatch):
    variables = {"token": "x" * 50}
    budget = verifier.CaptureBudget({"scenario": variables})
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", budget.used)
    before = budget.used
    for _ in range(100):
        budget.store(variables, "token", "y" * 50)
    assert budget.used == before
    with pytest.raises(verifier.CheckFailure, match="总预算"):
        budget.store(variables, "token", "z" * 51)
    assert variables["token"] == "y" * 50
    budget.store(variables, "token", "small")
    assert budget.used == before - 45


def test_invalid_saved_capture_is_rejected_before_interpolation_or_request():
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: pytest.fail("request reached"))
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="单值预算"):
            verifier.run_steps(
                client, [HttpStep(path="/${token}", status=200)], {"token": "x" * 16385}
            )


def test_interpolation_retains_scalar_types_and_bounds_repetition_before_join(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_INTERPOLATED_BYTES", 100)
    assert verifier.interpolate(
        {"id": "${id}", "enabled": "${flag}"}, {"id": 123, "flag": True}
    ) == {"id": 123, "enabled": True}
    assert verifier.interpolate("/${value}", {"value": "a/b"}, path=True) == "/a%2Fb"
    with pytest.raises(verifier.CheckFailure, match="替换超过预算"):
        verifier.interpolate("${token}" * 11, {"token": "x" * 10})
    with pytest.raises(verifier.CheckFailure, match="替换超过预算"):
        verifier.interpolate(["${token}"] * 11, {"token": "x" * 10})


def test_decoder_recursion_failure_is_classified_without_retaining_data(monkeypatch):
    # Decoder recursion behavior differs across supported interpreter builds.
    # Inject the exception rather than depending on a particular C stack limit.
    def too_deep(_raw):
        raise RecursionError("synthetic decoder depth")

    monkeypatch.setattr(verifier.json, "loads", too_deep)
    body = b"{}"
    with httpx.Client(
        base_url="http://candidate.invalid",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=httpx.ByteStream(body))
        ),
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="JSON"):
            verifier.run_steps(
                client, [HttpStep(path="/", status=200, captures={"value": "$"})], {}
            )
