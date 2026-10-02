# tests/fixtures/customer_design_diagnostics/dd7e5f2/FASTAPI_PROVENANCE.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/dd7e5f2/FASTAPI_PROVENANCE.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L26。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1648`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/dd7e5f2/FASTAPI_PROVENANCE.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "46b2b39e5a73125e295ae6260b5edd97dde318f6a654b04b9c52cc8f0e1aa87a"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/dd7e5f2/FASTAPI_PROVENANCE.md -->
# FastapiAdmin unapproved diagnostic replay only

These two files are byte-exact copies of normalized diagnostics from genuine
DeepSeek Actions run [36840557604](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36840557604),
attempt 1, source commit `dd7e5f2135fdfe8b84f36dd1de5ab6e090c6a45a`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| fastapi-unapproved-design.json | 49980 | 9c8cdc4576208ee3f3954d724a7789e2f635e50ae25b66f65d75e34d0e41b5f5 |
| fastapi-summary.json | 17671 | a7782be7e86a74cfae44ca9ccad835107ac4a7de2e7fff9ebcb4d747b6138e7a |

The design envelope remains explicitly **unapproved**, **non-executable**, and
for **offline contract validation only**. Only pure Requirement/Plan validators
may read it or validate deep-copied synthetic mutations. Never approve, generate
from, execute, supply this candidate as provider output, or use it as delivery
proof or as a substitute for a future model-generated Plan.

The unchanged requirement has two positive service/customers/all permission
declarations, one granting read and one granting read_metrics. The unchanged
candidate correctly consolidates them into the sole Plan row allowed for that
role/resource. The original summary records two false coverage gaps and two
schema-rejected repair attempts to duplicate permission rows. The regression
accepts their exact semantic action union within the same source collection;
independent matrices, restrictions, row scopes, extra actions, foreign grants,
and malformed declarations remain binding. A pure validator pass is not model
workflow completion, design approval, runtime acceptance, or delivery proof.
````
