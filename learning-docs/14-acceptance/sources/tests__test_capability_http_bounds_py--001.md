# tests/test_capability_http_bounds.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Body`（L15–L27）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Body.__init__`（L16–L19）：接收`chunks`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Body.__iter__`（L21–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L22遍历`self.chunks`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Body.close`（L26–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run`（L30–L47）：接收`body`、`response_headers`、`step_headers`、`equals`。 调用`httpx.Client`、`httpx.MockTransport`、`run_steps`、`HttpStep`。 返回路径：L47的`result, requests`。
- `run.handler`（L33–L35）：接收`request`。 调用`requests.append`、`httpx.Response`。 返回路径：L35的`httpx.Response(200, headers=response_headers, stream=body)`。
- `test_compressed_or_unknown_encoding_rejected_before_first_body_read`（L51–L56）：接收`encoding`。 控制顺序：L55断言`body.reads == 0`；L56断言`body.closed`。 调用`Body`、`gzip.compress`、`pytest.raises`、`run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_json_and_case_insensitive_request_header_override`（L60–L71）：接收`encoding`。 控制顺序：L68断言`result[0]["passed"] is True`；L69断言`requests[0].headers.get_list("accept-encoding") == ["identity"]`；L70断言`requests[0].headers["x-product-test"] == "value"`；L71断言`body.closed`。 调用`Body`、`run`、`requests[0].headers.get_list`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_two_megabyte_identity_body_is_allowed`（L74–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L77断言`result[0]["passed"] is True`；L78断言`body.closed`。 调用`Body`、`run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_raw_budget_rejects_overflow_and_stops_consuming`（L82–L87）：接收`chunks`。 控制顺序：L86断言`body.reads == len(chunks)`；L87断言`body.closed`。 调用`Body`、`pytest.raises`、`run`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_http_bounds.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L87。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2816`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_http_bounds.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9da065e33862e8cd4876468c8925e564a37c22ab96e87cf347cca5a8eb79d29c"} -->
````python
# tests/test_capability_http_bounds.py
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
````
