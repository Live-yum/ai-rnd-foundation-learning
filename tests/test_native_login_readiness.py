"""Real HTTP/Chromium regressions for the native login driver, not stack acceptance."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from workbench.settings import ROOT
from workbench.tools import clean_env

DRIVER = r"""
const assert = require('node:assert/strict');
const http = require('node:http');
const { loginNativeSession } = require('./scripts/business_yudao_browser.cjs');
const [fault, playwrightPath, oldTimeout = '1800'] = process.argv.slice(1);
const { chromium } = require(playwrightPath);
const actor = { username: 'fixture-manager', password: 'fixture-only-password' };
const requests = [], heldImages = [];
const shell = '<aside>Native menu</aside><header>Native header</header><main id="__vben_main_content">Dashboard</main>';
const foreign = http.createServer((req, res) => res.end(shell));
const server = http.createServer(async (req, res) => {
  const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
  if (pathname === '/delayed-dashboard-image') {
    heldImages.push(res); return; // Complete the real HTTP response only after the assertions.
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
    if (pathname.endsWith('/auth/get-permission-info')) {
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
        await (await fetch('/admin-api/system/auth/get-permission-info')).json();
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
  await new Promise(resolve => foreign.listen(0, '127.0.0.1', resolve));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage(); page.setDefaultTimeout(1800);
    page.setDefaultNavigationTimeout(Number(oldTimeout));
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
      if (fault === 'foreign-origin' && found.response.url().endsWith('/auth/get-permission-info')) {
        await page.evaluate(() => dispatchEvent(new Event('permissions-inspected')));
      }
      return body.data;
    };
    let failure, businessReady = false;
    try {
      await loginNativeSession(page, base, actor, observe, checked);
      businessReady = true;
    } catch (error) { failure = error; }
    if (fault === 'none') {
      assert.ifError(failure); assert.equal(businessReady, true);
      assert.deepEqual(checkedPaths, ['/admin-api/system/tenant/simple-list', '/admin-api/system/auth/login', '/admin-api/system/auth/get-permission-info']);
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
      for (const response of heldImages) response.end();
      await page.waitForLoadState('load');
      assert.equal(await page.evaluate(() => window.loaded), true);
    } else {
      assert.equal(businessReady, false, 'A failed prerequisite must block business readiness');
      assert(failure, 'Driver must reject ' + fault);
      const expected = { 'login-failure': /Business application error 401/, 'permissions-failure': /Business application error 403/,
        'permissions-http-failure': /Business browser HTTP 403/, 'missing-menu': /Native role menu missing/,
        'auth-route': /waitForURL: Timeout/, 'foreign-origin': /waitForURL: Timeout/,
        'missing-aside': /locator.waitFor: Timeout/, 'missing-main': /locator.waitFor: Timeout/ };
      assert.match(failure.message, expected[fault]);
      assert(!requests.some(route => route.includes('/infra/')), 'Never start business requests before login is ready');
    }
    console.log('Native login HTTP/Chromium fixture verified: ' + fault + '; old load timeout=' + oldTimeout);
  } finally {
    for (const response of heldImages) response.end();
    await browser.close();
    await Promise.all([server, foreign].map(service => new Promise(resolve => service.close(resolve))));
  }
})().catch(error => { console.error(error); server.close(); foreign.close(); process.exitCode = 1; });
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
def test_native_login_requires_authentication_permissions_route_and_shell(fault):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is required in Actions")
    result = subprocess.run(
        [shutil.which("node"), "-e", DRIVER, fault, module],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_actual_native_journey_uses_checked_login_readiness_without_extending_timeout():
    source = (ROOT / "scripts/business_yudao_browser.cjs").read_text(encoding="utf-8")
    login = source.split("  async function login(role) {", 1)[1].split(
        "  async function openPage(", 1
    )[0]
    assert "await loginNativeSession(page, base, scenario.actors[role], observe, checked);" in login
    assert "page.setDefaultTimeout(45000)" in login
    assert login.index("await loginNativeSession(") < login.index("report.checks.push(")
    assert "await checked(response); const identity = await checked(info)" in source
