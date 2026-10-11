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


class Session:
    def __init__(self, settings, task, selection, product, deadline, path, binding):
        if not 15 < deadline - time.monotonic() <= 180:
            raise UnsupportedScope("File session requires the original bounded module deadline")
        self.deadline, self.work_end = deadline, deadline - 15
        self.settings, self.path, self.binding = settings, path, dict(binding)
        self.name = (
            ("rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-")
            + "agent-"
            + uuid.uuid4().hex
        )
        self.identifier = None
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
                env=clean_env(),
                **process_options(),
            )
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

    def finish(self):
        with self.lock:
            owner = not self.closing
            self.closing = True
        if owner:
            self.cancel.set()
            try:
                if self.process is not None:
                    try:
                        if os.name == "posix":
                            # Kill the owned session before reaping its leader, including inspectors.
                            os.killpg(self.process.pid, signal.SIGKILL)
                        elif self.process.poll() is None:
                            self.process.kill()
                    except ProcessLookupError:
                        pass
                    self.process.wait(timeout=max(0.001, min(2, self.deadline - time.monotonic())))
                    for pipe in (self.process.stdin, self.process.stdout):
                        try:
                            pipe.close()
                        except OSError, ValueError:
                            pass  # The reaped worker owns no remaining SDK transport.
                delete_owned(
                    self.settings,
                    self.name,
                    self.identifier,
                    self.binding,
                    self.path,
                    self.deadline,
                )
            except BaseException as exc:
                self.error = exc
                write_json(
                    self.path,
                    receipt(self.binding, self.name, self.identifier, "deletion_unconfirmed"),
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

    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        with _local_environment(
            Settings(_env_file=None, **payload["settings"]),
            CapabilityTaskV2.model_validate(payload["task"]),
            payload["selection"],
            Path(payload["product"]),
            deadline=payload["deadline"],
            owned_name=payload["name"],
            external_cleanup=True,
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
                    files.write(CapabilityEdits.model_validate(request["edits"]))
                    result = True
                elif request["operation"] == "snapshot":
                    result = files.snapshot(request["paths"])
                else:
                    raise ValueError("Unknown file-only operation")
                emit({"result": result})


if __name__ == "__main__":
    main()
