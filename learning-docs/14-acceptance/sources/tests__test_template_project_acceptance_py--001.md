# tests/test_template_project_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_template_projects`、`scripts.template_acceptance_cases`、`scripts.template_acceptance_runtime`、`workbench.domain`、`workbench.generator`、`workbench.llm`、`workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture_plan`（L37–L52）：接收`case`。 源码说明：Test-only metadata for exercising the harness; the live controller cannot import it.。 控制顺序：L49按`data.get("business")`分支；L50遍历`[*data["business"]["roles"], *data["business"]["metrics"]]`。 调用`copy.deepcopy`、`data.update`、`fields.items`、`data["entities"].items`、`data.get`、`Plan.model_validate`。 返回路径：L52的`Plan.model_validate(data)`。
- `test_three_explicit_scales_and_independent_contracts`（L55–L70）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L57断言`[len(case.contract["entities"]) for case in cases] == [1, 3, 6]`；L58断言`[len(case.contract.get("business", {}).get("workflows", [])) for case in cases] == [ …`；L63断言`[len(case.contract.get("business", {}).get("roles", [])) for case in cases] == [0, 3,…`；L64遍历`cases`；L65断言`require_contract(case, fixture_plan(case).model_dump())`；L66断言`set(case.expected_checks) == {block["id"] for block in case.scenario}`；L67遍历`case.contract["entities"].items()`；L68断言`name in case.requirement`。后续分支沿下方源码相同行号继续阅读。 调用`suite_cases`、`len`、`case.contract.get("business", {}).get`、`case.contract.get`、`require_contract`、`fixture_plan(case).model_dump`、`fixture_plan`、`set`、`case.contract["entities"].items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_scenario_over_real_generated_http_and_restart`（L74–L84）：接收`tmp_path`、`index`。 控制顺序：L81断言`report["passed"] is True and report["restart"] is True`；L82断言`report["browser"]["real_browser"] is False`；L83断言`report["http_requests"] >= sum(len(block["requests"]) for block in case.scenario)`。 调用`suite_cases`、`generate_basic`、`fixture_plan`、`run_scenario`、`sum`、`len`、`require_scenario_checks`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_plan_cannot_drop_or_change_obligations`（L88–L103）：接收`mutation`。 控制顺序：L91按`mutation == "field"`分支；L93按`mutation == "entity"`分支；L95按`mutation == "permission"`分支；L98按`mutation == "query"`分支。 调用`suite_cases`、`fixture_plan(case).model_dump`、`fixture_plan`、`plan["entities"][0]["fields"].append`、`next`、`policy["actions"].append`、`plan["business"]["metrics"].pop`、`pytest.raises`、`require_contract`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_assertions_preserve_numbers_booleans_counts_and_row_identity`（L106–L126）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L108断言`resolve({"count": "${row.quantity}", "enabled": "${row.enabled}"}, refs) == { "count"…`；L112断言`resolve("/api/orders/${row.id}", refs) == "/api/orders/x"`；L119遍历`[ (True, {"equals": 1}), ([], {"contains": {"id": "x"}}), ([{"id"…`。 调用`resolve`、`check_json`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `github_env`（L129–L137）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L130的`{ "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_EVENT_NAME": "pull_re…`。
- `github_event`（L140–L148）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L141的`{ "action": "labeled", "label": {"name": "run-live-acceptance"}, "pull_request": { "head":…`。
- `test_explicit_label_and_manual_dispatch_bind_exact_head_and_allow_rerun`（L151–L155）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L153断言`trusted_event(env, event)["head_sha"] == "a" * 40`；L155断言`trusted_event(env, {})["event"] == "workflow_dispatch"`。 调用`github_env`、`github_event`、`trusted_event`、`env.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_scope_rejects_implicit_or_untrusted_events`（L161–L176）：接收`reason`。 控制顺序：L163按`reason == "fork"`分支；L165按`reason == "wrong_label"`分支；L167按`reason == "new_head"`分支；L169按`reason == "synchronize"`分支；L171按`reason == "pull_request_target"`分支。 调用`github_env`、`github_event`、`pytest.raises`、`trusted_event`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `configured_settings`（L179–L187）：接收`tmp_path`。 调用`acceptance_settings`。 返回路径：L180的`acceptance_settings( { "BASE_URL": "https://model.invalid/v1", "MODE": "unit-only-model", …`。
- `test_live_suite_disables_optional_review_profile_as_well_as_flag`（L190–L194）：接收`tmp_path`。 控制顺序：L192断言`settings.model_review is False`；L193断言`settings.review_enabled is False`；L194断言`settings.max_model_calls == MAX_MODEL_CALLS`。 调用`configured_settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_events_keep_safe_structure_and_redact_before_bounding`（L197–L227）：接收`tmp_path`。 控制顺序：L224断言`retained[0]["attempt"] == 2`；L225断言`retained[0]["details"][0]["type"] == "enum"`；L226断言`"unit-only-key" not in json.dumps(retained)`；L227断言`"raw response" not in json.dumps(retained)`。 调用`configured_settings`、`SimpleNamespace`、`failure_events`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_survive_failed_provider_responses_without_their_values`（L230–L267）：接收`tmp_path`。 控制顺序：L259断言`response.status_code == 200`；L260断言`transport.receipts[0]["schema_valid"] is False`；L261断言`transport.receipts[0]["validation_code"] == "schema_validation"`；L262断言`"unit-only-key" not in json.dumps(transport.receipts)`；L263断言`any( item["path"] == ["entities"] for item in transport.receipts[0]["schema_diagnosti…`。 调用`configured_settings`、`BoundedTransport`、`transport.inner.close`、`json.dumps`、`httpx.MockTransport`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_analysis_counts_as_requirement_without_relabeling_wire_receipt`（L270–L285）：接收`tmp_path`、`monkeypatch`。 控制顺序：L280断言`transport.stage == "recommend"`；L281断言`gateway.traces == [ {"run_id": "unit-only", "stage": "requirement", "validated": True…`。 调用`configured_settings`、`BoundedTransport`、`ObservedGateway`、`monkeypatch.setattr`、`object`、`gateway.complete`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_bounds_actual_requests_before_dispatch`（L291–L323）：接收`tmp_path`、`case`。 控制顺序：L306按`case == "destination"`分支；L308按`case == "model"`分支；L310按`case == "token_budget"`分支；L312按`case == "call_budget"`分支；L314按`case == "authorization"`分支；L322断言`not calls`。 调用`BoundedTransport`、`configured_settings`、`transport.inner.close`、`httpx.MockTransport`、`calls.append`、`httpx.Response`、`pytest.raises`、`transport.handle_request`、`httpx.Request`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `success_receipts`（L326–L347）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Fabricated metadata for negative aggregate tests only; never written as evidence.。 调用`list`、`suite_cases`。 返回路径：L328的`[ { "case": case.identity, "source_digest": case.source_digest, "passed": True, "ready": T…`。
- `test_all_three_must_pass_with_real_calls_and_complete_evidence`（L364–L385）：接收`reason`。 控制顺序：L366断言`aggregate(suite_cases(), results)`；L367按`reason == "missing"`分支；L369按`reason == "duplicate"`分支；L371按`reason == "failure"`分支；L373按`reason == "wrong_source"`分支；L375按`reason == "no_browser"`分支；L377按`reason == "missing_check"`分支；L379按`reason == "no_model_plan"`分支。后续分支沿下方源码相同行号继续阅读。 调用`success_receipts`、`aggregate`、`suite_cases`、`results.pop`、`copy.deepcopy`、`results[2]["scenario"]["checks"].pop`、`results[2].update`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_uses_rnd_key_without_automatic_cost_trigger`（L388–L402）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L393断言`set(events) == {"workflow_dispatch", "pull_request"}`；L394断言`events["pull_request"]["types"] == ["labeled"]`；L396断言`job["environment"] == "rnd"`；L397断言`"run-live-acceptance" in job["if"]`；L398断言`"head.repo.full_name == github.repository" in job["if"]`；L400断言`len(secret_steps) == 1`；L401断言`secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"`；L402断言`secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"`。 调用`Path(__file__).resolve`、`Path`、`(root / ".github/workflows/template-project-acceptance.yml").read…`、`yaml.safe_load`、`workflow.get`、`set`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_template_project_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L402。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14756`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_template_project_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e42496bb05088d2f6ee1c36f93388421675924fb64cacc6f70805c4992b9fd35"} -->
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
