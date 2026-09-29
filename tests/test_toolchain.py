"""Real parsers/SQLite/MCP; explicit fixtures only for paid external transports."""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from pydantic import SecretStr

from workbench.aider_tool import EditBlocks, apply_blocks, preview_blocks
from workbench.context_mcp import export_continue, make_server
from workbench.domain import digest
from workbench.filesystem import manifest, sha
from workbench.generator import PrerequisiteError, generate_basic
from workbench.knowledge import build_index
from workbench.retrieval import add_embeddings, compact_map, embed, embedding_profile, query
from workbench.sandbox import checks_for, validate_configuration, verify_in_daytona
from workbench.settings import ModelProfile
from workbench.symbols import parse_file
from workbench.toolchain import prepare_context


@pytest.fixture
def indexed(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "ArticleController.java").write_text(
        "package demo;\nimport org.springframework.web.bind.annotation.RestController;\n"
        "@RestController\npublic class ArticleController extends BaseController {\n"
        ' @TableField("title") private String title;\n'
        " public String getArticle(int id) { return title; }\n}\n",
        encoding="utf-8",
    )
    (source / "hooks.ts").write_text(
        "export interface FormSchema { title: string; }\n"
        "export function useArticleForm() { return 'form'; }\n",
        encoding="utf-8",
    )
    (source / "Article.vue").write_text(
        '<template><VbenForm /><p>中文</p></template>\n<script setup lang="ts">\n'
        "import { useVbenForm } from '@vben/common-ui';\n"
        "function submitArticle(): void { }\n</script>\n",
        encoding="utf-8",
    )
    index = tmp_path / "index"
    build_index(source, index)
    return source, index


def test_real_java_symbols_annotations_and_bases(indexed):
    source, _ = indexed
    parsed = parse_file(source / "ArticleController.java")
    assert parsed["parser"] == "tree-sitter" and not parsed["parse_error"]
    symbol = next(s for s in parsed["symbols"] if s["name"] == "ArticleController")
    assert symbol["annotations"] == ["@RestController"]
    assert "BaseController" in " ".join(symbol["bases"])
    field = next(s for s in parsed["symbols"] if s["kind"] == "field_declaration")
    assert '@TableField("title")' in field["annotations"]
    assert any(s["name"] == "getArticle" and s["line"] == 6 for s in parsed["symbols"])


def test_typescript_and_vue_real_sfc_offsets(indexed):
    source, _ = indexed
    ts = parse_file(source / "hooks.ts")
    assert {"FormSchema", "useArticleForm"} <= {s["name"] for s in ts["symbols"]}
    vue = parse_file(source / "Article.vue")
    assert any(s["name"] == "submitArticle" and s["line"] == 4 for s in vue["symbols"])
    assert any(
        s["name"] == "VbenForm" and s["kind"] == "vue_component_usage" for s in vue["symbols"]
    )
    assert "useVbenForm" in vue["imports"][0]


def test_incremental_hash_cache_and_deletion(indexed):
    source, index = indexed
    assert build_index(source, index)["reused"] == 3
    (source / "hooks.ts").unlink()
    with pytest.raises(ValueError, match="源码已改变"):
        query(source, index, "FormSchema")
    build_index(source, index)
    # Camel-case expansion may correctly match Form in another existing file.
    # Assert the deleted path is absent from the real index, not that recall is empty.
    assert all(hit["path"] != "hooks.ts" for hit in query(source, index, "FormSchema")["matches"])
    import sqlite3
    from contextlib import closing

    with closing(sqlite3.connect(index / "search.sqlite3")) as db:
        assert db.execute("SELECT count(*) FROM chunks WHERE path='hooks.ts'").fetchone()[0] == 0
    assert "hooks.ts" not in compact_map(index)["text"]


def test_search_is_bounded_source_backed_and_parameterized(indexed):
    source, index = indexed
    result = query(source, index, "useVbenForm")
    hit = result["matches"][0]
    assert result["mode"] == "ast+fts5"
    assert hit["path"] == "Article.vue"
    assert hit["sha256"] == sha(source / hit["path"])
    assert hit["start"] <= 3 <= hit["end"]
    assert result["chars"] <= 12000
    assert query(source, index, '" OR 1=1 --')["mode"] == "ast+fts5"
    assert not query(source, index, "useVbenForm", max_chars=100)["matches"]
    with pytest.raises(ValueError):
        query(source, index, "", limit=30)


