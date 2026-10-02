# .github/workflows/toolchain.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/toolchain.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L52。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1730`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/toolchain.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1855bab469168003116b626ea7c6c96501f007cd7d4a74cea1aa014cc8933129"} -->
````yaml
# .github/workflows/toolchain.yml
name: Toolchain integration acceptance
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: toolchain-${{ github.ref }}
  cancel-in-progress: true
env:
  PLAYWRIGHT_BROWSERS_PATH: '0'
  PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
jobs:
  real-tools:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 30
    env:
      PYTHONUTF8: '1'
      LITELLM_LOCAL_MODEL_COST_MAP: 'True'
      AIDER_ANALYTICS: 'false'
      RND_REQUIRE_NODE_TESTS: '1'
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
      - name: Install mandatory product browser acceptance tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - run: npm ci --prefix tools/node --no-audit --no-fund
      - run: npm run build --prefix tools/node
      - run: uv sync --locked --all-extras
      - run: uv sync --locked --project tools/aider --python 3.12
      - run: uv run pytest tests/test_toolchain.py tests/test_continue_index.py -q --junitxml=reports/toolchain-contracts.xml
      - run: uv run python -m scripts.ci_toolchain
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: toolchain-${{ matrix.os }}
          path: reports/
````
