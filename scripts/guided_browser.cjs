// Real local application and provider HTTP. No fulfilled page routes or preapproved gates.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");

async function capture(page, options) {
  if (options.fullPage) {
    const main = page.locator("#main-content");
    if (await main.count()) await main.focus();
    await page.evaluate(() => window.scrollTo(0, 0));
  }
  await page.evaluate(
    () =>
      new Promise((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(resolve)),
      ),
  );
  await page.screenshot(options);
}

async function antSelect(page, id, label) {
  await page
    .locator(".ant-select")
    .filter({ has: page.locator(id) })
    .click();
  await page
    .locator(".ant-select-dropdown:visible .ant-select-item-option")
    .filter({ hasText: label })
    .first()
    .click();
}
async function connect(page, cfg) {
  await page.goto(cfg.platform);
  const connection = page.getByRole("button", {
    name: "连接本地服务",
    exact: true,
  });
  await connection.focus();
  await connection.press("Enter");
  await page.getByRole("dialog").waitFor();
  await page.locator("#access-token").focus();
  await page.keyboard.press("Escape");
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page
    .waitForFunction(
      () => document.activeElement?.textContent?.trim() === "连接本地服务",
      null,
      { timeout: 3000 },
    )
    .catch(async (error) => {
      throw new Error(
        error.message +
          " active=" +
          JSON.stringify(
            await page.evaluate(() => ({
              tag: document.activeElement?.tagName,
              id: document.activeElement?.id,
              text: document.activeElement?.textContent?.slice(0, 180),
            })),
          ),
      );
    });
  assert(
    await connection.evaluate((element) => element === document.activeElement),
    "Closing connection dialog restores keyboard focus",
  );
  await connection.press("Enter");
  await page.locator("#access-token").fill(cfg.token);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "连接工作空间", exact: true })
    .click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page
    .getByRole("button", { name: "锁定工作空间", exact: true })
    .waitFor();
  await page.getByText("本地服务已连接", { exact: true }).waitFor();
}
async function route(page, hash) {
  await page.evaluate((hash) => {
    window.location.hash = "/" + hash;
  }, hash);
}
async function waitStatus(page, status, timeout = 60000) {
  await page.waitForFunction(
    (expected) => {
      const root = document.querySelector('[data-testid="run-workspace"]');
      return (
        root &&
        [expected, "FAILED", "PAUSED_LIMIT", "REJECTED"].includes(
          root.dataset.status,
        )
      );
    },
    status,
    { timeout },
  );
  assert.equal(
    await page
      .locator('[data-testid="run-workspace"]')
      .getAttribute("data-status"),
    status,
    await page.locator("main").innerText(),
  );
}
async function api(page, cfg, endpoint, options = {}) {
  const response = await page.request.fetch(cfg.platform + endpoint, {
    ...options,
    headers: {
      Authorization: "Bearer " + cfg.token,
      "Idempotency-Key": crypto.randomUUID(),
      ...(options.headers || {}),
    },
  });
  assert(
    response.ok(),
    `${endpoint}: ${response.status()} ${await response.text()}`,
  );
  return response.json();
}
async function fixture(page, cfg) {
  const response = await page.request.get(cfg.fixture + "/fixture/status");
  assert(response.ok());
  return response.json();
}
async function noHorizontalOverflow(page) {
  const layout = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: window.innerWidth,
    overflowing: [...document.querySelectorAll("body *")]
      .filter((element) => {
        const box = element.getBoundingClientRect();
        return (
          box.width &&
          box.right > window.innerWidth + 1 &&
          getComputedStyle(element).visibility !== "hidden"
        );
      })
      .slice(0, 8)
      .map((element) => ({
        tag: element.tagName,
        class: element.className,
        width: element.getBoundingClientRect().width,
      })),
  }));
  assert(
    layout.documentWidth <= layout.viewportWidth + 1,
    "No page-level horizontal overflow: " + JSON.stringify(layout),
  );
}
async function createRun(page, cfg, title, { ime = false } = {}) {
  console.log("Create run: drafting " + title);
  const composer = page.getByRole("textbox", { name: "描述你的产品需求" });
  await composer.fill(cfg.requirement);
  if (ime) {
    await composer.dispatchEvent("compositionstart");
    await composer.dispatchEvent("keydown", {
      key: "Enter",
      code: "Enter",
      keyCode: 229,
      isComposing: true,
      bubbles: true,
    });
    assert.equal(
      await page.getByRole("dialog").count(),
      0,
      "IME Enter must not send or open selection",
    );
    await composer.dispatchEvent("compositionend");
    await composer.press("Shift+Enter");
    assert(
      (await composer.inputValue()).includes("\n"),
      "Shift+Enter keeps editing a multiline draft",
    );
    await composer.fill(cfg.requirement);
  }
  await composer.press("Enter");
  const modal = page.getByRole("dialog");
  await modal.waitFor();
  console.log("Create run: selecting stack");
  // The backend receives neither project nor run before a deliberate stack confirmation.
  const before = await api(page, cfg, "/runs");
  await modal.locator("#new-project-title").fill(title);
  await antSelect(page, "#template-selection", "FastAPI + 轻量管理页面");
  console.log("Create run: selected backend");
  await antSelect(page, "#frontend-selection", "simple-admin");
  console.log("Create run: selected frontend");
  await antSelect(page, "#database-selection", "sqlite");
  console.log("Create run: selected database");
  assert.equal((await api(page, cfg, "/runs")).length, before.length);
  // True repeated browser click, not a direct API shortcut.
  await modal
    .getByRole("button", { name: "确认选型并开始", exact: true })
    .dblclick();
  console.log("Create run: confirmed");
  await page.locator('[data-testid="run-workspace"]').waitFor();
  const id = await page
    .locator('[data-testid="run-workspace"]')
    .getAttribute("data-run-id");
  assert(id);
  const after = await api(page, cfg, "/runs");
  assert.equal(
    after.length,
    before.length + 1,
    "Double click creates exactly one run",
  );
  return id;
}
async function checkSettings(page, cfg, errors) {
  const callsBefore = (await fixture(page, cfg)).calls.length;
  const responses = [];
  const watch = async (response) => {
    if (response.url().includes("/settings/models"))
      responses.push(await response.text().catch(() => ""));
  };
  page.on("response", watch);
  await route(page, "settings");
  await page.getByRole("heading", { name: "模型与服务，一处配置" }).waitFor();
  const connectionTest = page.getByRole("button", { name: "测试连接", exact: true });
  assert(await connectionTest.isEnabled(), "Saved configuration exposes the explicit probe");
  await connectionTest.click();
  const probeConfirmation = page.getByRole("dialog");
  await probeConfirmation.getByText("发起一次真实模型连接测试？", { exact: true }).waitFor();
  assert.equal((await fixture(page, cfg)).calls.length, callsBefore,
    "Opening the cost confirmation must not call a model");
  await probeConfirmation.getByRole("button", { name: /^取\s*消$/ }).click();
  await probeConfirmation.waitFor({ state: "hidden" });
  assert.equal((await fixture(page, cfg)).calls.length, callsBefore,
    "Cancelling a connection test must not call a model");
  await page.getByRole("tab", { name: /^计划阶段/ }).click();
  await page.locator("#model-url").fill(cfg.fixture + "/another-v1");
  const save = page.getByRole("button", { name: "保存配置", exact: true });
  assert(
    await save.isDisabled(),
    "Changing a provider URL cannot reuse its old key",
  );
  await antSelect(page, "#key-action", "替换为新密钥");
  assert(await save.isDisabled(), "A replacement key cannot be blank");
  await page.locator("#model-key").fill("explicit-ci-only");
  const rejectedOldKey = page.waitForResponse(
    (response) =>
      response.url().endsWith("/settings/models") && response.status() === 422,
  );
  await save.click();
  await rejectedOldKey;
  await page
    .getByText("该 API Key 已用于其他地址；新地址必须使用独立密钥", {
      exact: true,
    })
    .waitFor();
  assert.equal(
    await page.locator("#model-key").inputValue(),
    "",
    "Failed saves also clear key input",
  );
  const secret = "fixture-settings-only-separate-key";
  await page.locator("#model-key").fill(secret);
  assert.equal(
    await page.locator("#model-key").getAttribute("type"),
    "password",
  );
  await save.click();
  await page
    .getByText("配置已保存 · 仅完成格式校验 · 未测试连接", { exact: true })
    .waitFor();
  await page.getByText(/^当前配置版本 /).waitFor();
  assert.equal(
    await page.locator("#model-key").count(),
    0,
    "Saving clears the credential input",
  );
  const publicConfig = await api(page, cfg, "/settings/models");
  assert.equal(publicConfig.stages.planning.api_key, "configured");
  assert.equal(publicConfig.stages.planning.key_source, "override");
  const exposed = await page.evaluate(() =>
    JSON.stringify({
      html: document.documentElement.outerHTML,
      local: { ...localStorage },
      session: { ...sessionStorage },
      url: location.href,
    }),
  );
  for (const value of [secret, cfg.token, "explicit-ci-only"]) {
    assert(
      !exposed.includes(value),
      "Credentials must not remain in DOM, storage or URLs",
    );
    assert(
      !responses.some((body) => body.includes(value)),
      "Settings response must never echo saved credentials",
    );
    assert(
      !errors.some((error) => error.includes(value)),
      "No credential in browser diagnostics",
    );
  }
  assert.equal(
    (await fixture(page, cfg)).calls.length,
    callsBefore,
    "Saving and format status never make a paid model call",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-settings-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#main-content").focus();
  await page.evaluate(() => window.scrollTo(0, 0));
  await noHorizontalOverflow(page);
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-settings-mobile.png"),
    fullPage: false,
  });
  page.off("response", watch);
}