@pytest.mark.parametrize(
    "name", [".env", ".env.local", ".netrc", ".aider.chat.history.md", "secret.sqlite3"]
)
def test_tool_context_excludes_credentials(tmp_path, name):
    root = tmp_path / "src"
    root.mkdir()
    (root / name).write_text("secret-api-key", encoding="utf-8")
    assert manifest(root) == {}


def test_continue_configuration_and_actual_server(indexed, tmp_path):
    source, index = indexed
    export_continue(tmp_path, source, index)
    content = (tmp_path / ".continue/mcpServers/rnd.json").read_text(encoding="utf-8")
    config = json.loads(content)["mcpServers"]["rnd-context"]
    assert config["command"] == "uv" and "context-server" in config["args"]
    assert "API_KEY" not in content
    with pytest.raises(ValueError, match="已存在"):
        export_continue(tmp_path, source, index)

    async def inspect():
        server = make_server(source, index)
        tools = await server.list_tools()
        assert {tool.name for tool in tools} == {"search_code", "repository_map"}
        result = await server.call_tool("search_code", {"question": "useVbenForm"})
        assert "Article.vue" in str(result)

    asyncio.run(inspect())


def test_export_in_source_does_not_invalidate_index(indexed):
    source, index = indexed
    export_continue(source, source, index)
    assert query(source, index, "useVbenForm")["matches"]


def test_embeddings_require_explicit_credentials(settings):
    settings.embedding_model = "embedding-fixture"
    settings.embedding_base_url = "https://embeddings.example/v1"
    settings.api_key = SecretStr("default-provider-secret")
    with pytest.raises(ValueError):
        embedding_profile(settings)


def test_real_vector_fusion_with_explicit_transport(indexed, settings):
    source, index = indexed
    settings.embedding_model = "embedding-fixture"
    settings.embedding_base_url = "https://embeddings.example/v1"
    settings.embedding_api_key = SecretStr("separate-key")
    settings.embedding_allow_upload = True
    calls = []

    def handler(request):
        assert request.headers["Authorization"] == "Bearer separate-key"
        body = json.loads(request.content)
        calls.append(body)
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": i, "embedding": [1.0, 2.0 if "Vben" in text else 0.5]}
                    for i, text in enumerate(body["input"])
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    assert add_embeddings(source, index, settings, transport)["embedded"] > 0
    before = len(calls)
    assert add_embeddings(source, index, settings, transport)["embedded"] == 0
    assert len(calls) == before
    result = query(source, index, "useVbenForm", settings=settings, transport=transport)
    assert result["mode"] == "ast+fts5+vector-rrf"
    assert result["matches"][0]["path"] == "Article.vue"
    (source / "extra.ts").write_text("export function extra() { return 1; }\n", encoding="utf-8")
    build_index(source, index)
    assert add_embeddings(source, index, settings, transport)["embedded"] == 1


@pytest.mark.parametrize("vector", [[0, 0], [float("nan")], ["not-a-number"]])
def test_embedding_rejects_invalid_vectors(vector):
    profile = ModelProfile(
        stage="embedding",
        base_url="https://fixture.example",
        model="test",
        api_key=SecretStr("fixture"),
    )
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200, content=json.dumps({"data": [{"index": 0, "embedding": vector}]}).encode()
        )
    )
    with pytest.raises(ValueError):
        embed(profile, ["hello"], transport)


def blocks():
    return (
        "custom_rules.py\n<<<<<<< SEARCH\n    return None\n=======\n"
        "    if data.get('priority', 0) < 0:\n        raise ValueError('nonnegative')\n"
        "    return None\n>>>>>>> REPLACE\n"
    )


def test_search_replace_preview_and_refusals():
    before = "def validate(entity, data):\n    return None\n"
    assert "nonnegative" in preview_blocks(before, blocks())
    for value in [
        blocks().replace("custom_rules.py", "../app.py"),
        blocks().replace("    return None\n=======", "\n======="),
        blocks() + "rm -rf anything",
        blocks().replace("    return None\n=======", "missing\n======="),
    ]:
        with pytest.raises(ValueError):
            preview_blocks(before, value)


def test_stale_aider_patch_does_not_call_tool(tmp_path, settings, monkeypatch):
    (tmp_path / "custom_rules.py").write_text(
        "def validate(entity, data):\n    return None\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        "workbench.aider_tool.command", lambda *a: pytest.fail("must not call aider")
    )
    value = EditBlocks(before_sha256="0" * 64, blocks=blocks(), explanation="fixture")
    with pytest.raises(ValueError, match="SHA"):
        apply_blocks(tmp_path, value, settings)


