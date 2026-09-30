# Exact, reviewable UTF-8 source operations against verified commit c3d3c612.
PATCHES = {
    'tools/node/build.mjs': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''// Compile the unmodified, licensed Continue index with explicit local host adapters.
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
'''),
    ]),
    'tools/node/continue-host.mjs': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''// Host services for the actual Continue component; no Continue IDE/global-cache emulation.
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
'''),
    ]),
    'tools/node/continue-runner.mjs': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''// Fixed JSON-file protocol. Indexed source is data; it is never imported or executed.
import fs from 'node:fs';
import { FullTextSearchCodebaseIndex } from './upstream/FullTextSearchCodebaseIndex.ts';
import { openDatabase, closeDatabase, nativeHandle, ranking, tagToString } from './continue-host.mjs';
async function main() {
const [requestFile, outputFile] = process.argv.slice(2);
if (!requestFile || !outputFile || fs.statSync(requestFile).size > 16_000_000) throw new Error('Invalid local index request');
const request = JSON.parse(fs.readFileSync(requestFile, 'utf8'));
if (!['build', 'query'].includes(request.operation) || !/^[a-f0-9]{64}$/.test(request.identity)) throw new Error('Invalid index operation or identity');
const tag = { directory: 'rnd-source', branch: request.identity, artifactId: 'sqliteFts' };
let response;
openDatabase(request.database, request.operation === 'query');
try {
  const db = nativeHandle();
  if (db.prepare("SELECT value FROM meta WHERE key='identity'").get()?.value !== request.identity) throw new Error('Continue cache identity mismatch');
  const index = new FullTextSearchCodebaseIndex();
  if (request.operation === 'build') {
    const items = db.prepare('SELECT DISTINCT path,cacheKey FROM chunks ORDER BY path').all();
    let completed = 0;
    db.exec('BEGIN');
    try {
      const addTag = db.prepare('INSERT INTO chunk_tags(chunkId,tag) SELECT id,? FROM chunks');
      addTag.run(tagToString({ ...tag, artifactId: 'chunks' }));
      const results = { compute: items, addTag: [], removeTag: [], del: [] };
      for await (const progress of index.update(tag, results, async (rows) => { completed += rows.length; }, undefined)) {
        if (progress.status !== 'indexing') throw new Error('Unexpected Continue indexing status');
      }
      const chunks = Number(db.prepare('SELECT COUNT(*) AS n FROM chunks').get().n);
      const indexed = Number(db.prepare('SELECT COUNT(*) AS n FROM fts_metadata').get().n);
      if (chunks !== indexed || completed !== items.length) throw new Error('Continue omitted source chunks');
      db.exec('COMMIT');
      response = { passed: true, files: completed, chunks: indexed, engine: 'Continue.FullTextSearchCodebaseIndex', identity: request.identity };
    } catch (error) { db.exec('ROLLBACK'); throw error; }
  } else {
    if (typeof request.text !== 'string' || request.text.length > 10000 || !Number.isInteger(request.limit) || request.limit < 1 || request.limit > 80) throw new Error('Invalid retrieval budget');
    if (request.filterPaths && (!Array.isArray(request.filterPaths) || request.filterPaths.length > 20000 || request.filterPaths.some((value) => typeof value !== 'string'))) throw new Error('Invalid retrieval path scope');
    const rows = await index.retrieve({ tags: [tag], text: request.text, n: request.limit, bm25Threshold: 0, filterPaths: request.filterPaths });
    const locate = db.prepare('SELECT id,source_id FROM chunks WHERE path=? AND cacheKey=? AND startLine=? AND endLine=?');
    const hits = rows.map((row) => {
      const result = locate.get(row.filepath, row.digest, row.startLine, row.endLine);
      if (!result) throw new Error('Continue returned a chunk outside the approved cache');
      return { id: result.source_id, position: ranking().indexOf(Number(result.id)) };
    });
    if (hits.some((row) => row.position < 0)) throw new Error('Continue result was not ranked by FTS');
    // retrieve() fetches chunks with an IN clause, which does not retain SQL rank order.
    // Restore the exact order produced by its own BM25 query, not a second ranking model.
    hits.sort((a, b) => a.position - b.position);
    response = { passed: true, ids: hits.map((row) => row.id), engine: 'Continue.FullTextSearchCodebaseIndex', identity: request.identity };
  }
} finally { closeDatabase(); }
fs.writeFileSync(outputFile, JSON.stringify(response), { encoding: 'utf8', flag: 'wx', mode: 0o600 });

}
main().catch((error) => { console.error(error.message); process.exitCode = 1; });
'''),
    ]),
    'tools/node/no-network.cjs': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''// Fail closed for network APIs used by these trusted local tools. Not a hostile-JS sandbox.
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
'''),
    ]),
    'tools/node/package.json': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''{
  "name": "rnd-local-node-tools",
  "private": true,
  "type": "module",
  "version": "1.0.0",
  "dependencies": {
    "esbuild": "0.25.9"
  },
  "engines": {
    "node": ">=22.13.0"
  },
  "scripts": {
    "build": "node build.mjs"
  }
}
'''),
    ]),
    'tools/node/upstream/manifest.json': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''{
  "repository": "https://github.com/continuedev/continue",
  "revision": "5522c6f44ca0ac3528b37244818fbfa39b5af470",
  "files": {
    "FullTextSearchCodebaseIndex.ts": {
      "path": "core/indexing/FullTextSearchCodebaseIndex.ts",
      "git_blob_sha1": "8016d04d3eddc84ec48ffa517ba96b2caba9b14e",
      "sha256": "ef2e80c7db63f3148fe8894f2ea4fbd23e57148f2f33b7cec55620c51ec16c60"
    },
    "LICENSE": {
      "path": "LICENSE",
      "git_blob_sha1": "c25dc1768217ba50d454fcc06290d66886512872",
      "sha256": "b14a17598cb08c4c7c82c070731126304e0a75d001ed59fb9ea3955a0b561802"
    }
  }
}
'''),
    ]),
    'workbench/continue_index.py': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''"""Actual pinned Continue FTS component with a local SQLite host, not an IDE emulator."""

