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
