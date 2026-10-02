# tests/test_provider_structured_outputs.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.model_protocol`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `profile`（L25–L32）：接收`provider`、`model`、`**kwargs`。 调用`ModelProfile`、`SecretStr`。 返回路径：L26的`ModelProfile( stage="requirements", base_url=f"https://api.{provider}.com/v1", api_key=Sec…`。
- `envelope`（L35–L48）：接收`content`、`finish`、`**message_fields`。 返回路径：L36的`{ "choices": [ { "finish_reason": finish, "message": { "role": "assistant", "content": con…`。
- `gateway`（L51–L64）：接收`store`、`responses`、`provider`、`model`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L64的`ModelGateway(store.settings, store, httpx.MockTransport(handle)), seen`。
- `gateway.handle`（L57–L62）：接收`request`。 控制顺序：L60按`isinstance(response, httpx.Response)`分支。 调用`seen.append`、`json.loads`、`min`、`len`、`isinstance`、`httpx.Response`。 返回路径：L61的`response`；L62的`httpx.Response(200, json=response)`。
- `test_official_wrappers_own_structured_request_without_model_tables`（L79–L110）：接收`store`、`monkeypatch`、`provider`、`model`、`token_field`。 控制顺序：L101断言`result.summary == "ok"`；L102断言`wrappers == [(ModelReview, {"method": "json_mode", "include_raw": True})]`；L103断言`seen[0]["response_format"] == {"type": "json_object"}`；L104断言`seen[0]["model"] == model`；L105断言`seen[0][token_field] == (65536 if provider == "deepseek" else 16384)`；L106断言`"thinking" not in seen[0] and "temperature" not in seen[0]`；L107断言`not seen[0]["stream"]`；L108断言`"ModelReview" in seen[0]["messages"][0]["content"]`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`gateway`、`envelope`、`ModelReview(summary="ok").model_dump_json`、`ModelReview`、`model_gateway.complete`、`new_run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_official_wrappers_own_structured_request_without_model_tables.wrapped`（L89–L91）：接收`schema`、`**kwargs`。 调用`wrappers.append`、`original`。 返回路径：L91的`original(self, schema, **kwargs)`。
- `test_same_json_mode_pipeline_preserves_every_domain_schema`（L114–L121）：接收`schema`。 控制顺序：L116遍历`("openai", "deepseek")`；L118断言`contract.mode == "json_object"`；L119断言`contract.reason == "langchain_json_mode"`；L120断言`contract.receipt()["structured_output"] == "langchain.with_structured_output"`；L121断言`before == schema.model_json_schema()`。 调用`copy.deepcopy`、`schema.model_json_schema`、`output_contract`、`profile`、`contract.receipt`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_four_graph_stage_schemas_use_real_framework_parser`（L126–L158）：接收`store`、`provider`、`schema`。 控制顺序：L157断言`isinstance(result, schema)`；L158断言`len(seen) == 1 and seen[0]["response_format"] == {"type": "json_object"}`。 调用`requirement().model_dump_json`、`requirement`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.dumps`、`ModelReview(summary="offline review").model_dump_json`、`ModelReview`、`gateway`、`envelope`、`model.complete`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_output_mode_fails_locally_without_request_or_budget`（L161–L167）：接收`store`。 控制顺序：L167断言`seen == [] and store.get_run(run)["model_calls"] == 0`。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_endpoint_detection_uses_exact_host_and_proxy_can_select_official_integration`（L170–L175）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L173断言`contract.provider == "compatible" and contract.mode == "json_object"`；L175断言`explicit.provider == "deepseek" and explicit.mode == "json_object"`。 调用`profile().model_copy`、`profile`、`output_contract`、`fake.model_copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stage_provider_overrides_do_not_leak_on_endpoint_change`（L178–L203）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L191断言`settings.model_for("requirements").provider == "openai"`；L193断言`(planning.provider, planning.output_mode, planning.max_output_tokens) == ( "auto", "a…`；L198断言`output_contract(planning, Plan).provider == "deepseek"`；L200断言`output_contract(settings.model_for("planning"), Plan).request_fields["max_output_toke…`。 调用`Settings`、`settings.model_for`、`output_contract`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_request_receipt_cache_and_capability_changes`（L206–L224）：接收`store`。 控制顺序：L211断言`model.complete(run, "requirement:1", "Preserve confirmed facts", {}, Requirement) == …`；L214断言`len(seen) == 1`；L215断言`seen[0]["response_format"] == {"type": "json_object"}`；L216断言`"JSON" in seen[0]["messages"][0]["content"]`；L218断言`receipt["provider"] == "openai"`；L219断言`receipt["output_mode"] == "json_object"`；L220断言`receipt["contract_version"] == 2 and receipt["finish_reason"] == "stop"`；L221断言`"offline-test-key" not in json.dumps(receipt)`。后续分支沿下方源码相同行号继续阅读。 调用`envelope`、`requirement().model_dump_json`、`requirement`、`gateway`、`new_run`、`model.complete`、`len`、`store.model_records`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_records_stay_identifiable_but_cannot_satisfy_new_framework_cache`（L227–L244）：接收`store`。 控制顺序：L242断言`len(seen) == 1`；L243断言`[row["status"] for row in records] == ["legacy", "validated"]`；L244断言`[row["contract_version"] for row in records] == [0, 2]`。 调用`gateway`、`envelope`、`requirement().model_dump_json`、`requirement`、`new_run`、`store.step`、`requirement().model_dump`、`model.complete`、`store.model_records`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_status_never_accepts_otherwise_valid_json_or_repairs`（L257–L270）：接收`store`、`finish`、`extra`、`match`。 控制顺序：L262断言`"sensitive provider text" not in str(error.value)`；L263断言`len(seen) == store.get_run(run)["model_calls"] == 1`；L265断言`len(records) == 1 and records[0]["status"] == "failed"`；L266断言`records[0]["code"] in {"refusal", "truncated", "content_filter", "unexpected_tool_cal…`；L267断言`records[0]["contract_version"] == 2`；L268断言`records[0]["output_mode"] == "json_object"`；L269断言`"sensitive provider text" not in json.dumps(records, default=str)`；L270断言`"offline-test-key" not in json.dumps(records, default=str)`。 调用`gateway`、`envelope`、`requirement().model_dump_json`、`requirement`、`new_run`、`pytest.raises`、`model.complete`、`str`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_or_interrupted_envelopes_are_bounded_and_not_success`（L287–L293）：接收`store`、`bad`。 控制顺序：L292断言`len(seen) == 2`；L293断言`all(record["status"] == "failed" for record in store.model_records(run))`。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`len`、`all`、`store.model_records`、`pytest.mark.parametrize`、`envelope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_empty_deepseek_content_can_repair_once_without_using_reasoning`（L296–L309）：接收`store`。 控制顺序：L307断言`len(seen) == 2`；L308断言`"private reasoning" not in json.dumps(seen[1])`；L309断言`seen[1]["response_format"] == {"type": "json_object"}`。 调用`gateway`、`envelope`、`requirement().model_dump_json`、`requirement`、`model.complete`、`new_run`、`len`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typed_validation_rejects_coercion_and_repairs_exact_field_without_changing_schema`（L312–L321）：接收`store`。 控制顺序：L318断言`result.business is not None and len(seen) == 2`；L319断言`"bool_type" in seen[1]["messages"][-1]["content"]`；L320断言`"required" in seen[1]["messages"][-1]["content"]`；L321断言`seen[0]["response_format"] == seen[1]["response_format"]`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`copy.deepcopy`、`gateway`、`envelope`、`json.dumps`、`model.complete`、`new_run`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_mode_rejects_duplicate_nonfinite_nonobject_and_fenced_content`（L335–L337）：接收`content`。 调用`pytest.raises`、`validate_content`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lenient_framework_parser_cannot_hide_incomplete_raw_json`（L340–L347）：接收`store`。 控制顺序：L346断言`len(seen) == 2`；L347断言`all(row["status"] == "failed" for row in store.model_records(run))`。 调用`ModelReview(summary="test").model_dump_json`、`ModelReview`、`gateway`、`envelope`、`new_run`、`pytest.raises`、`model.complete`、`len`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dynamic_facts_and_choice_labels_are_preserved_in_json_mode`（L350–L360）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L353断言`validate_content(json.dumps(facts), Requirement, mode="json_object").facts == facts["…`；L360断言`any(f.choice_labels for e in validated.entities for f in e.fields)`。 调用`requirement().model_dump`、`requirement`、`validate_content`、`json.dumps`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_validator_is_still_required_after_valid_provider_json`（L363–L368）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`pytest.raises`、`validate_content`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_usage_is_sanitized_and_duplicate_envelopes_or_malformed_refusals_fail`（L371–L385）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L381断言`completion_content(result, contract)[1] == {}`。 调用`ModelReview(summary="test").model_dump_json`、`ModelReview`、`envelope`、`OutputContract`、`completion_content`、`pytest.raises`、`load_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_error_retry_budget_never_downgrades_output_format`（L391–L397）：接收`store`、`status`、`expected_calls`。 控制顺序：L395断言`len(seen) == expected_calls`；L396断言`"raw-provider-secret" not in str(error.value)`；L397断言`all(call["response_format"]["type"] == "json_object" for call in seen)`。 调用`gateway`、`httpx.Response`、`pytest.raises`、`model.complete`、`new_run`、`len`、`str`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_full_context_and_repair_are_bounded_before_an_extra_model_call`（L400–L406）：接收`store`。 控制顺序：L406断言`seen == [] and store.get_run(run)["model_calls"] == 0`。 调用`gateway`、`envelope`、`requirement().model_dump_json`、`requirement`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop`（L411–L445）：接收`store`、`monkeypatch`、`inside_event_loop`、`http_status`。 控制顺序：L440按`inside_event_loop`分支；L444断言`len(seen) == 1 and clients`；L445断言`all(client.is_closed for client in clients)`。 调用`monkeypatch.setattr`、`envelope`、`requirement().model_dump_json`、`requirement`、`httpx.Response`、`gateway`、`asyncio.run`、`call_inside_loop`、`call`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop.TrackedAsync`（L419–L422）：继承`actual_async`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop.TrackedAsync.__init__`（L420–L422）：接收`*args`、`**kwargs`。 调用`super().__init__`、`super`、`clients.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop.call`（L430–L435）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L431按`http_status == 200`分支。 调用`model.complete`、`new_run`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop.call_inside_loop`（L437–L438）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`call`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_provider_structured_outputs.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L445。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17840`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_provider_structured_outputs.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "16acb2ed1776601e44d426d2d9477bb94a3a53a01212738e7157f0dd887d189e"} -->
````python
# tests/test_provider_structured_outputs.py
"""Offline request/response contracts only: these tests never call a real provider."""

import asyncio
import copy
import json

import httpx
import pytest
from conftest import new_run, requirement
from pydantic import SecretStr

from workbench.domain import ModelReview, Patches, Plan, Requirement
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_protocol import (
    OutputContract,
    OutputFailure,
    completion_content,
    load_json,
    output_contract,
    validate_content,
)
from workbench.settings import ROOT, ModelProfile, Settings


def profile(provider="openai", model="gpt-4o-mini", **kwargs):
    return ModelProfile(
        stage="requirements",
        base_url=f"https://api.{provider}.com/v1",
        api_key=SecretStr("offline-test-key"),
        model=model,
        **kwargs,
    )


def envelope(content=None, finish="stop", **message_fields):
    return {
        "choices": [
            {
                "finish_reason": finish,
                "message": {
                    "role": "assistant",
                    "content": content,
                    **message_fields,
                },
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
    }


def gateway(store, responses, *, provider="openai", model="gpt-4o-mini"):
    store.settings.base_url = f"https://api.{provider}.com/v1"
    store.settings.model = model
    store.settings.api_key = SecretStr("offline-test-key")
    seen = []

    def handle(request):
        seen.append(json.loads(request.content))
        response = responses[min(len(seen) - 1, len(responses) - 1)]
        if isinstance(response, httpx.Response):
            return response
        return httpx.Response(200, json=response)

    return ModelGateway(store.settings, store, httpx.MockTransport(handle)), seen


@pytest.mark.parametrize(
    "provider,model,token_field",
    [
        ("deepseek", "deepseek-flash", "max_tokens"),
        ("deepseek", "deepseek-v4-pro", "max_tokens"),
        ("openai", "gpt-4o-mini", "max_completion_tokens"),
        ("openai", "gpt-4.1-mini", "max_completion_tokens"),
        ("openai", "gpt-5.4", "max_completion_tokens"),
        ("openai", "o3", "max_completion_tokens"),
        ("openai", "unreviewed-model-no-substitution", "max_completion_tokens"),
    ],
)
def test_official_wrappers_own_structured_request_without_model_tables(
    store, monkeypatch, provider, model, token_field
):
    from langchain_deepseek import ChatDeepSeek
    from langchain_openai import ChatOpenAI

    cls = ChatDeepSeek if provider == "deepseek" else ChatOpenAI
    original = cls.with_structured_output
    wrappers = []

    def wrapped(self, schema, **kwargs):
        wrappers.append((schema, kwargs))
        return original(self, schema, **kwargs)

    monkeypatch.setattr(cls, "with_structured_output", wrapped)
    model_gateway, seen = gateway(
        store,
        [envelope(ModelReview(summary="ok").model_dump_json())],
        provider=provider,
        model=model,
    )
    result = model_gateway.complete(new_run(store), "review:1", "Return JSON", {}, ModelReview)
    assert result.summary == "ok"
    assert wrappers == [(ModelReview, {"method": "json_mode", "include_raw": True})]
    assert seen[0]["response_format"] == {"type": "json_object"}
    assert seen[0]["model"] == model
    assert seen[0][token_field] == (65536 if provider == "deepseek" else 16384)
    assert "thinking" not in seen[0] and "temperature" not in seen[0]
    assert not seen[0]["stream"]
    assert "ModelReview" in seen[0]["messages"][0]["content"]
    if model == "o3":
        assert seen[0]["messages"][0]["role"] == "developer"  # Official SDK integration owns this.


@pytest.mark.parametrize("schema", [Requirement, Plan, Patches, ModelReview])
def test_same_json_mode_pipeline_preserves_every_domain_schema(schema):
    before = copy.deepcopy(schema.model_json_schema())
    for provider in ("openai", "deepseek"):
        contract = output_contract(profile(provider, model="user-selected-id"), schema)
        assert contract.mode == "json_object"
        assert contract.reason == "langchain_json_mode"
        assert contract.receipt()["structured_output"] == "langchain.with_structured_output"
    assert before == schema.model_json_schema()


@pytest.mark.parametrize("provider", ["openai", "deepseek"])
@pytest.mark.parametrize("schema", [Requirement, Plan, Patches, ModelReview])
def test_all_four_graph_stage_schemas_use_real_framework_parser(store, provider, schema):
    samples = {
        Requirement: requirement().model_dump_json(),
        Plan: (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"),
        Patches: json.dumps(
            {
                "explanation": "offline fixture",
                "patches": [
                    {
                        "path": "custom_rules.py",
                        "before_sha256": "0" * 64,
                        "content": "pass\n",
                    }
                ],
            }
        ),
        ModelReview: ModelReview(summary="offline review").model_dump_json(),
    }
    keys = {
        Requirement: "requirement:1",
        Plan: "plan:1",
        Patches: "coding:1",
        ModelReview: "review:1",
    }
    model, seen = gateway(
        store,
        [envelope(samples[schema])],
        provider=provider,
        model="deepseek-flash" if provider == "deepseek" else "gpt-4o-mini",
    )
    result = model.complete(new_run(store), keys[schema], "Return JSON", {}, schema)
    assert isinstance(result, schema)
    assert len(seen) == 1 and seen[0]["response_format"] == {"type": "json_object"}


def test_invalid_output_mode_fails_locally_without_request_or_budget(store):
    model, seen = gateway(store, [])
    store.settings.output_mode = "json_schema"  # Simulate invalid mutable app configuration.
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "requirement:1", "JSON", {}, Requirement)
    assert seen == [] and store.get_run(run)["model_calls"] == 0


def test_endpoint_detection_uses_exact_host_and_proxy_can_select_official_integration():
    fake = profile().model_copy(update={"base_url": "https://api.openai.com.example.test/v1"})
    contract = output_contract(fake, Requirement)
    assert contract.provider == "compatible" and contract.mode == "json_object"
    explicit = output_contract(fake.model_copy(update={"provider": "deepseek"}), Requirement)
    assert explicit.provider == "deepseek" and explicit.mode == "json_object"


def test_stage_provider_overrides_do_not_leak_on_endpoint_change():
    settings = Settings(
        base_url="https://proxy.example/v1",
        api_key="default-key",
        model="gpt-4o-mini",
        provider="openai",
        output_mode="json_object",
        max_output_tokens=8192,
        planning_base_url="https://api.deepseek.com",
        planning_api_key="planning-key",
        planning_model="deepseek-flash",
        _env_file=None,
    )
    assert settings.model_for("requirements").provider == "openai"
    planning = settings.model_for("planning")
    assert (planning.provider, planning.output_mode, planning.max_output_tokens) == (
        "auto",
        "auto",
        None,
    )
    assert output_contract(planning, Plan).provider == "deepseek"
    settings.planning_max_output_tokens = 4096
    assert (
        output_contract(settings.model_for("planning"), Plan).request_fields["max_output_tokens"]
        == 4096
    )


def test_actual_request_receipt_cache_and_capability_changes(store):
    response = envelope(requirement().model_dump_json())
    model, seen = gateway(store, [response])
    run = new_run(store)
    first = model.complete(run, "requirement:1", "Preserve confirmed facts", {}, Requirement)
    assert (
        model.complete(run, "requirement:1", "Preserve confirmed facts", {}, Requirement) == first
    )
    assert len(seen) == 1
    assert seen[0]["response_format"] == {"type": "json_object"}
    assert "JSON" in seen[0]["messages"][0]["content"]
    receipt = store.model_records(run)[0]
    assert receipt["provider"] == "openai"
    assert receipt["output_mode"] == "json_object"
    assert receipt["contract_version"] == 2 and receipt["finish_reason"] == "stop"
    assert "offline-test-key" not in json.dumps(receipt)
    store.settings.max_output_tokens = 4096
    model.complete(run, "requirement:1", "Preserve confirmed facts", {}, Requirement)
    assert len(seen) == 2  # Capability/token-budget changes cannot reuse stale cached answers.


def test_legacy_records_stay_identifiable_but_cannot_satisfy_new_framework_cache(store):
    model, seen = gateway(store, [envelope(requirement().model_dump_json())])
    run = new_run(store)
    store.step(
        run,
        "model:requirements:legacy",
        lambda: {
            "value": requirement().model_dump(),
            "stage": "requirements",
            "model": "gpt-4o-mini",
            "usage": {},
        },
    )
    model.complete(run, "requirement:1", "Return JSON", {}, Requirement)
    records = store.model_records(run)
    assert len(seen) == 1
    assert [row["status"] for row in records] == ["legacy", "validated"]
    assert [row["contract_version"] for row in records] == [0, 2]


@pytest.mark.parametrize(
    "finish,extra,match",
    [
        ("stop", {"refusal": "sensitive provider text"}, "拒绝"),
        ("length", {}, "截断"),
        ("content_filter", {}, "过滤"),
        ("tool_calls", {}, "工具调用"),
        ("stop", {"tool_calls": [{"id": "unexpected"}]}, "工具调用"),
    ],
)
def test_terminal_status_never_accepts_otherwise_valid_json_or_repairs(store, finish, extra, match):
    model, seen = gateway(store, [envelope(requirement().model_dump_json(), finish, **extra)])
    run = new_run(store)
    with pytest.raises(ModelFailure, match=match) as error:
        model.complete(run, "requirement:1", "JSON", {}, Requirement)
    assert "sensitive provider text" not in str(error.value)
    assert len(seen) == store.get_run(run)["model_calls"] == 1
    records = store.model_records(run)
    assert len(records) == 1 and records[0]["status"] == "failed"
    assert records[0]["code"] in {"refusal", "truncated", "content_filter", "unexpected_tool_call"}
    assert records[0]["contract_version"] == 2
    assert records[0]["output_mode"] == "json_object"
    assert "sensitive provider text" not in json.dumps(records, default=str)
    assert "offline-test-key" not in json.dumps(records, default=str)


@pytest.mark.parametrize(
    "bad",
    [
        {},
        {"choices": []},
        {"choices": "invalid"},
        {"choices": [None]},
        envelope("{}", finish=None),
        envelope("{}", finish="unknown"),
        envelope("{}", finish="aborted"),
        envelope("{}", finish="insufficient_system_resource"),
        envelope("", reasoning_content="must never become the answer"),
    ],
)
def test_malformed_or_interrupted_envelopes_are_bounded_and_not_success(store, bad):
    model, seen = gateway(store, [bad])
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "requirement:1", "JSON", {}, Requirement)
    assert len(seen) == 2
    assert all(record["status"] == "failed" for record in store.model_records(run))


def test_empty_deepseek_content_can_repair_once_without_using_reasoning(store):
    model, seen = gateway(
        store,
        [
            envelope(None, reasoning_content="private reasoning must not be retried"),
            envelope(requirement().model_dump_json()),
        ],
        provider="deepseek",
        model="deepseek-flash",
    )
    model.complete(new_run(store), "requirement:1", "JSON", {}, Requirement)
    assert len(seen) == 2
    assert "private reasoning" not in json.dumps(seen[1])
    assert seen[1]["response_format"] == {"type": "json_object"}


def test_typed_validation_rejects_coercion_and_repairs_exact_field_without_changing_schema(store):
    good = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(good)
    bad["entities"][0]["fields"][0]["required"] = "true"
    model, seen = gateway(store, [envelope(json.dumps(bad)), envelope(json.dumps(good))])
    result = model.complete(new_run(store), "plan:1", "Preserve approved requirements", {}, Plan)
    assert result.business is not None and len(seen) == 2
    assert "bool_type" in seen[1]["messages"][-1]["content"]
    assert "required" in seen[1]["messages"][-1]["content"]
    assert seen[0]["response_format"] == seen[1]["response_format"]


@pytest.mark.parametrize(
    "content",
    [
        '{"summary":"first","summary":"second"}',
        '{"value":NaN}',
        '{"value":Infinity}',
        '{"value":1e999}',
        "[]",
        '```json\n{"summary":"example","observations":[],"uncovered_requirements":[]}\n```',
    ],
)
def test_json_mode_rejects_duplicate_nonfinite_nonobject_and_fenced_content(content):
    with pytest.raises(ValueError):
        validate_content(content, ModelReview, mode="json_object")


def test_lenient_framework_parser_cannot_hide_incomplete_raw_json(store):
    raw = ModelReview(summary="test").model_dump_json()[:-1]
    model, seen = gateway(store, [envelope(raw)])
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "review:1", "Return JSON", {}, ModelReview)
    assert len(seen) == 2
    assert all(row["status"] == "failed" for row in store.model_records(run))


def test_dynamic_facts_and_choice_labels_are_preserved_in_json_mode():
    facts = requirement().model_dump()
    facts["facts"] = {"label": "用户原话", "nested": {"enabled": True, "values": [1, None]}}
    assert (
        validate_content(json.dumps(facts), Requirement, mode="json_object").facts == facts["facts"]
    )
    data = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    field = next(f for e in data["entities"] for f in e["fields"] if f["kind"] == "enum")
    field["choice_labels"] = {field["choices"][0]: "原始标签"}
    validated = validate_content(json.dumps(data), Plan, mode="json_object")
    assert any(f.choice_labels for e in validated.entities for f in e.fields)


def test_business_validator_is_still_required_after_valid_provider_json():
    data = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    field = next(f for e in data["entities"] for f in e["fields"] if f["kind"] == "datetime")
    field["date_range"] = True
    with pytest.raises(ValueError, match="日期范围只支持 date 类型"):
        validate_content(json.dumps(data), Plan, mode="json_object")


def test_usage_is_sanitized_and_duplicate_envelopes_or_malformed_refusals_fail():
    content = ModelReview(summary="test").model_dump_json()
    result = envelope(content)
    result["usage"] = {
        "prompt_tokens": True,
        "completion_tokens": -1,
        "total_tokens": "provider-secret",
        "extra": "provider-secret",
    }
    contract = OutputContract("openai", "json_object", "langchain_json_mode", {})
    assert completion_content(result, contract)[1] == {}
    with pytest.raises(ValueError, match="duplicate_json_key"):
        load_json('{"choices":[],"choices":[]}')
    with pytest.raises(OutputFailure, match="拒绝"):
        completion_content(envelope(content, refusal={"unexpected": "data"}), contract)


@pytest.mark.parametrize(
    "status,expected_calls", [(400, 1), (401, 1), (403, 1), (404, 1), (429, 2), (500, 2)]
)
def test_http_error_retry_budget_never_downgrades_output_format(store, status, expected_calls):
    model, seen = gateway(store, [httpx.Response(status, text="raw-provider-secret")])
    with pytest.raises(ModelFailure) as error:
        model.complete(new_run(store), "review:1", "JSON", {}, ModelReview)
    assert len(seen) == expected_calls
    assert "raw-provider-secret" not in str(error.value)
    assert all(call["response_format"]["type"] == "json_object" for call in seen)


def test_full_context_and_repair_are_bounded_before_an_extra_model_call(store):
    model, seen = gateway(store, [envelope(requirement().model_dump_json())])
    store.settings.max_context_chars = 10000
    run = new_run(store)
    with pytest.raises(ModelFailure, match="MAX_CONTEXT_CHARS"):
        model.complete(run, "requirement:1", "x" * 10000, {}, Requirement)
    assert seen == [] and store.get_run(run)["model_calls"] == 0


@pytest.mark.parametrize("inside_event_loop", [False, True])
@pytest.mark.parametrize("http_status", [200, 401])
def test_injected_async_clients_are_closed_on_success_failure_and_existing_event_loop(
    store, monkeypatch, inside_event_loop, http_status
):
    import workbench.model_protocol as protocol

    actual_async = httpx.AsyncClient
    clients = []

    class TrackedAsync(actual_async):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            clients.append(self)

    monkeypatch.setattr(protocol.httpx, "AsyncClient", TrackedAsync)
    response = (
        envelope(requirement().model_dump_json()) if http_status == 200 else httpx.Response(401)
    )
    model, seen = gateway(store, [response])

    def call():
        if http_status == 200:
            model.complete(new_run(store), "requirement:1", "JSON", {}, Requirement)
        else:
            with pytest.raises(ModelFailure):
                model.complete(new_run(store), "requirement:1", "JSON", {}, Requirement)

    async def call_inside_loop():
        call()

    if inside_event_loop:
        asyncio.run(call_inside_loop())
    else:
        call()
    assert len(seen) == 1 and clients
    assert all(client.is_closed for client in clients)
````
