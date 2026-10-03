# scripts/guided_browser.cjs · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__guided_browser_cjs--001.md)

**作用：在真实浏览器操作研发工作台。** 通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。

**对应关系：** ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/guided_browser.cjs`；**本文件共有 2 段**。本段覆盖源文件 L873–L1203。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11763`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/guided_browser.cjs", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "fa0c3b9678a718fbffd2ef1443490812aedbc99e16d816ca62cabb79dc78451d"} -->
````javascript
// scripts/guided_browser.cjs
async function navigationDialogGuards(page, cfg, runId) {
  const completed = (await api(page, cfg, "/runs")).find(
    (run) => run.status === "READY" && run.auto_mode,
  );
  assert(completed);
  const mutations = [];
  const watch = (request) => {
    if (
      request.method() === "POST" &&
      /\/(resume|automation)$/.test(request.url())
    )
      mutations.push(request.url());
  };
  page.on("request", watch);
  for (const action of [
    { open: "了解并开启智能推荐", confirm: "确认授权" },
    { open: "拒绝并结束本轮", confirm: "确认拒绝" },
  ]) {
    await route(page, `run/${completed.id}/conversation`);
    await waitStatus(page, "READY");
    await route(page, `run/${runId}/conversation`);
    await waitStatus(page, "WAITING_CLARIFICATION");
    await page.getByRole("button", { name: action.open, exact: true }).click();
    await page.getByRole("dialog").waitFor();
    await page.goBack();
    await waitStatus(page, "READY");
    // Navigation cancels the old confirmation rather than retargeting it.
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await page.waitForTimeout(300);
    assert.deepEqual(
      mutations,
      [],
      "A navigation-invalidated confirmation cannot mutate either run",
    );
    const original = await api(page, cfg, `/runs/${runId}`);
    assert.equal(original.auto_mode, false);
    assert.equal(original.status, "WAITING_CLARIFICATION");
    assert.equal(
      (await api(page, cfg, `/runs/${completed.id}`)).auto_mode,
      true,
    );
  }
  page.off("request", watch);
}

async function rejectWithoutModel(page, cfg, runId) {
  const before = (await fixture(page, cfg)).calls.length;
  await page.getByRole("tab", { name: /^默认连接/ }).click();
  await antSelect(page, "#key-action", "清除此处密钥");
  const saved = page.waitForResponse(
    (response) =>
      response.url().endsWith("/settings/models") &&
      response.request().method() === "PATCH" &&
      response.status() === 200,
  );
  await page.getByRole("button", { name: "保存配置", exact: true }).click();
  await saved;
  await page.getByText(/^当前配置版本 /).waitFor();
  assert.equal((await api(page, cfg, "/settings/models")).ready, false);
  await route(page, `run/${runId}/conversation`);
  await waitStatus(page, "WAITING_CLARIFICATION");
  await page.getByText("模型配置尚未就绪", { exact: true }).waitFor();
  assert(
    await page
      .getByRole("button", { name: "提交本组答案", exact: true })
      .isDisabled(),
  );
  await page
    .getByRole("button", { name: "拒绝并结束本轮", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "确认拒绝", exact: true })
    .click();
  await waitStatus(page, "REJECTED");
  assert.equal(
    (await fixture(page, cfg)).calls.length,
    before,
    "Rejecting remains safe and free when model configuration is unavailable",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-rejected-without-model.png"),
    fullPage: true,
  });
}

