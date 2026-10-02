"""Optional, bounded startup diagnostics for one owned local sandbox before deletion.

Never enumerate containers, dump environment variables, alter the failed sandbox,
change network settings, or turn failed creation into successful acceptance.
"""

import json
import re
import time
import uuid

from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command

MAX_CHARS = 8192
TOTAL_SECONDS = 15
STATE_FORMAT = (
    '{"Status":{{json .State.Status}},"Running":{{json .State.Running}},'
    '"OOMKilled":{{json .State.OOMKilled}},"ExitCode":{{json .State.ExitCode}},'
    '"Error":{{json .State.Error}},"StartedAt":{{json .State.StartedAt}},'
    '"FinishedAt":{{json .State.FinishedAt}},"RestartCount":{{json .RestartCount}}}'
)


def capture_startup(sandbox_id, sandbox_name, settings):
    """Only called after SDK lookup by this attempt's unpredictable exact name."""
    from scripts.daytona_local import HOME, PROJECT

    if str(uuid.UUID(sandbox_id)) != sandbox_id or not re.fullmatch(
        r"rnd-verify-[0-9a-f]{32}", sandbox_name
    ):
        raise ValueError("Startup diagnostics require the exact owned sandbox UUID and name")
    compose = HOME / "compose.lock.yaml"
    report = {
        "sandbox_id": sandbox_id,
        "sandbox_name": sandbox_name,
        "scope": "exact-owned-local-sandbox",
        "passed": False,
        "affects_acceptance": False,
        "diagnostics": {},
    }
    if not compose.is_file() or compose.is_symlink():
        return {**report, "status": "fixed-local-compose-unavailable"}
    secrets = []
    for filename in ("credentials.json", "api-key.json"):
        path = HOME / filename
        if path.is_file() and not path.is_symlink() and path.stat().st_size <= 16384:
            try:
                values = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(values, dict):
                    secrets.extend(v for v in values.values() if isinstance(v, str) and len(v) > 5)
            except OSError, UnicodeError, json.JSONDecodeError:
                pass

    def redact(text):
        text = settings.redact(text)
        for secret in sorted(secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(r"(?i)(bearer\s+)[^\s\"']+", r"\1[REDACTED]", text)
        text = re.sub(
            r"(?i)((?:[\"']?)(?:password|api[_-]?key|auth[_-]?token|access[_-]?token|token|authorization|secret)(?:[\"']?)\s*[=:]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
            r"\1[REDACTED]",
            text,
        )
        text = re.sub(r"(://[^/@:\s]+:)[^@\s]+@", r"\1[REDACTED]@", text)
        return text[-MAX_CHARS:]

    # run_command pins the outer Docker CLI to this machine's local socket.
    # Compose exec must also pin the inner CLI to the runner's own DinD socket;
    # explicit fixed values override its environment without a shell or a remote
    # context. Do not pass --host through the generic command policy.
    prefix = [
        "docker",
        "compose",
        "-p",
        PROJECT,
        "-f",
        str(compose),
        "exec",
        "-T",
        "-e",
        "DOCKER_HOST=unix:///var/run/docker.sock",
        "-e",
        "DOCKER_CONTEXT=",
        "-e",
        "DOCKER_TLS=",
        "-e",
        "DOCKER_TLS_VERIFY=",
        "-e",
        "DOCKER_CERT_PATH=",
        "runner",
        "docker",
    ]
    commands = {
        "state": ["inspect", "--format", STATE_FORMAT, sandbox_id],
        "daemon_stdout": ["logs", "--tail", "80", sandbox_id],
        "daemon_file": [
            "exec",
            sandbox_id,
            "tail",
            "--bytes=" + str(MAX_CHARS),
            "/tmp/daytona-daemon.log",
        ],
    }
    deadline = time.monotonic() + TOTAL_SECONDS
    for label, argv in commands.items():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            report["diagnostics"][label] = {"status": "diagnostic-budget-exhausted"}
            continue
        try:
            result = run_command(prefix + argv, ROOT, timeout=min(5, remaining))
            report["diagnostics"][label] = {"status": "captured", "text": redact(result["log"])}
        except ToolFailure as exc:
            report["diagnostics"][label] = {
                "status": "unavailable",
                "error_type": type(exc).__name__,
                "text": redact(getattr(exc, "log", "")),
            }
        except Exception as exc:
            # Do not serialize unexpected exception messages that may contain secrets.
            report["diagnostics"][label] = {
                "status": "unavailable",
                "error_type": type(exc).__name__,
            }
    return {**report, "status": "collected-before-delete"}
