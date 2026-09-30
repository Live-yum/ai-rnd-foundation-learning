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
