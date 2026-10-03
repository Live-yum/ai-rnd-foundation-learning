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

</details>

**创建路径：** `tests/test_model_feedback_ci.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L362。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12296`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_feedback_ci.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "629d7c04f3511a42943c5be3244c712e21b82d7b9c617427e73a20b892d13877"} -->
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
````
