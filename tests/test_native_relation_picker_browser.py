"""Driver regressions for the pinned Ant ApiSelect's mapped, virtualized options.

The DOM fixture uses real Chromium and HTTP, not Playwright route interception.
Source-parity checks bind its labels, filtering and option mapping to the native
adapter. Full native-stack acceptance remains in the Actions browser journeys.
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from workbench.settings import ROOT
from workbench.tools import clean_env

DRIVER = r"""
const assert = require('node:assert/strict'), http = require('node:http');
const [fault, playwrightPath] = process.argv.slice(1);
const { chromium } = require(playwrightPath);
const { selectNativeOption, verifyNativeRelationPayload } = require('./scripts/business_yudao_browser.cjs');
const fresh = { id: '121', title: 'Browser fresh employee requests title', workspace: 'own' };
const foreign = { id: '999', title: 'Foreign workspace private request', workspace: 'foreign' };
const rows = Array.from({ length: 120 }, (_, i) => ({ id: String(i + 1), title: 'Synthetic request ' + (i + 1), workspace: 'own' }));
rows.push(foreign);
let selected, referenceRows, creates = 0;
const wanted = fault === 'foreign-record' ? foreign : fresh;
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  res.setHeader('Content-Type', 'application/json');
  if (url.pathname === '/create-request') {
    creates++; rows.push(fresh); res.end(JSON.stringify({ code: 0, data: fresh.id })); return;
  }
  if (url.pathname === '/references') {
    assert.equal(creates, 1, 'Fetch options only after the fresh record is created');
    assert.equal(url.searchParams.get('entity'), 'requests');
    referenceRows = rows.filter(row => row.workspace === 'own' && !(fault === 'stale-options' && row.id === fresh.id))
      .map(row => row.id !== fresh.id ? row : { ...row,
        id: fault === 'wrong-id' ? '998' : row.id,
        title: fault === 'wrong-label' ? row.title + ' other record' : row.title });
    if (fault === 'duplicate-label') referenceRows.push({ ...fresh, id: '998' });
    res.end(JSON.stringify({ code: 0, data: referenceRows })); return;
  }
  if (url.pathname === '/create-task') {
    let body = ''; req.on('data', chunk => { body += chunk; });
    req.on('end', () => { selected = JSON.parse(body); res.end(JSON.stringify({ code: 0, data: '201' })); }); return;
  }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(`<!doctype html><meta charset="utf-8">
    <button id="new-request">Create fresh request</button><button id="new-task">Create task</button>
    <div data-testid="business-field-request_id" class="ant-select" hidden>
      <input role="combobox"><span class="ant-select-selection-item" hidden></span>
    </div><button id="save">Save task</button>
    <div class="ant-select-dropdown" hidden></div>
    <script>
      const fault = ${JSON.stringify(fault)};
      const field = document.querySelector('.ant-select'), input = field.querySelector('input');
      const dropdown = document.querySelector('.ant-select-dropdown'), selected = field.querySelector('span');
      let options = [], value;
      function render() {
        // ApiComponent maps the declared title/id to label/value; Ant virtualizes
        // the options. Offscreen rows are absent until label filtering reveals them.
        const matches = options.filter(option => String(option[fault === 'value-filter' ? 'value' : 'label']).toLowerCase().includes(input.value.toLowerCase()));
        dropdown.innerHTML = '';
        for (const option of matches.slice(0, 8)) {
          const row = document.createElement('div'); row.className = 'ant-select-item-option';
          const label = document.createElement('div'); label.className = 'ant-select-item-option-content'; label.textContent = option.label;
          row.append(label); row.onclick = event => {
            event.stopPropagation(); value = option.value; selected.textContent = option.label;
            selected.hidden = false; input.value = ''; dropdown.hidden = true;
          }; dropdown.append(row);
        }
      }
      document.querySelector('#new-request').onclick = async () => { await fetch('/create-request', { method: 'POST' }); };
      document.querySelector('#new-task').onclick = async () => {
        const body = await (await fetch('/references?entity=requests')).json();
        options = body.data.map(row => ({ label: row.title, value: row.id })); field.hidden = false;
      };
      field.onclick = () => { dropdown.hidden = false; render(); };
      input.oninput = () => render();
      input.onkeydown = event => { if (event.key === 'Escape') { dropdown.hidden = true; input.value = ''; } };
      document.querySelector('#save').onclick = () => fetch('/create-task', { method: 'POST', body: JSON.stringify({ requestId: value }) });
    </script>`);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage(); page.setDefaultTimeout(1800);
    await page.goto('http://127.0.0.1:' + server.address().port);
    await Promise.all([page.waitForResponse('**/create-request'), page.getByText('Create fresh request', { exact: true }).click()]);
    const [references] = await Promise.all([page.waitForResponse('**/references?entity=requests'), page.getByText('Create task', { exact: true }).click()]);
    assert((await references.json()).data.length >= 120, 'Fresh record follows seeded records');
    assert(!referenceRows.some(row => row.id === foreign.id), 'Foreign-workspace options must remain absent');
    const field = page.getByTestId('business-field-request_id');
    await field.click();
    assert.equal(await page.locator('.ant-select-dropdown').getByText(wanted.title, { exact: true }).count(), 0,
      'The fresh option is outside the initial virtualized DOM');
    // An interrupted, unrelated search must not determine the next selection.
    await field.getByRole('combobox').fill('Synthetic request 117');
    await field.getByRole('combobox').press('Escape');
    let failure, captures = 0;
    try {
      await selectNativeOption(page, field, wanted.title, async () => {
        captures++;
        assert(await page.locator('.ant-select-dropdown:visible').getByText(wanted.title, { exact: true }).isVisible());
      }, true);
      const [response] = await Promise.all([page.waitForResponse('**/create-task'), page.getByText('Save task', { exact: true }).click()]);
      assert.equal((await response.json()).code, 0);
      verifyNativeRelationPayload(response.request().postDataJSON(), { requestId: wanted.id });
    } catch (error) { failure = error; }
    if (fault === 'none') {
      assert.ifError(failure); assert.equal(captures, 1); assert.deepEqual(selected, { requestId: fresh.id });
    } else {
      assert(failure, 'Driver must reject ' + fault);
      assert.match(String(failure.message), fault === 'wrong-id' ? /must submit the browser-owned record ID/
        : fault === 'duplicate-label' ? /strict mode violation/ : /locator.waitFor: Timeout/);
      if (fault !== 'wrong-id') assert.equal(selected, undefined, 'Never submit a stale, ambiguous or inaccessible option');
    }
    console.log('Virtual native relation picker verified: ' + fault);
  } finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
