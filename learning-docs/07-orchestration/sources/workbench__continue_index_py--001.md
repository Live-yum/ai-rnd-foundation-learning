# workbench/continue_index.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：固定Continue全文索引组件的本机适配器。** bridge_identity校验源码与已编译工具；seed_cache把Tree-sitter分块转换为上游组件需要的表列。rank按索引身份原子重建并运行实际update/retrieve，再把结果限制在平台已验证的分块范围。缺少工具时报出安装命令，绝不连接云端替代。

**对应关系：** retrieval.query → continue_index → 固定Continue组件 → 独立本机SQLite缓存；test_continue_index。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `bridge_identity`（L31–L47）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Reject missing/stale compiled tools; never download dependencies during a query.。 控制顺序：L36按`receipt["inputs"] != expected or receipt["revision"] != CONTINUE_REVISION or sha(NODE…`分支；L41抛异常，停止当前正常路径；L43抛异常，停止当前正常路径。 调用`json.loads`、`(NODE_ROOT / ".built/manifest.json").read_text`、`sha`、`ValueError`、`ToolFailure`、`digest`。 返回路径：L47的`digest(expected)`。
- `invoke`（L50–L72）：接收`request`、`folder`、`timeout`。 源码说明：Only the fixed registered executable is run, with no model keys or proxy env.。 控制顺序：L67按`not target.is_file() or target.stat().st_size > 100000`分支；L68抛异常，停止当前正常路径；L70按`result.get("passed") is not True or result.get("identity") != request["identity"]`分支；L71抛异常，停止当前正常路径。 调用`tempfile.TemporaryDirectory`、`Path`、`write_json`、`run_command`、`str`、`target.is_file`、`target.stat`、`ToolFailure`、`json.loads`等。 返回路径：L72的`result`。
- `seed_cache`（L75–L99）：接收`search`、`target`、`identity`。 源码说明：Translate our AST chunks to the upstream component's documented cache columns.。 调用`closing`、`sqlite3.connect`、`db.execute`、`source.execute`、`db.executemany`、`enumerate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `rank`（L102–L172）：接收`index_dir`、`index`、`expression`、`filter_paths`、`timeout`。 源码说明：Rebuild atomically on changed chunk identity, then query the real Continue engine.。 控制顺序：L109按`filter_paths is not None and not filter_paths`分支；L111按`filter_paths is not None and len(filter_paths) > 20000`分支；L112抛异常，停止当前正常路径；L115按`target.exists()`分支；L123按`not valid`分支；L166按`not isinstance(keys, list) or len(keys) > 80 or any(not isinstance(key, str) for key …`分支；L171抛异常，停止当前正常路径。 调用`Path`、`digest`、`search_identity`、`bridge_identity`、`len`、`ValueError`、`FileLock`、`str`、`target.exists`等。 返回路径：L110的`[]`；L172的`list(dict.fromkeys(keys))`。

</details>

**创建路径：** `workbench/continue_index.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L172。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6959`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/continue_index.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "42b57094f8a7b30537f26961d140b193d296510a525e0610dee1a5e38d719412"} -->
````python
# workbench/continue_index.py
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
````
