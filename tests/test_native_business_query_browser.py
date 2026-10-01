"""Chromium regression of the native drivers against a local HTTP/DOM fixture.

These are driver/serialization fault tests, not actual native-stack acceptance.
The native Actions jobs run the same helpers inside both generated native apps.
"""

import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from workbench.settings import ROOT
from workbench.tools import clean_env

DRIVER = r"""
const assert = require('node:assert/strict');
const http = require('node:http');
const [template, fault, playwrightPath] = process.argv.slice(1);
const yudao = template === 'yudao';
const { verifyNativeCustomerQuery } = require('./scripts/business_' + template + '_browser.cjs');
const { chromium } = require(playwrightPath);
const customer = { id: '21', name: 'Browser Query Customer 713', category: 'enterprise' };
const category = { filterable: true, choices: ['enterprise', 'personal'], choice_labels: { enterprise: '企业', personal: '个人' } };
const route = yudao ? '/admin-api/infra/wb-customers/page' : '/business/customers/list';
let requests = [];
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  if (url.pathname === route) {
    requests.push(Object.fromEntries(url.searchParams));
    const q = url.searchParams.get(yudao ? 'name' : 'q') || '';
    const filters = yudao ? { category: url.searchParams.get('category') || '' } : JSON.parse(url.searchParams.get('filters') || '{}');
    const rows = [customer, { id: '22', name: 'Unrelated customer', category: 'personal' }].filter(row =>
      (!q || (fault === 'case-sensitive' ? row.name.includes(q) : row.name.toLowerCase().includes(q.toLowerCase())))
      && (!filters.category || fault === 'ignored-and' || row.category === filters.category));
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ code: 0, data: { [yudao ? 'list' : 'items']: rows, total: rows.length } }));
    return;
  }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><meta charset="utf-8">
    <section data-rnd-business-entity="customers">
      <div data-testid="business-search">
        <input data-testid="business-field-name" aria-label="搜索">
        <div data-testid="business-field-category" class="${yudao ? 'ant-select' : 'el-select'}" tabindex="0"><span id="selected" class="is-placeholder">请选择</span></div>
        <button id="search">${yudao ? '搜 索' : '查询'}</button><button id="reset">${yudao ? '重 置' : '重置'}</button>
      </div>
      <div class="fa-table-card"><table><tbody id="rows"></tbody></table></div>
    </section>
    <div id="dropdown" class="ant-select-dropdown" hidden><div role="option" data-value="enterprise">企业</div><div role="option" data-value="personal">个人</div></div>
    <script>
      const yudao = ${JSON.stringify(yudao)}, fault = ${JSON.stringify(fault)}, route = ${JSON.stringify(route)};
      if (fault === 'missing-search-control') document.querySelector('#search').hidden = true;
      let selectedValue = '';
      const keyword = document.querySelector('input'), selected = document.querySelector('#selected');
      document.querySelector('[data-testid="business-field-category"]').onclick = () => document.querySelector('#dropdown').hidden = false;
      document.querySelectorAll('[role="option"]').forEach(option => option.onclick = () => {
        selectedValue = option.dataset.value; selected.textContent = option.textContent;
        selected.className = yudao ? 'ant-select-selection-item' : 'el-select__selected-item';
        document.querySelector('#dropdown').hidden = true;
      });
      async function load(reset = false) {
        let q = reset ? '' : keyword.value, value = reset ? '' : selectedValue;
        if (reset && fault !== 'stale-reset') {
          keyword.value = ''; selectedValue = ''; selected.textContent = '请选择'; selected.className = 'is-placeholder';
        }
        const query = new URLSearchParams();
        if (fault !== 'missing-keyword') query.set(yudao ? 'name' : 'q', q);
        if (fault === 'missing-filter') value = '';
        if (yudao) {
          if (value) query.set('category', value);
          query.set('pageNo', fault === 'wrong-pagination' ? '2' : '1'); query.set('pageSize', '20');
        } else {
          query.set('filters', JSON.stringify(value ? { category: value } : {}));
          query.set('page', fault === 'wrong-pagination' ? '2' : '1');
        }
        const body = await (await fetch(route + '?' + query)).json();
        const rows = fault === 'missing-rendered-row' && q ? [] : body.data[yudao ? 'list' : 'items'];
        document.querySelector('#rows').innerHTML = rows.map(row => '<tr class="' + (yudao ? 'vxe-body--row' : 'el-table__row') + '" rowid="' + row.id + '"><td>' + row.name + '</td><td><button data-testid="related-' + row.id + '">关联记录</button></td></tr>').join('');
      }
      document.querySelector('#search').onclick = () => load();
      document.querySelector('#reset').onclick = () => load(true);
    </script>`);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage(); page.setDefaultTimeout(1800);
    await page.goto('http://127.0.0.1:' + server.address().port);
    let captures = 0;
    const capture = async () => {
      captures++;
      assert(await page.getByText(customer.name, { exact: true }).isVisible());
      assert.equal(requests.length, 2, 'Capture the combined positive query before mismatch and reset');
    };
    let result, failure;
    try {
      result = yudao ? await verifyNativeCustomerQuery(page, route, customer, category, capture)
        : await verifyNativeCustomerQuery(page, customer, category, capture);
    } catch (error) { failure = error; }
    if (fault === 'none') {
      assert.ifError(failure);
      assert.deepEqual(result, { entity: 'customers', keyword_field: 'name', filter_field: 'category', cases: 3,
        keyword: true, combined_positive: true, combined_mismatch: true, request_values_verified: true,
        response_ids_exact: true, rendered_ids_exact: true, controls_reset: true });
      assert.equal(requests.length, 4); assert.equal(captures, 1);
    } else {
      assert(failure, 'Driver must reject the injected query fault: ' + fault);
      const message = String(failure.message);
      const expected = { 'missing-keyword': /keyword serialization/, 'missing-filter': /category serialization/,
        'ignored-and': /total must match/, 'case-sensitive': /total must match/, 'wrong-pagination': /must use page/,
        'missing-rendered-row': /waitForFunction: Timeout/, 'stale-reset': /reset must clear keyword/,
        'missing-search-control': /locator.waitFor: Timeout/ };
      assert.match(message, expected[fault], 'Reject for the intended regression, not an unrelated driver error');
    }
    console.log('Local native-query driver fixture regression verified: ' + template + '/' + fault);
  } finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
"""


