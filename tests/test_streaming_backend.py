"""Offline provider streams only. No saved credentials or paid model calls."""

import asyncio
import json

import httpx
import pytest
from conftest import new_run, requirement
from fastapi.testclient import TestClient
from pydantic import SecretStr

from workbench.api import create_app
from workbench.domain import ModelReview, Patches, Requirement
from workbench.llm import ModelFailure, ModelGateway
from workbench.store import Store
from workbench.streaming import AssistantStream, event_stream, root_string_prefix


def frame(text=None, *, finish=None, **delta):
    if text is not None:
        delta["content"] = text
    return (
        "data: "
        + json.dumps(
            {
                "id": "fixture",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "offline",
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            },
            ensure_ascii=False,
        )
        + "\n\n"
    ).encode()


def stream_body(text, *, finish="stop", done=True, fragment_size=12):
    return (
        frame(role="assistant", reasoning_content="private-reasoning-canary")
        + b"".join(frame(text[i : i + fragment_size]) for i in range(0, len(text), fragment_size))
        + frame(finish=finish)
        + (
            b'data: {"choices":[],"usage":{"total_tokens":12,"extra":"private-usage"}}\n\n'
            b"data: [DONE]\n\n"
            if done
            else b""
        )
    )


class Bytes(httpx.SyncByteStream):
    def __init__(self, value, *, size=1):
        self.value, self.size, self.closed = value, size, False

    def __iter__(self):
        for offset in range(0, len(self.value), self.size):
            yield self.value[offset : offset + self.size]

    def close(self):
        self.closed = True


def gateway(store, handler):
    store.settings.base_url = "https://api.openai.com/v1"
    store.settings.model = "offline-model"
    store.settings.api_key = SecretStr("offline-key-secret")
    return ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True)


def assistant_events(store, run):
    return [r for r in store.events(run) if r["kind"].startswith("assistant_")]


def test_real_provider_stream_is_visible_before_response_finishes_and_replays_once(store):
    run = new_run(store)
    first = frame('{"summary":"你好')
    rest = stream_body('世界🌍","observations":[],"uncovered_requirements":[]}', fragment_size=7)
    seen = []

    class Progressive(httpx.SyncByteStream):
        def __iter__(self):
            yield first
            drafts = [e for e in assistant_events(store, run) if e["kind"] == "assistant_delta"]
            assert "".join(e["data"]["text"] for e in drafts) == "你好"
            assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))
            yield rest

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=Progressive()
        )

    model = gateway(store, handler)
    result = model.complete(run, "review:1", "JSON", {}, ModelReview)
    assert result.summary == "你好世界🌍"
    assert seen[0]["stream"] is True
    assert seen[0]["response_format"] == {"type": "json_object"}
    assert model.complete(run, "review:1", "JSON", {}, ModelReview) == result
    assert len(seen) == store.get_run(run)["model_calls"] == 1
    events = assistant_events(store, run)
    assert len([e for e in events if e["kind"] == "assistant_completed"]) == 1
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == "你好世界🌍" and final["validation"] == "validated"
    assert final["transport"] == "streaming"
    assert "private-reasoning-canary" not in json.dumps(events)
    assert "private-usage" not in json.dumps(events)
    assert store.model_records(run)[0]["usage"] == {"total_tokens": 12}
    assert store.messages(run) == [{"role": "user", "content": "个人任务 CRUD"}]
    other = Store(store.settings)
    try:
        assert other.transcript(run) == store.transcript(run)
    finally:
        other.engine.dispose()


@pytest.mark.parametrize("ensure_ascii", [True, False])
def test_unicode_provider_byte_boundaries_and_json_escape_boundaries(store, ensure_ascii):
    expected = '中文🌍「引号"」\\路径\n第二行'
    raw = json.dumps(ModelReview(summary=expected).model_dump(), ensure_ascii=ensure_ascii)
    body = Bytes(stream_body(raw, fragment_size=1))
    model = gateway(
        store,
        lambda _: httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body),
    )
    run = new_run(store)
    assert model.complete(run, "review:unicode", "JSON", {}, ModelReview).summary == expected
    events = assistant_events(store, run)
    assert "".join(e["data"]["text"] for e in events if e["kind"] == "assistant_delta") == expected
    assert body.closed


