# scripts/capability_browser_apparmor.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_browser_apparmor.；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/capability_browser_apparmor.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L15。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`622`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_browser_apparmor.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f65a9695f879d21e87760b8d20b546e2bea39ecde83b9cb0b7586cf5c41b795e"} -->
````javascript
// scripts/capability_browser_apparmor.cjs
// Read the kernel's actual current label before any candidate/browser work.
const fs = require('node:fs')
function requireAppArmor(api = fs) {
  const fd = api.openSync('/proc/self/attr/current', 'r')
  const buffer = Buffer.alloc(128)
  try {
    const size = api.readSync(fd, buffer, 0, buffer.length, 0)
    const label = buffer.subarray(0, size)
    if (!label.equals(Buffer.from('docker-default (enforce)')) && !label.equals(Buffer.from('docker-default (enforce)\n'))) {
      throw new Error('worker_apparmor_not_enforced')
    }
  } finally { api.closeSync(fd) }
  return true
}
module.exports = {requireAppArmor}
````
