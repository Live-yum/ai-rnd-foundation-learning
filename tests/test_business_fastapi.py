"""Native business extension mounting and safety boundaries (no provider calls)."""

import ast
import importlib.util

import pytest
from sqlalchemy.dialects import mysql, postgresql, sqlite

from workbench.business_fastapi import extension_schema
from workbench.settings import ROOT


@pytest.mark.parametrize("dialect", [sqlite.dialect(), postgresql.dialect(), mysql.dialect()])
def test_schema_is_additive_namespaced_and_restricts_user_deletion(dialect):
    sql = extension_schema("wb_123456789abc", dialect)
    assert "CREATE TABLE wb_123456789abc_events" in sql
    assert "ON DELETE RESTRICT" in sql
    assert "source_key" in sql and "UNIQUE" in sql
    assert not any(word in sql.upper() for word in ("DROP TABLE", "DELETE FROM", "ALTER TABLE"))


def test_schema_rejects_identifier_injection():
    with pytest.raises(ValueError):
        extension_schema("events;DROP TABLE sys_user", sqlite.dialect())


def test_native_generated_crud_guard_blocks_every_caller():
    import asyncio

    from fastapi import HTTPException

    spec = importlib.util.spec_from_file_location(
        "business_guard", ROOT / "templates/business/fastapiadmin/guard.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(HTTPException) as caught:
        asyncio.run(module.block_generated_crud())
    assert caught.value.status_code == 403


def test_runtime_retains_native_auth_orm_and_no_global_admin_grant():
    folder = ROOT / "templates/business/fastapiadmin"
    controller = (folder / "controller.py").read_text(encoding="utf-8")
    runtime = (folder / "runtime.py").read_text(encoding="utf-8")
    for file in folder.glob("*.py"):
        ast.parse(file.read_text(encoding="utf-8"))
    assert "get_current_user" in controller and "db_getter" in controller
    assert "UserRolesModel" in runtime and "RoleMenusModel" in runtime
    assert "app.plugin.module_rnd." in runtime
    assert "is_superuser =" not in runtime and "is_superuser=True" not in runtime
    assert "with_for_update()" in runtime
    assert "Use the business workflow API" in (folder / "guard.py").read_text(encoding="utf-8")


def test_ui_uses_native_components_and_session_request_layer():
    page = (ROOT / "templates/business/fastapiadmin/index.vue").read_text(encoding="utf-8")
    for marker in (
        "FaSearchBar",
        "FaDialog",
        "ElTable",
        "ElTimeline",
        "ElCard",
        "from '@utils'",
    ):
        assert marker in page
    assert "localStorage" not in page and "fetch(" not in page


def fixture_plan():
    return {
        "title": "Native case",
        "data_scope": "shared",
        "acceptance": ["Business"],
        "entities": [
            {
                "name": "cases",
                "description": "Cases",
                "fields": [{"name": "title", "kind": "text"}],
            }
        ],
        "business": {
            "roles": [
                {"name": "manager", "label": "Manager"},
                {"name": "employee", "label": "Employee"},
            ],
            "registration": {"enabled": True, "default_role": "employee"},
            "bootstrap_role": "manager",
            "role_admin_roles": ["manager"],
            "resources": [{"entity": "cases"}],
            "permissions": [
                {
                    "role": "manager",
                    "entity": "cases",
                    "actions": ["create", "read"],
                    "scope": "all",
                }
            ],
        },
    }


def test_extension_preserves_actual_generated_model_and_backs_up_originals(tmp_path, monkeypatch):
    import shutil

    from workbench import business_fastapi as adapter

    root = tmp_path / "source"
    shutil.copytree(
        ROOT / "templates/business/fastapiadmin",
        root / "templates/business/fastapiadmin",
    )
    policy = root / "templates/business/common/policy.py"
    policy.parent.mkdir(parents=True)
    policy.write_text("# portable policy fixture", encoding="utf-8")
    monkeypatch.setattr(adapter, "ROOT", root)
    backend, frontend, reports = (
        tmp_path / "backend",
        tmp_path / "frontend",
        tmp_path / "reports",
    )
    registration = backend / "app/modules/system/user/controller.py"
    registration.parent.mkdir(parents=True)
    registration.write_text(
        "async def register_controller():\n    register_result: UserOutSchema = await UserService(auth, db).register(data=data)\n"
        "async def create_user_controller():\n    result_dict: UserOutSchema = await UserService(auth, db).create(data=data)\n"
        "    return SuccessResponse(data=result_dict)\n",
        encoding="utf-8",
    )
    folder = backend / "app/plugin/module_rnd/cases"
    folder.mkdir(parents=True)
    controller = (
        'from fastapi import APIRouter, Depends\nCasesRouter = APIRouter(prefix="/cases")\n'
    )
    (folder / "controller.py").write_text(controller, encoding="utf-8")
    (folder / "model.py").write_text("# original generated model\n", encoding="utf-8")
    page = frontend / "src/views/module_rnd/cases/index.vue"
    page.parent.mkdir(parents=True)
    page.write_text("<template>Original</template>", encoding="utf-8")
    shell = frontend / "src/layouts/index.vue"
    shell.parent.mkdir()
    shell.write_text("original shell", encoding="utf-8")
    result = adapter.extend_business(
        fixture_plan(),
        backend,
        frontend,
        [{"entity": "cases", "table": "wb_cases"}],
        reports,
        database_url="sqlite://",
    )
    assert result["entities"][0]["generated_crud_guarded"]
    assert (folder / "model.py").read_text(encoding="utf-8") == "# original generated model\n"
    assert (reports / "business-originals/cases/controller.py").read_text(
        encoding="utf-8"
    ) == controller
    assert "dependencies=[Depends(block_generated_crud)]" in (folder / "controller.py").read_text(
        encoding="utf-8"
    )
    assert shell.read_text(encoding="utf-8") == "original shell"
    patched_controller = registration.read_text(encoding="utf-8")
    assert patched_controller.index("await db.commit()") < patched_controller.index(
        "return SuccessResponse(data=result_dict)"
    )
    # Execute the mounted create handler, rather than merely matching its text.
    # Native CRUD flushes and returns before the request dependency commits.
    import asyncio

    calls = []

    class Service:
        def __init__(self, auth, db):
            pass

        async def create(self, data):
            calls.append("native_create_flushed")
            return {"id": 6}

    class Session:
        async def commit(self):
            calls.append("committed")

    def response(**kwargs):
        assert calls == ["native_create_flushed", "committed"]
        calls.append("success_response")
        return kwargs["data"]

    create_function = next(
        node
        for node in ast.parse(patched_controller).body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "create_user_controller"
    )
    scope = {
        "UserService": Service,
        "auth": None,
        "db": Session(),
        "data": {},
        "SuccessResponse": response,
    }
    exec(
        compile(ast.Module(body=[create_function], type_ignores=[]), "mounted-controller", "exec"),
        scope,
    )
    assert asyncio.run(scope["create_user_controller"]()) == {"id": 6}
    assert calls[-1] == "success_response"
    assert (reports / "business-extension-schema.sql").is_file()
    with pytest.raises(ValueError, match="already exists"):
        adapter.extend_business(
            fixture_plan(),
            backend,
            frontend,
            [{"entity": "cases", "table": "wb_cases"}],
            reports,
        )


def test_bootstrap_and_role_mutation_serialization_are_explicit():
    source = (ROOT / "templates/business/fastapiadmin/controller.py").read_text(encoding="utf-8")
    assert 'source_key="bootstrap"' in source
    assert 'source_key == "bootstrap"' in source
    assert "except IntegrityError" in source
    role = source[source.index("async def role(") : source.index('@BusinessRouter.get("/users")')]
    assert role.index("with_for_update()") < role.index("await rt.actor")


def test_generated_native_status_is_initialized_without_exposing_it_to_input():
    runtime = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    assert 'values["status"] = 0' in runtime
    assert "set(data) - set(fields)" in runtime


def generated_relation_model():
    return """from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class CasesModel(ModelMixin):
    __tablename__: str = 'wb_cases'
    # 原生生成字段；保留备注与所有其他字段
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='客户')
    assignee_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='负责人')
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='完成日期')
    title: Mapped[str] = mapped_column(String(250), nullable=False, comment='标题')
"""


def relation_contract():
    from types import SimpleNamespace

    entity = SimpleNamespace(
        name="cases", fields=[SimpleNamespace(name="resolved_at", kind="datetime")]
    )
    relations = [
        SimpleNamespace(entity="cases", field="customer_id", target_entity="customers"),
        SimpleNamespace(entity="cases", field="assignee_id", target_entity="$users"),
    ]
    targets = {"cases": {"table": "wb_cases"}, "customers": {"table": "wb_customers"}}
    return entity, relations, targets


def test_actual_generator_shape_preserves_native_fk_and_timezone_on_fresh_metadata():
    from sqlalchemy import Column, Integer, Table
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    from workbench.business_fastapi import extend_model

    class NativeBase(DeclarativeBase):
        pass

    class ModelMixin(NativeBase):
        __abstract__ = True
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

    Table("sys_user", NativeBase.metadata, Column("id", Integer, primary_key=True))
    Table("wb_customers", NativeBase.metadata, Column("id", Integer, primary_key=True))
    source = generated_relation_model()
    transformed = extend_model(source, *relation_contract())
    scope = {"ModelMixin": ModelMixin}
    exec(compile(transformed, "generated-model.py", "exec"), scope)
    table = scope["CasesModel"].__table__
    assert table.c.resolved_at.type.timezone is True
    assert {(fk.parent.name, fk.target_fullname, fk.ondelete) for fk in table.foreign_keys} == {
        ("customer_id", "wb_customers.id", "RESTRICT"),
        ("assignee_id", "sys_user.id", "RESTRICT"),
    }
    assert "# 原生生成字段；保留备注与所有其他字段" in transformed
    assert (
        "title: Mapped[str] = mapped_column(String(250), nullable=False, comment='标题')"
        in transformed
    )
    assert "FOREIGN KEY" in str(
        __import__("sqlalchemy").schema.CreateTable(table).compile(dialect=postgresql.dialect())
    )


@pytest.mark.parametrize("change", ["missing", "wrong_table", "wrong_type", "existing_fk"])
def test_model_extension_rejects_unrecognized_native_shapes(change):
    from workbench.business_fastapi import extend_model

    source = generated_relation_model()
    if change == "missing":
        source = source.replace("customer_id:", "other_id:")
    elif change == "wrong_table":
        source = source.replace("'wb_cases'", "'unrelated'")
    elif change == "wrong_type":
        source = source.replace("mapped_column(Integer,", "mapped_column(String(40),", 1)
    else:
        source = source.replace(
            "mapped_column(Integer,", "mapped_column(Integer, ForeignKey('other.id'),", 1
        )
    with pytest.raises(ValueError):
        extend_model(source, *relation_contract())


def test_namespaced_roles_pass_the_pinned_native_output_validator():
    import re
    import zipfile

    runtime = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    prefix = next(
        node.value
        for node in ast.parse(runtime).body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "ROLE_PREFIX" for t in node.targets)
    )
    namespace = "wb_6e02530c6239"
    actual = eval(
        compile(ast.Expression(prefix), "runtime-prefix", "eval"),
        {"CONFIG": {"namespace": namespace}},
    )
    with zipfile.ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as archive:
        source = archive.read("backend/app/core/validator.py").decode("utf-8")
    validator = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "validate_required_code"
    )
    scope = {"re": re}
    exec(
        compile(ast.Module(body=[validator], type_ignores=[]), "pinned-native-validator", "exec"),
        scope,
    )
    for role in ("manager", "service", "employee", "a" * 40):
        code = actual + role
        assert scope["validate_required_code"](code) == code
    with pytest.raises(ValueError):
        scope["validate_required_code"](namespace + ":manager")


