# scripts/template_acceptance_browser.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.template_acceptance_browser.；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/template_acceptance_browser.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L64。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3272`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/template_acceptance_browser.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "338b1fc03ac095b40f45b6710084523a21adda07e33c9052d5839ef736952cd0"} -->
````javascript
// scripts/template_acceptance_browser.cjs
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
````
