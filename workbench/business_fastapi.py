"""Mount business behavior on actual FastapiAdmin-generated models and native UI."""

import ast
import shutil
from pathlib import Path

from workbench.domain import Plan, digest
from workbench.filesystem import atomic_text, sha, write_json
from workbench.settings import ROOT


def extend_business(plan, backend, frontend, targets, reports, **context):
    plan = Plan.model_validate(plan)
    if plan.business is None:
        return None
    plan.business.validate_plan(plan)
    backend, frontend, reports = map(Path, (backend, frontend, reports))
    source = ROOT / "templates/business/fastapiadmin"
    plugin = backend / "app/plugin/module_business"
    if plugin.exists():
        raise ValueError("Business extension already exists; never overwrite runtime data/source")
    mapped = {target["entity"]: target for target in targets}
    if set(mapped) != {entity.name for entity in plan.entities}:
        raise ValueError("Business extension requires every actual native generator target")
    originals = reports / "business-originals"
    originals.mkdir(parents=True, exist_ok=True)
    staged = []
    for entity in plan.entities:
        controller = backend / f"app/plugin/module_rnd/{entity.name}/controller.py"
        model = controller.with_name("model.py")
        page = frontend / f"src/views/module_rnd/{entity.name}/index.vue"
        if not controller.is_file() or not model.is_file() or not page.is_file():
            raise ValueError("Actual generated controller/model/native page missing")
        tree = ast.parse(controller.read_text(encoding="utf-8"))
        routers = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "APIRouter"
        ]
        if len(routers) != 1 or any(k.arg == "dependencies" for k in routers[0].keywords):
            raise ValueError(
                "Unexpected generated router shape; cannot guarantee bypass protection"
            )
        body = controller.read_text(encoding="utf-8")
        body = body.replace(
            "APIRouter(", "APIRouter(dependencies=[Depends(block_generated_crud)], ", 1
        )
        body = "from app.plugin.module_business.guard import block_generated_crud\n" + body
        ast.parse(body)
        model_body = extend_model(
            model.read_text(encoding="utf-8"), entity, plan.business.relations, mapped
        )
        staged.append((entity, controller, model, page, body, model_body))
    policy_source = ROOT / "templates/business/common/policy.py"
    if not policy_source.is_file():
        raise ValueError("Portable business policy is missing")
    registration = backend / "app/modules/system/user/controller.py"
    registration_body = registration.read_text(encoding="utf-8")
    original_registration = registration_body
    anchor = "    register_result: UserOutSchema = await UserService(auth, db).register(data=data)"
    if registration_body.count(anchor) != 1:
        raise ValueError(
            "Unexpected native registration controller; cannot safely attach membership"
        )
    registration_body = registration_body.replace(
        anchor,
        "    await before_registration(db)\n"
        + anchor
        + "\n    await registration_completed(db, register_result.id)",
    )
    # The pinned native service only flushes. Its request-scoped dependency commits
    # after response/background logging, so an immediate role update can observe
    # a successful create whose user row is still uncommitted. Publish creation
    # atomically before returning the native success response.
    create_anchor = "    result_dict: UserOutSchema = await UserService(auth, db).create(data=data)"
    if registration_body.count(create_anchor) != 1:
        raise ValueError(
            "Unexpected native user creation controller; cannot ensure committed users"
        )
    registration_body = registration_body.replace(
        create_anchor, create_anchor + "\n    await db.commit()", 1
    )
    registration_body = (
        "from app.plugin.module_business.registration import before_registration, registration_completed\n"
        + registration_body
    )
    ast.parse(registration_body)
    plugin.mkdir(parents=True)
    for name in (
        "__init__.py",
        "controller.py",
        "model.py",
        "runtime.py",
        "guard.py",
        "registration.py",
    ):
        shutil.copyfile(source / name, plugin / name)
    shutil.copyfile(ROOT / "templates/business/common/policy.py", plugin / "policy.py")
    configuration = {
        "plan": plan.model_dump(mode="json"),
        "targets": mapped,
        "namespace": "wb_" + digest([target["table"] for target in targets])[:12],
    }
    write_json(plugin / "business.json", configuration)
    atomic_text(originals / "native-user-controller.py", original_registration)
    atomic_text(registration, registration_body)
    receipts = []
    for entity, controller, model, page, body, model_body in staged:
        backup = originals / entity.name
        backup.mkdir()
        for file in (controller, model, page):
            shutil.copyfile(file, backup / file.name)
        atomic_text(controller, body)
        atomic_text(model, model_body)
        atomic_text(page, (source / "index.vue").read_text(encoding="utf-8"))
        receipts.append(
            {
                "entity": entity.name,
                "native_model_sha256": sha(model),
                "original_native_model_sha256": sha(backup / "model.py"),
                "original_controller_sha256": sha(backup / "controller.py"),
                "generated_crud_guarded": True,
                "native_ui_extended": True,
            }
        )
    database_url = context.get("database_url")
    if database_url:
        from sqlalchemy import create_engine

        engine = create_engine(database_url)
        try:
            atomic_text(
                reports / "business-extension-schema.sql",
                extension_schema(configuration["namespace"], engine.dialect),
            )
        finally:
            engine.dispose()
    result = {
        "adapter": "fastapiadmin",
        "native_auth": True,
        "native_registration_extended": True,
        "native_orm": True,
        "namespace": configuration["namespace"],
        "entities": receipts,
        "schema_migration_required": True,
        "bootstrap": "/business/bootstrap",
    }
    write_json(reports / "business-extension.json", result)
    return result


