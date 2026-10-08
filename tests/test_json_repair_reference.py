"""A malformed response remains failed even when its object can guide one retry."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import BaseModel, SecretStr, model_validator

from workbench.domain import Plan
from workbench.llm import ModelFailure, ModelGateway, _json_repair_reference
from workbench.model_diagnostics import json_diagnostics
from workbench.model_protocol import validate_content


def plan_object():
    return {
        "title": "Strict format repair",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "records",
                "description": "Preserve every requested constraint",
                "fields": [
                    {"name": "note", "kind": "text", "required": False, "max_length": 80},
                    {"name": "quantity", "kind": "integer", "minimum": 0, "maximum": 12},
                ],
            }
        ],
        "acceptance": ["Keep optional notes, numeric bounds and owner isolation"],
    }


def response(content, streaming):
    if not streaming:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )
    chunks = []
    for index, (fragment, finish) in enumerate(
        ((content[:-1], None), (content[-1:], None), ("", "stop"))
    ):
        chunks.append(
            "data: "
            + json.dumps(
                {
                    "id": "offline-format-repair",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": "offline-model",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": fragment,
                                **({"role": "assistant"} if index == 0 else {}),
                            },
                            "finish_reason": finish,
                        }
                    ],
                }
            )
            + "\n\n"
        )
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content="".join(chunks) + "data: [DONE]\n\n",
    )


def gateway(store, handler, streaming=False):
    store.settings.base_url = "https://example.test/v1"
    store.settings.model = "offline-model"
    store.settings.api_key = SecretStr("private-api-key-canary")
    return ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=streaming)


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("succeeds", [False, True])
def test_redundant_closers_require_another_validated_provider_response(store, streaming, succeeds):
    source = plan_object()
    valid = json.dumps(source)
    invalid = valid + "\n } ]\t} \r\n"
    payload = {
        "original_scope": source,
        "resolution_feedback": {"round": 2, "blocked": ["Keep all fields"]},
    }
    requests = []
    run = new_run(store)

    def handler(request):
        requests.append(json.loads(request.content))
        assert all(item["status"] == "failed" for item in store.model_records(run))
        assert not any(event["kind"] == "assistant_completed" for event in store.events(run))
        return response(valid if succeeds and len(requests) == 2 else invalid, streaming)

    model = gateway(store, handler, streaming)
    if succeeds:
        assert model.complete(
            run, "plan:repair", "Keep the original requirements", payload, Plan
        ) == Plan.model_validate(source)
        assert model.complete(
            run, "plan:repair", "Keep the original requirements", payload, Plan
        ) == Plan.model_validate(source)
    else:
        with pytest.raises(ModelFailure, match="两次尝试"):
            model.complete(run, "plan:repair", "Keep the original requirements", payload, Plan)
        assert all(item["status"] == "failed" for item in store.model_records(run))
        assert not any(event["kind"] == "assistant_completed" for event in store.events(run))
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert all(json.loads(item["messages"][1]["content"]) == payload for item in requests)
    assert all(item["response_format"] == {"type": "json_object"} for item in requests)
    references = [
        item["content"] for item in requests[1]["messages"] if item["role"] == "assistant"
    ]
    assert len(references) == 1
    assert json.loads(references[0]) == source
    assert "\n  " in references[0]
    assert "searchable" not in json.loads(references[0])["entities"][0]["fields"][0]
    assert invalid not in references
    assert "尚未批准" in requests[1]["messages"][-1]["content"]
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == (1 if succeeds else 2)
    assert {event["data"]["code"] for event in failures} == {"invalid_json"}
    assert all(
        event["data"]["diagnostic"]["details"][0]["category"] == "extra_closing_delimiters"
        for event in failures
    )
    assert "Preserve every requested constraint" not in json.dumps(failures)
    assert "private-api-key-canary" not in json.dumps(failures)


@pytest.mark.parametrize(
    "tail",
    [
        " private-tail-canary",
        ',"private-tail-canary":false}',
        " {}",
        " []",
        " null",
        " 1",
        '"private-tail-canary"',
        "\u00a0}",
        "\v}",
    ],
)
def test_data_or_non_json_whitespace_never_becomes_a_reference(tail):
    content = json.dumps(plan_object()) + tail
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    assert _json_repair_reference(error.value, content, Plan) is None
    details = json_diagnostics(error.value, content)
    assert details[0]["category"] == "extra_data"
    assert "private-tail-canary" not in json.dumps(details)


@pytest.mark.parametrize(
    "prefix",
    [
        '{"title":"first","title":"second"}',
        '{"quantity":NaN}',
        '{"quantity":1e9999}',
        '"private-scalar-canary"',
        "[]",
        "{}",
        '{"entities":"private-schema-canary"}',
    ],
)
def test_invalid_prefix_never_becomes_a_reference(prefix):
    content = prefix + "}"
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    assert _json_repair_reference(error.value, content, Plan) is None
    assert "private-" not in json.dumps(json_diagnostics(error.value, content))


def test_reference_keeps_source_values_when_a_validator_mutates_its_input():
    class MutatingSchema(BaseModel):
        value: str

        @model_validator(mode="before")
        @classmethod
        def normalizes(cls, data):
            data["value"] = "normalized"
            return data

    content = '{"value":"original"}}'
    with pytest.raises(ValueError) as error:
        validate_content(content, MutatingSchema, mode="json_object")
    reference = _json_repair_reference(error.value, content, MutatingSchema)
    assert json.loads(reference) == {"value": "original"}
    assert error.value.doc == content


def test_reference_encoding_respects_the_response_byte_bound(monkeypatch):
    from workbench import llm

    content = json.dumps(plan_object()) + "}"
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    monkeypatch.setattr(llm, "MAX_MODEL_CONTENT_BYTES", 10)
    assert _json_repair_reference(error.value, content, Plan) is None


def test_optional_reference_is_omitted_when_full_retry_context_would_not_fit(store):
    source = plan_object()
    source["entities"] = [
        {
            "name": f"records_{index}",
            "description": "Keep all source fields",
            "fields": [{"name": f"value_{field}", "kind": "text"} for field in range(8)],
        }
        for index in range(8)
    ]
    valid = json.dumps(source)
    assert len(json.dumps(source, indent=2)) > 4000
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            store.settings.max_context_chars = (
                sum(len(item["content"]) for item in body["messages"]) + 2000
            )
        return response(valid + "}" if len(requests) == 1 else valid, False)

    model = gateway(store, handler)
    run = new_run(store)
    payload = {
        "scope": "Keep all eight entities and their fields",
        "resolution_feedback": {"round": 1},
    }
    assert model.complete(
        run, "plan:bounded-reference", "Keep the original scope", payload, Plan
    ) == Plan.model_validate(source)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert [item["role"] for item in requests[1]["messages"]] == ["system", "user", "user"]
    assert json.loads(requests[1]["messages"][1]["content"]) == payload
    assert (
        sum(len(item["content"]) for item in requests[1]["messages"])
        <= store.settings.max_context_chars
    )
