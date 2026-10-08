# tests/test_template_project_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_template_projects`、`scripts.template_acceptance_cases`、`scripts.template_acceptance_runtime`、`workbench.domain`、`workbench.generator`、`workbench.llm`、`workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture_plan`（L38–L53）：接收`case`。 源码说明：Test-only metadata for exercising the harness; the live controller cannot import it.。 控制顺序：L50按`data.get("business")`分支；L51遍历`[*data["business"]["roles"], *data["business"]["metrics"]]`。 调用`copy.deepcopy`、`data.update`、`fields.items`、`data["entities"].items`、`data.get`、`Plan.model_validate`。 返回路径：L53的`Plan.model_validate(data)`。
- `test_three_explicit_scales_and_independent_contracts`（L56–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L58断言`[len(case.contract["entities"]) for case in cases] == [1, 3, 6]`；L59断言`[len(case.contract.get("business", {}).get("workflows", [])) for case in cases] == [ …`；L64断言`[len(case.contract.get("business", {}).get("roles", [])) for case in cases] == [0, 3,…`；L65遍历`cases`；L66断言`require_contract(case, fixture_plan(case).model_dump())`；L67断言`set(case.expected_checks) == {block["id"] for block in case.scenario}`；L68遍历`case.contract["entities"].items()`；L69断言`name in case.requirement`。后续分支沿下方源码相同行号继续阅读。 调用`suite_cases`、`len`、`case.contract.get("business", {}).get`、`case.contract.get`、`require_contract`、`fixture_plan(case).model_dump`、`fixture_plan`、`set`、`case.contract["entities"].items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_scenario_over_real_generated_http_and_restart`（L75–L85）：接收`tmp_path`、`index`。 控制顺序：L82断言`report["passed"] is True and report["restart"] is True`；L83断言`report["browser"]["real_browser"] is False`；L84断言`report["http_requests"] >= sum(len(block["requests"]) for block in case.scenario)`。 调用`suite_cases`、`generate_basic`、`fixture_plan`、`run_scenario`、`sum`、`len`、`require_scenario_checks`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_plan_cannot_drop_or_change_obligations`（L89–L104）：接收`mutation`。 控制顺序：L92按`mutation == "field"`分支；L94按`mutation == "entity"`分支；L96按`mutation == "permission"`分支；L99按`mutation == "query"`分支。 调用`suite_cases`、`fixture_plan(case).model_dump`、`fixture_plan`、`plan["entities"][0]["fields"].append`、`next`、`policy["actions"].append`、`plan["business"]["metrics"].pop`、`pytest.raises`、`require_contract`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_assertions_preserve_numbers_booleans_counts_and_row_identity`（L107–L127）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L109断言`resolve({"count": "${row.quantity}", "enabled": "${row.enabled}"}, refs) == { "count"…`；L113断言`resolve("/api/orders/${row.id}", refs) == "/api/orders/x"`；L120遍历`[ (True, {"equals": 1}), ([], {"contains": {"id": "x"}}), ([{"id"…`。 调用`resolve`、`check_json`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `github_env`（L130–L138）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L131的`{ "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_EVENT_NAME": "pull_re…`。
- `github_event`（L141–L149）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L142的`{ "action": "labeled", "label": {"name": "run-live-acceptance"}, "pull_request": { "head":…`。
- `test_explicit_label_and_manual_dispatch_bind_exact_head_and_allow_rerun`（L152–L156）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L154断言`trusted_event(env, event)["head_sha"] == "a" * 40`；L156断言`trusted_event(env, {})["event"] == "workflow_dispatch"`。 调用`github_env`、`github_event`、`trusted_event`、`env.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_scope_rejects_implicit_or_untrusted_events`（L162–L177）：接收`reason`。 控制顺序：L164按`reason == "fork"`分支；L166按`reason == "wrong_label"`分支；L168按`reason == "new_head"`分支；L170按`reason == "synchronize"`分支；L172按`reason == "pull_request_target"`分支。 调用`github_env`、`github_event`、`pytest.raises`、`trusted_event`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `configured_settings`（L180–L188）：接收`tmp_path`。 调用`acceptance_settings`。 返回路径：L181的`acceptance_settings( { "BASE_URL": "https://model.invalid/v1", "MODE": "unit-only-model", …`。
- `test_live_suite_disables_optional_review_profile_as_well_as_flag`（L191–L195）：接收`tmp_path`。 控制顺序：L193断言`settings.model_review is False`；L194断言`settings.review_enabled is False`；L195断言`settings.max_model_calls == MAX_MODEL_CALLS`。 调用`configured_settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_events_keep_safe_structure_and_redact_before_bounding`（L198–L228）：接收`tmp_path`。 控制顺序：L225断言`retained[0]["attempt"] == 2`；L226断言`retained[0]["details"][0]["type"] == "enum"`；L227断言`"unit-only-key" not in json.dumps(retained)`；L228断言`"raw response" not in json.dumps(retained)`。 调用`configured_settings`、`SimpleNamespace`、`failure_events`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_survive_failed_provider_responses_without_their_values`（L231–L268）：接收`tmp_path`。 控制顺序：L260断言`response.status_code == 200`；L261断言`transport.receipts[0]["schema_valid"] is False`；L262断言`transport.receipts[0]["validation_code"] == "schema_validation"`；L263断言`"unit-only-key" not in json.dumps(transport.receipts)`；L264断言`any( item["path"] == ["entities"] for item in transport.receipts[0]["schema_diagnosti…`。 调用`configured_settings`、`BoundedTransport`、`transport.inner.close`、`json.dumps`、`httpx.MockTransport`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_provider_receipts_keep_only_static_categories_and_numbers`（L278–L313）：接收`tmp_path`、`content`、`category`。 控制顺序：L305断言`receipt["schema_valid"] is False`；L306断言`receipt["validation_code"] == "invalid_json"`；L308断言`detail["category"] == category`；L309断言`detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}`；L310断言`"message" not in detail`；L311断言`"unit-only-key" not in json.dumps(receipt)`。 调用`configured_settings`、`BoundedTransport`、`transport.inner.close`、`httpx.MockTransport`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`len`、`content.encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_receipt_metadata_rejects_text_booleans_and_unbounded_numbers`（L316–L329）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L328断言`details == [{"type": "json_syntax", "lengths": {"bytes": 37}}]`；L329断言`"private-" not in json.dumps(details)`。 调用`diagnostic_facts`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_analysis_counts_as_requirement_without_relabeling_wire_receipt`（L332–L347）：接收`tmp_path`、`monkeypatch`。 控制顺序：L342断言`transport.stage == "recommend"`；L343断言`gateway.traces == [ {"run_id": "unit-only", "stage": "requirement", "validated": True…`。 调用`configured_settings`、`BoundedTransport`、`ObservedGateway`、`monkeypatch.setattr`、`object`、`gateway.complete`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_bounds_actual_requests_before_dispatch`（L353–L385）：接收`tmp_path`、`case`。 控制顺序：L368按`case == "destination"`分支；L370按`case == "model"`分支；L372按`case == "token_budget"`分支；L374按`case == "call_budget"`分支；L376按`case == "authorization"`分支；L384断言`not calls`。 调用`BoundedTransport`、`configured_settings`、`transport.inner.close`、`httpx.MockTransport`、`calls.append`、`httpx.Response`、`pytest.raises`、`transport.handle_request`、`httpx.Request`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `success_receipts`（L388–L409）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Fabricated metadata for negative aggregate tests only; never written as evidence.。 调用`list`、`suite_cases`。 返回路径：L390的`[ { "case": case.identity, "source_digest": case.source_digest, "passed": True, "ready": T…`。
- `test_all_three_must_pass_with_real_calls_and_complete_evidence`（L426–L447）：接收`reason`。 控制顺序：L428断言`aggregate(suite_cases(), results)`；L429按`reason == "missing"`分支；L431按`reason == "duplicate"`分支；L433按`reason == "failure"`分支；L435按`reason == "wrong_source"`分支；L437按`reason == "no_browser"`分支；L439按`reason == "missing_check"`分支；L441按`reason == "no_model_plan"`分支。后续分支沿下方源码相同行号继续阅读。 调用`success_receipts`、`aggregate`、`suite_cases`、`results.pop`、`copy.deepcopy`、`results[2]["scenario"]["checks"].pop`、`results[2].update`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_uses_rnd_key_without_automatic_cost_trigger`（L450–L464）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L455断言`set(events) == {"workflow_dispatch", "pull_request"}`；L456断言`events["pull_request"]["types"] == ["labeled"]`；L458断言`job["environment"] == "rnd"`；L459断言`"run-live-acceptance" in job["if"]`；L460断言`"head.repo.full_name == github.repository" in job["if"]`；L462断言`len(secret_steps) == 1`；L463断言`secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"`；L464断言`secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"`。 调用`Path(__file__).resolve`、`Path`、`(root / ".github/workflows/template-project-acceptance.yml").read…`、`yaml.safe_load`、`workflow.get`、`set`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_template_project_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L464。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17072`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_template_project_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "087b557835526f0ec8cc31d6d30ab2ed9d9456cbc6aa9795c711ea857cb43e0a"} -->
````python
# tests/test_template_project_acceptance.py
"""Harness integrity and synthetic HTTP checks. None of these are live-model evidence."""

import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml

from scripts.ci_template_projects import (
    MAX_MODEL_CALLS,
    MAX_OUTPUT_TOKENS,
    REPOSITORY,
    BoundedTransport,
    ObservedGateway,
    acceptance_settings,
    aggregate,
    diagnostic_facts,
    failure_events,
    trusted_event,
)
from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require_contract,
    require_scenario_checks,
    suite_cases,
)
from scripts.template_acceptance_runtime import check_json, resolve, run_scenario
from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.llm import ModelGateway
from workbench.model_protocol import OutputFailure


