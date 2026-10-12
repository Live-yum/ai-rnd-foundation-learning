"""Optional fixed-label/numeric diagnostics; never execution authority."""

import json
import math
import time
from contextlib import contextmanager

from workbench.filesystem import write_json

TURN_FIELDS = {
    "step": 8,
    "module_remaining_seconds": 180,
    "work_remaining_seconds": 180,
    "timeout_seconds": 180,
    "elapsed_seconds": 5400,
    "remaining_after_seconds": 180,
    "overrun_seconds": 5400,
    "payload_chars": 40000,
    "http_attempts_before": 32,
    "http_attempts_after": 32,
}
ATTEMPT_FIELDS = {
    "attempt": 32,
    "request_body_bytes": 1_000_000,
    "read_timeout_seconds": 180,
    "headers_seconds": 5400,
    "elapsed_seconds": 5400,
    "response_bytes": 2_000_000,
}
HTTP_TRACE_PHASES = ("connect", "tls", "request_headers", "request_body", "response_headers")
HTTP_TRACE_TIMES = {
    f"{phase}_{state}_seconds": 5400
    for phase in HTTP_TRACE_PHASES
    for state in ("started", "complete", "failed")
}
TURN_OPERATIONS = ("edit", "submit", "edit_and_submit")


def http_trace_receipt(value):
    """Fixed phases and bounded numbers only; never retain trace info or exceptions."""
    if not isinstance(value, dict):
        return None
    phase = value.get("failed_phase")
    count = value.get("event_count")
    return {
        "event_count": count if type(count) is int and 0 <= count <= 64 else None,
        "failed_phase": phase if type(phase) is str and phase in HTTP_TRACE_PHASES else None,
        **{key: numeric(value.get(key), limit) for key, limit in HTTP_TRACE_TIMES.items()},
    }


def numeric(value, maximum):
    return (
        round(value, 4)
        if type(value) in (int, float) and 0 <= value <= maximum and math.isfinite(value)
        else None
    )


def timing_receipts(values, *, attempts=False):
    fields = ATTEMPT_FIELDS if attempts else TURN_FIELDS
    if not isinstance(values, list):
        return []
    return [
        {
            **{key: numeric(value.get(key), limit) for key, limit in fields.items()},
            **(
                {"http_trace": http_trace_receipt(value["http_trace"])}
                if attempts and "http_trace" in value
                else {}
            ),
            **(
                {
                    "operation": value["operation"]
                    if type(value["operation"]) is str and value["operation"] in TURN_OPERATIONS
                    else None
                }
                if not attempts and "operation" in value
                else {}
            ),
        }
        for value in values[: 32 if attempts else 8]
        if isinstance(value, dict)
    ]


def read_turns(path):
    try:
        if path.stat().st_size > 32768:
            return []
        return timing_receipts(json.loads(path.read_text()))
    except OSError, ValueError, TypeError:
        return []


@contextmanager
def record_turn(path, step, deadline, timeout, payload, transport):
    started = time.monotonic()
    value = {
        "step": step,
        "module_remaining_seconds": max(0, deadline - started),
        "work_remaining_seconds": max(0, deadline - started - 15),
        "timeout_seconds": timeout,
        "payload_chars": len(json.dumps(payload, ensure_ascii=False)),
        "http_attempts_before": getattr(transport, "calls", None),
    }
    try:
        yield value
    finally:
        ended = time.monotonic()
        value.update(
            elapsed_seconds=max(0, ended - started),
            remaining_after_seconds=max(0, deadline - ended),
            overrun_seconds=max(0, ended - deadline),
            http_attempts_after=getattr(transport, "calls", None),
        )
        try:
            write_json(path, timing_receipts([*read_turns(path), value]))
        except OSError, ValueError, TypeError:
            pass  # Optional diagnostics cannot replace the model outcome.
