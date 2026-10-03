"""Bound model text separately from repeated SSE metadata; no network access."""

import json
from contextlib import contextmanager

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from workbench.domain import ModelReview
from workbench.llm import ModelGateway
from workbench.model_protocol import (
    MAX_MODEL_CONTENT_BYTES,
    MAX_STREAM_WIRE_BYTES,
    AuditedEventStream,
    AuditedTransport,
    OutputContract,
    OutputFailure,
    stream_wire_limit,
)


class Chunks(httpx.SyncByteStream):
    def __init__(self, data):
        self.data, self.closed = data, False

    def __iter__(self):
        for offset in range(0, len(self.data), 65536):
            yield self.data[offset : offset + 65536]

    def close(self):
        self.closed = True


def audited_stream(body, tokens=8192):
    chunks = Chunks(body)
    response = httpx.Response(200, stream=chunks)
    contract = OutputContract("compatible", "json_object", "offline", {"max_output_tokens": tokens})
    audit = AuditedTransport(contract, httpx.MockTransport(lambda request: None))
    return AuditedEventStream(response, audit), audit, chunks


def frame(delta):
    return (
        b"data: "
        + json.dumps({"choices": [{"index": 0, "delta": delta, "finish_reason": None}]}).encode()
        + b"\n\n"
    )


@pytest.mark.parametrize("field", ["content", "reasoning_content"])
def test_cumulative_decoded_text_stays_bounded_despite_larger_wire_allowance(field):
    part = "x" * 2000
    body = frame({field: part}) * (MAX_MODEL_CONTENT_BYTES // len(part) + 1)
    stream, audit, chunks = audited_stream(body)
    with pytest.raises(OutputFailure) as caught:
        list(stream)
    assert caught.value.code == "response_too_large" and caught.value.retry is False
    assert audit.error is caught.value and chunks.closed
    assert stream.bytes_read < stream.wire_limit


@pytest.mark.parametrize("field", ["reasoning_content", "reasoning"])
@pytest.mark.parametrize("value", [["x" * 800_000], {"content": "x"}, 123, True])
def test_non_string_reasoning_cannot_bypass_decoded_content_budget(field, value):
    stream, audit, chunks = audited_stream(frame({field: value}) * 3)
    with pytest.raises(OutputFailure) as caught:
        list(stream)
    assert caught.value.code == "invalid_message" and caught.value.retry is False
    assert audit.error is caught.value and chunks.closed
    assert stream.content_bytes == 0


def test_unterminated_or_multiline_frame_cannot_accumulate_above_two_mb():
    for body in (
        b"data: " + b"x" * (MAX_MODEL_CONTENT_BYTES + 1),
        (b"data: " + b"x" * 2000 + b"\n") * 1001,
    ):
        stream, audit, chunks = audited_stream(body)
        with pytest.raises(OutputFailure) as caught:
            list(stream)
        assert caught.value.code == "response_too_large" and chunks.closed


def test_empty_comment_frames_cannot_bypass_total_wire_bound():
    stream, audit, chunks = audited_stream((b":" + b"x" * 1_000_000 + b"\n") * 3, tokens=1)
    with pytest.raises(OutputFailure) as caught:
        list(stream)
    assert caught.value.code == "stream_wire_limit" and caught.value.retry is False
    assert audit.error is caught.value and chunks.closed


def test_wire_allowance_depends_on_requested_tokens_and_has_hard_ceiling():
    assert stream_wire_limit(8192) == 10_388_608
    assert stream_wire_limit(128) == 2_131_072
    assert stream_wire_limit(393216) == MAX_STREAM_WIRE_BYTES == 64_000_000


def test_static_transport_guard_survives_sdk_boundary_in_audit():
    failure = OutputFailure("monetary_budget_exceeded", "fixed-safe-message")

    def blocked(request):
        raise failure

    contract = OutputContract("compatible", "json_object", "offline", {})
    audit = AuditedTransport(contract, httpx.MockTransport(blocked))
    with pytest.raises(OutputFailure):
        audit.handle_request(httpx.Request("POST", "https://offline.example"))
    assert audit.error is failure


def test_unexpected_adapter_exception_reports_class_without_raw_message(store, monkeypatch):
    secret = "private-adapter-exception-canary"
    store.settings.base_url = "https://offline.example"
    store.settings.model = "offline-model"
    store.settings.api_key = SecretStr(secret)

    @contextmanager
    def broken(*args, **kwargs):
        raise RuntimeError(secret)
        yield  # pragma: no cover

    monkeypatch.setattr("workbench.llm.structured_model", broken)
    run_id = new_run(store)
    gateway = ModelGateway(
        store.settings, store, httpx.MockTransport(lambda req: None), streaming=True
    )
    with pytest.raises(RuntimeError):
        gateway.complete(run_id, "review:unexpected", "JSON", {}, ModelReview)
    events = [event for event in store.events(run_id) if event["kind"] == "assistant_failed"]
    assert len(events) == 1
    diagnostic = events[0]["data"]["diagnostic"]
    assert diagnostic["code"] == "unexpected_model_error"
    assert diagnostic["details"] == [
        {"type": "RuntimeError", "path": [], "message": "模型适配器异常"}
    ]
    assert secret not in json.dumps(events)
