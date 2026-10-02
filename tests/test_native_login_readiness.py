"""Real HTTP/Chromium regressions for the native login driver, not stack acceptance."""

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
const assert = require('node:assert/strict');
const http = require('node:http');
const { loginNativeSession } = require('./scripts/business_yudao_browser.cjs');
const { submitNativeLogin } = require('./scripts/native_browser.cjs');
const [fault, playwrightPath, oldTimeout = '1800', driver = 'business'] = process.argv.slice(1);
const { chromium } = require(playwrightPath);
const actor = { username: 'fixture-manager', password: 'fixture-only-password' };
const started = Date.now(), workDeadline = started + 25000; // Leave cleanup inside the unchanged 30 s outer cap.
const remaining = () => Math.max(1, workDeadline - Date.now());
const mark = (phase, event, extra = {}) => console.log(JSON.stringify({
  phase, event, timestamp: new Date().toISOString(), elapsed_ms: Date.now() - started, ...extra,
}));
async function stage(name, operation, budget = remaining()) {
  mark(name, 'start'); let timer;
  try {
    const result = await Promise.race([Promise.resolve().then(operation), new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error('Fixture stage timed out: ' + name)), budget);
    })]);
    mark(name, 'done'); return result;
  } catch (error) {
    mark(name, 'error', { name: error.name, message: error.message }); throw error;
  } finally { clearTimeout(timer); }
}
const requests = [], heldImages = []; let closing = false;
const imageState = response => ({ ended: response.writableEnded, finished: response.writableFinished,
  destroyed: response.destroyed });
