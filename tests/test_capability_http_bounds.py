"""Untrusted candidate HTTP responses cannot trigger controller decompression.

Data-only MockTransport checks: no candidate code or external requests run.
"""

import gzip

import httpx
import pytest

from workbench.capability_contracts import HttpStep
from workbench.capability_verification import CheckFailure, run_steps


class Body(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks = chunks
        self.reads = 0
        self.closed = False

    def __iter__(self):
        for chunk in self.chunks:
            self.reads += 1
            yield chunk

    def close(self):
        self.closed = True


def run(body, *, response_headers=None, step_headers=None, equals=None):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, headers=response_headers, stream=body)

    with httpx.Client(
        base_url="http://candidate.invalid",
        transport=httpx.MockTransport(handler),
        headers={"Accept-Encoding": "gzip, deflate"},
    ) as client:
        result = run_steps(
            client,
            [HttpStep(path="/", status=200, headers=step_headers or {}, equals=equals or {})],
            {},
        )
    return result, requests


@pytest.mark.parametrize("encoding", ["gzip", "deflate", "br", "zstd", "identity, gzip", ""])
def test_compressed_or_unknown_encoding_rejected_before_first_body_read(encoding):
    body = Body([gzip.compress(b"A" * (8 * 1024 * 1024))])
    with pytest.raises(CheckFailure, match="identity"):
        run(body, response_headers={"Content-Encoding": encoding})
    assert body.reads == 0
    assert body.closed


@pytest.mark.parametrize("encoding", [None, "identity", " Identity "])
def test_identity_json_and_case_insensitive_request_header_override(encoding):
    body = Body([b'{"ok":', b"true}"])
    result, requests = run(
        body,
        response_headers={} if encoding is None else {"Content-Encoding": encoding},
        step_headers={"aCcEpT-EnCoDiNg": "gzip", "X-Product-Test": "value"},
        equals={"$.ok": True},
    )
    assert result[0]["passed"] is True
    assert requests[0].headers.get_list("accept-encoding") == ["identity"]
    assert requests[0].headers["x-product-test"] == "value"
    assert body.closed


def test_exact_two_megabyte_identity_body_is_allowed():
    body = Body([b"A" * 1_000_000, b"B" * 1_000_000])
    result, _ = run(body)
    assert result[0]["passed"] is True
    assert body.closed


@pytest.mark.parametrize("chunks", [[b"A" * 2_000_001], [b"A" * 2_000_000, b"B"]])
def test_raw_budget_rejects_overflow_and_stops_consuming(chunks):
    body = Body([*chunks, b"must not be consumed"])
    with pytest.raises(CheckFailure, match="2MB"):
        run(body)
    assert body.reads == len(chunks)
    assert body.closed
