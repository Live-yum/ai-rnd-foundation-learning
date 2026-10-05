# tests/fixtures/contest_native/module_contest/__init__.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `tests/fixtures/contest_native/module_contest/__init__.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L1。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`74`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/contest_native/module_contest/__init__.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "744ff127760936adcb57a88c562b67e093786c30c9a5531237864977b477c553"} -->
````python
# tests/fixtures/contest_native/module_contest/__init__.py
"""Human-authored CI fixture; copied into the real native plugin tree."""
````
