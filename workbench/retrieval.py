"""Local AST/keyword/TF-IDF retrieval. No remote embeddings and no hidden model call."""

import json
import math
import re
from collections import Counter
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import inside, manifest, secret_name, write_json

# Extra exclusions affect context, not the pinned-template manifest algorithm.
BLOCKED_PARTS = {".continue", ".aider", ".ssh", ".aws", ".config"}


def allowed(name):
    path = Path(name)
    return not (
        secret_name(name)
        or set(path.parts) & BLOCKED_PARTS
        or any(p.startswith(".aider") for p in path.parts)
        or path.name in {"config.json", "settings.local.json"}
    )


def load_current(source, index_dir):
    from workbench.code_index import parser_identity
    from workbench.knowledge import INDEX_VERSION

    index = json.loads((Path(index_dir) / "index.json").read_text(encoding="utf-8"))
    if index.get("schema") != INDEX_VERSION or index.get("parsers") != parser_identity():
        raise ValueError("索引版本过期，请执行 rnd index 重建")
    current = manifest(source)
    if (
        index["source_digest"] != digest(current)
        or {n: e["sha256"] for n, e in index["files"].items()} != current
    ):
        raise ValueError("源码已变化，请重建知识包后查询")
    return index


def terms(text):
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return Counter(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", text.lower()))


def search(source, index_dir, query, limit=8, max_chars=12000):
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        raise ValueError("查询需要1到2000个字符")
    if not 1 <= limit <= 20 or not 500 <= max_chars <= 30000:
        raise ValueError("检索数量或字符预算超出允许范围")
    index = load_current(source, index_dir)
    docs, frequency = [], Counter()
    for name, entry in index["files"].items():
        if not allowed(name):
            continue
        for symbol in entry.get("symbols", []):
            if entry.get("parse_error"):
                continue  # Incomplete parses are diagnostics, not authoritative model context.
            words = terms(name + " " + symbol["name"] + " " + symbol.get("signature", ""))
            docs.append((name, entry, symbol, words))
            frequency.update(words.keys())
    q = terms(query)
    idf = {word: math.log(1 + (len(docs) + 1) / (frequency[word] + 1)) for word in q}
    ranks = []
    for name, entry, symbol, words in docs:
        overlap = set(q) & set(words)
        if not overlap:
            continue
        # Sparse lexical vector cosine; not advertised as neural semantic embeddings.
        dot = sum(q[t] * words[t] * idf[t] ** 2 for t in overlap)
        qnorm = math.sqrt(sum((q[t] * idf[t]) ** 2 for t in q))
        dnorm = math.sqrt(
            sum(
                (n * math.log(1 + (len(docs) + 1) / (frequency[t] + 1))) ** 2
                for t, n in words.items()
            )
        )
        cosine = dot / (qnorm * dnorm) if qnorm and dnorm else 0
        exact = 2 if symbol["name"].lower() in query.lower() else 0
        score = exact + len(overlap) / max(len(q), 1) + cosine
        ranks.append((score, name, entry, symbol))
    rows, used = [], 0
    for score, name, entry, symbol in sorted(ranks, key=lambda x: (-x[0], x[1], x[3]["line"])):
        start = symbol["line"]
        end = min(symbol["end_line"], start + 19)
        lines = inside(source, name).read_text(encoding="utf-8").splitlines()
        snippet = "\n".join(lines[start - 1 : end])
        item = {
            "path": name,
            "line": start,
            "end_line": end,
            "sha256": entry["sha256"],
            "symbol": symbol["name"],
            "score": round(score, 5),
            "content": snippet,
        }
        size = len(json.dumps(item, ensure_ascii=False))
        if used + size > max_chars:
            continue
        rows.append(item)
        used += size
        if len(rows) == limit:
            break
    return {
        "engine": "local-ast-keyword-tfidf",
        "source_digest": index["source_digest"],
        "results": rows,
        "budget_chars": max_chars,
        "untrusted_source": True,
    }


def symbol_map(source, index_dir, max_chars=12000):
    if not 100 <= max_chars <= 30000:
        raise ValueError("地图预算需要100到30000字符")
    index = load_current(source, index_dir)
    lines, used, omitted = [], 0, 0
    for name, entry in index["files"].items():
        if not allowed(name) or entry.get("parse_error"):
            continue
        for s in entry.get("symbols", []):
            line = f"{name}:{s['line']} {s['kind']} {s['name']}\n"
            if used + len(line) > max_chars:
                omitted += 1
                continue
            lines.append(line)
            used += len(line)
    return {
        "engine": "deterministic-symbol-map",
        "source_digest": index["source_digest"],
        "text": "".join(lines),
        "omitted_symbols": omitted,
    }


def template_context(settings, template, query, destination):
    """Called by planning: same pinned archives as generation, evidence outside the product."""
    from workbench.knowledge import build_index
    from workbench.settings import ROOT
    from workbench.vendor import prepare

    if template == "python-basic":
        root = ROOT / "templates/product"
        index = settings.data_dir / "knowledge/python-basic"
        build_index(root, index, "bundled-product")
        sources = [("product", root, index)]
    else:
        sources = [
            (
                r["slot"],
                Path(r["path"]),
                settings.data_dir / "knowledge" / template / r["slot"] / r["sha"],
            )
            for r in prepare(settings, template)
        ]
    result = {}
    for slot, root, index in sources:
        result[slot] = search(root, index, query[:2000], limit=4, max_chars=6000)
        result[slot]["map"] = symbol_map(root, index, 4000)
        if settings.repo_map_engine == "aider":
            from workbench.aider_tools import repo_map

            result[slot]["map"] = repo_map(root, settings)
    write_json(Path(destination) / "template-context.json", result)
    return result
