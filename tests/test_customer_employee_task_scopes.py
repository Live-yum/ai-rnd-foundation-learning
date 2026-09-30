"""Actual generated API enforces both approved read-only employee task scopes."""

import json
import os
import subprocess
import sys

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env

SCENARIO = r"""
import getpass, json, sys
from fastapi.testclient import TestClient
import manage

scope = sys.argv[1]
password = 'Scope-Test-Password-123'
getpass.getpass = lambda _: password
manage.bootstrap_admin('admin')
from app import app

with TestClient(app) as client:
    def call(method, path, token=None, expected=200, **kwargs):
        response = client.request(
            method, path,
            headers={'Authorization': 'Bearer ' + token} if token else {},
            **kwargs,
        )
        assert response.status_code == expected, (method, path, response.status_code, response.text)
        data = response.json()
        if method == 'GET' and path.split('?')[0] == '/api/tasks' and expected == 200:
            assert int(response.headers['X-Total-Count']) == len(data)
        return data

    def login(username):
        return call('POST', '/auth/login', json={'username': username, 'password': password})['access_token']

    manager = login('admin')
    actors = {}
    # Real manager-created historical rows make own-scope reads non-vacuous.
    # No SQL seeding, impersonation, or employee task-create grant is used.
    for name, role in [('employee-a', 'manager'), ('employee-b', 'manager'),
                       ('service-a', 'service'), ('no-task-reader', 'observer'),
                       ('scoped-assigner', 'dispatcher')]:
        user = call('POST', '/business/users', manager, expected=201,
                    json={'username': name, 'password': password, 'role': role})
        actors[name] = {'id': user['id'], 'token': login(name)}

    customer = call('POST', '/api/customers', manager, expected=201,
                    json={'name': 'Scope customer', 'category': '企业'})
    requests = {}
    for name in ['employee-a', 'employee-b']:
        requests[name] = call('POST', '/api/requests', actors[name]['token'], expected=201,
                             json={'title': name + ' request', 'detail': 'Scope boundary',
                                   'customer_id': customer['id'], 'priority': '普通'})

    tasks = {}
    def create_task(name, creator, assignee=None):
        row = call('POST', '/api/tasks', creator, expected=201,
                   json={'title': 'Scope task ' + name, 'detail': 'Read-only scope boundary',
                         'request_id': requests['employee-a']['id']})
        if assignee is not None:
            row = call('POST', '/api/tasks/' + row['id'] + '/assign', manager,
                       json={'user_id': actors[assignee]['id']})
        tasks[name] = row

    # Creator and assignee deliberately disagree, so an own/assigned union or
    # fallback would leak a row and fail the exact expected-ID assertions below.
    create_task('own-a', actors['employee-a']['token'], 'service-a')
    create_task('own-b', actors['employee-b']['token'], 'service-a')
    if scope == 'own':
        create_task('assigned-a', manager, 'employee-a')
        create_task('assigned-b', manager, 'employee-b')
    create_task('unassigned', manager)
    assert tasks['own-a']['created_by'] == actors['employee-a']['id']
    assert tasks['own-a']['assignee_id'] != actors['employee-a']['id']
    assert tasks['unassigned']['assignee_id'] is None

    # The same issued tokens must immediately enforce the new employee role.
    for name in ['employee-a', 'employee-b']:
        call('PUT', '/business/users/' + actors[name]['id'] + '/role', manager,
             json={'role': 'employee'})
        assert call('GET', '/business/me', actors[name]['token'])['role'] == 'employee'

    if scope == 'assigned':
        # These are direct manager assignments to users already holding only
        # employee read permission. Role changes never bypass assignability.
        create_task('assigned-a', manager, 'employee-a')
        create_task('assigned-b', manager, 'employee-b')
    assert tasks['assigned-a']['created_by'] != actors['employee-a']['id']
    assert tasks['assigned-a']['assignee_id'] == actors['employee-a']['id']
    eligible_ids = {user['id'] for user in call('GET', '/business/users?entity=tasks', manager)}
    assert actors['service-a']['id'] in eligible_ids
    assert actors['no-task-reader']['id'] not in eligible_ids
    for name in ['employee-a', 'employee-b']:
        assert (actors[name]['id'] in eligible_ids) == (scope == 'assigned')
    unassigned_path = '/api/tasks/' + tasks['unassigned']['id']
    unassigned_history = call('GET', unassigned_path + '/history', manager)
    for target in ['no-task-reader'] + (['employee-a'] if scope == 'own' else []):
        call('POST', unassigned_path + '/assign', manager,
             expected=422, json={'user_id': actors[target]['id']})
        assert call('GET', unassigned_path, manager) == tasks['unassigned']
        assert call('GET', unassigned_path + '/history', manager) == unassigned_history

    manager_rows = call('GET', '/api/tasks', manager)
    assert {row['id'] for row in manager_rows} == {row['id'] for row in tasks.values()}
    before_history = {
        row['id']: call('GET', '/api/tasks/' + row['id'] + '/history', manager)
        for row in tasks.values()
    }
    before_notes = {
        row['id']: call('GET', '/api/tasks/' + row['id'] + '/notes', manager)
        for row in tasks.values()
    }
    manager_metrics = call('GET', '/business/metrics', manager)
    assert next(m for m in manager_metrics if m['name'] == 'task_scope_control')['value'] == 5

    denied_mutations = 0
    for suffix in ['a', 'b']:
        name = 'employee-' + suffix
        token = actors[name]['token']
        visible_name = ('own-' if scope == 'own' else 'assigned-') + suffix
        visible = tasks[visible_name]
        expected_ids = {visible['id']}
        permission = call('GET', '/schema', token)['permissions']['tasks']
        assert permission['actions'] == ['read'] and permission['scope'] == scope
        for path in ['/api/tasks', '/api/tasks?q=Scope', '/api/tasks?filter_task_state=new']:
            assert {row['id'] for row in call('GET', path, token)} == expected_ids
        for row in tasks.values():
            if row['id'] in expected_ids:
                assert call('GET', '/api/tasks/' + row['id'], token) == row
            else:
                call('GET', '/api/tasks/' + row['id'], token, expected=404)

        labels = call('POST', '/business/labels/tasks', token,
                      json={'record_ids': [row['id'] for row in tasks.values()]})
        assignee_name = next(name for name, actor in actors.items() if actor['id'] == visible['assignee_id'])
        assert labels == {
            'assignee_id': {visible['assignee_id']: assignee_name},
            'request_id': {requests['employee-a']['id']: requests['employee-a']['title']} if suffix == 'a' else {},
        }
        hidden_ids = [row['id'] for row in tasks.values() if row['id'] not in expected_ids]
        assert call('POST', '/business/labels/tasks', token, json={'record_ids': hidden_ids}) == {}

        # Employee requests remain own even when task reads use assigned scope.
        call('GET', '/api/requests/' + requests[name]['id'], token)
        other = 'employee-b' if suffix == 'a' else 'employee-a'
        call('GET', '/api/requests/' + requests[other]['id'], token, expected=404)
        if suffix == 'a':
            related = call('GET', '/business/related/requests/' + requests[name]['id'], token)
            task_group = next(group for group in related if group['entity'] == 'tasks')
            assert {row['id'] for row in task_group['records']} == expected_ids
        else:
            call('GET', '/business/related/requests/' + requests[other]['id'], token, expected=404)

        call('POST', '/api/tasks', token, expected=403,
             json={'title': 'Forbidden create', 'detail': 'Valid input', 'request_id': requests[name]['id']})
        denied_mutations += 1
        call('GET', '/business/users?entity=tasks', token, expected=403)
        call('GET', '/api/tasks/' + visible['id'] + '/history', token, expected=403)
        call('GET', '/api/tasks/' + visible['id'] + '/notes', token, expected=403)
        # Test forbidden writes against both an authorized and an unauthorized
        # row; valid payloads must reach action authorization rather than 422.
        for row in [visible, tasks['unassigned']]:
            path = '/api/tasks/' + row['id']
            for method, endpoint, kwargs in [
                ('PUT', path, {'json': {'title': 'Forbidden update'}}),
                ('POST', path + '/archive', {}),
                ('POST', path + '/notes', {'json': {'body': 'Forbidden note'}}),
                ('POST', path + '/assign', {'json': {'user_id': actors['service-a']['id']}}),
                ('POST', path + '/transition', {'json': {'transition': 'start'}}),
            ]:
                call(method, endpoint, token, expected=403, **kwargs)
                denied_mutations += 1
        # The shared metrics route filters unauthorized metrics rather than
        # returning 403. A declared nonempty manager control prevents a vacuous pass.
        assert call('GET', '/business/metrics', token) == []

    # Every denied request leaves rows, notes and immutable audit history intact.
    assert call('GET', '/api/tasks', manager) == manager_rows
    for row in tasks.values():
        path = '/api/tasks/' + row['id']
        assert call('GET', path, manager) == row
        assert call('GET', path + '/history', manager) == before_history[row['id']]
        assert call('GET', path + '/notes', manager) == before_notes[row['id']]

    if scope == 'assigned':
        # A real reassignment revokes all employee read surfaces immediately.
        row = tasks['assigned-a']
        call('POST', '/api/tasks/' + row['id'] + '/assign', manager,
             json={'user_id': actors['service-a']['id']})
        token = actors['employee-a']['token']
        call('GET', '/api/tasks/' + row['id'], token, expected=404)
        assert call('GET', '/api/tasks', token) == []
        assert call('POST', '/business/labels/tasks', token,
                    json={'record_ids': [row['id']]}) == {}
        related = call('GET', '/business/related/requests/' + requests['employee-a']['id'], token)
        assert next(group for group in related if group['entity'] == 'tasks')['records'] == []

    # A separate test-only approved assigner has assigned row scope. The target
    # eligibility change must not let an authorized assigner mutate a foreign row.
    scoped_token = actors['scoped-assigner']['token']
    foreign = tasks['own-a']
    call('POST', '/api/tasks/' + foreign['id'] + '/assign', scoped_token, expected=404,
         json={'user_id': actors['service-a']['id']})
    assert call('GET', '/api/tasks/' + foreign['id'], manager) == foreign
    assert call('GET', '/api/tasks/' + foreign['id'] + '/history', manager) == before_history[foreign['id']]
    control = tasks['unassigned']
    call('POST', '/api/tasks/' + control['id'] + '/assign', manager,
         json={'user_id': actors['scoped-assigner']['id']})
    moved = call('POST', '/api/tasks/' + control['id'] + '/assign', scoped_token,
                 json={'user_id': actors['service-a']['id']})
    assert moved['assignee_id'] == actors['service-a']['id']
    call('GET', '/api/tasks/' + control['id'], scoped_token, expected=404)

print(json.dumps({'passed': True, 'scope': scope, 'employees': 2, 'task_controls': 5,
                  'denied_mutations': denied_mutations, 'metrics_denied': True,
                  'request_own_preserved': True, 'audit_unchanged': True,
                  'foreign_row_assignment_denied': True}))
"""


