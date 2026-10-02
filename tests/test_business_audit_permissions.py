"""Synthetic generated-product regressions for independent audit/history grants.

These are declared test Plans, never execution of diagnostic model envelopes.
"""

import json
import os
import subprocess
import sys

import pytest
import test_business_browser_evidence as browser_evidence
from test_business_acceptance_evidence import execute
from test_business_browser_evidence import run_browser_gate

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.symbols import parse_file
from workbench.tools import clean_env
from workbench.verification import require_business_evidence


def audit_only_plan():
    raw = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    for grant in raw["business"]["permissions"]:
        if grant["entity"] == "customers" and grant["role"] in {"manager", "employee"}:
            grant["actions"] = [
                action for action in grant["actions"] if action not in {"read_history", "add_note"}
            ]
    next(r for r in raw["business"]["resources"] if r["entity"] == "customers")["notes"] = False
    return Plan.model_validate(raw)


def test_native_audit_entry_points_honor_independent_audit_and_history_permissions():
    fastapi = ROOT / "templates/business/fastapiadmin/index.vue"
    source = fastapi.read_text(encoding="utf-8")
    button = next(line for line in source.splitlines() if '@click="showHistory(row)"' in line)
    assert "v-if=\"can('read_history') || can('read_audit')\"" in button
    assert "{ audit: can('read_audit') }" in source
    controller = (ROOT / "templates/business/fastapiadmin/controller.py").read_text(
        encoding="utf-8"
    )
    assert 'entity, row_id, "read_audit" if audit else "read_history"' in controller
    assert parse_file(fastapi)["parse_error"] is False
    yudao = (ROOT / "templates/business/yudao/panel.vue").read_text(encoding="utf-8")
    assert 'v-if="meta.actions.includes(\'read_audit\')" @click="toggleAudit"' in yudao
    assert "result.actions.includes(audit.value ? 'read_audit' : 'read_history')" in yudao
    assert "audit: audit.value" in yudao
    service = (ROOT / "templates/business/yudao/RndBusinessService.java").read_text(
        encoding="utf-8"
    )
    assert 'require(name,row,audit?"read_audit":"read_history")' in service


SCENARIO = r"""
import getpass, json
from fastapi.testclient import TestClient
import manage

password = 'Audit-Test-Password-123'
getpass.getpass = lambda _: password
manage.bootstrap_admin('admin')
from app import app
with TestClient(app) as client:
    def call(method, path, token=None, status=200, **kwargs):
        response = client.request(method, path, headers={'Authorization':'Bearer '+token} if token else {}, **kwargs)
        assert response.status_code == status, (method, path, response.status_code, response.text)
        return response.json()
    def login(name):
        return call('POST', '/auth/login', json={'username':name, 'password':password})['access_token']
    manager = login('admin')
    actors = {}
    for role in ['service', 'employee', 'scoped_auditor']:
        call('POST', '/business/users', manager, status=201,
             json={'username':role, 'password':password, 'role':role})
        actors[role] = login(role)
    foreign = call('POST', '/api/customers', manager, status=201,
                   json={'name':'Manager customer', 'category':'企业'})
    owned = call('POST', '/api/customers', actors['scoped_auditor'], status=201,
                 json={'name':'Own customer', 'category':'个人'})
    path = '/api/customers/' + foreign['id']
    audit = call('GET', path + '/history', manager)
    assert audit and all({'before','after'} <= entry.keys() for entry in audit)
    assert audit[0]['after']['id'] == foreign['id']
    history = call('GET', path + '/history', actors['service'])
    assert [entry['id'] for entry in history] == [entry['id'] for entry in audit]
    assert all('before' not in entry and 'after' not in entry for entry in history)
    call('GET', path + '/history', actors['employee'], status=403)
    call('GET', path + '/history', actors['scoped_auditor'], status=404)
    own_path = '/api/customers/' + owned['id']
    own_audit = call('GET', own_path + '/history', actors['scoped_auditor'])
    assert own_audit and own_audit[0]['after']['id'] == owned['id']
    # Audit access never grants the independent notes/history permission.
    call('GET', path + '/notes', manager, status=403)
    call('GET', own_path + '/notes', actors['scoped_auditor'], status=403)
    assert call('GET', path + '/notes', actors['service']) == []
    for endpoint in [path + '/history', path + '/history/' + audit[0]['id']]:
        for method in ['PUT', 'PATCH', 'DELETE']:
            response = client.request(method, endpoint, headers={'Authorization':'Bearer '+manager},
                                      json={'action':'forged', 'before':{}, 'after':{}})
            assert response.status_code in {403,404,405}, response.text
            assert call('GET', path + '/history', manager) == audit
    call('POST', path + '/archive', manager)
    archived = call('GET', path + '/history', manager)
    assert archived[:len(audit)] == audit and archived[-1]['action'] == 'archived'
    call('GET', path + '/history', actors['scoped_auditor'], status=404)
    assert call('GET', own_path + '/history', actors['scoped_auditor']) == own_audit
print(json.dumps({'passed':True,'audit_only':True,'history_redacted':True,'row_acl':True,
                  'notes_denied':True,'audit_mutations_denied':6,'archive_preserved':True}))
"""


