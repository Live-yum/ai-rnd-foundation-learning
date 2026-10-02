# .github/workflows/local-embeddings.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/local-embeddings.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L47。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1556`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/local-embeddings.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "07b19893f4e90f9ed542a8a45fa42a3b66daea53c567d2b32c94e41ed16a0695"} -->
````yaml
# .github/workflows/local-embeddings.yml
name: Real local embedding and Continue acceptance
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: local-embeddings-${{ github.ref }}
  cancel-in-progress: true
jobs:
  real-cpu-weights:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      HF_HUB_DISABLE_TELEMETRY: '1'
      HF_HUB_DISABLE_IMPLICIT_TOKEN: '1'
      HF_HUB_DISABLE_XET: '1'
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install locked platform and independent CPU inference runtime
        run: |
          uv sync --locked --all-extras
          uv sync --locked --project tools/embeddings --python 3.12
          npm ci --prefix tools/node --no-audit --no-fund
          npm run build --prefix tools/node
      - name: Explicitly download checksum-pinned official public weights
        run: tools/embeddings/.venv/bin/python scripts/ci_local_embeddings.py prepare
      - name: Run local inference and actual Continue hybrid retrieval without model credentials
        env:
          HF_HUB_OFFLINE: '1'
          TRANSFORMERS_OFFLINE: '1'
        run: uv run python -m scripts.ci_local_embeddings verify
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: real-local-embedding-evidence
          path: reports/local-embeddings.json
````
