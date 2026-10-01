import json

import httpx
import pytest
from conftest import new_run, requirement
from pydantic import SecretStr

from workbench.domain import Requirement
from workbench.llm import ModelGateway
from workbench.settings import Settings


def test_one_model_remains_the_default(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "BASE_URL=https://provider.example/v1\nAPI_KEY=secret-default\nMODE=one-model\n",
        encoding="utf-8",
    )
    settings = Settings(_env_file=env)
    settings.require_model()
    assert not settings.review_enabled
    for stage in ["requirements", "planning", "coding"]:
        model = settings.model_for(stage)
        assert model.model == "one-model"
        assert model.base_url == "https://provider.example/v1"
        assert model.api_key.get_secret_value() == "secret-default"
        assert "secret-default" not in str(model.public())


def test_mixed_per_stage_models_and_provider_keys(tmp_path):
    env = tmp_path / ".env"
    env.write_text("""BASE_URL=https://base.example/v1
API_KEY=default-secret
MODE=default
REQUIREMENTS_MODE=cheap-analysis
PLANNING_BASE_URL=https://planning.example/v1
PLANNING_API_KEY=planning-secret
PLANNING_MODEL=planner
CODING_MODE=coder
REVIEW_BASE_URL=https://review.example/v1
REVIEW_API_KEY=review-secret
REVIEW_MODE=reviewer
""")
    settings = Settings(_env_file=env)
    settings.require_model()
    assert settings.model_for("requirements").model == "cheap-analysis"
    assert settings.model_for("coding").base_url == "https://base.example/v1"
    assert settings.model_for("planning").api_key.get_secret_value() == "planning-secret"
    assert settings.model_for("review").model == "reviewer"
    assert settings.review_enabled
    assert "default-secret" not in settings.redact("default-secret planning-secret review-secret")
    assert "planning-secret" not in settings.redact("default-secret planning-secret review-secret")


def test_new_endpoint_never_inherits_another_provider_key():
    s = Settings(
        base_url="https://base.example/v1",
        api_key="secret",
        model="a",
        planning_base_url="https://other.example/v1",
        _env_file=None,
    )
    with pytest.raises(ValueError, match="API_KEY"):
        s.model_for("planning")


def test_gateway_sends_each_stage_to_its_selected_model(store):
    settings = store.settings
    settings.base_url = "https://base.example/v1"
    settings.api_key = SecretStr("base-key")
    settings.model = "shared-model"
    settings.planning_base_url = "https://planner.example/v1"
    settings.planning_api_key = SecretStr("planner-key")
    settings.planning_model = "planner"
    seen = []

    def handler(request):
        seen.append(
            (
                request.url.host,
                request.headers["authorization"],
                json.loads(request.content)["model"],
            )
        )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": requirement().model_dump_json()}}
                ]
            },
        )

    gateway = ModelGateway(settings, store, httpx.MockTransport(handler))
    rid = new_run(store)
    gateway.complete(rid, "requirement:1", "requirements", {}, Requirement)
    gateway.complete(rid, "plan:1", "plan", {}, Requirement)
    assert seen == [
        ("base.example", "Bearer base-key", "shared-model"),
        ("planner.example", "Bearer planner-key", "planner"),
    ]
    assert {x["stage"] for x in store.model_records(rid)} == {"requirements", "planning"}
    settings.planning_model = "planner-v2"
    gateway.complete(rid, "plan:1", "plan", {}, Requirement)
    assert (
        len(seen) == 3
    )  # Changed model must not read a previous provider/model's cached response.


def test_default_model_budget_does_not_kill_long_conversations(store):
    rid = new_run(store)
    assert store.settings.max_rounds == 0 and store.settings.max_model_calls == 0
    for _ in range(80):
        store.reserve_model_call(rid)
    assert store.get_run(rid)["model_calls"] == 80
