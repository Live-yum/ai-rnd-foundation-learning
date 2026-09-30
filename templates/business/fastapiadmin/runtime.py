"""Transactional native ORM business services; all authorization is server-side."""

import importlib
from datetime import UTC, date, datetime

from app.modules.system.menu.model import MenuModel
from app.modules.system.role.model import RoleMenusModel, RoleModel
from app.modules.system.user.model import UserModel, UserRolesModel
from fastapi import HTTPException
from sqlalchemy import delete, or_, select

from .model import CONFIG, BusinessEvent
from .policy import Policy, PolicyError

PLAN = CONFIG["plan"]
SPEC = PLAN["business"]
POLICY = Policy(PLAN)
ENTITIES = {e["name"]: e for e in PLAN["entities"]}
MODELS = {
    name: getattr(
        importlib.import_module(f"app.plugin.module_rnd.{name}.model"),
        "".join(part.title() for part in name.split("_")) + "Model",
    )
    for name in ENTITIES
}
ROLE_PREFIX = CONFIG["namespace"] + "_"


def fail(code=403, reason="Business permission denied"):
    raise HTTPException(code, reason)


def identifier(value):
    if isinstance(value, bool) or not str(value).isdigit() or int(value) < 1:
        fail(422, "Invalid record identifier")
    return int(value)


def date_value(value):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            fail(422, "Date must use YYYY-MM-DD")
        return parsed
    except ValueError, TypeError:
        fail(422, "Invalid date")


def instant(value):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if result.tzinfo is None:
            fail(422, "Timestamp must include timezone")
        return result.astimezone(UTC)
    except ValueError:
        fail(422, "Invalid timestamp")


def serialize(row, entity):
    result = {f["name"]: getattr(row, f["name"]) for f in ENTITIES[entity]["fields"]}
    for relation in SPEC["relations"]:
        if relation["entity"] == entity and result.get(relation["field"]) is not None:
            result[relation["field"]] = str(result[relation["field"]])
    result.update(
        id=str(row.id),
        created_by=str(row.created_id),
        created_at=row.created_time,
        updated_at=row.updated_time,
        archived_at=row.deleted_time if row.is_deleted else None,
    )
    return {
        k: (v.replace(tzinfo=UTC) if v.tzinfo is None else v.astimezone(UTC)).isoformat()
        if isinstance(v, datetime)
        else v.isoformat()
        if isinstance(v, date)
        else v
        for k, v in result.items()
    }


def record_title(entity, values):
    references = {r["field"] for r in SPEC["relations"] if r["entity"] == entity}
    for field in ENTITIES[entity]["fields"]:
        if field["kind"] == "text" and field["name"] not in references:
            value = values.get(field["name"])
            if value:
                return str(value)
    return ENTITIES[entity].get("description") or "业务记录"


async def user_label(db, user_id, cache):
    key = ("$users", str(user_id))
    if key not in cache:
        name = await db.scalar(
            select(UserModel.name)
            .join(UserRolesModel, UserModel.id == UserRolesModel.user_id)
            .join(RoleModel, RoleModel.id == UserRolesModel.role_id)
            .where(
                UserModel.id == identifier(user_id),
                UserModel.is_deleted.is_(False),
                RoleModel.is_deleted.is_(False),
                RoleModel.code.startswith(ROLE_PREFIX, autoescape=True),
            )
            .limit(1)
        )
        cache[key] = name or "历史参与者"
    return cache[key]


async def present_values(db, who, entity, values, cache=None):
    """Resolve only names referenced by already-authorized business rows/history."""
    cache = {} if cache is None else cache
    display = {}
    for relation in SPEC["relations"]:
        if relation["entity"] != entity or values.get(relation["field"]) is None:
            continue
        field, target = relation["field"], relation["target_entity"]
        identifier = values[field]
        if target == "$users":
            display[field] = await user_label(db, identifier, cache)
        else:
            key = (target, str(identifier))
            if key not in cache:
                try:
                    linked = await record(db, who, target, identifier, "read")
                    cache[key] = record_title(target, serialize(linked, target))
                except HTTPException as error:
                    if error.status_code not in {403, 404}:
                        raise
                    cache[key] = "无权查看关联记录"
            display[field] = cache[key]
    if values.get("created_by") is not None:
        display["created_by"] = await user_label(db, values["created_by"], cache)
    return {**values, "_display": display, "_title": record_title(entity, values)}


