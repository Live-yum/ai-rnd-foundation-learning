# .github/workflows/test.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/test.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L233。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8447`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/test.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db72663a3dbbc2136b5611f4073f07bcb93f7f688ffc2e9b20486b1d58189702"} -->
````yaml
# .github/workflows/test.yml
name: Python 3.14 acceptance
on:
  push:
    branches: [main, feat/guided-multimodel-workbench]
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: test-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
env:
  PLAYWRIGHT_BROWSERS_PATH: '0'
  PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
jobs:
  frontend:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm ci --prefix ui --no-audit --no-fund
      - run: npm run format:check --prefix ui
      - run: npm test --prefix ui
      - run: npm run build --prefix ui
      - name: Verify committed local UI bundle matches its source
        run: git diff --exit-code -- workbench/web
  tests:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    # Windows includes a cold native dependency install before the complete suite.
    # Keep individual test/browser deadlines unchanged; bound each job explicitly.
    timeout-minutes: ${{ matrix.os == 'windows-latest' && 60 || 35 }}
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
      - run: uv run python --version
      - name: Check capability protocol and receipt portability before full acceptance
        env:
          RND_REQUIRE_NODE_TESTS: '1'
        run: uv run pytest -q tests/test_capability_browser_protocol.py tests/test_capability_isolation.py tests/test_daytona_capability_profile.py tests/test_capability_browser_preflight.py
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run python -m scripts.build_handbook --check
      - run: uv run python -m scripts.build_learning_docs --check
      - run: uv run pytest -m "not postgres" --junitxml=reports/tests.xml --cov=workbench --cov-report=term-missing
        env:
          RND_REQUIRE_NODE_TESTS: '1'
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: tests-${{ matrix.os }}
          path: reports/
  postgres:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_HOST_AUTH_METHOD: trust
          POSTGRES_DB: workbench_test
        ports: ['127.0.0.1:5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 20
    env:
      TEST_DATABASE_URL: postgresql+psycopg://postgres@127.0.0.1:5432/workbench_test
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
      - run: uv sync --locked --all-extras
      - run: uv run pytest -m postgres -q --junitxml=reports/postgres.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: postgres-evidence
          path: reports/
  clean-install:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 30
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
      - run: uv sync --locked
      - run: uv run python -m scripts.ci_clean_install
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: clean-install-${{ matrix.os }}
          path: reports/
  native-sources:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - run: uv sync --locked
      - run: uv run python -m scripts.ci_native_sources
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pinned-native-source-evidence
          path: reports/
  handbook-only:
    runs-on: ubuntu-latest
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - run: uv sync --locked --all-extras
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install mandatory product browser acceptance tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - name: Reconstruct from only learning-docs and test the complete platform
        run: uv run python -m scripts.ci_learning_docs
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: handbook-clean-room
          path: |
            reports/handbook-clean-room.json
            reports/handbook-tests.xml
            reports/handbook-test-status.json
            reports/learning-docs-clean-room.json
            reports/learning-docs-tests.xml
  browser:
    runs-on: ubuntu-latest
    timeout-minutes: 15
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
      - name: Install isolated Chromium test tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - run: npm ci --prefix ui --no-audit --no-fund
      - run: npm run build --prefix ui
      - run: uv run python -m scripts.ci_guided_browser
      - name: Verify persisted registration scope recovery in the real workbench
        run: uv run python -m scripts.ci_signup_scope_browser
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: guided-workbench-and-news-browser
          path: reports/
  delivery:
    needs: [frontend, tests, postgres, clean-install, native-sources, handbook-only, browser]
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - run: git archive --format=zip --output=workbench-source.zip HEAD
      - uses: actions/upload-artifact@v4
        with:
          name: source-and-complete-handbook
          path: |
            workbench-source.zip
            从零实现AI研发平台_逐步实操手册_完整版.md
            learning-docs/
````
