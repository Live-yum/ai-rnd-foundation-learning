# .github/workflows/native-probe.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/native-probe.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L165。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6393`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/native-probe.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1adeb51cc9d087566ec84344ea4b7256bb1c46558b5979b3982fb7b5f42b21ed"} -->
````yaml
# .github/workflows/native-probe.yml
name: Bundled template integrity
on:
  workflow_dispatch:
    inputs:
      real_model:
        description: Explicitly run paid real-model acceptance using environment rnd
        type: boolean
        required: false
        default: false
      expected_sha:
        description: Exact reviewed commit SHA required when real_model is true
        type: string
        required: false
        default: ''
  pull_request:
    paths: ['templates/vendor/**', 'workbench/vendor.py', '.github/workflows/native-probe.yml']
permissions:
  contents: read
jobs:
  verify-bundles:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - run: uv sync --locked
      - run: uv run pytest tests/test_vendor.py -q
      - run: uv run python -m scripts.ci_native_sources
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bundled-template-integrity
          path: reports/
  real-model:
    if: >-
      github.event_name == 'workflow_dispatch' && inputs.real_model == true &&
      github.repository == 'Live-yum/ai-rnd-foundation-learning' &&
      (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/feat/complete-platform-acceptance' || github.ref == 'refs/heads/feat/real-model-acceptance' || github.ref == 'refs/heads/feat/customer-service-acceptance')
    environment: rnd
    runs-on: ubuntu-latest
    timeout-minutes: 120
    strategy:
      fail-fast: false
      matrix:
        include:
          - template: python-basic
            pnpm: '9.15.3'
          - template: fastapiadmin
            pnpm: '9.15.3'
          - template: yudao-vben
            pnpm: '11.16.0'
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
    steps:
      - name: Verify explicitly requested immutable commit before model access
        shell: bash
        env:
          EXPECTED_SHA: ${{ inputs.expected_sha }}
        run: |
          set -euo pipefail
          [[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]
          test "$EXPECTED_SHA" = "$GITHUB_SHA"
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          ref: ${{ github.sha }}
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - uses: actions/setup-java@v4
        if: matrix.template == 'yudao-vben'
        with:
          distribution: temurin
          java-version: '17'
      - uses: actions/cache@v4
        if: matrix.template == 'yudao-vben'
        with:
          path: ~/.m2/repository
          key: native-maven-central-v2-${{ runner.os }}-47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
      - name: Install native package manager
        if: matrix.template != 'python-basic'
        run: npm install --global pnpm@${{ matrix.pnpm }}
      - name: Allocate ephemeral native build swap
        if: matrix.template == 'yudao-vben'
        run: |
          sudo fallocate -l 8G /mnt/native-build.swap
          sudo chmod 600 /mnt/native-build.swap
          sudo mkswap /mnt/native-build.swap
          sudo swapon /mnt/native-build.swap
      - name: Install locked platform without provider credentials
        run: uv sync --locked --all-extras
      - name: Cheap real provider smoke before browser installation
        env:
          API_KEY: ${{ secrets.APK_KEY }}
          BASE_URL: ${{ vars.BASE_URL }}
          MODE: ${{ vars.MODE }}
          PYTHONUTF8: '1'
        run: uv run python -m scripts.ci_real_model --phase smoke
      - name: Install isolated pinned browser
        env:
          PLAYWRIGHT_BROWSERS_PATH: '0'
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - name: Verify actual smart customer delivery after successful smoke
        env:
          API_KEY: ${{ secrets.APK_KEY }}
          BASE_URL: ${{ vars.BASE_URL }}
          MODE: ${{ vars.MODE }}
          PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
          PLAYWRIGHT_BROWSERS_PATH: '0'
          PYTHONUTF8: '1'
          NATIVE_TEST_DATABASE_URL: postgresql+psycopg://native:native-ci-only@127.0.0.1:5432/native_codegen
        run: uv run python -m scripts.ci_real_model --phase full --template ${{ matrix.template }}
      - name: Upload only allowlisted non-secret acceptance receipt
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: real-model-sanitized-${{ matrix.template }}-${{ github.run_id }}-${{ github.run_attempt }}
          path: reports/real-model/summary.json
          if-no-files-found: ignore
          retention-days: 7
      - name: Retain only validated secret-scanned customer Plan for offline replay
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: customer-plan-replay-${{ matrix.template }}-${{ github.sha }}
          path: reports/real-model/approved-plan-replay.json
          if-no-files-found: ignore
          retention-days: 7
      - name: Retain unapproved normalized design for offline diagnostics only
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: customer-design-replay-${{ matrix.template }}-${{ github.sha }}
          path: reports/real-model/unapproved-design-contract.json
          if-no-files-found: ignore
          retention-days: 7
      - name: Upload synthetic customer UI screenshots only
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: customer-ui-${{ matrix.template }}-${{ github.sha }}
          path: reports/real-model/screenshots/*.png
          if-no-files-found: error
          retention-days: 7
````
