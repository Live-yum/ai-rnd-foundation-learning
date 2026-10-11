// Test-fixture lifecycle only. A failed close must leave Node alive for its
// Python owner to terminate the owned tree, rather than orphaning Chromium.
async function cleanupFixture({ browser, context, services, stage, deadline }) {
  const ownership = setInterval(() => {}, 1000);
  const remaining = () => Math.max(1, deadline - Date.now());
  // Stop serving before closing the context; release in-flight HTTP sockets too.
  const servers = services.map(([service, name]) => stage(name + '-cleanup', () =>
    new Promise((resolve, reject) => {
      service.close(error => error && error.code !== 'ERR_SERVER_NOT_RUNNING' ? reject(error) : resolve());
      service.closeAllConnections();
    }), remaining()));
  const browserCleanup = stage('browser-cleanup', async () => {
    if (context) await context.close();
    if (browser) await browser.close();
  }, remaining());
  await Promise.all([...servers, browserCleanup]);
  // Clear only after every close succeeds. Timeout/rejection remains a failure,
  // and the unchanged outer deadline then invokes owned-tree recovery.
  clearInterval(ownership);
}
module.exports = { cleanupFixture };