def extension_schema(namespace, dialect):
    """Additive DDL only, applied by the caller's explicit migration step."""
    import re

    from sqlalchemy import (
        JSON,
        Column,
        DateTime,
        ForeignKey,
        Integer,
        MetaData,
        String,
        Table,
    )
    from sqlalchemy.schema import CreateIndex, CreateTable

    if not re.fullmatch(r"wb_[0-9a-f]{12}", namespace):
        raise ValueError("Invalid business namespace")
    metadata = MetaData()
    Table("sys_user", metadata, Column("id", Integer, primary_key=True))
    table = Table(
        namespace + "_events",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("entity", String(40), nullable=False, index=True),
        Column("record_id", Integer, nullable=False, index=True),
        Column(
            "actor",
            Integer,
            ForeignKey("sys_user.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        Column(
            "recipient",
            Integer,
            ForeignKey("sys_user.id", ondelete="RESTRICT"),
            index=True,
        ),
        Column("event", String(40), nullable=False),
        Column("payload", JSON, nullable=False),
        Column("source_key", String(200), unique=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("read_at", DateTime(timezone=True)),
    )
    return (
        str(CreateTable(table).compile(dialect=dialect))
        + ";\n"
        + "\n".join(
            str(CreateIndex(index).compile(dialect=dialect)) + ";"
            for index in sorted(table.indexes, key=lambda i: i.name)
        )
    )


def extend_model(source, entity, relations, targets):
    """Preserve generator output, adding only approved FK and timezone metadata.

    Upstream codegen introspects integer relation columns but drops foreign keys,
    and emits timezone-naive DateTime. Both must match the approved physical DDL
    before native metadata can build an independent fresh database.
    """
    tree = ast.parse(source)
    relations = {r.field: r for r in relations if r.entity == entity.name}
    datetimes = {f.name for f in entity.fields if f.kind == "datetime"}
    required = set(relations) | datetimes
    if not required:
        return source
    models = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(isinstance(base, ast.Name) and base.id == "ModelMixin" for base in node.bases)
    ]
    if len(models) != 1:
        raise ValueError("Unexpected generated ORM class shape")
    model = models[0]
    table = next(
        (
            node.value.value
            for node in model.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__tablename__"
            and isinstance(node.value, ast.Constant)
        ),
        None,
    )
    if table != targets[entity.name]["table"]:
        raise ValueError("Generated ORM table does not match native target")
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode("utf-8")))
    encoded = source.encode("utf-8")
    edits, found = [], set()
    for node in model.body:
        if (
            not isinstance(node, ast.AnnAssign)
            or not isinstance(node.target, ast.Name)
            or node.target.id not in required
        ):
            continue
        name, call = node.target.id, node.value
        if (
            name in found
            or not isinstance(call, ast.Call)
            or not isinstance(call.func, ast.Name)
            or call.func.id != "mapped_column"
            or not call.args
        ):
            raise ValueError("Unexpected generated ORM column shape")
        found.add(name)
        if name in relations:
            relation = relations[name]
            target = (
                "sys_user"
                if relation.target_entity == "$users"
                else targets[relation.target_entity]["table"]
            )
            first = call.args[0]
            if not (isinstance(first, ast.Name) and first.id == "Integer"):
                raise ValueError("Generated relation must retain native integer storage")
            if len(call.args) != 1:
                raise ValueError("Unexpected preexisting generated relation constraint")
            call.args.append(
                ast.Call(
                    func=ast.Name(id="ForeignKey", ctx=ast.Load()),
                    args=[ast.Constant(value=target + ".id")],
                    keywords=[ast.keyword(arg="ondelete", value=ast.Constant(value="RESTRICT"))],
                )
            )
        if name in datetimes:
            first = call.args[0]
            if not (isinstance(first, ast.Name) and first.id == "DateTime"):
                raise ValueError("Unexpected generated datetime storage")
            call.args[0] = ast.Call(
                func=ast.Name(id="DateTime", ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg="timezone", value=ast.Constant(value=True))],
            )
        replacement = ast.unparse(call).encode("utf-8")
        edits.append(
            (
                offsets[node.value.lineno - 1] + node.value.col_offset,
                offsets[node.value.end_lineno - 1] + node.value.end_col_offset,
                replacement,
            )
        )
    if found != required:
        raise ValueError("Generated ORM omitted approved business metadata")
    for start, end, replacement in sorted(edits, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    result = ("from sqlalchemy import ForeignKey\n" if relations else "") + encoded.decode("utf-8")
    ast.parse(result)
    return result
