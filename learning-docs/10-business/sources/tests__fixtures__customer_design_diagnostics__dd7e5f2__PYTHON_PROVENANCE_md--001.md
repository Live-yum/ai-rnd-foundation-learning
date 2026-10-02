# tests/fixtures/customer_design_diagnostics/dd7e5f2/PYTHON_PROVENANCE.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/dd7e5f2/PYTHON_PROVENANCE.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L28。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1671`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/dd7e5f2/PYTHON_PROVENANCE.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "799c42c171aa7a55a3daa5d34837bf54cd335ba124b6439294ebaa30342b87b1"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/dd7e5f2/PYTHON_PROVENANCE.md -->
# Unapproved Python diagnostic replay only

The two Python files are byte-exact normalized diagnostics from genuine DeepSeek
Actions run [36840557604](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36840557604),
source commit `dd7e5f2135fdfe8b84f36dd1de5ab6e090c6a45a`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| python-unapproved-design.json | 46721 | fd69760f6ad7b4431b16a387e47ea29ee22dbea03f811199dc5f996f2456d642 |
| python-summary.json | 15872 | 018c8f491895293e02f522fcce19a80f191df60ad302463bf1ee668b6a0ab7f5 |

The summary preserves the original failure, source indices, run identity, and
provider receipts unchanged. Acceptance item 1 names independent customers
length limits and requests/tasks length limits. The original clause parser
carried the customers namespace into the explicit requests/tasks subject and
reported a nonexistent customers.title obligation.

The design envelope is explicitly unapproved and non-executable. It is only an
input to pure Requirement/Plan validation and deep-copied diagnostic mutations.
Never approve, generate from, execute, supply it as provider output, or substitute
it for a future genuine model-generated Plan. Passing pure validation is not
workflow completion, execution authorization, or customer acceptance.

The generic regressions exercise equivalent entity groups and explicit switches
across punctuation/conjunctions, qualified field references, field exclusions,
length constraints, typed ledger conflicts, and requirement-only source
projection. They preserve genuine missing-field and length violations. No model
calls are needed to reproduce or verify these parser behaviors.
````
