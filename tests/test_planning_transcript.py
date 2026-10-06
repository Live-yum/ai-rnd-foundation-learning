"""Planning summaries use real schemas, never a recursive search of model output."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr, create_model
from test_streaming_backend import Bytes, assistant_events, gateway, stream_body

from workbench.capability_contracts import CapabilityEdits
from workbench.catalog import Selection
from workbench.feature_planning import FeatureDesign, FeatureOutline
from workbench.llm import ModelFailure
from workbench.streaming import public_field, public_text


def feature_design(plan):
    return FeatureDesign(
        outline=FeatureOutline(
            summary="登录后提交报名，学生查看本人记录，管理员审核。",
            selection=Selection(),
            source_digest="a" * 64,
            features=[
                {
                    "id": "registration",
                    "title": "private-feature-title",
                    "requirements": ["source-0-0"],
                    "route": "native",
                    "capability": "typed-crud",
                    "entity": "task",
                }
            ],
        ),
        baseline=plan,
    )


def response(raw, streaming):
    if streaming:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw), size=100),
        )
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"role": "assistant", "content": raw}, "finish_reason": "stop"}]
        },
    )


@pytest.mark.parametrize("streaming", [False, True])
def test_feature_summary_is_shown_after_validation_and_replays_once(store, plan, streaming):
    value = feature_design(plan)
    raw = value.model_dump_json()
    calls = []

    def handler(request):
        calls.append(request)
        return response(raw, streaming)

    model = gateway(store, handler)
    run = new_run(store)
    for _ in range(2):
        assert model.complete(run, "plan:features:1", "JSON", {}, FeatureDesign) == value
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == value.outline.summary
    assert final["validation"] == "validated"
    assert final["transport"] == ("streaming" if streaming else "non_streaming")
    events = assistant_events(store, run)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    assert len([e for e in events if e["kind"] == "assistant_completed"]) == 1
    # Nested summaries must not appear as partial JSON or a draft result.
    assert not any(e["kind"] == "assistant_delta" for e in events)
    assert "private-feature-title" not in json.dumps(events)


def test_invalid_feature_design_never_exposes_its_nested_summary(store, plan):
    raw = feature_design(plan).model_dump()
    raw["outline"]["features"][0]["id"] = "invalid feature id"
    model = gateway(store, lambda _: response(json.dumps(raw), True))
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "plan:features:invalid", "JSON", {}, FeatureDesign)
    events = assistant_events(store, run)
    assert store.get_run(run)["model_calls"] == 2
    assert not any(e["kind"] in {"assistant_completed", "assistant_delta"} for e in events)
    assert raw["outline"]["summary"] not in json.dumps(events, ensure_ascii=False)


@pytest.mark.parametrize("cached", [False, True])
def test_nested_summary_redacts_current_and_rotated_keys_including_cached_replay(
    store, plan, cached
):
    value = feature_design(plan)
    value.outline.summary = "报名方案 old-key-canary current-key-canary"
    calls = []

    def handler(request):
        calls.append(request)
        return response(value.model_dump_json(), model.streaming)

    model = gateway(store, handler)
    store.settings.api_key = SecretStr("old-key-canary")
    store.settings._remember_model_keys(store.settings.model_configuration())
    store.settings.api_key = SecretStr("current-key-canary")
    model.streaming = not cached
    run = new_run(store)
    model.complete(run, "plan:features:secrets", "JSON", {}, FeatureDesign)
    if cached:
        assert not assistant_events(store, run)
        model.streaming = True
        model.complete(run, "plan:features:secrets", "JSON", {}, FeatureDesign)
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == "报名方案 [redacted] [redacted]"
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    events = json.dumps(assistant_events(store, run))
    assert "old-key-canary" not in events and "current-key-canary" not in events


def test_capability_edit_explanation_does_not_expose_source(store):
    value = CapabilityEdits(
        explanation="已生成本轮业务修改，等待独立验收。",
        files=[{"path": "app.py", "content": "private-source-canary"}],
    )
    model = gateway(store, lambda _: response(value.model_dump_json(), True))
    run = new_run(store)
    model.complete(run, "coding:extension:1", "JSON", {}, CapabilityEdits)
    assert store.transcript(run)["messages"][-1]["content"] == value.explanation
    assert "private-source-canary" not in json.dumps(assistant_events(store, run))


@pytest.mark.parametrize(
    ("module", "name"),
    [
        ("workbench.domain", "Requirement"),
        ("workbench.feature_planning", "FeatureDesign"),
        ("workbench.capability_contracts", "CapabilityEdits"),
    ],
)
def test_same_named_external_schemas_cannot_select_public_fields(module, name):
    schema = create_model(
        name,
        __module__=module,
        summary=(str, "private-summary"),
        explanation=(str, "private-source"),
    )
    assert public_field(schema) is None
    assert public_text(schema(), schema) == ""
