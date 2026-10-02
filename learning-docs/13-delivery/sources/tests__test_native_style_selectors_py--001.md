# tests/test_native_style_selectors.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_style_checks_ignore_hidden_header_button_and_id_field`（L9–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44断言`result["returncode"] == 0`。 调用`run_command`、`os.environ.get`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_style_selectors.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L44。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1977`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_style_selectors.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "61098606f1981d1fabb1a16da9ab01b2d046663492efc621e6dfd6cd544deeb9"} -->
````python
# tests/test_native_style_selectors.py
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
````
