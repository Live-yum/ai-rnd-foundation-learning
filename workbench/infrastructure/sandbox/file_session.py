"""Parent-owned bounded file RPC; no SDK call can hold the controller past its deadline."""

import contextlib
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from workbench.errors import UnsupportedScope
from workbench.filesystem import write_json
from workbench.infrastructure.sandbox.cleanup import delete_owned, receipt
from workbench.tools import clean_env, process_options

LIMIT = 1_200_000
SUPERVISION_PHASES = {"terminate", "wait", "reader", "pipes", "job_close", "delete", "journal"}
SUPERVISION_KINDS = {
    "OSError",
    "PermissionError",
    "ValueError",
    "TimeoutExpired",
    "UnsupportedScope",
    "other",
}


def supervision_failure(phase, error):
    kind = type(error).__name__
    return {
        "supervision_failure_phase": phase if phase in SUPERVISION_PHASES else "journal",
        "supervision_failure_kind": kind if kind in SUPERVISION_KINDS else "other",
    }


PHASES = {
    "protocol",
    "admission",
    "client",
    "create",
    "refresh",
    "inspection",
    "initial_upload",
    "write",
    "snapshot",
}


def failure_facts(value):
    from workbench.infrastructure.sandbox.cleanup import FAILURE_KINDS

    return (
        {"failure_phase": value["phase"], "failure_kind": value["kind"]}
        if (value.get("phase") in PHASES and value.get("kind") in FAILURE_KINDS)
        else {}
    )


def preserve_state(path, binding, name, identifier, error, failure):
    try:
        value = json.loads(path.read_text()) if path.stat().st_size <= 4096 else {}
        if (
            value.get("binding") != binding
            or value.get("sandbox_name") != name
            or value.get("sandbox_id") != identifier
        ):
            raise ValueError("Stale cleanup state")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        value = {
            **receipt(binding, name, identifier, "deletion_unconfirmed"),
            **supervision_failure("journal", exc),
        }
    if error is not None and value.get("status") not in {"unconfirmed"}:
        value.update(status="unconfirmed", reason="deletion_unconfirmed")
    value.update(failure)
    write_json(path, value)


def close_pipes_bounded(process):
    def close():
        for pipe in (process.stdin, process.stdout):
            try:
                pipe.close()
            except OSError, ValueError:
                pass

    thread = threading.Thread(target=close, daemon=True)
    thread.start()
    thread.join(timeout=0.2)
    if thread.is_alive():
        raise UnsupportedScope("File RPC pipe close exceeded bound")


