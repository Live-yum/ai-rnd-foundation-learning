# workbench/postgres_lab.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：基础产品真实PostgreSQL验收环境。** checked_admin_url拒绝远程或能覆盖主机的参数。database在显式本机管理连接或本机Docker中创建独立测试数据库，并在上下文退出时清理本次资源；不连接云数据库。

**对应关系：** verification → 本机PG验收；test_guided_postgres。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.local_only`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `checked_admin_url`（L20–L24）：接收`value`。 控制顺序：L22按`url.get_backend_name() != "postgresql" or url.host not in {"127.0.0.1", "localhost", …`分支；L23抛异常，停止当前正常路径。 调用`make_url`、`local_database_url`、`url.get_backend_name`、`PrerequisiteError`。 返回路径：L24的`url`。
- `database`（L28–L108）：接收`settings`。 控制顺序：L33抛异常，停止当前正常路径；L43按`configured`分支；L47按`not docker`分支；L48抛异常，停止当前正常路径；L83遍历`range(60)`；L90按`attempt == 59`分支；L91抛异常，停止当前正常路径；L97按`created`分支。后续分支沿下方源码相同行号继续阅读。 调用`PrerequisiteError`、`settings.product_postgres_url.get_secret_value`、`os.getenv`、`uuid.uuid4`、`checked_admin_url`、`shutil.which`、`tempfile.TemporaryDirectory`、`Path`、`secrets.token_urlsafe`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/postgres_lab.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L108。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4177`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/postgres_lab.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "72a304fe35d7a30d5d4bd48eb081067af98c3284064dcc5aee64ef4b5a9f4e8f"} -->
````python
# workbench/postgres_lab.py
"""Disposable PostgreSQL databases for real product verification, not the user's target data."""

import json
import os
import secrets
import shutil
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.engine import make_url

from workbench.generator import PrerequisiteError
from workbench.local_only import local_database_url
from workbench.tools import run_command


def checked_admin_url(value):
    url = make_url(local_database_url(value))
    if url.get_backend_name() != "postgresql" or url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise PrerequisiteError("产品验收数据库必须是本机独立 PostgreSQL 服务")
    return url


@contextmanager
def database(settings):
    try:
        import psycopg
        from psycopg import sql
    except ImportError:
        raise PrerequisiteError(
            "PostgreSQL产品请先运行 uv sync --locked --extra postgres"
        ) from None
    configured = settings.product_postgres_url.get_secret_value() or os.getenv(
        "TEST_PRODUCT_DATABASE_URL", ""
    )
    container = None
    name = "rnd_verify_" + uuid.uuid4().hex
    created = False
    try:
        if configured:
            base = checked_admin_url(configured)
        else:
            docker = shutil.which("docker")
            if not docker:
                raise PrerequisiteError(
                    "已选 PostgreSQL 产品：需要 Docker Desktop，或在 .env 配置 PRODUCT_POSTGRES_URL 指向可创建测试库的本机开发服务"
                )
            container = "rnd-verify-" + uuid.uuid4().hex
            with tempfile.TemporaryDirectory(prefix="rnd-pg-") as temp:
                env = Path(temp) / "postgres.env"
                password = secrets.token_urlsafe(32)
                env.write_text(
                    f"POSTGRES_USER=rnd\nPOSTGRES_PASSWORD={password}\nPOSTGRES_DB=postgres\n",
                    encoding="utf-8",
                )
                env.chmod(0o600)
                run_command(
                    [
                        docker,
                        "run",
                        "-d",
                        "--name",
                        container,
                        "--env-file",
                        str(env),
                        "-p",
                        "127.0.0.1::5432",
                        "postgres:17",
                    ],
                    Path(temp),
                    180,
                )
            result = run_command(
                [docker, "inspect", container, "--format", "{{json .NetworkSettings.Ports}}"],
                settings.data_dir,
            )
            port = int(json.loads(result["log"])["5432/tcp"][0]["HostPort"])
            base = make_url(f"postgresql+psycopg://rnd:{password}@127.0.0.1:{port}/postgres")
        connection_url = base.set(drivername="postgresql").render_as_string(hide_password=False)
        for attempt in range(60):
            try:
                with psycopg.connect(connection_url, autocommit=True, connect_timeout=3) as c:
                    c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
                created = True
                break
            except psycopg.OperationalError:
                if attempt == 59:
                    raise PrerequisiteError(
                        "PostgreSQL验收服务未就绪；未更改任何已有业务库"
                    ) from None
                time.sleep(0.5)
        yield base.set(database=name).render_as_string(hide_password=False)
    finally:
        if created:
            try:
                with psycopg.connect(connection_url, autocommit=True, connect_timeout=5) as c:
                    c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
            except Exception:
                # Preserve main failure; the UUID makes the leftover test DB identifiable.
                pass
        if container:
            try:
                run_command(["docker", "rm", "-f", container], settings.data_dir, 30)
            except Exception:
                pass
````
