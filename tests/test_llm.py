import json
from contextlib import contextmanager

import httpx
import pytest
from conftest import new_run, requirement

from workbench.domain import Plan, Requirement
from workbench.llm import ModelFailure, ModelGateway


def gateway(store, handler):
    store.settings.base_url = "https://example.test/v1"
    store.settings.model = "test-model"
    from pydantic import SecretStr

    store.settings.api_key = SecretStr("do-not-disclose")
    return ModelGateway(store.settings, store, httpx.MockTransport(handler))


def test_success_cache_and_usage(store):
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": requirement().model_dump_json()}}
                ],
                "usage": {"total_tokens": 12},
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    a = model.complete(run, "test", "instruction", {}, Requirement)
    assert model.complete(run, "test", "instruction", {}, Requirement) == a
    assert len(calls) == 1
    assert store.get_run(run)["model_calls"] == 1


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
def test_failures_not_fake_success(store, status):
    model = gateway(store, lambda _: httpx.Response(status, text="do-not-disclose"))
    with pytest.raises(ModelFailure) as error:
        model.complete(new_run(store), "error", "x", {}, Requirement)
    assert "do-not-disclose" not in str(error.value)


def test_invalid_json_bounded(store):
    model = gateway(
        store,
        lambda _: httpx.Response(
            200, json={"choices": [{"message": {"role": "assistant", "content": "not-json"}}]}
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "error", "x", {}, Requirement)
    assert store.get_run(run)["model_calls"] == 2


def test_schema_retry_contains_exact_validator_feedback_without_credentials(store):
    from workbench.domain import Plan
    from workbench.settings import ROOT

    valid = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    invalid = json.loads(json.dumps(valid))
    field = next(f for f in invalid["entities"][1]["fields"] if f["kind"] == "datetime")
    field["date_range"] = True
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(invalid if len(requests) == 1 else valid),
                        }
                    }
                ]
            },
        )

    model = gateway(store, handler)
    result = model.complete(new_run(store), "plan:1", "Preserve customer requirements", {}, Plan)
    assert result.business is not None
    assert len(requests) == 2
    retry = requests[1]["messages"]
    assert retry[-2]["role"] == "assistant"
    assert json.loads(retry[-2]["content"]) == invalid
    assert "日期范围只支持 date 类型" in retry[-1]["content"]
    assert "entities" in retry[-1]["content"] and "fields" in retry[-1]["content"]
    assert "do-not-disclose" not in json.dumps(retry)


def test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract(store):
    bad = '{\n "summary": "private-response-canary do-not-disclose",\n "users": ]}'
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": bad
                            if len(requests) == 1
                            else requirement().model_dump_json(),
                        },
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    payload = {"request": "Keep all confirmed fields"}
    assert model.complete(run, "requirement:json-repair", "instruction", payload, Requirement)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == 1
    failure = failures[0]["data"]
    detail = failure["diagnostic"]["details"][0]
    assert failure["code"] == "invalid_json"
    assert detail["category"] == "expected_value"
    assert detail["position"] == {"line": 3, "column": 11, "offset": bad.index("]")}
    assert detail["lengths"] == {"characters": len(bad), "bytes": len(bad.encode())}
    assert "private-response-canary" not in json.dumps(failures)
    assert "do-not-disclose" not in json.dumps(failures)
    feedback = requests[1]["messages"][-1]["content"]
    assert json.dumps(detail, ensure_ascii=False) in feedback
    assert "private-response-canary" not in feedback
    assert json.loads(requests[1]["messages"][1]["content"]) == payload
    assert (
        requests[0]["response_format"] == requests[1]["response_format"] == {"type": "json_object"}
    )


