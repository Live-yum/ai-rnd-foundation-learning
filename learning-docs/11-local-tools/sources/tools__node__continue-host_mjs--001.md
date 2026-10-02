# tools/node/continue-host.mjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Node索引运行边界。** package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。

**对应关系：** 先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/continue-host.mjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L41。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1982`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/continue-host.mjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "305f5e1d1a7784069da7a047fa2a52173f2c2e1eb4455743292c9eb4ca721b93"} -->
````javascript
// tools/node/continue-host.mjs
// Host services for the actual Continue component; no Continue IDE/global-cache emulation.
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
let handle;
let rankIds = [];
export const RETRIEVAL_PARAMS = { bm25Threshold: 0 };
export const ChunkCodebaseIndex = { artifactId: 'chunks' };
export const IndexResultType = { Compute: 'compute', AddTag: 'addTag', RemoveTag: 'removeTag', Delete: 'delete' };
export const getUriPathBasename = (value) => path.basename(value);
export function tagToString(tag) {
  // Our tag uses a fixed short directory plus a digest, never a long filesystem URI.
  const result = `${tag.directory}::${tag.branch}::${tag.artifactId}`;
  if (result.length > 240) throw new Error('Local Continue tag exceeds its supported bound');
  return result;
}
export function openDatabase(filename, readonly) {
  if (handle) throw new Error('Only one local index per process');
  // The upstream FTS metadata refers to virtual tables; FK enforcement is inapplicable
  // to that cache schema. This never opens or modifies an application database.
  handle = new DatabaseSync(filename, { readOnly: readonly, enableForeignKeyConstraints: false });
}
export function closeDatabase() { if (handle) handle.close(); handle = undefined; }
export function nativeHandle() { return handle; }
export function ranking() { return rankIds; }
export const SqliteDb = {
  async get() {
    if (!handle) throw new Error('Local cache not opened');
    return {
      async exec(sql) { handle.exec(sql); },
      async all(sql, parameters = []) {
        const rows = handle.prepare(sql).all(...parameters);
        if (sql.includes('SELECT fts_metadata.chunkId')) rankIds = rows.map((row) => Number(row.chunkId));
        return rows;
      },
      async run(sql, parameters = []) {
        const result = handle.prepare(sql).run(...parameters);
        return { lastID: Number(result.lastInsertRowid), changes: Number(result.changes) };
      },
    };
  },
};
````
