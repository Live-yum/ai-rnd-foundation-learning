# .github/workflows/native-toolchain-daytona.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/native-toolchain-daytona.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L124。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5137`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/native-toolchain-daytona.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "611cdc0f2fd053dc459c19b16fca412693cf7505b5ac0a97baf7921609f9d444"} -->
````yaml
# .github/workflows/native-toolchain-daytona.yml
name: Native Plop Aider and Daytona database matrix
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: native-toolchain-daytona-${{ github.ref }}
  cancel-in-progress: true
jobs:
  real-matrix:
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
    runs-on: ubuntu-latest
    timeout-minutes: 120
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
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
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
      - name: Reuse public Maven dependencies for the exact pinned Yudao revision
        uses: actions/cache/restore@v4
        if: matrix.template == 'yudao-vben'
        with:
          path: ~/.m2/repository
          key: native-maven-central-v2-${{ runner.os }}-47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
      - name: Provision ephemeral build capacity without removing verification
        run: |
          df -h
          sudo fallocate -l 10G /mnt/native-tools.swap
          sudo chmod 600 /mnt/native-tools.swap
          sudo mkswap /mnt/native-tools.swap
          sudo swapon /mnt/native-tools.swap
      - name: Install pinned local tooling
        run: |
          uv sync --locked --all-extras
          uv sync --locked --project tools/aider --python 3.12
          npm ci --prefix tools/node --no-audit --no-fund
          npm run build --prefix tools/node
          npm install --global pnpm@${{ matrix.pnpm }}
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          PLAYWRIGHT_BROWSERS_PATH=0 .native/browser/node_modules/.bin/playwright install --with-deps chromium
      - name: Actual Plop, Aider failed candidate rollback, repair, APIs, browser and new database
        if: matrix.template != 'python-basic'
        run: uv run python -m scripts.ci_native_tools ${{ matrix.template }}
        env:
          NATIVE_TEST_DATABASE_URL: postgresql+psycopg://native:native-ci-only@127.0.0.1:5432/native_codegen
          PLAYWRIGHT_BROWSERS_PATH: '0'
      - name: Deterministic PostgreSQL news product
        if: matrix.template == 'python-basic'
        run: uv run python -m scripts.ci_daytona_matrix prepare-basic python-basic
      - name: Prepare the pinned local Daytona control plane
        run: |
          uv run python -m scripts.daytona_local prepare
          uv run python -m scripts.daytona_local images
          uv run python -m scripts.daytona_local snapshot-image
          uv run python -m scripts.daytona_local up
          uv run python -m scripts.daytona_bootstrap auth
          uv run python -m scripts.daytona_bootstrap snapshot
      - name: Build registered per-stack offline dependencies into local registry
        run: uv run python -m scripts.daytona_matrix_image ${{ matrix.template }} --database postgresql --product .native/tool-product
      - name: Register only this immutable local snapshot
        run: uv run python -m scripts.daytona_bootstrap snapshot
      - name: No-egress sandbox owns its database and validates independent native launch
        run: uv run python -m scripts.ci_daytona_matrix verify ${{ matrix.template }}
        env:
          DAYTONA_CAPTURE_STARTUP_DIAGNOSTICS: 'true'
      - name: Preserve bounded redacted failure evidence
        if: always()
        run: |
          uv run python -m scripts.daytona_diagnostics
          mkdir -p reports
          git rev-parse HEAD > reports/matrix-commit.txt
          if test -f .native/daytona-verification.json; then cp .native/daytona-verification.json reports/; fi
      - name: Stop only this job's local test installation
        if: always()
        run: |
          if test -f .data/daytona-local/compose.lock.yaml; then
            docker --host unix:///var/run/docker.sock compose -p rnd-daytona-local -f .data/daytona-local/compose.lock.yaml down
          fi
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: native-toolchain-daytona-${{ matrix.template }}
          path: |
            reports/native-tools/
            reports/daytona*.json
            reports/daytona*.log
            reports/matrix-commit.txt
          retention-days: 14
````
