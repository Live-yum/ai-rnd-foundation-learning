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
from workbench.tools import run_command


def checked_admin_url(value):
    url = make_url(value)
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
