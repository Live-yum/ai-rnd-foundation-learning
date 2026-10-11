"""Offline contracts only: no paid models, Docker, Daytona or live evidence."""

import json

import pytest
import yaml

from scripts import ci_live_modules as live
from scripts.sla_fixture import authored_files
from workbench.core.contracts import digest
from workbench.filesystem import manifest, write_json


def dispatch():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": live.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "LIVE_SCENARIO": live.SCENARIO,
        "BASE_URL": "https://model.invalid/v1",
        "MODE": "offline-contract",
        "LIVE_MAX_COST_USD": "5",
        "LIVE_USD_PER_MILLION_TOKENS": "1",
    }


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("REVIEWED_SHA", "b" * 40),
        ("LIVE_SCENARIO", "yudao-mini-swe"),
        ("BASE_URL", "http://model.invalid/v1"),
        ("BASE_URL", "https://user:password@model.invalid/v1"),
        ("BASE_URL", "https://model.invalid/v1?key=bad"),
        ("LIVE_MAX_COST_USD", "0"),
        ("LIVE_MAX_COST_USD", "11"),
        ("LIVE_MAX_COST_USD", "NaN"),
        ("LIVE_MAX_COST_USD", "Infinity"),
        ("LIVE_MAX_COST_USD", "0.0001"),
        ("LIVE_USD_PER_MILLION_TOKENS", "0"),
        ("LIVE_USD_PER_MILLION_TOKENS", "garbage"),
        ("MODE", ""),
    ],
)
def test_preflight_rejects_unreviewed_or_unbounded_dispatch(key, value):
    with pytest.raises(ValueError):
        live.configuration({**dispatch(), key: value})


def test_preflight_needs_no_key_and_cannot_report_real_acceptance(tmp_path, monkeypatch):
    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules", "--preflight"])
    monkeypatch.setattr(live, "execute", lambda *a: pytest.fail("preflight called executor"))
    live.main()
    summary = json.loads(live.REPORT.read_text())
    assert summary["configuration_valid"] is True
    assert summary["passed"] is summary["real_model_acceptance"] is False
    assert summary["limits"]["max_model_calls"] == 32