def test_only_allowlisted_root_field_is_projected_and_patch_source_is_never_streamed(store):
    value = Patches(
        explanation="已增加字段校验",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "source-code-private-canary",
            }
        ],
    )
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(value.model_dump_json()), size=50),
        ),
    )
    run = new_run(store)
    model.complete(run, "coding:1", "private-system-instruction", {}, Patches)
    events = assistant_events(store, run)
    assert store.transcript(run)["messages"][-1]["content"] == "已增加字段校验"
    assert "source-code-private-canary" not in json.dumps(events)
    assert "private-system-instruction" not in json.dumps(events)
    assert (
        root_string_prefix('{"facts":{"summary":"hidden"},"summary":"shown', "summary") == "shown"
    )
    assert root_string_prefix('{"facts":{"summary":"hidden', "summary") == ""


def test_credentials_are_redacted_across_every_chunk_and_hot_config_keys(store):
    model = gateway(store, lambda _: None)
    run = new_run(store)
    store.settings._remember_model_keys(store.settings.model_configuration())
    with store.settings._model_keys_lock:
        store.settings._model_keys.add("ui-only-hot-key")
        store.settings._model_keys.add("abab")
    observer = AssistantStream(
        store,
        store.settings,
        run,
        "response",
        "review",
        ModelReview,
        True,
        api_key=SecretStr("frozen-profile-key"),
    )
    observer.mode("streaming")
    value = "前缀 offline-key-secret ui-only-hot-key frozen-profile-key abab 后缀"
    raw = json.dumps({"summary": value}, ensure_ascii=False)
    for char in raw:
        observer.content(char)
    result = observer.completed_data(ModelReview(summary=value), ModelReview)
    store.assistant_event(run, "assistant_completed", result)
    text = "".join(
        e["data"]["text"] for e in assistant_events(store, run) if e["kind"] == "assistant_delta"
    )
    assert text == result["content"] == "前缀 [redacted] [redacted] [redacted] [redacted] 后缀"
    assert "offline-key-secret" not in json.dumps(assistant_events(store, run))
    assert model.streaming


@pytest.mark.parametrize(
    "finish,extra,expected_calls",
    [
        ("length", {}, 1),
        ("content_filter", {}, 1),
        ("stop", {"refusal": "private-refusal"}, 1),
        ("stop", {"tool_calls": [{"name": "private-tool"}]}, 1),
        ("aborted", {}, 2),
    ],
)
def test_failed_stream_never_completes_and_safe_failure_clears_draft(
    store, finish, extra, expected_calls
):
    calls = []

    def handler(request):
        calls.append(request)
        body = frame('{"summary":"draft"') + frame(finish=finish, **extra) + b"data: [DONE]\n\n"
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=Bytes(body)
        )

    model = gateway(store, handler)
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "review:bad", "JSON", {}, ModelReview)
    assert len(calls) == expected_calls
    assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))
    assert all(
        m["validation"] == "failed" and m["content"] == ""
        for m in store.transcript(run)["messages"]
        if m["role"] == "assistant"
    )
    assert "private-refusal" not in json.dumps(assistant_events(store, run))
    assert "private-tool" not in json.dumps(assistant_events(store, run))


@pytest.mark.parametrize(
    "raw,done",
    [
        ('{"summary":"first","summary":"second"}', True),
        ('{"summary":"incomplete"', True),
        ('{"summary":"valid"}', False),
        ('{"summary":"valid","observations":"wrong-type"}', True),
    ],
)
def test_strict_final_validation_and_missing_done_cannot_be_hidden_by_sdk(store, raw, done):
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw, done=done), size=19),
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "review:invalid", "JSON", {}, ModelReview)
    assert store.get_run(run)["model_calls"] == 2
    assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))


def test_json_only_provider_is_honest_completed_response_without_fake_deltas(store):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": requirement().model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "requirement:1", "JSON", {}, Requirement)
    assert len(seen) == 1 and seen[0]["stream"] is True
    assert not any(e["kind"] == "assistant_delta" for e in assistant_events(store, run))
    assert store.transcript(run)["messages"][-1]["transport"] == "non_streaming"
    assert store.transcript(run)["messages"][-1]["content"] == requirement().summary


