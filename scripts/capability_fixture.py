"""Explicit authored source/model fixture for real custom-node acceptance.

It proves the generic execution path with a small real app, not completion of
the much larger competition request or success against a paid model/provider.
"""

from workbench.capability_contracts import (
    CapabilityEdits,
    CapabilityOutline,
    CapabilityPlan,
    CapabilityScenarioBatch,
)
from workbench.domain import Plan
from workbench.feature_planning import FeatureOutline

GOAL = "实现用户登录后创建和保存自己的资料。队主可给同组成员只读访问，并隐藏共享视图中的创建者身份；其他人应被拒绝。保留全部已提出功能，规划并自定义实现模板未覆盖的能力。"

APP = '''import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI()
database = Path(os.environ["DATABASE_URL"].removeprefix("sqlite:///"))
database.parent.mkdir(parents=True, exist_ok=True)

def connection():
    c = sqlite3.connect(database)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

with connection() as c:
    c.executescript("CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY, salt TEXT NOT NULL, hash TEXT NOT NULL); CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, name TEXT NOT NULL REFERENCES users(name)); CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY, owner TEXT NOT NULL REFERENCES users(name), title TEXT NOT NULL); CREATE TABLE IF NOT EXISTS members(entry_id INTEGER REFERENCES entries(id), name TEXT REFERENCES users(name), PRIMARY KEY(entry_id,name));")

class Account(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=12, max_length=100)

class Document(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class Share(BaseModel):
    name: str = Field(min_length=1, max_length=100)

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210000).hex()

def actor(authorization):
    with connection() as c:
        row = c.execute("SELECT name FROM sessions WHERE token=?", (authorization.removeprefix("Bearer "),)).fetchone()
    if not row: raise HTTPException(401, "login required")
    return row["name"]

@app.get("/health")
def health(): return {"ok": True}

@app.post("/users", status_code=201)
def register(account: Account):
    salt = secrets.token_hex(16)
    try:
        with connection() as c: c.execute("INSERT INTO users VALUES(?,?,?)", (account.name,salt,password_hash(account.password,salt)))
    except sqlite3.IntegrityError: raise HTTPException(409, "name exists")
    return {"name": account.name}

@app.post("/login")
def login(account: Account):
    with connection() as c:
        row = c.execute("SELECT * FROM users WHERE name=?", (account.name,)).fetchone()
        if not row or not hmac.compare_digest(row["hash"], password_hash(account.password,row["salt"])): raise HTTPException(401, "invalid login")
        token = secrets.token_urlsafe(32)
        c.execute("INSERT INTO sessions VALUES(?,?)", (token,account.name))
    return {"token": token}

@app.post("/entries", status_code=201)
def create(document: Document, authorization: str = Header(default="")):
    name = actor(authorization)
    with connection() as c:
        cursor = c.execute("INSERT INTO entries(owner,title) VALUES(?,?)", (name,document.title))
        return {"id": cursor.lastrowid, "title": document.title}

def record(identifier, authorization):
    name = actor(authorization)
    with connection() as c:
        row = c.execute("SELECT * FROM entries WHERE id=?", (identifier,)).fetchone()
        member = bool(c.execute("SELECT 1 FROM members WHERE entry_id=? AND name=?", (identifier,name)).fetchone())
    if not row: raise HTTPException(404, "not found")
    allowed = row["owner"] == name
    # CUSTOM_ACCESS
    if not allowed: raise HTTPException(403, "forbidden")
    return row, name

@app.get("/entries/{identifier}")
def read(identifier: int, authorization: str = Header(default="")):
    row, _ = record(identifier,authorization)
    return {"id": row["id"], "title": row["title"]}

# CUSTOM_ROUTES

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>资料工作台</title><main><h1>资料工作台</h1><label>账号<input name='name'></label><label>密码<input name='password' type='password'></label><button id='login'>登录</button><p id='session'></p><label>资料标题<input name='title'></label><button id='save'>保存资料</button><p id='result'></p></main><script>
let token=''; const field=n=>document.querySelector('[name='+n+']');
document.querySelector('#login').onclick=async()=>{let r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:field('name').value,password:field('password').value})});if(r.ok){token=(await r.json()).token;document.querySelector('#session').textContent='已登录'}else document.querySelector('#session').textContent='登录失败'};
document.querySelector('#save').onclick=async()=>{let r=await fetch('/entries',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:JSON.stringify({title:field('title').value})});document.querySelector('#result').textContent=r.ok?'保存成功':'保存失败'};
</script></html>"""
'''

