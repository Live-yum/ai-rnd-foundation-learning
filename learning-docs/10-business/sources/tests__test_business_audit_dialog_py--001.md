# tests/test_business_audit_dialog.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_customer_audit_dialog_readable_and_permission_scoped`（L133–L205）：接收`tmp_path`。 控制顺序：L135按`not module or not Path(module).is_dir()`分支；L152遍历`[["manage.py", "init"], ["-c", SEED]]`；L162断言`result.returncode == 0`；L175遍历`range(100)`；L177按`httpx.get(url + "/health", trust_env=False).status_code == 200`分支；L201断言`result.returncode == 0`；L202断言`json.loads(result.stdout.splitlines()[-1])["passed"]`。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`Plan.model_validate_json`、`(Path(__file__).parents[1] / "examples/plans/customer-service.jso…`、`generate_basic`、`clean_env`、`os.environ.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_audit_dialog.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L205。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10321`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_audit_dialog.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fe51a801eb365ab4d847c849fcc0594f0402512904646b8835e73958c6ffea72"} -->
````python
# tests/test_business_audit_dialog.py
"""Customer-only Chromium evidence for readable, permission-scoped audit details."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env

SEED = r"""
import getpass
from fastapi.testclient import TestClient
import manage
getpass.getpass=lambda _: 'Example-Test-Password-123'
manage.bootstrap_admin('manager')
from app import app
with TestClient(app) as client:
 def call(method,path,token=None,**kwargs):
  result=client.request(method,path,headers={'Authorization':'Bearer '+token} if token else {},**kwargs)
  assert result.is_success,result.text
  return result.json()
 def login(name):return call('POST','/auth/login',json={'username':name,'password':'Example-Test-Password-123'})['access_token']
 manager=login('manager');users={}
 for name,role in [('service-demo','service'),('employee-demo','employee'),('outsider-demo','employee')]:
  users[name]=call('POST','/business/users',manager,json={'username':name,'password':'Example-Test-Password-123','role':role})
 service=login('service-demo');employee=login('employee-demo')
 customer=call('POST','/api/customers',manager,json={'name':'演示客户','organization':'演示单位','contact':'合成测试数据','category':'企业'})
 request=call('POST','/api/requests',employee,json={'title':'演示服务请求','detail':'合成测试：检查服务进度','customer_id':customer['id'],'priority':'普通','due_at':'2030-01-01T00:00:00Z'})
 identity=request['id']
 call('POST',f'/api/requests/{identity}/assign',manager,json={'user_id':users['service-demo']['id']})
 call('POST',f'/api/requests/{identity}/transition',service,json={'transition':'start'})
 call('POST',f'/api/requests/{identity}/notes',service,json={'body':'已联系演示客户，正在跟进处理'})
 call('POST','/api/tasks',manager,json={'title':'演示协作任务','detail':'合成测试：关联跟进','request_id':identity,'due_at':'2030-01-01T00:00:00Z'})
