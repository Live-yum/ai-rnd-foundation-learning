"""Startup hints cannot become product acceptance or disclose candidate output."""

import builtins
import importlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import traceback
from io import StringIO
from types import SimpleNamespace

import pytest

from workbench.capability_sandbox import (
    startup_command_exit_facts,
    startup_command_exit_status,
    startup_failure_diagnostic,
)
from workbench.capability_startup_paths import NATIVE_TAIL_LIMIT, node_failure_facts


def test_startup_hints_are_finite_even_for_secret_bearing_tracebacks():
    output = (
        "secret content /private/secret token=secret\n"
        "ModuleNotFoundError: No module named 'secret.module'\n"
        "PermissionError: secret path\nApplication startup complete"
    )
    result = startup_failure_diagnostic(output, 503, "secret transport error")
    assert result == {
        "phase": "health_deadline",
        "http_status": 503,
        "http_error": "other",
        "output_readable": True,
        "output_nonempty": True,
        "output_raw_bytes": len(output.encode()),
        "output_normalized_bytes": len(output.encode()),
        "output_normalized_nonspace": True,
        "output_read_limit_reached": False,
        "output_has_non_sgr_control": False,
        "output_hints": ["permission-denied", "missing-module"],
        "output_shapes": [],
        "known_missing_modules": [],
        "startup_phase_hint": "unknown",
        "failure_component": "unknown",
        "exception_type": "PermissionError",
        "exception_errno": None,
        "application_startup_reported": True,
        "tmpfs_noexec": None,
        "command_exit_status": "unknown",
        "command_exit_code": None,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 1024
    assert "passed" not in result


@pytest.mark.parametrize("output", [None, [], {"secret": "private"}, True])
def test_nontext_startup_output_never_stringifies_candidate_data(output):
    result = startup_failure_diagnostic(output, True, [])
    assert result["output_readable"] is False
    assert result["http_status"] is None
    assert result["http_error"] == "other"
    assert result["output_hints"] == []
    assert result["startup_phase_hint"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    for name in (
        "output_raw_bytes",
        "output_normalized_bytes",
        "output_normalized_nonspace",
        "output_read_limit_reached",
        "output_has_non_sgr_control",
    ):
        assert result[name] is None
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "module", ["uvicorn", "fastapi", "sqlalchemy", "pydantic", "app", "access"]
)
def test_only_exact_public_module_names_can_be_reported(module):
    result = startup_failure_diagnostic(
        "ModuleNotFoundError: No module named '" + module + "'", 502, "none"
    )
    assert result["known_missing_modules"] == [module]
    assert (
        startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"] == []
    )


def test_native_loader_failure_is_not_mislabeled_as_missing_module():
    result = startup_failure_diagnostic(
        "ImportError: /private/secret: failed to map segment from shared object",
        502,
        "none",
        True,
    )
    assert result["output_hints"] == ["import-error", "native-library-mapping"]
    assert result["tmpfs_noexec"] is True
    assert "secret" not in json.dumps(result)
    assert startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None


SEMAPHORE_TRACE = """Traceback (most recent call last):
  File "/private/secret/backend/app/__init__.py", line 146, in create_app
    register_routers(app)
  File "/private/secret/python/concurrent/futures/process.py", line 731, in __init__
    self._call_queue = _SafeQueue(
  File "/private/secret/python/multiprocessing/synchronize.py", line 57, in __init__
    sl = self._semlock = _multiprocessing.SemLock(
PermissionError: [Errno 13] Permission denied: '/private/secret'
"""


def colored(text):
    return "\x1b[31m" + "\x1b[0m\x1b[38;2;1;2;3m".join(text) + "\x1b[0m"


def test_observed_sgr_can_split_exception_words_and_errno():
    output = colored("FileNotFoundError: [Errno 2] No such file or directory")
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["missing-file"]
    assert result["output_shapes"] == ["file-not-found-type", "ansi-control"]


def test_sgr_trace_retains_same_trace_association_with_later_cleanup():
    # Ordinary per-line coloring stays comfortably within the original budget.
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in SEMAPHORE_TRACE.splitlines())
    trace += "\nTraceback (most recent call last):\n" + colored(
        "FileNotFoundError: [Errno 2] secret"
    )
    result = startup_failure_diagnostic(trace, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError" and result["exception_errno"] == 2
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "prefix", ["\x1b[", "\x1b[123", "\x1b[" + "1;" * 10000 + "m", "\x1b]0;private\x07"]
)
def test_incomplete_oversize_and_non_sgr_sequences_are_not_interpreted(prefix):
    result = startup_failure_diagnostic(prefix + "PermissionError: [Errno 13] secret", 502, "none")
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result) and "secret" not in json.dumps(result)


