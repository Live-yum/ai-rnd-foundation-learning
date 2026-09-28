"""Local business application: authenticated per-user CRUD with approved typed fields."""
import hashlib
import hmac
import secrets
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, ValidationError, create_model
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

import custom_rules
from schema import SPEC, engine, metadata


@asynccontextmanager
async def lifespan(app):
    with engine.connect() as connection:
        connection.execute(select(metadata.tables["users"]).limit(1))
    yield
    engine.dispose()


app = FastAPI(title=SPEC["title"], lifespan=lifespan)
auth = HTTPBearer()
models = {}
for entity in SPEC["entities"]:
    fields = {}
    for field in entity["fields"]:
        kind = {"text": StrictStr, "integer": StrictInt, "boolean": StrictBool}[field["kind"]]
        settings = {"max_length": field["max_length"]} if field["kind"] == "text" else {}
        fields[field["name"]] = (kind if field["required"] else kind | None,
                                  Field(default=... if field["required"] else None, **settings))
    models[entity["name"]] = create_model(entity["name"] + "Input",
                                         __config__=ConfigDict(extra="forbid"), **fields)


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=200)


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 210000).hex()
    return salt + ":" + hashed


def issue_token(connection, user_id):
    token = secrets.token_urlsafe(32)
    connection.execute(insert(metadata.tables["tokens"]).values(
        token=hashlib.sha256(token.encode()).hexdigest(), user_id=user_id,
        expires_at=int(time.time()) + 86400))
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/register", status_code=201)
def register(data: Credentials):
    try:
        with engine.begin() as c:
            user_id = str(uuid.uuid4())
            c.execute(insert(metadata.tables["users"]).values(
                id=user_id, username=data.username, password=password_hash(data.password)))
            return issue_token(c, user_id)
    except IntegrityError:
        raise HTTPException(409, "用户名已经存在") from None


@app.post("/auth/login")
def login(data: Credentials):
    with engine.begin() as c:
        table = metadata.tables["users"]
        user = c.execute(select(table).where(table.c.username == data.username)).mappings().first()
        if not user or not hmac.compare_digest(user["password"], password_hash(data.password, user["password"].split(":")[0])):
            raise HTTPException(401, "用户名或密码错误")
        return issue_token(c, user["id"])


def actor(token: HTTPAuthorizationCredentials = Depends(auth)):
    table = metadata.tables["tokens"]
    with engine.connect() as c:
        user_id = c.scalar(select(table.c.user_id).where(
            table.c.token == hashlib.sha256(token.credentials.encode()).hexdigest(),
            table.c.expires_at > int(time.time())))
    if not user_id:
        raise HTTPException(401, "登录已失效")
    return user_id


def business_table(entity):
    if entity not in models:
        raise HTTPException(404, "实体不存在")
    return metadata.tables[entity]


def validated(entity, data):
    business_table(entity)
    try:
        value = models[entity].model_validate(data).model_dump()
        custom_rules.validate(entity, value)
        return value
    except (ValidationError, ValueError):
        raise HTTPException(422, "字段或业务规则验证失败") from None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/{entity}")
def list_items(entity: str, limit: int = 50, offset: int = 0, user=Depends(actor)):
    table = business_table(entity)
    with engine.connect() as c:
        rows = c.execute(select(table).where(table.c.owner_id == user).order_by(table.c.id)
                         .limit(max(1, min(limit, 100))).offset(max(0, offset))).mappings().all()
        return [dict(row) for row in rows]


@app.post("/api/{entity}", status_code=201)
def create_item(entity: str, data: dict, user=Depends(actor)):
    value = validated(entity, data)
    value.update(id=str(uuid.uuid4()), owner_id=user)
    with engine.begin() as c:
        c.execute(insert(business_table(entity)).values(**value))
    return value


@app.get("/api/{entity}/{item_id}")
def get_item(entity: str, item_id: str, user=Depends(actor)):
    table = business_table(entity)
    with engine.connect() as c:
        row = c.execute(select(table).where(table.c.id == item_id, table.c.owner_id == user)).mappings().first()
    if not row:
        raise HTTPException(404, "记录不存在")
    return dict(row)


@app.put("/api/{entity}/{item_id}")
def update_item(entity: str, item_id: str, data: dict, user=Depends(actor)):
    table = business_table(entity)
    value = validated(entity, data)
    with engine.begin() as c:
        changed = c.execute(update(table).where(table.c.id == item_id, table.c.owner_id == user).values(**value)).rowcount
        if not changed:
            raise HTTPException(404, "记录不存在")
    return get_item(entity, item_id, user)


@app.delete("/api/{entity}/{item_id}", status_code=204)
def delete_item(entity: str, item_id: str, user=Depends(actor)):
    table = business_table(entity)
    with engine.begin() as c:
        changed = c.execute(delete(table).where(table.c.id == item_id, table.c.owner_id == user)).rowcount
        if not changed:
            raise HTTPException(404, "记录不存在")
