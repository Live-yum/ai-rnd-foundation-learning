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
      <div class="ant-notification-notice"><button class="ant-notification-notice-close">Close notice</button></div><input id="selected">
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
      await captureNativeScreenshot(page,file,100);
      assert(fs.existsSync(file));
      assert(await page.locator('.ant-select-dropdown').isVisible(), 'Screenshot must not dismiss the open picker');
      assert(await page.locator('.ant-notification-notice-close').isVisible(), 'Screenshot must not click a notice close button');
      await page.getByText('Readable customer',{exact:true}).click();
      assert.equal(await page.locator('#selected').inputValue(),'Readable customer');
    }
    await page.locator('#select').click();
    await page.evaluate(() => {
      const toast = document.createElement('div'); toast.className = 'ant-message-notice'; toast.textContent = 'Saved'; document.body.append(toast);
      setTimeout(() => document.querySelector('.ant-notification-notice').remove(), 120);
      setTimeout(() => toast.remove(), 240);
    });
    await captureNativeScreenshot(page,path.join(process.argv[2],'settled-notices.png'));
    assert.equal(await page.locator('.ant-notification-notice, .ant-message-notice').count(),0,
      'Capture must await both natural notice and toast expiry');
    assert(await page.locator('.ant-select-dropdown').isVisible(), 'Passive waiting must preserve the open picker');
    assert.equal(fs.readdirSync(process.argv[2]).filter(n=>n.endsWith('.png')).length,3);
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


def test_native_dashboard_scrolls_statistics_and_history_clears_wrapped_actions(tmp_path):
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
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.argv[1]);
const { showNativeDashboard, verifyNativeHistorySpacing, captureNativeScreenshot } = require('./scripts/business_yudao_browser.cjs');
(async () => {
  const source = fs.readFileSync('templates/business/yudao/panel.vue','utf8');
  const spacing = source.match(/\.rnd-business-timeline\s*\{[^}]+\}/)[0];
  assert(source.includes('<Timeline class="rnd-business-timeline" data-testid="business-history">'));
  assert(source.includes('<Space wrap data-testid="business-actions">'));
  assert(source.includes('<Card title="业务统计" v-if="metrics.length" data-testid="business-metrics">'));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 1100 } });
    await page.setContent(`<style>
      body { margin:0; } header { height:88px; } main { height:1012px; overflow:auto; }
      .actions { display:inline-flex; flex-wrap:wrap; gap:8px; } button { width:100px; height:32px; }
      .ant-timeline-item-content { position:relative; top:-7px; } ${spacing}
      .ant-card-head { height:56px; } canvas { display:block; width:500px; height:300px; }
      </style><header>Native shell test fixture</header><main>
      <section data-rnd-business-entity="customers" hidden><section data-testid="business-metrics"><div class="ant-card-head">Wrong cached dashboard</div><canvas></canvas></section></section>
      <section data-rnd-business-entity="requests"><section data-rnd-business-panel>
        <div data-testid="business-actions" class="actions"><button>Assign</button><button>Start</button><button>Note</button><button>Audit</button><button>Refresh</button></div>
        <div data-testid="business-history" class="rnd-business-timeline"><div class="ant-timeline-item-content">First history event</div></div>
        <div style="height:1800px">Related record history</div>
        <section data-testid="business-metrics"><div class="ant-card-head">业务统计</div><div>Total requests 4</div><div data-rnd-metric-chart data-rnd-metric-rendered="false"><canvas></canvas></div></section>
        <div style="height:1100px">Reminders</div>
      </section></section></main>`);
    for (const width of [1500,420]) {
      await page.setViewportSize({ width, height:1100 });
      await verifyNativeHistorySpacing(page);
    }
    await page.locator('[data-testid="business-history"]').evaluate(element => element.style.marginTop='0px');
    await assert.rejects(verifyNativeHistorySpacing(page), /separated from the bottom/);
    await page.locator('[data-testid="business-history"]').evaluate(element => element.style.removeProperty('margin-top'));
    await page.setViewportSize({ width:1500, height:1100 });
    await page.evaluate(() => setTimeout(() => {
      document.querySelector('[data-rnd-metric-chart]').setAttribute('data-rnd-metric-rendered','true');
    },120));
    await showNativeDashboard(page);
    assert.equal(await page.locator('[data-rnd-metric-chart]').getAttribute('data-rnd-metric-rendered'),'true');
    assert(await page.locator('main').evaluate(element => element.scrollTop > 1000));
    const heading = await page.locator('[data-rnd-business-entity="requests"] .ant-card-head').boundingBox();
    assert.equal(heading.y,88, 'Statistics must align below the actual native shell');
    await captureNativeScreenshot(page,path.join(process.argv[2],'dashboard.png'));
    assert.equal(await page.locator('[data-rnd-business-entity="requests"] .ant-card-head').textContent(),'业务统计');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
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


