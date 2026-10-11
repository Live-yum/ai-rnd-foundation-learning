# tests/test_native_schema.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding.candidates`、`workbench.coding.ports`、`workbench.filesystem`、`workbench.llm`、`workbench.model_protocol`、`workbench.native_schema`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `no_network`（L22–L27）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fixture`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `no_network.deny`（L23–L24）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `model_gateway`（L30–L45）：接收`store`、`handler`、`native`、`model`、`streaming`。 调用`store.settings.model_copy`、`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L43的`ModelGateway( settings, store, httpx.MockTransport(handler), native_strict=native, streami…`。
- `invoke`（L48–L56）：接收`gateway`、`run`、`key`、`task`。 调用`design`、`gateway.complete`、`task.model_dump`、`approved_turn_schema`。 返回路径：L50的`gateway.complete( run, key, "Return the approved action.", {"task": task.model_dump()}, ap…`。
- `response`（L59–L77）：接收`content`、`status`、`finish`、`refusal`。 控制顺序：L60按`status != 200`分支。 调用`httpx.Response`。 返回路径：L61的`httpx.Response(status, json={"error": {"message": "private-provider-text"}})`；L62的`httpx.Response( 200, json={ "id": "offline", "object": "chat.completion", "created": 0, "m…`。
- `edit`（L80–L90）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L81的`{ "operation": "edit", "edits": { "explanation": "offline", "files": [ {"path": "app.py", …`。
- `test_actual_sdk_wire_closed_required_union_and_safe_success_receipt`（L93–L133）：接收`store`。 控制顺序：L123断言`invoke(model, run).operation == "submit"`；L124断言`invoke(model, run).operation == "submit"`；L125断言`len(seen) == 1`；L126断言`approved_turn_schema(design().implementation.tasks[0]).model_json_schema() == origina…`；L128断言`record["output_mode"] == "json_schema"`；L129断言`record["native_strict_requested"] is True`；L130断言`record["native_request_verified"] is True`；L131断言`record["native_local_conformant"] is True`。后续分支沿下方源码相同行号继续阅读。 调用`approved_turn_schema(design().implementation.tasks[0]).model_json…`、`approved_turn_schema`、`design`、`model_gateway`、`new_run`、`invoke`、`len`、`store.model_records`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sdk_wire_closed_required_union_and_safe_success_receipt.handler`（L97–L119）：接收`request`。 控制顺序：L100断言`set(body) == { "model", "messages", "stream", "max_completion_tokens", "response_form…`；L107断言`body["stream"] is False and body["max_completion_tokens"] == 8192`；L108断言`len(request.content) <= 4 * 40000`；L109断言`request.extensions["timeout"]["read"] == 60`；L111断言`fmt["type"] == "json_schema" and fmt["json_schema"]["strict"] is True`；L113遍历`(schema, *schema["$defs"].values())`；L114断言`obj["additionalProperties"] is False`；L115断言`set(obj["required"]) == set(obj["properties"])`。后续分支沿下方源码相同行号继续阅读。 调用`seen.append`、`json.loads`、`set`、`len`、`schema["$defs"].values`、`response`。 返回路径：L119的`response('{"operation":"submit","edits":null}')`。
- `test_http_200_ignoring_strict_stops_once_without_repair`（L151–L185）：接收`store`、`kind`。 控制顺序：L153按`kind == "missing_edits"`分支；L155按`kind == "missing_before"`分支；L157按`kind == "extra"`分支；L159按`kind == "nested_extra"`分支；L161按`kind == "type"`分支；L163按`kind == "union"`分支；L181断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L183断言`record["code"] == "native_schema_violation"`。后续分支沿下方源码相同行号继续阅读。 调用`edit`、`value["edits"]["files"][1].pop`、`json.dumps`、`{ "malformed": content + "}", "duplicate": '{"operation":"submit"…`、`new_run`、`pytest.raises`、`invoke`、`model_gateway`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_200_ignoring_strict_stops_once_without_repair.handler`（L174–L176）：接收`request`。 调用`calls.append`、`response`。 返回路径：L176的`response(content)`。
- `test_rejection_timeout_and_refusal_have_no_compatibility_retry`（L200–L224）：接收`store`、`kind`、`code`、`count`。 控制顺序：L221断言`len(calls) == store.get_run(run)["model_calls"] == count`；L223断言`[r["code"] for r in records] == [code] * count`；L224断言`"private" not in json.dumps(records)`。 调用`new_run`、`pytest.raises`、`invoke`、`model_gateway`、`len`、`store.get_run`、`store.model_records`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejection_timeout_and_refusal_have_no_compatibility_retry.handler`（L203–L216）：接收`request`。 控制顺序：L205按`kind == "timeout"`分支；L206抛异常，停止当前正常路径；L207按`kind == "stream"`分支。 调用`calls.append`、`httpx.ReadTimeout`、`httpx.Response`、`response`、`kind.isdigit`、`int`。 返回路径：L208的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, content=b"data: {}\n\n…`；L211的`response( '{"operation":"submit","edits":null}', status=int(kind) if kind.isdigit() else 2…`。
- `test_native_schema_keeps_original_business_validation`（L228–L243）：接收`store`、`kind`。 控制顺序：L230按`kind == "edit_null"`分支；L232按`kind == "submit_edits"`分支；L234按`kind == "wrong_path"`分支；L242断言`[r["code"] for r in records] == ["schema_validation"] * 2`；L243断言`all(r["native_local_conformant"] is True for r in records)`。 调用`edit`、`new_run`、`pytest.raises`、`invoke`、`model_gateway`、`response`、`json.dumps`、`store.model_records`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_edit_still_requires_matching_preimage`（L246–L262）：接收`store`、`tmp_path`。 调用`base.mkdir`、`(base / "app.py").write_text`、`edit`、`sha`、`model_gateway`、`response`、`json.dumps`、`invoke`、`new_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incompatible_sdk_or_scope_stops_before_network`（L274–L289）：接收`store`、`monkeypatch`、`kind`、`code`。 控制顺序：L275按`kind == "version"`分支；L287断言`record["code"] == code`；L288断言`record["native_request_verified"] is False`；L289断言`record["native_local_conformant"] is None`。 调用`monkeypatch.setattr`、`model_gateway`、`pytest.fail`、`new_run`、`pytest.raises`、`invoke`、`store.model_records`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outbound_drift_never_reaches_transport`（L309–L349）：接收`store`、`monkeypatch`、`change`。 控制顺序：L349断言`store.model_records(run)[0]["code"] == "native_request_mismatch"`。 调用`monkeypatch.setattr`、`new_run`、`pytest.raises`、`invoke`、`model_gateway`、`pytest.fail`、`store.model_records`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outbound_drift_never_reaches_transport.changed`（L312–L343）：接收`request`。 控制顺序：L314按`change == "schema"`分支；L316按`change == "strict"`分支；L318按`change == "strict_integer"`分支；L320按`change == "format"`分支；L322按`change == "tools"`分支；L324按`change == "stream"`分支；L326按`change == "tokens"`分支；L328按`change == "legacy_tokens"`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`body["response_format"]["json_schema"]["schema"]["required"].remo…`、`body.pop`、`copy.deepcopy`、`httpx.Request`、`original`。 返回路径：L343的`original(self, bad)`。
- `test_json_object_default_and_cache_are_separate_from_opt_in`（L352–L362）：接收`store`。 控制顺序：L362断言`seen == ["json_object", "json_schema"]`。 调用`new_run`、`invoke`、`model_gateway`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_object_default_and_cache_are_separate_from_opt_in.handler`（L355–L357）：接收`request`。 调用`seen.append`、`json.loads`、`response`。 返回路径：L357的`response('{"operation":"submit","edits":null}')`。
- `test_cached_native_result_cannot_bypass_sdk_version_preflight`（L365–L382）：接收`store`、`monkeypatch`。 控制顺序：L374断言`invoke(model, run).operation == "submit"`；L378断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L380断言`record["code"] == "native_sdk_unsupported"`；L381断言`record["attempt"] is None`；L382断言`record["native_request_verified"] is False`。 调用`model_gateway`、`new_run`、`invoke`、`monkeypatch.setattr`、`pytest.raises`、`len`、`store.get_run`、`store.model_records`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cached_native_result_cannot_bypass_sdk_version_preflight.handler`（L368–L370）：接收`request`。 调用`calls.append`、`response`。 返回路径：L370的`response('{"operation":"submit","edits":null}')`。
- `test_native_guards_are_bound_into_isolation_source_identity`（L386–L394）：接收`monkeypatch`、`name`。 控制顺序：L394断言`execution.verifier_identity() != original`。 调用`execution.verifier_identity`、`monkeypatch.setattr`、`real_sha`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_transport_cannot_be_constructed_without_wire_guard`（L397–L401）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L401断言`failure.value.code == "native_request_mismatch"`。 调用`OutputContract`、`pytest.raises`、`AuditedTransport`、`httpx.MockTransport`、`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejected_stream_cleanup_error_cannot_authorize_retry`（L404–L424）：接收`store`。 控制顺序：L423断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L424断言`store.model_records(run)[0]["code"] == "native_request_mismatch"`。 调用`new_run`、`pytest.raises`、`invoke`、`model_gateway`、`len`、`store.get_run`、`store.model_records`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejected_stream_cleanup_error_cannot_authorize_retry.BrokenClose`（L407–L412）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_rejected_stream_cleanup_error_cannot_authorize_retry.BrokenClose.__iter__`（L408–L409）：不接收显式业务参数，从已配置对象/模块读取依赖。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_rejected_stream_cleanup_error_cannot_authorize_retry.BrokenClose.close`（L411–L412）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L412抛异常，停止当前正常路径。 调用`httpx.ReadError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejected_stream_cleanup_error_cannot_authorize_retry.handler`（L414–L418）：接收`request`。 调用`calls.append`、`httpx.Response`、`BrokenClose`。 返回路径：L416的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=BrokenClose() )`。

</details>

**创建路径：** `tests/test_native_schema.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L424。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15152`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_schema.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "486a9c781169c9c7b077a52f0b1e46984298ac91b2fa3457269300f9b2b86c28"} -->
````python
# tests/test_native_schema.py
"""Real locked SDK serialization; only lowest HTTP is replaced, no external model."""