def fixture_plan(case):
    """Test-only metadata for exercising the harness; the live controller cannot import it."""
    data = copy.deepcopy(case.contract)
    data.update(title=case.title, acceptance=["Synthetic offline harness validation only"])
    data["entities"] = [
        {
            "name": entity,
            "description": entity,
            "fields": [{"name": name, **field} for name, field in fields.items()],
        }
        for entity, fields in data["entities"].items()
    ]
    if data.get("business"):
        for item in [*data["business"]["roles"], *data["business"]["metrics"]]:
            item["label"] = item["name"]
    return Plan.model_validate(data)


def test_three_explicit_scales_and_independent_contracts():
    cases = suite_cases()
    assert [len(case.contract["entities"]) for case in cases] == [1, 3, 6]
    assert [len(case.contract.get("business", {}).get("workflows", [])) for case in cases] == [
        0,
        1,
        4,
    ]
    assert [len(case.contract.get("business", {}).get("roles", [])) for case in cases] == [0, 3, 4]
    for case in cases:
        assert require_contract(case, fixture_plan(case).model_dump())
        assert set(case.expected_checks) == {block["id"] for block in case.scenario}
        for name, fields in case.contract["entities"].items():
            assert name in case.requirement
            assert all(field in case.requirement for field in fields)
        assert len(case.source_digest) == 64


