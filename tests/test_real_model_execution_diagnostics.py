"""No provider calls: exercise failure artifact retention before private cleanup."""

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ci_real_model as harness
from workbench.filesystem import write_json
from workbench.settings import ROOT


def configuration():
    return harness.configuration(
        {"BASE_URL": harness.ENDPOINT, "MODE": harness.MODEL, "API_KEY": "test-only-secret"}
    )


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Native assertion failed: HTTP 422", "Native assertion failed: HTTP 422"),
        (
            "Bad test-only-secret https://host/path?token=private-canary",
            "Bad [REDACTED] [URL REDACTED]",
        ),
        ("Bad /tmp/private-directory/file.json", "Bad [PATH]"),
        (r"Bad C:\Users\private-directory\file.json", "Bad [PATH]"),
        ("Authorization: Bearer private-canary", "[REDACTED HEADER]"),
        (
            "Failed to connect DATABASE_PASSWORD=private-canary",
            "Failed to connect [REDACTED CREDENTIAL]",
        ),
        ("Invalid OPENAI_API_KEY=private-canary", "Invalid [REDACTED CREDENTIAL]"),
        (
            'Bad provider reply: {"choices": [{"content": "private-canary"}]}',
            "Bad provider reply: [structured payload omitted]",
        ),
        ('{"provider_response": "private-canary"}', "Oversized exception headline omitted"),
        ("x" * 5000, "Oversized exception headline omitted"),
        ("Selected assertion\nraw provider response private-canary", "Selected assertion"),
    ],
)
def test_execution_diagnostic_is_bounded_selected_and_secret_redacted(message, expected):
    try:
        raise RuntimeError(message)
    except RuntimeError as error:
        result = harness.safe_execution_failure(
            error, "downloaded_native_runtime", harness.DiagnosticTextBudget(("test-only-secret",))
        )
    assert result["message_excerpt"] == expected
    assert result["exception_type"] == "RuntimeError"
    assert result["stage"] == "downloaded_native_runtime"
    assert result["frames"] == [
        {
            "file": Path(__file__).name,
            "function": "test_execution_diagnostic_is_bounded_selected_and_secret_redacted",
            "line": result["frames"][0]["line"],
        }
    ]
    assert isinstance(result["frames"][0]["line"], int)
    rendered = json.dumps(result)
    for private in ("test-only-secret", "private-canary", "private-directory", "provider_response"):
        assert private not in rendered
    assert len(rendered) < 1600


def test_unprintable_exception_and_unknown_stage_are_safe():
    class Unprintable(Exception):
        def __str__(self):
            raise ValueError("never disclose")

    result = harness.safe_execution_failure(
        Unprintable(), "secret-stage", harness.DiagnosticTextBudget()
    )
    assert result["message_excerpt"] == "Exception text unavailable"
    assert result["stage"] == "unknown"
    assert result["frames"] == []