class Session:
    def __init__(self, settings, task, selection, product, deadline, path, binding):
        if not 15 < deadline - time.monotonic() <= 180:
            raise UnsupportedScope("File session requires the original bounded module deadline")
        from workbench.capability_sandbox import verifier_policy_environment

        policy_environment = verifier_policy_environment()
        self.deadline, self.work_end = deadline, deadline - 15
        self.settings, self.path, self.binding = settings, path, dict(binding)
        self.name = (
            ("rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-")
            + "agent-"
            + uuid.uuid4().hex
        )
        self.identifier = None
        self.failure = {}
        self.windows_job = None
        self.lock, self.done, self.cancel = threading.Lock(), threading.Event(), threading.Event()
        self.closing, self.error = False, None
        self.answers = queue.Queue(maxsize=2)
        self.process = None
        write_json(path, receipt(self.binding, self.name, None, "create_unconfirmed"))
        keys = (
            "sandbox_provider",
            "daytona_allow_local_execution",
            "daytona_api_url",
            "daytona_snapshot",
            "daytona_snapshots",
            "daytona_target",
            "daytona_runtime_timeout",
            "tool_timeout",
            "capability_execution_enabled",
            "capability_browser_image",
        )
        config = {key: getattr(settings, key) for key in keys}
        config["capability_profile_directory"] = str(settings.capability_profile_directory)
        config["daytona_api_key"] = settings.daytona_api_key.get_secret_value()
        payload = {
            "settings": config,
            "task": task.model_dump(),
            "selection": selection,
            "product": str(Path(product).resolve()),
            "deadline": deadline,
            "name": self.name,
            "nonce": self.binding["nonce"],
        }
        try:
            self.process = subprocess.Popen(
                [sys.executable, "-m", __name__],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                env=clean_env(policy_environment),
                **process_options(),
            )
            if os.name == "nt":
                from workbench.infrastructure.sandbox.windows_job import WindowsJob

                self.windows_job = WindowsJob(self.process)
            self.reader = threading.Thread(target=self.read, daemon=True)
            self.reader.start()
            self.watchdog = threading.Thread(target=self.watch, daemon=True)
            self.watchdog.start()
            self.send(payload)
            self.receive()
        except BaseException:
            self.finish()
            raise

    def read(self):
        try:
            while True:
                raw = self.process.stdout.readline(LIMIT + 1)
                if not raw or len(raw) > LIMIT:
                    raise ValueError("File worker protocol ended")
                value = json.loads(raw)
                if value.get("nonce") != self.binding["nonce"]:
                    raise ValueError("File worker session binding mismatch")
                if value.get("event") == "created":
                    with self.lock:
                        if self.closing or time.monotonic() >= self.work_end:
                            continue
                        if (
                            self.identifier is not None
                            or value.get("name") != self.name
                            or type(value.get("id")) is not str
                            or not 0 < len(value["id"]) <= 256
                        ):
                            raise ValueError("File worker identity mismatch")
                        self.identifier = value["id"]
                        write_json(self.path, receipt(self.binding, self.name, self.identifier))
                else:
                    if value.get("error") is True:
                        with self.lock:
                            if not self.closing:
                                self.failure = failure_facts(value)
                    self.answers.put(value, timeout=max(0.001, self.work_end - time.monotonic()))
        except Exception:
            try:
                self.answers.put_nowait({"error": True})
            except queue.Full:
                pass

    def send(self, value):
        raw = json.dumps(value).encode() + b"\n"
        if len(raw) > LIMIT or time.monotonic() >= self.work_end:
            raise UnsupportedScope("File RPC exceeds original budget")
        self.process.stdin.write(raw)
        self.process.stdin.flush()

    def receive(self):
        try:
            value = self.answers.get(timeout=max(0, self.work_end - time.monotonic()))
        except queue.Empty:
            raise UnsupportedScope("File SDK deadline exhausted") from None
        if (
            self.closing
            or time.monotonic() >= self.work_end
            or value.get("error")
            or "result" not in value
        ):
            raise UnsupportedScope("File SDK failed or returned after deadline")
        return value["result"]

    def bind_candidate(self, source):
        with self.lock:
            if self.closing or time.monotonic() >= self.work_end:
                raise UnsupportedScope("File session expired")
            self.binding = {**self.binding, "source": source}
            write_json(self.path, receipt(self.binding, self.name, self.identifier))

    def write(self, edits):
        self.send({"operation": "write", "edits": edits.model_dump()})
        self.receive()

    def snapshot(self, paths):
        self.send({"operation": "snapshot", "paths": paths})
        return self.receive()

    def watch(self):
        if not self.cancel.wait(max(0, self.work_end - time.monotonic())):
            try:
                self.finish()
            except UnsupportedScope:
                pass  # Parent RPC/finally observes the stored terminal error.

    def remember_error(self, error, phase):
        if self.error is None:
            self.error = error
            self.failure.update(supervision_failure(phase, error))

    def finish(self):
        with self.lock:
            owner = not self.closing
            self.closing = True
        if owner:
            self.cancel.set()
            phase = "terminate"
            try:
                try:
                    if self.process is not None:
                        try:
                            if os.name == "posix":
                                # Kill the owned session before reaping its leader, including inspectors.
                                os.killpg(self.process.pid, signal.SIGKILL)
                            elif self.windows_job is not None:
                                self.windows_job.terminate()
                            elif self.process.poll() is None:
                                self.process.kill()  # Job setup failed before any request was sent.
                        except ProcessLookupError:
                            pass
                        phase = "wait"
                        self.process.wait(
                            timeout=max(0.001, min(2, self.deadline - time.monotonic()))
                        )
                        phase = "reader"
                        if hasattr(self, "reader"):
                            self.reader.join(timeout=0.2)
                            if self.reader.is_alive():
                                raise UnsupportedScope(
                                    "File RPC pipe did not close after tree termination"
                                )
                        phase = "pipes"
                        close_pipes_bounded(self.process)
                except BaseException as exc:
                    self.remember_error(exc, phase)
                finally:
                    if self.windows_job is not None:
                        try:
                            self.windows_job.close()
                        except BaseException as exc:
                            self.remember_error(exc, "job_close")
                # A local reaping error must not suppress the owned remote deletion attempt.
                # Both paths retain the original deadline; local failure still rejects the run.
                phase = "delete"
                delete_owned(
                    self.settings,
                    self.name,
                    self.identifier,
                    self.binding,
                    self.path,
                    self.deadline,
                )
            except BaseException as exc:
                self.remember_error(exc, phase)
            finally:
                try:
                    preserve_state(
                        self.path,
                        self.binding,
                        self.name,
                        self.identifier,
                        self.error,
                        self.failure,
                    )
                finally:
                    self.done.set()
        else:
            # SDK work is killed at its deadline; allow only bounded child reaping here.
            self.done.wait(max(0, self.deadline - time.monotonic()) + 3)
        if not self.done.is_set() or self.error is not None:
            raise UnsupportedScope("File session cleanup unconfirmed; execution stopped")


