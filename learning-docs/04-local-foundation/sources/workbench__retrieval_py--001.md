# workbench/retrieval.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机代码检索及可选本机向量融合。** chunks给片段附上文件和行号，FTS5负责关键词排序。query先核对源码摘要，防止返回过期行号，再应用路径/扩展名与预算限制；启用本机embedding时以独立配置生成和复用向量，采用倒数排名融合而非直接相加不同尺度的分数。

**对应关系：** toolchain/context_mcp → query → 本机SQLite；add_embeddings → 本机模型服务；test_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `terms`（L29–L31）：接收`value`。 调用`re.sub`、`list`、`dict.fromkeys`、`re.findall`。 返回路径：L31的`list(dict.fromkeys(re.findall(r"[\w]+", value + " " + expanded, re.UNICODE)))[:40]`。
- `chunks`（L34–L72）：接收`source`、`index`。 控制顺序：L36遍历`sorted(index["files"].items())`；L37按`Path(name).suffix not in CODE_SUFFIXES or entry["bytes"] > 2_000_000`分支；L49在`first <= len(lines)`成立时循环；L51按`last < len(lines)`分支；L53按`boundary >= first + 39`分支；L57遍历`spans`；L61按`count > MAX_CHUNKS`分支；L62抛异常，停止当前正常路径。 调用`sorted`、`index["files"].items`、`Path`、`inside`、`path.read_text(encoding="utf-8").splitlines`、`path.read_text`、`len`、`min`、`bisect_right`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `search_identity`（L75–L83）：接收`index`。 调用`digest`。 返回路径：L76的`digest( { "source": index["source_digest"], "schema": index["schema"], "parsers": index["p…`。
- `write_search_index`（L86–L132）：接收`source`、`output`、`index`。 控制顺序：L90按`target.exists()`分支；L94按`old and old[0] == search_identity(index)`分支；L117按`target.exists()`分支。 调用`Path`、`FileLock`、`str`、`target.exists`、`closing`、`sqlite3.connect`、`db.execute("SELECT value FROM meta WHERE key='identity'").fetchon…`、`db.execute`、`search_identity`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `current_index`（L135–L139）：接收`source`、`index_dir`。 控制顺序：L137按`digest(manifest(source)) != index["source_digest"]`分支；L138抛异常，停止当前正常路径。 调用`json.loads`、`(Path(index_dir) / "index.json").read_text`、`Path`、`digest`、`manifest`、`ValueError`。 返回路径：L139的`index`。
- `embedding_profile`（L142–L150）：接收`settings`。 控制顺序：L143按`not settings.embedding_model`分支。 调用`ModelProfile( stage="embedding", base_url=local_http_url(settings…`、`ModelProfile`、`local_http_url`。 返回路径：L144的`None`；L145的`ModelProfile( stage="embedding", base_url=local_http_url(settings.embedding_base_url, "向量服…`。
- `embed`（L153–L186）：接收`profile`、`texts`、`transport`。 控制顺序：L155按`not texts or len(texts) > 32 or sum(map(len, texts)) > 100000`分支；L156抛异常，停止当前正常路径；L168遍历`response.iter_bytes()`；L170按`len(body) > 4_000_000`分支；L171抛异常，停止当前正常路径；L173按`[r["index"] for r in rows] != list(range(len(texts)))`分支；L174抛异常，停止当前正常路径；L177按`not 1 <= dimension <= 8192`分支。后续分支沿下方源码相同行号继续阅读。 调用`local_http_url`、`len`、`sum`、`map`、`ValueError`、`httpx.Client`、`client.stream`、`endpoint.rstrip`、`profile.api_key.get_secret_value`等。 返回路径：L186的`vectors`。
- `profile_id`（L189–L190）：接收`profile`。 调用`digest`、`profile.base_url.rstrip`。 返回路径：L190的`digest({"url": profile.base_url.rstrip("/"), "model": profile.model})`。
- `add_embeddings`（L193–L223）：接收`source`、`index_dir`、`settings`、`transport`。 控制顺序：L196按`profile is None or not settings.embedding_enabled`分支；L197抛异常，停止当前正常路径；L207按`len(rows) > settings.embedding_max_chunks`分支；L208抛异常，停止当前正常路径；L209遍历`range(0, len(rows), 12)`。 调用`current_index`、`embedding_profile`、`ValueError`、`FileLock`、`str`、`Path`、`closing`、`sqlite3.connect`、`db.execute( "SELECT id,content FROM chunks WHERE id NOT IN " "(SE…`等。 返回路径：L219的`{ "embedded": len(rows), "profile": profile_id(profile), "provider": "explicit-embeddings"…`。
- `query`（L226–L348）：接收`source`、`index_dir`、`question`、`limit`、`max_chars`、`settings`、`transport`、`file_suffix`、`path_prefix`。 控制顺序：L237按`not question.strip() or len(question) > 2000 or not 1 <= limit <= 20 or not 100 <= ma…`分支；L243抛异常，停止当前正常路径；L246按`not words`分支；L247抛异常，停止当前正常路径；L248按`file_suffix and file_suffix not in CODE_SUFFIXES`分支；L249抛异常，停止当前正常路径；L250按`path_prefix`分支；L258按`db.execute("SELECT value FROM meta WHERE key='identity'").fetchone()[ 0 ] != search_i…`分支。后续分支沿下方源码相同行号继续阅读。 调用`question.strip`、`len`、`ValueError`、`current_index`、`terms`、`inside`、`Path(path_prefix).as_posix().rstrip`、`Path(path_prefix).as_posix`、`Path`等。 返回路径：L342的`{ "source_digest": index["source_digest"], "mode": mode, "matches": result, "chars": used,…`。
- `compact_map`（L351–L369）：接收`index_dir`、`max_chars`。 控制顺序：L354遍历`sorted(index["files"].items())`；L355遍历`entry["symbols"]`；L357按`used + len(line) + 1 > max_chars`分支。 调用`json.loads`、`(Path(index_dir) / "index.json").read_text`、`Path`、`sorted`、`index["files"].items`、`symbol.get`、`len`、`lines.append`、`"\n".join`等。 返回路径：L369的`result`。