@pytest.mark.parametrize("index", [0, 1, 2])
def test_each_scenario_over_real_generated_http_and_restart(tmp_path, index):
    case = suite_cases()[index]
    product = tmp_path / "product"
    generate_basic(fixture_plan(case), product)
    report = run_scenario(
        case, product, sys.executable, tmp_path / "scenario", tmp_path / "screens", browser=False
    )
    assert report["passed"] is True and report["restart"] is True
    assert report["browser"]["real_browser"] is False
    assert report["http_requests"] >= sum(len(block["requests"]) for block in case.scenario)
    require_scenario_checks(case, report["checks"])


@pytest.mark.parametrize("mutation", ["field", "entity", "permission", "metric", "query"])
def test_model_plan_cannot_drop_or_change_obligations(mutation):
    case = suite_cases()[2]
    plan = fixture_plan(case).model_dump()
    if mutation == "field":
        plan["entities"][0]["fields"][0]["max_length"] = 300
    elif mutation == "entity":
        plan["entities"][0]["fields"].append({"name": "unrequested", "kind": "text"})
    elif mutation == "permission":
        policy = next(p for p in plan["business"]["permissions"] if p["role"] == "auditor")
        policy["actions"].append("update")
    elif mutation == "query":
        plan["entities"][1]["fields"][2]["searchable"] = True
    else:
        plan["business"]["metrics"].pop()
    with pytest.raises(AcceptanceFailure, match="contract_mismatch"):
        require_contract(case, plan)


