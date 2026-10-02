"""Bounded clean-room suite orchestration, not a substitute for the full suite."""

import inspect
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ci_handbook


def test_only_full_suite_has_the_expanded_explicit_budget():
    assert ci_handbook.FULL_SUITE_TIMEOUT == 1800
    assert inspect.signature(ci_handbook.run_full_tests).parameters["timeout"].default == 1800
    assert inspect.signature(ci_handbook.run).parameters["timeout"].default == 900
    workflow = (ci_handbook.ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
    section = workflow.split("  handbook-only:", 1)[1].split("  browser:", 1)[0]
    assert "timeout-minutes: 40" in section
    assert "reports/handbook-test-status.json" in section
    assert "timeout-minutes: ${{ matrix.os == 'windows-latest' && 60 || 35 }}" in workflow


@pytest.mark.parametrize("code", [0, 3])
def test_completed_child_preserves_xml_and_exact_exit_status(tmp_path, code):
    junit, reports = tmp_path / "student.xml", tmp_path / "reports"
    body = "<testsuites><testsuite><testcase name='unit-only'/></testsuite></testsuites>"
    argv = [
        sys.executable,
        "-c",
        "from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2], encoding='utf-8'); sys.exit(int(sys.argv[3]))",
        str(junit),
        body,
        str(code),
    ]
    if code:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            ci_handbook.run_full_tests(argv, tmp_path, dict(os.environ), junit, reports, timeout=10)
        assert failure.value.returncode == code
    else:
        ci_handbook.run_full_tests(argv, tmp_path, dict(os.environ), junit, reports, timeout=10)
    status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
    assert status["timed_out"] is False and status["returncode"] == code
    assert status["junit_available"] is True
    assert (reports / "handbook-tests.xml").read_text(encoding="utf-8") == body


@pytest.mark.parametrize("exit_during_grace", [True, False])
def test_deadline_remains_failure_even_when_interrupt_writes_success_xml(
    tmp_path, monkeypatch, exit_during_grace
):
    junit, reports = tmp_path / "student.xml", tmp_path / "reports"
    waits, signals, stopped, cleaned = [], [], [], []
    process = SimpleNamespace(pid=321, returncode=None)

    def wait(*, timeout):
        waits.append(timeout)
        if len(waits) == 2 and exit_during_grace:
            junit.write_text("<testsuites/>", encoding="utf-8")
            process.returncode = 0
            return 0
        raise subprocess.TimeoutExpired("unit-owned-pytest", timeout)

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        owned.returncode = -9

    process.wait = wait
    process.send_signal = signals.append
    process.poll = lambda: process.returncode
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    monkeypatch.setattr(
        ci_handbook, "capture_owned_descendants", lambda _: {321: "parent", 322: "child"}
    )
    monkeypatch.setattr(
        ci_handbook, "cleanup_owned_descendants", lambda owned: cleaned.append(owned)
    )
    with pytest.raises(subprocess.TimeoutExpired) as failure:
        ci_handbook.run_full_tests(["unit-only"], tmp_path, {}, junit, reports)
    assert failure.value.timeout == 1800
    assert waits == [1800, 15] and len(signals) == 1
    assert stopped == ([] if exit_during_grace else [321])
    assert cleaned == [{321: "parent", 322: "child"}]
    status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
    assert status["timed_out"] is True and status["timeout_seconds"] == 1800
    assert status["junit_available"] is exit_during_grace


def test_timeout_receipt_survives_owned_cleanup_failure(tmp_path, monkeypatch):
    def wait(**kwargs):
        raise subprocess.TimeoutExpired("unit-owned-pytest", kwargs["timeout"])

    process = SimpleNamespace(
        returncode=None, wait=wait, poll=lambda: None, send_signal=lambda _: None
    )
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "capture_owned_descendants", lambda _: {321: "owned"})
    monkeypatch.setattr(ci_handbook, "cleanup_owned_descendants", lambda _: None)

    def stop(_):
        raise RuntimeError("owned cleanup canary")

    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    with pytest.raises(subprocess.TimeoutExpired):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    status = json.loads(
        (tmp_path / "reports/handbook-test-status.json").read_text(encoding="utf-8")
    )
    assert status["timed_out"] is True and status["cleanup_error_type"] == "RuntimeError"
    assert status["junit_available"] is False


