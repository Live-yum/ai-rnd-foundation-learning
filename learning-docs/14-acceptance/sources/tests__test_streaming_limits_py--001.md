# tests/test_streaming_limits.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Chunks`（L24–L33）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Chunks.__init__`（L25–L26）：接收`data`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Chunks.__iter__`（L28–L30）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L29遍历`range(0, len(self.data), 65536)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Chunks.close`（L32–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `audited_stream`（L36–L41）：接收`body`、`tokens`。 调用`Chunks`、`httpx.Response`、`OutputContract`、`AuditedTransport`、`httpx.MockTransport`、`AuditedEventStream`。 返回路径：L41的`AuditedEventStream(response, audit), audit, chunks`。
- `frame`（L44–L49）：接收`delta`。 调用`json.dumps({"choices": [{"index": 0, "delta": delta, "finish_reas…`、`json.dumps`。 返回路径：L45的`b"data: " + json.dumps({"choices": [{"index": 0, "delta": delta, "finish_reason": None}]})…`。
- `test_cumulative_decoded_text_stays_bounded_despite_larger_wire_allowance`（L53–L61）：接收`field`。 控制顺序：L59断言`caught.value.code == "response_too_large" and caught.value.retry is False`；L60断言`audit.error is caught.value and chunks.closed`；L61断言`stream.bytes_read < stream.wire_limit`。 调用`frame`、`len`、`audited_stream`、`pytest.raises`、`list`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_string_reasoning_cannot_bypass_decoded_content_budget`（L66–L72）：接收`field`、`value`。 控制顺序：L70断言`caught.value.code == "invalid_message" and caught.value.retry is False`；L71断言`audit.error is caught.value and chunks.closed`；L72断言`stream.content_bytes == 0`。 调用`audited_stream`、`frame`、`pytest.raises`、`list`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unterminated_or_multiline_frame_cannot_accumulate_above_two_mb`（L75–L83）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76遍历`( b"data: " + b"x" * (MAX_MODEL_CONTENT_BYTES + 1), (b"data: " + …`；L83断言`caught.value.code == "response_too_large" and chunks.closed`。 调用`audited_stream`、`pytest.raises`、`list`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_empty_comment_frames_cannot_bypass_total_wire_bound`（L86–L91）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L90断言`caught.value.code == "stream_wire_limit" and caught.value.retry is False`；L91断言`audit.error is caught.value and chunks.closed`。 调用`audited_stream`、`pytest.raises`、`list`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_wire_allowance_depends_on_requested_tokens_and_has_hard_ceiling`（L94–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L95断言`stream_wire_limit(8192) == 10_388_608`；L96断言`stream_wire_limit(128) == 2_131_072`；L97断言`stream_wire_limit(393216) == MAX_STREAM_WIRE_BYTES == 64_000_000`。 调用`stream_wire_limit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_static_transport_guard_survives_sdk_boundary_in_audit`（L100–L110）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L110断言`audit.error is failure`。 调用`OutputFailure`、`OutputContract`、`AuditedTransport`、`httpx.MockTransport`、`pytest.raises`、`audit.handle_request`、`httpx.Request`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_static_transport_guard_survives_sdk_boundary_in_audit.blocked`（L103–L104）：接收`request`。 控制顺序：L104抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unexpected_adapter_exception_reports_class_without_raw_message`（L113–L138）：接收`store`、`monkeypatch`。 控制顺序：L132断言`len(events) == 1`；L134断言`diagnostic["code"] == "unexpected_model_error"`；L135断言`diagnostic["details"] == [ {"type": "RuntimeError", "path": [], "message": "模型适配器异常"}…`；L138断言`secret not in json.dumps(events)`。 调用`SecretStr`、`monkeypatch.setattr`、`new_run`、`ModelGateway`、`httpx.MockTransport`、`pytest.raises`、`gateway.complete`、`store.events`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unexpected_adapter_exception_reports_class_without_raw_message.broken`（L120–L122）：接收`*args`、`**kwargs`。 控制顺序：L121抛异常，停止当前正常路径。 调用`RuntimeError`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `tests/test_streaming_limits.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L138。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5119`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_streaming_limits.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "44aecf4647126373a4acaf156603b894e59d94d7be00de8e20140528311d7a54"} -->
````python
# tests/test_streaming_limits.py
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
````