def test_explicit_unsupported_stream_falls_back_once_without_downgrading_contract(store):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        if len(seen) == 1:
            return httpx.Response(
                400, json={"error": {"code": "unsupported_stream", "message": "private-error"}}
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": ModelReview(summary="完成").model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "review:1", "JSON", {}, ModelReview)
    assert [v["stream"] for v in seen] == [True, False]
    assert all(v["response_format"] == {"type": "json_object"} for v in seen)
    assert store.transcript(run)["messages"][-1]["transport"] == "non_streaming"
    assert "private-error" not in json.dumps(assistant_events(store, run))


def test_sse_auth_cursor_replay_pagination_and_no_generation_on_subscribe(settings):
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        store = app.state.store
        run = new_run(store)
        assert client.get(f"/runs/{run}/stream").status_code == 401
        assert client.get(f"/runs/{run}/transcript").status_code == 401
        headers = {"Authorization": "Bearer " + app.state.token}
        for index in range(231):
            store.record_event(run, "fixture", {"number": index})
        job = store.claim()
        store.finish(job, "WAITING_REQUIREMENT")
        response = client.get(f"/runs/{run}/stream", headers=headers)
        assert response.status_code == 200 and response.headers["content-type"].startswith(
            "text/event-stream"
        )
        ids = [int(line[4:]) for line in response.text.splitlines() if line.startswith("id: ")]
        assert len(ids) == 232 and ids == sorted(set(ids))
        assert "event: idle" in response.text
        again = client.get(
            f"/runs/{run}/stream?after={ids[3]}",
            headers={**headers, "Last-Event-ID": str(ids[200])},
        )
        assert [
            int(line[4:]) for line in again.text.splitlines() if line.startswith("id: ")
        ] == ids[201:]
        transcript = client.get(f"/runs/{run}/transcript", headers=headers).json()
        assert transcript["cursor"] == ids[-1]
        assert store.get_run(run)["model_calls"] == 0
        assert (
            client.get(
                f"/runs/{run}/stream", headers={**headers, "Last-Event-ID": "oops"}
            ).status_code
            == 422
        )
        assert client.get(f"/runs/{run}/stream?after=-1", headers=headers).status_code == 422
        assert client.get("/runs/missing/stream", headers=headers).status_code == 404


def test_disconnect_only_closes_subscription_and_durable_work_can_continue(store):
    run = new_run(store)
    job = store.claim()
    observer = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    observer.mode("streaming")
    observer.content('{"summary":"first')

    class Request:
        disconnected = False

        async def is_disconnected(self):
            return self.disconnected

    request = Request()

    async def subscribe():
        events = event_stream(request, store, run, 0, interval=0)
        first = await anext(events)
        assert "assistant_start" in first
        request.disconnected = True
        with pytest.raises(StopAsyncIteration):
            await anext(events)

    asyncio.run(subscribe())
    assert store.get_run(run)["status"] == "RUNNING"
    observer.content(' second"}')
    store.assistant_event(
        run,
        "assistant_completed",
        observer.completed_data(ModelReview(summary="first second"), ModelReview),
    )
    store.finish(job, "WAITING_REQUIREMENT")
    assert store.transcript(run)["messages"][-1]["content"] == "first second"


def test_new_attempt_marks_interrupted_draft_and_terminal_event_is_idempotent(store):
    run = new_run(store)
    old = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    old.content('{"summary":"unfinished')
    new = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    complete = new.completed_data(ModelReview(summary="完成"), ModelReview)
    store.assistant_event(run, "assistant_completed", complete)
    store.assistant_event(run, "assistant_completed", complete)
    old.content("still should not append")
    messages = store.transcript(run)["messages"]
    assert messages[-2]["code"] == "worker_interrupted" and messages[-2]["content"] == ""
    assert messages[-1]["content"] == "完成"
    assert sum(e["kind"] == "assistant_completed" for e in assistant_events(store, run)) == 1


def test_deepseek_real_sse_preserves_framework_strict_validation(store):
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(ModelReview(summary="审阅完成").model_dump_json()), size=2),
        )

    model = gateway(store, handler)
    store.settings.base_url = "https://api.deepseek.com"
    store.settings.model = "offline-deepseek"
    run = new_run(store)
    assert model.complete(run, "review:deepseek", "JSON", {}, ModelReview).summary == "审阅完成"
    assert calls[0]["stream"] is True and calls[0]["response_format"] == {"type": "json_object"}
    assert store.model_records(run)[0]["provider"] == "deepseek"


def test_schema_repair_keeps_failed_and_validated_attempts_separate(store):
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        raw = (
            '{"summary":"candidate","observations":false}'
            if len(calls) == 1
            else ModelReview(summary="corrected").model_dump_json()
        )
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw), size=33),
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "review:repair", "JSON", {}, ModelReview)
    messages = store.transcript(run)["messages"]
    assert len(calls) == 2
    assert messages[-2]["validation"] == "failed" and messages[-2]["content"] == ""
    assert messages[-1]["validation"] == "validated" and messages[-1]["content"] == "corrected"
    assert messages[-1]["message_id"] != messages[-2]["message_id"]


