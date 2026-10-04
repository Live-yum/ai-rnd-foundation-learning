"""Portable real pipes and simulated Windows backpressure; no Docker certification."""

import errno
import hashlib
import json
import selectors
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

import pytest

from workbench import capability_browser_isolation as isolation

IMAGE = "sha256:" + "a" * 64
NAME = "rnd-browser-" + "b" * 32


@pytest.fixture(autouse=True)
def no_pipe_selectors(monkeypatch):
    # Windows select accepts sockets only. Exercise every path with selectors
    # forbidden, including success: converting WinError to a failure cannot pass.
    def unavailable(*args, **kwargs):
        pytest.fail("Anonymous pipes must not use Windows socket-only selectors")

    monkeypatch.setattr(selectors, "DefaultSelector", unavailable)

    def no_threads(*args, **kwargs):
        pytest.fail("Bounded pipe I/O must not create uncancellable helper threads")

    monkeypatch.setattr(threading.Thread, "start", no_threads)


@pytest.fixture
def child_processes():
    before = set(threading.enumerate())
    processes = []
    real_popen = subprocess.Popen

    def launch(script, **kwargs):
        process = real_popen(
            [sys.executable, "-I", "-S", "-c", script],
            **kwargs,
        )
        processes.append(process)
        return process

    yield launch, processes
    for process in processes:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()
    assert not set(threading.enumerate()) - before


def read_all(stream, deadline):
    output = bytearray()
    while chunk := isolation._read_pipe(stream, deadline, "test pipe deadline"):
        output.extend(chunk)
    return bytes(output)