</details>

**创建路径：** `workbench/retrieval.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L369。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15340`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/retrieval.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "83da454daf503b6ffe7c2d0be8b570dca955b081d17076aa31f092a25a522103"} -->
````python
# workbench/retrieval.py
"""AST chunks + SQLite FTS5; optional explicit embeddings and rank fusion.

The AST/vector index is shared by LangGraph and Continue via MCP. The optional
Continue engine runs its pinned upstream FTS component, with a separate local
host cache. No API key is inherited from the coding model.
"""

import json
import math
import re
import sqlite3
import tempfile
from bisect import bisect_right
from contextlib import closing
from pathlib import Path

import httpx
from filelock import FileLock

from workbench.domain import digest
from workbench.filesystem import inside, manifest, sha, write_json
from workbench.local_only import local_http_url
from workbench.settings import ModelProfile

CODE_SUFFIXES = {".py", ".java", ".ts", ".tsx", ".js", ".jsx", ".vue", ".sql", ".md"}
MAX_CHUNKS = 60000


def terms(value):
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return list(dict.fromkeys(re.findall(r"[\w]+", value + " " + expanded, re.UNICODE)))[:40]


def chunks(source, index):
    count = 0
    for name, entry in sorted(index["files"].items()):
        if Path(name).suffix not in CODE_SUFFIXES or entry["bytes"] > 2_000_000:
            continue
        path = inside(source, name)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeError:
            continue
        anchors = sorted({1, *(s["line"] for s in entry["symbols"])})
        # Pack adjacent declarations, preserving every line instead of making
        # a separate tiny chunk for every local variable in large Vue workspaces.
        spans = []
        first = 1
        while first <= len(lines):
            last = min(first + 59, len(lines))
            if last < len(lines):
                boundary = anchors[bisect_right(anchors, last + 1) - 1] - 1
                if boundary >= first + 39:
                    last = boundary
            spans.append((first, last))
            first = last + 1
        for first, last in spans:
            content = "\n".join(lines[first - 1 : last])[:8000]
            names = " ".join(s["name"] for s in entry["symbols"] if first <= s["line"] <= last)
            count += 1
            if count > MAX_CHUNKS:
                raise ValueError(f"索引分块超过{MAX_CHUNKS}，需缩小源码范围；没有静默漏掉文件")
            yield (
                digest([name, first, content]),
                name,
                first,
                last,
                entry["sha256"],
                names,
                content,
                " ".join(terms(names + " " + name)),
            )


