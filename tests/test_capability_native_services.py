"""Native service/runtime contracts, not proof of a running PostgreSQL or Redis."""

import json
from types import SimpleNamespace

import pytest

from workbench.capability_contracts import RuntimeContract, TaskCommand
from workbench.capability_isolation import product_argv
from workbench.capability_native_runtime import native_prepare_commands, native_start_command
from workbench.capability_services import (
    NATIVE_SERVICE_PROBE,
    prepare_native_services,
    verify_native_services,
)
from workbench.capability_stack import database_environment
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection


def plan():
    return SimpleNamespace(
        selection=Selection(template="fastapiadmin"),
        runtime=RuntimeContract(
            start=TaskCommand(
                cwd="backend",
                argv=[
                    ".venv/bin/python",
                    "-m",
                    "uvicorn",
                    "app:create_app",
                    "--factory",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                ],
            ),
            port=8001,
            database_tables=["rnd_device"],
            health_path="/openapi.json",
        ),
    )


def test_native_environment_uses_only_passed_ephemeral_service_identities():
    result = database_environment(
        plan(),
        "temporary-db-password",
        {"redis_password": "temporary-redis-password", "session_key": "temporary-jwt"},
    )
    assert {
        name: result[name]
        for name in (
            "DATABASE_TYPE",
            "DATABASE_HOST",
            "DATABASE_PORT",
            "DATABASE_USER",
            "DATABASE_PASSWORD",
            "DATABASE_NAME",
        )
    } == {
        "DATABASE_TYPE": "postgres",
        "DATABASE_HOST": "127.0.0.1",
        "DATABASE_PORT": "55432",
        "DATABASE_USER": "rnd_app",
        "DATABASE_PASSWORD": "temporary-db-password",
        "DATABASE_NAME": "rnd_product",
    }
    assert result["REDIS_USER"] == "rnd_app" and result["REDIS_DB_NAME"] == "0"
    assert (
        result["REDIS_PORT"] == "55433" and result["REDIS_PASSWORD"] == "temporary-redis-password"
    )
    assert result["SECRET_KEY"] == "temporary-jwt"
    assert result["SCHEDULER_ALLOW_CODE_EXEC"] == "False"
    assert result["OPENAI_API_KEY"] == ""
    with pytest.raises(CheckFailure, match="Redis"):
        database_environment(plan(), "temporary-db-password")


def test_private_redis_control_password_is_not_application_environment_or_command_line(monkeypatch):
    from workbench import capability_services as services

    tokens = iter(["a" * 48, "b" * 48, "c" * 64])
    monkeypatch.setattr(services.secrets, "token_hex", lambda size: next(tokens))
    commands, uploads = [], {}
    monkeypatch.setattr(
        services,
        "control_exec",
        lambda sandbox, argv, timeout: commands.append(argv) or SimpleNamespace(exit_code=0),
    )
    sandbox = SimpleNamespace(
        id="owned-sandbox",
        fs=SimpleNamespace(
            upload_file=lambda body, path, **kwargs: uploads.__setitem__(path, body)
        ),
    )
    result = prepare_native_services(sandbox, plan(), 30)
    assert result == {"redis_password": "a" * 48, "session_key": "c" * 64}
    assert "b" * 48 not in json.dumps(commands)
    config = uploads["/tmp/rnd-redis/redis.conf"].decode()
    assert "bind 127.0.0.1" in config and "databases 1" in config
    assert "user default off" in config and "-@admin -@dangerous -select" in config
    assert "maxmemory 134217728" in config
    assert any(argv[:3] == ["/usr/bin/chmod", "700", "/tmp/rnd-redis"] for argv in commands)
    assert (
        json.loads(uploads["/tmp/rnd-module-control/private/redis-control.json"])["password"]
        == "b" * 48
    )