def test_saved_ui_only_secret_never_leaks_across_provider_fragments(store):
    from workbench.model_settings import ModelSettingsRepository

    repository = ModelSettingsRepository(store.settings)
    repository.update(
        {
            "expected_revision": repository.snapshot().revision,
            "default": {
                "base_url": "https://api.openai.com/v1",
                "model": "offline",
                "api_key": "ui-configuration-only-secret",
            },
        }
    )
    assert not store.settings.api_key.get_secret_value()
    raw = ModelReview(summary="Before ui-configuration-only-secret after").model_dump_json()
    model = ModelGateway(
        store.settings,
        store,
        httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=Bytes(stream_body(raw, fragment_size=1), size=3),
            )
        ),
        streaming=True,
    )
    run = new_run(store)
    model.complete(run, "review:ui-key", "JSON", {}, ModelReview)
    events = assistant_events(store, run)
    deltas = "".join(e["data"]["text"] for e in events if e["kind"] == "assistant_delta")
    assert deltas == "Before [redacted] after"
    assert "ui-configuration-only-secret" not in json.dumps(events)


def test_cached_legacy_completion_backfills_transcript_without_another_model_call(store):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": ModelReview(summary="cached").model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    model.streaming = False
    run = new_run(store)
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    model.streaming = True
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    assert len(calls) == 1
    assert store.transcript(run)["messages"][-1]["content"] == "cached"
    assert len(assistant_events(store, run)) == 1


def test_provider_stream_size_bound_is_enforced_before_line_buffering(store):
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(b"data: " + b"x" * 2_000_001, size=65536),
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure, match="响应过大"):
        model.complete(run, "review:oversize", "JSON", {}, ModelReview)
    assert store.get_run(run)["model_calls"] == 1
    assert store.transcript(run)["messages"][-1]["code"] == "response_too_large"


def test_public_text_length_cap_cannot_cut_a_secret_before_redaction(store):
    from workbench.streaming import MAX_PUBLIC_TEXT

    gateway(store, lambda _: None)
    observer = AssistantStream(
        store, store.settings, new_run(store), "limit", "coding", Patches, True
    )
    value = Patches(
        explanation="x" * (MAX_PUBLIC_TEXT - 4) + "offline-key-secret",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "pass",
            }
        ],
    )
    final = observer.completed_data(value, Patches)["content"]
    assert len(final) == MAX_PUBLIC_TEXT
    assert final.endswith("[red") and not final.endswith("offl")


@pytest.mark.parametrize("boundary", ["closed", "cap"])
def test_public_projection_never_reparses_or_retains_tail_after_boundary(
    settings, monkeypatch, boundary
):
    import workbench.streaming as streaming

    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "coding", Patches, True)
    calls = []
    project = streaming.root_string_projection

    def tracked(source, field):
        calls.append(len(source))
        return project(source, field)

    monkeypatch.setattr(streaming, "root_string_projection", tracked)
    if boundary == "closed":
        # An escaped quote must not end the projection; the genuine quote must.
        observer.content('{"explanation":"hello \\"')
        assert not observer.projection_finished
        observer.content(' world"')
        expected = 'hello " world'
    else:
        observer.content('{"explanation":"' + "x" * streaming.MAX_PUBLIC_TEXT)
        expected = "x" * streaming.MAX_PUBLIC_TEXT
    assert observer.projection_finished and observer.raw == ""
    boundary_calls = len(calls)
    tail = ',"patches":[{"content":"' + "private-body" * 20000 + '"}]}'
    for offset in range(0, len(tail), 32):
        observer.content(tail[offset : offset + 32])
    assert len(calls) == boundary_calls
    assert observer.raw == "" and observer.sent == expected
    assert not any(kind == "assistant_completed" for kind, _ in fake.events)


def test_projection_cap_keeps_split_key_held_until_full_validated_redaction(settings, monkeypatch):
    import workbench.streaming as streaming

    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    settings.api_key = SecretStr("cap-split-key-secret")
    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "coding", Patches, True)
    prefix = "x" * (streaming.MAX_PUBLIC_TEXT - 4)
    observer.content('{"explanation":"' + prefix + "cap-")
    assert observer.projection_finished and observer.sent == prefix

    def forbidden_reparse(*args):
        pytest.fail("Public projection must remain frozen after its display cap")

    monkeypatch.setattr(streaming, "root_string_projection", forbidden_reparse)
    observer.content('split-key-secret","patches":[] }')
    assert observer.sent == prefix and observer.raw == ""
    result = Patches(
        explanation=prefix + "cap-split-key-secret",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "pass",
            }
        ],
    )
    completed = observer.completed_data(result, Patches)
    assert completed["content"] == prefix + "[red"
    assert "cap-" not in "".join(data.get("text", "") for _, data in fake.events)