def test_large_valid_plan_does_not_trigger_a_local_json_size_or_node_threshold(store):
    expected = Plan.model_validate(
        {
            "title": "Large protocol boundary fixture",
            "data_scope": "per_user",
            "entities": [
                {
                    "name": f"record_{entity}",
                    "description": "Independent entity in a parser test",
                    "fields": [{"name": f"field_{field}", "kind": "text"} for field in range(16)],
                }
                for entity in range(8)
            ],
            "acceptance": ["Every declared entity and field remains present"],
        }
    )
    content = expected.model_dump_json(indent=2)
    assert len(content) > 30000
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        ),
    )
    run = new_run(store)
    assert model.complete(run, "plan:large-protocol", "instruction", {}, Plan) == expected
    assert store.get_run(run)["model_calls"] == 1
    assert not [event for event in store.events(run) if event["kind"] == "model_failure"]


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts(
    store, repair_succeeds
):
    compact = {
        "title": "Protocol repair fixture",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "record",
                "description": "Keep all requested fields and constraints",
                "fields": [
                    {"name": "note", "kind": "text", "required": False, "max_length": 80},
                    {"name": "quantity", "kind": "integer", "minimum": 0, "maximum": 12},
                ],
            }
        ],
        "acceptance": ["Owner isolation, optional notes up to 80 characters, quantity 0 to 12"],
    }
    expected = Plan.model_validate(compact, strict=True)
    valid = json.dumps(compact)
    invalid = valid + ',"private-tail-canary":false}'
    original_schema = Plan.model_json_schema()
    payload = {"confirmed_plan_scope": compact}
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": valid if repair_succeeds and len(requests) == 2 else invalid,
                        },
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    if repair_succeeds:
        assert model.complete(
            run, "plan:extra-data", "Preserve confirmed scope", payload, Plan
        ) == (expected)
    else:
        with pytest.raises(ModelFailure, match="两次尝试"):
            model.complete(run, "plan:extra-data", "Preserve confirmed scope", payload, Plan)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert Plan.model_json_schema() == original_schema
    assert requests[0]["messages"][0] == requests[1]["messages"][0]
    instruction = requests[0]["messages"][0]["content"]
    assert instruction.endswith(json.dumps(original_schema, ensure_ascii=False))
    assert "同一对象内的字段名只能出现一次" in instruction
    assert "required 的字段" in instruction
    assert "仅可省略已有 Schema 默认值且本轮需求无需指定的可选字段" in instruction
    assert "即使等于默认值也要保留" in instruction
    assert all(json.loads(request["messages"][1]["content"]) == payload for request in requests)
    assert all(request["response_format"] == {"type": "json_object"} for request in requests)
    feedback = requests[1]["messages"][-1]["content"]
    assert "extra_data" in feedback and "同一根对象的最后一个 } 之前" in feedback
    assert "保留全部业务字段" in feedback and "private-tail-canary" not in feedback
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == (1 if repair_succeeds else 2)
    assert all(event["data"]["code"] == "invalid_json" for event in failures)
    assert "private-tail-canary" not in json.dumps(failures)


@pytest.mark.parametrize("raises", [False, True])
def test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code(
    store, monkeypatch, raises
):
    from workbench import llm

    original = llm.structured_model

    @contextmanager
    def disagrees(*args, **kwargs):
        with original(*args, **kwargs) as structured:

            class RejectingParser:
                def invoke(self, *invoke_args, **invoke_kwargs):
                    result = structured.invoke(*invoke_args, **invoke_kwargs)
                    if raises:
                        raise ValueError("private-adapter-canary")
                    return {
                        **result,
                        "parsed": None,
                        "parsing_error": ValueError("private-adapter-canary"),
                    }

            yield RejectingParser()

    monkeypatch.setattr(llm, "structured_model", disagrees)
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": requirement().model_dump_json(),
                        },
                    }
                ]
            },
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure, match="两次尝试"):
        model.complete(run, "requirement:adapter", "instruction", {}, Requirement)
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == store.get_run(run)["model_calls"] == 2
    assert {event["data"]["code"] for event in failures} == {"structured_parser_disagreement"}
    assert all(event["data"]["diagnostic"]["phase"] == "model_execution" for event in failures)
    assert "private-adapter-canary" not in json.dumps(failures)


@pytest.mark.parametrize(
    "wire,category",
    [
        (b'{"private-wire-key": 1, "private-wire-key": 2}', "duplicate_json_key"),
        (b'{"private-wire-key": 1e9999}', "non_finite_json_number"),
    ],
)
def test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text(store, wire, category):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, headers={"content-type": "application/json"}, content=wire)

    model = gateway(store, handler)
    run = new_run(store)
    with pytest.raises(ModelFailure, match="两次尝试"):
        model.complete(run, "requirement:wire-rejection", "instruction", {}, Requirement)
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == store.get_run(run)["model_calls"] == 2
    for event in failures:
        detail = event["data"]["diagnostic"]["details"][0]
        assert event["data"]["code"] == "invalid_json"
        assert detail["category"] == category
        assert detail["lengths"] == {"bytes": len(wire)}
        assert "position" not in detail
    assert category in requests[1]["messages"][-1]["content"]
    assert "private-wire-key" not in json.dumps(failures)
    assert "private-wire-key" not in json.dumps(requests)
