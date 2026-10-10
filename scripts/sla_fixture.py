"""Audited customer/ticket SLA fixture, never a real-model completion claim."""

from workbench.catalog import Selection
from workbench.core.contracts import Plan, digest
from workbench.planning.contracts import CapabilityPlan
from workbench.planning.feature_planner import FeatureDesign, FeatureOutline
from workbench.planning.versioning import compile_v2

GOAL = "客户与工单基础管理；增加仅本人可见的特殊SLA看板，排除已解决工单，分别统计逾期和紧急逾期，重启后保留数据。"
SLA_SOURCE = """from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy import select


def install(app, actor, engine, metadata):
    # Initial creation only; no alteration of an existing table or dependency.
    metadata.create_all(engine)
    @app.get("/sla/summary")
    def summary(user=Depends(actor)):
        tickets = metadata.tables["tickets"]
        with engine.connect() as connection:
            rows = connection.execute(select(tickets).where(tickets.c.owner_id == user)).mappings().all()
        now = datetime.now(timezone.utc)
        overdue = [row for row in rows if row["status"] != "resolved" and datetime.fromisoformat(row["due_at"]).replace(tzinfo=timezone.utc) < now]
        return {"overdue": len(overdue), "urgent_overdue": sum(row["priority"] == "urgent" for row in overdue)}
"""
DASHBOARD_SOURCE = '''from fastapi.responses import HTMLResponse


def install(app):
    @app.get("/sla-dashboard", response_class=HTMLResponse)
    def dashboard():
        return """<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>特殊 SLA 看板</title>
        <h1>特殊 SLA 看板</h1><p>仅显示当前用户的未解决逾期工单。</p>
        <a href="/">返回客户与工单</a><label>账号 <input id="username" autocomplete="username"></label><label>密码 <input id="password" type="password" autocomplete="current-password"></label><button id="login">登录</button><button id="load">刷新</button><output id="result" aria-live="polite">尚未加载</output>
        <script>let token=sessionStorage.getItem('product-token')||'';document.getElementById('login').onclick=async()=>{const r=await fetch('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('username').value,password:document.getElementById('password').value})});if(r.ok){token=(await r.json()).access_token;sessionStorage.setItem('product-token',token);document.getElementById('load').click();}else document.getElementById('result').textContent='登录失败';};document.getElementById('load').onclick=async()=>{const r=await fetch('/sla/summary',{headers:{Authorization:'Bearer '+token}});const data=await r.json();document.getElementById('result').textContent=r.ok?'逾期 '+data.overdue+'；紧急逾期 '+data.urgent_overdue:'未授权';};</script></html>"""
'''


def baseline():
    return Plan.model_validate(
        {
            "title": "客户与工单SLA",
            "data_scope": "per_user",
            "acceptance": ["客户和工单CRUD及用户隔离"],
            "entities": [
                {
                    "name": "customers",
                    "description": "客户",
                    "fields": [{"name": "name", "kind": "text"}],
                },
                {
                    "name": "tickets",
                    "description": "工单",
                    "fields": [
                        {"name": "title", "kind": "text"},
                        {"name": "customer", "kind": "text"},
                        {"name": "due_at", "kind": "datetime"},
                        {"name": "status", "kind": "enum", "choices": ["open", "resolved"]},
                        {"name": "priority", "kind": "enum", "choices": ["normal", "urgent"]},
                    ],
                },
            ],
        }
    )