async def actor(db, auth):
    if not auth.user.id:
        fail(401)
    codes = list(
        (
            await db.scalars(
                select(RoleModel.code)
                .join(UserRolesModel, RoleModel.id == UserRolesModel.role_id)
                .where(
                    UserRolesModel.user_id == auth.user.id,
                    RoleModel.is_deleted.is_(False),
                    RoleModel.status == 0,
                    RoleModel.code.startswith(ROLE_PREFIX, autoescape=True),
                )
            )
        ).all()
    )
    declared = {r["name"] for r in SPEC["roles"]}
    roles = [code[len(ROLE_PREFIX) :] for code in codes if code[len(ROLE_PREFIX) :] in declared]
    if len(roles) != 1:
        fail(403, "Exactly one project business role is required")
    return {"id": str(auth.user.id), "role": roles[0]}


def grant(who, entity, action):
    try:
        return POLICY.grant(who["role"], entity, action)
    except PolicyError:
        fail()


def scope(who, entity, action):
    permission = grant(who, entity, action)
    model = MODELS[entity]
    if permission["scope"] == "all":
        return model.id > 0
    if permission["scope"] == "own":
        return model.created_id == identifier(who["id"])
    return getattr(model, POLICY.resource(entity)["assignee_field"]) == identifier(who["id"])


async def record(db, who, entity, row_id, action, lock=False):
    if entity not in MODELS:
        fail(404)
    model = MODELS[entity]
    query = select(model).where(model.id == identifier(row_id), scope(who, entity, action))
    if lock:
        query = query.with_for_update()
    row = await db.scalar(query)
    if row is None:
        fail(404, "Record unavailable")
    if lock and row.is_deleted:
        fail(409, "Archived records are immutable")
    return row


async def validate(db, who, entity, data, creation=False):
    if not isinstance(data, dict):
        fail(422)
    fields = {f["name"]: f for f in ENTITIES[entity]["fields"]}
    protected = POLICY.protected(entity)
    if set(data) - set(fields) or set(data) & protected:
        fail(422, "Unknown or server-controlled field")
    result = {}
    for name, spec in fields.items():
        if name in protected:
            continue
        if name not in data:
            if creation and spec["required"]:
                fail(422, "Required field missing: " + name)
            continue
        value = data[name]
        if value is None:
            if spec["required"]:
                fail(422, "Required field missing: " + name)
        elif spec["kind"] in {"text", "enum"}:
            if isinstance(value, str):
                value = value.strip()
            if (
                not isinstance(value, str)
                or len(value.strip()) > spec["max_length"]
                or len(value.strip()) < max(spec["min_length"], 1 if spec["required"] else 0)
            ):
                fail(422, "Invalid text length: " + name)
            if spec["kind"] == "enum" and value not in spec["choices"]:
                fail(422, "Invalid enum: " + name)
        elif spec["kind"] == "integer":
            if type(value) is not int or not -(2**63) <= value < 2**63:
                fail(422, "Expected integer: " + name)
        elif spec["kind"] == "boolean":
            if type(value) is not bool:
                fail(422, "Expected boolean: " + name)
        elif spec["kind"] == "datetime":
            value = instant(value)
        elif spec["kind"] == "date":
            try:
                value = date.fromisoformat(value)
            except ValueError, TypeError:
                fail(422, "Invalid date: " + name)
        result[name] = value
    for relation in SPEC["relations"]:
        field = relation["field"]
        if relation["entity"] != entity or field not in result or result[field] is None:
            continue
        value = identifier(result[field])
        if relation["target_entity"] == "$users":
            target = await db.scalar(
                select(UserModel).where(
                    UserModel.id == value,
                    UserModel.is_deleted.is_(False),
                    UserModel.status == 0,
                )
            )
            if target is None:
                fail(422, "Related user unavailable")
        else:
            target = await record(db, who, relation["target_entity"], value, "read")
            if target.is_deleted:
                fail(422, "Related record archived")
        result[field] = value
    return result


