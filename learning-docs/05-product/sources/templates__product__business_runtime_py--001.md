# templates/product/business_runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 独立客服产品事务执行器：每请求读真实角色，把all/own/assigned放进查询；保护创建人/负责人/状态/时间，锁定记录执行动作，追加事件与提醒，并按范围计算四类指标。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `StrictBody`（L13–L14）：继承`BaseModel`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `NoteBody`（L17–L18）：继承`StrictBody`。声明的数据项为`body`；类型约束/数据库列参数以完整定义为准。
- `Assignment`（L21–L22）：继承`StrictBody`。声明的数据项为`user_id`；类型约束/数据库列参数以完整定义为准。
- `TransitionBody`（L25–L26）：继承`StrictBody`。声明的数据项为`transition`；类型约束/数据库列参数以完整定义为准。
- `LabelRequest`（L29–L30）：继承`StrictBody`。声明的数据项为`record_ids`；类型约束/数据库列参数以完整定义为准。
- `UserBody`（L33–L36）：继承`StrictBody`。声明的数据项为`username`、`password`、`role`；类型约束/数据库列参数以完整定义为准。
- `RoleBody`（L39–L40）：继承`StrictBody`。声明的数据项为`role`；类型约束/数据库列参数以完整定义为准。
- `install_business`（L43–L820）：接收`app`、`actor_dependency`、`password_hash`、`issue_token`、`legacy_validate`。 调用`Policy`、`getattr(route, "path", "").startswith`、`getattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_business.current`（L61–L70）：接收`user_id`。 控制顺序：L68按`not row or row["role"] not in policy.roles`分支；L69抛异常，停止当前正常路径。 调用`Depends`、`engine.connect`、`connection.execute(select(tables["users"]).where(tables["users"].…`、`connection.execute`、`select(tables["users"]).where`、`select`、`HTTPException`。 返回路径：L70的`{"id": row["id"], "username": row["username"], "role": row["role"]}`。
- `install_business.grant`（L72–L76）：接收`actor`、`entity`、`action`。 控制顺序：L76抛异常，停止当前正常路径。 调用`policy.grant`、`HTTPException`、`str`。 返回路径：L74的`policy.grant(actor["role"], entity, action)`。
- `install_business.table`（L78–L81）：接收`entity`。 控制顺序：L79按`entity not in entities`分支；L80抛异常，停止当前正常路径。 调用`HTTPException`。 返回路径：L81的`tables[entity]`。
- `install_business.scope`（L83–L93）：接收`actor`、`entity`、`action`。 控制顺序：L86按`permission["scope"] == "all"`分支。 调用`grant`、`table`、`policy.resource`。 返回路径：L87的`[]`；L93的`[target.c[key] == actor["id"]]`。
- `install_business.record`（L95–L105）：接收`connection`、`actor`、`entity`、`record_id`、`action`、`lock`、`archived`。 控制顺序：L98按`not archived`分支；L100按`lock`分支；L103按`row is None`分支；L104抛异常，停止当前正常路径。 调用`table`、`select(target).where`、`select`、`scope`、`stmt.where`、`target.c.archived_at.is_`、`stmt.with_for_update`、`connection.execute(stmt).mappings().first`、`connection.execute(stmt).mappings`等。 返回路径：L105的`dict(row)`。
- `install_business.administrator`（L107–L109）：接收`actor`。 控制顺序：L108按`actor["role"] not in business["role_admin_roles"]`分支；L109抛异常，停止当前正常路径。 调用`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_business.history_actor_names`（L111–L124）：接收`connection`、`rows`。 源码说明：Resolve only actors from already-authorized history, never arbitrary IDs.。 控制顺序：L116遍历`range(0, len(identities), 100)`。 调用`sorted`、`range`、`len`、`result.update`、`connection.execute( select(users.c.id, users.c.username).where( u…`、`connection.execute`、`select(users.c.id, users.c.username).where`、`select`、`users.c.id.in_`。 返回路径：L124的`result`。
- `install_business.serialize_administrator`（L126–L139）：接收`connection`、`actor`。 控制顺序：L133按`changed != 1`分支；L134抛异常，停止当前正常路径；L138按`role not in business["role_admin_roles"]`分支；L139抛异常，停止当前正常路径。 调用`connection.execute`、`update(marker).where(marker.c.key == "bootstrap_admin").values`、`update(marker).where`、`update`、`HTTPException`、`connection.scalar`、`select(tables["users"].c.role).where`、`select`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_business.event`（L141–L155）：接收`connection`、`actor`、`entity`、`record_id`、`action`、`before`、`after`。 调用`str`、`uuid.uuid4`、`connection.execute`、`insert(tables["business_audit"]).values`、`insert`、`utc`、`json.dumps`。 返回路径：L155的`identity`。
- `install_business.notify`（L157–L200）：接收`connection`、`entity`、`row`、`name`、`identity`、`transition`、`notification`。 控制顺序：L158遍历`business["notifications"]`；L159按`notification is not None and item != notification`分支；L161按`item["entity"] != entity or item["event"] != name`分支；L163按`name == "transitioned" and item["transition"] != transition`分支；L170按`not recipient`分支；L173按`connection.scalar( select(tables["business_notifications"].c.id).where( tables["busin…`分支；L195按`not connection.scalar( select(tables["business_notifications"].c.id).where( tables["b…`分支；L200抛异常，停止当前正常路径。 调用`row.get`、`policy.resource`、`hashlib.sha256(f"{identity}:{entity}:{recipient}:{name}".encode()…`、`hashlib.sha256`、`f"{identity}:{entity}:{recipient}:{name}".encode`、`connection.scalar`、`select(tables["business_notifications"].c.id).where`、`select`、`connection.begin_nested`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_business.reference_checks`（L202–L226）：接收`connection`、`actor`、`entity`、`values`、`before`。 控制顺序：L203遍历`policy.relations.items()`；L204按`source != entity or values.get(field) is None`分支；L206按`before is not None and values[field] == before.get(field)`分支；L209按`target == "$users"`分支；L215按`user is None`分支；L216抛异常，停止当前正常路径；L217按`field == policy.resource(entity).get("assignee_field")`分支；L219按`not permission or "read" not in permission["actions"] or permission["scope"] not in {…`分支。后续分支沿下方源码相同行号继续阅读。 调用`policy.relations.items`、`values.get`、`before.get`、`connection.execute(select(tables["users"]).where(tables["users"].…`、`connection.execute`、`select(tables["users"]).where`、`select`、`HTTPException`、`policy.resource(entity).get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_business.values_for`（L228–L250）：接收`actor`、`entity`、`data`、`old`。 控制顺序：L229按`not isinstance(data, dict)`分支；L230抛异常，停止当前正常路径；L232按`set(data) & protected`分支；L233抛异常，停止当前正常路径；L237按`workflow and old is None`分支；L239按`old is None`分支；L240遍历`entities[entity]["fields"]`；L241按`f["name"] in protected and f["name"] not in values`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`HTTPException`、`policy.protected`、`set`、`old.get`、`values.update`、`policy.workflow`、`policy.validate_fields`、`RULES.validate`。 返回路径：L248的`value`。
- `install_business.me`（L253–L254）：接收`actor`。 调用`Depends`、`app.get`。 返回路径：L254的`actor`。
- `install_business.schema`（L257–L273）：接收`actor`。 调用`Depends`、`json.loads`、`(ROOT / "selection.json").read_text`、`policy.permissions.get((actor["role"], name), {}).get`、`policy.permissions.get`、`app.get`。 返回路径：L266的`{ "spec": {**SPEC, "entities": [entities[name] for name in visible]}, "selection": selecti…`。
- `install_business.users`（L276–L296）：接收`entity`、`actor`。 控制顺序：L277按`entity is None`分支；L289按`entity`分支。 调用`Depends`、`administrator`、`grant`、`engine.connect`、`connection.execute( select(tables["users"].c.id, tables["users"].…`、`connection.execute`、`select`、`policy.permissions.get((row["role"], entity), {}).get`、`policy.permissions.get`等。 返回路径：L296的`[dict(row) for row in rows]`。
- `install_business.create_user`（L299–L326）：接收`data`、`actor`。 控制顺序：L301按`data.role not in policy.roles`分支；L302抛异常，停止当前正常路径；L325抛异常，停止当前正常路径。 调用`Depends`、`administrator`、`HTTPException`、`str`、`uuid.uuid4`、`engine.begin`、`serialize_administrator`、`connection.execute`、`insert(tables["users"]).values`等。 返回路径：L326的`{"id": identity, "username": data.username, "role": data.role}`。
- `install_business.change_role`（L329–L367）：接收`identity`、`data`、`actor`。 控制顺序：L331按`data.role not in policy.roles`分支；L332抛异常，停止当前正常路径；L340按`old is None`分支；L341抛异常，停止当前正常路径；L342按`old["role"] in business["role_admin_roles"] and data.role not in business["role_admin…`分支；L351按`len(administrators) <= 1`分支；L352抛异常，停止当前正常路径。 调用`Depends`、`administrator`、`HTTPException`、`engine.begin`、`serialize_administrator`、`connection.execute(select(tables["users"]).where(tables["users"].…`、`connection.execute`、`select(tables["users"]).where`、`select`等。 返回路径：L367的`{"id": identity, "role": data.role}`。
- `install_business.reference_labels`（L370–L416）：接收`entity`、`data`、`actor`。 源码说明：Resolve only references present in rows this actor can already read.。 控制顺序：L386遍历`business["relations"]`；L387按`relation["entity"] != entity`分支；L391按`not identities`分支；L393按`target_name == "$users"`分支；L399按`"read" in policy.permissions.get((actor["role"], target_name), {}).get( "actions", []…`分支。 调用`Depends`、`table`、`engine.connect`、`connection.execute( select(source).where( source.c.id.in_(data.re…`、`connection.execute`、`select(source).where`、`select`、`source.c.id.in_`、`source.c.archived_at.is_`等。 返回路径：L416的`result`。
- `install_business.list_items`（L419–L457）：接收`entity`、`request`、`response`、`limit`、`offset`、`actor`。 控制顺序：L429按`len(request.query_params.multi_items()) != len(request.query_params) or not 1 <= limi…`分支；L434抛异常，停止当前正常路径；L439抛异常，停止当前正常路径。 调用`Depends`、`table`、`len`、`request.query_params.multi_items`、`ValueError`、`conditions`、`HTTPException`、`str`、`target.c.archived_at.is_`等。 返回路径：L457的`[dict(row) for row in rows]`。
- `install_business.create`（L460–L486）：接收`entity`、`data`、`actor`。 控制顺序：L485抛异常，停止当前正常路径。 调用`Depends`、`grant`、`values_for`、`utc`、`values.update`、`str`、`uuid.uuid4`、`engine.begin`、`reference_checks`等。 返回路径：L486的`row`。
- `install_business.get`（L489–L491）：接收`entity`、`identity`、`actor`。 调用`Depends`、`engine.connect`、`record`、`app.get`。 返回路径：L491的`record(connection, actor, entity, identity, "read")`。
- `install_business.edit`（L494–L512）：接收`entity`、`identity`、`data`、`actor`。 控制顺序：L508按`changed != 1`分支；L509抛异常，停止当前正常路径。 调用`Depends`、`engine.begin`、`record`、`values_for`、`reference_checks`、`utc`、`connection.execute`、`update(table(entity)) .where( table(entity).c.id == identity, tab…`、`update(table(entity)) .where`等。 返回路径：L512的`after`。
- `install_business.archive`（L515–L526）：接收`entity`、`identity`、`actor`。 调用`Depends`、`engine.begin`、`record`、`utc`、`connection.execute`、`update(table(entity)) .where(table(entity).c.id == identity) .val…`、`update(table(entity)) .where`、`update`、`table`等。 返回路径：L526的`after`。
- `install_business.assign`（L529–L552）：接收`entity`、`identity`、`data`、`actor`。 控制顺序：L533按`data.user_id is None and next(f for f in entities[entity]["fields"] if f["name"] == f…`分支；L537抛异常，停止当前正常路径；L548按`changed != 1`分支；L549抛异常，停止当前正常路径。 调用`Depends`、`engine.begin`、`record`、`policy.resource`、`next`、`HTTPException`、`utc`、`reference_checks`、`connection.execute`等。 返回路径：L552的`after`。
- `install_business.transition`（L555–L590）：接收`entity`、`identity`、`data`、`actor`。 控制顺序：L564抛异常，停止当前正常路径；L566按`operation.get("set_timestamp")`分支；L577按`changed != 1`分支；L578抛异常，停止当前正常路径。 调用`Depends`、`engine.begin`、`record`、`policy.workflow`、`policy.transition`、`HTTPException`、`str`、`utc`、`operation.get`等。 返回路径：L590的`after`。
- `install_business.add_note`（L593–L609）：接收`entity`、`identity`、`data`、`actor`。 控制顺序：L596按`not policy.resource(entity)["notes"]`分支；L597抛异常，停止当前正常路径。 调用`Depends`、`engine.begin`、`record`、`policy.resource`、`HTTPException`、`str`、`uuid.uuid4`、`utc`、`connection.execute`等。 返回路径：L609的`note`。
- `install_business.notes`（L612–L628）：接收`entity`、`identity`、`actor`。 调用`Depends`、`engine.connect`、`record`、`connection.execute( select(tables["business_notes"]) .where( tabl…`、`connection.execute`、`select(tables["business_notes"]) .where( tables["business_notes"]…`、`select(tables["business_notes"]) .where`、`select`、`history_actor_names`等。 返回路径：L628的`[{**dict(row), "actor_username": names.get(row["actor_id"])} for row in rows]`。
- `install_business.history`（L631–L675）：接收`entity`、`identity`、`actor`。 调用`Depends`、`engine.connect`、`policy.permissions.get((actor["role"], entity), {}).get`、`policy.permissions.get`、`record`、`connection.execute( select(tables["business_audit"]) .where( tabl…`、`connection.execute`、`select(tables["business_audit"]) .where( tables["business_audit"]…`、`select(tables["business_audit"]) .where`等。 返回路径：L659的`[ { **{k: row[k] for k in ("id", "actor_id", "action", "created_at")}, "actor_username": n…`。
- `install_business.related`（L678–L710）：接收`entity`、`identity`、`actor`。 控制顺序：L682遍历`business["relations"]`；L684按`relation["target_entity"] != entity or "read" not in policy.permissions.get( (actor["…`分支。 调用`Depends`、`engine.connect`、`record`、`policy.permissions.get( (actor["role"], source), {} ).get`、`policy.permissions.get`、`table`、`connection.execute( select(target) .where( target.c[relation["fie…`、`connection.execute`、`select(target) .where( target.c[relation["field"]] == identity, t…`等。 返回路径：L710的`result`。
- `install_business.metrics`（L713–L739）：接收`actor`。 控制顺序：L716遍历`business["metrics"]`；L717按`"read_metrics" not in policy.permissions.get( (actor["role"], metric["entity"]), {} )…`分支。 调用`Depends`、`engine.connect`、`policy.permissions.get( (actor["role"], metric["entity"]), {} ).g…`、`policy.permissions.get`、`table`、`connection.execute( select(target).where( target.c.archived_at.is…`、`connection.execute`、`select(target).where`、`select`等。 返回路径：L739的`result`。
- `install_business.notifications`（L742–L797）：接收`actor`。 控制顺序：L744遍历`business["notifications"]`；L745按`item["event"] != "due"`分支；L748按`"read" not in policy.permissions.get((actor["role"], entity), {}).get( "actions", [] …`分支；L771遍历`rows`；L773按`workflow and row[workflow["status_field"]] not in { state for transition in workflow[…`分支。 调用`Depends`、`engine.begin`、`policy.permissions.get((actor["role"], entity), {}).get`、`policy.permissions.get`、`table`、`policy.resource`、`connection.execute( select(target).where( recipient == actor["id"…`、`connection.execute`、`select(target).where`等。 返回路径：L786的`[ dict(row) for row in connection.execute( select(tables["business_notifications"]) .where…`。
- `install_business.mark_read`（L800–L820）：接收`identity`、`actor`。 控制顺序：L812按`row is None`分支；L813抛异常，停止当前正常路径。 调用`Depends`、`engine.begin`、`connection.execute( select(target).where( target.c.id == identity…`、`connection.execute`、`select(target).where`、`select`、`HTTPException`、`utc`、`update(target) .where(target.c.id == identity, target.c.recipient…`等。 返回路径：L820的`{"id": identity, "read_at": timestamp}`。

</details>

**创建路径：** `templates/product/business_runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L820。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`33899`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/business_runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "60d0cef61fa1b8143f5398930bf3fc1021b97210a68983fce02d5cc625c51675"} -->
````python
# templates/product/business_runtime.py
"""Generated-product business runtime. Authorization and events are database-backed."""

import hashlib
import json
import uuid

from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class NoteBody(StrictBody):
    body: str = Field(min_length=1, max_length=10000)


class Assignment(StrictBody):
    user_id: str | None = Field(default=None, max_length=36)


class TransitionBody(StrictBody):
    transition: str = Field(min_length=1, max_length=40)


class LabelRequest(StrictBody):
    record_ids: list[str] = Field(min_length=1, max_length=100)


class UserBody(StrictBody):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=200)
    role: str = Field(min_length=1, max_length=40)


class RoleBody(StrictBody):
    role: str = Field(min_length=1, max_length=40)


def install_business(app, actor_dependency, password_hash, issue_token, legacy_validate):
    from business_policy import Policy, PolicyError, utc
    from querying import conditions
    from schema import SPEC, engine, metadata

    policy = Policy(SPEC)
    business = SPEC["business"]
    tables = metadata.tables
    entities = {item["name"]: item for item in SPEC["entities"]}
    # Replace only legacy CRUD/schema routes. Authentication token verification
    # remains the same; role is loaded fresh from the server for every request.
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if not getattr(route, "path", "").startswith("/api/")
        and getattr(route, "path", "") != "/schema"
    ]

    def current(user_id=Depends(actor_dependency)):
        with engine.connect() as connection:
            row = (
                connection.execute(select(tables["users"]).where(tables["users"].c.id == user_id))
                .mappings()
                .first()
            )
        if not row or row["role"] not in policy.roles:
            raise HTTPException(403, "账号没有有效业务角色")
        return {"id": row["id"], "username": row["username"], "role": row["role"]}

    def grant(actor, entity, action):
        try:
            return policy.grant(actor["role"], entity, action)
        except PolicyError as exc:
            raise HTTPException(403, str(exc)) from None

    def table(entity):
        if entity not in entities:
            raise HTTPException(404, "实体不存在")
        return tables[entity]

    def scope(actor, entity, action):
        permission = grant(actor, entity, action)
        target = table(entity)
        if permission["scope"] == "all":
            return []
        key = (
            "created_by"
            if permission["scope"] == "own"
            else policy.resource(entity)["assignee_field"]
        )
        return [target.c[key] == actor["id"]]

    def record(connection, actor, entity, record_id, action, *, lock=False, archived=False):
        target = table(entity)
        stmt = select(target).where(target.c.id == record_id, *scope(actor, entity, action))
        if not archived:
            stmt = stmt.where(target.c.archived_at.is_(None))
        if lock:
            stmt = stmt.with_for_update()
        row = connection.execute(stmt).mappings().first()
        if row is None:
            raise HTTPException(404, "记录不存在或无权访问")
        return dict(row)

    def administrator(actor):
        if actor["role"] not in business["role_admin_roles"]:
            raise HTTPException(403, "只有已批准的角色管理员可以管理账号")

    def history_actor_names(connection, rows):
        """Resolve only actors from already-authorized history, never arbitrary IDs."""
        identities = sorted({row["actor_id"] for row in rows})
        users = tables["users"]
        result = {}
        for start in range(0, len(identities), 100):
            result.update(
                connection.execute(
                    select(users.c.id, users.c.username).where(
                        users.c.id.in_(identities[start : start + 100])
                    )
                ).all()
            )
        return result

    def serialize_administrator(connection, actor):
        # A real UPDATE serializes SQLite writers too (FOR UPDATE is ignored
        # there). Recheck the caller after the lock, not only at request start.
        marker = tables["business_setup"]
        changed = connection.execute(
            update(marker).where(marker.c.key == "bootstrap_admin").values(key="bootstrap_admin")
        ).rowcount
        if changed != 1:
            raise HTTPException(409, "管理员尚未初始化")
        role = connection.scalar(
            select(tables["users"].c.role).where(tables["users"].c.id == actor["id"])
        )
        if role not in business["role_admin_roles"]:
            raise HTTPException(403, "账号角色已变化，请重新登录")

    def event(connection, actor, entity, record_id, action, before, after):
        identity = str(uuid.uuid4())
        connection.execute(
            insert(tables["business_audit"]).values(
                id=identity,
                entity=entity,
                record_id=record_id,
                actor_id=actor["id"],
                action=action,
                created_at=utc(),
                before_json=json.dumps(before, ensure_ascii=False) if before is not None else None,
                after_json=json.dumps(after, ensure_ascii=False) if after is not None else None,
            )
        )
        return identity

    def notify(connection, entity, row, name, identity, transition=None, notification=None):
        for item in business["notifications"]:
            if notification is not None and item != notification:
                continue
            if item["entity"] != entity or item["event"] != name:
                continue
            if name == "transitioned" and item["transition"] != transition:
                continue
            recipient = (
                row["created_by"]
                if item["recipient"] == "creator"
                else row.get(policy.resource(entity)["assignee_field"])
            )
            if not recipient:
                continue
            key = hashlib.sha256(f"{identity}:{entity}:{recipient}:{name}".encode()).hexdigest()
            if connection.scalar(
                select(tables["business_notifications"].c.id).where(
                    tables["business_notifications"].c.dedupe_key == key
                )
            ):
                continue
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(tables["business_notifications"]).values(
                            id=str(uuid.uuid4()),
                            recipient_id=recipient,
                            entity=entity,
                            record_id=row["id"],
                            event=name,
                            created_at=utc(),
                            dedupe_key=key,
                        )
                    )
            except IntegrityError:
                # Only an exact event/recipient duplicate is safe to suppress. Other
                # constraint failures must roll back the originating mutation too.
                if not connection.scalar(
                    select(tables["business_notifications"].c.id).where(
                        tables["business_notifications"].c.dedupe_key == key
                    )
                ):
                    raise

    def reference_checks(connection, actor, entity, values, before=None):
        for (source, field), relation in policy.relations.items():
            if source != entity or values.get(field) is None:
                continue
            if before is not None and values[field] == before.get(field):
                continue  # An unchanged established relation is not a new reference grant.
            value, target = values[field], relation["target_entity"]
            if target == "$users":
                user = (
                    connection.execute(select(tables["users"]).where(tables["users"].c.id == value))
                    .mappings()
                    .first()
                )
                if user is None:
                    raise HTTPException(422, "关联用户不存在")
                if field == policy.resource(entity).get("assignee_field"):
                    permission = policy.permissions.get((user["role"], entity))
                    if (
                        not permission
                        or "read" not in permission["actions"]
                        or permission["scope"] not in {"all", "assigned"}
                    ):
                        raise HTTPException(422, "该用户的业务角色不能处理此资源")
            else:
                record(connection, actor, target, value, "read")

    def values_for(actor, entity, data, old=None):
        if not isinstance(data, dict):
            raise HTTPException(422, "记录必须是对象")
        protected = policy.protected(entity)
        if set(data) & protected:
            raise HTTPException(422, "系统字段、分配和状态只能通过专用操作修改")
        values = {f["name"]: old.get(f["name"]) for f in entities[entity]["fields"]} if old else {}
        values.update(data)
        workflow = policy.workflow(entity)
        if workflow and old is None:
            values[workflow["status_field"]] = workflow["initial"]
        if old is None:
            for f in entities[entity]["fields"]:
                if f["name"] in protected and f["name"] not in values:
                    values[f["name"]] = None
        try:
            value = policy.validate_fields(entity, values)
            from app import RULES

            RULES.validate(entity, value)
            return value
        except ValueError, TypeError, OverflowError:
            raise HTTPException(422, "字段或业务规则验证失败") from None

    @app.get("/business/me")
    def me(actor=Depends(current)):
        return actor

    @app.get("/schema")
    def schema(actor=Depends(current)):
        from schema import ROOT

        selection = json.loads((ROOT / "selection.json").read_text(encoding="utf-8"))
        visible = [
            name
            for name in entities
            if "read" in policy.permissions.get((actor["role"], name), {}).get("actions", [])
        ]
        return {
            "spec": {**SPEC, "entities": [entities[name] for name in visible]},
            "selection": selection,
            "actor": actor,
            "permissions": {
                name: policy.permissions.get((actor["role"], name)) for name in visible
            },
        }

    @app.get("/business/users")
    def users(entity: str | None = None, actor=Depends(current)):
        if entity is None:
            administrator(actor)
        else:
            grant(actor, entity, "assign")
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    select(tables["users"].c.id, tables["users"].c.username, tables["users"].c.role)
                )
                .mappings()
                .all()
            )
        if entity:
            rows = [
                row
                for row in rows
                if "read" in policy.permissions.get((row["role"], entity), {}).get("actions", [])
                and policy.permissions[row["role"], entity]["scope"] in {"all", "assigned"}
            ]
        return [dict(row) for row in rows]

    @app.post("/business/users", status_code=201)
    def create_user(data: UserBody, actor=Depends(current)):
        administrator(actor)
        if data.role not in policy.roles:
            raise HTTPException(422, "角色未声明")
        identity = str(uuid.uuid4())
        try:
            with engine.begin() as connection:
                serialize_administrator(connection, actor)
                connection.execute(
                    insert(tables["users"]).values(
                        id=identity,
                        username=data.username,
                        password=password_hash(data.password),
                        role=data.role,
                    )
                )
                event(
                    connection,
                    actor,
                    "$users",
                    identity,
                    "create_user",
                    None,
                    {"username": data.username, "role": data.role},
                )
        except IntegrityError:
            raise HTTPException(409, "用户名已经存在") from None
        return {"id": identity, "username": data.username, "role": data.role}

    @app.put("/business/users/{identity}/role")
    def change_role(identity: str, data: RoleBody, actor=Depends(current)):
        administrator(actor)
        if data.role not in policy.roles:
            raise HTTPException(422, "角色未声明")
        with engine.begin() as connection:
            serialize_administrator(connection, actor)
            old = (
                connection.execute(select(tables["users"]).where(tables["users"].c.id == identity))
                .mappings()
                .first()
            )
            if old is None:
                raise HTTPException(404, "用户不存在")
            if (
                old["role"] in business["role_admin_roles"]
                and data.role not in business["role_admin_roles"]
            ):
                administrators = connection.execute(
                    select(tables["users"].c.id).where(
                        tables["users"].c.role.in_(business["role_admin_roles"])
                    )
                ).all()
                if len(administrators) <= 1:
                    raise HTTPException(409, "不能移除最后一个管理员")
            connection.execute(
                update(tables["users"])
                .where(tables["users"].c.id == identity)
                .values(role=data.role)
            )
            event(
                connection,
                actor,
                "$users",
                identity,
                "change_role",
                {"role": old["role"]},
                {"role": data.role},
            )
        return {"id": identity, "role": data.role}

    @app.post("/business/labels/{entity}")
    def reference_labels(entity: str, data: LabelRequest, actor=Depends(current)):
        """Resolve only references present in rows this actor can already read."""
        source = table(entity)
        result = {}
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    select(source).where(
                        source.c.id.in_(data.record_ids),
                        source.c.archived_at.is_(None),
                        *scope(actor, entity, "read"),
                    )
                )
                .mappings()
                .all()
            )
            for relation in business["relations"]:
                if relation["entity"] != entity:
                    continue
                key, target_name = relation["field"], relation["target_entity"]
                identities = {row[key] for row in rows if row[key] is not None}
                if not identities:
                    continue
                if target_name == "$users":
                    target = tables["users"]
                    values = connection.execute(
                        select(target.c.id, target.c.username).where(target.c.id.in_(identities))
                    ).all()
                    result[key] = {identity: username for identity, username in values}
                elif "read" in policy.permissions.get((actor["role"], target_name), {}).get(
                    "actions", []
                ):
                    target = table(target_name)
                    values = (
                        connection.execute(
                            select(target).where(
                                target.c.id.in_(identities), *scope(actor, target_name, "read")
                            )
                        )
                        .mappings()
                        .all()
                    )
                    result[key] = {
                        row["id"]: row.get("name") or row.get("title") or "关联记录"
                        for row in values
                    }
        return result

    @app.get("/api/{entity}")
    def list_items(
        entity: str,
        request: Request,
        response: Response,
        limit: int = 50,
        offset: int = 0,
        actor=Depends(current),
    ):
        target = table(entity)
        try:
            if (
                len(request.query_params.multi_items()) != len(request.query_params)
                or not 1 <= limit <= 100
                or offset < 0
            ):
                raise ValueError("查询或分页参数无效")
            expressions, ordering = conditions(
                target, entities[entity], request.query_params, actor["id"], scoped=False
            )
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        expressions += [target.c.archived_at.is_(None), *scope(actor, entity, "read")]
        from sqlalchemy import func

        with engine.connect() as connection:
            count = connection.scalar(select(func.count()).select_from(target).where(*expressions))
            rows = (
                connection.execute(
                    select(target)
                    .where(*expressions)
                    .order_by(ordering, target.c.id)
                    .limit(limit)
                    .offset(offset)
                )
                .mappings()
                .all()
            )
        response.headers["X-Total-Count"] = str(count)
        return [dict(row) for row in rows]

    @app.post("/api/{entity}", status_code=201)
    def create(entity: str, data: dict, actor=Depends(current)):
        grant(actor, entity, "create")
        values = values_for(actor, entity, data)
        now = utc()
        values.update(
            id=str(uuid.uuid4()),
            owner_id=actor["id"],
            created_by=actor["id"],
            created_at=now,
            updated_at=now,
        )
        try:
            with engine.begin() as connection:
                reference_checks(connection, actor, entity, values)
                connection.execute(insert(table(entity)).values(**values))
                row = dict(
                    connection.execute(
                        select(table(entity)).where(table(entity).c.id == values["id"])
                    )
                    .mappings()
                    .one()
                )
                identity = event(connection, actor, entity, row["id"], "created", None, row)
                notify(connection, entity, row, "created", identity)
        except IntegrityError:
            raise HTTPException(409, "关联记录冲突") from None
        return row

    @app.get("/api/{entity}/{identity}")
    def get(entity: str, identity: str, actor=Depends(current)):
        with engine.connect() as connection:
            return record(connection, actor, entity, identity, "read")

    @app.put("/api/{entity}/{identity}")
    def edit(entity: str, identity: str, data: dict, actor=Depends(current)):
        with engine.begin() as connection:
            before = record(connection, actor, entity, identity, "update", lock=True)
            values = values_for(actor, entity, data, before)
            reference_checks(connection, actor, entity, values, before)
            values["updated_at"] = utc()
            changed = connection.execute(
                update(table(entity))
                .where(
                    table(entity).c.id == identity,
                    table(entity).c.updated_at == before["updated_at"],
                )
                .values(**values)
            ).rowcount
            if changed != 1:
                raise HTTPException(409, "记录已更新，请刷新")
            after = {**before, **values}
            event(connection, actor, entity, identity, "updated", before, after)
            return after

    @app.post("/api/{entity}/{identity}/archive")
    def archive(entity: str, identity: str, actor=Depends(current)):
        with engine.begin() as connection:
            before = record(connection, actor, entity, identity, "archive", lock=True)
            now = utc()
            connection.execute(
                update(table(entity))
                .where(table(entity).c.id == identity)
                .values(archived_at=now, updated_at=now)
            )
            after = {**before, "archived_at": now, "updated_at": now}
            event(connection, actor, entity, identity, "archived", before, after)
            return after

    @app.post("/api/{entity}/{identity}/assign")
    def assign(entity: str, identity: str, data: Assignment, actor=Depends(current)):
        with engine.begin() as connection:
            before = record(connection, actor, entity, identity, "assign", lock=True)
            field = policy.resource(entity)["assignee_field"]
            if (
                data.user_id is None
                and next(f for f in entities[entity]["fields"] if f["name"] == field)["required"]
            ):
                raise HTTPException(422, "负责人必填")
            after = {**before, field: data.user_id, "updated_at": utc()}
            reference_checks(connection, actor, entity, after, before)
            changed = connection.execute(
                update(table(entity))
                .where(
                    table(entity).c.id == identity,
                    table(entity).c.updated_at == before["updated_at"],
                )
                .values(**{field: data.user_id, "updated_at": after["updated_at"]})
            ).rowcount
            if changed != 1:
                raise HTTPException(409, "记录已更新，请刷新")
            event_id = event(connection, actor, entity, identity, "assigned", before, after)
            notify(connection, entity, after, "assigned", event_id)
            return after

    @app.post("/api/{entity}/{identity}/transition")
    def transition(entity: str, identity: str, data: TransitionBody, actor=Depends(current)):
        with engine.begin() as connection:
            before = record(connection, actor, entity, identity, "transition", lock=True)
            workflow = policy.workflow(entity)
            try:
                operation = policy.transition(
                    actor["role"], entity, data.transition, before[workflow["status_field"]]
                )
            except PolicyError as exc:
                raise HTTPException(409, str(exc)) from None
            values = {workflow["status_field"]: operation["to_state"], "updated_at": utc()}
            if operation.get("set_timestamp"):
                values[operation["set_timestamp"]] = values["updated_at"]
            changed = connection.execute(
                update(table(entity))
                .where(
                    table(entity).c.id == identity,
                    table(entity).c[workflow["status_field"]] == before[workflow["status_field"]],
                    table(entity).c.updated_at == before["updated_at"],
                )
                .values(**values)
            ).rowcount
            if changed != 1:
                raise HTTPException(409, "状态已变化，请刷新")
            after = {**before, **values}
            event_id = event(
                connection,
                actor,
                entity,
                identity,
                "transitioned:" + data.transition,
                before,
                after,
            )
            notify(connection, entity, after, "transitioned", event_id, data.transition)
            return after

    @app.post("/api/{entity}/{identity}/notes", status_code=201)
    def add_note(entity: str, identity: str, data: NoteBody, actor=Depends(current)):
        with engine.begin() as connection:
            row = record(connection, actor, entity, identity, "add_note", lock=True)
            if not policy.resource(entity)["notes"]:
                raise HTTPException(403, "记录未启用备注")
            note = {
                "id": str(uuid.uuid4()),
                "entity": entity,
                "record_id": identity,
                "actor_id": actor["id"],
                "created_at": utc(),
                "body": data.body,
            }
            connection.execute(insert(tables["business_notes"]).values(**note))
            eid = event(connection, actor, entity, identity, "note_added", None, note)
            notify(connection, entity, row, "note_added", eid)
            return note

    @app.get("/api/{entity}/{identity}/notes")
    def notes(entity: str, identity: str, actor=Depends(current)):
        with engine.connect() as connection:
            record(connection, actor, entity, identity, "read_history", archived=True)
            rows = (
                connection.execute(
                    select(tables["business_notes"])
                    .where(
                        tables["business_notes"].c.entity == entity,
                        tables["business_notes"].c.record_id == identity,
                    )
                    .order_by(tables["business_notes"].c.created_at, tables["business_notes"].c.id)
                )
                .mappings()
                .all()
            )
            names = history_actor_names(connection, rows)
            return [{**dict(row), "actor_username": names.get(row["actor_id"])} for row in rows]

    @app.get("/api/{entity}/{identity}/history")
    def history(entity: str, identity: str, actor=Depends(current)):
        with engine.connect() as connection:
            # Audit is an independent grant, not a history permission add-on.
            full = "read_audit" in policy.permissions.get((actor["role"], entity), {}).get(
                "actions", []
            )
            record(
                connection,
                actor,
                entity,
                identity,
                "read_audit" if full else "read_history",
                archived=True,
            )
            rows = (
                connection.execute(
                    select(tables["business_audit"])
                    .where(
                        tables["business_audit"].c.entity == entity,
                        tables["business_audit"].c.record_id == identity,
                    )
                    .order_by(tables["business_audit"].c.created_at, tables["business_audit"].c.id)
                )
                .mappings()
                .all()
            )
            names = history_actor_names(connection, rows)
            # History shows actors/actions/time; full snapshots require read_audit.
            return [
                {
                    **{k: row[k] for k in ("id", "actor_id", "action", "created_at")},
                    "actor_username": names.get(row["actor_id"]),
                    **(
                        {
                            "before": json.loads(row["before_json"])
                            if row["before_json"]
                            else None,
                            "after": json.loads(row["after_json"]) if row["after_json"] else None,
                        }
                        if full
                        else {}
                    ),
                }
                for row in rows
            ]

    @app.get("/business/related/{entity}/{identity}")
    def related(entity: str, identity: str, actor=Depends(current)):
        result = []
        with engine.connect() as connection:
            record(connection, actor, entity, identity, "read", archived=True)
            for relation in business["relations"]:
                source = relation["entity"]
                if relation["target_entity"] != entity or "read" not in policy.permissions.get(
                    (actor["role"], source), {}
                ).get("actions", []):
                    continue
                target = table(source)
                rows = (
                    connection.execute(
                        select(target)
                        .where(
                            target.c[relation["field"]] == identity,
                            target.c.archived_at.is_(None),
                            *scope(actor, source, "read"),
                        )
                        .order_by(target.c.created_at.desc())
                        .limit(100)
                    )
                    .mappings()
                    .all()
                )
                result.append(
                    {
                        "entity": source,
                        "field": relation["field"],
                        "records": [dict(row) for row in rows],
                    }
                )
        return result

    @app.get("/business/metrics")
    def metrics(actor=Depends(current)):
        result = []
        with engine.connect() as connection:
            for metric in business["metrics"]:
                if "read_metrics" not in policy.permissions.get(
                    (actor["role"], metric["entity"]), {}
                ).get("actions", []):
                    continue
                target = table(metric["entity"])
                rows = (
                    connection.execute(
                        select(target).where(
                            target.c.archived_at.is_(None),
                            *scope(actor, metric["entity"], "read_metrics"),
                        )
                    )
                    .mappings()
                    .all()
                )
                result.append(
                    {
                        "name": metric["name"],
                        "label": metric["label"],
                        **policy.metric(rows, metric),
                    }
                )
        return result

    @app.get("/business/notifications")
    def notifications(actor=Depends(current)):
        with engine.begin() as connection:
            for item in business["notifications"]:
                if item["event"] != "due":
                    continue
                entity, due = item["entity"], item["due_field"]
                if "read" not in policy.permissions.get((actor["role"], entity), {}).get(
                    "actions", []
                ):
                    continue
                target = table(entity)
                recipient = (
                    target.c.created_by
                    if item["recipient"] == "creator"
                    else target.c[policy.resource(entity)["assignee_field"]]
                )
                rows = (
                    connection.execute(
                        select(target).where(
                            recipient == actor["id"],
                            *scope(actor, entity, "read"),
                            target.c.archived_at.is_(None),
                            target.c[due].is_not(None),
                            target.c[due] <= utc(),
                        )
                    )
                    .mappings()
                    .all()
                )
                for row in rows:
                    workflow = policy.workflow(entity)
                    if workflow and row[workflow["status_field"]] not in {
                        state
                        for transition in workflow["transitions"]
                        for state in transition["from_states"]
                    }:
                        continue  # Completed terminal records do not generate overdue reminders.
                    notify(
                        connection,
                        entity,
                        dict(row),
                        "due",
                        f"due:{entity}:{row['id']}:{due}:{row[due]}",
                    )
            return [
                dict(row)
                for row in connection.execute(
                    select(tables["business_notifications"])
                    .where(tables["business_notifications"].c.recipient_id == actor["id"])
                    .order_by(
                        tables["business_notifications"].c.created_at.desc(),
                        tables["business_notifications"].c.id,
                    )
                    .limit(200)
                ).mappings()
            ]

    @app.post("/business/notifications/{identity}/read")
    def mark_read(identity: str, actor=Depends(current)):
        target = tables["business_notifications"]
        with engine.begin() as connection:
            row = (
                connection.execute(
                    select(target).where(
                        target.c.id == identity, target.c.recipient_id == actor["id"]
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                raise HTTPException(404, "通知不存在")
            timestamp = row["read_at"] or utc()
            connection.execute(
                update(target)
                .where(target.c.id == identity, target.c.recipient_id == actor["id"])
                .values(read_at=timestamp)
            )
        return {"id": identity, "read_at": timestamp}
````
