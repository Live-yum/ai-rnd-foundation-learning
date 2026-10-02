# tests/test_native_delivery_boundaries.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_runtime_logs_never_enter_source_manifest`（L7–L13）：接收`tmp_path`。 控制顺序：L12断言`set(dict(files(tmp_path))) == {"app.py"}`；L13断言`set(manifest(tmp_path)) == {"app.py"}`。 调用`(tmp_path / "app.py").write_text`、`(tmp_path / "logs").mkdir`、`(tmp_path / "logs/server.log").write_text`、`(tmp_path / ".env.native").write_text`、`set`、`dict`、`files`、`manifest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_copy_is_independent_of_generated_edits`（L16–L25）：接收`tmp_path`。 控制顺序：L24断言`manifest(source) == before`；L25断言`manifest(copied) != before`。 调用`source.mkdir`、`(source / "module.py").write_text`、`manifest`、`copy_source`、`(copied / "module.py").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_delivery_boundaries.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L25。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1086`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_delivery_boundaries.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6c18b063946b20ffcad69ea6bba16861017cf19170e74ae04bca9c3cdcea2080"} -->
````python
# tests/test_native_delivery_boundaries.py
"""Native product source must not export server logs or include secret credentials."""

from workbench.filesystem import files, manifest
from workbench.native_environment import copy_source


def test_native_runtime_logs_never_enter_source_manifest(tmp_path):
    (tmp_path / "app.py").write_text("print('native')\n", encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/server.log").write_text("password=local-example\n", encoding="utf-8")
    (tmp_path / ".env.native").write_text("NATIVE_DB_PASSWORD=private\n", encoding="utf-8")
    assert set(dict(files(tmp_path))) == {"app.py"}
    assert set(manifest(tmp_path)) == {"app.py"}


def test_source_copy_is_independent_of_generated_edits(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "module.py").write_text("original\n", encoding="utf-8")
    before = manifest(source)
    copied = tmp_path / "product"
    copy_source(source, copied)
    (copied / "module.py").write_text("generated\n", encoding="utf-8")
    assert manifest(source) == before
    assert manifest(copied) != before
````