def test_json_assertions_preserve_numbers_booleans_counts_and_row_identity():
    refs = {"row": {"id": "x", "quantity": 12, "enabled": False}}
    assert resolve({"count": "${row.quantity}", "enabled": "${row.enabled}"}, refs) == {
        "count": 12,
        "enabled": False,
    }
    assert resolve("/api/orders/${row.id}", refs) == "/api/orders/x"
    check_json([{"id": "x"}], {"ids": ["x"]}, "unit-only")
    check_json(
        [{"name": "metric", "value": 5}],
        {"where": {"name": "metric"}, "one": True, "path": ["value"], "gte": 0},
        "unit-only",
    )
    for value, assertion in [
        (True, {"equals": 1}),
        ([], {"contains": {"id": "x"}}),
        ([{"id": "y"}], {"ids": ["x"]}),
        ([{"id": "x"}], {"count": 0}),
    ]:
        with pytest.raises(AcceptanceFailure):
            check_json(value, assertion, "unit-only")


def github_env():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_EVENT_NAME": "pull_request",
        "ACCEPTANCE_HEAD_SHA": "a" * 40,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "2",
    }


def github_event():
    return {
        "action": "labeled",
        "label": {"name": "run-live-acceptance"},
        "pull_request": {
            "head": {"sha": "a" * 40, "repo": {"full_name": REPOSITORY}},
            "base": {"repo": {"full_name": REPOSITORY}},
        },
    }


def test_explicit_label_and_manual_dispatch_bind_exact_head_and_allow_rerun():
    env, event = github_env(), github_event()
    assert trusted_event(env, event)["head_sha"] == "a" * 40
    env.update(GITHUB_EVENT_NAME="workflow_dispatch", GITHUB_SHA="a" * 40)
    assert trusted_event(env, {})["event"] == "workflow_dispatch"


@pytest.mark.parametrize(
    "reason", ["fork", "wrong_label", "new_head", "synchronize", "pull_request_target", "local"]
)
def test_secret_scope_rejects_implicit_or_untrusted_events(reason):
    env, event = github_env(), github_event()
    if reason == "fork":
        event["pull_request"]["head"]["repo"]["full_name"] = "outside/fork"
    elif reason == "wrong_label":
        event["label"]["name"] = "bug"
    elif reason == "new_head":
        event["pull_request"]["head"]["sha"] = "b" * 40
    elif reason == "synchronize":
        event["action"] = "synchronize"
    elif reason == "pull_request_target":
        env["GITHUB_EVENT_NAME"] = reason
    else:
        env["GITHUB_ACTIONS"] = "false"
    with pytest.raises(AcceptanceFailure):
        trusted_event(env, event)


def configured_settings(tmp_path):
    return acceptance_settings(
        {
            "BASE_URL": "https://model.invalid/v1",
            "MODE": "unit-only-model",
            "API_KEY": "unit-only-key",
        },
        tmp_path,
    )


def test_live_suite_disables_optional_review_profile_as_well_as_flag(tmp_path):
    settings = configured_settings(tmp_path)
    assert settings.model_review is False
    assert settings.review_enabled is False
    assert settings.max_model_calls == MAX_MODEL_CALLS