"""


@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "wrong-label",
        "wrong-id",
        "stale-options",
        "foreign-record",
        "duplicate-label",
        "value-filter",
    ],
)
def test_virtualized_relation_picker_selects_only_exact_fresh_record(fault):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is required in Actions")
    result = subprocess.run(
        [shutil.which("node"), "-e", DRIVER, fault, module],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_relation_picker_fixture_matches_pinned_api_select_mapping_and_search():
    with zipfile.ZipFile(ROOT / "templates/vendor/yudao-frontend.zip") as archive:
        component = archive.read(
            "packages/effects/common-ui/src/components/api-component/api-component.vue"
        ).decode("utf-8")
        adapter = archive.read("apps/web-antd/src/adapter/component/index.ts").decode("utf-8")
    assert "label: labelFn ? labelFn(item) : get(item, labelField)" in component
    assert "value: numberToString ? `${value}` : value" in component
    assert (
        "ApiSelect: withDefaultPlaceholder(ApiComponent, 'select', {\n      component: Select,"
        in adapter
    )
    source = (ROOT / "templates/business/yudao/business-form.ts").read_text(encoding="utf-8")
    relation = source.split("if (relation) {", 1)[1].split("} else if", 1)[0]
    assert "labelField: relation.label, valueField: 'id'" in relation
    assert "showSearch: true, optionFilterProp: 'label'" in relation
    assert "virtual: false" not in relation
    assert "requestClient.get('/infra/rnd-business/references'" in relation
    driver = (ROOT / "scripts/business_yudao_browser.cjs").read_text(encoding="utf-8")
    assert (
        "verifyNativeRelationPayload(received.response.request().postDataJSON(), expectedRelations)"
        in driver
    )
