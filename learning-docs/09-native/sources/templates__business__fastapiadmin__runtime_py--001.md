# templates/business/fastapiadmin/runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：FastapiAdmin合同事务运行时。** 读取真实原生身份，实施角色/行范围、关联锁、命名动作、事件与通知；指标使用当前可见范围，关键写入共同提交或回滚。

**对应关系：** controller → policy/生成模型/扩展模型 → PostgreSQL → 原生响应。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fail`（L29–L30）：接收`code`、`reason`。 控制顺序：L30抛异常，停止当前正常路径。 调用`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `identifier`（L33–L36）：接收`value`。 控制顺序：L34按`isinstance(value, bool) or not str(value).isdigit() or int(value) < 1`分支。 调用`isinstance`、`str(value).isdigit`、`str`、`int`、`fail`。 返回路径：L36的`int(value)`。
- `date_value`（L39–L46）：接收`value`。 控制顺序：L42按`parsed.isoformat() != value`分支。 调用`date.fromisoformat`、`parsed.isoformat`、`fail`。 返回路径：L44的`parsed`。
- `instant`（L49–L56）：接收`value`。 控制顺序：L52按`result.tzinfo is None`分支。 调用`datetime.fromisoformat`、`str(value).replace`、`str`、`fail`、`result.astimezone`。 返回路径：L54的`result.astimezone(UTC)`。
- `serialize`（L59–L78）：接收`row`、`entity`。 控制顺序：L61遍历`SPEC["relations"]`；L62按`relation["entity"] == entity and result.get(relation["field"]) is not None`分支。 调用`getattr`、`result.get`、`str`、`result.update`、`isinstance`、`(v.replace(tzinfo=UTC) if v.tzinfo is None else v.astimezone(UTC)…`、`v.replace`、`v.astimezone`、`v.isoformat`等。 返回路径：L71的`{ k: (v.replace(tzinfo=UTC) if v.tzinfo is None else v.astimezone(UTC)).isoformat() if isi…`。
- `record_title`（L81–L88）：接收`entity`、`values`。 控制顺序：L83遍历`ENTITIES[entity]["fields"]`；L84按`field["kind"] == "text" and field["name"] not in references`分支；L86按`value`分支。 调用`values.get`、`str`、`ENTITIES[entity].get`。 返回路径：L87的`str(value)`；L88的`ENTITIES[entity].get("description") or "业务记录"`。
- `user_label`（L91–L107）：接收`db`、`user_id`、`cache`。 控制顺序：L93按`key not in cache`分支。 调用`str`、`db.scalar`、`select(UserModel.name) .join(UserRolesModel, UserModel.id == User…`、`select(UserModel.name) .join`、`select`、`identifier`、`UserModel.is_deleted.is_`、`RoleModel.is_deleted.is_`、`RoleModel.code.startswith`。 返回路径：L107的`cache[key]`。
- `present_values`（L110–L134）：接收`db`、`who`、`entity`、`values`、`cache`。 源码说明：Resolve only names referenced by already-authorized business rows/history.。 控制顺序：L114遍历`SPEC["relations"]`；L115按`relation["entity"] != entity or values.get(relation["field"]) is None`分支；L119按`target == "$users"`分支；L123按`key not in cache`分支；L128按`error.status_code not in {403, 404}`分支；L129抛异常，停止当前正常路径；L132按`values.get("created_by") is not None`分支。 调用`values.get`、`user_label`、`str`、`record`、`record_title`、`serialize`。 返回路径：L134的`{**values, "_display": display, "_title": record_title(entity, values)}`。
- `actor`（L137–L158）：接收`db`、`auth`。 控制顺序：L138按`not auth.user.id`分支；L156按`len(roles) != 1`分支。 调用`fail`、`list`、`( await db.scalars( select(RoleModel.code) .join(UserRolesModel, …`、`db.scalars`、`select(RoleModel.code) .join(UserRolesModel, RoleModel.id == User…`、`select(RoleModel.code) .join`、`select`、`RoleModel.is_deleted.is_`、`RoleModel.code.startswith`等。 返回路径：L158的`{"id": str(auth.user.id), "role": roles[0]}`。
- `grant`（L161–L165）：接收`who`、`entity`、`action`。 调用`POLICY.grant`、`fail`。 返回路径：L163的`POLICY.grant(who["role"], entity, action)`。
- `scope`（L168–L175）：接收`who`、`entity`、`action`。 控制顺序：L171按`permission["scope"] == "all"`分支；L173按`permission["scope"] == "own"`分支。 调用`grant`、`identifier`、`getattr`、`POLICY.resource`。 返回路径：L172的`model.id > 0`；L174的`model.created_id == identifier(who["id"])`；L175的`getattr(model, POLICY.resource(entity)["assignee_field"]) == identifier(who["id"])`。
- `record`（L178–L190）：接收`db`、`who`、`entity`、`row_id`、`action`、`lock`。 控制顺序：L179按`entity not in MODELS`分支；L183按`lock`分支；L186按`row is None`分支；L188按`lock and row.is_deleted`分支。 调用`fail`、`select(model).where`、`select`、`identifier`、`scope`、`query.with_for_update`、`db.scalar`。 返回路径：L190的`row`。
- `validate`（L193–L261）：接收`db`、`who`、`entity`、`data`、`creation`。 控制顺序：L194按`not isinstance(data, dict)`分支；L198按`set(data) - set(fields) or set(data) & protected`分支；L201遍历`fields.items()`；L202按`name in protected`分支；L204按`name not in data`分支；L205按`creation and spec["required"]`分支；L209按`value is None`分支；L210按`spec["required"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`fail`、`POLICY.protected`、`set`、`fields.items`、`value.strip`、`len`、`max`、`type`等。 返回路径：L261的`result`。
- `event`（L264–L299）：接收`db`、`who`、`entity`、`row`、`name`、`data`。 控制顺序：L277遍历`SPEC["notifications"]`；L278按`rule["entity"] != entity or rule["event"] != notification_name`分支；L280按`notification_name == "transitioned" and rule["transition"] != data.get("transition")`分支；L287按`recipient and identifier(recipient) not in recipients`分支。 调用`BusinessEvent`、`identifier`、`db.add`、`db.flush`、`set`、`data.get`、`getattr`、`POLICY.resource`、`recipients.add`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `create`（L302–L322）：接收`db`、`who`、`entity`、`data`。 控制顺序：L306按`workflow`分支；L309按`resource.get("assignee_field")`分支；L311按`hasattr(MODELS[entity], "status")`分支。 调用`grant`、`validate`、`POLICY.workflow`、`POLICY.resource`、`resource.get`、`hasattr`、`MODELS[entity]`、`identifier`、`db.add`等。 返回路径：L322的`result`。
- `mutate`（L325–L417）：接收`db`、`who`、`entity`、`row_id`、`action`、`data`。 控制顺序：L330按`action == "update"`分支；L331遍历`(await validate(db, who, entity, data)).items()`；L333按`action == "assign"`分支；L334按`set(data) != {"assignee"}`分支；L358按`target is None or len(memberships) != 1`分支；L369按`not eligible or eligible["scope"] not in {"all", "assigned"} or "read" not in eligibl…`分支；L377按`action == "transition"`分支；L378按`set(data) != {"transition"}`分支。后续分支沿下方源码相同行号继续阅读。 调用`record`、`serialize`、`(await validate(db, who, entity, data)).items`、`validate`、`setattr`、`set`、`fail`、`identifier`、`db.scalar`等。 返回路径：L417的`after`。
- `rows`（L420–L465）：接收`db`、`who`、`entity`、`action`、`query`、`filters`、`archived`。 控制顺序：L421按`entity not in MODELS`分支；L426按`query`分支；L432按`not searched`分支；L435遍历`(filters or {}).items()`；L436按`name.endswith(("_from", "_to"))`分支；L438按`field not in fields or not fields[field]["date_range"]`分支；L444按`name not in fields or not fields[name]["filterable"]`分支；L449按`relation`分支。后续分支沿下方源码相同行号继续阅读。 调用`fail`、`select(model).where`、`select`、`scope`、`model.is_deleted.is_`、`getattr(model, name).icontains`、`getattr`、`fields.items`、`statement.where`等。 返回路径：L465的`list((await db.scalars(statement.order_by(model.id.desc()))).all())`。
- `readable_entities`（L468–L473）：接收`role`。 返回路径：L469的`{ permission["entity"] for permission in SPEC["permissions"] if permission["role"] == role…`。
- `set_role`（L476–L523）：接收`db`、`user_id`、`role`。 控制顺序：L477按`role not in {r["name"] for r in SPEC["roles"]}`分支；L485按`target is None`分支；L488按`native_role is None`分支；L509遍历`list(chosen)`；L511在`parent in by_id and parent not in chosen`成立时循环；L514遍历`chosen`。 调用`fail`、`identifier`、`db.scalar`、`select(UserModel) .where(UserModel.id == user_id, UserModel.is_de…`、`select(UserModel) .where`、`select`、`UserModel.is_deleted.is_`、`select(RoleModel).where`、`RoleModel`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/business/fastapiadmin/runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L523。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19648`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/fastapiadmin/runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1f4bc4cbb4ceeb90a2d0c75615bf157c660618b2a7ecdadb371db5ebbab49f9e"} -->
````python
# templates/business/fastapiadmin/runtime.py
"""Transactional native ORM business services; all authorization is server-side."""

import importlib
from datetime import UTC, date, datetime

from app.modules.system.menu.model import MenuModel
from app.modules.system.role.model import RoleMenusModel, RoleModel
from app.modules.system.user.model import UserModel, UserRolesModel
from fastapi import HTTPException
from sqlalchemy import delete, or_, select

from .model import CONFIG, BusinessEvent
from .policy import Policy, PolicyError, validate_scalar_constraints

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
            if type(value) is not int or not -(2**31) <= value < 2**31:
                fail(422, "Expected integer: " + name)
            try:
                validate_scalar_constraints("integer", spec, value)
            except PolicyError as error:
                fail(422, str(error))
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
````
