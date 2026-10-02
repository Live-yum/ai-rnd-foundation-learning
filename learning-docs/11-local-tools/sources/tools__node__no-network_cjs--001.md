# tools/node/no-network.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Node索引运行边界。** package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。

**对应关系：** 先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/no-network.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L20。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`948`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/no-network.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "03c704db1a7b4aad522555f50eaa18991dee8024395d024aeb7fb147089cd907"} -->
````javascript
// tools/node/no-network.cjs
// Fail closed for network APIs used by these trusted local tools. Not a hostile-JS sandbox.
const deny = () => { throw new Error('RND local tool network access is disabled'); };
const net = require('node:net');
net.connect = net.createConnection = deny;
net.Socket.prototype.connect = deny;
require('node:tls').connect = deny;
require('node:dgram').createSocket = deny;
for (const kind of ['node:http', 'node:https']) {
  const module = require(kind); module.request = module.get = deny;
}
require('node:http2').connect = deny;
const dns = require('node:dns');
for (const key of Object.keys(dns)) {
  if (/^(lookup|resolve|reverse)/.test(key) && typeof dns[key] === 'function') dns[key] = deny;
}
for (const key of Object.keys(dns.promises)) {
  if (/^(lookup|resolve|reverse)/.test(key) && typeof dns.promises[key] === 'function') dns.promises[key] = deny;
}
globalThis.fetch = async () => deny();
require('node:module').syncBuiltinESMExports();
````