def test_real_pipe_transfers_large_binary_payload_and_eof(child_processes):
    launch, _ = child_processes
    body = bytes(range(256)) * 8192
    process = launch(
        "import hashlib,sys; data=sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(hashlib.sha256(data).digest()); sys.stdout.flush()",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    isolation._write_pipe(process.stdin, body, deadline)
    process.stdin.close()
    assert read_all(process.stdout, deadline) == hashlib.sha256(body).digest()
    assert process.wait(timeout=5) == 0


@pytest.mark.parametrize("direction", ["read", "write"])
def test_real_unresponsive_pipe_honors_deadline(child_processes, direction):
    launch, _ = child_processes
    process = launch(
        "import time; time.sleep(30)",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    started = time.monotonic()
    deadline = started + 0.15
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "write":
            isolation._write_pipe(process.stdin, b"x" * 2_000_000, deadline)
        else:
            isolation._read_pipe(process.stdout, deadline, "test read deadline")
    assert time.monotonic() - started < 2
    assert process.poll() is None


def test_real_closed_read_end_is_broken_pipe_not_timeout(child_processes):
    launch, _ = child_processes
    process = launch(
        "pass", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    assert process.wait(timeout=5) == 0
    with pytest.raises(BrokenPipeError):
        isolation._write_pipe(process.stdin, b"not delivered", time.monotonic() + 5)
    assert isolation._read_pipe(process.stdout, time.monotonic() + 5, "deadline") == b""


@pytest.fixture
def simulated_pipes(monkeypatch):
    state = SimpleNamespace(now=100.0, sleeps=[], modes=[], reads=[], writes=[])

    def sleep(seconds):
        assert 0 < seconds <= isolation.PIPE_POLL_INTERVAL
        state.sleeps.append(seconds)
        state.now += seconds

    def operation(events):
        event = events.pop(0)
        if isinstance(event, Exception):
            raise event
        return event

    def read(fd, size):
        assert fd == 17 and size == isolation.PIPE_CHUNK
        return operation(state.reads)

    def write(fd, data):
        assert fd == 17 and 0 < len(data) <= isolation.PIPE_CHUNK
        state.attempts.append(bytes(data))
        return operation(state.writes)

    state.attempts = []
    monkeypatch.setattr(
        isolation, "time", SimpleNamespace(monotonic=lambda: state.now, sleep=sleep)
    )
    monkeypatch.setattr(
        isolation,
        "os",
        SimpleNamespace(
            set_blocking=lambda fd, flag: state.modes.append((fd, flag)), read=read, write=write
        ),
    )
    return state, SimpleNamespace(fileno=lambda: 17)


def test_simulated_windows_partial_zero_and_full_pipe_writes(simulated_pipes):
    state, stream = simulated_pipes
    state.writes = [2, 0, BlockingIOError(errno.EAGAIN, "full pipe"), 1, 3]
    isolation._write_pipe(stream, b"abcdef", 101)
    assert state.modes == [(17, False)]
    assert state.attempts == [b"abcdef", b"cdef", b"cdef", b"cdef", b"def"]
    assert len(state.sleeps) == 2


def test_simulated_windows_empty_pipe_is_not_eof(simulated_pipes):
    state, stream = simulated_pipes
    state.reads = [BlockingIOError(errno.EAGAIN, "empty pipe"), b"partial", b""]
    assert isolation._read_pipe(stream, 101, "deadline") == b"partial"
    assert isolation._read_pipe(stream, 101, "deadline") == b""
    assert state.modes == [(17, False), (17, False)]
    assert len(state.sleeps) == 1


@pytest.mark.parametrize("direction", ["read", "write", "zero-write"])
def test_simulated_blocked_pipe_never_extends_absolute_deadline(simulated_pipes, direction):
    state, stream = simulated_pipes
    state.reads = [BlockingIOError(errno.EAGAIN, "empty")] * 40
    state.writes = [0 if direction == "zero-write" else BlockingIOError(errno.EAGAIN, "full")] * 40
    deadline = state.now + 0.025
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, deadline, "deadline")
        else:
            isolation._write_pipe(stream, b"x", deadline)
    assert state.now == deadline
    assert sum(state.sleeps) == pytest.approx(0.025)


@pytest.mark.parametrize("direction", ["read", "write"])
def test_simulated_expired_deadline_does_not_attempt_io(simulated_pipes, direction):
    state, stream = simulated_pipes
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, state.now, "deadline")
        else:
            isolation._write_pipe(stream, b"x", state.now)
    assert state.attempts == state.sleeps == []


@pytest.mark.parametrize("direction", ["read", "write"])
@pytest.mark.parametrize("code", [errno.EBADF, errno.EIO, errno.EPIPE])
def test_simulated_real_pipe_errors_propagate(simulated_pipes, direction, code):
    state, stream = simulated_pipes
    error = OSError(code, "genuine pipe failure")
    state.reads = state.writes = [error]
    with pytest.raises(OSError) as raised:
        if direction == "read":
            isolation._read_pipe(stream, 101, "deadline")
        else:
            isolation._write_pipe(stream, b"x", 101)
    assert raised.value is error
    assert not state.sleeps


def setup_worker(monkeypatch, child_processes, script):
    launch, processes = child_processes
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout=b"[{}]")

    monkeypatch.setattr(isolation.subprocess, "run", run)
    monkeypatch.setattr(isolation.subprocess, "Popen", lambda args, **kw: launch(script, **kw))
    monkeypatch.setattr(isolation, "require_worker_inspection", lambda *args: {})
    monkeypatch.setattr(isolation, "require_image_sources", lambda *args: {})
    return calls, processes


def assert_worker_cleaned(calls, processes):
    assert len(processes) == 1
    assert processes[0].poll() is not None
    assert processes[0].stdin.closed and processes[0].stdout.closed
    creates = [args for args in calls if "create" in args]
    removes = [args for args in calls if "rm" in args]
    assert len(creates) == len(removes) == 1
    name = creates[0][creates[0].index("--name") + 1]
    assert removes[0] == [*isolation.DOCKER, "rm", "-f", name]


