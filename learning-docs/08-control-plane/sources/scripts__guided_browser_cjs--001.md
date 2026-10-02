# scripts/guided_browser.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：在真实浏览器操作研发工作台。** 通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。

**对应关系：** ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/guided_browser.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L165。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6398`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/guided_browser.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ef6fba4efcbc3c69be53ddb3b79f218a6bcee17613d24db3cbe4c954f6e584b6"} -->
````javascript
// scripts/guided_browser.cjs
// No mocked page routes, injected login tokens, or preapproved workflow gates.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
async function main() {
  const [mode, file, modulePath] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(file, "utf8"));
  const { chromium } = require(modulePath);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
    locale: "zh-CN",
  });
  page.setDefaultTimeout(60000);
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  try {
    if (mode === "workbench") {
      await page.goto(cfg.platform);
      assert(await page.locator("#request").isHidden());
      await page.locator("#token").fill(cfg.token);
      await page.locator("#connect button").click();
      await page.locator("#template").selectOption("python-basic");
      await page.locator("#frontend").selectOption("simple-admin");
      await page.locator("#database").selectOption("sqlite");
      assert(await page.locator("#request").isHidden());
      await page.locator("#choose").click();
      await page.locator("#project-title").fill("游戏资讯助手");
      await page.locator("#requirement").fill(cfg.requirement);
      await page.locator("#new-run button").click();
      await page.waitForFunction(
        () =>
          document.querySelector("#status").textContent ===
          "状态：WAITING_CLARIFICATION",
      );
      const runId = (await page.locator("#run-title").innerText())
        .split(" ")
        .at(-1);
      await page.locator("#smart").click();
      await page.waitForFunction(
        () => document.querySelector("#status").textContent === "状态：READY",
        null,
        { timeout: 100000 },
      );
      assert(
        (await page.locator("#auto-state").innerText()).includes("已启用"),
      );
      assert(await page.locator("#answer-form").isHidden());
      const downloadPromise = page.waitForEvent("download");
      await page.locator("#download").click();
      await (await downloadPromise).saveAs(cfg.output);
      await page.screenshot({
        path: path.join(cfg.reports, "workbench-ready.png"),
        fullPage: true,
      });
      fs.writeFileSync(
        path.join(cfg.reports, "workbench.json"),
        JSON.stringify(
          {
            passed: true,
            run_id: runId,
            selection_before_requirement: true,
            smart_clicked: true,
            subsequent_manual_actions: 0,
            errors,
          },
          null,
          2,
        ),
      );
    } else {
      await page.goto(cfg.product);
      await page.locator("#auth input[name=username]").fill("browser-user");
      await page
        .locator("#auth input[name=password]")
        .fill("browser-only-password");
      await page.locator("#register").click();
      await page.locator("#workspace").waitFor({ state: "visible" });
      const create = async (title, body, date, category) => {
        await page.locator("#create").click();
        await page.locator("#record [name=title]").fill(title);
        await page.locator("#record [name=body]").fill(body);
        await page.locator("#record [name=published_on]").fill(date);
        await page.locator("#record [name=category]").selectOption(category);
        await page.locator("#record button[type=submit]").click();
        await page.locator("#editor").waitFor({ state: "hidden" });
      };
      await create("泰拉瑞亚资讯", "测试矿石内容", "2026-03-08", "资讯");
      await create("攻略内容", "泰拉瑞亚建造教程", "2026-03-09", "攻略");
      await create("大神经验", "其他内容", "2026-03-10", "大神");
      await page.waitForFunction(
        () => document.querySelectorAll("#rows tr").length === 3,
      );
      async function filter(values, count) {
        await page.locator("#reset").click();
        assert.deepEqual(await page.locator("#filters").evaluate(form => [...new FormData(form).values()].filter(Boolean)), [], "Clear filters must clear all prior conditions");
        for (const [key, value] of Object.entries(values)) {
          const f = page.locator(`#filters [name=${key}]`);
          if (key === "filter_category") await f.selectOption(value);
          else await f.fill(value);
        }
        await page.locator("#filters button[type=submit]").click();
        await page.waitForFunction(
          (n) => document.querySelectorAll("#rows tr").length === n,
          count,
        );
      }
      await filter({ q: "泰拉瑞亚" }, 2);
      await filter({ q: "矿石" }, 1);
      await filter({ filter_category: "攻略" }, 1);
      await filter({ q: "泰拉瑞亚", filter_category: "攻略", from_published_on: "2026-03-09", to_published_on: "2026-03-09" }, 1);
      await filter({ filter_published_on: "2026-03-08" }, 1);
      await filter(
        { from_published_on: "2026-03-08", to_published_on: "2026-03-09" },
        2,
      );
      await page.screenshot({
        path: path.join(cfg.reports, "news-date-range.png"),
        fullPage: true,
      });
      await page.locator("#create").click();
      assert.equal(
        await page.locator("#record [name=title]").getAttribute("maxlength"),
        "250",
      );
      assert.equal(
        await page.locator("#record [name=body]").getAttribute("maxlength"),
        "3000",
      );
      await page.locator("#cancel").click();
      fs.writeFileSync(
        path.join(cfg.reports, "product.json"),
        JSON.stringify(
          {
            passed: true,
            register_login: true,
            created_records: 3,
            title_and_body_search: true,
            category_filter: true,
            combined_search_category_date_filter: true,
            exact_date: true,
            inclusive_date_range: true,
            field_lengths: true,
            errors,
          },
          null,
          2,
        ),
      );
    }
    assert.equal(errors.length, 0, "Browser errors");
  } catch (error) {
    await page.screenshot({
      path: path.join(cfg.reports, mode + "-failure.png"),
      fullPage: true,
    });
    throw error;
  } finally {
    await browser.close();
  }
}
main().catch((e) => {
  console.error(e.stack);
  process.exitCode = 1;
});
````
