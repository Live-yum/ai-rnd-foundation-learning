# tests/test_model_feedback_ci.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_model_feedback`、`workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configured`（L29–L38）：接收`**values`。 调用`configuration`。 返回路径：L30的`configuration( { "BASE_URL": ENDPOINT, "MODE": "deepseek-flash", "API_KEY": KEY, "APPROVED…`。
- `request`（L41–L53）：接收`**body`。 调用`httpx.Request`。 返回路径：L42的`httpx.Request( "POST", ENDPOINT + "/chat/completions", headers={"Authorization": "Bearer "…`。
- `mocked_transport`（L56–L60）：接收`config`、`handler`。 调用`BoundedFeedbackTransport`、`transport.transport.close`、`httpx.MockTransport`。 返回路径：L60的`transport`。
- `test_unapproved_configuration_fails_before_transport`（L77–L79）：接收`values`。 调用`pytest.raises`、`configured`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prices_are_allowlisted_and_full_worst_case_below_user_limit`（L82–L86）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L83断言`set(PRICES) == {"deepseek-flash", "deepseek-v4-pro"}`；L84断言`configured().maximum_cost() == Decimal("1.614848")`；L85断言`configured(MODE="deepseek-v4-pro").maximum_cost() == Decimal("6.970752")`；L86断言`KEY not in repr(configured())`。 调用`set`、`configured().maximum_cost`、`configured`、`Decimal`、`configured(MODE="deepseek-v4-pro").maximum_cost`、`repr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `dispatch_context`（L89–L98）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L90的`{ "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REPOSITORY":…`。
- `test_only_manual_owner_repo_reviewed_branch_first_attempt_is_allowed`（L114–L117）：接收`key`、`value`。 调用`trusted_dispatch`、`dispatch_context`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_transport_scope_never_calls_provider`（L133–L141）：接收`body`。 控制顺序：L139断言`not calls and transport.calls == 0 and transport.reserved_cny == 0`。 调用`mocked_transport`、`configured`、`calls.append`、`httpx.Response`、`pytest.raises`、`transport.handle_request`、`request`、`transport.shutdown`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_call_count_phase_caps_and_reserved_money_are_enforced_before_requests`（L144–L164）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L154遍历`("initial_requirements", "corrected_requirements")`；L156遍历`range(2)`；L158断言`len(calls) == transport.calls == MAX_CALLS`；L159断言`0 < transport.reserved_cny <= configured().maximum_cost()`；L162断言`KEY not in json.dumps(transport.receipts)`。 调用`mocked_transport`、`configured`、`calls.append`、`httpx.Response`、`transport.handle_request`、`request`、`pytest.raises`、`range`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_destination_and_credentials_cannot_be_replaced`（L167–L182）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L171遍历`( ("https://evil.example/chat/completions", KEY), (ENDPOINT + "/c…`；L180断言`not calls`。 调用`mocked_transport`、`configured`、`calls.append`、`httpx.Response`、`request`、`httpx.URL`、`pytest.raises`、`transport.handle_request`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_network_failure_reserves_full_cost_and_is_not_retried_by_transport`（L185–L200）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L196断言`len(calls) == transport.calls == 1 and transport.reserved_cny > 0`；L197断言`transport.receipts[0]["transport_error"]`；L198断言`KEY not in json.dumps(transport.receipts)`。 调用`mocked_transport`、`configured`、`pytest.raises`、`transport.handle_request`、`request`、`len`、`json.dumps`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_network_failure_reserves_full_cost_and_is_not_retried_by_transport.fail`（L188–L190）：接收`req`。 控制顺序：L190抛异常，停止当前正常路径。 调用`calls.append`、`httpx.ConnectError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_remaining_money_guard_blocks_before_network_even_under_call_limit`（L203–L212）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L210断言`not calls and transport.calls == 0`。 调用`mocked_transport`、`configured`、`calls.append`、`httpx.Response`、`Decimal`、`pytest.raises`、`transport.handle_request`、`request`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_receipt_drops_provider_text_and_supports_streamed_usage`（L215–L238）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L228遍历`( json.dumps(data).encode(), b"data: " + json.dumps(data).encode(…`；L233断言`result == { "http_status": 200, "finish_reason": "stop", "usage": {"prompt_tokens": 1…`；L238断言`KEY not in json.dumps(result)`。 调用`json.dumps(data).encode`、`json.dumps`、`response_receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_runtime_two_phase_signup_flow_has_no_generation_or_fake_gateway`（L241–L295）：接收`tmp_path`。 控制顺序：L280断言`result["passed"]`；L281断言`result["connection"]["ok"] and result["answer_preserved"] and result["scope_preserved…`；L284断言`result["initial"]["gate_stage"] == "clarification"`；L285断言`result["corrected"]["status"] == "WAITING_REQUIREMENTS"`；L286断言`result["generation_absent"] and result["approvals"] == 0`；L287断言`transport.phase_calls == { "connection": 1, "initial_requirements": 0, "corrected_req…`；L292断言`KEY not in json.dumps(result)`；L293断言`len(json.dumps(calls[-1]).encode()) < MAX_REQUEST_BYTES`。 调用`mocked_transport`、`configured`、`run_check`、`json.dumps`、`len`、`json.dumps(calls[-1]).encode`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_runtime_two_phase_signup_flow_has_no_generation_or_fake_gateway.handle`（L244–L275）：接收`req`。 控制顺序：L247按`len(calls) == 1`分支；L250断言`ORIGINAL in json.dumps(body, ensure_ascii=False)`；L251断言`ANSWER in json.dumps(body, ensure_ascii=False)`。 调用`json.loads`、`calls.append`、`len`、`json.dumps`、`Requirement( summary=ORIGINAL, users=["参赛者", "管理员"], data_scope="…`、`Requirement`、`httpx.Response`。 返回路径：L259的`httpx.Response( 200, json={ "id": "offline-adapter", "object": "chat.completion", "created…`。
- `test_failed_schema_run_retains_answer_and_exports_only_safe_diagnostic_paths`（L298–L335）：接收`tmp_path`。 控制顺序：L324断言`not result["passed"] and result["answer_preserved"]`；L325断言`result["corrected"]["status"] == "FAILED"`；L326断言`transport.phase_calls["corrected_requirements"] == 2`；L327断言`len(result["model_failures"]) == 2`；L329断言`diagnostic["phase"] == "response_validation" and diagnostic["trace_id"]`；L330断言`diagnostic["code"] == "schema_validation" and diagnostic["attempt"] == 2`；L331断言`any(detail["path"] == ["summary"] for detail in diagnostic["details"])`；L332断言`KEY not in json.dumps(result)`。后续分支沿下方源码相同行号继续阅读。 调用`mocked_transport`、`configured`、`run_check`、`len`、`any`、`json.dumps`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_schema_run_retains_answer_and_exports_only_safe_diagnostic_paths.handle`（L301–L319）：接收`req`。 调用`calls.append`、`len`、`json.dumps`、`httpx.Response`。 返回路径：L304的`httpx.Response( 200, json={ "id": "offline", "object": "chat.completion", "created": 0, "m…`。
- `test_workflow_exposes_only_bounded_branch_and_allowlisted_receipt`（L338–L362）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L345断言`job["environment"] == "rnd" and job["timeout-minutes"] == 15`；L346断言`"refs/heads/fix/model-feedback-history" in job["if"]`；L347断言`"github.run_attempt == 1" in job["if"]`；L353断言`live["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"`；L354断言`live["env"]["APPROVED_MAX_CNY"] == "${{ inputs.remaining_budget_cny }}"`；L355断言`live["env"]["REVIEWED_SHA"] == "${{ inputs.reviewed_sha }}"`；L361断言`uploads == ["reports/model-feedback/summary.json"]`；L362断言`"fix/model-feedback-history" not in workflow["jobs"]["real-model"]["if"]`。 调用`yaml.safe_load`、`(ROOT / ".github/workflows/real-model.yml").read_text`、`next`、`step.get`、`step.get("uses", "").startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `StreamingBytes`（L365–L375）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `StreamingBytes.__init__`（L366–L368）：接收`value`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `StreamingBytes.__iter__`（L370–L372）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L371遍历`range(0, len(self.value), 65536)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `StreamingBytes.close`（L374–L375）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `large_token_framed_response`（L378–L401）：接收`content`。 调用`frame`。 返回路径：L395的`frame({"role": "assistant", "reasoning_content": "x"}) + frame({"reasoning_content": "x"})…`。
- `large_token_framed_response.frame`（L379–L393）：接收`delta`、`finish`。 调用`json.dumps( { "id": "chatcmpl-" + "a" * 64, "object": "chat.compl…`、`json.dumps`。 返回路径：L380的`b"data: " + json.dumps( { "id": "chatcmpl-" + "a" * 64, "object": "chat.completion.chunk",…`。
- `test_real_adapter_accepts_small_valid_json_inside_more_than_two_mb_of_sse_framing`（L404–L451）：接收`tmp_path`。 控制顺序：L414断言`len(body) > 2_000_000`；L441断言`result["passed"]`；L442断言`len(calls) == 2 and stream.closed`；L444断言`receipt["response_bytes"] == len(body)`；L445断言`receipt["response_byte_limit"] > len(body)`；L446断言`receipt["http_status"] == 200 and receipt["response_transport"] == "sse"`；L447断言`receipt["usage"]["completion_tokens"] == 7100`；L448断言`transport.reserved_cny <= configured().maximum_cost()`。后续分支沿下方源码相同行号继续阅读。 调用`Requirement( summary=ORIGINAL, users=["参赛者", "管理员"], data_scope="…`、`Requirement`、`large_token_framed_response`、`len`、`StreamingBytes`、`mocked_transport`、`configured`、`run_check`、`configured().maximum_cost`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_adapter_accepts_small_valid_json_inside_more_than_two_mb_of_sse_framing.handler`（L417–L436）：接收`req`。 控制顺序：L419按`len(calls) == 1`分支。 调用`calls.append`、`len`、`httpx.Response`。 返回路径：L420的`httpx.Response( 200, json={ "id": "probe", "object": "chat.completion", "created": 0, "mod…`；L436的`httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)`。
- `test_response_guard_records_status_bytes_and_static_error_before_stopping`（L454–L488）：接收`tmp_path`。 控制顺序：L478断言`not result["passed"] and result["answer_preserved"]`；L479断言`len(calls) == 2 and stream.closed`；L481断言`failure["code"] == "response_byte_limit"`；L482断言`failure["code"] != "unexpected_model_error"`；L484断言`receipt["error_code"] == "response_byte_limit" and receipt["http_status"] == 200`；L485断言`receipt["response_bytes"] == len(body)`；L486断言`transport.guard_failures == [{"code": "response_byte_limit", "call": 2}]`。 调用`StreamingBytes`、`mocked_transport`、`configured`、`run_check`、`len`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_response_guard_records_status_bytes_and_static_error_before_stopping.handler`（L459–L473）：接收`req`。 控制顺序：L461按`len(calls) == 1`分支。 调用`calls.append`、`len`、`httpx.Response`。 返回路径：L462的`httpx.Response( 200, json={ "choices": [ { "message": {"role": "assistant", "content": '{"…`；L473的`httpx.Response(200, stream=stream)`。
- `test_partial_stream_read_timeout_keeps_status_and_safe_exception_type`（L491–L514）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L507断言`receipt["http_status"] == 200 and receipt["response_bytes"] == 11`；L508断言`receipt["exception_type"] == "ReadTimeout" and receipt["error_code"] == "transport_ti…`；L512断言`KEY not in json.dumps(receipt)`。 调用`mocked_transport`、`configured`、`httpx.Response`、`BrokenStream`、`pytest.raises`、`transport.handle_request`、`request`、`json.dumps`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_stream_read_timeout_keeps_status_and_safe_exception_type.BrokenStream`（L492–L495）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_partial_stream_read_timeout_keeps_status_and_safe_exception_type.BrokenStream.__iter__`（L493–L495）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L495抛异常，停止当前正常路径。 调用`httpx.ReadTimeout`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_unexpected_transport_exception_is_safe_specific_and_non_retryable`（L517–L532）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L525断言`caught.value.code == "harness_internal_error" and not caught.value.retry`；L526断言`transport.receipts[-1]["exception_type"] == "RuntimeError"`；L527断言`transport.guard_failures[-1]["exception_type"] == "RuntimeError"`；L528断言`KEY not in json.dumps(transport.receipts + transport.guard_failures) + str( caught.va…`。 调用`mocked_transport`、`configured`、`pytest.raises`、`transport.handle_request`、`request`、`json.dumps`、`str`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unexpected_transport_exception_is_safe_specific_and_non_retryable.broken`（L518–L519）：接收`request`。 控制顺序：L519抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_feedback_ci.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L532。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18420`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_feedback_ci.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d5ed4cb2a663901a238d890cf8f8c2f470c68d5167a64f305895c052cca3b730"} -->
````python
# tests/test_model_feedback_ci.py
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
    assert live["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"
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
````