def test_real_worker_success_with_large_bidirectional_frames(monkeypatch, child_processes):
    script = """
import base64, hashlib, json, sys
request = json.loads(sys.stdin.buffer.readline())
assert request['token'] == ''
assert request['url'] == 'http://127.0.0.1:18080'
assert len(request['padding']) == 800000
body = bytes(range(256)) * 8192
frame = {'type':'request', 'id':1, 'method':'POST', 'path':'/large',
         'headers':{}, 'body':base64.b64encode(body).decode()}
sys.stdout.write(json.dumps(frame) + '\\n')
sys.stdout.flush()
response = json.loads(sys.stdin.buffer.readline())
assert response['id'] == 1
assert base64.b64decode(response['body']) == body
report = {'digest':hashlib.sha256(body).hexdigest()}
sys.stdout.write(json.dumps({'type':'report', 'report':report, 'exit_code':0}) + '\\n')
sys.stdout.flush()
"""
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    relayed = []

    def relay(client, frame, *, deadline):
        assert client.headers["x-daytona-preview-token"] == "controller-only-token"
        assert deadline > time.monotonic()
        relayed.append(frame)
        return {"type": "response", "id": 1, "body": frame["body"]}, 4 * 1024 * 1024

    monkeypatch.setattr(isolation, "relay_request", relay)
    report, status = isolation.execute_worker(
        {"padding": "x" * 800000}, "http://127.0.0.1:3456", "controller-only-token", 15, image=IMAGE
    )
    assert status == 0
    assert json.loads(report) == {"digest": hashlib.sha256(bytes(range(256)) * 8192).hexdigest()}
    assert len(relayed) == 1
    assert all("controller-only-token" not in str(args) for args in calls)
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize(
    ("mode", "script", "error", "message"),
    [
        ("blocked-input", "import time; time.sleep(30)", TimeoutError, "pipe deadline"),
        ("eof", "import sys; sys.stdin.readline()", ValueError, "Incomplete"),
        (
            "partial-eof",
            "import sys; sys.stdin.readline(); sys.stdout.write('{'); sys.stdout.flush()",
            ValueError,
            "Incomplete",
        ),
        (
            "partial-stall",
            "import sys,time; sys.stdin.readline(); sys.stdout.write('{'); "
            "sys.stdout.flush(); time.sleep(30)",
            TimeoutError,
            "worker deadline",
        ),
    ],
)
def test_real_worker_pipe_failures_cleanup(
    monkeypatch, child_processes, mode, script, error, message
):
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    payload = {"padding": "x" * 800000} if mode == "blocked-input" else {}
    with pytest.raises(error, match=message):
        isolation.execute_worker(payload, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize("mode", ["success", "oversized", "nonzero", "timeout"])
def test_real_provenance_pipe_bounds_and_cleanup(monkeypatch, child_processes, mode):
    launch, processes = child_processes
    scripts = {
        "success": "import sys; sys.stdout.buffer.write(bytes(range(256))*1000)",
        "oversized": "import sys; sys.stdout.buffer.write(b'x'*600000); sys.stdout.flush()",
        "nonzero": "import sys; sys.stdout.write('partial'); sys.exit(2)",
        "timeout": "import time; time.sleep(30)",
    }
    monkeypatch.setattr(
        isolation.subprocess, "Popen", lambda args, **kw: launch(scripts[mode], **kw)
    )
    if mode == "timeout":
        real_read = isolation._read_pipe
        deadlines = []

        def read(stream, deadline, message):
            deadlines.append(deadline)
            return real_read(stream, min(deadline, time.monotonic() + 0.1), message)

        monkeypatch.setattr(isolation, "_read_pipe", read)
    if mode == "success":
        assert isolation._image_file_archive(NAME, "/source") == bytes(range(256)) * 1000
    else:
        error, message = {
            "oversized": (ValueError, "too large"),
            "nonzero": (ValueError, "unavailable"),
            "timeout": (TimeoutError, "timed out"),
        }[mode]
        with pytest.raises(error, match=message):
            isolation._image_file_archive(NAME, "/source")
    assert len(processes) == 1
    assert processes[0].poll() is not None and processes[0].stdout.closed


def test_read_and_write_requests_are_chunk_bounded(simulated_pipes):
    state, stream = simulated_pipes
    body = b"x" * (2 * isolation.PIPE_CHUNK + 7)
    state.writes = [isolation.PIPE_CHUNK, isolation.PIPE_CHUNK, 7]
    isolation._write_pipe(stream, body, 101)
    assert b"".join(state.attempts) == body
    assert max(map(len, state.attempts)) == isolation.PIPE_CHUNK


@pytest.mark.parametrize("direction", ["read", "write"])
def test_progress_does_not_reset_or_overrun_absolute_deadline(
    monkeypatch, simulated_pipes, direction
):
    state, stream = simulated_pipes
    deadline = state.now + 0.01

    def slow_read(fd, size):
        state.now = deadline
        return b"arrived too late"

    def slow_write(fd, data):
        state.now = deadline
        return len(data)

    monkeypatch.setattr(isolation.os, "read", slow_read)
    monkeypatch.setattr(isolation.os, "write", slow_write)
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, deadline, "deadline")
        else:
            isolation._write_pipe(stream, b"sent too late", deadline)
    assert state.sleeps == []


