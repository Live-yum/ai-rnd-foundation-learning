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
