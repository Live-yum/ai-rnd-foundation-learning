# scripts/capability_browser.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_browser.；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/capability_browser.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L160。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9881`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_browser.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "26e1057f64edf285e84c1238e37036b01b543052b2ea7ebb4b15016dc6402cd4"} -->
````javascript
// scripts/capability_browser.cjs
// scripts/capability_browser.cjs
// Trusted controller-side browser checks; no model JavaScript is evaluated here.
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')

const identity = {
  protocol: 1,
  request_id: null,
  verifier_sha256: crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
}
const progress = { phase: 'contract', scenario_index: null, step_index: null, action: null, navigation_status: null }
let firstFailure = null
const errorNames = new Set(['Error', 'TypeError', 'SyntaxError', 'ReferenceError', 'TimeoutError'])

// Fixed local kernel interfaces only. Cap every read and return finite values;
// unavailable facts stay unknown and never authorize a sandbox fallback.
// Facts describe this verifier process, not proof of the browser denial cause.
function browserSecurityFacts() {
  function read(filename) {
    let fd
    try {
      fd = fs.openSync(filename, 'r')
      const buffer = Buffer.alloc(8193)
      const size = fs.readSync(fd, buffer, 0, buffer.length, 0)
      return size <= 8192 ? buffer.subarray(0, size).toString('ascii').trim() : null
    } catch { return null }
    finally { if (fd !== undefined) { try { fs.closeSync(fd) } catch {} } }
  }
  function flag(filename) {
    const value = read(filename)
    return value === '1' || value === 'Y' ? true : value === '0' || value === 'N' ? false : null
  }
  const status = read('/proc/self/status')
  function field(name) { return status === null ? null : status.match(new RegExp(`^${name}:\\s*([0-9a-f]+)$`, 'm'))?.[1] ?? null }
  const nnp = field('NoNewPrivs')
  const seccomp = field('Seccomp')
  const caps = field('CapEff')
  const profile = read('/proc/self/attr/current')
  return {
    uid_zero: typeof process.getuid === 'function' ? process.getuid() === 0 : null,
    no_new_privileges: nnp === '1' ? true : nnp === '0' ? false : null,
    seccomp_mode: ['0', '1', '2'].includes(seccomp) ? Number(seccomp) : null,
    effective_capabilities: caps !== null && /^[0-9a-f]{16}$/.test(caps) ? /[1-9a-f]/.test(caps) : null,
    apparmor_profile: profile === 'docker-default (enforce)' ? 'docker-default' : profile === 'unconfined' ? 'unconfined' : profile !== null && / \(enforce\)$/.test(profile) ? 'other-enforced' : 'unknown',
    apparmor_enabled: flag('/sys/module/apparmor/parameters/enabled'),
    apparmor_userns_restricted: flag('/proc/sys/kernel/apparmor_restrict_unprivileged_userns'),
    unprivileged_userns_enabled: flag('/proc/sys/kernel/unprivileged_userns_clone'),
  }
}

