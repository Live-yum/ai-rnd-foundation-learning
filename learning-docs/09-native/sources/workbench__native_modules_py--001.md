# workbench/native_modules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把Plan的实体挂载成原生业务模块。** validate_plan先拒绝尚未适配的业务类型；元数据生成与业务建表使用同一Plan。generate_modules实际调用原生生成器，解包并挂载后端、前端、菜单和权限，记录映射，不能以几个示例文件冒充整套原生工程。

**对应关系：** native_lab → create_native_tables/generate_modules → NativeClient/native_vben；test_native_modules。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native`、`workbench.native_checks`、`workbench.native_compatibility`、`workbench.native_environment`、`workbench.native_vben`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 批准的实体不是直接拷贝成通用Python CRUD。这里把表和字段翻译成所选框架的真实代码生成输入，再安装实际导出文件与菜单；表名、序列、逻辑删除字段和原生权限均需匹配。源码导出仅证明SOURCE_READY，之后还要编译、启动、HTTP和原生浏览器检查。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `validate_plan`（L59–L100）：接收`plan`。 控制顺序：L61按`plan.unsupported`分支；L62抛异常，停止当前正常路径；L63按`len({rule.entity for rule in plan.custom_rules}) != len(plan.custom_rules)`分支；L64抛异常，停止当前正常路径；L67按`any(field.name in RULE_RESERVED for entity in plan.entities for field in entity.field…`分支；L68抛异常，停止当前正常路径；L69按`plan.data_scope != "shared"`分支；L70抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Plan.model_validate`、`ValueError`、`len`、`any`、`e.name.replace`、`re.fullmatch`。 返回路径：L100的`plan`。
- `native_metadata`（L103–L216）：接收`template`、`plan`、`url`、`run_id`。 源码说明：Include the framework audit columns and PG sequence used by the generated ORM.。 控制顺序：L108按`template == "fastapiadmin"`分支；L110按`template == "yudao-vben" and plan.business`分支；L121遍历`plan.entities`；L123按`template == "fastapiadmin"`分支；L150按`template == "yudao-vben"`分支；L172抛异常，停止当前正常路径；L173遍历`entity.fields`；L184按`relation`分支。后续分支沿下方源码相同行号继续阅读。 调用`checked_database`、`validate_plan`、`MetaData`、`Table`、`Column`、`digest`、`String`、`text`、`DateTime`等。 返回路径：L216的`metadata, tables, mapping`。
- `create_native_tables`（L219–L244）：接收`template`、`plan`、`url`、`run_id`、`reports`。 控制顺序：L225按`existing.intersection(mapping.values())`分支；L226抛异常，停止当前正常路径；L231遍历`metadata.sorted_tables`；L232按`table not in tables`分支；L234按`template == "yudao-vben"`分支；L239遍历`sorted(table.indexes, key=lambda item: item.name)`。 调用`native_metadata`、`create_engine`、`engine.begin`、`set`、`inspect(connection).get_table_names`、`inspect`、`existing.intersection`、`mapping.values`、`ValueError`等。 返回路径：L244的`mapping`。
- `yudao_menu`（L247–L249）：接收`client`、`data`。 调用`client.client.post`、`record_id`、`payload`。 返回路径：L249的`record_id(payload(response))`。
- `mount_yudao_export`（L252–L345）：接收`export`、`backend`、`frontend`、`entity`、`reports`、`used_errors`。 源码说明：Mount only generated feature paths; resolve ErrorCodeConstants TODO deterministically.。 控制顺序：L260遍历`sorted(root.rglob("*"))`；L261按`not file.is_file()`分支；L265按`"ErrorCodeConstants_手动操作" in name`分支；L268按`name.startswith("sql/")`分支；L270按`name.startswith("yudao-module-infra/") and "/src/main/" in name`分支；L272按`not (f"/{slug}/" in name or f"/mapper/{slug}/" in name)`分支；L273抛异常，停止当前正常路径；L275按`target.exists()`分支。后续分支沿下方源码相同行号继续阅读。 调用`tempfile.TemporaryDirectory`、`Path`、`archive.write_bytes`、`unpack`、`sorted`、`root.rglob`、`file.is_file`、`file.relative_to(root).as_posix`、`file.relative_to`等。 返回路径：L345的`{"files": writes, "error_constants": added}`。
- `generate_modules`（L348–L579）：接收`template`、`backend`、`frontend`、`base_url`、`openapi`、`token`、`mapping`、`plan`、`reports`。 源码说明：Native APIs generate every feature. No fake controller replaces upstream codegen.。 控制顺序：L364按`template == "fastapiadmin"`分支；L369遍历`plan.entities`；L397按`export.headers.get("X-Skipped-Tables")`分支；L398抛异常，停止当前正常路径；L430按`template == "yudao-vben"`分支；L454按`len(ids) != len(plan.entities)`分支；L455抛异常，停止当前正常路径；L466遍历`zip(plan.entities, ids, strict=True)`。后续分支沿下方源码相同行号继续阅读。 调用`validate_plan`、`Path`、`reports.mkdir`、`NativeClient`、`NativeConfig`、`client.payload`、`client.request`、`list`、`mapping.values`等。 返回路径：L579的`targets`。

</details>

**创建路径：** `workbench/native_modules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L579。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`24738`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_modules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "78c7aea7893d42830dccc1fb62843f7a26c58cb8d437075ad2846232208db3c0"} -->
````python
# workbench/native_modules.py
"""Native codegen -> deterministic mounting -> native menu metadata. No model-written CRUD."""

import re
import tempfile
from pathlib import Path

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Sequence,
    SmallInteger,
    String,
    Table,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.schema import CreateIndex, CreateSequence, CreateTable

from workbench.domain import Plan, digest
from workbench.filesystem import atomic_text, inside, sha, unpack, write_json
from workbench.native import NativeClient, NativeConfig
from workbench.native_checks import payload, record_id
from workbench.native_compatibility import prepare_java_time_imports
from workbench.native_environment import checked_database
from workbench.native_vben import (
    adapt_generated_form,
    adapt_generated_schema,
    prune_generated_import,
)

RESERVED = {
    "id",
    "uuid",
    "status",
    "description",
    "creator",
    "updater",
    "create_time",
    "update_time",
    "created_time",
    "updated_time",
    "created_id",
    "updated_id",
    "deleted_id",
    "is_deleted",
    "deleted_time",
    "deleted",
    "tenant_id",
}


def validate_plan(plan):
    plan = Plan.model_validate(plan)
    if plan.unsupported:
        raise ValueError("Native runtime does not accept unsupported requirements")
    if len({rule.entity for rule in plan.custom_rules}) != len(plan.custom_rules):
        raise ValueError("每个原生实体只能有一个合并后的业务规则及完整正反例")
    from workbench.native_coding import RESERVED as RULE_RESERVED

    if any(field.name in RULE_RESERVED for entity in plan.entities for field in entity.fields):
        raise ValueError("Native field uses a reserved runtime name")
    if plan.data_scope != "shared":
        raise ValueError(
            "Native runtime currently requires explicitly approved shared data with role permissions"
        )
    if len({"wb" + e.name.replace("_", "") for e in plan.entities}) != len(plan.entities):
        raise ValueError("Native normalized business names collide")
    for entity in plan.entities:
        for field in entity.fields:
            if plan.business is None and field.kind not in {"text", "integer", "boolean"}:
                raise ValueError("Native enum/date/datetime fields require a business contract")
            if plan.business is None and (
                field.searchable or field.filterable or field.date_range or field.min_length
            ):
                raise ValueError(
                    "Native adapters do not yet execute searchable/filterable/date_range/min_length; "
                    "use a supported template or explicitly revise the requirement"
                )
        if not any(field.kind == "text" and field.required for field in entity.fields):
            raise ValueError(
                "Native runtime requires a required text field in each entity for independent UI acceptance"
            )
        if len(entity.name) > 20 or not re.fullmatch(r"[a-z][a-z0-9_]*", entity.name):
            raise ValueError(
                "Native entity identifiers must be lowercase and at most 20 characters"
            )
        if not re.fullmatch(r"[\w\s\-\u4e00-\u9fff]{1,100}", entity.description) or any(
            c in entity.description for c in "\r\n\t"
        ):
            raise ValueError("Native labels cannot contain code delimiters or multiline text")
        if any(field.name in RESERVED for field in entity.fields):
            raise ValueError("Field conflicts with native framework audit columns")
    return plan


def native_metadata(template, plan, url, run_id):
    """Include the framework audit columns and PG sequence used by the generated ORM."""
    checked_database(url)
    plan = validate_plan(plan)
    metadata = MetaData()
    if template == "fastapiadmin":
        Table("sys_user", metadata, Column("id", Integer, primary_key=True))
    elif template == "yudao-vben" and plan.business:
        Table("system_users", metadata, Column("id", BigInteger, primary_key=True))
    tables = []
    mapping = {
        entity.name: "wb_" + digest(run_id)[:8] + "_" + entity.name for entity in plan.entities
    }
    relations = (
        {(item.entity, item.field): item for item in plan.business.relations}
        if plan.business
        else {}
    )
    for entity in plan.entities:
        name = mapping[entity.name]
        if template == "fastapiadmin":
            columns = [
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column("uuid", String(64), nullable=False, unique=True),
                Column("is_deleted", Boolean, nullable=False, server_default=text("false")),
                Column(
                    "created_time",
                    DateTime(timezone=True),
                    nullable=False,
                    server_default=text("CURRENT_TIMESTAMP"),
                ),
                Column(
                    "updated_time",
                    DateTime(timezone=True),
                    nullable=False,
                    server_default=text("CURRENT_TIMESTAMP"),
                ),
                Column("deleted_time", DateTime(timezone=True)),
                Column("status", Integer, nullable=False, server_default=text("0"), comment="状态"),
                Column("description", String(500), comment="备注"),
            ]
            columns += [
                Column(
                    n, Integer, ForeignKey("sys_user.id", ondelete="SET NULL", onupdate="CASCADE")
                )
                for n in ("created_id", "updated_id", "deleted_id")
            ]
        elif template == "yudao-vben":
            seq = Sequence(name + "_seq", metadata=metadata)
            columns = [
                Column("id", BigInteger, seq, primary_key=True, server_default=seq.next_value()),
                Column("creator", String(64), server_default=""),
                Column("updater", String(64), server_default=""),
                Column(
                    "create_time",
                    DateTime(),
                    nullable=False,
                    server_default=text("CURRENT_TIMESTAMP"),
                ),
                Column(
                    "update_time",
                    DateTime(),
                    nullable=False,
                    server_default=text("CURRENT_TIMESTAMP"),
                ),
                Column("deleted", SmallInteger, nullable=False, server_default=text("0")),
                Column("tenant_id", BigInteger, nullable=False, server_default=text("1")),
            ]
        else:
            raise ValueError("Unknown native template")
        for field in entity.fields:
            kind = {
                "text": String(field.max_length),
                "integer": Integer(),
                "boolean": Boolean(),
                "enum": String(max([len(value) for value in field.choices] or [1])),
                "date": Date(),
                "datetime": DateTime(timezone=template == "fastapiadmin"),
            }[field.kind]
            constraints = []
            relation = relations.get((entity.name, field.name))
            if relation:
                kind = Integer() if template == "fastapiadmin" else BigInteger()
                target = (
                    ("sys_user" if template == "fastapiadmin" else "system_users")
                    if relation.target_entity == "$users"
                    else mapping[relation.target_entity]
                )
                constraints.append(ForeignKey(target + ".id", ondelete="RESTRICT"))
            columns.append(
                Column(
                    field.name, kind, *constraints, nullable=not field.required, comment=field.name
                )
            )
        for column in columns:
            if (
                plan.business
                and template == "fastapiadmin"
                and column.name
                in {
                    "id",
                    "uuid",
                    "is_deleted",
                    "created_time",
                    "created_id",
                    "updated_id",
                    "deleted_id",
                }
            ):
                column.index = True
            if not column.comment:
                column.comment = column.name
        tables.append(Table(name, metadata, *columns, comment=entity.description))
    return metadata, tables, mapping


def create_native_tables(template, plan, url, run_id, reports):
    metadata, tables, mapping = native_metadata(template, plan, url, run_id)
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            existing = set(inspect(connection).get_table_names())
            if existing.intersection(mapping.values()):
                raise ValueError(
                    "Business tables already exist; use a new run ID, never overwrite data"
                )
            metadata.create_all(connection, tables=tables)
        ddl = []
        for table in metadata.sorted_tables:
            if table not in tables:
                continue
            if template == "yudao-vben":
                ddl.append(
                    str(CreateSequence(table.c.id.default).compile(dialect=engine.dialect)) + ";"
                )
            ddl.append(str(CreateTable(table).compile(dialect=engine.dialect)) + ";")
            for index in sorted(table.indexes, key=lambda item: item.name):
                ddl.append(str(CreateIndex(index).compile(dialect=engine.dialect)) + ";")
        atomic_text(Path(reports) / "business-schema.sql", "\n".join(ddl) + "\n")
    finally:
        engine.dispose()
    return mapping


def yudao_menu(client, data):
    response = client.client.post("/admin-api/system/menu/create", json=data)
    return record_id(payload(response))


def mount_yudao_export(export, backend, frontend, entity, reports, used_errors):
    """Mount only generated feature paths; resolve ErrorCodeConstants TODO deterministically."""
    writes, snippets = [], []
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "export.zip"
        archive.write_bytes(export)
        root = Path(tmp) / "source"
        unpack(archive, root)
        for file in sorted(root.rglob("*")):
            if not file.is_file():
                continue
            name = file.relative_to(root).as_posix()
            body = file.read_text(encoding="utf-8")
            if "ErrorCodeConstants_手动操作" in name:
                snippets.append(body)
                continue
            if name.startswith("sql/"):
                target = Path(reports) / "native-sql" / entity.name / name
            elif name.startswith("yudao-module-infra/") and "/src/main/" in name:
                slug = "wb" + entity.name.replace("_", "")
                if not (f"/{slug}/" in name or f"/mapper/{slug}/" in name):
                    raise ValueError("Unexpected generated Java target: " + name)
                target = inside(backend, name)
                if target.exists():
                    raise FileExistsError("Refusing to overwrite native Java source: " + name)
                if name.endswith(".java"):
                    body = prepare_java_time_imports(body)
            elif "/src/" in name and (
                name.startswith("yudao-ui-admin-vben/") or name.startswith("yudao-ui-admin-vben5/")
            ):
                relative = name.split("/src/", 1)[1]
                slug = "wb" + entity.name.replace("_", "")
                if not (
                    relative.startswith(f"views/infra/{slug}/")
                    or relative.startswith(f"api/infra/{slug}/")
                ):
                    raise ValueError("Unexpected generated Vben path: " + name)
                target = inside(Path(frontend) / "apps/web-antd/src", relative)
                if target.exists():
                    raise FileExistsError(
                        "Refusing to overwrite existing Vben feature: " + relative
                    )
                if relative == f"views/infra/{slug}/modules/form.vue":
                    class_name = "Wb" + "".join(p.title() for p in entity.name.split("_"))
                    body = adapt_generated_form(body, class_name)
                elif relative == f"views/infra/{slug}/data.ts":
                    body = adapt_generated_schema(body, entity.fields)
                elif relative == f"api/infra/{slug}/index.ts":
                    body = prune_generated_import(
                        body, "Dayjs", "import type { Dayjs } from 'dayjs';\n"
                    )
            else:
                raise ValueError("Unsupported native generated file: " + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_text(target, body)
            writes.append(
                {
                    "source": name,
                    "path": str(target),
                    "source_sha256": sha(file),
                    "sha256": sha(target),
                    "compatibility_applied": sha(file) != sha(target),
                }
            )
    constants = (
        Path(backend)
        / "yudao-module-infra/yudao-module-infra-api/src/main/java/cn/iocoder/yudao/module/infra/enums/ErrorCodeConstants.java"
    )
    source = constants.read_text(encoding="utf-8")
    if not snippets:
        raise ValueError("Native export omitted error code declarations")
    added = []
    for snippet in snippets:
        matches = re.findall(
            r'ErrorCode\s+([A-Z0-9_]+)\s*=\s*new ErrorCode\(TODO 补充编号,\s*("[^"\n]*")\);',
            snippet,
        )
        if len(matches) != 1:
            raise ValueError("Unsupported native error declaration")
        name, message = matches[0]
        if re.search(r"\b" + name + r"\s*=", source):
            raise ValueError("Native error constant already exists")
        number = 1_900_000_000 + int(digest(name)[:7], 16) % 100_000_000
        while number in used_errors:
            number += 1
        used_errors.add(number)
        declaration = f"    ErrorCode {name} = new ErrorCode({number}, {message});\n"
        closing = source.rfind("}")
        if closing < 0:
            raise ValueError("Invalid native constant interface")
        source = source[:closing] + declaration + source[closing:]
        added.append({"name": name, "number": number})
    atomic_text(constants, source)
    return {"files": writes, "error_constants": added}


def generate_modules(template, backend, frontend, base_url, openapi, token, mapping, plan, reports):
    """Native APIs generate every feature. No fake controller replaces upstream codegen."""
    plan = validate_plan(plan)
    reports = Path(reports)
    reports.mkdir(parents=True, exist_ok=True)
    client = NativeClient(
        NativeConfig(
            base_url=base_url,
            openapi_path=openapi,
            token_env="NATIVE_TOKEN",
            database_url_env="NATIVE_DATABASE",
        ),
        token,
    )
    targets, receipts = [], []
    try:
        if template == "fastapiadmin":
            client.payload(client.request("POST", "/gencode/import", json=list(mapping.values())))
            rows = client.payload(client.request("GET", "/gencode/list", params={"page_size": 100}))
            rows = rows.get("items", rows.get("list", [])) if isinstance(rows, dict) else rows
            known = {r["table_name"]: r["id"] for r in rows}
            for entity in plan.entities:
                table_id = known[mapping[entity.name]]
                detail = client.payload(
                    client.request(
                        "GET", "/gencode/detail/{table_id}", replace={"table_id": table_id}
                    )
                )
                update = {
                    "table_name": mapping[entity.name],
                    "columns": detail["columns"],
                    "package_name": "module_rnd",
                    "module_name": entity.name,
                    "business_name": entity.name,
                    "class_name": "".join(p.title() for p in entity.name.split("_")),
                    "function_name": entity.description,
                    "table_comment": entity.description,
                }
                client.payload(
                    client.request(
                        "PUT",
                        "/gencode/update/{table_id}",
                        replace={"table_id": table_id},
                        json=update,
                    )
                )
                export = client.request(
                    "PATCH", "/gencode/batch/output", json=[mapping[entity.name]]
                )
                if export.headers.get("X-Skipped-Tables"):
                    raise ValueError("Native generator skipped a business table")
                archive = reports / (entity.name + "-native.zip")
                archive.write_bytes(export.content)
                client.payload(
                    client.request(
                        "POST",
                        "/gencode/output/{table_name}",
                        replace={"table_name": mapping[entity.name]},
                    )
                )
                from workbench.native_compatibility import commit_before_response

                transaction_fix = commit_before_response(
                    Path(backend) / "app/plugin/module_rnd" / entity.name / "controller.py"
                )
                target = {
                    "entity": entity.name,
                    "api": "/rnd/" + entity.name,
                    "list": "/rnd/" + entity.name + "/list",
                    "route": "/module_rnd/" + entity.name,
                    "permission": "module_rnd:" + entity.name,
                    "table": mapping[entity.name],
                }
                targets.append(target)
                receipts.append(
                    {
                        "entity": entity.name,
                        "export_sha256": sha(archive),
                        "native_local_mount": True,
                        "compatibility": transaction_fix,
                    }
                )
        elif template == "yudao-vben":
            parent = yudao_menu(
                client,
                {
                    "name": "Workbench",
                    "type": 1,
                    "sort": 99,
                    "parentId": 0,
                    "path": "/workbench",
                    "icon": "lucide:database",
                    "component": "",
                    "status": 0,
                    "visible": True,
                    "keepAlive": True,
                    "alwaysShow": True,
                },
            )
            ids = client.payload(
                client.request(
                    "POST",
                    "/infra/codegen/create-list",
                    json={"dataSourceConfigId": 0, "tableNames": list(mapping.values())},
                )
            )
            if len(ids) != len(plan.entities):
                raise ValueError("Native generator did not import every business table")
            constants = (
                Path(backend)
                / "yudao-module-infra/yudao-module-infra-api/src/main/java/cn/iocoder/yudao/module/infra/enums/ErrorCodeConstants.java"
            )
            used_errors = {
                int(n.replace("_", ""))
                for n in re.findall(
                    r"new ErrorCode\(([0-9_]+),", constants.read_text(encoding="utf-8")
                )
            }
            for entity, table_id in zip(plan.entities, ids, strict=True):
                detail = client.payload(
                    client.request("GET", "/infra/codegen/detail", params={"tableId": table_id})
                )
                slug = "wb" + entity.name.replace("_", "")
                class_name = "Wb" + "".join(p.title() for p in entity.name.split("_"))
                kebab = "wb-" + entity.name.replace("_", "-")
                if detail["table"]["tableName"] != mapping[entity.name]:
                    raise ValueError("Native generator imported tables in unexpected order")
                detail["table"].update(
                    moduleName="infra",
                    businessName=slug,
                    className=class_name,
                    classComment=entity.description,
                    tableComment=entity.description,
                    author="Workbench",
                    frontType=40,
                    scene=1,
                    templateType=1,
                    parentMenuId=parent,
                )
                fields = {f.name for f in entity.fields}
                for column in detail["columns"]:
                    if column["columnName"] == "tenant_id":
                        column.update(
                            createOperation=False,
                            updateOperation=False,
                            listOperation=False,
                            listOperationResult=False,
                        )
                    if column["columnName"] in fields:
                        column.update(
                            columnComment=column["columnName"],
                            createOperation=True,
                            updateOperation=True,
                            listOperationResult=True,
                        )
                client.payload(
                    client.request(
                        "PUT",
                        "/infra/codegen/update",
                        json={"table": detail["table"], "columns": detail["columns"]},
                    )
                )
                response = client.request(
                    "GET", "/infra/codegen/download", params={"tableId": table_id}
                )
                archive = reports / (entity.name + "-native.zip")
                archive.write_bytes(response.content)
                receipt = mount_yudao_export(
                    response.content, backend, frontend, entity, reports, used_errors
                )
                menu = yudao_menu(
                    client,
                    {
                        "name": entity.description,
                        "type": 2,
                        "sort": 1,
                        "parentId": parent,
                        "path": kebab,
                        "icon": "lucide:database",
                        "component": "infra/" + slug + "/index",
                        "componentName": class_name,
                        "permission": "",
                        "status": 0,
                        "visible": True,
                        "keepAlive": True,
                        "alwaysShow": True,
                    },
                )
                for i, operation in enumerate(("query", "create", "update", "delete", "export")):
                    yudao_menu(
                        client,
                        {
                            "name": entity.description + " " + operation,
                            "type": 3,
                            "sort": i,
                            "parentId": menu,
                            "path": "",
                            "component": "",
                            "status": 0,
                            "permission": f"infra:{kebab}:{operation}",
                            "visible": True,
                            "keepAlive": True,
                            "alwaysShow": False,
                        },
                    )
                targets.append(
                    {
                        "entity": entity.name,
                        "api": "/admin-api/infra/" + kebab,
                        "list": "/admin-api/infra/" + kebab + "/page",
                        "route": "/workbench/" + kebab,
                        "permission": "infra:" + kebab,
                        "table": mapping[entity.name],
                    }
                )
                receipts.append({"entity": entity.name, "export_sha256": sha(archive), **receipt})
        else:
            raise ValueError("Unknown native template")
    finally:
        client.close()
    write_json(
        reports / "generation.json",
        {
            "template": template,
            "spec_digest": digest(plan.model_dump()),
            "targets": targets,
            "receipts": receipts,
            "runtime_verified": False,
        },
    )
    write_json(reports / "browser-targets.json", targets)
    return targets
````
