"""Actual pinned SDK multipart reader; only the HTTP peer is a local protocol fixture."""

import json
from types import SimpleNamespace

import httpx
import pytest
from daytona._sync.filesystem import FileSystem

from workbench.generator import PrerequisiteError
from workbench.sandbox import MAX_RUNTIME_REPORT_BYTES, REMOTE, read_runtime_report

REPORT = {"passed": True, "http": True, "restart": True}


class TrackedStream(httpx.SyncByteStream):
    def __init__(self, body):
        self.body = body
        self.closed = False
        self.read_bytes = 0

    def __iter__(self):
        for offset in range(0, len(self.body), 4096):
            chunk = self.body[offset : offset + 4096]
            self.read_bytes += len(chunk)
            yield chunk

    def close(self):
        self.closed = True


def multipart(payload, *, complete=True):
    body = (
        b'--rnd-boundary\r\nContent-Disposition: form-data; name="file"; '
        b'filename="/tmp/rnd-verification/runtime.json"\r\n'
        b"Content-Type: application/octet-stream\r\n\r\n" + payload
    )
    return body + (b"\r\n--rnd-boundary--\r\n" if complete else b"")


def sdk_reader(payload, *, complete=True, status=200):
    stream = TrackedStream(multipart(payload, complete=complete))

    def serialize(**kwargs):
        assert kwargs["download_files"].paths == [REMOTE + "/runtime.json"]
        return (
            "POST",
            "http://127.0.0.1:3000/download",
            {},
            {"paths": kwargs["download_files"].paths},
        )

    def handler(request):
        assert request.url.host == "127.0.0.1"
        assert request.extensions["timeout"]["read"] == 7
        assert request.extensions["timeout"]["write"] == 7
        return httpx.Response(
            status,
            headers={"Content-Type": "multipart/form-data; boundary=rnd-boundary"},
            stream=stream,
        )

    http = httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)
    return FileSystem(SimpleNamespace(_download_files_serialize=serialize), http), http, stream


def test_actual_sdk_stream_timeout_and_report_are_consumed_and_closed():
    filesystem, http, stream = sdk_reader(json.dumps(REPORT).encode())
    with http:
        assert read_runtime_report(filesystem, 7) == REPORT
    assert stream.closed


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"broken",
        b"[]",
        b"null",
        b"true",
        b'"text"',
        b"{}",
        b'{"passed":1,"http":true,"restart":true}',
        b"\xff",
    ],
)
def test_invalid_or_nonobject_reports_never_pass(payload):
    filesystem, http, stream = sdk_reader(payload)
    with http, pytest.raises(Exception):
        read_runtime_report(filesystem, 7)
    assert stream.closed


def test_oversize_stops_reading_early_and_closes_real_sdk_stream():
    payload = b" " * (MAX_RUNTIME_REPORT_BYTES * 3)
    filesystem, http, stream = sdk_reader(payload)
    with http, pytest.raises(PrerequisiteError, match="报告过大"):
        read_runtime_report(filesystem, 7)
    assert stream.closed and stream.read_bytes < len(payload)


def test_valid_json_inside_truncated_multipart_is_not_a_success():
    filesystem, http, stream = sdk_reader(json.dumps(REPORT).encode(), complete=False)
    with http, pytest.raises(Exception, match="Truncated"):
        read_runtime_report(filesystem, 7)
    assert stream.closed


@pytest.mark.parametrize("status", [401, 403, 404, 500])
def test_http_failures_cannot_be_reported_as_passed(status):
    filesystem, http, stream = sdk_reader(json.dumps(REPORT).encode(), status=status)
    with http, pytest.raises(Exception):
        read_runtime_report(filesystem, 7)
    assert stream.closed
