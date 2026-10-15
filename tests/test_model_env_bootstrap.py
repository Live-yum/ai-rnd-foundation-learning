"""Offline coverage from repository .env parsing to the authenticated UI bootstrap."""

import json
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from workbench.api import create_app
from workbench.model_settings import ModelSettingsRepository
from workbench.settings import STAGES, Settings

KEY = "synthetic-env-bootstrap-key"


@pytest.fixture
def env_settings(tmp_path, monkeypatch):
    # Never depend on a developer's shell credentials or their real .env file.
    names = set(Settings.model_fields)
    for field in Settings.model_fields.values():
        alias = field.validation_alias
        if hasattr(alias, "choices"):
            names.update(str(choice).lower() for choice in alias.choices)
    for name in os.environ:
        if name.lower() in names:
            monkeypatch.delenv(name)
    env = tmp_path / ".env"
    monkeypatch.setitem(Settings.model_config, "env_file", env)
    elsewhere = tmp_path / "another-directory"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    def load(*, encoding="utf-8", model_name="MODE", extra=""):
        env.write_text(
            f"BASE_URL=https://model.example.invalid/v1\nAPI_KEY={KEY}\n"
            f"{model_name}=synthetic-model\n{extra}",
            encoding=encoding,
        )
        return Settings(data_dir=tmp_path / "data", install_products=False)

    return load


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("model_name", ["MODE", "MODEL"])
def test_env_bootstrap_is_ready_without_saving_or_network(
    env_settings, monkeypatch, encoding, model_name
):
    def unexpected_network(*args, **kwargs):
        pytest.fail("Reading model readiness must not contact a provider")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", unexpected_network)
    settings = env_settings(encoding=encoding, model_name=model_name)
    settings.require_model()
    assert settings.models_ready()
    repository = ModelSettingsRepository(settings)
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        assert client.get("/settings/models").status_code == 401
        client.headers["Authorization"] = "Bearer " + app.state.token
        response = client.get("/settings/models")
        assert response.status_code == 200
        view = response.json()
        assert view["ready"] and view["revision"] == "0"
        assert view["source"] == "environment"
        assert view["default"]["api_key"] == "configured"
        assert view["validation_scope"] == "format_only"
        assert KEY not in response.text
        models = client.get("/models")
        assert models.status_code == 200
        assert all(row["valid"] for row in models.json() if row["enabled"])
        assert KEY not in models.text
        for stage in STAGES:
            assert view["stages"][stage]["key_source"] == "default"
    assert not repository.path.exists()


def test_saved_configuration_still_takes_precedence(env_settings):
    settings = env_settings()
    repository = ModelSettingsRepository(settings)
    saved = repository.update({"expected_revision": "0", "default": {"model": "saved-model"}})
    fresh = env_settings()
    public = ModelSettingsRepository(fresh).public()
    assert saved["source"] == public["source"] == "saved"
    assert public["ready"]
    assert public["revision"] == saved["revision"]
    assert public["default"]["model"] == "saved-model"
    assert KEY not in json.dumps(public)
    assert "source" not in json.loads(repository.path.read_text())


def test_env_stage_endpoint_cannot_inherit_default_secret(env_settings):
    settings = env_settings(extra="CODING_BASE_URL=https://different.example.invalid/v1\n")
    assert not settings.models_ready()
    public = ModelSettingsRepository(settings).public()
    assert not public["ready"]
    assert public["stages"]["coding"]["effective"] is None
    assert KEY not in json.dumps(public)


@pytest.mark.parametrize("prefix", ["", "REQUIREMENTS_", "PLANNING_", "CODING_", "REVIEW_"])
def test_nonempty_model_alias_after_empty_mode_in_dotenv(env_settings, prefix):
    extra = f"{prefix}MODE=\n{prefix}MODEL=alias-model\n"
    settings = env_settings(extra=extra)
    name = prefix.lower() + "model"
    assert getattr(settings, name) == "alias-model"
    assert settings.models_ready()


def test_nonempty_model_alias_in_process_env(env_settings, monkeypatch):
    monkeypatch.setenv("MODE", "")
    monkeypatch.setenv("MODEL", "process-model")
    settings = env_settings()
    assert settings.model == "process-model"
    assert settings.models_ready()


def test_explicit_empty_process_values_do_not_fall_back_to_dotenv(env_settings, monkeypatch):
    monkeypatch.setenv("API_KEY", "")
    monkeypatch.setenv("MODE", "")
    settings = env_settings()
    assert settings.api_key.get_secret_value() == ""
    assert settings.model == ""
    assert not settings.models_ready()


def test_nonempty_mode_wins_over_model_alias(env_settings, monkeypatch):
    settings = env_settings(extra="MODEL=unused-alias\n")
    assert settings.model == "synthetic-model"
    monkeypatch.setenv("MODE", "process-mode")
    monkeypatch.setenv("MODEL", "unused-process-alias")
    assert env_settings().model == "process-mode"


def test_settings_api_reports_saved_source_on_save_and_reload(env_settings):
    settings = env_settings()
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        client.headers["Authorization"] = "Bearer " + app.state.token
        before = client.get("/settings/models").json()
        response = client.patch(
            "/settings/models",
            json={"expected_revision": before["revision"], "default": {"model": "saved-model"}},
        )
        assert response.status_code == 200
        saved = response.json()
        assert saved["source"] == "saved"
        assert saved["revision"] != before["revision"]
        assert KEY not in response.text
        current = client.get("/settings/models").json()
        assert current["source"] == saved["source"]
        assert current["revision"] == saved["revision"]
