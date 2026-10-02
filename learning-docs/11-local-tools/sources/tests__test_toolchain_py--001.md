# tests/test_toolchain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.aider_tool`、`workbench.context_mcp`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.knowledge`、`workbench.retrieval`、`workbench.sandbox`、`workbench.settings`、`workbench.symbols`、`workbench.toolchain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `indexed`（L25–L48）：接收`tmp_path`。 调用`source.mkdir`、`(source / "ArticleController.java").write_text`、`(source / "hooks.ts").write_text`、`(source / "Article.vue").write_text`、`build_index`。 返回路径：L48的`source, index`。
- `test_real_java_symbols_annotations_and_bases`（L51–L60）：接收`indexed`。 控制顺序：L54断言`parsed["parser"] == "tree-sitter" and not parsed["parse_error"]`；L56断言`symbol["annotations"] == ["@RestController"]`；L57断言`"BaseController" in " ".join(symbol["bases"])`；L59断言`'@TableField("title")' in field["annotations"]`；L60断言`any(s["name"] == "getArticle" and s["line"] == 6 for s in parsed["symbols"])`。 调用`parse_file`、`next`、`" ".join`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typescript_and_vue_real_sfc_offsets`（L63–L72）：接收`indexed`。 控制顺序：L66断言`{"FormSchema", "useArticleForm"} <= {s["name"] for s in ts["symbols"]}`；L68断言`any(s["name"] == "submitArticle" and s["line"] == 4 for s in vue["symbols"])`；L69断言`any( s["name"] == "VbenForm" and s["kind"] == "vue_component_usage" for s in vue["sym…`；L72断言`"useVbenForm" in vue["imports"][0]`。 调用`parse_file`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incremental_hash_cache_and_deletion`（L75–L90）：接收`indexed`。 控制顺序：L77断言`build_index(source, index)["reused"] == 3`；L84断言`all(hit["path"] != "hooks.ts" for hit in query(source, index, "FormSchema")["matches"…`；L89断言`db.execute("SELECT count(*) FROM chunks WHERE path='hooks.ts'").fetchone()[0] == 0`；L90断言`"hooks.ts" not in compact_map(index)["text"]`。 调用`build_index`、`(source / "hooks.ts").unlink`、`pytest.raises`、`query`、`all`、`closing`、`sqlite3.connect`、`db.execute("SELECT count(*) FROM chunks WHERE path='hooks.ts'").f…`、`db.execute`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_search_is_bounded_source_backed_and_parameterized`（L93–L105）：接收`indexed`。 控制顺序：L97断言`result["mode"] == "ast+fts5"`；L98断言`hit["path"] == "Article.vue"`；L99断言`hit["sha256"] == sha(source / hit["path"])`；L100断言`hit["start"] <= 3 <= hit["end"]`；L101断言`result["chars"] <= 12000`；L102断言`query(source, index, '" OR 1=1 --')["mode"] == "ast+fts5"`；L103断言`not query(source, index, "useVbenForm", max_chars=100)["matches"]`。 调用`query`、`sha`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tool_context_excludes_credentials`（L111–L115）：接收`tmp_path`、`name`。 控制顺序：L115断言`manifest(root) == {}`。 调用`root.mkdir`、`(root / name).write_text`、`manifest`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_continue_configuration_and_actual_server`（L118–L135）：接收`indexed`、`tmp_path`。 控制顺序：L123断言`config["command"] == "uv" and "context-server" in config["args"]`；L124断言`"API_KEY" not in content`。 调用`export_continue`、`(tmp_path / ".continue/mcpServers/rnd.json").read_text`、`json.loads`、`pytest.raises`、`asyncio.run`、`inspect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_continue_configuration_and_actual_server.inspect`（L128–L133）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L131断言`{tool.name for tool in tools} == {"search_code", "repository_map"}`；L133断言`"Article.vue" in str(result)`。 调用`make_server`、`server.list_tools`、`server.call_tool`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_export_in_source_does_not_invalidate_index`（L138–L141）：接收`indexed`。 控制顺序：L141断言`query(source, index, "useVbenForm")["matches"]`。 调用`export_continue`、`query`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_embeddings_require_explicit_credentials`（L144–L152）：接收`settings`。 控制顺序：L149断言`embedding_profile(settings).api_key.get_secret_value() == "local-no-auth"`。 调用`SecretStr`、`embedding_profile(settings).api_key.get_secret_value`、`embedding_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_vector_fusion_with_explicit_transport`（L155–L187）：接收`indexed`、`settings`。 控制顺序：L178断言`add_embeddings(source, index, settings, transport)["embedded"] > 0`；L180断言`add_embeddings(source, index, settings, transport)["embedded"] == 0`；L181断言`len(calls) == before`；L183断言`result["mode"] == "ast+fts5+vector-rrf"`；L184断言`result["matches"][0]["path"] == "Article.vue"`；L187断言`add_embeddings(source, index, settings, transport)["embedded"] == 1`。 调用`SecretStr`、`httpx.MockTransport`、`add_embeddings`、`len`、`query`、`(source / "extra.ts").write_text`、`build_index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_vector_fusion_with_explicit_transport.handler`（L163–L175）：接收`request`。 控制顺序：L164断言`request.headers["Authorization"] == "Bearer separate-key"`。 调用`json.loads`、`calls.append`、`httpx.Response`、`enumerate`。 返回路径：L167的`httpx.Response( 200, json={ "data": [ {"index": i, "embedding": [1.0, 2.0 if "Vben" in tex…`。
- `test_embedding_rejects_invalid_vectors`（L191–L204）：接收`vector`。 调用`ModelProfile`、`SecretStr`、`httpx.MockTransport`、`httpx.Response`、`json.dumps({"data": [{"index": 0, "embedding": vector}]}).encode`、`json.dumps`、`pytest.raises`、`embed`、`pytest.mark.parametrize`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `blocks`（L207–L212）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L208的`"custom_rules.py\n<<<<<<< SEARCH\n return None\n=======\n" " if data.get('priority', 0) < …`。
- `test_search_replace_preview_and_refusals`（L215–L225）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L217断言`"nonnegative" in preview_blocks(before, blocks())`；L218遍历`[ blocks().replace("custom_rules.py", "../app.py"), blocks().repl…`。 调用`preview_blocks`、`blocks`、`blocks().replace`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_aider_patch_does_not_call_tool`（L228–L237）：接收`tmp_path`、`settings`、`monkeypatch`。 调用`(tmp_path / "custom_rules.py").write_text`、`monkeypatch.setattr`、`pytest.fail`、`EditBlocks`、`blocks`、`pytest.raises`、`apply_blocks`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_is_actually_available_to_planning`（L240–L246）：接收`settings`、`tmp_path`。 控制顺序：L244断言`context["model_calls"] == 0`；L245断言`"app.py" in context["contexts"][0]["repo_map"]["text"]`；L246断言`(tmp_path / "context/context-receipt.json").is_file()`。 调用`prepare_context`、`(tmp_path / "context/context-receipt.json").is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_requires_consent_and_never_inherits_model_key`（L249–L255）：接收`settings`。 调用`pytest.raises`、`validate_configuration`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fake_daytona`（L258–L298）：接收`settings`、`fail`。 调用`SecretStr`、`Client`。 返回路径：L298的`Client(), events`。
- `fake_daytona.Files`（L265–L279）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fake_daytona.Files.create_folder`（L266–L267）：接收`*args`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fake_daytona.Files.upload_file`（L269–L273）：接收`data`、`path`、`**kwargs`。 控制顺序：L270断言`b"daytona-test-key" not in data`；L272按`fail == "upload"`分支；L273抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fake_daytona.Files.download_file_stream`（L275–L279）：接收`path`、`timeout`。 控制顺序：L276断言`path.endswith("/runtime.json") and timeout == settings.tool_timeout`；L277按`fail == "download"`分支；L278抛异常，停止当前正常路径。 调用`path.endswith`、`RuntimeError`、`json.dumps({"passed": True, "http": True, "restart": True}).encod…`、`json.dumps`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `fake_daytona.Process`（L281–L284）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fake_daytona.Process.exec`（L282–L284）：接收`command`、`**kwargs`。 调用`events.append`、`SimpleNamespace`。 返回路径：L284的`SimpleNamespace(exit_code=1 if fail == "exec" else 0, result="fixture")`。
- `fake_daytona.Client`（L286–L296）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fake_daytona.Client.create`（L287–L291）：接收`params`、`**kwargs`。 控制顺序：L288断言`"daytona-test-key" not in json.dumps(params.model_dump(), default=str)`；L289断言`params.public is False and params.auto_stop_interval == 5`。 调用`json.dumps`、`params.model_dump`、`events.append`、`SimpleNamespace`、`Files`、`Process`。 返回路径：L291的`SimpleNamespace(id="fixture-sandbox", fs=Files(), process=Process())`。
- `fake_daytona.Client.delete`（L293–L296）：接收`sandbox`、`**kwargs`。 控制顺序：L295按`fail == "delete"`分支；L296抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_always_cleans_and_blocks_failed_checks`（L302–L318）：接收`settings`、`plan`、`tmp_path`、`failure`。 控制顺序：L308按`failure`分支；L313断言`result["passed"] and result["cleanup"] == "deleted"`；L314断言`events[-1] == ("delete", "fixture-sandbox")`；L316断言`receipt["passed"] is (failure is None)`；L317断言`receipt["source_digest"] == digest(before)`；L318断言`manifest(product) == before`。 调用`generate_basic`、`fake_daytona`、`manifest`、`pytest.raises`、`verify_in_daytona`、`json.loads`、`(tmp_path / "daytona-verification.json").read_text`、`digest`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sandbox_commands_are_registered_not_model_chosen`（L321–L328）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L323断言`len(checks) == 1`；L324断言`checks[0][1][-4:] == ["--template", "yudao-vben", "--database", "postgresql"]`；L325断言`checks[0][1][2] == "/opt/rnd/harness/.venv/bin/python"`；L326断言`"daytona_matrix_probe.py" in checks[0][1][3]`。 调用`checks_for`、`len`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_daytona_gate_blocks_packaging`（L331–L343）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L335断言`workflow.after_verify({"verification": {"passed": True}}) == "sandbox"`。 调用`Workflow`、`workflow.after_verify`、`monkeypatch.setattr`、`pytest.raises`、`workflow.sandbox`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_daytona_gate_blocks_packaging.failed`（L338–L339）：接收`*args`。 控制顺序：L339抛异常，停止当前正常路径。 调用`PrerequisiteError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ast_packing_covers_every_line_without_one_chunk_per_variable`（L346–L359）：接收`tmp_path`。 控制顺序：L355断言`len(data["files"]["dense.ts"]["symbols"]) == 180`；L357断言`len(packed) == 3`；L358断言`"\n".join(row[6] for row in packed) == text.rstrip("\n")`；L359断言`[(row[2], row[3]) for row in packed] == [(1, 60), (61, 120), (121, 180)]`。 调用`source.mkdir`、`"\n".join`、`range`、`(source / "dense.ts").write_text`、`build_index`、`json.loads`、`(index / "index.json").read_text`、`len`、`list`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_hook_usage_is_not_displaced_by_short_camel_case_matches`（L362–L380）：接收`tmp_path`。 控制顺序：L365遍历`range(100)`；L379断言`found["matches"][0]["path"] == "usage.vue"`；L380断言`"useVbenForm" in found["matches"][0]["content"]`。 调用`source.mkdir`、`range`、`(source / f"decoy{number}.ts").write_text`、`(source / "usage.vue").write_text`、`build_index`、`query`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_search_path_filters_apply_before_ranking`（L383–L394）：接收`indexed`。 控制顺序：L385断言`not query(source, index, "useVbenForm", file_suffix=".java")["matches"]`；L386断言`query(source, index, "useVbenForm", file_suffix=".vue")["matches"][0]["path"] == "Art…`；L390断言`not query(source, index, "useVbenForm", path_prefix="other-app/")["matches"]`。 调用`query`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_aider_uses_mapping_config_and_separate_empty_env`（L397–L433）：接收`tmp_path`、`settings`、`monkeypatch`。 控制顺序：L433断言`len(calls) == 2`。 调用`home.mkdir`、`work.mkdir`、`monkeypatch.setenv`、`monkeypatch.setattr`、`aider_tool.command`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_aider_uses_mapping_config_and_separate_empty_env.invoke`（L413–L429）：接收`argv`、`cwd`、`**kwargs`。 控制顺序：L415断言`argv[1].endswith("tools/aider/offline_runner.py") or argv[1].endswith( "tools\\aider\…`；L419断言`environment["OPENAI_API_KEY"] == "unused-local-editing-only"`；L420断言`"ANTHROPIC_API_KEY" not in environment`；L421按`"--version" in argv`分支；L425断言`config != env_file`；L426断言`yaml.safe_load(config.read_text(encoding="utf-8")) == {}`；L427断言`env_file.read_text(encoding="utf-8") == ""`；L428断言`Path(environment["GIT_CONFIG_GLOBAL"]).read_text(encoding="utf-8") == ""`。 调用`calls.append`、`argv[1].endswith`、`clean_env`、`Path`、`argv.index`、`yaml.safe_load`、`config.read_text`、`env_file.read_text`、`Path(environment["GIT_CONFIG_GLOBAL"]).read_text`。 返回路径：L422的`{"log": "aider 0.86.2"}`；L429的`{"log": "actual CLI is exercised by ci_toolchain"}`。
- `test_runtime_preserves_redacted_wrapped_tool_failure`（L436–L465）：接收`settings`、`store`。 控制顺序：L459断言`run["status"] == "FAILED" and "tool-failure.json" in run["error"]`；L462断言`report["returncode"] == 2 and report["passed"] is False`；L463断言`report["run_id"] == run_id and report["job_id"]`；L464断言`"fixture-secret-token" not in path.read_text(encoding="utf-8")`；L465断言`"[redacted]" in report["log"] and len(report["log"]) <= 65536`。 调用`SecretStr`、`new_run`、`Runtime`、`FailingToolGateway`、`worker.tick`、`store.get_run`、`json.loads`、`path.read_text`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_preserves_redacted_wrapped_tool_failure.FailingToolGateway`（L444–L453）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_runtime_preserves_redacted_wrapped_tool_failure.FailingToolGateway.complete`（L445–L453）：接收`*args`、`**kwargs`。 控制顺序：L451抛异常，停止当前正常路径；L453抛异常，停止当前正常路径。 调用`ToolFailure`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_does_not_accept_http_only_receipt_for_generated_ui`（L468–L476）：接收`settings`、`plan`、`tmp_path`。 控制顺序：L474断言`events[-1] == ("delete", "fixture-sandbox")`；L476断言`receipt["passed"] is False and "浏览器" in receipt["error_detail"]`。 调用`generate_basic`、`fake_daytona`、`pytest.raises`、`verify_in_daytona`、`json.loads`、`(tmp_path / "daytona-verification.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_toolchain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L476。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19832`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_toolchain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f2ce0306dc8adc0603b3589895a2ed8a978950b7d1541ab96e6ebf4d6e210975"} -->
````python
# tests/test_toolchain.py
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
    settings.embedding_base_url = "http://127.0.0.1:11434/v1"
    settings.api_key = SecretStr("default-provider-secret")
    # An unauthenticated localhost model is valid; never inherit the chat key.
    assert embedding_profile(settings).api_key.get_secret_value() == "local-no-auth"
    settings.embedding_api_key = SecretStr("")
    with pytest.raises(ValueError):
        embedding_profile(settings)


def test_real_vector_fusion_with_explicit_transport(indexed, settings):
    source, index = indexed
    settings.embedding_model = "embedding-fixture"
    settings.embedding_base_url = "http://127.0.0.1:11434/v1"
    settings.embedding_api_key = SecretStr("separate-key")
    settings.embedding_enabled = True
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
    with pytest.raises(PrerequisiteError, match="ALLOW_LOCAL_EXECUTION"):
        validate_configuration(settings, "python-basic")
    settings.daytona_allow_local_execution = True
    with pytest.raises(ValueError):
        validate_configuration(settings, "python-basic")


def fake_daytona(settings, *, fail=None):
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = True
    settings.daytona_snapshot = "fixture-self-hosted"
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

        def download_file_stream(self, path, timeout=1800):
            assert path.endswith("/runtime.json") and timeout == settings.tool_timeout
            if fail == "download":
                raise RuntimeError("test interrupted download")
            yield json.dumps({"passed": True, "http": True, "restart": True}).encode()

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


@pytest.mark.parametrize("failure", [None, "upload", "exec", "download", "delete"])
def test_daytona_always_cleans_and_blocks_failed_checks(settings, plan, tmp_path, failure):
    product = tmp_path / "product"
    # This fixture validates the SDK cleanup protocol, not browser execution.
    generate_basic(plan, product, {"template": "python-basic", "frontend": "api-only"})
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
    checks = checks_for("yudao-vben")
    assert len(checks) == 1
    assert checks[0][1][-4:] == ["--template", "yudao-vben", "--database", "postgresql"]
    assert checks[0][1][2] == "/opt/rnd/harness/.venv/bin/python"
    assert "daytona_matrix_probe.py" in checks[0][1][3]
    with pytest.raises(PrerequisiteError):
        checks_for("shell:rm-anything")


def test_workflow_daytona_gate_blocks_packaging(settings, store, monkeypatch):
    from workbench.flow import Workflow

    workflow = Workflow(settings, store, None)
    assert workflow.after_verify({"verification": {"passed": True}}) == "sandbox"
    settings.sandbox_provider = "daytona"

    def failed(*args):
        raise PrerequisiteError("local sandbox verification rejected")

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
        assert argv[1].endswith("tools/aider/offline_runner.py") or argv[1].endswith(
            "tools\\aider\\offline_runner.py"
        )
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


def test_daytona_does_not_accept_http_only_receipt_for_generated_ui(settings, plan, tmp_path):
    product = tmp_path / "product"
    generate_basic(plan, product)
    client, events = fake_daytona(settings)
    with pytest.raises(PrerequisiteError):
        verify_in_daytona(product, "python-basic", settings, client=client)
    assert events[-1] == ("delete", "fixture-sandbox")
    receipt = json.loads((tmp_path / "daytona-verification.json").read_text(encoding="utf-8"))
    assert receipt["passed"] is False and "浏览器" in receipt["error_detail"]
````