def test_stripped_control_bytes_do_not_create_a_larger_scan_window():
    result = startup_failure_diagnostic(
        "\x1b[0m" * 2000 + "PermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["output_nonempty"] is True
    assert result["exception_type"] == "unknown" and result["output_hints"] == []
    assert result["output_shapes"] == ["ansi-control"]


def test_sgr_from_another_trace_cannot_supply_a_semaphore_denial():
    first = SEMAPHORE_TRACE.replace("PermissionError: [Errno 13]", "FileNotFoundError: [Errno 2]")
    second = "Traceback (most recent call last):\nPermissionError: [Errno 13] secret"
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in (first + second).splitlines())
    assert startup_failure_diagnostic(trace, 502, "none")["failure_component"] == "unknown"


def test_semaphore_failure_requires_known_constructor_frames_and_denial():
    result = startup_failure_diagnostic(SEMAPHORE_TRACE, 502, "none", True)
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["startup_phase_hint"] == "factory"
    assert result["application_startup_reported"] is False
    assert "secret" not in json.dumps(result)
    assert "passed" not in result


@pytest.mark.parametrize(
    "old,new",
    [
        ("concurrent/futures/process.py", "private/secret.py"),
        ("multiprocessing/synchronize.py", "private/secret.py"),
        ("_multiprocessing.SemLock(", "private_constructor("),
        ("in __init__", "in private_constructor"),
        ("PermissionError", "FileNotFoundError"),
        ("[Errno 13]", "[Errno 2]"),
        ("[Errno 13]", "[Errno 9999999999]"),
    ],
)
def test_partial_or_unrelated_trace_does_not_claim_semaphore(old, new):
    result = startup_failure_diagnostic(SEMAPHORE_TRACE.replace(old, new), 502, "none")
    assert result["failure_component"] == "unknown"
    assert "private_constructor" not in json.dumps(result)


@pytest.mark.parametrize("number", [1, 2, 13, 28, 30])
def test_only_fixed_errno_values_are_emitted(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] == number


@pytest.mark.parametrize("number", [0, -1, 5, 42, 9999999999999999999999999999])
def test_unknown_errno_is_not_copied(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] is None
    assert "secret" not in json.dumps(result)


