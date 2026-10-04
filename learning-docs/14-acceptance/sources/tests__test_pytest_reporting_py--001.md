# tests/test_pytest_reporting.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_ordinary_ids_remain_pytest_defaults`（L10–L11）：接收`value`。 控制顺序：L11断言`pytest_make_parametrize_id(None, value, "payload") is None`。 调用`pytest_make_parametrize_id`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_large_ids_are_bounded_deterministic_and_input_is_unchanged`（L17–L27）：接收`value`。 控制顺序：L21断言`result == f"payload-{type(value).__name__}-{len(value)}-{hashlib.sha256(raw).hexdiges…`；L25断言`len(result) < 80`；L26断言`value is original`；L27断言`pytest_make_parametrize_id(None, value, "payload") == result`。 调用`isinstance`、`value.encode`、`pytest_make_parametrize_id`、`type`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_pytest_reporting.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L27。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`993`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_pytest_reporting.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c6a02c49e3776d486f264f1ae7916a8a3c2c743e5f4a6515fb9c081bab87adb6"} -->
````python
# tests/test_pytest_reporting.py
"""Bound report identifiers while preserving exact adversarial test inputs."""

import hashlib

import pytest
from conftest import pytest_make_parametrize_id


@pytest.mark.parametrize("value", [None, 7, {}, "ordinary", b"ordinary", "x" * 80])
def test_ordinary_ids_remain_pytest_defaults(value):
    assert pytest_make_parametrize_id(None, value, "payload") is None


@pytest.mark.parametrize(
    "value", ["x" * 81, b"x" * 81, "中" * 100, "\ud800" * 100, b"x" * 2_000_001]
)
def test_large_ids_are_bounded_deterministic_and_input_is_unchanged(value):
    original = value
    raw = value.encode("utf-8", errors="surrogatepass") if isinstance(value, str) else value
    result = pytest_make_parametrize_id(None, value, "payload")
    assert (
        result
        == f"payload-{type(value).__name__}-{len(value)}-{hashlib.sha256(raw).hexdigest()[:16]}"
    )
    assert len(result) < 80
    assert value is original
    assert pytest_make_parametrize_id(None, value, "payload") == result
````
