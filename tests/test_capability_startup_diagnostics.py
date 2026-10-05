"""Startup hints cannot become product acceptance or disclose candidate output."""

import json

import pytest

from workbench.capability_sandbox import startup_failure_diagnostic


def test_startup_hints_are_finite_even_for_secret_bearing_tracebacks():
    result = startup_failure_diagnostic(
        "secret content /private/secret token=secret\n"
        "ModuleNotFoundError: No module named 'secret.module'\n"
        "PermissionError: secret path\nApplication startup complete",
        503,
        "secret transport error",
    )
    assert result == {
        "phase": "health_deadline",
        "http_status": 503,
        "http_error": "other",
        "output_readable": True,
        "output_nonempty": True,
        "output_hints": ["permission-denied", "missing-module"],
        "known_missing_modules": [],
        "startup_phase_hint": "unknown",
        "failure_component": "unknown",
        "exception_type": "PermissionError",
        "exception_errno": None,
        "application_startup_reported": True,
        "tmpfs_noexec": None,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 768
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
