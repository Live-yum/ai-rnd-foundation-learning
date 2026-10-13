# scripts/sla_fixture.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.sla_fixture；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.core.contracts`、`workbench.planning.contracts`、`workbench.planning.feature_planner`、`workbench.planning.versioning`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `baseline`（L40–L65）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`。 返回路径：L41的`Plan.model_validate( { "title": "客户与工单SLA", "data_scope": "per_user", "acceptance": ["客户和工…`。
- `design`（L68–L216）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Selection().model_dump`、`Selection`、`CapabilityPlan.model_validate`、`digest`、`task.model_dump`、`FeatureOutline.model_validate`、`compile_v2`、`FeatureDesign`、`baseline`。 返回路径：L213的`compile_v2( FeatureDesign(outline=outline, baseline=baseline(), implementation=plan), exec…`。
- `authored_files`（L219–L230）：接收`task`、`before`。 控制顺序：L220按`task.id == "sla-api"`分支。 返回路径：L221的`{ "app.py": before + "\nfrom sla import install as install_sla\ninstall_sla(app, actor, en…`；L226的`{ "app.py": before + "\nfrom sla_dashboard import install as install_dashboard\ninstall_da…`。

</details>

**创建路径：** `scripts/sla_fixture.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L230。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9670`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/sla_fixture.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "02621ad20cde57b13a7f926c29d4c7ee74afa38f6e562942ea42bcb8aa9e0c28"} -->
````python
# scripts/sla_fixture.py
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
````
