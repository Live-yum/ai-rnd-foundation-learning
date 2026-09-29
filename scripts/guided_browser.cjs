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
      await page
        .locator("#requirement")
        .fill(
          "仅本人手动录入资讯。标题250字、正文3000字，发布日期YYYY-MM-DD。搜索标题正文，分类资讯/攻略/大神可选，日期支持单日和包含两端的区间筛选。",
        );
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
      await filter({ filter_category: "攻略" }, 1);
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