import copy
import json
import socket

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from scripts.sla_fixture import design
from workbench.coding.candidates import apply_candidate
from workbench.coding.ports import approved_turn_schema
from workbench.filesystem import sha
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_protocol import AuditedTransport, OutputContract, OutputFailure
from workbench.native_schema import NativeSchema


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        pytest.fail("native schema tests must not connect to any endpoint")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def model_gateway(store, handler, *, native=True, model="offline-native", streaming=False):
    settings = store.settings.model_copy(
        update={
            "coding_base_url": "https://fixture.invalid/v1",
            "coding_model": model,
            "coding_api_key": SecretStr("offline-secret"),
            "coding_provider": "compatible",
            "coding_output_mode": "json_object",
            "coding_max_output_tokens": 8192,
            "max_context_chars": 40000,
            "llm_timeout": 60,
        }
    )
    return ModelGateway(
        settings, store, httpx.MockTransport(handler), native_strict=native, streaming=streaming
    )


def invoke(gateway, run, *, key="coding:mini_swe:offline:0", task=None):
    task = task or design().implementation.tasks[0]
    return gateway.complete(
        run,
        key,
        "Return the approved action.",
        {"task": task.model_dump()},
        approved_turn_schema(task),
    )


def response(content, *, status=200, finish="stop", refusal=None):
    if status != 200:
        return httpx.Response(status, json={"error": {"message": "private-provider-text"}})
    return httpx.Response(
        200,
        json={
            "id": "offline",
            "object": "chat.completion",
            "created": 0,
            "model": "offline-native",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": finish,
                    "message": {"role": "assistant", "content": content, "refusal": refusal},
                }
            ],
        },
    )


