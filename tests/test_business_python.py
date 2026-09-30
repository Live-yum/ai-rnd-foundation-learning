"""Real generated Python product HTTP/SQL behavior in an isolated interpreter."""

import json
import os
import subprocess
import sys

import pytest
from test_business_contracts import business_plan

from workbench.domain import Plan
from workbench.generator import generate_basic


def runtime_plan():
    raw = business_plan()
    for permission in raw["business"]["permissions"]:
        if permission["role"] == "manager":
            permission["actions"] = [
                "create",
                "read",
                "update",
                "archive",
                "add_note",
                "read_history",
                "read_audit",
                "read_metrics",
            ] + (["assign", "transition"] if permission["entity"] == "requests" else [])
        if permission["role"] == "service":
            permission["actions"] += ["update", "read_history", "read_metrics"]
        if permission["role"] == "employee":
            permission["actions"] += ["add_note", "read_metrics"]
    for role in ["employee", "service"]:
        raw["business"]["permissions"].append(
            {"role": role, "entity": "customers", "actions": ["read"], "scope": "all"}
        )
    raw["entities"][0]["fields"][0]["searchable"] = True
    return Plan.model_validate(raw)


SCENARIO = r"""
import getpass,json
from fastapi.testclient import TestClient
from sqlalchemy import delete,insert,select
from sqlalchemy.exc import IntegrityError
import manage
getpass.getpass=lambda _: 'Example-Test-Password-123'
manage.bootstrap_admin('admin')
try:
    manage.bootstrap_admin('second-admin')
except SystemExit:
    pass
else:
    raise AssertionError('bootstrap repeated')
from app import app
from schema import engine,metadata
with TestClient(app) as c:
    def call(method,path,token=None,**kw):
        response=c.request(method,path,headers={'Authorization':'Bearer '+token} if token else {},**kw)
        return response
    def login(name):
        r=call('POST','/auth/login',json={'username':name,'password':'Example-Test-Password-123'})
        assert r.status_code==200,r.text
        return r.json()['access_token']
    manager=login('admin')
    actors={}
    for name,role in [('service-a','service'),('service-b','service'),('employee-a','employee'),('employee-b','employee')]:
        r=call('POST','/business/users',manager,json={'username':name,'password':'Example-Test-Password-123','role':role})
        assert r.status_code==201,r.text
        actors[name]={'id':r.json()['id'],'token':login(name)}
    employee=actors['employee-a']['token']; service=actors['service-a']['token']; outsider=actors['employee-b']['token']
    r=call('POST','/auth/register',json={'username':'public','password':'Example-Test-Password-123','role':'manager'})
    assert r.status_code==422,r.text
    r=call('POST','/auth/register',json={'username':'public','password':'Example-Test-Password-123'})
    assert r.status_code==201,r.text
    assert call('GET','/business/me',r.json()['access_token']).json()['role']=='employee'
    assert call('GET','/business/users',employee).status_code==403
    assert call('POST','/business/users',employee,json={'username':'hacker','password':'Example-Test-Password-123','role':'manager'}).status_code==403
    customer=call('POST','/api/customers',manager,json={'name':'Acme'}).json()
    assert call('GET','/api/customers?q=Acme',employee).json()[0]['id']==customer['id']
    assert call('POST','/api/customers',employee,json={'name':'forbidden'}).status_code==403
    r=call('POST','/api/requests',employee,json={'customer_id':customer['id'],'due_at':'2020-01-01T00:00:00Z'})
    assert r.status_code==201,r.text
    item=r.json(); identity=item['id']
    assert item['request_state']=='new' and item['created_by']==actors['employee-a']['id']
    assert item['created_at'] and item['updated_at'] and item['resolved_at'] is None
    assert call('GET','/api/requests/'+identity,outsider).status_code==404
    assert call('GET','/api/requests/'+identity,service).status_code==404
    assert call('GET','/api/requests',outsider).json()==[]
    assert call('GET',f'/business/related/customers/{customer["id"]}',outsider).json()[0]['records']==[]
    for protected in ['created_by','created_at','updated_at','archived_at','owner_id','request_state','assignee_id','resolved_at']:
        assert call('PUT','/api/requests/'+identity,manager,json={protected:'forged'}).status_code==422,protected
    assert call('POST','/api/requests',employee,json={'customer_id':'missing'}).status_code==404
    assert call('POST',f'/api/requests/{identity}/assign',employee,json={'user_id':actors['service-a']['id']}).status_code==403
    assert call('POST',f'/api/requests/{identity}/assign',manager,json={'user_id':actors['employee-b']['id']}).status_code==422
    r=call('POST',f'/api/requests/{identity}/assign',manager,json={'user_id':actors['service-a']['id']})
    assert r.status_code==200,r.text
    assert call('GET','/api/requests/'+identity,service).status_code==200
    assert call('GET','/api/requests',actors['service-b']['token']).json()==[]
    assert call('POST',f'/api/requests/{identity}/transition',service,json={'transition':'resolve'}).status_code==409
    assert call('POST',f'/api/requests/{identity}/transition',employee,json={'transition':'start'}).status_code==403
    assert call('POST',f'/api/requests/{identity}/transition',service,json={'transition':'start'}).status_code==200
    r=call('POST',f'/api/requests/{identity}/notes',service,json={'body':'Working on it','actor_id':actors['employee-b']['id']})
    assert r.status_code==422
    r=call('POST',f'/api/requests/{identity}/notes',service,json={'body':'Working on it'})
    assert r.status_code==201,r.text
    assert r.json()['actor_id']==actors['service-a']['id']
    assert call('GET',f'/api/requests/{identity}/notes',outsider).status_code==404
    reminders=call('GET','/business/notifications',service).json()
    assert {x['event'] for x in reminders}=={'assigned','due'},reminders
    assert len(call('GET','/business/notifications',service).json())==len(reminders)
    assert call('POST',f'/business/notifications/{reminders[0]["id"]}/read',outsider).status_code==404
    assert call('POST',f'/business/notifications/{reminders[0]["id"]}/read',service).status_code==200
    resolved=call('POST',f'/api/requests/{identity}/transition',service,json={'transition':'resolve'})
    assert resolved.status_code==200,resolved.text
    assert resolved.json()['resolved_at'] and resolved.json()['request_state']=='resolved'
    assert call('POST',f'/api/requests/{identity}/transition',service,json={'transition':'resolve'}).status_code==409
    events=call('GET',f'/api/requests/{identity}/history',manager).json()
    assert [e['action'] for e in events]==['created','assigned','transitioned:start','note_added','transitioned:resolve'],events
    assert all(e['actor_id'] and e['created_at'] for e in events)
    assert all('after' not in e for e in call('GET',f'/api/requests/{identity}/history',employee).json())
    assert 'transitioned' in [n['event'] for n in call('GET','/business/notifications',employee).json()]
    stats={x['name']:x for x in call('GET','/business/metrics',manager).json()}
    assert stats['total']['value']==1 and stats['resolution']['samples']==1 and stats['resolution']['value']>=0,stats
    outside={x['name']:x for x in call('GET','/business/metrics',outsider).json()}
    assert outside['total']['value']==0 and outside['resolution']['value'] is None,outside
    assert call('DELETE','/api/requests/'+identity,manager).status_code==405
    assert call('POST',f'/api/requests/{identity}/archive',manager).status_code==200
    assert call('GET','/api/requests/'+identity,manager).status_code==404
    assert len(call('GET',f'/api/requests/{identity}/history',manager).json())==6
    with engine.begin() as conn:
        try:
            with conn.begin_nested():
                conn.execute(delete(metadata.tables['customers']).where(metadata.tables['customers'].c.id==customer['id']))
        except IntegrityError:
            pass
        else:
            raise AssertionError('actual FK did not restrict deletion')
    own=call('GET','/business/me',manager).json()['id']
    assert call('PUT',f'/business/users/{own}/role',manager,json={'role':'employee'}).status_code==409
print(json.dumps({'passed':True,'roles':3,'row_acl':True,'fk':True,'transitions':True,'audit':True,'notes':True,'notifications':True,'scoped_metrics':True}))
"""