def test_failure_events_keep_safe_structure_and_redact_before_bounding(tmp_path):
    settings = configured_settings(tmp_path)
    events = [
        {
            "id": 1,
            "kind": "assistant_failed",
            "data": {
                "stage": "planning",
                "code": "schema_validation",
                "response_id": "a" * 32,
                "content": "raw response must not be retained",
                "diagnostic": {
                    "attempt": 2,
                    "details": [
                        {
                            "type": "enum",
                            "path": ["unit-only-key"],
                            "constraints": {"enum": ["unit-only-key"]},
                            "message": "raw response must not be retained",
                        }
                    ],
                },
            },
        }
    ]
    store = SimpleNamespace(events=lambda run_id, after=0: events if after == 0 else [])
    retained = failure_events(store, "unit-only", settings)
    assert retained[0]["attempt"] == 2
    assert retained[0]["details"][0]["type"] == "enum"
    assert "unit-only-key" not in json.dumps(retained)
    assert "raw response" not in json.dumps(retained)


def test_schema_diagnostics_survive_failed_provider_responses_without_their_values(tmp_path):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    transport.inner.close()
    # Malformed content includes a secret-like value: only schema-owned paths survive.
    raw = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps({"title": "unit-only-key"})},
            }
        ],
        "usage": {"total_tokens": 7},
    }
    transport.inner = httpx.MockTransport(lambda request: httpx.Response(200, json=raw))
    transport.run_id, transport.stage, transport.schema = "unit-only", "plan", Plan
    try:
        response = transport.handle_request(
            httpx.Request(
                "POST",
                "https://model.invalid/v1/chat/completions",
                headers={"Authorization": "Bearer unit-only-key"},
                json={
                    "model": "unit-only-model",
                    "response_format": {"type": "json_object"},
                    "max_tokens": MAX_OUTPUT_TOKENS,
                },
            )
        )
        assert response.status_code == 200
        assert transport.receipts[0]["schema_valid"] is False
        assert transport.receipts[0]["validation_code"] == "schema_validation"
        assert "unit-only-key" not in json.dumps(transport.receipts)
        assert any(
            item["path"] == ["entities"] for item in transport.receipts[0]["schema_diagnostics"]
        )
    finally:
        transport.shutdown()


@pytest.mark.parametrize(
    "content,category",
    [
        ('{\n "title": "unit-only-key",\n "entities": ]}', "expected_value"),
        ('{"unit-only-key":1,"unit-only-key":2}', "duplicate_json_key"),
    ],
)
def test_json_provider_receipts_keep_only_static_categories_and_numbers(
    tmp_path, content, category
):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    transport.inner.close()
    transport.inner = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
        )
    )
    transport.run_id, transport.stage, transport.schema = "unit-only", "plan", Plan
    try:
        transport.handle_request(
            httpx.Request(
                "POST",
                "https://model.invalid/v1/chat/completions",
                headers={"Authorization": "Bearer unit-only-key"},
                json={
                    "model": "unit-only-model",
                    "response_format": {"type": "json_object"},
                    "max_tokens": MAX_OUTPUT_TOKENS,
                },
            )
        )
        receipt = transport.receipts[0]
        assert receipt["schema_valid"] is False
        assert receipt["validation_code"] == "invalid_json"
        detail = receipt["json_diagnostics"][0]
        assert detail["category"] == category
        assert detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}
        assert "message" not in detail
        assert "unit-only-key" not in json.dumps(receipt)
    finally:
        transport.shutdown()


def test_json_receipt_metadata_rejects_text_booleans_and_unbounded_numbers():
    details = diagnostic_facts(
        [
            {
                "type": "json_syntax",
                "category": "private-category-canary",
                "position": {"line": "private-location-canary", "column": True, "offset": -1},
                "lengths": {"characters": 2_000_001, "bytes": 37, "raw": "private-value-canary"},
                "message": "private-message-canary",
            }
        ]
    )
    assert details == [{"type": "json_syntax", "lengths": {"bytes": 37}}]
    assert "private-" not in json.dumps(details)


def test_autonomous_analysis_counts_as_requirement_without_relabeling_wire_receipt(
    tmp_path, monkeypatch
):
    settings = configured_settings(tmp_path)
    transport = BoundedTransport(settings)
    gateway = ObservedGateway(settings, None, transport)
    # Test only the observation layer: there is no real-model receipt from this unit test.
    monkeypatch.setattr(ModelGateway, "complete", lambda *args, **kwargs: object())
    try:
        gateway.complete("unit-only", "recommend:1", "", {}, object)
        assert transport.stage == "recommend"
        assert gateway.traces == [
            {"run_id": "unit-only", "stage": "requirement", "validated": True}
        ]
    finally:
        transport.shutdown()


