# tests/test_daytona_startup_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.filesystem`、`workbench.generator`、`workbench.sandbox`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `local_compose`（L21–L27）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`atomic_text`、`json.dumps`。 返回路径：L27的`daytona_local`。
- `test_diagnostics_only_exact_owned_id_fixed_daemons_and_no_environment_dump`（L30–L67）：接收`tmp_path`、`settings`、`monkeypatch`。 控制顺序：L52断言`len(calls) == 3 and report["affects_acceptance"] is False`；L54遍历`[ "api-secret-sentinel", "local-password-sentinel", "hidden-token…`；L62断言`secret not in body`；L63断言`all( len(value["text"]) <= diagnostics.MAX_CHARS for value in report["diagnostics"].v…`；L66断言`"OOMKilled" in calls[0][calls[0].index("--format") + 1]`；L67断言`calls[-1][-3:] == ["tail", "--bytes=8192", "/tmp/daytona-daemon.log"]`。 调用`local_compose`、`SecretStr`、`monkeypatch.setattr`、`diagnostics.capture_startup`、`len`、`json.dumps`、`all`、`report["diagnostics"].values`、`calls[0].index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostics_only_exact_owned_id_fixed_daemons_and_no_environment_dump.command`（L37–L48）：接收`argv`、`cwd`、`timeout`。 控制顺序：L39断言`0 < timeout <= 5`；L40断言`argv[:2] == ["docker", "compose"]`；L41断言`"DOCKER_HOST=unix:///var/run/docker.sock" in argv`；L42断言`"runner" in argv and OWNED_ID in argv`；L43断言`"ps" not in argv and "Env" not in " ".join(argv)`。 调用`calls.append`、`" ".join`。 返回路径：L44的`{ "log": "x" * 10000 + " api-secret-sentinel local-password-sentinel Bearer hidden-token p…`。
- `test_diagnostics_cross_real_local_command_policy_with_fixed_inner_environment`（L70–L147）：接收`tmp_path`、`settings`、`monkeypatch`。 控制顺序：L83遍历`hostile.items()`；L135断言`len(calls) == len(waits) == 3`；L136遍历`zip(calls, expected_suffixes, strict=True)`；L137断言`argv == expected_prefix + suffix`；L138断言`options["shell"] is False`；L139断言`all(name not in options["env"] for name in hostile)`；L140断言`all(0 < timeout <= 5 for timeout in waits)`；L141断言`diagnostics.TOTAL_SECONDS == 15`。后续分支沿下方源码相同行号继续阅读。 调用`local_compose`、`SecretStr`、`hostile.items`、`monkeypatch.setenv`、`monkeypatch.setattr`、`diagnostics.capture_startup`、`str`、`len`、`zip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostics_cross_real_local_command_policy_with_fixed_inner_environment.Process`（L88–L97）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_diagnostics_cross_real_local_command_policy_with_fixed_inner_environment.Process.__init__`（L89–L93）：接收`argv`、`**kwargs`。 调用`calls.append`、`kwargs["stdout"].write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostics_cross_real_local_command_policy_with_fixed_inner_environment.Process.wait`（L95–L97）：接收`timeout`。 调用`waits.append`。 返回路径：L97的`0`。
- `test_diagnostics_fix_does_not_relax_general_docker_overrides`（L160–L165）：接收`argv`、`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`tools.run_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_identity_never_invokes_docker`（L176–L183）：接收`identifier`、`name`、`settings`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`diagnostics.capture_startup`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_fixed_compose_does_not_discover_other_installations`（L186–L198）：接收`tmp_path`、`settings`、`monkeypatch`。 控制顺序：L195断言`diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)["status"] == "fixed-local…`。 调用`monkeypatch.setattr`、`pytest.fail`、`diagnostics.capture_startup`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_errors_are_bounded_and_do_not_escape`（L201–L214）：接收`tmp_path`、`settings`、`monkeypatch`。 控制顺序：L211断言`len(report["diagnostics"]) == 3`；L212断言`all(row["status"] == "unavailable" for row in report["diagnostics"].values())`；L213断言`"hidden-secret" not in json.dumps(report)`；L214断言`"private exception" not in json.dumps(report)`。 调用`local_compose`、`monkeypatch.setattr`、`diagnostics.capture_startup`、`len`、`all`、`report["diagnostics"].values`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_errors_are_bounded_and_do_not_escape.fail`（L204–L207）：接收`*a`、`**kw`。 控制顺序：L207抛异常，停止当前正常路径。 调用`ToolFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup`（L220–L267）：接收`tmp_path`、`settings`、`monkeypatch`、`enabled`、`diagnostic_failure`。 控制顺序：L258断言`events == [ "create", "lookup-exact-name", *(["diagnostics"] if enabled else []), "de…`；L266断言`report["passed"] is False and report["cleanup"] == "deleted"`；L267断言`report["sandbox_id"] == OWNED_ID and "must-not-leak-private-exception" not in body`。 调用`product.mkdir`、`atomic_text`、`SecretStr`、`monkeypatch.setattr`、`pytest.raises`、`verify_in_daytona`、`Client`、`(tmp_path / "daytona-verification.json").read_text`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup.Client`（L233–L246）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup.Client.create`（L234–L237）：接收`params`、`**kwargs`。 控制顺序：L237抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup.Client.get`（L239–L242）：接收`name`。 控制顺序：L240断言`name == self.name and name.startswith("rnd-verify-")`。 调用`name.startswith`、`events.append`、`SimpleNamespace`。 返回路径：L242的`SimpleNamespace(id=OWNED_ID)`。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup.Client.delete`（L244–L246）：接收`sandbox`、`**kwargs`。 控制顺序：L245断言`sandbox.id == OWNED_ID`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup.capture`（L248–L253）：接收`identifier`、`name`、`configuration`。 控制顺序：L249断言`identifier == OWNED_ID and name.startswith("rnd-verify-")`；L251按`diagnostic_failure`分支；L252抛异常，停止当前正常路径。 调用`name.startswith`、`events.append`、`RuntimeError`。 返回路径：L253的`{"status": "captured", "affects_acceptance": False}`。

