"""Loopback native lab lifecycle. Never resets existing databases or mocks authentication."""

import errno
import io
import json
import os
import re
import secrets
import shutil
import signal
import socket
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
from workbench.local_only import local_database_url
from workbench.tools import clean_env, process_options, run_command, stop_process


def checked_database(url):
    parsed = make_url(local_database_url(url))
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


def native_environment(template, backend, url, port, redis_port=6379, redis_database=None):
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
            "REDIS_DB_NAME": str(redis_database if redis_database is not None else 1),
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
        "spring.data.redis.database": str(redis_database if redis_database is not None else 2),
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


def prepare_fastapi_registry(backend, reports):
    """Use canonical PyPI URLs without changing any locked package version/hash."""
    import tomllib

    from workbench.filesystem import sha, write_json

    backend, reports = Path(backend), Path(reports)
    replacements = {
        "https://pypi.tuna.tsinghua.edu.cn/simple": "https://pypi.org/simple",
        "https://pypi.tuna.tsinghua.edu.cn/packages/": "https://files.pythonhosted.org/packages/",
    }
    receipt = {}
    for name in ("pyproject.toml", "uv.lock"):
        path = backend / name
        original = path.read_text(encoding="utf-8")
        before = sha(path)
        updated = original
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        # Parsing both documents detects malformed source. Only the literal,
        # known public mirror URLs can change; hashes and versions are retained.
        tomllib.loads(original)
        tomllib.loads(updated)
        if updated != original:
            atomic_text(path, updated)
        receipt[name] = {"before_sha256": before, "after_sha256": sha(path), "url_only": True}
    write_json(reports / "official-python-registry.json", receipt)
    return receipt