def test_worker_recovery_closes_abandoned_stream_after_model_profile_change(store):
    class WorkerCrash(BaseException):
        pass

    class CrashStream(httpx.SyncByteStream):
        def __iter__(self):
            yield frame('{"summary":"old model draft')
            raise WorkerCrash()

    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        body = (
            CrashStream()
            if len(calls) == 1
            else Bytes(
                stream_body(ModelReview(summary="new model result").model_dump_json()), size=31
            )
        )
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)

    model = gateway(store, handler)
    run = new_run(store)
    job = store.claim()
    with pytest.raises(WorkerCrash):
        model.complete(run, "review:recovery", "JSON", {}, ModelReview)
    draft = store.transcript(run)["messages"][-1]
    assert draft["validation"] == "pending" and draft["content"] == "old model draft"
    store.settings.model = "different-model-after-restart"
    store.recover()
    interrupted = store.transcript(run)["messages"][-1]
    assert interrupted["message_id"] == draft["message_id"]
    assert interrupted["validation"] == "failed" and interrupted["content"] == ""
    assert interrupted["code"] == "worker_interrupted"
    resumed = store.claim()
    assert resumed["id"] == job["id"]
    assert (
        model.complete(run, "review:recovery", "JSON", {}, ModelReview).summary
        == "new model result"
    )
    store.finish(resumed, "WAITING_REQUIREMENTS")
    messages = store.transcript(run)["messages"]
    assert messages[-1]["response_id"] != draft["response_id"]
    assert messages[-1]["validation"] == "validated"
    assert not any(row["validation"] == "pending" for row in messages)
    assert len(calls) == 2


def test_worker_recovery_repairs_committed_step_before_missing_completion_event(store, monkeypatch):
    class WorkerCrash(BaseException):
        pass

    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(
                stream_body(
                    ModelReview(summary="validated offline-key-secret result").model_dump_json()
                ),
                size=32,
            ),
        )

    model = gateway(store, handler)
    run = new_run(store)
    job = store.claim()
    append = store.assistant_event

    def crash_before_completion(run_id, kind, data):
        if kind == "assistant_completed":
            raise WorkerCrash()
        return append(run_id, kind, data)

    monkeypatch.setattr(store, "assistant_event", crash_before_completion)
    with pytest.raises(WorkerCrash):
        model.complete(run, "review:committed", "JSON", {}, ModelReview)
    draft = store.transcript(run)["messages"][-1]
    assert draft["validation"] == "pending"
    assert store.model_records(run)[0]["status"] == "validated"
    monkeypatch.setattr(store, "assistant_event", append)
    store.recover()
    store.recover()  # Recovery itself must be idempotent.
    completed = store.transcript(run)["messages"][-1]
    assert completed["message_id"] == draft["message_id"]
    assert completed["validation"] == "validated"
    assert completed["content"] == "validated [redacted] result"
    assert not any(event["kind"] == "assistant_failed" for event in assistant_events(store, run))
    resumed = store.claim()
    assert resumed["id"] == job["id"]
    model.complete(run, "review:committed", "JSON", {}, ModelReview)
    assert len(calls) == 1
    assert (
        sum(event["kind"] == "assistant_completed" for event in assistant_events(store, run)) == 1
    )
    assert "offline-key-secret" not in json.dumps(assistant_events(store, run))


def test_recovery_does_not_fail_drafts_outside_recovered_running_jobs(store):
    run = new_run(store)
    observer = AssistantStream(store, store.settings, run, "unrelated", "review", ModelReview, True)
    observer.content('{"summary":"queued fixture')
    store.recover()
    assert store.transcript(run)["messages"][-1]["validation"] == "pending"


@pytest.mark.parametrize(
    "keys,summary",
    [
        (("ababa",), "abababa"),
        (("ababa",), "ababababababa"),
        (("aa",), "aaaaaa"),
        (("abcde", "cdefg"), "abcdefghi"),
        (("aaaa", "aabaa"), "aaaaaabaaaaa"),
    ],
)
def test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix(settings, keys, summary):
    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    settings.api_key = SecretStr(keys[0])
    if len(keys) > 1:
        settings.planning_api_key = SecretStr(keys[1])
    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "review", ModelReview, True)
    final = observer.completed_data(ModelReview(summary=summary), ModelReview)["content"]
    for char in json.dumps({"summary": summary}):
        observer.content(char)
        assert final.startswith(observer.sent)
    if keys == ("ababa",) and summary == "abababa":
        assert final == "[redacted]ba"
        assert observer.sent == ""
    for key in keys:
        assert key not in "".join(data.get("text", "") for _, data in fake.events)
