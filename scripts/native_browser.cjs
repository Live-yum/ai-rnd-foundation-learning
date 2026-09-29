// Real Chromium against the disposable loopback lab; no route mocks or injected tokens.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

async function main() {
  const [template, base, reportDir, playwrightPath, moduleFile] = process.argv.slice(2);
  assert(['fastapiadmin', 'yudao-vben'].includes(template));
  assert.equal(new URL(base).hostname, '127.0.0.1');
  const { chromium } = require(playwrightPath);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'zh-CN' });
  const page = await context.newPage();
  page.setDefaultTimeout(45000);
  fs.mkdirSync(reportDir, { recursive: true });
  const errors = [];
  const responses = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => responses.push({ url: new URL(response.url()).pathname, status: response.status(), method: response.request().method() }));
  const fastapi = template === 'fastapiadmin';
  const report = { template, scope: moduleFile ? 'generated-native-frontend' : 'original-upstream-frontend', passed: false };
  const observe = (part, method = 'GET') => page.waitForResponse(r => r.url().includes(part) && r.request().method() === method).then(r => ({ response: r }), error => ({ error }));
  const checked = async promise => {
    const value = await promise;
    if (value.error) throw value.error;
    assert(value.response.ok(), `HTTP ${value.response.status()}`);
    const body = await value.response.json();
    assert([0, 200].includes(body.code), `Application code ${body.code}`);
    return body.data;
  };
  try {
    const captcha = fastapi ? observe('/system/auth/captcha/get') : null;
    await page.goto(base + (fastapi ? '/#/login' : '/#/auth/login'), { waitUntil: 'domcontentloaded' });
    if (captcha) await checked(captcha);
    await page.getByPlaceholder(/用户名|账号|username/i).first().fill(fastapi ? 'super' : 'admin');
    await page.locator('input[type="password"]').first().fill(fastapi ? '123456' : 'admin123');
    if (fastapi) {
      const handle = page.locator('.dv_handler').first();
      const track = page.locator('.drag_verify').first();
      await handle.waitFor({ state: 'visible' });
      const from = await handle.boundingBox();
      const to = await track.boundingBox();
      assert(from && to);
      const slider = observe('/system/auth/captcha/slider/complete', 'POST');
      await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
      await page.mouse.down();
      await page.mouse.move(to.x + to.width + 10, from.y + from.height / 2, { steps: 40 });
      await page.mouse.up();
      await checked(slider);
    }
    const loginResponse = observe('/system/auth/login', 'POST');
    const infoResponse = observe(fastapi ? '/system/user/current/info' : '/system/auth/get-permission-info');
    await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
    await checked(loginResponse);
    const info = await checked(infoResponse);
    assert(info.menus && info.menus.length, 'No native menus');
    const targets = moduleFile ? JSON.parse(fs.readFileSync(moduleFile, 'utf8')) : [{ route: '/system/user', list: fastapi ? '/system/user/list' : '/system/user/page' }];
    report.pages = [];
    for (const target of targets) {
      const listing = observe(target.list);
      await page.goto(base + '/#' + target.route, { waitUntil: 'domcontentloaded' });
      await checked(listing);
      await page.locator(fastapi ? '.el-table' : '.vxe-table').first().waitFor({ state: 'visible' });
      if (target.sample) await page.getByText(target.sample, { exact: true }).first().waitFor({ state: 'visible' });
      await page.screenshot({ path: path.join(reportDir, (target.entity || 'system-user') + '.png'), fullPage: true });
      report.pages.push({ route: target.route, real_list_request: true, rendered: true });
    }
    assert.equal(errors.length, 0, 'Uncaught frontend errors');
    Object.assign(report, { passed: true, real_login: true, native_menu_received: true, generated_modules_verified: !!moduleFile });
    console.log('Native frontend login, menus and tables PASS');
  } catch (error) {
    report.error = error.message;
    await page.screenshot({ path: path.join(reportDir, 'browser-failure.png'), fullPage: true }).catch(() => {});
    throw error;
  } finally {
    report.page_errors = errors;
    report.responses = responses;
    fs.writeFileSync(path.join(reportDir, 'browser.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
main().catch(error => { console.error(error.stack); process.exitCode = 1; });
