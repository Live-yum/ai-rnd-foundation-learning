# tests/test_capability_isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_identity_rejects_output_contamination_before_any_setup`（L33–L59）：接收`output`、`exit_code`、`shape`。 控制顺序：L49断言`evidence["control_output_shape"] == shape`；L50断言`evidence["control_result_chars"] == (len(output) if isinstance(output, str) else None…`；L51断言`"private-sentinel" not in json.dumps(evidence)`；L52断言`set(evidence) == { "control_exec_exit_code", "control_euid", "control_result_type", "…`；L59断言`len(calls) == 1`。 调用`SimpleNamespace`、`pytest.raises`、`prepare_identity`、`object`、`isinstance`、`len`、`json.dumps`、`set`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_rejects_output_contamination_before_any_setup.execute`（L38–L43）：接收`command`、`env`、`timeout`。 控制顺序：L40断言`len(calls) == 1`；L41断言`shlex.split(command)[-2:] == ["/usr/bin/id", "-u"]`；L42断言`env == CONTROL_SHELL_ENV and timeout == 10`。 调用`calls.append`、`len`、`shlex.split`、`SimpleNamespace`。 返回路径：L43的`SimpleNamespace(result=output, exit_code=exit_code)`。
- `test_exact_root_identity_progresses_to_setup_without_weaker_parsing`（L62–L77）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76断言`len(calls) == 2`；L77断言`"/usr/sbin/groupadd" in calls[1]`。 调用`SimpleNamespace`、`pytest.raises`、`prepare_identity`、`object`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_root_identity_progresses_to_setup_without_weaker_parsing.execute`（L67–L71）：接收`command`、`env`、`timeout`。 调用`calls.append`、`shlex.split`、`SimpleNamespace`、`len`。 返回路径：L69的`SimpleNamespace( result="0\n" if len(calls) == 1 else "", exit_code=0 if len(calls) == 1 e…`。
- `test_actual_sdk_env_protocol_prevents_outer_shell_contamination`（L81–L122）：接收`tmp_path`。 源码说明：Real SDK + subprocess protocol fixture, not the missing live CI output.。 控制顺序：L117断言`noisy.exit_code == 0`；L118断言`"setlocale" in noisy.result and "private-bootstrap-sentinel" in noisy.result`；L119断言`noisy.result.strip() != str(os.geteuid())`；L121断言`safe.exit_code == 0 and safe.result.strip() == str(os.geteuid())`；L122断言`requests[-1].envs == CONTROL_SHELL_ENV`。 调用`bootstrap.write_text`、`httpx.Client`、`Process`、`SimpleNamespace`、`sdk.exec`、`shlex.join`、`system_argv`、`noisy.result.strip`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sdk_env_protocol_prevents_outer_shell_contamination.execute_command`（L92–L111）：接收`request`、`**kwargs`。 调用`requests.append`、`subprocess.run`、`str`、`SimpleNamespace`。 返回路径：L109的`SimpleNamespace( result=result.stdout, exit_code=result.returncode, additional_properties=…`。
- `test_physical_count_probe_uses_same_outer_shell_environment`（L126–L148）：接收`engine`。 控制顺序：L143断言`database_counts(sandbox, plan, 10) == {"entries": 7}`；L144断言`len(calls) == (1 if engine == "sqlite" else 2)`；L145按`engine == "postgresql"`分支；L146断言`"rnd_verify" in calls[0][-1]`；L147断言`"postgres-verifier.json" in calls[0][-1]`；L148断言`"head" in " ".join(calls[1])`。 调用`SimpleNamespace`、`database_counts`、`len`、`" ".join`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_physical_count_probe_uses_same_outer_shell_environment.execute`（L132–L136）：接收`command`、`env`、`timeout`。 控制顺序：L134断言`env == CONTROL_SHELL_ENV and timeout == 10`；L135断言`calls[-1][:2] == ["/usr/bin/env", "-i"]`。 调用`calls.append`、`shlex.split`、`SimpleNamespace`。 返回路径：L136的`SimpleNamespace(exit_code=0, result='{"entries":7}' if engine == "sqlite" else "7\n")`。
- `test_generated_prepare_and_start_cannot_bypass_identity_or_network_guard`（L152–L186）：接收`database`。 控制顺序：L158断言`result[:2] == ["/usr/bin/env", "-i"]`；L159断言`"--reuid=rnd-module" in result and "--regid=rnd-module" in result`；L161断言`result[session : session + 4] == [ "/usr/bin/setsid", "--fork", "--wait", "/usr/bin/s…`；L167遍历`( "--clear-groups", "--no-new-privs", "--bounding-set=-all", "--i…`；L174断言`flag in result`；L176断言`result[index : index + 6] == [ "/usr/bin/python3", "-I", "-S", "/tmp/rnd-module-contr…`；L184断言`result[-len(command) :] == command`；L185断言`result.index("--") < index`。后续分支沿下方源码相同行号继续阅读。 调用`SimpleNamespace`、`product_argv`、`result.index`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_product_cannot_allow_its_control_or_database_listener`（L190–L195）：接收`port`。 调用`SimpleNamespace`、`pytest.raises`、`product_argv`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_isolation_receipt_requires_each_field_actual_abi_and_current_guard_digest`（L198–L224）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L215断言`require_isolation_evidence(value) == value`；L216遍历`list(value)`；L220遍历`[True, 5, "6"]`。 调用`sha`、`dict.fromkeys`、`require_isolation_evidence`、`list`、`value.items`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_detached_session_waits_for_ordinary_command_and_preserves_exit`（L229–L249）：接收`tmp_path`、`exit_code`。 控制顺序：L248断言`result.returncode == exit_code`；L249断言`completed.read_text(encoding="utf-8") == "completed"`。 调用`subprocess.run`、`str`、`completed.read_text`、`pytest.mark.skipif`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_container_receipt_requires_current_sandbox_and_all_boundaries`（L252–L275）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L268断言`require_container_evidence(value, identifier) == value`；L269遍历`value`。 调用`require_container_evidence`、`pytest.raises`、`value.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_container_inspection_failure_stops_before_source_upload`（L279–L324）：接收`settings`、`tmp_path`、`unknown_error`。 控制顺序：L321断言`result["passed"] is False and result["cleanup"] == "deleted"`；L322断言`result["kind"] == "isolation_environment" and operations == ["deleted"]`；L323断言`result["isolation_diagnostic"] == {}`；L324断言`"must-not-leak" not in json.dumps(result) and "private/path" not in json.dumps(result…`。 调用`fixed_application`、`SimpleNamespace`、`operations.append`、`_verify`、`plan.selection.model_dump`、`profile_record`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_container_inspection_failure_stops_before_source_upload.forbidden`（L289–L290）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_container_inspection_failure_stops_before_source_upload.observer`（L292–L298）：接收`_`。 控制顺序：L293按`unknown_error`分支；L297抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L298的`{}`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths`（L371–L632）：接收`settings`、`tmp_path`、`monkeypatch`、`failure`、`secure_execution`。 源码说明：Real HTTPX lifecycle with transport/process fixtures, not live isolation proof.。 控制顺序：L383按`failure in STARTUP_FAILURE_FIXTURES`分支；L487遍历`("prepare_readonly_dependencies", "verify_readonly_dependencies")`；L566断言`result["passed"] is (failure is None)`；L567断言`result["restarted"] is (failure is None)`；L568断言`result["cleanup"] == ("delete-failed" if failure == "browser-cleanup" else "deleted")`；L569断言`events[-1] == "deleted"`；L570断言`len(clients) == ( 1 if failure in {"baseline", "initial", *BROWSER_FAILURE_FIXTURES, …`；L576断言`all(client.is_closed for client in clients)`。后续分支沿下方源码相同行号继续阅读。 调用`fixed_application`、`monkeypatch.setattr`、`clock.__setitem__`、`SimpleNamespace`、`events.append`、`iter`、`profile_record`、`container_binding`、`dependency_evidence`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.build_http`（L392–L412）：接收`**kwargs`。 控制顺序：L394断言`kwargs["headers"] == {"x-daytona-preview-token": "fixture-private-token"}`；L395断言`kwargs["trust_env"] is False and kwargs["follow_redirects"] is False`。 调用`len`、`original_client`、`httpx.MockTransport`、`clients.append`。 返回路径：L412的`client`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.build_http.respond`（L397–L408）：接收`request`。 控制顺序：L399断言`request.url.host == f"8123-{identifier}.proxy.localhost"`；L400按`failure == "startup-connect"`分支；L401抛异常，停止当前正常路径；L402按`failure == "startup-timeout"`分支；L403抛异常，停止当前正常路径；L404按`failure in STARTUP_FAILURE_FIXTURES`分支；L406按`failure == "restart-health" and launch == 1`分支；L407抛异常，停止当前正常路径。 调用`events.append`、`httpx.ConnectError`、`httpx.ReadTimeout`、`httpx.Response`、`RuntimeError`。 返回路径：L405的`httpx.Response(503)`；L408的`httpx.Response(200, json={"ok": True})`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.delete`（L429–L432）：接收`*args`、`**kwargs`。 控制顺序：L431按`failure == "browser-cleanup"`分支；L432抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.create`（L434–L447）：接收`parameters`、`**kwargs`。 控制顺序：L441断言`ordinary.auto_delete_interval == 0`；L442断言`parameters.auto_delete_interval > (2 * settings.tool_timeout) / 60`；L443断言`parameters.network_block_all is True`；L444断言`parameters.public is False`；L445断言`parameters.name.startswith("rnd-source-" if secure_execution else "rnd-capability-")`。 调用`params_for`、`parameters.name.startswith`。 返回路径：L447的`sandbox`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.stop`（L449–L451）：接收`*args`、`**kwargs`。 控制顺序：L450断言`sandbox.auto_delete_interval > 0`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.database_counts`（L461–L464）：接收`*args`。 控制顺序：L462按`failure == "baseline"`分支；L463抛异常，停止当前正常路径。 调用`CheckFailure`、`next`。 返回路径：L464的`{"entries": next(counts)}`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.run_scenarios`（L466–L471）：接收`http`、`scenarios`、`saved`、`after_restart`。 控制顺序：L468断言`http.get("/fixture-" + phase).status_code == 200`；L469按`failure == phase`分支；L470抛异常，停止当前正常路径。 调用`http.get`、`CheckFailure`。 返回路径：L471的`[{"phase": phase, "fixture_only": True}], {}`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.run_browser`（L473–L476）：接收`*args`。 控制顺序：L474按`failure in BROWSER_FAILURE_FIXTURES`分支；L475抛异常，停止当前正常路径。 调用`BrowserFailure`、`BROWSER_FAILURE_FIXTURES[failure].copy`。 返回路径：L476的`[{"fixture_only": True}]`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.control`（L493–L511）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L494按`"os.statvfs('/tmp')" in argv[-1]`分支；L495断言`timeout <= 5`；L497按`failure == "startup-probe-error"`分支；L498抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`、`SimpleNamespace`。 返回路径：L499的`SimpleNamespace( exit_code=1 if failure == "startup-probe-nonzero" else False if failure =…`；L511的`SimpleNamespace(exit_code=0)`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.startup_output`（L515–L521）：接收`sandbox`、`path`、`timeout`。 控制顺序：L516断言`path.startswith("/tmp/rnd-module-control/private/")`；L517断言`timeout <= 5`；L519按`failure == "startup-output-unavailable"`分支；L520抛异常，停止当前正常路径。 调用`path.startswith`、`events.append`、`RuntimeError`。 返回路径：L521的`"PermissionError: secret path, content and fixture-private-token"`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.fixed_browser`（L527–L529）：接收`*args`。 控制顺序：L528断言`not secure_execution`。 调用`run_browser`。 返回路径：L529的`run_browser(*args)`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.isolated_browser`（L531–L535）：接收`image`、`*args`。 控制顺序：L532断言`secure_execution`；L533断言`image == settings.capability_browser_image`。 调用`events.append`、`run_browser`。 返回路径：L535的`run_browser(*args)`。
- `test_verifier_closes_health_opened_http_clients_on_all_paths.security_probe`（L548–L550）：接收`*args`。 调用`events.append`。 返回路径：L550的`{"fixture_only": True}`。
- `test_nonaggregate_verifier_keeps_delete_on_stop_and_mandatory_cleanup`（L635–L668）：接收`settings`、`tmp_path`。 控制顺序：L666断言`calls == ["created", "deleted"]`；L667断言`result["passed"] is False`；L668断言`result["cleanup"] == "deleted"`。 调用`fixed_application`、`SimpleNamespace`、`calls.append`、`_verify`、`plan.selection.model_dump`、`profile_record`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonaggregate_verifier_keeps_delete_on_stop_and_mandatory_cleanup.create`（L645–L649）：接收`parameters`、`**kwargs`。 控制顺序：L646断言`parameters.auto_delete_interval == 0`；L647断言`parameters.network_block_all is True and parameters.public is False`。 调用`calls.append`。 返回路径：L649的`sandbox`。

</details>

**创建路径：** `tests/test_capability_isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L668。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26450`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "181b2a0a1c752c4d7d7de68d4fbaf49c14628b4e9d1dee49664c3ae88859e7a4"} -->
````python
# tests/test_capability_isolation.py
"""Verify every source command is composed through the same non-bypassable launcher."""

import json
import os
import shlex
import subprocess
import sys
from types import SimpleNamespace

import pytest
from capability_dependency_fixtures import container_binding, dependency_evidence, profile_record

from workbench.capability_isolation import IsolationUnavailable, product_argv


@pytest.mark.parametrize(
    "output,exit_code,shape",
    [
        ("warning: setlocale: private-sentinel\n0\n", 0, "locale-warning"),
        ("private-sentinel\n0\n", 0, "other"),
        ("", 0, "empty"),
        (None, 0, "empty"),
        (b"0\n", 0, "empty"),
        (0, 0, "empty"),
        ("1000\n", 0, "decimal"),
        ("0\n", 7, "decimal"),
        ("0\n", False, "decimal"),
        ("0\n", "0", "decimal"),
        ("0\n0\n", 0, "other"),
        ("\x1b[0m0\n", 0, "other"),
    ],
)
def test_identity_rejects_output_contamination_before_any_setup(output, exit_code, shape):
    from workbench.capability_isolation import CONTROL_SHELL_ENV, prepare_identity

    calls = []

    def execute(command, *, env, timeout):
        calls.append((command, env, timeout))
        assert len(calls) == 1, "No setup or application command after failed identity"
        assert shlex.split(command)[-2:] == ["/usr/bin/id", "-u"]
        assert env == CONTROL_SHELL_ENV and timeout == 10
        return SimpleNamespace(result=output, exit_code=exit_code)

    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    with pytest.raises(IsolationUnavailable) as caught:
        prepare_identity(sandbox, object(), 10)
    evidence = caught.value.evidence
    assert evidence["control_output_shape"] == shape
    assert evidence["control_result_chars"] == (len(output) if isinstance(output, str) else None)
    assert "private-sentinel" not in json.dumps(evidence)
    assert set(evidence) == {
        "control_exec_exit_code",
        "control_euid",
        "control_result_type",
        "control_result_chars",
        "control_output_shape",
    }
    assert len(calls) == 1


def test_exact_root_identity_progresses_to_setup_without_weaker_parsing():
    from workbench.capability_isolation import prepare_identity

    calls = []

    def execute(command, *, env, timeout):
        calls.append(shlex.split(command))
        return SimpleNamespace(
            result="0\n" if len(calls) == 1 else "", exit_code=0 if len(calls) == 1 else 1
        )

    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    with pytest.raises(IsolationUnavailable, match="无法建立"):
        prepare_identity(sandbox, object(), 10)
    assert len(calls) == 2
    assert "/usr/sbin/groupadd" in calls[1]


@pytest.mark.skipif(os.name != "posix", reason="Pinned daemon shell fixture requires POSIX bash")
def test_actual_sdk_env_protocol_prevents_outer_shell_contamination(tmp_path):
    """Real SDK + subprocess protocol fixture, not the missing live CI output."""
    import httpx
    from daytona._sync.process import Process

    from workbench.capability_isolation import CONTROL_SHELL_ENV, control_exec, system_argv

    bootstrap = tmp_path / "fixture-bootstrap.sh"
    bootstrap.write_text("printf 'private-bootstrap-sentinel\\n'\n", encoding="utf-8")
    requests = []

    def execute_command(*, request, **kwargs):
        requests.append(request)
        result = subprocess.run(
            ["/bin/bash"],
            input=request.command,
            env={
                "PATH": os.defpath,
                "LC_ALL": "rnd_nonexistent_locale.UTF-8",
                "BASH_ENV": str(bootstrap),
                **(request.envs or {}),
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
            check=False,
        )
        return SimpleNamespace(
            result=result.stdout, exit_code=result.returncode, additional_properties={}
        )

    with httpx.Client(trust_env=False) as client:
        sdk = Process("python", SimpleNamespace(execute_command=execute_command), client)
        sandbox = SimpleNamespace(process=sdk)
        noisy = sdk.exec(shlex.join(system_argv(["/usr/bin/id", "-u"])), timeout=10)
        assert noisy.exit_code == 0
        assert "setlocale" in noisy.result and "private-bootstrap-sentinel" in noisy.result
        assert noisy.result.strip() != str(os.geteuid())
        safe = control_exec(sandbox, ["/usr/bin/id", "-u"], 10)
        assert safe.exit_code == 0 and safe.result.strip() == str(os.geteuid())
        assert requests[-1].envs == CONTROL_SHELL_ENV


@pytest.mark.parametrize("engine", ["sqlite", "postgresql"])
def test_physical_count_probe_uses_same_outer_shell_environment(engine):
    from workbench.capability_isolation import CONTROL_SHELL_ENV
    from workbench.capability_stack import database_counts

    calls = []

    def execute(command, *, env, timeout):
        calls.append(shlex.split(command))
        assert env == CONTROL_SHELL_ENV and timeout == 10
        assert calls[-1][:2] == ["/usr/bin/env", "-i"]
        return SimpleNamespace(exit_code=0, result='{"entries":7}' if engine == "sqlite" else "7\n")

    plan = SimpleNamespace(
        selection=SimpleNamespace(database=engine),
        runtime=SimpleNamespace(database_tables=["entries"], database_path="data/app.db"),
    )
    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    assert database_counts(sandbox, plan, 10) == {"entries": 7}
    assert len(calls) == (1 if engine == "sqlite" else 2)
    if engine == "postgresql":
        assert "rnd_verify" in calls[0][-1]
        assert "postgres-verifier.json" in calls[0][-1]
        assert "head" in " ".join(calls[1])


@pytest.mark.parametrize("database", ["sqlite", "postgresql"])
def test_generated_prepare_and_start_cannot_bypass_identity_or_network_guard(database):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=8123), selection=SimpleNamespace(database=database)
    )
    command = ["/bin/sh", "-c", "sudo -n id; curl http://127.0.0.1:2280/process/execute"]
    result = product_argv(plan, command, {"DATABASE_URL": "synthetic-only"})
    assert result[:2] == ["/usr/bin/env", "-i"]
    assert "--reuid=rnd-module" in result and "--regid=rnd-module" in result
    session = result.index("/usr/bin/setsid")
    assert result[session : session + 4] == [
        "/usr/bin/setsid",
        "--fork",
        "--wait",
        "/usr/bin/setpriv",
    ]
    for flag in (
        "--clear-groups",
        "--no-new-privs",
        "--bounding-set=-all",
        "--inh-caps=-all",
        "--ambient-caps=-all",
    ):
        assert flag in result
    index = result.index("/usr/bin/python3")
    assert result[index : index + 6] == [
        "/usr/bin/python3",
        "-I",
        "-S",
        "/tmp/rnd-module-control/guard.py",
        "8123",
        "55432" if database == "postgresql" else "",
    ]
    assert result[-len(command) :] == command
    assert result.index("--") < index
    assert result[index + 6] == "--"


@pytest.mark.parametrize("port", [2280, 55432])
def test_product_cannot_allow_its_control_or_database_listener(port):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=port), selection=SimpleNamespace(database="sqlite")
    )
    with pytest.raises(IsolationUnavailable):
        product_argv(plan, ["echo", "should-not-run"], {})


def test_isolation_receipt_requires_each_field_actual_abi_and_current_guard_digest():
    from workbench.capability_isolation import (
        APP_UID,
        ISOLATION_FLAGS,
        ISOLATION_PROFILE,
        require_isolation_evidence,
    )
    from workbench.filesystem import sha
    from workbench.settings import ROOT

    value = {
        "profile": ISOLATION_PROFILE,
        "application_uid": APP_UID,
        "landlock_abi": 6,
        "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
        **dict.fromkeys(ISOLATION_FLAGS, True),
    }
    assert require_isolation_evidence(value) == value
    for key in list(value):
        missing = {k: v for k, v in value.items() if k != key}
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence(missing)
    for invalid in [True, 5, "6"]:
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence({**value, "landlock_abi": invalid})
    with pytest.raises(IsolationUnavailable):
        require_isolation_evidence({**value, "guard_sha256": "0" * 64})


@pytest.mark.skipif(os.name != "posix", reason="Linux executor profile uses util-linux setsid")
@pytest.mark.parametrize("exit_code", [0, 7])
def test_detached_session_waits_for_ordinary_command_and_preserves_exit(tmp_path, exit_code):
    completed = tmp_path / "completed.txt"
    result = subprocess.run(
        [
            "/usr/bin/setsid",
            "--fork",
            "--wait",
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import pathlib,sys,time;time.sleep(0.05);pathlib.Path(sys.argv[1]).write_text('completed',encoding='utf-8');raise SystemExit(int(sys.argv[2]))",
            str(completed),
            str(exit_code),
        ],
        capture_output=True,
        timeout=5,
        start_new_session=True,
    )
    assert result.returncode == exit_code
    assert completed.read_text(encoding="utf-8") == "completed"


def test_container_receipt_requires_current_sandbox_and_all_boundaries():
    from workbench.capability_isolation import require_container_evidence

    identifier = "00000000-0000-0000-0000-000000000001"
    value = {
        "profile": "fixed-authored-sqlite-v1",
        "sandbox_id": identifier,
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
        "runner_image_id": "sha256:" + "0" * 64,
        "snapshot_image_id": "sha256:" + "1" * 64,
        "snapshot_digest": "registry:6000/rnd-python@sha256:" + "2" * 64,
    }
    assert require_container_evidence(value, identifier) == value
    for key in value:
        with pytest.raises(IsolationUnavailable):
            require_container_evidence({k: v for k, v in value.items() if k != key}, identifier)
    with pytest.raises(IsolationUnavailable):
        require_container_evidence(value, None)
    with pytest.raises(IsolationUnavailable):
        require_container_evidence({**value, "privileged": True}, identifier)


@pytest.mark.parametrize("unknown_error", [False, True])
def test_live_container_inspection_failure_stops_before_source_upload(
    settings, tmp_path, unknown_error
):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_sandbox import _verify

    product = tmp_path / "product"
    plan = fixed_application(product)
    operations = []

    def forbidden(*args, **kwargs):
        pytest.fail("No source upload or command before container policy verification")

    def observer(_):
        if unknown_error:
            error = ValueError("secret error /private/path TOKEN=must-not-leak")
            # An arbitrary provider exception cannot opt in to trusted evidence.
            error.evidence = {"container_rejection": "resource_limits", "TOKEN": "must-not-leak"}
            raise error
        return {}

    sandbox = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        fs=SimpleNamespace(create_folder=forbidden, upload_file=forbidden),
        process=SimpleNamespace(exec=forbidden),
    )
    client = SimpleNamespace(
        create=lambda *a, **k: sandbox, delete=lambda *a, **k: operations.append("deleted")
    )
    settings.daytona_snapshot = "fixture-owned-snapshot"
    result = _verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "receipt.json",
        client=client,
        aggregate=True,
        profile_record=profile_record(product),
        control_observer=observer,
    )
    assert result["passed"] is False and result["cleanup"] == "deleted"
    assert result["kind"] == "isolation_environment" and operations == ["deleted"]
    assert result["isolation_diagnostic"] == {}
    assert "must-not-leak" not in json.dumps(result) and "private/path" not in json.dumps(result)


BROWSER_FAILURE_FIXTURES = {
    "browser-launch": {"phase": "launch", "error_code": "operation-failed"},
    "browser-timeout": {"phase": "python-timeout", "error_code": "timeout", "cleanup": "stopped"},
    "browser-json": {
        "phase": "python-report",
        "error_code": "invalid-report",
        "report_error": "invalid-json",
    },
    "browser-head": {
        "phase": "python-report",
        "error_code": "invalid-report",
        "report_error": "wrong-verifier-or-request",
    },
    "browser-exit": {"phase": "python-exit", "error_code": "nonzero-exit", "exit_code": 1},
    "browser-cleanup": {"phase": "launch", "error_code": "operation-failed"},
}


STARTUP_FAILURE_FIXTURES = {
    "startup-status",
    "startup-connect",
    "startup-timeout",
    "startup-output-unavailable",
    "startup-probe-error",
    "startup-probe-nonzero",
    "startup-probe-malformed",
    "startup-probe-boolean",
    "startup-probe-executable",
}


@pytest.mark.parametrize(
    "failure",
    [
        None,
        "baseline",
        "initial",
        "restart-health",
        "restart",
        *BROWSER_FAILURE_FIXTURES,
        *sorted(STARTUP_FAILURE_FIXTURES),
    ],
)
@pytest.mark.parametrize("secure_execution", [False, True])
def test_verifier_closes_health_opened_http_clients_on_all_paths(
    settings, tmp_path, monkeypatch, failure, secure_execution
):
    """Real HTTPX lifecycle with transport/process fixtures, not live isolation proof."""
    import httpx

    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier
    from workbench.capability_verification import BrowserFailure, CheckFailure

    product = tmp_path / "product"
    plan = fixed_application(product)
    if failure in STARTUP_FAILURE_FIXTURES:
        plan.runtime.startup_seconds = 1
        clock = [0]
        monkeypatch.setattr(verifier.time, "monotonic", lambda: clock[0])
        monkeypatch.setattr(verifier.time, "sleep", lambda _: clock.__setitem__(0, clock[0] + 1))
    identifier = "00000000-0000-0000-0000-000000000001"
    events, clients = [], []
    original_client = httpx.Client

    def build_http(**kwargs):
        launch = len(clients)
        assert kwargs["headers"] == {"x-daytona-preview-token": "fixture-private-token"}
        assert kwargs["trust_env"] is False and kwargs["follow_redirects"] is False

        def respond(request):
            events.append((launch, request.url.path))
            assert request.url.host == f"8123-{identifier}.proxy.localhost"
            if failure == "startup-connect":
                raise httpx.ConnectError("secret transport path and token", request=request)
            if failure == "startup-timeout":
                raise httpx.ReadTimeout("secret transport path and token", request=request)
            if failure in STARTUP_FAILURE_FIXTURES:
                return httpx.Response(503)
            if failure == "restart-health" and launch == 1:
                raise RuntimeError("fixture health failure")
            return httpx.Response(200, json={"ok": True})

        client = original_client(**kwargs, transport=httpx.MockTransport(respond))
        clients.append(client)
        return client

    sandbox = SimpleNamespace(
        id=identifier,
        public=False,
        network_block_all=True,
        refresh_data=lambda: events.append("network-refreshed"),
        fs=SimpleNamespace(create_folder=lambda *a: None, upload_file=lambda *a, **k: None),
        process=SimpleNamespace(
            create_session=lambda *a: None,
            execute_session_command=lambda *a, **k: SimpleNamespace(cmd_id="fixture-command"),
        ),
        get_preview_link=lambda port: SimpleNamespace(
            url=f"http://{port}-{identifier}.proxy.localhost", token="fixture-private-token"
        ),
    )

    def delete(*args, **kwargs):
        events.append("deleted")
        if failure == "browser-cleanup":
            raise RuntimeError("fixture sandbox cleanup failure")

    def create(parameters, **kwargs):
        # Reproduce the pinned SDK's actual delete-on-stop parameter semantics.
        # An aggregate sandbox must survive both bounded lifecycle operations;
        # the ordinary disposable verifier policy must remain zero.
        from workbench.sandbox import params_for

        ordinary = params_for(settings, "fixture-ordinary")
        assert ordinary.auto_delete_interval == 0
        assert parameters.auto_delete_interval > (2 * settings.tool_timeout) / 60
        assert parameters.network_block_all is True
        assert parameters.public is False
        assert parameters.name.startswith("rnd-source-" if secure_execution else "rnd-capability-")
        sandbox.auto_delete_interval = parameters.auto_delete_interval
        return sandbox

    def stop(*args, **kwargs):
        assert sandbox.auto_delete_interval > 0, "Zero deletes the sandbox before restart"
        events.append("stopped")

    daytona = SimpleNamespace(
        create=create,
        stop=stop,
        start=lambda *a, **k: events.append("started"),
        delete=delete,
    )
    counts = iter([0, 1, 1])

    def database_counts(*args):
        if failure == "baseline":
            raise CheckFailure("fixture baseline failure")
        return {"entries": next(counts)}

    def run_scenarios(http, scenarios, *, saved=None, after_restart=False):
        phase = "restart" if after_restart else "initial"
        assert http.get("/fixture-" + phase).status_code == 200
        if failure == phase:
            raise CheckFailure("fixture scenario failure")
        return [{"phase": phase, "fixture_only": True}], {}

    def run_browser(*args):
        if failure in BROWSER_FAILURE_FIXTURES:
            raise BrowserFailure(BROWSER_FAILURE_FIXTURES[failure].copy())
        return [{"fixture_only": True}]

    admitted = profile_record(product)
    monkeypatch.setattr(
        verifier, "require_container_evidence", lambda *a: container_binding(admitted)
    )
    # Transport fixtures do not attest a real installed dependency tree. Keep
    # descriptor/launcher admission real and mock only remote verification.
    proof = dependency_evidence(
        admitted["snapshot"]["dependency_manifest"], verifier.manifest(product)
    )
    for name in ("prepare_readonly_dependencies", "verify_readonly_dependencies"):
        monkeypatch.setattr(
            "workbench.capability_dependencies." + name, lambda *a, **k: proof.copy()
        )
    monkeypatch.setattr(verifier, "prepare_identity", lambda *a: {"fixture_only": True})

    def control(sandbox, argv, timeout):
        if "os.statvfs('/tmp')" in argv[-1]:
            assert timeout <= 5
            events.append("tmpfs-mode-read")
            if failure == "startup-probe-error":
                raise RuntimeError("secret probe failure")
            return SimpleNamespace(
                exit_code=1
                if failure == "startup-probe-nonzero"
                else False
                if failure == "startup-probe-boolean"
                else 0,
                result="secret"
                if failure == "startup-probe-malformed"
                else "0\n"
                if failure == "startup-probe-executable"
                else "1\n",
            )
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(verifier, "control_exec", control)

    def startup_output(sandbox, path, timeout):
        assert path.startswith("/tmp/rnd-module-control/private/")
        assert timeout <= 5
        events.append("startup-output-read")
        if failure == "startup-output-unavailable":
            raise RuntimeError("secret private log path")
        return "PermissionError: secret path, content and fixture-private-token"

    monkeypatch.setattr(verifier, "read_command_output", startup_output)
    monkeypatch.setattr(verifier, "database_counts", database_counts)
    monkeypatch.setattr(verifier, "run_scenarios", run_scenarios)

    def fixed_browser(*args):
        assert not secure_execution, "Custom source must never fall back to host Chromium"
        return run_browser(*args)

    def isolated_browser(*args, image):
        assert secure_execution
        assert image == settings.capability_browser_image
        events.append("isolated-browser")
        return run_browser(*args)

    monkeypatch.setattr(verifier, "run_browser", fixed_browser)
    monkeypatch.setattr(
        "workbench.capability_browser_isolation.run_isolated_browser", isolated_browser
    )
    monkeypatch.setattr(verifier.httpx, "Client", build_http)
    monkeypatch.setattr(
        "workbench.daytona_sessions.run_session_command",
        lambda *a, **k: SimpleNamespace(exit_code=0),
    )
    settings.daytona_snapshot = "fixture-owned-snapshot"

    def security_probe(*args):
        events.append("security-probed")
        return {"fixture_only": True}

    try:
        result = verifier._verify(
            product,
            plan,
            plan.scenarios,
            settings,
            plan.selection.model_dump(),
            tmp_path / "receipt.json",
            client=daytona,
            aggregate=True,
            profile_record=admitted,
            control_observer=lambda _: {},
            security_probe=security_probe if secure_execution else None,
        )
        assert result["passed"] is (failure is None)
        assert result["restarted"] is (failure is None)
        assert result["cleanup"] == ("delete-failed" if failure == "browser-cleanup" else "deleted")
        assert events[-1] == "deleted"
        assert len(clients) == (
            1
            if failure
            in {"baseline", "initial", *BROWSER_FAILURE_FIXTURES, *STARTUP_FAILURE_FIXTURES}
            else 2
        )
        assert all(client.is_closed for client in clients)
        assert (0, "/health") in events
        persisted = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
        assert persisted == result
        if failure in STARTUP_FAILURE_FIXTURES:
            diagnostic = persisted["startup_diagnostic"]
            assert diagnostic["phase"] == "health_deadline"
            assert diagnostic["http_error"] == (
                "connect"
                if failure == "startup-connect"
                else "timeout"
                if failure == "startup-timeout"
                else "none"
            )
            assert diagnostic["http_status"] == (
                None if failure in {"startup-connect", "startup-timeout"} else 503
            )
            assert diagnostic["output_hints"] == (
                [] if failure == "startup-output-unavailable" else ["permission-denied"]
            )
            assert events.count("startup-output-read") == 1
            assert events.count("tmpfs-mode-read") == 1
            assert diagnostic["tmpfs_noexec"] is (
                False
                if failure == "startup-probe-executable"
                else None
                if failure.startswith("startup-probe-")
                else True
            )
            assert "secret" not in json.dumps(persisted)
            assert "fixture-private-token" not in json.dumps(persisted)
        else:
            assert "startup-output-read" not in events and "tmpfs-mode-read" not in events
            assert "startup_diagnostic" not in persisted
        if failure in BROWSER_FAILURE_FIXTURES:
            assert persisted["browser_diagnostic"] == BROWSER_FAILURE_FIXTURES[failure]
            assert "fixture-private-token" not in json.dumps(persisted)
            if failure == "browser-cleanup":
                assert persisted["error"] == "真实浏览器场景未通过；查看安全阶段诊断，未跳过"
                assert "删除未确认" in persisted["cleanup_error"]
        if failure is None:
            assert result["restart_kind"] == (
                "application_process" if secure_execution else "container"
            )
            if secure_execution:
                assert "stopped" not in events and "started" not in events
                assert events.count("security-probed") == 2
                assert result["restart_security_checks"] == result["security_checks"]
            else:
                assert "stopped" in events and "started" in events
            assert [check["phase"] for check in result["checks"]] == ["initial", "restart"]
            assert (0, "/openapi.json") in events
            assert (0, "/fixture-initial") in events and (1, "/fixture-restart") in events
            assert result["database"]["after_restart"] == {"entries": 1}
    finally:
        for client in clients:
            client.close()


def test_nonaggregate_verifier_keeps_delete_on_stop_and_mandatory_cleanup(settings, tmp_path):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_sandbox import _verify

    product = tmp_path / "product"
    plan = fixed_application(product)
    settings.daytona_snapshot = "fixture-owned-snapshot"
    sandbox = SimpleNamespace(id="00000000-0000-0000-0000-000000000001")
    calls = []

    def create(parameters, **kwargs):
        assert parameters.auto_delete_interval == 0
        assert parameters.network_block_all is True and parameters.public is False
        calls.append("created")
        return sandbox

    client = SimpleNamespace(create=create, delete=lambda *a, **k: calls.append("deleted"))
    result = _verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "receipt.json",
        client=client,
        aggregate=False,
        profile_record=profile_record(product),
        # Deliberately reject before source upload; this is a lifecycle contract
        # regression and supplies no live container or application evidence.
        control_observer=lambda identifier: {},
    )
    assert calls == ["created", "deleted"]
    assert result["passed"] is False
    assert result["cleanup"] == "deleted"
````