def test_native_business_menus_follow_read_grants_without_admin_fallback():
    import json

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    source = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    function = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "readable_entities"
    )
    scope = {"SPEC": plan["business"]}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "native-role-menus", "exec"), scope)
    readable = scope["readable_entities"]
    assert readable("manager") == {"customers", "requests", "tasks"}
    assert readable("service") == {"customers", "requests", "tasks"}
    assert readable("employee") == {"customers", "requests"}
    assert readable("unknown") == set()
    plan["business"]["permissions"] = []
    assert readable("manager") == set()
    assert "for e in readable_entities(role)" in source
    assert "while parent in by_id and parent not in chosen" in source


def test_presentation_resolves_only_authorized_references_and_preserves_raw_values():
    import asyncio
    from copy import deepcopy

    from fastapi import HTTPException

    source = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    selected = [
        node
        for node in ast.parse(source).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in {"record_title", "present_values"}
    ]
    called = []

    async def record(db, who, entity, identifier, action):
        called.append((entity, str(identifier), action))
        if str(identifier) == "99":
            raise HTTPException(404)
        return {"display_name": "Authorized partner"}

    async def user_label(db, identifier, cache):
        called.append(("$users", str(identifier), "name"))
        return "Business member"

    scope = {
        "SPEC": {
            "relations": [
                {"entity": "cases", "field": "partner", "target_entity": "partners"},
                {"entity": "cases", "field": "assignee", "target_entity": "$users"},
            ]
        },
        "ENTITIES": {
            "cases": {
                "description": "事项",
                "fields": [
                    {"name": "subject", "kind": "text"},
                    {"name": "partner", "kind": "text"},
                ],
            },
            "partners": {
                "description": "合作方",
                "fields": [{"name": "display_name", "kind": "text"}],
            },
        },
        "record": record,
        "serialize": lambda row, entity: row,
        "user_label": user_label,
        "HTTPException": HTTPException,
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), "native-display", "exec"), scope)
    values = {"subject": "Synthetic subject", "partner": "7", "assignee": "6", "created_by": "2"}
    original = deepcopy(values)
    visible = asyncio.run(scope["present_values"](None, {"id": "2"}, "cases", values))
    assert values == original
    assert all(visible[key] == value for key, value in original.items())
    assert visible["_display"] == {
        "partner": "Authorized partner",
        "assignee": "Business member",
        "created_by": "Business member",
    }
    assert visible["_title"] == "Synthetic subject"
    assert called == [("partners", "7", "read"), ("$users", "6", "name"), ("$users", "2", "name")]
    denied = asyncio.run(
        scope["present_values"](None, {"id": "2"}, "cases", {**values, "partner": "99"})
    )
    assert denied["_display"]["partner"] == "无权查看关联记录"
    assert "Authorized partner" not in denied["_display"].values()