"""

DRIVER = r"""
const assert=require('node:assert/strict');
const path=require('node:path');
const [url,modulePath,output,beforeScript]=process.argv.slice(2);
(async()=>{
 const {chromium}=require(modulePath);
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 page.setDefaultTimeout(15000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 const uuid=/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
 async function login(name){
  if(await page.locator('#logout').isVisible()){
   await Promise.all([page.waitForEvent('load'),page.locator('#logout').click()]);
  }
  await page.locator('#auth input[name=username]').fill(name);
  await page.locator('#auth input[name=password]').fill('Example-Test-Password-123');
  await page.locator('#auth button[type=submit]').click();
  await page.locator('#workspace').waitFor({state:'visible'});
 }
 async function chooseRequests(){
  await page.locator('#entities button').filter({hasText:'服务请求'}).click();
  await page.waitForFunction(()=>document.getElementById('rows').dataset.entity==='requests'&&document.getElementById('rows').dataset.loading==='false');
 }
 async function open(){
  const response=page.waitForResponse(r=>/\/api\/requests\/[^/]+\/history$/.test(r.url()));
  await page.getByRole('button',{name:'详情 / 处理',exact:true}).click();
  const events=await(await response).json();
  await page.locator('#business-detail').waitFor({state:'visible'});
  return events;
 }
 try {
  if(beforeScript)await page.route('**/web/app.js',route=>route.fulfill({path:beforeScript,contentType:'text/javascript'}));
  await page.goto(url);await login('manager');await chooseRequests();
  if(beforeScript){
   await open();await page.screenshot({path:path.join(output,'manager--requests--before.png')});
   await page.unroute('**/web/app.js');await page.reload();
   await page.locator('#workspace').waitFor({state:'visible'});await chooseRequests();
  }
  const events=await open();
  const history=page.locator('#business-history');
  const text=await history.innerText();
  for(const label of ['已创建','已分配','开始处理','新增处理记录','employee-demo','manager','service-demo','UTC'])assert(text.includes(label),label);
  assert(!uuid.test(text));assert(!text.includes('transitioned:'));assert(!text.includes('created'));assert(!/T\d\d:\d\d/.test(text));
  const notes=await page.locator('#business-notes').innerText();
  assert(notes.includes('service-demo'));assert(notes.includes('UTC'));assert(!uuid.test(notes));
  assert.equal(await page.locator('#business-related h4').innerText(),'协作任务');
  assert((await page.locator('#business-related').innerText()).includes('演示协作任务 · 待处理'));
  const details=history.locator('details');
  assert.equal(await details.count(),events.length);assert.equal(await history.locator('details[open]').count(),0);
  for(let i=0;i<events.length;i++)assert(await details.nth(i).locator('pre').isHidden());
  await page.screenshot({path:path.join(output,'manager--requests--collapsed.png')});
  const first=details.first();await first.locator('summary').click();
  assert(await first.locator('pre').isVisible());
  assert.deepEqual(JSON.parse(await first.locator('pre').textContent()),events[0]);
  await page.screenshot({path:path.join(output,'manager--requests--expanded.png')});
  await first.locator('summary').click();assert(await first.locator('pre').isHidden());
  await first.locator('summary').focus();await page.keyboard.press('Enter');assert(await first.locator('pre').isVisible());
  await page.keyboard.press('Space');assert(await first.locator('pre').isHidden());
  await page.keyboard.press('Escape');await page.locator('#business-detail').waitFor({state:'hidden'});
  await open();assert.equal(await history.locator('details[open]').count(),0);
  await page.locator('#business-close').click();await page.locator('#business-detail').waitFor({state:'hidden'});
  await open();assert.equal(await history.locator('details[open]').count(),0);
  await page.setViewportSize({width:390,height:844});
  assert((await page.locator('#business-detail').boundingBox()).width<=390);
  await page.screenshot({path:path.join(output,'manager--requests--mobile.png')});
  await page.setViewportSize({width:1440,height:1100});
  await page.locator('#business-related button').click();
  await page.locator('#business-detail-title').getByText('演示协作任务',{exact:true}).waitFor();
  await page.locator('#business-close').click();
  for(const name of ['service-demo','employee-demo']){
   await login(name);await chooseRequests();const limited=await open();
   const full=name==='service-demo';
   assert(limited.every(item=>Object.hasOwn(item,'after')===full&&Object.hasOwn(item,'before')===full));
   assert.equal(await history.locator('details').count(),full?limited.length:0);
   assert.equal(await history.locator('pre').count(),full?limited.length:0);
   assert.equal(await history.locator('details[open]').count(),0);
   assert(!(await history.innerText()).match(uuid));
   await page.screenshot({path:path.join(output,`${name}--requests--history.png`)});
   await page.locator('#business-close').click();
  }
  await login('outsider-demo');await chooseRequests();assert.equal(await page.locator('#rows tr').count(),0);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,actual_browser:true,roles:3,audit_toggle:true,exact_snapshots:true,row_isolation:true}));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
"""


def test_customer_audit_dialog_readable_and_permission_scoped(tmp_path):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual browser tooling not configured; required in Actions")
    plan = Plan.model_validate_json(
        (Path(__file__).parents[1] / "examples/plans/customer-service.json").read_text(
            encoding="utf-8"
        )
    )
    product = tmp_path / "product"
    generate_basic(plan, product)
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
            "PLAYWRIGHT_BROWSERS_PATH": "0",
        }
    )
    for args in [["manage.py", "init"], ["-c", SEED]]:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=product,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        url = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                if httpx.get(url + "/health", trust_env=False).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        output = Path(os.getenv("PRODUCT_AUDIT_SCREENSHOT_DIR", str(tmp_path / "screenshots")))
        output.mkdir(parents=True, exist_ok=True)
        script = tmp_path / "audit-browser.cjs"
        script.write_text(DRIVER, encoding="utf-8")
        result = subprocess.run(
            [
                "node",
                str(script),
                url,
                module,
                str(output),
                os.getenv("PRODUCT_AUDIT_BEFORE_JS", ""),
            ],
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout.splitlines()[-1])["passed"]
    finally:
        process.terminate()
        process.wait(timeout=10)
````
