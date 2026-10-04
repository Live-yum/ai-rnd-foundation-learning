# templates/deployment/run.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生独立交付启动器。** 该文件随成品复制，负责本机数据库初始化、业务/菜单SQL恢复和前后端启动。helper文件来自portable.HELPERS的明确清单，不允许从原开发目录隐式导入。

**对应关系：** portable.build_native_delivery → 新目录运行start.py → 新数据库复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_environment`、`workbench.native_frontend`、`workbench.native_ports`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `free_port`（L43–L46）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L46的`sock.getsockname()[1]`。
- `services`（L49–L92）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Use explicit external local services, or start only this delivery's Compose project.。 控制顺序：L52按`explicit`分支；L57按`not path.exists()`分支。 调用`os.getenv`、`int`、`state.mkdir`、`path.exists`、`secrets.token_urlsafe`、`free_port`、`secrets.token_hex`、`path.open`、`json.dump`等。 返回路径：L53的`explicit, int(os.getenv("NATIVE_DELIVERY_REDIS_PORT", "6379"))`；L89的`( f"postgresql+psycopg://native:{value['password']}@127.0.0.1:{value['pg_port']}/product_c…`。
- `db_url`（L95–L96）：接收`url`。 调用`checked_database(url).set(drivername="postgresql").render_as_stri…`、`checked_database(url).set`、`checked_database`。 返回路径：L96的`checked_database(url).set(drivername="postgresql").render_as_string(hide_password=False)`。
- `ownership`（L99–L119）：接收`url`、`manifest`。 源码说明：Refuse anything except an empty DB or a DB already claimed by this exact product.。 控制顺序：L107按`current in {marker + ":claimed", marker + ":ready"}`分支；L112按`count or current`分支；L113抛异常，停止当前正常路径。 调用`checked_database`、`psycopg.connect`、`db_url`、`c.execute( "SELECT shobj_description(oid, 'pg_database') FROM pg_…`、`c.execute`、`current.endswith`、`c.execute( "SELECT count(*) FROM pg_class c JOIN pg_namespace n O…`、`ValueError`、`sql.SQL("COMMENT ON DATABASE {} IS {}").format`等。 返回路径：L108的`marker, current.endswith(":ready")`；L119的`marker, False`。
- `seed_yudao`（L122–L127）：接收`url`、`backend`。 控制顺序：L125按`present`分支。 调用`psycopg.connect`、`db_url`、`c.execute("SELECT to_regclass('public.system_users')").fetchone`、`c.execute`、`(backend / "sql/postgresql/ruoyi-vue-pro.sql").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `apply_delivery_sql`（L130–L158）：接收`url`、`manifest`、`marker`。 源码说明：Schema and menu SQL is trusted generated metadata, never raw model SQL.。 控制顺序：L132按`manifest.get("business_schema")`分支；L139遍历`existing`；L141按`actual != set(manifest["tables"][name])`分支；L142抛异常，停止当前正常路径；L149按`not existing`分支；L151按`existing != set(manifest["tables"])`分支；L152抛异常，停止当前正常路径。 调用`manifest.get`、`apply_business_delivery_sql`、`create_engine`、`engine.connect`、`inspect`、`inspector.has_table`、`inspector.get_columns`、`set`、`ValueError`等。 返回路径：L133的`apply_business_delivery_sql(url, manifest, marker)`。
- `apply_business_delivery_sql`（L161–L205）：接收`url`、`manifest`、`marker`。 控制顺序：L170按`existing and existing != set(manifest["tables"])`分支；L171抛异常，停止当前正常路径；L173按`installed`分支；L175按`existing`分支；L176遍历`existing`；L182按`table_signature(connection, name) != expected`分支；L183抛异常，停止当前正常路径；L185按`not existing`分支。后续分支沿下方源码相同行号继续阅读。 调用`create_engine`、`engine.connect`、`inspect`、`inspector.has_table`、`set`、`ValueError`、`bool`、`verify_tables`、`dict`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_manifest`（L208–L213）：接收`data`。 控制顺序：L209遍历`data["sql_files"].items()`；L210按`sha(HERE / name) != expected`分支；L211抛异常，停止当前正常路径；L212按`digest(data["sql_files"]) != data["sql_digest"]`分支；L213抛异常，停止当前正常路径。 调用`data["sql_files"].items`、`sha`、`ValueError`、`digest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L216–L353）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L233按`args.skip_build and os.getenv("NATIVE_DELIVERY_PORT")`分支；L238按`args.skip_build and not os.getenv("NATIVE_DELIVERY_PORT")`分支；L240按`saved_backend_port(port_receipt) is None`分支；L241抛异常，停止当前正常路径；L245按`args.skip_build`分支；L249按`not ready and template == "yudao-vben"`分支；L262按`not args.skip_build`分支；L264按`not ready and template == "yudao-vben"`分支。后续分支沿下方源码相同行号继续阅读。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`json.loads`、`(HERE / "manifest.json").read_text`、`verify_manifest`、`os.getenv`、`require_frontend_backend`、`saved_backend_port`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/deployment/run.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L360。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15603`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/deployment/run.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6c6ceef859b517f7a57f1e420df4e140dac6d2197fec7502eacfb7ea95975af3"} -->
````python
# templates/deployment/run.py
"""Initialize the delivered product into a NEW owned database, restore menus, then start.

No dependency on the workbench control database, model account, or the original development DB.
Existing unrelated databases are refused. A database comment binds resumable initialization
and subsequent starts to this immutable product specification.
"""

import argparse
import json
import os
import secrets
import socket
import time
from contextlib import ExitStack
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy import create_engine, inspect

from workbench.domain import digest
from workbench.filesystem import sha, write_json
from workbench.native_environment import (
    checked_database,
    install_backend,
    login,
    native_environment,
    running_backend,
)
from workbench.native_frontend import (
    build_frontend,
    frontend_environment,
    frontend_preview,
    require_frontend_backend,
)
from workbench.native_ports import backend_port_lease, saved_backend_port
from workbench.tools import run_command

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parent


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def services():
    """Use explicit external local services, or start only this delivery's Compose project."""
    explicit = os.getenv("NATIVE_DELIVERY_DATABASE_URL", "")
    if explicit:
        return explicit, int(os.getenv("NATIVE_DELIVERY_REDIS_PORT", "6379"))
    state = PRODUCT / ".deployment"
    state.mkdir(exist_ok=True)
    path = state / "services.json"
    if not path.exists():
        value = {
            "password": secrets.token_urlsafe(32),
            "pg_port": free_port(),
            "redis_port": free_port(),
            "project": "rnd" + secrets.token_hex(6),
        }
        with path.open("x", encoding="utf-8") as f:
            json.dump(value, f)
        path.chmod(0o600)
    value = json.loads(path.read_text(encoding="utf-8"))
    env = state / "services.env"
    env.write_text(
        f"POSTGRES_PASSWORD={value['password']}\nPG_PORT={value['pg_port']}\nREDIS_PORT={value['redis_port']}\nCOMPOSE_PROJECT_NAME={value['project']}\n",
        encoding="utf-8",
    )
    env.chmod(0o600)
    run_command(
        [
            "docker",
            "compose",
            "--env-file",
            str(env),
            "-f",
            str(HERE / "services.yaml"),
            "up",
            "-d",
            "--wait",
        ],
        PRODUCT,
        300,
    )
    return (
        f"postgresql+psycopg://native:{value['password']}@127.0.0.1:{value['pg_port']}/product_codegen",
        value["redis_port"],
    )


def db_url(url):
    return checked_database(url).set(drivername="postgresql").render_as_string(hide_password=False)


def ownership(url, manifest):
    """Refuse anything except an empty DB or a DB already claimed by this exact product."""
    parsed = checked_database(url)
    marker = "rnd-delivery:" + manifest["spec_digest"] + ":" + manifest["sql_digest"]
    with psycopg.connect(db_url(url)) as c:
        current = c.execute(
            "SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname=current_database()"
        ).fetchone()[0]
        if current in {marker + ":claimed", marker + ":ready"}:
            return marker, current.endswith(":ready")
        count = c.execute(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r','p','v','m','S')"
        ).fetchone()[0]
        if count or current:
            raise ValueError("拒绝初始化非空或不属于此交付的数据库；不会DROP已有数据库")
        c.execute(
            sql.SQL("COMMENT ON DATABASE {} IS {}").format(
                sql.Identifier(parsed.database), sql.Literal(marker + ":claimed")
            )
        )
    return marker, False


def seed_yudao(url, backend):
    with psycopg.connect(db_url(url)) as c:
        present = c.execute("SELECT to_regclass('public.system_users')").fetchone()[0]
        if present:
            return
        c.execute((backend / "sql/postgresql/ruoyi-vue-pro.sql").read_text(encoding="utf-8"))


def apply_delivery_sql(url, manifest, marker):
    """Schema and menu SQL is trusted generated metadata, never raw model SQL."""
    if manifest.get("business_schema"):
        return apply_business_delivery_sql(url, manifest, marker)
    engine = create_engine(url)
    try:
        with engine.connect() as c:
            inspector = inspect(c)
            existing = {name for name in manifest["tables"] if inspector.has_table(name)}
            for name in existing:
                actual = {column["name"] for column in inspector.get_columns(name)}
                if actual != set(manifest["tables"][name]):
                    raise ValueError("数据库已有业务表结构与交付不一致；不覆盖")
    finally:
        engine.dispose()
    parsed = checked_database(url)
    with psycopg.connect(db_url(url)) as c:
        # All business tables are either created by FastapiAdmin metadata on startup,
        # or created here before MyBatis serves any business request.
        if not existing:
            c.execute((HERE / "database/002-business.sql").read_text(encoding="utf-8"))
        elif existing != set(manifest["tables"]):
            raise ValueError("部分业务表缺失；保留现场，不进行不确定的自动覆盖")
        c.execute((HERE / "database/003-menus.sql").read_text(encoding="utf-8"))
        c.execute(
            sql.SQL("COMMENT ON DATABASE {} IS {}").format(
                sql.Identifier(parsed.database), sql.Literal(marker + ":ready")
            )
        )


def apply_business_delivery_sql(url, manifest, marker):
    from workbench.business_schema_receipt import table_signature, verify_tables

    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            existing = {name for name in manifest["tables"] if inspector.has_table(name)}
            sidecars = {name for name in manifest["extension_tables"] if inspector.has_table(name)}
            if existing and existing != set(manifest["tables"]):
                raise ValueError("Partial business schema; preserve the owned database")
            installed = bool(sidecars)
            if installed:
                verify_tables(connection, manifest["business_schema"])
            elif existing:
                for name in existing:
                    expected = dict(manifest["business_schema"][name])
                    # Yudao's explicit extension adds this server-owned archive column.
                    expected["columns"] = [
                        c for c in expected["columns"] if c["name"] != "rnd_archived_at"
                    ]
                    if table_signature(connection, name) != expected:
                        raise ValueError("Base business schema changed; preserve the database")
        with psycopg.connect(db_url(url)) as connection:
            if not existing:
                connection.execute((HERE / "database/002-business.sql").read_text(encoding="utf-8"))
            connection.execute((HERE / "database/003-menus.sql").read_text(encoding="utf-8"))
            if not installed:
                connection.execute(
                    (HERE / "database/004-business-extension.sql").read_text(encoding="utf-8")
                )
            roles = HERE / "database/005-business-roles.sql"
            if roles.is_file():
                connection.execute(roles.read_text(encoding="utf-8"))
        with engine.connect() as connection:
            verify_tables(connection, manifest["business_schema"])
        parsed = checked_database(url)
        with psycopg.connect(db_url(url)) as connection:
            connection.execute(
                sql.SQL("COMMENT ON DATABASE {} IS {}").format(
                    sql.Identifier(parsed.database), sql.Literal(marker + ":ready")
                )
            )
    finally:
        engine.dispose()


def verify_manifest(data):
    for name, expected in data["sql_files"].items():
        if sha(HERE / name) != expected:
            raise ValueError("交付数据库脚本哈希变化；拒绝自动执行")
    if digest(data["sql_files"]) != data["sql_digest"]:
        raise ValueError("数据库脚本清单摘要错误")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="initialize in the supplied new DB, verify native APIs and stop",
    )
    parser.add_argument(
        "--skip-build", action="store_true", help="reuse already installed native build outputs"
    )
    args = parser.parse_args()
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    verify_manifest(manifest)
    template = manifest["template"]
    backend = PRODUCT / "backend"
    frontend = PRODUCT / ("frontend/web" if template == "fastapiadmin" else "frontend-product")
    reports = PRODUCT / ".deployment/reports"
    if args.skip_build and os.getenv("NATIVE_DELIVERY_PORT"):
        # Reject a stale bundle before replacing a valid saved port receipt.
        require_frontend_backend(
            template, frontend, "http://127.0.0.1:" + os.environ["NATIVE_DELIVERY_PORT"]
        )
    if args.skip_build and not os.getenv("NATIVE_DELIVERY_PORT"):
        port_receipt = PRODUCT / ".deployment/backend-port.json"
        if saved_backend_port(port_receipt) is None:
            raise ValueError("No backend port for this copy; rebuild without --skip-build")
    with backend_port_lease(
        PRODUCT / ".deployment/backend-port.json", os.getenv("NATIVE_DELIVERY_PORT")
    ) as port:
        if args.skip_build:
            require_frontend_backend(template, frontend, f"http://127.0.0.1:{port}")
        url, redis_port = services()
        marker, ready = ownership(url, manifest)
        if not ready and template == "yudao-vben":
            seed_yudao(url, backend)
        env = native_environment(
            template,
            backend,
            url,
            port,
            redis_port=redis_port,
            redis_database=int(os.environ["NATIVE_DELIVERY_REDIS_DB"])
            if os.getenv("NATIVE_DELIVERY_REDIS_DB")
            else None,
        )
        # Compile the new properties into the Java jar, or install the original Python lock.
        if not args.skip_build:
            install_backend(template, backend, reports)
        if not ready and template == "yudao-vben":
            apply_delivery_sql(url, manifest, marker)
        with running_backend(template, backend, env, reports) as (base, _):
            if not ready and template == "fastapiadmin":
                apply_delivery_sql(url, manifest, marker)
            if args.check or (not ready and not manifest["plan"].get("business")):
                token = login(template, base)
                from workbench.portable_checks import check_restored_product

                outcome = check_restored_product(
                    template, base, token, manifest["targets"], manifest["plan"]
                )
                if manifest["plan"].get("business"):
                    from workbench.portable_checks import snapshot_business_records

                    before_restart = snapshot_business_records(
                        template, base, token, manifest["targets"], outcome["business"]
                    )
            else:
                # A regular restart must not require the seed admin's old password.
                outcome = {"database_initialized": True, "verification_rerun": False}
            write_json(reports / "portable-start.json", outcome)
            print("数据库、业务表、菜单和新业务CRUD已就绪。", flush=True)
        # --check must reach frontend startup; do not report backend-only success.
        # Full frontend is built while Java is stopped, using already patched source.
        front_env = frontend_environment(template, f"http://127.0.0.1:{port}")
        if not args.skip_build:
            build_frontend(template, frontend, front_env, reports, prepared=True)
        with ExitStack() as stack:
            base, _ = stack.enter_context(running_backend(template, backend, env, reports))
            frontend_url = stack.enter_context(
                frontend_preview(template, frontend, front_env, reports)
            )
            if args.check:
                # The first running_backend context has stopped its process. Verify
                # persisted rows through a newly authenticated, independently started
                # delivered backend before any second-process browser mutation.
                token = login(template, base)
                if manifest["plan"].get("business"):
                    from workbench.portable_checks import (
                        require_preserved_business_records,
                        snapshot_business_records,
                    )

                    after_restart = snapshot_business_records(
                        template, base, token, manifest["targets"], outcome["business"]
                    )
                    require_preserved_business_records(before_restart, after_restart)
                    outcome["restart_preserved_records"] = True
                    outcome["restart_records"] = after_restart
                    if template == "yudao-vben":
                        from workbench.domain import Plan
                        from workbench.yudao_navigation_checks import check_navigation_restart

                        outcome["business"]["installed_navigation_restart"] = (
                            check_navigation_restart(
                                template,
                                base,
                                token,
                                manifest["targets"],
                                outcome["business"],
                                Plan.model_validate(manifest["plan"]),
                            )
                        )
                outcome["restart"] = True
            if args.check and manifest["plan"].get("business"):
                from workbench.business_browser import run_business_browser
                from workbench.domain import Plan

                module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
                if not module:
                    raise ValueError("Business --check requires pinned local Playwright/Chromium")
                outcome["browser"] = run_business_browser(
                    template,
                    HERE / "business-browser.cjs",
                    frontend_url,
                    reports,
                    outcome["business"],
                    Plan.model_validate(manifest["plan"]),
                    module,
                )
            outcome["backend_port"] = port
            outcome["backend_url"] = base
            outcome["frontend_started"] = True
            write_json(reports / "portable-start.json", outcome)
            print(f"后端 {base}；前端 {frontend_url}；Ctrl+C停止，数据不会删除。", flush=True)
            if args.check:
                return
            while True:
                time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("已停止应用。数据库持久卷保留。")
````