@pytest.mark.parametrize("collector_failure", [False, True])
@pytest.mark.parametrize("template", ["python-basic", "fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "failure_at,expected_stage",
    [
        ("browser", "smart_delivery_browser"),
        ("receipt", "delivery_receipt"),
        ("integrity", "delivery_receipt"),
        ("unpack", "download_unpack"),
        ("contract", "approved_contract"),
        ("runtime", None),
    ],
)
def test_failure_retains_approved_plan_before_cleanup(
    tmp_path, monkeypatch, template, failure_at, expected_stage, collector_failure
):
    import tempfile

    import uvicorn

    from workbench import api, filesystem, portable, settings, verification

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    public = tmp_path / "public"
    public.mkdir()
    monkeypatch.setattr(settings, "ROOT", public)
    monkeypatch.setattr(harness, "customer_request", lambda: "Synthetic customer request")
    monkeypatch.setattr(
        harness, "safe_workflow_details", lambda *a, **kw: {"terminal_state": "READY"}
    )
    monkeypatch.setattr(
        harness, "preserve_unapproved_design_contract", lambda *a, **kw: {"status": "unavailable"}
    )
    if collector_failure:

        def broken_collector(*args, **kwargs):
            raise ValueError("secondary error test-only-secret")

        monkeypatch.setattr(harness, "safe_workflow_details", broken_collector)
        monkeypatch.setattr(harness, "preserve_unapproved_design_contract", broken_collector)
    payload = b"synthetic zip stub"

    class Store:
        def get_run(self, run_id):
            assert run_id == "test-run"
            return {
                "status": "READY",
                "auto_mode": failure_at != "receipt",
                "model_calls": 3,
                "result": {
                    "sha256": "mismatch"
                    if failure_at == "integrity"
                    else hashlib.sha256(payload).hexdigest(),
                    "cleanroom": {"passed": True},
                },
            }

        def latest_revision(self, run_id, stage):
            return {"requirement": {}}

    application = SimpleNamespace(
        state=SimpleNamespace(token="private-platform-token", store=Store())
    )
    monkeypatch.setattr(api, "create_app", lambda *a, **kw: application)
    monkeypatch.setattr(uvicorn, "Config", lambda *a, **kw: None)
    server = SimpleNamespace(started=True, run=lambda: None, should_exit=False)
    monkeypatch.setattr(uvicorn, "Server", lambda *a: server)

    def fail():
        raise RuntimeError(
            "Selected failure test-only-secret https://private.invalid/path?token=private-canary\nraw tool output"
        )

    with tempfile.TemporaryDirectory(dir=tmp_path) as private:
        directory = Path(private)

        def browser(*a, **kw):
            write_json(directory / "browser-result.json", {"run_id": "test-run", "page_errors": []})
            artifact = harness.approved_plan_artifact_directory(
                directory / "private-platform", "test-run", template
            )
            write_json(artifact / "approved-spec.json", plan)
            (directory / "download.zip").write_bytes(payload)
            if failure_at == "browser":
                fail()
            return SimpleNamespace(returncode=0)

        def unpack(archive, product, *, template):
            if failure_at == "unpack":
                fail()
            write_json(product / "approved-spec.json", plan)
            write_json(product / "deployment/manifest.json", {"plan": plan})

        def contract(*a, **kw):
            if failure_at == "contract":
                fail()

        monkeypatch.setattr(harness.subprocess, "run", browser)
        monkeypatch.setattr(filesystem, "unpack", unpack)
        monkeypatch.setattr(harness, "require_customer_spec", contract)
        monkeypatch.setattr(verification, "require_browser_evidence", lambda *a: None)
        monkeypatch.setattr(verification, "product_interpreter", lambda *a: sys.executable)
        monkeypatch.setattr(verification, "run_probe", lambda *a, **kw: fail())
        monkeypatch.setattr(portable, "verify_native_delivery", lambda *a, **kw: fail())
        monkeypatch.setenv("NATIVE_TEST_DATABASE_URL", "not-exported-database-url")
        with pytest.raises(harness.SafeFailure) as caught:
            harness.run_acceptance(
                configuration(), SimpleNamespace(statuses=[200]), directory, template
            )
        details = caught.value.details
        expected_stage = expected_stage or (
            "downloaded_python_runtime"
            if template == "python-basic"
            else "downloaded_native_runtime"
        )
        assert details["execution"]["stage"] == expected_stage
        assert details["approved_plan_replay"]["status"] == "saved"
        if collector_failure:
            assert details["diagnostic_error_type"] == "ValueError"
            assert details["unapproved_design_replay"] == {
                "status": "diagnostic_failed",
                "error_type": "ValueError",
            }
        assert details["execution"]["frames"]
        assert server.should_exit is True
        assert caught.value.code == {
            "receipt": "delivery_not_ready",
            "integrity": "download_integrity_failed",
        }.get(failure_at, "acceptance_execution_failed")
        for private_value in (
            "test-only-secret",
            "private-canary",
            "raw tool output",
            "not-exported-database-url",
            "private-platform-token",
        ):
            assert private_value not in json.dumps(details)
    assert not directory.exists()
    replay = public / "reports/real-model/approved-plan-replay.json"
    assert json.loads(replay.read_text(encoding="utf-8"))["business"] == plan["business"]
    assert list(replay.parent.iterdir()) == [replay]


@pytest.mark.parametrize("phase", ["configuration", "smoke", "workflow"])
def test_outer_failure_retains_safe_diagnostic(tmp_path, monkeypatch, capsys, phase):
    from workbench import settings

    monkeypatch.setattr(settings, "ROOT", tmp_path)
    if phase == "workflow":
        for name in ("approved-plan-replay.json", "unapproved-design-contract.json"):
            write_json(tmp_path / "reports/real-model" / name, {"stale": True})
    monkeypatch.setattr(
        sys, "argv", ["ci_real_model", "--phase", "smoke" if phase != "workflow" else "full"]
    )
    monkeypatch.setenv("API_KEY", "test-only-secret")

    def fail(*a, **kw):
        raise RuntimeError(
            "Outer failure test-only-secret https://private.invalid/?token=private-canary\nraw environment dump"
        )

    transport = SimpleNamespace(calls=0, statuses=[], receipts=[], shutdown=lambda: None)
    monkeypatch.setattr(
        harness, "trusted_dispatch", fail if phase == "configuration" else lambda *a: None
    )
    monkeypatch.setattr(harness, "BoundedRealTransport", lambda *a: transport)
    monkeypatch.setattr(harness, "verified_smoke_receipt", lambda *a: {"passed": True})
    monkeypatch.setattr(harness, "smoke", fail)
    monkeypatch.setattr(harness, "run_acceptance", fail)
    monkeypatch.setattr(harness, "configuration", lambda *a: config_value)
    config_value = SimpleNamespace(
        key=SimpleNamespace(get_secret_value=lambda: "test-only-secret"),
        model=harness.MODEL,
        base_url=harness.ENDPOINT,
    )
    with pytest.raises(SystemExit, match="1"):
        harness.main()
    result = json.loads((tmp_path / "reports/real-model/summary.json").read_text(encoding="utf-8"))
    assert result["failure_details"]["execution"]["stage"] == phase
    if phase == "workflow":
        assert not (tmp_path / "reports/real-model/approved-plan-replay.json").exists()
        assert not (tmp_path / "reports/real-model/unapproved-design-contract.json").exists()
    assert result["failure_details"]["execution"]["exception_type"] == "RuntimeError"
    rendered = capsys.readouterr().out
    for private in ("test-only-secret", "private-canary", "raw environment dump"):
        assert private not in rendered


def test_trace_frames_are_bounded_and_secret_filenames_are_not_retained():
    scope = {}
    exec(
        compile(
            "def recurse(n):\n if n: return recurse(n-1)\n raise RuntimeError('selected')",
            "/tmp/test-only-secret.py",
            "exec",
        ),
        scope,
    )
    try:
        scope["recurse"](20)
    except RuntimeError as error:
        result = harness.safe_execution_failure(
            error, "workflow", harness.DiagnosticTextBudget(("test-only-secret",))
        )
    assert len(result["frames"]) == 8
    assert all(frame["file"] == "unavailable" for frame in result["frames"])
    assert all(set(frame) == {"file", "function", "line"} for frame in result["frames"])
    assert "test-only-secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "content,finish,extra,error",
    [
        ('{"value":1}', "length", {}, "truncated"),
        ('{"value":1}', "stop", {"refusal": "private refusal text"}, "refusal"),
        (
            '{"value":1}',
            "tool_calls",
            {"tool_calls": [{"id": "private tool"}]},
            "unexpected_tool_call",
        ),
        ('{"value":1}', None, {}, "invalid_finish_reason"),
        ('```json\n{"value":1}\n```', "stop", {}, "json_invalid"),
        ('{"value":1,"value":2}', "stop", {}, "duplicate_json_key"),
        ('{"value":"1"}', "stop", {}, "int_type"),
    ],
)
def test_actual_provider_receipt_uses_same_fail_closed_output_gate(content, finish, extra, error):
    from pydantic import BaseModel

    class Schema(BaseModel):
        value: int

    data = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": finish,
                    "message": {"role": "assistant", "content": content, **extra},
                }
            ]
        }
    ).encode()
    result = harness.response_receipt(200, data, "plan", Schema)
    assert result["schema_valid"] is False
    assert result.get("response_contract_error") == error or error in result.get(
        "schema_error_types", []
    )
    assert "private refusal" not in json.dumps(result)
    assert "private tool" not in json.dumps(result)


