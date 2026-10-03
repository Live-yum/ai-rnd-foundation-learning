# workbench/capability_stack.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_isolation`、`workbench.capability_verification`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `inspect_stack`（L26–L107）：接收`product`、`plan`。 控制顺序：L32按`selected["backend"] in {"fastapi", "fastapiadmin"}`分支；L33按`command not in {"uv", "uvicorn", "python", "python3", "python3.14"} or not any( "uvic…`分支；L36抛异常，停止当前正常路径；L42按`len(modules) != 1`分支；L43抛异常，停止当前正常路径；L48按`entry not in inventory`分支；L49抛异常，停止当前正常路径；L51遍历`inventory`。后续分支沿下方源码相同行号继续阅读。 调用`plan.selection.model_dump`、`PurePosixPath`、`manifest`、`any`、`CheckFailure`、`re.fullmatch`、`len`、`( PurePosixPath(plan.runtime.start.cwd) / (modules[0].split(":")[…`、`modules[0].split(":")[0].replace`等。 返回路径：L107的`evidence`。
- `database_environment`（L110–L120）：接收`plan`、`password`。 控制顺序：L111按`plan.selection.database == "sqlite"`分支；L113按`not password`分支；L114抛异常，停止当前正常路径。 调用`CheckFailure`。 返回路径：L112的`{"DATABASE_URL": "sqlite:///" + REMOTE + "/product/" + plan.runtime.database_path}`；L115的`{ "DATABASE_URL": f"postgresql+psycopg://rnd_app:{password}@127.0.0.1:{PG_PORT}/rnd_produc…`。
- `pg_control`（L123–L130）：接收`argv`。 调用`system_argv`。 返回路径：L124的`[ "/usr/sbin/runuser", "-u", "postgres", "--", *system_argv(["/usr/bin/env", "PGOPTIONS=-c…`。
- `prepare_database`（L133–L201）：接收`sandbox`、`plan`、`timeout`、`restart`、`password`。 控制顺序：L134按`plan.selection.database == "sqlite"`分支；L136按`not restart`分支；L137遍历`( ["/usr/bin/mkdir", "-p", PG_SOCKET], ["/usr/bin/chown", "-R", "…`；L142按`control_exec(sandbox, argv, timeout).exit_code`分支；L143抛异常，停止当前正常路径；L152按`control_exec(sandbox, pg_control(command), timeout).exit_code`分支；L153抛异常，停止当前正常路径；L165按`control_exec(sandbox, pg_control(command), timeout).exit_code`分支。后续分支沿下方源码相同行号继续阅读。 调用`control_exec`、`CheckFailure`、`pg_control`、`secrets.token_hex`、`str`。 返回路径：L135的`""`；L201的`password`。
- `database_counts`（L204–L269）：接收`sandbox`、`plan`、`timeout`。 控制顺序：L206按`plan.selection.database == "sqlite"`分支；L233按`result.exit_code != 0`分支；L234抛异常，停止当前正常路径；L238抛异常，停止当前正常路径；L241遍历`tables`；L264按`result.exit_code != 0 or not re.fullmatch(r"\d+\s*", result.result or "")`分支；L265抛异常，停止当前正常路径；L267按`set(values) != set(tables) or any(type(v) is not int or v < 0 for v in values.values(…`分支。后续分支沿下方源码相同行号继续阅读。 调用`sandbox.process.exec`、`shlex.join`、`dict`、`CheckFailure`、`json.loads`、`str`、`control_exec`、`pg_control`、`re.fullmatch`等。 返回路径：L269的`values`。

</details>

**创建路径：** `workbench/capability_stack.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L269。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10972`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_stack.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "896642df20a86921f7b8bdf5950b04d6a85b0e12de0a55ab2dca2466c39e3ac4"} -->
````python
# workbench/capability_stack.py
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

from workbench.capability_isolation import CONTROL_SHELL_ENV, control_exec, system_argv
from workbench.capability_verification import CheckFailure
from workbench.filesystem import inside, manifest

REMOTE = "/tmp/rnd-capability"
PG_BIN = "/usr/lib/postgresql/17/bin/"
PG_PORT = 55432
PG_ROOT = "/tmp/rnd-postgres"
PG_SOCKET = PG_ROOT + "/socket"


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
        entry = (
            PurePosixPath(plan.runtime.start.cwd)
            / (modules[0].split(":")[0].replace(".", "/") + ".py")
        ).as_posix()
        if entry not in inventory:
            raise CheckFailure("FastAPI入口不是本次产物源码")
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


def database_environment(plan, password=""):
    if plan.selection.database == "sqlite":
        return {"DATABASE_URL": "sqlite:///" + REMOTE + "/product/" + plan.runtime.database_path}
    if not password:
        raise CheckFailure("隔离PostgreSQL缺少专用应用身份")
    return {
        "DATABASE_URL": f"postgresql+psycopg://rnd_app:{password}@127.0.0.1:{PG_PORT}/rnd_product",
        "SPRING_DATASOURCE_URL": f"jdbc:postgresql://127.0.0.1:{PG_PORT}/rnd_product",
        "SPRING_DATASOURCE_USERNAME": "rnd_app",
        "SPRING_DATASOURCE_PASSWORD": password,
    }


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
        sql = f"CREATE ROLE rnd_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{password}'; REVOKE ALL ON DATABASE rnd_product FROM PUBLIC; GRANT CONNECT,TEMPORARY ON DATABASE rnd_product TO rnd_app; REVOKE ALL ON SCHEMA public FROM PUBLIC; GRANT USAGE,CREATE ON SCHEMA public TO rnd_app;"
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
            argv = [
                PG_BIN + "psql",
                "-X",
                "-q",
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
                "-A",
                "-t",
                "-c",
                query,
            ]
            result = control_exec(sandbox, pg_control(argv), timeout)
            if result.exit_code != 0 or not re.fullmatch(r"\d+\s*", result.result or ""):
                raise CheckFailure("独立PostgreSQL物理数据探针失败，未采用模型声称的存储证据")
            values[table] = int(result.result.strip())
    if set(values) != set(tables) or any(type(v) is not int or v < 0 for v in values.values()):
        raise CheckFailure("物理数据库证据与批准表清单不一致")
    return values
````
