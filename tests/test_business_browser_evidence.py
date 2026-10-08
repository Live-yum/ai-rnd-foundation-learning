"""Real generated-product Chromium evidence and explicit UI fault-injection checks.

Fault cases mutate only a disposable generated product. They prove the independent
browser gate rejects regressions; they never stand in for the passing runtime run.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env
from workbench.verification import require_business_evidence

ROOT = Path(__file__).parents[1]


def customer_plan(with_employee_history=True):
    data = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    if not with_employee_history:
        for permission in data["business"]["permissions"]:
            if permission["role"] == "employee":
                permission["actions"] = [
                    action
                    for action in permission["actions"]
                    if action not in {"read_history", "read_audit"}
                ]
    return Plan.model_validate(data)


def run_browser_gate(tmp_path, plan, fault=None):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium required; no simulated browser fallback")
    product = tmp_path / "product"
    generate_basic(
        plan,
        product,
        {"template": "python-basic", "frontend": "simple-admin", "database": "sqlite"},
    )
    if fault:
        app = product / "web/app.js"
        source = app.read_text(encoding="utf-8")
        mutations = {
            "raw_list_reference": (
                'value=labels[field.name]?.[String(raw)] || "关联记录不可见"',
                "value=String(raw)",
            ),
            "raw_select_reference": (
                'node("option", item.name || item.title || item.id, input)',
                'node("option", item.id, input)',
            ),
            "raw_assignee_detail": (
                'node("option",user.username,select)',
                'node("option",user.id,select)',
            ),
            "omitted_related_records": (
                "group.records.forEach(item=>{",
                "group.records.slice(0,0).forEach(item=>{",
            ),
            "forbidden_datetime_range": (
                "if (field.date_range) {",
                'if (field.date_range || field.kind === "datetime") {',
            ),
        }
        before, after = mutations[fault]
        assert before in source, "UI fault injection must hit the actual generated implementation"
        app.write_text(source.replace(before, after), encoding="utf-8")
    report = tmp_path / "runtime-report.json"
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_VERIFY_PLAYWRIGHT": module,
            "PLAYWRIGHT_BROWSERS_PATH": "0",
            "PYTHONUTF8": "1",
        }
    )
    result = subprocess.run(
        [sys.executable, "verify.py", "--python", sys.executable, "--report", str(report)],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=360,
    )
    assert report.is_file(), result.stdout + result.stderr
    return result, json.loads(report.read_text(encoding="utf-8"))


def assert_bounded_evidence(plan, report):
    browser = report["browser"]
    assert browser["passed"] is True and browser["real_browser"] is True
    evidence = browser["evidence"]
    assert set(evidence) == {
        "version",
        "relation_labels",
        "related_views",
        "related_sources",
        "datetime_controls",
        "query_matrix",
    }
    assert evidence["version"] == 1
    roles = {role.name for role in plan.business.roles}
    entities = {entity.name: entity for entity in plan.entities}
    relations = {(relation.entity, relation.field) for relation in plan.business.relations}
    field_count = sum(len(entity.fields) for entity in plan.entities)
    assert len(evidence["relation_labels"]) <= len(roles) * len(relations)
    assert len(evidence["related_views"]) <= len(roles) * len(relations)
    assert len(evidence["related_sources"]) <= len(roles) * len(entities)
    assert len(evidence["datetime_controls"]) <= len(roles) * field_count
    for entry in evidence["relation_labels"]:
        assert set(entry) == {
            "role",
            "entity",
            "field",
            "list",
            "select",
            "detail",
            "records_checked",
        }
        assert entry["role"] in roles and (entry["entity"], entry["field"]) in relations
        assert entry["list"] is True and 0 < entry["records_checked"] <= 100
        assert entry["select"] is True or entry["select"] is None
        assert entry["detail"] is True or entry["detail"] is None
    for entry in evidence["related_views"]:
        assert set(entry) == {
            "role",
            "entity",
            "target_entity",
            "field",
            "source_records",
            "expected_records",
            "visible_records",
            "target_acl",
            "navigation",
        }
        assert entry["role"] in roles and entry["entity"] in entities
        assert (entry["target_entity"], entry["field"]) in relations
        assert entry["target_acl"] is True
        assert 0 < entry["source_records"] <= 100
        assert entry["expected_records"] == entry["visible_records"]
        assert entry["navigation"] is (True if entry["expected_records"] else None)
    for entry in evidence["related_sources"]:
        assert set(entry) == {"role", "entity", "source_records", "groups_checked", "target_acl"}
        assert entry["role"] in roles and entry["entity"] in entities
        assert entry["target_acl"] is True and 0 < entry["source_records"] <= 100
    for entry in evidence["datetime_controls"]:
        assert set(entry) == {
            "role",
            "entity",
            "field",
            "searchable",
            "date_range",
            "filterable",
            "controls_absent",
        }
        assert entry["role"] in roles and entry["entity"] in entities
        field = next(
            field for field in entities[entry["entity"]].fields if field.name == entry["field"]
        )
        assert field.kind == "datetime"
        assert entry["searchable"] is field.searchable
        assert entry["date_range"] is field.date_range
        assert entry["filterable"] is field.filterable
        assert entry["controls_absent"] is True
    # No raw customer data, generated credentials, usernames or identities escape.
    encoded = json.dumps(evidence, ensure_ascii=False)
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f-]{27,}", encoded, re.I)
    assert not any(
        secret in encoded for secret in ["password", "token", "verify-", "record_id", 'label":']
    )


@pytest.mark.parametrize("with_employee_history", [True, False])
def test_customer_browser_evidence_is_real_bounded_and_plan_derived(
    tmp_path, with_employee_history
):
    plan = customer_plan(with_employee_history)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert_bounded_evidence(plan, report)
    evidence = report["browser"]["evidence"]
    labels = {
        (item["role"], item["entity"], item["field"]): item for item in evidence["relation_labels"]
    }
    for entity, field in [
        ("requests", "customer_id"),
        ("tasks", "request_id"),
        ("tasks", "assignee_id"),
    ]:
        assert labels["manager", entity, field]["select"] is True
    assert labels["manager", "requests", "assignee_id"]["detail"] is True
    views = {
        (item["role"], item["entity"], item["target_entity"]): item
        for item in evidence["related_views"]
    }
    assert views["manager", "customers", "requests"]["visible_records"] > 0
    assert views["manager", "requests", "tasks"]["visible_records"] > 0
    assert views["employee", "customers", "requests"]["visible_records"] > 0
    assert ("employee", "requests", "tasks") not in views
    assert any(
        item["role"] == "employee" and item["entity"] == "requests" and item["groups_checked"] == 0
        for item in evidence["related_sources"]
    )
    assert {
        "business-browser-relation-labels",
        "business-browser-related-views",
        "business-browser-related-row-acl",
        "business-browser-datetime-controls",
    } <= set(report["browser"]["checks"])


@pytest.mark.parametrize(
    "fault, failure",
    [
        ("raw_list_reference", "relation-list-label"),
        ("raw_select_reference", "relation-select-label"),
        ("raw_assignee_detail", "assignee-detail-label"),
        ("omitted_related_records", "related-rendered-records"),
        ("forbidden_datetime_range", "filter-controls-contract"),
    ],
)
def test_browser_fault_injection_cannot_claim_customer_evidence(tmp_path, fault, failure):
    result, report = run_browser_gate(tmp_path, customer_plan(), fault)
    assert result.returncode != 0 and report["passed"] is False, report
    assert "business-browser-" + failure in report["message"], report
    assert '"source":"verify-business-browser.cjs"' in report["message"]
    assert '"callsites":[{"line":' in report["message"]


def test_generic_business_browser_uses_declared_display_fields(tmp_path):
    # An approved generic resource may have no name/title. The customer contract
    # does declare them and remains subject to strict non-ID display assertions.
    data = customer_plan().model_dump()
    requests = next(entity for entity in data["entities"] if entity["name"] == "requests")
    requests["fields"] = [field for field in requests["fields"] if field["name"] != "title"]
    plan = Plan.model_validate(data)
    assert not any(field.name in {"name", "title"} for field in plan.entities[1].fields)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert_bounded_evidence(plan, report)
    assert report["browser"]["evidence"]["related_views"]


def test_minimal_schema_mobile_sticky_actions_remain_inside_table(tmp_path):
    # A single data column used to stretch the auto-layout sticky action column
    # beyond the mobile viewport. Keep every real 390px/1440px, left/right
    # geometry assertion in the generated browser verifier unchanged.
    from test_business_python import runtime_plan

    plan = runtime_plan()
    assert len(plan.entities[0].fields) == 1
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-browser-responsive-actions" in report["browser"]["checks"]
    assert_bounded_evidence(plan, report)


def test_stock_browser_receipt_reaches_platform_gate_without_undeclared_assignment(tmp_path):
    # This contract-derived offline Plan exercises the actual generated HTTP,
    # Chromium and restart checks. It never substitutes for the live model Plan.
    from test_template_project_acceptance import fixture_plan

    from scripts.template_acceptance_cases import load_case

    plan = fixture_plan(load_case("stock-purchasing"))
    assert len(plan.entities) == 3 and len(plan.business.roles) == 3
    assert any(field.kind == "integer" for entity in plan.entities for field in entity.fields)
    assert all(resource.assignee_field is None for resource in plan.business.resources)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    checks = set(report["browser"]["checks"])
    assert "business-browser-assignment" not in checks
    assert {
        "business-browser-transitions",
        "business-browser-notes-history",
        "business-browser-reminders",
        "business-browser-metrics",
        "business-browser-relation-labels",
    } <= checks
    require_business_evidence(plan.model_dump(), report, True)
