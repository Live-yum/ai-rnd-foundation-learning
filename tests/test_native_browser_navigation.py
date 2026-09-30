"""Native cached tabs must be refreshed through the visible UI before list assertions."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from workbench.settings import ROOT


def test_yudao_cached_tab_uses_actual_search_before_verifying_response():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for native browser helper execution")
    result = subprocess.run(
        [
            node,
            "-e",
            r"""
const assert = require('node:assert/strict');
const { refreshNativeList } = require('./scripts/business_yudao_browser.cjs');
(async () => {
  let clicks = 0, resolveResponse, watching = false;
  const search = {
    async waitFor(options) { assert.equal(options.state, 'visible'); },
    async click() {
      assert.equal(watching, true, 'Response observation must precede the UI action');
      clicks++; watching = false;
      resolveResponse({ list: [{ id: String(clicks) }] });
    },
  };
  const page = { locator(selector) {
    assert.equal(selector, '[data-rnd-business-entity=\"requests\"]:visible');
    return { getByRole(role, options) {
      assert.equal(role, 'button'); assert(options.name.test('搜 索')); return search;
    } };
  } };
  const observe = list => {
    assert.equal(list, '/admin-api/infra/wb-requests/page');
    watching = true;
    return new Promise(resolve => { resolveResponse = resolve; });
  };
  // A kept-alive tab has no navigation-triggered network request. Each assertion
  // must be satisfied by a fresh response caused by clicking the actual UI control.
  for (let visit = 1; visit <= 2; visit++) {
    const rows = await refreshNativeList(page, 'requests', '/admin-api/infra/wb-requests/page', observe, async value => value);
    assert.equal(rows.list[0].id, String(visit));
  }
  assert.equal(clicks, 2);
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_yudao_pages_provide_entity_specific_navigation_scope():
    from workbench.business_yudao import _mount_panel

    source = """<script lang="ts" setup></script>
<template><Page auto-content-height><Grid><template #actions="{ row }">
<TableAction :actions="[]" /></template></Grid></Page></template>"""
    for entity in ("customers", "requests", "tasks"):
        mounted = _mount_panel(source, entity)
        assert f'<Page data-rnd-business-entity="{entity}" auto-content-height>' in mounted
        assert mounted.count("data-rnd-business-entity=") == 1
        assert '<Grid class="rnd-business-grid"' in mounted


def test_vxe_fixed_action_table_selects_same_entity_and_record_in_real_browser():
    module = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is mandatory in Actions")
    from workbench.tools import clean_env

    result = subprocess.run(
        [
            shutil.which("node"),
            "-e",
            r"""
const assert = require('node:assert/strict');
const { nativeDetailButton } = require('./scripts/business_yudao_browser.cjs');
const { chromium } = require(process.argv[1]);
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.setContent(`
      <section data-rnd-business-entity="customers"><table><tr class="vxe-body--row" rowid="2"><td><button onclick="window.selected='wrong-entity'">业务详情</button></td></tr></table></section>
      <section data-rnd-business-entity="requests">
        <table><tr class="vxe-body--row" rowid="2"><td>Visible request title</td></tr></table>
        <table class="fixed-right"><tr class="vxe-body--row" rowid="1"><td><button onclick="window.selected='wrong-record'">业务详情</button></td></tr>
          <tr class="vxe-body--row" rowid="2"><td><button onclick="window.selected='correct-record'">业务详情</button></td></tr></table>
        <section data-rnd-business-panel><button onclick="window.refreshed=true"><span>刷 新</span></button></section>
      </section>`);
    await nativeDetailButton(page, 'requests', '2').click();
    assert.equal(await page.evaluate(() => window.selected), 'correct-record');
    await page.locator('[data-rnd-business-entity=\"requests\"] [data-rnd-business-panel]').getByRole('button', { name: /^刷\s*新$/ }).click();
    assert.equal(await page.evaluate(() => window.refreshed), true);
    assert.throws(() => nativeDetailButton(page, 'requests', 'unsafe\"row'), /integer identifier/);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
            module,
        ],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cached_selected_business_detail_requests_an_explicit_refresh():
    source = (ROOT / "scripts/business_yudao_browser.cjs").read_text(encoding="utf-8")
    details = source.split("async function detail(entity, label) {", 1)[1].split(
        "async function select(", 1
    )[0]
    assert "{ entity, id: identifier }" in details
    assert "panel.getByRole('button', { name: /^刷\\s*新$/ }).click()" in details
    assert "String(metadata.record.id), identifier" in details


def test_native_browser_creates_fresh_employee_request_before_recipient_reminder_proof():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for native browser helper execution")
    result = subprocess.run(
        [
            node,
            "-e",
            r"""
const assert = require('node:assert/strict');
const { createBrowserOwnedRecords, rememberCreatedRecord } = require('./scripts/business_yudao_browser.cjs');
(async () => {
  let role, sequence = 70;
  const created = {}, labels = {}, rows = [], calls = [];
  const login = async value => { role = value; calls.push(['login', role]); };
  const create = async (entity, prefix = 'Browser proof') => {
    const row = { id: String(++sequence), entity, creator: role, label: `${prefix} ${entity}` };
    if (entity === 'requests') row.customer_id = created.customers;
    if (entity === 'tasks') row.request_id = created.requests;
    rememberCreatedRecord(created, labels, entity, row.id, row.label);
    rows.push(row); calls.push(['create', role, entity]);
  };
  await createBrowserOwnedRecords(login, create, 'Browser proof');
  assert.deepEqual(calls, [
    ['login','manager'], ['create','manager','customers'], ['create','manager','requests'],
    ['login','employee'], ['create','employee','requests'],
    ['login','manager'], ['create','manager','tasks'],
  ]);
  const own = rows.find(row => row.id === created.requests);
  assert.equal(own.creator, 'employee');
  assert.equal(labels.requests, own.label, 'Fresh employee ID and visible label must remain paired');
  assert.notEqual(own.label, rows.find(row => row.entity === 'requests' && row.creator === 'manager').label);
  assert.equal(rows.find(row => row.entity === 'tasks').request_id, own.id);
  assert.notEqual(own.id, '1', 'Never reuse the HTTP fixture whose reminders were already read');
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_native_screenshot_observes_open_relation_picker_without_dismissing_it(tmp_path):
    module = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is mandatory in Actions")
    from workbench.tools import clean_env

    result = subprocess.run(
        [
            "node",
            "-e",
            r"""
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { chromium } = require(process.argv[1]);
const { captureNativeScreenshot } = require('./scripts/business_yudao_browser.cjs');
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage();
    await page.setContent(`<button id="select">Customer</button>
      <div class="ant-select-dropdown" hidden><button id="option">Readable customer</button></div>
      <button class="ant-notification-notice-close">Close notice</button><input id="selected">
      <script>
      document.querySelector('#select').onclick=()=>document.querySelector('.ant-select-dropdown').hidden=false;
      document.addEventListener('mousedown',e=>{if(!e.target.closest('.ant-select-dropdown')&&e.target.id!=='select')document.querySelector('.ant-select-dropdown').hidden=true;});
      document.querySelector('.ant-notification-notice-close').onclick=e=>e.target.remove();
      document.querySelector('#option').onclick=()=>{document.querySelector('#selected').value='Readable customer';document.querySelector('.ant-select-dropdown').hidden=true;};
      </script>`);
    for (const role of ['manager','employee']) {
      await page.locator('#select').click();
      await page.getByText('Readable customer',{exact:true}).waitFor({state:'visible'});
      const file=path.join(process.argv[2],`${role}-requests-customer_id-relation-picker.png`);
      await captureNativeScreenshot(page,file);
      assert(fs.existsSync(file));
      assert(await page.locator('.ant-select-dropdown').isVisible(), 'Screenshot must not dismiss the open picker');
      assert(await page.locator('.ant-notification-notice-close').isVisible(), 'Screenshot must not click a notice close button');
      await page.getByText('Readable customer',{exact:true}).click();
      assert.equal(await page.locator('#selected').inputValue(),'Readable customer');
    }
    assert.equal(fs.readdirSync(process.argv[2]).filter(n=>n.endsWith('.png')).length,2);
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
""",
            module,
            str(tmp_path),
        ],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
