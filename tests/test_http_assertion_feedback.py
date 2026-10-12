"""Safe approved assertion coordinates flow to repair without changing acceptance."""

import json

import httpx
import pytest
from test_mini_swe_checkpoints import bound_check_fixture, exercise

from workbench.capability_contracts import HttpStep
from workbench.capability_diagnostics import http_assertion_diagnostic, node_diagnostic
from workbench.capability_verification import BusinessCheckFailure, CheckFailure, run_steps
from workbench.coding import mini_swe as agent


@pytest.mark.parametrize("code", ["http_status", "json_decode", "json_equals", "json_absent"])
def test_actual_oracle_reports_only_fixed_coordinates(code):
    step = HttpStep(path="/approved", status=200, equals={"$.first": 1, "$.second": 2})
    raw = b'{"first":1,"second":"private-value"}'
    status = 200
    if code == "http_status":
        status = 418
    elif code == "json_decode":
        raw = b"private-invalid-json"
    elif code == "json_absent":
        step = HttpStep(path="/approved", status=200, absent=["$.missing", "$.private"])
        raw = b'{"private":"private-value"}'
    with (
        httpx.Client(
            base_url="https://fixture.invalid",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status, stream=httpx.ByteStream(raw))
            ),
        ) as client,
        pytest.raises(BusinessCheckFailure) as caught,
    ):
        run_steps(client, [step], {})
    expected = {"code": code, "step": 1}
    if code == "http_status":
        expected.update(expected_status=200, actual_status=418)
    if code in {"json_equals", "json_absent"}:
        expected["assertion"] = 2
    assert caught.value.diagnostic == expected
    assert "private" not in json.dumps(http_assertion_diagnostic(caught.value.diagnostic))


@pytest.mark.parametrize("status", [502, 503, 504])
def test_gateway_failure_does_not_become_repairable_assertion(status):
    with (
        httpx.Client(
            base_url="https://fixture.invalid",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status, stream=httpx.ByteStream(b""))
            ),
        ) as client,
        pytest.raises(CheckFailure) as caught,
    ):
        run_steps(client, [HttpStep(path="/", status=200)], {})
    assert type(caught.value) is CheckFailure


@pytest.mark.parametrize(
    "mutation",
    [
        {"code": "private"},
        {"step": True},
        {"step": 4097},
        {"step": 0},
        {"assertion": True},
        {"assertion": 0},
        {"assertion": 4097},
    ],
)
def test_projection_rejects_invalid_fields(mutation):
    value = {"code": "json_equals", "step": 1, "assertion": 1, **mutation}
    assert http_assertion_diagnostic(value) is None


def test_summary_projection_drops_extra_text(tmp_path):
    path = tmp_path / "candidate-node-verification.json"
    path.write_text(
        json.dumps(
            {
                "passed": False,
                "http_assertion": {
                    "code": "json_equals",
                    "step": 3,
                    "assertion": 2,
                    "response": "private-content",
                    "pointer": "private-pointer",
                    "expected": "private",
                },
            }
        )
    )
    value = node_diagnostic(tmp_path / "candidate", aggregate=False)
    assert value["http_assertion"] == {"code": "json_equals", "step": 3, "assertion": 2}
    assert "private" not in json.dumps(value)


def business_proof(proof, diagnostic):
    proof.update(
        repairable_failure="business_assertion",
        failed_scenario="sla-api-check",
        http_assertion=diagnostic,
    )


@pytest.mark.parametrize(
    "diagnostic,accepted",
    [
        ({"code": "json_equals", "step": 3, "assertion": 2}, True),
        ({"code": "json_equals", "step": 3, "assertion": 3}, False),
        ({"code": "json_absent", "step": 3, "assertion": 1}, False),
        ({"code": "json_decode", "step": 2}, False),
        ({"code": "json_decode", "step": 1}, True),
        ({"code": "http_status", "step": 4, "expected_status": 401, "actual_status": 200}, True),
        ({"code": "http_status", "step": 4, "expected_status": 200, "actual_status": 401}, False),
        ({"code": "http_status", "step": 3, "expected_status": 200, "actual_status": 503}, False),
        ({"code": "json_equals", "step": 5, "assertion": 1}, False),
    ],
)
def test_feedback_coordinates_match_approved_scenario(
    settings, tmp_path, monkeypatch, diagnostic, accepted
):
    import time

    plan, task, candidate = bound_check_fixture(
        tmp_path, monkeypatch, lambda proof: business_proof(proof, diagnostic)
    )
    value = agent.check_candidate(settings, task, plan, candidate, time.monotonic() + 40)
    assert ("http_assertion" in value) is accepted
    assert value["scenario"] == "sla-api-check"
    assert value["category"] == "business_assertion" and value["passed"] is False


