"""Offline security and lifecycle coverage for writable model configuration."""

import json
import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import httpx
import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import SecretStr
from typer.testing import CliRunner

from workbench import cli
from workbench.domain import Requirement
from workbench.llm import ModelGateway
from workbench.model_settings import (
    MAX_CONFIG_BYTES,
    ModelSettingsError,
    ModelSettingsRepository,
    RevisionConflict,
    register_model_settings_routes,
)
from workbench.runtime import Runtime
from workbench.settings import STAGES, ModelProfile, Settings, validate_model_url

DUMMY_KEY = "dummy-config-key-never-real"
NEXT_KEY = "dummy-replacement-key-never-real"


@pytest.fixture
def repository(settings):
    return ModelSettingsRepository(settings)


@pytest.fixture
def settings_client(settings):
    app = FastAPI()

    def auth(request: Request):
        if request.headers.get("authorization") != "Bearer dummy-local-token":
            raise HTTPException(401)

    register_model_settings_routes(app, settings, auth)
    with TestClient(app) as client:
        client.headers["authorization"] = "Bearer dummy-local-token"
        yield client


def configure(repository, **values):
    return repository.update(
        {
            "expected_revision": repository.public()["revision"],
            "default": {
                "base_url": "https://provider.example/v1",
                "model": "dummy-model",
                "api_key": DUMMY_KEY,
                **values,
            },
        }
    )


def test_first_run_configuration_has_only_missing_keys(repository, settings):
    result = repository.public()
    assert not result["ready"] and result["revision"] == "0"
    assert result["default"]["api_key"] == "missing"
    assert result["validation_scope"] == "format_only"
    assert set(result["stages"]) == set(STAGES)
    assert not settings.models_ready()
    assert not repository.path.exists()


def test_atomic_private_save_and_process_reload(repository, settings):
    result = configure(repository)
    assert result["ready"] and result["revision"] != "0"
    assert result["default"]["api_key"] == "configured"
    assert DUMMY_KEY not in json.dumps(result)
    assert all(row["key_source"] == "default" for row in result["stages"].values())
    if os.name == "posix":
        assert stat.S_IMODE(repository.path.stat().st_mode) == 0o600
    assert not list(repository.path.parent.glob(".model-settings-*"))
    # This file contains local credentials but every public representation is redacted.
    assert json.loads(repository.path.read_text())["default"]["api_key"] == DUMMY_KEY
    fresh = Settings(data_dir=settings.data_dir, _env_file=None)
    assert fresh.models_ready()
    assert fresh.model_for("requirements").api_key.get_secret_value() == DUMMY_KEY
    assert DUMMY_KEY not in json.dumps(ModelSettingsRepository(fresh).public())
    assert DUMMY_KEY not in repr(fresh)


def test_partial_stage_update_inheritance_and_secret_preservation(repository, settings):
    saved = configure(repository)
    result = repository.update(
        {
            "expected_revision": saved["revision"],
            "stages": {"coding": {"model": "dummy-coder"}},
        }
    )
    assert result["stages"]["coding"]["effective"]["model"] == "dummy-coder"
    assert settings.model_for("coding").api_key.get_secret_value() == DUMMY_KEY
    assert settings.model_for("planning").model == "dummy-model"
    assert settings.redact(DUMMY_KEY) == "[redacted]"


@pytest.mark.parametrize("patch_key", [{}, {"api_key": DUMMY_KEY}, {"api_key": ""}])
def test_default_endpoint_change_never_reuses_old_key(repository, settings, patch_key):
    saved = configure(repository)
    with pytest.raises(ModelSettingsError, match="API Key"):
        repository.update(
            {
                "expected_revision": saved["revision"],
                "default": {"base_url": "https://other.example/v1", **patch_key},
            }
        )
    assert settings.model_for("coding").base_url == "https://provider.example/v1"
    assert repository.public()["revision"] == saved["revision"]


def test_endpoint_rotation_uses_new_key_and_retains_old_redaction(repository, settings):
    saved = configure(
        repository, provider="openai", output_mode="json_object", max_output_tokens=2000
    )
    old = settings.model_for("coding")
    result = repository.update(
        {
            "expected_revision": saved["revision"],
            "default": {"base_url": "https://other.example/v1", "api_key": NEXT_KEY},
        }
    )
    latest = settings.model_for("coding")
    assert old.base_url == "https://provider.example/v1"
    assert old.api_key.get_secret_value() == DUMMY_KEY
    assert latest.base_url == "https://other.example/v1"
    assert latest.api_key.get_secret_value() == NEXT_KEY
    assert latest.provider == "auto" and latest.max_output_tokens is None
    assert DUMMY_KEY not in json.dumps(result) and NEXT_KEY not in json.dumps(result)
    assert settings.redact(DUMMY_KEY + " " + NEXT_KEY) == "[redacted] [redacted]"


