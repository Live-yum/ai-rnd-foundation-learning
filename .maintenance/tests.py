# Exact, reviewable UTF-8 source operations against verified commit c3d3c612.
PATCHES = {
    'pyproject.toml': ('4d1bdbd93469d750912ccf9129d084471f9818e969393b6d742a6eb0764ce1d4', [
        (30, 31, r'''markers = ["postgres: PostgreSQL integration requires TEST_DATABASE_URL", "node_tools: real optional local Node tools; required in toolchain CI"]
'''),
    ]),
    'tests/test_aider_offline.py': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''"""The child guard is tested in a fresh interpreter; it never changes pytest's networking."""

import sys

import pytest

from workbench.settings import ROOT
from workbench.tools import run_command


@pytest.mark.parametrize("operation", [
    "socket.getaddrinfo('example.com',443)",
    "socket.gethostbyname('localhost')",
    "socket.socket().connect(('127.0.0.1',80))",
    "socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b'x',('127.0.0.1',9))",
    "socket.socket().bind(('127.0.0.1',0))",
])
def test_aider_guard_blocks_dns_tcp_udp_and_listening(operation):
    runner = ROOT / "tools/aider/offline_runner.py"
    script = (
        f"import runpy,socket; ns=runpy.run_path({str(runner)!r},run_name='guard-test'); "
        "ns['install_offline_guard']()\n"
        f"try:\n {operation}\nexcept PermissionError as e:\n assert 'network access is disabled' in str(e)\n"
        "else:\n raise AssertionError('unguarded network operation')\n"
    )
    assert run_command([sys.executable,"-c",script],ROOT,20)["returncode"] == 0
'''),
    ]),
    'tests/test_continue_index.py': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''"""Run the real pinned Continue TypeScript component, with its local SQLite host."""

import hashlib
import json
import os
import shutil
import sqlite3
from contextlib import closing

import httpx
import pytest

from workbench import continue_index
from workbench.continue_index import CONTINUE_REVISION, NODE_ROOT, bridge_identity
from workbench.knowledge import build_index
from workbench.retrieval import add_embeddings, query
from workbench.tools import ToolFailure, run_command


@pytest.fixture
def actual_node():
    if not (NODE_ROOT / ".built/manifest.json").is_file() or not shutil.which("node"):
        message = "Optional Continue engine: install Node 22 and run npm ci/build in tools/node"
        if os.environ.get("RND_REQUIRE_NODE_TESTS") == "1":
            pytest.fail(message)
        pytest.skip(message)
    bridge_identity()


@pytest.fixture
def source_index(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "Article.java").write_text(
        '@RestController\npublic class Article { public String title() { return "hello"; } }\n', encoding="utf-8"
    )
    for name in ["apps/web-antd/Article.vue", "apps/web-ele/Decoy.vue"]:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('<script setup lang="ts">\nconst form = useVbenForm();\n</script>\n<template><Form/></template>\n', encoding="utf-8")
    (source / "short.py").write_text('def go():\n    return 0\n', encoding="utf-8")
    index = tmp_path / "index"
    build_index(source, index)
    return source, index


def test_vendored_continue_component_and_license_match_pinned_git_blobs():
    expected = {
        "FullTextSearchCodebaseIndex.ts": "8016d04d3eddc84ec48ffa517ba96b2caba9b14e",
        "LICENSE": "c25dc1768217ba50d454fcc06290d66886512872",
    }
    manifest = json.loads((NODE_ROOT / "upstream/manifest.json").read_text())
    assert manifest["revision"] == CONTINUE_REVISION
    for name, checksum in expected.items():
        data = (NODE_ROOT / "upstream" / name).read_bytes()
        assert hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == checksum
        assert hashlib.sha256(data).hexdigest() == manifest["files"][name]["sha256"]


def test_missing_opted_in_engine_is_actionable_not_a_cloud_or_fake_fallback(settings, source_index, tmp_path, monkeypatch):
    assert settings.retrieval_engine == "local"
    assert query(*source_index, "RestController", settings=settings)["matches"]
    monkeypatch.setattr(continue_index, "NODE_ROOT", tmp_path / "missing-tool")
    settings.retrieval_engine = "continue"
    with pytest.raises(ToolFailure, match="npm ci"):
        query(*source_index, "RestController", settings=settings)


@pytest.mark.node_tools
def test_actual_component_indexes_and_queries_java_vue_without_source_execution(actual_node, settings, source_index):
    settings.retrieval_engine = "continue"
    source, index = source_index
    before = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    result = query(source, index, "RestController", settings=settings)
    assert result["matches"][0]["path"] == "Article.java"
    assert result["matches"][0]["score"] > 1 / 61  # Both actual Continue and local symbol/FTS rankings contributed.
    assert result["mode"] == "ast+continue-fts5+fts5"
    report = json.loads((index / "continue-index.json").read_text())
    assert report["engine"] == "Continue.FullTextSearchCodebaseIndex"
    assert report["revision"] == CONTINUE_REVISION and report["network"] == "disabled"
    assert report["chunks"] == 4 and report["model_calls"] == 0
    with closing(sqlite3.connect(index / "continue.sqlite3")) as db:
        assert db.execute("SELECT COUNT(*) FROM fts_metadata").fetchone()[0] == 4
        assert db.execute("SELECT COUNT(*) FROM fts WHERE fts MATCH 'RestController'").fetchone()[0] == 1
    cached = (index / "continue.sqlite3").stat().st_mtime_ns
    result = query(source, index, "useVbenForm", settings=settings, file_suffix=".vue", path_prefix="apps/web-antd")
    assert [row["path"] for row in result["matches"]] == ["apps/web-antd/Article.vue"]
    assert (index / "continue.sqlite3").stat().st_mtime_ns == cached
    assert before == {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}


@pytest.mark.node_tools
def test_no_hits_empty_scope_and_short_tokens_do_not_broaden_or_crash(actual_node, settings, source_index):
    settings.retrieval_engine = "continue"
    assert not query(*source_index, "CompletelyMissingSymbol", settings=settings)["matches"]
    assert not query(*source_index, "useVbenForm", settings=settings, path_prefix="absent")["matches"]
    assert not query(*source_index, "RestController", settings=settings, file_suffix=".vue")["matches"]
    assert query(*source_index, "go", settings=settings)["matches"][0]["path"] == "short.py"


@pytest.mark.node_tools
def test_changed_or_deleted_files_invalidate_actual_continue_cache(actual_node, settings, source_index):
    settings.retrieval_engine = "continue"
    source, index = source_index
    query(source, index, "RestController", settings=settings)
    old = json.loads((index / "continue-index.json").read_text())["identity"]
    (source / "Article.java").unlink()
    (source / "Added.java").write_text('@RestController\nclass Added {}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="源码已改变"):
        query(source, index, "RestController", settings=settings)
    build_index(source, index)
    result = query(source, index, "RestController", settings=settings)
    assert [row["path"] for row in result["matches"]] == ["Added.java"]
    assert json.loads((index / "continue-index.json").read_text())["identity"] != old
    with closing(sqlite3.connect(index / "continue.sqlite3")) as db:
        assert db.execute("SELECT COUNT(*) FROM fts_metadata WHERE path='Article.java'").fetchone()[0] == 0


@pytest.mark.node_tools
def test_actual_continue_can_fuse_explicit_local_embedding_protocol(actual_node, settings, source_index):
    settings.retrieval_engine = "continue"
    settings.embedding_enabled = True
    settings.embedding_model = "local-protocol-fixture"
    settings.embedding_base_url = "http://127.0.0.1:11434/v1"
    seen = []
    def peer(request):
        assert request.url.host == "127.0.0.1"
        assert request.headers["Authorization"] == "Bearer local-no-auth"
        body = json.loads(request.content)
        seen.append(body)
        return httpx.Response(200, json={"data": [
            {"index": i, "embedding": [1.0, 0.5]} for i in range(len(body["input"]))
        ]})
    transport = httpx.MockTransport(peer)
    add_embeddings(*source_index, settings, transport)
    result = query(*source_index, "useVbenForm", settings=settings, transport=transport, file_suffix=".vue", path_prefix="apps/web-antd")
    assert result["mode"].endswith("+vector-rrf")
    assert [row["path"] for row in result["matches"]] == ["apps/web-antd/Article.vue"]
    assert len(seen) == 2


@pytest.mark.node_tools
@pytest.mark.parametrize("statement", [
    "require('node:net').connect(80,'127.0.0.1')",
    "require('node:https').get('https://example.com')",
    "require('node:dns').lookup('example.com',()=>{})",
    "require('node:dgram').createSocket('udp4')",
    "require('node:http2').connect('https://example.com')",
])
def test_registered_node_process_rejects_network_apis_before_connect(actual_node, statement):
    script = f"try {{ {statement}; process.exitCode=2; }} catch(e) {{ if(!e.message.includes('network access is disabled')) throw e; }}"
    assert run_command(["node", "--require", str(NODE_ROOT / "no-network.cjs"), "-e", script], NODE_ROOT, 20)["returncode"] == 0
'''),
    ]),
    'tests/test_toolchain.py': ('f6b5f40b9bef88cfae694d447ddaece68a552443ef12e82bca49216533820796', [
        (409, 409, r'''        assert argv[1].endswith("tools/aider/offline_runner.py") or argv[1].endswith("tools\\aider\\offline_runner.py")
'''),
    ]),
}