</details>

**创建路径：** `tests/test_daytona_startup_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L267。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9786`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_startup_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "67345fab14faed7f0b33b7caab02a5cee021979b815bdc1a7ab4e84ffbd05a3b"} -->
````python
# tests/test_daytona_startup_diagnostics.py
"""Read-only startup inspection must be scoped, redacted and cleanup-independent."""

import json
import os
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from workbench import daytona_diagnostics as diagnostics
from workbench import tools
from workbench.filesystem import atomic_text
from workbench.generator import PrerequisiteError
from workbench.sandbox import verify_in_daytona
from workbench.tools import ToolFailure

OWNED_ID = "11111111-2222-4333-8444-555555555555"
OWNED_NAME = "rnd-verify-" + "a" * 32


def local_compose(tmp_path, monkeypatch):
    from scripts import daytona_local

    monkeypatch.setattr(daytona_local, "HOME", tmp_path)
    atomic_text(tmp_path / "compose.lock.yaml", "fixture-only-compose")
    atomic_text(tmp_path / "credentials.json", json.dumps({"password": "local-password-sentinel"}))
    return daytona_local


def test_diagnostics_only_exact_owned_id_fixed_daemons_and_no_environment_dump(
    tmp_path, settings, monkeypatch
):
    local_compose(tmp_path, monkeypatch)
    settings.daytona_api_key = SecretStr("api-secret-sentinel")
    calls = []

    def command(argv, cwd, timeout):
        calls.append(argv)
        assert 0 < timeout <= 5
        assert argv[:2] == ["docker", "compose"]
        assert "DOCKER_HOST=unix:///var/run/docker.sock" in argv
        assert "runner" in argv and OWNED_ID in argv
        assert "ps" not in argv and "Env" not in " ".join(argv)
        return {
            "log": "x" * 10000
            + " api-secret-sentinel local-password-sentinel Bearer hidden-token password=other-secret"
            + ' {"token":"json-private-token"} postgresql://u:db-private-password@127.0.0.1/test'
        }

    monkeypatch.setattr(diagnostics, "run_command", command)
    report = diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)
    assert len(calls) == 3 and report["affects_acceptance"] is False
    body = json.dumps(report)
    for secret in [
        "api-secret-sentinel",
        "local-password-sentinel",
        "hidden-token",
        "other-secret",
        "json-private-token",
        "db-private-password",
    ]:
        assert secret not in body
    assert all(
        len(value["text"]) <= diagnostics.MAX_CHARS for value in report["diagnostics"].values()
    )
    assert "OOMKilled" in calls[0][calls[0].index("--format") + 1]
    assert calls[-1][-3:] == ["tail", "--bytes=8192", "/tmp/daytona-daemon.log"]


