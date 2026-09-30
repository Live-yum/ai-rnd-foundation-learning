// Real Vben/Ant business journey. Only scenario-owned synthetic accounts; no mocks/token injection.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

async function main() {
  const [base, reportDir, playwrightPath, scenarioFile] = process.argv.slice(2);
  assert.equal(new URL(base).hostname, '127.0.0.1');
  const scenario = JSON.parse(fs.readFileSync(scenarioFile, 'utf8'));
  for (const role of ['manager', 'service', 'employee']) {
    assert.equal(typeof scenario.actors?.[role]?.username, 'string');
    assert.equal(typeof scenario.actors?.[role]?.password, 'string');
  }
  const { chromium } = require(playwrightPath);
  const browser = await chromium.launch({ headless: true });
  fs.mkdirSync(reportDir, { recursive: true });
  const report = { passed: false, template: 'yudao-vben', real_login: false, native_shell: false, pages: [], journeys: [], checks: [], screenshots: [] };
  const secrets = Object.values(scenario.actors).map(actor => actor.password);
  const redact = value => secrets.reduce((text, secret) => text.split(secret).join('[REDACTED]'), String(value));
  const errors = [];
  let context, page;
  const target = entity => {
    const found = scenario.targets.find(item => item.entity === entity);
    assert(found, `Missing target ${entity}`); return found;
  };
  const observe = (part, method = 'GET') => page.waitForResponse(r => new URL(r.url()).pathname.endsWith(part) && r.request().method() === method)
    .then(response => ({ response }), error => ({ error }));
  const checked = async promise => {
    const found = await promise; if (found.error) throw found.error;
    assert(found.response.ok(), `Business browser HTTP ${found.response.status()}`);
    const value = await found.response.json(); assert.equal(value.code, 0, `Business application error ${value.code}`); return value.data;
  };
  async function capture(name) {
    await page.screenshot({ path: path.join(reportDir, name), fullPage: true, animations: 'disabled' });
    report.screenshots.push(name);
  }
  async function login(role) {
    if (context) await context.close();
    context = await browser.newContext({ locale: 'zh-CN', viewport: { width: 1500, height: 1100 }, reducedMotion: 'reduce' });
    page = await context.newPage(); page.setDefaultTimeout(45000);
    page.on('pageerror', error => errors.push(redact(error.message)));
    const tenants = observe('/admin-api/system/tenant/simple-list');
    await page.goto(base + '/#/auth/login', { waitUntil: 'domcontentloaded' });
    const available = await checked(tenants); const tenant = available.find(item => item.id === 1); assert(tenant);
    await page.getByRole('combobox').first().click();
    await page.getByRole('option', { name: tenant.name, exact: true }).click();
    await page.getByPlaceholder(/用户名|账号|username/i).first().fill(scenario.actors[role].username);
    await page.locator('input[type=password]').first().fill(scenario.actors[role].password);
    const response = observe('/admin-api/system/auth/login', 'POST');
    const info = observe('/admin-api/system/auth/get-permission-info');
    await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
    await checked(response); const identity = await checked(info); assert(identity.menus?.length, 'Native role menu missing');
    await page.waitForURL(url => !url.hash.includes('login'));
    report.checks.push(`${role}:native-login-and-tenant`);
  }
  async function openPage(entity) {
    const current = target(entity), listing = observe(current.list);
    await page.goto(base + '/#' + current.route, { waitUntil: 'domcontentloaded' });
    await checked(listing);
    for (const selector of ['aside:visible', 'header:visible', '#__vben_main_content', '.vxe-table:visible', '[data-rnd-business-panel]']) await page.locator(selector).first().waitFor({ state: 'visible' });
    assert.equal(await page.locator('#workspace').count(), 0, 'Generic frontend is forbidden');
    const theme = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return Object.fromEntries(['--primary', '--background', '--font-family'].map(key => [key, style.getPropertyValue(key).trim()]));
    });
    assert(Object.values(theme).every(Boolean)); report.native_shell = true;
    let proof = report.pages.find(item => item.entity === entity);
    if (!proof) { proof = { entity, route: current.route }; report.pages.push(proof); }
    Object.assign(proof, { native_shell_visible: true, native_component_family: 'Vben/Ant Design/VXE', native_theme_tokens: theme, rendered: true, real_list_request: true });
    return current;
  }
  async function detail(entity, label) {
    await openPage(entity);
    const row = page.locator('.vxe-body--row').filter({ has: page.getByText(label, { exact: true }) }).first();
    await row.waitFor({ state: 'visible' });
    const meta = observe('/admin-api/infra/rnd-business/meta');
    await row.getByRole('button', { name: '业务详情', exact: true }).click();
    await checked(meta);
    await page.locator('[data-rnd-business-panel]').scrollIntoViewIfNeeded();
  }
  async function select(locator, label, screenshot) {
    await locator.click();
    const option = page.locator('.ant-select-dropdown:visible').getByText(label, { exact: true }).last();
    if (screenshot) { await option.waitFor({ state: 'visible' }); await capture(screenshot); }
    await option.click();
  }
  const created = {}, labels = {};
  const marker = 'Browser ' + Date.now();
  async function create(entity) {
    const current = await openPage(entity);
    await page.getByRole('button', { name: /^新增|^创建/ }).first().click();
    const dialog = page.getByRole('dialog').last(); await dialog.waitFor({ state: 'visible' });
    await dialog.locator('.ant-input:visible, .ant-select:visible, .ant-input-number:visible').first().waitFor({ state: 'visible' });
    report.pages.find(item => item.entity === entity).native_form_components_visible = true;
    const definition = scenario.plan.entities.find(item => item.name === entity); assert(definition);
    const resource = scenario.plan.business.resources.find(item => item.entity === entity);
    const workflow = scenario.plan.business.workflows.find(item => item.entity === entity);
    const protectedFields = new Set([resource.assignee_field, workflow?.status_field, ...(workflow?.transitions || []).map(item => item.set_timestamp)]);
    for (const field of definition.fields) {
      if (protectedFields.has(field.name)) continue;
      const relation = scenario.plan.business.relations.find(item => item.entity === entity && item.field === field.name);
      const input = dialog.getByTestId('business-field-' + field.name);
      if (relation) {
        assert(labels[relation.target_entity], 'Create referenced browser record first');
        await select(input, labels[relation.target_entity], `${entity}-${field.name}-relation-picker.png`);
      } else if (field.kind === 'enum') await select(input, field.choices[0]);
      else if (field.kind === 'boolean') await select(input, '否');
      else if (field.kind === 'integer') await input.fill('1');
      else if (field.kind === 'datetime' || field.kind === 'date') {
        if (field.required) {
          await input.fill(field.kind === 'date' ? '2026-09-30' : '2026-09-30 12:00:00 UTC');
          await input.press('Enter');
        }
      } else {
        const value = (marker + ' ' + entity + ' ' + field.name).slice(0, field.max_length || 200);
        await input.fill(value); if (!labels[entity]) labels[entity] = value;
      }
    }
    await capture(`${entity}-filled-native-form.png`);
    const response = observe(current.api + '/create', 'POST');
    await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
    created[entity] = String(await checked(response));
    await dialog.waitFor({ state: 'hidden' });
    await page.getByText(labels[entity], { exact: true }).first().waitFor({ state: 'visible' });
    await capture(`${entity}-native-list.png`);
    report.checks.push(`manager:${entity}:native-form-create`);
  }
  async function action(kind, transition, note) {
    const id = kind === 'assign' ? 'business-assign' : kind === 'add_note' ? 'business-note' : 'business-transition-' + transition;
    await page.getByTestId(id).click();
    const dialog = page.getByRole('dialog').last(); await dialog.waitFor({ state: 'visible' });
    if (kind === 'assign') {
      await dialog.getByTestId('business-assignee').click();
      await page.locator('.ant-select-dropdown:visible [title]').filter({ hasText: `(#${scenario.actors.service.id})` }).last().click();
    }
    if (note) await dialog.getByTestId('business-note-input').fill(note);
    const response = observe('/admin-api/infra/rnd-business/action', 'POST');
    await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
    const row = await checked(response);
    await dialog.waitFor({ state: 'hidden' });
    if (kind === 'assign') assert.equal(row.assigneeId, String(scenario.actors.service.id));
    report.checks.push(`native-business-action:${kind}:${transition || ''}`);
    return row;
  }
  try {
    await login('manager');
    for (const entity of ['customers', 'requests', 'tasks']) await create(entity);
    for (const entity of ['requests', 'tasks']) { await detail(entity, labels[entity]); await action('assign', null, 'Browser assignment'); await capture(`${entity}-manager-workflow-controls.png`); }
    for (const [parent, child] of [['customers', 'requests'], ['requests', 'tasks']]) {
      await detail(parent, labels[parent]);
      const group = page.getByTestId('business-related-' + child);
      await group.waitFor({ state: 'visible' });
      await group.getByText(labels[child], { exact: true }).waitFor({ state: 'visible' });
      const historyResponse = observe('/admin-api/infra/rnd-business/history');
      await group.getByTestId(`related-history-${child}-${created[child]}`).click();
      const events = await checked(historyResponse);
      assert(events.some(event => event.action === 'assign'), 'Related child assignment history missing');
      await page.getByTestId('business-related-history').locator('.ant-timeline-item').first().waitFor({ state: 'visible' });
      await capture(`${parent}-${child}-related-history.png`);
      report.checks.push(`manager:${parent}:${child}:related-record-and-history`);
    }
    await page.locator('[data-rnd-business-panel] canvas').first().waitFor({ state: 'visible' });
    report.checks.push('manager:real-native-echarts-metrics');
    await capture('manager-vben-business.png');
    await capture('manager-business-dashboard.png');
    report.journeys.push({ actor: 'manager', real_create: ['customers', 'requests', 'tasks'], real_assignment: true, native_form_modal: true });
    await login('service');
    for (const entity of ['requests', 'tasks']) {
      await detail(entity, labels[entity]);
      await action('transition', 'start', 'Browser processing');
      await action('add_note', null, 'Browser work recorded');
      await action('transition', 'resolve', 'Browser complete');
      await page.getByText('Browser work recorded', { exact: true }).first().waitFor({ state: 'visible' });
      await capture(`${entity}-service-handling-history.png`);
    }
    await capture('service-vben-timeline.png');
    report.journeys.push({ actor: 'service', assigned_records: true, transitions: true, handling_notes: true, timeline: true });
    await login('employee');
    const employeeLabel = scenario.labels?.requests || 'Synthetic consultation ' + scenario.attempt;
    await detail('requests', employeeLabel);
    const panel = page.locator('[data-rnd-business-panel]');
    assert.equal(await panel.getByTestId('business-assign').count(), 0, 'Employee must not receive assignment controls');
    assert.equal(await panel.getByTestId('business-transition-start').count(), 0, 'Employee must not receive transition controls');
    await panel.locator('.ant-timeline-item').first().waitFor({ state: 'visible' });
    await capture('employee-owned-history.png');
    await panel.getByText('站内提醒', { exact: true }).waitFor({ state: 'visible' });
    const reminder = panel.getByText('requests #' + scenario.records.requests + ' transitioned', { exact: true });
    await reminder.first().waitFor({ state: 'visible' });
    const reminderRow = page.locator('.ant-table-row').filter({ has: reminder }).first();
    const unread = reminderRow.getByRole('button', { name: '标为已读', exact: true });
    if (await unread.count()) {
      const marked = observe('/admin-api/infra/rnd-business/notifications/read', 'POST');
      await unread.click(); await checked(marked);
      await reminderRow.getByText('已读', { exact: true }).waitFor({ state: 'visible' });
    }
    await capture('employee-vben-reminders.png');
    report.journeys.push({ actor: 'employee', own_history: true, recipient_reminders: true, unauthorized_controls_absent: true });
    assert.equal(errors.length, 0, 'Uncaught business frontend errors');
    Object.assign(report, { passed: true, real_login: true, native_component_family: 'Vben/Ant Design/VXE/Echarts', created_records: created });
  } catch (error) {
    report.error = redact(error.message);
    if (page) await page.screenshot({ path: path.join(reportDir, 'business-browser-failure.png'), fullPage: true, animations: 'disabled' }).catch(() => {});
    throw new Error(report.error);
  } finally {
    report.errors = errors;
    report.page_errors = errors;
    fs.writeFileSync(path.join(reportDir, 'business-browser.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
module.exports = { main };
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