def test_native_identity_checks_are_strict_and_source_bound(monkeypatch):
    import workbench.capability_services as services

    compile(NATIVE_SERVICE_PROBE, "<trusted-native-service-probe>", "exec")
    expected = {
        "postgres_application_role_restricted": True,
        "redis_owned_namespace_only": True,
        "private_redis_control_denied": True,
    }
    monkeypatch.setattr(services, "run_guarded_control", lambda *args: (0, json.dumps(expected)))
    monkeypatch.setattr(
        services,
        "control_exec",
        lambda sandbox, argv, timeout: (
            SimpleNamespace(exit_code=0, result="rnd_verify|rnd_verify|f|f|f|f|f")
            if argv[-1].startswith("SELECT current_user")
            else SimpleNamespace(exit_code=1, result="denied")
        ),
    )
    assert verify_native_services(None, plan(), {}, 10) == {
        **expected,
        "postgres_verifier_role_restricted": True,
    }
    for altered in (
        {**expected, "private_redis_control_denied": 1},
        {},
        {**expected, "model_claim": True},
    ):
        monkeypatch.setattr(services, "run_guarded_control", lambda *args: (0, json.dumps(altered)))
        with pytest.raises(CheckFailure):
            verify_native_services(None, plan(), {}, 10)


def test_native_guard_ports_do_not_allow_daemon_or_unlisted_services():
    argv = product_argv(plan(), ["/bin/true"], {})
    guard = argv.index("/tmp/rnd-module-control/guard.py")
    assert argv[guard + 1] == "5173,8001"
    assert argv[guard + 2] == "8001,55432,55433"
    assert "2280" not in argv[guard + 1 : guard + 3]
    assert "HOME=/tmp/rnd-capability/home" in argv


@pytest.mark.parametrize(
    "mutate", ["app-dir", "alternate-factory", "alternate-interpreter", "wrong-cwd"]
)
def test_native_factory_disallows_launch_aliases_and_alternate_code(mutate):
    value = plan()
    assert native_start_command(value) == value.runtime.start
    if mutate == "app-dir":
        value.runtime.start.argv += ["--app-dir", "/tmp/other"]
    elif mutate == "alternate-factory":
        value.runtime.start.argv[3] = "other:create_app"
    elif mutate == "alternate-interpreter":
        value.runtime.start.argv[0] = "uv"
    else:
        value.runtime.start.cwd = "."
    with pytest.raises(CheckFailure):
        native_start_command(value)


def test_native_mandatory_build_contains_install_build_and_typecheck():
    commands = native_prepare_commands()
    assert len(commands) == 4
    assert commands[0].argv[:4] == ["uv", "sync", "--locked", "--offline"]
    assert "--frozen-lockfile" in commands[1].argv
    assert commands[2].argv == ["pnpm", "exec", "vite", "build", "--mode", "production"]
    assert commands[3].argv[:3] == ["pnpm", "exec", "vue-tsc"]


@pytest.mark.parametrize(
    "identity", ["postgres|postgres|t|t|t|t|t", "rnd_verify|postgres|f|f|f|f|f"]
)
def test_verifier_must_be_separately_authenticated_without_admin_session(monkeypatch, identity):
    from workbench import capability_services as services

    checks = {
        "postgres_application_role_restricted": True,
        "redis_owned_namespace_only": True,
        "private_redis_control_denied": True,
    }
    monkeypatch.setattr(services, "run_guarded_control", lambda *a: (0, json.dumps(checks)))
    monkeypatch.setattr(
        services, "control_exec", lambda *a: SimpleNamespace(exit_code=0, result=identity)
    )
    with pytest.raises(CheckFailure, match="独立低权限"):
        verify_native_services(None, plan(), {}, 10)


def test_verifier_subprocess_auth_secret_and_resource_bounds():
    from workbench.capability_stack import PG_VERIFIER_EXEC, pg_verifier_argv

    compile(PG_VERIFIER_EXEC, "<trusted-pg-verifier>", "exec")
    argv = pg_verifier_argv("SELECT 1")
    assert argv[-1] == "SELECT 1"
    assert "'rnd_verify'" in PG_VERIFIER_EXEC
    assert "PGPASSWORD" in PG_VERIFIER_EXEC and "postgres-verifier.json" in PG_VERIFIER_EXEC
    assert "default_transaction_read_only=on" in PG_VERIFIER_EXEC
    assert "enable_indexscan=off" in PG_VERIFIER_EXEC and "row_security=off" in PG_VERIFIER_EXEC
    assert "RLIMIT_FSIZE,(65536,65536)" in PG_VERIFIER_EXEC
    assert "SET ROLE" not in PG_VERIFIER_EXEC