async function workbench(page, cfg, errors) {
  const streams = [];
  page.on("request", (request) => {
    if (/\/stream\?/.test(request.url()))
      streams.push({ url: request.url(), headers: request.headers() });
  });
  await connect(page, cfg);
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-home-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#main-content").focus();
  await page.evaluate(() => window.scrollTo(0, 0));
  await noHorizontalOverflow(page);
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-home-mobile.png"),
    fullPage: false,
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  const firstStream = page
    .waitForResponse(
      (response) =>
        /\/stream\?/.test(response.url()) && response.status() === 200,
    )
    .catch((error) => ({ error }));
  const runId = await createRun(page, cfg, "游戏资讯助手", { ime: true });
  // Start provider bytes only after the browser has opened its real event stream,
  // proving this is a live delta rather than an already-populated transcript snapshot.
  const openedStream = await firstStream;
  if (openedStream.error) throw openedStream.error;
  assert.equal(
    (await api(page, cfg, `/runs/${runId}/transcript`)).messages.filter(
      (message) => message.role === "assistant" && message.content,
    ).length,
    0,
  );
  await page.request.post(cfg.fixture + "/fixture/start");
  const draft = page.locator(
    '[data-testid="assistant-message"][data-validation="pending"] .message-text',
  );
  await draft.filter({ hasText: cfg.stream_summary }).waitFor();
  const unfinished = await fixture(page, cfg);
  assert(
    unfinished.draft_sent && !unfinished.completed,
    "The browser must render a delta while provider final bytes are withheld",
  );
  assert.equal(await draft.count(), 1);
  assert.equal(
    await draft.innerText(),
    cfg.stream_summary,
    "Split Unicode and surrogate fragments assemble without replacement characters",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-streaming-desktop.png"),
    fullPage: true,
  });
  await route(page, "projects");
  await page
    .getByRole("heading", { name: "每个项目，都能继续往下走", exact: true })
    .waitFor();
  assert(
    !(await fixture(page, cfg)).completed,
    "Leaving a page cannot finish or cancel provider work",
  );
  await route(page, `run/${runId}/conversation`);
  await draft.filter({ hasText: cfg.stream_summary }).waitFor();
  assert.equal(
    await draft.count(),
    1,
    "Navigation replay must not duplicate a draft",
  );
  assert.equal(await draft.innerText(), cfg.stream_summary);
  const localDraft = "当前步骤执行中只暂存，不自动提交";
  const busyComposer = page.getByRole("textbox", {
    name: "本轮补充草稿（仅保存在当前页面）",
    exact: true,
  });
  await busyComposer.fill(localDraft);
  await busyComposer.press("Enter");
  assert(
    await page
      .getByRole("button", { name: "当前步骤执行中，暂不可发送", exact: true })
      .isDisabled(),
  );
  assert(
    !JSON.stringify(await api(page, cfg, `/runs/${runId}/transcript`)).includes(
      localDraft,
    ),
    "Busy drafts never enter stored conversation without a gate submission",
  );
  // Browser-level offline/reconnect exercises cursor replay over the real endpoint.
  await page.context().setOffline(true);
  await page.waitForTimeout(250);
  await page.context().setOffline(false);
  await page.getByRole("button", { name: "查看进度", exact: true }).click();
  await page
    .getByRole("heading", { name: "每个阶段，都有可追溯的结果" })
    .waitFor();
  await page.getByRole("button", { name: "返回对话", exact: true }).click();
  await draft.filter({ hasText: cfg.stream_summary }).waitFor();
  assert.equal(await draft.innerText(), cfg.stream_summary);
  assert(
    (await busyComposer.inputValue()).includes(localDraft),
    "Same-run views preserve a local draft",
  );
  await page.request.post(cfg.fixture + "/fixture/release");
  await waitStatus(page, "WAITING_CLARIFICATION");
  const finalMessage = page.locator(
    '[data-testid="assistant-message"][data-validation="validated"] .message-text',
  );
  await finalMessage.filter({ hasText: cfg.stream_summary }).waitFor();
  assert.equal(await finalMessage.count(), 1);
  assert.equal(
    await finalMessage.innerText(),
    cfg.stream_summary,
    "Completion replaces the draft rather than appending it again",
  );
  assert.equal(
    await page
      .locator('[data-testid="assistant-message"][data-validation="pending"]')
      .count(),
    0,
  );
  assert(streams.length >= 2, "Navigation reconnects the authenticated stream");
  assert(
    streams.some(
      (request) => Number(new URL(request.url).searchParams.get("after")) > 0,
    ),
    "Reconnect uses durable event cursor",
  );
  for (const request of streams) {
    assert.equal(request.headers.authorization, "Bearer " + cfg.token);
    assert(!request.url.includes(cfg.token));
  }
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-question-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#main-content").focus();
  await page.evaluate(() => window.scrollTo(0, 0));
  await noHorizontalOverflow(page);
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-question-mobile.png"),
    fullPage: false,
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page
    .getByRole("button", { name: "了解并开启智能推荐", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "确认授权", exact: true })
    .click();
  await waitStatus(page, "READY", 100000);
  assert(
    (await page.locator(".progress-rail").innerText()).includes(
      "智能推荐已开启",
    ),
  );
  assert.equal(
    await page.getByRole("textbox", { name: "需求回答", exact: true }).count(),
    0,
  );
  await page.getByRole("button", { name: "查看交付结果", exact: true }).click();
  const downloadPromise = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "下载完整交付包", exact: true })
    .click();
  await (await downloadPromise).saveAs(cfg.output);
  const report = await api(page, cfg, `/runs/${runId}/report`);
  assert(
    report["verification.json"],
    "Actual run-level verification evidence must exist",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-ready.png"),
    fullPage: true,
  });
  fs.writeFileSync(
    path.join(cfg.reports, "workbench.json"),
    JSON.stringify(
      {
        passed: true,
        run_id: runId,
        selection_before_model_call: true,
        smart_clicked: true,
        subsequent_manual_actions: 0,
        first_delta_before_provider_complete: true,
        unicode_split: true,
        replay_deduplication: true,
        ime_enter: true,
        double_click_single_run: true,
        busy_draft_not_submitted: true,
        errors,
      },
      null,
      2,
    ),
  );
}

