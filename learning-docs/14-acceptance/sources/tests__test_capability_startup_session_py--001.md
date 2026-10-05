# tests/test_capability_startup_session.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`、`workbench.capability_dependencies`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_plan`（L33–L55）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`、`RuntimeContract`、`TaskCommand`。 返回路径：L34的`SimpleNamespace( selection=Selection(template="fastapiadmin"), runtime=RuntimeContract( st…`。
- `startup_submission`（L58–L119）：接收`remote`、`product_argv`。 源码说明：Execute only the actual session-construction statements, never start().。 控制顺序：L111断言`len(calls) == 2`；L112断言`calls[0] == ("create", SESSION)`；L113断言`calls[1][0:2] == ("submit", SESSION)`；L114断言`calls[1][3] == {"timeout": 5}`；L115断言`calls[1][2].run_async is True`；L116断言`namespace["response"].cmd_id == "owned-command"`。 调用`Path`、`ast.parse`、`source.read_text`、`next`、`ast.walk`、`isinstance`、`enumerate`、`assigns`、`native_plan`等。 返回路径：L119的`calls[1][2].command, namespace["command_output"]`。
- `startup_submission.assigns`（L68–L71）：接收`node`、`name`。 调用`isinstance`、`any`。 返回路径：L69的`isinstance(node, ast.Assign) and any( isinstance(target, ast.Name) and target.id == name f…`。
- `startup_submission.submit`（L77–L79）：接收`session`、`request`、`**kwargs`。 调用`calls.append`、`SimpleNamespace`。 返回路径：L79的`SimpleNamespace(cmd_id="owned-command")`。
- `fixture_submission`（L122–L136）：接收`tmp_path`、`monkeypatch`、`argv`。 调用`(remote / "product/backend").mkdir`、`(control / "private").mkdir`、`monkeypatch.setattr`、`str`、`startup_submission`、`Path`。 返回路径：L136的`command, Path(output)`。
- `fixture_submission.harmless_argv`（L129–L133）：接收`plan`、`original`、`database`、`**options`。 控制顺序：L130断言`original == readonly_start_command(plan).argv`；L131断言`database == {}`；L132断言`options == {"native_semaphore_storage": True}`。 调用`readonly_start_command`。 返回路径：L133的`argv`。
- `launch_protocol`（L139–L150）：接收`tmp_path`、`command`。 调用`command_path.write_text`、`subprocess.Popen`、`str`。 返回路径：L150的`process, status_path`。
- `stop_owned_group`（L153–L166）：接收`process`。 源码说明：Only the process group created by this fixture is eligible for signals.。 调用`os.killpg`、`process.communicate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_startup_preserves_session_exit_status`（L171–L192）：接收`tmp_path`、`monkeypatch`、`status`。 控制顺序：L187断言`process.returncode == 0`；L188断言`stdout == stderr == b""`；L189断言`status_path.read_text() == str(status) + "\n"`；L190断言`output.read_text() == "owned\n"`。 调用`fixture_submission`、`str`、`launch_protocol`、`process.communicate`、`status_path.read_text`、`output.read_text`、`stop_owned_group`、`pytest.mark.skipif`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_previous_outer_exec_loses_exit_status`（L196–L212）：接收`tmp_path`、`monkeypatch`。 控制顺序：L204断言`previous != command`；L208断言`process.returncode == 7`；L209断言`not status_path.exists()`；L210断言`output.read_text() == "owned\n"`。 调用`fixture_submission`、`command.replace`、`launch_protocol`、`process.communicate`、`status_path.exists`、`output.read_text`、`stop_owned_group`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_submission_preserves_inner_exec_and_full_native_guard`（L215–L248）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L217断言`type(output) is str`；L218断言`output.startswith("/tmp/rnd-module-control/private/") and "\\" not in output`；L220断言`command.startswith(prefix)`；L222断言`launcher[:2] == ["/bin/sh", "-c"]`；L223断言`len(launcher) == 3`；L224断言`launcher[2].startswith("exec ")`；L231断言`launcher[2] == ( "exec " + shlex.join(expected) + " </dev/null >" + shlex.quote(outpu…`；L235断言`expected[guard - 3 : guard] == ["/usr/bin/python3", "-I", "-S"]`。后续分支沿下方源码相同行号继续阅读。 调用`startup_submission`、`type`、`output.startswith`、`command.startswith`、`shlex.split`、`len`、`launcher[2].startswith`、`isolation.product_argv`、`native_plan`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `live_process`（L251–L255）：接收`pid`。 调用`Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split`、`Path(f"/proc/{pid}/stat").read_text().rsplit`、`Path(f"/proc/{pid}/stat").read_text`、`Path`。 返回路径：L253的`Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"`；L255的`False`。
- `test_timed_out_fixture_cleans_owned_group_and_descendant`（L259–L295）：接收`tmp_path`、`monkeypatch`。 控制顺序：L279在`not marker.exists()`成立时循环；L280断言`process.poll() is None`；L281断言`time.monotonic() < deadline`；L284断言`len(owned_pids) == 2`；L285断言`all(os.getpgid(pid) == process.pid and live_process(pid) for pid in owned_pids)`；L288断言`not status_path.exists()`；L292在`any(live_process(pid) for pid in owned_pids) and time.monotonic()…`成立时循环；L294断言`owned_pids and all(not live_process(pid) for pid in owned_pids)`。后续分支沿下方源码相同行号继续阅读。 调用`fixture_submission`、`str`、`launch_protocol`、`time.monotonic`、`marker.exists`、`process.poll`、`time.sleep`、`json.loads`、`marker.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_session.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L295。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10600`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_session.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "75739acef82c89a81f529e925cbaf1c5a201bba72c6e9d5219db28238ed98266"} -->
````python
# tests/test_capability_startup_session.py
"""Real shell regression for Daytona 0.190.0's sourced-command protocol.

Only owned shell/Python fixtures execute locally. Production privilege and
candidate argv are inspected as data, never executed by these tests.
"""

