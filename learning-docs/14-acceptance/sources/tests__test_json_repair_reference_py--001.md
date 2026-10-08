# tests/test_json_repair_reference.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.model_diagnostics`、`workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `plan_object`（L16–L31）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L17的`{ "title": "Strict format repair", "data_scope": "per_user", "entities": [ { "name": "reco…`。
- `response`（L34–L74）：接收`content`、`streaming`。 控制顺序：L35按`not streaming`分支；L45遍历`enumerate( ((content[:-1], None), (content[-1:], None), ("", "sto…`。 调用`httpx.Response`、`enumerate`、`chunks.append`、`json.dumps`、`"".join`。 返回路径：L36的`httpx.Response( 200, json={ "choices": [ {"finish_reason": "stop", "message": {"role": "as…`；L70的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, content="".join(chunks…`。
- `gateway`（L77–L81）：接收`store`、`handler`、`streaming`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L81的`ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=streaming)`。
- `test_redundant_closers_require_another_validated_provider_response`（L86–L136）：接收`store`、`streaming`、`succeeds`。 控制顺序：L104按`succeeds`分支；L105断言`model.complete( run, "plan:repair", "Keep the original requirements", payload, Plan )…`；L108断言`model.complete( run, "plan:repair", "Keep the original requirements", payload, Plan )…`；L114断言`all(item["status"] == "failed" for item in store.model_records(run))`；L115断言`not any(event["kind"] == "assistant_completed" for event in store.events(run))`；L116断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L117断言`all(json.loads(item["messages"][1]["content"]) == payload for item in requests)`；L118断言`all(item["response_format"] == {"type": "json_object"} for item in requests)`。后续分支沿下方源码相同行号继续阅读。 调用`plan_object`、`json.dumps`、`new_run`、`gateway`、`model.complete`、`Plan.model_validate`、`pytest.raises`、`all`、`store.model_records`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_redundant_closers_require_another_validated_provider_response.handler`（L97–L101）：接收`request`。 控制顺序：L99断言`all(item["status"] == "failed" for item in store.model_records(run))`；L100断言`not any(event["kind"] == "assistant_completed" for event in store.events(run))`。 调用`requests.append`、`json.loads`、`all`、`store.model_records`、`any`、`store.events`、`response`、`len`。 返回路径：L101的`response(valid if succeeds and len(requests) == 2 else invalid, streaming)`。
- `test_data_or_non_json_whitespace_never_becomes_a_reference`（L153–L160）：接收`tail`。 控制顺序：L157断言`_json_repair_reference(error.value, content, Plan) is None`；L159断言`details[0]["category"] == "extra_data"`；L160断言`"private-tail-canary" not in json.dumps(details)`。 调用`json.dumps`、`plan_object`、`pytest.raises`、`validate_content`、`_json_repair_reference`、`json_diagnostics`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_prefix_never_becomes_a_reference`（L175–L180）：接收`prefix`。 控制顺序：L179断言`_json_repair_reference(error.value, content, Plan) is None`；L180断言`"private-" not in json.dumps(json_diagnostics(error.value, content))`。 调用`pytest.raises`、`validate_content`、`_json_repair_reference`、`json.dumps`、`json_diagnostics`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reference_keeps_source_values_when_a_validator_mutates_its_input`（L183–L198）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L197断言`json.loads(reference) == {"value": "original"}`；L198断言`error.value.doc == content`。 调用`pytest.raises`、`validate_content`、`_json_repair_reference`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reference_keeps_source_values_when_a_validator_mutates_its_input.MutatingSchema`（L184–L191）：继承`BaseModel`。声明的数据项为`value`；类型约束/数据库列参数以完整定义为准。
- `test_reference_keeps_source_values_when_a_validator_mutates_its_input.MutatingSchema.normalizes`（L189–L191）：接收`data`。 调用`model_validator`。 返回路径：L191的`data`。
- `test_reference_encoding_respects_the_response_byte_bound`（L201–L208）：接收`monkeypatch`。 控制顺序：L208断言`_json_repair_reference(error.value, content, Plan) is None`。 调用`json.dumps`、`plan_object`、`pytest.raises`、`validate_content`、`monkeypatch.setattr`、`_json_repair_reference`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_reference_is_omitted_when_full_retry_context_would_not_fit`（L211–L249）：接收`store`。 控制顺序：L222断言`len(json.dumps(source, indent=2)) > 4000`；L240断言`model.complete( run, "plan:bounded-reference", "Keep the original scope", payload, Pl…`；L243断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L244断言`[item["role"] for item in requests[1]["messages"]] == ["system", "user", "user"]`；L245断言`json.loads(requests[1]["messages"][1]["content"]) == payload`；L246断言`sum(len(item["content"]) for item in requests[1]["messages"]) <= store.settings.max_c…`。 调用`plan_object`、`range`、`json.dumps`、`len`、`gateway`、`new_run`、`model.complete`、`Plan.model_validate`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_reference_is_omitted_when_full_retry_context_would_not_fit.handler`（L225–L232）：接收`request`。 控制顺序：L228按`len(requests) == 1`分支。 调用`json.loads`、`requests.append`、`len`、`sum`、`response`。 返回路径：L232的`response(valid + "}" if len(requests) == 1 else valid, False)`。

</details>

**创建路径：** `tests/test_json_repair_reference.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L249。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9250`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_json_repair_reference.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fe9d94ef99686c694b451e25a141891498ffc45a74570114fad4e63d8e449112"} -->
````python
# tests/test_json_repair_reference.py
"""A malformed response remains failed even when its object can guide one retry."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import BaseModel, SecretStr, model_validator

from workbench.domain import Plan
from workbench.llm import ModelFailure, ModelGateway, _json_repair_reference
from workbench.model_diagnostics import json_diagnostics
from workbench.model_protocol import validate_content


def plan_object():
    return {
        "title": "Strict format repair",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "records",
                "description": "Preserve every requested constraint",
                "fields": [
                    {"name": "note", "kind": "text", "required": False, "max_length": 80},
                    {"name": "quantity", "kind": "integer", "minimum": 0, "maximum": 12},
                ],
            }
        ],
        "acceptance": ["Keep optional notes, numeric bounds and owner isolation"],
    }


def response(content, streaming):
    if not streaming:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )
    chunks = []
    for index, (fragment, finish) in enumerate(
        ((content[:-1], None), (content[-1:], None), ("", "stop"))
    ):
        chunks.append(
            "data: "
            + json.dumps(
                {
                    "id": "offline-format-repair",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": "offline-model",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": fragment,
                                **({"role": "assistant"} if index == 0 else {}),
                            },
                            "finish_reason": finish,
                        }
                    ],
                }
            )
            + "\n\n"
        )
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content="".join(chunks) + "data: [DONE]\n\n",
    )


def gateway(store, handler, streaming=False):
    store.settings.base_url = "https://example.test/v1"
    store.settings.model = "offline-model"
    store.settings.api_key = SecretStr("private-api-key-canary")
    return ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=streaming)


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("succeeds", [False, True])
def test_redundant_closers_require_another_validated_provider_response(store, streaming, succeeds):
    source = plan_object()
    valid = json.dumps(source)
    invalid = valid + "\n } ]\t} \r\n"
    payload = {
        "original_scope": source,
        "resolution_feedback": {"round": 2, "blocked": ["Keep all fields"]},
    }
    requests = []
    run = new_run(store)

    def handler(request):
        requests.append(json.loads(request.content))
        assert all(item["status"] == "failed" for item in store.model_records(run))
        assert not any(event["kind"] == "assistant_completed" for event in store.events(run))
        return response(valid if succeeds and len(requests) == 2 else invalid, streaming)

    model = gateway(store, handler, streaming)
    if succeeds:
        assert model.complete(
            run, "plan:repair", "Keep the original requirements", payload, Plan
        ) == Plan.model_validate(source)
        assert model.complete(
            run, "plan:repair", "Keep the original requirements", payload, Plan
        ) == Plan.model_validate(source)
    else:
        with pytest.raises(ModelFailure, match="两次尝试"):
            model.complete(run, "plan:repair", "Keep the original requirements", payload, Plan)
        assert all(item["status"] == "failed" for item in store.model_records(run))
        assert not any(event["kind"] == "assistant_completed" for event in store.events(run))
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert all(json.loads(item["messages"][1]["content"]) == payload for item in requests)
    assert all(item["response_format"] == {"type": "json_object"} for item in requests)
    references = [
        item["content"] for item in requests[1]["messages"] if item["role"] == "assistant"
    ]
    assert len(references) == 1
    assert json.loads(references[0]) == source
    assert "\n  " in references[0]
    assert "searchable" not in json.loads(references[0])["entities"][0]["fields"][0]
    assert invalid not in references
    assert "尚未批准" in requests[1]["messages"][-1]["content"]
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == (1 if succeeds else 2)
    assert {event["data"]["code"] for event in failures} == {"invalid_json"}
    assert all(
        event["data"]["diagnostic"]["details"][0]["category"] == "extra_closing_delimiters"
        for event in failures
    )
    assert "Preserve every requested constraint" not in json.dumps(failures)
    assert "private-api-key-canary" not in json.dumps(failures)


@pytest.mark.parametrize(
    "tail",
    [
        " private-tail-canary",
        ',"private-tail-canary":false}',
        " {}",
        " []",
        " null",
        " 1",
        '"private-tail-canary"',
        "\u00a0}",
        "\v}",
    ],
)
def test_data_or_non_json_whitespace_never_becomes_a_reference(tail):
    content = json.dumps(plan_object()) + tail
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    assert _json_repair_reference(error.value, content, Plan) is None
    details = json_diagnostics(error.value, content)
    assert details[0]["category"] == "extra_data"
    assert "private-tail-canary" not in json.dumps(details)


@pytest.mark.parametrize(
    "prefix",
    [
        '{"title":"first","title":"second"}',
        '{"quantity":NaN}',
        '{"quantity":1e9999}',
        '"private-scalar-canary"',
        "[]",
        "{}",
        '{"entities":"private-schema-canary"}',
    ],
)
def test_invalid_prefix_never_becomes_a_reference(prefix):
    content = prefix + "}"
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    assert _json_repair_reference(error.value, content, Plan) is None
    assert "private-" not in json.dumps(json_diagnostics(error.value, content))


def test_reference_keeps_source_values_when_a_validator_mutates_its_input():
    class MutatingSchema(BaseModel):
        value: str

        @model_validator(mode="before")
        @classmethod
        def normalizes(cls, data):
            data["value"] = "normalized"
            return data

    content = '{"value":"original"}}'
    with pytest.raises(ValueError) as error:
        validate_content(content, MutatingSchema, mode="json_object")
    reference = _json_repair_reference(error.value, content, MutatingSchema)
    assert json.loads(reference) == {"value": "original"}
    assert error.value.doc == content


def test_reference_encoding_respects_the_response_byte_bound(monkeypatch):
    from workbench import llm

    content = json.dumps(plan_object()) + "}"
    with pytest.raises(ValueError) as error:
        validate_content(content, Plan, mode="json_object")
    monkeypatch.setattr(llm, "MAX_MODEL_CONTENT_BYTES", 10)
    assert _json_repair_reference(error.value, content, Plan) is None


def test_optional_reference_is_omitted_when_full_retry_context_would_not_fit(store):
    source = plan_object()
    source["entities"] = [
        {
            "name": f"records_{index}",
            "description": "Keep all source fields",
            "fields": [{"name": f"value_{field}", "kind": "text"} for field in range(8)],
        }
        for index in range(8)
    ]
    valid = json.dumps(source)
    assert len(json.dumps(source, indent=2)) > 4000
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            store.settings.max_context_chars = (
                sum(len(item["content"]) for item in body["messages"]) + 2000
            )
        return response(valid + "}" if len(requests) == 1 else valid, False)

    model = gateway(store, handler)
    run = new_run(store)
    payload = {
        "scope": "Keep all eight entities and their fields",
        "resolution_feedback": {"round": 1},
    }
    assert model.complete(
        run, "plan:bounded-reference", "Keep the original scope", payload, Plan
    ) == Plan.model_validate(source)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert [item["role"] for item in requests[1]["messages"]] == ["system", "user", "user"]
    assert json.loads(requests[1]["messages"][1]["content"]) == payload
    assert (
        sum(len(item["content"]) for item in requests[1]["messages"])
        <= store.settings.max_context_chars
    )
````
