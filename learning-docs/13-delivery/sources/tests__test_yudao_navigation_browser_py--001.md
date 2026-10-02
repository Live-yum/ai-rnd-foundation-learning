# tests/test_yudao_navigation_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_sidebar_driver_requires_visible_generated_pages_and_rejects_unavailable_modules`（L112–L118）：接收`role`、`fault`。 控制顺序：L116按`not module or not Path(module).is_dir()`分支。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`_run_driver`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sidebar_driver_rejects_ungranted_installed_module_for_ordinary_role`（L121–L125）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L123按`not module or not Path(module).is_dir()`分支。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`_run_driver`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_process_identity`（L128–L134）：接收`pid`。 源码说明：Read only process identity/ancestry, never command lines or environment.。 调用`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") "…`、`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit`、`Path(f"/proc/{pid}/stat").read_text`、`Path`、`int`。 返回路径：L132的`int(fields[1]), fields[19]`；L134的`None`。
- `_stop_owned_tree`（L137–L174）：接收`process`。 源码说明：Kill only descendants of this still-owned fixture, including detached Chromium.。 控制顺序：L139按`process.poll() is not None`分支；L141按`os.name == "nt"`分支；L151按`own_identity is None`分支；L152抛异常，停止当前正常路径；L154遍历`Path("/proc").iterdir()`；L155按`path.name.isdecimal() and (identity := _process_identity(int(path.name)))`分支；L158在`added := { pid: identity for pid, identity in snapshot.items() if…`成立时循环；L166遍历`reversed(list(owned.items()))`。后续分支沿下方源码相同行号继续阅读。 调用`process.poll`、`subprocess.run`、`str`、`process.wait`、`_process_identity`、`RuntimeError`、`Path("/proc").iterdir`、`Path`、`path.name.isdecimal`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_read_diagnostic`（L177–L193）：接收`output`、`limit`。 源码说明：Retain startup and final phase evidence without unbounded output reads.。 控制顺序：L181按`size <= limit`分支。 调用`output.seek`、`output.read(limit).decode`、`output.read`、`len`、`prefix.decode`、`marker.decode`、`output.read(last).decode`。 返回路径：L182的`output.read(limit).decode("utf-8", errors="replace")`；L189的`prefix.decode("utf-8", errors="ignore") + marker.decode() + output.read(last).decode("utf-…`。
- `_run_driver`（L196–L224）：接收`fault`、`role`、`module`。 控制顺序：L220断言`not timed_out`；L223断言`cleanup_error is None`；L224断言`process.returncode == 0`。 调用`tempfile.TemporaryFile`、`subprocess.Popen`、`shutil.which`、`clean_env`、`process_options`、`process.wait`、`_stop_owned_tree`、`type`、`_read_diagnostic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_cleanup_kills_descendants_but_rejects_foreign_and_recycled_pids`（L227–L262）：接收`monkeypatch`。 控制顺序：L261断言`killed == [(102, signal.SIGKILL), (101, signal.SIGKILL), (100, signal.SIGKILL)]`；L262断言`waited == [{"timeout": 3}]`。 调用`monkeypatch.setitem`、`globals`、`SimpleNamespace`、`str`、`killed.append`、`waited.append`、`_stop_owned_tree`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_cleanup_kills_descendants_but_rejects_foreign_and_recycled_pids.identity`（L240–L246）：接收`pid`。 控制顺序：L242按`pid == 102 and reads[pid] > 1`分支；L244按`pid == 103 and reads[pid] > 1`分支。 调用`reads.get`。 返回路径：L243的`(1, "renderer-start")`；L245的`(100, "recycled-start")`；L246的`identities[pid]`。
- `test_owned_cleanup_refuses_missing_root_identity`（L265–L273）：接收`monkeypatch`。 调用`monkeypatch.setitem`、`globals`、`SimpleNamespace`、`pytest.fail`、`pytest.raises`、`_stop_owned_tree`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_cleanup_does_nothing_after_fixture_exit`（L276–L280）：接收`monkeypatch`。 调用`monkeypatch.setitem`、`globals`、`pytest.fail`、`_stop_owned_tree`、`SimpleNamespace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_cleanup_windows_targets_only_fixture_and_reaps_direct_child`（L283–L295）：接收`monkeypatch`。 控制顺序：L289断言`called == [ ( ["taskkill", "/PID", "100", "/T", "/F"], {"capture_output": True, "time…`；L295断言`waited == [{"timeout": 3}]`。 调用`monkeypatch.setitem`、`globals`、`SimpleNamespace`、`monkeypatch.setattr`、`called.append`、`waited.append`、`_stop_owned_tree`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_retains_phase_receipt_and_original_cap_when_owned_cleanup_fails`（L298–L320）：接收`monkeypatch`。 控制顺序：L317断言`"exceeded unchanged 25 s cap" in message`；L318断言`'{"phase":"browser-start","event":"start"}' in message`；L319断言`"Owned fixture cleanup failed: RuntimeError: fixture cleanup canary" in message`；L320断言`waited == [{"timeout": 25}]`。 调用`monkeypatch.setattr`、`monkeypatch.setitem`、`globals`、`pytest.raises`、`_run_driver`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_retains_phase_receipt_and_original_cap_when_owned_cleanup_fails.timed_out`（L301–L303）：接收`**kwargs`。 控制顺序：L303抛异常，停止当前正常路径。 调用`waited.append`、`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_retains_phase_receipt_and_original_cap_when_owned_cleanup_fails.launch`（L305–L307）：接收`command`、`**kwargs`。 调用`kwargs["stdout"].write`、`SimpleNamespace`。 返回路径：L307的`SimpleNamespace(pid=100, wait=timed_out, returncode=None)`。
- `test_timeout_retains_phase_receipt_and_original_cap_when_owned_cleanup_fails.cleanup`（L309–L310）：接收`_`。 控制顺序：L310抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_output_is_bounded_and_retains_first_and_last_phase`（L323–L331）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L326断言`len(result.encode("utf-8")) <= 512`；L327断言`result.startswith('{"phase":"browser-start"}')`；L328断言`result.endswith('{"phase":"browser-cleanup"}\n')`；L329断言`"diagnostic bytes omitted" in result`；L331断言`_read_diagnostic(io.BytesIO(small)) == small.decode("utf-8")`。 调用`_read_diagnostic`、`io.BytesIO`、`len`、`result.encode`、`result.startswith`、`result.endswith`、`small.decode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_yudao_navigation_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L331。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14985`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_yudao_navigation_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fdd3dd86200df73bf64244d0b9f8449107df09de7c84671e038e073a37128509"} -->
````python
# tests/test_yudao_navigation_browser.py
"""Actual Chromium tests of sidebar inspection against a local DOM/HTTP fixture.

These verify the driver and its negatives, not the compiled native-stack result.
"""

import io
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from workbench.settings import ROOT
from workbench.tools import clean_env, process_options

DRIVER = r"""
const assert=require('node:assert/strict');
const http=require('node:http');
const { verifyInstalledSidebar }=require('./scripts/business_yudao_browser.cjs');
const [fault,role,playwrightPath]=process.argv.slice(1);
const {chromium}=require(playwrightPath);
const started=Date.now(), workDeadline=started+20000; // Reserve cleanup inside the unchanged 25 s outer cap.
const remaining=()=>Math.max(1,workDeadline-Date.now());
const mark=(phase,event,extra={})=>console.log(JSON.stringify({phase,event,elapsed_ms:Date.now()-started,...extra}));
async function stage(name,operation,budget=remaining()){
 mark(name,'start');let timer;
 try{
  const value=await Promise.race([Promise.resolve().then(operation),new Promise((_,reject)=>{
   timer=setTimeout(()=>reject(new Error('Fixture stage timed out: '+name)),budget);
  })]);mark(name,'done');return value;
 }catch(error){mark(name,'error',{name:error.name,message:error.message});throw error;}
 finally{clearTimeout(timer);}
}
const entities=['customers','requests','tasks'];
const roots=role==='manager'?['/system','/infra','/workbench']:['/workbench'];
const targets=entities.map(entity=>({entity,route:'/workbench/wb-'+entity}));
const plan={business:{permissions:entities.map(entity=>({entity,role,actions:['read']}))}};
const identity={menus:roots.map(path=>({path,name:path.slice(1),children:path==='/workbench'?entities.map(entity=>({component:'infra/wb'+entity+'/index'})):[]}))};
if(fault==='auth-unavailable')identity.menus.push({path:'/crm',name:'CRM',children:[]});
if(fault==='wrong-generated-component')identity.menus.find(menu=>menu.path==='/workbench').children[0].component='crm/customer/index';
const server=http.createServer((req,res)=>{
 res.writeHead(200,{'Content-Type':'text/html;charset=utf-8'});
 const other=roots.filter(path=>path!='/workbench').map(path=>`<li><div class="vben-sub-menu-content__title">${path.slice(1)}</div></li>`).join('');
 const generated=targets.filter(target=>fault!=='missing-positive'||target.entity!=='tasks').map(target=>`<a role="menuitem" href="#${target.route}">${target.entity}</a>`).join('');
 const extra=fault==='hidden-extra-route'?'<a role="menuitem" href="#/crm/customer" style="display:none">CRM</a>':'';
 const empty=fault==='empty-extra-root'?'<li><div class="vben-sub-menu-content__title">Unsupported empty module</div></li>':'';
 const ungranted=fault==='ungranted-sidebar'?'<a role="menuitem" href="#/system/user">Users</a>':'';
 res.end(`<aside><ul class="${fault==='missing-native-dom'?'foreign-menu':'vben-menu'}">
 <li><div class="vben-sub-menu-content__title">Dashboard</div><ul><a role="menuitem" href="#/dashboard/analytics">Analytics</a></ul></li>
 ${other}<li><div class="vben-sub-menu-content__title" id="expand">workbench</div><ul id="children" style="display:none">${generated}</ul></li>${extra}${empty}${ungranted}</ul></aside>
 <script>document.querySelector('#expand').onclick=()=>document.querySelector('#children').style.display='block';</script>`);
});
(async()=>{
 let browser;
 try{
  await stage('server-start',()=>new Promise(resolve=>server.listen(0,'127.0.0.1',resolve)));
  browser=await stage('browser-start',()=>chromium.launch({headless:true,timeout:remaining()}));
  const page=await stage('page-start',()=>browser.newPage());page.setDefaultTimeout(1200);
  await stage('page-navigation',()=>page.goto('http://127.0.0.1:'+server.address().port));
  await stage('assertions',async()=>{
   let result,error;try{result=await verifyInstalledSidebar(page,identity,role,plan,targets);}catch(e){error=e;}
   if(fault==='none'){
    assert.ifError(error);assert.deepEqual(result.rendered_entities,entities);assert.equal(result.unavailable_count,0);assert(result.native_sidebar_inspected);
    assert(await page.locator('#children').isVisible());
   }else{
    assert(error,'Must reject '+fault);
    const expected={
     'auth-unavailable':['AssertionError','Native auth response exposed unavailable/ungranted modules'],
     'wrong-generated-component':['AssertionError','Generated sidebar menu differs from approved read ACL'],
     'missing-positive':['TimeoutError','locator.waitFor: Timeout 1200ms exceeded.'],
     'hidden-extra-route':['AssertionError','Rendered sidebar exposed an unavailable module'],
     'empty-extra-root':['AssertionError','Rendered top-level sidebar contains an unrecognized module'],
     'missing-native-dom':['AssertionError','Actual Vben menu DOM was not inspected'],
     'ungranted-sidebar':['AssertionError','Rendered sidebar exposed an unavailable module'],
    }[fault];
    assert(expected,'Unexpected fixture fault');assert.equal(error.name,expected[0]);
    assert.equal(error.message.split('\n')[0],expected[1]);
    if(fault==='missing-positive')assert(error.message.includes('/workbench/wb-tasks'),error.message);
    mark('negative-rejected','done',{fault,name:error.name,message:error.message.split('\n')[0]});
   }
  });
  console.log('Local actual Chromium navigation-driver fixture PASS '+role+'/'+fault);
 }finally{
  try{if(browser)await stage('browser-cleanup',()=>browser.close(),3000);}
  finally{
   await stage('server-cleanup',()=>new Promise(resolve=>{
    server.close(resolve);server.closeAllConnections();
   }),1000);
  }
 }
})().catch(error=>{console.error(error);process.exitCode=1;});
"""


@pytest.mark.parametrize("role", ["manager", "employee"])
@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "auth-unavailable",
        "wrong-generated-component",
        "missing-positive",
        "hidden-extra-route",
        "empty-extra-root",
        "missing-native-dom",
    ],
)
def test_sidebar_driver_requires_visible_generated_pages_and_rejects_unavailable_modules(
    role, fault
):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium is required in Actions")
    _run_driver(fault, role, module)


def test_sidebar_driver_rejects_ungranted_installed_module_for_ordinary_role():
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium is required in Actions")
    _run_driver("ungranted-sidebar", "employee", module)


def _process_identity(pid):
    """Read only process identity/ancestry, never command lines or environment."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
        return int(fields[1]), fields[19]  # Parent PID and immutable Linux start tick.
    except OSError, ValueError, IndexError:
        return None


def _stop_owned_tree(process):
    """Kill only descendants of this still-owned fixture, including detached Chromium."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=3,
            check=False,
        )
        process.wait(timeout=3)
        return
    own_identity = _process_identity(process.pid)
    if own_identity is None:
        raise RuntimeError("Owned fixture identity is unavailable; refusing blind cleanup")
    snapshot = {}
    for path in Path("/proc").iterdir():
        if path.name.isdecimal() and (identity := _process_identity(int(path.name))):
            snapshot[int(path.name)] = identity
    owned = {process.pid: own_identity}
    while added := {
        pid: identity
        for pid, identity in snapshot.items()
        if identity[0] in owned and pid not in owned
    }:
        owned.update(added)
    # Chromium deliberately creates a new session. Killing only Node's group leaks it.
    # Start ticks prevent a recycled PID from being mistaken for an owned descendant.
    for pid, identity in reversed(list(owned.items())):
        current = _process_identity(pid)
        if identity is not None and current is not None and current[1] == identity[1]:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    # Reap only the direct child; its output is a file, so descendants cannot hold a pipe open.
    process.wait(timeout=3)


def _read_diagnostic(output, limit=16000):
    """Retain startup and final phase evidence without unbounded output reads."""
    size = output.seek(0, os.SEEK_END)
    output.seek(0)
    if size <= limit:
        return output.read(limit).decode("utf-8", errors="replace")
    marker = b"\n[... diagnostic bytes omitted ...]\n"
    first = (limit - len(marker)) // 2
    last = limit - first - len(marker)
    prefix = output.read(first)
    output.seek(-last, os.SEEK_END)
    # ASCII JSON phases are exact; ignore only incomplete UTF-8 at truncation boundaries.
    return (
        prefix.decode("utf-8", errors="ignore")
        + marker.decode()
        + output.read(last).decode("utf-8", errors="ignore")
    )


def _run_driver(fault, role, module):
    with tempfile.TemporaryFile(mode="w+b") as output:
        process = subprocess.Popen(
            [shutil.which("node"), "-e", DRIVER, fault, role, module],
            cwd=ROOT,
            env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
            stdout=output,
            stderr=subprocess.STDOUT,
            **process_options(),
        )
        timed_out = False
        cleanup_error = None
        try:
            process.wait(timeout=25)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            try:
                _stop_owned_tree(process)
            except Exception as error:
                cleanup_error = f"{type(error).__name__}: {error}"[:2000]
        suffix = f"\nOwned fixture cleanup failed: {cleanup_error}\n" if cleanup_error else ""
        diagnostic = _read_diagnostic(output, 16000 - len(suffix.encode("utf-8"))) + suffix
    print(diagnostic, end="")
    assert not timed_out, (
        f"Navigation fixture exceeded unchanged 25 s cap: {role}/{fault}\n{diagnostic}"
    )
    assert cleanup_error is None, diagnostic
    assert process.returncode == 0, diagnostic


def test_owned_cleanup_kills_descendants_but_rejects_foreign_and_recycled_pids(monkeypatch):
    identities = {
        100: (1, "fixture-start"),
        101: (100, "browser-start"),
        102: (101, "renderer-start"),
        103: (100, "original-start"),
        200: (1, "foreign-start"),
        201: (200, "foreign-renderer"),
    }
    reads, killed, waited = {}, [], []
    # Simulate POSIX signals without depending on Windows exposing SIGKILL.
    monkeypatch.setitem(globals(), "signal", SimpleNamespace(SIGKILL=9))

    def identity(pid):
        reads[pid] = reads.get(pid, 0) + 1
        if pid == 102 and reads[pid] > 1:
            return (1, "renderer-start")  # Still our descendant after teardown reparenting.
        if pid == 103 and reads[pid] > 1:
            return (100, "recycled-start")
        return identities[pid]

    monkeypatch.setitem(globals(), "_process_identity", identity)
    monkeypatch.setitem(
        globals(),
        "Path",
        lambda _: SimpleNamespace(
            iterdir=lambda: [SimpleNamespace(name=str(pid)) for pid in identities]
        ),
    )
    monkeypatch.setitem(
        globals(), "os", SimpleNamespace(name="posix", kill=lambda *args: killed.append(args))
    )
    process = SimpleNamespace(pid=100, poll=lambda: None, wait=lambda **kw: waited.append(kw))
    _stop_owned_tree(process)
    assert killed == [(102, signal.SIGKILL), (101, signal.SIGKILL), (100, signal.SIGKILL)]
    assert waited == [{"timeout": 3}]


def test_owned_cleanup_refuses_missing_root_identity(monkeypatch):
    monkeypatch.setitem(globals(), "_process_identity", lambda _: None)
    monkeypatch.setitem(
        globals(),
        "os",
        SimpleNamespace(name="posix", kill=lambda *args: pytest.fail("No proven owner")),
    )
    with pytest.raises(RuntimeError, match="identity is unavailable"):
        _stop_owned_tree(SimpleNamespace(pid=100, poll=lambda: None))


def test_owned_cleanup_does_nothing_after_fixture_exit(monkeypatch):
    monkeypatch.setitem(
        globals(), "_process_identity", lambda _: pytest.fail("Do not inspect a released PID")
    )
    _stop_owned_tree(SimpleNamespace(pid=100, poll=lambda: 0))


def test_owned_cleanup_windows_targets_only_fixture_and_reaps_direct_child(monkeypatch):
    called, waited = [], []
    monkeypatch.setitem(globals(), "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(subprocess, "run", lambda command, **kw: called.append((command, kw)))
    process = SimpleNamespace(pid=100, poll=lambda: None, wait=lambda **kw: waited.append(kw))
    _stop_owned_tree(process)
    assert called == [
        (
            ["taskkill", "/PID", "100", "/T", "/F"],
            {"capture_output": True, "timeout": 3, "check": False},
        )
    ]
    assert waited == [{"timeout": 3}]


def test_timeout_retains_phase_receipt_and_original_cap_when_owned_cleanup_fails(monkeypatch):
    waited = []

    def timed_out(**kwargs):
        waited.append(kwargs)
        raise subprocess.TimeoutExpired("fixture-node", kwargs["timeout"])

    def launch(command, **kwargs):
        kwargs["stdout"].write(b'{"phase":"browser-start","event":"start"}\n')
        return SimpleNamespace(pid=100, wait=timed_out, returncode=None)

    def cleanup(_):
        raise RuntimeError("fixture cleanup canary")

    monkeypatch.setattr(subprocess, "Popen", launch)
    monkeypatch.setitem(globals(), "_stop_owned_tree", cleanup)
    with pytest.raises(AssertionError) as failure:
        _run_driver("wrong-generated-component", "manager", "/fixture/playwright")
    message = str(failure.value)
    assert "exceeded unchanged 25 s cap" in message
    assert '{"phase":"browser-start","event":"start"}' in message
    assert "Owned fixture cleanup failed: RuntimeError: fixture cleanup canary" in message
    assert waited == [{"timeout": 25}]


def test_diagnostic_output_is_bounded_and_retains_first_and_last_phase():
    data = b'{"phase":"browser-start"}\n' + b"x" * 40000 + b'{"phase":"browser-cleanup"}\n'
    result = _read_diagnostic(io.BytesIO(data), limit=512)
    assert len(result.encode("utf-8")) <= 512
    assert result.startswith('{"phase":"browser-start"}')
    assert result.endswith('{"phase":"browser-cleanup"}\n')
    assert "diagnostic bytes omitted" in result
    small = b'{"phase":"assertions","event":"done"}\n'
    assert _read_diagnostic(io.BytesIO(small)) == small.decode("utf-8")
````
