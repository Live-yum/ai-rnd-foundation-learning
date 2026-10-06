"""Independent selected-language/framework and physical-database evidence.

This is a bounded runtime profile, not a model's claimed framework boolean.
Generated code remains inside Daytona; database probes use trusted system tools.
"""

import ast
import json
import re
import secrets
import shlex
from pathlib import PurePosixPath
from xml.etree import ElementTree

from workbench.capability_isolation import (
    CONTROL_SHELL_ENV,
    control_exec,
    run_guarded_control,
    system_argv,
)
from workbench.capability_verification import CheckFailure
from workbench.filesystem import inside, manifest

REMOTE = "/tmp/rnd-capability"
PG_BIN = "/usr/lib/postgresql/17/bin/"
PG_PORT = 55432
PG_ROOT = "/tmp/rnd-postgres"
PG_SOCKET = PG_ROOT + "/socket"
PG_VERIFIER_SECRET = "/tmp/rnd-module-control/private/postgres-verifier.json"


def inspect_stack(product, plan):
    selected = plan.selection.model_dump()
    argv = plan.runtime.start.argv
    command = PurePosixPath(argv[0]).name
    inventory = manifest(product)
    evidence = {"selection": selected, "source_checks": {}, "launcher": ""}
    if selected["backend"] in {"fastapi", "fastapiadmin"}:
        if command not in {"uv", "uvicorn", "python", "python3", "python3.14"} or not any(
            "uvicorn" == PurePosixPath(arg).name for arg in argv
        ):
            raise CheckFailure("所选FastAPI技术栈必须通过真实uvicorn入口运行")
        modules = [
            arg
            for arg in argv
            if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_.]*:[a-zA-Z_][a-zA-Z0-9_]*", arg)
        ]
        if len(modules) != 1:
            raise CheckFailure("FastAPI启动命令必须声明唯一ASGI模块入口")
        module, attribute = modules[0].split(":")
        base = PurePosixPath(plan.runtime.start.cwd) / module.replace(".", "/")
        entries = [str(base) + ".py", (base / "__init__.py").as_posix()]
        found_entries = [name for name in entries if name in inventory]
        if len(found_entries) != 1:
            raise CheckFailure("FastAPI入口不是本次产物源码")
        entry = found_entries[0]
        if selected["backend"] == "fastapiadmin":
            if (
                plan.runtime.start.cwd != "backend"
                or modules != ["app:create_app"]
                or "--factory" not in argv
                or entry != "backend/app/__init__.py"
            ):
                raise CheckFailure("FastapiAdmin必须保留原生app:create_app包工厂入口")
            entry_tree = ast.parse(inside(product, entry).read_text(encoding="utf-8"))
            if not any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == attribute
                for node in entry_tree.body
            ):
                raise CheckFailure("FastapiAdmin原生应用工厂不存在")
        evidence["source_checks"][entry] = inventory[entry]
        found = False
        for name in inventory:
            if not name.endswith(".py"):
                continue
            try:
                tree = ast.parse(inside(product, name).read_text(encoding="utf-8"))
            except SyntaxError:
                raise CheckFailure("自定义Python源码语法未通过") from None
            aliases = {
                item.asname or item.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module == "fastapi"
                for item in node.names
                if item.name == "FastAPI"
            }
            if any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in aliases
                for node in ast.walk(tree)
            ):
                found = True
                evidence["source_checks"][name] = inventory[name]
        if not found:
            raise CheckFailure("源码没有真实FastAPI应用构造，不能用另一框架冒充所选栈")
        evidence["launcher"] = "uvicorn"
    else:
        if command != "java" or "-jar" not in argv:
            raise CheckFailure("所选Java技术栈必须通过真实Java应用入口运行")
        poms = [name for name in inventory if name.endswith("pom.xml")]
        spring = False
        for name in poms:
            try:
                root = ElementTree.fromstring(inside(product, name).read_text(encoding="utf-8"))
            except ElementTree.ParseError:
                raise CheckFailure("Maven构建清单无效") from None
            if any(
                node.tag.endswith("groupId") and node.text == "org.springframework.boot"
                for node in root.iter()
            ):
                evidence["source_checks"][name] = inventory[name]
                spring = True
        if not spring:
            raise CheckFailure("所选Java/Spring技术栈缺少实际构建清单")
        evidence["launcher"] = "java"
    if selected["frontend"] in {"fastapiadmin-vue", "vben-antd"}:
        vue = False
        for name in inventory:
            if not name.endswith("package.json"):
                continue
            package = json.loads(inside(product, name).read_text(encoding="utf-8"))
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            if "vue" in deps:
                evidence["source_checks"][name] = inventory[name]
                vue = True
        if not vue or not any(name.endswith(".vue") for name in inventory):
            raise CheckFailure("所选Vue前端缺少Vue依赖和实际组件源码")
    return evidence