def test_live_profile_pins_https_costs_and_coding_stage(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.daytona_capability_profile.HOME", tmp_path / "local-profile")
    env = {**dispatch(), "API_KEY": "offline-fixture-only"}
    settings = live.live_settings(env, live.configuration(env), tmp_path)
    assert settings.allow_insecure_model_http is False
    assert settings.mini_swe_enabled is True
    assert settings.mini_swe_max_cost_usd * 2 == 5
    assert settings.mini_swe_usd_per_million_tokens == 1
    assert settings.max_model_calls == 32
    profile = settings.model_for("coding")
    assert profile.base_url == env["BASE_URL"]
    assert profile.max_output_tokens == 8192


def test_failure_receipt_never_publishes_raw_provider_error(tmp_path, monkeypatch):
    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules"])
    monkeypatch.setattr(live, "live_settings", lambda *a: None)

    def reject(*args, **kwargs):
        raise RuntimeError("secret-and-untrusted-provider-text")

    monkeypatch.setattr(live, "execute", reject)
    with pytest.raises(SystemExit):
        live.main()
    raw = live.REPORT.read_text()
    assert "secret-and-untrusted" not in raw
    assert json.loads(raw)["real_model_acceptance"] is False
    assert json.loads(raw)["failure_diagnostic"]["exception_type"] == "RuntimeError"


def test_diagnostic_locates_real_sandbox_boundary_without_sdk_text(settings, tmp_path, monkeypatch):
    from types import SimpleNamespace

    from workbench.infrastructure.sandbox import coding

    closed = []

    def reject(*args, **kwargs):
        raise RuntimeError("private endpoint key headers prompt")

    client = SimpleNamespace(create=reject)
    monkeypatch.setattr(coding, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(coding, "client_for", lambda *a: client)
    monkeypatch.setattr(coding, "close_client", lambda value: closed.append(value))
    plan = live.acceptance_design().implementation
    with pytest.raises(RuntimeError) as captured:
        with coding._local_environment(
            settings, plan.tasks[0], plan.selection.model_dump(), tmp_path
        ):
            pytest.fail("unadmitted sandbox yielded")
    diagnostic = live.failure_diagnostic(captured.value)
    assert diagnostic["stage"] == "coding_sandbox"
    assert diagnostic["exception_type"] == "RuntimeError"
    assert type(diagnostic["trusted_source_line"]) is int
    assert "private" not in json.dumps(diagnostic)
    assert closed == [client]


def test_diagnostic_suppresses_unknown_exception_names_and_untrusted_frames():
    error = type("private-provider-content", (Exception,), {})("private-message")
    try:
        raise error
    except Exception as exc:
        diagnostic = live.failure_diagnostic(exc)
    assert diagnostic == {"exception_type": "other", "stage": "other"}


def test_diagnostic_retains_only_bounded_inspector_facts():
    from workbench.capability_isolation import ContainerInspectionRejected

    error = ContainerInspectionRejected(
        "private docker inspect output",
        category="container_policy",
        facts={"network_mode": "private-network-name", "secret": "private-key"},
    )
    diagnostic = live.failure_diagnostic(error)
    assert diagnostic["container"] == {
        "container_rejection": "container_policy",
        "network_mode": "other",
    }
    assert "private" not in json.dumps(diagnostic)


@pytest.mark.parametrize("receipt_read_fails", [False, True])
def test_real_worker_and_live_context_reach_offline_transport(
    tmp_path, monkeypatch, receipt_read_fails
):
    """Exercise pre-call orchestration; this supplies no real sandbox/model evidence."""
    from contextlib import contextmanager

    import httpx

    import workbench.capability_execution as admission
    from workbench.coding.mini_swe import worker_python
    from workbench.infrastructure.sandbox import coding

    if not worker_python().is_file():
        pytest.skip("optional locked Python3.12 worker not installed")

    @contextmanager
    def offline_environment(*args, **kwargs):
        yield None  # Stop at the first transport call, before any edits.

    monkeypatch.setattr(admission, "capability_execution_prerequisites", lambda *a: None)
    monkeypatch.setattr(coding, "coding_environment", offline_environment)
    monkeypatch.setattr("scripts.daytona_capability_profile.HOME", tmp_path / "absent-profile")
    env = {**dispatch(), "API_KEY": "offline-fixture-only"}
    settings = live.live_settings(env, live.configuration(env), tmp_path)
    seen = []

    def stop(request):
        seen.append(request.url.path)
        raise RuntimeError("offline pre-call boundary reached")

    class OfflineTransport(httpx.MockTransport):
        calls = 0
        responses = 0

    if receipt_read_fails:
        from workbench.store import Store

        def unavailable(*args):
            raise RuntimeError("private-receipt-error")

        monkeypatch.setattr(Store, "model_records", unavailable)
    progress = {}
    with OfflineTransport(stop) as transport, pytest.raises(Exception):
        live.execute(settings, tmp_path, transport=transport, progress=progress)
    assert seen == ["/v1/chat/completions"]
    assert progress["model_call_reservations"] == 1
    assert progress["model_failure_receipts"] == (None if receipt_read_fails else [])


def test_reviewed_scenarios_and_consumer_preserve_isolation(tmp_path):
    from workbench.capability_consumer import prepare_consumer
    from workbench.capability_dependencies import readonly_start_command
    from workbench.generator import generate_basic

    selected = live.acceptance_design()
    plan = selected.implementation
    assert len(plan.tasks) == 2
    assert all(t.executor == "mini_swe" and t.max_steps == 8 for t in plan.tasks)
    assert plan.selection.template == "python-basic" and plan.selection.database == "sqlite"
    for scenario in plan.scenarios:
        assert any(s.status == 401 for s in scenario.steps)
        assert any(s.body.get("status") == "resolved" for s in scenario.steps if s.body)
        assert any(s.body.get("due_at", "").startswith("2099") for s in scenario.steps if s.body)
        assert any(s.equals.get("$.overdue") == 0 for s in scenario.after_restart)
    generate_basic(selected.baseline, tmp_path / "product", plan.selection.model_dump())
    prepare_consumer(tmp_path / "product", plan)
    assert readonly_start_command(plan).argv[3] == "app:app"


def test_missing_isolation_stops_before_any_model_or_worker(settings, tmp_path, monkeypatch):
    import workbench.capability_execution as admission
    import workbench.coding.mini_swe as controller

    monkeypatch.setattr(controller, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(controller, "run_agent", lambda *a: pytest.fail("agent started"))

    def reject(*args):
        raise ValueError("missing same-job security proof")

    monkeypatch.setattr(admission, "capability_execution_prerequisites", reject)
    with pytest.raises(ValueError, match="same-job"):
        live.execute(settings, tmp_path)


@pytest.mark.parametrize("reject_proof", [False, True])
def test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip(
    settings, tmp_path, monkeypatch, reject_proof
):
    import workbench.capability_consumer as consumer
    import workbench.capability_execution as admission
    import workbench.capability_sandbox as verifier
    import workbench.coding.mini_swe as controller
    import workbench.production.candidates as ledger
    from workbench.planning.contracts import CapabilityEdits

    monkeypatch.setattr(controller, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(admission, "capability_execution_prerequisites", lambda *a: None)
    seen = []

    def mock_agent(settings, gateway, run_id, task, plan, product, workspace, context):
        gateway.store.reserve_model_call(run_id)
        sources = authored_files(task, (product / "app.py").read_text())
        write_json(
            workspace / "agent-budget.json", {"tokens_reserved": 1, "cost_reserved_usd": 0.1}
        )
        return CapabilityEdits(
            explanation="explicit offline fixture",
            files=[
                {"path": name, "before_sha256": manifest(product).get(name), "content": content}
                for name, content in sources.items()
            ],
        )

    def mock_verify(product, plan, scenarios, settings, *, aggregate, selection):
        seen.append((product.name, aggregate))
        return {
            "passed": not reject_proof,
            "cleanup": "deleted",
            "plan_digest": digest(plan.model_dump()),
            "source_digest": digest(manifest(product)),
        }

    def mock_require(proof, **kwargs):
        # Testing sequencing only; never substitutes for real require_evidence in the CLI.
        if not proof["passed"]:
            raise ValueError("independent rejection")

    monkeypatch.setattr(controller, "run_agent", mock_agent)
    monkeypatch.setattr(verifier, "verify_capabilities", mock_verify)
    monkeypatch.setattr(ledger, "require_evidence", mock_require)
    consumers = []
    monkeypatch.setattr(
        consumer, "require_consumer_evidence", lambda *a: consumers.append(a[0].name)
    )
    if reject_proof:
        with pytest.raises(ValueError, match="independent rejection"):
            live.execute(settings, tmp_path)
        assert json.loads((tmp_path / "ledger/current.json").read_text())["version"] == 0
        assert not (tmp_path / "delivery.zip").exists()
    else:
        result = live.execute(settings, tmp_path)
        assert result["real_model_calls"] == 2  # Simulated Store reservations, NOT real calls.
        assert seen == [
            ("sla-api-candidate", False),
            ("sla-dashboard-candidate", False),
            ("fresh-consumer", True),
        ]
        assert consumers == ["fresh-consumer"]
        assert result["full_workflow_crash_recovery"] is False


def test_workflow_only_exposes_key_after_preflight_and_real_security():
    workflow = yaml.safe_load((live.ROOT / ".github/workflows/real-model.yml").read_text())
    job = workflow["jobs"]["mini-swe-sla"]
    assert job["environment"] == "rnd" and job["timeout-minutes"] == 90
    assert "workflow_dispatch" in job["if"] and "run_attempt == 1" in job["if"]
    steps = job["steps"]
    commands = [s.get("run", "") for s in steps]
    preflight = commands.index("uv run python -m scripts.ci_live_modules --preflight")
    security = commands.index("uv run python -m scripts.ci_capability_security")
    paid = commands.index("uv run python -m scripts.ci_live_modules")
    assert preflight < security < paid
    assert "API_KEY" not in job["env"]
    assert [i for i, s in enumerate(steps) if "API_KEY" in s.get("env", {})] == [paid]
    assert "ALLOW_INSECURE_MODEL_HTTP" not in json.dumps(job)
    assert workflow["permissions"] == {"contents": "read"}


def test_model_receipts_are_bounded_and_drop_all_unapproved_fields():
    poison = {
        "status": "failed",
        "code": "private-provider-code",
        "attempt": True,
        "transport_kind": "private-kind",
        "endpoint": "private-url",
        "model": "private-model",
        "diagnostic": {"details": [{"path": ["private-path"], "message": "private-message"}]},
        "headers": {"Authorization": "private-key"},
        "prompt": "private-prompt",
    }
    records = [
        poison,
        {**poison, "code": "transport_error", "attempt": 2},
        {**poison, "code": "http_429", "attempt": 1},
        {**poison, "code": "http_999", "attempt": 900},
        {**poison, "status": "validated"},
    ]
    assert live.model_failure_receipts(records) == [
        {"code": "other", "attempt": None},
        {"code": "transport_error", "attempt": 2, "transport_kind": "other"},
        {"code": "http_429", "attempt": 1},
        {"code": "other", "attempt": None},
    ]
    result = live.model_failure_receipts(records * 20)
    assert len(result) == live.MODEL_CALLS
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("status", [True, -1, 99, 600, "200", None, 200])
def test_json_response_facts_reject_poison_and_preserve_legacy_receipts(status):
    facts = {
        "phase": "private-stage",
        "finish_reason": "private-finish",
        "http_status": status,
        "body": "private-source-key",
        "headers": {"Authorization": "private-secret"},
    }
    base = {"status": "failed", "code": "invalid_json", "attempt": 2}
    result = live.model_failure_receipts(
        [
            base,
            {**base, "response_facts": facts},
            {**base, "code": "schema_validation", "response_facts": facts},
            {**base, "response_facts": [facts]},
        ]
    )
    safe = {"phase": "unknown", "finish_reason": "unknown"}
    if type(status) is int and status == 200:
        safe["http_status"] = status
    assert result == [
        {"code": "invalid_json", "attempt": 2},
        {"code": "invalid_json", "attempt": 2, "response_facts": safe},
        {"code": "schema_validation", "attempt": 2},
        {"code": "invalid_json", "attempt": 2},
    ]
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    ("content", "category"),
    [
        ('{"private-key": }', "expected_value"),
        ("{} private-tail", "extra_data"),
        ("{}}", "extra_closing_delimiters"),
        ('{"private-key":1,"private-key":2}', "duplicate_json_key"),
        ('{"private-key":NaN}', "non_finite_json_number"),
    ],
)
def test_real_json_diagnostic_reaches_safe_receipt(content, category):
    from workbench.model_diagnostics import json_diagnostics
    from workbench.model_protocol import load_json

    with pytest.raises(ValueError) as failure:
        load_json(content)
    details = json_diagnostics(failure.value, content)
    facts = {
        "category": category,
        "lengths": {"characters": len(content), "bytes": len(content.encode())},
    }
    if isinstance(failure.value, json.JSONDecodeError):
        facts["position"] = {
            "line": failure.value.lineno,
            "column": failure.value.colno,
            "offset": failure.value.pos,
        }
    assert live.model_failure_receipts(
        [
            {
                "status": "failed",
                "code": "invalid_json",
                "attempt": 1,
                "diagnostic": {"details": details},
            }
        ]
    ) == [{"code": "invalid_json", "attempt": 1, "json_facts": facts}]


@pytest.mark.parametrize(
    "number",
    [True, False, -1, 0, 1, 2_000_000, 2_000_001, 2_000_002, 10**100, 1.0, "1", None, [], {}],
)
def test_json_fact_numbers_are_bounded_and_poison_is_dropped(number):
    detail = {
        "category": "expected_value",
        "type": "private-type",
        "position": {
            "line": number,
            "column": number,
            "offset": number,
            "private-field": "private-source",
        },
        "lengths": {"characters": number, "bytes": number, "private-size": 4},
        "message": "private-message",
        "path": ["private-key"],
        "body": "private-body",
        "snippet": "private-snippet",
    }
    facts = {"category": "expected_value"}
    position = {}
    if type(number) is int and 1 <= number <= 2_000_001:
        position.update(line=number, column=number)
    if type(number) is int and 0 <= number <= 2_000_000:
        position["offset"] = number
        facts["lengths"] = {"characters": number, "bytes": number}
    if position:
        facts["position"] = position
    result = live.model_failure_receipts(
        [
            {
                "status": "failed",
                "code": "invalid_json",
                "attempt": 1,
                "diagnostic": {"details": [detail], "private-extra": "private-value"},
            }
        ]
    )
    assert result == [{"code": "invalid_json", "attempt": 1, "json_facts": facts}]
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "details",
    [
        None,
        {},
        "private",
        [],
        [None],
        [[], {}],
        [{"category": "private-category"}],
        [{"category": []}],
        [{"category": True}],
        [{"category": "langchain_structured_output_parsing_failed"}],
        [{"category": "expected_value"}, {"category": "extra_data"}],
    ],
)
def test_invalid_json_fact_shapes_preserve_legacy_receipt(details):
    assert live.model_failure_receipts(
        [
            {
                "status": "failed",
                "code": "invalid_json",
                "attempt": 2,
                "diagnostic": {"details": details},
            }
        ]
    ) == [{"code": "invalid_json", "attempt": 2}]


@pytest.mark.parametrize(
    "code", ["schema_validation", "structured_parser_disagreement", "empty_content", "truncated"]
)
def test_json_facts_are_only_exported_for_invalid_json(code):
    assert live.model_failure_receipts(
        [
            {
                "status": "failed",
                "code": code,
                "attempt": 1,
                "diagnostic": {"details": [{"category": "expected_value"}]},
            }
        ]
    ) == [{"code": code, "attempt": 1}]


def test_node_failure_reaches_final_artifact_after_workspace_deletion(tmp_path, monkeypatch):
    from workbench.capability_diagnostics import record_failure
    from workbench.generator import PrerequisiteError

    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules"])
    monkeypatch.setattr(live, "live_settings", lambda *a: None)
    directories = []

    def execute(settings, directory, *, progress, **kwargs):
        directories.append(directory)
        product = directory / "node"
        path = directory / "node-node-verification.json"
        write_json(
            path,
            {
                "passed": False,
                "cleanup": "deleted",
                "checks": ["private-source"],
                "error": "private-key-prompt",
                "sandbox_name": "private-path",
                "startup_diagnostic": {
                    "phase": "health_deadline",
                    "http_status": 502,
                    "command_exit_code": 1,
                    "command_exit_status": "nonzero",
                    "output_hints": ["missing-module", "private-module"],
                    "raw_output": "private",
                },
            },
        )

        def reject(*args, **kwargs):
            try:
                raise ValueError("private-headers-response")
            except ValueError as exc:
                record_failure(path, exc)
                raise PrerequisiteError("private-child-message") from None

        return live.verify_with_diagnostics(reject, product, aggregate=False, progress=progress)

    monkeypatch.setattr(live, "execute", execute)
    with pytest.raises(SystemExit) as error:
        live.main()
    assert error.value.code == 1
    assert all(not path.exists() for path in directories)
    raw = live.REPORT.read_text()
    report = json.loads(raw)
    assert report["passed"] is report["real_model_acceptance"] is False
    assert report["failure_diagnostic"]["exception_type"] == "PrerequisiteError"
    node = report["verification_receipts"][0]
    assert node["exception_type"] == "ValueError"
    assert node["cleanup"] == "deleted" and node["checks_count"] == 1
    assert node["startup"]["http_status"] == 502
    assert node["startup"]["command_exit_code"] == 1
    assert node["startup"]["output_hints"] == ["missing-module"]
    assert "private" not in raw


def test_node_diagnostic_read_failure_preserves_original_oracle_error(monkeypatch, tmp_path):
    import workbench.capability_diagnostics as diagnostics

    def unavailable(*args, **kwargs):
        raise OSError("private-path")

    monkeypatch.setattr(diagnostics, "node_diagnostic", unavailable)
    original = ValueError("original independent rejection")

    def reject(*args, **kwargs):
        raise original

    progress = {}
    with pytest.raises(ValueError) as error:
        live.verify_with_diagnostics(reject, tmp_path / "node", aggregate=False, progress=progress)
    assert error.value is original
    assert progress["verification_diagnostic_unavailable"] is True
