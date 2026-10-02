# .github/workflows/daytona-local.yml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可复现的自动化验收配置。** on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。

**对应关系：** 与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.github/workflows/daytona-local.yml`；**本文件共有 1 段**。本段覆盖源文件 L1–L93。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4355`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".github/workflows/daytona-local.yml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "005f6752c65ea8721b2c632f334c1f8d2a6b4ccd881467cd82e0ce917d9c5bed"} -->
````yaml
# .github/workflows/daytona-local.yml
name: Self-hosted Daytona local acceptance
on:
  pull_request:
  workflow_dispatch:
  workflow_call:
    inputs:
      source-ref:
        type: string
        required: true
permissions:
  contents: read
env:
  PLAYWRIGHT_BROWSERS_PATH: '0'
  PRODUCT_VERIFY_PLAYWRIGHT: ${{ github.workspace }}/.native/browser/node_modules/playwright
jobs:
  local-service:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.source-ref || github.sha }}
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
      - name: Prepare locked local Aider and Continue tools
        run: |
          uv sync --locked --project tools/aider --python 3.12
          npm ci --prefix tools/node --no-audit --no-fund
          npm run build --prefix tools/node
      - name: Create the local control plane with random local credentials
        run: uv run python -m scripts.daytona_local prepare
      - name: Build pinned release locally and lock immutable images
        run: uv run python -m scripts.daytona_local images
      - name: Build the offline snapshot in the local registry
        run: uv run python -m scripts.daytona_local snapshot-image
      - name: Start local API, Runner, Dex, database, registry and storage
        run: uv run python -m scripts.daytona_local up
      - name: Authenticate through real local Dex and API
        run: uv run python -m scripts.daytona_bootstrap auth
      - name: Register the prebuilt snapshot without any hosted service
        run: uv run python -m scripts.daytona_bootstrap snapshot
      - name: Verify smart-news workflow, local tools, sandbox, cleanup and independent ZIP
        run: uv run python -m scripts.ci_daytona_local
      - name: Preserve bounded redacted diagnostics only
        if: always()
        run: |
          python - <<'PY'
          import json, pathlib, subprocess
          root = pathlib.Path('.data/daytona-local')
          secrets = []
          for name in ['credentials.json', 'api-key.json']:
              path = root / name
              if path.exists():
                  secrets += [v for v in json.loads(path.read_text()).values() if isinstance(v,str) and len(v)>5]
          outputs = []
          compose = root / 'compose.lock.yaml'
          if compose.exists():
              for args in [['ps','--all'],['logs','--no-color','--tail','80']]:
                  run = subprocess.run(['docker','--host','unix:///var/run/docker.sock','compose','-p','rnd-daytona-local','-f',str(compose),*args], capture_output=True, timeout=60)
                  text=(run.stdout+run.stderr).decode('utf-8',errors='replace')[-80000:]
                  for secret in sorted(secrets,key=len,reverse=True):
                      text=text.replace(secret,'[REDACTED]')
                  outputs.append(text)
          reports = pathlib.Path('reports'); reports.mkdir(exist_ok=True)
          (reports/'daytona-local-diagnostics.log').write_text('\n'.join(outputs),encoding='utf-8')
          if (root/'images.lock.json').exists():
              (reports/'daytona-images.lock.json').write_bytes((root/'images.lock.json').read_bytes())
          print('Diagnostics saved without local credentials or environment files.')
          PY
      - name: Stop this local test deployment without deleting persistent volumes
        if: always()
        run: |
          if test -f .data/daytona-local/compose.lock.yaml; then
            docker --host unix:///var/run/docker.sock compose -p rnd-daytona-local -f .data/daytona-local/compose.lock.yaml down
          fi
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: local-daytona-${{ github.run_id }}-${{ github.job }}
          path: |
            reports/daytona-local.json
            reports/daytona-local-diagnostics.log
            reports/daytona-images.lock.json
````
