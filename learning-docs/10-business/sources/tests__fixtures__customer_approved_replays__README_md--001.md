# tests/fixtures/customer_approved_replays/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_approved_replays/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L11。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2410`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_approved_replays/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c024ec03263fd57d059b8b9e2f53c1933ff9cfecd451907d7d0bec55dfab6ba3"} -->
````markdown
<!-- tests/fixtures/customer_approved_replays/README.md -->
# Approved synthetic customer replay

`yudao-1d7.json` is the byte-identical normalized Plan that passed design approval, native generation/verification, and independent model review in real DeepSeek run [36795375784](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36795375784), job 110157491211, source `1d7c70b03e63509830e97af9af398c0bd148902e`. The overall run then failed at ZIP extraction because the generic 10,000-entry ceiling rejected the full original Yudao monorepo. This fixture is not evidence that the downloaded product passed.

Artifact 11133539312 retained only this approved synthetic Plan after schema, size, known-key and credential-pattern rejection. Its SHA-256 is `16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5` (19,534 bytes). The loader rechecks hash, template, schema, size and credential patterns before any replay.

The `approved-1d7` customer-runtime case regenerates this exact Plan with the original pinned native generator, consumes the distributable ZIP, and verifies an independent database, browser and restart. It makes no model calls. The genuine real-model workflow continues to obtain a fresh recommendation, Plan and independent review and never reads this fixture. Unapproved diagnostic artifacts in the sibling directory must never be used for generation.

`fastapi-0e8.json` is the byte-identical normalized Plan approved by the design gate in real DeepSeek run [36826237130](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36826237130), job 110252442728, source `0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9`. Artifact 11145826640 retained this approved synthetic Plan with SHA-256 `023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4` (19,099 bytes). Native execution reported accepted, but the production evidence projection failed before independent model review. The original complete execution report was not exported, so neither the fixture nor that run establishes a successful full workflow or the precise original projection failure.

The `approved-0e8` FastapiAdmin customer-runtime case uses this exact approved Plan without model calls. It must retain fresh, genuinely executed original/restored acceptance evidence and pass the same strict evidence projection used by production review. This fixture is never used as a replacement for fresh output in the genuine real-model workflow.
````