import ast
import json
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from daytona import SessionExecuteRequest

from workbench import capability_isolation as isolation
from workbench.capability_contracts import RuntimeContract, TaskCommand
from workbench.capability_dependencies import readonly_start_command
from workbench.catalog import Selection

# Exact source/status operations from the pinned daemon wrapper, with FIFO
# demultiplexing omitted: our production launcher redirects all stdio itself.
# https://github.com/daytonaio/daytona/blob/v0.190.0/apps/daemon/pkg/session/execute.go
SESSION_PROTOCOL = '{ . "$1"; }\n_ec=$?\necho "$_ec" >> "$2"\n'
SESSION = "rnd-app-" + "1" * 32


def native_plan():
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


def startup_submission(*, remote, product_argv=isolation.product_argv):
    """Execute only the actual session-construction statements, never start()."""
    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    start = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "start"
    )

    def assigns(node, name):
        return isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        )

    first = next(i for i, node in enumerate(start.body) if assigns(node, "session"))
    last = next(i for i, node in enumerate(start.body) if assigns(node, "response"))
    calls = []

    def submit(session, request, **kwargs):
        calls.append(("submit", session, request, kwargs))
        return SimpleNamespace(cmd_id="owned-command")

    plan = native_plan()
    namespace = {
        "uuid": SimpleNamespace(uuid4=lambda: SimpleNamespace(hex="1" * 32)),
        "sandbox": SimpleNamespace(
            process=SimpleNamespace(
                create_session=lambda session: calls.append(("create", session)),
                execute_session_command=submit,
            )
        ),
        "plan": plan,
        "command": readonly_start_command(plan),
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "port": None,
        "health_path": None,
        "REMOTE": str(remote),
        "product_argv": product_argv,
        "redirected_command": isolation.redirected_command,
        "SessionExecuteRequest": SessionExecuteRequest,
        "shlex": shlex,
        "settings": SimpleNamespace(tool_timeout=5),
    }
    exec(
        compile(
            ast.Module(body=start.body[first : last + 1], type_ignores=[]),
            "<actual-startup-submission>",
            "exec",
        ),
        namespace,
    )
    assert len(calls) == 2
    assert calls[0] == ("create", SESSION)
    assert calls[1][0:2] == ("submit", SESSION)
    assert calls[1][3] == {"timeout": 5}
    assert calls[1][2].run_async is True
    assert namespace["response"].cmd_id == "owned-command"
    # This is a remote Linux path even when the controller test runs on Windows.
    # Converting it to the host Path here changes slash and shell-quoting bytes.
    return calls[1][2].command, namespace["command_output"]


def fixture_submission(tmp_path, monkeypatch, argv):
    remote = tmp_path / "source ' with spaces; literal"
    (remote / "product/backend").mkdir(parents=True)
    control = tmp_path / "owned-control"
    (control / "private").mkdir(parents=True)
    monkeypatch.setattr(isolation, "CONTROL", str(control))

    def harmless_argv(plan, original, database, **options):
        assert original == readonly_start_command(plan).argv
        assert database == {}
        assert options == {"native_semaphore_storage": True}
        return argv

    command, output = startup_submission(remote=remote, product_argv=harmless_argv)
    return command, Path(output)


