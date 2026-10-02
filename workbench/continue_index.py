"""Actual pinned Continue FTS component with a local SQLite host, not an IDE emulator."""

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
    "package.json",
    "package-lock.json",
    "build.mjs",
    "continue-runner.mjs",
    "continue-host.mjs",
    "no-network.cjs",
    "upstream/manifest.json",
    "upstream/FullTextSearchCodebaseIndex.ts",
    "upstream/LICENSE",
)


def bridge_identity():
    """Reject missing/stale compiled tools; never download dependencies during a query."""
    try:
        receipt = json.loads((NODE_ROOT / ".built/manifest.json").read_text(encoding="utf-8"))
        expected = {name: sha(NODE_ROOT / name) for name in INPUTS}
        if (
            receipt["inputs"] != expected
            or receipt["revision"] != CONTINUE_REVISION
            or sha(NODE_ROOT / ".built/continue.cjs") != receipt["output_sha256"]
        ):
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
            [
                "node",
                "--require",
                str(NODE_ROOT / "no-network.cjs"),
                str(NODE_ROOT / ".built/continue.cjs"),
                str(source),
                str(target),
            ],
            NODE_ROOT,
            timeout,
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
        db.execute(
            "CREATE TABLE chunks(id INTEGER PRIMARY KEY,source_id TEXT UNIQUE NOT NULL,"
            "path TEXT NOT NULL,cacheKey TEXT NOT NULL,content TEXT NOT NULL,"
            '"index" INTEGER NOT NULL,startLine INTEGER NOT NULL,endLine INTEGER NOT NULL)'
        )
        db.execute(
            "CREATE TABLE chunk_tags(chunkId INTEGER NOT NULL,tag TEXT NOT NULL,UNIQUE(chunkId,tag))"
        )
        rows = source.execute(
            "SELECT id,path,sha256,content,start,end FROM chunks ORDER BY path,start"
        )
        db.executemany(
            'INSERT INTO chunks(source_id,path,cacheKey,content,"index",startLine,endLine) VALUES(?,?,?,?,?,?,?)',
            (
                (key, path, checksum, content, i, first, last)
                for i, (key, path, checksum, content, first, last) in enumerate(rows)
            ),
        )
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
                    valid = db.execute(
                        "SELECT value FROM meta WHERE key='identity'"
                    ).fetchone() == (identity,)
                except sqlite3.DatabaseError:
                    valid = False
        if not valid:
            with tempfile.NamedTemporaryFile(
                dir=folder, suffix=".sqlite3", delete=False
            ) as temporary:
                filename = Path(temporary.name)
            try:
                seed_cache(folder / "search.sqlite3", filename, identity)
                receipt = invoke(
                    {
                        "operation": "build",
                        "database": str(filename.resolve()),
                        "identity": identity,
                    },
                    folder,
                    timeout,
                )
                filename.replace(target)
                write_json(
                    folder / "continue-index.json",
                    {
                        **receipt,
                        "revision": CONTINUE_REVISION,
                        "source_digest": index["source_digest"],
                        "network": "disabled",
                        "host": "local-node-sqlite",
                        "model_calls": 0,
                    },
                )
            finally:
                filename.unlink(missing_ok=True)
        result = invoke(
            {
                "operation": "query",
                "database": str(target.resolve()),
                "identity": identity,
                "text": expression,
                "filterPaths": filter_paths,
                "limit": 80,
            },
            folder,
            timeout,
        )
    keys = result.get("ids")
    if (
        not isinstance(keys, list)
        or len(keys) > 80
        or any(not isinstance(key, str) for key in keys)
    ):
        raise ToolFailure("Continue返回了无效检索结果")
    return list(dict.fromkeys(keys))