def test_real_blocked_reply_uses_original_deadline_and_cleans_up(monkeypatch, child_processes):
    script = (
        "import sys,time; sys.stdin.readline(); "
        'print(\'{"type":"request","id":1}\', flush=True); time.sleep(30)'
    )
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    monkeypatch.setattr(
        isolation, "relay_request", lambda *a, **k: ({"body": "x" * 900000}, 900000)
    )
    deadlines = []
    real_write = isolation._write_pipe

    def write(stream, data, deadline):
        deadlines.append(deadline)
        return real_write(stream, data, deadline)

    monkeypatch.setattr(isolation, "_write_pipe", write)
    with pytest.raises(TimeoutError, match="pipe deadline"):
        isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert len(deadlines) == 2 and deadlines[0] == deadlines[1]
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize("operation", ["worker", "provenance"])
def test_final_process_wait_never_adds_minimum_grace(monkeypatch, operation):
    state = SimpleNamespace(now=100.0, waits=[], closed=[])
    streams = {
        name: SimpleNamespace(close=lambda name=name: state.closed.append(name))
        for name in ("stdin", "stdout")
    }
    process = SimpleNamespace(
        **streams,
        poll=lambda: 0,
        wait=lambda *, timeout: state.waits.append(timeout) or 0,
    )
    monkeypatch.setattr(isolation, "time", SimpleNamespace(monotonic=lambda: state.now))
    monkeypatch.setattr(isolation.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(
        isolation.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=b"[{}]")
    )
    monkeypatch.setattr(isolation, "require_worker_inspection", lambda *a: {})
    monkeypatch.setattr(isolation, "require_image_sources", lambda *a: {})
    monkeypatch.setattr(isolation, "_write_pipe", lambda *a: None)
    frames = [b'{"type":"report","report":{},"exit_code":0}\n', b""]

    def read(stream, deadline, message):
        state.now = deadline - 0.025
        return frames.pop(0) if operation == "worker" else b""

    monkeypatch.setattr(isolation, "_read_pipe", read)
    if operation == "worker":
        assert isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE) == (
            b"{}",
            0,
        )
        assert state.closed == ["stdin", "stdout"]
    else:
        assert isolation._image_file_archive(NAME, "/source") == b""
        assert state.closed == ["stdout"]
    assert state.waits == pytest.approx([0.025, 5])


def test_real_eof_before_exit_still_times_out_and_cleans_up(monkeypatch, child_processes):
    script = (
        "import os,sys,time; sys.stdin.readline(); "
        'print(\'{"type":"report","report":{},"exit_code":0}\', flush=True); '
        "os.close(sys.stdout.fileno()); time.sleep(30)"
    )
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    with pytest.raises(subprocess.TimeoutExpired):
        isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert_worker_cleaned(calls, processes)
