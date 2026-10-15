# tests/test_model_env_bootstrap.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.model_settings`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `env_settings`（L18–L42）：接收`tmp_path`、`monkeypatch`。 控制顺序：L21遍历`Settings.model_fields.values()`；L23按`hasattr(alias, "choices")`分支；L25遍历`os.environ`；L26按`name.lower() in names`分支。 调用`set`、`Settings.model_fields.values`、`hasattr`、`names.update`、`str(choice).lower`、`str`、`name.lower`、`monkeypatch.delenv`、`monkeypatch.setitem`等。 返回路径：L42的`load`。
- `env_settings.load`（L34–L40）：接收`encoding`、`model_name`、`extra`。 调用`env.write_text`、`Settings`。 返回路径：L40的`Settings(data_dir=tmp_path / "data", install_products=False)`。
- `test_env_bootstrap_is_ready_without_saving_or_network`（L47–L76）：接收`env_settings`、`monkeypatch`、`encoding`、`model_name`。 控制顺序：L56断言`settings.models_ready()`；L60断言`client.get("/settings/models").status_code == 401`；L63断言`response.status_code == 200`；L65断言`view["ready"] and view["revision"] == "0"`；L66断言`view["source"] == "environment"`；L67断言`view["default"]["api_key"] == "configured"`；L68断言`view["validation_scope"] == "format_only"`；L69断言`KEY not in response.text`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`env_settings`、`settings.require_model`、`settings.models_ready`、`ModelSettingsRepository`、`create_app`、`TestClient`、`client.get`、`response.json`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_env_bootstrap_is_ready_without_saving_or_network.unexpected_network`（L50–L51）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_saved_configuration_still_takes_precedence`（L79–L90）：接收`env_settings`。 控制顺序：L85断言`saved["source"] == public["source"] == "saved"`；L86断言`public["ready"]`；L87断言`public["revision"] == saved["revision"]`；L88断言`public["default"]["model"] == "saved-model"`；L89断言`KEY not in json.dumps(public)`；L90断言`"source" not in json.loads(repository.path.read_text())`。 调用`env_settings`、`ModelSettingsRepository`、`repository.update`、`ModelSettingsRepository(fresh).public`、`json.dumps`、`json.loads`、`repository.path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_env_stage_endpoint_cannot_inherit_default_secret`（L93–L99）：接收`env_settings`。 控制顺序：L95断言`not settings.models_ready()`；L97断言`not public["ready"]`；L98断言`public["stages"]["coding"]["effective"] is None`；L99断言`KEY not in json.dumps(public)`。 调用`env_settings`、`settings.models_ready`、`ModelSettingsRepository(settings).public`、`ModelSettingsRepository`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonempty_model_alias_after_empty_mode_in_dotenv`（L103–L108）：接收`env_settings`、`prefix`。 控制顺序：L107断言`getattr(settings, name) == "alias-model"`；L108断言`settings.models_ready()`。 调用`env_settings`、`prefix.lower`、`getattr`、`settings.models_ready`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonempty_model_alias_in_process_env`（L111–L116）：接收`env_settings`、`monkeypatch`。 控制顺序：L115断言`settings.model == "process-model"`；L116断言`settings.models_ready()`。 调用`monkeypatch.setenv`、`env_settings`、`settings.models_ready`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_empty_process_values_do_not_fall_back_to_dotenv`（L119–L125）：接收`env_settings`、`monkeypatch`。 控制顺序：L123断言`settings.api_key.get_secret_value() == ""`；L124断言`settings.model == ""`；L125断言`not settings.models_ready()`。 调用`monkeypatch.setenv`、`env_settings`、`settings.api_key.get_secret_value`、`settings.models_ready`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonempty_mode_wins_over_model_alias`（L128–L133）：接收`env_settings`、`monkeypatch`。 控制顺序：L130断言`settings.model == "synthetic-model"`；L133断言`env_settings().model == "process-mode"`。 调用`env_settings`、`monkeypatch.setenv`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_settings_api_reports_saved_source_on_save_and_reload`（L136–L153）：接收`env_settings`。 控制顺序：L146断言`response.status_code == 200`；L148断言`saved["source"] == "saved"`；L149断言`saved["revision"] != before["revision"]`；L150断言`KEY not in response.text`；L152断言`current["source"] == saved["source"]`；L153断言`current["revision"] == saved["revision"]`。 调用`env_settings`、`create_app`、`TestClient`、`client.get("/settings/models").json`、`client.get`、`client.patch`、`response.json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_env_bootstrap.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L153。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6153`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_env_bootstrap.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "30686d0cb6529692e277d6b6740a125e60f9ef03b5916b0d4c0bf38276d791a0"} -->
````python
# tests/test_model_env_bootstrap.py
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
````