def test_native_history_spacing_measures_one_frame_after_delayed_history_mount():
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
const { chromium } = require(process.argv[1]);
const { verifyNativeHistorySpacing } = require('./scripts/business_yudao_browser.cjs');
(async () => {
  const browser = await chromium.launch({ headless:true });
  try {
    const page = await browser.newPage({ viewport:{ width:1500,height:1100 } });
    const setup = async () => page.setContent(`<style>
      body { margin:0; } main { height:1000px; overflow:auto; }
      #before { height:600px; } [data-testid="business-actions"] { height:32px; }
      [data-testid="business-history"] { margin-top:24px; }
      .ant-timeline-item-content { position:relative; top:-7px; height:24px; }
      </style><main><div id="before"></div>
      <section data-rnd-business-entity="requests"><section data-rnd-business-panel>
      <div data-testid="business-actions"><button>Add note</button><button>Refresh</button></div>
      <div data-testid="business-history"></div><div style="height:1400px"></div>
      </section></section></main>`);
    const mountLater = async () => page.evaluate(() => setTimeout(() => {
      document.querySelector('[data-testid="business-history"]').innerHTML='<div class="ant-timeline-item-content">First employee history row</div>';
      document.querySelector('main').scrollTop=200;
    },120));
    await setup();
    // Reproduce the previous real-browser measurement order: old actionbar position,
    // then await delayed history while the native scrolling container moves.
    const actions = await page.getByTestId('business-actions').boundingBox();
    await mountLater();
    const first = page.getByTestId('business-history').locator('.ant-timeline-item-content');
    await first.waitFor({ state:'visible' });
    const history = await first.boundingBox();
    const staleGap = history.y-actions.y-actions.height;
    assert.equal(staleGap,-183, 'Cross-frame rectangles must reproduce the false overlap');
    await verifyNativeHistorySpacing(page); // The actual rendered gap remains 17 px.
    await setup();
    await mountLater();
    await verifyNativeHistorySpacing(page); // Start verification before history exists.
    assert.equal(await page.locator('main').evaluate(element => element.scrollTop),200);
    await page.getByTestId('business-history').evaluate(element => element.style.marginTop='14px');
    await assert.rejects(verifyNativeHistorySpacing(page), /"gap":7/);
    await page.getByTestId('business-history').evaluate(element => element.style.marginTop='15px');
    await verifyNativeHistorySpacing(page); // Exactly 8 px still passes.
    await page.getByTestId('business-history').evaluate(element => element.style.marginTop='0px');
    await assert.rejects(verifyNativeHistorySpacing(page), error => {
      assert.match(error.message,/separated from the bottom/);
      const geometry = JSON.parse(error.message.split('geometry=')[1]);
      assert.equal(geometry.gap,-7, 'A real overlap must still fail the unchanged 8 px threshold');
      assert(Object.values(geometry.actions).every(Number.isFinite));
      assert(Object.values(geometry.history).every(Number.isFinite));
      assert.equal(Object.keys(geometry).sort().join(','),'actions,gap,history');
      return true;
    });
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
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


def test_native_metric_options_respect_reduced_motion_and_show_single_point():
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
const fs = require('node:fs');
const { stripTypeScriptTypes } = require('node:module');
const { chromium } = require(process.argv[1]);
(async () => {
  const source = fs.readFileSync('templates/business/yudao/metric-chart.vue','utf8');
  assert(source.includes('data-rnd-metric-chart :data-rnd-metric-rendered="rendered"'));
  const script = stripTypeScriptTypes(source.split('<script lang="ts" setup>')[1].split('</script>')[0]
    .replace(/^import[^\n]+\n/gm,''));
  const browser = await chromium.launch({ headless:true });
  try {
    const page = await browser.newPage();
    for (const reducedMotion of ['reduce','no-preference']) {
      await page.emulateMedia({ reducedMotion });
      for (const kind of ['time_count','group_count']) {
        // Run the actual component setup/options in Chromium with its real media query.
        // Only the native render promise is controlled to test completion ordering.
        const observed = await page.evaluate(async ({ script,kind }) => {
          const props = { buckets:{ '2026-09-30':4 }, bucketLabels:{}, kind, label:'Request trend' };
          let update;
          const pending=[];
          const setup = new Function('defineProps','ref','watch','nextTick','useEcharts',
            script+'; return { rendered };');
          const state = setup(() => props, value => ({value}), (_,callback) => {update=callback;},
            async () => {}, () => ({ renderEcharts:options => new Promise(resolve => pending.push({options,resolve})) }));
          const before = state.rendered.value;
          const first = update(); await Promise.resolve();
          const second = update(); await Promise.resolve();
          pending[0].resolve({}); await first;
          const afterStale = state.rendered.value;
          pending[1].resolve({}); await second;
          const afterCurrent = state.rendered.value;
          const third = update(); await Promise.resolve();
          pending[2].resolve(null); await third;
          return { before,afterStale,afterCurrent,afterMissing:state.rendered.value,options:pending[1].options };
        },{script,kind});
        assert.equal(observed.before,false);
        assert.equal(observed.afterStale,false, 'A superseded render must not mark a newer metric ready');
        assert.equal(observed.afterCurrent,true);
        assert.equal(observed.afterMissing,false, 'A missing native chart must not count as rendered');
        assert.equal(observed.options.animation,reducedMotion!=='reduce');
        assert.deepEqual(observed.options.series[0].data,[4], 'The native metric data must remain unchanged');
        assert.equal(observed.options.series[0].type,kind==='time_count'?'line':'bar');
        if (kind==='time_count') {
          assert.equal(observed.options.series[0].showSymbol,true);
          assert.equal(observed.options.series[0].symbol,'circle');
          assert.equal(observed.options.series[0].symbolSize,8);
        }
        assert.deepEqual(observed.options.xAxis.data,['2026-09-30']);
      }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
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
