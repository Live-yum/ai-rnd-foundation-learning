// Actual delivered product UI. Inputs are synthetic accounts and independently checked rows.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const [configPath, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));

(async () => {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless: true});
  const errors = [];
  const screenshots = [];
  try {
    for (const [index, view] of cfg.views.entries()) {
      const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
      const page = await context.newPage();
      page.setDefaultTimeout(20000);
      page.on('pageerror', () => errors.push('page_error'));
      await page.goto(cfg.url, {waitUntil: 'domcontentloaded'});
      await page.locator('#auth input[name=username]').fill(cfg.actors[view.actor].username);
      await page.locator('#auth input[name=password]').fill(cfg.password);
      await page.locator('#auth button[type=submit]').click();
      await page.locator('#workspace').waitFor({state: 'visible'});
      const entity = cfg.spec.entities.find(item => item.name === view.entity);
      assert(entity, 'Missing expected entity');
      await page.locator('#entities').getByRole('button', {name: entity.description || entity.name, exact: true}).click();
      await page.waitForFunction(name => {
        const rows = document.querySelector('#rows');
        return rows?.dataset.entity === name && rows.dataset.loading === 'false';
      }, view.entity);
      for (const record of view.rows) {
        const row = page.locator(`#rows tr[data-id="${record.id}"]`);
        await row.waitFor({state: 'visible'});
        for (const [fieldName, raw] of Object.entries(record.values)) {
          const fieldIndex = entity.fields.findIndex(item => item.name === fieldName);
          assert(fieldIndex >= 0, 'Missing expected field');
          const field = entity.fields[fieldIndex];
          const expected = field.choice_labels?.[String(raw)] || String(raw);
          assert.equal((await row.locator('td').nth(fieldIndex).innerText()).trim(), expected);
        }
        if (view.readonly) {
          assert.equal(await row.getByRole('button', {name: '编辑', exact: true}).count(), 0);
          assert.equal(await row.getByRole('button', {name: '归档', exact: true}).count(), 0);
        }
      }
      for (const identity of view.absent || []) {
        assert.equal(await page.locator(`#rows tr[data-id="${identity}"]`).count(), 0);
      }
      if (view.readonly) assert(await page.locator('#create').isHidden());
      const filename = `${cfg.case}-${index + 1}.png`;
      await page.screenshot({path: path.join(cfg.screenshots, filename), fullPage: true});
      screenshots.push(filename);
      await context.close();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(cfg.output, JSON.stringify({passed: true, real_browser: true, views: cfg.views.length, errors, screenshots}));
  } finally {
    await browser.close();
  }
})().catch(() => {
  // No account values, response bodies, or screenshots of a login form in logs.
  console.error('scenario_browser_failed');
  process.exitCode = 1;
});
