import json

import httpx
import pytest
from conftest import new_run, requirement

from workbench.domain import Requirement
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
