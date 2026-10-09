# .github/workflows/template-project-acceptance.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/template-project-acceptance.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L82。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3266`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/template-project-acceptance.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0b2674ff850d3debcea7011f89d05342209e109599d6055e3102f78aa9af7033"} -->
````yaml
# .github/workflows/template-project-acceptance.yml
name: Three-project live acceptance

on:
  workflow_dispatch:
  pull_request:
    types: [labeled]

permissions:
  contents: read

concurrency:
  group: rnd-three-project-live-acceptance
  cancel-in-progress: false

jobs:
  all-three-projects:
    if: >-
      github.repository == 'Live-yum/ai-rnd-foundation-learning' &&
      (github.event_name == 'workflow_dispatch' ||
       (github.event.action == 'labeled' &&
        github.event.label.name == 'run-live-acceptance' &&
        github.event.pull_request.head.repo.full_name == github.repository &&
        github.event.pull_request.base.repo.full_name == github.repository))
    environment: rnd
    runs-on: ubuntu-latest
    timeout-minutes: 90
    env:
      ACCEPTANCE_HEAD_SHA: ${{ github.event.pull_request.head.sha || github.sha }}
      PYTHONUTF8: '1'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ env.ACCEPTANCE_HEAD_SHA }}
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install locked dependencies before credential access
        run: uv sync --locked
      - name: Verify scenario and acceptance guards without a model
        run: |
          uv run python -m scripts.ci_template_projects --validate-fixtures
          uv run pytest tests/test_template_project_acceptance.py -q
      - name: Install pinned product browser without model credentials
        env:
          PLAYWRIGHT_BROWSERS_PATH: '0'
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - name: Generate and accept all three real-model projects
        env:
          API_KEY: ${{ secrets.API_KEY }}
          BASE_URL: ${{ vars.BASE_URL }}
          MODE: ${{ vars.MODE }}
          # Explicit opt-in for the user-configured compatible HTTP gateway.
          ALLOW_INSECURE_MODEL_HTTP: 'true'
          PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
          PLAYWRIGHT_BROWSERS_PATH: '0'
        run: uv run python -m scripts.ci_template_projects
      - name: Upload bounded acceptance receipts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: three-project-receipts-${{ env.ACCEPTANCE_HEAD_SHA }}-${{ github.run_id }}-${{ github.run_attempt }}
          path: |
            reports/template-project-acceptance/summary.json
            reports/template-project-acceptance/reading-shelf.json
            reports/template-project-acceptance/stock-purchasing.json
            reports/template-project-acceptance/facilities-ops.json
          if-no-files-found: ignore
          retention-days: 7
      - name: Upload verified synthetic project screens
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: three-project-ui-${{ env.ACCEPTANCE_HEAD_SHA }}-${{ github.run_id }}-${{ github.run_attempt }}
          path: reports/template-project-acceptance/screenshots/*.png
          if-no-files-found: error
          retention-days: 7
````
