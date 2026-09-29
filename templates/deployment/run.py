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
from workbench.native_frontend import build_frontend, frontend_environment, frontend_preview
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
    url, redis_port = services()
    marker, ready = ownership(url, manifest)
    if not ready and template == "yudao-vben":
        seed_yudao(url, backend)
    port = int(os.getenv("NATIVE_DELIVERY_PORT", "8001" if template == "fastapiadmin" else "48080"))
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
    reports = PRODUCT / ".deployment/reports"
    # Compile the new properties into the Java jar, or install the original Python lock.
    if not args.skip_build:
        install_backend(template, backend, reports)
    if not ready and template == "yudao-vben":
        apply_delivery_sql(url, manifest, marker)
    with running_backend(template, backend, env, reports) as (base, _):
        if not ready and template == "fastapiadmin":
            apply_delivery_sql(url, manifest, marker)
        token = login(template, base)
        from workbench.portable_checks import check_restored_product

        outcome = check_restored_product(
            template, base, token, manifest["targets"], manifest["plan"]
        )
        write_json(reports / "portable-start.json", outcome)
        print("数据库、业务表、菜单和新业务CRUD已就绪。", flush=True)
        if args.check:
            return
    # Full frontend is built while Java is stopped, using already patched source.
    front_env = frontend_environment(template, f"http://127.0.0.1:{port}")
    if not args.skip_build:
        build_frontend(template, frontend, front_env, reports, prepared=True)
    with ExitStack() as stack:
        base, _ = stack.enter_context(running_backend(template, backend, env, reports))
        frontend_url = stack.enter_context(frontend_preview(template, frontend, front_env, reports))
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
