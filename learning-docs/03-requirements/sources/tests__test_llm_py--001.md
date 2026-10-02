# tests/test_llm.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `gateway`（L11–L17）：接收`store`、`handler`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L17的`ModelGateway(store.settings, store, httpx.MockTransport(handler))`。
- `test_success_cache_and_usage`（L20–L40）：接收`store`。 控制顺序：L38断言`model.complete(run, "test", "instruction", {}, Requirement) == a`；L39断言`len(calls) == 1`；L40断言`store.get_run(run)["model_calls"] == 1`。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_success_cache_and_usage.handler`（L23–L33）：接收`request`。 调用`calls.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L25的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_failures_not_fake_success`（L44–L48）：接收`store`、`status`。 控制顺序：L48断言`"do-not-disclose" not in str(error.value)`。 调用`gateway`、`httpx.Response`、`pytest.raises`、`model.complete`、`new_run`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_json_bounded`（L51–L61）：接收`store`。 控制顺序：L61断言`store.get_run(run)["model_calls"] == 2`。 调用`gateway`、`httpx.Response`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials`（L64–L99）：接收`store`。 控制顺序：L92断言`result.business is not None`；L93断言`len(requests) == 2`；L95断言`retry[-2]["role"] == "assistant"`；L96断言`json.loads(retry[-2]["content"]) == invalid`；L97断言`"日期范围只支持 date 类型" in retry[-1]["content"]`；L98断言`"entities" in retry[-1]["content"] and "fields" in retry[-1]["content"]`；L99断言`"do-not-disclose" not in json.dumps(retry)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.dumps`、`next`、`gateway`、`model.complete`、`new_run`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials.handler`（L74–L88）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`json.dumps`、`len`。 返回路径：L76的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": js…`。

</details>

**创建路径：** `tests/test_llm.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L99。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3405`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_llm.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e2c0a2f6e4a1db2a27d71c66cc648e3f321d29c96341fb122e29d58c33ca9c17"} -->
````python
# tests/test_llm.py
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
````
