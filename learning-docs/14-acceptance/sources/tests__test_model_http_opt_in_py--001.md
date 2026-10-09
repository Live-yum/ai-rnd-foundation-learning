# tests/test_model_http_opt_in.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_settings`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_http_requires_explicit_operator_configuration`（L14–L28）：接收`settings`。 控制顺序：L18断言`not settings.models_ready()`；L22断言`snapshot.base_url == ENDPOINT`；L23断言`snapshot.validate_endpoint() is snapshot`；L24断言`"dummy-http-key" not in json.dumps(snapshot.public())`；L26断言`not settings.models_ready()`；L28断言`snapshot.validate_endpoint() is snapshot`。 调用`SecretStr`、`settings.models_ready`、`settings.require_model`、`settings.model_for`、`snapshot.validate_endpoint`、`json.dumps`、`snapshot.public`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_opt_in_applies_to_saved_profiles_but_is_never_persisted`（L31–L57）：接收`settings`。 控制顺序：L40断言`result["ready"]`；L41断言`"allow_insecure" not in repository.path.read_text(encoding="utf-8")`；L44断言`not fresh.models_ready()`；L46断言`fresh.models_ready()`。 调用`ModelSettingsRepository`、`repository.update`、`repository.path.read_text`、`Settings`、`fresh.models_ready`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_opt_in_does_not_disable_other_endpoint_checks`（L71–L73）：接收`url`。 调用`pytest.raises`、`validate_model_url`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_opt_in_does_not_forward_keys_between_endpoints`（L76–L91）：接收`settings`。 调用`ModelSettingsRepository`、`repository.update`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_http_opt_in.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L91。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3300`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_http_opt_in.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1761735533ffef8b34beab787beb617ef0904a8b8440abe669728ca49a30efb7"} -->
````python
# tests/test_model_http_opt_in.py
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
````