def test_diagnostics_cross_real_local_command_policy_with_fixed_inner_environment(
    tmp_path, settings, monkeypatch
):
    local = local_compose(tmp_path, monkeypatch)
    settings.daytona_api_key = SecretStr("api-secret-sentinel")
    hostile = {
        "DOCKER_HOST": "tcp://remote.invalid:2376",
        "DOCKER_CONTEXT": "remote-context",
        "DOCKER_TLS": "1",
        "DOCKER_TLS_VERIFY": "1",
        "DOCKER_CERT_PATH": "/untrusted-certificates",
        "DOCKER_CONFIG": "/untrusted-config",
    }
    for name, value in hostile.items():
        monkeypatch.setenv(name, value)
    calls = []
    waits = []

    class Process:
        def __init__(self, argv, **kwargs):
            calls.append((argv, kwargs))
            kwargs["stdout"].write(
                b"x" * 10000 + b" api-secret-sentinel local-password-sentinel password=other-secret"
            )

        def wait(self, timeout):
            waits.append(timeout)
            return 0

    # Keep capture_startup, run_command and local_docker_command real. Only the
    # process creation is stubbed, so a rejected diagnostic cannot look captured.
    monkeypatch.setattr(tools.subprocess, "Popen", Process)
    report = diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)
    endpoint = (
        "npipe:////./pipe/docker_engine" if os.name == "nt" else "unix:///var/run/docker.sock"
    )
    expected_prefix = [
        "docker",
        "--host",
        endpoint,
        "compose",
        "-p",
        local.PROJECT,
        "-f",
        str(tmp_path / "compose.lock.yaml"),
        "exec",
        "-T",
        "-e",
        "DOCKER_HOST=unix:///var/run/docker.sock",
        "-e",
        "DOCKER_CONTEXT=",
        "-e",
        "DOCKER_TLS=",
        "-e",
        "DOCKER_TLS_VERIFY=",
        "-e",
        "DOCKER_CERT_PATH=",
        "runner",
        "docker",
    ]
    expected_suffixes = [
        ["inspect", "--format", diagnostics.STATE_FORMAT, OWNED_ID],
        ["logs", "--tail", "80", OWNED_ID],
        ["exec", OWNED_ID, "tail", "--bytes=8192", "/tmp/daytona-daemon.log"],
    ]
    assert len(calls) == len(waits) == 3
    for (argv, options), suffix in zip(calls, expected_suffixes, strict=True):
        assert argv == expected_prefix + suffix
        assert options["shell"] is False
        assert all(name not in options["env"] for name in hostile)
    assert all(0 < timeout <= 5 for timeout in waits)
    assert diagnostics.TOTAL_SECONDS == 15
    assert report["passed"] is False and report["affects_acceptance"] is False
    assert all(row["status"] == "captured" for row in report["diagnostics"].values())
    assert all(len(row["text"]) <= 8192 for row in report["diagnostics"].values())
    body = json.dumps(report)
    for secret in ["api-secret-sentinel", "local-password-sentinel", "other-secret"]:
        assert secret not in body