def launch_protocol(tmp_path, command):
    command_path = tmp_path / "cmd.sh"
    status_path = tmp_path / "exit-code"
    command_path.write_text(command + "\n")
    process = subprocess.Popen(
        ["/bin/sh", "-c", SESSION_PROTOCOL, "fixture", str(command_path), str(status_path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    return process, status_path


def stop_owned_group(process):
    """Only the process group created by this fixture is eligible for signals."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=3)


@pytest.mark.skipif(os.name != "posix", reason="POSIX sourced-session protocol")
@pytest.mark.parametrize("status", [0, 7, 127])
def test_actual_startup_preserves_session_exit_status(tmp_path, monkeypatch, status):
    command, output = fixture_submission(
        tmp_path,
        monkeypatch,
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import sys; print('owned'); sys.exit(int(sys.argv[1]))",
            str(status),
        ],
    )
    process, status_path = launch_protocol(tmp_path, command)
    try:
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode == 0
        assert stdout == stderr == b""
        assert status_path.read_text() == str(status) + "\n"
        assert output.read_text() == "owned\n"
    finally:
        stop_owned_group(process)


@pytest.mark.skipif(os.name != "posix", reason="POSIX sourced-session protocol")
def test_previous_outer_exec_loses_exit_status(tmp_path, monkeypatch):
    command, output = fixture_submission(
        tmp_path,
        monkeypatch,
        [sys.executable, "-I", "-S", "-c", "import sys; print('owned'); sys.exit(7)"],
    )
    # Restore only the removed outer exec, retaining the actual inner launcher.
    previous = command.replace(" && ", " && exec ", 1)
    assert previous != command
    process, status_path = launch_protocol(tmp_path, previous)
    try:
        process.communicate(timeout=5)
        assert process.returncode == 7
        assert not status_path.exists()
        assert output.read_text() == "owned\n"
    finally:
        stop_owned_group(process)


def test_submission_preserves_inner_exec_and_full_native_guard():
    command, output = startup_submission(remote="/tmp/rnd-capability")
    assert type(output) is str
    assert output.startswith("/tmp/rnd-module-control/private/") and "\\" not in output
    prefix = "cd /tmp/rnd-capability/product/backend && "
    assert command.startswith(prefix)
    launcher = shlex.split(command[len(prefix) :])
    assert launcher[:2] == ["/bin/sh", "-c"]
    assert len(launcher) == 3
    assert launcher[2].startswith("exec ")
    expected = isolation.product_argv(
        native_plan(),
        readonly_start_command(native_plan()).argv,
        {},
        native_semaphore_storage=True,
    )
    assert launcher[2] == (
        "exec " + shlex.join(expected) + " </dev/null >" + shlex.quote(output) + " 2>&1"
    )
    guard = expected.index(isolation.GUARD)
    assert expected[guard - 3 : guard] == ["/usr/bin/python3", "-I", "-S"]
    assert expected[guard + 1 : guard + 5] == [
        "5173,8001",
        "8001,55432,55433",
        "--native-shm",
        "--",
    ]
    for flag in (
        "--reuid=rnd-module",
        "--regid=rnd-module",
        "--no-new-privs",
        "--bounding-set=-all",
    ):
        assert flag in expected


def live_process(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except FileNotFoundError:
        return False


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process-group cleanup evidence")
def test_timed_out_fixture_cleans_owned_group_and_descendant(tmp_path, monkeypatch):
    marker = tmp_path / "owned-pids.json"
    worker = """import json,os,pathlib,signal,subprocess,sys,time
child=subprocess.Popen([sys.executable,'-I','-S','-c','import time; time.sleep(60)'])
def terminate(signum,frame):
 child.terminate()
 try:child.wait(timeout=2)
 except subprocess.TimeoutExpired:child.kill();child.wait(timeout=2)
 raise SystemExit(0)
signal.signal(signal.SIGTERM,terminate)
pathlib.Path(sys.argv[1]).write_text(json.dumps([os.getpid(),child.pid]))
time.sleep(60)
"""
    command, _ = fixture_submission(
        tmp_path, monkeypatch, [sys.executable, "-I", "-S", "-c", worker, str(marker)]
    )
    process, status_path = launch_protocol(tmp_path, command)
    owned_pids = []
    try:
        deadline = time.monotonic() + 5
        while not marker.exists():
            assert process.poll() is None, "Owned fixture exited before creating its child"
            assert time.monotonic() < deadline, "Owned fixture did not become ready"
            time.sleep(0.01)
        owned_pids = json.loads(marker.read_text())
        assert len(owned_pids) == 2
        assert all(os.getpgid(pid) == process.pid and live_process(pid) for pid in owned_pids)
        with pytest.raises(subprocess.TimeoutExpired):
            process.communicate(timeout=0.05)
        assert not status_path.exists()
    finally:
        stop_owned_group(process)
    deadline = time.monotonic() + 3
    while any(live_process(pid) for pid in owned_pids) and time.monotonic() < deadline:
        time.sleep(0.01)
    assert owned_pids and all(not live_process(pid) for pid in owned_pids)
    assert process.poll() is not None
````
