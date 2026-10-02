# tests/test_local_embeddings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_local_model_requires_exact_weight_identity`（L10–L15）：接收`tmp_path`。 调用`(tmp_path / "onnx").mkdir`、`(tmp_path / "onnx/model.onnx").write_bytes`、`(tmp_path / "tokenizer.json").write_bytes`、`pytest.raises`、`local.check_weights`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_model_requires_matching_tokenizer_identity`（L18–L25）：接收`tmp_path`、`monkeypatch`。 调用`(tmp_path / "onnx").mkdir`、`(tmp_path / "onnx/model.onnx").write_bytes`、`(tmp_path / "tokenizer.json").write_bytes`、`monkeypatch.setattr`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`、`pytest.raises`、`local.check_weights`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_weights_cannot_be_replaced_with_fixture`（L28–L30）：接收`tmp_path`。 调用`pytest.raises`、`local.check_weights`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_local_embeddings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L30。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1099`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_local_embeddings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9f2016b86d0ec99dd036671ac3ec9966f3256d81334bac64e0cf3640d6b3e8b8"} -->
````python
# tests/test_local_embeddings.py
"""Negative contracts; real-model success is only proved by the dedicated workflow."""

import hashlib

import pytest

from scripts import ci_local_embeddings as local


def test_local_model_requires_exact_weight_identity(tmp_path):
    (tmp_path / "onnx").mkdir()
    (tmp_path / "onnx/model.onnx").write_bytes(b"not an inference model")
    (tmp_path / "tokenizer.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="pinned official ONNX"):
        local.check_weights(tmp_path)


def test_local_model_requires_matching_tokenizer_identity(tmp_path, monkeypatch):
    data = b"test bytes only for negative identity check"
    (tmp_path / "onnx").mkdir()
    (tmp_path / "onnx/model.onnx").write_bytes(data)
    (tmp_path / "tokenizer.json").write_bytes(b"{}")
    monkeypatch.setattr(local, "WEIGHT_SHA", hashlib.sha256(data).hexdigest())
    with pytest.raises(ValueError, match="tokenizer"):
        local.check_weights(tmp_path)


def test_missing_weights_cannot_be_replaced_with_fixture(tmp_path):
    with pytest.raises(FileNotFoundError):
        local.check_weights(tmp_path)
````