def database_environment(plan, password="", services=None):
    if plan.selection.database == "sqlite":
        url = "sqlite:///" + REMOTE + "/product/" + plan.runtime.database_path
        return {"PRODUCT_DATABASE_URL": url, "DATABASE_URL": url}
    if not password:
        raise CheckFailure("隔离PostgreSQL缺少专用应用身份")
    result = {
        "DATABASE_URL": f"postgresql+psycopg://rnd_app:{password}@127.0.0.1:{PG_PORT}/rnd_product",
        "SPRING_DATASOURCE_URL": f"jdbc:postgresql://127.0.0.1:{PG_PORT}/rnd_product",
        "SPRING_DATASOURCE_USERNAME": "rnd_app",
        "SPRING_DATASOURCE_PASSWORD": password,
    }
    if getattr(plan.selection, "template", "") == "fastapiadmin":
        from workbench.capability_services import REDIS_PORT

        if not services or not services.get("redis_password") or not services.get("session_key"):
            raise CheckFailure("FastapiAdmin缺少本次独立Redis和会话身份")
        result.update(
            {
                "ENVIRONMENT": "dev",
                "DATABASE_TYPE": "postgres",
                "DATABASE_HOST": "127.0.0.1",
                "DATABASE_PORT": str(PG_PORT),
                "DATABASE_USER": "rnd_app",
                "DATABASE_PASSWORD": password,
                "DATABASE_NAME": "rnd_product",
                "REDIS_HOST": "127.0.0.1",
                "REDIS_PORT": str(REDIS_PORT),
                "REDIS_USER": "rnd_app",
                "REDIS_PASSWORD": services["redis_password"],
                "REDIS_DB_NAME": "0",
                "SECRET_KEY": services["session_key"],
                "SERVER_HOST": "0.0.0.0",
                "SERVER_PORT": str(plan.runtime.port),
                "DEBUG": "False",
                "WORKERS": "1",
                "SCHEDULER_ALLOW_CODE_EXEC": "False",
                "DEMO_ENABLE": "False",
                "CAPTCHA_ENABLE": "True",
                "LOGIN_RATE_LIMIT_MAX_ATTEMPTS": "100",
                "OPENAI_API_KEY": "",
                "CI": "true",
                "HUSKY": "0",
                "NODE_OPTIONS": "--max-old-space-size=3072",
                "VITE_APP_TITLE": "Native extension",
                "VITE_VERSION": "3.0.0",
                "VITE_PORT": "5173",
                "VITE_BASE_URL": "/",
                "VITE_APP_BASE_API": "/api/v1",
                "VITE_API_BASE_URL": f"http://127.0.0.1:{plan.runtime.port}",
                "VITE_API_TIMEOUT": "120000",
                "VITE_ACCESS_MODE": "mixed",
                "VITE_WITH_CREDENTIALS": "false",
                "VITE_LOCK_ENCRYPT_KEY": "native-lab-only",
                "RND_OFFLINE_TOOLS": "1",
                "npm_config_store_dir": "/tmp/rnd-capability/pnpm-store",
            }
        )
    return result