function releaseHeldImages(reason) {
  mark('held-images', 'release', { reason, count: heldImages.length });
  for (const [index, response] of heldImages.entries()) {
    mark('held-image', 'release', { index, ...imageState(response) });
    if (!response.writableEnded && !response.destroyed) response.end();
  }
}
mark('fixture', 'start', { driver, fault, tmpdir: require('node:os').tmpdir() });
const shell = '<aside id="app-sidebar">Native menu</aside><header id="app-header">Native header</header><main id="app-content"><div id="__vben_main_content">Dashboard</div></main>';
const foreign = http.createServer((req, res) => res.end(shell));
const server = http.createServer(async (req, res) => {
  const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
  if (pathname === '/delayed-dashboard-image') {
    const index = heldImages.push(res) - 1;
    mark('held-image', 'received', { index });
    res.once('finish', () => mark('held-image', 'finish', { index, ...imageState(res) }));
    res.once('close', () => mark('held-image', 'close', { index, ...imageState(res) }));
    if (closing) res.end();
    return; // Complete the real HTTP response only after the assertions.
  }
  if (pathname.startsWith('/admin-api/')) {
    requests.push(pathname);
    res.setHeader('Content-Type', 'application/json');
    if (pathname.endsWith('/tenant/simple-list')) {
      res.end(JSON.stringify({ code: 0, data: [{ id: 1, name: 'Fixture tenant' }] })); return;
    }
    if (pathname.endsWith('/auth/login')) {
      assert.equal(req.method, 'POST');
      let raw = ''; for await (const part of req) raw += part;
      assert.deepEqual(JSON.parse(raw), { ...actor, tenantId: 1 });
      res.end(JSON.stringify({ code: fault === 'login-failure' ? 401 : 0, data: {} })); return;
    }
    if (pathname.endsWith('/auth/get-permission-info') || pathname.endsWith('/user/current/info')) {
      if (fault === 'permissions-http-failure') res.statusCode = 403;
      res.end(JSON.stringify({ code: fault === 'permissions-failure' ? 403 : 0,
        data: { menus: fault === 'missing-menu' ? [] : [{ path: '/dashboard/analytics' }] } })); return;
    }
    throw new Error('Unexpected API request: ' + pathname);
  }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><meta charset="utf-8">
    <img src="/delayed-dashboard-image" alt="Delayed dashboard resource">
    <section id="login"><button role="combobox" onclick="document.querySelector('#tenant').hidden=false">Tenant</button>
      <button id="tenant" role="option" hidden>Fixture tenant</button>
      <input placeholder="用户名"><input type="password"><button id="submit">登 录</button></section>
    <script>
      window.loaded = false; addEventListener('load', () => window.loaded = true);
      let tenantId;
      document.querySelector('#tenant').onclick = () => { tenantId = 1; document.querySelector('#tenant').hidden = true; };
      fetch('/admin-api/system/tenant/simple-list');
      document.querySelector('#submit').onclick = async () => {
        await (await fetch('/admin-api/system/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: document.querySelector('input').value,
            password: document.querySelector('input[type=password]').value, tenantId }) })).json();
        const inspected = new Promise(resolve => addEventListener('permissions-inspected', resolve, { once: true }));
        await (await fetch(${JSON.stringify(driver === 'generic-fastapi' ? '/admin-api/system/user/current/info' : '/admin-api/system/auth/get-permission-info')})).json();
        // Even a plausible shell must never override rejected login/permissions responses.
        document.querySelector('#login').remove();
        document.body.insertAdjacentHTML('beforeend', ${JSON.stringify(shell)});
        const fault = ${JSON.stringify(fault)};
        if (fault === 'missing-aside') document.querySelector('aside').remove();
        if (fault === 'missing-main') document.querySelector('main').remove();
        if (fault === 'auth-route') location.hash = '/auth/session-expired';
        else if (fault === 'foreign-origin') {
          // Preserve the response body until the driver has inspected it, isolating route validation.
          await inspected; location.href = 'http://127.0.0.1:${foreign.address().port}/#/dashboard/analytics';
        }
        else location.hash = '/dashboard/analytics';
      };
    </script>`);
});
(async () => {
  let browser;
  try {
    await stage('foreign-server-start', () => new Promise((resolve, reject) => {
      foreign.once('error', reject); foreign.listen(0, '127.0.0.1', resolve);
    }));
    await stage('server-start', () => new Promise((resolve, reject) => {
      server.once('error', reject); server.listen(0, '127.0.0.1', resolve);
    }));
    browser = await stage('browser-start', () => chromium.launch({ headless: true, timeout: remaining() }));
    const page = await stage('page-start', () => browser.newPage()); page.setDefaultTimeout(1800);
    page.setDefaultNavigationTimeout(Number(oldTimeout));
    page.on('load', () => mark('page-load', 'delivered'));
    for (const event of ['requestfinished', 'requestfailed']) page.on(event, request => {
      if (new URL(request.url()).pathname === '/delayed-dashboard-image') {
        mark('held-image', event, event === 'requestfailed' ? { error_class: 'RequestFailed' } : {});
      }
    });
    const base = 'http://127.0.0.1:' + server.address().port;
    const checkedPaths = []; let oldReadiness;
    const observe = (part, method = 'GET') => {
      if (fault === 'none' && part.endsWith('/auth/login')) {
        // Begin the original exact wait before the same-document route changes.
        oldReadiness = page.waitForURL(url => !url.hash.includes('login'))
          .then(() => ({}), error => ({ error }));
      }
      return page.waitForResponse(response =>
        new URL(response.url()).pathname.endsWith(part) && response.request().method() === method)
        .then(response => ({ response }), error => ({ error }));
    };
    const checked = async promise => {
      const found = await promise; if (found.error) throw found.error;
      checkedPaths.push(new URL(found.response.url()).pathname);
      assert(found.response.ok(), 'Business browser HTTP ' + found.response.status());
      const body = await found.response.json();
      assert.equal(body.code, 0, 'Business application error ' + body.code);
      if (fault === 'foreign-origin' && /\/(auth\/get-permission-info|user\/current\/info)$/.test(found.response.url())) {
        await page.evaluate(() => dispatchEvent(new Event('permissions-inspected')));
      }
      return body.data;
    };
    let failure, businessReady = false;
    try {
      await stage('login-driver', async () => {
        if (driver === 'business') await loginNativeSession(page, base, actor, observe, checked);
        else {
          const tenants = observe('/system/tenant/simple-list');
          await page.goto(base + '/#/auth/login', { waitUntil: 'domcontentloaded' });
          const available = await checked(tenants);
          const tenant = available.find(item => item.id === 1); assert(tenant);
          await page.getByRole('combobox').first().click();
          await page.getByRole('option', { name: tenant.name, exact: true }).click();
          await page.getByPlaceholder('用户名').fill(actor.username);
          await page.locator('input[type=password]').fill(actor.password);
          await submitNativeLogin(page, base, driver === 'generic-fastapi', observe, checked);
        }
        businessReady = true;
      });
    } catch (error) { failure = error; }
    await stage('assertions', async () => {
      if (fault === 'none') {
        assert.ifError(failure); assert.equal(businessReady, true);
        assert.deepEqual(checkedPaths, ['/admin-api/system/tenant/simple-list', '/admin-api/system/auth/login', driver === 'generic-fastapi' ? '/admin-api/system/user/current/info' : '/admin-api/system/auth/get-permission-info']);
        assert.equal(page.url(), base + '/#/dashboard/analytics');
        assert.equal(await page.evaluate(() => document.readyState), 'interactive');
        assert.equal(await page.evaluate(() => window.loaded), false);
        assert.equal(heldImages.length, 1);
        for (const selector of ['aside', 'header', '#__vben_main_content']) assert(await page.locator(selector).isVisible());
        // The old exact predicate/default load semantics still fail with URL, API and DOM ready.
        const oldFailure = (await oldReadiness).error;
        assert.equal(oldFailure?.name, 'TimeoutError');
        assert.match(oldFailure.message, /waiting for navigation until "load"/);
        assert.match(oldFailure.message, /navigated to .*#\/dashboard\/analytics/);
        assert.equal(await page.evaluate(() => window.loaded), false);
        releaseHeldImages('positive-assertions-complete');
        await stage('released-image-load', () => page.waitForLoadState('load'));
        assert.equal(await page.evaluate(() => window.loaded), true);
      } else {
        assert.equal(businessReady, false, 'A failed prerequisite must block business readiness');
        assert(failure, 'Driver must reject ' + fault);
        const expected = { 'login-failure': /Business application error 401/, 'permissions-failure': /Business application error 403/,
          'permissions-http-failure': /Business browser HTTP 403/, 'missing-menu': /Native role menu missing|No native menus/,
          'auth-route': /waitForURL: Timeout/, 'foreign-origin': /waitForURL: Timeout/,
          'missing-aside': /locator.waitFor: Timeout/, 'missing-main': /locator.waitFor: Timeout/ };
        assert.match(failure.message, expected[fault]);
        assert(!requests.some(route => route.includes('/infra/')), 'Never start business requests before login is ready');
      }
    });
    console.log('Native login HTTP/Chromium fixture verified: ' + driver + '/' + fault + '; old load timeout=' + oldTimeout);
  } finally {
    closing = true; releaseHeldImages('cleanup');
    try {
      if (browser) await stage('browser-cleanup', () => browser.close(), 3000);
    } finally {
      await Promise.all([[server, 'server'], [foreign, 'foreign-server']].map(([service, name]) =>
        stage(name + '-cleanup', () => new Promise(resolve => {
          service.close(resolve); service.closeAllConnections();
        }), 1000)));
    }
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
"""


@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "login-failure",
        "permissions-failure",
        "permissions-http-failure",
        "missing-menu",
        "auth-route",
        "foreign-origin",
        "missing-aside",
        "missing-main",
    ],
)
@pytest.mark.parametrize("driver", ["business", "generic", "generic-fastapi"])
def test_native_login_requires_authentication_permissions_route_and_shell(fault, driver, tmp_path):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is required in Actions")
    _run_driver(fault, driver, module, tmp_path)


def test_actual_native_journey_uses_checked_login_readiness_without_extending_timeout():
    source = (ROOT / "scripts/business_yudao_browser.cjs").read_text(encoding="utf-8")
    login = source.split("  async function login(role) {", 1)[1].split(
        "  async function openPage(", 1
    )[0]
    assert "await loginNativeSession(page, base, scenario.actors[role], observe, checked);" in login
    assert "page.setDefaultTimeout(45000)" in login
    assert login.index("await loginNativeSession(") < login.index("report.checks.push(")
    assert "await checked(response); const identity = await checked(info)" in source


def test_generic_native_journey_uses_checked_login_before_actual_list_and_ui():
    source = (ROOT / "scripts/native_browser.cjs").read_text(encoding="utf-8")
    main = source.split("async function main() {", 1)[1]
    assert "page.setDefaultTimeout(45000)" in main
    assert "await submitNativeLogin(page, base, fastapi, observe, checked);" in main
    assert main.index("await submitNativeLogin(") < main.index("await checked(listing)")
    assert main.index("await checked(listing)") < main.index("const pageResult =")
    assert "native_shell_visible: true" in main
    assert "Native boolean option was not selected" in main


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


def _run_driver(fault, driver, module, tmp_path):
    # clean_env intentionally drops arbitrary environment, including TMPDIR.
    # Pass only this fixture's owned directory; do not broaden the global allowlist.
    runtime_dir = (tmp_path / "browser-runtime").resolve()
    runtime_dir.mkdir()
    extras = {"PLAYWRIGHT_BROWSERS_PATH": "0"}
    extras.update({name: str(runtime_dir) for name in ("TMPDIR", "TMP", "TEMP")})
    with tempfile.TemporaryFile(mode="w+b", dir=runtime_dir) as output:
        process = subprocess.Popen(
            [shutil.which("node"), "-e", DRIVER, fault, module, "1800", driver],
            cwd=ROOT,
            env=clean_env(extras),
            stdout=output,
            stderr=subprocess.STDOUT,
            **process_options(),
        )
        timed_out = False
        cleanup_error = None
        try:
            process.wait(timeout=30)
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
        f"Native login fixture exceeded unchanged 30 s cap: {driver}/{fault}\n{diagnostic}"
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


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_timeout_retains_phase_receipt_and_original_cap(monkeypatch, tmp_path, cleanup_fails):
    waited = []
    process = SimpleNamespace(pid=100, returncode=None)

    def timed_out(**kwargs):
        waited.append(kwargs)
        raise subprocess.TimeoutExpired("fixture-node", kwargs["timeout"])

    process.wait = timed_out

    def launch(command, **kwargs):
        kwargs["stdout"].write(b'{"phase":"browser-start","event":"start"}\n')
        return process

    def cleanup(_):
        if cleanup_fails:
            raise RuntimeError("fixture cleanup canary")
        process.returncode = 0  # Even successful cleanup must not erase the timeout.

    monkeypatch.setattr(subprocess, "Popen", launch)
    monkeypatch.setitem(globals(), "_stop_owned_tree", cleanup)
    with pytest.raises(AssertionError) as failure:
        _run_driver("login-failure", "generic", "/fixture/playwright", tmp_path)
    message = str(failure.value)
    assert "exceeded unchanged 30 s cap" in message
    assert '{"phase":"browser-start","event":"start"}' in message
    if cleanup_fails:
        assert "Owned fixture cleanup failed: RuntimeError: fixture cleanup canary" in message
    assert waited == [{"timeout": 30}]


def test_fixture_tmpdir_extras_are_owned_and_do_not_broaden_clean_env(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setenv("TMPDIR", "/ambient-not-owned")
    monkeypatch.setenv("TMP", "/ambient-not-owned")
    monkeypatch.setenv("TEMP", "/ambient-not-owned")
    monkeypatch.setenv("FIXTURE_UNRELATED_ENV_CANARY", "must-not-leak")

    def launch(command, **kwargs):
        calls.append((command, kwargs))
        assert Path(kwargs["env"]["TMPDIR"]).is_dir()
        return SimpleNamespace(pid=100, wait=lambda **kw: None, poll=lambda: 0, returncode=0)

    monkeypatch.setattr(subprocess, "Popen", launch)
    _run_driver("none", "business", "/fixture/playwright", tmp_path)
    command, kwargs = calls[0]
    expected = str((tmp_path / "browser-runtime").resolve())
    assert {key: kwargs["env"][key] for key in ("TMPDIR", "TMP", "TEMP")} == {
        key: expected for key in ("TMPDIR", "TMP", "TEMP")
    }
    assert kwargs["env"]["PLAYWRIGHT_BROWSERS_PATH"] == "0"
    assert "FIXTURE_UNRELATED_ENV_CANARY" not in kwargs["env"]
    assert "TMPDIR" not in clean_env(), "Do not broaden the production allowlist"
    assert command[-4:] == ["none", "/fixture/playwright", "1800", "business"]


def test_fixture_diagnostics_and_cleanup_preserve_original_readiness_budgets():
    assert "page.setDefaultTimeout(1800)" in DRIVER
    assert "page.setDefaultNavigationTimeout(Number(oldTimeout))" in DRIVER
    assert "stage('released-image-load', () => page.waitForLoadState('load'))" in DRIVER
    assert "timestamp: new Date().toISOString()" in DRIVER
    for event in ("'received'", "'finish'", "'close'", "'release'"):
        assert event in DRIVER
    assert "page.on('load', () => mark('page-load', 'delivered'))" in DRIVER
    assert "['requestfinished', 'requestfailed']" in DRIVER
    assert DRIVER.index("let browser;\n  try {") < DRIVER.index("stage('foreign-server-start'")
    assert "} finally {\n      await Promise.all([[server, 'server']" in DRIVER
    assert "service.close(resolve); service.closeAllConnections();" in DRIVER


def test_diagnostic_output_is_bounded_and_retains_first_and_last_phase():
    data = b'{"phase":"browser-start"}\n' + b"x" * 40000 + b'{"phase":"browser-cleanup"}\n'
    result = _read_diagnostic(io.BytesIO(data), limit=512)
    assert len(result.encode("utf-8")) <= 512
    assert result.startswith('{"phase":"browser-start"}')
    assert result.endswith('{"phase":"browser-cleanup"}\n')
    assert "diagnostic bytes omitted" in result
    small = b'{"phase":"assertions","event":"done"}\n'
    assert _read_diagnostic(io.BytesIO(small)) == small.decode("utf-8")
