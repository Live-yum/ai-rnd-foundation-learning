# tests/test_business_python.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `runtime_plan`（L16–L39）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L18遍历`raw["business"]["permissions"]`；L19按`permission["role"] == "manager"`分支；L30按`permission["role"] == "service"`分支；L32按`permission["role"] == "employee"`分支；L34遍历`["employee", "service"]`。 调用`business_plan`、`raw["business"]["permissions"].append`、`Plan.model_validate`。 返回路径：L39的`Plan.model_validate(raw)`。
- `test_generated_business_api_transactions_and_permissions`（L187–L226）：接收`tmp_path`、`monkeypatch`。 控制顺序：L208断言`init.returncode == 0`；L218断言`result.returncode == 0`；L219断言`json.loads(result.stdout.splitlines()[-1])["passed"]`；L220遍历`["sqlite", "postgresql"]`；L222断言`"business_audit" in sql and "business_notifications" in sql and "FOREIGN KEY(customer…`。 调用`monkeypatch.setattr`、`generate_basic`、`runtime_plan`、`clean_env`、`os.environ.get`、`str`、`subprocess.run`、`json.loads`、`result.stdout.splitlines`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_common_metric_normalizes_datetime_predicate_offsets`（L229–L252）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L239遍历`["eq", "gte", "lte", "in"]`；L252断言`policy.metric(rows, metric)["value"] == 1`。 调用`Path`、`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`module.Policy`、`runtime_plan().model_dump`、`runtime_plan`、`policy.metric`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_business_postgres_actual_fk_and_permissions`（L256–L302）：接收`tmp_path`。 控制顺序：L263按`not url`分支；L291断言`init.returncode == 0`；L301断言`result.returncode == 0`；L302断言`json.loads(result.stdout.splitlines()[-1])["passed"]`。 调用`os.getenv`、`pytest.skip`、`Settings`、`SecretStr`、`database`、`generate_basic`、`runtime_plan`、`clean_env`、`os.environ.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_customer_service_example_three_resources`（L395–L431）：接收`tmp_path`、`monkeypatch`。 控制顺序：L420断言`init.returncode == 0`；L430断言`result.returncode == 0`；L431断言`json.loads(result.stdout.splitlines()[-1])["three_resources"]`。 调用`monkeypatch.setattr`、`Path`、`Plan.model_validate_json`、`path.read_text`、`generate_basic`、`clean_env`、`os.environ.get`、`str`、`subprocess.run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_business_api_only_independent_receipt`（L434–L462）：接收`tmp_path`。 控制顺序：L457断言`result.returncode == 0`；L459断言`receipt["passed"] and receipt["http"] and receipt["restart"]`；L460断言`receipt["business"]["resources_checked"] == ["customers", "requests", "tasks"]`；L461断言`receipt["browser"]["applicable"] is False`；L462断言`not receipt["browser"].get("real_browser")`。 调用`Plan.model_validate_json`、`(Path(__file__).parents[1] / "examples/plans/customer-service.jso…`、`Path`、`generate_basic`、`clean_env`、`os.environ.get`、`subprocess.run`、`str`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_business_postgres_independent_receipt`（L466–L513）：接收`tmp_path`。 控制顺序：L475按`not url`分支；L509断言`result.returncode == 0`；L511断言`receipt["passed"] and receipt["business"]["passed"] and receipt["restart"]`；L512断言`receipt["database"] == "real-isolated-postgresql"`；L513断言`receipt["browser"]["applicable"] is False`。 调用`os.getenv`、`pytest.skip`、`Settings`、`SecretStr`、`Plan.model_validate_json`、`(Path(__file__).parents[1] / "examples/plans/customer-service.jso…`、`Path`、`database`、`generate_basic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_python.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L513。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26781`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_python.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1aa0c9d1ac9abae1d22ec805f73094ca5c3fd5eab4334eac9d7a145e1be9b400"} -->
````python
# tests/test_business_python.py
"""Real generated Python product HTTP/SQL behavior in an isolated interpreter."""

import json
import os
import subprocess
import sys

import pytest
from test_business_contracts import business_plan

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env


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
    assert [e['actor_username'] for e in events]==['employee-a','admin','service-a','service-a','service-a']
    limited=call('GET',f'/api/requests/{identity}/history',employee).json()
    assert all('after' not in e and 'before' not in e for e in limited)
    assert [e['actor_username'] for e in limited]==[e['actor_username'] for e in events]
    assert call('GET',f'/api/requests/{identity}/history',outsider).status_code==404
    assert call('GET',f'/api/requests/{identity}/history',actors['service-b']['token']).status_code==404
    notes=call('GET',f'/api/requests/{identity}/notes',employee).json()
    assert [n['actor_username'] for n in notes]==['service-a']
    assert not any('password' in row or 'role' in row for row in events+notes)
    assert 'employee-b' not in json.dumps(events+notes)
    # Label enrichment is presentation-only: exact stored snapshots and IDs survive reads.
    with engine.connect() as conn:
        audit=metadata.tables['business_audit']
        stored={r['id']:dict(r) for r in conn.execute(select(audit).where(audit.c.record_id==identity)).mappings()}
    for entry in events:
        original=stored[entry['id']]
        assert entry['actor_id']==original['actor_id'] and entry['action']==original['action']
        assert entry['created_at']==original['created_at']
        for key in ['before','after']:
            assert entry[key]==(json.loads(original[key+'_json']) if original[key+'_json'] else None)
    assert call('GET',f'/api/requests/{identity}/history',manager).json()==events
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
    # More than one lookup batch, with all IDs derived from this record's visible notes.
    from sqlalchemy import event as sql_event
    with engine.begin() as conn:
        for index in range(105):
            actor_id=f'history-actor-{index:03d}'
            conn.execute(insert(metadata.tables['users']).values(id=actor_id,username=actor_id,password='synthetic-unused',role='employee'))
            conn.execute(insert(metadata.tables['business_notes']).values(id=f'history-note-{index:03d}',entity='requests',record_id=identity,actor_id=actor_id,created_at='2026-01-01T00:00:00.000000Z',body='Synthetic batching check'))
    lookups=[]
    def capture_lookup(connection,cursor,statement,parameters,context,executemany):
        if 'users.id IN (' in statement and 'users.username' in statement:
            assert 'users.password' not in statement and 'users.role' not in statement
            lookups.append(len(parameters))
    sql_event.listen(engine,'before_cursor_execute',capture_lookup)
    try:
        assert call('GET',f'/api/requests/{identity}/notes',outsider).status_code==404
        assert lookups==[]
        authorized=call('GET',f'/api/requests/{identity}/notes',employee).json()
        assert len(authorized)==106 and sorted(lookups)==[6,100],lookups
        assert {n['actor_username'] for n in authorized}=={'service-a'}|{f'history-actor-{index:03d}' for index in range(105)}
    finally:
        sql_event.remove(engine,'before_cursor_execute',capture_lookup)
print(json.dumps({'passed':True,'roles':3,'row_acl':True,'fk':True,'transitions':True,'audit':True,'notes':True,'notifications':True,'scoped_metrics':True}))
"""


def test_generated_business_api_transactions_and_permissions(tmp_path, monkeypatch):
    # Windows may default to cp1252 even though clean_env makes the child emit UTF-8.
    # Force that parent default on every platform so missing wire encoding regresses locally.
    monkeypatch.setattr(subprocess, "_text_encoding", lambda: "cp1252")
    product = tmp_path / "product"
    generate_basic(runtime_plan(), product)
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
        }
    )
    init = subprocess.run(
        [sys.executable, "manage.py", "init"],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert init.returncode == 0, init.stdout + init.stderr
    result = subprocess.run(
        [sys.executable, "-c", SCENARIO],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
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
        env = clean_env(
            {
                "PATH": os.environ.get("PATH", ""),
                "PRODUCT_DATA_DIR": str(tmp_path / "pg-data"),
                "PRODUCT_DATABASE_URL": isolated_url,
                "PYTHONUTF8": "1",
            }
        )
        init = subprocess.run(
            [sys.executable, "manage.py", "init"],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        assert init.returncode == 0, init.stdout + init.stderr
        result = subprocess.run(
            [sys.executable, "-c", SCENARIO],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
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
 assert call('POST','/api/customers',a,json={'name':'Forbidden','category':'个人'}).status_code==403
 assert call('PUT',f'/api/customers/{customer["id"]}',a,json={'name':'Forbidden'}).status_code==403
 assert call('POST',f'/api/customers/{customer["id"]}/notes',a,json={'body':'Forbidden'}).status_code==403
 personal=call('POST','/api/customers',manager,json={'name':'Personal customer','category':'个人'}).json()
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
 def notices(token,entity,identity,event):
  return {n['id']:n for n in call('GET','/business/notifications',token).json() if n['entity']==entity and n['record_id']==identity and n['event']==event}
 for entity,identity,actor,creator,other in [('tasks',task_id,b,manager,a),('requests',first_request,a,first,b)]:
  for event in ['assigned','due']:
   received=notices(actor,entity,identity,event)
   assert len(received)==1,(entity,event,received)
   assert set(notices(actor,entity,identity,event))==set(received)
   notice_id=next(iter(received))
   assert call('POST',f'/business/notifications/{notice_id}/read',other).status_code==404
   assert call('POST',f'/business/notifications/{notice_id}/read',actor).status_code==200
   assert notices(actor,entity,identity,event)[notice_id]['read_at']
  before=set(notices(creator,entity,identity,'note_added'))
  note=call('POST',f'/api/{entity}/{identity}/notes',actor,json={'body':'Handling progress'})
  assert note.status_code==201,note.text
  received=notices(creator,entity,identity,'note_added')
  assert len(set(received)-before)==1,(entity,received)
  assert set(notices(creator,entity,identity,'note_added'))==set(received)
  notice_id=next(iter(set(received)-before))
  assert call('POST',f'/business/notifications/{notice_id}/read',other).status_code==404
  assert call('POST',f'/business/notifications/{notice_id}/read',creator).status_code==200
  assert notices(creator,entity,identity,'note_added')[notice_id]['read_at']
  assert not notices(other,entity,identity,'note_added')
  for transition in ['start','resolve']:
   before=set(notices(creator,entity,identity,'transitioned'))
   assert call('POST',f'/api/{entity}/{identity}/transition',actor,json={'transition':transition}).status_code==200
   assert len(set(notices(creator,entity,identity,'transitioned'))-before)==1,(entity,transition)
  history=call('GET',f'/api/{entity}/{identity}/history',manager).json()
  assert history[-1]['action']=='transitioned:resolve'
  assert history[-1]['after']['resolved_at']
 metrics={x['name']:x for x in call('GET','/business/metrics',manager).json()}
 assert metrics['total']['value']==2 and metrics['customer_total']['value']==2
 assert metrics['resolved_total']['value']==1
 assert sorted(metrics['customer_categories']['groups'],key=lambda x:x['key'])==sorted([{'key':'企业','count':1},{'key':'个人','count':1}],key=lambda x:x['key'])
 assert metrics['resolution']['samples']==1 and metrics['resolution']['value']>=0
 assert metrics['by_customer']['groups']==[{'key':customer['id'],'count':2}]
 assert sum(x['count'] for x in metrics['daily']['groups'])==2
 assert {x['name']:x for x in call('GET','/business/metrics',a).json()}['total']['value']==1
 assert {x['name']:x for x in call('GET','/business/metrics',b).json()}['total']['value']==0
 assert call('GET','/business/metrics',first).json()==[]
 assert len(notices(b,'tasks',task_id,'due'))==1
 assert not notices(b,'requests',first_request,'due')
 labels=call('POST','/business/labels/requests',first,json={'record_ids':[first_request,other_request]}).json()
 assert labels['customer_id']=={customer['id']:'Enterprise customer'}
 assert labels['assignee_id']=={actors['agent-a']['id']:'agent-a'}
 assert call('POST','/business/labels/requests',b,json={'record_ids':[first_request]}).json()=={}
 assert call('POST','/business/labels/tasks',first,json={'record_ids':[task_id]}).status_code==403
 assert call('POST','/business/labels/requests',first,json={'record_ids':[first_request]*101}).status_code==422
print(json.dumps({'passed':True,'three_resources':True,'linked_row_acl':True,'tasks':True,'metrics':len(metrics)}))
"""


def test_exact_customer_service_example_three_resources(tmp_path, monkeypatch):
    # Windows may default to cp1252 even though clean_env makes the child emit UTF-8.
    # Force that parent default on every platform so missing wire encoding regresses locally.
    monkeypatch.setattr(subprocess, "_text_encoding", lambda: "cp1252")
    from pathlib import Path

    path = Path(__file__).parents[1] / "examples/plans/customer-service.json"
    plan = Plan.model_validate_json(path.read_text(encoding="utf-8"))
    product = tmp_path / "customer-product"
    generate_basic(plan, product)
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
        }
    )
    init = subprocess.run(
        [sys.executable, "manage.py", "init"],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert init.returncode == 0, init.stdout + init.stderr
    result = subprocess.run(
        [sys.executable, "-c", CUSTOMER_SCENARIO],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
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
    env = clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"})
    result = subprocess.run(
        [sys.executable, "verify.py", "--report", str(report)],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
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
        env = clean_env(
            {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONUTF8": "1",
                "VERIFY_DATABASE_URL": isolated_url,
            }
        )
        result = subprocess.run(
            [sys.executable, "verify.py", "--report", str(report)],
            cwd=product,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=180,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        receipt = json.loads(report.read_text(encoding="utf-8"))
        assert receipt["passed"] and receipt["business"]["passed"] and receipt["restart"]
        assert receipt["database"] == "real-isolated-postgresql"
        assert receipt["browser"]["applicable"] is False
````
