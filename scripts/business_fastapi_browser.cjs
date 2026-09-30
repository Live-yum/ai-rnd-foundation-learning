// Actual native sessions and rendered Fa/ElementPlus UI. No injected tokens or mocked routes.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

async function main() {
  const [baseURL, reportDir, playwrightPath, scenarioJSON] = process.argv.slice(2);
  assert.equal(new URL(baseURL).hostname, '127.0.0.1');
  const scenario = JSON.parse(fs.readFileSync(scenarioJSON, 'utf8'));
  const { chromium } = require(playwrightPath);
  const browser = await chromium.launch({ headless: true });
  const report = { passed: false, template: 'fastapiadmin', scope: 'native-business-ui', checks: [], errors: [], pages: [] };
  fs.mkdirSync(reportDir, { recursive: true });
  const contexts = [];
  report.screenshots = [];
  async function capture(p, label) {
    assert(/^[a-z0-9_-]+$/.test(label));
    const filename = label + '.png';
    await p.screenshot({ path: path.join(reportDir, filename), fullPage: true });
    report.screenshots.push(filename);
  }
  let page;
  async function checked(response) {
    assert(response.ok(), `Native business HTTP ${response.status()}`);
    const body = await response.json();
    assert([0, 200].includes(body.code), `Native business code ${body.code}`);
    return body.data;
  }
  function response(p, route, method = 'GET') {
    return p.waitForResponse(r => new URL(r.url()).pathname.endsWith(route) && r.request().method() === method);
  }
  async function login(role) {
    const credentials = scenario.actors[role];
    assert(credentials && credentials.username && credentials.password, `Missing synthetic role fixture: ${role}`);
    const context = await browser.newContext({ viewport: { width: 1600, height: 1100 }, locale: 'zh-CN' });
    contexts.push(context);
    const p = await context.newPage();
    p.setDefaultTimeout(45000);
    p.on('pageerror', () => report.errors.push('uncaught_frontend_error'));
    const captcha = response(p, '/system/auth/captcha/get');
    await p.goto(baseURL + '/#/login');
    await checked(await captcha);
    await p.getByPlaceholder(/用户名|账号|username/i).first().fill(credentials.username);
    await p.locator('input[type=password]').first().fill(credentials.password);
    const handle = p.locator('.dv_handler').first(), track = p.locator('.drag_verify').first();
    await handle.hover();
    const from = await handle.boundingBox(), to = await track.boundingBox();
    assert(from && to);
    const slider = response(p, '/system/auth/captcha/slider/complete', 'POST');
    await p.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
    await p.mouse.down();
    for (let step = 1; step <= 40; step++) {
      await p.mouse.move(from.x + from.width / 2 + (to.x + to.width - 2 - from.x - from.width / 2) * step / 40, from.y + from.height / 2);
      await p.waitForTimeout(20);
    }
    await p.mouse.up();
    await checked(await slider);
    const logged = response(p, '/system/auth/login', 'POST');
    const info = response(p, '/system/user/current/info');
    await p.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
    await checked(await logged);
    assert((await checked(await info)).menus.length, 'Native business menus missing');
    await p.waitForURL(url => !url.hash.includes('login'));
    const tour = p.getByRole('button', { name: '跳过', exact: true });
    if (await tour.isVisible()) await tour.click();
    const configResponse = response(p, '/business/configuration');
    await p.goto(baseURL + '/#' + (scenario.route || '/module_rnd/customers'));
    const config = await checked(await configResponse);
    assert.equal(config.actor.role, role.includes('employee') ? 'employee' : role.includes('service') ? 'service' : 'manager');
    for (const selector of ['#app-sidebar', '#app-header', '#app-content', '.fa-table']) await p.locator(selector).first().waitFor({ state: 'visible' });
    assert.equal(await p.locator('#workspace').count(), 0);
    const theme = await p.evaluate(() => {
      const css = getComputedStyle(document.documentElement);
      return Object.fromEntries(['--el-color-primary', '--el-font-size-base'].map(key => [key, css.getPropertyValue(key).trim()]));
    });
    assert(Object.values(theme).every(Boolean), 'Native theme tokens missing');
    p.businessProof = { role, route: scenario.route || '/module_rnd/customers', rendered: true, native_shell_visible: true, native_component_family: 'Fa/Element Plus', native_theme_tokens: theme, real_login: true, native_menu_received: true };
    report.pages.push({ ...p.businessProof });
    await capture(p, role + "-native-list");
    report.checks.push(`${role}:real_native_login_menu_shell`);
    return { p, config };
  }
  async function tab(p, config, entity) {
    const label = config.entities.find(e => e.name === entity)?.description || entity;
    const loaded = response(p, `/business/${entity}/list`);
    await p.getByRole('tab', { name: label, exact: true }).click();
    return checked(await loaded);
  }
  async function closeNativeDialog(dialog) {
    // Pinned FaDialog uses icon DIVs, not named button elements. The final icon is Close.
    const actions = dialog.locator('.core-overlay-dialog__actions .core-overlay-icon-btn');
    assert.equal(await actions.count(), 2, 'Pinned native dialog header changed');
    await actions.last().click();
    await dialog.waitFor({ state: 'hidden' });
  }
  async function choose(p, locator, value) {
    await locator.click();
    await p.getByRole('option', { name: value, exact: true }).last().click();
  }
  async function create(p, entity, fields) {
    await p.getByTestId('business-create').click();
    const dialog = p.getByRole('dialog', { name: '新增记录' });
    await dialog.locator('.el-form').waitFor({ state: 'visible' });
    for (const [name, spec] of Object.entries(fields)) {
      const field = dialog.getByTestId('field-' + name);
      if (spec.select) await choose(p, field.locator('.el-select'), spec.select);
      else await field.locator('input, textarea').first().fill(spec.text);
    }
    await capture(p, p.businessProof.role + "-" + entity + "-native-form");
    const created = response(p, `/business/${entity}/create`, 'POST');
    const refreshed = response(p, `/business/${entity}/list`);
    await dialog.getByTestId('business-save').click();
    const row = await checked(await created);
    assert((await checked(await refreshed)).items.some(item => item.id === row.id), 'Created row absent from real native list');
    await dialog.waitFor({ state: 'hidden' });
    report.pages.push({ ...p.businessProof, entity, route: '/module_rnd/' + entity, native_form_components_visible: true, real_form_create: true, real_list_request: true });
    return row;
  }
  async function assign(p, entity, row, name) {
    await p.getByTestId('assign-' + row.id).click();
    const dialog = p.getByRole('dialog', { name: '分配负责人' });
    await dialog.locator('.el-select').click();
    await p.getByRole('option', { name: new RegExp(name) }).click();
    await capture(p, "manager-" + entity + "-assignment");
    const assigned = response(p, `/business/${entity}/${row.id}/assign`, 'POST');
    await dialog.getByRole('button', { name: '确定', exact: true }).click();
    await checked(await assigned);
    await dialog.waitFor({ state: 'hidden' });
  }
  async function transition(p, entity, id, action) {
    const changed = response(p, `/business/${entity}/${id}/transition`, 'POST');
    await p.getByTestId(`transition-${id}-${action}`).click();
    return checked(await changed);
  }
  try {
    const manager = await login('manager'); page = manager.p;
    const marker = 'Browser ' + scenario.attempt;
    const customer = await create(page, 'customers', { name: { text: marker }, organization: { text: 'Synthetic browser team' }, contact: { text: 'ui@example.invalid' }, category: { select: '企业' } });
    assert.equal(customer.name, marker);
    report.checks.push('manager:customer_native_form_create');
    await page.getByTestId('update-' + customer.id).click();
    const edit = page.getByRole('dialog', { name: '编辑记录' });
    await edit.getByTestId('field-organization').locator('input').fill('Changed team');
    await capture(page, 'manager-customer-edit');
    const updated = response(page, `/business/customers/${customer.id}/update`, 'POST');
    await edit.getByTestId('business-save').click();
    assert.equal((await checked(await updated)).organization, 'Changed team');
    report.checks.push('manager:changed_value_edit');
    const employee = await login('employee'); page = employee.p;
    await tab(page, employee.config, 'requests');
    const request = await create(page, 'requests', { title: { text: marker + ' request' }, detail: { text: 'Browser-created support request' }, customer_id: { select: marker }, priority: { select: '普通' } });
    report.checks.push('employee:related_request_native_form_create');
    page = manager.p;
    await tab(page, manager.config, 'requests');
    await assign(page, 'requests', request, scenario.actors.service.name || 'Synthetic service');
    await tab(page, manager.config, 'tasks');
    const task = await create(page, 'tasks', { title: { text: marker + ' task' }, detail: { text: 'Browser follow-up' }, request_id: { select: marker + ' request' } });
    await assign(page, 'tasks', task, scenario.actors.service.name || 'Synthetic service');
    report.checks.push('manager:linked_task_and_native_assignment');
    const service = await login('service'); page = service.p;
    await tab(page, service.config, 'tasks');
    await transition(page, 'tasks', task.id, 'start');
    const doneTask = await transition(page, 'tasks', task.id, 'resolve');
    assert(doneTask.resolved_at);
    await tab(page, service.config, 'requests');
    await transition(page, 'requests', request.id, 'start');
    await page.getByTestId('note-' + request.id).click();
    const note = page.getByRole('dialog', { name: '新增备注' });
    await note.locator('textarea').fill('Browser handling note');
    const savedNote = response(page, `/business/requests/${request.id}/add_note`, 'POST');
    await note.getByRole('button', { name: '确定', exact: true }).click();
    await checked(await savedNote);
    assert((await transition(page, 'requests', request.id, 'resolve')).resolved_at);
    await capture(page, 'service-handled-request');
    report.checks.push('service:assigned_workflows_notes_timestamps');
    page = employee.p;
    await page.reload();
    await tab(page, employee.config, 'requests');
    await page.getByTestId('history-' + request.id).click();
    await page.getByRole('dialog', { name: '记录历史' }).getByText('Browser handling note', { exact: true }).waitFor();
    await capture(page, 'employee-request-timeline');
    await closeNativeDialog(page.getByRole('dialog', { name: '记录历史' }));
    const inbox = response(page, '/business/inbox');
    await page.getByRole('tab', { name: '提醒', exact: true }).click();
    const notices = await checked(await inbox);
    const own = notices.find(n => n.record_id === request.id && n.event === 'transitioned');
    assert(own, 'Own resolution reminder missing');
    await capture(page, 'employee-resolution-reminders');
    const marked = response(page, `/business/inbox/${own.id}/read`, 'POST');
    await page.getByTestId('read-notice-' + own.id).click(); await checked(await marked);
    report.checks.push('employee:own_timeline_and_read_reminder');
    for (const role of ['other_employee', 'other_service']) {
      const outsider = await login(role); page = outsider.p;
      const listing = await tab(page, outsider.config, 'requests');
      assert(!listing.items.some(row => row.id === request.id));
      assert.equal(await page.getByTestId('history-' + request.id).count(), 0);
      report.checks.push(`${role}:row_isolation`);
    }
    page = manager.p;
    await tab(page, manager.config, 'customers');
    await page.getByTestId('related-' + customer.id).click();
    const relations = page.getByRole('dialog', { name: '关联历史' });
    await relations.getByText(marker + ' request', { exact: true }).waitFor();
    await capture(page, 'manager-customer-related-history');
    await closeNativeDialog(relations);
    const metricResponse = response(page, '/business/metrics');
    await page.getByRole('tab', { name: '统计', exact: true }).click();
    const metrics = await checked(await metricResponse);
    assert.equal(metrics.length, scenario.plan.business.metrics.length);
    for (const metric of metrics) await page.getByRole('heading', { name: metric.label, exact: true }).waitFor();
    report.checks.push('manager:five_native_metric_cards');
    assert.equal(report.errors.length, 0);
    await capture(page, 'manager-native-dashboard');
    report.records = { customers: customer.id, requests: request.id, tasks: task.id };
    report.passed = true;
  } catch (error) {
    report.failure = { name: error.name, code: 'native_business_ui_failed' };
    if (page) await page.screenshot({ path: path.join(reportDir, 'business-native-failure.png'), fullPage: true }).catch(() => {});
    throw error;
  } finally {
    fs.writeFileSync(path.join(reportDir, 'business-browser.json'), JSON.stringify(report, null, 2));
    await Promise.all(contexts.map(context => context.close()));
    await browser.close();
  }
}
main().catch(error => { console.error(error.name + ': native business UI acceptance failed'); process.exitCode = 1; });
