"""Native cached tabs must be refreshed through the visible UI before list assertions."""

import shutil
import subprocess

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
  const page = { getByRole(role, options) {
    assert.equal(role, 'button'); assert(options.name.test('搜 索')); return search;
  } };
  const observe = list => {
    assert.equal(list, '/admin-api/infra/wb-requests/page');
    watching = true;
    return new Promise(resolve => { resolveResponse = resolve; });
  };
  // A kept-alive tab has no navigation-triggered network request. Each assertion
  // must be satisfied by a fresh response caused by clicking the actual UI control.
  for (let visit = 1; visit <= 2; visit++) {
    const rows = await refreshNativeList(page, '/admin-api/infra/wb-requests/page', observe, async value => value);
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
