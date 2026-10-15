# scripts/guided_browser.cjs · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](scripts__guided_browser_cjs--002.md)

**作用：在真实浏览器操作研发工作台。** 通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。

**对应关系：** ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/guided_browser.cjs`；**本文件共有 2 段**。本段覆盖源文件 L1–L899。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`36149`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/guided_browser.cjs", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "f932bc5f927ea303a35441033c9ed4d65933e036d0215bd66018f05fa547332c"} -->
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
  const before = await api(page, cfg, "/runs");
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
      (await api(page, cfg, "/runs")).length,
      before.length,
      "IME Enter must not submit a run",
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
  assert((await composer.inputValue()).includes("\n"), "Enter keeps editing a multiline draft");
  await composer.fill(cfg.requirement);
  console.log("Create run: selecting stack");
  // The backend receives neither project nor run before a deliberate stack confirmation.
  await page.locator("#new-project-title").fill(title);
  await page.getByRole("radio", { name: "FastAPI + 轻量管理页面", exact: true }).check();
  await page.locator(".selection-details .ant-collapse-header").click();
  console.log("Create run: selected backend");
  await antSelect(page, "#frontend-selection", "simple-admin");
  console.log("Create run: selected frontend");
  await antSelect(page, "#database-selection", "sqlite");
  console.log("Create run: selected database");
  assert.equal((await api(page, cfg, "/runs")).length, before.length);
  // True repeated browser click, not a direct API shortcut.
  await page
    .getByRole("button", { name: "创建并开始", exact: true })
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
async function fixtureControl(page, cfg, endpoint, data) {
  const response = await page.request.post(cfg.fixture + "/fixture/" + endpoint, {
    ...(data ? { data } : {}),
  });
  assert(response.ok(), "Local fixture control must succeed: " + endpoint);
}
async function waitFixture(page, cfg, predicate, message) {
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    const status = await fixture(page, cfg);
    assert.deepEqual(status.failures, [], "Local provider fixture must remain valid");
    if (predicate(status)) return status;
    await new Promise((resolve) => setTimeout(resolve, 25));
  }
  throw new Error(message);
}
async function clickDisabled(page, button) {
  assert(await button.isDisabled(), "Repeated action is disabled while pending");
  await button.scrollIntoViewIfNeeded();
  const box = await button.boundingBox();
  assert(box, "Disabled button must still be visible");
  // Real pointer events exercise the disabled element, with no forced handler calls.
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2, {
    clickCount: 2,
  });
}
async function modelSettings(page, cfg, errors) {
  const before = await fixture(page, cfg);
  const requests = [], responseBodies = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/settings/models"))
      requests.push({ method: request.method(), path: new URL(request.url()).pathname });
  });
  page.on("response", (response) => {
    if (new URL(response.url()).pathname.startsWith("/settings/models"))
      responseBodies.push(response.text());
  });
  await fixtureControl(page, cfg, "settings-read", { mode: "hold" });
  const connecting = connect(page, { ...cfg, platform: cfg.platform + "/#/settings" });
  await waitFixture(page, cfg, (status) => status.settings_reads.started,
    "Initial settings GET never reached the real local application");
  await page.locator("h1").filter({ hasText: "模型与服务，一处配置" }).waitFor();
  for (const id of ["#model-url", "#model-name", "#model-provider", "#key-action"]) {
    assert(await page.locator(id).isDisabled(), "First read locks " + id);
  }
  const discover = page.getByRole("button", { name: "查询模型列表", exact: true, includeHidden: true });
  const save = page.getByRole("button", { name: "保存配置", exact: true, includeHidden: true });
  const refresh = page.getByRole("button", { name: "读取最新配置", exact: true });
  const probe = page.getByRole("button", { name: "测试连接", exact: true });
  assert(await discover.isDisabled());
  assert(await save.isDisabled());
  await fixtureControl(page, cfg, "settings-read/release");
  await connecting;
  const original = await api(page, cfg, "/settings/models");
  assert.equal(original.ready, false);
  assert.equal(original.default.base_url, "");
  assert.equal(original.default.model, "");
  assert.equal(original.default.api_key, "missing");
  assert.equal(await page.locator("#model-name").inputValue(), "");
  assert(await discover.isDisabled());
  assert(await probe.isDisabled());
  assert(await refresh.isEnabled(), "First-time configuration always offers an explicit reload");

  await page.locator("#model-url").fill(cfg.fixture + "/catalog-v1");
  await antSelect(page, "#key-action", "替换为新密钥");
  await page.locator("#model-key").fill(cfg.catalog_key);
  assert(await discover.isEnabled(), "An unsaved endpoint/key can query before choosing a model");
  assert.equal((await fixture(page, cfg)).catalog.calls.length, before.catalog.calls.length,
    "Editing never automatically queries a provider");
  await fixtureControl(page, cfg, "catalog", { mode: "success", hold: true });
  const initialCatalogResponse = page.waitForResponse((response) =>
    response.url().endsWith("/settings/models/discover"));
  await discover.click();
  await waitFixture(page, cfg, (status) => status.catalog.started,
    "The real GET /models was not observed by the local provider");
  for (const id of ["#model-url", "#model-name", "#model-key"]) {
    assert(await page.locator(id).isDisabled(), "Pending discovery locks " + id);
  }
  assert(await save.isDisabled());
  assert(await refresh.isDisabled());
  await clickDisabled(page, discover);
  assert.equal((await fixture(page, cfg)).catalog.calls.length, before.catalog.calls.length + 1);
  assert.equal(requests.filter((request) => request.path.endsWith("/discover")).length, 1,
    "Repeated pending clicks send exactly one discovery POST");
  await fixtureControl(page, cfg, "catalog/release");
  const initialCatalog = await (await initialCatalogResponse).json();
  assert.equal(initialCatalog.ok, true);
  assert.deepEqual(initialCatalog.models, cfg.catalog_models);
  await page.getByText(/已获取模型 ID；列表不代表模型权限或推理兼容性已验证/).waitFor();
  await page.locator("#model-name").fill("catalog");
  await page.locator(".ant-select-dropdown:visible .ant-select-item-option")
    .filter({ hasText: cfg.catalog_models[1] }).click();
  assert.equal(await page.locator("#model-name").inputValue(), cfg.catalog_models[1]);
  assert.deepEqual(await api(page, cfg, "/settings/models"), original,
    "Discovery and choosing an offered ID cannot persist the draft");
  assert.equal(requests.filter((request) => request.method === "PATCH").length, 0);
  assert.equal((await fixture(page, cfg)).calls.length, before.calls.length,
    "Catalog lookup must never call an inference endpoint");

  async function saveModel(expected) {
    const saved = page.waitForResponse((response) =>
      response.url().endsWith("/settings/models") && response.request().method() === "PATCH");
    await save.click();
    const response = await saved;
    assert.equal(response.status(), 200);
    assert.equal((await response.json()).default.model, expected);
    await page.getByText("配置已保存 · 仅完成格式校验 · 未测试连接", { exact: true }).waitFor();
    await page.waitForFunction(() => !document.querySelector("#model-name").disabled);
    assert.equal(await page.locator("#model-key").count(), 0, "Save clears draft credentials");
  }
  await saveModel(cfg.catalog_models[1]);
  assert.equal((await api(page, cfg, "/settings/models")).default.api_key, "configured");

  async function query(mode, code) {
    const count = (await fixture(page, cfg)).catalog.calls.length;
    await fixtureControl(page, cfg, "catalog", { mode });
    const pending = page.waitForResponse((response) =>
      response.url().endsWith("/settings/models/discover"));
    await discover.click();
    const response = await pending;
    assert.equal(response.status(), 200);
    const result = await response.json();
    assert.equal(result.code, code);
    assert.equal(result.ok, mode === "success");
    await page.getByText(result.message + "；仍可手动填写模型 ID。", { exact: true }).waitFor();
    assert.equal((await fixture(page, cfg)).catalog.calls.length, count + 1,
      "Catalog errors must not automatically retry");
    return result;
  }
  await query("unsupported", "discovery_unsupported");
  const manualId = "manual-fixture-not-in-catalog";
  await page.locator("#model-name").fill(manualId);
  assert(await save.isEnabled(), "Unsupported catalog still permits a manual model ID");
  await saveModel(manualId);
  const savedConfig = await api(page, cfg, "/settings/models");
  assert.equal(savedConfig.default.model, manualId);
  await query("denied", "authentication_failed");
  assert(await page.locator("#model-name").isEnabled(), "Failed query keeps manual input usable");
  await query("success", "models_discovered");
  assert.equal(await page.locator("#model-name").inputValue(), manualId,
    "A successful retry must not replace the manually configured ID");

  const catalogCount = (await fixture(page, cfg)).catalog.calls.length;
  await page.locator("#model-url").fill(cfg.fixture + "/changed-catalog-v1");
  assert(await discover.isDisabled(), "A new URL cannot discover using a stored old key");
  assert(await save.isDisabled());
  await clickDisabled(page, discover);
  await antSelect(page, "#key-action", "替换为新密钥");
  await page.locator("#model-key").fill(cfg.catalog_key);
  const rejectedKey = page.waitForResponse((response) =>
    response.url().endsWith("/settings/models/discover") && response.status() === 422);
  await discover.click();
  await rejectedKey;
  await page.getByText(/该 API Key 已用于其他地址；新地址必须使用独立密钥/).waitFor();
  assert.equal((await fixture(page, cfg)).catalog.calls.length, catalogCount,
    "Re-entering the old key is rejected before any request reaches the new destination");
  assert.deepEqual(await api(page, cfg, "/settings/models"), savedConfig);

  const draftModel = "draft-kept-after-failed-refresh";
  const draftKey = "explicit-unsaved-reload-ci-only";
  await page.locator("#model-name").fill(draftModel);
  await page.locator("#model-key").fill(draftKey);
  const readsBefore = (await fixture(page, cfg)).settings_reads.requests.length;
  await refresh.click();
  const confirmation = page.getByRole("dialog");
  await confirmation.getByText("读取最新配置并放弃未保存的修改？", { exact: true }).waitFor();
  await confirmation.getByRole("button", { name: "继续编辑", exact: true }).click();
  await confirmation.waitFor({ state: "hidden" });
  assert.equal((await fixture(page, cfg)).settings_reads.requests.length, readsBefore,
    "Cancelling dirty reload sends no settings request");
  assert.equal(await page.locator("#model-name").inputValue(), draftModel);
  assert.equal(await page.locator("#model-key").inputValue(), draftKey);
  assert.equal(await page.locator("#model-url").inputValue(), cfg.fixture + "/changed-catalog-v1");

  async function confirmRefresh(status) {
    await refresh.click();
    await confirmation.getByText("读取最新配置并放弃未保存的修改？", { exact: true }).waitFor();
    const response = page.waitForResponse((response) =>
      response.url().endsWith("/settings/models") && response.request().method() === "GET");
    await confirmation.getByRole("button", { name: "读取最新配置", exact: true }).click();
    assert.equal((await response).status(), status);
    await confirmation.waitFor({ state: "hidden" });
  }
  await fixtureControl(page, cfg, "settings-read", { mode: "fail" });
  await confirmRefresh(503);
  await page.getByText(cfg.settings_read_failure, { exact: true }).waitFor();
  assert.equal(await page.locator("#model-name").inputValue(), draftModel);
  assert.equal(await page.locator("#model-key").inputValue(), draftKey,
    "Failed reload cannot silently discard the user's unsaved key");
  assert(await refresh.isEnabled(), "Read failure retains the explicit retry button");
  await confirmRefresh(200);
  await page.getByText("已读取最新配置，请重新核对后保存", { exact: true }).waitFor();
  assert.equal(await page.locator("#model-name").inputValue(), manualId);
  assert.equal(await page.locator("#model-url").inputValue(), cfg.fixture + "/catalog-v1");
  assert.equal(await page.locator("#model-key").count(), 0);
  assert.deepEqual(await api(page, cfg, "/settings/models"), savedConfig,
    "Reload retries never mutate persisted configuration");
  assert.equal(requests.filter((request) => request.method === "PATCH").length, 2,
    "Only the two explicit Save clicks may persist configuration");
  const after = await fixture(page, cfg);
  assert.equal(after.calls.length, before.calls.length, "Entire settings scenario makes zero inference calls");
  assert.equal(after.catalog.calls.length, before.catalog.calls.length + 4);
  const exposed = await page.evaluate(() => JSON.stringify({
    html: document.documentElement.outerHTML,
    local: { ...localStorage }, session: { ...sessionStorage }, url: location.href,
  }));
  const bodies = await Promise.all(responseBodies);
  for (const secret of [cfg.catalog_key, draftKey, cfg.token]) {
    assert(!exposed.includes(secret), "No key or token remains in browser-rendered state");
    assert(!bodies.some((body) => body.includes(secret)), "Real settings responses never echo credentials");
    assert(!errors.some((error) => error.includes(secret)), "Browser diagnostics never echo credentials");
  }
  await capture(page, {
    animations: "disabled", path: path.join(cfg.reports, "workbench-model-discovery.png"), fullPage: true,
  });
  fs.writeFileSync(path.join(cfg.reports, "settings.json"), JSON.stringify({
    passed: true, empty_configuration: true, slow_first_read_locked: true,
    unsaved_catalog: true, pending_query_locked: true, catalog_selection_saved: true,
    manual_fallback_saved: true, unsupported_and_failed_catalog: true, catalog_manual_retry: true,
    changed_url_key_binding: true, dirty_refresh_cancel: true, failed_refresh_preserves_draft: true,
    refresh_manual_retry: true, no_inference: true, no_secret_echo: true,
    catalog_calls: after.catalog.calls, errors,
  }, null, 2));
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
    .getByRole("heading", { name: "项目工作台", exact: true })
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
  await page.getByRole("button", { name: "执行过程", exact: true }).click();
  await page
    .getByRole("heading", { name: "执行过程" })
    .waitFor();
  await page.getByRole("button", { name: "对话与审批", exact: true }).click();
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
      "智能委托已开启",
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

````
