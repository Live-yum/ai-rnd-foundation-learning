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
