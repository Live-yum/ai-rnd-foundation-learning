"""Owned coding-sandbox deletion; the parent alone publishes terminal cleanup state."""

import json
import re
import subprocess
import sys
import time

from workbench.errors import UnsupportedScope
from workbench.filesystem import write_json
from workbench.tools import clean_env, process_options

NAME = re.compile(r"rnd-source-(?:native-)?agent-[a-f0-9]{32}")


FAILURE_KINDS = {
    "PrerequisiteError",
    "UnsupportedScope",
    "ValueError",
    "TimeoutError",
    "DaytonaNotFoundError",
    "DaytonaTimeoutError",
    "DaytonaAuthorizationError",
    "DaytonaAuthenticationError",
    "DaytonaError",
    "other",
}


def failure_kind(exc):
    name = type(exc).__name__
    return name if name in FAILURE_KINDS else "other"


def receipt(binding, name, identifier, reason="pending"):
    return {
        "binding": binding,
        "sandbox_name": name,
        "sandbox_id": identifier,
        "status": "pending" if reason == "pending" else "unconfirmed",
        "reason": reason,
    }


def confirm_deleted(client, target, deadline, timeout_cap):
    from daytona.common.errors import DaytonaNotFoundError

    remaining = min(timeout_cap, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError("Cleanup deadline")
    identifier = target.id
    client.delete(target, timeout=remaining)
    while time.monotonic() < deadline:
        try:
            client.get(identifier)
        except DaytonaNotFoundError:
            if time.monotonic() >= deadline:
                raise TimeoutError("Deletion confirmation arrived after deadline") from None
            return
        time.sleep(min(0.05, max(0, deadline - time.monotonic())))
    raise TimeoutError("Deletion not confirmed absent")


def delete_owned(settings, name, identifier, binding, path, deadline):
    if not NAME.fullmatch(name):
        raise UnsupportedScope("Cleanup ownership name rejected")
    late = time.monotonic() >= deadline
    unresolved_create = identifier is None
    value = receipt(
        binding,
        name,
        identifier,
        "module_deadline" if late else "create_unconfirmed" if unresolved_create else "pending",
    )
    write_json(path, value)
    end = time.monotonic() + 1 if late else deadline
    payload = {
        "name": name,
        "identifier": identifier,
        "binding": binding,
        "deadline": end,
        "settings": {key: getattr(settings, key) for key in ("daytona_api_url", "daytona_target")},
    }
    payload["settings"]["daytona_api_key"] = settings.daytona_api_key.get_secret_value()
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "workbench.infrastructure.sandbox.cleanup"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=clean_env(),
            **process_options(),
        )
        output, _ = process.communicate(
            json.dumps(payload).encode(), timeout=max(0, end - time.monotonic())
        )
        if not process.returncode and len(output) <= 4096:
            diagnostic = json.loads(output)
            if (
                diagnostic.get("binding") == binding
                and diagnostic.get("deleted") is False
                and diagnostic.get("failure_kind") in FAILURE_KINDS
            ):
                value["cleanup_failure_kind"] = diagnostic["failure_kind"]
                write_json(path, value)
        if late or unresolved_create:
            raise UnsupportedScope("Terminated cleanup state cannot be upgraded by a late result")
        if time.monotonic() >= end or process.returncode or len(output) > 4096:
            raise UnsupportedScope("Cleanup result missing or late")
        result = json.loads(output)
        if result != {"binding": binding, "deleted": True}:
            raise UnsupportedScope("Cleanup acknowledgement binding rejected")
        value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)
    except BaseException:
        if value["status"] == "pending":
            value.update(status="unconfirmed", reason="deletion_unconfirmed")
            write_json(path, value)
        if process is not None and process.poll() is None:
            process.kill()  # no SDK callback or late child can write this parent-owned journal
            process.wait(timeout=2)
        raise


def perform(payload):
    from workbench.local_only import install_loopback_guard
    from workbench.sandbox import client_for, close_client
    from workbench.settings import Settings

    install_loopback_guard()
    if not NAME.fullmatch(payload["name"]):
        raise ValueError("Unowned cleanup target")
    client = client_for(Settings(_env_file=None, **payload["settings"]))
    try:
        target = client.get(payload["identifier"] or payload["name"])
        if target.name != payload["name"] or (
            payload["identifier"] is not None and target.id != payload["identifier"]
        ):
            raise ValueError("Cleanup identity mismatch")
        confirm_deleted(client, target, payload["deadline"], 120)
        return {"binding": payload["binding"], "deleted": True}
    finally:
        close_client(client)


