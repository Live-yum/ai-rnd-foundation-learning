# .github/workflows/capability-profile.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/capability-profile.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L142。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7520`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/capability-profile.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e4c3726adf4f74df2ca50539eb7acf1775cef145cf8da468b445f24bdd32432e"} -->
````yaml
# .github/workflows/capability-profile.yml
name: Fixed authored SQLite isolation profile
on:
  pull_request:
    paths:
      - 'workbench/capability_*.py'
      - 'scripts/capability*.py'
      - 'scripts/ci_capability_security.py'
      - 'scripts/daytona_capability_profile.py'
      - 'tests/test_capability*.py'
      - 'tools/daytona/capability*'
      - 'tools/browser/**'
      - 'scripts/capability_browser*.cjs'
      - 'scripts/ci_capability_browser_isolation.py'
      - '.github/workflows/capability-profile.yml'
  push:
    branches: [main, feature/durable-capability-orchestration]
    paths:
      - 'workbench/capability_*.py'
      - 'scripts/capability_guard.py'
      - 'scripts/capability_fixture.py'
      - 'scripts/capability_browser.cjs'
      - 'tests/test_capability_browser_protocol.py'
      - 'scripts/ci_capability_profile.py'
      - 'scripts/ci_capability_browser_preflight.py'
      - 'tests/test_capability_browser_preflight.py'
      - 'scripts/daytona_capability_profile.py'
      - 'tools/daytona/capability*'
      - 'tools/browser/**'
      - 'scripts/capability_browser*.cjs'
      - 'scripts/ci_capability_browser_isolation.py'
      - '.github/workflows/capability-profile.yml'
  workflow_dispatch:
concurrency:
  group: fixed-sqlite-profile-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read
env:
  PLAYWRIGHT_BROWSERS_PATH: '0'
  PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
  PRODUCT_VERIFY_BROWSER_CHANNEL: 'chrome'
jobs:
  local-service:
    runs-on: ubuntu-24.04
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.sha }}
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: '3.14'
      - run: uv sync --locked --all-extras
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Check ordinary launcher behavior and strict receipt contracts
        env:
          RND_REQUIRE_NODE_TESTS: '1'
          RND_REQUIRE_LANDLOCK: '1'
          RND_REQUIRE_SECCOMP_BPF: '1'
        run: uv run pytest -q tests/test_capability*.py tests/test_daytona_capability_profile.py tests/test_daytona_dependency_build.py tests/test_daytona_dependency_image.py tests/test_native_capability_profile.py tests/test_ci_native_capability_security.py tests/test_extension_business_oracle.py
      - name: Install mandatory product browser acceptance tooling
        run: |
          npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
          node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
      - name: Require sandboxed browser readiness before building the local service
        run: uv run python -m scripts.ci_capability_browser_preflight
      - name: Build immutable networkless browser worker in this same job
        run: |
          docker --host unix:///var/run/docker.sock build -f tools/browser/Dockerfile -t rnd-capability-browser .
          echo "CAPABILITY_BROWSER_APPROVED_POLICY=9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f" >> "$GITHUB_ENV"
          echo "CAPABILITY_BROWSER_IMAGE=$(docker --host unix:///var/run/docker.sock image inspect --format '{{.Id}}' rnd-capability-browser)" >> "$GITHUB_ENV"
      - name: Require real browser network resource and cleanup proof in this same job
        run: uv run python -m scripts.ci_capability_browser_isolation
      - name: Create the local control plane with random local credentials
        run: uv run python -m scripts.daytona_local prepare --directory .data/daytona-capability
      - name: Build pinned release locally and lock immutable images
        run: uv run python -m scripts.daytona_local images --directory .data/daytona-capability
      - name: Build the offline snapshot in the local registry
        run: uv run python -m scripts.daytona_capability_profile prepare
      - name: Start local API, Runner, Dex, database, registry and storage
        run: uv run python -m scripts.daytona_capability_profile up
      - name: Authenticate through real local Dex and API
        run: uv run python -m scripts.daytona_bootstrap auth --directory .data/daytona-capability
      - name: Register the prebuilt snapshot without any hosted service
        run: uv run python -m scripts.daytona_bootstrap snapshot --directory .data/daytona-capability
      - name: Require positive fixed-application isolation profile and real HTTP browser database restart
        run: uv run python -m scripts.ci_capability_profile
      - name: Require real adversarial isolation and resource enforcement before source admission
        run: uv run python -m scripts.ci_capability_security
      - name: Preserve bounded redacted diagnostics only
        if: always()
        run: |
          python - <<'PY'
          import json, pathlib, subprocess
          root = pathlib.Path('.data/daytona-capability')
          secrets = []
          for name in ['credentials.json', 'api-key.json']:
              path = root / name
              if path.exists():
                  secrets += [v for v in json.loads(path.read_text()).values() if isinstance(v,str) and len(v)>5]
          outputs = []
          compose = root / 'compose.capability.lock.yaml'
          if compose.exists():
              for args in [['ps','--all'],['logs','--no-color','--tail','80']]:
                  run = subprocess.run(['docker','--host','unix:///var/run/docker.sock','compose','-p','rnd-daytona-capability','-f',str(compose),*args], capture_output=True, timeout=60)
                  text=(run.stdout+run.stderr).decode('utf-8',errors='replace')[-80000:]
                  for secret in sorted(secrets,key=len,reverse=True):
                      text=text.replace(secret,'[REDACTED]')
                  outputs.append(text)
          reports = pathlib.Path('reports'); reports.mkdir(exist_ok=True)
          (reports/'daytona-local-diagnostics.log').write_text('\n'.join(outputs),encoding='utf-8')
          if (root/'images.lock.json').exists():
              (reports/'daytona-images.lock.json').write_bytes((root/'images.lock.json').read_bytes())
          profile = root / 'capability-profile.lock.json'
          if profile.exists():
              (reports/'capability-image-provenance.json').write_bytes(profile.read_bytes())
          print('Diagnostics saved without local credentials or environment files.')
          PY
      - name: Stop this local test deployment without deleting persistent volumes
        if: always()
        run: |
          if test -f .data/daytona-capability/compose.capability.lock.yaml; then
            docker --host unix:///var/run/docker.sock compose -p rnd-daytona-capability -f .data/daytona-capability/compose.capability.lock.yaml down
          fi
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: fixed-sqlite-profile-${{ github.sha }}-${{ github.run_id }}
          path: |
            reports/daytona-local-diagnostics.log
            reports/daytona-images.lock.json
            reports/capability-profile.json
            reports/capability-profile-detail.json
            reports/capability-image-provenance.json
            reports/capability-browser-preflight.json
            reports/capability-security.json
            reports/capability-security-detail.json
            reports/capability-browser-isolation.json
            reports/capability-browser-raw-syscalls.json
````