def test_terminal_unknown_error_does_not_hide_complete_earlier_trace():
    result = startup_failure_diagnostic(
        SEMAPHORE_TRACE + "\nprivate.SecretError: [Errno 13] secret\n", 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert "SecretError" not in json.dumps(result)


@pytest.mark.parametrize(
    "separator",
    [
        "\n",
        "\nDuring handling of the above exception, another exception occurred:\n\n",
        "\nThe above exception was the direct cause of the following exception:\n\n",
    ],
)
def test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno(separator):
    output = (
        SEMAPHORE_TRACE
        + separator
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "FileNotFoundError: [Errno 2] No such file or directory: '/private/secret'\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["permission-denied", "missing-file"]
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize("header", ["", "Traceback (most recent call last):\n"])
def test_unrelated_permission_error_cannot_complete_a_constructor_trace(header):
    unrelated = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    result = startup_failure_diagnostic(
        unrelated + "\n" + header + "PermissionError: [Errno 13] private\n", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["failure_component"] == "unknown"


def test_incomplete_traceback_cannot_supply_a_semaphore_hint():
    no_header = SEMAPHORE_TRACE.split("\n", 1)[1]
    no_error = SEMAPHORE_TRACE.split("PermissionError:", 1)[0]
    for output in (no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] private"):
        result = startup_failure_diagnostic(output, 502, "none")
        assert result["failure_component"] == "unknown"


@pytest.mark.parametrize(
    "output,phase",
    [
        ('  File "/secret/uvicorn/importer.py", line 10, in import_from_string\n', "import"),
        (SEMAPHORE_TRACE, "factory"),
        ("INFO:     Waiting for application startup.\n" + SEMAPHORE_TRACE, "lifespan"),
        ("ERROR:    Application startup failed. Exiting.", "lifespan"),
        ("private-phase secret", "unknown"),
    ],
)
def test_startup_phase_is_only_a_fixed_hint(output, phase):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["startup_phase_hint"] == phase
    assert "secret" not in json.dumps(result)


def test_context_outside_the_existing_output_bound_cannot_supply_a_hint():
    result = startup_failure_diagnostic("x" * 8000 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None


def test_tail_traceback_preserves_final_error_without_joining_truncated_primary_trace():
    primary = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    output = (
        primary.split("\n", 1)[1]
        + "\nDuring handling of the above exception, another exception occurred:\n\n"
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "PermissionError: [Errno 13] secret\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


def test_non_ascii_output_has_same_byte_budget_before_any_parsing():
    result = startup_failure_diagnostic("汉" * 2667 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert "汉" not in json.dumps(result, ensure_ascii=False)


def test_split_utf8_and_surrogate_data_never_escape_diagnostic():
    result = startup_failure_diagnostic(
        "\ufffd\udc80secret\nPermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "value,expected",
    [(0, "zero"), (1, "nonzero"), (137, "nonzero"), (255, "nonzero")],
)
def test_pinned_sdk_command_exit_facts_use_status_only(value, expected, monkeypatch):
    import httpx
    from daytona._sync.process import Process
    from daytona_toolbox_api_client.models.command import Command

    from workbench import daytona_sessions

    seen = []
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: 100)
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda *a, **k: seen.append(k["_request_timeout"]),
    )
    daytona_sessions.harden_toolbox_transport(
        SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest))
    )

    def get_command(*, session_id, command_id):
        assert session_id == "private-session" and command_id == "private-command"
        rest.request("GET", "local")
        return Command.from_dict(
            {"id": command_id, "command": "secret TOKEN=secret", "exitCode": value}
        )

    with httpx.Client(trust_env=False) as client:
        process = Process("python", SimpleNamespace(get_session_command=get_command), client)
        assert startup_command_exit_facts(process, "private-session", "private-command", 5) == {
            "command_exit_status": expected,
            "command_exit_code": value,
        }
    assert seen == [5]
    assert daytona_sessions._DEADLINE.get() is None


@pytest.mark.parametrize("exit_present", [False, True])
def test_pinned_sdk_null_or_omitted_exit_never_proves_running(exit_present):
    from daytona_toolbox_api_client.models.command import Command

    payload = {"id": "fixture-command", "command": "secret"}
    if exit_present:
        payload["exitCode"] = None
    command = Command.from_dict(payload)
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [True, False, "1", 1.0])
def test_pinned_sdk_strict_exit_model_rejection_is_safe(value):
    from daytona_toolbox_api_client.models.command import Command
    from pydantic import ValidationError

    def get_command(*args):
        return Command.from_dict({"id": "fixture-command", "command": "secret", "exitCode": value})

    with pytest.raises(ValidationError):
        get_command()
    process = SimpleNamespace(get_session_command=get_command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [None, True, False, "1", 1.0, [], {}, -1, 256, 10**100])
def test_malformed_exit_values_remain_unknown(value):
    process = SimpleNamespace(
        get_session_command=lambda *a: SimpleNamespace(id="fixture-command", exit_code=value)
    )
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize(
    "command",
    [None, SimpleNamespace(), SimpleNamespace(id="other-command", exit_code=1)],
)
def test_missing_or_different_command_remains_unknown(command):
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


def test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline():
    from workbench import daytona_sessions

    def unavailable(*args):
        raise RuntimeError("secret session, command and SDK body")

    token = daytona_sessions._DEADLINE.set(123)
    try:
        for process in (SimpleNamespace(), SimpleNamespace(get_session_command=unavailable)):
            assert (
                startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"
            )
            assert daytona_sessions._DEADLINE.get() == 123
    finally:
        daytona_sessions._DEADLINE.reset(token)


@pytest.mark.parametrize("value", [True, 1, [], {"secret": "secret"}, "running", "secret"])
def test_command_status_classifier_cannot_disclose_arbitrary_values(value):
    result = startup_failure_diagnostic("", 502, "none", command_exit_status=value)
    assert result["command_exit_status"] == "unknown"
    assert "secret" not in json.dumps(result)


def rich_trace(exc, *, panel=False, width=100, legacy_windows=None):
    """Render real Rich 15 tracebacks, including its actual SGR and borders."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.traceback import Traceback

    output = StringIO()
    console = Console(
        file=output,
        width=width,
        force_terminal=True,
        color_system="truecolor",
        no_color=False,
        legacy_windows=legacy_windows,
    )
    try:
        raise exc
    except BaseException as caught:
        rendered = Traceback.from_exception(
            type(caught), caught, caught.__traceback__, show_locals=False, extra_lines=0
        )
        console.print(Panel(rendered) if panel else rendered)
    value = output.getvalue()
    assert "\x1b[" in value
    return value


@pytest.mark.parametrize("panel", [False, True])
@pytest.mark.parametrize(
    "name",
    [
        "TypeError",
        "AttributeError",
        "KeyError",
        "IndexError",
        "NameError",
        "UnboundLocalError",
        "AssertionError",
        "ValueError",
        "RuntimeError",
        "RecursionError",
        "NotImplementedError",
        "ImportError",
        "ModuleNotFoundError",
        "MemoryError",
        "SyntaxError",
        "IndentationError",
        "OSError",
        "FileNotFoundError",
        "PermissionError",
        "TimeoutError",
        "ConnectionRefusedError",
        "ZeroDivisionError",
        "OverflowError",
        "EOFError",
        "StopIteration",
        "SystemExit",
        "KeyboardInterrupt",
        "GeneratorExit",
        "Exception",
        "BaseException",
    ],
)
def test_real_rich_builtin_exception_matrix(name, panel):
    output = rich_trace(getattr(builtins, name)("private-sentinel /private/token"), panel=panel)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == name
    assert result["output_raw_bytes"] == len(output.encode())
    assert result["output_normalized_bytes"] < result["output_raw_bytes"]
    assert result["output_normalized_nonspace"] is True
    assert result["output_has_non_sgr_control"] is False
    assert "ansi-control" in result["output_shapes"]
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
@pytest.mark.parametrize("exc", [AssertionError(), KeyboardInterrupt(), SystemExit()])
def test_real_empty_message_exception_headers(renderer, exc):
    result = startup_failure_diagnostic(renderer(exc), 502, "none")
    assert result["exception_type"] == type(exc).__name__


@pytest.mark.parametrize("width", [80, 100, 120])
@pytest.mark.parametrize("exception", [TypeError, KeyError, SystemExit])
def test_real_rich_panel_padding_preserves_empty_exception_headers(width, exception):
    output = rich_trace(exception(), panel=True, width=width)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == exception.__name__
    assert result["failure_component"] == "unknown"


@pytest.mark.parametrize("width", [80, 100, 120])
def test_real_rich_panel_padding_does_not_publish_unknown_empty_exception(width):
    class PrivateSentinelError(Exception):
        pass

    result = startup_failure_diagnostic(
        rich_trace(PrivateSentinelError(), panel=True, width=width), 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "PrivateSentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "output",
    [
        "TypeError" + " " * 80,
        "│ TypeError" + " " * 80,
        "| TypeError" + " " * 80 + " |",
        "│ TypeError" + " " * 600 + " │",
    ],
)
def test_padding_normalization_requires_complete_bounded_known_panel(output):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "unknown"


@pytest.mark.parametrize("panel", [False, True])
def test_real_rich_chained_trace_preserves_terminal_exception(panel):
    terminal = KeyError("private-terminal")
    terminal.__cause__ = TypeError("private-primary")
    result = startup_failure_diagnostic(rich_trace(terminal, panel=panel), 502, "none")
    assert result["exception_type"] == "KeyError"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("panel", [False, True])
def test_real_rich_unknown_exception_remains_unknown(panel):
    class PrivateSentinelError(Exception):
        pass

    result = startup_failure_diagnostic(
        rich_trace(PrivateSentinelError("private-sentinel"), panel=panel), 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert "PrivateSentinel" not in json.dumps(result)
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "prefix", ["secret.", "prefix ", "│ ", "\x1b]0;private\x07", "\x1b[2J", "\x1b[", " " * 33]
)
def test_unrecognized_prefix_is_not_normalized_into_a_builtin(prefix):
    result = startup_failure_diagnostic(prefix + "TypeError: private", 502, "none")
    assert result["exception_type"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("prefix", ["", "  ", "\t", " " * 32])
def test_bounded_standard_exception_indentation(prefix):
    result = startup_failure_diagnostic(prefix + "TypeError: private", 502, "none")
    assert result["exception_type"] == "TypeError"


def test_rich_wrappers_cannot_complete_a_semaphore_trace():
    first = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    output = first + rich_trace(PermissionError(13, "private-sentinel"), panel=True)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["failure_component"] == "unknown"


@pytest.mark.parametrize("limit", [NATIVE_TAIL_LIMIT, 8000])
@pytest.mark.parametrize("prefix", ["x", "\x1b[0m", "汉", "\x1b]0;secret\x07"])
def test_raw_budget_precedes_sgr_rich_wrappers_and_exception_search(limit, prefix):
    output = prefix * limit + "\n│ TypeError: private │\n"
    result = startup_failure_diagnostic(output, 502, "none", output_limit=limit)
    assert result["output_raw_bytes"] == limit
    assert 0 <= result["output_normalized_bytes"] <= limit
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "output,normalized,nonspace,control",
    [
        ("", "", False, False),
        ("\x1b[0m\x1b[31m", "", False, False),
        ("\x1b[0m \n\t\r", " \n\t\r", False, False),
        ("\x1b[31munmatched私\x1b[0m", "unmatched私", True, False),
        ("\x1b]0;private\x07", "\x1b]0;private\x07", True, True),
        ("\x1b[2J", "\x1b[2J", True, True),
        ("\x1b[", "\x1b[", True, True),
        ("\x00\x08\x7f\x9b", "\x00\x08\x7f\x9b", True, True),
    ],
)
def test_measured_output_facts_do_not_serialize_text(output, normalized, nonspace, control):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["output_raw_bytes"] == len(output.encode())
    assert result["output_normalized_bytes"] == len(normalized.encode())
    assert result["output_normalized_nonspace"] is nonspace
    assert result["output_has_non_sgr_control"] is control
    assert result["output_read_limit_reached"] is False
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("limit", [NATIVE_TAIL_LIMIT, 8000])
@pytest.mark.parametrize("length", [-1, 0, 1])
def test_read_limit_fact_measures_observed_cap_without_claiming_truncation(limit, length):
    result = startup_failure_diagnostic("x" * (limit + length), 502, "none", output_limit=limit)
    assert result["output_read_limit_reached"] is (length >= 0)
    assert result["output_raw_bytes"] == min(limit + length, limit)
    assert "truncated" not in result


@pytest.mark.parametrize("limit", [None, True, "5440", 0, -1, 8001, 10**100])
def test_invalid_read_limit_cannot_expand_existing_budget(limit):
    result = startup_failure_diagnostic(
        "x" * 8000 + "\nTypeError: private", 502, "none", output_limit=limit
    )
    assert result["output_raw_bytes"] == 8000
    assert result["exception_type"] == "unknown"


@pytest.mark.parametrize("code", [0, 1, 2, 127, 137, 255])
def test_exact_exit_code_is_authoritative_and_finite(code):
    result = startup_failure_diagnostic(
        "", 502, "none", command_exit_status="unknown", command_exit_code=code
    )
    assert result["command_exit_code"] == code
    assert result["command_exit_status"] == ("zero" if code == 0 else "nonzero")


@pytest.mark.parametrize("code", [None, True, False, "1", 1.0, [], {}, -1, 256, 10**100])
def test_invalid_exit_code_is_never_serialized(code):
    result = startup_failure_diagnostic("", 502, "none", command_exit_code=code)
    assert result["command_exit_code"] is None
    assert result["command_exit_status"] == "unknown"


def test_owned_argparse_fixture_reports_real_exit_two_without_exception():
    # This owned stdlib fixture executes no candidate code or application imports.
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import argparse; argparse.ArgumentParser(prog='private-sentinel').parse_args()",
            "--unknown-private",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 2 and result.stdout == ""
    diagnostic = startup_failure_diagnostic(
        result.stderr, 502, "none", command_exit_code=result.returncode
    )
    assert diagnostic["command_exit_status"] == "nonzero"
    assert diagnostic["command_exit_code"] == 2
    assert diagnostic["exception_type"] == "unknown"
    assert diagnostic["output_shapes"] == ["cli-usage", "cli-error"]
    assert "private" not in json.dumps(diagnostic)


def test_owned_argparse_success_does_not_claim_failure_or_usage():
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import argparse; argparse.ArgumentParser().parse_args()",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 0
    diagnostic = startup_failure_diagnostic(
        result.stderr, 502, "none", command_exit_code=result.returncode
    )
    assert diagnostic["command_exit_code"] == 0
    assert diagnostic["output_shapes"] == []
    assert diagnostic["output_nonempty"] is False


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
def test_real_pydantic_validation_error_has_only_fixed_public_facts(renderer):
    from pydantic import BaseModel, ValidationError

    class OwnedModel(BaseModel):
        value: int

    try:
        OwnedModel(value="private-sentinel")
    except ValidationError as exc:
        output = renderer(exc)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "ValidationError"
    assert "pydantic-validation" in result["output_shapes"]
    assert "private" not in json.dumps(result)
    assert "OwnedModel" not in json.dumps(result)


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
@pytest.mark.parametrize(
    "name", ["InterfaceError", "OperationalError", "ProgrammingError", "IntegrityError"]
)
def test_real_sqlalchemy_dbapi_error_uses_exact_public_alias(renderer, name):
    from sqlalchemy import exc

    error = getattr(exc, name)(
        "private-sql", {"private-key": "private-value"}, RuntimeError("private-error")
    )
    output = renderer(error)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == name
    assert "sqlalchemy-error" in result["output_shapes"]
    assert "private" not in json.dumps(result)


def test_real_framework_message_tails_supply_only_finite_format_hints():
    from pydantic import ValidationError, create_model
    from sqlalchemy.exc import OperationalError

    model = create_model("PrivateSentinel", **{f"field{n}": (int, ...) for n in range(100)})
    try:
        model(**{f"field{n}": "private-sentinel" for n in range(100)})
    except ValidationError as exc:
        pydantic_output = rich_trace(exc)
    sql_output = rich_trace(
        OperationalError("private-sentinel" * 1000, {}, RuntimeError("private-error"))
    )
    for output, shape in (
        (pydantic_output, "pydantic-validation"),
        (sql_output, "sqlalchemy-error"),
    ):
        tail = output.encode()[-NATIVE_TAIL_LIMIT:].decode("utf-8", errors="ignore")
        result = startup_failure_diagnostic(tail, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
        assert result["exception_type"] == "unknown"
        assert shape in result["output_shapes"]
        assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "name", ["private.ValidationError", "private.OperationalError", "custom.TypeError"]
)
def test_qualified_unknown_classes_do_not_inherit_public_suffixes(name):
    result = startup_failure_diagnostic(name + ": private-sentinel", 502, "none")
    assert result["exception_type"] == "unknown"
    assert "private" not in json.dumps(result)


def public_framework_classes():
    """Check the installed packages independently of production's frozen list.

    Their 66 non-warning defining classes also match the native tagged sources:
    SQLAlchemy 2.0.51, Pydantic 2.12.5, pydantic-core 2.41.5. Tests inspect only
    controller dependencies; no candidate module or downloaded source executes.
    """
    classes = {}
    for module_name in (
        "pydantic",
        "pydantic.errors",
        "pydantic_core",
        "sqlalchemy.exc",
        "sqlalchemy.orm.exc",
    ):
        module = importlib.import_module(module_name)
        for name in getattr(module, "__all__", vars(module)):
            if name.startswith("_"):
                continue
            value = getattr(module, name, None)
            if (
                inspect.isclass(value)
                and issubclass(value, Exception)
                and not issubclass(value, Warning)
            ):
                classes[module_name + "." + name] = value.__name__
                classes[value.__module__ + "." + value.__name__] = value.__name__
                classes[name] = value.__name__
    return sorted(classes.items())


@pytest.mark.parametrize("alias,canonical", public_framework_classes())
def test_verified_public_framework_inventory_has_no_missing_alias(alias, canonical):
    result = startup_failure_diagnostic(alias + ": private-sentinel", 502, "none")
    assert result["exception_type"] == canonical
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


def framework_exception_examples():
    from pydantic import errors
    from pydantic_core import (
        PydanticCustomError,
        PydanticKnownError,
        PydanticOmit,
        PydanticSerializationError,
        PydanticSerializationUnexpectedValue,
        PydanticUseDefault,
        SchemaError,
    )
    from sqlalchemy import exc
    from sqlalchemy.orm.exc import (
        DetachedInstanceError,
        FlushError,
        MappedAnnotationError,
        StaleDataError,
    )

    return [
        errors.PydanticUserError("private-sentinel", code=None),
        errors.PydanticUndefinedAnnotation("PrivateSentinel", "private-sentinel"),
        errors.PydanticImportError("private-sentinel"),
        errors.PydanticSchemaGenerationError("private-sentinel"),
        errors.PydanticInvalidForJsonSchema("private-sentinel"),
        errors.PydanticForbiddenQualifier("final", "private-sentinel"),
        PydanticCustomError("private-kind", "private-sentinel"),
        PydanticKnownError("int_parsing"),
        PydanticOmit(),
        PydanticUseDefault(),
        PydanticSerializationError("private-sentinel"),
        PydanticSerializationUnexpectedValue("private-sentinel"),
        SchemaError("private-sentinel"),
        exc.InvalidRequestError("private-sentinel"),
        exc.MissingGreenlet("private-sentinel"),
        exc.AwaitRequired("private-sentinel"),
        exc.NoResultFound(),
        exc.MultipleResultsFound(),
        exc.DataError("private-sql", {}, RuntimeError("private-sentinel")),
        exc.InternalError("private-sql", {}, RuntimeError("private-sentinel")),
        exc.NotSupportedError("private-sql", {}, RuntimeError("private-sentinel")),
        DetachedInstanceError("private-sentinel"),
        FlushError("private-sentinel"),
        MappedAnnotationError("private-sentinel"),
        StaleDataError("private-sentinel"),
    ]


@pytest.mark.parametrize(
    "renderer",
    [
        rich_trace,
        lambda exc: rich_trace(exc, panel=True),
        lambda exc: "".join(traceback.format_exception(exc)),
    ],
    ids=["rich", "rich-panel", "plain"],
)
@pytest.mark.parametrize("exc", framework_exception_examples(), ids=lambda exc: type(exc).__name__)
def test_real_extended_framework_exception_renderers(renderer, exc):
    result = startup_failure_diagnostic(renderer(exc), 502, "none")
    assert result["exception_type"] == type(exc).__name__
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)
    assert "PrivateSentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "renderer",
    [
        rich_trace,
        lambda exc: rich_trace(exc, panel=True),
        lambda exc: "".join(traceback.format_exception(exc)),
    ],
    ids=["rich", "rich-panel", "plain"],
)
@pytest.mark.parametrize("message", [(), ("private-sentinel",)])
@pytest.mark.parametrize("lowercase", [False, True])
def test_terminal_suffixless_unknown_suppresses_prior_known_exception(renderer, message, lowercase):
    class PrivateFailure(Exception):
        pass

    class privatefailure(Exception):
        pass

    terminal = (privatefailure if lowercase else PrivateFailure)(*message)
    terminal.__cause__ = TypeError("private-primary")
    result = startup_failure_diagnostic(renderer(terminal), 502, "none")
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("legacy_windows", [False, True])
@pytest.mark.parametrize("panel", [False, True])
@pytest.mark.parametrize("empty", [False, True])
@pytest.mark.parametrize("terminal_kind", ["known", "private", "lowercase"])
def test_real_rich_console_modes_preserve_terminal_chain(
    legacy_windows, panel, empty, terminal_kind
):
    class PrivateFailure(Exception):
        pass

    class privatefailure(Exception):
        pass

    exception = {"known": KeyError, "private": PrivateFailure, "lowercase": privatefailure}[
        terminal_kind
    ]
    terminal = exception() if empty else exception("private-sentinel")
    terminal.__cause__ = TypeError("private-primary")
    output = rich_trace(terminal, panel=panel, legacy_windows=legacy_windows)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    if panel:
        left, right = ("└", "┘") if legacy_windows else ("╰", "╯")
        assert left in output.splitlines()[-1] and right in output.splitlines()[-1]
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == ("KeyError" if terminal_kind == "known" else "unknown")
    assert result["failure_component"] == "unknown"
    assert result["output_read_limit_reached"] is False
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "alias",
    [
        "private.MissingGreenlet",
        "private.PydanticUserError",
        "sqlalchemy.exc.PrivateFailure",
        "pydantic.errors.PrivateFailure",
        "pydantic_core._pydantic_core.PrivateFailure",
    ],
)
def test_framework_prefix_never_authorizes_a_private_exception(alias):
    result = startup_failure_diagnostic(
        "TypeError: private-first\n" + alias + ": private-last", 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("prefix", ["", "\x1b[31m", "TypeError: private-primary\n"])
def test_cut_unknown_name_cannot_become_a_known_empty_exception(prefix):
    limit = len((prefix + "TypeError").encode())
    result = startup_failure_diagnostic(
        prefix + "TypeErrorPrivate", 502, "none", output_limit=limit
    )
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "unknown"


def test_complete_bare_exception_newline_remains_known_at_exact_cap():
    output = "TypeError\n"
    result = startup_failure_diagnostic(output, 502, "none", output_limit=len(output))
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "TypeError"


NODE_SYSTEM_ERROR = """SystemError [ERR_SYSTEM_ERROR]: private-sentinel
    at private-location:1:1 {
  code: 'ERR_SYSTEM_ERROR',
  info: {
    errno: 1,
    code: 'Unknown system error 1',
    message: 'private-sentinel',
    syscall: 'uv_interface_addresses'
  },
  errno: [Getter/Setter],
  syscall: [Getter/Setter]
}
"""


def test_node_interface_failure_requires_same_closed_info_block():
    assert node_failure_facts(NODE_SYSTEM_ERROR) == {
        "error_code": "ERR_SYSTEM_ERROR",
        "errno": 1,
        "syscall": "uv_interface_addresses",
        "component": "node-interface-enumeration",
    }
    colored_output = "\n".join(
        "\x1b[31m" + line + "\x1b[0m" for line in NODE_SYSTEM_ERROR.splitlines()
    )
    assert node_failure_facts(colored_output) == node_failure_facts(NODE_SYSTEM_ERROR)
    assert "private" not in json.dumps(node_failure_facts(NODE_SYSTEM_ERROR))


@pytest.mark.parametrize(
    "old,new",
    [
        ("SystemError [ERR_SYSTEM_ERROR]", "PrivateError [ERR_PRIVATE]"),
        ("    errno: 1,", "    errno: -1,"),
        ("    errno: 1,", "    errno: 1,\n    errno: 13,"),
        ("    syscall: 'uv_interface_addresses'", "    syscall: 'private-sentinel'"),
        ("  info: {", "  private: {"),
        ("  },", ""),
        ("  code: 'ERR_SYSTEM_ERROR',", "  code: 'ERR_PRIVATE',"),
    ],
)
def test_node_missing_conflicting_or_unrelated_properties_stay_unknown(old, new):
    result = node_failure_facts(NODE_SYSTEM_ERROR.replace(old, new))
    assert result["component"] == "unknown" and result["syscall"] == "unknown"
    assert "private" not in json.dumps(result)
    assert "ERR_PRIVATE" not in json.dumps(result)


def test_node_properties_cannot_cross_error_records_or_truncated_boundaries():
    first = NODE_SYSTEM_ERROR.replace("    errno: 1,\n", "")
    second = NODE_SYSTEM_ERROR.replace("    syscall: 'uv_interface_addresses'\n", "")
    for text in (
        first + second,
        NODE_SYSTEM_ERROR + "Error: private-terminal\n    at private:1:1 {\n}\n",
        "\x1b[0m" * NATIVE_TAIL_LIMIT + NODE_SYSTEM_ERROR,
        NODE_SYSTEM_ERROR[: NODE_SYSTEM_ERROR.index("  info:")]
        + "}\n"
        + NODE_SYSTEM_ERROR[NODE_SYSTEM_ERROR.index("  info:") :],
    ):
        result = node_failure_facts(text)
        assert result["component"] == "unknown"
        assert "private" not in json.dumps(result)


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned formatter fixture"
)
@pytest.mark.parametrize(
    "code,errno", [("ERR_SYSTEM_ERROR", 1), ("EACCES", -13), ("ENOENT", -2), ("EMFILE", -24)]
)
@pytest.mark.parametrize("logged", [False, True])
def test_actual_node_formatter_produces_only_verified_public_facts(code, errno, logged):
    # Trusted Node's own formatter with synthetic context; no candidate imports,
    # kernel-error claim, permission changes, or filesystem/network operations.
    if code == "ERR_SYSTEM_ERROR":
        construct = "new codes.ERR_SYSTEM_ERROR({errno:1,code:'Unknown system error 1',message:'Unknown system error 1',syscall:'uv_interface_addresses'})"
    else:
        construct = (
            "new UVException("
            + json.dumps(
                {
                    "errno": errno,
                    "code": code,
                    "message": "private-sentinel",
                    "syscall": "open",
                    "path": "/private-sentinel",
                }
            )
            + ")"
        )
    script = (
        "Error.stackTraceLimit=1;const {codes,UVException}=require('internal/errors');const e="
        + construct
        + ";"
        + ("console.error(e);" if logged else "throw e;")
    )
    process = subprocess.run(
        [shutil.which("node"), "--expose-internals", "-e", script],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        },
    )
    assert process.returncode == (0 if logged else 1)
    result = node_failure_facts(process.stderr)
    assert result["error_code"] == code and result["errno"] == errno
    assert result["syscall"] == ("uv_interface_addresses" if code == "ERR_SYSTEM_ERROR" else "open")
    assert result["component"] == (
        "node-interface-enumeration" if code == "ERR_SYSTEM_ERROR" else "unknown"
    )
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("value", [None, True, "", [], "x" * 129])
@pytest.mark.parametrize("field", ["session", "command_id"])
def test_invalid_command_identity_cannot_issue_a_status_query(value, field):
    identities = {"session": "owned-session", "command_id": "owned-command"}
    identities[field] = value
    process = SimpleNamespace(
        get_session_command=lambda *a: pytest.fail("Invalid identity queried")
    )
    assert startup_command_exit_facts(process, **identities, timeout=5) == {
        "command_exit_status": "unknown",
        "command_exit_code": None,
    }


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned formatter fixture"
)
@pytest.mark.parametrize("name", ["PrivateFailure", "privatefailure", "私有错误"])
@pytest.mark.parametrize("logged", [False, True])
def test_actual_node_suffixless_terminal_error_cannot_borrow_prior_component(name, logged):
    script = (
        "Error.stackTraceLimit=1;const {codes}=require('internal/errors');"
        "console.error(new codes.ERR_SYSTEM_ERROR({errno:1,code:'Unknown system error 1',"
        "message:'Unknown system error 1',syscall:'uv_interface_addresses'}));"
        "const terminal=new Error('private-sentinel');terminal.name="
        + json.dumps(name)
        + ";"
        + ("console.error(terminal);" if logged else "throw terminal;")
    )
    process = subprocess.run(
        [shutil.which("node"), "--expose-internals", "-e", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        },
    )
    assert process.returncode == (0 if logged else 1)
    assert "ERR_SYSTEM_ERROR" in process.stderr and name + ": private-sentinel" in process.stderr
    assert len(process.stderr.encode()) < NATIVE_TAIL_LIMIT
    result = node_failure_facts(process.stderr)
    assert result == {
        "error_code": "unknown",
        "errno": None,
        "syscall": "unknown",
        "component": "unknown",
    }
    assert name not in json.dumps(result, ensure_ascii=False)


@pytest.mark.parametrize(
    "terminal",
    [
        "PrivateFailure: private-sentinel\n",
        "PrivateFailure:",
        "PrivateFailure: " + "x" * NATIVE_TAIL_LIMIT,
        "Private" + "x" * 256 + ": private-sentinel\n",
        "private-terminal-text\n",
    ],
)
def test_node_unknown_or_partial_terminal_record_remains_conservative(terminal):
    result = node_failure_facts(NODE_SYSTEM_ERROR + terminal)
    assert result == {
        "error_code": "unknown",
        "errno": None,
        "syscall": "unknown",
        "component": "unknown",
    }


def test_node_latest_known_record_and_raw_budget_do_not_borrow_other_records():
    denied = """Error: EACCES: private-sentinel
    at private-location:1:1 {
  errno: -13,
  syscall: 'open',
  code: 'EACCES',
  path: '/private-sentinel'
}
"""
    assert node_failure_facts(NODE_SYSTEM_ERROR + denied) == {
        "error_code": "EACCES",
        "errno": -13,
        "syscall": "open",
        "component": "unknown",
    }
    assert node_failure_facts(
        NODE_SYSTEM_ERROR.ljust(NATIVE_TAIL_LIMIT) + "PrivateFailure: outside-budget"
    ) == node_failure_facts(NODE_SYSTEM_ERROR)
