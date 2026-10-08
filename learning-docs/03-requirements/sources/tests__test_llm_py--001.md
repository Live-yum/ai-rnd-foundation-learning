# tests/test_llm.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `gateway`（L12–L18）：接收`store`、`handler`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L18的`ModelGateway(store.settings, store, httpx.MockTransport(handler))`。
- `test_success_cache_and_usage`（L21–L41）：接收`store`。 控制顺序：L39断言`model.complete(run, "test", "instruction", {}, Requirement) == a`；L40断言`len(calls) == 1`；L41断言`store.get_run(run)["model_calls"] == 1`。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_success_cache_and_usage.handler`（L24–L34）：接收`request`。 调用`calls.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L26的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_failures_not_fake_success`（L45–L49）：接收`store`、`status`。 控制顺序：L49断言`"do-not-disclose" not in str(error.value)`。 调用`gateway`、`httpx.Response`、`pytest.raises`、`model.complete`、`new_run`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_json_bounded`（L52–L62）：接收`store`。 控制顺序：L62断言`store.get_run(run)["model_calls"] == 2`。 调用`gateway`、`httpx.Response`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials`（L65–L101）：接收`store`。 控制顺序：L93断言`result.business is not None`；L94断言`len(requests) == 2`；L96断言`[message["role"] for message in retry] == ["system", "user", "assistant", "user"]`；L97断言`retry[-2]["role"] == "assistant"`；L98断言`json.loads(retry[-2]["content"]) == invalid`；L99断言`"日期范围只支持 date 类型" in retry[-1]["content"]`；L100断言`"entities" in retry[-1]["content"] and "fields" in retry[-1]["content"]`；L101断言`"do-not-disclose" not in json.dumps(retry)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.dumps`、`next`、`gateway`、`model.complete`、`new_run`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials.handler`（L75–L89）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`json.dumps`、`len`。 返回路径：L77的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": js…`。
- `test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract`（L122–L178）：接收`store`、`bad`、`category`。 控制顺序：L149断言`model.complete(run, "requirement:json-repair", "instruction", payload, Requirement)`；L150断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L152断言`len(failures) == 1`；L155断言`failure["code"] == "invalid_json"`；L156断言`detail["category"] == category`；L157按`category == "expected_value"`分支；L158断言`detail["position"] == {"line": 3, "column": 11, "offset": bad.index("]")}`；L160断言`"position" not in detail`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.get_run`、`store.events`、`bad.index`、`bad.encode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract.handler`（L127–L144）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`len`、`requirement().model_dump_json`、`requirement`。 返回路径：L129的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": { "role": "…`。
- `test_large_valid_plan_does_not_trigger_a_local_json_size_or_node_threshold`（L181–L213）：接收`store`。 控制顺序：L198断言`len(content) > 30000`；L211断言`model.complete(run, "plan:large-protocol", "instruction", {}, Plan) == expected`；L212断言`store.get_run(run)["model_calls"] == 1`；L213断言`not [event for event in store.events(run) if event["kind"] == "model_failure"]`。 调用`Plan.model_validate`、`range`、`expected.model_dump_json`、`len`、`gateway`、`httpx.Response`、`new_run`、`model.complete`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts`（L217–L299）：接收`store`、`repair_succeeds`。 控制顺序：L269按`repair_succeeds`分支；L270断言`model.complete( run, "plan:extra-data", "Preserve confirmed scope", payload, Plan ) =…`；L276断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L277断言`Plan.model_json_schema() == original_schema`；L278断言`requests[0]["messages"][0] == requests[1]["messages"][0]`；L280断言`instruction.endswith(json.dumps(original_schema, ensure_ascii=False))`；L281断言`"同一对象内的字段名只能出现一次" in instruction`；L282断言`"required 的字段" in instruction`。后续分支沿下方源码相同行号继续阅读。 调用`Plan.model_validate`、`json.dumps`、`Plan.model_json_schema`、`gateway`、`new_run`、`model.complete`、`pytest.raises`、`len`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts.handler`（L250–L265）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`len`。 返回路径：L252的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": { "role": "…`。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code`（L303–L352）：接收`store`、`monkeypatch`、`raises`。 控制顺序：L349断言`len(failures) == store.get_run(run)["model_calls"] == 2`；L350断言`{event["data"]["code"] for event in failures} == {"structured_parser_disagreement"}`；L351断言`all(event["data"]["diagnostic"]["phase"] == "model_execution" for event in failures)`；L352断言`"private-adapter-canary" not in json.dumps(failures)`。 调用`monkeypatch.setattr`、`gateway`、`httpx.Response`、`requirement().model_dump_json`、`requirement`、`new_run`、`pytest.raises`、`model.complete`、`store.events`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees`（L311–L325）：接收`*args`、`**kwargs`。 调用`original`、`RejectingParser`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees.RejectingParser`（L314–L323）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees.RejectingParser.invoke`（L315–L323）：接收`*invoke_args`、`**invoke_kwargs`。 控制顺序：L317按`raises`分支；L318抛异常，停止当前正常路径。 调用`structured.invoke`、`ValueError`。 返回路径：L319的`{ **result, "parsed": None, "parsing_error": ValueError("private-adapter-canary"), }`。
- `test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text`（L362–L383）：接收`store`、`wire`、`category`。 控制顺序：L374断言`len(failures) == store.get_run(run)["model_calls"] == 2`；L375遍历`failures`；L377断言`event["data"]["code"] == "invalid_json"`；L378断言`detail["category"] == category`；L379断言`detail["lengths"] == {"bytes": len(wire)}`；L380断言`"position" not in detail`；L381断言`category in requests[1]["messages"][-1]["content"]`；L382断言`"private-wire-key" not in json.dumps(failures)`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`store.events`、`len`、`store.get_run`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text.handler`（L365–L367）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`。 返回路径：L367的`httpx.Response(200, headers={"content-type": "application/json"}, content=wire)`。

</details>

**创建路径：** `tests/test_llm.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L383。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14753`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_llm.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0f593e8ea7555a31f770e289dc44ccdd3d10c4727efb1e7c786babf74b0d716a"} -->
````python
# tests/test_llm.py
import json
from contextlib import contextmanager

import httpx
import pytest
from conftest import new_run, requirement

from workbench.domain import Plan, Requirement
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
    assert [message["role"] for message in retry] == ["system", "user", "assistant", "user"]
    assert retry[-2]["role"] == "assistant"
    assert json.loads(retry[-2]["content"]) == invalid
    assert "日期范围只支持 date 类型" in retry[-1]["content"]
    assert "entities" in retry[-1]["content"] and "fields" in retry[-1]["content"]
    assert "do-not-disclose" not in json.dumps(retry)


@pytest.mark.parametrize(
    "bad,category",
    [
        (
            '{\n "summary": "private-response-canary do-not-disclose",\n "users": ]}',
            "expected_value",
        ),
        (
            '{"private-response-canary":"do-not-disclose","private-response-canary":1}',
            "duplicate_json_key",
        ),
        (
            '{"summary":"private-response-canary do-not-disclose","value":NaN}',
            "non_finite_json_number",
        ),
        ('["private-response-canary do-not-disclose"]', "response_must_be_json_object"),
    ],
)
def test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract(
    store, bad, category
):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": bad
                            if len(requests) == 1
                            else requirement().model_dump_json(),
                        },
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    payload = {"request": "Keep all confirmed fields"}
    assert model.complete(run, "requirement:json-repair", "instruction", payload, Requirement)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == 1
    failure = failures[0]["data"]
    detail = failure["diagnostic"]["details"][0]
    assert failure["code"] == "invalid_json"
    assert detail["category"] == category
    if category == "expected_value":
        assert detail["position"] == {"line": 3, "column": 11, "offset": bad.index("]")}
    else:
        assert "position" not in detail
    assert detail["lengths"] == {"characters": len(bad), "bytes": len(bad.encode())}
    assert "private-response-canary" not in json.dumps(failures)
    assert "do-not-disclose" not in json.dumps(failures)
    feedback = requests[1]["messages"][-1]["content"]
    assert json.dumps(detail, ensure_ascii=False) in feedback
    assert "private-response-canary" not in feedback
    assert [message["role"] for message in requests[1]["messages"]] == [
        "system",
        "user",
        "user",
    ]
    assert "private-response-canary" not in json.dumps(requests[1])
    assert "do-not-disclose" not in json.dumps(requests[1])
    assert requests[0]["messages"][0] == requests[1]["messages"][0]
    assert json.loads(requests[1]["messages"][1]["content"]) == payload
    assert (
        requests[0]["response_format"] == requests[1]["response_format"] == {"type": "json_object"}
    )


def test_large_valid_plan_does_not_trigger_a_local_json_size_or_node_threshold(store):
    expected = Plan.model_validate(
        {
            "title": "Large protocol boundary fixture",
            "data_scope": "per_user",
            "entities": [
                {
                    "name": f"record_{entity}",
                    "description": "Independent entity in a parser test",
                    "fields": [{"name": f"field_{field}", "kind": "text"} for field in range(16)],
                }
                for entity in range(8)
            ],
            "acceptance": ["Every declared entity and field remains present"],
        }
    )
    content = expected.model_dump_json(indent=2)
    assert len(content) > 30000
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        ),
    )
    run = new_run(store)
    assert model.complete(run, "plan:large-protocol", "instruction", {}, Plan) == expected
    assert store.get_run(run)["model_calls"] == 1
    assert not [event for event in store.events(run) if event["kind"] == "model_failure"]


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts(
    store, repair_succeeds
):
    compact = {
        "title": "Protocol repair fixture",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "record",
                "description": "Keep all requested fields and constraints",
                "fields": [
                    {"name": "note", "kind": "text", "required": False, "max_length": 80},
                    {"name": "quantity", "kind": "integer", "minimum": 0, "maximum": 12},
                ],
            }
        ],
        "acceptance": ["Owner isolation, optional notes up to 80 characters, quantity 0 to 12"],
    }
    expected = Plan.model_validate(compact, strict=True)
    valid = json.dumps(compact)
    invalid = valid + ',"private-tail-canary":false}'
    original_schema = Plan.model_json_schema()
    payload = {
        "confirmed_plan_scope": compact,
        "previous_plan": compact,
        "resolution_feedback": {
            "stage": "design",
            "round": 2,
            "blocked": ["Preserve optional notes, the numeric range and owner isolation"],
        },
    }
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": valid if repair_succeeds and len(requests) == 2 else invalid,
                        },
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    if repair_succeeds:
        assert model.complete(
            run, "plan:extra-data", "Preserve confirmed scope", payload, Plan
        ) == (expected)
    else:
        with pytest.raises(ModelFailure, match="两次尝试"):
            model.complete(run, "plan:extra-data", "Preserve confirmed scope", payload, Plan)
    assert len(requests) == store.get_run(run)["model_calls"] == 2
    assert Plan.model_json_schema() == original_schema
    assert requests[0]["messages"][0] == requests[1]["messages"][0]
    instruction = requests[0]["messages"][0]["content"]
    assert instruction.endswith(json.dumps(original_schema, ensure_ascii=False))
    assert "同一对象内的字段名只能出现一次" in instruction
    assert "required 的字段" in instruction
    assert "仅可省略已有 Schema 默认值且本轮需求无需指定的可选字段" in instruction
    assert "即使等于默认值也要保留" in instruction
    assert all(json.loads(request["messages"][1]["content"]) == payload for request in requests)
    assert all(request["response_format"] == {"type": "json_object"} for request in requests)
    assert [message["role"] for message in requests[1]["messages"]] == [
        "system",
        "user",
        "user",
    ]
    assert "private-tail-canary" not in json.dumps(requests[1])
    feedback = requests[1]["messages"][-1]["content"]
    assert "extra_data" in feedback and "同一根对象的最后一个 } 之前" in feedback
    assert "保留全部业务字段" in feedback and "private-tail-canary" not in feedback
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == (1 if repair_succeeds else 2)
    assert all(event["data"]["code"] == "invalid_json" for event in failures)
    assert "private-tail-canary" not in json.dumps(failures)


@pytest.mark.parametrize("raises", [False, True])
def test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code(
    store, monkeypatch, raises
):
    from workbench import llm

    original = llm.structured_model

    @contextmanager
    def disagrees(*args, **kwargs):
        with original(*args, **kwargs) as structured:

            class RejectingParser:
                def invoke(self, *invoke_args, **invoke_kwargs):
                    result = structured.invoke(*invoke_args, **invoke_kwargs)
                    if raises:
                        raise ValueError("private-adapter-canary")
                    return {
                        **result,
                        "parsed": None,
                        "parsing_error": ValueError("private-adapter-canary"),
                    }

            yield RejectingParser()

    monkeypatch.setattr(llm, "structured_model", disagrees)
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": requirement().model_dump_json(),
                        },
                    }
                ]
            },
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure, match="两次尝试"):
        model.complete(run, "requirement:adapter", "instruction", {}, Requirement)
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == store.get_run(run)["model_calls"] == 2
    assert {event["data"]["code"] for event in failures} == {"structured_parser_disagreement"}
    assert all(event["data"]["diagnostic"]["phase"] == "model_execution" for event in failures)
    assert "private-adapter-canary" not in json.dumps(failures)


@pytest.mark.parametrize(
    "wire,category",
    [
        (b'{"private-wire-key": 1, "private-wire-key": 2}', "duplicate_json_key"),
        (b'{"private-wire-key": 1e9999}', "non_finite_json_number"),
    ],
)
def test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text(store, wire, category):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, headers={"content-type": "application/json"}, content=wire)

    model = gateway(store, handler)
    run = new_run(store)
    with pytest.raises(ModelFailure, match="两次尝试"):
        model.complete(run, "requirement:wire-rejection", "instruction", {}, Requirement)
    failures = [event for event in store.events(run) if event["kind"] == "model_failure"]
    assert len(failures) == store.get_run(run)["model_calls"] == 2
    for event in failures:
        detail = event["data"]["diagnostic"]["details"][0]
        assert event["data"]["code"] == "invalid_json"
        assert detail["category"] == category
        assert detail["lengths"] == {"bytes": len(wire)}
        assert "position" not in detail
    assert category in requests[1]["messages"][-1]["content"]
    assert "private-wire-key" not in json.dumps(failures)
    assert "private-wire-key" not in json.dumps(requests)
````
