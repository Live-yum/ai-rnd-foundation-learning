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
def no_network(monkeypatch, request):
    # Windows asyncio uses TCP socketpair for its private wakeup pipe. Create a
    # bounded pool before blocking connections; never allow arbitrary loopback
    # connects during the test, including while the SDK closes its async client.
    pair_factory = (
        socket._fallback_socketpair
        if getattr(request, "param", "platform") == "tcp"
        else socket.socketpair
    )
    available = []
    owned = []

    def deny(*args, **kwargs):
        pytest.fail("native schema tests must not connect to any endpoint")

    def private_socketpair(*args, **kwargs):
        if args or kwargs or not available:
            pytest.fail("unregistered or exhausted native-test socketpair")
        return available.pop()

    try:
        for _ in range(8):
            pair = pair_factory()
            owned.extend(pair)
            available.append(pair)
        monkeypatch.setattr(socket, "socketpair", private_socketpair)
        monkeypatch.setattr(socket.socket, "connect", deny)
        monkeypatch.setattr(socket.socket, "connect_ex", deny)
        monkeypatch.setattr(socket, "create_connection", deny)
        monkeypatch.setattr(socket, "getaddrinfo", deny)
        yield
    finally:
        for connection in owned:
            connection.close()


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


@pytest.mark.parametrize("no_network", ["platform", "tcp"], indirect=True)
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


@pytest.mark.parametrize("no_network", ["platform", "tcp"], indirect=True)
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


@pytest.mark.parametrize("no_network", ["platform", "tcp"], indirect=True)
@pytest.mark.parametrize("address", [("127.0.0.1", 9), ("192.0.2.1", 443)])
@pytest.mark.parametrize("operation", ["connect", "connect_ex", "create_connection", "getaddrinfo"])
def test_fixture_still_blocks_every_new_connection(address, operation):
    with (
        socket.socket() as connection,
        pytest.raises(pytest.fail.Exception, match="must not connect to any endpoint"),
    ):
        if operation in {"connect", "connect_ex"}:
            getattr(connection, operation)(address)
        elif operation == "create_connection":
            socket.create_connection(address)
        else:
            socket.getaddrinfo(*address)


@pytest.mark.parametrize("no_network", ["platform", "tcp"], indirect=True)
def test_fixture_socketpairs_are_connected_owned_and_bounded():
    pairs = [socket.socketpair() for _ in range(8)]
    for reader, writer in pairs:
        reader.settimeout(1)
        writer.sendall(b"self-pipe")
        assert reader.recv(9) == b"self-pipe"
        assert reader.getpeername() == writer.getsockname()
        assert writer.getpeername() == reader.getsockname()
    with pytest.raises(pytest.fail.Exception, match="unregistered or exhausted"):
        socket.socketpair()
    with pytest.raises(pytest.fail.Exception, match="unregistered or exhausted"):
        socket.socketpair(socket.AF_INET)