def install_backend(template, backend, reports, *, navigation_api_only=False):
    backend, reports = Path(backend), Path(reports)
    reports.mkdir(parents=True, exist_ok=True)
    if template == "fastapiadmin":
        prepare_fastapi_registry(backend, reports)
        commands = [["uv", "sync", "--locked", "--python", "3.14"]]
    else:
        from workbench.yudao_navigation import prepare_yudao_navigation

        prepare_yudao_navigation(backend, reports, api_only=navigation_api_only)
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
    if os.environ.get("RND_OFFLINE_TOOLS") == "1":
        commands = [
            command[:1] + (["-o"] if command[0] == "mvn" else []) + command[1:]
            for command in commands
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
            result = run_command(
                command, backend, 360, environment, heartbeat="native-backend-build"
            )
        except Exception as exc:
            logs.append(getattr(exc, "log", str(exc)))
            atomic_text(reports / "backend-build.log", "\n".join(logs))
            raise
        logs.append(result["log"])
    atomic_text(reports / "backend-build.log", "\n".join(logs))
    if template == "yudao-vben":
        verify_aggregate_jars(backend)


def loopback_port_bindable(port):
    """Observe bind availability without connecting to a possibly unowned service.

    Readiness probes must not allocate an outbound ephemeral socket to their own
    destination before the server listens (Linux permits such self-connections).
    SO_REUSEADDR matches server restart semantics on POSIX, including TIME_WAIT.
    This function never terminates a listener or changes host networking.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if os.name != "nt":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        elif hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            if error.errno in {errno.EADDRINUSE, errno.EACCES}:
                return False
            raise
    return True


def backend_port_state(port, group_pid):
    """Bounded Linux listener ownership, with no environment or process arguments.

    Unlike a bind/connect probe this cannot race with server startup. Other
    platforms retain their existing readiness behavior and report unobservable.
    """
    tcp = Path("/proc/net/tcp")
    if os.name != "posix" or not tcp.is_file():
        return {"observable": False}
    inodes, listener_inodes = set(), set()
    local_port_states = {}
    try:
        for path in (tcp, Path("/proc/net/tcp6")):
            if path.is_file():
                for line in path.read_text(encoding="utf-8").splitlines()[1:8193]:
                    parts = line.split()
                    if len(parts) > 9 and int(parts[1].rsplit(":", 1)[1], 16) == port:
                        inodes.add(parts[9])
                        local_port_states[parts[3]] = local_port_states.get(parts[3], 0) + 1
                        if parts[3] == "0A":
                            listener_inodes.add(parts[9])
        pids = []
        for path in list(Path("/proc").glob("[0-9]*/stat"))[:4096]:
            try:
                fields = path.read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
                if int(fields[2]) == group_pid and int(fields[3]) == group_pid:
                    pids.append(int(path.parent.name))
            except OSError, ValueError, IndexError:
                continue
        owners, socket_owners = set(), set()
        for pid in pids[:64]:
            for fd in list((Path("/proc") / str(pid) / "fd").glob("*"))[:2048]:
                try:
                    target = os.readlink(fd)
                except OSError:
                    continue
                if target.startswith("socket:[") and target[8:-1] in inodes:
                    socket_owners.add(pid)
                    if target[8:-1] in listener_inodes:
                        owners.add(pid)
        return {
            "observable": True,
            "listening": bool(listener_inodes),
            "owned_listener": bool(owners),
            "owned_listener_pids": sorted(owners),
            "owned_group_pids": sorted(pids[:64]),
            "owned_socket_pids": sorted(socket_owners),
            "local_port_state_counts": dict(sorted(local_port_states.items())),
        }
    except OSError, ValueError, IndexError:
        return {"observable": False}


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
        command = [
            "java",
            "-Xmx1400m",
            "-jar",
            str(jars[0]),
            "--spring.profiles.active=native",
            # Use current explicit native config even when a previously built jar
            # is reused; it includes both the listener and OpenFeign self URLs.
            "--spring.config.additional-location="
            + (backend / "yudao-server/src/main/resources/application-native.properties").as_uri(),
        ]
        openapi = "/v3/api-docs"
    base_url = f"http://127.0.0.1:{port}"
    if not loopback_port_bindable(port):
        raise RuntimeError(
            "Native backend port is already occupied; refusing to test another process"
        )
    attempt = 1
    previous = reports / "backend-lifecycle.json"
    if previous.is_file() and not previous.is_symlink() and previous.stat().st_size <= 16384:
        try:
            value = json.loads(previous.read_text(encoding="utf-8")).get("startup_attempt")
            if type(value) is int and 0 < value < 1_000_000:
                attempt = value + 1
        except OSError, ValueError, AttributeError:
            pass
    log = (reports / "backend-runtime.log").open("ab")
    log_start = log.tell()
    process = subprocess.Popen(
        command,
        cwd=backend,
        env=clean_env({"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", **env}),
        stdout=log,
        stderr=subprocess.STDOUT,
        **process_options(),
    )
    lifecycle = {
        "port": port,
        "pid": process.pid,
        "owned_process_group": True,
        "started": True,
        "startup_attempt": attempt,
        "runtime_log_start_bytes": log_start,
        "phase": "backend-readiness",
    }
    write_json(reports / "backend-lifecycle.json", lifecycle)
    failure = None
    try:
        with httpx.Client(trust_env=False, timeout=5) as client:
            for _ in range(90):
                if process.poll() is not None:
                    raise RuntimeError("Native backend exited; inspect backend-runtime.log")
                port_state = backend_port_state(port, process.pid)
                lifecycle["port_state"] = port_state
                if port_state.get("observable"):
                    if not port_state["listening"]:
                        time.sleep(2)
                        continue
                    if not port_state["owned_listener"]:
                        raise RuntimeError(
                            "Native backend port belongs to another process; refusing readiness"
                        )
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
        lifecycle["phase"] = "backend-running"
        write_json(reports / "backend-lifecycle.json", lifecycle)
        yield base_url, openapi
    except BaseException as error:
        failure = error
        lifecycle["failure"] = {"phase": lifecycle["phase"], "type": type(error).__name__}
        raise
    finally:
        cleanup_failure = None
        lifecycle["returncode_before_cleanup"] = process.poll()
        lifecycle["phase"] = "backend-cleanup"
        lifecycle["port_released"] = False
        try:
            lifecycle["port_state_before_cleanup"] = backend_port_state(port, process.pid)
            # An exited launcher may have left same-session descendants. Stop
            # only the still-observed group created by this context, never a
            # process discovered merely because it has acquired this port.
            state = lifecycle["port_state_before_cleanup"]
            if process.poll() is not None and state.get("owned_group_pids"):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            stop_process(process)
            deadline = time.monotonic() + 5
            released = loopback_port_bindable(port)
            while not released and time.monotonic() < deadline:
                time.sleep(0.1)
                released = loopback_port_bindable(port)
            lifecycle["port_released"] = released
            lifecycle["port_state_after_cleanup"] = backend_port_state(port, process.pid)
            if not released:
                raise RuntimeError(
                    "Native backend port remained occupied after owned-process cleanup"
                )
        except Exception as error:
            cleanup_failure = error
            lifecycle["cleanup_failure"] = {"type": type(error).__name__}
        finally:
            try:
                log.close()
            except Exception as error:
                cleanup_failure = cleanup_failure or error
                lifecycle.setdefault("cleanup_failure", {"type": type(error).__name__})
            lifecycle["returncode"] = process.poll()
            try:
                write_json(reports / "backend-lifecycle.json", lifecycle)
            except Exception as error:
                cleanup_failure = cleanup_failure or error
        if cleanup_failure is not None:
            if failure is None:
                raise cleanup_failure
            failure.add_note(
                "Native backend cleanup also failed "
                f"({type(cleanup_failure).__name__}, port_released={lifecycle['port_released']}); "
                "inspect backend-lifecycle.json"
            )


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