async def event(db, who, entity, row, name, data):
    audit = BusinessEvent(
        entity=entity,
        record_id=row.id,
        actor=identifier(who["id"]),
        event=name,
        payload=data,
    )
    db.add(audit)
    await db.flush()
    # Keep native audit actions stable while dispatching canonical contract events.
    notification_name = "note_added" if name == "add_note" else name
    recipients = set()
    for rule in SPEC["notifications"]:
        if rule["entity"] != entity or rule["event"] != notification_name:
            continue
        if notification_name == "transitioned" and rule["transition"] != data.get("transition"):
            continue
        recipient = (
            row.created_id
            if rule["recipient"] == "creator"
            else getattr(row, POLICY.resource(entity)["assignee_field"])
        )
        if recipient and identifier(recipient) not in recipients:
            recipients.add(identifier(recipient))
            db.add(
                BusinessEvent(
                    entity=entity,
                    record_id=row.id,
                    actor=identifier(who["id"]),
                    recipient=identifier(recipient),
                    event="notification",
                    payload={"event": notification_name},
                    source_key=f"{audit.id}:{recipient}",
                )
            )


async def create(db, who, entity, data):
    grant(who, entity, "create")
    values = await validate(db, who, entity, data, True)
    workflow = POLICY.workflow(entity)
    if workflow:
        values[workflow["status_field"]] = workflow["initial"]
    resource = POLICY.resource(entity)
    if resource.get("assignee_field"):
        values[resource["assignee_field"]] = None
    if hasattr(MODELS[entity], "status"):
        # Native generator omits ORM default for this status column.
        values["status"] = 0
    row = MODELS[entity](
        **values, created_id=identifier(who["id"]), updated_id=identifier(who["id"])
    )
    db.add(row)
    await db.flush()
    await event(db, who, entity, row, "created", {"after": serialize(row, entity)})
    result = serialize(row, entity)
    await db.commit()
    return result


async def mutate(db, who, entity, row_id, action, data):
    row = await record(db, who, entity, row_id, action, True)
    before = serialize(row, entity)
    event_name = action
    extra = {}
    if action == "update":
        for name, value in (await validate(db, who, entity, data)).items():
            setattr(row, name, value)
    elif action == "assign":
        if set(data) != {"assignee"}:
            fail(422)
        user_id = identifier(data["assignee"])
        target = await db.scalar(
            select(UserModel).where(
                UserModel.id == user_id,
                UserModel.is_deleted.is_(False),
                UserModel.status == 0,
            )
        )
        memberships = list(
            (
                await db.scalars(
                    select(RoleModel.code)
                    .join(UserRolesModel, RoleModel.id == UserRolesModel.role_id)
                    .where(
                        UserRolesModel.user_id == user_id,
                        RoleModel.is_deleted.is_(False),
                        RoleModel.status == 0,
                        RoleModel.code.startswith(ROLE_PREFIX, autoescape=True),
                    )
                )
            ).all()
        )
        if target is None or len(memberships) != 1:
            fail(422, "Assignee must be an active project user")
        membership = memberships[0]
        eligible = next(
            (
                p
                for p in SPEC["permissions"]
                if p["role"] == membership[len(ROLE_PREFIX) :] and p["entity"] == entity
            ),
            None,
        )
        if (
            not eligible
            or eligible["scope"] not in {"all", "assigned"}
            or "read" not in eligible["actions"]
            or not {"update", "transition"}.intersection(eligible["actions"])
        ):
            fail(422, "Assignee cannot handle this resource")
        setattr(row, POLICY.resource(entity)["assignee_field"], user_id)
        event_name = "assigned"
    elif action == "transition":
        if set(data) != {"transition"}:
            fail(422)
        workflow = POLICY.workflow(entity)
        try:
            transition = POLICY.transition(
                who["role"],
                entity,
                data["transition"],
                getattr(row, workflow["status_field"]),
            )
        except PolicyError:
            fail(409, "Transition unavailable")
        setattr(row, workflow["status_field"], transition["to_state"])
        if transition.get("set_timestamp"):
            setattr(row, transition["set_timestamp"], datetime.now(UTC))
        extra["transition"] = transition["name"]
        event_name = "transitioned"
    elif action == "archive":
        if data:
            fail(422)
        row.is_deleted, row.deleted_time = True, datetime.now(UTC)
        row.deleted_id = identifier(who["id"])
    elif action == "add_note":
        if not POLICY.resource(entity)["notes"]:
            fail(403, "Notes are disabled for this resource")
        if (
            set(data) != {"text"}
            or not isinstance(data["text"], str)
            or not 1 <= len(data["text"].strip()) <= 4000
        ):
            fail(422, "A note must contain 1–4000 characters")
        extra["text"] = data["text"].strip()
    else:
        fail(404)
    row.updated_id, row.updated_time = identifier(who["id"]), datetime.now(UTC)
    await db.flush()
    after = serialize(row, entity)
    await event(db, who, entity, row, event_name, {"before": before, "after": after, **extra})
    await db.commit()
    return after


