/* Spec-driven real Chromium acceptance. No network mocks or injected login tokens. */
'use strict';
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const os = require('node:os');
const {isDeepStrictEqual} = require('node:util');

async function captureReloadScreenshot(page, filename) {
  // Diagnostic pixels at the failure instant: do not wait for fonts/load or
  // hide, cancel, animate, or otherwise change any page content.
  const session = await page.context().newCDPSession(page);
  try {
    const {cssVisualViewport:viewport} = await session.send('Page.getLayoutMetrics');
    const result = await session.send('Page.captureScreenshot', {format:'png', captureBeyondViewport:false,
      clip:{x:viewport.pageX, y:viewport.pageY, width:viewport.clientWidth, height:viewport.clientHeight,
        scale:Math.min(1, 1600 / viewport.clientWidth, 1200 / viewport.clientHeight)}});
    fs.writeFileSync(filename, Buffer.from(result.data, 'base64'));
  } finally { await session.detach(); }
}

// Navigation completion is not authentication or rendered-data readiness. Keep
// the real document/resources intact and prove all three independently.
async function reloadAuthenticatedWorkspace(page, {url, spec, records, timeout = 12000,
  diagnosticsDirectory}) {
  const expectedURL = new URL(url);
  const entity = spec.entities[0];
  assert(entity && records.length, 'Reload proof requires actual created records');
  const pending = new Map(), responses = [], events = [];
  let committed = false, phase = 'navigation-and-api';
  const allowedPaths = new Set([expectedURL.pathname, '/schema', '/api/' + entity.name, '/web/app.js', '/web/style.css']);
  const route = value => {
    const target = new URL(value);
    return {same_origin:target.origin === expectedURL.origin,
      path:target.origin === expectedURL.origin && allowedPaths.has(target.pathname) ? target.pathname : '[other-route]'};
  };
  const append = (items, value) => { if (items.length < 64) items.push(value); };
  const failedAt = at => error => { error.reloadPhase = at; throw error; };
  const onRequest = request => {
    if (request.isNavigationRequest() && request.frame() === page.mainFrame()) {
      committed = true;
      append(events, {event:'document-request', route:route(request.url())});
    }
    if (committed) pending.set(request, {route:route(request.url()), type:request.resourceType()});
  };
  const onFinished = request => pending.delete(request);
  const onFailed = request => {
    if (pending.has(request)) append(events, {...pending.get(request), event:'request-failed'});
    pending.delete(request);
  };
  const onResponse = response => {
    if (committed) append(responses, {route:route(response.url()), status:response.status()});
  };
  const onLoad = () => append(events, {event:'load'});
  const sameEndpoint = (response, pathname) => {
    const target = new URL(response.url());
    return committed && pending.has(response.request()) && response.request().frame() === page.mainFrame() &&
      target.origin === expectedURL.origin && target.pathname === pathname &&
      response.request().method() === 'GET';
  };
  page.on('request', onRequest);
  page.on('requestfinished', onFinished);
  page.on('requestfailed', onFailed);
  page.on('response', onResponse);
  page.on('load', onLoad);
  try {
    const schema = page.waitForResponse(r => sameEndpoint(r, '/schema'), {timeout}).then(async r => {
      assert.equal(r.status(), 200, 'Reload authenticated schema denied');
      assert(/^Bearer \S+$/.test(r.request().headers().authorization || ''), 'Missing genuine session');
      const data = await r.json();
      assert(isDeepStrictEqual(data.spec, spec), 'Reload schema differs from approved spec');
      return r.status();
    }).catch(failedAt('authenticated-schema'));
    const listed = page.waitForResponse(r => sameEndpoint(r, '/api/' + entity.name), {timeout}).then(async r => {
      assert.equal(r.status(), 200, 'Reload business list denied');
      assert(/^Bearer \S+$/.test(r.request().headers().authorization || ''), 'Missing genuine session');
      const data = await r.json();
      const ordered = values => [...values].sort((a,b) => a.id.localeCompare(b.id));
      assert(isDeepStrictEqual(ordered(data), ordered(records)), 'Reload lost or exposed different authenticated records');
      return r.status();
    }).catch(failedAt('business-list'));
    const navigated = page.reload({waitUntil:'domcontentloaded', timeout}).then(response => {
      assert(response && response.status() === 200, 'Reload document did not return HTTP 200');
      const current = new URL(page.url());
      assert(current.origin === expectedURL.origin, 'Reload left the product origin');
      assert(current.pathname === expectedURL.pathname, 'Reload left the product page');
      assert(current.search === expectedURL.search, 'Reload changed the product query');
      assert(current.hash === expectedURL.hash, 'Reload changed the product fragment');
      return response.status();
    }).catch(failedAt('document-navigation'));
    const [documentStatus, schemaStatus, listStatus] = await Promise.all([navigated, schema, listed]);
    phase = 'business-dom';
    await page.locator('#workspace').waitFor({state:'visible', timeout});
    assert(await page.locator('#login').isHidden(), 'Reload returned to login');
    await page.waitForFunction(({entity, records}) => {
      const root = document.querySelector('#rows');
      if (!root || root.dataset.loading !== 'false' || root.dataset.entity !== entity.name) return false;
      const wanted = records.map(record => ({id:record.id, values:entity.fields.map(field =>
        record[field.name] == null ? '' : String(field.choice_labels?.[String(record[field.name])] || record[field.name]))}));
      const actual = [...root.querySelectorAll('tr')].map(row => ({id:row.dataset.id,
        values:[...row.querySelectorAll('td')].slice(0,-1).map(cell => cell.textContent)}));
      const ordered = values => values.sort((a,b) => a.id.localeCompare(b.id));
      return JSON.stringify(ordered(actual)) === JSON.stringify(ordered(wanted));
    }, {entity, records}, {timeout});
    phase = 'business-controls';
    assert(isDeepStrictEqual(await page.locator('#entities button').allTextContents(),
      spec.entities.map(item => item.description || item.name)), 'Reload entity permissions/navigation changed');
    assert(isDeepStrictEqual(await page.locator('#columns th').allTextContents(),
      [...entity.fields.map(field => field.label || field.name), '操作']), 'Reload business columns missing');
    assert((await page.locator('#notice').textContent()) === '', 'Reload displayed a business error');
    return {document_status:documentStatus, schema_status:schemaStatus, list_status:listStatus,
      entity:entity.name, exact_record_count:records.length, same_origin:true, authenticated:true,
      wait_until:'domcontentloaded', business_dom:true};
  } catch (error) {
    const evidence = {phase:error.reloadPhase || phase,
      error_name:['TimeoutError', 'AssertionError', 'Error'].includes(error.name) ? error.name : 'Error',
      route:route(page.url()), pending:[...pending.values()].slice(0,32), responses, events};
    try {
      evidence.state = await page.evaluate(entityName => ({readyState:document.readyState,
        loginVisible:!!document.querySelector('#login')?.checkVisibility(),
        workspaceVisible:!!document.querySelector('#workspace')?.checkVisibility(),
        expectedEntity:document.querySelector('#rows')?.dataset.entity === entityName,
        loading:document.querySelector('#rows')?.dataset.loading === 'true',
        rowCount:document.querySelectorAll('#rows tr').length,
        noticePresent:!!document.querySelector('#notice')?.textContent}), entity.name);
    } catch { evidence.state_unavailable = true; }
    try {
      // verify.py deletes its working directory. Retain only bounded, allowlisted
      // state outside it; never save tokens, headers, inputs, raw HTML, or records.
      diagnosticsDirectory ||= fs.mkdtempSync(path.join(os.tmpdir(), 'product-browser-failure-'));
      fs.mkdirSync(diagnosticsDirectory, {recursive:true});
      const prefix = path.join(diagnosticsDirectory, 'reload-' + require('node:crypto').randomUUID());
      evidence.artifact_prefix = prefix;
      if (evidence.route.same_origin && evidence.route.path === expectedURL.pathname) {
        // Local failure pixels can show synthetic acceptance records. They are
        // capped to 1600x1200, never uploaded, and never modify the business page.
        try { await captureReloadScreenshot(page, prefix + '.png'); }
        catch { evidence.screenshot_unavailable = true; }
      } else { evidence.screenshot_skipped = 'not-product-page'; }
      fs.writeFileSync(prefix + '.json', JSON.stringify(evidence, null, 2));
    } catch { evidence.artifact_unavailable = true; }
    error.reloadEvidence = evidence;
    throw error;
  } finally {
    page.off('request', onRequest);
    page.off('requestfinished', onFinished);
    page.off('requestfailed', onFailed);
    page.off('response', onResponse);
    page.off('load', onLoad);
  }
}
async function main() {
  const [input, modulePath, output] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(input, 'utf8'));
  const version = require(modulePath + '/package.json').version;
  assert.equal(version, '1.56.1', 'Pinned Playwright 1.56.1 is required');
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext();
  const page = await context.newPage();
  page.setDefaultTimeout(12000);
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const checks = [];
  const user = 'browser-' + Date.now();
  const password = 'Browser-only-acceptance-314';
  async function auth(name, pass, register) {
    await page.locator('#auth [name=username]').fill(name);
    await page.locator('#auth [name=password]').fill(pass);
    await page.locator(register ? '#register' : '#auth button[type=submit]').click();
  }
  async function choose(index, name) {
    const loaded = page.waitForResponse(r=>r.url().includes('/api/'+name+'?') && r.request().method()==='GET');
    await page.locator('#entities button').nth(index).click();
    assert.equal((await loaded).status(), 200);
  }
  async function rows(expected) {
    // Wait for exact displayed values, not only a count that could match a stale response.
    await page.waitForFunction(wanted => {
      const got = [...document.querySelectorAll('#rows tr')].map(row =>
        [...row.querySelectorAll('td')].slice(0, -1).map(cell => cell.textContent));
      return JSON.stringify(got.sort()) === JSON.stringify(wanted.sort());
    }, expected);
  }
  async function request(path, method = 'GET', body) {
    return page.evaluate(async ({path, method, body}) => {
      const response = await fetch(path, {method, headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + (sessionStorage.getItem('product-token') || '')
      }, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
      return {status: response.status, body: await response.text()};
    }, {path, method, body});
  }
  try {
    await page.goto(cfg.url);
    assert(await page.locator('#login').isVisible());
    assert(await page.locator('#workspace').isHidden());
    await auth(user, password, true);
    await page.locator('#workspace').waitFor({state: 'visible'});
    checks.push('browser-registration');
    const entities = [];
    for (const [index, entity] of cfg.spec.entities.entries()) {
      const fields = entity.fields;
      await choose(index, entity.name);
      await rows([]);
      const rules = (cfg.spec.custom_rules || []).filter(rule => rule.entity === entity.name);
      const samples = rules.length ? rules[0].accept_examples.slice(0, 3) : [0, 1, 2].map(i =>
        Object.fromEntries(fields.map((field, n) => [field.name,
          field.kind === 'text' ? String.fromCharCode(0x4e00+n*3+i).repeat(Math.max(1, Math.min(field.max_length, Math.max(field.min_length || 0, 8+n)))) :
          field.kind === 'integer' ? i+1 : field.kind === 'boolean' ? i%2 === 0 :
          field.kind === 'date' ? `2026-03-${String(8+i).padStart(2,'0')}` : field.choices[i%field.choices.length]
        ])));
      assert(samples.length > 0, 'Need approved browser samples');
      if (!rules.length && fields.some(f=>f.kind==='text')) {
        const boundary = {...samples[0]};
        fields.forEach((field,n)=> { if (field.kind==='text') boundary[field.name] = String.fromCharCode(0x4e00+n*3).repeat(field.max_length); });
        samples.push(boundary);
      }
      const display = values => values.map(s => fields.map(f => s[f.name] == null ? '' : (f.choice_labels?.[String(s[f.name])] || String(s[f.name]))));
      const records = [];
      for (const sample of samples) {
        await page.locator('#create').click();
        for (const field of fields) {
          const control = page.locator(`#record [name="${field.name}"]`);
          if (field.kind === 'text') {
            assert.equal(await control.getAttribute('maxlength'), String(field.max_length));
            assert.equal(await control.getAttribute('minlength'), String(field.min_length || 0));
          }
          const value = sample[field.name] == null ? '' : String(sample[field.name]);
          if (['enum','boolean'].includes(field.kind)) await control.selectOption(value);
          else await control.fill(value);
        }
        const created = page.waitForResponse(r => r.url().endsWith('/api/'+entity.name) && r.request().method() === 'POST');
        await page.locator('#record button[type=submit]').click();
        const response = await created;
        assert.equal(response.status(), 201, await response.text());
        records.push(await response.json());
        await page.locator('#editor').waitFor({state:'hidden'});
        await rows(display(samples.slice(0, records.length)));
      }
      checks.push(`browser-create:${entity.name}`, `browser-field-lengths:${entity.name}`);
      async function filter(values, expected) {
        await page.locator('#reset').click();
        await rows(display(samples));
        assert.deepEqual(await page.locator('#filters').evaluate(f => [...new FormData(f).values()].filter(Boolean)), []);
        for (const [name,value] of Object.entries(values)) {
          const control = page.locator(`#filters [name="${name}"]`);
          if (await control.evaluate(el => el.tagName) === 'SELECT') await control.selectOption(String(value));
          else await control.fill(String(value));
        }
        const loaded = page.waitForResponse(r => r.url().includes('/api/'+entity.name+'?') && r.request().method() === 'GET');
        await page.locator('#filters button[type=submit]').click();
        assert.equal((await loaded).status(), 200);
        await rows(display(expected));
      }
      const conjunction = {};
      for (const field of fields) {
        const value = samples[0][field.name];
        if (field.kind === 'text') {
          const invalid = {...samples[0], [field.name]: 'x'.repeat(field.max_length+1)};
          assert.equal((await request('/api/'+entity.name, 'POST', invalid)).status, 422);
          if (field.min_length > 0) assert.equal((await request('/api/'+entity.name, 'POST', {...samples[0], [field.name]:''})).status, 422);
          checks.push(`browser-overlength-rejected:${entity.name}.${field.name}`);
        }
        if (value == null) {
          assert(!field.searchable && !field.filterable && !field.date_range,
            `No executable non-null approved browser sample for ${entity.name}.${field.name}; add a valid acceptance example`);
          continue;
        }
        if (field.searchable) {
          const searchFields = fields.filter(f => f.searchable);
          await filter({q: String(value)}, samples.filter(s => searchFields.some(f => String(s[f.name] || '').toLowerCase().includes(String(value).toLowerCase()))));
          await filter({q: 'no-match-'+Date.now()}, []);
          conjunction.q = String(value);
          checks.push(`browser-search:${entity.name}.${field.name}`);
        }
        if (field.filterable) {
          await filter({['filter_'+field.name]: value}, samples.filter(s => s[field.name] === value));
          conjunction['filter_'+field.name] = value;
          checks.push(`browser-filter:${entity.name}.${field.name}`);
        }
        if (field.date_range) {
          const dates = samples.map(s => s[field.name]).filter(Boolean).sort();
          const lo = dates[0], hi = dates[Math.min(1, dates.length-1)];
          await filter({['from_'+field.name]: lo, ['to_'+field.name]: hi}, samples.filter(s => s[field.name] >= lo && s[field.name] <= hi));
          await filter({['from_'+field.name]: value, ['to_'+field.name]: value}, samples.filter(s => s[field.name] === value));
          const absent = Array.from({length: dates.length+1}, (_,i)=>`2000-01-${String(i+1).padStart(2,'0')}`).find(day=>!dates.includes(day));
          await filter({['from_'+field.name]: absent, ['to_'+field.name]: absent}, []);
          conjunction['from_'+field.name] = value;
          conjunction['to_'+field.name] = value;
          checks.push(`browser-inclusive-date:${entity.name}.${field.name}`);
        }
      }
      const expected = samples.filter(s => Object.entries(conjunction).every(([key,value]) => {
        if (key === 'q') return fields.filter(f=>f.searchable).some(f=>String(s[f.name] || '').toLowerCase().includes(String(value).toLowerCase()));
        if (key.startsWith('filter_')) return s[key.slice(7)] === value;
        if (key.startsWith('from_')) return s[key.slice(5)] >= value;
        return s[key.slice(3)] <= value;
      }));
      await filter(conjunction, expected);
      await filter({}, samples);
      checks.push(`browser-combined-filter:${entity.name}`);
      // Repeated open/cancel must leave no phantom record or stuck dialog.
      for (let i=0; i<2; i++) {
        await page.locator('#create').click();
        await page.locator('#cancel').click();
        await page.locator('#editor').waitFor({state:'hidden'});
      }
      await rows(display(samples));
      // Exercise the actual edit/save and delete controls, not just HTTP CRUD.
      const firstValues = await page.locator('#rows tr').first().locator('td').evaluateAll(cells=>cells.slice(0,-1).map(c=>c.textContent));
      const firstIndex = display(samples).findIndex(values=>JSON.stringify(values)===JSON.stringify(firstValues));
      assert(firstIndex >= 0);
      const replacement = samples.find(sample=>JSON.stringify(display([sample])[0])!==JSON.stringify(firstValues)) || samples[firstIndex];
      await page.locator('#rows tr').first().getByRole('button', {name:'编辑', exact:true}).click();
      for (const field of fields) {
        const control = page.locator(`#record [name="${field.name}"]`);
        const value = replacement[field.name] == null ? '' : String(replacement[field.name]);
        if (['enum','boolean'].includes(field.kind)) await control.selectOption(value);
        else await control.fill(value);
      }
      const updated = page.waitForResponse(r => r.url().includes('/api/'+entity.name+'/') && r.request().method()==='PUT');
      await page.locator('#record button[type=submit]').click();
      const updateResponse = await updated;
      assert.equal(updateResponse.status(), 200);
      const changed = await updateResponse.json();
      for (const field of fields) assert.equal(changed[field.name], replacement[field.name] ?? null);
      samples[firstIndex] = {...replacement};
      await page.locator('#editor').waitFor({state:'hidden'});
      await rows(display(samples));
      // Test cancellation first; rejection must not dispatch a delete request.
      page.once('dialog', dialog => dialog.dismiss());
      await page.locator('#rows tr').first().getByRole('button', {name:'删除', exact:true}).click();
      await rows(display(samples));
      // The real deletion is exercised on a temporary extra record through the UI.
      await page.locator('#create').click();
      for (const field of fields) {
        const control = page.locator(`#record [name="${field.name}"]`);
        const value = samples[0][field.name] == null ? '' : String(samples[0][field.name]);
        if (['enum','boolean'].includes(field.kind)) await control.selectOption(value);
        else await control.fill(value);
      }
      const extraCreated = page.waitForResponse(r=>r.url().endsWith('/api/'+entity.name) && r.request().method()==='POST');
      await page.locator('#record button[type=submit]').click();
      assert.equal((await extraCreated).status(), 201);
      await page.locator('#editor').waitFor({state:'hidden'});
      await rows(display([...samples, samples[0]]));
      const deleted = page.waitForResponse(r=>r.url().includes('/api/'+entity.name+'/') && r.request().method()==='DELETE');
      page.once('dialog', dialog => dialog.accept());
      await page.locator('#rows tr').first().getByRole('button', {name:'删除', exact:true}).click();
      assert.equal((await deleted).status(), 204);
      const live = await request('/api/'+entity.name);
      assert.equal(live.status, 200);
      const remaining = JSON.parse(live.body);
      assert.equal(remaining.length, samples.length);
      await rows(display(remaining));
      records.splice(0, records.length, ...remaining);
      checks.push(`browser-update-delete:${entity.name}`);
      entities.push({name:entity.name, samples, records});
    }
    await page.locator('#logout').click();
    await page.locator('#login').waitFor({state:'visible'});
    await auth(user, 'wrong-password', false);
    await page.waitForFunction(() => document.querySelector('#notice').textContent.length > 0);
    assert(await page.locator('#workspace').isHidden());
    await auth(user, password, false);
    await page.locator('#workspace').waitFor({state:'visible'});
    const reload = await reloadAuthenticatedWorkspace(page, {url:cfg.url, spec:cfg.spec,
      records:entities[0].records, diagnosticsDirectory:cfg.diagnostics_directory});
    checks.push('browser-login-invalid-password-logout-reload');
    await page.locator('#logout').click();
    await page.locator('#login').waitFor({state:'visible'});
    await auth(user+'-other', password, true);
    await page.locator('#workspace').waitFor({state:'visible'});
    for (const [index, entity] of entities.entries()) {
      await choose(index, entity.name);
      await rows([]);
      const path = '/api/'+entity.name+'/'+entity.records[0].id;
      for (const method of ['GET','PUT','DELETE']) assert.equal((await request(path, method, method==='PUT'?entity.samples[0]:undefined)).status, 404);
      checks.push(`browser-user-isolation:${entity.name}`);
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(output, JSON.stringify({passed:true, engine:'chromium', browser_version:browser.version(), playwright_version:version, real_browser:true,
      entities:entities.map(e=>e.name), checks, errors, reload}, null, 2));
  } finally { await browser.close(); }
}
module.exports = {reloadAuthenticatedWorkspace, captureReloadScreenshot};
if (require.main === module) main().catch(error => {
  if (error.reloadEvidence) {
    const {artifact_prefix, artifact_unavailable, phase, error_name, state, pending} = error.reloadEvidence;
    console.error('Reload failure evidence: ' + JSON.stringify({artifact_prefix, artifact_unavailable, phase, error_name, state, pending}));
  } else { console.error(error.stack); }
  process.exitCode=1;
});
