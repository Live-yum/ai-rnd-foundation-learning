# tests/test_template_project_acceptance.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](tests__test_template_project_acceptance_py--002.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_template_projects`、`scripts.template_acceptance_cases`、`scripts.template_acceptance_runtime`、`workbench.business_capabilities`、`workbench.domain`、`workbench.generator`、`workbench.llm`、`workbench.model_protocol`、`workbench.requirement_coverage`、`workbench.requirement_sources`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture_plan`（L49–L64）：接收`case`。 源码说明：Test-only metadata for exercising the harness; the live controller cannot import it.。 控制顺序：L61按`data.get("business")`分支；L62遍历`[*data["business"]["roles"], *data["business"]["metrics"]]`。 调用`copy.deepcopy`、`data.update`、`fields.items`、`data["entities"].items`、`data.get`、`Plan.model_validate`。 返回路径：L64的`Plan.model_validate(data)`。
- `test_three_explicit_scales_and_independent_contracts`（L67–L82）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L69断言`[len(case.contract["entities"]) for case in cases] == [1, 3, 6]`；L70断言`[len(case.contract.get("business", {}).get("workflows", [])) for case in cases] == [ …`；L75断言`[len(case.contract.get("business", {}).get("roles", [])) for case in cases] == [0, 3,…`；L76遍历`cases`；L77断言`require_contract(case, fixture_plan(case).model_dump())`；L78断言`set(case.expected_checks) == {block["id"] for block in case.scenario}`；L79遍历`case.contract["entities"].items()`；L80断言`name in case.requirement`。后续分支沿下方源码相同行号继续阅读。 调用`suite_cases`、`len`、`case.contract.get("business", {}).get`、`case.contract.get`、`require_contract`、`fixture_plan(case).model_dump`、`fixture_plan`、`set`、`case.contract["entities"].items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_scenario_over_real_generated_http_and_restart`（L86–L96）：接收`tmp_path`、`index`。 控制顺序：L93断言`report["passed"] is True and report["restart"] is True`；L94断言`report["browser"]["real_browser"] is False`；L95断言`report["http_requests"] >= sum(len(block["requests"]) for block in case.scenario)`。 调用`suite_cases`、`generate_basic`、`fixture_plan`、`run_scenario`、`sum`、`len`、`require_scenario_checks`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_plan_cannot_drop_or_change_obligations`（L100–L115）：接收`mutation`。 控制顺序：L103按`mutation == "field"`分支；L105按`mutation == "entity"`分支；L107按`mutation == "permission"`分支；L110按`mutation == "query"`分支。 调用`suite_cases`、`fixture_plan(case).model_dump`、`fixture_plan`、`plan["entities"][0]["fields"].append`、`next`、`policy["actions"].append`、`plan["business"]["metrics"].pop`、`pytest.raises`、`require_contract`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contract_failure_identifies_the_exact_declared_field_attribute`（L130–L146）：接收`field`、`attribute`、`actual`、`expected`。 控制顺序：L140断言`caught.value.code == "contract_mismatch"`；L141断言`caught.value.path == f"books.{field}.{attribute}"`；L142断言`caught.value.contract_difference == { "attribute": attribute, "expected": expected, "…`。 调用`suite_cases`、`fixture_plan`、`next(item for item in plan.entities[0].fields if item.name == fie…`、`next`、`pytest.raises`、`require_contract`、`plan.model_dump`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contract_comparison_still_ignores_display_labels_and_enum_order`（L149–L156）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L153遍历`plan.entities[0].fields`；L156断言`require_contract(case, plan.model_dump())`。 调用`suite_cases`、`fixture_plan`、`field.choices.reverse`、`require_contract`、`plan.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contract_comparison_does_not_treat_missing_attributes_as_explicit_null`（L159–L170）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L165断言`caught.value.path == "books.title.pattern"`；L166断言`caught.value.contract_difference == { "attribute": "pattern", "expected": None, "actu…`。 调用`suite_cases`、`copy.deepcopy`、`pytest.raises`、`require_contract`、`replace`、`fixture_plan(case).model_dump`、`fixture_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_assertions_preserve_numbers_booleans_counts_and_row_identity`（L173–L193）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L175断言`resolve({"count": "${row.quantity}", "enabled": "${row.enabled}"}, refs) == { "count"…`；L179断言`resolve("/api/orders/${row.id}", refs) == "/api/orders/x"`；L186遍历`[ (True, {"equals": 1}), ([], {"contains": {"id": "x"}}), ([{"id"…`。 调用`resolve`、`check_json`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `github_env`（L196–L204）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L197的`{ "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_EVENT_NAME": "pull_re…`。
- `github_event`（L207–L215）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L208的`{ "action": "labeled", "label": {"name": "run-live-acceptance"}, "pull_request": { "head":…`。
- `test_explicit_label_and_manual_dispatch_bind_exact_head_and_allow_rerun`（L218–L222）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L220断言`trusted_event(env, event)["head_sha"] == "a" * 40`；L222断言`trusted_event(env, {})["event"] == "workflow_dispatch"`。 调用`github_env`、`github_event`、`trusted_event`、`env.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_scope_rejects_implicit_or_untrusted_events`（L228–L243）：接收`reason`。 控制顺序：L230按`reason == "fork"`分支；L232按`reason == "wrong_label"`分支；L234按`reason == "new_head"`分支；L236按`reason == "synchronize"`分支；L238按`reason == "pull_request_target"`分支。 调用`github_env`、`github_event`、`pytest.raises`、`trusted_event`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `configured_settings`（L246–L254）：接收`tmp_path`。 调用`acceptance_settings`。 返回路径：L247的`acceptance_settings( { "BASE_URL": "https://model.invalid/v1", "MODE": "unit-only-model", …`。
- `test_live_suite_disables_optional_review_profile_as_well_as_flag`（L257–L261）：接收`tmp_path`。 控制顺序：L259断言`settings.model_review is False`；L260断言`settings.review_enabled is False`；L261断言`settings.max_model_calls == MAX_MODEL_CALLS`。 调用`configured_settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_events_keep_safe_structure_and_redact_before_bounding`（L264–L294）：接收`tmp_path`。 控制顺序：L291断言`retained[0]["attempt"] == 2`；L292断言`retained[0]["details"][0]["type"] == "enum"`；L293断言`"unit-only-key" not in json.dumps(retained)`；L294断言`"raw response" not in json.dumps(retained)`。 调用`configured_settings`、`SimpleNamespace`、`failure_events`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_survive_failed_provider_responses_without_their_values`（L297–L334）：接收`tmp_path`。 控制顺序：L326断言`response.status_code == 200`；L327断言`transport.receipts[0]["schema_valid"] is False`；L328断言`transport.receipts[0]["validation_code"] == "schema_validation"`；L329断言`"unit-only-key" not in json.dumps(transport.receipts)`；L330断言`any( item["path"] == ["entities"] for item in transport.receipts[0]["schema_diagnosti…`。 调用`configured_settings`、`BoundedTransport`、`transport.inner.close`、`json.dumps`、`httpx.MockTransport`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_provider_receipts_keep_only_static_categories_and_numbers`（L344–L379）：接收`tmp_path`、`content`、`category`。 控制顺序：L371断言`receipt["schema_valid"] is False`；L372断言`receipt["validation_code"] == "invalid_json"`；L374断言`detail["category"] == category`；L375断言`detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}`；L376断言`"message" not in detail`；L377断言`"unit-only-key" not in json.dumps(receipt)`。 调用`configured_settings`、`BoundedTransport`、`transport.inner.close`、`httpx.MockTransport`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`len`、`content.encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_receipt_metadata_rejects_text_booleans_and_unbounded_numbers`（L382–L395）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L394断言`details == [{"type": "json_syntax", "lengths": {"bytes": 37}}]`；L395断言`"private-" not in json.dumps(details)`。 调用`diagnostic_facts`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_analysis_counts_as_requirement_without_relabeling_wire_receipt`（L398–L421）：接收`tmp_path`、`monkeypatch`。 控制顺序：L408断言`transport.stage == "recommend"`；L409断言`gateway.traces == [ { "run_id": "unit-only", "stage": "requirement", "logical_key": "…`。 调用`configured_settings`、`BoundedTransport`、`ObservedGateway`、`monkeypatch.setattr`、`object`、`gateway.complete`、`digest`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_preserves_design_feedback_before_terminal_json_failure`（L424–L539）：接收`tmp_path`。 控制顺序：L456断言`coverage and business`；L494断言`gateway.complete(run_id, "plan:1", "private-instruction-canary", payload, Plan) == ca…`；L499断言`gateway.complete(run_id, "plan:2", "private-instruction-canary", payload, Plan) == ca…`；L507断言`trace["omitted"] == 0`；L508断言`[item["logical_key"] for item in trace["items"]] == ["plan:1", "plan:2", "plan:3"]`；L509断言`[item["validated"] for item in trace["items"]] == [True, True, False]`；L511断言`last["payload_sha256"] == digest(payload)`；L512断言`last["previous_plan_sha256"] == digest(candidate.model_dump())`。后续分支沿下方源码相同行号继续阅读。 调用`suite_cases`、`fixture_plan(case).model_dump`、`fixture_plan`、`next`、`Requirement`、`copy.deepcopy`、`approved_grant["actions"].remove`、`Plan.model_validate`、`coverage_gaps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_preserves_design_feedback_before_terminal_json_failure.provider`（L473–L483）：接收`request`。 调用`sent.append`、`json.loads`、`len`、`candidate.model_dump_json`、`httpx.Response`。 返回路径：L476的`httpx.Response( 200, json={ "choices": [ {"finish_reason": "stop", "message": {"role": "as…`。
- `test_planning_diagnostic_projection_hides_unknown_keys_and_values_before_bounding`（L542–L656）：接收`tmp_path`。 控制顺序：L635断言`feedback == original`；L636断言`shown["business_diagnostics"][0]["source"]["path"] == "business.<key>.permissions.0"`；L637断言`shown["business_diagnostics"][0]["expected"] == diagnostic["expected"]`；L638断言`shown["business_diagnostics"][0]["actual"][0]["scope"] == "all"`；L639断言`shown["business_diagnostics"][1]["expected"] == {"enabled": True}`；L640断言`shown["business_diagnostics"][1]["actual"]["enabled"] is False`；L641断言`shown["coverage_diagnostics"][0]["actual"]["characters"] == len("[redacted]")`；L643断言`[record["origin"] for record in sources] == [ "previous_requirement", "user_input", "…`。后续分支沿下方源码相同行号继续阅读。 调用`configured_settings`、`copy.deepcopy`、`feedback_snapshot`、`feedback_vocabulary`、`suite_cases`、`len`、`json.dumps`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_retains_safe_analysis_feedback_when_recommendation_retry_fails`（L666–L765）：接收`tmp_path`、`action`、`code`。 控制顺序：L691断言`len(issues) == 1 and issues[0]["code"] == code`；L728断言`[r["logical_key"] for r in trace["items"]] == ["recommend:1", "recommend:2"]`；L730断言`last["validated"] is False`；L731断言`last["feedback_sha256"] == digest(feedback)`；L732断言`last["payload_sha256"] == digest(payload)`；L734断言`shown["stage"] == "clarification" and shown["round"] == 1`；L735断言`shown["analysis_diagnostics_count"] == 1`；L736断言`shown["analysis_diagnostics_omitted"] == 0`。后续分支沿下方源码相同行号继续阅读。 调用`Requirement`、`business_analysis_conflicts`、`len`、`analysis_feedback`、`configured_settings`、`Store`、`store.migrate`、`BoundedTransport`、`transport.inner.close`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_retains_safe_analysis_feedback_when_recommendation_retry_fails.provider`（L705–L715）：接收`request`。 调用`sent.append`、`json.loads`、`len`、`analysis.model_dump_json`、`httpx.Response`。 返回路径：L708的`httpx.Response( 200, json={ "choices": [ {"finish_reason": "stop", "message": {"role": "as…`。
- `test_planning_diagnostics_and_terminal_trace_have_explicit_byte_and_count_bounds`（L768–L860）：接收`tmp_path`、`monkeypatch`。 控制顺序：L801断言`len(json.dumps(bounded, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES`；L802断言`bounded["business_diagnostics_count"] == 13`；L803断言`bounded["business_diagnostics_omitted"] > 0`；L804断言`bounded["blocked_count"] == 100 and bounded["block_sources"] == { "business_coverage"…`；L807断言`"private" not in json.dumps(bounded)`；L835断言`len(json.dumps(analysis, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES`；L836断言`analysis["analysis_diagnostics_count"] == 13`；L837断言`analysis["analysis_diagnostics_omitted"] > 0`。后续分支沿下方源码相同行号继续阅读。 调用`configured_settings`、`feedback_vocabulary`、`suite_cases`、`range`、`".".join`、`feedback_snapshot`、`len`、`json.dumps(bounded, ensure_ascii=False).encode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text`（L864–L954）：接收`tmp_path`、`monkeypatch`、`capsys`、`failure_kind`。 控制顺序：L899按`failure_kind == "contract"`分支；L916断言`internal_errors == [error if failure_kind == "workflow" else None] * 3`；L917断言`report["passed"] is False and report["real_model"] is False`；L918断言`report["actual_model_calls"] == 0 and len(report["cases"]) == 3`；L919遍历`report["cases"]`；L920断言`receipt["passed"] is False`；L921按`failure_kind == "workflow"`分支；L922断言`receipt["workflow_status"] == "BLOCKED"`。后续分支沿下方源码相同行号继续阅读。 调用`configured_settings`、`monkeypatch.setattr`、`suite.run_suite`、`len`、`hashlib.sha256(error.encode()).hexdigest`、`hashlib.sha256`、`error.encode`、`json.dumps(difference).encode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_template_project_acceptance.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L872。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`33479`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_template_project_acceptance.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "949412fecda6bb1c95f1f6d973b689b26896a1b821b172ccc75792521ce8084e"} -->
````python
# tests/test_template_project_acceptance.py
"""Harness integrity and synthetic HTTP checks. None of these are live-model evidence."""

import copy
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml
from conftest import new_run

from scripts.ci_template_projects import (
    MAX_FEEDBACK_BYTES,
    MAX_MODEL_CALLS,
    MAX_OUTPUT_TOKENS,
    MAX_TRACE_BYTES,
    REPOSITORY,
    BoundedTransport,
    ObservedGateway,
    acceptance_settings,
    aggregate,
    diagnostic_facts,
    failure_events,
    feedback_snapshot,
    feedback_vocabulary,
    trusted_event,
)
from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require_contract,
    require_scenario_checks,
    suite_cases,
)
from scripts.template_acceptance_runtime import check_json, resolve, run_scenario
from workbench.business_capabilities import business_analysis_conflicts, business_gaps
from workbench.domain import Plan, Requirement, digest
from workbench.generator import generate_basic
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_protocol import OutputFailure
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_feedback
from workbench.store import Store


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


@pytest.mark.parametrize(
    "field,attribute,actual,expected",
    [
        ("started_on", "filterable", True, False),
        ("started_on", "date_range", False, True),
        ("started_on", "required", False, True),
        ("pages", "minimum", 2, 1),
        ("title", "max_length", 199, 200),
        ("author", "searchable", False, True),
        ("note", "kind", "boolean", "text"),
    ],
)
def test_contract_failure_identifies_the_exact_declared_field_attribute(
    field, attribute, actual, expected
):
    case = suite_cases()[0]
    plan = fixture_plan(case)
    next(item for item in plan.entities[0].fields if item.name == field).__setattr__(
        attribute, actual
    )
    with pytest.raises(AcceptanceFailure) as caught:
        require_contract(case, plan.model_dump())
    assert caught.value.code == "contract_mismatch"
    assert caught.value.path == f"books.{field}.{attribute}"
    assert caught.value.contract_difference == {
        "attribute": attribute,
        "expected": expected,
        "actual": actual,
    }


def test_contract_comparison_still_ignores_display_labels_and_enum_order():
    case = suite_cases()[0]
    plan = fixture_plan(case)
    plan.entities[0].description = "A model-authored display description"
    for field in plan.entities[0].fields:
        field.label = "A model-authored display label"
        field.choices.reverse()
    assert require_contract(case, plan.model_dump())


def test_contract_comparison_does_not_treat_missing_attributes_as_explicit_null():
    case = suite_cases()[0]
    contract = copy.deepcopy(case.contract)
    contract["entities"]["books"]["title"]["pattern"] = None
    with pytest.raises(AcceptanceFailure) as caught:
        require_contract(replace(case, contract=contract), fixture_plan(case).model_dump())
    assert caught.value.path == "books.title.pattern"
    assert caught.value.contract_difference == {
        "attribute": "pattern",
        "expected": None,
        "actual": {"type": "missing"},
    }


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
            {
                "run_id": "unit-only",
                "stage": "requirement",
                "logical_key": "recommend:1",
                "payload_sha256": digest({}),
                "feedback_sha256": digest({}),
                "resolution_feedback": {},
                "validated": True,
            }
        ]
    finally:
        transport.shutdown()


def test_real_gateway_preserves_design_feedback_before_terminal_json_failure(tmp_path):
    # Actual LangChain/ModelGateway/guard stack over an explicit mock HTTP provider;
    # these local receipts are never used as live-project acceptance evidence.
    case = suite_cases()[1]
    data = fixture_plan(case).model_dump()
    approved_grant = next(
        p
        for p in data["business"]["permissions"]
        if (p["role"], p["entity"]) == ("warehouse", "purchase_orders")
    )
    approved = Requirement(
        summary="Synthetic gateway diagnostic regression",
        users=["warehouse"],
        data_scope="shared",
        features=["Inventory"],
        acceptance=["Checks"],
        field_requirements=[{"entity": "items", "field": "stock", "minimum": 0}],
        facts={"business": {"permissions": [copy.deepcopy(approved_grant)]}},
    )
    approved_grant["actions"].remove("read_history")
    stock = next(
        f
        for e in data["entities"]
        if e["name"] == "items"
        for f in e["fields"]
        if f["name"] == "stock"
    )
    stock["minimum"] = -1
    candidate = Plan.model_validate(data)
    coverage, business = [], []
    reasons = coverage_gaps(approved, candidate, diagnostics=coverage)
    business_reasons = business_gaps(approved, candidate, diagnostics=business)
    assert coverage and business
    feedback = {
        "stage": "design",
        "round": 1,
        "blocked": reasons + business_reasons,
        "block_sources": ["requirement_coverage"] * len(reasons)
        + ["business_coverage"] * len(business_reasons),
        "coverage_diagnostics": coverage,
        "business_diagnostics": business,
    }
    settings = configured_settings(tmp_path)
    store = Store(settings)
    store.migrate()
    transport = BoundedTransport(settings)
    transport.inner.close()
    sent = []

    def provider(request):
        sent.append(json.loads(request.content))
        content = candidate.model_dump_json() if len(sent) <= 2 else '{"private-response-canary":]}'
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )

    transport.inner = httpx.MockTransport(provider)
    gateway = ObservedGateway(settings, store, transport, [case])
    run_id = new_run(store)
    payload = {
        "approved_requirement": approved.model_dump(),
        "resolution_feedback": {},
        "previous_plan": {},
    }
    try:
        assert (
            gateway.complete(run_id, "plan:1", "private-instruction-canary", payload, Plan)
            == candidate
        )
        payload.update(previous_plan=candidate.model_dump(), resolution_feedback=feedback)
        assert (
            gateway.complete(run_id, "plan:2", "private-instruction-canary", payload, Plan)
            == candidate
        )
        payload["resolution_feedback"] = {**feedback, "round": 2}
        with pytest.raises(ModelFailure):
            gateway.complete(run_id, "plan:3", "private-instruction-canary", payload, Plan)
        trace = gateway.receipt_trace(run_id)
        assert trace["omitted"] == 0
        assert [item["logical_key"] for item in trace["items"]] == ["plan:1", "plan:2", "plan:3"]
        assert [item["validated"] for item in trace["items"]] == [True, True, False]
        last = trace["items"][-1]
        assert last["payload_sha256"] == digest(payload)
        assert last["previous_plan_sha256"] == digest(candidate.model_dump())
        assert last["feedback_sha256"] == digest(payload["resolution_feedback"])
        assert trace["items"][1]["feedback_sha256"] != last["feedback_sha256"]
        shown = last["resolution_feedback"]
        assert shown["stage"] == "design" and shown["round"] == 2
        assert shown["block_sources"]["business_coverage"] == len(business_reasons)
        assert any(
            item.get("attribute") == "minimum" and item["expected"] == 0 and item["actual"] == -1
            for item in shown["coverage_diagnostics"]
        )
        assert any(
            item["source"]["domain"] == "permissions" for item in shown["business_diagnostics"]
        )
        assert [r["logical_key"] for r in transport.receipts] == [
            "plan:1",
            "plan:2",
            "plan:3",
            "plan:3",
        ]
        assert [r["schema_valid"] for r in transport.receipts] == [True, True, False, False]
        assert len(sent) == store.get_run(run_id)["model_calls"] == transport.calls[run_id] == 4
        assert json.loads(sent[2]["messages"][1]["content"]) == payload
        encoded = json.dumps(trace)
        assert "private-" not in encoded and "unit-only-key" not in encoded
        assert "blocked" not in shown and "previous_plan" not in last
    finally:
        transport.shutdown()
        store.engine.dispose()


def test_planning_diagnostic_projection_hides_unknown_keys_and_values_before_bounding(tmp_path):
    settings = configured_settings(tmp_path)
    secret = "unit-only-key"
    diagnostic = {
        "code": "business_scope_mismatch",
        "source": {
            "section": "facts",
            "domain": "permissions",
            "path": "business.private_identifier.permissions.0",
        },
        "expected": {
            "any_of": [
                [
                    {
                        "role": "technician",
                        "entity": "work_orders",
                        "action": "read_metrics",
                        "scope": "assigned",
                    }
                ]
            ]
        },
        "actual": [
            {
                "role": "technician",
                "entity": "work_orders",
                "actions": ["read", "read_metrics"],
                "scope": "all",
                "label": "private-label-canary",
                "api_key": secret,
                "content": "private-body-canary",
            }
        ],
    }
    feedback = {
        "stage": "design",
        "round": 2,
        "blocked": ["private-block-canary " + secret],
        "block_sources": ["business_coverage"],
        "business_diagnostics": [
            diagnostic,
            {
                "code": "business_unsupported_shape",
                "source": {
                    "section": "facts",
                    "domain": "policy",
                    "path": "business.registration.enabled",
                },
                "expected": {"enabled": True},
                "actual": {"enabled": False, "value": "private_identifier"},
            },
        ],
        "coverage_diagnostics": [
            {
                "code": "constraint_mismatch",
                "source": {"section": "field_requirements", "index": 0},
                "targets": [{"entity": "items", "field": "stock"}],
                "attribute": "pattern",
                "expected": "private-regex-canary",
                "actual": secret,
            }
        ],
        "analysis_diagnostics": [
            {
                "code": "requirement_business_shape",
                "target": {"entity": "books", "field": None},
                "sources": [
                    {
                        "source": {"section": "facts", "path": "business.private_identifier"},
                        "expected": {"entity": "books"},
                        "origin": "previous_requirement",
                        "previous_source": {
                            "section": "user_messages",
                            "index": 0,
                            "path": "private_identifier.permissions",
                            "text": "private-source-canary",
                        },
                        "excerpt": "private-excerpt-canary",
                    },
                    {
                        "source": {"section": "user_messages", "index": 1},
                        "expected": "private-input-canary",
                        "origin": "user_input",
                    },
                    {"source": {}, "expected": None, "origin": "private-origin-canary"},
                ],
            }
        ],
        "prompt": "private-prompt-canary",
        "previous_plan": {"title": "private-plan-canary"},
    }
    original = copy.deepcopy(feedback)
    shown = feedback_snapshot(feedback, settings, feedback_vocabulary(suite_cases()))
    assert feedback == original
    assert shown["business_diagnostics"][0]["source"]["path"] == "business.<key>.permissions.0"
    assert shown["business_diagnostics"][0]["expected"] == diagnostic["expected"]
    assert shown["business_diagnostics"][0]["actual"][0]["scope"] == "all"
    assert shown["business_diagnostics"][1]["expected"] == {"enabled": True}
    assert shown["business_diagnostics"][1]["actual"]["enabled"] is False
    assert shown["coverage_diagnostics"][0]["actual"]["characters"] == len("[redacted]")
    sources = shown["analysis_diagnostics"][0]["sources"]
    assert [record["origin"] for record in sources] == [
        "previous_requirement",
        "user_input",
        "unknown",
    ]
    assert sources[0]["previous_source"] == {
        "section": "user_messages",
        "index": 0,
        "path": "<key>.permissions",
    }
    assert sources[1]["source"] == {"section": "user_messages", "index": 1}
    encoded = json.dumps(shown)
    assert "private" not in encoded and secret not in encoded
    assert all(name not in encoded for name in ("api_key", "previous_plan", "prompt", "label"))


@pytest.mark.parametrize(
    "action,code",
    [
        ("private-action-canary", "requirement_business_shape"),
        ("read", "requirement_business_scope"),
    ],
)
def test_real_gateway_retains_safe_analysis_feedback_when_recommendation_retry_fails(
    tmp_path, action, code
):
    analysis = Requirement(
        summary="private-analysis-canary",
        users=[],
        data_scope="per_user",
        features=[],
        acceptance=[],
        facts={
            "private_fact_namespace": {
                "business": {
                    "permissions": [
                        {
                            "role": "private-role-canary",
                            "entity": "books",
                            "actions": [action],
                            "scope": "own",
                        }
                    ]
                }
            }
        },
    )
    issues = business_analysis_conflicts(analysis)
    assert len(issues) == 1 and issues[0]["code"] == code
    feedback = {
        "stage": "clarification",
        "round": 1,
        "blocked": [issues[0]["message"]],
        "analysis_diagnostics": analysis_feedback(issues),
    }
    settings = configured_settings(tmp_path)
    store = Store(settings)
    store.migrate()
    transport = BoundedTransport(settings)
    transport.inner.close()
    sent = []

    def provider(request):
        sent.append(json.loads(request.content))
        content = analysis.model_dump_json() if len(sent) == 1 else '{"private-response-canary":]}'
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
                ]
            },
        )

    transport.inner = httpx.MockTransport(provider)
    gateway = ObservedGateway(settings, store, transport)
    run_id = new_run(store)
    try:
        gateway.complete(run_id, "recommend:1", "private-instruction-canary", {}, Requirement)
        payload = {"resolution_feedback": feedback, "current_requirement": {}}
        with pytest.raises(ModelFailure):
            gateway.complete(
                run_id, "recommend:2", "private-instruction-canary", payload, Requirement
            )
        trace = gateway.receipt_trace(run_id)
        assert [r["logical_key"] for r in trace["items"]] == ["recommend:1", "recommend:2"]
        last = trace["items"][-1]
        assert last["validated"] is False
        assert last["feedback_sha256"] == digest(feedback)
        assert last["payload_sha256"] == digest(payload)
        shown = last["resolution_feedback"]
        assert shown["stage"] == "clarification" and shown["round"] == 1
        assert shown["analysis_diagnostics_count"] == 1
        assert shown["analysis_diagnostics_omitted"] == 0
        diagnostic = shown["analysis_diagnostics"][0]
        assert diagnostic["code"] == code
        assert diagnostic["target"] == {"entity": "books", "field": None}
        assert diagnostic["attribute"] == "permissions"
        source = diagnostic["sources"][0]
        assert source["source"] == {
            "section": "facts",
            "path": "<key>.business.permissions.0",
            "domain": "permissions",
        }
        assert source["origin"] == "model_analysis"
        assert source["expected"]["scope"] == "own"
        assert source["expected"]["role"] == {"type": "string", "characters": 19}
        assert source["expected"]["actions"] == (
            ["read"] if action == "read" else [{"type": "string", "characters": len(action)}]
        )
        assert [r["logical_key"] for r in transport.receipts] == [
            "recommend:1",
            "recommend:2",
            "recommend:2",
        ]
        assert len(sent) == transport.calls[run_id] == store.get_run(run_id)["model_calls"] == 3
        assert "private" not in json.dumps(trace) and "unit-only-key" not in json.dumps(trace)
        assert all(
            key not in source for key in ("text", "excerpt", "user_sources", "previous_source")
        )
    finally:
        transport.shutdown()
        store.engine.dispose()


def test_planning_diagnostics_and_terminal_trace_have_explicit_byte_and_count_bounds(
    tmp_path, monkeypatch
):
    settings = configured_settings(tmp_path)
    vocabulary = feedback_vocabulary(suite_cases())
    large = {
        "stage": "design",
        "round": 2,
        "blocked": ["private-free-text" for _ in range(100)],
        "block_sources": ["business_coverage"] * 100,
        "business_diagnostics": [
            {
                "code": "business_unsupported_shape",
                "source": {
                    "section": "facts",
                    "domain": "permissions",
                    "path": ".".join(["private_identifier"] * 100),
                },
                "expected": [
                    {
                        "role": "technician",
                        "entity": "work_orders",
                        "actions": ["read_metrics"] * 13,
                        "scope": "assigned",
                    }
                ]
                * 13,
                "actual": None,
            }
        ]
        * 13,
    }
    bounded = feedback_snapshot(large, settings, vocabulary)
    assert len(json.dumps(bounded, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES
    assert bounded["business_diagnostics_count"] == 13
    assert bounded["business_diagnostics_omitted"] > 0
    assert bounded["blocked_count"] == 100 and bounded["block_sources"] == {
        "business_coverage": 100
    }
    assert "private" not in json.dumps(bounded)
    analysis = feedback_snapshot(
        {
            "stage": "clarification",
            "analysis_diagnostics": [
                {
                    "code": "requirement_business_shape",
                    "target": {"entity": "books", "field": None},
                    "attribute": "permissions",
                    "sources": [
                        {
                            "source": {
                                "section": "facts",
                                "path": "private.business.permissions.0",
                            },
                            "expected": {"entity": "books", "actions": ["read"], "scope": "own"},
                            "origin": "model_analysis",
                            "excerpt": "private-analysis-canary",
                        }
                    ]
                    * 6,
                }
            ]
            * 13,
        },
        settings,
        vocabulary,
    )
    assert len(json.dumps(analysis, ensure_ascii=False).encode()) <= MAX_FEEDBACK_BYTES
    assert analysis["analysis_diagnostics_count"] == 13
    assert analysis["analysis_diagnostics_omitted"] > 0
    first = analysis["analysis_diagnostics"][0]
    assert first["sources_count"] == 6 and first["sources_omitted"] == 2
    assert len(first["sources"]) == 4
    assert "private" not in json.dumps(analysis)
    transport = BoundedTransport(settings)
    gateway = ObservedGateway(settings, None, transport)
    monkeypatch.setattr(ModelGateway, "complete", lambda *args, **kwargs: object())
    try:
        trace_feedback = {**large, "business_diagnostics": large["business_diagnostics"][:1]}
        for index in range(30):
            gateway.complete(
                "unit-only", f"plan:{index}", "", {"resolution_feedback": trace_feedback}, object
            )
        gateway.traces[-1]["validated"] = False
        trace = gateway.receipt_trace("unit-only")
        assert len(json.dumps(trace, ensure_ascii=False).encode()) <= MAX_TRACE_BYTES
        assert 0 < len(trace["items"]) < MAX_MODEL_CALLS + 1
        assert trace["omitted"] == 30 - len(trace["items"])
        assert trace["items"][-1]["logical_key"] == "plan:29"
        assert trace["items"][-1]["validated"] is False
        assert not transport.receipts
    finally:
        transport.shutdown()


@pytest.mark.parametrize("failure_kind", ["workflow", "contract"])
def test_complete_offline_terminal_receipts_never_export_workflow_error_text(
    tmp_path, monkeypatch, capsys, failure_kind
):
    from scripts import ci_template_projects as suite

    settings = configured_settings(tmp_path)
    error = "private_fact_namespace.permissions.0: private-excerpt-canary unit-only-key"
    internal_errors = []

````
