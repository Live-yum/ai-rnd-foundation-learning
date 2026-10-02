# tests/test_product_reload_readiness.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_real_product_reload_uses_authenticated_business_readiness`（L178–L272）：接收`tmp_path`、`plan`、`mode`。 控制顺序：L180按`not module or not Path(module).is_dir()`分支；L198断言`migrated.returncode == 0`；L223遍历`range(100)`；L224断言`process.poll() is None`；L226按`client.get(url + "health").status_code == 200`分支；L254断言`result.returncode == 0`；L257按`mode == "delayed-resource"`分支；L258断言`json.loads( (evidence / "old-load-timeout-state.json").read_text(encoding="utf-8") ) …`。 调用`os.environ.get`、`Path(module).is_dir`、`Path`、`pytest.skip`、`generate_basic`、`(product / "reload_fixture.py").write_text`、`SERVER.replace`、`repr`、`clean_env`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_product_reload_readiness.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L272。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12490`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_product_reload_readiness.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "769e5bcf4c05000bdfb0e440e771d971900c7ae089929a7dc95a718513a91366"} -->
````python
# tests/test_product_reload_readiness.py
"""Authenticated reload proves real API/data readiness without waiting for decorations."""

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env

# Only the test server introduces failure/delay cases; the generated frontend and
# the production readiness gate run unchanged against real HTTP/SQLite/Chromium.
SERVER = r"""
import asyncio
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from app import app, engine, metadata, delete
from pathlib import Path
MODE = __MODE__
visits = 0

@app.middleware("http")
async def reload_case(request, call_next):
    global visits
    if request.url.path == "/":
        visits += 1
        if visits >= 2:
            if MODE.startswith("expired-auth"):
                with engine.begin() as connection:
                    connection.execute(delete(metadata.tables["tokens"]))
            if MODE == "lost-records":
                with engine.begin() as connection:
                    connection.execute(delete(metadata.tables["task"]))
            if visits == 2 and MODE == "same-origin-redirect":
                return RedirectResponse("/redirected")
            if visits == 2 and MODE == "cross-origin-redirect":
                return RedirectResponse(str(request.url).replace("127.0.0.1", "localhost"))
            if MODE == "delayed-resource":
                html = Path("web/index.html").read_text(encoding="utf-8")
                return HTMLResponse(html.replace("</body>", '<img id="delayed-decoration" src="/test-delayed-resource"></body>'))
    if visits >= 2 and MODE == "forbidden-list" and request.url.path == "/api/task":
        return HTMLResponse("Forbidden", status_code=403)
    if visits >= 2 and MODE == "unrendered-records" and request.url.path == "/web/app.js":
        # A deliberately broken renderer must fail even with genuine API 200s.
        script = Path("web/app.js").read_text(encoding="utf-8")
        script = script.replace("if (sequence !== loadSequence) return;", "if (true) return;", 1)
        return Response(script, media_type="application/javascript")
    return await call_next(request)

@app.get("/test-delayed-resource")
async def delayed_resource():
    await asyncio.sleep(8)
    return HTMLResponse("complete")

@app.get("/redirected")
def redirected():
    return HTMLResponse(Path("web/index.html").read_text(encoding="utf-8"))
"""

