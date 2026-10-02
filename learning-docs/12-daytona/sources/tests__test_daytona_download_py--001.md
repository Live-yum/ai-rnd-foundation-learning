# tests/test_daytona_download.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `TrackedStream`（L16–L29）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `TrackedStream.__init__`（L17–L20）：接收`body`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TrackedStream.__iter__`（L22–L26）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23遍历`range(0, len(self.body), 4096)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `TrackedStream.close`（L28–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `multipart`（L32–L38）：接收`payload`、`complete`。 返回路径：L38的`body + (b"\r\n--rnd-boundary--\r\n" if complete else b"")`。
- `sdk_reader`（L41–L64）：接收`payload`、`complete`、`status`。 调用`TrackedStream`、`multipart`、`httpx.Client`、`httpx.MockTransport`、`FileSystem`、`SimpleNamespace`。 返回路径：L64的`FileSystem(SimpleNamespace(_download_files_serialize=serialize), http), http, stream`。
- `sdk_reader.serialize`（L44–L51）：接收`**kwargs`。 控制顺序：L45断言`kwargs["download_files"].paths == [REMOTE + "/runtime.json"]`。 返回路径：L46的`( "POST", "http://127.0.0.1:3000/download", {}, {"paths": kwargs["download_files"].paths},…`。
- `sdk_reader.handler`（L53–L61）：接收`request`。 控制顺序：L54断言`request.url.host == "127.0.0.1"`；L55断言`request.extensions["timeout"]["read"] == 7`；L56断言`request.extensions["timeout"]["write"] == 7`。 调用`httpx.Response`。 返回路径：L57的`httpx.Response( status, headers={"Content-Type": "multipart/form-data; boundary=rnd-bounda…`。
- `test_actual_sdk_stream_timeout_and_report_are_consumed_and_closed`（L67–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L70断言`read_runtime_report(filesystem, 7) == REPORT`；L71断言`stream.closed`。 调用`sdk_reader`、`json.dumps(REPORT).encode`、`json.dumps`、`read_runtime_report`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_or_nonobject_reports_never_pass`（L88–L92）：接收`payload`。 控制顺序：L92断言`stream.closed`。 调用`sdk_reader`、`pytest.raises`、`read_runtime_report`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversize_stops_reading_early_and_closes_real_sdk_stream`（L95–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L100断言`stream.closed and stream.read_bytes < len(payload)`。 调用`sdk_reader`、`pytest.raises`、`read_runtime_report`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_valid_json_inside_truncated_multipart_is_not_a_success`（L103–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L107断言`stream.closed`。 调用`sdk_reader`、`json.dumps(REPORT).encode`、`json.dumps`、`pytest.raises`、`read_runtime_report`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_failures_cannot_be_reported_as_passed`（L111–L115）：接收`status`。 控制顺序：L115断言`stream.closed`。 调用`sdk_reader`、`json.dumps(REPORT).encode`、`json.dumps`、`pytest.raises`、`read_runtime_report`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_download.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L115。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3735`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_download.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a1e10ac9d93f320a173da0e9d6a5f508eb35ff2efaf25cb35e06848e857ce618"} -->
````python
# tests/test_daytona_download.py
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
````
