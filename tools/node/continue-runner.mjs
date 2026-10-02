// Fixed JSON-file protocol. Indexed source is data; it is never imported or executed.
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
