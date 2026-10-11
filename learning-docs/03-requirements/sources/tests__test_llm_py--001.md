# tests/test_llm.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `gateway`（L13–L19）：接收`store`、`handler`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L19的`ModelGateway(store.settings, store, httpx.MockTransport(handler))`。
- `test_success_cache_and_usage`（L22–L42）：接收`store`。 控制顺序：L40断言`model.complete(run, "test", "instruction", {}, Requirement) == a`；L41断言`len(calls) == 1`；L42断言`store.get_run(run)["model_calls"] == 1`。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_success_cache_and_usage.handler`（L25–L35）：接收`request`。 调用`calls.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L27的`httpx.Response( 200, json={ "choices": [ {"message": {"role": "assistant", "content": requ…`。
- `test_failures_not_fake_success`（L46–L50）：接收`store`、`status`。 控制顺序：L50断言`"do-not-disclose" not in str(error.value)`。 调用`gateway`、`httpx.Response`、`pytest.raises`、`model.complete`、`new_run`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permanent_transport_diagnostics_are_redacted_and_not_retried`（L57–L77）：接收`store`、`kind`、`message`。 控制顺序：L75断言`message in str(error.value)`；L76断言`"do-not-disclose" not in str(error.value)`；L77断言`len(calls) == store.get_run(run)["model_calls"] == 1`。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`str`、`len`、`store.get_run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permanent_transport_diagnostics_are_redacted_and_not_retried.handler`（L60–L69）：接收`request`。 控制顺序：L62按`kind == "proxy"`分支；L63抛异常，停止当前正常路径；L65抛异常，停止当前正常路径；L67按`kind == "proxy_certificate"`分支；L68抛异常，停止当前正常路径；L69抛异常，停止当前正常路径。 调用`calls.append`、`httpx.ProxyError`、`ssl.SSLCertVerificationError`、`httpx.ConnectError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_json_bounded`（L80–L90）：接收`store`。 控制顺序：L90断言`store.get_run(run)["model_calls"] == 2`。 调用`gateway`、`httpx.Response`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials`（L93–L129）：接收`store`。 控制顺序：L121断言`result.business is not None`；L122断言`len(requests) == 2`；L124断言`[message["role"] for message in retry] == ["system", "user", "assistant", "user"]`；L125断言`retry[-2]["role"] == "assistant"`；L126断言`json.loads(retry[-2]["content"]) == invalid`；L127断言`"日期范围只支持 date 类型" in retry[-1]["content"]`；L128断言`"entities" in retry[-1]["content"] and "fields" in retry[-1]["content"]`；L129断言`"do-not-disclose" not in json.dumps(retry)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.dumps`、`next`、`gateway`、`model.complete`、`new_run`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_retry_contains_exact_validator_feedback_without_credentials.handler`（L103–L117）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`json.dumps`、`len`。 返回路径：L105的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": js…`。
- `test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract`（L150–L206）：接收`store`、`bad`、`category`。 控制顺序：L177断言`model.complete(run, "requirement:json-repair", "instruction", payload, Requirement)`；L178断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L180断言`len(failures) == 1`；L183断言`failure["code"] == "invalid_json"`；L184断言`detail["category"] == category`；L185按`category == "expected_value"`分支；L186断言`detail["position"] == {"line": 3, "column": 11, "offset": bad.index("]")}`；L188断言`"position" not in detail`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.get_run`、`store.events`、`bad.index`、`bad.encode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonstream_json_failure_persists_safe_location_and_repairs_same_contract.handler`（L155–L172）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`len`、`requirement().model_dump_json`、`requirement`。 返回路径：L157的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": { "role": "…`。
- `test_large_valid_plan_does_not_trigger_a_local_json_size_or_node_threshold`（L209–L241）：接收`store`。 控制顺序：L226断言`len(content) > 30000`；L239断言`model.complete(run, "plan:large-protocol", "instruction", {}, Plan) == expected`；L240断言`store.get_run(run)["model_calls"] == 1`；L241断言`not [event for event in store.events(run) if event["kind"] == "model_failure"]`。 调用`Plan.model_validate`、`range`、`expected.model_dump_json`、`len`、`gateway`、`httpx.Response`、`new_run`、`model.complete`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts`（L245–L327）：接收`store`、`repair_succeeds`。 控制顺序：L297按`repair_succeeds`分支；L298断言`model.complete( run, "plan:extra-data", "Preserve confirmed scope", payload, Plan ) =…`；L304断言`len(requests) == store.get_run(run)["model_calls"] == 2`；L305断言`Plan.model_json_schema() == original_schema`；L306断言`requests[0]["messages"][0] == requests[1]["messages"][0]`；L308断言`instruction.endswith(json.dumps(original_schema, ensure_ascii=False))`；L309断言`"同一对象内的字段名只能出现一次" in instruction`；L310断言`"required 的字段" in instruction`。后续分支沿下方源码相同行号继续阅读。 调用`Plan.model_validate`、`json.dumps`、`Plan.model_json_schema`、`gateway`、`new_run`、`model.complete`、`pytest.raises`、`len`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_data_repair_preserves_compact_plan_and_stops_after_two_attempts.handler`（L278–L293）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`、`len`。 返回路径：L280的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": { "role": "…`。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code`（L331–L380）：接收`store`、`monkeypatch`、`raises`。 控制顺序：L377断言`len(failures) == store.get_run(run)["model_calls"] == 2`；L378断言`{event["data"]["code"] for event in failures} == {"structured_parser_disagreement"}`；L379断言`all(event["data"]["diagnostic"]["phase"] == "model_execution" for event in failures)`；L380断言`"private-adapter-canary" not in json.dumps(failures)`。 调用`monkeypatch.setattr`、`gateway`、`httpx.Response`、`requirement().model_dump_json`、`requirement`、`new_run`、`pytest.raises`、`model.complete`、`store.events`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees`（L339–L353）：接收`*args`、`**kwargs`。 调用`original`、`RejectingParser`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees.RejectingParser`（L342–L351）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_valid_local_json_with_langchain_disagreement_has_its_own_failure_code.disagrees.RejectingParser.invoke`（L343–L351）：接收`*invoke_args`、`**invoke_kwargs`。 控制顺序：L345按`raises`分支；L346抛异常，停止当前正常路径。 调用`structured.invoke`、`ValueError`。 返回路径：L347的`{ **result, "parsed": None, "parsing_error": ValueError("private-adapter-canary"), }`。
- `test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text`（L390–L411）：接收`store`、`wire`、`category`。 控制顺序：L402断言`len(failures) == store.get_run(run)["model_calls"] == 2`；L403遍历`failures`；L405断言`event["data"]["code"] == "invalid_json"`；L406断言`detail["category"] == category`；L407断言`detail["lengths"] == {"bytes": len(wire)}`；L408断言`"position" not in detail`；L409断言`category in requests[1]["messages"][-1]["content"]`；L410断言`"private-wire-key" not in json.dumps(failures)`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`store.events`、`len`、`store.get_run`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_audited_envelope_failure_survives_sdk_wrapping_without_raw_text.handler`（L393–L395）：接收`request`。 调用`requests.append`、`json.loads`、`httpx.Response`。 返回路径：L395的`httpx.Response(200, headers={"content-type": "application/json"}, content=wire)`。
- `test_live_receipts_preserve_each_attempt_without_provider_content`（L417–L451）：接收`store`、`kind`。 控制顺序：L441断言`len(calls) == store.get_run(run)["model_calls"] == 2`；L446按`second["code"] == "transport_error"`分支；L448断言`model_failure_receipts(store.model_records(run)) == [ {"code": "invalid_json", "attem…`。 调用`new_run`、`pytest.raises`、`gateway(store, handler).complete`、`gateway`、`len`、`store.get_run`、`model_failure_receipts`、`store.model_records`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_receipts_preserve_each_attempt_without_provider_content.handler`（L422–L436）：接收`request`。 控制顺序：L424按`len(calls) == 2`分支；L425按`kind == "read_timeout"`分支；L426抛异常，停止当前正常路径；L427按`kind == "remote_protocol_error"`分支；L428抛异常，停止当前正常路径；L429按`kind == "http_429"`分支。 调用`calls.append`、`len`、`httpx.ReadTimeout`、`httpx.RemoteProtocolError`、`httpx.Response`。 返回路径：L430的`httpx.Response(429, text="private-error-url-key-prompt")`；L431的`httpx.Response( 200, json={ "choices": [{"message": {"role": "assistant", "content": "priv…`。
- `test_transport_category_follows_typed_causes_and_stops_cycles`（L454–L462）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L458断言`transport_category(outer) == "other"`；L460断言`transport_category(outer) == "read_timeout"`；L462断言`transport_category(outer) == "other"`。 调用`RuntimeError`、`transport_category`、`httpx.ReadTimeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_llm.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L462。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17797`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_llm.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "da7b2deffac217c7737e48b9547f36b6da8fd2a615da02b2940aaf32d72bb944"} -->
````python
# tests/test_llm.py
import json
import ssl
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


@pytest.mark.parametrize(
    "kind,message",
    [("proxy", "代理"), ("certificate", "TLS 证书"), ("proxy_certificate", "TLS 证书")],
)
def test_permanent_transport_diagnostics_are_redacted_and_not_retried(store, kind, message):
    calls = []

    def handler(request):
        calls.append(request)
        if kind == "proxy":
            raise httpx.ProxyError("403 do-not-disclose", request=request)
        try:
            raise ssl.SSLCertVerificationError(1, "do-not-disclose")
        except ssl.SSLCertVerificationError as cause:
            if kind == "proxy_certificate":
                raise httpx.ProxyError("do-not-disclose", request=request) from cause
            raise httpx.ConnectError("do-not-disclose", request=request) from cause

    model = gateway(store, handler)
    run = new_run(store)
    with pytest.raises(ModelFailure) as error:
        model.complete(run, "error", "x", {}, Requirement)
    assert message in str(error.value)
    assert "do-not-disclose" not in str(error.value)
    assert len(calls) == store.get_run(run)["model_calls"] == 1


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


@pytest.mark.parametrize(
    "kind", ["read_timeout", "remote_protocol_error", "http_429", "invalid_json"]
)
def test_live_receipts_preserve_each_attempt_without_provider_content(store, kind):
    from scripts.ci_live_modules import model_failure_receipts

    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) == 2:
            if kind == "read_timeout":
                raise httpx.ReadTimeout("private-error-url-key-prompt", request=request)
            if kind == "remote_protocol_error":
                raise httpx.RemoteProtocolError("private-error-url-key-prompt", request=request)
            if kind == "http_429":
                return httpx.Response(429, text="private-error-url-key-prompt")
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"role": "assistant", "content": "private-invalid-json"}}]
            },
        )

    run = new_run(store)
    with pytest.raises(ModelFailure):
        gateway(store, handler).complete(run, "error", "private-instruction", {}, Requirement)
    assert len(calls) == store.get_run(run)["model_calls"] == 2
    second = {
        "code": kind if kind in {"http_429", "invalid_json"} else "transport_error",
        "attempt": 2,
    }
    if second["code"] == "transport_error":
        second["transport_kind"] = kind
    assert model_failure_receipts(store.model_records(run)) == [
        {"code": "invalid_json", "attempt": 1},
        second,
    ]


def test_transport_category_follows_typed_causes_and_stops_cycles():
    from workbench.model_diagnostics import transport_category

    outer = RuntimeError("ReadTimeout in private error text is not evidence")
    assert transport_category(outer) == "other"
    outer.__cause__ = httpx.ReadTimeout("private")
    assert transport_category(outer) == "read_timeout"
    outer.__cause__ = outer
    assert transport_category(outer) == "other"
````
