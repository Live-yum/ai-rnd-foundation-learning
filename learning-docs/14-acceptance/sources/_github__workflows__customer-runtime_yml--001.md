# .github/workflows/customer-runtime.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/customer-runtime.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L192。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7320`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/customer-runtime.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a7443c0ef0773cfbf8f34582f6b5a25b531b40de98ac9304a4f3a23c48bfaa53"} -->
````yaml
# .github/workflows/customer-runtime.yml
name: Customer-service native integration
on:
  push:
    branches: [main]
    paths:
      - 'workbench/**'
      - 'templates/**'
      - 'scripts/ci_native*.py'
      - 'scripts/native_browser.cjs'
      - 'examples/plans/customer-service.json'
      - 'tests/fixtures/customer_design_diagnostics/**'
      - 'uv.lock'
      - 'pyproject.toml'
      - '.github/workflows/customer-runtime.yml'
  pull_request:
    branches: [main, feat/complete-platform-acceptance]
    paths:
      - 'workbench/**'
      - 'templates/**'
      - 'scripts/ci_native*.py'
      - 'scripts/native_browser.cjs'
      - 'examples/plans/customer-service.json'
      - 'tests/fixtures/customer_design_diagnostics/**'
      - 'uv.lock'
      - 'pyproject.toml'
      - '.github/workflows/customer-runtime.yml'
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: customer-native-${{ github.event_name }}-${{ github.ref }}
  cancel-in-progress: false
env:
  PLAYWRIGHT_BROWSERS_PATH: '0'
  PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
jobs:
  gate:
    if: >-
      github.event_name == 'push' ||
      github.event_name == 'pull_request' ||
      github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    timeout-minutes: 5
    outputs:
      sha: ${{ steps.head.outputs.sha }}
      eligible: ${{ steps.head.outputs.eligible }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          persist-credentials: false
      - name: Verify literal final head before allocating the runtime matrix
        id: head
        shell: bash
        env:
          EXPECTED_SHA: ${{ github.event.pull_request.head.sha || github.sha }}
        run: |
          set -euo pipefail
          [[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]
          test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"
          printf 'sha=%s\n' "$EXPECTED_SHA" >> "$GITHUB_OUTPUT"
          if [ -e .github/workflows/customer-handbook-once.yml ] || [ -L .github/workflows/customer-handbook-once.yml ]; then
            echo 'eligible=false' >> "$GITHUB_OUTPUT"
            echo 'Waiting for the handbook refresh and helper removal at the final head.'
          else
            echo 'eligible=true' >> "$GITHUB_OUTPUT"
            echo "Literal helper-free final head is eligible: $EXPECTED_SHA"
          fi
  runtime:
    needs: gate
    if: needs.gate.outputs.eligible == 'true'
    strategy:
      fail-fast: false
      matrix:
        include:
          - template: fastapiadmin
            case: canonical
            repository: fastapiadmin/FastapiAdmin
            revision: 1cd12c726ad9032c17ef85ce805ce991be60fbdf
            pnpm: '9.15.3'
          - template: fastapiadmin
            case: approved-0e8
            repository: fastapiadmin/FastapiAdmin
            revision: 1cd12c726ad9032c17ef85ce805ce991be60fbdf
            pnpm: '9.15.3'
          - template: yudao-vben
            case: canonical
            repository: yudaocode/yudao-cloud-mini
            revision: 47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
            pnpm: '11.16.0'
          - template: yudao-vben
            case: approved-1d7
            repository: yudaocode/yudao-cloud-mini
            revision: 47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
            pnpm: '11.16.0'
    runs-on: ubuntu-latest
    timeout-minutes: 55
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_DB: native_codegen
          POSTGRES_USER: native
          POSTGRES_PASSWORD: native-ci-only
        ports: ['127.0.0.1:5432:5432']
        options: >-
          --health-cmd "pg_isready -U native -d native_codegen"
          --health-interval 5s --health-timeout 5s --health-retries 20
      redis:
        image: redis:7.4-alpine
        ports: ['127.0.0.1:6379:6379']
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s --health-timeout 5s --health-retries 20
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.gate.outputs.sha }}
          persist-credentials: false
      - name: Verify checked-out runtime head
        shell: bash
        env:
          EXPECTED_SHA: ${{ needs.gate.outputs.sha }}
        run: |
          set -euo pipefail
          [[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]
          test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - uses: actions/setup-java@v4
        if: matrix.template == 'yudao-vben'
        with:
          distribution: temurin
          java-version: '17'
      - uses: actions/cache/restore@v4
        if: matrix.template == 'yudao-vben'
        with:
          path: ~/.m2/repository
          key: native-maven-central-v2-${{ runner.os }}-${{ matrix.revision }}
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Allocate ephemeral swap for the complete Vben build
        if: matrix.template == 'yudao-vben'
        run: |
          free -m
          df -h /mnt
          sudo fallocate -l 8G /mnt/native-build.swap
          sudo chmod 600 /mnt/native-build.swap
          sudo mkswap /mnt/native-build.swap
          sudo swapon /mnt/native-build.swap
          free -m
      - name: Install pinned native frontend package manager
        run: npm install --global pnpm@${{ matrix.pnpm }}
      - name: Install isolated browser test tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - run: uv sync --locked --all-extras
      - name: Bundled source, native generation and independent fresh-database delivery
        timeout-minutes: 45
        run: |
          if [ "$CUSTOMER_CASE" = approved-1d7 ]; then
            uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" --approved-replay yudao-1d7
          elif [ "$CUSTOMER_CASE" = approved-0e8 ]; then
            uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" --approved-replay fastapi-0e8
          else
            uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" --spec examples/plans/customer-service.json
          fi
        env:
          CUSTOMER_CASE: ${{ matrix.case }}
          CUSTOMER_TEMPLATE: ${{ matrix.template }}
          NATIVE_TEST_DATABASE_URL: postgresql+psycopg://native:native-ci-only@127.0.0.1:5432/native_codegen
          PLAYWRIGHT_BROWSERS_PATH: '0'
      - uses: actions/cache/save@v4
        if: always() && matrix.template == 'yudao-vben'
        with:
          path: ~/.m2/repository
          key: native-maven-central-v2-${{ runner.os }}-${{ matrix.revision }}
      - name: Preserve revisions and actual evidence
        if: always()
        run: |
          mkdir -p reports/native
          git rev-parse HEAD > reports/native/platform-sha.txt
          cp templates/vendor/manifest.json reports/native/bundled-template-manifest.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: native-runtime-${{ matrix.template }}-${{ matrix.case }}
          path: reports/native/
          retention-days: 7
````
