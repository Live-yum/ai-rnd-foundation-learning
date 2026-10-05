# scripts/native_browser.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：真实原生登录、菜单、表单与规则浏览器检查。** 按FastapiAdmin或Vben的真实DOM操作，登录提交必须核对实际认证/权限HTTP、同源非登录路由和原生shell，不等待概览页无关资源的整页load；再验证生成菜单的实际列表API/DOM、原生组件及表单正反例。失败截图/网络错误用于诊断，不能注入令牌越过登录，45秒等待上限不变。

**对应关系：** native_frontend.browser_check → 本文件 → browser.json与截图。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/native_browser.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L214。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13551`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/native_browser.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e9bb081a34d7c3a52e02fd0be18de221bfd27cfe7c752ce8b6cf8d1d443d34ad"} -->
````javascript
// scripts/native_browser.cjs
// Real Chromium against the disposable loopback lab; no route mocks or injected tokens.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

function nativeComponentSelectors(fastapi) {
  return {
    button: fastapi ? '.el-button:visible' : '.ant-btn:visible',
    form: fastapi ? '.el-input:visible, .el-switch:visible' : '.ant-input:visible, .ant-input-number:visible, .ant-radio:visible',
  };
}

async function submitNativeLogin(page, base, fastapi, observe, checked) {
  const loginResponse = observe('/system/auth/login', 'POST');
  const infoResponse = observe(fastapi ? '/system/user/current/info' : '/system/auth/get-permission-info');
  await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
  await checked(loginResponse);
  const info = await checked(infoResponse);
  assert(Array.isArray(info.menus) && info.menus.length, 'No native menus');
  const origin = new URL(base).origin;
  // A native SPA shell can be authenticated while a dashboard image still
  // delays window.load. Authentication, permissions, same-origin route and
  // actual shell visibility are mandatory; the real target list is checked next.
  await page.waitForURL(url => url.origin === origin && url.hash.startsWith('#/')
    && !/^#\/(?:auth|login)(?:[/?]|$)/.test(url.hash), { waitUntil: 'domcontentloaded' });
  const shell = fastapi ? ['#app-sidebar', '#app-header', '#app-content'] : ['aside:visible', 'header:visible', '#__vben_main_content'];
  for (const selector of shell) await page.locator(selector).first().waitFor({ state: 'visible' });
  return info;
}

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
  const requests = [];
  page.on('request', request => requests.push({ url: new URL(request.url()).pathname, method: request.method() }));
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => responses.push({ url: new URL(response.url()).pathname, status: response.status(), method: response.request().method() }));
  const fastapi = template === 'fastapiadmin';
  const components = nativeComponentSelectors(fastapi);
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
    const tenants = fastapi ? null : observe('/system/tenant/simple-list');
    await page.goto(base + (fastapi ? '/#/login' : '/#/auth/login'), { waitUntil: 'domcontentloaded' });
    if (captcha) await checked(captcha);
    if (tenants) {
      const available = await checked(tenants);
      assert(Array.isArray(available) && available.length, 'No selectable native tenant');
      const tenant = available.find(item => item.id === 1);
      assert(tenant, 'The seeded native tenant 1 is unavailable');
      // The asynchronous default label is not proof of a validated form value.
      // Select the actual tenant via the UI before submitting, never inject tokens.
      await page.getByRole('combobox').first().click();
      await page.getByRole('option', { name: tenant.name, exact: true }).click();
      report.tenant_selected = tenant.id;
    }
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
    await submitNativeLogin(page, base, fastapi, observe, checked);
    // Dismiss the native first-login product tour through its visible UI.
    const skipTour = page.getByRole('button', { name: '跳过', exact: true });
    if (fastapi && await skipTour.isVisible()) await skipTour.click();
    const targets = moduleFile ? JSON.parse(fs.readFileSync(moduleFile, 'utf8')) : [{ route: '/system/user', list: fastapi ? '/system/user/list' : '/system/user/page' }];
    report.pages = [];
    for (const target of targets) {
      const listing = observe(target.list);
      await page.goto(base + '/#' + target.route, { waitUntil: 'domcontentloaded' });
      const listData = await checked(listing);
      if (target.sample_record) {
        const rows = listData.items || listData.list;
        assert(Array.isArray(rows), 'Native listing omitted actual rows');
        const persisted = rows.find(row => row.id === target.sample_record.id);
        assert(persisted, 'Native browser list omitted persistent sample');
        for (const [key, value] of Object.entries(target.sample_record)) assert.deepEqual(persisted[key], value, 'Native browser list field differs: ' + key);
      }
      await page.locator(fastapi ? '.el-table' : '.vxe-table').first().waitFor({ state: 'visible' });
      if (target.sample_record && !target.sample) await page.locator(fastapi ? '.el-table__body tbody tr' : '.vxe-table--body tbody tr').first().waitFor({ state: 'visible' });
      if (target.sample) await page.getByText(target.sample, { exact: true }).first().waitFor({ state: 'visible' });
      // Verify the selected template's actual rendered shell and component system.
      // A generic table with matching data is not a native frontend acceptance.
      const shell = fastapi ? ['#app-sidebar', '#app-header', '#app-content'] : ['aside:visible', 'header:visible', '#__vben_main_content'];
      for (const selector of shell) await page.locator(selector).first().waitFor({ state: 'visible' });
      await page.locator(components.button).first().waitFor({ state: 'visible' });
      assert.equal(await page.locator('#workspace').count(), 0, 'Generic simple-admin cannot replace a native template');
      const theme = await page.evaluate(fast => {
        const style = getComputedStyle(document.documentElement);
        const variables = fast ? ['--el-color-primary', '--el-font-size-base'] : ['--primary', '--background', '--font-family'];
        return Object.fromEntries(variables.map(name => [name, style.getPropertyValue(name).trim()]));
      }, fastapi);
      assert(Object.values(theme).every(Boolean), 'Native theme tokens were not loaded');

      await page.screenshot({ path: path.join(reportDir, (target.entity || 'system-user') + '.png'), fullPage: true });
      const pageResult = { route: target.route, real_list_request: true, rendered: true, native_shell_visible: true, native_component_family: fastapi ? 'Fa/Element Plus' : 'Vben/Ant Design/VXE', native_theme_tokens: theme };
      if (target.fields || target.business_rule) {
        // Submit through the real generated UI; zero/false must not become strings or disappear.
        await page.getByRole('button', { name: /^新增|^创建/ }).first().click();
        const dialog = page.getByRole('dialog').last();
        await dialog.waitFor({ state: 'visible' });
        await dialog.locator(components.form).first().waitFor({ state: 'visible' });
        await page.screenshot({ path: path.join(reportDir, target.entity + '-native-form.png'), fullPage: true });
        pageResult.native_form_components_visible = true;

        async function fill(sample) {
          const expected = {};
          let booleanIndex = 0;
          for (const field of target.fields) {
            const key = fastapi ? field.name : field.name.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
            const value = sample ? sample[key] : (field.kind === 'boolean' ? false : field.kind === 'integer' ? 0 : (target.entity + '-browser').slice(0, field.max_length));
            if (field.kind === 'boolean') {
              if (fastapi) {
                const toggle = dialog.getByRole('switch').nth(booleanIndex++);
                if ((await toggle.getAttribute('aria-checked') === 'true') !== value) await toggle.click();
              } else {
                const radio = dialog.getByRole('radio', { name: value ? '是' : '否', exact: true }).nth(booleanIndex++);
                await radio.locator('xpath=ancestor::label[1]').click();
                assert(await radio.isChecked(), 'Native boolean option was not selected');
              }
            } else {
              await dialog.getByPlaceholder('请输入' + field.name, { exact: true }).fill(String(value));
            }
            expected[key] = value;
          }
          return expected;
        }
        if (target.business_rule) {
          await dialog.getByRole('note').waitFor({ state: 'visible' });
          pageResult.plop_rule_component_rendered = true;
          await fill(target.business_rule.reject);
          const before = requests.filter(r => r.url.endsWith(target.api + '/create') && r.method === 'POST').length;
          await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
          await page.getByText('RND_BUSINESS_RULE', { exact: true }).first().waitFor({ state: 'visible' });
          assert.equal(requests.filter(r => r.url.endsWith(target.api + '/create') && r.method === 'POST').length, before, 'Frontend guard must reject before calling the backend');
          assert(await dialog.isVisible(), 'Rejected business input closed the form');
          pageResult.business_rule_rejected_before_http = true;
        }
        const expected = await fill(target.business_rule?.accept);
        const created = observe(target.api + '/create', 'POST');
        const refreshed = observe(target.list);
        await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
        const captured = await created;
        if (captured.error) throw captured.error;
        const sent = captured.response.request().postDataJSON();
        for (const [key, value] of Object.entries(expected)) assert.equal(sent[key], value, 'Generated form kind: ' + key);
        await checked(Promise.resolve(captured));
        const listed = await checked(refreshed);
        assert((listed.items || listed.list).some(row => Object.entries(expected).every(([key, value]) => row[key] === value)), 'Submitted record was not returned by real list API');
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
    report.requests = requests;
    report.final_url = page.url();
    fs.writeFileSync(path.join(reportDir, 'browser.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
module.exports = { nativeComponentSelectors, submitNativeLogin };
if (require.main === module) main().catch(error => { console.error(error.stack); process.exitCode = 1; });
````
