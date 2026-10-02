# templates/product/app.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** FastAPI产品认证与路由入口：无business时保留per_user实体接口；有business时安装business_runtime事务接口与角色范围。网页不能直接访问数据库或伪造操作者，角色从服务器读取。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `lifespan`（L32–L36）：接收`app`。 调用`engine.connect`、`connection.execute`、`select(metadata.tables["users"]).limit`、`select`、`engine.dispose`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Credentials`（L48–L51）：继承`BaseModel`。声明的数据项为`username`、`password`；类型约束/数据库列参数以完整定义为准。
- `password_hash`（L54–L57）：接收`password`、`salt`。 调用`secrets.token_hex`、`hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 2…`、`hashlib.pbkdf2_hmac`、`password.encode`、`salt.encode`。 返回路径：L57的`salt + ":" + hashed`。
- `issue_token`（L60–L69）：接收`connection`、`user_id`。 调用`secrets.token_urlsafe`、`connection.execute`、`insert(metadata.tables["tokens"]).values`、`insert`、`hashlib.sha256(token.encode()).hexdigest`、`hashlib.sha256`、`token.encode`、`int`、`time.time`。 返回路径：L69的`{"access_token": token, "token_type": "bearer"}`。
- `register`（L73–L106）：接收`data`。 控制顺序：L74按`SPEC.get("business") and not SPEC["business"]["registration"]["enabled"]`分支；L75抛异常，停止当前正常路径；L84按`SPEC.get("business")`分支；L106抛异常，停止当前正常路径。 调用`SPEC.get`、`HTTPException`、`engine.begin`、`str`、`uuid.uuid4`、`c.execute`、`insert(metadata.tables["users"]).values`、`insert`、`password_hash`等。 返回路径：L104的`issue_token(c, user_id)`。
- `login`（L110–L118）：接收`data`。 控制顺序：L114按`not user or not hmac.compare_digest( user["password"], password_hash(data.password, u…`分支；L117抛异常，停止当前正常路径。 调用`engine.begin`、`c.execute(select(table).where(table.c.username == data.username))…`、`c.execute`、`select(table).where`、`select`、`hmac.compare_digest`、`password_hash`、`user["password"].split`、`HTTPException`等。 返回路径：L118的`issue_token(c, user["id"])`。
- `actor`（L121–L132）：接收`token`。 控制顺序：L130按`not user_id`分支；L131抛异常，停止当前正常路径。 调用`Depends`、`engine.connect`、`c.scalar`、`select(table.c.user_id).where`、`select`、`hashlib.sha256(token.credentials.encode()).hexdigest`、`hashlib.sha256`、`token.credentials.encode`、`int`等。 返回路径：L132的`user_id`。
- `business_table`（L135–L138）：接收`entity`。 控制顺序：L136按`entity not in models`分支；L137抛异常，停止当前正常路径。 调用`HTTPException`。 返回路径：L138的`metadata.tables[entity]`。
- `validated`（L141–L149）：接收`entity`、`data`。 控制顺序：L149抛异常，停止当前正常路径。 调用`business_table`、`models[entity].model_validate(data).model_dump`、`models[entity].model_validate`、`validate_options`、`RULES.validate`、`HTTPException`。 返回路径：L147的`value`。
- `health`（L153–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`app.get`。 返回路径：L154的`{"status": "ok"}`。
- `index`（L158–L161）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L159按`SELECTION["frontend"] == "api-only"`分支。 调用`FileResponse`、`Path(__file__).resolve`、`Path`、`app.get`。 返回路径：L160的`{"title": SPEC["title"], "docs": "/docs", "frontend": "api-only"}`；L161的`FileResponse(Path(__file__).resolve().parent / "web/index.html")`。
- `asset`（L165–L168）：接收`asset`。 控制顺序：L166按`asset not in {"app.js", "style.css"} or SELECTION["frontend"] == "api-only"`分支；L167抛异常，停止当前正常路径。 调用`HTTPException`、`FileResponse`、`Path(__file__).resolve`、`Path`、`app.get`。 返回路径：L168的`FileResponse(Path(__file__).resolve().parent / "web" / asset)`。
- `product_schema`（L172–L173）：接收`user`。 调用`Depends`、`app.get`。 返回路径：L173的`{"spec": SPEC, "selection": SELECTION}`。
- `list_items`（L177–L208）：接收`entity`、`request`、`response`、`limit`、`offset`、`user`。 控制顺序：L187按`len(request.query_params.multi_items()) != len(request.query_params)`分支；L188抛异常，停止当前正常路径；L190按`not 1 <= limit <= 100 or offset < 0`分支；L191抛异常，停止当前正常路径；L193抛异常，停止当前正常路径。 调用`Depends`、`business_table`、`len`、`request.query_params.multi_items`、`ValueError`、`conditions`、`HTTPException`、`str`、`engine.connect`等。 返回路径：L208的`[dict(row) for row in rows]`。
- `create_item`（L212–L217）：接收`entity`、`data`、`user`。 调用`Depends`、`validated`、`value.update`、`str`、`uuid.uuid4`、`engine.begin`、`c.execute`、`insert(business_table(entity)).values`、`insert`等。 返回路径：L217的`value`。
- `get_item`（L221–L231）：接收`entity`、`item_id`、`user`。 控制顺序：L229按`not row`分支；L230抛异常，停止当前正常路径。 调用`Depends`、`business_table`、`engine.connect`、`c.execute(select(table).where(table.c.id == item_id, table.c.owne…`、`c.execute`、`select(table).where`、`select`、`HTTPException`、`dict`等。 返回路径：L231的`dict(row)`。
- `update_item`（L235–L244）：接收`entity`、`item_id`、`data`、`user`。 控制顺序：L242按`not changed`分支；L243抛异常，停止当前正常路径。 调用`Depends`、`business_table`、`validated`、`engine.begin`、`c.execute`、`update(table).where(table.c.id == item_id, table.c.owner_id == us…`、`update(table).where`、`update`、`HTTPException`等。 返回路径：L244的`get_item(entity, item_id, user)`。
- `delete_item`（L248–L255）：接收`entity`、`item_id`、`user`。 控制顺序：L254按`not changed`分支；L255抛异常，停止当前正常路径。 调用`Depends`、`business_table`、`engine.begin`、`c.execute`、`delete(table).where`、`delete`、`HTTPException`、`app.delete`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/product/app.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L261。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8641`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/app.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "79979ebc0794cf59b7193496c4265a03c59989a43b2a2f4846a8f5ff42f436cd"} -->
````python
# templates/product/app.py
"""Local business application: authenticated per-user CRUD with approved typed fields."""

import hashlib
import hmac
import json
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fields import input_model, validate_options
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)
from querying import conditions
from rule_engine import Rules
from schema import SPEC, engine, metadata
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

RULES = Rules((Path(__file__).resolve().parent / "custom_rules.py").read_text(encoding="utf-8"))


@asynccontextmanager
async def lifespan(app):
    with engine.connect() as connection:
        connection.execute(select(metadata.tables["users"]).limit(1))
    yield
    engine.dispose()


app = FastAPI(title=SPEC["title"], lifespan=lifespan)
auth = HTTPBearer()
ENTITIES = {entity["name"]: entity for entity in SPEC["entities"]}
models = {name: input_model(entity) for name, entity in ENTITIES.items()}
SELECTION = json.loads(
    (Path(__file__).resolve().parent / "selection.json").read_text(encoding="utf-8")
)


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=200)


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 210000).hex()
    return salt + ":" + hashed


def issue_token(connection, user_id):
    token = secrets.token_urlsafe(32)
    connection.execute(
        insert(metadata.tables["tokens"]).values(
            token=hashlib.sha256(token.encode()).hexdigest(),
            user_id=user_id,
            expires_at=int(time.time()) + 86400,
        )
    )
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/register", status_code=201)
def register(data: Credentials):
    if SPEC.get("business") and not SPEC["business"]["registration"]["enabled"]:
        raise HTTPException(403, "本系统由管理员创建账号")
    try:
        with engine.begin() as c:
            user_id = str(uuid.uuid4())
            c.execute(
                insert(metadata.tables["users"]).values(
                    id=user_id, username=data.username, password=password_hash(data.password)
                )
            )
            if SPEC.get("business"):
                from business_policy import utc

                c.execute(
                    insert(metadata.tables["business_audit"]).values(
                        id=str(uuid.uuid4()),
                        entity="$users",
                        record_id=user_id,
                        actor_id=user_id,
                        action="registered",
                        created_at=utc(),
                        before_json=None,
                        after_json=json.dumps(
                            {
                                "username": data.username,
                                "role": SPEC["business"]["registration"]["default_role"],
                            }
                        ),
                    )
                )
            return issue_token(c, user_id)
    except IntegrityError:
        raise HTTPException(409, "用户名已经存在") from None


@app.post("/auth/login")
def login(data: Credentials):
    with engine.begin() as c:
        table = metadata.tables["users"]
        user = c.execute(select(table).where(table.c.username == data.username)).mappings().first()
        if not user or not hmac.compare_digest(
            user["password"], password_hash(data.password, user["password"].split(":")[0])
        ):
            raise HTTPException(401, "用户名或密码错误")
        return issue_token(c, user["id"])


def actor(token: HTTPAuthorizationCredentials = Depends(auth)):
    table = metadata.tables["tokens"]
    with engine.connect() as c:
        user_id = c.scalar(
            select(table.c.user_id).where(
                table.c.token == hashlib.sha256(token.credentials.encode()).hexdigest(),
                table.c.expires_at > int(time.time()),
            )
        )
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
        validate_options(ENTITIES[entity], value)
        RULES.validate(entity, value)
        return value
    except ValidationError, ValueError:
        raise HTTPException(422, "字段或业务规则验证失败") from None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    if SELECTION["frontend"] == "api-only":
        return {"title": SPEC["title"], "docs": "/docs", "frontend": "api-only"}
    return FileResponse(Path(__file__).resolve().parent / "web/index.html")


@app.get("/web/{asset}")
def asset(asset: str):
    if asset not in {"app.js", "style.css"} or SELECTION["frontend"] == "api-only":
        raise HTTPException(404)
    return FileResponse(Path(__file__).resolve().parent / "web" / asset)


@app.get("/schema")
def product_schema(user=Depends(actor)):
    return {"spec": SPEC, "selection": SELECTION}


@app.get("/api/{entity}")
def list_items(
    entity: str,
    request: Request,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    user=Depends(actor),
):
    table = business_table(entity)
    try:
        if len(request.query_params.multi_items()) != len(request.query_params):
            raise ValueError("不接受重复查询参数")
        expressions, ordering = conditions(table, ENTITIES[entity], request.query_params, user)
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError("分页参数超出范围")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    with engine.connect() as c:
        count = c.scalar(select(func.count()).select_from(table).where(*expressions))
        rows = (
            c.execute(
                select(table)
                .where(*expressions)
                .order_by(ordering, table.c.id)
                .limit(limit)
                .offset(offset)
            )
            .mappings()
            .all()
        )
    response.headers["X-Total-Count"] = str(count)
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
        row = (
            c.execute(select(table).where(table.c.id == item_id, table.c.owner_id == user))
            .mappings()
            .first()
        )
    if not row:
        raise HTTPException(404, "记录不存在")
    return dict(row)


@app.put("/api/{entity}/{item_id}")
def update_item(entity: str, item_id: str, data: dict, user=Depends(actor)):
    table = business_table(entity)
    value = validated(entity, data)
    with engine.begin() as c:
        changed = c.execute(
            update(table).where(table.c.id == item_id, table.c.owner_id == user).values(**value)
        ).rowcount
        if not changed:
            raise HTTPException(404, "记录不存在")
    return get_item(entity, item_id, user)


@app.delete("/api/{entity}/{item_id}", status_code=204)
def delete_item(entity: str, item_id: str, user=Depends(actor)):
    table = business_table(entity)
    with engine.begin() as c:
        changed = c.execute(
            delete(table).where(table.c.id == item_id, table.c.owner_id == user)
        ).rowcount
        if not changed:
            raise HTTPException(404, "记录不存在")


if SPEC.get("business"):
    from business_runtime import install_business

    install_business(app, actor, password_hash, issue_token, validated)
````
