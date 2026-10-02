# tools/node/build.mjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Node索引运行边界。** package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。

**对应关系：** 先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/build.mjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L43。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2178`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/build.mjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e4efeec6a1e868740407c62f3e9b21a71557162c858a3f12532a31512ec43c96"} -->
````javascript
// tools/node/build.mjs
// Compile the unmodified, licensed Continue index with explicit local host adapters.
import { build } from 'esbuild';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const hash = (data, kind = 'sha256') => createHash(kind).update(data).digest('hex');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'upstream/manifest.json'), 'utf8'));
for (const [name, expected] of Object.entries(manifest.files)) {
  const data = fs.readFileSync(path.join(root, 'upstream', name));
  const blob = Buffer.concat([Buffer.from(`blob ${data.length}\0`), data]);
  if (hash(data) !== expected.sha256 || hash(blob, 'sha1') !== expected.git_blob_sha1) {
    throw new Error(`Pinned Continue source integrity mismatch: ${name}`);
  }
}
const output = path.join(root, '.built');
fs.mkdirSync(output, { recursive: true });
await build({
  entryPoints: [path.join(root, 'continue-runner.mjs')],
  bundle: true,
  platform: 'node',
  target: 'node22',
  format: 'cjs',
  outfile: path.join(output, 'continue.cjs'),
  plugins: [{
    name: 'explicit-local-continue-host',
    setup(builder) {
      builder.onResolve({ filter: /^\.\.?\// }, (args) => {
        if (args.importer.endsWith('upstream/FullTextSearchCodebaseIndex.ts') || args.importer.endsWith('upstream\\FullTextSearchCodebaseIndex.ts')) {
          return { path: path.join(root, 'continue-host.mjs') };
        }
        return null;
      });
    },
  }],
});
const inputs = {};
for (const name of ['package.json', 'package-lock.json', 'build.mjs', 'continue-runner.mjs', 'continue-host.mjs', 'no-network.cjs', 'upstream/manifest.json', 'upstream/FullTextSearchCodebaseIndex.ts', 'upstream/LICENSE']) {
  inputs[name] = hash(fs.readFileSync(path.join(root, name)));
}
fs.writeFileSync(path.join(output, 'manifest.json'), JSON.stringify({ inputs, output_sha256: hash(fs.readFileSync(path.join(output, 'continue.cjs'))), revision: manifest.revision }, null, 2) + '\n');
console.log('Verified Continue source compiled locally; no index, source code or credentials uploaded.');
````
