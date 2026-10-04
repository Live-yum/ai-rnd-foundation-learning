# .github/workflows/capability-browser-isolation.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/capability-browser-isolation.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L58。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2408`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/capability-browser-isolation.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "eb341f763f2880e029c1d10669fead8046a6e4970646c09ad9fcc9cfba55b73a"} -->
````yaml
# .github/workflows/capability-browser-isolation.yml
name: Offline candidate browser isolation
on:
  pull_request:
    paths:
      - 'workbench/capability_browser_isolation.py'
      - 'workbench/capability_verification.py'
      - 'scripts/capability_browser*'
      - 'scripts/ci_capability_browser_isolation.py'
      - 'tests/test_capability_browser_isolation.py'
      - 'tools/browser/**'
      - '.github/workflows/capability-browser-isolation.yml'
  push:
    branches: [feature/capability-nodes-transcript]
    paths:
      - 'workbench/capability_browser_isolation.py'
      - 'workbench/capability_verification.py'
      - 'scripts/capability_browser*'
      - 'scripts/ci_capability_browser_isolation.py'
      - 'tests/test_capability_browser_isolation.py'
      - 'tools/browser/**'
      - '.github/workflows/capability-browser-isolation.yml'
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: offline-browser-${{ github.ref }}
  cancel-in-progress: true
jobs:
  browser-isolation:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - run: uv sync --locked
      - name: Validate isolation policy and bounded relay protocol
        run: uv run pytest -q tests/test_capability_browser_isolation.py
      - name: Build pinned official Playwright worker
        run: |
          docker --host unix:///var/run/docker.sock build -f tools/browser/Dockerfile -t rnd-capability-browser .
          echo "CAPABILITY_BROWSER_IMAGE=$(docker --host unix:///var/run/docker.sock image inspect --format '{{.Id}}' rnd-capability-browser)" >> "$GITHUB_ENV"
      - name: Require real kernel network resource browser and cleanup proof
        run: uv run python -m scripts.ci_capability_browser_isolation
      - name: Remove only this job's offline browser workers after interruption
        if: always()
        run: |
          docker --host unix:///var/run/docker.sock ps -a --filter 'name=^/rnd-browser-' --format '{{.ID}}' | while read -r id; do
            test -z "$id" || docker --host unix:///var/run/docker.sock rm -f "$id"
          done
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: browser-isolation-${{ github.sha }}-${{ github.run_id }}
          path: reports/capability-browser-isolation.json
````
