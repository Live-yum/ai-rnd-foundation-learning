# tests/fixtures/customer_design_diagnostics/0e8ebdd/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/0e8ebdd/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L28。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1812`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/0e8ebdd/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "08afaf87884a8e1041e13dfbbf50c1bb75f6b7f4a56766c816b337e8c03f9e4f"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/0e8ebdd/README.md -->
# Unapproved diagnostic replay only

These are byte-exact, normalized diagnostics from genuine DeepSeek Actions run
[36826237130](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36826237130),
at source commit `0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9`.
The `*-summary.json` files retain the original failure messages, source indices,
provider receipts, and run identity unchanged. The Python job was `110252442739`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| python-unapproved-design.json | 49293 | a492b0e6e379b6062698bfde77b05a52ba81aab7e7b47d2a84e15e5173fd7ab6 |
| python-summary.json | 18684 | b64b86827ef6ecd63df33ca9fdb3c08ac9b2b9917adc2f32a9e1f1871159f929 |
| yudao-unapproved-design.json | 48753 | dd7bf0dbe805ae9d1527b899bd014fd87e1c69179b2134748cdf7d49b0d7c115 |
| yudao-summary.json | 28816 | 755265754504037327c38c643592894c51cd9789ac399023f1037b6b299c5631 |

Both design envelopes are explicitly unapproved, non-executable, and for offline
contract validation only. Only pure Requirement/Plan validators may replay them
or validate deep-copied synthetic mutations. Never approve, generate from,
execute, supply these candidates as provider output, or use them as delivery
proof or substitutes for a future model-generated Plan.

The original Python diagnostics contain two false positives: a forbidden-field
mention interpreted as a required field, and a multi-metric list interpreted as
one filtered metric. The original Yudao diagnostics contain two false broad
search-target obligations plus seven genuine typed `searchable=False` conflicts.
Tests preserve those seven conflicts on the unchanged Yudao candidate; a separate
synthetic deep copy corrects only its explicit false flags. A pure validator pass
is not workflow completion, approval, or customer acceptance.
````