async function interaction(page, cfg, errors) {
  await connect(page, cfg);
  const runId = await createRun(page, cfg, "并发关卡与键盘验收");
  await waitStatus(page, "WAITING_CLARIFICATION");
  const before = await api(page, cfg, `/runs/${runId}`);
  const oldGate = before.pending;
  await page
    .getByRole("textbox", { name: "需求回答", exact: true })
    .fill("旧页面上的回答不应误提交到新版本");
  let intercepted = 0;
  // Delay, never fulfill/mock, one genuine request. Another real client wins the race.
  await page.route(`**/runs/${runId}/resume`, async (route) => {
    if (intercepted++ === 0) {
      const response = await page.request.post(
        cfg.platform + `/runs/${runId}/resume`,
        {
          headers: {
            Authorization: "Bearer " + cfg.token,
            "Idempotency-Key": "fixture-concurrent-" + runId,
          },
          data: {
            gate_id: oldGate.gate_id,
            version: oldGate.version,
            digest: oldGate.digest,
            action: "answer",
            text: "另一个窗口确认采用个人管理页面",
          },
        },
      );
      assert.equal(response.status(), 202);
      for (let attempt = 0; attempt < 100; attempt++) {
        const current = await api(page, cfg, `/runs/${runId}`);
        if (current.pending && current.pending.gate_id !== oldGate.gate_id)
          break;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      const newer = await api(page, cfg, `/runs/${runId}`);
      assert(
        newer.pending && newer.pending.gate_id !== oldGate.gate_id,
        "Concurrent answer must produce a genuine newer gate",
      );
    }
    await route.continue();
  });
  const staleResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/runs/${runId}/resume`) &&
      response.status() === 409,
  );
  const submitAnswer = page.getByRole("button", {
    name: "提交本组答案",
    exact: true,
  });
  await submitAnswer.focus();
  await submitAnswer.press("Enter");
  await staleResponse;
  await page
    .getByText("审核内容已更新，需要重新阅读", { exact: true })
    .waitFor();
  assert(
    await page
      .getByRole("button", { name: "提交本组答案", exact: true })
      .isDisabled(),
  );
  await page.waitForTimeout(1200);
  assert.equal(intercepted, 1, "409 must not auto-retry stale human decisions");
  const transcript = await api(page, cfg, `/runs/${runId}/transcript`);
  assert(
    !JSON.stringify(transcript).includes("旧页面上的回答不应误提交到新版本"),
  );
  await page.getByRole("button", { name: "查看最新版本", exact: true }).click();
  await page
    .getByRole("heading", { name: "一起把需求说清楚", exact: true })
    .waitFor();
  assert.equal(
    await page
      .getByRole("textbox", { name: "需求回答", exact: true })
      .inputValue(),
    "",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-rereview-desktop.png"),
    fullPage: true,
  });
  await page.unroute(`**/runs/${runId}/resume`);
  await navigationDialogGuards(page, cfg, runId);
  const choiceRun = await choices(page, cfg);
  await checkSettings(page, cfg, errors);
  await rejectWithoutModel(page, cfg, choiceRun);
  fs.writeFileSync(
    path.join(cfg.reports, "interaction.json"),
    JSON.stringify(
      {
        passed: true,
        real_stale_409: true,
        rereview_required: true,
        no_automatic_retry: true,
        saved_keys_not_returned: true,
        changed_url_requires_separate_key: true,
        no_paid_connection_check: true,
        visible_user_answer_exactly_once: true,
        other_answer_discarded_on_fixed_choice: true,
        idle_is_not_disconnect: true,
        navigation_invalidates_confirmation: true,
        reject_without_model_config: true,
        errors,
      },
      null,
      2,
    ),
  );
}

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
    if (mode === "workbench") await workbench(page, cfg, errors);
    else if (mode === "recovery") await recovery(page, cfg);
    else if (mode === "manual") await manual(page, cfg);
    else if (mode === "interaction") await interaction(page, cfg, errors);
    else {
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
        assert.deepEqual(
          await page
            .locator("#filters")
            .evaluate((form) =>
              [...new FormData(form).values()].filter(Boolean),
            ),
          [],
          "Clear filters must clear all prior conditions",
        );
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
      await filter(
        {
          q: "泰拉瑞亚",
          filter_category: "攻略",
          from_published_on: "2026-03-09",
          to_published_on: "2026-03-09",
        },
        1,
      );
      await filter({ filter_published_on: "2026-03-08" }, 1);
      await filter(
        { from_published_on: "2026-03-08", to_published_on: "2026-03-09" },
        2,
      );
      await capture(page, {
        animations: "disabled",
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
    await capture(page, {
      animations: "disabled",
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
