"""Cost/destination/receipt controls are tested only with explicit mock transports."""

import json
from decimal import Decimal

import httpx
import pytest

from scripts.ci_model_feedback import (
    ANSWER,
    ENDPOINT,
    MAX_CALLS,
    MAX_REQUEST_BYTES,
    ORIGINAL,
    PRICES,
    REPOSITORY,
    BoundedFeedbackTransport,
    SafeFailure,
    configuration,
    response_receipt,
    run_check,
    trusted_dispatch,
)
from workbench.domain import Requirement

KEY = "dummy-feedback-harness-key-never-real"


def configured(**values):
    return configuration(
        {
            "BASE_URL": ENDPOINT,
            "MODE": "deepseek-flash",
            "API_KEY": KEY,
            "APPROVED_MAX_CNY": "10",
            **values,
        }
    )


def request(**body):
    return httpx.Request(
        "POST",
        ENDPOINT + "/chat/completions",
        headers={"Authorization": "Bearer " + KEY},
        json={
            "model": "deepseek-flash",
            "messages": [{"role": "user", "content": "fixed JSON"}],
            "response_format": {"type": "json_object"},
            "max_tokens": 128,
            **body,
        },
    )


def mocked_transport(config, handler):
    transport = BoundedFeedbackTransport(config)
    transport.transport.close()
    transport.transport = httpx.MockTransport(handler)
    return transport


@pytest.mark.parametrize(
    "values",
    [
        {"BASE_URL": "https://evil.example"},
        {"BASE_URL": ENDPOINT + "/v1"},
        {"MODE": "unpriced-model"},
        {"API_KEY": ""},
        {"APPROVED_MAX_CNY": "NaN"},
        {"APPROVED_MAX_CNY": "Infinity"},
        {"APPROVED_MAX_CNY": "-1"},
        {"APPROVED_MAX_CNY": "11"},
        {"APPROVED_MAX_CNY": "0.01"},
    ],
)
def test_unapproved_configuration_fails_before_transport(values):
    with pytest.raises(SafeFailure):
        configured(**values)


def test_prices_are_allowlisted_and_full_worst_case_below_user_limit():
    assert set(PRICES) == {"deepseek-flash", "deepseek-v4-pro"}
    assert configured().maximum_cost() == Decimal("1.614848")
    assert configured(MODE="deepseek-v4-pro").maximum_cost() == Decimal("6.970752")
    assert KEY not in repr(configured())


def dispatch_context():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": "refs/heads/fix/model-feedback-history",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
    }


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_EVENT_NAME", "schedule"),
        ("GITHUB_REPOSITORY", "attacker/fork"),
        ("GITHUB_REF", "refs/heads/unreviewed"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("GITHUB_SHA", "not-a-sha"),
        ("REVIEWED_SHA", "b" * 40),
    ],
)
def test_only_manual_owner_repo_reviewed_branch_first_attempt_is_allowed(key, value):
    trusted_dispatch(dispatch_context())
    with pytest.raises(SafeFailure):
        trusted_dispatch({**dispatch_context(), key: value})


@pytest.mark.parametrize(
    "body",
    [
        {"model": "substitution"},
        {"response_format": None},
        {"max_tokens": 129},
        {"max_tokens": 0},
        {"max_tokens": True},
        {"max_tokens": None},
        {"max_tokens": 128, "max_completion_tokens": 128},
        {"messages": [{"role": "user", "content": "x" * MAX_REQUEST_BYTES}]},
    ],
)
def test_invalid_transport_scope_never_calls_provider(body):
    calls = []
    transport = mocked_transport(configured(), lambda req: calls.append(req) or httpx.Response(200))
    try:
        with pytest.raises(SafeFailure):
            transport.handle_request(request(**body))
        assert not calls and transport.calls == 0 and transport.reserved_cny == 0
    finally:
        transport.shutdown()


