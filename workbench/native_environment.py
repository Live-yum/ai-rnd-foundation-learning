"""Loopback native lab lifecycle. Never resets an existing database or mocks login."""

import os
import re
import secrets
import shutil
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url

from workbench.filesystem import atomic_text, files, inside, write_json
from workbench.tools import clean_env, process_options, run_command, stop_process


def checked_database(url):
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or parsed.host not in {"127.0.0.1", "localhost"}:
        raise ValueError("Native runtime requires a loopback PostgreSQL database")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,40}_codegen", parsed.database or ""):
        raise ValueError("Use a dedicated lowercase database identifier ending in _codegen")
    return parsed


def copy_source(source, destination):
    """Copy source only, never upstream environments, dependencies or credentials."""
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    for name, path in files(source):
        target = inside(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def bootstrap_database(template, backend, url):
    """YuDao seeds contain DROP statements: execute ONLY in an empty dedicated database."""
    parsed = checked_database(url)
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            if inspect(connection).get_table_names():
                raise ValueError("Native bootstrap requires an EMPTY dedicated database; nothing was deleted")
        if template == "yudao-vben":
            import psycopg

            sql_path = Path(backend) / "sql/postgresql/ruoyi-vue-pro.sql"
            with psycopg.connect(parsed.set(drivername="postgresql").render_as_string(hide_password=False)) as connection:
                connection.execute(sql_path.read_text(encoding="utf-8"))
    finally:
        engine.dispose()


def native_environment(template, backend, url, port, redis_port=6379):
    """Development-only profile; no model/API secrets inherited by native processes."""
    parsed = checked_database(url)
    if not 1024 <= int(port) <= 65535:
        raise ValueError("Invalid native backend port")
    if template == "fastapiadmin":
        return {
            "ENVIRONMENT": "dev", "SERVER_HOST": "127.0.0.1", "SERVER_PORT": str(port),
            "DEBUG": "False", "WORKERS": "1", "DATABASE_TYPE": "postgres",
            "DATABASE_HOST": parsed.host, "DATABASE_PORT": str(parsed.port or 5432),
            "DATABASE_USER": parsed.username or "", "DATABASE_PASSWORD": parsed.password or "",
            "DATABASE_NAME": parsed.database, "REDIS_HOST": "127.0.0.1",
            "REDIS_PORT": str(redis_port), "REDIS_PASSWORD": "", "REDIS_DB_NAME": "1",
            "SECRET_KEY": secrets.token_hex(32), "CAPTCHA_ENABLE": "False",
            "SCHEDULER_ALLOW_CODE_EXEC": "False", "DEMO_ENABLE": "False",
            "LOGIN_RATE_LIMIT_MAX_ATTEMPTS": "100", "OPENAI_API_KEY": "",
            "PYTHONUTF8": "1", "UV_PYTHON": "3.14",
        }
    if template != "yudao-vben":
        raise ValueError("Unknown native template")
    resource = Path(backend) / "yudao-server/src/main/resources"
    properties = {
        "server.address": "127.0.0.1", "server.port": str(port),
        "spring.datasource.dynamic.primary": "master",
        "spring.datasource.dynamic.datasource.master.url": f"jdbc:postgresql://{parsed.host}:{parsed.port or 5432}/{parsed.database}",
        "spring.datasource.dynamic.datasource.master.username": "${NATIVE_DB_USER}",
        "spring.datasource.dynamic.datasource.master.password": "${NATIVE_DB_PASSWORD}",
        "spring.datasource.dynamic.datasource.master.name": "public",
        "spring.datasource.dynamic.datasource.master.driver-class-name": "org.postgresql.Driver",
        "spring.datasource.dynamic.druid.initial-size": "1",
        "spring.datasource.dynamic.druid.min-idle": "1",
        "spring.datasource.dynamic.druid.max-active": "10",
        "spring.datasource.dynamic.druid.validation-query": "SELECT 1",
        "spring.data.redis.host": "127.0.0.1", "spring.data.redis.port": str(redis_port),
        "spring.data.redis.database": "2", "xxl.job.enabled": "false",
        "yudao.security.mock-enable": "false", "yudao.captcha.enable": "false",
        "yudao.codegen.db-schemas": "public", "yudao.codegen.front-type": "40",
        "yudao.codegen.unit-test-enable": "false", "yudao.codegen.import-enable": "false",
        "spring.boot.admin.client.enabled": "false", "spring.cloud.nacos.discovery.enabled": "false",
        "spring.cloud.nacos.config.enabled": "false", "spring.cloud.sentinel.enabled": "false",
        "spring.ai.vectorstore.qdrant.initialize-schema": "false",
        "management.endpoints.web.exposure.include": "health",
        "logging.file.name": "./logs/native-server.log",
        "yudao.access-log.enable": "false", "yudao.error-code.enable": "false",
    }
    atomic_text(resource / "application-native.properties", "\n".join(f"{k}={v}" for k, v in properties.items()) + "\n")
    return {"SPRING_PROFILES_ACTIVE": "native", "NATIVE_DB_USER": parsed.username or "",
            "NATIVE_DB_PASSWORD": parsed.password or "", "JAVA_HOME": os.environ.get("JAVA_HOME", "")}


def install_backend(template, backend, reports):
    backend, reports = Path(backend), Path(reports)
    reports.mkdir(parents=True, exist_ok=True)
    if template == "fastapiadmin":
        command = ["uv", "sync", "--python", "3.14"]
    else:
        command = ["mvn", "-B", "-ntp", "-pl", "yudao-server", "-am", "package", "-DskipTests"]
    environment = {"JAVA_HOME": os.environ.get("JAVA_HOME", ""), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    if os.environ.get("UV_CACHE_DIR"):
        environment["UV_CACHE_DIR"] = os.environ["UV_CACHE_DIR"]
    try:
        result = run_command(command, backend, 1500, environment)
    except Exception as exc:
        atomic_text(reports / "backend-build.log", getattr(exc, "log", str(exc)))
        raise
    atomic_text(reports / "backend-build.log", result["log"])


@contextmanager
def running_backend(template, backend, env, reports):
    backend, reports = Path(backend).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    if template == "fastapiadmin":
        executable = backend / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
        port = int(env["SERVER_PORT"])
        command = [str(executable), "-m", "uvicorn", "app:create_app", "--factory", "--host", "127.0.0.1", "--port", str(port)]
        openapi = "/openapi.json"
    else:
        properties = (backend / "yudao-server/src/main/resources/application-native.properties").read_text(encoding="utf-8")
        port = int(next(line.split("=", 1)[1] for line in properties.splitlines() if line.startswith("server.port=")))
        jars = list((backend / "yudao-server/target").glob("*.jar"))
        if len(jars) != 1:
            raise ValueError("Expected exactly one compiled native server jar")
        command = ["java", "-Xmx1400m", "-jar", str(jars[0]), "--spring.profiles.active=native"]
        openapi = "/v3/api-docs"
    base_url = f"http://127.0.0.1:{port}"
    with httpx.Client(trust_env=False, timeout=1) as client:
        try:
            client.get(base_url + openapi)
        except httpx.HTTPError:
            pass
        else:
            raise RuntimeError("Native backend port is already occupied; refusing to test another process")
    log = (reports / "backend-runtime.log").open("ab")
    process = subprocess.Popen(command, cwd=backend, env=clean_env({"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", **env}), stdout=log, stderr=subprocess.STDOUT, **process_options())
    try:
        with httpx.Client(trust_env=False, timeout=5) as client:
            for _ in range(90):
                if process.poll() is not None:
                    raise RuntimeError("Native backend exited; inspect backend-runtime.log")
                try:
                    response = client.get(base_url + openapi)
                    if response.status_code == 200 and "paths" in response.json():
                        write_json(reports / "openapi.json", response.json())
                        break
                    if response.is_redirect:
                        raise RuntimeError("Native readiness redirected; check the development profile and API prefix")
                except (httpx.HTTPError, ValueError):
                    pass
                time.sleep(2)
            else:
                raise TimeoutError("Native backend did not become ready; inspect backend-runtime.log")
        yield base_url, openapi
    finally:
        stop_process(process)
        log.close()


def login(template, base_url, username=None, password=None):
    with httpx.Client(base_url=base_url, trust_env=False, timeout=30, headers={"tenant-id": "1"}) as client:
        if template == "fastapiadmin":
            response = client.post("/system/auth/login", data={"username": username or "super", "password": password or "123456"})
        else:
            response = client.post("/admin-api/system/auth/login", json={"username": username or "admin", "password": password or "admin123"})
        response.raise_for_status()
        body = response.json()
        if body.get("code", 200) not in (0, 200):
            raise RuntimeError(f"Native login rejected (code {body.get('code')}): {body.get('msg', '')}")
        value = body.get("data", body)
        token = value.get("access_token", value.get("accessToken"))
        if not isinstance(token, str) or not token:
            raise RuntimeError("No native access token")
        return token
