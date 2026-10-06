# tests/test_business_fastapi.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_fastapi`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_schema_is_additive_namespaced_and_restricts_user_deletion`（L14–L19）：接收`dialect`。 控制顺序：L16断言`"CREATE TABLE wb_123456789abc_events" in sql`；L17断言`"ON DELETE RESTRICT" in sql`；L18断言`"source_key" in sql and "UNIQUE" in sql`；L19断言`not any(word in sql.upper() for word in ("DROP TABLE", "DELETE FROM", "ALTER TABLE"))`。 调用`extension_schema`、`any`、`sql.upper`、`pytest.mark.parametrize`、`sqlite.dialect`、`postgresql.dialect`、`mysql.dialect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_rejects_identifier_injection`（L22–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`extension_schema`、`sqlite.dialect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_generated_crud_guard_blocks_every_caller`（L27–L39）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L39断言`caught.value.status_code == 403`。 调用`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`pytest.raises`、`asyncio.run`、`module.block_generated_crud`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_retains_native_auth_orm_and_no_global_admin_grant`（L42–L53）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L46遍历`folder.glob("*.py")`；L48断言`"get_current_user" in controller and "db_getter" in controller`；L49断言`"UserRolesModel" in runtime and "RoleMenusModel" in runtime`；L50断言`"app.plugin.module_rnd." in runtime`；L51断言`"is_superuser =" not in runtime and "is_superuser=True" not in runtime`；L52断言`"with_for_update()" in runtime`；L53断言`"Use the business workflow API" in (folder / "guard.py").read_text(encoding="utf-8")`。 调用`(folder / "controller.py").read_text`、`(folder / "runtime.py").read_text`、`folder.glob`、`ast.parse`、`file.read_text`、`(folder / "guard.py").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ui_uses_native_components_and_session_request_layer`（L56–L67）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L58遍历`( "FaSearchBar", "FaDialog", "ElTable", "ElTimeline", "ElCard", "…`；L66断言`marker in page`；L67断言`"localStorage" not in page and "fetch(" not in page`。 调用`(ROOT / "templates/business/fastapiadmin/index.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fixture_plan`（L70–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L71的`{ "title": "Native case", "data_scope": "shared", "acceptance": ["Business"], "entities": …`。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals`（L103–L213）：接收`tmp_path`、`monkeypatch`。 控制顺序：L151断言`result["entities"][0]["generated_crud_guarded"]`；L152断言`(folder / "model.py").read_text(encoding="utf-8") == "# original generated model\n"`；L153断言`(reports / "business-originals/cases/controller.py").read_text( encoding="utf-8" ) ==…`；L156断言`"dependencies=[Depends(block_generated_crud)]" in (folder / "controller.py").read_tex…`；L159断言`shell.read_text(encoding="utf-8") == "original shell"`；L161断言`patched_controller.index("await db.commit()") < patched_controller.index( "return Suc…`；L203断言`asyncio.run(scope["create_user_controller"]()) == {"id": 6}`；L204断言`calls[-1] == "success_response"`。后续分支沿下方源码相同行号继续阅读。 调用`shutil.copytree`、`policy.parent.mkdir`、`policy.write_text`、`monkeypatch.setattr`、`registration.parent.mkdir`、`registration.write_text`、`folder.mkdir`、`(folder / "controller.py").write_text`、`(folder / "model.py").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.Service`（L170–L176）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.Service.__init__`（L171–L172）：接收`auth`、`db`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.Service.create`（L174–L176）：接收`data`。 调用`calls.append`。 返回路径：L176的`{"id": 6}`。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.Session`（L178–L180）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.Session.commit`（L179–L180）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`calls.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extension_preserves_actual_generated_model_and_backs_up_originals.response`（L182–L185）：接收`**kwargs`。 控制顺序：L183断言`calls == ["native_create_flushed", "committed"]`。 调用`calls.append`。 返回路径：L185的`kwargs["data"]`。
- `test_bootstrap_and_role_mutation_serialization_are_explicit`（L216–L222）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L218断言`'source_key="bootstrap"' in source`；L219断言`'source_key == "bootstrap"' in source`；L220断言`"except IntegrityError" in source`；L222断言`role.index("with_for_update()") < role.index("await rt.actor")`。 调用`(ROOT / "templates/business/fastapiadmin/controller.py").read_tex…`、`source.index`、`role.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_native_status_is_initialized_without_exposing_it_to_input`（L225–L228）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L227断言`'values["status"] = 0' in runtime`；L228断言`"set(data) - set(fields)" in runtime`。 调用`(ROOT / "templates/business/fastapiadmin/runtime.py").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_quantity_validator_rejects_out_of_contract_post_and_put_values`（L231–L295）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Exercise the native callback over HTTP without importing its ORM stack.。 控制顺序：L288遍历`(("POST", "/cases", 201), ("PUT", "/cases/1", 200))`；L289遍历`(2, 8)`；L291断言`response.status_code == success`；L292断言`response.json() == {"quantity": value}`；L293遍历`(0, 1, 9, -1, 2**31, -(2**31) - 1, True, 2.0, "2")`；L295断言`response.status_code == 422`。 调用`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`(ROOT / "templates/business/fastapiadmin/runtime.py").read_text`、`ast.parse`、`isinstance`、`policy.Policy`、`exec`、`compile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_quantity_validator_rejects_out_of_contract_post_and_put_values.validate_record`（L282–L283）：接收`data`、`request`。 调用`scope["validate"]`。 返回路径：L283的`await scope["validate"](None, None, "cases", data, creation=request.method == "POST")`。
- `generated_relation_model`（L298–L310）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L299的`"""from datetime import datetime from sqlalchemy import DateTime, Integer, String from sql…`。
- `relation_contract`（L313–L324）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`。 返回路径：L324的`entity, relations, targets`。
- `test_actual_generator_shape_preserves_native_fk_and_timezone_on_fresh_metadata`（L327–L359）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L347断言`table.c.resolved_at.type.timezone is True`；L348断言`{(fk.parent.name, fk.target_fullname, fk.ondelete) for fk in table.foreign_keys} == {…`；L352断言`"# 原生生成字段；保留备注与所有其他字段" in transformed`；L353断言`"title: Mapped[str] = mapped_column(String(250), nullable=False, comment='标题')" in tr…`；L357断言`"FOREIGN KEY" in str( __import__("sqlalchemy").schema.CreateTable(table).compile(dial…`。 调用`Table`、`Column`、`generated_relation_model`、`extend_model`、`relation_contract`、`exec`、`compile`、`str`、`__import__("sqlalchemy").schema.CreateTable(table).compile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_generator_shape_preserves_native_fk_and_timezone_on_fresh_metadata.NativeBase`（L333–L334）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_actual_generator_shape_preserves_native_fk_and_timezone_on_fresh_metadata.ModelMixin`（L336–L338）：继承`NativeBase`。声明的数据项为`id`；类型约束/数据库列参数以完整定义为准。
- `test_model_extension_rejects_unrecognized_native_shapes`（L363–L378）：接收`change`。 控制顺序：L367按`change == "missing"`分支；L369按`change == "wrong_table"`分支；L371按`change == "wrong_type"`分支。 调用`generated_relation_model`、`source.replace`、`pytest.raises`、`extend_model`、`relation_contract`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_namespaced_roles_pass_the_pinned_native_output_validator`（L381–L413）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L409遍历`("manager", "service", "employee", "a" * 40)`；L411断言`scope["validate_required_code"](code) == code`。 调用`(ROOT / "templates/business/fastapiadmin/runtime.py").read_text`、`next`、`ast.parse`、`isinstance`、`any`、`eval`、`compile`、`ast.Expression`、`zipfile.ZipFile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_business_menus_follow_read_grants_without_admin_fallback`（L416–L436）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L429断言`readable("manager") == {"customers", "requests", "tasks"}`；L430断言`readable("service") == {"customers", "requests", "tasks"}`；L431断言`readable("employee") == {"customers", "requests"}`；L432断言`readable("unknown") == set()`；L434断言`readable("manager") == set()`；L435断言`"for e in readable_entities(role)" in source`；L436断言`"while parent in by_id and parent not in chosen" in source`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`(ROOT / "templates/business/fastapiadmin/runtime.py").read_text`、`next`、`ast.parse`、`isinstance`、`exec`、`compile`、`ast.Module`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_presentation_resolves_only_authorized_references_and_preserves_raw_values`（L439–L506）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L493断言`values == original`；L494断言`all(visible[key] == value for key, value in original.items())`；L495断言`visible["_display"] == { "partner": "Authorized partner", "assignee": "Business membe…`；L500断言`visible["_title"] == "Synthetic subject"`；L501断言`called == [("partners", "7", "read"), ("$users", "6", "name"), ("$users", "2", "name"…`；L505断言`denied["_display"]["partner"] == "无权查看关联记录"`；L506断言`"Authorized partner" not in denied["_display"].values()`。 调用`(ROOT / "templates/business/fastapiadmin/runtime.py").read_text`、`ast.parse`、`isinstance`、`exec`、`compile`、`ast.Module`、`deepcopy`、`asyncio.run`、`scope["present_values"]`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_presentation_resolves_only_authorized_references_and_preserves_raw_values.record`（L454–L458）：接收`db`、`who`、`entity`、`identifier`、`action`。 控制顺序：L456按`str(identifier) == "99"`分支；L457抛异常，停止当前正常路径。 调用`called.append`、`str`、`HTTPException`。 返回路径：L458的`{"display_name": "Authorized partner"}`。
- `test_presentation_resolves_only_authorized_references_and_preserves_raw_values.user_label`（L460–L462）：接收`db`、`identifier`、`cache`。 调用`called.append`、`str`。 返回路径：L462的`"Business member"`。
- `test_native_display_uses_contract_labels_and_keeps_parseable_original_components`（L509–L520）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L514断言`"field.label \|\| field.name" in source`；L515断言`"field.choice_labels?.[choice] \|\| choice" in source`；L516断言`"transition.label \|\| transition.name" in source`；L517断言`"item.actor_name" in source and "row._display" in source`；L518断言`':min-width="columnWidth(field)"' in source`；L519断言`"white-space: nowrap" in source and " + ' UTC'" in source`；L520断言`parse_file(page)["parse_error"] is False`。 调用`page.read_text`、`parse_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_assignee_selection_uses_unique_authorized_username_after_restart`（L523–L533）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L529断言`"UserModel.name, UserModel.username, RoleModel.code" in controller`；L530断言`'"username": username' in controller`；L531断言`"${user.name} · ${user.username}" in page`；L532断言`"assign(page, 'requests', request, scenario.actors.service.username)" in browser`；L533断言`"assign(page, 'tasks', task, scenario.actors.service.username)" in browser`。 调用`(ROOT / "templates/business/fastapiadmin/controller.py").read_tex…`、`(ROOT / "templates/business/fastapiadmin/index.vue").read_text`、`(ROOT / "scripts/business_fastapi_browser.cjs").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_fastapi.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L533。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21237`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_fastapi.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b899241021d5060129b6dc32d56ddd54a0f6a24281eb8b74aafffb8078f1cba6"} -->
````python
# tests/test_business_fastapi.py
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


def test_native_quantity_validator_rejects_out_of_contract_post_and_put_values():
    """Exercise the native callback over HTTP without importing its ORM stack."""
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.testclient import TestClient

    spec = importlib.util.spec_from_file_location(
        "native_numeric_policy", ROOT / "templates/business/common/policy.py"
    )
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    config = {
        "entities": [
            {
                "name": "cases",
                "fields": [
                    {
                        "name": "quantity",
                        "kind": "integer",
                        "required": True,
                        "minimum": 2,
                        "maximum": 8,
                    }
                ],
            }
        ],
        "business": {
            "resources": [{"entity": "cases"}],
            "roles": [],
            "permissions": [],
            "workflows": [],
            "relations": [],
        },
    }
    source = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    functions = [
        node
        for node in ast.parse(source).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in {"fail", "validate"}
    ]
    scope = {
        "HTTPException": HTTPException,
        "ENTITIES": {"cases": config["entities"][0]},
        "POLICY": policy.Policy(config),
        "SPEC": config["business"],
        "PolicyError": policy.PolicyError,
        "validate_scalar_constraints": policy.validate_scalar_constraints,
    }
    exec(compile(ast.Module(body=functions, type_ignores=[]), "native-validate", "exec"), scope)
    app = FastAPI()

    async def validate_record(data: dict, request: Request):
        return await scope["validate"](None, None, "cases", data, creation=request.method == "POST")

    app.post("/cases", status_code=201)(validate_record)
    app.put("/cases/1")(validate_record)
    with TestClient(app) as client:
        for method, path, success in (("POST", "/cases", 201), ("PUT", "/cases/1", 200)):
            for value in (2, 8):
                response = client.request(method, path, json={"quantity": value})
                assert response.status_code == success, response.text
                assert response.json() == {"quantity": value}
            for value in (0, 1, 9, -1, 2**31, -(2**31) - 1, True, 2.0, "2"):
                response = client.request(method, path, json={"quantity": value})
                assert response.status_code == 422, (method, value, response.text)


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
````
