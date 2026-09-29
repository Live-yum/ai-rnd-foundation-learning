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
      // Hover uses Playwright's visibility/stability checks before sampling the
      // animated native form. Keep the pointer INSIDE the parent: mouseleave
      // resets this upstream slider before it can report success.
      await handle.hover();
      const from = await handle.boundingBox();
      const to = await track.boundingBox();
      assert(from && to);
      const slider = observe('/system/auth/captcha/slider/complete', 'POST');
      await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
      await page.mouse.down();
      const start = from.x + from.width / 2;
      const finish = to.x + to.width - 2;
      for (let step = 1; step <= 40; step++) {
        await page.mouse.move(start + (finish - start) * step / 40, from.y + from.height / 2);
        await page.waitForTimeout(20);
      }
      report.slider = { before: from, track: to, after: await handle.boundingBox() };
      await page.mouse.up();
      await checked(slider);
    }
    const loginResponse = observe('/system/auth/login', 'POST');
    const infoResponse = observe(fastapi ? '/system/user/current/info' : '/system/auth/get-permission-info');
    await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
    await checked(loginResponse);
    const info = await checked(infoResponse);
    await page.waitForURL(url => !url.hash.includes('login'));
    assert(info.menus && info.menus.length, 'No native menus');
    // Dismiss the native first-login product tour through its visible UI.
    const skipTour = page.getByRole('button', { name: '跳过', exact: true });
    if (fastapi && await skipTour.isVisible()) await skipTour.click();
    const targets = moduleFile ? JSON.parse(fs.readFileSync(moduleFile, 'utf8')) : [{ route: '/system/user', list: fastapi ? '/system/user/list' : '/system/user/page' }];
    report.pages = [];
    for (const target of targets) {
      const listing = observe(target.list);
      await page.goto(base + '/#' + target.route, { waitUntil: 'domcontentloaded' });
      await checked(listing);
      await page.locator(fastapi ? '.el-table' : '.vxe-table').first().waitFor({ state: 'visible' });
      if (target.sample) await page.getByText(target.sample, { exact: true }).first().waitFor({ state: 'visible' });
      await page.screenshot({ path: path.join(reportDir, (target.entity || 'system-user') + '.png'), fullPage: true });
      const pageResult = { route: target.route, real_list_request: true, rendered: true };
      if (!fastapi && target.fields) {
        // Submit through the real generated UI; zero/false must not become strings or disappear.
        await page.getByRole('button', { name: /^新增|^创建/ }).first().click();
        const dialog = page.getByRole('dialog').last();
        await dialog.waitFor({ state: 'visible' });
        const expected = {};
        let booleanIndex = 0;
        for (const field of target.fields) {
          const key = field.name.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
          if (field.kind === 'boolean') {
            await dialog.getByRole('radio', { name: '否', exact: true }).nth(booleanIndex++).check();
            expected[key] = false;
          } else {
            const value = field.kind === 'integer' ? 0 : (target.entity + '-browser').slice(0, field.max_length);
            await dialog.getByPlaceholder('请输入' + field.name, { exact: true }).fill(String(value));
            expected[key] = value;
          }
        }
        const created = observe(target.api + '/create', 'POST');
        const refreshed = observe(target.list);
        await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
        const captured = await created;
        if (captured.error) throw captured.error;
        const sent = captured.response.request().postDataJSON();
        for (const [key, value] of Object.entries(expected)) assert.equal(sent[key], value, 'Generated form kind: ' + key);
        await checked(Promise.resolve(captured));
        const listed = await checked(refreshed);
        assert(listed.list.some(row => Object.entries(expected).every(([key, value]) => row[key] === value)), 'Submitted record was not returned by real list API');
        await dialog.waitFor({ state: 'hidden' });
        const text = Object.values(expected).find(value => typeof value === 'string');
        if (text) await page.getByText(text, { exact: true }).first().waitFor({ state: 'visible' });
        await page.screenshot({ path: path.join(reportDir, target.entity + '-created.png'), fullPage: true });
        pageResult.real_form_create = true;
        pageResult.typed_values_preserved = true;
      }
      report.pages.push(pageResult);
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
