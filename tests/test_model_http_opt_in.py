"""HTTP transport is an explicit process setting; it cannot be enabled by a draft."""

import json

import pytest
from pydantic import SecretStr

from workbench.model_settings import ModelSettingsError, ModelSettingsRepository
from workbench.settings import Settings, validate_model_url

ENDPOINT = "http://model.example:8317/v1"


def test_http_requires_explicit_operator_configuration(settings):
    settings.base_url = ENDPOINT
    settings.model = "test-model"
    settings.api_key = SecretStr("dummy-http-key")
    assert not settings.models_ready()
    settings.allow_insecure_model_http = True
    settings.require_model()
    snapshot = settings.model_for("planning")
    assert snapshot.base_url == ENDPOINT
    assert snapshot.validate_endpoint() is snapshot
    assert "dummy-http-key" not in json.dumps(snapshot.public())
    settings.allow_insecure_model_http = False
    assert not settings.models_ready()
    # Calls already holding an immutable, operator-approved snapshot remain coherent.
    assert snapshot.validate_endpoint() is snapshot


def test_opt_in_applies_to_saved_profiles_but_is_never_persisted(settings):
    settings.allow_insecure_model_http = True
    repository = ModelSettingsRepository(settings)
    result = repository.update(
        {
            "expected_revision": "0",
            "default": {"base_url": ENDPOINT, "model": "test", "api_key": "dummy-http-key"},
        }
    )
    assert result["ready"]
    assert "allow_insecure" not in repository.path.read_text(encoding="utf-8")
    # Restarting without the process opt-in must fail closed even for a saved URL.
    fresh = Settings(data_dir=settings.data_dir, _env_file=None)
    assert not fresh.models_ready()
    fresh.allow_insecure_model_http = True
    assert fresh.models_ready()
    with pytest.raises(ModelSettingsError, match="未知"):
        repository.update(
            {"expected_revision": result["revision"], "allow_insecure_model_http": True}
        )
    with pytest.raises(ModelSettingsError, match="未知"):
        repository.update(
            {
                "expected_revision": result["revision"],
                "default": {"allow_insecure_http": True},
            }
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://user:secret@model.example/v1",
        "http://model.example/v1?key=secret",
        "http://model.example/v1/chat/completions",
        "http://model.example:0/v1",
        "http://model.example/v1#secret",
        "file:///tmp/model",
    ],
)
def test_http_opt_in_does_not_disable_other_endpoint_checks(url):
    with pytest.raises(ValueError):
        validate_model_url(url, allow_insecure_http=True)


def test_http_opt_in_does_not_forward_keys_between_endpoints(settings):
    settings.allow_insecure_model_http = True
    repository = ModelSettingsRepository(settings)
    saved = repository.update(
        {
            "expected_revision": "0",
            "default": {"base_url": ENDPOINT, "model": "test", "api_key": "dummy-http-key"},
        }
    )
    with pytest.raises(ModelSettingsError, match="API Key"):
        repository.update(
            {
                "expected_revision": saved["revision"],
                "stages": {"coding": {"base_url": "http://other.example/v1"}},
            }
        )
