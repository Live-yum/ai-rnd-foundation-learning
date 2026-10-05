# tests/test_capability_capture_bounds.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `client_for`（L12–L20）：接收`values`、`seen`。 调用`iter`、`httpx.Client`、`httpx.MockTransport`。 返回路径：L20的`httpx.Client(base_url="http://candidate.invalid", transport=httpx.MockTransport(respond))`。
- `client_for.respond`（L15–L18）：接收`request`。 调用`seen.append`、`json.dumps(next(values)).encode`、`json.dumps`、`next`、`httpx.Response`、`httpx.ByteStream`。 返回路径：L18的`httpx.Response(200, stream=httpx.ByteStream(body))`。
- `test_capture_single_value_exact_byte_limit_and_overflow`（L24–L27）：接收`text`。 控制顺序：L25断言`verifier.capture_scalar_size(text) == verifier.MAX_CAPTURE_VALUE_BYTES`。 调用`verifier.capture_scalar_size`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_rejects_nonfinite_or_nonscalar_values`（L31–L33）：接收`value`。 调用`pytest.raises`、`verifier.capture_scalar_size`、`pytest.mark.parametrize`、`float`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversize_response_capture_is_never_retained`（L36–L43）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L42断言`variables == {}`；L43断言`"secret" not in str(raised.value)`。 调用`HttpStep`、`client_for`、`pytest.raises`、`verifier.run_steps`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_boundary_overwrite_credit_and_reuse_across_http_steps`（L46–L67）：接收`monkeypatch`。 控制顺序：L64断言`len(receipts) == 3`；L65断言`json.loads(seen[1].content) == {"echo": value}`；L66断言`seen[2].url.path == "/short"`；L67断言`variables == {"token": "short", "small": True}`。 调用`verifier.CaptureBudget.entry_size`、`monkeypatch.setattr`、`HttpStep`、`client_for`、`verifier.run_steps`、`len`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_state_limit_counts_scenarios_together_without_storing_overflow`（L70–L88）：接收`monkeypatch`。 控制顺序：L85断言`len(seen) == 2`；L86断言`saved["first"]["token"] == "x" * 1000`；L87断言`"token" not in saved["second"]`；L88断言`verifier.CaptureBudget(saved).used <= 2048`。 调用`monkeypatch.setattr`、`AcceptanceScenario`、`HttpStep`、`client_for`、`pytest.raises`、`verifier.run_scenarios`、`len`、`verifier.CaptureBudget`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_same_variable_replacement_does_not_accumulate_historical_size`（L91–L103）：接收`monkeypatch`。 控制顺序：L96遍历`range(100)`；L98断言`budget.used == before`；L101断言`variables["token"] == "y" * 50`；L103断言`budget.used == before - 45`。 调用`verifier.CaptureBudget`、`monkeypatch.setattr`、`range`、`budget.store`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_saved_capture_is_rejected_before_interpolation_or_request`（L106–L113）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.fail`、`pytest.raises`、`verifier.run_steps`、`HttpStep`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_interpolation_retains_scalar_types_and_bounds_repetition_before_join`（L116–L125）：接收`monkeypatch`。 控制顺序：L118断言`verifier.interpolate( {"id": "${id}", "enabled": "${flag}"}, {"id": 123, "flag": True…`；L121断言`verifier.interpolate("/${value}", {"value": "a/b"}, path=True) == "/a%2Fb"`。 调用`monkeypatch.setattr`、`verifier.interpolate`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_decoder_recursion_failure_is_classified_without_retaining_data`（L128–L145）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`httpx.ByteStream`、`pytest.raises`、`verifier.run_steps`、`HttpStep`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_decoder_recursion_failure_is_classified_without_retaining_data.too_deep`（L131–L132）：接收`_raw`。 控制顺序：L132抛异常，停止当前正常路径。 调用`RecursionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_capture_bounds.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L145。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5994`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_capture_bounds.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e084e7e63974877a8f9c01391767a0f400b988b1565408f99ec162722000b528"} -->
````python
# tests/test_capability_capture_bounds.py
"""Synthetic data-only checks for bounded retained captures and substitutions."""

import json

import httpx
import pytest

from workbench import capability_verification as verifier
from workbench.capability_contracts import AcceptanceScenario, HttpStep


def client_for(values, seen):
    values = iter(values)

    def respond(request):
        seen.append(request)
        body = json.dumps(next(values)).encode()
        return httpx.Response(200, stream=httpx.ByteStream(body))

    return httpx.Client(base_url="http://candidate.invalid", transport=httpx.MockTransport(respond))


@pytest.mark.parametrize("text", ["x" * 16384, "é" * 8192])
def test_capture_single_value_exact_byte_limit_and_overflow(text):
    assert verifier.capture_scalar_size(text) == verifier.MAX_CAPTURE_VALUE_BYTES
    with pytest.raises(verifier.CheckFailure, match="单值预算"):
        verifier.capture_scalar_size(text + "x")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), [], {}, None])