@pytest.mark.parametrize("template", ["yudao", "fastapi"])
@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "missing-keyword",
        "missing-filter",
        "ignored-and",
        "case-sensitive",
        "wrong-pagination",
        "missing-rendered-row",
        "stale-reset",
        "missing-search-control",
    ],
)
def test_native_query_driver_rejects_http_and_rendering_faults(template, fault):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is required in Actions")
    result = subprocess.run(
        [shutil.which("node"), "-e", DRIVER, template, fault, module],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("template", ["yudao", "fastapi"])
def test_query_journey_is_in_each_actual_native_driver(template):
    source = (ROOT / f"scripts/business_{template}_browser.cjs").read_text(encoding="utf-8")
    main = source.split("async function main() {", 1)[1]
    assert "report.query_journey = await verifyNativeCustomerQuery(" in main
    assert "report.checks.push('manager:customers:native-query-and-exact-filter')" in main
    if template == "fastapi":
        assert "await capture(page, 'manager-customers-native-query-positive')" in main
        assert "const filename = label + '.png'" in main
    else:
        assert "manager-customers-native-query-positive.png" in main


def test_query_button_fixture_matches_pinned_native_locales():
    with zipfile.ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as archive:
        locale = json.loads(archive.read("frontend/web/src/locales/langs/zh.json"))
        component = archive.read(
            "frontend/web/src/components/forms/fa-search-bar/index.vue"
        ).decode("utf-8")
    assert locale["table"]["searchBar"]["search"] == "查询"
    assert locale["table"]["searchBar"]["reset"] == "重置"
    assert 't("table.searchBar.search")' in component
    with zipfile.ZipFile(ROOT / "templates/vendor/yudao-frontend.zip") as archive:
        component = archive.read("packages/effects/plugins/src/vxe-table/use-vxe-grid.vue").decode(
            "utf-8"
        )
    assert "content: computed(() => $t('common.search'))" in component
    assert "${yudao ? '搜 索' : '查询'}" in DRIVER
