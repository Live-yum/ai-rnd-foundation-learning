"""Export a self-contained native launcher, immutable SQL and menu seed (no user data)."""

import json
import shutil
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy import create_engine, inspect

from workbench.domain import digest
from workbench.filesystem import atomic_text, sha, write_json
from workbench.native_environment import checked_database
from workbench.settings import ROOT

HELPERS = (
    "__init__.py",
    "local_only.py",
    "settings.py",
    "domain.py",
    "business_contracts.py",
    "business_schema_receipt.py",
    "business_probe.py",
    "business_browser.py",
    "native_checks.py",
    "catalog.py",
    "errors.py",
    "filesystem.py",
    "tools.py",
    "native_environment.py",
    "native_frontend.py",
    "native_vben.py",
    "portable_checks.py",
    "native_business_checks.py",
)


def connection_url(url):
    return checked_database(url).set(drivername="postgresql").render_as_string(hide_password=False)


def menu_snapshot(template, url):
    table = "sys_menu" if template == "fastapiadmin" else "system_menu"
    with psycopg.connect(connection_url(url), row_factory=psycopg.rows.dict_row) as c:
        rows = c.execute(
            sql.SQL("SELECT * FROM {} ORDER BY id").format(sql.Identifier(table))
        ).fetchall()
    # JSON hash compares timestamps as ISO strings, but SQL retains actual Python values.
    return {row["id"]: digest(json.loads(json.dumps(row, default=str))) for row in rows}


def export_menu_sql(template, url, before, target):
    table = "sys_menu" if template == "fastapiadmin" else "system_menu"
    with psycopg.connect(connection_url(url), row_factory=psycopg.rows.dict_row) as c:
        rows = c.execute(
            sql.SQL("SELECT * FROM {} ORDER BY id").format(sql.Identifier(table))
        ).fetchall()
        changed = [
            row
            for row in rows
            if before.get(row["id"]) != digest(json.loads(json.dumps(row, default=str)))
        ]
        if not changed:
            raise ValueError("原生生成器没有新增/修改菜单，不能打包一个缺菜单的产品")
        statements = [
            "-- Deterministic native generated menu seed. No users, passwords or business rows."
        ]
        for row in changed:
            keys = list(row)
            statement = sql.SQL(
                "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {};"
            ).format(
                sql.Identifier(table),
                sql.SQL(", ").join(map(sql.Identifier, keys)),
                sql.SQL(", ").join(sql.Literal(row[key]) for key in keys),
                sql.SQL(", ").join(
                    sql.SQL("{}=EXCLUDED.{}").format(sql.Identifier(key), sql.Identifier(key))
                    for key in keys
                    if key != "id"
                ),
            )
            statements.append(statement.as_string(c))
        statements.append(
            sql.SQL(
                "SELECT setval(pg_get_serial_sequence({}, 'id'), COALESCE((SELECT max(id) FROM {}),0)+1, false);"
            )
            .format(sql.Literal(table), sql.Identifier(table))
            .as_string(c)
        )
    atomic_text(target, "\n".join(statements) + "\n")
    return {"table": table, "row_ids": [row["id"] for row in changed], "sha256": sha(target)}


