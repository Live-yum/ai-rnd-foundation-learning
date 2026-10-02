# tests/fixtures/customer_design_diagnostics/d3ea684/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/d3ea684/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L19。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1210`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/d3ea684/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5a2d7d8d8ae7a675f184db71ca12e55a0e94ee117782649493664d833f686aea"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/d3ea684/README.md -->
# Recorded d3ea684 diagnostics

These are sanitized synthetic customer-service CI artifacts from run 36899875461,
commit d3ea6848360054bc83792bb5c6defbe34409b0a9. They contain no provider credentials
or real customer records. The summaries preserve failed outcomes and source
provenance. The paired design files are explicitly unapproved, pure-validator
inputs: never approve, generate, execute, or replace them with corrected output.

- Fastapi: mixed keyword-search and exact-filter prose was bound across separate
  field lists although the explicit typed properties matched the candidate
- Yudao: a multi-role acceptance sentence invented service request creation; the
  typed grant-only contract did not grant it, and independent review blocked
  delivery. Schema-valid JSON does not prove arbitrary prose is semantically
  consistent. The fix constrains the existing analysis prompt and Pydantic schema;
  it does not grant the action or weaken independent review

Exact byte sizes and SHA-256 values are pinned in the offline regression tests.
Corrected synthetic cases are built independently in the tests. Genuine success
must be established by a new authorized full workflow on the final source SHA.
````