def test_generated_audit_only_access_preserves_scope_redaction_notes_and_immutability(tmp_path):
    raw = audit_only_plan().model_dump()
    raw["business"]["roles"].append({"name": "scoped_auditor", "label": "Scoped test auditor"})
    raw["business"]["permissions"].append(
        {
            "role": "scoped_auditor",
            "entity": "customers",
            "scope": "own",
            "actions": ["read", "create", "read_audit"],
        }
    )
    product = tmp_path / "product"
    generate_basic(Plan.model_validate(raw), product)
    env = clean_env({"PATH": os.environ.get("PATH", ""), "PRODUCT_DATA_DIR": str(tmp_path / "db")})
    for args in [["manage.py", "init"], ["-c", SCENARIO]]:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.splitlines()[-1])["passed"]


@pytest.mark.parametrize("fault", [None, "missing_auditor", "redacted_audit"])
def test_audit_only_delivery_retains_full_mutation_archive_restart_proof(tmp_path, fault):
    plan = audit_only_plan()
    if fault == "missing_auditor":
        for grant in plan.business.permissions:
            if grant.entity == "customers" and "read_audit" in grant.actions:
                grant.actions.remove("read_audit")
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    if fault == "redacted_audit":
        path = product / "business_runtime.py"
        source = path.read_text(encoding="utf-8")
        assert "if full\n" in source
        path.write_text(source.replace("if full\n", "if False\n"), encoding="utf-8")
    result = execute(product)
    report = json.loads(result.stdout.splitlines()[-1])
    if fault:
        assert result.returncode == 1 and report["passed"] is False, report
        expected = (
            "no permitted audit reader"
            if fault == "missing_auditor"
            else "Audit snapshots unavailable"
        )
        assert expected in report["message"], report
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        require_business_evidence(plan.model_dump(), report, False)
        proof = report["business"]["evidence"]["audit_immutability"]
        assert {entry["entity"] for entry in proof} == {"customers", "requests", "tasks"}
        assert all(
            entry["mutation_delete_attempts_rejected"] == 6
            and entry["archive_and_restart_preserved"]
            for entry in proof
        )
        assert "business-notes-history" in report["business"]["checks"]


@pytest.mark.parametrize("hide_audit", [False, True])
def test_browser_displays_audit_only_customer_and_preserves_history_redaction(
    tmp_path, monkeypatch, hide_audit
):
    plan = audit_only_plan()
    if hide_audit:
        generate = browser_evidence.generate_basic

        def faulty_generate(spec, product, selection):
            result = generate(spec, product, selection)
            path = product / "web/app.js"
            source = path.read_text(encoding="utf-8")
            expected = 'if(can("read_history") || can("read_audit")) {'
            assert expected in source
            path.write_text(source.replace(expected, 'if(can("read_history")) {'), encoding="utf-8")
            return result

        monkeypatch.setattr(browser_evidence, "generate_basic", faulty_generate)
    result, report = run_browser_gate(tmp_path, plan)
    if hide_audit:
        assert result.returncode == 1 and report["passed"] is False, report
        assert "history-visible" in report["message"], report
        return
    assert result.returncode == 0, result.stdout + result.stderr
    require_business_evidence(plan.model_dump(), report, True)
    assert report["browser"]["real_browser"] is True
