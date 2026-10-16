# .github/workflows/source-candidate.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/source-candidate.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L36。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1353`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/source-candidate.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "70fb3ca32cb0a9d0b97cf156237fd580e69aa799d90a9c7a67addcf61f2e0f9a"} -->
````yaml
# .github/workflows/source-candidate.yml
name: Portable source candidate validation
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: source-candidate-${{ github.ref }}
  cancel-in-progress: true
jobs:
  source-only:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - name: Install only locked base and test dependencies
        run: uv sync --locked
      - name: Validate source-only generation, snapshots and honest delivery status
        run: uv run pytest -q tests/test_native_offline.py tests/test_source_candidate_delivery.py tests/test_source_candidate_workflow.py tests/test_native_optional_dependencies.py tests/test_native_service_failures.py tests/test_source_snapshot_integrity.py tests/test_source_candidate_derivation.py tests/test_native_sandbox_route_gate.py --junitxml=reports/source-candidate.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: source-candidate-${{ matrix.os }}
          path: reports/source-candidate.xml
          if-no-files-found: error
````