import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from filelock import FileLock

from workbench.domain import digest
from workbench.filesystem import sha, write_json
from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command

CONTINUE_REVISION = "5522c6f44ca0ac3528b37244818fbfa39b5af470"
NODE_ROOT = ROOT / "tools/node"
INPUTS = (
    "package.json", "package-lock.json", "build.mjs", "continue-runner.mjs",
    "continue-host.mjs", "no-network.cjs", "upstream/manifest.json",
    "upstream/FullTextSearchCodebaseIndex.ts", "upstream/LICENSE",
)


def bridge_identity():
    """Reject missing/stale compiled tools; never download dependencies during a query."""
    try:
        receipt = json.loads((NODE_ROOT / ".built/manifest.json").read_text(encoding="utf-8"))
        expected = {name: sha(NODE_ROOT / name) for name in INPUTS}
        if (receipt["inputs"] != expected or receipt["revision"] != CONTINUE_REVISION
                or sha(NODE_ROOT / ".built/continue.cjs") != receipt["output_sha256"]):
            raise ValueError("stale build")
    except (OSError, KeyError, ValueError) as exc:
        raise ToolFailure(
            "Continue本机组件缺失或过期；在仓库根目录执行 npm ci --prefix tools/node --no-audit --no-fund "
            "与 npm run build --prefix tools/node；需要Node 22.13或更高版本"
        ) from exc
    return digest(expected)


def invoke(request, folder, timeout):
    """Only the fixed registered executable is run, with no model keys or proxy env."""
    with tempfile.TemporaryDirectory(prefix="continue-request-", dir=folder) as temp:
        source, target = Path(temp) / "request.json", Path(temp) / "result.json"
        write_json(source, request)
        run_command(
            ["node", "--require", str(NODE_ROOT / "no-network.cjs"),
             str(NODE_ROOT / ".built/continue.cjs"), str(source), str(target)],
            NODE_ROOT, timeout,
        )
        if not target.is_file() or target.stat().st_size > 100000:
            raise ToolFailure("Continue本机索引没有返回有界回执")
        result = json.loads(target.read_text(encoding="utf-8"))
        if result.get("passed") is not True or result.get("identity") != request["identity"]:
            raise ToolFailure("Continue回执与当前源码索引不一致")
        return result