def pg_control(argv):
    return [
        "/usr/sbin/runuser",
        "-u",
        "postgres",
        "--",
        *system_argv(["/usr/bin/env", "PGOPTIONS=-c search_path=pg_catalog", *argv]),
    ]


def prepare_database(sandbox, plan, timeout, *, restart=False, password=""):
    if plan.selection.database == "sqlite":
        return ""
    if not restart:
        for argv in (
            ["/usr/bin/mkdir", "-p", PG_SOCKET],
            ["/usr/bin/chown", "-R", "postgres:postgres", PG_ROOT],
            ["/usr/bin/chmod", "700", PG_ROOT, PG_SOCKET],
        ):
            if control_exec(sandbox, argv, timeout).exit_code:
                raise CheckFailure("无法建立独立PostgreSQL私有目录")
        command = [
            PG_BIN + "initdb",
            "-D",
            PG_ROOT + "/data",
            "--username=postgres",
            "--auth-local=peer",
            "--auth-host=scram-sha-256",
        ]
        if control_exec(sandbox, pg_control(command), timeout).exit_code:
            raise CheckFailure("独立PostgreSQL初始化失败")
    command = [
        PG_BIN + "pg_ctl",
        "-D",
        PG_ROOT + "/data",
        "-l",
        PG_ROOT + "/postgres.log",
        "-o",
        f"-h 127.0.0.1 -k {PG_SOCKET} -p {PG_PORT}",
        "-w",
        "start",
    ]
    if control_exec(sandbox, pg_control(command), timeout).exit_code:
        raise CheckFailure("独立PostgreSQL进程无法启动")
    if not restart:
        password = secrets.token_hex(24)
        verifier_password = secrets.token_hex(32)
        sandbox.fs.upload_file(
            json.dumps({"password": verifier_password}).encode(),
            PG_VERIFIER_SECRET,
            timeout=timeout,
        )
        if control_exec(sandbox, ["/usr/bin/chmod", "600", PG_VERIFIER_SECRET], timeout).exit_code:
            raise CheckFailure("无法保护独立数据库验证身份")
        command = [
            PG_BIN + "createdb",
            "-h",
            PG_SOCKET,
            "-p",
            str(PG_PORT),
            "-U",
            "postgres",
            "--owner=postgres",
            "rnd_product",
        ]
        if control_exec(sandbox, pg_control(command), timeout).exit_code:
            raise CheckFailure("无法建立非应用拥有的验证数据库")
        sql = f"CREATE ROLE rnd_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{password}'; CREATE ROLE rnd_verify LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{verifier_password}'; REVOKE CONNECT ON DATABASE postgres,template1 FROM PUBLIC; REVOKE ALL ON DATABASE rnd_product FROM PUBLIC; GRANT CONNECT,TEMPORARY ON DATABASE rnd_product TO rnd_app; REVOKE ALL ON SCHEMA public FROM PUBLIC; GRANT USAGE,CREATE ON SCHEMA public TO rnd_app; GRANT CONNECT ON DATABASE rnd_product TO rnd_verify; GRANT USAGE ON SCHEMA public TO rnd_verify; ALTER DEFAULT PRIVILEGES FOR ROLE rnd_app IN SCHEMA public GRANT SELECT ON TABLES TO rnd_verify;"
        command = [
            PG_BIN + "psql",
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-h",
            PG_SOCKET,
            "-p",
            str(PG_PORT),
            "-U",
            "postgres",
            "-d",
            "rnd_product",
            "-c",
            sql,
        ]
        if control_exec(sandbox, pg_control(command), timeout).exit_code:
            raise CheckFailure("无法建立最小应用数据库权限")
    return password


