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