def seed_cache(search, target, identity):
    """Translate our AST chunks to the upstream component's documented cache columns."""
    with closing(sqlite3.connect(search)) as source, closing(sqlite3.connect(target)) as db, db:
        db.execute("CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        db.execute("INSERT INTO meta VALUES('identity',?)", (identity,))
        db.execute('CREATE TABLE chunks(id INTEGER PRIMARY KEY,source_id TEXT UNIQUE NOT NULL,'
                   'path TEXT NOT NULL,cacheKey TEXT NOT NULL,content TEXT NOT NULL,'
                   '"index" INTEGER NOT NULL,startLine INTEGER NOT NULL,endLine INTEGER NOT NULL)')
        db.execute("CREATE TABLE chunk_tags(chunkId INTEGER NOT NULL,tag TEXT NOT NULL,UNIQUE(chunkId,tag))")
        rows = source.execute("SELECT id,path,sha256,content,start,end FROM chunks ORDER BY path,start")
        db.executemany('INSERT INTO chunks(source_id,path,cacheKey,content,"index",startLine,endLine) VALUES(?,?,?,?,?,?,?)',
                       ((key, path, checksum, content, i, first, last)
                        for i, (key, path, checksum, content, first, last) in enumerate(rows)))
        db.execute("CREATE INDEX chunks_file ON chunks(path,cacheKey)")
        db.execute("CREATE INDEX chunk_tags_tag ON chunk_tags(tag)")


def rank(index_dir, index, expression, filter_paths, timeout=180):
    """Rebuild atomically on changed chunk identity, then query the real Continue engine."""
    from workbench.retrieval import search_identity

    folder = Path(index_dir)
    identity = digest([search_identity(index), bridge_identity(), "continue-host-v1"])
    target = folder / "continue.sqlite3"
    if filter_paths is not None and not filter_paths:
        return []  # Upstream treats an empty filter as no filter; never broaden caller scope.
    if filter_paths is not None and len(filter_paths) > 20000:
        raise ValueError("Continue路径筛选超过20000个文件，请缩小索引；没有静默扩大范围")
    with FileLock(str(folder / "continue.lock"), timeout=60):
        valid = False
        if target.exists():
            with closing(sqlite3.connect(target)) as db:
                try:
                    valid = db.execute("SELECT value FROM meta WHERE key='identity'").fetchone() == (identity,)
                except sqlite3.DatabaseError:
                    valid = False
        if not valid:
            with tempfile.NamedTemporaryFile(dir=folder, suffix=".sqlite3", delete=False) as temporary:
                filename = Path(temporary.name)
            try:
                seed_cache(folder / "search.sqlite3", filename, identity)
                receipt = invoke({"operation": "build", "database": str(filename.resolve()), "identity": identity}, folder, timeout)
                filename.replace(target)
                write_json(folder / "continue-index.json", {
                    **receipt, "revision": CONTINUE_REVISION,
                    "source_digest": index["source_digest"], "network": "disabled",
                    "host": "local-node-sqlite", "model_calls": 0,
                })
            finally:
                filename.unlink(missing_ok=True)
        result = invoke({"operation": "query", "database": str(target.resolve()), "identity": identity,
                         "text": expression, "filterPaths": filter_paths, "limit": 80}, folder, timeout)
    keys = result.get("ids")
    if not isinstance(keys, list) or len(keys) > 80 or any(not isinstance(key, str) for key in keys):
        raise ToolFailure("Continue返回了无效检索结果")
    return list(dict.fromkeys(keys))
'''),
    ]),
    'workbench/retrieval.py': ('33faa01ae8362be903b8694d4836fb02418fe628a70510dd69dbf14616124deb', [
        (2, 4, r'''The AST/vector index is shared by LangGraph and Continue via MCP. The optional
Continue engine runs its pinned upstream FTS component, with a separate local
host cache. No API key is inherited from the coding model.
'''),
        (281, 281, r'''        if settings and settings.retrieval_engine == "continue":
            from workbench.continue_index import rank

            scoped = None
            if file_suffix or path_prefix:
                scoped = [row[0] for row in db.execute(
                    "SELECT DISTINCT path FROM chunks WHERE 1=1" + path_clause, path_params
                )]
            native = rank(index_dir, index, exact_expression, scoped, settings.tool_timeout)
            valid_keys = {row[0] for row in db.execute("SELECT id FROM chunks WHERE 1=1" + path_clause, path_params)}
            if any(key not in valid_keys for key in native):
                raise ValueError("Continue检索结果超出已验证分块或路径范围")
            ranks.insert(0, native)
            mode = "ast+continue-fts5+fts5"
'''),
    ]),
    'workbench/settings.py': ('b31051f5cef3e2ed3d97b1dd0135043b46ecaafdbc66adb1d2f33e19dcbebf2c', [
        (95, 95, r'''    retrieval_engine: Literal["local", "continue"] = "local"
'''),
    ]),
}
