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

function rememberFailure(error) {
  if (firstFailure) return
  // Inspect trusted tool errors only to classify them. Never return their text,
  // command lines, URLs, selectors, payloads, or credential-bearing arguments.
  const message = error instanceof Error ? error.message : ''
  let errorCode = 'operation-failed'
  if (error && error.name === 'TimeoutError') errorCode = 'timeout'
  else if (message === 'pinned_playwright_required') errorCode = 'tool-version'
  else if (message === 'browser_contract_too_large') errorCode = 'contract-too-large'
  else if (message === 'browser_navigation_outside_product') errorCode = 'origin-rejected'
  else if (message === 'unknown_browser_action') errorCode = 'action-rejected'
  else if (message === 'browser_application_error') errorCode = 'application-error'
  else if (progress.phase === 'tool' && error && error.code === 'MODULE_NOT_FOUND') errorCode = 'tool-missing'
  else if (progress.phase === 'launch' && /No usable sandbox|Failed to move to new namespace|Running as root without --no-sandbox/.test(message)) errorCode = 'sandbox-unavailable'
  else if (progress.phase === 'launch' && /Executable doesn't exist/.test(message)) errorCode = 'browser-missing'
  else if (progress.phase === 'launch' && /error while loading shared libraries/.test(message)) errorCode = 'browser-dependency'
  else if (progress.phase === 'navigation' && /net::ERR_NAME_NOT_RESOLVED/.test(message)) errorCode = 'name-resolution'
  else if (progress.phase === 'navigation' && /net::ERR_CONNECTION_REFUSED/.test(message)) errorCode = 'connection-refused'
  else if (progress.phase === 'navigation' && /net::ERR_/i.test(message)) errorCode = 'navigation-network'
  firstFailure = {
    ...progress,
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
  const origin = new URL(contract.url).origin
  progress.phase = 'launch'
  const browser = await chromium.launch({ headless: true, chromiumSandbox: true, args: ['--force-webrtc-ip-handling-policy=disable_non_proxied_udp', `--host-resolver-rules=MAP ${new URL(origin).hostname} 127.0.0.1`] })
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
