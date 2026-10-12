# tests/test_live_http_trace.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.coding.timing`、`workbench.llm`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `MemoryBackend`（L19–L70）：继承`MockBackend`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `MemoryBackend.__init__`（L20–L23）：接收`clock`、`failure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryBackend.connect_tcp`（L25–L64）：接收`host`、`port`、`timeout`、`**kwargs`。 控制顺序：L26断言`host == "fixture.invalid" and port == 443 and timeout == 60`；L28按`self.failure == "connect"`分支；L29抛异常，停止当前正常路径；L32按`self.failure == "schema"`分支。 调用`httpcore.ConnectTimeout`、`response`、`str(len(raw)).encode`、`str`、`len`、`Stream`、`self.streams.append`。 返回路径：L64的`stream`。
- `MemoryBackend.connect_tcp.Stream`（L37–L60）：继承`MockStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `MemoryBackend.connect_tcp.Stream.start_tls`（L38–L45）：接收`ssl_context`、`server_hostname`、`timeout`。 控制顺序：L39断言`ssl_context.check_hostname and ssl_context.verify_mode == ssl.CERT_REQUIRED`；L40断言`server_hostname == "fixture.invalid" and timeout == 60`；L42按`backend.failure == "tls"`分支；L44抛异常，停止当前正常路径。 调用`self.close`、`httpcore.ConnectTimeout`。 返回路径：L45的`self`。
- `MemoryBackend.connect_tcp.Stream.write`（L47–L53）：接收`buffer`、`timeout`。 控制顺序：L48断言`timeout == 60`；L50按`buffer.startswith(b"{")`分支；L52按`backend.failure == "request_body"`分支；L53抛异常，停止当前正常路径。 调用`buffer.startswith`、`backend.bodies.append`、`json.loads`、`httpcore.WriteTimeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryBackend.connect_tcp.Stream.read`（L55–L60）：接收`max_bytes`、`timeout`。 控制顺序：L56断言`timeout == 60`；L58按`backend.failure == "response_headers"`分支；L59抛异常，停止当前正常路径。 调用`httpcore.ReadTimeout`、`super().read`、`super`。 返回路径：L60的`super().read(max_bytes, timeout)`。
- `MemoryBackend.connect_unix_socket`（L66–L67）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryBackend.sleep`（L69–L70）：接收`seconds`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `transport`（L73–L80）：接收`monkeypatch`、`failure`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`client.TestServiceTransport`、`MemoryBackend`。 返回路径：L80的`value, backend`。
- `test_actual_sdk_reports_transport_boundary_without_changing_guards`（L86–L127）：接收`store`、`monkeypatch`、`failure`。 控制顺序：L92按`failure`分支；L96断言`invoke(model, run).operation == "submit"`；L100断言`value.calls == store.get_run(run)["model_calls"] == count`；L101断言`value.responses == (1 if failure in (None, "schema") else 0)`；L103断言`len(receipts) == count`；L104遍历`receipts`；L106断言`trace["connect_started_seconds"] == 0`；L107断言`trace["event_count"] > 0`。后续分支沿下方源码相同行号继续阅读。 调用`transport`、`model_gateway`、`pytest.fail`、`new_run`、`pytest.raises`、`invoke`、`value.close`、`store.get_run`、`timing_receipts`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_trace_and_lazy_response_body_semantics_are_preserved`（L131–L166）：接收`monkeypatch`、`reject`。 控制顺序：L151按`reject`分支；L154断言`caught.value is failure`；L157断言`request.extensions["trace"] is previous`；L158断言`"http11.receive_response_body.started" not in events`；L161断言`"http11.receive_response_body.started" in events`；L164断言`request.extensions["trace"] is previous`；L165断言`all(stream._closed for stream in backend.streams)`；L166断言`"private" not in json.dumps(timing_receipts(value.timings, attempts=True))`。 调用`transport`、`RuntimeError`、`httpx.Request`、`dict.fromkeys`、`pytest.raises`、`value.handle_request`、`result.read`、`result.close`、`value.close`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_trace_and_lazy_response_body_semantics_are_preserved.previous`（L136–L139）：接收`name`、`info`。 控制顺序：L138按`reject and name == "http11.send_request_body.started"`分支；L139抛异常，停止当前正常路径。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trace_projection_drops_unknown_phases_values_and_info`（L169–L191）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L179断言`facts["failed_phase"] == "response_headers" and facts["event_count"] == 1`；L180遍历`(True, -1, 65, "private", {}, [], float("nan"), float("inf"))`；L189断言`data["event_count"] is None and data["failed_phase"] is None`；L190断言`"private" not in json.dumps(data)`；L191断言`len(timing_receipts([{"http_trace": facts}] * 40, attempts=True)) == 32`。 调用`client.phase_trace`、`callback`、`Poison`、`float`、`http_trace_receipt`、`dict.fromkeys`、`json.dumps`、`len`、`timing_receipts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trace_projection_drops_unknown_phases_values_and_info.Poison`（L172–L174）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_trace_projection_drops_unknown_phases_values_and_info.Poison.__repr__`（L173–L174）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_live_http_trace.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L191。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7946`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_live_http_trace.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0bf979f86475aeb36f017320b48e88b8204ffa3dc6b86ef44c22ab948d763553"} -->
````python
# tests/test_live_http_trace.py
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
````