def test_actual_schema_request_requires_explicit_json_mode_before_http():
    import httpx
    from pydantic import BaseModel

    class Schema(BaseModel):
        value: int

    transport = harness.BoundedRealTransport(configuration())
    transport.transport.close()
    requests = []
    transport.transport = httpx.MockTransport(
        lambda request: (
            requests.append(request)
            or httpx.Response(
                200,
                json={
                    "choices": [{"finish_reason": "stop", "message": {"content": '{"value":1}'}}]
                },
            )
        )
    )
    transport.current_schema = Schema
    transport.current_stage = "plan"
    body = {"model": harness.MODEL, "messages": [{"role": "user", "content": "Return JSON"}]}
    try:
        with pytest.raises(harness.SafeFailure, match="workflow_json_mode_required"):
            transport.handle_request(
                httpx.Request(
                    "POST",
                    harness.ENDPOINT + "/chat/completions",
                    headers={"Authorization": "Bearer test-only-secret"},
                    json=body,
                )
            )
        assert requests == [] and transport.calls == 0
        body["response_format"] = {"type": "json_object"}
        transport.handle_request(
            httpx.Request(
                "POST",
                harness.ENDPOINT + "/chat/completions",
                headers={"Authorization": "Bearer test-only-secret"},
                json=body,
            )
        )
        assert len(requests) == 1
        assert transport.receipts[0]["schema_valid"] is True
        assert transport.receipts[0]["requested_output_mode"] == "json_object"
        assert transport.receipts[0]["provider"] == "deepseek"
    finally:
        transport.shutdown()


def test_actual_acceptance_pins_all_deepseek_structured_profiles(tmp_path, monkeypatch):
    from workbench.settings import STAGES

    monkeypatch.setenv("PROVIDER", "openai")
    monkeypatch.setenv("PLANNING_PROVIDER", "compatible")
    monkeypatch.setenv("REVIEW_MAX_OUTPUT_TOKENS", "1")
    settings = harness.acceptance_settings(configuration(), tmp_path)
    for stage in STAGES:
        profile = settings.model_for(stage)
        assert profile.provider == "deepseek"
        assert profile.output_mode == "json_object"
        assert profile.max_output_tokens == harness.MAX_COMPLETION_TOKENS
        assert profile.base_url == harness.ENDPOINT
        assert profile.model == harness.MODEL