def test_launch_failure_is_retained_without_claiming_tests_ran(tmp_path, monkeypatch):
    def launch(*args, **kwargs):
        raise OSError("unit launch canary")

    monkeypatch.setattr(ci_handbook.subprocess, "Popen", launch)
    with pytest.raises(OSError, match="unit launch canary"):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    status = json.loads(
        (tmp_path / "reports/handbook-test-status.json").read_text(encoding="utf-8")
    )
    assert status["error_type"] == "OSError" and status["returncode"] is None
    assert status["junit_available"] is False and status["timed_out"] is False


def test_grace_exit_cleans_proven_surviving_child_not_foreign_or_recycled_pid(monkeypatch):
    identities = {321: None, 322: (1, "child"), 323: (1, "recycled"), 999: (1, "foreign")}
    killed = []
    # This is a POSIX ownership simulation even when the test host is Windows.
    monkeypatch.setattr(ci_handbook, "signal", SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(ci_handbook, "process_identity", identities.get)
    monkeypatch.setattr(ci_handbook.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    ci_handbook.cleanup_owned_descendants({321: "parent", 322: "child", 323: "old-child"})
    assert killed == [(322, ci_handbook.signal.SIGKILL)]


def test_no_snapshot_stops_live_owned_tree_without_grace_or_expired_pid_lookup(
    tmp_path, monkeypatch
):
    process = SimpleNamespace(pid=321, returncode=None)
    waits, stopped = [], []

    def wait(*, timeout):
        waits.append(timeout)
        raise subprocess.TimeoutExpired("unit-owned-pytest", timeout)

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        owned.returncode = -9

    process.wait, process.poll = wait, lambda: process.returncode
    process.send_signal = lambda _: pytest.fail("No unverifiable grace-period cleanup")
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "capture_owned_descendants", lambda _: None)
    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    with pytest.raises(subprocess.TimeoutExpired):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    assert waits == [1800] and stopped == [321]


@pytest.mark.skipif(
    os.name == "nt" or not Path("/proc").is_dir(), reason="Linux process identity integration"
)
def test_real_grace_exit_cleans_detached_owned_child_and_preserves_foreign_process(tmp_path):
    junit, child_file, reports = (
        tmp_path / "student.xml",
        tmp_path / "child.pid",
        tmp_path / "reports",
    )
    script = """
import json, signal, subprocess, sys, time
from pathlib import Path
def interrupt(*_):
    Path(sys.argv[1]).write_text('<testsuites/>', encoding='utf-8')
    raise SystemExit(0)
signal.signal(signal.SIGINT, interrupt)
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
started = Path(f'/proc/{child.pid}/stat').read_text(encoding='utf-8').rsplit(') ', 1)[1].split()[19]
Path(sys.argv[2]).write_text(json.dumps({'pid': child.pid, 'started': started}), encoding='utf-8')
time.sleep(30)
"""
    foreign = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            ci_handbook.run_full_tests(
                [sys.executable, "-c", script, str(junit), str(child_file)],
                tmp_path,
                dict(os.environ),
                junit,
                reports,
                timeout=2,
            )
        owned_child = json.loads(child_file.read_text(encoding="utf-8"))
        child = owned_child["pid"]
        for _ in range(50):
            path = Path(f"/proc/{child}/stat")
            try:
                fields = path.read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
            except FileNotFoundError, ProcessLookupError:
                # Exit/reaping can occur during read(), not only before exists().
                break
            if fields[0] == "Z" or fields[19] != owned_child["started"]:
                break
            time.sleep(0.02)
        else:
            pytest.fail("Proven detached child survived the exited leader")
        assert foreign.poll() is None
        status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
        assert status["timed_out"] is True and status["returncode"] == 0
        assert status["junit_available"] is True and status["owned_processes_at_timeout"] >= 2
    finally:
        if child_file.is_file():
            owned = json.loads(child_file.read_text(encoding="utf-8"))
            current = ci_handbook.process_identity(owned["pid"])
            if current is not None and current[1] == owned["started"]:
                try:
                    os.kill(owned["pid"], ci_handbook.signal.SIGKILL)
                except ProcessLookupError:
                    pass
        foreign.terminate()
        foreign.wait(timeout=3)