async function recovery(page, cfg) {
  await connect(page, cfg);
  async function model(name) {
    await route(page, "settings");
    await page
      .getByRole("heading", { name: "模型与服务，一处配置", exact: true })
      .waitFor();
    await page.getByRole("tab", { name: /^需求阶段/ }).click();
    await page.locator("#model-name").fill(name);
    const saved = page.waitForResponse(
      (response) =>
        response.url().endsWith("/settings/models") &&
        response.request().method() === "PATCH" &&
        response.status() === 200,
    );
    await page.getByRole("button", { name: "保存配置", exact: true }).click();
    await saved;
    await page
      .getByText("配置已保存 · 仅完成格式校验 · 未测试连接", { exact: true })
      .waitFor();
    await page.getByText(/^当前配置版本 /).waitFor();
  }
  await model("denied-fixture");
  await route(page, "home");
  const runId = await createRun(page, cfg, "模型失败与同轮恢复验收");
  await waitStatus(page, "FAILED");
  assert((await page.locator("main").innerText()).includes("HTTP 401"));
  const failedCalls = (await fixture(page, cfg)).calls.filter(
    (call) => call.model === "denied-fixture",
  );
  assert.equal(
    failedCalls.length,
    1,
    "A permanent provider denial is not silently retried",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-failed-recovery-desktop.png"),
    fullPage: true,
  });
  await model("requirements-fixture");
  await route(page, `run/${runId}/conversation`);
  await waitStatus(page, "FAILED");
  const beforeRuns = (await api(page, cfg, "/runs")).length;
  const retried = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/runs/${runId}/retry`) &&
      response.status() === 202,
  );
  await page.getByRole("button", { name: "重试当前运行", exact: true }).click();
  await retried;
  await page
    .locator('[data-testid="run-workspace"][data-status="FAILED"]')
    .waitFor({ state: "hidden" });
  await waitStatus(page, "WAITING_CLARIFICATION");
  assert.equal(
    await page
      .locator('[data-testid="run-workspace"]')
      .getAttribute("data-run-id"),
    runId,
  );
  assert.equal(
    (await api(page, cfg, "/runs")).length,
    beforeRuns,
    "Retry resumes the existing run",
  );
  await capture(page, {
    animations: "disabled",
    path: path.join(cfg.reports, "workbench-recovered-desktop.png"),
    fullPage: true,
  });
  fs.writeFileSync(
    path.join(cfg.reports, "recovery.json"),
    JSON.stringify(
      {
        passed: true,
        run_id: runId,
        permanent_provider_denial: true,
        configuration_corrected_in_ui: true,
        same_run_retry: true,
      },
      null,
      2,
    ),
  );
}

async function manual(page, cfg) {
  await connect(page, cfg);
  const runId = await createRun(
    page,
    { ...cfg, requirement: "人工审批验收" },
    "人工审核完整交付验收",
  );
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
  await page
    .getByRole("checkbox", {
      name: "我已阅读本次验收证据与交付等级",
      exact: true,
    })
    .check();
  await deliver.click();
  await waitStatus(page, "READY");
  assert.equal(submissions.length, 3);
  assert.equal((await api(page, cfg, `/runs/${runId}`)).auto_mode, false);
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
