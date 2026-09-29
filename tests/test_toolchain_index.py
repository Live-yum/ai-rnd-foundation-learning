import json

import pytest

from workbench.code_index import extract
from workbench.continue_mcp import config, read_code
from workbench.filesystem import sha
from workbench.knowledge import build_index
from workbench.retrieval import search, symbol_map


def source_tree(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "ArticleController.java").write_text(
        "package demo;\nimport java.util.List;\n@RestController\npublic class ArticleController extends BaseController {\n"
        '  @TableField("title") private String title;\n'
        "  public String findTitle(String value) { return value; }\n}\n",
        encoding="utf-8",
    )
    (source / "hooks.ts").write_text(
        "export interface FormOptions { title: string }\n"
        "export function useArticleForm(options: FormOptions) { return options; }\n",
        encoding="utf-8",
    )
    (source / "Article.vue").write_text(
        '<template><VbenForm /></template>\n<script setup lang="ts">\n'
        "import { useArticleForm } from './hooks';\n"
        "const form = useArticleForm({ title: '新闻' });\n</script>\n",
        encoding="utf-8",
    )
    (source / ".env").write_text("API_KEY=do-not-read", encoding="utf-8")
    (source / ".continue").mkdir()
    (source / ".continue/secret.ts").write_text("export function SecretKey() {}", encoding="utf-8")
    index = tmp_path / "index"
    build_index(source, index)
    return source, index


def test_real_java_typescript_and_vue_script_offsets(tmp_path):
    source, index = source_tree(tmp_path)
    data = json.loads((index / "index.json").read_text(encoding="utf-8"))
    java = data["files"]["ArticleController.java"]
    assert not java.get("parse_error")
    names = {s["name"] for s in java["symbols"]}
    assert {"ArticleController", "findTitle", "RestController", "TableField", "title"} <= names
    assert java["imports"]
    vue = data["files"]["Article.vue"]
    assert not vue.get("parse_error")
    assert any(s["name"] == "VbenForm" and s["line"] == 1 for s in vue["symbols"])
    assert any(s["name"] == "form" and s["line"] == 4 for s in vue["symbols"])
    assert "useArticleForm" in vue["references"]
    result = search(source, index, "useArticleForm")
    assert result["results"] and result["engine"] == "local-ast-keyword-tfidf"
    assert any(r["path"] == "hooks.ts" for r in result["results"])
    assert not search(source, index, "SecretKey")["results"]
    assert ".env" not in data["files"]


def test_cache_invalidation_deleted_files_and_parser_upgrade(tmp_path):
    source, index = source_tree(tmp_path)
    assert build_index(source, index)["reused"] == 4
    (source / "hooks.ts").unlink()
    with pytest.raises(ValueError, match="变化"):
        search(source, index, "form")
    build_index(source, index)
    data = json.loads((index / "index.json").read_text(encoding="utf-8"))
    assert "hooks.ts" not in data["files"]
    data["parsers"] = {"tree-sitter": "wrong"}
    (index / "index.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="版本"):
        search(source, index, "form")
    assert build_index(source, index)["reused"] == 0


def test_bad_syntax_and_size_are_visible():
    assert extract(b"public class {", ".java")["parse_error"]
    assert extract(b"a" * 1_000_001, ".ts")["parse_error"] == "file_too_large"
    result = extract(b'<script lang="coffee">x = 1</script>', ".vue")
    assert "unsupported_script_language" in result["parse_error"]


def test_context_bounds_and_no_tool_secrets(tmp_path):
    source, index = source_tree(tmp_path)
    fingerprint = sha(source / "hooks.ts")
    result = read_code(source, index, "hooks.ts", 1, 2, fingerprint)
    assert "useArticleForm" in result["content"] and result["sha256"] == fingerprint
    for path in ("../outside", ".env", ".continue/secret.ts"):
        with pytest.raises(ValueError):
            read_code(source, index, path, 1, 1, fingerprint)
    with pytest.raises(ValueError):
        read_code(source, index, "hooks.ts", 1, 2, "0" * 64)
    with pytest.raises(ValueError):
        search(source, index, "a", limit=21)
    assert len(symbol_map(source, index, 100)["text"]) <= 100
    value = config(source, index)
    assert "API_KEY" not in json.dumps(value)
    assert value["mcpServers"][0]["args"][1] == "workbench.continue_mcp"


def test_tampered_index_hash_is_not_trusted(tmp_path):
    source, index = source_tree(tmp_path)
    data = json.loads((index / "index.json").read_text(encoding="utf-8"))
    data["files"]["hooks.ts"]["sha256"] = "0" * 64
    (index / "index.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        read_code(source, index, "hooks.ts", 1, 1, "0" * 64)
