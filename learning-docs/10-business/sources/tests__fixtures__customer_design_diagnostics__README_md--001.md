# tests/fixtures/customer_design_diagnostics/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L27。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1659`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "80dab4d872da28a44b4303a79769c8100bd9e098f0284bcb1b21edf807c86cd0"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/README.md -->
# Recorded unapproved diagnostic contracts

These are normalized, secret-scanned synthetic customer requirements and candidate plans
from genuine DeepSeek Actions run 36781842534 on source
`f6bcbedfc14ded4c720d6cac40c4757369d90b4c`.

They are deliberately **unapproved**, **not executable**, and **not delivery proof**.
They are used only by pure offline requirement/business validation regression tests.
No generation, model call, approval, or runtime acceptance may consume these candidates.
Tests may mutate a deep copy to establish which explicit obligation causes a validator gap.
The recorded originals remain unchanged, including genuine missing permissions.

Artifact IDs and original normalized SHA256:
- python-basic: 11128691529, c168b09cfb9ad7a06c55f2e3fcd78ecba260dd78bc82793e2c8dff35b75ea9c8
- fastapiadmin: 11128137959, 09fead7bdd076d1f50dacab5574072c78ac15900aa6141f58e4d90e1d9a702c6
- yudao-vben: 11127513878, 387597908c075b12193585499482402359ba99afcc8c99cd173e17d93f806afe

## Additional exact failure regressions

Subdirectory `2a4106f` records the same bounded diagnostics from genuine run
36786392571 on source `2a4106fc108d7aabebf7185a0e05afb51489ddd4`.
The same unapproved, no-execution boundaries apply, including Python's contract
whose actual workflow reached independent product verification before failing.

- python-basic: artifact11130460173, SHA2560ad2c86625dd7454bab688edf402c59b4a3d28ba3e4f5eb07f8c3b9747dfd8a5
- fastapiadmin: artifact11130470403, SHA2563b03ca2f5b8b488bf958f4e685c398428b17e640d697bdcf284ddabfddc13099
- yudao-vben: artifact11130296278, SHA256561b5bcabca92dff7d845c31ca33f2c3c221004bd195384cbca471e8db0fa72c
````
