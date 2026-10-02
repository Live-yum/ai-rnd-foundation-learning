"""Verify every source command is composed through the same non-bypassable launcher."""

import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from workbench.capability_isolation import IsolationUnavailable, product_argv


@pytest.mark.parametrize("database", ["sqlite", "postgresql"])
def test_generated_prepare_and_start_cannot_bypass_identity_or_network_guard(database):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=8123), selection=SimpleNamespace(database=database)
    )
    command = ["/bin/sh", "-c", "sudo -n id; curl http://127.0.0.1:2280/process/execute"]
    result = product_argv(plan, command, {"DATABASE_URL": "synthetic-only"})
    assert result[:2] == ["/usr/bin/env", "-i"]
    assert "--reuid=rnd-module" in result and "--regid=rnd-module" in result
    session = result.index("/usr/bin/setsid")
    assert result[session : session + 4] == [
        "/usr/bin/setsid",
        "--fork",
        "--wait",
        "/usr/bin/setpriv",
    ]
    for flag in (
        "--clear-groups",
        "--no-new-privs",
        "--bounding-set=-all",
        "--inh-caps=-all",
        "--ambient-caps=-all",
    ):
        assert flag in result
    index = result.index("/usr/bin/python3")
    assert result[index : index + 6] == [
        "/usr/bin/python3",
        "-I",
        "-S",
        "/tmp/rnd-module-control/guard.py",
        "8123",
        "55432" if database == "postgresql" else "",
    ]
    assert result[-len(command) :] == command
    assert result.index("--") < index
    assert result[index + 6] == "--"


@pytest.mark.parametrize("port", [2280, 55432])
def test_product_cannot_allow_its_control_or_database_listener(port):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=port), selection=SimpleNamespace(database="sqlite")
    )
    with pytest.raises(IsolationUnavailable):
        product_argv(plan, ["echo", "should-not-run"], {})


def test_isolation_receipt_requires_each_field_actual_abi_and_current_guard_digest():
    from workbench.capability_isolation import (
        APP_UID,
        ISOLATION_FLAGS,
        ISOLATION_PROFILE,
        require_isolation_evidence,
    )
    from workbench.filesystem import sha
    from workbench.settings import ROOT

    value = {
        "profile": ISOLATION_PROFILE,
        "application_uid": APP_UID,
        "landlock_abi": 6,
        "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
        **dict.fromkeys(ISOLATION_FLAGS, True),
    }
    assert require_isolation_evidence(value) == value
    for key in list(value):
        missing = {k: v for k, v in value.items() if k != key}
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence(missing)
    for invalid in [True, 5, "6"]:
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence({**value, "landlock_abi": invalid})
    with pytest.raises(IsolationUnavailable):
        require_isolation_evidence({**value, "guard_sha256": "0" * 64})


@pytest.mark.skipif(os.name != "posix", reason="Linux executor profile uses util-linux setsid")
@pytest.mark.parametrize("exit_code", [0, 7])
def test_detached_session_waits_for_ordinary_command_and_preserves_exit(tmp_path, exit_code):
    completed = tmp_path / "completed.txt"
    result = subprocess.run(
        [
            "/usr/bin/setsid",
            "--fork",
            "--wait",
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import pathlib,sys,time;time.sleep(0.05);pathlib.Path(sys.argv[1]).write_text('completed',encoding='utf-8');raise SystemExit(int(sys.argv[2]))",
            str(completed),
            str(exit_code),
        ],
        capture_output=True,
        timeout=5,
        start_new_session=True,
    )
    assert result.returncode == exit_code
    assert completed.read_text(encoding="utf-8") == "completed"