def test_capture_rejects_nonfinite_or_nonscalar_values(value):
    with pytest.raises(verifier.CheckFailure):
        verifier.capture_scalar_size(value)


def test_oversize_response_capture_is_never_retained():
    variables, seen = {}, []
    step = HttpStep(path="/", status=200, captures={"token": "$.token"})
    with client_for([{"token": "secret" * 3000}], seen) as client:
        with pytest.raises(verifier.CheckFailure, match="单值预算") as raised:
            verifier.run_steps(client, [step], variables)
    assert variables == {}
    assert "secret" not in str(raised.value)


def test_capture_boundary_overwrite_credit_and_reuse_across_http_steps(monkeypatch):
    variables, seen = {}, []
    value = "x" * verifier.MAX_CAPTURE_VALUE_BYTES
    exact_budget = 128 + verifier.CaptureBudget.entry_size("token", value)
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", exact_budget)
    steps = [
        HttpStep(path="/first", status=200, captures={"token": "$.token"}),
        HttpStep(
            method="POST",
            path="/second",
            status=200,
            body={"echo": "${token}"},
            captures={"token": "$.token"},
        ),
        HttpStep(path="/${token}", status=200, captures={"small": "$.small"}),
    ]
    with client_for([{"token": value}, {"token": "short"}, {"small": True}], seen) as client:
        receipts = verifier.run_steps(client, steps, variables)
    assert len(receipts) == 3
    assert json.loads(seen[1].content) == {"echo": value}
    assert seen[2].url.path == "/short"
    assert variables == {"token": "short", "small": True}


def test_state_limit_counts_scenarios_together_without_storing_overflow(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", 2048)
    saved, seen = {}, []
    scenarios = [
        AcceptanceScenario(
            id=name,
            title="Synthetic",
            requirements=["r"],
            steps=[HttpStep(path="/", status=200, captures={"token": "$.token"})],
        )
        for name in ("first", "second")
    ]
    with client_for([{"token": "x" * 1000}, {"token": "y" * 1000}], seen) as client:
        with pytest.raises(verifier.CheckFailure, match="总预算"):
            verifier.run_scenarios(client, scenarios, saved=saved)
    assert len(seen) == 2
    assert saved["first"]["token"] == "x" * 1000
    assert "token" not in saved["second"]
    assert verifier.CaptureBudget(saved).used <= 2048


def test_same_variable_replacement_does_not_accumulate_historical_size(monkeypatch):
    variables = {"token": "x" * 50}
    budget = verifier.CaptureBudget({"scenario": variables})
    monkeypatch.setattr(verifier, "MAX_CAPTURE_STATE_BYTES", budget.used)
    before = budget.used
    for _ in range(100):
        budget.store(variables, "token", "y" * 50)
    assert budget.used == before
    with pytest.raises(verifier.CheckFailure, match="总预算"):
        budget.store(variables, "token", "z" * 51)
    assert variables["token"] == "y" * 50
    budget.store(variables, "token", "small")
    assert budget.used == before - 45


def test_invalid_saved_capture_is_rejected_before_interpolation_or_request():
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: pytest.fail("request reached"))
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="单值预算"):
            verifier.run_steps(
                client, [HttpStep(path="/${token}", status=200)], {"token": "x" * 16385}
            )


def test_interpolation_retains_scalar_types_and_bounds_repetition_before_join(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_INTERPOLATED_BYTES", 100)
    assert verifier.interpolate(
        {"id": "${id}", "enabled": "${flag}"}, {"id": 123, "flag": True}
    ) == {"id": 123, "enabled": True}
    assert verifier.interpolate("/${value}", {"value": "a/b"}, path=True) == "/a%2Fb"
    with pytest.raises(verifier.CheckFailure, match="替换超过预算"):
        verifier.interpolate("${token}" * 11, {"token": "x" * 10})
    with pytest.raises(verifier.CheckFailure, match="替换超过预算"):
        verifier.interpolate(["${token}"] * 11, {"token": "x" * 10})


def test_decoder_recursion_failure_is_classified_without_retaining_data(monkeypatch):
    # Decoder recursion behavior differs across supported interpreter builds.
    # Inject the exception rather than depending on a particular C stack limit.
    def too_deep(_raw):
        raise RecursionError("synthetic decoder depth")

    monkeypatch.setattr(verifier.json, "loads", too_deep)
    body = b"{}"
    with httpx.Client(
        base_url="http://candidate.invalid",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=httpx.ByteStream(body))
        ),
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="JSON"):
            verifier.run_steps(
                client, [HttpStep(path="/", status=200, captures={"value": "$"})], {}
            )
````