@pytest.mark.parametrize(
    "case", ["destination", "model", "token_budget", "call_budget", "authorization", "stream"]
)
def test_transport_bounds_actual_requests_before_dispatch(tmp_path, case):
    transport = BoundedTransport(configured_settings(tmp_path))
    transport.inner.close()
    calls = []
    transport.inner = httpx.MockTransport(
        lambda request: calls.append(request) or httpx.Response(200, json={})
    )
    transport.run_id, transport.stage = "unit-only", "plan"
    body = {
        "model": "unit-only-model",
        "response_format": {"type": "json_object"},
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "stream": False,
    }
    url, auth = "https://model.invalid/v1/chat/completions", "Bearer unit-only-key"
    if case == "destination":
        url = "https://outside.invalid/v1/chat/completions"
    elif case == "model":
        body["model"] = "different-model"
    elif case == "token_budget":
        body["max_completion_tokens"] += 1
    elif case == "call_budget":
        transport.calls["unit-only"] = MAX_MODEL_CALLS
    elif case == "authorization":
        auth = "wrong"
    else:
        body["stream"] = True
    with pytest.raises(OutputFailure):
        transport.handle_request(
            httpx.Request("POST", url, headers={"Authorization": auth}, json=body)
        )
    assert not calls
    transport.shutdown()


def success_receipts():
    """Fabricated metadata for negative aggregate tests only; never written as evidence."""
    return [
        {
            "case": case.identity,
            "source_digest": case.source_digest,
            "passed": True,
            "ready": True,
            "contract_preserved": True,
            "model_calls": 2,
            "provider_http_calls": 2,
            "completed_model_stages": ["requirement", "plan"],
            "cleanroom": {"passed": True, "real_browser": True},
            "scenario": {
                "passed": True,
                "restart": True,
                "checks": list(case.expected_checks),
                "browser": {"passed": True, "real_browser": True},
            },
        }
        for case in suite_cases()
    ]


@pytest.mark.parametrize(
    "reason",
    [
        "missing",
        "duplicate",
        "failure",
        "wrong_source",
        "no_browser",
        "missing_check",
        "no_model_plan",
        "fake_call_count",
        "over_budget",
    ],
)
def test_all_three_must_pass_with_real_calls_and_complete_evidence(reason):
    results = success_receipts()
    assert aggregate(suite_cases(), results)
    if reason == "missing":
        results.pop()
    elif reason == "duplicate":
        results[2] = copy.deepcopy(results[1])
    elif reason == "failure":
        results[2]["passed"] = False
    elif reason == "wrong_source":
        results[2]["source_digest"] = "f" * 64
    elif reason == "no_browser":
        results[2]["scenario"]["browser"]["real_browser"] = False
    elif reason == "missing_check":
        results[2]["scenario"]["checks"].pop()
    elif reason == "no_model_plan":
        results[2]["completed_model_stages"] = ["requirement"]
    elif reason == "fake_call_count":
        results[2]["provider_http_calls"] = 0
    else:
        results[2].update(model_calls=MAX_MODEL_CALLS + 1, provider_http_calls=MAX_MODEL_CALLS + 1)
    assert not aggregate(suite_cases(), results)


def test_workflow_uses_rnd_key_without_automatic_cost_trigger():
    root = Path(__file__).resolve().parents[1]
    raw = (root / ".github/workflows/template-project-acceptance.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(raw)
    events = workflow.get("on", workflow.get(True))
    assert set(events) == {"workflow_dispatch", "pull_request"}
    assert events["pull_request"]["types"] == ["labeled"]
    job = workflow["jobs"]["all-three-projects"]
    assert job["environment"] == "rnd"
    assert "run-live-acceptance" in job["if"]
    assert "head.repo.full_name == github.repository" in job["if"]
    secret_steps = [step for step in job["steps"] if "secrets." in json.dumps(step)]
    assert len(secret_steps) == 1
    assert secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"
    assert secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"
````