def test_generated_business_api_transactions_and_permissions(tmp_path):
    product = tmp_path / "product"
    generate_basic(runtime_plan(), product)
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PRODUCT_DATA_DIR": str(tmp_path / "db"),
        "PYTHONUTF8": "1",
    }
    init = subprocess.run(
        [sys.executable, "manage.py", "init"], cwd=product, env=env, text=True, capture_output=True
    )
    assert init.returncode == 0, init.stdout + init.stderr
    result = subprocess.run(
        [sys.executable, "-c", SCENARIO],
        cwd=product,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.splitlines()[-1])["passed"]
    for dialect in ["sqlite", "postgresql"]:
        sql = (product / "database" / f"schema.{dialect}.sql").read_text(encoding="utf-8")
        assert (
            "business_audit" in sql
            and "business_notifications" in sql
            and "FOREIGN KEY(customer_id)" in sql
        )


def test_common_metric_normalizes_datetime_predicate_offsets():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).parents[1] / "templates/business/common/policy.py"
    spec = importlib.util.spec_from_file_location("business_policy_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = module.Policy(runtime_plan().model_dump())
    rows = [{"created_at": "2026-01-01T00:00:00.000000Z"}]
    for operator in ["eq", "gte", "lte", "in"]:
        value = "2026-01-01T01:00:00+01:00"
        metric = {
            "entity": "requests",
            "kind": "count",
            "filters": [
                {
                    "field": "created_at",
                    "op": operator,
                    "value": [value] if operator == "in" else value,
                }
            ],
        }
        assert policy.metric(rows, metric)["value"] == 1


@pytest.mark.postgres
def test_generated_business_postgres_actual_fk_and_permissions(tmp_path):
    from pydantic import SecretStr

    from workbench.postgres_lab import database
    from workbench.settings import Settings

    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; mandatory in PostgreSQL Actions job")
    settings = Settings(
        data_dir=tmp_path / "state", product_postgres_url=SecretStr(url), _env_file=None
    )
    with database(settings) as isolated_url:
        product = tmp_path / "postgres-product"
        generate_basic(
            runtime_plan(),
            product,
            {"template": "python-basic", "frontend": "simple-admin", "database": "postgresql"},
        )
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "pg-data"),
            "PRODUCT_DATABASE_URL": isolated_url,
            "PYTHONUTF8": "1",
        }
        init = subprocess.run(
            [sys.executable, "manage.py", "init"],
            cwd=product,
            env=env,
            text=True,
            capture_output=True,
        )
        assert init.returncode == 0, init.stdout + init.stderr
        result = subprocess.run(
            [sys.executable, "-c", SCENARIO],
            cwd=product,
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout.splitlines()[-1])["passed"]


