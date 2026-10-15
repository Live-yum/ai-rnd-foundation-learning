# .github/workflows/model-settings-connection.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/model-settings-connection.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L101。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4297`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/model-settings-connection.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cd4972918d38bfc91f9f16bc5858939c0fc039882241d379508f8debdd281a95"} -->
````yaml
# .github/workflows/model-settings-connection.yml
name: Bounded model settings connection acceptance
on:
  push:
    branches: [fix/model-settings-env-connection]
permissions:
  contents: read
concurrency:
  group: rnd-model-settings-connection
  cancel-in-progress: false
jobs:
  connection:
    # One marked branch-creation push only. Later fix pushes and reruns must
    # never spend another provider request under this acceptance authorization.
    if: >-
      github.repository == 'Live-yum/ai-rnd-foundation-learning' &&
      github.ref == 'refs/heads/fix/model-settings-env-connection' &&
      github.event.created == true &&
      github.event.before == '0000000000000000000000000000000000000000' &&
      contains(github.event.head_commit.message, '[settings-connection-acceptance-20261015]') &&
      github.run_attempt == 1
    environment: rnd
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - name: Install locked dependencies without provider credentials
        run: uv sync --locked
      - name: Verify offline contracts before secret injection
        run: uv run --no-sync pytest tests/test_ci_model_settings_connection.py tests/test_model_settings.py tests/test_model_connection.py tests/test_model_discovery.py -q
      - name: One real default probe and optional catalog, no retries
        env:
          API_KEY: ${{ secrets.API_KEY }}
          BASE_URL: ${{ vars.BASE_URL }}
          MODE: ${{ vars.MODE }}
        run: uv run --no-sync python -m scripts.ci_model_settings_connection
      - name: Upload static classifications only
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: model-settings-connection-${{ github.run_id }}
          path: reports/model-settings-connection/summary.json
          if-no-files-found: ignore
          retention-days: 7
  browser:
    # Separate runner: no rnd environment and no model-provider credentials.
    # A probe configuration/network failure must not suppress fixture UI evidence.
    if: >-
      github.repository == 'Live-yum/ai-rnd-foundation-learning' &&
      github.ref == 'refs/heads/fix/model-settings-env-connection' &&
      github.run_attempt == 1
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      PLAYWRIGHT_BROWSERS_PATH: '0'
      PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
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
      - run: uv sync --locked --all-extras
      - run: npm ci --prefix tools/node --no-audit --no-fund
      - run: npm run build --prefix tools/node
      - name: Install fixed isolated Chromium test tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - run: npm ci --prefix ui --no-audit --no-fund
      - run: npm run build --prefix ui
      - name: Real Chromium and local HTTP with explicit fake models only
        shell: bash
        run: |
          set -o pipefail
          mkdir -p reports/guided-browser
          uv run --no-sync python -m scripts.ci_guided_browser 2>&1 | tee reports/guided-browser/runner.log
      - name: Upload anonymous fixture UI evidence, including failures
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: model-settings-fixture-browser-${{ github.run_id }}
          # Never upload temporary browser-input/config files, databases or .env.
          path: |
            reports/guided-browser/summary.json
            reports/guided-browser/settings.json
            reports/guided-browser/screenshot-manifest.json
            reports/guided-browser/*-failure-facts.json
            reports/guided-browser/*.png
            reports/guided-browser/*.log
            reports/guided-browser/manual-stale/*.log
          if-no-files-found: ignore
          retention-days: 7
````
