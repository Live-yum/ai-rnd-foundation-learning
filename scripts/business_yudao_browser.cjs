// Real Vben/Ant business journey. Only scenario-owned synthetic accounts; no mocks/token injection.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

// Vben keeps visited tabs alive, so activating a tab need not issue a new list request.
// Exercise its actual search control to refresh the list and verify the resulting HTTP response.
async function refreshNativeList(page, entity, list, observe, checked) {
  const current = page.locator(`[data-rnd-business-entity="${entity}"]:visible`);
  const search = current.getByRole('button', { name: /^搜\s*索$/ });
  await search.waitFor({ state: 'visible' });
  const listing = observe(list);
  await search.click();
  return checked(listing);
}

// VXE renders fixed action columns in a separate table row with the same rowid.
// The visible title cell and its action button need not share a DOM row.
function nativeDetailButton(page, entity, identifier) {
  assert(/^[a-z][a-z0-9_]*$/.test(entity));
  assert(/^[0-9]+$/.test(String(identifier)), 'Native row key must be an integer identifier');
  return page.locator(`[data-rnd-business-entity="${entity}"]:visible`)
    .locator(`.vxe-body--row[rowid="${identifier}"]`)
    .getByRole('button', { name: '业务详情', exact: true }).filter({ visible: true }).first();
}

async function createBrowserOwnedRecords(login, create, marker) {
  await login('manager');
  await create('customers');
  await create('requests'); // Independently exercise manager creation.
  await login('employee');
  await create('requests', marker + ' employee');
  await login('manager');
  await create('tasks'); // Link to the fresh employee-created browser request.
}