def test_call_count_phase_caps_and_reserved_money_are_enforced_before_requests():
    calls = []
    transport = mocked_transport(
        configured(),
        lambda req: calls.append(req) or httpx.Response(429, json={"error": {"message": KEY}}),
    )
    try:
        transport.handle_request(request())
        with pytest.raises(SafeFailure, match="request_count_limit"):
            transport.handle_request(request())
        for phase in ("initial_requirements", "corrected_requirements"):
            transport.phase = phase
            for _ in range(2):
                transport.handle_request(request(max_tokens=8192))
        assert len(calls) == transport.calls == MAX_CALLS
        assert 0 < transport.reserved_cny <= configured().maximum_cost()
        with pytest.raises(SafeFailure, match="request_count_limit"):
            transport.handle_request(request())
        assert KEY not in json.dumps(transport.receipts)
    finally:
        transport.shutdown()


def test_destination_and_credentials_cannot_be_replaced():
    calls = []
    transport = mocked_transport(configured(), lambda req: calls.append(req) or httpx.Response(200))
    try:
        for url, auth in (
            ("https://evil.example/chat/completions", KEY),
            (ENDPOINT + "/chat/completions", "other-key"),
        ):
            req = request()
            req.url = httpx.URL(url)
            req.headers["Authorization"] = "Bearer " + auth
            with pytest.raises(SafeFailure):
                transport.handle_request(req)
        assert not calls
    finally:
        transport.shutdown()


def test_network_failure_reserves_full_cost_and_is_not_retried_by_transport():
    calls = []

    def fail(req):
        calls.append(req)
        raise httpx.ConnectError(KEY, request=req)

    transport = mocked_transport(configured(), fail)
    try:
        with pytest.raises(httpx.ConnectError):
            transport.handle_request(request())
        assert len(calls) == transport.calls == 1 and transport.reserved_cny > 0
        assert transport.receipts[0]["transport_error"]
        assert KEY not in json.dumps(transport.receipts)
    finally:
        transport.shutdown()


def test_remaining_money_guard_blocks_before_network_even_under_call_limit():
    calls = []
    transport = mocked_transport(configured(), lambda req: calls.append(req) or httpx.Response(200))
    try:
        transport.reserved_cny = Decimal("10")
        with pytest.raises(SafeFailure, match="monetary_budget_exceeded"):
            transport.handle_request(request())
        assert not calls and transport.calls == 0
    finally:
        transport.shutdown()


def test_receipt_drops_provider_text_and_supports_streamed_usage():
    data = {
        "choices": [
            {"message": {"content": KEY, "reasoning_content": "private"}, "finish_reason": "stop"}
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 12,
            "total_tokens": 112,
            "secret": KEY,
        },
        "error": KEY,
    }
    for raw in (
        json.dumps(data).encode(),
        b"data: " + json.dumps(data).encode() + b"\n\ndata: [DONE]\n\n",
    ):
        result = response_receipt(200, raw)
        assert result == {
            "http_status": 200,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 100, "completion_tokens": 12, "total_tokens": 112},
        }
        assert KEY not in json.dumps(result)


def test_real_runtime_two_phase_signup_flow_has_no_generation_or_fake_gateway(tmp_path):
    calls = []

    def handle(req):
        body = json.loads(req.content)
        calls.append(body)
        if len(calls) == 1:
            content = '{"ok":true}'
        else:
            assert ORIGINAL in json.dumps(body, ensure_ascii=False)
            assert ANSWER in json.dumps(body, ensure_ascii=False)
            content = Requirement(
                summary=ORIGINAL,
                users=["参赛者", "管理员"],
                data_scope="shared",
                features=[ANSWER],
                acceptance=["参赛者仅可创建和维护本人报名，不能管理其他参赛者报名"],
            ).model_dump_json()
        return httpx.Response(
            200,
            json={
                "id": "offline-adapter",
                "object": "chat.completion",
                "created": 0,
                "model": "deepseek-flash",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 200},
            },
        )

    transport = mocked_transport(configured(), handle)
    try:
        result = run_check(configured(), transport, tmp_path)
        assert result["passed"], result
        assert (
            result["connection"]["ok"] and result["answer_preserved"] and result["scope_preserved"]
        )
        assert result["initial"]["gate_stage"] == "clarification"
        assert result["corrected"]["status"] == "WAITING_REQUIREMENTS"
        assert result["generation_absent"] and result["approvals"] == 0
        assert transport.phase_calls == {
            "connection": 1,
            "initial_requirements": 0,
            "corrected_requirements": 1,
        }
        assert KEY not in json.dumps(result)
        assert len(json.dumps(calls[-1]).encode()) < MAX_REQUEST_BYTES
    finally:
        transport.shutdown()