async def rows(db, who, entity, action="read", query="", filters=None, archived=False):
    if entity not in MODELS:
        fail(404)
    model = MODELS[entity]
    statement = select(model).where(scope(who, entity, action), model.is_deleted.is_(archived))
    fields = {f["name"]: f for f in ENTITIES[entity]["fields"]}
    if query:
        searched = [
            getattr(model, name).icontains(query, autoescape=True)
            for name, f in fields.items()
            if f["searchable"]
        ]
        if not searched:
            fail(422, "Search is not available")
        statement = statement.where(or_(*searched))
    for name, value in (filters or {}).items():
        if name.endswith(("_from", "_to")):
            field, suffix = name.rsplit("_", 1)
            if field not in fields or not fields[field]["date_range"]:
                fail(422, "Unknown range filter")
            bound = instant(value) if fields[field]["kind"] == "datetime" else date_value(value)
            column = getattr(model, field)
            statement = statement.where(column >= bound if suffix == "from" else column <= bound)
        else:
            if name not in fields or not fields[name]["filterable"]:
                fail(422, "Unknown exact filter")
            column = getattr(model, name)
            kind = fields[name]["kind"]
            relation = any(r["entity"] == entity and r["field"] == name for r in SPEC["relations"])
            if relation:
                value = identifier(value)
            elif kind == "integer":
                try:
                    value = int(value)
                except ValueError, TypeError:
                    fail(422, "Invalid integer filter")
            elif kind == "boolean":
                if value not in (True, False, "true", "false"):
                    fail(422, "Invalid boolean filter")
                value = value is True or value == "true"
            elif kind == "datetime":
                value = instant(value)
            elif kind == "date":
                value = date_value(value)
            statement = statement.where(column == value)
    return list((await db.scalars(statement.order_by(model.id.desc()))).all())


def readable_entities(role):
    return {
        permission["entity"]
        for permission in SPEC["permissions"]
        if permission["role"] == role and "read" in permission["actions"]
    }


async def set_role(db, user_id, role):
    if role not in {r["name"] for r in SPEC["roles"]}:
        fail(422, "Unknown business role")
    user_id = identifier(user_id)
    target = await db.scalar(
        select(UserModel)
        .where(UserModel.id == user_id, UserModel.is_deleted.is_(False))
        .with_for_update()
    )
    if target is None:
        fail(404)
    native_role = await db.scalar(select(RoleModel).where(RoleModel.code == ROLE_PREFIX + role))
    if native_role is None:
        native_role = RoleModel(
            code=ROLE_PREFIX + role,
            name=next(r["label"] for r in SPEC["roles"] if r["name"] == role),
            data_scope=1,
        )
        db.add(native_role)
        await db.flush()
        # Only business menu tree, never native user/role administration permissions.
        menus = list(
            (await db.scalars(select(MenuModel).where(MenuModel.is_deleted.is_(False)))).all()
        )
        chosen = {
            m.id
            for m in menus
            if any(
                (m.component_path or "").lstrip("/") == "module_rnd/" + e + "/index"
                for e in readable_entities(role)
            )
        }
        by_id = {m.id: m for m in menus}
        for mid in list(chosen):
            parent = by_id[mid].parent_id
            while parent in by_id and parent not in chosen:
                chosen.add(parent)
                parent = by_id[parent].parent_id
        for mid in chosen:
            db.add(RoleMenusModel(role_id=native_role.id, menu_id=mid))
    owned = select(RoleModel.id).where(RoleModel.code.startswith(ROLE_PREFIX, autoescape=True))
    await db.execute(
        delete(UserRolesModel).where(
            UserRolesModel.user_id == user_id, UserRolesModel.role_id.in_(owned)
        )
    )
    db.add(UserRolesModel(user_id=user_id, role_id=native_role.id))
    await db.flush()