def design():
    selection = Selection().model_dump()
    refs = ["source-sla"]
    token = {"Authorization": "Bearer ${owner}"}
    summary = {
        "path": "/sla/summary",
        "headers": token,
        "status": 200,
        "equals": {"$.overdue": 1, "$.urgent_overdue": 1},
    }
    register = {
        "method": "POST",
        "path": "/auth/register",
        "body": {"username": "sla-${nonce}", "password": "authored-fixture-password"},
        "status": 201,
        "captures": {"owner": "$.access_token"},
    }
    create = {
        "method": "POST",
        "path": "/api/tickets",
        "headers": token,
        "body": {
            "title": "逾期-${nonce}",
            "customer": "客户A",
            "due_at": "2000-01-01T00:00:00Z",
            "status": "open",
            "priority": "urgent",
        },
        "status": 201,
    }
    plan = CapabilityPlan.model_validate(
        {
            "title": "SLA纵向升级",
            "summary": GOAL,
            "selection": selection,
            "source_digest": digest(GOAL),
            "tasks": [
                {
                    "id": "sla-api",
                    "title": "独立SLA统计",
                    "requirements": refs,
                    "files": ["app.py", "sla.py"],
                    "contract": GOAL,
                    "scenarios": ["sla-api-check"],
                },
                {
                    "id": "sla-dashboard",
                    "title": "SLA浏览器看板",
                    "requirements": refs,
                    "files": ["app.py", "sla_dashboard.py"],
                    "contract": "保留基础后台，通过认证API展示SLA指标",
                    "scenarios": ["sla-dashboard-check"],
                    "depends_on": ["sla-api"],
                },
            ],
            "runtime": {
                "start": {
                    "argv": [
                        "./.venv/bin/python",
                        "-m",
                        "uvicorn",
                        "app:app",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        "8123",
                    ]
                },
                "port": 8123,
                "database_tables": ["customers", "tickets"],
            },
            "scenarios": [
                {
                    "id": "sla-api-check",
                    "title": "SLA认证与统计",
                    "requirements": refs,
                    "steps": [register, create, summary, {"path": "/sla/summary", "status": 401}],
                    "after_restart": [summary],
                },
                {
                    "id": "sla-dashboard-check",
                    "title": "真实页面展示统计",
                    "requirements": refs,
                    "steps": [
                        {
                            **register,
                            "body": {**register["body"], "username": "dashboard-${nonce}"},
                        },
                        create,
                        summary,
                    ],
                    "after_restart": [summary],
                    "browser": [
                        {"action": "open", "value": "/sla-dashboard"},
                        {"action": "fill", "selector": "#username", "value": "dashboard-${nonce}"},
                        {
                            "action": "fill",
                            "selector": "#password",
                            "value": "authored-fixture-password",
                        },
                        {"action": "click", "selector": "#login"},
                        {"action": "click", "selector": "#load"},
                        {"action": "text", "selector": "#result", "value": "逾期 1；紧急逾期 1"},
                    ],
                },
            ],
        }
    )
    modules = [
        {
            **task.model_dump(),
            "adapter": "python-basic",
            "extension": "approved-source-module",
            "interfaces": [task.contract],
        }
        for task in plan.tasks
    ]
    outline = FeatureOutline.model_validate(
        {
            "summary": GOAL,
            "selection": selection,
            "source_digest": plan.source_digest,
            "features": [
                {
                    "id": "baseline-crud",
                    "title": "客户工单CRUD",
                    "requirements": refs,
                    "route": "native",
                    "capability": "typed-crud",
                },
                *[
                    {
                        "id": task.id,
                        "title": task.title,
                        "requirements": refs,
                        "route": "module",
                        "capability": "approved-source-module",
                        "module_id": task.id,
                    }
                    for task in plan.tasks
                ],
            ],
            "modules": modules,
        }
    )
    return compile_v2(
        FeatureDesign(outline=outline, baseline=baseline(), implementation=plan),
        executor="mini_swe",
    )


def authored_files(task, before):
    if task.id == "sla-api":
        return {
            "app.py": before
            + "\nfrom sla import install as install_sla\ninstall_sla(app, actor, engine, metadata)\n",
            "sla.py": SLA_SOURCE,
        }
    return {
        "app.py": before
        + "\nfrom sla_dashboard import install as install_dashboard\ninstall_dashboard(app)\n",
        "sla_dashboard.py": DASHBOARD_SOURCE,
    }
