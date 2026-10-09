# tests/test_business_receipt.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.settings`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `receipt`（L14–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L25断言`report.pop("unit_test_fixture_only") is True`。 调用`Plan.model_validate_json( (ROOT / "examples/plans/customer-servic…`、`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.loads`、`(ROOT / "tests/fixtures/customer_evidence_receipt_unit_only.json"…`、`report.pop`。 返回路径：L27的`spec, report`。
- `test_complete_business_receipt_and_api_only`（L30–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`receipt`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_wrong_business_evidence_blocks`（L51–L56）：接收`section`、`key`、`value`。 调用`receipt`、`deepcopy`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_declared_browser_capability_cannot_pass_without_executed_marker`（L63–L73）：接收`capability`。 控制顺序：L71断言`detail["missing_checks"] == [marker]`；L72断言`detail["missing_check_count"] == 1`；L73断言`detail["invalid_fields"] == []`。 调用`receipt`、`require_business_evidence`、`report["browser"]["checks"].remove`、`pytest.raises`、`json.loads`、`str(failure.value).split`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bind_unit_receipt`（L76–L81）：接收`spec`、`report`。 源码说明：Rebind synthetic unit metadata only; no changes to live evidence or fixtures.。 控制顺序：L79遍历`("business", "browser")`。 调用`Plan.model_validate(spec).model_dump`、`Plan.model_validate`、`digest`。 返回路径：L81的`spec`。
- `test_browser_actions_without_any_role_authorization_are_not_required`（L88–L94）：接收`action`、`capability`。 控制顺序：L90遍历`spec["business"]["permissions"]`。 调用`receipt`、`bind_unit_receipt`、`report["browser"]["checks"].remove`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_declared_metrics_does_not_require_a_dashboard_action`（L97–L102）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`receipt`、`bind_unit_receipt`、`report["browser"]["checks"].remove`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_due_only_notifications_still_require_actual_browser_reminder_evidence`（L105–L115）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L110断言`spec["business"]["notifications"] and report["business"]["evidence"]["due_notificatio…`。 调用`receipt`、`bind_unit_receipt`、`require_business_evidence`、`report["browser"]["checks"].remove`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_datetime_fields_without_notification_rules_do_not_create_reminder_obligations`（L118–L125）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L120断言`any(field["kind"] == "datetime" for e in spec["entities"] for field in e["fields"])`。 调用`receipt`、`any`、`bind_unit_receipt`、`report["browser"]["checks"].remove`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stock_browser_obligations_preserve_every_declared_capability`（L128–L150）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`business_browser_checks(spec) == { "business-browser-auth", "business-browser-role-na…`。 调用`fixture_plan(load_case("stock-purchasing")).model_dump`、`fixture_plan`、`load_case`、`business_browser_checks`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_failure_summary_contains_only_bounded_approved_markers_and_static_fields`（L153–L166）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L162断言`"unknown-raw-browser-data" not in message and len(message) < 2000`；L163断言`set(detail["invalid_fields"]) == {"errors", "checks"}`；L164断言`detail["expected_check_count"] == detail["missing_check_count"]`；L165断言`detail["observed_check_count"] == 0`；L166断言`0 < len(detail["missing_checks"]) <= 20`。 调用`receipt`、`pytest.raises`、`require_business_evidence`、`str`、`json.loads`、`message.split`、`len`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_receipt.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L166。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6638`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_receipt.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9e7fac3572f7114be7b1bdcdd667eb8c0b577f52bf300ebef95477768b06979a"} -->
````python
# tests/test_business_receipt.py
"""Business packaging cannot reuse classic CRUD or mismatched browser evidence."""

import json
from copy import deepcopy

import pytest

from workbench.domain import Plan, digest
from workbench.generator import PrerequisiteError
from workbench.settings import ROOT
from workbench.verification import business_browser_checks, require_business_evidence


def receipt():
    # This fixture only exercises receipt validation; live generated HTTP/browser
    # tests separately execute the complete workflow and reject injected faults.
    spec = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    ).model_dump()
    report = json.loads(
        (ROOT / "tests/fixtures/customer_evidence_receipt_unit_only.json").read_text(
            encoding="utf-8"
        )
    )
    assert report.pop("unit_test_fixture_only") is True
    report.pop("source")
    return spec, report


def test_complete_business_receipt_and_api_only():
    spec, report = receipt()
    require_business_evidence(spec, report, True)
    require_business_evidence(spec, {"business": report["business"]}, False)


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("business", "passed", 1),
        ("business", "spec_digest", "old"),
        ("business", "resources_checked", []),
        ("business", "roles_checked", []),
        ("business", "checks", []),
        ("browser", "real_browser", 1),
        ("browser", "spec_digest", "old"),
        ("browser", "entities", []),
        ("browser", "errors", ["page error"]),
        ("browser", "checks", []),
    ],
)
def test_missing_or_wrong_business_evidence_blocks(section, key, value):
    spec, report = receipt()
    report = deepcopy(report)
    report[section][key] = value
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "capability",
    ["assignment", "transitions", "notes-history", "reminders", "metrics", "relation-labels"],
)
def test_declared_browser_capability_cannot_pass_without_executed_marker(capability):
    spec, report = receipt()
    require_business_evidence(spec, report, True)
    marker = "business-browser-" + capability
    report["browser"]["checks"].remove(marker)
    with pytest.raises(PrerequisiteError) as failure:
        require_business_evidence(spec, report, True)
    detail = json.loads(str(failure.value).split(": ", 1)[1])
    assert detail["missing_checks"] == [marker]
    assert detail["missing_check_count"] == 1
    assert detail["invalid_fields"] == []


def bind_unit_receipt(spec, report):
    """Rebind synthetic unit metadata only; no changes to live evidence or fixtures."""
    spec = Plan.model_validate(spec).model_dump()
    for section in ("business", "browser"):
        report[section]["spec_digest"] = digest(spec)
    return spec


@pytest.mark.parametrize(
    "action,capability",
    [("assign", "assignment"), ("add_note", "notes-history"), ("read_metrics", "metrics")],
)
def test_browser_actions_without_any_role_authorization_are_not_required(action, capability):
    spec, report = receipt()
    for grant in spec["business"]["permissions"]:
        grant["actions"] = [value for value in grant["actions"] if value != action]
    spec = bind_unit_receipt(spec, report)
    report["browser"]["checks"].remove("business-browser-" + capability)
    require_business_evidence(spec, report, True)


def test_no_declared_metrics_does_not_require_a_dashboard_action():
    spec, report = receipt()
    spec["business"]["metrics"] = []
    spec = bind_unit_receipt(spec, report)
    report["browser"]["checks"].remove("business-browser-metrics")
    require_business_evidence(spec, report, True)


def test_due_only_notifications_still_require_actual_browser_reminder_evidence():
    spec, report = receipt()
    spec["business"]["notifications"] = [
        rule for rule in spec["business"]["notifications"] if rule["event"] == "due"
    ]
    assert spec["business"]["notifications"] and report["business"]["evidence"]["due_notifications"]
    spec = bind_unit_receipt(spec, report)
    require_business_evidence(spec, report, True)
    report["browser"]["checks"].remove("business-browser-reminders")
    with pytest.raises(PrerequisiteError, match="business-browser-reminders"):
        require_business_evidence(spec, report, True)


def test_datetime_fields_without_notification_rules_do_not_create_reminder_obligations():
    spec, report = receipt()
    assert any(field["kind"] == "datetime" for e in spec["entities"] for field in e["fields"])
    spec["business"]["notifications"] = []
    report["business"]["evidence"]["due_notifications"] = []
    spec = bind_unit_receipt(spec, report)
    report["browser"]["checks"].remove("business-browser-reminders")
    require_business_evidence(spec, report, True)


def test_stock_browser_obligations_preserve_every_declared_capability():
    from test_template_project_acceptance import fixture_plan

    from scripts.template_acceptance_cases import load_case

    spec = fixture_plan(load_case("stock-purchasing")).model_dump()
    assert business_browser_checks(spec) == {
        "business-browser-auth",
        "business-browser-role-navigation",
        "business-browser-role-restrictions",
        "business-browser-related-views",
        "business-browser-related-row-acl",
        "business-browser-datetime-controls",
        "business-browser-query-matrix",
        "business-browser-records:suppliers",
        "business-browser-records:items",
        "business-browser-records:purchase_orders",
        "business-browser-transitions",
        "business-browser-notes-history",
        "business-browser-reminders",
        "business-browser-metrics",
        "business-browser-relation-labels",
    }


def test_browser_failure_summary_contains_only_bounded_approved_markers_and_static_fields():
    spec, report = receipt()
    sensitive = "unknown-raw-browser-data" * 500
    report["browser"]["errors"] = [{"message": sensitive}]
    report["browser"]["checks"] = [sensitive, {"invalid_marker": sensitive}]
    with pytest.raises(PrerequisiteError) as failure:
        require_business_evidence(spec, report, True)
    message = str(failure.value)
    detail = json.loads(message.split(": ", 1)[1])
    assert "unknown-raw-browser-data" not in message and len(message) < 2000
    assert set(detail["invalid_fields"]) == {"errors", "checks"}
    assert detail["expected_check_count"] == detail["missing_check_count"]
    assert detail["observed_check_count"] == 0
    assert 0 < len(detail["missing_checks"]) <= 20
````