SHARED_ROUTES = """@app.post("/entries/{identifier}/share")
def share(identifier: int, user: Share, authorization: str = Header(default="")):
    row, name = record(identifier,authorization)
    if row["owner"] != name: raise HTTPException(403,"owner required")
    try:
        with connection() as c: c.execute("INSERT INTO members VALUES(?,?)",(identifier,user.name))
    except sqlite3.IntegrityError: raise HTTPException(400,"invalid member")
    return {"shared": True}
"""


def make_plan(payload):
    refs = [s["id"] for s in payload["source_units"]]
    base = []
    for actor in ("owner", "member", "outsider"):
        base += [
            {
                "method": "POST",
                "path": "/users",
                "body": {"name": actor + "-${nonce}", "password": "fixture-only-password"},
                "status": 201,
            },
            {
                "method": "POST",
                "path": "/login",
                "body": {"name": actor + "-${nonce}", "password": "fixture-only-password"},
                "status": 200,
                "captures": {actor: "$.token"},
            },
        ]
    create = {
        "method": "POST",
        "path": "/entries",
        "headers": {"Authorization": "Bearer ${owner}"},
        "body": {"title": "持久化资料-${nonce}"},
        "status": 201,
        "captures": {"entry": "$.id"},
        "equals": {"$.title": "持久化资料-${nonce}"},
    }
    own = {
        "path": "/entries/${entry}",
        "headers": {"Authorization": "Bearer ${owner}"},
        "status": 200,
        "equals": {"$.title": "持久化资料-${nonce}"},
    }
    denied = {
        "path": "/entries/${entry}",
        "headers": {"Authorization": "Bearer ${outsider}"},
        "status": 403,
    }
    scenarios = [
        {
            "id": "private_records",
            "title": "登录、真实保存、本人访问和越权拒绝",
            "requirements": refs,
            "steps": [*base, create, own, denied],
            "after_restart": [own, denied],
            "browser": [
                {"action": "open", "value": "/"},
                {"action": "fill", "selector": "[name=name]", "value": "owner-${nonce}"},
                {"action": "fill", "selector": "[name=password]", "value": "fixture-only-password"},
                {"action": "click", "selector": "#login"},
                {"action": "text", "selector": "#session", "value": "已登录"},
                {"action": "viewport", "width": 390, "height": 844},
                {"action": "fill", "selector": "[name=title]", "value": "手机资料"},
                {"action": "click", "selector": "#save"},
                {"action": "text", "selector": "#result", "value": "保存成功"},
            ],
        },
        {
            "id": "team_sharing",
            "title": "授权同组只读且隐藏身份，成员不能再次授权",
            "requirements": refs,
            "steps": [
                *base,
                create,
                {
                    "method": "POST",
                    "path": "/entries/${entry}/share",
                    "headers": {"Authorization": "Bearer ${owner}"},
                    "body": {"name": "member-${nonce}"},
                    "status": 200,
                    "equals": {"$.shared": True},
                },
                {
                    "path": "/entries/${entry}",
                    "headers": {"Authorization": "Bearer ${member}"},
                    "status": 200,
                    "equals": {"$.title": "持久化资料-${nonce}"},
                    "absent": ["$.owner", "$.name", "$.school"],
                },
                {
                    "method": "POST",
                    "path": "/entries/${entry}/share",
                    "headers": {"Authorization": "Bearer ${member}"},
                    "body": {"name": "outsider-${nonce}"},
                    "status": 403,
                },
                denied,
            ],
        },
    ]
    return CapabilityPlan.model_validate(
        {
            "title": "独立资料协作",
            "summary": "先构建登录和持久化，再独立实现团队共享与身份投影",
            "selection": payload["selection"],
            "source_digest": payload["source_digest"],
            "tasks": [
                {
                    "id": "accounts_records",
                    "title": "登录与私有资料",
                    "requirements": refs,
                    "files": ["app.py"],
                    "contract": "真实FastAPI服务，SQLite持久化与登录权限",
                    "scenarios": ["private_records"],
                },
                {
                    "id": "team_access",
                    "title": "独立团队只读授权",
                    "depends_on": ["accounts_records"],
                    "requirements": refs,
                    "files": ["app.py", "access.py"],
                    "contract": "所有者可授予成员只读权限，成员不能再授权，共享投影隐藏身份",
                    "scenarios": ["team_sharing"],
                },
            ],
            "runtime": {
                "prepare": [
                    {
                        "argv": [
                            "uv",
                            "sync",
                            "--locked",
                            "--offline",
                            "--no-dev",
                            "--python",
                            "3.14",
                        ]
                    }
                ],
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
                "database_tables": ["entries"],
            },
            "scenarios": scenarios,
        }
    )


