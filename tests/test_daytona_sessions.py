import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

from workbench.daytona_sessions import harden_toolbox_transport, run_session_command


class Process:
    def __init__(self, statuses=(None, None, 0), failure=None):
        self.statuses = iter(statuses)
        self.calls = []
        self.failure = failure

    def create_session(self, session):
        self.calls.append("create")

    def execute_session_command(self, session, request, **kwargs):
        self.calls.append("submit")
        assert request.run_async is True
        assert request.command == "cd '/tmp/a b' && python 'a;b.py'"
        if self.failure:
            raise self.failure
        return SimpleNamespace(cmd_id="cmd-1")

    def get_session_command(self, *args):
        self.calls.append("poll")
        return SimpleNamespace(exit_code=next(self.statuses))

    def get_session_command_logs(self, *args):
        self.calls.append("logs")
        return SimpleNamespace(output="actual command output")

    def exec(self, *args, **kwargs):
        pytest.fail("Synchronous fallback would repeat the mutation")


def test_single_submission_polls_to_completion_and_records_identity():
    process = Process()
    evidence = {}
    result = run_session_command(
        process, ["python", "a;b.py"], "/tmp/a b", 10, evidence, poll_seconds=0
    )
    assert result.exit_code == 0
    assert result.result == "actual command output"
    assert process.calls == ["create", "submit", "poll", "poll", "poll", "logs"]
    assert evidence["mode"] == "async-session"
    assert evidence["session_id"].startswith("rnd-check-")
    assert evidence["command_id"] == "cmd-1"


def test_lost_submission_never_falls_back_or_submits_twice():
    process = Process(failure=ConnectionError("response lost after server execution"))
    evidence = {}
    with pytest.raises(ConnectionError):
        run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, evidence)
    assert process.calls == ["create", "submit"]
    assert evidence["session_id"]
    assert "command_id" not in evidence


def test_timeout_has_no_resubmission_or_log_fetch(monkeypatch):
    from workbench import daytona_sessions

    ticks = iter([0, 0, 0, 0, 11])
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: next(ticks))
    process = Process()
    with pytest.raises(TimeoutError):
        run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {})
    assert process.calls == ["create", "submit"]
    assert daytona_sessions._DEADLINE.get() is None


def test_nonzero_command_is_returned_without_retry():
    process = Process(statuses=[9])
    assert run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {}).exit_code == 9
    assert process.calls == ["create", "submit", "poll", "logs"]


def test_real_pinned_transport_does_not_replay_lost_post():
    from daytona.internal.urllib3_retry import RemoteDisconnectedRetry
    from daytona_toolbox_api_client import ApiClient, Configuration

    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            calls.append("server-executed")
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    config = Configuration()
    config.retries = RemoteDisconnectedRetry(total=3)
    api = ApiClient(config)
    client = SimpleNamespace(_toolbox_api_client=api)
    harden_toolbox_transport(client)
    try:
        with pytest.raises(Exception):
            api.rest_client.request(
                "POST",
                f"http://127.0.0.1:{server.server_port}/execute",
                headers={"Content-Type": "application/json"},
                body={},
            )
        assert calls == ["server-executed"]
        assert api.rest_client.pool_manager.connection_pool_kw["retries"].total == 0
    finally:
        api.rest_client.pool_manager.clear()
        server.shutdown()
        server.server_close()
        worker.join()


def test_missing_timeouts_bounded_and_session_deadline_applies(monkeypatch):
    from workbench import daytona_sessions

    seen = []
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda *args, **kwargs: seen.append(kwargs["_request_timeout"]),
    )
    harden_toolbox_transport(SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest)))
    rest.request("GET", "local")
    rest.request("POST", "local", _request_timeout=120)
    token = daytona_sessions._DEADLINE.set(105)
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: 100)
    try:
        rest.request("GET", "local")
        rest.request("POST", "local", _request_timeout=20)
        rest.request("GET", "local", _request_timeout=(None, None))
    finally:
        daytona_sessions._DEADLINE.reset(token)
    assert seen == [30, 120, 5, 5, 5]


def test_command_can_run_beyond_gateway_idle_budget_with_short_polls(monkeypatch):
    from workbench import daytona_sessions

    clock = [0.0]
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        daytona_sessions.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    process = Process(statuses=[None, None, None, None, 0])
    result = run_session_command(
        process, ["python", "a;b.py"], "/tmp/a b", 1000, {}, poll_seconds=100
    )
    assert clock[0] == 400
    assert result.exit_code == 0
    assert process.calls.count("submit") == 1
    assert process.calls.count("poll") == 5
    assert process.calls.count("logs") == 1


def test_split_logs_are_preserved_and_bounded():
    process = Process(statuses=[1])
    process.get_session_command_logs = lambda *args: SimpleNamespace(
        output=None, stdout="first\n", stderr="error" + "x" * 9000
    )
    result = run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {})
    assert result.exit_code == 1
    assert result.result.startswith("first\nerror")
    assert len(result.result) == 8000
