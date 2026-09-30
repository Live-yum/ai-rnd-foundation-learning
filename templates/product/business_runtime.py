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
                        or not ({"update", "transition"} & set(permission["actions"]))
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
                and {"update", "transition"}
                & set(policy.permissions[row["role"], entity]["actions"])
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
            record(connection, actor, entity, identity, "read_history", archived=True)
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
            full = "read_audit" in policy.permissions.get((actor["role"], entity), {}).get(
                "actions", []
            )
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