CUSTOMER_SCENARIO = r"""
import getpass,json
from fastapi.testclient import TestClient
import manage
getpass.getpass=lambda _: 'Example-Test-Password-123'
manage.bootstrap_admin('admin')
from app import app
with TestClient(app) as c:
 def call(method,path,token=None,**kw):return c.request(method,path,headers={'Authorization':'Bearer '+token} if token else {},**kw)
 def login(name):return call('POST','/auth/login',json={'username':name,'password':'Example-Test-Password-123'}).json()['access_token']
 manager=login('admin');actors={}
 for name,role in [('first','employee'),('second','employee'),('agent-a','service'),('agent-b','service')]:
  r=call('POST','/business/users',manager,json={'username':name,'password':'Example-Test-Password-123','role':role});assert r.status_code==201,r.text
  actors[name]={'id':r.json()['id'],'token':login(name)}
 first,second,a,b=[actors[name]['token'] for name in ['first','second','agent-a','agent-b']]
 customer=call('POST','/api/customers',manager,json={'name':'Enterprise customer','organization':'Org','contact':'internal test','category':'企业'}).json()
 requests=[]
 for owner,title in [(first,'First request'),(second,'Other request')]:
  r=call('POST','/api/requests',owner,json={'title':title,'detail':'Needs service','customer_id':customer['id'],'priority':'普通','due_at':'2020-01-01T00:00:00Z'});assert r.status_code==201,r.text
  requests.append(r.json())
 first_request=requests[0]['id'];other_request=requests[1]['id']
 assert call('POST',f'/api/requests/{first_request}/assign',manager,json={'user_id':actors['agent-a']['id']}).status_code==200
 task=call('POST','/api/tasks',manager,json={'title':'Linked work','detail':'Follow up','request_id':first_request,'due_at':'2020-01-01T00:00:00Z'})
 assert task.status_code==201,task.text
 task=task.json();task_id=task['id']
 assert call('POST',f'/api/tasks/{task_id}/assign',manager,json={'user_id':actors['agent-b']['id']}).status_code==200
 assert call('GET',f'/api/tasks/{task_id}',a).status_code==404
 assert call('GET',f'/api/tasks/{task_id}',first).status_code==403
 assert call('GET',f'/api/requests/{first_request}',b).status_code==404
 assert call('PUT',f'/api/tasks/{task_id}',b,json={'detail':'Work can proceed without reading another assignee’s request'}).status_code==200
 assert call('PUT',f'/api/tasks/{task_id}',b,json={'request_id':other_request}).status_code==404
 assert len(call('GET',f'/business/related/customers/{customer["id"]}',manager).json()[0]['records'])==2
 assert len(call('GET',f'/business/related/customers/{customer["id"]}',first).json()[0]['records'])==1
 assert call('GET',f'/business/related/requests/{first_request}',first).json()==[]
 assert len(call('GET',f'/business/related/requests/{first_request}',manager).json()[0]['records'])==1
 note=call('POST',f'/api/tasks/{task_id}/notes',b,json={'body':'Task progress'})
 assert note.status_code==201,note.text
 assert call('GET',f'/api/tasks/{task_id}/notes',a).status_code==404
 for entity,identity,actor in [('tasks',task_id,b),('requests',first_request,a)]:
  assert call('POST',f'/api/{entity}/{identity}/transition',actor,json={'transition':'start'}).status_code==200
  assert call('POST',f'/api/{entity}/{identity}/transition',actor,json={'transition':'resolve'}).status_code==200
  history=call('GET',f'/api/{entity}/{identity}/history',manager).json()
  assert history[-1]['action']=='transitioned:resolve'
  assert history[-1]['after']['resolved_at']
 metrics={x['name']:x for x in call('GET','/business/metrics',manager).json()}
 assert metrics['total']['value']==2 and metrics['customer_total']['value']==1
 assert metrics['resolution']['samples']==1 and metrics['resolution']['value']>=0
 assert metrics['by_customer']['groups']==[{'key':customer['id'],'count':2}]
 assert sum(x['count'] for x in metrics['daily']['groups'])==2
 assert {x['name']:x for x in call('GET','/business/metrics',a).json()}['total']['value']==1
 assert {x['name']:x for x in call('GET','/business/metrics',b).json()}['total']['value']==0
 assert call('GET','/business/metrics',first).json()==[]
 assert all(x['event']!='due' for x in call('GET','/business/notifications',b).json())
print(json.dumps({'passed':True,'three_resources':True,'linked_row_acl':True,'tasks':True,'metrics':5}))
"""


