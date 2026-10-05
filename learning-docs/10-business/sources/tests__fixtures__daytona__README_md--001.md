# tests/fixtures/daytona/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/daytona/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L15。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`849`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/daytona/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b4a3848ad2ab13d01a4e1a3c5585690fe4735337097b6f4211ccac71216b2026"} -->
````markdown
<!-- tests/fixtures/daytona/README.md -->
# Pinned Daytona API image-reference fixture

`docker-image.util.ts` is an unchanged upstream file, used to execute the actual
parser and serializer before and after the local build patch. It is not a
reimplementation or live-container proof.

- Upstream: https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/api/src/common/utils/docker-image.util.ts
- Release: v0.190.0
- Git blob: `b0b03b28ce08b2865db9d2dc291c1745cb6492cf`
- Copyright 2025 Daytona Platforms Inc.; AGPL-3.0, included in `LICENSE`.
- Local change: `tools/daytona/api-digest-reference.patch`, applied only after
  checking the exact source blob and patch bytes by `scripts.daytona_build`.

The regression executes this TypeScript directly with Node's type stripping.
API build tests also reject source/revision/patch drift before any image build.
````
