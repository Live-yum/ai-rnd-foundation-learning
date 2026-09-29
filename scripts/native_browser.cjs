// Runs against our disposable loopback lab. No mocked requests or injected authentication state.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

async function main() {
  const [template, base, reportDir, playwrightPath] = process.argv.slice(2);
  assert(['fastapiadmin', 'yudao-vben'].includes(template));
  assert.equal(new URL(base).hostname, '127.0.0.1');
  const { chromium } = require(playwrightPath);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'zh-CN' });
  const page = await context.newPage();
  page.setDefaultTimeout(45000);
  fs.mkdirSync(reportDir, { recursive: true });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const fastapi = template === 'fastapiadmin';
  const report = { template, scope: 'original-upstream-frontend', generated_modules_verified: false, passed: false };
  try {
    await page.goto(base + (fastapi ? '/#/login' : '/#/auth/login'), { waitUntil: 'domcontentloaded' });
    await page.getByPlaceholder(/用户名|账号|username/i).first().fill(fastapi ? 'super' : 'admin');
    await page.locator('input[type="password"]').first().fill(fastapi ? '123456' : 'admin123');
    if (fastapi) {
      // Exercise the local, visible demo drag widget; do not bypass server authentication.
      const handle = page.locator('.dv_handler').first();
      const track = page.locator('.drag_verify').first();
      await handle.waitFor({ state: 'visible' });
      const from = await handle.boundingBox();
      const to = await track.boundingBox();
      assert(from && to);
      await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
      await page.mouse.down();
      await page.mouse.move(to.x + to.width - 2, from.y + from.height / 2, { steps: 30 });
      await page.mouse.up();
    }
    const infoPath = fastapi ? '/system/user/current/info' : '/system/auth/get-permission-info';
    const loginPromise = page.waitForResponse(r => r.url().includes('/system/auth/login') && r.request().method() === 'POST');
    const menuPromise = page.waitForResponse(r => r.url().includes(infoPath) && r.request().method() === 'GET');
    await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
    const response = await loginPromise;
    assert(response.ok(), 'Native browser login HTTP failure');
    const loginBody = await response.json();
    assert([0, 200].includes(loginBody.code), 'Native browser login application failure');
    const menuResponse = await menuPromise;
    assert(menuResponse.ok());
    const info = await menuResponse.json();
    assert([0, 200].includes(info.code));
    assert(info.data.menus && info.data.menus.length, 'Native server returned no menus');
    const listPath = fastapi ? '/system/user/list' : '/system/user/page';
    const listPromise = page.waitForResponse(r => r.url().includes(listPath) && r.request().method() === 'GET');
    await page.goto(base + '/#/system/user', { waitUntil: 'domcontentloaded' });
    const listResponse = await listPromise;
    assert(listResponse.ok());
    const data = await listResponse.json();
    assert([0, 200].includes(data.code), 'Native user page API rejected the browser request');
    await page.locator(fastapi ? '.el-table' : '.vxe-table').first().waitFor({ state: 'visible' });
    await page.screenshot({ path: path.join(reportDir, 'native-user-page.png'), fullPage: true });
    assert.equal(errors.length, 0, 'Frontend emitted uncaught runtime errors');
    Object.assign(report, { passed: true, real_login: true, native_menu_received: true, original_user_page_rendered: true });
    console.log('Original native frontend: real login, menus and user page PASS');
  } catch (error) {
    report.error = error.message;
    await page.screenshot({ path: path.join(reportDir, 'browser-failure.png'), fullPage: true }).catch(() => {});
    throw error;
  } finally {
    report.page_errors = errors;
    fs.writeFileSync(path.join(reportDir, 'browser.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
