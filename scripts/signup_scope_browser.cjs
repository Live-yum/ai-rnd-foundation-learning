// Real backend gates and compiled Vue UI; no mocked browser routes or model network.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const { randomUUID } = require("node:crypto");

async function main() {
  const cfg = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const { chromium } = require(process.argv[3]);
  const browser = await chromium.launch({ headless: true, ...(process.env.PRODUCT_VERIFY_CHROMIUM ? { executablePath: process.env.PRODUCT_VERIFY_CHROMIUM } : {}) });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1050 },
  });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const api = async (endpoint, options = {}) => {
    const response = await page.request.fetch(cfg.platform + endpoint, {
      ...options,
      headers: {
        Authorization: "Bearer " + cfg.token,
        "Idempotency-Key": randomUUID(),
        ...(options.headers || {}),
      },
    });
    assert(
      response.ok(),
      `${endpoint}: ${response.status()} ${await response.text()}`,
    );
    return response.json();
  };
  const status = async (expected) => {
    await page.waitForFunction(
      (value) =>
        document.querySelector('[data-testid="run-workspace"]')?.dataset
          .status === value,
      expected,
      { timeout: 15000 },
    );
  };
  try {
    await page.goto(cfg.platform);
    await page
      .getByRole("button", { name: "连接本地服务", exact: true })
      .click();
    await page.locator("#access-token").fill(cfg.token);
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "连接工作空间", exact: true })
      .click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    const runId = cfg.legacy_run_id;
    await page.evaluate((id) => {
      location.hash = `/run/${id}/conversation`;
    }, runId);
    await status("FAILED");
    assert.equal((await api(`/runs/${runId}`)).pending, null);
    await page
      .getByRole("button", { name: "重试当前运行", exact: true })
      .click();
    await status("BLOCKED");
    await page
      .getByRole("heading", { name: "先确认参与者入口与报名范围", exact: true })
      .waitFor();
    assert.equal(
      await page.locator('.question-card input[type="radio"]:checked').count(),
      0,
    );
    assert(
      (
        await page.locator('[data-testid="user-message"]').first().innerText()
      ).includes(cfg.original),
    );
    const originalGate = (await api(`/runs/${runId}`)).pending;
    assert.equal(originalGate.can_approve, false);
    for (let index = 0; index < 3; index++) {
      const repeated = await api(`/runs/${runId}/automation`, {
        method: "POST",
        data: { enabled: true, accepted: true },
      });
      assert.equal(repeated.status, "BLOCKED");
    }
    assert.equal(
      (await api(`/runs/${runId}`)).pending.gate_id,
      originalGate.gate_id,
    );
    assert.equal(await page.locator(".rail-steps li.done").count(), 0);
    await page.locator("#main-content").focus();
    await page.screenshot({
      path: path.join(cfg.reports, "scope-blocked.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    assert(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth <= innerWidth + 1 &&
          document.body.scrollWidth <= innerWidth + 1,
      ),
      "Mobile scope clarification must not overflow horizontally",
    );
    await page.screenshot({
      path: path.join(cfg.reports, "scope-blocked-mobile.png"),
      fullPage: true,
    });
    const mobileSubmit = page.getByRole("button", {
      name: "提交本组答案",
      exact: true,
    });
    await mobileSubmit.evaluate((element) =>
      element.scrollIntoView({ block: "center" }),
    );
    const mobileGeometry = await mobileSubmit.evaluate((element) => {
      const submit = element.getBoundingClientRect();
      const nav = document
        .querySelector(".mobile-bottom-nav")
        .getBoundingClientRect();
      return {
        submit_top: submit.top,
        submit_bottom: submit.bottom,
        navigation_top: nav.top,
      };
    });
    assert(mobileGeometry.submit_top >= 0);
    assert(
      mobileGeometry.submit_bottom < mobileGeometry.navigation_top,
      "Mobile submit must remain above the fixed bottom navigation",
    );
    await page.screenshot({
      path: path.join(cfg.reports, "scope-options-mobile.png"),
      fullPage: false,
    });
    await page.setViewportSize({ width: 1440, height: 1050 });

    await page
      .getByRole("button", { name: "恢复人工确认", exact: true })
      .click();
    await status("WAITING_CLARIFICATION");
    const recommend = page.getByRole("button", {
      name: "了解并开启智能推荐",
      exact: true,
    });
    assert(
      await recommend.isDisabled(),
      "Known scope choice must not become another smart request",
    );
    await page
      .getByRole("radio", { name: cfg.admin_scope, exact: true })
      .check();
    await page
      .getByRole("radio", { name: cfg.authenticated_scope, exact: true })
      .check();
    assert.equal(
      await page.locator('.question-card input[type="radio"]:checked').count(),
      1,
    );
    await page
      .getByRole("button", { name: "提交本组答案", exact: true })
      .click();
    await status("WAITING_REQUIREMENTS");
    const result = await api(`/runs/${runId}`);
    assert.equal(result.pending.can_approve, true);
    assert.equal(result.pending.data.requirement.summary, cfg.original);
    assert(!result.pending.data.capability_conflicts?.length);
    assert(
      result.pending.data.requirement.features.includes(
        cfg.authenticated_scope,
      ),
    );
    const messages = await api(`/runs/${runId}/messages`);
    assert.equal(messages.length, 2);
    assert.equal(messages[0].content, cfg.original);
    assert(messages[1].content.includes(cfg.authenticated_scope));
    assert(!messages[1].content.includes(cfg.admin_scope));
    assert.equal(await page.locator(".rail-steps li.done").count(), 0);
    await page.locator("#main-content").focus();
    await page.screenshot({
      path: path.join(cfg.reports, "scope-corrected.png"),
      fullPage: true,
    });
    const history = page.locator('[data-validation="historical_gate"]');
    assert((await history.allTextContents()).join("\n").includes("参与者"));
    await page.evaluate((id) => { location.hash = `/run/${id}/conversation`; }, cfg.diagnostic_run_id);
    await status("FAILED");
    const checkDiagnostics = async () => {
      assert.equal(await page.locator('.failure-diagnostic').count(), 2);
      const text = await page.locator('.messages').innerText();
      for (const expected of ["参与者将通过哪种入口报名？", "模板不支持匿名公开报名页", "仅管理本人报名记录", "schema_validation", "response_validation", "string_type", "追踪 ID", "无需重填已提交的回答"]) assert(text.includes(expected), expected);
      assert(!text.includes("暂无可展示的摘要"));
      assert.equal(await page.locator('.question-card').count(), 0);
    };
    await checkDiagnostics();
    await page.reload();
    await page.getByRole("button", { name: "连接本地服务", exact: true }).click();
    await page.locator("#access-token").fill(cfg.token);
    await page.getByRole("dialog").getByRole("button", { name: "连接工作空间", exact: true }).click();
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await status("FAILED");
    await checkDiagnostics();
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(cfg.reports, "browser.json"),
      JSON.stringify(
        {
          run_id: runId,
          real_browser: true,
          real_http: true,
          status: result.status,
          errors,
          diagnostic_failure_and_history_survive_refresh: true,
          provider_mode: "offline-fixture",
          earlier_scope_invalidates_old_progress: true,
          mobile_no_horizontal_overflow: true,
          mobile_submit_above_fixed_navigation: true,
          screenshots: [
            "scope-blocked.png",
            "scope-blocked-mobile.png",
            "scope-options-mobile.png",
            "scope-corrected.png",
          ],
        },
        null,
        2,
      ),
    );
  } catch (error) {
    await page
      .screenshot({
        path: path.join(cfg.reports, "scope-failed.png"),
        fullPage: true,
      })
      .catch(() => {});
    throw error;
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