def edit():
    return {
        "operation": "edit",
        "edits": {
            "explanation": "offline",
            "files": [
                {"path": "app.py", "before_sha256": "a" * 64, "content": "# candidate\n"},
                {"path": "sla.py", "before_sha256": None, "content": "# new module\n"},
            ],
        },
    }


def test_actual_sdk_wire_closed_required_union_and_safe_success_receipt(store):
    seen = []
    original = approved_turn_schema(design().implementation.tasks[0]).model_json_schema()

    def handler(request):
        seen.append(request)
        body = json.loads(request.content)
        assert set(body) == {
            "model",
            "messages",
            "stream",
            "max_completion_tokens",
            "response_format",
        }
        assert body["stream"] is False and body["max_completion_tokens"] == 8192
        assert len(request.content) <= 4 * 40000
        assert request.extensions["timeout"]["read"] == 60
        fmt = body["response_format"]
        assert fmt["type"] == "json_schema" and fmt["json_schema"]["strict"] is True
        schema = fmt["json_schema"]["schema"]
        for obj in (schema, *schema["$defs"].values()):
            assert obj["additionalProperties"] is False
            assert set(obj["required"]) == set(obj["properties"])
        assert {"type": "null"} in schema["properties"]["edits"]["anyOf"]
        before = schema["$defs"]["SourceEdit"]["properties"]["before_sha256"]
        assert {"type": "null"} in before["anyOf"] and "default" not in before
        return response('{"operation":"submit","edits":null}')

    model = model_gateway(store, handler)
    run = new_run(store)
    assert invoke(model, run).operation == "submit"
    assert invoke(model, run).operation == "submit"  # Same durable entry, no extra request.
    assert len(seen) == 1
    assert approved_turn_schema(design().implementation.tasks[0]).model_json_schema() == original
    record = store.model_records(run)[0]
    assert record["output_mode"] == "json_schema"
    assert record["native_strict_requested"] is True
    assert record["native_request_verified"] is True
    assert record["native_local_conformant"] is True
    assert record["native_provider_enforcement"] == "unknown"
    assert record["native_http_status"] == 200


