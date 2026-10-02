# tests/test_native_business_evidence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.native_delivery`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `evidence`（L14–L139）：接收`tmp_path`、`template`。 控制顺序：L55按`fastapi`分支；L99按`not fastapi`分支；L106遍历`plan.entities`。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`write_json`、`plan.model_dump`、`digest`、`contract.update`、`synthetic_navigation`、`deepcopy`、`browser["pages"].append`等。 返回路径：L139的`report, {"spec_digest": identity, "template": template}, spec_path`。
- `test_both_original_and_fresh_database_business_evidence_pass`（L143–L144）：接收`tmp_path`、`template`。 控制顺序：L144断言`require_native_business(*evidence(tmp_path, template)) is True`。 调用`require_native_business`、`evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_query_ui_journey_must_be_complete_and_strict`（L151–L169）：接收`tmp_path`、`location`、`change`。 控制顺序：L158按`change == "missing"`分支；L160按`change == "marker_only"`分支；L162按`change == "wrong_keys"`分支；L164按`change == "false_count"`分支。 调用`evidence`、`browser["checks"].remove`、`browser.pop`、`pytest.raises`、`require_native_business`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_or_partial_business_receipts_fail_closed`（L176–L194）：接收`tmp_path`、`location`、`change`。 控制顺序：L183按`change == "missing"`分支；L185按`change == "false_positive"`分支；L187按`change == "digest"`分支；L189按`"browser" in location`分支。 调用`evidence`、`location.startswith`、`location.removeprefix`、`container.pop`、`container[key]["checks"].remove`、`pytest.raises`、`require_native_business`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_replaced_approved_plan_cannot_reuse_business_receipt`（L197–L204）：接收`tmp_path`。 调用`evidence`、`spec_path.unlink`、`pytest.raises`、`require_native_business`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_restart_requires_positive_exact_record_proof`（L217–L221）：接收`tmp_path`、`field`、`value`。 调用`evidence`、`pytest.raises`、`require_native_business`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requested_note_and_status_reminders_require_independent_runtime_evidence`（L227–L234）：接收`tmp_path`、`template`、`field`、`restored`。 调用`evidence`、`contract.pop`、`pytest.raises`、`require_native_business`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_business_evidence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L234。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8997`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_business_evidence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "16153fa01d2c896ce8eab912f8dc165fb30a5cca13e762373d747de52d867ce4"} -->
````python
# tests/test_native_business_evidence.py
"""Business delivery must prove both native installations against the exact plan."""

from copy import deepcopy

import pytest

from workbench.domain import Plan, digest
from workbench.filesystem import write_json
from workbench.generator import PrerequisiteError
from workbench.native_delivery import require_native_business
from workbench.settings import ROOT


def evidence(tmp_path, template="fastapiadmin"):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    spec_path = tmp_path / "approved-spec.json"
    write_json(spec_path, plan.model_dump())
    identity = digest(plan.model_dump())
    contract = {
        key: True
        for key in (
            "passed",
            "real_native_auth",
            "public_native_registration",
            "three_roles",
            "relations",
            "related_history",
            "assignment",
            "transitions",
            "handling_history",
            "audit",
            "in_app_reminders",
            "due_reminders",
            "note_reminders",
            "status_change_reminders",
            "reminder_read_isolation",
            "metrics",
            "row_isolation",
        )
    }
    contract.update(spec_digest=identity, records={"customers": "1", "requests": "2", "tasks": "3"})
    fastapi = template == "fastapiadmin"
    checks = [
        role + (":real_native_login_menu_shell" if fastapi else ":native-login-and-tenant")
        for role in ("manager", "service", "employee")
    ]
    checks += [
        "manager:customers:native-query-and-exact-filter",
        "employee:own_record_history_acl_and_read_reminder",
        "other_employee:row_isolation",
        "other_service:row_isolation",
    ]
    if fastapi:
        checks += [
            "manager:customer_native_form_create",
            "manager:changed_value_edit",
            "employee:related_request_native_form_create",
            "manager:linked_task_and_native_assignment",
            "service:assigned_workflows_notes_timestamps",
            "manager:all_declared_native_metric_cards",
        ]
    else:
        checks += [
            "manager:customers:native-form-create",
            "manager:requests:native-form-create",
            "employee:requests:native-form-create",
            "manager:tasks:native-form-create",
            "native-business-action:assign:",
            "native-business-action:transition:start",
            "native-business-action:transition:resolve",
            "native-business-action:add_note:",
            "manager:customers:requests:related-record-and-history",
            "manager:requests:tasks:related-record-and-history",
            "manager:real-native-echarts-metrics",
        ]
    browser = {
        "passed": True,
        "errors": [],
        "spec_digest": identity,
        "template": template,
        "checks": checks,
        "pages": [],
        "query_journey": {
            "entity": "customers",
            "keyword_field": "name",
            "filter_field": "category",
            "cases": 3,
            "keyword": True,
            "combined_positive": True,
            "combined_mismatch": True,
            "request_values_verified": True,
            "response_ids_exact": True,
            "rendered_ids_exact": True,
            "controls_reset": True,
        },
    }
    if not fastapi:
        from test_yudao_navigation_evidence import synthetic_navigation

        navigation, sidebar = synthetic_navigation(plan)
        contract["installed_navigation"] = navigation
        contract["installed_navigation_restart"] = deepcopy(navigation)
        browser["installed_navigation"] = sidebar
    for entity in plan.entities:
        browser["pages"].append(
            {
                "entity": entity.name,
                "native_shell_visible": True,
                "native_form_components_visible": True,
                "real_list_request": True,
                "native_component_family": "Fa/Element Plus" if fastapi else "Vben/Ant Design/VXE",
                "native_theme_tokens": {
                    key: "native-value"
                    for key in (
                        ["--el-color-primary", "--el-font-size-base"]
                        if fastapi
                        else ["--primary", "--background", "--font-family"]
                    )
                },
            }
        )
    report = {
        "spec_digest": identity,
        "business_contract": contract,
        "business_browser": browser,
        "portable_restored": {
            "business": deepcopy(contract),
            "browser": deepcopy(browser),
            "restart": True,
            "restart_preserved_records": True,
            "restart_records": {
                entity: {"id": identifier, "sha256": "a" * 64}
                for entity, identifier in contract["records"].items()
            },
        },
    }
    return report, {"spec_digest": identity, "template": template}, spec_path


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_both_original_and_fresh_database_business_evidence_pass(tmp_path, template):
    assert require_native_business(*evidence(tmp_path, template)) is True


@pytest.mark.parametrize("location", ["business_browser", "restored_browser"])
@pytest.mark.parametrize(
    "change", ["missing", "marker_only", "wrong_keys", "false_count", "false_flag"]
)
def test_native_query_ui_journey_must_be_complete_and_strict(tmp_path, location, change):
    report, receipt, spec_path = evidence(tmp_path)
    browser = (
        report["business_browser"]
        if location == "business_browser"
        else report["portable_restored"]["browser"]
    )
    if change == "missing":
        browser["checks"].remove("manager:customers:native-query-and-exact-filter")
    elif change == "marker_only":
        browser.pop("query_journey")
    elif change == "wrong_keys":
        browser["query_journey"]["filter_field"] = "organization"
    elif change == "false_count":
        browser["query_journey"]["cases"] = 1
    else:
        browser["query_journey"]["request_values_verified"] = 1
    with pytest.raises(PrerequisiteError):
        require_native_business(report, receipt, spec_path)


@pytest.mark.parametrize(
    "location", ["business_contract", "restored_business", "business_browser", "restored_browser"]
)
@pytest.mark.parametrize("change", ["missing", "false_positive", "digest", "partial"])
def test_legacy_or_partial_business_receipts_fail_closed(tmp_path, location, change):
    report, receipt, spec_path = evidence(tmp_path)
    container, key = (
        (report["portable_restored"], location.removeprefix("restored_"))
        if location.startswith("restored_")
        else (report, location)
    )
    if change == "missing":
        container.pop(key)
    elif change == "false_positive":
        container[key]["passed"] = 1
    elif change == "digest":
        container[key]["spec_digest"] = "other-plan"
    elif "browser" in location:
        container[key]["checks"].remove("other_employee:row_isolation")
    else:
        container[key]["row_isolation"] = False
    with pytest.raises(PrerequisiteError, match="原生业务"):
        require_native_business(report, receipt, spec_path)


def test_missing_or_replaced_approved_plan_cannot_reuse_business_receipt(tmp_path):
    report, receipt, spec_path = evidence(tmp_path)
    spec_path.unlink()
    with pytest.raises(PrerequisiteError, match="原生业务"):
        require_native_business(report, receipt, spec_path)
    write_json(spec_path, {"title": "different"})
    with pytest.raises(PrerequisiteError, match="原生业务"):
        require_native_business(report, receipt, spec_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("restart", False),
        ("restart", 1),
        ("restart_preserved_records", False),
        ("restart_records", {}),
        ("restart_records", {"customers": {"id": "5", "sha256": "fake"}}),
    ],
)
def test_business_restart_requires_positive_exact_record_proof(tmp_path, field, value):
    report, receipt, spec_path = evidence(tmp_path)
    report["portable_restored"][field] = value
    with pytest.raises(PrerequisiteError):
        require_native_business(report, receipt, spec_path)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("field", ["note_reminders", "status_change_reminders"])
@pytest.mark.parametrize("restored", [False, True])
def test_requested_note_and_status_reminders_require_independent_runtime_evidence(
    tmp_path, template, field, restored
):
    report, receipt, spec_path = evidence(tmp_path, template)
    contract = report["portable_restored"]["business"] if restored else report["business_contract"]
    contract.pop(field)
    with pytest.raises(PrerequisiteError, match="原生业务"):
        require_native_business(report, receipt, spec_path)
````