def test_failed_schema_run_retains_answer_and_exports_only_safe_diagnostic_paths(tmp_path):
    calls = []

    def handle(req):
        calls.append(req)
        content = '{"ok":true}' if len(calls) == 1 else json.dumps({"summary": 123, KEY: KEY})
        return httpx.Response(
            200,
            json={
                "id": "offline",
                "object": "chat.completion",
                "created": 0,
                "model": "deepseek-flash",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    transport = mocked_transport(configured(), handle)
    try:
        result = run_check(configured(), transport, tmp_path)
        assert not result["passed"] and result["answer_preserved"]
        assert result["corrected"]["status"] == "FAILED"
        assert transport.phase_calls["corrected_requirements"] == 2
        assert len(result["model_failures"]) == 2
        diagnostic = result["model_failures"][-1]
        assert diagnostic["phase"] == "response_validation" and diagnostic["trace_id"]
        assert diagnostic["code"] == "schema_validation" and diagnostic["attempt"] == 2
        assert any(detail["path"] == ["summary"] for detail in diagnostic["details"])
        assert KEY not in json.dumps(result)
        assert result["generation_absent"] and result["approvals"] == 0
    finally:
        transport.shutdown()


def test_workflow_exposes_only_bounded_branch_and_allowlisted_receipt():
    import yaml

    from workbench.settings import ROOT

    workflow = yaml.safe_load((ROOT / ".github/workflows/real-model.yml").read_text())
    job = workflow["jobs"]["model-feedback"]
    assert job["environment"] == "rnd" and job["timeout-minutes"] == 15
    assert "refs/heads/fix/model-feedback-history" in job["if"]
    assert "github.run_attempt == 1" in job["if"]
    live = next(
        step
        for step in job["steps"]
        if step.get("run") == "uv run python -m scripts.ci_model_feedback"
    )
    assert live["env"]["API_KEY"] == "${{ secrets.API_KEY }}"
    assert live["env"]["APPROVED_MAX_CNY"] == "${{ inputs.remaining_budget_cny }}"
    assert live["env"]["REVIEWED_SHA"] == "${{ inputs.reviewed_sha }}"
    uploads = [
        step["with"]["path"]
        for step in job["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert uploads == ["reports/model-feedback/summary.json"]
    assert "fix/model-feedback-history" not in workflow["jobs"]["real-model"]["if"]


class StreamingBytes(httpx.SyncByteStream):
    def __init__(self, value):
        self.value = value
        self.closed = False

    def __iter__(self):
        for offset in range(0, len(self.value), 65536):
            yield self.value[offset : offset + 65536]

    def close(self):
        self.closed = True


def large_token_framed_response(content):
    def frame(delta, finish=None):
        return (
            b"data: "
            + json.dumps(
                {
                    "id": "chatcmpl-" + "a" * 64,
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": "deepseek-flash",
                    "system_fingerprint": "f" * 120,
                    "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
                }
            ).encode()
            + b"\n\n"
        )

    return (
        frame({"role": "assistant", "reasoning_content": "x"})
        + frame({"reasoning_content": "x"}) * 6999
        + frame({"content": content}, "stop")
        + b'data: {"choices":[],"usage":{"prompt_tokens":100,"completion_tokens":7100,"total_tokens":7200}}\n\n'
        + b"data: [DONE]\n\n"
    )


def test_real_adapter_accepts_small_valid_json_inside_more_than_two_mb_of_sse_framing(tmp_path):
    calls = []
    content = Requirement(
        summary=ORIGINAL,
        users=["参赛者", "管理员"],
        data_scope="shared",
        features=[ANSWER],
        acceptance=["参赛者仅可维护本人报名记录"],
    ).model_dump_json()
    body = large_token_framed_response(content)
    assert len(body) > 2_000_000
    stream = StreamingBytes(body)

    def handler(req):
        calls.append(req)
        if len(calls) == 1:
            return httpx.Response(
                200,
                json={
                    "id": "probe",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "deepseek-flash",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": '{"ok":true}'},
                            "finish_reason": "stop",
                        }
                    ],
                },
            )
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    transport = mocked_transport(configured(), handler)
    try:
        result = run_check(configured(), transport, tmp_path)
        assert result["passed"], result
        assert len(calls) == 2 and stream.closed
        receipt = transport.receipts[-1]
        assert receipt["response_bytes"] == len(body)
        assert receipt["response_byte_limit"] > len(body)
        assert receipt["http_status"] == 200 and receipt["response_transport"] == "sse"
        assert receipt["usage"]["completion_tokens"] == 7100
        assert transport.reserved_cny <= configured().maximum_cost()
        assert not transport.guard_failures
    finally:
        transport.shutdown()


def test_response_guard_records_status_bytes_and_static_error_before_stopping(tmp_path):
    calls = []
    body = b"x" * 2_000_001
    stream = StreamingBytes(body)

    def handler(req):
        calls.append(req)
        if len(calls) == 1:
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": '{"ok":true}'},
                            "finish_reason": "stop",
                        }
                    ]
                },
            )
        return httpx.Response(200, stream=stream)

    transport = mocked_transport(configured(), handler)
    try:
        result = run_check(configured(), transport, tmp_path)
        assert not result["passed"] and result["answer_preserved"]
        assert len(calls) == 2 and stream.closed  # The trusted guard is not retried.
        failure = result["model_failures"][-1]
        assert failure["code"] == "response_byte_limit"
        assert failure["code"] != "unexpected_model_error"
        receipt = transport.receipts[-1]
        assert receipt["error_code"] == "response_byte_limit" and receipt["http_status"] == 200
        assert receipt["response_bytes"] == len(body)
        assert transport.guard_failures == [{"code": "response_byte_limit", "call": 2}]
    finally:
        transport.shutdown()


