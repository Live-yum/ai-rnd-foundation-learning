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
