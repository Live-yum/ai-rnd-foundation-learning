# templates/business/fastapiadmin/controller.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：FastapiAdmin原生认证下的业务HTTP入口。** 路由接收严格动作载荷，使用框架当前用户和数据库依赖调用运行时；业务权限不能由浏览器传入角色或负责人来决定。

**对应关系：** 原生路由注册 → controller → runtime → SQLAlchemy模型与policy。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configuration`（L22–L35）：接收`auth`、`db`。 调用`Depends`、`rt.actor`、`SuccessResponse`、`BusinessRouter.get`。 返回路径：L27的`SuccessResponse( data={ "actor": who, "entities": rt.PLAN["entities"], "business": rt.SPEC…`。
- `bootstrap`（L39–L64）：接收`auth`、`db`。 控制顺序：L42按`not auth.user.is_superuser`分支。 调用`Depends`、`rt.fail`、`db.add`、`BusinessEvent`、`db.flush`、`rt.set_role`、`db.rollback`、`db.commit`、`SuccessResponse`等。 返回路径：L64的`SuccessResponse(data={"initialized": True})`。
- `join`（L68–L99）：接收`auth`、`db`。 控制顺序：L69按`not rt.SPEC["registration"]["enabled"]`分支；L74按`initialized is None`分支；L85按`existing is not None`分支。 调用`Depends`、`rt.fail`、`db.scalar`、`select(BusinessEvent.id).where(BusinessEvent.source_key == "boots…`、`select(BusinessEvent.id).where`、`select`、`select(UserModel).where(UserModel.id == auth.user.id).with_for_up…`、`select(UserModel).where`、`select(RoleModel.id) .join(UserRolesModel, RoleModel.id == UserRo…`等。 返回路径：L99的`SuccessResponse(data={"role": role})`。
- `role`（L103–L130）：接收`user_id`、`data`、`auth`、`db`。 控制顺序：L112按`marker is None`分支；L115按`who["role"] not in rt.SPEC["role_admin_roles"] or set(data) != {"role"}`分支；L117按`str(user_id) == who["id"]`分支。 调用`Body`、`Depends`、`db.scalar`、`select(BusinessEvent).where(BusinessEvent.source_key == "bootstra…`、`select(BusinessEvent).where`、`select`、`rt.fail`、`rt.actor`、`set`等。 返回路径：L130的`SuccessResponse(data={"id": user_id, "role": data["role"]})`。
- `users`（L134–L158）：接收`auth`、`db`。 控制顺序：L138按`who["role"] not in rt.SPEC["role_admin_roles"] and not any( p["role"] == who["role"] …`分支。 调用`Depends`、`rt.actor`、`any`、`rt.fail`、`select(UserModel.id, UserModel.name, UserModel.username, RoleMode…`、`select`、`UserModel.is_deleted.is_`、`RoleModel.is_deleted.is_`、`RoleModel.code.startswith`等。 返回路径：L158的`SuccessResponse(data=result)`。
- `metrics`（L162–L186）：接收`auth`、`db`。 控制顺序：L167遍历`rt.SPEC["metrics"]`；L175按`metric["kind"] == "group_count"`分支；L177遍历`value["groups"]`。 调用`Depends`、`rt.actor`、`rt.POLICY.grant`、`rt.rows`、`rt.POLICY.metric`、`rt.serialize`、`rt.present_values`、`groups.append`、`shown["_display"].get`等。 返回路径：L186的`SuccessResponse(data=result)`。
- `inbox`（L190–L260）：接收`auth`、`db`。 控制顺序：L197遍历`rt.SPEC["notifications"]`；L198按`rule["event"] != "due"`分支；L214遍历`candidates`；L216按`await db.scalar(select(BusinessEvent.id).where(BusinessEvent.source_key == key)) is N…`分支；L240遍历`notices`；L246按`error.status_code not in {403, 404}`分支；L247抛异常，停止当前正常路径。 调用`Depends`、`rt.actor`、`db.scalar`、`select(UserModel).where(UserModel.id == auth.user.id).with_for_up…`、`select(UserModel).where`、`select`、`datetime.now`、`getattr`、`rt.POLICY.resource`等。 返回路径：L260的`SuccessResponse(data=result)`。
- `read_notice`（L264–L282）：接收`notice_id`、`auth`、`db`。 控制顺序：L278按`notice is None`分支。 调用`Depends`、`rt.actor`、`db.scalar`、`select(BusinessEvent) .where( BusinessEvent.id == rt.identifier(n…`、`select(BusinessEvent) .where`、`select`、`rt.identifier`、`rt.fail`、`datetime.now`等。 返回路径：L282的`SuccessResponse(data={"read": True})`。
- `listing`（L286–L315）：接收`entity`、`q`、`filters`、`archived`、`page`、`page_size`、`auth`、`db`。 控制顺序：L300按`not isinstance(filters, dict)`分支。 调用`Query`、`Depends`、`json.loads`、`isinstance`、`rt.fail`、`rt.actor`、`rt.rows`、`SuccessResponse`、`rt.present_values`等。 返回路径：L307的`SuccessResponse( data={ "items": [ await rt.present_values(db, who, entity, rt.serialize(r…`。
- `create`（L319–L327）：接收`entity`、`data`、`auth`、`db`。 控制顺序：L325按`entity not in rt.MODELS`分支。 调用`Body`、`Depends`、`rt.fail`、`SuccessResponse`、`rt.create`、`rt.actor`、`BusinessRouter.post`。 返回路径：L327的`SuccessResponse(data=await rt.create(db, await rt.actor(db, auth), entity, data))`。
- `history`（L331–L374）：接收`entity`、`row_id`、`audit`、`auth`、`db`。 调用`Depends`、`rt.actor`、`rt.record`、`( await db.scalars( select(BusinessEvent) .where( BusinessEvent.e…`、`db.scalars`、`select(BusinessEvent) .where( BusinessEvent.entity == entity, Bus…`、`select(BusinessEvent) .where`、`select`、`rt.identifier`等。 返回路径：L352的`SuccessResponse( data=[ { "id": str(e.id), "event": e.event, "actor": str(e.actor), "actor…`。
- `related`（L378–L400）：接收`entity`、`row_id`、`auth`、`db`。 控制顺序：L387遍历`rt.SPEC["relations"]`；L388按`relation["target_entity"] != entity`分支。 调用`Depends`、`rt.actor`、`rt.record`、`rt.POLICY.grant`、`rt.present_values`、`rt.serialize`、`rt.rows`、`str`、`getattr`等。 返回路径：L400的`SuccessResponse(data=result)`。
- `mutation`（L404–L416）：接收`entity`、`row_id`、`action`、`data`、`auth`、`db`。 控制顺序：L412按`action not in {"update", "assign", "transition", "archive", "add_note"}`分支。 调用`Body`、`Depends`、`rt.fail`、`SuccessResponse`、`rt.mutate`、`rt.actor`、`BusinessRouter.post`。 返回路径：L414的`SuccessResponse( data=await rt.mutate(db, await rt.actor(db, auth), entity, row_id, action…`。

</details>

**创建路径：** `templates/business/fastapiadmin/controller.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L416。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14113`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/fastapiadmin/controller.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5cdac0f03b27245fcf0fd7c391f984cfab26390771c108aac37b0c449ebee443"} -->
````python
# templates/business/fastapiadmin/controller.py
# ruff: noqa: B008
"""Native FastapiAdmin session-authenticated business API."""

from datetime import UTC, datetime

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import db_getter, get_current_user
from app.modules.system.role.model import RoleModel
from app.modules.system.user.model import UserModel, UserRolesModel
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import runtime as rt
from .model import BusinessEvent

BusinessRouter = APIRouter(tags=["Business workflows"])


@BusinessRouter.get("/configuration")
async def configuration(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    who = await rt.actor(db, auth)
    permissions = [p for p in rt.SPEC["permissions"] if p["role"] == who["role"]]
    return SuccessResponse(
        data={
            "actor": who,
            "entities": rt.PLAN["entities"],
            "business": rt.SPEC,
            "permissions": permissions,
            "can_manage_roles": who["role"] in rt.SPEC["role_admin_roles"],
        }
    )


@BusinessRouter.post("/bootstrap")
async def bootstrap(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    if not auth.user.is_superuser:
        rt.fail()
    from sqlalchemy.exc import IntegrityError

    # Namespace-wide unique marker serializes different native administrators.
    db.add(
        BusinessEvent(
            entity="roles",
            record_id=auth.user.id,
            actor=auth.user.id,
            event="bootstrap",
            payload={"role": rt.SPEC["bootstrap_role"]},
            source_key="bootstrap",
        )
    )
    try:
        await db.flush()
        await rt.set_role(db, auth.user.id, rt.SPEC["bootstrap_role"])
    except IntegrityError:
        await db.rollback()
        rt.fail(409, "Project roles already initialized")
    await db.commit()
    return SuccessResponse(data={"initialized": True})


@BusinessRouter.post("/join")
async def join(auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)):
    if not rt.SPEC["registration"]["enabled"]:
        rt.fail()
    initialized = await db.scalar(
        select(BusinessEvent.id).where(BusinessEvent.source_key == "bootstrap").with_for_update()
    )
    if initialized is None:
        rt.fail(409, "A native administrator must initialize this project first")
    await db.scalar(select(UserModel).where(UserModel.id == auth.user.id).with_for_update())
    existing = await db.scalar(
        select(RoleModel.id)
        .join(UserRolesModel, RoleModel.id == UserRolesModel.role_id)
        .where(
            UserRolesModel.user_id == auth.user.id,
            RoleModel.code.startswith(rt.ROLE_PREFIX, autoescape=True),
        )
    )
    if existing is not None:
        rt.fail(409, "Project membership already exists")
    role = rt.SPEC["registration"]["default_role"]
    await rt.set_role(db, auth.user.id, role)
    db.add(
        BusinessEvent(
            entity="roles",
            record_id=auth.user.id,
            actor=auth.user.id,
            event="joined",
            payload={"role": role},
        )
    )
    await db.commit()
    return SuccessResponse(data={"role": role})


@BusinessRouter.put("/users/{user_id}/role")
async def role(
    user_id: str,
    data: dict = Body(...),
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    marker = await db.scalar(
        select(BusinessEvent).where(BusinessEvent.source_key == "bootstrap").with_for_update()
    )
    if marker is None:
        rt.fail(409, "Business project is not initialized")
    who = await rt.actor(db, auth)
    if who["role"] not in rt.SPEC["role_admin_roles"] or set(data) != {"role"}:
        rt.fail()
    if str(user_id) == who["id"]:
        rt.fail(409, "Role administrators cannot remove their own role")
    await rt.set_role(db, user_id, data["role"])
    db.add(
        BusinessEvent(
            entity="roles",
            record_id=rt.identifier(user_id),
            actor=rt.identifier(who["id"]),
            event="role_changed",
            payload={"role": data["role"]},
        )
    )
    await db.commit()
    return SuccessResponse(data={"id": user_id, "role": data["role"]})


@BusinessRouter.get("/users")
async def users(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    who = await rt.actor(db, auth)
    if who["role"] not in rt.SPEC["role_admin_roles"] and not any(
        p["role"] == who["role"] and "assign" in p["actions"] for p in rt.SPEC["permissions"]
    ):
        rt.fail()
    query = (
        select(UserModel.id, UserModel.name, UserModel.username, RoleModel.code)
        .join(UserRolesModel, UserModel.id == UserRolesModel.user_id)
        .join(RoleModel, RoleModel.id == UserRolesModel.role_id)
        .where(
            UserModel.is_deleted.is_(False),
            UserModel.status == 0,
            RoleModel.is_deleted.is_(False),
            RoleModel.status == 0,
            RoleModel.code.startswith(rt.ROLE_PREFIX, autoescape=True),
        )
    )
    result = [
        {"id": str(uid), "name": name, "username": username, "role": code[len(rt.ROLE_PREFIX) :]}
        for uid, name, username, code in (await db.execute(query)).all()
    ]
    return SuccessResponse(data=result)


@BusinessRouter.get("/metrics")
async def metrics(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    who = await rt.actor(db, auth)
    result = []
    for metric in rt.SPEC["metrics"]:
        try:
            rt.POLICY.grant(who["role"], metric["entity"], "read_metrics")
        except rt.PolicyError:
            continue
        rows = await rt.rows(db, who, metric["entity"], "read_metrics")
        value = rt.POLICY.metric([rt.serialize(row, metric["entity"]) for row in rows], metric)
        item = {"name": metric["name"], "label": metric["label"], "value": value}
        if metric["kind"] == "group_count":
            cache, groups = {}, []
            for group in value["groups"]:
                shown = await rt.present_values(
                    db, who, metric["entity"], {metric["group_by"]: group["key"]}, cache
                )
                groups.append(
                    {**group, "key": shown["_display"].get(metric["group_by"], group["key"])}
                )
            item["display_groups"] = groups
        result.append(item)
    return SuccessResponse(data=result)


@BusinessRouter.get("/inbox")
async def inbox(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    who = await rt.actor(db, auth)
    # Recipient row lock makes due reminders idempotent without an external scheduler.
    await db.scalar(select(UserModel).where(UserModel.id == auth.user.id).with_for_update())
    now = datetime.now(UTC)
    for rule in rt.SPEC["notifications"]:
        if rule["event"] != "due":
            continue
        model = rt.MODELS[rule["entity"]]
        recipient = (
            model.created_id
            if rule["recipient"] == "creator"
            else getattr(model, rt.POLICY.resource(rule["entity"])["assignee_field"])
        )
        due = getattr(model, rule["due_field"])
        candidates = (
            await db.scalars(
                select(model).where(
                    recipient == auth.user.id, due <= now, model.is_deleted.is_(False)
                )
            )
        ).all()
        for row in candidates:
            key = f"due:{rule['entity']}:{row.id}:{rule['due_field']}:{auth.user.id}"
            if (
                await db.scalar(select(BusinessEvent.id).where(BusinessEvent.source_key == key))
                is None
            ):
                db.add(
                    BusinessEvent(
                        entity=rule["entity"],
                        record_id=row.id,
                        actor=auth.user.id,
                        recipient=auth.user.id,
                        event="notification",
                        payload={"event": "due"},
                        source_key=key,
                    )
                )
    await db.flush()
    notices = (
        await db.scalars(
            select(BusinessEvent)
            .where(BusinessEvent.recipient == auth.user.id)
            .order_by(BusinessEvent.id.desc())
        )
    ).all()
    result = []
    for n in notices:
        title = "业务记录"
        try:
            row = await rt.record(db, who, n.entity, n.record_id, "read")
            title = rt.record_title(n.entity, rt.serialize(row, n.entity))
        except rt.HTTPException as error:
            if error.status_code not in {403, 404}:
                raise
        result.append(
            {
                "id": str(n.id),
                "entity": n.entity,
                "record_id": str(n.record_id),
                "event": n.payload["event"],
                "record_title": title,
                "created_at": n.created_at.isoformat(),
                "read": n.read_at is not None,
            }
        )
    await db.commit()
    return SuccessResponse(data=result)


@BusinessRouter.post("/inbox/{notice_id}/read")
async def read_notice(
    notice_id: str,
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    await rt.actor(db, auth)
    notice = await db.scalar(
        select(BusinessEvent)
        .where(
            BusinessEvent.id == rt.identifier(notice_id),
            BusinessEvent.recipient == auth.user.id,
        )
        .with_for_update()
    )
    if notice is None:
        rt.fail(404)
    notice.read_at = notice.read_at or datetime.now(UTC)
    await db.commit()
    return SuccessResponse(data={"read": True})


@BusinessRouter.get("/{entity}/list")
async def listing(
    entity: str,
    q: str = "",
    filters: str = "{}",
    archived: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    import json

    try:
        filters = json.loads(filters)
        if not isinstance(filters, dict):
            rt.fail(422, "Invalid filters")
    except ValueError:
        rt.fail(422, "Invalid filters")
    who = await rt.actor(db, auth)
    rows = await rt.rows(db, who, entity, query=q, filters=filters, archived=archived)
    cache = {}
    return SuccessResponse(
        data={
            "items": [
                await rt.present_values(db, who, entity, rt.serialize(r, entity), cache)
                for r in rows[(page - 1) * page_size : page * page_size]
            ],
            "total": len(rows),
        }
    )


@BusinessRouter.post("/{entity}/create")
async def create(
    entity: str,
    data: dict = Body(...),
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    if entity not in rt.MODELS:
        rt.fail(404)
    return SuccessResponse(data=await rt.create(db, await rt.actor(db, auth), entity, data))


@BusinessRouter.get("/{entity}/{row_id}/history")
async def history(
    entity: str,
    row_id: str,
    audit: bool = False,
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    who = await rt.actor(db, auth)
    await rt.record(db, who, entity, row_id, "read_audit" if audit else "read_history")
    events = (
        await db.scalars(
            select(BusinessEvent)
            .where(
                BusinessEvent.entity == entity,
                BusinessEvent.record_id == rt.identifier(row_id),
                BusinessEvent.recipient.is_(None),
            )
            .order_by(BusinessEvent.id)
        )
    ).all()
    cache = {}
    return SuccessResponse(
        data=[
            {
                "id": str(e.id),
                "event": e.event,
                "actor": str(e.actor),
                "actor_name": await rt.user_label(db, e.actor, cache),
                "after_display": (
                    await rt.present_values(db, who, entity, e.payload["after"], cache)
                )["_display"]
                if audit and isinstance(e.payload.get("after"), dict)
                else {},
                "created_at": e.created_at.isoformat(),
                "data": e.payload
                if audit
                else {
                    "transition": e.payload.get("transition"),
                    "text": e.payload.get("text"),
                },
            }
            for e in events
        ]
    )


@BusinessRouter.get("/{entity}/{row_id}/related")
async def related(
    entity: str,
    row_id: str,
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    who = await rt.actor(db, auth)
    await rt.record(db, who, entity, row_id, "read")
    result, cache = {}, {}
    for relation in rt.SPEC["relations"]:
        if relation["target_entity"] != entity:
            continue
        child = relation["entity"]
        try:
            rt.POLICY.grant(who["role"], child, "read")
        except rt.PolicyError:
            continue
        result[child] = [
            await rt.present_values(db, who, child, rt.serialize(r, child), cache)
            for r in await rt.rows(db, who, child)
            if str(getattr(r, relation["field"])) == str(row_id)
        ]
    return SuccessResponse(data=result)


@BusinessRouter.post("/{entity}/{row_id}/{action}")
async def mutation(
    entity: str,
    row_id: str,
    action: str,
    data: dict = Body(...),
    auth: AuthSchema = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter),
):
    if action not in {"update", "assign", "transition", "archive", "add_note"}:
        rt.fail(404)
    return SuccessResponse(
        data=await rt.mutate(db, await rt.actor(db, auth), entity, row_id, action, data)
    )
````