def build_native_delivery(template, product, reports, plan, targets, url):
    product, reports = Path(product), Path(reports)
    deployment = product / "deployment"
    deployment.mkdir(exist_ok=True)
    source = ROOT / "templates/deployment"
    for name in ("pyproject.toml", "uv.lock", ".python-version", "services.yaml", "run.py"):
        shutil.copyfile(source / name, deployment / name)
    shutil.copyfile(source / "entry.py", product / "start.py")
    if plan.business:
        script = (
            "business_fastapi_browser.cjs"
            if template == "fastapiadmin"
            else "business_yudao_browser.cjs"
        )
        shutil.copyfile(ROOT / "scripts" / script, deployment / "business-browser.cjs")
    helper_root = deployment / "workbench"
    helper_root.mkdir(exist_ok=True)
    for name in HELPERS:
        shutil.copyfile(ROOT / "workbench" / name, helper_root / name)
    sql_dir = deployment / "database"
    sql_dir.mkdir(exist_ok=True)
    shutil.copyfile(reports / "business-schema.sql", sql_dir / "002-business.sql")
    shutil.copyfile(reports / "menu-seed.sql", sql_dir / "003-menus.sql")
    if plan.business:
        for source_name, target_name in (
            ("business-extension-schema.sql", "004-business-extension.sql"),
            ("business-role-seed.sql", "005-business-roles.sql"),
        ):
            source_file = reports / source_name
            if source_file.is_file():
                shutil.copyfile(source_file, sql_dir / target_name)
    extension_tables = []
    if plan.business:
        if template == "fastapiadmin":
            adapter = json.loads((reports / "business-extension.json").read_text(encoding="utf-8"))
            extension_tables = [adapter["namespace"] + "_events"]
        else:
            adapter = json.loads((reports / "business-yudao.json").read_text(encoding="utf-8"))
            extension_tables = list(adapter["extension_tables"])
    schema_contract = {}
    metadata = create_engine(url)
    try:
        with metadata.connect() as c:
            inspector = inspect(c)
            tables = {
                target["table"]: [
                    column["name"] for column in inspector.get_columns(target["table"])
                ]
                for target in targets
            }
            if plan.business:
                from workbench.business_schema_receipt import table_signature

                schema_contract = {
                    name: table_signature(c, name) for name in [*tables, *extension_tables]
                }
                if any(value is None for value in schema_contract.values()):
                    raise ValueError("Missing installed business extension table")
    finally:
        metadata.dispose()
    sql_files = {"database/" + p.name: sha(p) for p in sorted(sql_dir.iterdir())}
    manifest = {
        "format": 1,
        "template": template,
        "spec_digest": digest(plan.model_dump()),
        "plan": plan.model_dump(),
        "targets": targets,
        "tables": tables,
        "business_schema": schema_contract,
        "extension_tables": extension_tables,
        "sql_files": sql_files,
        "sql_digest": digest(sql_files),
        "bootstrap": "native-seed-then-business-schema-and-menus",
        "contains_user_data": False,
    }
    write_json(deployment / "manifest.json", manifest)
    atomic_text(
        product / "START_HERE.md",
        f"""# 独立启动已生成的原生产品\n\n模板：{template}。不需要原研发平台、模型 API Key 或原开发数据库。\n\n在 Linux/WSL 2 安装 Python 3.14、uv、Node22、对应 pnpm（FastapiAdmin9.15.3 / Vben11.16.0）、Docker Compose；芋道额外需要JDK17/Maven。然后在本目录执行：\n\n```bash\nuv run --no-project --python 3.14 python start.py\n```\n\n启动器在本产品的独立 Compose 项目创建 PostgreSQL17/Redis7.4、使用新随机数据库密码和本机空闲端口，安装锁定依赖，执行原生初始化、`deployment/database/002-business.sql` 和 `003-menus.sql`，验证新库中的菜单与CRUD，构建前端并启动。\n\n默认管理员只供本机开发：FastapiAdmin super/123456；芋道 admin/admin123。第一次启动后应修改默认管理员密码；再次启动不会覆盖密码或删除记录。公网部署前必须完成额外的安全配置。\n\n已有的专用空本机 PostgreSQL 服务可用 `NATIVE_DELIVERY_DATABASE_URL`（库名以 `_codegen` 结尾）和 `NATIVE_DELIVERY_REDIS_PORT` 指定，不需要 Docker。程序只接受空库或之前被这份不可变交付认领的库，拒绝覆盖其他数据。\n\n首次启动需要互联网下载Python/Java/Node依赖，源码和数据库语句已在包内，不会重新克隆模板。重复启动复用持久数据；Ctrl+C仅停止应用，Compose数据卷保留。\n\n`--check` 在新库初始化并验证后退出；`--skip-build` 仅用于已经成功安装/构建的同一产品，不能拿它代替首次安装。\n\n`.deployment/` 保存本产品生成的数据库凭据，不要提交Git、分享或打包。备份需要同时备份数据库持久卷；源码包含初始化语句但不包含任何用户业务记录。\n""",
    )
    return {
        "sql_files": sql_files,
        "sql_digest": manifest["sql_digest"],
        "standalone_start": "uv run --no-project --python 3.14 python start.py",
        "database_initialization_included": True,
    }


def verify_native_delivery(product, url, reports, redis_port=6379, *, template):
    """Restore the distributable ZIP; run startup against a DIFFERENT empty DB."""
    import os
    import sys
    import tempfile
    import uuid

    from workbench.filesystem import manifest, pack_source, unpack
    from workbench.tools import run_command

    name = "restore_" + uuid.uuid4().hex[:16] + "_codegen"
    if template not in {"fastapiadmin", "yudao-vben"}:
        raise ValueError("原生交付模板未知")
    parsed = checked_database(url)
    created = False
    try:
        with psycopg.connect(connection_url(url), autocommit=True) as c:
            c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            created = True
        with tempfile.TemporaryDirectory(prefix="rnd-independent-native-") as directory:
            copy = Path(directory) / "product"
            archive = Path(directory) / "delivery.zip"
            listing = manifest(product)
            packaged = pack_source(product, archive, template=template)
            restored = unpack(archive, copy, template=template)
            if restored != packaged or manifest(copy) != listing:
                raise ValueError("原生交付ZIP与已验证源码不一致")
            clean_url = parsed.set(database=name).render_as_string(hide_password=False)
            try:
                command = run_command(
                    [sys.executable, str(copy / "start.py"), "--check"],
                    copy,
                    2100,
                    {
                        "NATIVE_DELIVERY_DATABASE_URL": clean_url,
                        "NATIVE_DELIVERY_REDIS_PORT": str(redis_port),
                        "NATIVE_DELIVERY_REDIS_DB": "8",
                        "UV_PYTHON": sys.executable,
                        "JAVA_HOME": os.environ.get("JAVA_HOME", ""),
                        "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get(
                            "PRODUCT_VERIFY_PLAYWRIGHT",
                            str(ROOT / ".native/browser/node_modules/playwright"),
                        ),
                        "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
                    },
                    heartbeat="independent-native-start",
                )
            except Exception as exc:
                atomic_text(Path(reports) / "portable-start.log", getattr(exc, "log", str(exc)))
                raise
            atomic_text(Path(reports) / "portable-start.log", command["log"])
            result = json.loads(
                (copy / ".deployment/reports/portable-start.json").read_text(encoding="utf-8")
            )
            if (
                result.get("passed") is not True
                or result.get("frontend_started") is not True
                or result.get("restart") is not True
                or result.get("business")
                and result.get("restart_preserved_records") is not True
            ):
                raise ValueError("独立交付包未完成新库/菜单/CRUD/前端启动与重启保留数据验收")
            result.update(
                fresh_database=True,
                standalone_launcher=True,
                installed_from_lock=True,
                original_platform_imported=False,
                source_database_reused=False,
                archive_round_trip=True,
                archive=restored,
            )
            write_json(Path(reports) / "portable-start.json", result)
            return result
    finally:
        if created:
            with psycopg.connect(connection_url(url), autocommit=True) as c:
                c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