function rememberFailure(error) {
  if (firstFailure) return
  // Inspect trusted tool errors only to classify them. Never return their text,
  // command lines, URLs, selectors, payloads, or credential-bearing arguments.
  const message = error instanceof Error ? error.message : ''
  let errorCode = 'operation-failed'
  if (error && error.name === 'TimeoutError') errorCode = 'timeout'
  else if (message === 'pinned_playwright_required') errorCode = 'tool-version'
  else if (message === 'browser_channel_rejected') errorCode = 'browser-channel-rejected'
  else if (message === 'browser_contract_too_large') errorCode = 'contract-too-large'
  else if (message === 'browser_navigation_outside_product') errorCode = 'origin-rejected'
  else if (message === 'unknown_browser_action') errorCode = 'action-rejected'
  else if (message === 'browser_application_error') errorCode = 'application-error'
  else if (progress.phase === 'tool' && error && error.code === 'MODULE_NOT_FOUND') errorCode = 'tool-missing'
  else if (progress.phase === 'launch' && /No usable sandbox|Failed to move to new namespace|Running as root without --no-sandbox/.test(message)) errorCode = 'sandbox-unavailable'
  else if (progress.phase === 'launch' && /Executable doesn't exist|Chromium distribution .* is not found/.test(message)) errorCode = 'browser-missing'
  else if (progress.phase === 'launch' && /error while loading shared libraries/.test(message)) errorCode = 'browser-dependency'
  else if (progress.phase === 'navigation' && /net::ERR_NAME_NOT_RESOLVED/.test(message)) errorCode = 'name-resolution'
  else if (progress.phase === 'navigation' && /net::ERR_CONNECTION_REFUSED/.test(message)) errorCode = 'connection-refused'
  else if (progress.phase === 'navigation' && /net::ERR_/i.test(message)) errorCode = 'navigation-network'
  const sandboxReason = errorCode !== 'sandbox-unavailable' ? null
    : /Running as root without --no-sandbox/.test(message) ? 'root-launch'
    : /Failed to move to new namespace/.test(message) ? 'namespace-entry-failed'
    : 'no-usable-sandbox'
  firstFailure = {
    ...progress,
    ...(progress.phase === 'launch' ? { sandbox_reason: sandboxReason, security_facts: browserSecurityFacts() } : {}),
    error_code: errorCode,
    error_type: error && errorNames.has(error.name) ? error.name : 'Other',
  }
  // Persist the first safe failure before cleanup, which may itself fail or
  // outlive the controller deadline. Never append a second error envelope.
  process.stdout.write(JSON.stringify({ ...identity, passed: false, diagnostic: firstFailure }))
}

async function main() {
  const chunks = []
  for await (const chunk of process.stdin) chunks.push(chunk)
  const raw = Buffer.concat(chunks)
  if (raw.length > 1000000) throw new Error('browser_contract_too_large')
  const contract = JSON.parse(raw.toString('utf8'))
  if (!/^[a-f0-9]{32}$/.test(contract.request_id)) throw new Error('invalid_request_identity')
  identity.request_id = contract.request_id
  progress.phase = 'tool'
  const modulePath = process.env.PRODUCT_VERIFY_PLAYWRIGHT || path.resolve('.native/browser/node_modules/playwright')
  if (JSON.parse(fs.readFileSync(path.join(modulePath, 'package.json'), 'utf8')).version !== '1.56.1') throw new Error('pinned_playwright_required')
  const { chromium } = require(modulePath)
  // Select only an installed, supported Chrome channel. Never retry without the
  // OS sandbox or accept caller-supplied executables/arguments. Ubuntu runners
  // already ship Chrome at its normal system location; no policy is changed.
  const channel = process.env.PRODUCT_VERIFY_BROWSER_CHANNEL || ''
  if (channel !== '' && channel !== 'chrome') throw new Error('browser_channel_rejected')
  const origin = new URL(contract.url).origin
  progress.phase = 'launch'
  const browser = await chromium.launch({ ...(channel ? { channel } : {}), headless: true, chromiumSandbox: true, args: ['--force-webrtc-ip-handling-policy=disable_non_proxied_udp', `--host-resolver-rules=MAP ${new URL(origin).hostname} 127.0.0.1`] })
  const contextOptions = {
    serviceWorkers: 'block', acceptDownloads: false,
    extraHTTPHeaders: { 'x-daytona-preview-token': contract.token },
    viewport: { width: 1280, height: 900 },
  }
  const receipts = []
  try {
    for (const [scenarioIndex, scenario] of contract.scenarios.entries()) {
      Object.assign(progress, { phase: 'context', scenario_index: scenarioIndex, step_index: null, action: null, navigation_status: null })
      const context = await browser.newContext(contextOptions)
      try {
        progress.phase = 'routing'
        await context.route('**/*', route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort())
        await context.routeWebSocket('**/*', socket => socket.close())
        progress.phase = 'page'
        const page = await context.newPage()
        const errors = []
        page.on('pageerror', () => errors.push('page_error'))
        for (const [stepIndex, step] of scenario.steps.entries()) {
          Object.assign(progress, { phase: 'action', step_index: stepIndex, action: ['viewport', 'open', 'fill', 'click', 'visible', 'hidden', 'text'].includes(step.action) ? step.action : null })
          if (step.action === 'viewport') await page.setViewportSize({ width: step.width, height: step.height })
          else if (step.action === 'open') {
            progress.phase = 'navigation'
            progress.navigation_status = null
            const url = new URL(step.value, origin)
            if (url.origin !== origin) throw new Error('browser_navigation_outside_product')
            const response = await page.goto(url.href, { waitUntil: 'domcontentloaded', timeout: 15000 })
            progress.navigation_status = response ? response.status() : null
          } else {
            const target = page.locator(step.selector)
            if (['visible', 'hidden', 'text'].includes(step.action)) progress.phase = 'assertion'
            if (step.action === 'fill') await target.fill(step.value, { timeout: 10000 })
            else if (step.action === 'click') await target.click({ timeout: 10000 })
            else if (step.action === 'visible') await target.waitFor({ state: 'visible', timeout: 10000 })
            else if (step.action === 'hidden') await target.waitFor({ state: 'hidden', timeout: 10000 })
            else if (step.action === 'text') {
              await target.filter({ hasText: step.value }).waitFor({ state: 'visible', timeout: 10000 })
            } else throw new Error('unknown_browser_action')
          }
        }
        progress.phase = 'application'
        if (errors.length) throw new Error('browser_application_error')
        receipts.push({ id: scenario.id, passed: true, steps: scenario.steps.length, real_browser: true, browser_os_sandbox: true })
      } catch (error) { rememberFailure(error); throw error }
      finally { progress.phase = 'context-close'; await context.close() }
    }
  } catch (error) { rememberFailure(error); throw error }
  finally { progress.phase = 'browser-close'; await browser.close() }
  return { ...identity, passed: true, checks: receipts }
}
main().then(report => process.stdout.write(JSON.stringify(report))).catch(error => {
  rememberFailure(error)
  process.exitCode = 1
})
````