@pytest.mark.parametrize(
    "kind",
    [
        "missing_edits",
        "missing_before",
        "extra",
        "nested_extra",
        "type",
        "union",
        "malformed",
        "duplicate",
        "nonfinite",
        "null_root",
    ],
)
def test_http_200_ignoring_strict_stops_once_without_repair(store, kind):
    value = edit()
    if kind == "missing_edits":
        value = {"operation": "submit"}
    elif kind == "missing_before":
        value["edits"]["files"][1].pop("before_sha256")
    elif kind == "extra":
        value["private-key"] = "private-content"
    elif kind == "nested_extra":
        value["edits"]["files"][0]["private-key"] = "private-content"
    elif kind == "type":
        value["operation"] = 1
    elif kind == "union":
        value["edits"] = []
    content = json.dumps(value)
    content = {
        "malformed": content + "}",
        "duplicate": '{"operation":"submit","operation":"submit","edits":null}',
        "nonfinite": '{"operation":"submit","edits":NaN}',
        "null_root": "null",
    }.get(kind, content)
    calls = []

    def handler(request):
        calls.append(request)
        return response(content)

    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(model_gateway(store, handler), run)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    record = store.model_records(run)[0]
    assert record["code"] == "native_schema_violation"
    assert record["native_local_conformant"] is False
    assert "private-content" not in json.dumps(record)


