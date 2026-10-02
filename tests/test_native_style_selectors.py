"""Real Chromium regression for upstream hidden controls preceding visible UI."""

import os

from workbench.settings import ROOT
from workbench.tools import run_command


def test_native_style_checks_ignore_hidden_header_button_and_id_field():
    # Exact selectors exported by the production native-browser driver, not copies.
    script = r"""
    const assert = require('node:assert/strict');
    const { nativeComponentSelectors } = require('./scripts/native_browser.cjs');
    const { chromium } = require(process.env.PRODUCT_VERIFY_PLAYWRIGHT);
    (async () => {
      const browser = await chromium.launch({headless:true});
      try {
        const page = await browser.newPage();
        for (const fast of [true, false]) {
          const button = fast ? 'el-button' : 'ant-btn';
          const field = fast ? 'el-input' : 'ant-input';
          await page.setContent(`<button class="${button}" style="display:none">Hidden header</button>
            <button class="${button}">Visible native button</button>
            <div role="dialog"><input class="${field}" name="id" style="display:none">
            <input class="${field}" name="name"></div>`);
          const selectors = nativeComponentSelectors(fast);
          assert.equal(await page.locator(selectors.button).first().innerText(), 'Visible native button');
          assert.equal(await page.getByRole('dialog').locator(selectors.form).first().getAttribute('name'), 'name');
        }
      } finally { await browser.close(); }
    })().catch(e=>{console.error(e);process.exitCode=1});
    """
    result = run_command(
        ["node", "-e", script],
        ROOT,
        60,
        {
            "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get(
                "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
            ),
            "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
        },
    )
    assert result["returncode"] == 0