def database_counts(sandbox, plan, timeout):
    tables = plan.runtime.database_tables
    if plan.selection.database == "sqlite":
        script = """import sqlite3,json,sys,pathlib,urllib.parse
p=pathlib.Path(sys.argv[1]); root=pathlib.Path('/tmp/rnd-capability/product')
assert p.resolve().is_relative_to(root.resolve())
if not p.exists():
 print(json.dumps({t:0 for t in sys.argv[2:]})); sys.exit(0)
c=sqlite3.connect('file:'+urllib.parse.quote(str(p))+'?mode=ro',uri=True)
c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA query_only=ON')
names={r[0] for r in c.execute("select name,sql from sqlite_schema where type='table'") if (r[1] or '').lstrip().upper().startswith('CREATE TABLE')}
print(json.dumps({t:c.execute('SELECT count(*) FROM '+t).fetchone()[0] if t in names else 0 for t in sys.argv[2:]}))
"""
        argv = [
            "/usr/bin/env",
            "-i",
            "PATH=/usr/bin:/bin",
            "HOME=/nonexistent",
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            script,
            REMOTE + "/product/" + plan.runtime.database_path,
            *tables,
        ]
        result = sandbox.process.exec(
            shlex.join(argv), env=dict(CONTROL_SHELL_ENV), timeout=timeout
        )
        if result.exit_code != 0:
            raise CheckFailure("独立SQLite物理数据探针失败，不能接受应用自报存储成功")
        try:
            values = json.loads(result.result)
        except ValueError, TypeError:
            raise CheckFailure("独立SQLite探针未返回有效计数") from None
    else:
        values = {}
        for table in tables:
            # Table identifiers are constrained by the reviewed Pydantic contract.
            query = f"SELECT CASE WHEN pg_catalog.to_regclass('public.{table}') IS NULL THEN 0 WHEN (SELECT relkind='r' AND relpersistence='p' FROM pg_catalog.pg_class WHERE oid=pg_catalog.to_regclass('public.{table}')) THEN (pg_catalog.xpath('/row/c/text()',pg_catalog.query_to_xml('SELECT pg_catalog.count(*) AS c FROM public.{table}',false,true,'')))[1]::text::bigint ELSE -1 END"
            status, output = run_guarded_control(sandbox, pg_verifier_argv(query), timeout)
            if status != 0 or not re.fullmatch(r"\d+\s*", output or ""):
                raise CheckFailure("独立PostgreSQL物理数据探针失败，未采用模型声称的存储证据")
            values[table] = int(output.strip())
    if set(values) != set(tables) or any(type(v) is not int or v < 0 for v in values.values()):
        raise CheckFailure("物理数据库证据与批准表清单不一致")
    return values


def owned_database_identity(sandbox, timeout):
    # PostgreSQL JSON encodes oid as text; int8 preserves its full unsigned range.
    query = "SELECT pg_catalog.json_build_object('database',current_database(),'database_oid',(SELECT oid::pg_catalog.int8 FROM pg_catalog.pg_database WHERE datname=current_database()),'cluster',system_identifier::text,'directory',current_setting('data_directory')) FROM pg_catalog.pg_control_system()"
    argv = [
        PG_BIN + "psql",
        "-X",
        "-At",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        PG_SOCKET,
        "-p",
        str(PG_PORT),
        "-U",
        "postgres",
        "-d",
        "rnd_product",
        "-c",
        query,
    ]
    result = control_exec(sandbox, pg_control(argv), timeout)
    try:
        value = json.loads(result.result) if len(result.result) <= 4096 else None
    except ValueError, TypeError:
        value = None
    if (
        result.exit_code
        or not isinstance(value, dict)
        or set(value) != {"database", "database_oid", "cluster", "directory"}
        or value["database"] != "rnd_product"
        or value["directory"] != PG_ROOT + "/data"
        or type(value["database_oid"]) is not int
        or not re.fullmatch(r"[0-9]{1,30}", str(value["cluster"]))
    ):
        raise CheckFailure("私有临时数据库身份无法确认")
    return {**value, "sandbox_id": sandbox.id}


