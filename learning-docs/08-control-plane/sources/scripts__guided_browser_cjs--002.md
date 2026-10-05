# scripts/guided_browser.cjs · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__guided_browser_cjs--001.md)

**作用：在真实浏览器操作研发工作台。** 通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。

**对应关系：** ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/guided_browser.cjs`；**本文件共有 2 段**。本段覆盖源文件 L790–L1520。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`25356`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/guided_browser.cjs", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "eba39b807277ef3c2329e228b7779de2d20f77f68638237147b8734f67899063"} -->
````javascript
// scripts/guided_browser.cjs
async function manual(page, cfg, delayedRefresh = false) {
  await connect(page, cfg);
  const runId = await createRun(
    page,
    { ...cfg, requirement: "人工审批验收" },
    "人工审核完整交付验收",
  );
  const refreshes = observeRunRefreshes(page, runId);
  await waitStatus(page, "WAITING_REQUIREMENTS");
  await page
    .getByRole("button", { name: "查看并审核当前版本", exact: true })
    .click();
  let approve = page.getByRole("button", {
    name: "确认需求，生成计划",
    exact: true,
  });
  assert(
    await approve.isDisabled(),
    "Reading acknowledgment must precede approval",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-requirements-desktop.png"),
    fullPage: true,
  });
  const submissions = [];
  page.on("request", (request) => {
    if (request.url().endsWith(`/runs/${runId}/resume`))
      submissions.push(request.postDataJSON());
  });
  await page
    .getByRole("checkbox", { name: "我已阅读并核对当前版本", exact: true })
    .check();
  await approve.dblclick();
  await waitStatus(page, "WAITING_DESIGN");
  assert.equal(
    submissions.length,
    1,
    "Repeated approval clicks consume a gate only once",
  );
  assert.equal(submissions[0].approved, true);
  assert(
    submissions[0].gate_id && submissions[0].version && submissions[0].digest,
  );
  await page
    .getByRole("button", { name: "查看并审核当前版本", exact: true })
    .click();
  approve = page.getByRole("button", {
    name: "确认设计，开始生成",
    exact: true,
  });
  assert(
    await approve.isDisabled(),
    "A new design requires its own fresh review",
  );
  for (const name of ["接口与业务", "数据模型", "任务与覆盖", "架构与模块"])
    await page.getByRole("tab", { name, exact: true }).click();
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-design-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#main-content").focus();
  await page.evaluate(() => window.scrollTo(0, 0));
  await noHorizontalOverflow(page);
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-design-mobile.png"),
    fullPage: false,
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page
    .getByRole("checkbox", { name: "我已阅读并核对当前版本", exact: true })
    .check();
  let releaseRefresh;
  let heldRefresh = false;
  let releasedRefresh = false;
  const held = new Promise((resolve) => {
    releaseRefresh = resolve;
  });
  if (delayedRefresh)
    await page.route(`**/runs/${runId}/report`, async (request) => {
      const status = await page.evaluate(
        () =>
          document.querySelector('[data-testid="run-workspace"]')?.dataset
            .status,
      );
      if (!heldRefresh && status === "RUNNING") {
        heldRefresh = true;
        // Delay one genuine read in an older refresh batch. Never fulfill/mock it.
        await held;
      }
      await request.continue();
    });
  await approve.click();
  await page.getByRole("button", { name: "查看进度", exact: true }).click();
  await page
    .getByRole("heading", { name: "每个阶段，都有可追溯的结果", exact: true })
    .waitFor();
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-progress-desktop.png"),
    fullPage: true,
  });
  await waitStatus(page, "WAITING_DELIVERY", 100000);
  const reviewDeadline = Date.now() + 60000;
  if (delayedRefresh) {
    assert(
      heldRefresh,
      "The regression must delay a real in-flight RUNNING refresh",
    );
    releaseRefresh();
    releasedRefresh = true;
    await page
      .getByText("审核内容已更新，需要重新阅读", { exact: true })
      .waitFor({ timeout: reviewTimeout(reviewDeadline) });
    await page.unroute(`**/runs/${runId}/report`);
  }
  await refreshes.drain(reviewDeadline);
  await waitStatus(page, "WAITING_DELIVERY", reviewTimeout(reviewDeadline));
  await route(page, `run/${runId}/delivery`);
  const download = page.getByRole("button", {
    name: "下载完整交付包",
    exact: true,
  });
  await download.waitFor();
  assert(
    await download.isDisabled(),
    "Download stays locked before human delivery approval",
  );
  const forbidden = await page.request.get(
    cfg.platform + `/runs/${runId}/download`,
    { headers: { Authorization: "Bearer " + cfg.token } },
  );
  assert.equal(forbidden.status(), 409);
  const deliver = page.getByRole("button", {
    name: "确认交付并开放下载",
    exact: true,
  });
  assert(await deliver.isDisabled());
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-delivery-review-desktop.png"),
    fullPage: true,
  });
  const prerequisites = await currentDeliveryFacts(
    page,
    cfg,
    runId,
    reviewDeadline,
  );
  fs.writeFileSync(
    path.join(cfg.reports, "manual-delivery-prerequisites.json"),
    JSON.stringify(prerequisites, null, 2),
  );
  requireDeliveryFacts(prerequisites);
  const providerCallsBeforeRereview = (
    await fixture(page, cfg, reviewTimeout(reviewDeadline))
  ).calls.length;
  const approvalsBeforeRereview = submissions.length;
  if (delayedRefresh)
    await page
      .getByRole("button", { name: "查看最新版本", exact: true })
      .waitFor({ timeout: reviewTimeout(reviewDeadline) });
  const staleRereview = await rereviewDelivery(page, runId, reviewDeadline);
  if (delayedRefresh)
    assert(staleRereview, "The real delayed snapshot must require rereview");
  const acknowledgment = page.getByRole("checkbox", {
    name: "我已阅读本次验收证据与交付等级",
    exact: true,
  });
  assert.equal(
    await acknowledgment.isChecked(),
    false,
    "A fresh delivery requires fresh acknowledgment",
  );
  assert(
    await deliver.isDisabled(),
    "Rereview alone must not approve delivery",
  );
  assert.deepEqual(
    await currentDeliveryFacts(page, cfg, runId, reviewDeadline),
    prerequisites,
    "Rereview must retain the same verified delivery gate",
  );
  assert.equal(
    submissions.length,
    approvalsBeforeRereview,
    "Rereview must not submit a decision",
  );
  assert.equal(
    (await fixture(page, cfg, reviewTimeout(reviewDeadline))).calls.length,
    providerCallsBeforeRereview,
    "Rereview must not call any model provider",
  );
  if (staleRereview)
    await capture(page, {
      animations: "disabled",
      path: path.join(cfg.reports, "workbench-delivery-rereview-desktop.png"),
      fullPage: true,
    });
  await acknowledgment.check({ timeout: reviewTimeout(reviewDeadline) });
  await deliver.click({ timeout: reviewTimeout(reviewDeadline) });
  await waitStatus(page, "READY");
  assert.equal(submissions.length, 3);
  assert.deepEqual(
    {
      gate_id: submissions[2].gate_id,
      version: submissions[2].version,
      digest: submissions[2].digest,
    },
    {
      gate_id: prerequisites.gate_id,
      version: prerequisites.gate_version,
      digest: prerequisites.gate_digest,
    },
    "Approval must bind the exact verified delivery gate",
  );
  assert.equal((await api(page, cfg, `/runs/${runId}`)).auto_mode, false);
  refreshes.close();
  fs.writeFileSync(
    path.join(cfg.reports, "manual.json"),
    JSON.stringify(
      {
        passed: true,
        run_id: runId,
        fresh_review_per_gate: true,
        double_click_single_approval: true,
        design_tabs: true,
        download_locked_until_delivery: true,
        stale_delivery_rereview: staleRereview,
        real_delayed_refresh: delayedRefresh && heldRefresh,
        delayed_refresh_released: delayedRefresh && releasedRefresh,
        verified_delivery_prerequisites: true,
        rereview_did_not_submit: true,
        rereview_did_not_call_provider: true,
        approval_bound_to_delivery_gate: true,
        explicit_approval_count: submissions.length,
      },
      null,
      2,
    ),
  );
}

async function choices(page, cfg) {
  await route(page, "home");
  const runId = await createRun(
    page,
    { ...cfg, requirement: "交互选项验收" },
    "真实选项与即时对话验收",
  );
  await waitStatus(page, "WAITING_CLARIFICATION");
  const submit = page.getByRole("button", {
    name: "提交本组答案",
    exact: true,
  });
  assert(
    await submit.isDisabled(),
    "Required choices cannot be submitted empty",
  );
  await page
    .getByRole("radio", { name: "其他，我来补充", exact: true })
    .check();
  const other = page.getByRole("textbox", {
    name: "这次采用哪种使用方式？的补充回答",
    exact: true,
  });
  await other.fill("切换到固定选项后必须丢弃的隐藏文字");
  await page.getByRole("radio", { name: "个人管理", exact: true }).check();
  assert.equal(await other.count(), 0);
  await page.getByRole("checkbox", { name: "搜索", exact: true }).check();
  await page.getByRole("checkbox", { name: "日期筛选", exact: true }).check();
  const extra = "浏览器确认后的补充只显示一次";
  await page.locator("#question-extra").fill(extra);
  const requests = [];
  const watch = (request) => {
    if (request.url().endsWith(`/runs/${runId}/resume`))
      requests.push(request.postDataJSON());
  };
  page.on("request", watch);
  const accepted = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/runs/${runId}/resume`) &&
      response.status() === 202,
  );
  await submit.dblclick();
  await accepted;
  // The stored human answer must enter the visible transcript immediately, not only on reload.
  await page.locator(".user-message").filter({ hasText: extra }).waitFor();
  assert.equal(
    await page.locator(".user-message").filter({ hasText: extra }).count(),
    1,
  );
  assert.equal(requests.length, 1, "Double-clicking answers submits once");
  assert(
    !JSON.stringify(requests).includes("切换到固定选项后必须丢弃的隐藏文字"),
  );
  assert.deepEqual(
    requests[0].answers.find((answer) => answer.question_id === "audience"),
    { question_id: "audience", option_ids: ["personal"], text: "" },
  );
  assert.deepEqual(
    requests[0].answers.find((answer) => answer.question_id === "filters")
      .option_ids,
    ["search", "date"],
  );
  await waitStatus(page, "WAITING_CLARIFICATION");
  await page.waitForTimeout(1200);
  assert.equal(
    await page
      .getByText("实时连接已中断，正在保留最后一次数据", { exact: true })
      .count(),
    0,
    "Normal idle SSE close is not a network failure",
  );
  await route(page, `run/${runId}/progress`);
  await page
    .getByRole("heading", { name: "每个阶段，都有可追溯的结果", exact: true })
    .waitFor();
  await route(page, `run/${runId}/conversation`);
  await page.locator(".user-message").filter({ hasText: extra }).waitFor();
  assert.equal(
    await page.locator(".user-message").filter({ hasText: extra }).count(),
    1,
  );
  const saved = await api(page, cfg, `/runs/${runId}/transcript`);
  assert.equal(
    saved.messages.filter(
      (message) => message.role === "user" && message.content.includes(extra),
    ).length,
    1,
  );
  assert(!JSON.stringify(saved).includes("切换到固定选项后必须丢弃的隐藏文字"));
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-choices-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#main-content").focus();
  await page.evaluate(() => window.scrollTo(0, 0));
  await noHorizontalOverflow(page);
  await page
    .locator(".question-card")
    .evaluate((element) => element.scrollIntoView({ block: "start" }));
  await page.evaluate(() => window.scrollBy(0, -80));
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-choices-mobile.png"),
    fullPage: false,
  });
  await page
    .getByRole("button", { name: "提交本组答案", exact: true })
    .evaluate((element) => element.scrollIntoView({ block: "center" }));
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-choices-mobile-submit.png"),
    fullPage: false,
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  page.off("request", watch);
  return runId;
}

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
    else if (mode === "manual-stale") await manual(page, cfg, true);
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
    try {
      const runId = await page
        .evaluate(
          () =>
            document
              .querySelector('[data-testid="run-workspace"]')
              ?.getAttribute("data-run-id") || null,
        )
        .catch(() => null);
      if (runId && /^[a-f0-9-]{36}$/.test(runId)) {
        const facts = await currentDeliveryFacts(page, cfg, runId).catch(
          () => ({
            unavailable: true,
          }),
        );
        facts.stale_review_visible = await page
          .getByRole("button", { name: "查看最新版本", exact: true })
          .isVisible();
        fs.writeFileSync(
          path.join(cfg.reports, mode + "-failure-facts.json"),
          JSON.stringify(facts, null, 2),
        );
      }
    } catch {
      // Optional diagnostics cannot replace the original browser failure.
    }
    await capture(page, {
      animations: "disabled",
      path: path.join(cfg.reports, mode + "-failure.png"),
      fullPage: true,
    }).catch(() => {});
    throw error;
  } finally {
    await browser.close();
  }
}
module.exports = {
  deliveryFacts,
  requireDeliveryFacts,
  rereviewDelivery,
  observeRunRefreshes,
};
if (require.main === module)
  main().catch((e) => {
    console.error(e.stack);
    process.exitCode = 1;
  });
````
