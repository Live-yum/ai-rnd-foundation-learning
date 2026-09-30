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
async def join(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    if not rt.SPEC["registration"]["enabled"]:
        rt.fail()
    initialized = await db.scalar(
        select(BusinessEvent.id)
        .where(BusinessEvent.source_key == "bootstrap")
        .with_for_update()
    )
    if initialized is None:
        rt.fail(409, "A native administrator must initialize this project first")
    await db.scalar(
        select(UserModel).where(UserModel.id == auth.user.id).with_for_update()
    )
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
        select(BusinessEvent)
        .where(BusinessEvent.source_key == "bootstrap")
        .with_for_update()
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
        p["role"] == who["role"] and "assign" in p["actions"]
        for p in rt.SPEC["permissions"]
    ):
        rt.fail()
    query = (
        select(UserModel.id, UserModel.name, RoleModel.code)
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
        {"id": str(uid), "name": name, "role": code[len(rt.ROLE_PREFIX) :]}
        for uid, name, code in (await db.execute(query)).all()
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
        value = rt.POLICY.metric(
            [rt.serialize(row, metric["entity"]) for row in rows], metric
        )
        result.append(
            {"name": metric["name"], "label": metric["label"], "value": value}
        )
    return SuccessResponse(data=result)


@BusinessRouter.get("/inbox")
async def inbox(
    auth: AuthSchema = Depends(get_current_user), db: AsyncSession = Depends(db_getter)
):
    await rt.actor(db, auth)
    # Recipient row lock makes due reminders idempotent without an external scheduler.
    await db.scalar(
        select(UserModel).where(UserModel.id == auth.user.id).with_for_update()
    )
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
                await db.scalar(
                    select(BusinessEvent.id).where(BusinessEvent.source_key == key)
                )
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
    result = [
        {
            "id": str(n.id),
            "entity": n.entity,
            "record_id": str(n.record_id),
            "event": n.payload["event"],
            "created_at": n.created_at.isoformat(),
            "read": n.read_at is not None,
        }
        for n in notices
    ]
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
    return SuccessResponse(
        data={
            "items": [
                rt.serialize(r, entity)
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
    return SuccessResponse(
        data=await rt.create(db, await rt.actor(db, auth), entity, data)
    )


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
    return SuccessResponse(
        data=[
            {
                "id": str(e.id),
                "event": e.event,
                "actor": str(e.actor),
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
    result = {}
    for relation in rt.SPEC["relations"]:
        if relation["target_entity"] != entity:
            continue
        child = relation["entity"]
        try:
            rt.POLICY.grant(who["role"], child, "read")
        except rt.PolicyError:
            continue
        result[child] = [
            rt.serialize(r, child)
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
