# tests/test_capability_native_services.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_native_runtime`、`workbench.capability_services`、`workbench.capability_stack`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `plan`（L21–L43）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`、`RuntimeContract`、`TaskCommand`。 返回路径：L22的`SimpleNamespace( selection=Selection(template="fastapiadmin"), runtime=RuntimeContract( st…`。
- `test_native_environment_uses_only_passed_ephemeral_service_identities`（L46–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52断言`{ name: result[name] for name in ( "DATABASE_TYPE", "DATABASE_HOST", "DATABASE_PORT",…`；L70断言`result["REDIS_USER"] == "rnd_app" and result["REDIS_DB_NAME"] == "0"`；L71断言`result["REDIS_PORT"] == "55433" and result["REDIS_PASSWORD"] == "temporary-redis-pass…`；L74断言`result["SECRET_KEY"] == "temporary-jwt"`；L75断言`result["SCHEDULER_ALLOW_CODE_EXEC"] == "False"`；L76断言`result["OPENAI_API_KEY"] == ""`。 调用`database_environment`、`plan`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_redis_control_password_is_not_application_environment_or_command_line`（L81–L109）：接收`monkeypatch`。 控制顺序：L99断言`result == {"redis_password": "a" * 48, "session_key": "c" * 64}`；L100断言`"b" * 48 not in json.dumps(commands)`；L102断言`"bind 127.0.0.1" in config and "databases 1" in config`；L103断言`"user default off" in config and "-@admin -@dangerous -select" in config`；L104断言`"maxmemory 134217728" in config`；L105断言`any(argv[:3] == ["/usr/bin/chmod", "700", "/tmp/rnd-redis"] for argv in commands)`；L106断言`json.loads(uploads["/tmp/rnd-module-control/private/redis-control.json"])["password"]…`。 调用`iter`、`monkeypatch.setattr`、`next`、`commands.append`、`SimpleNamespace`、`uploads.__setitem__`、`prepare_native_services`、`plan`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_identity_checks_are_strict_and_source_bound`（L112–L142）：接收`monkeypatch`。 控制顺序：L131断言`verify_native_services(None, plan(), {}, 10) == { **expected, "postgres_verifier_role…`；L135遍历`( {**expected, "private_redis_control_denied": 1}, {}, {**expecte…`。 调用`compile`、`monkeypatch.setattr`、`json.dumps`、`argv[-1].startswith`、`SimpleNamespace`、`verify_native_services`、`plan`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_guard_ports_do_not_allow_daemon_or_unlisted_services`（L145–L151）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L148断言`argv[guard + 1] == "5173,8001"`；L149断言`argv[guard + 2] == "8001,55432,55433"`；L150断言`"2280" not in argv[guard + 1 : guard + 3]`；L151断言`"HOME=/tmp/rnd-capability/home" in argv`。 调用`product_argv`、`plan`、`argv.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_factory_disallows_launch_aliases_and_alternate_code`（L157–L169）：接收`mutate`。 控制顺序：L159断言`native_start_command(value) == value.runtime.start`；L160按`mutate == "app-dir"`分支；L162按`mutate == "alternate-factory"`分支；L164按`mutate == "alternate-interpreter"`分支。 调用`plan`、`native_start_command`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_mandatory_build_contains_install_build_and_typecheck`（L172–L178）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L174断言`len(commands) == 4`；L175断言`commands[0].argv[:4] == ["uv", "sync", "--locked", "--offline"]`；L176断言`"--frozen-lockfile" in commands[1].argv`；L177断言`commands[2].argv == ["pnpm", "exec", "vite", "build", "--mode", "production"]`；L178断言`commands[3].argv[:3] == ["pnpm", "exec", "vue-tsc"]`。 调用`native_prepare_commands`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_must_be_separately_authenticated_without_admin_session`（L184–L197）：接收`monkeypatch`、`identity`。 调用`monkeypatch.setattr`、`json.dumps`、`SimpleNamespace`、`pytest.raises`、`verify_native_services`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_subprocess_auth_secret_and_resource_bounds`（L200–L211）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L205断言`argv[-1] == "SELECT 1"`；L206断言`"'rnd_verify'" in PG_VERIFIER_EXEC`；L207断言`"PGPASSWORD" in PG_VERIFIER_EXEC and "postgres-verifier.json" in PG_VERIFIER_EXEC`；L208断言`"default_transaction_read_only=on" in PG_VERIFIER_EXEC`；L209断言`"enable_indexscan=off" in PG_VERIFIER_EXEC and "row_security=off" in PG_VERIFIER_EXEC`；L210断言`"RLIMIT_FSIZE,(65536,65536)" in PG_VERIFIER_EXEC`；L211断言`"SET ROLE" not in PG_VERIFIER_EXEC`。 调用`compile`、`pg_verifier_argv`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_services.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L211。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8088`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_services.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2c604c7eb160692fe34d45c3ad85544913fd86dd728f288dd859d1b040d1e2a9"} -->
````python
# tests/test_capability_native_services.py
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
````
