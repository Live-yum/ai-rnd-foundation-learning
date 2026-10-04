"""Bounded OOM diagnostics preserve rejection; mocked transport is not live proof."""

import json
import subprocess
from types import SimpleNamespace

import pytest

from scripts import ci_capability_browser_isolation as probe


def test_memory_diagnostics_never_release_raw_errors_output_or_unknown_state():
    result = probe.memory_probe_diagnostic(
        SimpleNamespace(returncode=2**100, stdout=b"secret stdout", stderr=b"secret stderr"),
        {
            "Status": "secret status",
            "Running": 0,
            "OOMKilled": 1,
            "ExitCode": True,
            "Dead": "secret",
            "Restarting": [],
            "Error": "secret Docker path and credentials",
            "Env": ["secret"],
        },
    )
    assert result == {
        "phase": "memory_exhaustion",
        "timed_out": False,
        "inspection_failed": False,
        "docker_start_returncode": None,
        "container_status": "other",
        "container_running": None,
        "container_oom_killed": None,
        "container_exit_code": None,
        "container_dead": None,
        "container_restarting": None,
        "container_error_present": True,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 512


@pytest.mark.parametrize("state", [None, [], "secret", 1, True])
def test_malformed_memory_state_can_only_produce_empty_finite_facts(state):
    result = probe.memory_probe_diagnostic(None, state)
    assert result["container_status"] == "other"
    assert result["container_oom_killed"] is None
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "case,oom,running,exit_code",
    [
        ("genuine_oom", True, False, 137),
        ("node_abort", False, False, 134),
        ("unproven_sigkill", False, False, 137),
        ("still_running", True, True, 137),
        ("start_failure", False, False, 125),
        ("timeout", False, True, 0),
        ("inspect_failure", False, False, 0),
        ("malformed_state", False, False, 0),
    ],
)
def test_oom_gate_preserves_original_proof_budget_and_cleanup(
    monkeypatch, tmp_path, case, oom, running, exit_code
):
    image = "sha256:" + "a" * 64
    operations = []
    inspections = 0
    state = {
        "Status": "running" if running else "exited",
        "Running": running,
        "OOMKilled": oom,
        "ExitCode": exit_code,
        "Error": "secret internal runtime path",
        "Dead": False,
        "Restarting": False,
    }
    server = SimpleNamespace(
        server_port=1234,
        serve_forever=lambda: None,
        shutdown=lambda: operations.append("server_shutdown"),
        server_close=lambda: operations.append("server_close"),
    )
    monkeypatch.setattr(probe, "ROOT", tmp_path)
    monkeypatch.setattr(probe, "browser_image_identity", lambda: image)
    monkeypatch.setattr(probe, "browser_source_identity", lambda: {})
    monkeypatch.setattr(probe, "runtime_identity", lambda image: {})
    monkeypatch.setattr(probe, "selected_policy", lambda: None)
    monkeypatch.setattr(probe, "require_image_sources", lambda name: {})
    monkeypatch.setattr(probe, "require_worker_inspection", lambda *args: None)
    monkeypatch.setattr(probe, "worker_command", lambda image, name: ["docker", "create", image])
    monkeypatch.setattr(probe, "ThreadingHTTPServer", lambda *args: server)
    monkeypatch.setattr(
        probe.threading, "Thread", lambda **kwargs: SimpleNamespace(start=lambda: None)
    )

    def run(args, timeout=30):
        nonlocal inspections
        if "inspect" in args:
            inspections += 1
            if inspections == 3 and case == "inspect_failure":
                raise RuntimeError("secret inspection failure")
            value = [] if case == "malformed_state" else state
            return json.dumps([{"State": value}]).encode()
        if "start" in args:
            return b"{}"
        return b""

    def process(args, **kwargs):
        if "start" in args:
            operations.append("memory_start")
            assert kwargs["timeout"] == 30
            if case == "timeout":
                raise subprocess.TimeoutExpired(args, 30, output=b"secret output")
            return SimpleNamespace(returncode=exit_code, stdout=b"secret", stderr=b"secret")
        assert "rm" in args and "-f" in args
        operations.append("final_cleanup")
        assert kwargs["timeout"] == 15
        return SimpleNamespace(returncode=0)

    def browser(url, token, scenarios, *args):
        mode = scenarios[0].id
        if mode == "positive":
            return [True]
        diagnostic = (
            {"error_code": "application-error"}
            if mode == "error"
            else {"error_type": "TimeoutError"}
        )
        raise probe.BrowserFailure(diagnostic)

    monkeypatch.setattr(probe, "run", run)
    monkeypatch.setattr(probe.subprocess, "run", process)
    monkeypatch.setattr(probe, "run_isolated_browser", browser)
    if case == "genuine_oom":
        probe.main()
    else:
        with pytest.raises((RuntimeError, ValueError, subprocess.TimeoutExpired)):
            probe.main()
    report = json.loads((tmp_path / "reports/capability-browser-isolation.json").read_bytes())
    assert report["passed"] is (case == "genuine_oom")
    assert report["checks"].get("memory_exhaustion") is (True if case == "genuine_oom" else None)
    assert operations == ["memory_start", "final_cleanup", "server_shutdown", "server_close"]
    assert "secret" not in json.dumps(report)
    if case != "genuine_oom":
        assert report["diagnostic"]["timed_out"] is (case == "timeout")
        assert report["diagnostic"]["inspection_failed"] is (
            case in {"inspect_failure", "malformed_state"}
        )