def test_fixed_assertion_feedback_reaches_same_worker_repair(settings, tmp_path, monkeypatch):
    actual_check = agent.check_candidate
    diagnostic = {"code": "json_equals", "step": 3, "assertion": 2}
    bound_check_fixture(tmp_path, monkeypatch, lambda proof: business_proof(proof, diagnostic))
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], combined=True
    )
    successful_check = agent.check_candidate
    deadlines = []

    def checkpoint(*args):
        deadlines.append(args[-1])
        return actual_check(*args) if len(deadlines) == 1 else successful_check(*args)

    monkeypatch.setattr(agent, "check_candidate", checkpoint)
    run()
    assert len(calls) == 2 and len(deadlines) == 2 and deadlines[0] == deadlines[1]
    assert calls[1]["verification_feedback"]["http_assertion"] == diagnostic
    assert calls[1]["verification_feedback"]["scenario"] == "sla-api-check"
    assert cleaned == [True] and (product / "app.py").read_text() == "# baseline\n"


def test_original_controller_handler_preserves_fixed_assertion_in_receipt(tmp_path):
    import ast
    import inspect

    from workbench import capability_sandbox as sandbox
    from workbench.capability_verification import BrowserFailure

    tree = ast.parse(inspect.getsource(sandbox._verify))
    handler = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler)
        and isinstance(node.type, ast.Name)
        and node.type.id == "CheckFailure"
    )
    program = ast.fix_missing_locations(
        ast.Module(
            body=[
                ast.Try(
                    body=[ast.Raise(exc=ast.Name(id="failure", ctx=ast.Load()))],
                    handlers=[handler],
                    orelse=[],
                    finalbody=[],
                )
            ],
            type_ignores=[],
        )
    )
    diagnostic = {"code": "http_status", "step": 2, "expected_status": 201, "actual_status": 422}
    failure = BusinessCheckFailure(
        "private original message", diagnostic={**diagnostic, "body": "private"}
    )
    failure.scenario_id = "sla-api-check"
    scope = {
        "failure": failure,
        "CheckFailure": CheckFailure,
        "BusinessCheckFailure": BusinessCheckFailure,
        "BrowserFailure": BrowserFailure,
        "http_assertion_diagnostic": http_assertion_diagnostic,
        "receipt": {},
        "checkpoint": {},
        "native": False,
    }
    exec(compile(program, inspect.getsourcefile(sandbox), "exec"), scope)
    receipt = scope["receipt"]
    assert receipt["repairable_failure"] == "business_assertion"
    assert receipt["http_assertion"] == diagnostic
    (tmp_path / "candidate-node-verification.json").write_text(json.dumps(receipt))
    projected = node_diagnostic(tmp_path / "candidate", aggregate=False)
    assert projected["http_assertion"] == diagnostic and "private" not in json.dumps(projected)


@pytest.mark.parametrize("value", [True, 99, 600, "200", float("nan"), float("inf")])
def test_status_projection_rejects_non_status_values(value):
    assert (
        http_assertion_diagnostic(
            {"code": "http_status", "step": 1, "expected_status": 200, "actual_status": value}
        )
        is None
    )


@pytest.mark.parametrize("equals", [{"$.z": 2, "$.a": 1}, {"$.a": 1, "$.z": 2}])
def test_assertion_ordinal_survives_plan_dictionary_reordering(equals):
    step = HttpStep(path="/approved", status=200, equals=equals)
    with (
        httpx.Client(
            base_url="https://fixture.invalid",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, stream=httpx.ByteStream(b'{"a":1,"z":0}'))
            ),
        ) as client,
        pytest.raises(BusinessCheckFailure) as caught,
    ):
        run_steps(client, [step], {})
    assert caught.value.diagnostic == {"code": "json_equals", "step": 1, "assertion": 2}


@pytest.mark.parametrize(
    "scenario,bound",
    [
        ("sla-api-check", True),
        ("sla-dashboard-check", True),
        ("private", True),
        ("sla-api-check", False),
    ],
)
def test_checkpoint_summary_exports_only_bound_approved_scenario(tmp_path, scenario, bound):
    from test_mini_swe_checkpoints import cleanup_binding

    from workbench.core.contracts import digest
    from workbench.filesystem import manifest, write_json
    from workbench.infrastructure.sandbox.cleanup import checkpoint_receipts

    task, plan, binding = cleanup_binding()
    candidate = tmp_path / "step-1"
    candidate.mkdir()
    (candidate / "app.py").write_text("# offline fixture")
    write_json(
        tmp_path / "step-1-node-verification.json",
        {
            "checkpoint": {"nonce": binding["nonce"], "task": binding["task"]},
            "plan_digest": binding["plan"],
            "source_digest": digest(manifest(candidate)) if bound else "f" * 64,
            "sandbox_name": "rnd-source-" + "a" * 32,
            "cleanup": "deleted",
            "passed": False,
            "failed_scenario": scenario,
            "http_assertion": {"code": "json_equals", "step": 3, "assertion": 1},
        },
    )
    value = checkpoint_receipts(tmp_path, task, plan)[0]
    assert ("failed_scenario" in value) is (bound and scenario == "sla-api-check")
    assert ("http_assertion" in value) is bound
    assert "private" not in json.dumps(value)