@pytest.mark.parametrize(
    "kind,code,count",
    [
        ("400", "native_format_rejected", 1),
        ("422", "native_format_rejected", 1),
        ("500", "http_500", 2),
        ("timeout", "transport_error", 2),
        ("refusal", "refusal", 1),
        ("finish", "invalid_finish_reason", 1),
        ("stream", "native_request_mismatch", 1),
    ],
)
def test_rejection_timeout_and_refusal_have_no_compatibility_retry(store, kind, code, count):
    calls = []

    def handler(request):
        calls.append(request)
        if kind == "timeout":
            raise httpx.ReadTimeout("private-provider-text")
        if kind == "stream":
            return httpx.Response(
                200, headers={"content-type": "text/event-stream"}, content=b"data: {}\n\n"
            )
        return response(
            '{"operation":"submit","edits":null}',
            status=int(kind) if kind.isdigit() else 200,
            refusal="private-refusal" if kind == "refusal" else None,
            finish=None if kind == "finish" else "stop",
        )

    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(model_gateway(store, handler), run)
    assert len(calls) == store.get_run(run)["model_calls"] == count
    records = store.model_records(run)
    assert [r["code"] for r in records] == [code] * count
    assert "private" not in json.dumps(records)


@pytest.mark.parametrize("kind", ["edit_null", "submit_edits", "wrong_path", "duplicate_path"])
def test_native_schema_keeps_original_business_validation(store, kind):
    value = edit()
    if kind == "edit_null":
        value["edits"] = None
    elif kind == "submit_edits":
        value["operation"] = "submit"
    elif kind == "wrong_path":
        value["edits"]["files"][1]["path"] = "other.py"
    else:
        value["edits"]["files"][1]["path"] = "app.py"
    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(model_gateway(store, lambda _: response(json.dumps(value))), run)
    records = store.model_records(run)
    assert [r["code"] for r in records] == ["schema_validation"] * 2
    assert all(r["native_local_conformant"] is True for r in records)