def recreate_owned_native_database(sandbox, plan, timeout, ownership):
    """Replace only this sandbox's disposable DB after the app UID is drained.

    The fixed name, private peer socket and postgres identity cannot be supplied
    by candidate code. Never call this against a configured external database.
    """
    if plan.selection.template != "fastapiadmin" or plan.selection.database != "postgresql":
        raise CheckFailure("只有独立原生PostgreSQL测试profile可重建本次临时数据库")
    from workbench.capability_sandbox import restart_application_identity

    restart_application_identity(sandbox, plan.runtime.port, timeout, extra_ports=(5173,))
    if owned_database_identity(sandbox, timeout) != ownership:
        raise CheckFailure("临时数据库/集群/沙箱身份发生变化，未执行重建")
    base = ["-h", PG_SOCKET, "-p", str(PG_PORT), "-U", "postgres"]
    commands = [
        [PG_BIN + "dropdb", *base, "rnd_product"],
        [PG_BIN + "createdb", *base, "--owner=postgres", "--template=template0", "rnd_product"],
        [
            PG_BIN + "psql",
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            *base,
            "-d",
            "rnd_product",
            "-c",
            "REVOKE ALL ON DATABASE rnd_product FROM PUBLIC; "
            "GRANT CONNECT,TEMPORARY ON DATABASE rnd_product TO rnd_app; "
            "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
            "GRANT USAGE,CREATE ON SCHEMA public TO rnd_app; "
            "GRANT CONNECT ON DATABASE rnd_product TO rnd_verify; "
            "GRANT USAGE ON SCHEMA public TO rnd_verify; "
            "ALTER DEFAULT PRIVILEGES FOR ROLE rnd_app IN SCHEMA public GRANT SELECT ON TABLES TO rnd_verify;",
        ],
    ]
    for command in commands:
        if control_exec(sandbox, pg_control(command), timeout).exit_code:
            raise CheckFailure("独立临时PostgreSQL重建失败，不能报告新库复测通过")
    current = owned_database_identity(sandbox, timeout)
    if (
        current["cluster"] != ownership["cluster"]
        or current["sandbox_id"] != ownership["sandbox_id"]
        or current["database_oid"] == ownership["database_oid"]
    ):
        raise CheckFailure("新库身份未在同一私有集群中改变")
    return current


PG_VERIFIER_EXEC = r"""
import json,os,pathlib,resource,sys
secret=pathlib.Path('/tmp/rnd-module-control/private/postgres-verifier.json')
assert secret.stat().st_size<1024 and secret.stat().st_uid==0 and secret.stat().st_mode&0o077==0
password=json.loads(secret.read_text())['password']
assert isinstance(password,str) and len(password)==64
resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
resource.setrlimit(resource.RLIMIT_CPU,(10,10))
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent','PGPASSWORD':password,
 'PGOPTIONS':'-c default_transaction_read_only=on -c search_path=pg_catalog -c statement_timeout=3000 -c lock_timeout=1000 -c row_security=off -c enable_indexscan=off -c enable_indexonlyscan=off -c enable_bitmapscan=off -c max_parallel_workers_per_gather=0'}
os.execve('/usr/lib/postgresql/17/bin/psql',['psql','-X','-q','-At','-v','ON_ERROR_STOP=1','-h','127.0.0.1','-p','55432','-U','rnd_verify','-d','rnd_product','-c',sys.argv[1]],env)
"""


def pg_verifier_argv(query):
    """Actual low-privilege authentication, never SET ROLE on an admin session."""
    if not isinstance(query, str) or len(query.encode()) > 32768:
        raise CheckFailure("数据库验证SQL超过控制端预算")
    return ["/usr/bin/python3", "-I", "-S", "-c", PG_VERIFIER_EXEC, query]
