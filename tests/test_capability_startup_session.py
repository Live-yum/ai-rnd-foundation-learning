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
