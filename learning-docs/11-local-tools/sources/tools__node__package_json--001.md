# tools/node/package.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Node索引运行边界。** package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。

**对应关系：** 先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/package.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L16。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`268`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/package.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "30be8c89f1f1350a9ac9a9ed030780819f49c120a8d07110cb3e4a8630684877"} -->
````json
// tools/node/package.json
{
  "name": "rnd-local-node-tools",
  "private": true,
  "type": "module",
  "version": "1.0.0",
  "dependencies": {
    "esbuild": "0.25.9",
    "node-plop": "0.32.3"
  },
  "engines": {
    "node": ">=22.13.0"
  },
  "scripts": {
    "build": "node build.mjs"
  }
}
````