@contextlib.contextmanager
def supervised_environment(
    settings, task, selection, product, *, deadline, cleanup_record, cleanup_binding
):
    session = Session(settings, task, selection, product, deadline, cleanup_record, cleanup_binding)
    try:
        yield session
    finally:
        session.finish()


def main():
    from workbench.infrastructure.sandbox.coding import _local_environment
    from workbench.local_only import install_loopback_guard
    from workbench.planning.contracts import CapabilityEdits, CapabilityTaskV2
    from workbench.settings import Settings

    install_loopback_guard()
    body = sys.stdin.buffer.readline(LIMIT + 1)
    if len(body) > LIMIT:
        raise ValueError("File worker payload too large")
    payload = json.loads(body)
    output = sys.stdout

    def emit(value):
        output.write(json.dumps({"nonce": payload["nonce"], **value}) + "\n")
        output.flush()

    phase = {"value": "protocol"}
    try:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            with _local_environment(
                Settings(_env_file=None, **payload["settings"]),
                CapabilityTaskV2.model_validate(payload["task"]),
                payload["selection"],
                Path(payload["product"]),
                deadline=payload["deadline"],
                owned_name=payload["name"],
                external_cleanup=True,
                on_phase=lambda value: phase.update(value=value),
                on_created=lambda name, identifier: emit(
                    {"event": "created", "name": name, "id": identifier}
                ),
            ) as files:
                emit({"result": True})
                while True:
                    raw = sys.stdin.buffer.readline(LIMIT + 1)
                    if not raw or len(raw) > LIMIT:
                        raise ValueError("File worker request ended")
                    request = json.loads(raw)
                    if request["operation"] == "write":
                        phase["value"] = "write"
                        files.write(CapabilityEdits.model_validate(request["edits"]))
                        result = True
                    elif request["operation"] == "snapshot":
                        phase["value"] = "snapshot"
                        result = files.snapshot(request["paths"])
                    else:
                        raise ValueError("Unknown file-only operation")
                    emit({"result": result})
    except Exception as exc:
        from workbench.infrastructure.sandbox.cleanup import failure_kind

        emit({"error": True, "phase": phase["value"], "kind": failure_kind(exc)})
        raise


if __name__ == "__main__":
    main()
