"""Optional verifier failure facts; no product text, paths, or SDK messages."""

import json
from pathlib import Path

from workbench.settings import ROOT

STAGES = {
    "workbench/capability_sandbox.py": "verifier_controller",
    "workbench/capability_execution.py": "isolation_admission",
    "workbench/capability_dependencies.py": "dependency_admission",
    "workbench/capability_consumer.py": "consumer_contract",
    "workbench/capability_verification.py": "independent_oracle",
    "workbench/capability_browser_isolation.py": "browser_isolation",
    "workbench/sandbox.py": "sandbox_transport",
    "scripts/daytona_capability_profile.py": "container_inspection",
}
ERRORS = frozenset(
    {
        "CheckFailure",
        "BrowserFailure",
        "PrerequisiteError",
        "IsolationUnavailable",
        "ContainerInspectionRejected",
        "ValueError",
        "TypeError",
        "KeyError",
        "RuntimeError",
        "FileNotFoundError",
        "PermissionError",
        "TimeoutError",
        "TimeoutExpired",
        "ValidationError",
        "DaytonaError",
        "DaytonaNotFoundError",
    }
)
CLEANUP = frozenset(
    {"deleted", "not-started", "not-created", "pending", "delete-failed", "create-failed-unknown"}
)


def _read(path):
    try:
        with Path(path).open("rb") as source:
            raw = source.read(1_000_001)
        if len(raw) > 1_000_000:
            return {}
        result = json.loads(raw)
        return result if type(result) is dict else {}
    except OSError, ValueError, RecursionError:
        return {}


def _label(value, allowed):
    return value if type(value) is str and value in allowed else "other"


def record_failure(receipt_path, exc):
    """Write a separate diagnostic; never add fields to the acceptance receipt."""
    try:
        from workbench.filesystem import write_json

        failure = {"exception_type": _label(type(exc).__name__, ERRORS), "stage": "other"}
        trusted = {str(ROOT / name): stage for name, stage in STAGES.items()}
        frame = exc.__traceback__
        while frame is not None:
            stage = trusted.get(frame.tb_frame.f_code.co_filename)
            if stage is not None:
                failure.update(stage=stage, trusted_source_line=frame.tb_lineno)
            frame = frame.tb_next
        write_json(str(receipt_path) + ".diagnostic.json", failure)
    except Exception:
        pass  # Diagnostics cannot replace the verifier failure or interrupt cleanup.


def node_diagnostic(product, *, aggregate):
    product = Path(product)
    path = product.parent / (
        product.name + ("-aggregate" if aggregate else "-node") + "-verification.json"
    )
    receipt = _read(path)
    sidecar = Path(str(path) + ".diagnostic.json")
    failure = _read(sidecar)
    try:
        if sidecar.stat().st_mtime_ns < path.stat().st_mtime_ns:
            failure = {}
    except OSError:
        failure = {}
    result = {
        "scope": "aggregate" if aggregate else "node",
        "receipt_available": bool(receipt),
        "passed": receipt.get("passed") if type(receipt.get("passed")) is bool else None,
        "cleanup": _label(receipt.get("cleanup"), CLEANUP),
        "exception_type": _label(failure.get("exception_type"), ERRORS),
        "stage": _label(failure.get("stage"), set(STAGES.values())),
    }
    line = failure.get("trusted_source_line")
    if type(line) is int and 0 < line < 1_000_000:
        result["trusted_source_line"] = line
    for key in ("checks", "obligation_checks", "browser"):
        value = receipt.get(key)
        result[key + "_count"] = len(value) if type(value) is list and len(value) <= 10000 else None
    for key in ("restarted", "backend_health_observed"):
        result[key] = receipt.get(key) if type(receipt.get(key)) is bool else None
    return result