@pytest.mark.parametrize(
    "argv",
    [
        ["docker", "--host", "tcp://remote.invalid:2376", "ps"],
        ["docker", "--host", "unix:///var/run/docker.sock", "ps"],
        ["docker", "--context=remote", "ps"],
        ["docker", "-H", "unix:///var/run/docker.sock", "ps"],
        ["docker", "exec", OWNED_ID, "tail", "-c", "8192", "/tmp/daytona-daemon.log"],
    ],
)
def test_diagnostics_fix_does_not_relax_general_docker_overrides(argv, tmp_path, monkeypatch):
    monkeypatch.setattr(
        tools.subprocess, "Popen", lambda *a, **kw: pytest.fail("override reached process")
    )
    with pytest.raises(ValueError):
        tools.run_command(argv, tmp_path, timeout=5)


@pytest.mark.parametrize(
    "identifier,name",
    [
        ("other-container", OWNED_NAME),
        (OWNED_ID, "user-sandbox"),
        (OWNED_ID, "rnd-verify-../../other"),
    ],
)
def test_invalid_identity_never_invokes_docker(identifier, name, settings, monkeypatch):
    monkeypatch.setattr(
        tools.subprocess,
        "Popen",
        lambda *a, **kw: pytest.fail("must not inspect another container"),
    )
    with pytest.raises(ValueError):
        diagnostics.capture_startup(identifier, name, settings)


def test_missing_fixed_compose_does_not_discover_other_installations(
    tmp_path, settings, monkeypatch
):
    from scripts import daytona_local

    monkeypatch.setattr(daytona_local, "HOME", tmp_path)
    monkeypatch.setattr(
        diagnostics, "run_command", lambda *a, **kw: pytest.fail("must not enumerate Docker")
    )
    assert (
        diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)["status"]
        == "fixed-local-compose-unavailable"
    )


def test_diagnostic_errors_are_bounded_and_do_not_escape(tmp_path, settings, monkeypatch):
    local_compose(tmp_path, monkeypatch)

    def fail(*a, **kw):
        error = ToolFailure("private exception must not be serialized")
        error.log = "password=hidden-secret"
        raise error

    monkeypatch.setattr(diagnostics, "run_command", fail)
    report = diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)
    assert len(report["diagnostics"]) == 3
    assert all(row["status"] == "unavailable" for row in report["diagnostics"].values())
    assert "hidden-secret" not in json.dumps(report)
    assert "private exception" not in json.dumps(report)


@pytest.mark.parametrize(
    "enabled,diagnostic_failure", [(False, False), (True, False), (True, True)]
)
def test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup(
    tmp_path, settings, monkeypatch, enabled, diagnostic_failure
):
    product = tmp_path / "product"
    product.mkdir()
    atomic_text(product / "pyproject.toml", "fixture")
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = True
    settings.daytona_api_key = SecretStr("test-local-only")
    settings.daytona_snapshot = "test-local-snapshot"
    settings.daytona_capture_startup_diagnostics = enabled
    events = []

    class Client:
        def create(self, params, **kwargs):
            self.name = params.name
            events.append("create")
            raise RuntimeError("timeout waiting for daemon to start")

        def get(self, name):
            assert name == self.name and name.startswith("rnd-verify-")
            events.append("lookup-exact-name")
            return SimpleNamespace(id=OWNED_ID)

        def delete(self, sandbox, **kwargs):
            assert sandbox.id == OWNED_ID
            events.append("delete")

    def capture(identifier, name, configuration):
        assert identifier == OWNED_ID and name.startswith("rnd-verify-")
        events.append("diagnostics")
        if diagnostic_failure:
            raise RuntimeError("must-not-leak-private-exception")
        return {"status": "captured", "affects_acceptance": False}

    monkeypatch.setattr(diagnostics, "capture_startup", capture)
    with pytest.raises(PrerequisiteError):
        verify_in_daytona(product, "fastapiadmin", settings, client=Client())
    assert events == [
        "create",
        "lookup-exact-name",
        *(["diagnostics"] if enabled else []),
        "delete",
    ]
    body = (tmp_path / "daytona-verification.json").read_text(encoding="utf-8")
    report = json.loads(body)
    assert report["passed"] is False and report["cleanup"] == "deleted"
    assert report["sandbox_id"] == OWNED_ID and "must-not-leak-private-exception" not in body
````
