# tests/test_model_settings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.domain`、`workbench.llm`、`workbench.model_settings`、`workbench.runtime`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `repository`（L36–L37）：接收`settings`。 调用`ModelSettingsRepository`。 返回路径：L37的`ModelSettingsRepository(settings)`。
- `settings_client`（L41–L51）：接收`settings`。 调用`FastAPI`、`register_model_settings_routes`、`TestClient`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `settings_client.auth`（L44–L46）：接收`request`。用本机Dex真实签发的JWT访问本机API创建密钥，不伪造token，也不向云身份服务注册账号。 控制顺序：L45按`request.headers.get("authorization") != "Bearer dummy-local-token"`分支；L46抛异常，停止当前正常路径。 调用`request.headers.get`、`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `configure`（L54–L65）：接收`repository`、`**values`。 调用`repository.update`、`repository.public`。 返回路径：L55的`repository.update( { "expected_revision": repository.public()["revision"], "default": { "b…`。
- `test_first_run_configuration_has_only_missing_keys`（L68–L75）：接收`repository`、`settings`。 控制顺序：L70断言`not result["ready"] and result["revision"] == "0"`；L71断言`result["default"]["api_key"] == "missing"`；L72断言`result["validation_scope"] == "format_only"`；L73断言`set(result["stages"]) == set(STAGES)`；L74断言`not settings.models_ready()`；L75断言`not repository.path.exists()`。 调用`repository.public`、`set`、`settings.models_ready`、`repository.path.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_atomic_private_save_and_process_reload`（L78–L93）：接收`repository`、`settings`。 控制顺序：L80断言`result["ready"] and result["revision"] != "0"`；L81断言`result["default"]["api_key"] == "configured"`；L82断言`DUMMY_KEY not in json.dumps(result)`；L83断言`all(row["key_source"] == "default" for row in result["stages"].values())`；L84按`os.name == "posix"`分支；L85断言`stat.S_IMODE(repository.path.stat().st_mode) == 0o600`；L86断言`not list(repository.path.parent.glob(".model-settings-*"))`；L88断言`json.loads(repository.path.read_text())["default"]["api_key"] == DUMMY_KEY`。后续分支沿下方源码相同行号继续阅读。 调用`configure`、`json.dumps`、`all`、`result["stages"].values`、`stat.S_IMODE`、`repository.path.stat`、`list`、`repository.path.parent.glob`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_stage_update_inheritance_and_secret_preservation`（L96–L107）：接收`repository`、`settings`。 控制顺序：L104断言`result["stages"]["coding"]["effective"]["model"] == "dummy-coder"`；L105断言`settings.model_for("coding").api_key.get_secret_value() == DUMMY_KEY`；L106断言`settings.model_for("planning").model == "dummy-model"`；L107断言`settings.redact(DUMMY_KEY) == "[redacted]"`。 调用`configure`、`repository.update`、`settings.model_for("coding").api_key.get_secret_value`、`settings.model_for`、`settings.redact`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_default_endpoint_change_never_reuses_old_key`（L111–L121）：接收`repository`、`settings`、`patch_key`。 控制顺序：L120断言`settings.model_for("coding").base_url == "https://provider.example/v1"`；L121断言`repository.public()["revision"] == saved["revision"]`。 调用`configure`、`pytest.raises`、`repository.update`、`settings.model_for`、`repository.public`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_endpoint_rotation_uses_new_key_and_retains_old_redaction`（L124–L142）：接收`repository`、`settings`。 控制顺序：L136断言`old.base_url == "https://provider.example/v1"`；L137断言`old.api_key.get_secret_value() == DUMMY_KEY`；L138断言`latest.base_url == "https://other.example/v1"`；L139断言`latest.api_key.get_secret_value() == NEXT_KEY`；L140断言`latest.provider == "auto" and latest.max_output_tokens is None`；L141断言`DUMMY_KEY not in json.dumps(result) and NEXT_KEY not in json.dumps(result)`；L142断言`settings.redact(DUMMY_KEY + " " + NEXT_KEY) == "[redacted] [redacted]"`。 调用`configure`、`settings.model_for`、`repository.update`、`old.api_key.get_secret_value`、`latest.api_key.get_secret_value`、`json.dumps`、`settings.redact`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stage_endpoint_requires_separate_key_and_can_return_to_default`（L145–L171）：接收`repository`、`settings`。 控制顺序：L148遍历`({}, {"api_key": DUMMY_KEY})`；L162断言`result["stages"]["coding"]["key_source"] == "override"`；L163断言`settings.model_for("coding").api_key.get_secret_value() == NEXT_KEY`；L170断言`result["stages"]["coding"]["key_source"] == "default"`；L171断言`settings.model_for("coding").api_key.get_secret_value() == DUMMY_KEY`。 调用`configure`、`pytest.raises`、`repository.update`、`settings.model_for("coding").api_key.get_secret_value`、`settings.model_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_default_rotation_does_not_forward_a_stage_key_to_new_host`（L174–L196）：接收`repository`。 控制顺序：L196断言`result["ready"] and result["stages"]["coding"]["key_source"] == "default"`。 调用`configure`、`repository.update`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_key_clear_disables_execution_without_exposing_key`（L199–L203）：接收`repository`、`settings`。 控制顺序：L202断言`not result["ready"] and not settings.models_ready()`；L203断言`result["default"]["api_key"] == "missing"`。 调用`configure`、`repository.update`、`settings.models_ready`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_revision_and_concurrent_saves_do_not_lose_updates`（L206–L220）：接收`repository`。 控制顺序：L219断言`sorted(executor.map(save, ["model-a", "model-b"])) == ["saved", "stale"]`；L220断言`repository.public()["default"]["model"] in {"model-a", "model-b"}`。 调用`configure`、`threading.Barrier`、`ThreadPoolExecutor`、`sorted`、`executor.map`、`repository.public`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_revision_and_concurrent_saves_do_not_lose_updates.save`（L210–L216）：接收`name`。 调用`barrier.wait`、`repository.update`。 返回路径：L214的`"saved"`；L216的`"stale"`。
- `test_model_api_roots_reject_credential_leaks_and_unsafe_paths`（L248–L251）：接收`url`。 控制顺序：L251断言`"secret" not in str(caught.value) and "provider.example" not in str(caught.value)`。 调用`pytest.raises`、`validate_model_url`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_https_and_explicit_loopback_roots_work`（L263–L264）：接收`url`。 控制顺序：L264断言`validate_model_url(url) == url.rstrip("/")`。 调用`validate_model_url`、`url.rstrip`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_settings_endpoint_auth_origin_cache_and_secret_safe_errors`（L267–L314）：接收`settings_client`。 控制顺序：L268断言`settings_client.get( "/settings/models", headers={"authorization": "Bearer wrong"} ).…`；L275断言`initial.headers["cache-control"] == "no-store"`；L284遍历`[ "https://evil.example", "null", "http://testserver:9000", "http…`；L292断言`response.status_code == 403`；L293断言`DUMMY_KEY not in response.text`；L294断言`settings_client.patch( "/settings/models", json=body, headers={"Sec-Fetch-Site": "cro…`；L303断言`response.status_code == 200`；L304断言`response.json()["ready"] and DUMMY_KEY not in response.text`。后续分支沿下方源码相同行号继续阅读。 调用`settings_client.get`、`settings_client.patch`、`response.json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_body_limits_and_content_type_are_checked`（L317–L335）：接收`settings_client`。 控制顺序：L321断言`response.status_code == 422 and DUMMY_KEY not in response.text`；L322断言`settings_client.patch( "/settings/models", content="{}", headers={"content-type": "te…`；L328断言`settings_client.patch( "/settings/models", content="x" * (MAX_CONFIG_BYTES + 1), head…`。 调用`settings_client.patch`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_or_masked_keys_are_not_saved`（L341–L346）：接收`repository`、`value`。 调用`configure`、`pytest.raises`、`repository.update`、`repository.public`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupt_file_is_not_used_or_echoed`（L349–L356）：接收`repository`、`settings`、`settings_client`。 控制顺序：L352断言`not settings.models_ready()`；L354断言`response.status_code == 503 and DUMMY_KEY not in response.text`。 调用`configure`、`repository.path.write_text`、`settings.models_ready`、`settings_client.get`、`pytest.raises`、`settings.model_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_world_readable_configuration_fails_closed`（L360–L365）：接收`repository`、`settings`。 控制顺序：L363断言`not settings.models_ready()`。 调用`configure`、`repository.path.chmod`、`settings.models_ready`、`pytest.raises`、`repository.public`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlink_configuration_fails_closed`（L368–L380）：接收`repository`、`settings`、`tmp_path`。 控制顺序：L380断言`target.read_text() == DUMMY_KEY`。 调用`settings.data_dir.mkdir`、`target.write_text`、`repository.path.symlink_to`、`pytest.skip`、`pytest.raises`、`repository.public`、`configure`、`target.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_atomic_replace_failure_preserves_previous_file_and_removes_temporary`（L383–L399）：接收`repository`、`monkeypatch`。 控制顺序：L397断言`NEXT_KEY not in str(caught.value)`；L398断言`repository.path.read_bytes() == before`；L399断言`not list(repository.path.parent.glob(".model-settings-*"))`。 调用`configure`、`repository.path.read_bytes`、`monkeypatch.setattr`、`pytest.raises`、`repository.update`、`str`、`list`、`repository.path.parent.glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_atomic_replace_failure_preserves_previous_file_and_removes_temporary.failed`（L389–L390）：接收`*args`。 控制顺序：L390抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inflight_call_and_retry_keep_profile_snapshot_and_next_call_reloads`（L402–L447）：接收`store`。 控制顺序：L441断言`seen == [ ("provider.example", "Bearer " + DUMMY_KEY, "dummy-model"), ("provider.exam…`；L446断言`DUMMY_KEY not in str(store.events(run_id, 0))`；L447断言`NEXT_KEY not in str(store.events(run_id, 0))`。 调用`ModelSettingsRepository`、`configure`、`ModelGateway`、`httpx.MockTransport`、`new_run`、`gateway.complete`、`str`、`store.events`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inflight_call_and_retry_keep_profile_snapshot_and_next_call_reloads.transport`（L407–L435）：接收`request`。 控制顺序：L415按`len(seen) == 1`分支。 调用`seen.append`、`json.loads`、`len`、`repository.public`、`repository.update`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L427的`httpx.Response(500, text=DUMMY_KEY)`；L428的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_start_serves_shell_when_model_is_missing`（L450–L459）：接收`settings`、`monkeypatch`。 控制顺序：L457断言`result.exit_code == 0`；L458断言`"模型设置" in result.output`；L459断言`server.call_args.args == (fake_app,)`。 调用`object`、`Mock`、`monkeypatch.setattr`、`CliRunner().invoke`、`CliRunner`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_only_claims_rejections_without_valid_configuration`（L462–L473）：接收`settings`、`monkeypatch`。 控制顺序：L468断言`runtime.tick() is False`；L472断言`runtime.tick() is False`。 调用`Mock`、`monkeypatch.setattr`、`Runtime`、`runtime.tick`、`store.claim.assert_called_once_with`、`store.claim.reset_mock`、`configure`、`ModelSettingsRepository`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_profile_is_immutable`（L476–L484）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`ModelProfile`、`SecretStr`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejection_finishes_without_models_but_other_queued_work_waits`（L487–L499）：接收`store`、`plan`。 控制顺序：L491断言`store.get_run(run_id)["pending"]`；L495断言`not store.settings.models_ready()`；L496断言`runtime.tick()`；L497断言`store.get_run(run_id)["status"] == "REJECTED"`；L498断言`runtime.tick() is False`；L499断言`store.get_run(another)["status"] == "QUEUED"`。 调用`new_run`、`Runtime`、`FixtureGateway`、`runtime.tick`、`store.get_run`、`decision`、`store.settings.models_ready`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cannot_repurpose_another_stages_old_key_at_new_endpoint`（L502–L518）：接收`repository`。 调用`configure`、`repository.update`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_doctor_reads_the_saved_configuration_not_stale_environment`（L521–L530）：接收`settings`、`monkeypatch`。 控制顺序：L525断言`result.exit_code == 0`；L527断言`report["model"] == "dummy-model"`；L528断言`report["api_key"] == "configured"`；L529断言`report["validation_scope"] == "format_only"`；L530断言`DUMMY_KEY not in result.output`。 调用`configure`、`ModelSettingsRepository`、`monkeypatch.setattr`、`CliRunner().invoke`、`CliRunner`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trailing_slash_edit_does_not_reset_provider_or_require_new_key`（L533–L545）：接收`repository`。 控制顺序：L543断言`result["ready"]`；L544断言`result["default"]["provider"] == "openai"`；L545断言`result["default"]["max_output_tokens"] == 2000`。 调用`configure`、`repository.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_settings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L545。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20203`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_settings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0e113414e84798958a0638c6d6336ebc7d7f53ba9e84d3f5dd60a55015a36e5f"} -->
````python
# tests/test_model_settings.py
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
````