class CapabilityFixture:
    def __init__(self, fail_first_sharing=False):
        self.calls = []
        self.fail_first_sharing = fail_first_sharing
        self.sharing_calls = 0

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is FeatureOutline:
            return fixture_feature_outline(make_plan(payload))
        if schema is Plan:
            return fixture_baseline()
        if schema is CapabilityOutline:
            return schema.model_validate(make_plan(payload).model_dump(exclude={"scenarios"}))
        if schema is CapabilityScenarioBatch:
            full = make_plan(payload)
            return schema(
                summary="当前节点的具体运行验收合同",
                scenarios=[s for s in full.scenarios if s.id in payload["task"]["scenarios"]],
            )
        if schema is not CapabilityEdits:
            raise AssertionError("Unexpected model request in explicit capability fixture")
        if payload["task"]["id"] == "accounts_records":
            content = {"app.py": APP}
        else:
            self.sharing_calls += 1
            content = {
                "app.py": APP.replace(
                    "    # CUSTOM_ACCESS",
                    "    from access import readable\n    allowed = readable(row['owner'],name,member)",
                ).replace("# CUSTOM_ROUTES", SHARED_ROUTES),
                "access.py": "def readable(owner, actor, member):\n    return owner == actor or member\n",
            }
            if self.fail_first_sharing and self.sharing_calls == 1:
                content["access.py"] = (
                    "def readable(owner, actor, member):\n    return owner == actor\n"
                )
        return CapabilityEdits(
            explanation="离线固定模型响应；真实源码随后由独立隔离工具执行验收",
            files=[
                {"path": name, "before_sha256": payload["file_manifest"].get(name), "content": text}
                for name, text in content.items()
            ],
        )


def fixture_baseline():
    return Plan.model_validate(
        {
            "title": "固定资料基础",
            "data_scope": "per_user",
            "entities": [
                {
                    "name": "entries",
                    "description": "资料",
                    "fields": [{"name": "title", "kind": "text"}],
                }
            ],
            "acceptance": ["资料基础由确定性生成器产生；团队行为另由模块验证"],
        }
    )


def fixture_feature_outline(plan):
    return FeatureOutline.model_validate(
        {
            "summary": "固定模型fixture：保留模板基础，分模块扩展",
            "selection": plan.selection.model_dump(),
            "source_digest": plan.source_digest,
            "features": [
                {
                    "id": task.id,
                    "title": task.title,
                    "requirements": task.requirements,
                    "route": "module",
                    "capability": "fixture-extension",
                    "module_id": task.id,
                    "depends_on": task.depends_on,
                }
                for task in plan.tasks
            ],
            "modules": [
                {
                    **task.model_dump(),
                    "adapter": plan.selection.template,
                    "extension": "approved-source-module",
                    "interfaces": ["fixture: reviewed HTTP scenarios"],
                }
                for task in plan.tasks
            ],
        }
    )