def test_context_is_actually_available_to_planning(settings, tmp_path):
    context = prepare_context(
        settings, "python-basic", {"summary": "user CRUD"}, tmp_path / "context"
    )
    assert context["model_calls"] == 0
    assert "app.py" in context["contexts"][0]["repo_map"]["text"]
    assert (tmp_path / "context/context-receipt.json").is_file()


def test_daytona_requires_consent_and_never_inherits_model_key(settings):
    settings.sandbox_provider = "daytona"
    with pytest.raises(PrerequisiteError, match="ALLOW_UPLOAD"):
        validate_configuration(settings, "python-basic")
    settings.daytona_allow_upload = True
    with pytest.raises(ValueError):
        validate_configuration(settings, "python-basic")


def fake_daytona(settings, *, fail=None):
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_upload = True
    settings.daytona_snapshot = "fixture-not-a-real-cloud"
    settings.daytona_api_key = SecretStr("daytona-test-key")
    events = []

    class Files:
        def create_folder(self, *args):
            events.append(("mkdir", args))

        def upload_file(self, data, path, **kwargs):
            assert b"daytona-test-key" not in data
            events.append(("upload", path))
            if fail == "upload":
                raise RuntimeError("test upload failure")

        def download_file(self, *args, **kwargs):
            return json.dumps({"passed": True, "http": True, "restart": True}).encode()

    class Process:
        def exec(self, command, **kwargs):
            events.append(("exec", command))
            return SimpleNamespace(exit_code=1 if fail == "exec" else 0, result="fixture")

    class Client:
        def create(self, params, **kwargs):
            assert "daytona-test-key" not in json.dumps(params.model_dump(), default=str)
            assert params.public is False and params.auto_stop_interval == 5
            events.append(("create", None))
            return SimpleNamespace(id="fixture-sandbox", fs=Files(), process=Process())

        def delete(self, sandbox, **kwargs):
            events.append(("delete", sandbox.id))
            if fail == "delete":
                raise RuntimeError("fixture cleanup failure")

    return Client(), events


@pytest.mark.parametrize("failure", [None, "upload", "exec", "delete"])
def test_daytona_always_cleans_and_blocks_failed_checks(settings, plan, tmp_path, failure):
    product = tmp_path / "product"
    generate_basic(plan, product)
    client, events = fake_daytona(settings, fail=failure)
    before = manifest(product)
    if failure:
        with pytest.raises(PrerequisiteError):
            verify_in_daytona(product, "python-basic", settings, client=client)
    else:
        result = verify_in_daytona(product, "python-basic", settings, client=client)
        assert result["passed"] and result["cleanup"] == "deleted"
    assert events[-1] == ("delete", "fixture-sandbox")
    receipt = json.loads((tmp_path / "daytona-verification.json").read_text(encoding="utf-8"))
    assert receipt["passed"] is (failure is None)
    assert receipt["source_digest"] == digest(before)
    assert manifest(product) == before


def test_sandbox_commands_are_registered_not_model_chosen():
    assert any("mvn" in argv for _, argv, _ in checks_for("yudao-vben"))
    with pytest.raises(PrerequisiteError):
        checks_for("shell:rm-anything")


def test_workflow_daytona_gate_blocks_packaging(settings, store, monkeypatch):
    from workbench.flow import Workflow

    workflow = Workflow(settings, store, None)
    assert workflow.after_verify({"verification": {"passed": True}}) == "sandbox"
    settings.sandbox_provider = "daytona"

    def failed(*args):
        raise PrerequisiteError("remote verification rejected")

    monkeypatch.setattr("workbench.sandbox.verify_in_daytona", failed)
    with pytest.raises(PrerequisiteError):
        workflow.sandbox({"run_id": "fixture", "template": "python-basic"})


def test_ast_packing_covers_every_line_without_one_chunk_per_variable(tmp_path):
    from workbench.retrieval import chunks

    source, index = tmp_path / "source", tmp_path / "index"
    source.mkdir()
    text = "\n".join(f"export const value{i} = {i};" for i in range(180)) + "\n"
    (source / "dense.ts").write_text(text, encoding="utf-8")
    build_index(source, index)
    data = json.loads((index / "index.json").read_text(encoding="utf-8"))
    assert len(data["files"]["dense.ts"]["symbols"]) == 180
    packed = list(chunks(source, data))
    assert len(packed) == 3
    assert "\n".join(row[6] for row in packed) == text.rstrip("\n")
    assert [(row[2], row[3]) for row in packed] == [(1, 60), (61, 120), (121, 180)]