def test_exact_customer_service_example_three_resources(tmp_path):
    from pathlib import Path

    path = Path(__file__).parents[1] / "examples/plans/customer-service.json"
    plan = Plan.model_validate_json(path.read_text(encoding="utf-8"))
    product = tmp_path / "customer-product"
    generate_basic(plan, product)
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PRODUCT_DATA_DIR": str(tmp_path / "db"),
        "PYTHONUTF8": "1",
    }
    init = subprocess.run(
        [sys.executable, "manage.py", "init"], cwd=product, env=env, text=True, capture_output=True
    )
    assert init.returncode == 0, init.stdout + init.stderr
    result = subprocess.run(
        [sys.executable, "-c", CUSTOMER_SCENARIO],
        cwd=product,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.splitlines()[-1])["three_resources"]


def test_customer_business_api_only_independent_receipt(tmp_path):
    from pathlib import Path

    plan = Plan.model_validate_json(
        (Path(__file__).parents[1] / "examples/plans/customer-service.json").read_text(
            encoding="utf-8"
        )
    )
    product = tmp_path / "api-product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    report = tmp_path / "report.json"
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"}
    result = subprocess.run(
        [sys.executable, "verify.py", "--report", str(report)],
        cwd=product,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(report.read_text(encoding="utf-8"))
    assert receipt["passed"] and receipt["http"] and receipt["restart"]
    assert receipt["business"]["resources_checked"] == ["customers", "requests", "tasks"]
    assert receipt["browser"]["applicable"] is False
    assert not receipt["browser"].get("real_browser")


@pytest.mark.postgres
def test_customer_business_postgres_independent_receipt(tmp_path):
    from pathlib import Path

    from pydantic import SecretStr

    from workbench.postgres_lab import database
    from workbench.settings import Settings

    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; mandatory in PostgreSQL Actions job")
    settings = Settings(
        data_dir=tmp_path / "state", product_postgres_url=SecretStr(url), _env_file=None
    )
    plan = Plan.model_validate_json(
        (Path(__file__).parents[1] / "examples/plans/customer-service.json").read_text(
            encoding="utf-8"
        )
    )
    with database(settings) as isolated_url:
        product = tmp_path / "api-product"
        generate_basic(
            plan,
            product,
            {"template": "python-basic", "frontend": "api-only", "database": "postgresql"},
        )
        report = tmp_path / "report.json"
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONUTF8": "1",
            "VERIFY_DATABASE_URL": isolated_url,
        }
        result = subprocess.run(
            [sys.executable, "verify.py", "--report", str(report)],
            cwd=product,
            env=env,
            text=True,
            capture_output=True,
            timeout=180,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        receipt = json.loads(report.read_text(encoding="utf-8"))
        assert receipt["passed"] and receipt["business"]["passed"] and receipt["restart"]
        assert receipt["database"] == "real-isolated-postgresql"
        assert receipt["browser"]["applicable"] is False
