"""Loopback native lab lifecycle. Never resets existing databases or mocks authentication."""

import io
import os
import re
import secrets
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile
from contextlib import contextmanager
from pathlib import Path

import httpx
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url

from workbench.filesystem import atomic_text, files, inside, sha, write_json
from workbench.tools import clean_env, process_options, run_command, stop_process


def checked_database(url):
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or parsed.host not in {"127.0.0.1", "localhost"}:
        raise ValueError("Native runtime requires a loopback PostgreSQL database")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,40}_codegen", parsed.database or ""):
        raise ValueError("Use a dedicated lowercase database identifier ending in _codegen")
    return parsed


def copy_source(source, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    for name, path in files(source):
        target = inside(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def bootstrap_database(template, backend, url):
    """Upstream seeds include DROP: execute ONLY in an empty dedicated development database."""
    parsed = checked_database(url)
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            for schema in inspector.get_schema_names():
                if schema == "information_schema" or schema.startswith("pg_"):
                    continue
                if (
                    inspector.get_table_names(schema=schema)
                    or inspector.get_view_names(schema=schema)
                    or inspector.get_sequence_names(schema=schema)
                ):
                    raise ValueError(
                        "Native bootstrap requires an EMPTY dedicated database; nothing was deleted"
                    )
        if template == "yudao-vben":
            import psycopg

            sql_path = Path(backend) / "sql/postgresql/ruoyi-vue-pro.sql"
            with psycopg.connect(
                parsed.set(drivername="postgresql").render_as_string(hide_password=False)
            ) as connection:
                connection.execute(sql_path.read_text(encoding="utf-8"))
    finally:
        engine.dispose()


def native_environment(template, backend, url, port, redis_port=6379):
    """Explicit local profile. External OAuth/WeChat features are not configured or tested."""
    parsed = checked_database(url)
    if not 1024 <= int(port) <= 65535:
        raise ValueError("Invalid native backend port")
    if template == "fastapiadmin":
        return {
            "ENVIRONMENT": "dev",
            "SERVER_HOST": "127.0.0.1",
            "SERVER_PORT": str(port),
            "DEBUG": "False",
            "WORKERS": "1",
            "DATABASE_TYPE": "postgres",
            "DATABASE_HOST": parsed.host,
            "DATABASE_PORT": str(parsed.port or 5432),
            "DATABASE_USER": parsed.username or "",
            "DATABASE_PASSWORD": parsed.password or "",
            "DATABASE_NAME": parsed.database,
            "REDIS_HOST": "127.0.0.1",
            "REDIS_PORT": str(redis_port),
            "REDIS_PASSWORD": "",
            "REDIS_DB_NAME": "1",
            "SECRET_KEY": secrets.token_hex(32),
            "CAPTCHA_ENABLE": "True",
            "SCHEDULER_ALLOW_CODE_EXEC": "False",
            "DEMO_ENABLE": "False",
            "LOGIN_RATE_LIMIT_MAX_ATTEMPTS": "100",
            "OPENAI_API_KEY": "",
            "PYTHONUTF8": "1",
            "UV_PYTHON": "3.14",
        }
    if template != "yudao-vben":
        raise ValueError("Unknown native template")
    resource = Path(backend) / "yudao-server/src/main/resources"
    properties = {
        "server.address": "127.0.0.1",
        "server.port": str(port),
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
        "spring.data.redis.host": "127.0.0.1",
        "spring.data.redis.port": str(redis_port),
        "spring.data.redis.database": "2",
        "xxl.job.enabled": "false",
        "yudao.security.mock-enable": "false",
        "yudao.captcha.enable": "false",
        "yudao.codegen.db-schemas": "public",
        "yudao.codegen.front-type": "40",
        "yudao.codegen.unit-test-enable": "false",
        "yudao.codegen.import-enable": "false",
        "spring.boot.admin.client.enabled": "false",
        "spring.cloud.nacos.discovery.enabled": "false",
        "spring.cloud.nacos.config.enabled": "false",
        "spring.cloud.sentinel.enabled": "false",
        "spring.cloud.openfeign.client.config.yudao-system.url": f"http://127.0.0.1:{port}",
        "spring.cloud.openfeign.client.config.yudao-infra.url": f"http://127.0.0.1:{port}",
        "spring.ai.vectorstore.qdrant.initialize-schema": "false",
        "management.endpoints.web.exposure.include": "health",
        "logging.file.name": "./logs/native-server.log",
        "yudao.access-log.enable": "false",
        "yudao.error-code.enable": "false",
        "wx.mp.app-id": "native-lab-disabled",
        "wx.mp.secret": "not-a-real-credential",
        "wx.miniapp.appid": "native-lab-disabled",
        "wx.miniapp.secret": "not-a-real-credential",
        "wx.mp.config-storage.type": "Memory",
        "wx.miniapp.config-storage.type": "Memory",
    }
    atomic_text(
        resource / "application-native.properties",
        "\n".join(f"{k}={v}" for k, v in properties.items()) + "\n",
    )
    return {
        "SPRING_PROFILES_ACTIVE": "native",
        "NATIVE_DB_USER": parsed.username or "",
        "NATIVE_DB_PASSWORD": parsed.password or "",
        "JAVA_HOME": os.environ.get("JAVA_HOME", ""),
    }


def prepare_yudao_postgres(backend, reports):
    """Declare the selected JDBC runtime in the copied aggregate POM."""
    pom = Path(backend) / "yudao-server/pom.xml"
    before = sha(pom)
    source = pom.read_text(encoding="utf-8")
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    dependencies = ET.fromstring(source).find("m:dependencies", ns)
    if dependencies is None:
        raise ValueError("The pinned aggregate POM has no dependency section")
    present = any(
        item.findtext("m:groupId", namespaces=ns) == "org.postgresql"
        and item.findtext("m:artifactId", namespaces=ns) == "postgresql"
        for item in dependencies
    )
    if not present:
        if source.count("<dependencies>") != 1:
            raise ValueError("Unexpected aggregate POM structure")
        declaration = "\n        <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>"
        atomic_text(pom, source.replace("<dependencies>", "<dependencies>" + declaration, 1))
    write_json(
        Path(reports) / "jdbc-configuration.json",
        {
            "path": "yudao-server/pom.xml",
            "before_sha256": before,
            "after_sha256": sha(pom),
            "driver": "org.postgresql",
        },
    )


def verify_aggregate_jars(backend):
    jar = Path(backend) / "yudao-server/target/yudao-server.jar"
    with zipfile.ZipFile(jar) as archive:
        for module in ("yudao-module-infra-server", "yudao-module-system-server"):
            matches = [
                name
                for name in archive.namelist()
                if name.startswith("BOOT-INF/lib/" + module) and name.endswith(".jar")
            ]
            if len(matches) != 1:
                raise ValueError("Aggregate is missing one native service dependency")
            with zipfile.ZipFile(io.BytesIO(archive.read(matches[0]))) as dependency:
                if any(name.startswith("BOOT-INF/classes/") for name in dependency.namelist()):
                    raise ValueError(
                        "Nested executable service jar cannot be used as a library dependency"
                    )
                if not any(
                    name.startswith("cn/iocoder/yudao/module/") and name.endswith(".class")
                    for name in dependency.namelist()
                ):
                    raise ValueError("Native dependency contains no loadable module classes")
        if not any(name.startswith("BOOT-INF/lib/postgresql-") for name in archive.namelist()):
            raise ValueError("PostgreSQL JDBC driver is absent from aggregate")


def install_backend(template, backend, reports):
    backend, reports = Path(backend), Path(reports)
    reports.mkdir(parents=True, exist_ok=True)
    if template == "fastapiadmin":
        commands = [["uv", "sync", "--python", "3.14"]]
    else:
        prepare_yudao_postgres(backend, reports)
        # The upstream POM lists distant public mirrors before Central. Use one
        # explicit public repository for repeatable dependency resolution, not
        # a runner-specific ~/.m2/settings.xml containing account credentials.
        maven_settings = reports / "maven-settings.xml"
        atomic_text(
            maven_settings,
            '<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">'
            "<mirrors><mirror><id>native-central</id><mirrorOf>*</mirrorOf>"
            "<url>https://repo.maven.apache.org/maven2</url></mirror></mirrors></settings>",
        )
        commands = [
            [
                "mvn",
                "-B",
                "-ntp",
                "-pl",
                "yudao-server",
                "-am",
                "install",
                "-DskipTests",
                "-Dspring-boot.repackage.skip=true",
            ],
            ["mvn", "-B", "-ntp", "-pl", "yudao-server", "package", "-DskipTests"],
        ]
    if template == "yudao-vben":
        commands = [
            command[:1]
            + [
                "-s",
                str(maven_settings.resolve()),
                "-Dmaven.wagon.http.retryHandler.count=2",
                "-Dmaven.wagon.rto=30000",
            ]
            + command[1:]
            for command in commands
        ]
    environment = {
        "JAVA_HOME": os.environ.get("JAVA_HOME", ""),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    if os.environ.get("UV_CACHE_DIR"):
        environment["UV_CACHE_DIR"] = os.environ["UV_CACHE_DIR"]
    logs = []
    for command in commands:
        try:
            result = run_command(command, backend, 1500, environment)
        except Exception as exc:
            logs.append(getattr(exc, "log", str(exc)))
            atomic_text(reports / "backend-build.log", "\n".join(logs))
            raise
        logs.append(result["log"])
    atomic_text(reports / "backend-build.log", "\n".join(logs))
    if template == "yudao-vben":
        verify_aggregate_jars(backend)


@contextmanager
def running_backend(template, backend, env, reports):
    backend, reports = Path(backend).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    if template == "fastapiadmin":
        executable = backend / (
            ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python"
        )
        port = int(env["SERVER_PORT"])
        command = [
            str(executable),
            "-m",
            "uvicorn",
            "app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
        openapi = "/openapi.json"
    else:
        properties = (
            backend / "yudao-server/src/main/resources/application-native.properties"
        ).read_text(encoding="utf-8")
        port = int(
            next(
                line.split("=", 1)[1]
                for line in properties.splitlines()
                if line.startswith("server.port=")
            )
        )
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
            raise RuntimeError(
                "Native backend port is already occupied; refusing to test another process"
            )
    log = (reports / "backend-runtime.log").open("ab")
    process = subprocess.Popen(
        command,
        cwd=backend,
        env=clean_env({"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", **env}),
        stdout=log,
        stderr=subprocess.STDOUT,
        **process_options(),
    )
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
                        raise RuntimeError(
                            "Native readiness redirected; check profile and API prefix"
                        )
                except httpx.HTTPError, ValueError:
                    pass
                time.sleep(2)
            else:
                raise TimeoutError(
                    "Native backend did not become ready; inspect backend-runtime.log"
                )
        yield base_url, openapi
    finally:
        stop_process(process)
        log.close()


def login(template, base_url, username=None, password=None):
    with httpx.Client(
        base_url=base_url, trust_env=False, timeout=30, headers={"tenant-id": "1"}
    ) as client:
        if template == "fastapiadmin":
            challenge = client.get("/system/auth/captcha/get")
            challenge.raise_for_status()
            key = challenge.json()["data"]["key"]
            time.sleep(0.3)
            completed = client.post(
                "/system/auth/captcha/slider/complete", json={"captcha_key": key}
            )
            completed.raise_for_status()
            if completed.json().get("code") not in (0, 200):
                raise RuntimeError("Native slider verification was rejected")
            response = client.post(
                "/system/auth/login",
                data={
                    "username": username or "super",
                    "password": password or "123456",
                    "captcha_key": key,
                },
            )
        else:
            response = client.post(
                "/admin-api/system/auth/login",
                json={"username": username or "admin", "password": password or "admin123"},
            )
        response.raise_for_status()
        body = response.json()
        if body.get("code", 200) not in (0, 200):
            raise RuntimeError(
                f"Native login rejected (code {body.get('code')}): {body.get('msg', '')}"
            )
        value = body.get("data", body)
        token = value.get("access_token", value.get("accessToken"))
        if not isinstance(token, str) or not token:
            raise RuntimeError("No native access token")
        return token
