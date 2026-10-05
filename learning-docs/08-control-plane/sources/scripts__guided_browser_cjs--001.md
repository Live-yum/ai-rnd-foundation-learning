# scripts/guided_browser.cjs · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](scripts__guided_browser_cjs--002.md)

**作用：在真实浏览器操作研发工作台。** 通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。

**对应关系：** ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/guided_browser.cjs`；**本文件共有 2 段**。本段覆盖源文件 L1–L789。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26239`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/guided_browser.cjs", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "f0ea97f90fadb9298713c205777dda3050651cb7d13c591709546376074e087f"} -->
````javascript
// scripts/guided_browser.cjs
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
async function fixture(page, cfg, timeout = 60000) {
  const response = await page.request.get(cfg.fixture + "/fixture/status", {
    timeout,
  });
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
  const connectionTest = page.getByRole("button", {
    name: "测试连接",
    exact: true,
  });
  assert(
    await connectionTest.isEnabled(),
    "Saved configuration exposes the explicit probe",
  );
  await connectionTest.click();
  const probeConfirmation = page.getByRole("dialog");
  await probeConfirmation
    .getByText("发起一次真实模型连接测试？", { exact: true })
    .waitFor();
  assert.equal(
    (await fixture(page, cfg)).calls.length,
    callsBefore,
    "Opening the cost confirmation must not call a model",
  );
  await probeConfirmation.getByRole("button", { name: /^取\s*消$/ }).click();
  await probeConfirmation.waitFor({ state: "hidden" });
  assert.equal(
    (await fixture(page, cfg)).calls.length,
    callsBefore,
    "Cancelling a connection test must not call a model",
  );
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

// Only bounded status/boolean/hash fields are retained, never arbitrary API text.
function deliveryFacts(run, report) {
  const hash = (value) =>
    typeof value === "string" && /^[a-f0-9]{64}$/.test(value) ? value : null;
  const gate = run.pending || {};
  const delivery = report["delivery.json"] || {};
  const verification = report["verification.json"] || {};
  return {
    waiting_delivery: run.status === "WAITING_DELIVERY",
    manual_mode: run.auto_mode === false,
    delivery_gate: gate.stage === "delivery",
    can_approve: gate.can_approve === true,
    approve_action:
      Array.isArray(gate.actions) && gate.actions.includes("approve"),
    gate_id: hash(gate.gate_id),
    gate_digest: hash(gate.digest),
    gate_version:
      Number.isSafeInteger(gate.version) && gate.version >= 0
        ? gate.version
        : null,
    artifact_sha256: hash(delivery.sha256),
    gate_artifact_matches:
      hash(gate.data?.sha256) !== null && gate.data.sha256 === delivery.sha256,
    runtime_validation: delivery.validation_level === "runtime",
    verification_passed: verification.passed === true,
    verification_source_sha256: hash(verification.source_digest),
    browser_passed: verification.browser?.passed === true,
    real_browser: verification.browser?.real_browser === true,
    cleanroom_passed: delivery.cleanroom?.passed === true,
    cleanroom_http: delivery.cleanroom?.http === true,
    cleanroom_restart: delivery.cleanroom?.restart === true,
    isolated_sqlite: delivery.cleanroom?.database === "real-isolated-sqlite",
  };
}

function requireDeliveryFacts(facts) {
  for (const [name, value] of Object.entries(facts))
    assert(
      value !== null && value !== false,
      "Missing delivery prerequisite: " + name,
    );
}

function reviewTimeout(deadline) {
  const remaining = deadline - Date.now();
  assert(
    remaining > 0,
    "Delivery rereview exceeded the existing browser deadline",
  );
  return remaining;
}

async function currentDeliveryFacts(
  page,
  cfg,
  runId,
  deadline = Date.now() + 3000,
) {
  const [run, report] = await Promise.all([
    api(page, cfg, `/runs/${runId}`, {
      timeout: Math.min(3000, reviewTimeout(deadline)),
    }),
    api(page, cfg, `/runs/${runId}/report`, {
      timeout: Math.min(3000, reviewTimeout(deadline)),
    }),
  ]);
  return deliveryFacts(run, report);
}

async function rereviewDelivery(page, runId, deadline = Date.now() + 60000) {
  reviewTimeout(deadline);
  const latest = page.getByRole("button", {
    name: "查看最新版本",
    exact: true,
  });
  const stale = await latest.isVisible();
  if (stale) {
    const checkbox = page.getByRole("checkbox", {
      name: "我已阅读本次验收证据与交付等级",
      exact: true,
    });
    assert(
      await checkbox.isDisabled(),
      "A stale delivery cannot be acknowledged",
    );
    await latest.click({ timeout: reviewTimeout(deadline) });
    await latest.waitFor({ state: "hidden", timeout: reviewTimeout(deadline) });
    // The existing reread action opens the generic current-version view.
    // Return to its dedicated delivery evidence before making a fresh decision.
    await route(page, `run/${runId}/delivery`);
  }
  return stale;
}

function observeRunRefreshes(page, runId) {
  const pending = new Map();
  const paths = new Set([
    `/runs/${runId}`,
    `/runs/${runId}/report`,
    `/runs/${runId}/models`,
  ]);
  const started = (request) => {
    if (
      request.method() !== "GET" ||
      !paths.has(new URL(request.url()).pathname)
    )
      return;
    let done;
    const promise = new Promise((resolve) => {
      done = resolve;
    });
    pending.set(request, { promise, done });
  };
  const finished = (request) => {
    pending.get(request)?.done();
    pending.delete(request);
  };
  page.on("request", started);
  page.on("requestfinished", finished);
  page.on("requestfailed", finished);
  return {
    async drain(deadline) {
      let timer;
      try {
        await Promise.race([
          (async () => {
            while (pending.size)
              await Promise.all(
                [...pending.values()].map((entry) => entry.promise),
              );
          })(),
          new Promise((_, reject) => {
            timer = setTimeout(
              () =>
                reject(
                  new Error(
                    "UI refresh reads did not settle within the existing browser deadline",
                  ),
                ),
              reviewTimeout(deadline),
            );
          }),
        ]);
        // Cross a browser task boundary after response bodies finish so Vue can apply them.
        await page.evaluate(
          () => new Promise((resolve) => requestAnimationFrame(resolve)),
        );
      } finally {
        clearTimeout(timer);
      }
    },
    close() {
      page.off("request", started);
      page.off("requestfinished", finished);
      page.off("requestfailed", finished);
    },
  };
}

````