def test_native_display_uses_contract_labels_and_keeps_parseable_original_components():
    from workbench.symbols import parse_file

    page = ROOT / "templates/business/fastapiadmin/index.vue"
    source = page.read_text(encoding="utf-8")
    assert "field.label || field.name" in source
    assert "field.choice_labels?.[choice] || choice" in source
    assert "transition.label || transition.name" in source
    assert "item.actor_name" in source and "row._display" in source
    assert ':min-width="columnWidth(field)"' in source
    assert "white-space: nowrap" in source and " + ' UTC'" in source
    assert parse_file(page)["parse_error"] is False


def test_assignee_selection_uses_unique_authorized_username_after_restart():
    controller = (ROOT / "templates/business/fastapiadmin/controller.py").read_text(
        encoding="utf-8"
    )
    page = (ROOT / "templates/business/fastapiadmin/index.vue").read_text(encoding="utf-8")
    browser = (ROOT / "scripts/business_fastapi_browser.cjs").read_text(encoding="utf-8")
    assert "UserModel.name, UserModel.username, RoleModel.code" in controller
    assert '"username": username' in controller
    assert "${user.name} · ${user.username}" in page
    assert "assign(page, 'requests', request, scenario.actors.service.username)" in browser
    assert "assign(page, 'tasks', task, scenario.actors.service.username)" in browser