def test_stage_endpoint_requires_separate_key_and_can_return_to_default(repository, settings):
    saved = configure(repository)
    change = {"base_url": "https://coder.example/v1", "model": "dummy-coder"}
    for missing_or_old_key in ({}, {"api_key": DUMMY_KEY}):
        with pytest.raises(ModelSettingsError):
            repository.update(
                {
                    "expected_revision": saved["revision"],
                    "stages": {"coding": {**change, **missing_or_old_key}},
                }
            )
    result = repository.update(
        {
            "expected_revision": saved["revision"],
            "stages": {"coding": {**change, "api_key": NEXT_KEY}},
        }
    )
    assert result["stages"]["coding"]["key_source"] == "override"
    assert settings.model_for("coding").api_key.get_secret_value() == NEXT_KEY
    result = repository.update(
        {
            "expected_revision": result["revision"],
            "stages": {"coding": {"base_url": "", "api_key": "", "model": ""}},
        }
    )
    assert result["stages"]["coding"]["key_source"] == "default"
    assert settings.model_for("coding").api_key.get_secret_value() == DUMMY_KEY


def test_default_rotation_does_not_forward_a_stage_key_to_new_host(repository):
    saved = configure(repository)
    saved = repository.update(
        {
            "expected_revision": saved["revision"],
            "stages": {"coding": {"api_key": "dummy-stage-key"}},
        }
    )
    with pytest.raises(ModelSettingsError):
        repository.update(
            {
                "expected_revision": saved["revision"],
                "default": {"base_url": "https://new.example/v1", "api_key": NEXT_KEY},
            }
        )
    result = repository.update(
        {
            "expected_revision": saved["revision"],
            "default": {"base_url": "https://new.example/v1", "api_key": NEXT_KEY},
            "stages": {"coding": {"api_key": ""}},
        }
    )
    assert result["ready"] and result["stages"]["coding"]["key_source"] == "default"


def test_explicit_key_clear_disables_execution_without_exposing_key(repository, settings):
    saved = configure(repository)
    result = repository.update({"expected_revision": saved["revision"], "default": {"api_key": ""}})
    assert not result["ready"] and not settings.models_ready()
    assert result["default"]["api_key"] == "missing"


def test_stale_revision_and_concurrent_saves_do_not_lose_updates(repository):
    saved = configure(repository)
    barrier = threading.Barrier(2)

    def save(name):
        barrier.wait()
        try:
            repository.update({"expected_revision": saved["revision"], "default": {"model": name}})
            return "saved"
        except RevisionConflict:
            return "stale"

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(save, ["model-a", "model-b"])) == ["saved", "stale"]
    assert repository.public()["default"]["model"] in {"model-a", "model-b"}


@pytest.mark.parametrize(
    "url",
    [
        "http://remote.example/v1",
        "https://user:secret@provider.example/v1",
        "https://@provider.example/v1",
        "https://provider.example/v1?",
        "https://provider.example/v1#",
        "https://provider.example/v1?key=secret",
        "https://provider.example/v1#secret",
        "https://provider.example/v1/chat/completions",
        "https://provider.example/v1/completions/more",
        "https://provider.example/v1/%63ompletions",
        "https://provider.example/v1/responses",
        "https://provider.example:bad/v1",
        "https://provider.example:65536/v1",
        "https://provider.example:0/v1",
        "https://provider.example\\evil/v1",
        "https://provider.example/\nsecret",
        "https://[broken/v1",
        "file:///tmp/provider",
        "//provider.example/v1",
        "http://127.0.0.1.evil.example/v1",
    ],
)
def test_model_api_roots_reject_credential_leaks_and_unsafe_paths(url):
    with pytest.raises(ValueError) as caught:
        validate_model_url(url)
    assert "secret" not in str(caught.value) and "provider.example" not in str(caught.value)


@pytest.mark.parametrize(
    "url",
    [
        "https://provider.example/v1/",
        "http://127.0.0.1:11434/v1",
        "http://localhost:9000",
        "http://[::1]:9000/v1",
    ],
)
def test_https_and_explicit_loopback_roots_work(url):
    assert validate_model_url(url) == url.rstrip("/")