@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_generated_employee_tasks_are_read_only_and_row_scoped(tmp_path, scope):
    raw = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    raw["business"]["roles"].extend(
        [
            {"name": "observer", "label": "No task access"},
            {"name": "dispatcher", "label": "Scoped test assigner"},
        ]
    )
    raw["business"]["permissions"].append(
        {
            "role": "dispatcher",
            "entity": "tasks",
            "actions": ["read", "assign"],
            "scope": "assigned",
        }
    )
    raw["business"]["permissions"] = [
        permission
        for permission in raw["business"]["permissions"]
        if (permission["role"], permission["entity"]) != ("employee", "tasks")
    ]
    raw["business"]["permissions"].append(
        {"role": "employee", "entity": "tasks", "actions": ["read"], "scope": scope}
    )
    raw["business"]["metrics"].append(
        {
            "name": "task_scope_control",
            "label": "Task scope control",
            "entity": "tasks",
            "kind": "count",
        }
    )
    plan = Plan.model_validate(raw)
    request_grant = next(
        grant
        for grant in plan.business.permissions
        if (grant.role, grant.entity) == ("employee", "requests")
    )
    assert request_grant.scope == "own"
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
        }
    )
    for command in [["manage.py", "init"], ["-c", SCENARIO, scope]]:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.splitlines()[-1]) == {
        "passed": True,
        "scope": scope,
        "employees": 2,
        "task_controls": 5,
        "denied_mutations": 22,
        "metrics_denied": True,
        "request_own_preserved": True,
        "audit_unchanged": True,
        "foreign_row_assignment_denied": True,
    }
