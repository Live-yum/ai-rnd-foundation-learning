"""Locked SDK and real HTTP framing, with only the network backend replaced."""

import json
import ssl
from types import SimpleNamespace

import httpcore
import httpx
import pytest
from conftest import new_run
from httpcore._backends.mock import MockBackend, MockStream
from test_native_schema import invoke, model_gateway, no_network, response  # noqa: F401

from scripts import live_test_client as client
from workbench.coding.timing import HTTP_TRACE_TIMES, http_trace_receipt, timing_receipts
from workbench.llm import ModelFailure


class MemoryBackend(MockBackend):
    def __init__(self, clock, failure=None):
        self.clock, self.failure = clock, failure
        self.streams = []
        self.bodies = []

    def connect_tcp(self, host, port, timeout=None, **kwargs):
        assert host == "fixture.invalid" and port == 443 and timeout == 60
        self.clock[0] += 1
        if self.failure == "connect":
            raise httpcore.ConnectTimeout("private-connect-detail")
        backend = self
        content = '{"operation":"submit","edits":null}'
        if self.failure == "schema":
            content = '{"operation":"submit"}'
        raw = response(content).content
        wire = b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(raw)).encode() + b"\r\n\r\n" + raw

        class Stream(MockStream):
            def start_tls(self, ssl_context, server_hostname=None, timeout=None):
                assert ssl_context.check_hostname and ssl_context.verify_mode == ssl.CERT_REQUIRED
                assert server_hostname == "fixture.invalid" and timeout == 60
                backend.clock[0] += 2
                if backend.failure == "tls":
                    self.close()
                    raise httpcore.ConnectTimeout("private-tls-detail")
                return self

            def write(self, buffer, timeout=None):
                assert timeout == 60
                backend.clock[0] += 0.25
                if buffer.startswith(b"{"):
                    backend.bodies.append(json.loads(buffer))
                    if backend.failure == "request_body":
                        raise httpcore.WriteTimeout("private-upload-detail")

            def read(self, max_bytes, timeout=None):
                assert timeout == 60
                backend.clock[0] += 60 if backend.failure == "response_headers" else 4
                if backend.failure == "response_headers":
                    raise httpcore.ReadTimeout("private-read-detail")
                return super().read(max_bytes, timeout)

        stream = Stream([wire])
        self.streams.append(stream)
        return stream

    def connect_unix_socket(self, *args, **kwargs):
        pytest.fail("unexpected alternate transport")

    def sleep(self, seconds):
        pytest.fail("HTTP transport must not add retries")


def transport(monkeypatch, failure=None):
    clock = [100.0]
    monkeypatch.setattr(client, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    value = client.TestServiceTransport("https://fixture.invalid/v1")
    backend = MemoryBackend(clock, failure)
    # Keep the actual pinned HTTPTransport, pool, HTTP/1.1 parser and trace hooks.
    value.inner._pool._network_backend = backend
    return value, backend


@pytest.mark.parametrize(
    "failure", [None, "connect", "tls", "request_body", "response_headers", "schema"]
)
def test_actual_sdk_reports_transport_boundary_without_changing_guards(store, monkeypatch, failure):
    value, backend = transport(monkeypatch, failure)
    model = model_gateway(store, lambda _: pytest.fail("unused HTTP mock"))
    model.transport = value
    run = new_run(store)
    try:
        if failure:
            with pytest.raises(ModelFailure):
                invoke(model, run)
        else:
            assert invoke(model, run).operation == "submit"
    finally:
        value.close()
    count = 1 if failure in (None, "schema") else 2
    assert value.calls == store.get_run(run)["model_calls"] == count
    assert value.responses == (1 if failure in (None, "schema") else 0)
    receipts = timing_receipts(value.timings, attempts=True)
    assert len(receipts) == count
    for receipt in receipts:
        trace = receipt["http_trace"]
        assert trace["connect_started_seconds"] == 0
        assert trace["event_count"] > 0
        assert trace["failed_phase"] == (failure if failure not in (None, "schema") else None)
        assert receipt["read_timeout_seconds"] == 60
        if failure == "response_headers":
            assert trace["request_body_complete_seconds"] is not None
            assert trace["response_headers_started_seconds"] is not None
            assert trace["response_headers_complete_seconds"] is None
            assert receipt["headers_seconds"] is None and receipt["response_bytes"] == 0
    assert "private" not in json.dumps(receipts)
    assert "offline-secret" not in json.dumps(receipts)
    assert all(stream._closed for stream in backend.streams)
    if failure == "response_headers":
        # The real httpcore pool closes a timed-out connection; attempt two is fresh.
        assert len(backend.streams) == 2
    if failure == "schema":
        assert store.model_records(run)[0]["code"] == "native_schema_violation"
    for body in backend.bodies:
        assert body["response_format"]["type"] == "json_schema"
        assert body["response_format"]["json_schema"]["strict"] is True
        assert body["stream"] is False and body["max_completion_tokens"] == 8192
        assert "tools" not in body


@pytest.mark.parametrize("reject", [False, True])
def test_existing_trace_and_lazy_response_body_semantics_are_preserved(monkeypatch, reject):
    value, backend = transport(monkeypatch)
    events = []
    failure = RuntimeError("private-original-callback-error")

    def previous(name, info):
        events.append(name)
        if reject and name == "http11.send_request_body.started":
            raise failure

    request = httpx.Request(
        "POST",
        "https://fixture.invalid/v1/chat/completions",
        content=b"{}",
        extensions={
            "trace": previous,
            "timeout": dict.fromkeys(("connect", "read", "write", "pool"), 60),
        },
    )
    try:
        if reject:
            with pytest.raises(RuntimeError) as caught:
                value.handle_request(request)
            assert caught.value is failure
        else:
            result = value.handle_request(request)
            assert request.extensions["trace"] is previous
            assert "http11.receive_response_body.started" not in events
            result.read()
            result.close()
            assert "http11.receive_response_body.started" in events
    finally:
        value.close()
    assert request.extensions["trace"] is previous
    assert all(stream._closed for stream in backend.streams)
    assert "private" not in json.dumps(timing_receipts(value.timings, attempts=True))


def test_trace_projection_drops_unknown_phases_values_and_info():
    facts = {"event_count": 0, "failed_phase": None}

    class Poison:
        def __repr__(self):
            pytest.fail("trace info was inspected")

    callback = client.phase_trace(facts, 0, None)
    callback("http11.receive_response_headers.failed", Poison())
    callback("private-event.started", Poison())
    assert facts["failed_phase"] == "response_headers" and facts["event_count"] == 1
    for poison in (True, -1, 65, "private", {}, [], float("nan"), float("inf")):
        data = http_trace_receipt(
            {
                **dict.fromkeys(HTTP_TRACE_TIMES, poison),
                "event_count": poison,
                "failed_phase": "private",
                "info": Poison(),
            }
        )
        assert data["event_count"] is None and data["failed_phase"] is None
        assert "private" not in json.dumps(data)
    assert len(timing_receipts([{"http_trace": facts}] * 40, attempts=True)) == 32