def search_identity(index):
    return digest(
        {
            "source": index["source_digest"],
            "schema": index["schema"],
            "parsers": index["parsers"],
            "chunker": 2,
        }
    )


def write_search_index(source, output, index):
    output = Path(output)
    with FileLock(str(output / "search.lock"), timeout=60):
        target = output / "search.sqlite3"
        if target.exists():
            with closing(sqlite3.connect(target)) as db:
                try:
                    old = db.execute("SELECT value FROM meta WHERE key='identity'").fetchone()
                    if old and old[0] == search_identity(index):
                        return
                except sqlite3.DatabaseError:
                    pass
        with tempfile.NamedTemporaryFile(dir=output, suffix=".sqlite3", delete=False) as f:
            temporary = Path(f.name)
        try:
            with closing(sqlite3.connect(temporary)) as db, db:
                db.execute("CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                db.execute("INSERT INTO meta VALUES('source', ?)", (index["source_digest"],))
                db.execute("INSERT INTO meta VALUES('identity', ?)", (search_identity(index),))
                db.execute(
                    "CREATE TABLE chunks(id TEXT PRIMARY KEY,path TEXT,start INTEGER,"
                    "end INTEGER,sha256 TEXT,symbols TEXT,content TEXT,tokens TEXT)"
                )
                db.executemany("INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?)", chunks(source, index))
                db.execute(
                    "CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,path,symbols,content,tokens)"
                )
                db.execute("INSERT INTO search SELECT id,path,symbols,content,tokens FROM chunks")
                db.execute(
                    "CREATE TABLE vectors(id TEXT PRIMARY KEY,profile TEXT,values_json TEXT)"
                )
                if target.exists():
                    with closing(sqlite3.connect(target)) as old_db:
                        try:
                            cached = old_db.execute(
                                "SELECT id,profile,values_json FROM vectors"
                            ).fetchall()
                        except sqlite3.DatabaseError:
                            cached = []
                    valid = {row[0] for row in db.execute("SELECT id FROM chunks")}
                    db.executemany(
                        "INSERT INTO vectors VALUES(?,?,?)",
                        [row for row in cached if row[0] in valid],
                    )
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


def current_index(source, index_dir):
    index = json.loads((Path(index_dir) / "index.json").read_text(encoding="utf-8"))
    if digest(manifest(source)) != index["source_digest"]:
        raise ValueError("源码已改变，先重新执行 rnd index；拒绝使用过期检索结果")
    return index


def embedding_profile(settings):
    if not settings.embedding_model:
        return None
    return ModelProfile(
        stage="embedding",
        base_url=local_http_url(settings.embedding_base_url, "向量服务"),
        model=settings.embedding_model,
        api_key=settings.embedding_api_key,
    ).validate_endpoint()


def embed(profile, texts, transport=None):
    endpoint = local_http_url(profile.base_url, "向量服务")
    if not texts or len(texts) > 32 or sum(map(len, texts)) > 100000:
        raise ValueError("embedding 输入超出批次预算")
    with httpx.Client(
        timeout=60, trust_env=False, follow_redirects=False, transport=transport
    ) as client:
        with client.stream(
            "POST",
            endpoint.rstrip("/") + "/embeddings",
            headers={"Authorization": "Bearer " + profile.api_key.get_secret_value()},
            json={"model": profile.model, "input": texts},
        ) as response:
            response.raise_for_status()
            body = bytearray()
            for part in response.iter_bytes():
                body.extend(part)
                if len(body) > 4_000_000:
                    raise ValueError("embedding 响应过大")
    rows = sorted(json.loads(body)["data"], key=lambda row: row["index"])
    if [r["index"] for r in rows] != list(range(len(texts))):
        raise ValueError("embedding 响应索引不完整")
    vectors = [r["embedding"] for r in rows]
    dimension = len(vectors[0])
    if not 1 <= dimension <= 8192:
        raise ValueError("embedding 维数无效")
    for vector in vectors:
        if len(vector) != dimension or any(
            type(x) not in (float, int) or not math.isfinite(x) for x in vector
        ):
            raise ValueError("embedding 不是有限且等维的数值向量")
        if not sum(x * x for x in vector):
            raise ValueError("embedding 不接受零向量")
    return vectors


def profile_id(profile):
    return digest({"url": profile.base_url.rstrip("/"), "model": profile.model})


def add_embeddings(source, index_dir, settings, transport=None):
    current_index(source, index_dir)
    profile = embedding_profile(settings)
    if profile is None or not settings.embedding_enabled:
        raise ValueError(
            "向量索引需要 本机EMBEDDING_BASE_URL、EMBEDDING_MODE 和 EMBEDDING_ENABLED=true"
        )
    with FileLock(str(Path(index_dir) / "search.lock"), timeout=60):
        with closing(sqlite3.connect(Path(index_dir) / "search.sqlite3")) as db, db:
            rows = db.execute(
                "SELECT id,content FROM chunks WHERE id NOT IN "
                "(SELECT id FROM vectors WHERE profile=?) ORDER BY id",
                (profile_id(profile),),
            ).fetchall()
            if len(rows) > settings.embedding_max_chunks:
                raise ValueError("本次待嵌入分块超出 EMBEDDING_MAX_CHUNKS；未调用本机向量模型")
            for start in range(0, len(rows), 12):
                batch = rows[start : start + 12]
                values = embed(profile, [row[1] for row in batch], transport)
                db.executemany(
                    "INSERT OR REPLACE INTO vectors VALUES(?,?,?)",
                    [
                        (row[0], profile_id(profile), json.dumps(value))
                        for row, value in zip(batch, values, strict=True)
                    ],
                )
    return {
        "embedded": len(rows),
        "profile": profile_id(profile),
        "provider": "explicit-embeddings",
    }


def query(
    source,
    index_dir,
    question,
    limit=8,
    max_chars=12000,
    settings=None,
    transport=None,
    file_suffix="",
    path_prefix="",
):
    if (
        not question.strip()
        or len(question) > 2000
        or not 1 <= limit <= 20
        or not 100 <= max_chars <= 60000
    ):
        raise ValueError("检索参数超出范围")
    index = current_index(source, index_dir)
    words = terms(question)
    if not words:
        raise ValueError("查询需要至少一个关键词")
    if file_suffix and file_suffix not in CODE_SUFFIXES:
        raise ValueError("不支持的源码文件类型")
    if path_prefix:
        inside(source, path_prefix)
        path_prefix = Path(path_prefix).as_posix().rstrip("/") + "/"
    path_clause = " AND substr(path,1,?)=? AND (?='' OR substr(path,-length(?))=?)"
    path_params = (len(path_prefix), path_prefix, file_suffix, file_suffix, file_suffix)
    expression = " OR ".join('"' + word.replace('"', '""') + '"' for word in words)
    with closing(sqlite3.connect(Path(index_dir) / "search.sqlite3")) as db, db:
        db.row_factory = sqlite3.Row
        if db.execute("SELECT value FROM meta WHERE key='identity'").fetchone()[
            0
        ] != search_identity(index):
            raise ValueError("符号索引与检索库版本不一致，请重建")
        # Keep the original identifiers ahead of camel-case fallback terms.
        # Otherwise short "use" / "form" declarations can displace real Hook usages.
        original_words = list(dict.fromkeys(re.findall(r"[\w]+", question, re.UNICODE)))[:40]
        exact_expression = " OR ".join(
            '"' + word.replace('"', '""') + '"' for word in original_words
        )
        exact = db.execute(
            "SELECT id FROM search WHERE search MATCH ?"
            + path_clause
            + " ORDER BY bm25(search) LIMIT 80",
            (exact_expression, *path_params),
        ).fetchall()
        expanded = db.execute(
            "SELECT id FROM search WHERE search MATCH ?"
            + path_clause
            + " ORDER BY bm25(search) LIMIT 80",
            (expression, *path_params),
        ).fetchall()
        lexical = list(dict.fromkeys(row[0] for row in [*exact, *expanded]))[:80]
        ranks = [lexical]
        mode = "ast+fts5"
        if settings and settings.retrieval_engine == "continue":
            from workbench.continue_index import rank

            scoped = None
            if file_suffix or path_prefix:
                scoped = [
                    row[0]
                    for row in db.execute(
                        "SELECT DISTINCT path FROM chunks WHERE 1=1" + path_clause, path_params
                    )
                ]
            native = rank(index_dir, index, exact_expression, scoped, settings.tool_timeout)
            valid_keys = {
                row[0]
                for row in db.execute("SELECT id FROM chunks WHERE 1=1" + path_clause, path_params)
            }
            if any(key not in valid_keys for key in native):
                raise ValueError("Continue检索结果超出已验证分块或路径范围")
            ranks.insert(0, native)
            mode = "ast+continue-fts5+fts5"
        profile = embedding_profile(settings) if settings else None
        if profile and settings.embedding_enabled:
            vectors = db.execute(
                "SELECT vectors.id,values_json FROM vectors JOIN chunks ON chunks.id=vectors.id WHERE profile=?"
                + path_clause,
                (profile_id(profile), *path_params),
            ).fetchall()
            if vectors:
                needle = embed(profile, [question], transport)[0]
                norm = math.sqrt(sum(x * x for x in needle))
                scored = []
                for row in vectors:
                    value = json.loads(row[1])
                    if len(value) != len(needle):
                        raise ValueError("embedding 模型维度已变化，请重建向量索引")
                    score = sum(x * y for x, y in zip(value, needle, strict=True)) / (
                        norm * math.sqrt(sum(x * x for x in value))
                    )
                    scored.append((score, row[0]))
                ranks.append([key for _, key in sorted(scored, reverse=True)[:80]])
                mode += "+vector-rrf"
        scores = {}
        for ranking in ranks:
            for rank, key in enumerate(ranking, 1):
                scores[key] = scores.get(key, 0) + 1 / (60 + rank)
        result, used = [], 0
        for key in sorted(scores, key=lambda item: (-scores[item], item)):
            row = dict(db.execute("SELECT * FROM chunks WHERE id=?", (key,)).fetchone())
            if sha(inside(source, row["path"])) != row["sha256"]:
                raise ValueError("检索期间源码变化")
            row.pop("tokens")
            row["score"] = scores[key]
            size = len(json.dumps(row, ensure_ascii=False))
            if used + size > max_chars:
                continue
            result.append(row)
            used += size
            if len(result) == limit:
                break
    return {
        "source_digest": index["source_digest"],
        "mode": mode,
        "matches": result,
        "chars": used,
        "untrusted_source_context": True,
    }


def compact_map(index_dir, max_chars=12000):
    index = json.loads((Path(index_dir) / "index.json").read_text(encoding="utf-8"))
    lines, used, omitted = [], 0, 0
    for path, entry in sorted(index["files"].items()):
        for symbol in entry["symbols"]:
            line = f"{path}:{symbol['line']} {symbol.get('signature', symbol['name'])}"
            if used + len(line) + 1 > max_chars:
                omitted += 1
                continue
            lines.append(line)
            used += len(line) + 1
    result = {
        "provider": "local-symbol-map",
        "text": "\n".join(lines),
        "omitted_symbols": omitted,
        "source_digest": index["source_digest"],
    }
    write_json(Path(index_dir) / "repo-map.json", result)
    return result
````
