# tests/test_guided_models.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_one_model_remains_the_default`（L13–L27）：接收`tmp_path`。 控制顺序：L21断言`not settings.review_enabled`；L22遍历`["requirements", "planning", "coding"]`；L24断言`model.model == "one-model"`；L25断言`model.base_url == "https://provider.example/v1"`；L26断言`model.api_key.get_secret_value() == "secret-default"`；L27断言`"secret-default" not in str(model.public())`。 调用`env.write_text`、`Settings`、`settings.require_model`、`settings.model_for`、`model.api_key.get_secret_value`、`str`、`model.public`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mixed_per_stage_models_and_provider_keys`（L30–L52）：接收`tmp_path`。 控制顺序：L46断言`settings.model_for("requirements").model == "cheap-analysis"`；L47断言`settings.model_for("coding").base_url == "https://base.example/v1"`；L48断言`settings.model_for("planning").api_key.get_secret_value() == "planning-secret"`；L49断言`settings.model_for("review").model == "reviewer"`；L50断言`settings.review_enabled`；L51断言`"default-secret" not in settings.redact("default-secret planning-secret review-secret…`；L52断言`"planning-secret" not in settings.redact("default-secret planning-secret review-secre…`。 调用`env.write_text`、`Settings`、`settings.require_model`、`settings.model_for`、`settings.model_for("planning").api_key.get_secret_value`、`settings.redact`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_endpoint_never_inherits_another_provider_key`（L55–L64）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Settings`、`pytest.raises`、`s.model_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gateway_sends_each_stage_to_its_selected_model`（L67–L107）：接收`store`。 控制顺序：L98断言`seen == [ ("base.example", "Bearer base-key", "shared-model"), ("planner.example", "B…`；L102断言`{x["stage"] for x in store.model_records(rid)} == {"requirements", "planning"}`；L105断言`len(seen) == 3`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`、`new_run`、`gateway.complete`、`store.model_records`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gateway_sends_each_stage_to_its_selected_model.handler`（L77–L92）：接收`request`。 调用`seen.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L85的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_default_model_budget_does_not_kill_long_conversations`（L110–L115）：接收`store`。 控制顺序：L112断言`store.settings.max_rounds == 0 and store.settings.max_model_calls == 0`；L113遍历`range(80)`；L115断言`store.get_run(rid)["model_calls"] == 80`。 调用`new_run`、`range`、`store.reserve_model_call`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_guided_models.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L115。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4121`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_guided_models.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "373b15cfd95dc9de812d2f2cf82706b51bfdf4ceb23e33c46c173363bd54a3ec"} -->
````python
# tests/test_guided_models.py
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
````
