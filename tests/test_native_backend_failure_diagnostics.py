"""Primary backend failures remain visible when owned cleanup also fails."""

import itertools
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from workbench import native_environment as native


@pytest.mark.parametrize("primary", ["exit", "body", None])
@pytest.mark.parametrize("cleanup", ["occupied", "stop", "close", "receipt"])
def test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure(
    tmp_path, monkeypatch, primary, cleanup
):
    """Portable control-flow fakes, including the Windows unobservable-proc path."""

    class Process:
        pid = 12345678
        returncode = 42 if primary == "exit" else None

        def poll(self):
            return self.returncode

    process = Process()
    monkeypatch.setattr(native.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(native, "backend_port_state", lambda *args: {"observable": False})
    binds = itertools.count()
    monkeypatch.setattr(
        native, "loopback_port_bindable", lambda port: next(binds) == 0 or cleanup != "occupied"
    )
    times = itertools.count(0, 6)
    monkeypatch.setattr(native.time, "monotonic", lambda: next(times))
    stopped = []

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        if cleanup == "stop":
            raise OSError("explicit synthetic stop error")
        process.returncode = process.returncode if process.returncode is not None else -9

    monkeypatch.setattr(native, "stop_process", stop)
    if hasattr(native.os, "killpg"):
        monkeypatch.setattr(
            native.os, "killpg", lambda *args: pytest.fail("no observed group to kill")
        )

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url):
            assert primary != "exit"

            class Response:
                status_code = 200

                def json(self):
                    return {"paths": {}}

            return Response()

    monkeypatch.setattr(native.httpx, "Client", Client)
    original_open = Path.open

    class Log:
        def __init__(self, stream):
            self.stream = stream

        def tell(self):
            return self.stream.tell()

        def close(self):
            self.stream.close()
            raise OSError("explicit synthetic log close error")

    if cleanup == "close":

        def opened(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            return Log(stream) if path.name == "backend-runtime.log" else stream

        monkeypatch.setattr(Path, "open", opened)
    original_write = native.write_json
    if cleanup == "receipt":

        def write(path, value):
            if path.name == "backend-lifecycle.json" and value.get("phase") == "backend-cleanup":
                raise OSError("explicit synthetic receipt error")
            return original_write(path, value)

        monkeypatch.setattr(native, "write_json", write)
    body_failure = LookupError("original body error")
    with pytest.raises((RuntimeError, LookupError, OSError)) as raised:
        with native.running_backend(
            "fastapiadmin", tmp_path, {"SERVER_PORT": "18080"}, tmp_path / "report"
        ):
            if primary == "body":
                raise body_failure
            assert primary is None
    assert stopped == [process.pid]
    if primary == "exit":
        assert str(raised.value) == "Native backend exited; inspect backend-runtime.log"
    elif primary == "body":
        assert raised.value is body_failure
    elif cleanup == "occupied":
        assert "port remained occupied" in str(raised.value)
    else:
        assert isinstance(raised.value, OSError)
    if primary:
        assert any("cleanup also failed" in note for note in raised.value.__notes__)
    if cleanup != "receipt":
        report = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert report["cleanup_failure"]
        assert report["port_released"] is (cleanup == "close")
        assert report["returncode_before_cleanup"] == (42 if primary == "exit" else None)
        if primary:
            assert report["failure"]["phase"] == (
                "backend-readiness" if primary == "exit" else "backend-running"
            )


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/net/tcp").is_file(), reason="Linux /proc ownership facts"
)
def test_real_failed_child_retains_exit_code_and_never_kills_new_foreign_listener(
    tmp_path, monkeypatch
):
    with socket.socket() as foreign:
        foreign.bind(("127.0.0.1", 0))
        port = foreign.getsockname()[1]
    original = subprocess.Popen
    foreign = socket.socket()

    def start(command, **kwargs):
        child = original(
            [sys.executable, "-c", "print('specific child startup failure'); raise SystemExit(42)"],
            **kwargs,
        )
        child.wait(timeout=10)
        foreign.bind(("127.0.0.1", port))
        foreign.listen()
        return child

    monkeypatch.setattr(native.subprocess, "Popen", start)
    monkeypatch.setattr(
        native.os, "killpg", lambda *args: pytest.fail("foreign process must survive")
    )
    times = itertools.count(0, 6)
    monkeypatch.setattr(native.time, "monotonic", lambda: next(times))
    try:
        with pytest.raises(RuntimeError, match="Native backend exited") as raised:
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": str(port)}, tmp_path / "report"
            ):
                pytest.fail("child exited before readiness")
        result = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert result["returncode_before_cleanup"] == result["returncode"] == 42
        assert result["port_released"] is False
        assert result["port_state_after_cleanup"]["owned_listener"] is False
        assert result["port_state_after_cleanup"]["local_port_state_counts"]["0A"] == 1
        assert result["port_state_after_cleanup"]["owned_group_pids"] == []
        assert foreign.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) == 1
        assert "specific child startup failure" in (
            tmp_path / "report/backend-runtime.log"
        ).read_text(encoding="utf-8")
        assert "port_released=False" in raised.value.__notes__[0]
    finally:
        foreign.close()


def test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset(
    tmp_path, monkeypatch
):
    class Process:
        pid = 12345678

        def poll(self):
            return 42

    def start(command, **kwargs):
        kwargs["stdout"].write(b"failure from this attempt\n")
        return Process()

    monkeypatch.setattr(native.subprocess, "Popen", start)
    monkeypatch.setattr(native, "loopback_port_bindable", lambda port: True)
    monkeypatch.setattr(native, "backend_port_state", lambda *args: {"observable": False})
    for attempt in (1, 2):
        with pytest.raises(RuntimeError, match="Native backend exited"):
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": "18080"}, tmp_path / "report"
            ):
                pytest.fail("explicit exited process fake")
        result = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert result["startup_attempt"] == attempt
        assert result["runtime_log_start_bytes"] == (attempt - 1) * len(
            b"failure from this attempt\n"
        )