def main():
    import contextlib
    import os

    body = sys.stdin.buffer.read(16385)
    if len(body) > 16384:
        raise ValueError("Cleanup request too large")
    # SDK output is not protocol data and must not escape to the parent.
    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        payload = json.loads(body)
        try:
            result = perform(payload)
        except Exception as exc:
            result = {
                "binding": payload["binding"],
                "deleted": False,
                "failure_kind": failure_kind(exc),
            }
    print(json.dumps(result))


def public_receipt(path, task, plan):
    from workbench.core.contracts import digest

    unknown = {"status": "unconfirmed", "reason": "invalid_or_missing"}
    try:
        if path.stat().st_size > 4096:
            return unknown
        value = json.loads(path.read_text())
        bound = value["binding"]
        if (
            set(bound) != {"task", "plan", "source", "nonce"}
            or bound["task"] != digest(task.model_dump())
            or bound["plan"] != digest(plan.model_dump())
            or type(bound["source"]) is not str
            or not re.fullmatch("[a-f0-9]{64}", bound["source"])
            or type(bound["nonce"]) is not str
            or not re.fullmatch("[a-f0-9]{32}", bound["nonce"])
            or type(value["sandbox_name"]) is not str
            or not NAME.fullmatch(value["sandbox_name"])
            or value["status"] not in ("pending", "unconfirmed", "deleted")
            or value["reason"]
            not in (
                "pending",
                "confirmed_absent",
                "module_deadline",
                "create_unconfirmed",
                "deletion_unconfirmed",
                "transport_cleanup",
            )
            or (value["status"] == "deleted" and value["reason"] != "confirmed_absent")
        ):
            return unknown
        extra = {}
        from workbench.infrastructure.sandbox.file_session import (
            PHASES,
            SUPERVISION_KINDS,
            SUPERVISION_PHASES,
        )

        if value.get("failure_phase") in PHASES and value.get("failure_kind") in FAILURE_KINDS:
            extra.update(failure_phase=value["failure_phase"], failure_kind=value["failure_kind"])
        if value.get("cleanup_failure_kind") in FAILURE_KINDS:
            extra["cleanup_failure_kind"] = value["cleanup_failure_kind"]
        if (
            value.get("supervision_failure_phase") in SUPERVISION_PHASES
            and value.get("supervision_failure_kind") in SUPERVISION_KINDS
        ):
            extra.update(
                supervision_failure_phase=value["supervision_failure_phase"],
                supervision_failure_kind=value["supervision_failure_kind"],
            )
        return {
            **extra,
            "status": value["status"],
            "reason": value["reason"],
            "binding": bound,
            "sandbox_name": value["sandbox_name"],
        }
    except OSError, ValueError, TypeError, KeyError:
        return unknown


def checkpoint_receipts(workspace, task, plan):
    """Project at most eight owned checkpoint receipts before ephemeral source removal."""
    from workbench.capability_diagnostics import node_diagnostic
    from workbench.core.contracts import digest
    from workbench.filesystem import manifest

    result = []
    for step in range(1, 9):
        candidate = workspace / f"step-{step}"
        path = workspace / f"step-{step}-node-verification.json"
        if not path.exists():
            continue
        item = {"step": step, "cleanup": "unconfirmed", "binding_valid": False}
        try:
            if path.stat().st_size > 1_000_000:
                raise ValueError("Oversized checkpoint receipt")
            value = json.loads(path.read_text())
            bound = value["checkpoint"]
            if (
                type(bound["nonce"]) is not str
                or not re.fullmatch("[a-f0-9]{32}", bound["nonce"])
                or bound["task"] != digest(task.model_dump())
                or value["plan_digest"] != digest(plan.model_dump())
                or value["source_digest"] != digest(manifest(candidate))
                or type(value["sandbox_name"]) is not str
                or not re.fullmatch(
                    r"rnd-(?:source-(?:native-)?|capability-)[a-f0-9]{32}", value["sandbox_name"]
                )
            ):
                raise ValueError("Checkpoint binding rejected")
            item.update(node_diagnostic(candidate, aggregate=False))
            item.update(
                binding_valid=True,
                sandbox_name=value["sandbox_name"],
                binding={
                    "task": bound["task"],
                    "plan": value["plan_digest"],
                    "source": value["source_digest"],
                    "nonce": bound["nonce"],
                },
            )
        except OSError, ValueError, TypeError, KeyError:
            pass
        result.append(item)
    return result


if __name__ == "__main__":
    main()