DRIVER = r"""
const assert = require('node:assert/strict'), fs = require('node:fs');
const [url, modulePath, specFile, mode, directory] = process.argv.slice(1);
const {chromium} = require(modulePath);
const {reloadAuthenticatedWorkspace, captureReloadScreenshot} = require('./templates/product/verify-browser.cjs');
const spec = JSON.parse(fs.readFileSync(specFile,'utf8'));
(async()=>{
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage(); page.setDefaultTimeout(5000);
    await page.goto(url);
    await page.locator('#auth [name=username]').fill('reload-proof');
    await page.locator('#auth [name=password]').fill('Real-password-for-reload-314');
    await page.locator('#register').click();
    await page.locator('#workspace').waitFor({state:'visible'});
    await page.locator('#create').click();
    await page.locator('#record [name=title]').fill('Real authenticated record');
    await page.locator('#record [name=priority]').fill('2');
    await page.locator('#record [name=done]').selectOption('false');
    const created = page.waitForResponse(r=>new URL(r.url()).pathname==='/api/task' && r.request().method()==='POST');
    await page.locator('#record button[type=submit]').click();
    const response = await created; assert.equal(response.status(),201);
    const records = [await response.json()];
    await page.waitForFunction(()=>document.querySelector('#rows').dataset.loading==='false' && document.querySelectorAll('#rows tr').length===1);
    if (mode==='delayed-resource') {
      // Preserve the old wait's real failure and page state before exercising
      // the production replacement. No resources are aborted/removed/mocked.
      await assert.rejects(page.reload({timeout:500}), /Timeout/);
      await page.waitForFunction(()=>document.querySelector('#rows').dataset.loading==='false');
      const state = await page.evaluate(()=>({readyState:document.readyState,
        workspaceVisible:document.querySelector('#workspace').checkVisibility(),
        rows:document.querySelectorAll('#rows tr').length,
        delayedResourceComplete:document.querySelector('#delayed-decoration').complete}));
      assert.equal(state.readyState,'interactive'); assert(state.workspaceVisible);
      assert.equal(state.rows,1); assert.equal(state.delayedResourceComplete,false);
      fs.writeFileSync(directory+'/old-load-timeout-state.json',JSON.stringify(state,null,2));
      await captureReloadScreenshot(page,directory+'/old-load-timeout.png');
    }
    const args = {url,spec,records,timeout:3000,
      diagnosticsDirectory:mode==='expired-auth-default-evidence' ? undefined : directory};
    if (mode==='normal' || mode==='delayed-resource') {
      const result = await reloadAuthenticatedWorkspace(page,args);
      assert.equal(result.authenticated,true); assert.equal(result.business_dom,true);
      assert.equal(result.exact_record_count,1); assert.equal(result.list_status,200);
      if(mode==='delayed-resource') {
        assert.equal(await page.locator('#delayed-decoration').count(),1);
        assert.equal(await page.locator('#delayed-decoration').evaluate(el=>el.complete),false);
        assert.equal(await page.evaluate(()=>document.readyState),'interactive');
      }
      fs.writeFileSync(directory+'/success.json',JSON.stringify(result,null,2));
    } else {
      const expected = {
        'expired-auth': /Reload authenticated schema denied/,
        'expired-auth-default-evidence': /Reload authenticated schema denied/,
        'lost-records': /Reload lost or exposed different authenticated records/,
        'unrendered-records': /Timeout/,
        'forbidden-list': /Reload business list denied/,
        'same-origin-redirect': /Reload left the product page/,
        'cross-origin-redirect': /Reload left the product origin/
      }[mode];
      let failure;
      await assert.rejects(reloadAuthenticatedWorkspace(page,args), error=>{failure=error;return expected.test(error.message)});
      const artifacts = require('node:path').dirname(failure.reloadEvidence.artifact_prefix);
      if(mode==='expired-auth-default-evidence') {
        assert.notEqual(artifacts,directory);
        assert(require('node:path').basename(artifacts).startsWith('product-browser-failure-'));
        fs.writeFileSync(directory+'/default-artifact-reference.json',JSON.stringify({directory:artifacts}));
      }
      const files = fs.readdirSync(artifacts);
      const snapshot = files.find(file=>file.startsWith('reload-') && file.endsWith('.json'));
      assert(snapshot,'Failure must preserve diagnostics');
      const evidence = JSON.parse(fs.readFileSync(artifacts+'/'+snapshot,'utf8'));
      assert(evidence.state); assert(evidence.responses.length>0);
      if(mode==='unrendered-records') {
        assert(evidence.responses.some(r=>r.route.path==='/schema' && r.status===200));
        assert(evidence.responses.some(r=>r.route.path==='/api/task' && r.status===200));
        assert.equal(evidence.state.loading,true);assert.equal(evidence.state.rowCount,0);
      }
      assert(!files.some(file=>file.endsWith('.html')), 'Raw HTML must never be retained');
      if(mode.endsWith('redirect')) {
        assert.equal(evidence.screenshot_skipped,'not-product-page');
        assert(!files.some(file=>file.endsWith('.png')));
      } else assert(files.some(file=>file.endsWith('.png')));
      const receipt=fs.readFileSync(artifacts+'/'+snapshot,'utf8');
      assert(receipt.length<32000, 'Diagnostic metadata must remain bounded');
      for(const secret of ['Real-password-for-reload-314','reload-proof','Real authenticated record','Bearer ',
        await page.evaluate(()=>sessionStorage.getItem('product-token'))]) {
        if(secret)assert(!receipt.includes(secret),'Diagnostics must not expose credentials or record values');
      }
      assert(!fs.existsSync(directory+'/success.json'));
    }
    console.log('Real product reload proof: '+mode);
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
"""


@pytest.mark.parametrize(
    "mode",
    [
        "normal",
        "delayed-resource",
        "expired-auth",
        "expired-auth-default-evidence",
        "lost-records",
        "unrendered-records",
        "forbidden-list",
        "same-origin-redirect",
        "cross-origin-redirect",
    ],
)
def test_real_product_reload_uses_authenticated_business_readiness(tmp_path, plan, mode):
    module = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium required")
    product = tmp_path / "product"
    generate_basic(plan, product, {"template": "python-basic", "frontend": "simple-admin"})
    (product / "reload_fixture.py").write_text(
        SERVER.replace("__MODE__", repr(mode)), encoding="utf-8"
    )
    env = clean_env({"PRODUCT_DATA_DIR": str(tmp_path / "database")})
    migrated = subprocess.run(
        [sys.executable, "manage.py", "init"],
        cwd=product,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert migrated.returncode == 0, migrated.stdout + migrated.stderr
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server_log = tmp_path / "server.log"
    with server_log.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "reload_fixture:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=product,
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            url = f"http://127.0.0.1:{port}/"
            with httpx.Client(trust_env=False, timeout=0.5) as client:
                for _ in range(100):
                    assert process.poll() is None, server_log.read_text(encoding="utf-8")
                    try:
                        if client.get(url + "health").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.05)
                else:
                    pytest.fail("Real generated product server did not become healthy")
            evidence = tmp_path / "evidence"
            evidence.mkdir()
            result = subprocess.run(
                [
                    shutil.which("node"),
                    "-e",
                    DRIVER,
                    url,
                    module,
                    str(product / "approved-spec.json"),
                    mode,
                    str(evidence),
                ],
                cwd=ROOT,
                env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=False,
            )
            assert result.returncode == 0, (
                result.stdout + result.stderr + server_log.read_text(encoding="utf-8")
            )
            if mode == "delayed-resource":
                assert json.loads(
                    (evidence / "old-load-timeout-state.json").read_text(encoding="utf-8")
                ) == {
                    "readyState": "interactive",
                    "workspaceVisible": True,
                    "rows": 1,
                    "delayedResourceComplete": False,
                }
        finally:
            process.terminate()
            try:
                process.wait(timeout=12)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
````
