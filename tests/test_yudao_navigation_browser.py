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
