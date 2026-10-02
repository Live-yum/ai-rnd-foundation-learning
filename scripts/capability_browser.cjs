// scripts/capability_browser.cjs
// Trusted controller-side browser checks; no model JavaScript is evaluated here.
const fs = require('node:fs')
const path = require('node:path')

async function main() {
  const chunks = []
  for await (const chunk of process.stdin) chunks.push(chunk)
  const raw = Buffer.concat(chunks)
  if (raw.length > 1000000) throw new Error('browser_contract_too_large')
  const contract = JSON.parse(raw.toString('utf8'))
  const modulePath = process.env.PRODUCT_VERIFY_PLAYWRIGHT || path.resolve('.native/browser/node_modules/playwright')
  if (JSON.parse(fs.readFileSync(path.join(modulePath, 'package.json'), 'utf8')).version !== '1.56.1') throw new Error('pinned_playwright_required')
  const { chromium } = require(modulePath)
  const origin = new URL(contract.url).origin
  const browser = await chromium.launch({ headless: true, chromiumSandbox: true, args: ['--force-webrtc-ip-handling-policy=disable_non_proxied_udp', `--host-resolver-rules=MAP ${new URL(origin).hostname} 127.0.0.1`] })
  const contextOptions = {
    serviceWorkers: 'block', acceptDownloads: false,
    extraHTTPHeaders: { 'x-daytona-preview-token': contract.token },
    viewport: { width: 1280, height: 900 },
  }
  const receipts = []
  try {
    for (const scenario of contract.scenarios) {
      const context = await browser.newContext(contextOptions)
      await context.route('**/*', route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort())
      await context.routeWebSocket('**/*', socket => socket.close())
      const page = await context.newPage()
      const errors = []
      page.on('pageerror', () => errors.push('page_error'))
      try {
        for (const step of scenario.steps) {
          if (step.action === 'viewport') await page.setViewportSize({ width: step.width, height: step.height })
          else if (step.action === 'open') {
            const url = new URL(step.value, origin)
            if (url.origin !== origin) throw new Error('browser_navigation_outside_product')
            await page.goto(url.href, { waitUntil: 'domcontentloaded', timeout: 15000 })
          } else {
            const target = page.locator(step.selector)
            if (step.action === 'fill') await target.fill(step.value, { timeout: 10000 })
            else if (step.action === 'click') await target.click({ timeout: 10000 })
            else if (step.action === 'visible') await target.waitFor({ state: 'visible', timeout: 10000 })
            else if (step.action === 'hidden') await target.waitFor({ state: 'hidden', timeout: 10000 })
            else if (step.action === 'text') {
              await target.filter({ hasText: step.value }).waitFor({ state: 'visible', timeout: 10000 })
            } else throw new Error('unknown_browser_action')
          }
        }
        if (errors.length) throw new Error('browser_application_error')
        receipts.push({ id: scenario.id, passed: true, steps: scenario.steps.length, real_browser: true, browser_os_sandbox: true })
      } finally { await context.close() }
    }
    process.stdout.write(JSON.stringify({ passed: true, checks: receipts }))
  } finally { await browser.close() }
}
main().catch(error => { process.stderr.write(error instanceof Error ? error.name : 'BrowserCheckError'); process.exitCode = 1 })