def test_settings_endpoint_auth_origin_cache_and_secret_safe_errors(settings_client):
    assert (
        settings_client.get(
            "/settings/models", headers={"authorization": "Bearer wrong"}
        ).status_code
        == 401
    )
    initial = settings_client.get("/settings/models")
    assert initial.headers["cache-control"] == "no-store"
    body = {
        "expected_revision": "0",
        "default": {
            "base_url": "https://provider.example/v1",
            "model": "dummy",
            "api_key": DUMMY_KEY,
        },
    }
    for origin in [
        "https://evil.example",
        "null",
        "http://testserver:9000",
        "http://user@testserver",
        "http://testserver/",
    ]:
        response = settings_client.patch("/settings/models", json=body, headers={"origin": origin})
        assert response.status_code == 403
        assert DUMMY_KEY not in response.text
    assert (
        settings_client.patch(
            "/settings/models", json=body, headers={"Sec-Fetch-Site": "cross-site"}
        ).status_code
        == 403
    )
    response = settings_client.patch(
        "/settings/models", json=body, headers={"origin": "http://testserver"}
    )
    assert response.status_code == 200
    assert response.json()["ready"] and DUMMY_KEY not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert settings_client.patch("/settings/models", json=body).status_code == 409
    invalid = {
        "expected_revision": response.json()["revision"],
        "default": {"api_key": {"nested": NEXT_KEY}},
    }
    response = settings_client.patch("/settings/models", json=invalid)
    assert response.status_code == 422 and NEXT_KEY not in response.text
    response = settings_client.patch("/settings/models", json={NEXT_KEY: NEXT_KEY})
    assert response.status_code == 422 and NEXT_KEY not in response.text


def test_body_limits_and_content_type_are_checked(settings_client):
    response = settings_client.patch(
        "/settings/models", content="{" + DUMMY_KEY, headers={"content-type": "application/json"}
    )
    assert response.status_code == 422 and DUMMY_KEY not in response.text
    assert (
        settings_client.patch(
            "/settings/models", content="{}", headers={"content-type": "text/plain"}
        ).status_code
        == 415
    )
    assert (
        settings_client.patch(
            "/settings/models",
            content="x" * (MAX_CONFIG_BYTES + 1),
            headers={"content-type": "application/json"},
        ).status_code
        == 413
    )


@pytest.mark.parametrize(
    "value", ["configured", "missing", "**********", "dummy\nkey", "dummy key", 1, None]
)
def test_invalid_or_masked_keys_are_not_saved(repository, value):
    configure(repository)
    with pytest.raises(ModelSettingsError):
        repository.update(
            {"expected_revision": repository.public()["revision"], "default": {"api_key": value}}
        )


def test_corrupt_file_is_not_used_or_echoed(repository, settings, settings_client):
    configure(repository)
    repository.path.write_text('{"api_key":"' + DUMMY_KEY + '"')
    assert not settings.models_ready()
    response = settings_client.get("/settings/models")
    assert response.status_code == 503 and DUMMY_KEY not in response.text
    with pytest.raises(ModelSettingsError):
        settings.model_for("coding")


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions")
def test_world_readable_configuration_fails_closed(repository, settings):
    configure(repository)
    repository.path.chmod(0o644)
    assert not settings.models_ready()
    with pytest.raises(ModelSettingsError):
        repository.public()


def test_symlink_configuration_fails_closed(repository, settings, tmp_path):
    settings.data_dir.mkdir()
    target = tmp_path / "outside-config.json"
    target.write_text(DUMMY_KEY)
    try:
        repository.path.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(ModelSettingsError):
        repository.public()
    with pytest.raises(ModelSettingsError):
        configure(repository)
    assert target.read_text() == DUMMY_KEY


def test_atomic_replace_failure_preserves_previous_file_and_removes_temporary(
    repository, monkeypatch
):
    saved = configure(repository)
    before = repository.path.read_bytes()

    def failed(*args):
        raise OSError("dummy-sensitive-error " + NEXT_KEY)

    monkeypatch.setattr("workbench.model_settings.os.replace", failed)
    with pytest.raises(ModelSettingsError) as caught:
        repository.update(
            {"expected_revision": saved["revision"], "default": {"api_key": NEXT_KEY}}
        )
    assert NEXT_KEY not in str(caught.value)
    assert repository.path.read_bytes() == before
    assert not list(repository.path.parent.glob(".model-settings-*"))