def test_exact_hook_usage_is_not_displaced_by_short_camel_case_matches(tmp_path):
    source, index = tmp_path / "source", tmp_path / "index"
    source.mkdir()
    for number in range(100):
        (source / f"decoy{number}.ts").write_text(
            "export const use = 1; export const vben = 2; export const form = 3;\n",
            encoding="utf-8",
        )
    (source / "usage.vue").write_text(
        '<script setup lang="ts">\n'
        "import { useVbenForm } from '@vben/common-ui';\n"
        "const [Form, formApi] = useVbenForm({ schema: [] });\n"
        "</script>\n<template><Form /></template>\n",
        encoding="utf-8",
    )
    build_index(source, index)
    found = query(source, index, "useVbenForm", limit=3)
    assert found["matches"][0]["path"] == "usage.vue"
    assert "useVbenForm" in found["matches"][0]["content"]


def test_search_path_filters_apply_before_ranking(indexed):
    source, index = indexed
    assert not query(source, index, "useVbenForm", file_suffix=".java")["matches"]
    assert (
        query(source, index, "useVbenForm", file_suffix=".vue")["matches"][0]["path"]
        == "Article.vue"
    )
    assert not query(source, index, "useVbenForm", path_prefix="other-app/")["matches"]
    with pytest.raises(ValueError):
        query(source, index, "useVbenForm", path_prefix="../outside/")
    with pytest.raises(ValueError):
        query(source, index, "useVbenForm", file_suffix=".env")


def test_aider_uses_mapping_config_and_separate_empty_env(tmp_path, settings, monkeypatch):
    from pathlib import Path

    import yaml

    from workbench import aider_tool
    from workbench.tools import clean_env

    home, work = tmp_path / "home", tmp_path / "work"
    home.mkdir()
    work.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-leak-either")
    monkeypatch.setattr(aider_tool, "executable", lambda _: "pinned-aider")
    calls = []

    def invoke(argv, cwd, **kwargs):
        calls.append(argv)
        environment = clean_env(kwargs["extra_env"])
        assert environment["OPENAI_API_KEY"] == "unused-local-editing-only"
        assert "ANTHROPIC_API_KEY" not in environment
        if "--version" in argv:
            return {"log": "aider 0.86.2"}
        config = Path(argv[argv.index("--config") + 1])
        env_file = Path(argv[argv.index("--env-file") + 1])
        assert config != env_file
        assert yaml.safe_load(config.read_text(encoding="utf-8")) == {}
        assert env_file.read_text(encoding="utf-8") == ""
        assert Path(environment["GIT_CONFIG_GLOBAL"]).read_text(encoding="utf-8") == ""
        return {"log": "actual CLI is exercised by ci_toolchain"}

    monkeypatch.setattr(aider_tool, "run_command", invoke)
    aider_tool.command(settings, work, home, "--show-repo-map")
    assert len(calls) == 2


def test_runtime_preserves_redacted_wrapped_tool_failure(settings, store):
    from conftest import new_run

    from workbench.runtime import Runtime
    from workbench.tools import ToolFailure

    settings.api_key = SecretStr("fixture-secret-token")

    class FailingToolGateway:
        def complete(self, *args, **kwargs):
            error = ToolFailure("subprocess rejected configuration")
            error.log = "diagnostic fixture-secret-token " + "x" * 70000
            error.returncode = 2
            error.timed_out = False
            try:
                raise error
            except ToolFailure as exc:
                raise ValueError("adapter error") from exc

    run_id = new_run(store)
    with Runtime(settings, store, FailingToolGateway()) as worker:
        worker.tick()
    run = store.get_run(run_id)
    assert run["status"] == "FAILED" and "tool-failure.json" in run["error"]
    path = settings.data_dir / "runs" / run_id / "tool-failure.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["returncode"] == 2 and report["passed"] is False
    assert report["run_id"] == run_id and report["job_id"]
    assert "fixture-secret-token" not in path.read_text(encoding="utf-8")
    assert "[redacted]" in report["log"] and len(report["log"]) <= 65536
