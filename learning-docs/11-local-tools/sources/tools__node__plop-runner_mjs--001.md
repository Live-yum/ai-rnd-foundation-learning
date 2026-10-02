# tools/node/plop-runner.mjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生业务规则的真实Plop生成入口与模板。** 固定node-plop执行受信任的add/modify动作，模板定义Python、Java、Vue之间一致的规则入口。请求只提供受校验数据；已有文件、锚点数量和生成集合都要匹配，不能执行用户脚本。

**对应关系：** workbench.scaffolding → no-network → plop-runner → 实际规则文件/表单挂载；native_coding接着验证候选。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/plop-runner.mjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L31。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2012`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/plop-runner.mjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9818fe45dbe3f330e7f98de8ec0b147a5dad0ad251a82af5f4c2b85353229f50"} -->
````javascript
// tools/node/plop-runner.mjs
// Actual Plop actions, bounded to a disposable workspace by the Python adapter.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import nodePlop from 'node-plop';
import { fileURLToPath } from 'node:url';
const installed = JSON.parse(fs.readFileSync(new URL('./node_modules/node-plop/package.json', import.meta.url), 'utf8'));
assert.equal(installed.version, '0.32.3', 'Use the pinned local node-plop dependency');
const here = path.dirname(fileURLToPath(import.meta.url));
const [requestPath, output] = process.argv.slice(2);
const data = JSON.parse(fs.readFileSync(requestPath, 'utf8'));
assert(data.actions.length > 0 && data.actions.length <= 64);
const plop = await nodePlop(undefined, { destBasePath: output, force: false });
const actions = data.actions.map(item => {
  assert(/^[a-zA-Z0-9_./-]+$/.test(item.path) && !item.path.split('/').includes('..'));
  const target = path.resolve(output, item.path);
  assert(target.startsWith(path.resolve(output) + path.sep));
  if (item.type === 'add') {
    assert(['rule.py.hbs', 'rule.java.hbs', 'rule.vue.hbs'].includes(item.template));
    return { type: 'add', path: item.path, templateFile: path.join(here, 'templates', item.template), data: item.data };
  }
  assert.equal(item.type, 'modify');
  const source = fs.readFileSync(target, 'utf8');
  assert(item.before && source.split(item.before).length === 2, 'Plop anchor must match exactly once');
  return { type: 'modify', path: item.path, transform: body => body.replace(item.before, item.after) };
});
plop.setGenerator('native-business-rules', { description: 'Native rule scaffold', prompts: [], actions });
const result = await plop.getGenerator('native-business-rules').runActions({});
assert.equal(result.failures.length, 0, JSON.stringify(result.failures));
assert.equal(result.changes.length, actions.length);
console.log(JSON.stringify({ engine: 'node-plop', version: installed.version, actions: result.changes.length, network: 'disabled' }));
````
