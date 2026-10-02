"""Live generated-product proof and deliberate faults for customer delivery evidence."""

import json
import os
import subprocess
import sys

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env


def customer_plan():
    return Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )


def execute(product):
    return subprocess.run(
        [sys.executable, "verify.py", "--python", sys.executable],
        cwd=product,
        env=clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=150,
    )


def test_customer_delivery_exposes_executed_field_relation_datetime_due_and_audit_proof(tmp_path):
    plan = customer_plan()
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    proof = report["business"]["evidence"]
    assert proof["version"] == 1
    assert len(proof["field_validation"]) == sum(len(entity.fields) for entity in plan.entities)
    by_field = {(item["entity"], item["field"]): item for item in proof["field_validation"]}
    for entity in ("customers", "requests", "tasks"):
        definition = next(item for item in plan.entities if item.name == entity)
        for field in definition.fields:
            entry = by_field[entity, field.name]
            if entry.get("protected_create_rejected"):
                assert entry["protected_update_rejected"]
            else:
                if field.required:
                    assert entry["missing_required_rejected"] and entry["null_rejected"]
                if field.kind == "text":
                    assert (
                        entry["max_length"] == field.max_length
                        and entry["over_max_length_rejected"]
                    )
                if field.kind == "enum":
                    assert entry["invalid_enum_rejected"] and entry["declared_choices"] == len(
                        field.choices
                    )
    assert any(
        item["entity"] == "customers" and "requests" in item["target_entities"]
        for item in proof["related_views"]
    )
    assert any(
        item["entity"] == "requests" and "tasks" in item["target_entities"]
        for item in proof["related_views"]
    )
    assert any(
        item["role"] == "employee" and item["entity"] == "customers" and item["target_row_acl"]
        for item in proof["related_views"]
    )
    assert {item["field"] for item in proof["relation_labels"]} >= {
        "customer_id",
        "request_id",
        "assignee_id",
    }
    assert len(proof["datetime_policy"]) == 4
    assert all(
        item["timestamp_stored"]
        and item["excluded_from_keyword_search"]
        and set(item["undeclared_query_parameters_rejected"]) == {"filter", "from", "to"}
        for item in proof["datetime_policy"]
    )
    assert {item["entity"] for item in proof["due_notifications"]} == {"requests", "tasks"}
    assert all(
        item["past_due_events_verified"] > 0
        and item["future_deadline_no_event"]
        and item["repeated_reads_deduplicated"]
        and item["event_and_read_state_persisted_after_restart"]
        for item in proof["due_notifications"]
    )
    assert {item["entity"] for item in proof["audit_immutability"]} == {
        "customers",
        "requests",
        "tasks",
    }
    assert all(
        item["mutation_delete_attempts_rejected"] == 6
        and item["action_actor_timestamp"]
        and item["unchanged_after_attempts"]
        and item["archive_and_restart_preserved"]
        for item in proof["audit_immutability"]
    )
    assert len(json.dumps(proof).encode()) < 24000
    assert not any(
        secret in json.dumps(proof)
        for secret in ("Bearer", "password", "verify-manager", "record_id")
    )


@pytest.mark.parametrize(
    "file,old,new,expected",
    [
        ("business_policy.py", '<= field["max_length"]', "<= 1000000", "over_max_length_rejected"),
        (
            "business_policy.py",
            'if kind == "enum" and value not in field["choices"]:',
            "if False:",
            "invalid_enum_rejected",
        ),
        (
            "business_runtime.py",
            '*scope(actor, source, "read"),',
            "",
            "Related view violated target row ACL",
        ),
        (
            "business_runtime.py",
            'row.get("name") or row.get("title") or "关联记录"',
            'row["id"]',
            "Reference labels",
        ),
        (
            "querying.py",
            'if field.get("searchable")',
            'if field.get("searchable") or field["kind"] == "datetime"',
            "Nonsearchable datetime",
        ),
        (
            "querying.py",
            'if field.get("date_range"):',
            'if field.get("date_range") or field["kind"] == "datetime":',
            "expected 422",
        ),
        ("business_runtime.py", "target.c[due] <= utc(),", "", "notifications"),
    ],
)
def test_delivery_verifier_rejects_real_generated_runtime_faults(
    tmp_path, file, old, new, expected
):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    source = product / file
    text = source.read_text(encoding="utf-8")
    assert old in text
    source.write_text(text.replace(old, new), encoding="utf-8")
    result = execute(product)
    assert result.returncode == 1, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    assert report["passed"] is False and expected.lower() in report["message"].lower(), report


def test_delivery_verifier_rejects_audit_mutation_route_even_for_manager(tmp_path):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    source = product / "app.py"
    source.write_text(
        source.read_text(encoding="utf-8")
        + '\n@app.put("/api/{entity}/{identity}/history")\ndef mutable_audit(entity: str, identity: str):\n    return {"modified": True}\n',
        encoding="utf-8",
    )
    result = execute(product)
    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        "Audit mutation/deletion route accepted"
        in json.loads(result.stdout.splitlines()[-1])["message"]
    )