async function nativeScreenshotState(page) {
  return page.evaluate(() => {
    const visible = element => {
      const box = element.getBoundingClientRect(), style = getComputedStyle(element);
      return box.width > 0 && box.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const fontChecks = new Map(), geometry = [], textParts = [];
    const checkFont = (style, text) => {
      const font = style.font || `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      const loaded = document.fonts.check(font, text);
      fontChecks.set(font, (fontChecks.get(font) ?? true) && loaded);
    };
    const elements = [...document.querySelectorAll('body *')].filter(visible);
    if (elements.length > 6000) throw new Error('Native screenshot layout exceeds the bounded inspection scope');
    for (const element of elements) {
      const box = element.getBoundingClientRect();
      geometry.push([box.x, box.y, box.width, box.height]);
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(element.tagName)) {
        // Input values are painted text even though they are not DOM text nodes.
        // Never inspect a password value; only check its visible masking glyph.
        const text = element.type === 'password' ? '●' : String(element.value || element.getAttribute('placeholder') || '');
        if (text) { checkFont(getComputedStyle(element), text); textParts.push(text); }
      }
      for (const pseudo of ['::before', '::after']) {
        const style = getComputedStyle(element, pseudo), content = style.content;
        if (content && content !== 'none' && content !== 'normal' && style.visibility !== 'hidden') {
          checkFont(style, content.replace(/^['"]|['"]$/g, ''));
        }
      }
    }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const text = node.textContent.trim();
      if (!text || !node.parentElement || !visible(node.parentElement)) continue;
      const range = document.createRange(); range.selectNodeContents(node);
      const box = range.getBoundingClientRect();
      if (!box.width || !box.height) continue;
      if (text.length > 10000 || textParts.length > 3000) throw new Error('Native screenshot text exceeds the bounded inspection scope');
      checkFont(getComputedStyle(node.parentElement), text);
      textParts.push(text);
      geometry.push([box.x, box.y, box.width, box.height]);
    }
    const imagesReady = elements.filter(element => element.tagName === 'IMG')
      .every(element => element.complete && element.naturalWidth > 0);
    const fonts = [...fontChecks].map(([font, loaded]) => ({ font, loaded }));
    return {
      ready: textParts.length > 0 && fonts.length > 0 && fonts.every(font => font.loaded) && imagesReady,
      fonts, images_ready: imagesReady, visible_text_nodes: textParts.length,
      font_faces: [...document.fonts].slice(0, 64).map(font => ({ family: font.family, status: font.status })),
      // Used only in-memory for stability; never put customer text or geometry in diagnostics.
      signature: JSON.stringify([geometry, textParts, fonts, window.scrollX, window.scrollY]),
    };
  });
}

async function captureNativeScreenshot(page, file, noticeTimeout = 6000, timeout = 45000) {
  const deadline = Date.now() + timeout;
  let phase = 'notice-settlement', lastState, session;
  async function bounded(operation, name) {
    let timer;
    try {
      return await Promise.race([operation(), new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`Native screenshot ${name} did not become ready`)), Math.max(1, deadline - Date.now()));
      })]);
    } finally { clearTimeout(timer); }
  }
  // Capturing an open picker must not click, focus, blur, scroll or move the pointer.
  // Dismissing a login notification here used to close the already-visible picker.
  try {
    try {
      await page.locator('.ant-notification-notice:visible, .ant-message-notice:visible').first()
        .waitFor({ state: 'hidden', timeout: Math.min(noticeTimeout, timeout) });
    } catch (error) {
      // Persistent notices are legitimate UI; bounded waiting must never dismiss them.
      if (error.name !== 'TimeoutError') throw error;
    }
    phase = 'visible-fonts-and-layout';
    let previous, stable = 0;
    while (stable < 3) {
      lastState = await bounded(() => nativeScreenshotState(page), phase);
      stable = lastState.ready && lastState.signature === previous ? stable + 1 : 0;
      previous = lastState.signature;
      if (stable < 3) await bounded(() => new Promise(resolve => setTimeout(resolve, 40)), phase);
    }
    // document.fonts.ready also waits for unrelated, nonvisible font loads. Check
    // the actual visible text/pseudo-glyphs above, then capture the unmodified
    // Chromium surface directly. Never toggle Playwright's font-wait test flag.
    phase = 'native-pixel-capture';
    session = await bounded(() => page.context().newCDPSession(page), phase);
    const { cssContentSize: size } = await bounded(() => session.send('Page.getLayoutMetrics'), phase);
    const width = Math.ceil(size.width), height = Math.ceil(size.height);
    assert(width > 0 && height > 0 && width <= 4096 && height <= 8192 && width * height <= 20000000,
      'Native screenshot surface exceeds the bounded capture scope');
    const captured = await bounded(() => session.send('Page.captureScreenshot', {
      format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width, height, scale: 1 },
    }), phase);
    phase = 'post-capture-readiness';
    const after = await bounded(() => nativeScreenshotState(page), phase);
    assert(after.ready && after.signature === lastState.signature,
      'Native screenshot visible fonts or layout changed during capture');
    fs.writeFileSync(file, Buffer.from(captured.data, 'base64'));
  } catch (error) {
    // Fixed, bounded, local evidence. No raw HTML, field values, URLs, credentials,
    // source environment, or pending request headers are retained.
    try {
      fs.writeFileSync(file + '.capture.json', JSON.stringify({ phase,
        visible_text_nodes: lastState?.visible_text_nodes, images_ready: lastState?.images_ready,
        visible_fonts: lastState?.fonts.slice(0, 64).map(font => ({ font: font.font.slice(0, 300), loaded: font.loaded })),
        font_faces: lastState?.font_faces.map(font => ({ family: font.family.slice(0, 100), status: font.status })),
      }, null, 2));
    } catch { /* Preserve the original capture failure. */ }
    throw error;
  } finally {
    if (session) await session.detach().catch(() => {});
  }
}

async function showNativeDashboard(page) {
  const dashboard = page.locator('[data-rnd-business-entity]:visible').getByTestId('business-metrics');
  await dashboard.locator('canvas').first().waitFor({ state: 'visible' });
  // The journey uses reduced motion, so completed setOption calls draw final values.
  // A canvas alone can exist before its native metric options have been rendered.
  await dashboard.locator('[data-rnd-metric-chart]').first().waitFor({ state: 'visible' });
  await dashboard.locator('[data-rnd-metric-chart]:not([data-rnd-metric-rendered="true"])').first()
    .waitFor({ state: 'hidden', timeout: 6000 });
  const heading = dashboard.locator('.ant-card-head');
  // Vben scrolls its native main-content container, not the document. Move the
  // real stats heading into view explicitly, outside the noninteractive capture helper.
  await heading.evaluate(element => element.scrollIntoView({ block: 'start', inline: 'nearest' }));
  const box = await heading.boundingBox();
  assert(box && box.y >= 0 && box.y + box.height <= page.viewportSize().height,
    'Native statistics heading must be in the dashboard screenshot viewport');
}

async function verifyNativeHistorySpacing(page) {
  const panel = page.locator('[data-rnd-business-entity]:visible [data-rnd-business-panel]');
  const first = panel.getByTestId('business-history').locator('.ant-timeline-item-content').first();
  await first.waitFor({ state: 'visible' });
  // Reloading history can change the native scroll position while its rows mount.
  // Read both rectangles synchronously in one browser frame after visibility.
  const geometry = await panel.evaluate(element => new Promise(resolve => requestAnimationFrame(() => {
    const rectangle = node => {
      if (!node) return null;
      const { x, y, width, height } = node.getBoundingClientRect();
      return [x, y, width, height].every(Number.isFinite) ? { x, y, width, height } : null;
    };
    const actions = rectangle(element.querySelector('[data-testid="business-actions"]'));
    const history = rectangle(element.querySelector('[data-testid="business-history"] .ant-timeline-item-content'));
    const gap = actions && history ? history.y - actions.y - actions.height : null;
    resolve({ actions, history, gap: Number.isFinite(gap) ? gap : null });
  })));
  if (!(geometry.actions?.width > 0 && geometry.actions.height > 0
    && geometry.history?.width > 0 && geometry.history.height > 0
    && Number.isFinite(geometry.gap) && geometry.gap >= 8)) {
    assert.fail('Native history must be separated from the bottom of the wrapped action buttons; geometry=' + JSON.stringify(geometry));
  }
}

function rememberCreatedRecord(created, labels, entity, identifier, label) {
  assert.equal(typeof label, 'string');
  assert(label.length > 0, 'A newly created record needs its own visible label');
  created[entity] = String(identifier);
  labels[entity] = label;
}

async function selectNativeOption(page, locator, label, capture, search = false) {
  await locator.click();
  // Ant Select virtualizes long relation lists. Filter the native combobox by
  // its readable label so a newly created record need not be in the initial DOM.
  if (search) await locator.getByRole('combobox').fill(label);
  const option = page.locator('.ant-select-dropdown:visible')
    .locator('.ant-select-item-option').filter({ has: page.getByText(label, { exact: true }) });
  await option.waitFor({ state: 'visible' });
  if (capture) await capture();
  await option.click();
  await locator.locator('.ant-select-selection-item').getByText(label, { exact: true }).waitFor({ state: 'visible' });
}

function verifyNativeRelationPayload(payload, expected) {
  for (const [field, id] of Object.entries(expected)) {
    assert.equal(String(payload[field]), String(id), `Native relation ${field} must submit the browser-owned record ID`);
  }
}

// Drive the original Vben search form and inspect its real paginated request.
// A deliberately incompatible enum must remove the row, even when its name matches.
async function verifyNativeCustomerQuery(page, listRoute, customer, category, capture = async () => {}) {
  assert(category.filterable && category.choices.includes(customer.category));
  const other = category.choices.find(value => value !== customer.category);
  assert(other, 'Customer query journey requires two declared category choices');
  const scopeSelector = '[data-rnd-business-entity="customers"]';
  const scope = page.locator(scopeSelector + ':visible');
  const name = scope.getByTestId('business-field-name');
  const filter = scope.getByTestId('business-field-category');
  if (!(await filter.isVisible())) await scope.getByText('展开', { exact: true }).click();
  const keyword = customer.name.slice(1, -1).toUpperCase();
  assert(keyword && keyword !== customer.name, 'Exercise substring and case-insensitive search');
  async function submit(expectedCategory, expectedIds, reset = false) {
    const button = scope.getByRole('button', { name: reset ? /^重\s*置$/ : /^搜\s*索$/ });
    await button.waitFor({ state: 'visible' });
    const [response] = await Promise.all([
      page.waitForResponse(response => new URL(response.url()).pathname.endsWith(listRoute)
        && response.request().method() === 'GET'),
      button.click(),
    ]);
    const query = new URL(response.url()).searchParams;
    assert.equal(query.get('name') || '', reset ? '' : keyword, 'Native query keyword serialization');
    assert.equal(query.get('category') || '', expectedCategory || '', 'Native query exact category serialization');
    assert.equal(query.get('pageNo'), '1', 'Native query must use pageNo=1');
    assert(/^[1-9][0-9]*$/.test(query.get('pageSize') || ''), 'Native query must serialize pageSize');
    assert(response.ok(), `Native query HTTP ${response.status()}`);
    const body = await response.json();
    assert.equal(body.code, 0, 'Native query application error');
    assert(Array.isArray(body.data.list), 'Native query missing paginated list');
    if (reset) return;
    assert.equal(body.data.total, expectedIds.length, 'Native query total must match exact results');
    assert.deepEqual(body.data.list.map(row => String(row.id)).sort(), expectedIds, 'Native query response IDs');
    await page.waitForFunction(({ scopeSelector, expectedIds }) => {
      const ids = [...new Set([...document.querySelectorAll(scopeSelector + ' .vxe-body--row[rowid]')]
        .filter(row => row.getClientRects().length).map(row => row.getAttribute('rowid')))].sort();
      return JSON.stringify(ids) === JSON.stringify(expectedIds);
    }, { scopeSelector, expectedIds });
    if (expectedIds.length) await scope.getByText(customer.name, { exact: true }).first().waitFor({ state: 'visible' });
  }
  await name.fill(keyword);
  await submit(undefined, [String(customer.id)]);
  async function select(value) {
    await filter.click();
    await page.locator('.ant-select-dropdown:visible').getByText(category.choice_labels?.[value] || value, { exact: true }).last().click();
  }
  await select(customer.category);
  await submit(customer.category, [String(customer.id)]);
  await capture();
  await select(other);
  await submit(other, []);
  await submit(undefined, [], true);
  assert.equal(await name.inputValue(), '', 'Native query reset must clear keyword control');
  assert.equal(await filter.locator('.ant-select-selection-item').count(), 0, 'Native query reset must clear category control');
  return { entity: 'customers', keyword_field: 'name', filter_field: 'category', cases: 3,
    keyword: true, combined_positive: true, combined_mismatch: true, request_values_verified: true,
    response_ids_exact: true, rendered_ids_exact: true, controls_reset: true };
}

async function loginNativeSession(page, base, actor, observe, checked) {
  const tenants = observe('/admin-api/system/tenant/simple-list');
  await page.goto(base + '/#/auth/login', { waitUntil: 'domcontentloaded' });
  const available = await checked(tenants); const tenant = available.find(item => item.id === 1); assert(tenant);
  await page.getByRole('combobox').first().click();
  await page.getByRole('option', { name: tenant.name, exact: true }).click();
  await page.getByPlaceholder(/用户名|账号|username/i).first().fill(actor.username);
  await page.locator('input[type=password]').first().fill(actor.password);
  const response = observe('/admin-api/system/auth/login', 'POST');
  const info = observe('/admin-api/system/auth/get-permission-info');
  await page.getByRole('button', { name: /^登\s*录$|^sign in$|^login$/i }).first().click();
  await checked(response); const identity = await checked(info); assert(identity.menus?.length, 'Native role menu missing');
  // Hash navigation can finish while a dashboard subresource still delays window.load.
  // Successful authentication/permissions and the rendered native shell establish readiness.
  const origin = new URL(base).origin;
  await page.waitForURL(url => url.origin === origin && url.hash.startsWith('#/')
    && !/^#\/(?:auth|login)(?:[/?]|$)/.test(url.hash), { waitUntil: 'domcontentloaded' });
  for (const selector of ['aside:visible', 'header:visible', '#__vben_main_content']) {
    await page.locator(selector).first().waitFor({ state: 'visible' });
  }
  return identity;
}

async function verifyInstalledSidebar(page, identity, actor, plan, targets) {
  const expected = plan.business.permissions.filter(rule => rule.role === actor.replace(/^other_/, '') && rule.actions.includes('read')).map(rule => rule.entity).sort();
  const expectedRoots = actor === 'manager' ? ['/infra', '/system', '/workbench'] : ['/workbench'];
  const roots = identity.menus.map(menu => menu.path).sort();
  assert.deepEqual(roots, expectedRoots, 'Native auth response exposed unavailable/ungranted modules');
  const workbench = identity.menus.find(menu => menu.path === '/workbench');
  assert(workbench && workbench.children?.length, 'Generated Workbench disappeared');
  const byComponent = new Map(targets.map(target => [`infra/wb${target.entity.replaceAll('_', '')}/index`, target.entity]));
  const observed = workbench.children.map(menu => byComponent.get((menu.component || '').replace(/\.vue$/, ''))).sort();
  assert.deepEqual(observed, expected, 'Generated sidebar menu differs from approved read ACL');
  const aside = page.locator('aside:visible').first();
  const firstTarget = targets.find(target => target.entity === expected[0]);
  assert(firstTarget, 'Role needs an approved readable native page');
  if (!await aside.locator(`a[role="menuitem"][href$="${firstTarget.route}"]`).first().isVisible()) {
    await aside.getByText(workbench.name, { exact: true }).first().click();
  }
  for (const entity of expected) {
    const target = targets.find(item => item.entity === entity);
    await aside.locator(`a[role="menuitem"][href$="${target.route}"]`).first().waitFor({ state: 'visible' });
  }
  const sidebar = await aside.evaluate(element => {
    const menu = element.querySelector('ul.vben-menu');
    if (!menu) return null;
    return {
      paths: Array.from(menu.querySelectorAll('a[role="menuitem"][href]')).map(link => {
        const url = new URL(link.getAttribute('href'), location.href);
        return url.origin === location.origin ? url.hash.slice(1).split('?')[0] : url.href;
      }),
      groups: Array.from(menu.children).filter(child => child.matches('li')).map(child => ({
        title: child.querySelector('.vben-sub-menu-content__title')?.textContent?.trim(),
        paths: Array.from(child.querySelectorAll('a[role="menuitem"][href]')).map(link => new URL(link.getAttribute('href'), location.href).hash.slice(1).split('?')[0]),
      })),
    };
  });
  assert(sidebar && sidebar.paths.length, 'Actual Vben menu DOM was not inspected');
  const allowedRoots = new Set([...roots, '/dashboard']); // Pinned native client-only dashboard.
  const invalid = sidebar.paths.filter(value => !allowedRoots.has('/' + value.split('/')[1]));
  assert.equal(invalid.length, 0, 'Rendered sidebar exposed an unavailable module');
  for (const group of sidebar.groups) {
    assert(identity.menus.some(menu => menu.name === group.title)
      || (group.paths.length > 0 && group.paths.every(value => value.startsWith('/dashboard/'))),
    'Rendered top-level sidebar contains an unrecognized module');
  }
  return { actor, expected_roots: expectedRoots, observed_roots: roots, expected_entities: expected,
    observed_entities: observed, rendered_entities: expected, sidebar_link_count: sidebar.paths.length,
    unavailable_count: invalid.length, native_sidebar_inspected: true, generated_links_visible: true };
}

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
  let context, page, currentRole;
  const target = entity => {
    const found = scenario.targets.find(item => item.entity === entity);
    assert(found, `Missing target ${entity}`); return found;
  };
  const observe = (part, method = 'GET', query = {}) => page.waitForResponse(r => new URL(r.url()).pathname.endsWith(part) && r.request().method() === method && Object.entries(query).every(([key, value]) => new URL(r.url()).searchParams.get(key) === String(value)))
    .then(response => ({ response }), error => ({ error }));
  const checked = async promise => {
    const found = await promise; if (found.error) throw found.error;
    assert(found.response.ok(), `Business browser HTTP ${found.response.status()}`);
    const value = await found.response.json(); assert.equal(value.code, 0, `Business application error ${value.code}`); return value.data;
  };
  async function capture(name) {
    await captureNativeScreenshot(page, path.join(reportDir, name));
    report.screenshots.push(name);
  }
  async function login(role) {
    currentRole = role;
    if (context) await context.close();
    context = await browser.newContext({ locale: 'zh-CN', viewport: { width: 1500, height: 1100 }, reducedMotion: 'reduce' });
    page = await context.newPage(); page.setDefaultTimeout(45000);
    page.on('pageerror', error => errors.push(redact(error.message)));
    const identity = await loginNativeSession(page, base, scenario.actors[role], observe, checked);
    const navigation = await verifyInstalledSidebar(page, identity, role, scenario.plan, scenario.targets);
    report.installed_navigation ||= [];
    if (!report.installed_navigation.some(proof => proof.actor === role)) {
      report.installed_navigation.push(navigation);
      // Use an actually authorized business page, not the template's demo
      // overview. openPage requires its real list response and native DOM.
      await openPage(navigation.expected_entities[0]);
      await capture(`${role}-installed-navigation.png`);
    }
    report.checks.push(`${role}:native-login-and-tenant`);
  }
  async function openPage(entity) {
    const current = target(entity);
    await page.goto(base + '/#' + current.route, { waitUntil: 'domcontentloaded' });
    const rows = await refreshNativeList(page, entity, current.list, observe, checked);
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
    return { ...current, rows };
  }
  async function detail(entity, label) {
    const current = await openPage(entity);
    const matches = current.rows.list.filter(record => Object.values(record).includes(label));
    assert.equal(matches.length, 1, 'Exactly one returned native record must match the visible label');
    const identifier = String(matches[0].id);
    const scope = page.locator(`[data-rnd-business-entity="${entity}"]:visible`);
    const row = scope.locator('.vxe-body--row').filter({ has: page.getByText(label, { exact: true }) }).first();
    await row.waitFor({ state: 'visible' });
    await nativeDetailButton(page, entity, identifier).click();
    const panel = scope.locator('[data-rnd-business-panel]');
    await panel.scrollIntoViewIfNeeded();
    // Selecting an already-open record in a kept-alive page is a valid no-op.
    // Its native Refresh button provides a fresh, record-bound response every time.
    const meta = observe('/admin-api/infra/rnd-business/meta', 'GET', { entity, id: identifier });
    await panel.getByRole('button', { name: /^刷\s*新$/ }).click();
    const metadata = await checked(meta);
    assert.equal(String(metadata.record.id), identifier, 'Detail response must match the clicked row');
  }
  async function select(locator, label, screenshot) {
    await selectNativeOption(page, locator, label, screenshot ? () => capture(screenshot) : undefined, Boolean(screenshot));
  }
  const created = {}, labels = {};
  const marker = 'Browser ' + Date.now();
  async function create(entity, labelPrefix = marker) {
    let newLabel = null;
    const expectedRelations = {};
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
        await select(input, labels[relation.target_entity], `${currentRole}-${entity}-${field.name}-relation-picker.png`);
        expectedRelations[field.name.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())] = created[relation.target_entity];
      } else if (field.kind === 'enum') await select(input, field.choice_labels?.[field.choices[0]] || field.choices[0]);
      else if (field.kind === 'boolean') await select(input, '否');
      else if (field.kind === 'integer') await input.fill('1');
      else if (field.kind === 'datetime' || field.kind === 'date') {
        if (field.required) {
          await input.fill(field.kind === 'date' ? '2026-09-30' : '2026-09-30 12:00:00 UTC');
          await input.press('Enter');
        }
      } else {
        const value = (labelPrefix + ' ' + entity + ' ' + field.name).slice(0, field.max_length || 200);
        await input.fill(value); if (newLabel === null) newLabel = value;
      }
    }
    await capture(`${currentRole}-${entity}-filled-native-form.png`);
    const response = observe(current.api + '/create', 'POST');
    await dialog.getByRole('button', { name: /^确\s*认$|^确\s*定$/ }).click();
    const received = await response;
    const identifier = await checked(received);
    verifyNativeRelationPayload(received.response.request().postDataJSON(), expectedRelations);
    rememberCreatedRecord(created, labels, entity, identifier, newLabel);
    await dialog.waitFor({ state: 'hidden' });
    await page.getByText(labels[entity], { exact: true }).first().waitFor({ state: 'visible' });
    await capture(`${currentRole}-${entity}-native-list.png`);
    report.checks.push(`${currentRole}:${entity}:native-form-create`);
  }
  async function action(kind, transition, note) {
    const id = kind === 'assign' ? 'business-assign' : kind === 'add_note' ? 'business-note' : 'business-transition-' + transition;
    await page.getByTestId(id).click();
    const dialog = page.getByRole('dialog').last(); await dialog.waitFor({ state: 'visible' });
    if (kind === 'assign') {
      await dialog.getByTestId('business-assignee').click();
      await page.locator('.ant-select-dropdown:visible [title]').filter({ hasText: scenario.actors.service.username }).last().click();
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
    await createBrowserOwnedRecords(login, create, marker);
    const customerPage = await openPage('customers');
    const category = scenario.plan.entities.find(entity => entity.name === 'customers').fields.find(field => field.name === 'category');
    report.query_journey = await verifyNativeCustomerQuery(page, customerPage.list,
      { id: created.customers, name: labels.customers, category: category.choices[0] }, category,
      () => capture('manager-customers-native-query-positive.png'));
    report.checks.push('manager:customers:native-query-and-exact-filter');
    for (const entity of ['requests', 'tasks']) { await detail(entity, labels[entity]); await action('assign', null, 'Browser assignment'); await verifyNativeHistorySpacing(page); await capture(`${entity}-manager-workflow-controls.png`); }
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
    await capture('manager-vben-business.png');
    await showNativeDashboard(page);
    report.checks.push('manager:real-native-echarts-metrics');
    await capture('manager-business-dashboard.png');
    report.journeys.push({ actor: 'manager', real_create: ['customers', 'requests', 'tasks'], real_assignment: true, native_form_modal: true });
    await login('service');
    for (const entity of ['requests', 'tasks']) {
      await detail(entity, labels[entity]);
      await action('transition', 'start', 'Browser processing');
      await action('add_note', null, 'Browser work recorded');
      assert((await action('transition', 'resolve', 'Browser complete')).resolvedAt, 'Native resolution timestamp missing');
      await page.getByText('Browser work recorded', { exact: true }).first().waitFor({ state: 'visible' });
      await verifyNativeHistorySpacing(page);
      await capture(`${entity}-service-handling-history.png`);
    }
    await capture('service-vben-timeline.png');
    report.journeys.push({ actor: 'service', assigned_records: true, transitions: true, handling_notes: true, timeline: true });
    await login('employee');
    const employeeLabel = labels.requests;
    const notifications = observe('/admin-api/infra/rnd-business/notifications');
    await detail('requests', employeeLabel);
    const notices = await checked(notifications);
    const panel = page.locator('[data-rnd-business-panel]');
    assert.equal(await panel.getByTestId('business-assign').count(), 0, 'Employee must not receive assignment controls');
    assert.equal(await panel.getByTestId('business-transition-start').count(), 0, 'Employee must not receive transition controls');
    const employeeHistory = scenario.plan.business.permissions.some(rule => rule.role === 'employee' && rule.entity === 'requests' && rule.actions.includes('read_history'));
    if (employeeHistory) await verifyNativeHistorySpacing(page);
    else assert.equal(await panel.locator('.ant-timeline-item').count(), 0, 'Unpermitted history must not be displayed');
    await capture(employeeHistory ? 'employee-owned-history.png' : 'employee-owned-record.png');
    await panel.getByText('站内提醒', { exact: true }).waitFor({ state: 'visible' });
    const reminder = notices.find(notice => String(notice.record_id) === String(created.requests) && notice.message.endsWith(' transitioned'));
    assert(reminder, 'Native recipient resolution reminder missing');
    const unread = panel.getByTestId(`business-notice-read-${reminder.id}`);
    await unread.waitFor({ state: 'visible' });
    assert.equal(await unread.count(), 1, 'Fresh recipient reminder must be unread');
    const marked = observe('/admin-api/infra/rnd-business/notifications/read', 'POST');
    await unread.click(); await checked(marked);
    await panel.getByTestId(`business-notice-read-state-${reminder.id}`).waitFor({ state: 'visible' });
    await capture('employee-vben-reminders.png');
    report.checks.push('employee:own_record_history_acl_and_read_reminder');
    report.journeys.push({ actor: 'employee', real_create: ['requests'], own_history: employeeHistory, history_acl: true, recipient_reminders: true, unauthorized_controls_absent: true });
    for (const role of ['other_employee', 'other_service']) {
      await login(role);
      const current = await openPage('requests');
      const rows = current.rows.list;
      assert(Array.isArray(rows), 'Native paginated response missing list');
      assert(!rows.some(row => [String(scenario.records.requests), created.requests].includes(String(row.id))), 'Other native account read a private or assigned request');
      assert.equal(await page.getByText(labels.requests, { exact: true }).count(), 0);
      await capture(role.replaceAll('_', '-') + '-row-isolation.png');
      report.checks.push(`${role}:row_isolation`);
    }
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
module.exports = { main, loginNativeSession, verifyInstalledSidebar, nativeScreenshotState, refreshNativeList, nativeDetailButton, createBrowserOwnedRecords, captureNativeScreenshot, showNativeDashboard, verifyNativeHistorySpacing, rememberCreatedRecord, selectNativeOption, verifyNativeRelationPayload, verifyNativeCustomerQuery };
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
