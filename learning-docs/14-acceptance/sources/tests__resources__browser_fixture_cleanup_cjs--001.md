# tests/resources/browser_fixture_cleanup.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/resources/browser_fixture_cleanup.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L21。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1152`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/resources/browser_fixture_cleanup.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "25667ba67491caf2ed0925a5ec40a4d9a70c1ddc71fe7e813ae6e36bbb4c6036"} -->
````javascript
// tests/resources/browser_fixture_cleanup.cjs
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
````