def test_partial_stream_read_timeout_keeps_status_and_safe_exception_type():
    class BrokenStream(httpx.SyncByteStream):
        def __iter__(self):
            yield b": partial\n\n"
            raise httpx.ReadTimeout(KEY)

    transport = mocked_transport(
        configured(),
        lambda req: httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=BrokenStream()
        ),
    )
    try:
        with pytest.raises(httpx.ReadTimeout):
            transport.handle_request(request())
        receipt = transport.receipts[-1]
        assert receipt["http_status"] == 200 and receipt["response_bytes"] == 11
        assert (
            receipt["exception_type"] == "ReadTimeout"
            and receipt["error_code"] == "transport_timeout"
        )
        assert KEY not in json.dumps(receipt)
    finally:
        transport.shutdown()


def test_unexpected_transport_exception_is_safe_specific_and_non_retryable():
    def broken(request):
        raise RuntimeError(KEY + " private provider detail")

    transport = mocked_transport(configured(), broken)
    try:
        with pytest.raises(SafeFailure) as caught:
            transport.handle_request(request())
        assert caught.value.code == "harness_internal_error" and not caught.value.retry
        assert transport.receipts[-1]["exception_type"] == "RuntimeError"
        assert transport.guard_failures[-1]["exception_type"] == "RuntimeError"
        assert KEY not in json.dumps(transport.receipts + transport.guard_failures) + str(
            caught.value
        )
    finally:
        transport.shutdown()