def test_inflight_call_and_retry_keep_profile_snapshot_and_next_call_reloads(store):
    repository = ModelSettingsRepository(store.settings)
    configure(repository)
    seen = []

    def transport(request):
        seen.append(
            (
                request.url.host,
                request.headers["authorization"],
                json.loads(request.content)["model"],
            )
        )
        if len(seen) == 1:
            saved = repository.public()
            repository.update(
                {
                    "expected_revision": saved["revision"],
                    "default": {
                        "base_url": "https://next.example/v1",
                        "api_key": NEXT_KEY,
                        "model": "next-model",
                    },
                }
            )
            return httpx.Response(500, text=DUMMY_KEY)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": requirement().model_dump_json()}}
                ]
            },
        )

    gateway = ModelGateway(store.settings, store, httpx.MockTransport(transport))
    run_id = new_run(store)
    gateway.complete(run_id, "requirement:1", "requirements", {}, Requirement)
    gateway.complete(run_id, "requirement:2", "requirements", {}, Requirement)
    assert seen == [
        ("provider.example", "Bearer " + DUMMY_KEY, "dummy-model"),
        ("provider.example", "Bearer " + DUMMY_KEY, "dummy-model"),
        ("next.example", "Bearer " + NEXT_KEY, "next-model"),
    ]
    assert DUMMY_KEY not in str(store.events(run_id, 0))
    assert NEXT_KEY not in str(store.events(run_id, 0))


def test_start_serves_shell_when_model_is_missing(settings, monkeypatch):
    fake_app = object()
    server = Mock()
    monkeypatch.setattr(cli, "Settings", lambda: settings)
    monkeypatch.setattr("workbench.api.create_app", lambda *args, **kwargs: fake_app)
    monkeypatch.setattr("uvicorn.run", server)
    result = CliRunner().invoke(cli.app, ["start", "--no-worker"])
    assert result.exit_code == 0, result.output
    assert "模型设置" in result.output
    assert server.call_args.args == (fake_app,)


def test_real_worker_only_claims_rejections_without_valid_configuration(settings, monkeypatch):
    gateway = Mock()
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *args, **kwargs: gateway)
    store = Mock()
    store.claim.return_value = None
    runtime = Runtime(settings, store)
    assert runtime.tick() is False
    store.claim.assert_called_once_with(only_rejections=True, include_model_free=True)
    store.claim.reset_mock()
    configure(ModelSettingsRepository(settings))
    assert runtime.tick() is False
    store.claim.assert_called_once_with()


def test_model_profile_is_immutable():
    profile = ModelProfile(
        stage="coding",
        base_url="https://provider.example/v1",
        model="dummy",
        api_key=SecretStr(DUMMY_KEY),
    )
    with pytest.raises(ValueError):
        profile.base_url = "https://unexpected.example/v1"


def test_rejection_finishes_without_models_but_other_queued_work_waits(store, plan):
    run_id = new_run(store)
    with Runtime(store.settings, store, FixtureGateway(plan)) as runtime:
        runtime.tick()
        assert store.get_run(run_id)["pending"]
        decision(store, run_id, action="reject")
        another = new_run(store)
        runtime.requires_model_configuration = True
        assert not store.settings.models_ready()
        assert runtime.tick()
        assert store.get_run(run_id)["status"] == "REJECTED"
        assert runtime.tick() is False
        assert store.get_run(another)["status"] == "QUEUED"


def test_cannot_repurpose_another_stages_old_key_at_new_endpoint(repository):
    saved = configure(repository)
    saved = repository.update(
        {
            "expected_revision": saved["revision"],
            "stages": {"coding": {"base_url": "https://coder.example/v1", "api_key": NEXT_KEY}},
        }
    )
    with pytest.raises(ModelSettingsError):
        repository.update(
            {
                "expected_revision": saved["revision"],
                "stages": {
                    "coding": {"base_url": "https://unrelated.example/v1", "api_key": DUMMY_KEY}
                },
            }
        )


def test_doctor_reads_the_saved_configuration_not_stale_environment(settings, monkeypatch):
    configure(ModelSettingsRepository(settings))
    monkeypatch.setattr(cli, "Settings", lambda: settings)
    result = CliRunner().invoke(cli.app, ["doctor"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.output)
    assert report["model"] == "dummy-model"
    assert report["api_key"] == "configured"
    assert report["validation_scope"] == "format_only"
    assert DUMMY_KEY not in result.output


def test_trailing_slash_edit_does_not_reset_provider_or_require_new_key(repository):
    saved = configure(
        repository, provider="openai", output_mode="json_object", max_output_tokens=2000
    )
    result = repository.update(
        {
            "expected_revision": saved["revision"],
            "default": {"base_url": "https://provider.example/v1/"},
        }
    )
    assert result["ready"]
    assert result["default"]["provider"] == "openai"
    assert result["default"]["max_output_tokens"] == 2000