def test_native_edit_still_requires_matching_preimage(store, tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (base / "app.py").write_text("# baseline\n")
    value = edit()
    value["edits"]["files"][0]["before_sha256"] = sha(base / "app.py")
    model = model_gateway(store, lambda _: response(json.dumps(value)))
    turn = invoke(model, new_run(store))
    plan = design().implementation
    apply_candidate(
        base, turn.edits, plan.tasks[0], plan.selection.model_dump(), tmp_path / "accepted"
    )
    (base / "app.py").write_text("# changed after response\n")
    with pytest.raises(ValueError):
        apply_candidate(
            base, turn.edits, plan.tasks[0], plan.selection.model_dump(), tmp_path / "stale"
        )


@pytest.mark.parametrize(
    "kind,code",
    [
        ("legacy", "native_request_mismatch"),
        ("version", "native_sdk_unsupported"),
        ("stage", "native_scope_rejected"),
        ("streaming", "native_scope_rejected"),
    ],
)
def test_incompatible_sdk_or_scope_stops_before_network(store, monkeypatch, kind, code):
    if kind == "version":
        monkeypatch.setattr("workbench.native_schema.version", lambda _: "unreviewed")
    gateway = model_gateway(
        store,
        lambda _: pytest.fail("guard allowed network"),
        model="gpt-4" if kind == "legacy" else "offline-native",
        streaming=kind == "streaming",
    )
    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(gateway, run, key="coding:other" if kind == "stage" else "coding:mini_swe:offline:0")
    record = store.model_records(run)[0]
    assert record["code"] == code
    assert record["native_request_verified"] is False
    assert record["native_local_conformant"] is None


@pytest.mark.parametrize(
    "change",
    [
        "schema",
        "strict",
        "strict_integer",
        "format",
        "tools",
        "stream",
        "tokens",
        "legacy_tokens",
        "bytes",
        "url",
        "timeout",
        "model",
    ],
)
def test_outbound_drift_never_reaches_transport(store, monkeypatch, change):
    original = NativeSchema.check_request

    def changed(self, request):
        body = json.loads(request.content)
        if change == "schema":
            body["response_format"]["json_schema"]["schema"]["required"].remove("edits")
        elif change == "strict":
            body["response_format"]["json_schema"]["strict"] = False
        elif change == "strict_integer":
            body["response_format"]["json_schema"]["strict"] = 1
        elif change == "format":
            body["response_format"] = {"type": "json_object"}
        elif change == "tools":
            body["tools"] = []
        elif change == "stream":
            body["stream"] = True
        elif change == "tokens":
            body["max_completion_tokens"] = 8193
        elif change == "legacy_tokens":
            body["max_tokens"] = body.pop("max_completion_tokens")
        elif change == "bytes":
            body["messages"][0]["content"] = "x" * 160001
        elif change == "model":
            body["model"] = "substitution"
        extensions = copy.deepcopy(request.extensions)
        if change == "timeout":
            extensions["timeout"]["read"] = 61
        bad = httpx.Request(
            "POST",
            "https://other.invalid/v1/chat/completions" if change == "url" else request.url,
            json=body,
            extensions=extensions,
        )
        return original(self, bad)

    monkeypatch.setattr(NativeSchema, "check_request", changed)
    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(model_gateway(store, lambda _: pytest.fail("guard allowed network")), run)
    assert store.model_records(run)[0]["code"] == "native_request_mismatch"


def test_json_object_default_and_cache_are_separate_from_opt_in(store):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content)["response_format"]["type"])
        return response('{"operation":"submit","edits":null}')

    run = new_run(store)
    invoke(model_gateway(store, handler, native=False), run)
    invoke(model_gateway(store, handler, native=True), run)
    assert seen == ["json_object", "json_schema"]


def test_cached_native_result_cannot_bypass_sdk_version_preflight(store, monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        return response('{"operation":"submit","edits":null}')

    model = model_gateway(store, handler)
    run = new_run(store)
    assert invoke(model, run).operation == "submit"
    monkeypatch.setattr("workbench.native_schema.version", lambda _: "unreviewed")
    with pytest.raises(ModelFailure):
        invoke(model, run)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    record = store.model_records(run)[-1]
    assert record["code"] == "native_sdk_unsupported"
    assert record["attempt"] is None
    assert record["native_request_verified"] is False


@pytest.mark.parametrize("name", ["workbench/native_schema.py", "workbench/model_protocol.py"])
def test_native_guards_are_bound_into_isolation_source_identity(monkeypatch, name):
    from workbench import capability_execution as execution

    original = execution.verifier_identity()
    real_sha = execution.sha
    monkeypatch.setattr(
        execution, "sha", lambda path: "f" * 64 if path == execution.ROOT / name else real_sha(path)
    )
    assert execution.verifier_identity() != original


def test_native_transport_cannot_be_constructed_without_wire_guard():
    contract = OutputContract("compatible", "json_schema", "mini_swe_native_strict", {})
    with pytest.raises(OutputFailure) as failure:
        AuditedTransport(contract, httpx.MockTransport(lambda _: pytest.fail("network")))
    assert failure.value.code == "native_request_mismatch"


def test_rejected_stream_cleanup_error_cannot_authorize_retry(store):
    calls = []

    class BrokenClose(httpx.SyncByteStream):
        def __iter__(self):
            yield b"data: {}\n\n"

        def close(self):
            raise httpx.ReadError("private-cleanup-error")

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=BrokenClose()
        )

    run = new_run(store)
    with pytest.raises(ModelFailure):
        invoke(model_gateway(store, handler), run)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    assert store.model_records(run)[0]["code"] == "native_request_mismatch"
````
