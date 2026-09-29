"""AST chunks + SQLite FTS5; optional explicit embeddings and rank fusion.

The local index is shared by LangGraph and Continue via MCP. It is NOT Continue's
private indexing implementation. No API key is inherited from the coding model.
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
        base_url=settings.embedding_base_url,
        model=settings.embedding_model,
        api_key=settings.embedding_api_key,
    ).validate_endpoint()


def embed(profile, texts, transport=None):
    if not texts or len(texts) > 32 or sum(map(len, texts)) > 100000:
        raise ValueError("embedding 输入超出批次预算")
    with httpx.Client(
        timeout=60, trust_env=False, follow_redirects=False, transport=transport
    ) as client:
        with client.stream(
            "POST",
            profile.base_url.rstrip("/") + "/embeddings",
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
    if profile is None or not settings.embedding_allow_upload:
        raise ValueError(
            "向量索引需要 EMBEDDING_MODE/BASE_URL/API_KEY 和 EMBEDDING_ALLOW_UPLOAD=true"
        )
    with FileLock(str(Path(index_dir) / "search.lock"), timeout=60):
        with closing(sqlite3.connect(Path(index_dir) / "search.sqlite3")) as db, db:
            rows = db.execute(
                "SELECT id,content FROM chunks WHERE id NOT IN "
                "(SELECT id FROM vectors WHERE profile=?) ORDER BY id",
                (profile_id(profile),),
            ).fetchall()
            if len(rows) > settings.embedding_max_chunks:
                raise ValueError("本次待嵌入分块超出 EMBEDDING_MAX_CHUNKS；未调用收费接口")
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
        profile = embedding_profile(settings) if settings else None
        if profile and settings.embedding_allow_upload:
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
