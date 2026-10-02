"""No privileges or system policy changes: restrict only a disposable child."""

import json
import subprocess
import sys

from workbench.settings import ROOT


def test_network_guard_cannot_silently_fall_back(tmp_path):
    marker = tmp_path / "executed"
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            str(ROOT / "scripts/capability_guard.py"),
            "",
            "2280",
            "--",
            sys.executable,
            "-c",
            f"open({str(marker)!r}, 'w').write('unsafe')",
        ],
        capture_output=True,
        timeout=15,
    )
    assert process.returncode == 78
    assert not marker.exists()


def test_supported_kernel_restricts_real_daemon_port_or_fails_closed():
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            str(ROOT / "scripts/capability_guard.py"),
            "8123",
            "",
            "--probe",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if process.returncode == 78:
        assert process.stdout == ""
        assert "no product command was executed" in process.stderr
    else:
        assert process.returncode == 0
        result = json.loads(process.stdout)
        assert result["landlock_abi"] >= 6
        assert result["daemon_tcp_denied"] and result["no_new_privs"]
