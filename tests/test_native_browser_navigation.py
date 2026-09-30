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
      </section>`);
    await nativeDetailButton(page, 'requests', '2').click();
    assert.equal(await page.evaluate(() => window.selected), 'correct-record');
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
    assert "panel.getByRole('button', { name: '刷新', exact: true }).click()" in details
    assert "String(metadata.record.id), identifier" in details
