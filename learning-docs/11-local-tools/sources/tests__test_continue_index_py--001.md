# tests/test_continue_index.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.continue_index`、`workbench.knowledge`、`workbench.retrieval`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `actual_node`（L21–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L22按`not (NODE_ROOT / ".built/manifest.json").is_file() or not shutil.which("node")`分支；L24按`os.environ.get("RND_REQUIRE_NODE_TESTS") == "1"`分支。 调用`(NODE_ROOT / ".built/manifest.json").is_file`、`shutil.which`、`os.environ.get`、`pytest.fail`、`pytest.skip`、`bridge_identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_index`（L31–L48）：接收`tmp_path`。 控制顺序：L38遍历`["apps/web-antd/Article.vue", "apps/web-ele/Decoy.vue"]`。 调用`source.mkdir`、`(source / "Article.java").write_text`、`path.parent.mkdir`、`path.write_text`、`(source / "short.py").write_text`、`build_index`。 返回路径：L48的`source, index`。
- `test_vendored_continue_component_and_license_match_pinned_git_blobs`（L51–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L57断言`manifest["revision"] == CONTINUE_REVISION`；L58遍历`expected.items()`；L60断言`hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == checksum`；L61断言`hashlib.sha256(data).hexdigest() == manifest["files"][name]["sha256"]`。 调用`json.loads`、`(NODE_ROOT / "upstream/manifest.json").read_text`、`expected.items`、`(NODE_ROOT / "upstream" / name).read_bytes`、`hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest`、`hashlib.sha1`、`f"blob {len(data)}\0".encode`、`len`、`hashlib.sha256(data).hexdigest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_opted_in_engine_is_actionable_not_a_cloud_or_fake_fallback`（L64–L72）：接收`settings`、`source_index`、`tmp_path`、`monkeypatch`。 控制顺序：L67断言`settings.retrieval_engine == "local"`；L68断言`query(*source_index, "RestController", settings=settings)["matches"]`。 调用`query`、`monkeypatch.setattr`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_component_indexes_and_queries_java_vue_without_source_execution`（L76–L113）：接收`actual_node`、`settings`、`source_index`。 控制顺序：L85断言`result["matches"][0]["path"] == "Article.java"`；L86断言`result["matches"][0]["score"] > 1 / 61`；L89断言`result["mode"] == "ast+continue-fts5+fts5"`；L91断言`report["engine"] == "Continue.FullTextSearchCodebaseIndex"`；L92断言`report["revision"] == CONTINUE_REVISION and report["network"] == "disabled"`；L93断言`report["chunks"] == 4 and report["model_calls"] == 0`；L95断言`db.execute("SELECT COUNT(*) FROM fts_metadata").fetchone()[0] == 4`；L96断言`db.execute("SELECT COUNT(*) FROM fts WHERE fts MATCH 'RestController'").fetchone()[0]…`。后续分支沿下方源码相同行号继续阅读。 调用`p.relative_to(source).as_posix`、`p.relative_to`、`p.read_bytes`、`source.rglob`、`p.is_file`、`query`、`json.loads`、`(index / "continue-index.json").read_text`、`closing`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_hits_empty_scope_and_short_tokens_do_not_broaden_or_crash`（L117–L128）：接收`actual_node`、`settings`、`source_index`。 控制顺序：L121断言`not query(*source_index, "CompletelyMissingSymbol", settings=settings)["matches"]`；L122断言`not query(*source_index, "useVbenForm", settings=settings, path_prefix="absent")[ "ma…`；L125断言`not query(*source_index, "RestController", settings=settings, file_suffix=".vue")[ "m…`；L128断言`query(*source_index, "go", settings=settings)["matches"][0]["path"] == "short.py"`。 调用`query`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_or_deleted_files_invalidate_actual_continue_cache`（L132–L151）：接收`actual_node`、`settings`、`source_index`。 控制顺序：L145断言`[row["path"] for row in result["matches"]] == ["Added.java"]`；L146断言`json.loads((index / "continue-index.json").read_text())["identity"] != old`；L148断言`db.execute("SELECT COUNT(*) FROM fts_metadata WHERE path='Article.java'").fetchone()[…`。 调用`query`、`json.loads`、`(index / "continue-index.json").read_text`、`(source / "Article.java").unlink`、`(source / "Added.java").write_text`、`pytest.raises`、`build_index`、`closing`、`sqlite3.connect`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_continue_can_fuse_explicit_local_embedding_protocol`（L155–L188）：接收`actual_node`、`settings`、`source_index`。 控制顺序：L186断言`result["mode"].endswith("+vector-rrf")`；L187断言`[row["path"] for row in result["matches"]] == ["apps/web-antd/Article.vue"]`；L188断言`len(seen) == 2`。 调用`httpx.MockTransport`、`add_embeddings`、`query`、`result["mode"].endswith`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_continue_can_fuse_explicit_local_embedding_protocol.peer`（L164–L174）：接收`request`。 控制顺序：L165断言`request.url.host == "127.0.0.1"`；L166断言`request.headers["Authorization"] == "Bearer local-no-auth"`。 调用`json.loads`、`seen.append`、`httpx.Response`、`range`、`len`。 返回路径：L169的`httpx.Response( 200, json={ "data": [{"index": i, "embedding": [1.0, 0.5]} for i in range(…`。
- `test_registered_node_process_rejects_network_apis_before_connect`（L202–L209）：接收`actual_node`、`statement`。 控制顺序：L204断言`run_command( ["node", "--require", str(NODE_ROOT / "no-network.cjs"), "-e", script], …`。 调用`run_command`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_continue_index.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L209。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8229`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_continue_index.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2707d7ed6890ef4229ed0cf672de67e563514f2c8b55823d87cf3ccd53a98d1a"} -->
````python
# tests/test_continue_index.py
"""Run the real pinned Continue TypeScript component, with its local SQLite host."""

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
        '@RestController\npublic class Article { public String title() { return "hello"; } }\n',
        encoding="utf-8",
    )
    for name in ["apps/web-antd/Article.vue", "apps/web-ele/Decoy.vue"]:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '<script setup lang="ts">\nconst form = useVbenForm();\n</script>\n<template><Form/></template>\n',
            encoding="utf-8",
        )
    (source / "short.py").write_text("def go():\n    return 0\n", encoding="utf-8")
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


def test_missing_opted_in_engine_is_actionable_not_a_cloud_or_fake_fallback(
    settings, source_index, tmp_path, monkeypatch
):
    assert settings.retrieval_engine == "local"
    assert query(*source_index, "RestController", settings=settings)["matches"]
    monkeypatch.setattr(continue_index, "NODE_ROOT", tmp_path / "missing-tool")
    settings.retrieval_engine = "continue"
    with pytest.raises(ToolFailure, match="npm ci"):
        query(*source_index, "RestController", settings=settings)


@pytest.mark.node_tools
def test_actual_component_indexes_and_queries_java_vue_without_source_execution(
    actual_node, settings, source_index
):
    settings.retrieval_engine = "continue"
    source, index = source_index
    before = {
        p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()
    }
    result = query(source, index, "RestController", settings=settings)
    assert result["matches"][0]["path"] == "Article.java"
    assert (
        result["matches"][0]["score"] > 1 / 61
    )  # Both actual Continue and local symbol/FTS rankings contributed.
    assert result["mode"] == "ast+continue-fts5+fts5"
    report = json.loads((index / "continue-index.json").read_text())
    assert report["engine"] == "Continue.FullTextSearchCodebaseIndex"
    assert report["revision"] == CONTINUE_REVISION and report["network"] == "disabled"
    assert report["chunks"] == 4 and report["model_calls"] == 0
    with closing(sqlite3.connect(index / "continue.sqlite3")) as db:
        assert db.execute("SELECT COUNT(*) FROM fts_metadata").fetchone()[0] == 4
        assert (
            db.execute("SELECT COUNT(*) FROM fts WHERE fts MATCH 'RestController'").fetchone()[0]
            == 1
        )
    cached = (index / "continue.sqlite3").stat().st_mtime_ns
    result = query(
        source,
        index,
        "useVbenForm",
        settings=settings,
        file_suffix=".vue",
        path_prefix="apps/web-antd",
    )
    assert [row["path"] for row in result["matches"]] == ["apps/web-antd/Article.vue"]
    assert (index / "continue.sqlite3").stat().st_mtime_ns == cached
    assert before == {
        p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()
    }


@pytest.mark.node_tools
def test_no_hits_empty_scope_and_short_tokens_do_not_broaden_or_crash(
    actual_node, settings, source_index
):
    settings.retrieval_engine = "continue"
    assert not query(*source_index, "CompletelyMissingSymbol", settings=settings)["matches"]
    assert not query(*source_index, "useVbenForm", settings=settings, path_prefix="absent")[
        "matches"
    ]
    assert not query(*source_index, "RestController", settings=settings, file_suffix=".vue")[
        "matches"
    ]
    assert query(*source_index, "go", settings=settings)["matches"][0]["path"] == "short.py"


@pytest.mark.node_tools
def test_changed_or_deleted_files_invalidate_actual_continue_cache(
    actual_node, settings, source_index
):
    settings.retrieval_engine = "continue"
    source, index = source_index
    query(source, index, "RestController", settings=settings)
    old = json.loads((index / "continue-index.json").read_text())["identity"]
    (source / "Article.java").unlink()
    (source / "Added.java").write_text("@RestController\nclass Added {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="源码已改变"):
        query(source, index, "RestController", settings=settings)
    build_index(source, index)
    result = query(source, index, "RestController", settings=settings)
    assert [row["path"] for row in result["matches"]] == ["Added.java"]
    assert json.loads((index / "continue-index.json").read_text())["identity"] != old
    with closing(sqlite3.connect(index / "continue.sqlite3")) as db:
        assert (
            db.execute("SELECT COUNT(*) FROM fts_metadata WHERE path='Article.java'").fetchone()[0]
            == 0
        )


@pytest.mark.node_tools
def test_actual_continue_can_fuse_explicit_local_embedding_protocol(
    actual_node, settings, source_index
):
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
        return httpx.Response(
            200,
            json={
                "data": [{"index": i, "embedding": [1.0, 0.5]} for i in range(len(body["input"]))]
            },
        )

    transport = httpx.MockTransport(peer)
    add_embeddings(*source_index, settings, transport)
    result = query(
        *source_index,
        "useVbenForm",
        settings=settings,
        transport=transport,
        file_suffix=".vue",
        path_prefix="apps/web-antd",
    )
    assert result["mode"].endswith("+vector-rrf")
    assert [row["path"] for row in result["matches"]] == ["apps/web-antd/Article.vue"]
    assert len(seen) == 2


@pytest.mark.node_tools
@pytest.mark.parametrize(
    "statement",
    [
        "require('node:net').connect(80,'127.0.0.1')",
        "require('node:https').get('https://example.com')",
        "require('node:dns').lookup('example.com',()=>{})",
        "require('node:dgram').createSocket('udp4')",
        "require('node:http2').connect('https://example.com')",
    ],
)
def test_registered_node_process_rejects_network_apis_before_connect(actual_node, statement):
    script = f"try {{ {statement}; process.exitCode=2; }} catch(e) {{ if(!e.message.includes('network access is disabled')) throw e; }}"
    assert (
        run_command(
            ["node", "--require", str(NODE_ROOT / "no-network.cjs"), "-e", script], NODE_ROOT, 20
        )["returncode"]
        == 0
    )
````
