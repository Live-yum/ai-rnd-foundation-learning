# tests/test_capability_sqlite_quiescence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `wait_until`（L20–L24）：接收`predicate`。 控制顺序：L22在`not predicate()`成立时循环；L23断言`time.monotonic() < end`。 调用`time.monotonic`、`predicate`、`time.sleep`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `owned_writer`（L28–L52）：接收`tmp_path`、`monkeypatch`。 调用`repr`、`str`、`subprocess.Popen`、`wait_until`、`monkeypatch.setattr`、`pause`、`os.getuid`、`child.kill`、`child.wait`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `owned_writer.only_our_child`（L39–L40）：接收`uid`。 调用`inventory(uid).items`、`inventory`。 返回路径：L40的`{key: value for key, value in inventory(uid).items() if key[0] == child.pid}`。
- `assert_same_writer_resumed`（L55–L59）：接收`child`、`heartbeat`、`inventory`。 控制顺序：L58断言`child.poll() is None`；L59断言`all(row[0] != "T" for row in inventory(os.getuid()).values())`。 调用`heartbeat.read_text`、`wait_until`、`child.poll`、`all`、`inventory(os.getuid()).values`、`inventory`、`os.getuid`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_pauses_then_resumes_same_live_writer`（L62–L69）：接收`owned_writer`。 控制顺序：L68断言`supervisor.supervise([sys.executable, "-I", "-S", "-c", code], 2) == b"retained\n"`。 调用`repr`、`str`、`supervisor.supervise`、`assert_same_writer_resumed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supervisor_resumes_writer_when_reader_fails`（L73–L87）：接收`owned_writer`、`failure`。 控制顺序：L76按`failure == "reader-exit"`分支；L79按`failure == "reader-timeout"`分支。 调用`pytest.raises`、`supervisor.supervise`、`assert_same_writer_resumed`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_pause_acquisition_still_resumes_already_stopped_groups`（L90–L104）：接收`owned_writer`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`supervisor.supervise`、`assert_same_writer_resumed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_pause_acquisition_still_resumes_already_stopped_groups.partial`（L94–L99）：接收`uid`。 控制顺序：L97按`calls > 1`分支；L98抛异常，停止当前正常路径。 调用`RuntimeError`、`inventory`。 返回路径：L99的`inventory(uid)`。
- `test_resume_write_restop_race_cannot_forge_a_stopped_physical_observation`（L107–L116）：接收`owned_writer`。 调用`str`、`pytest.raises`、`supervisor.supervise`、`assert_same_writer_resumed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supervisor_termination_resumes_writer_and_reaps_reader`（L119–L153）：接收`owned_writer`。 控制顺序：L147断言`process.returncode != 0`；L148断言`stdout == b""`；L151按`process.poll() is None`分支。 调用`pathlib.Path(supervisor.__file__).read_text`、`pathlib.Path`、`source.replace`、`os.getuid`、`subprocess.Popen`、`wait_until`、`all`、`inventory(os.getuid()).values`、`inventory`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resume_error_closes_all_pidfds_and_never_yields_a_receipt`（L156–L172）：接收`monkeypatch`。 控制顺序：L170断言`signaled == [(31, signal.SIGCONT), (32, signal.SIGCONT)]`；L171断言`closed == [31, 32]`；L172断言`pause.handles == {}`。 调用`supervisor.ApplicationPause`、`time.monotonic`、`monkeypatch.setattr`、`pytest.raises`、`pause.resume`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resume_error_closes_all_pidfds_and_never_yields_a_receipt.resume`（L161–L164）：接收`fd`、`sig`。 控制顺序：L163按`fd == 31`分支；L164抛异常，停止当前正常路径。 调用`signaled.append`、`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_zombie_leader_does_not_hide_still_running_worker_thread`（L175–L207）：接收`monkeypatch`。 控制顺序：L189断言`selected and all(key[1] != child.pid for key in selected)`；L198断言`all(value[0] == "T" for value in pause.baseline.values())`。 调用`subprocess.Popen`、`pathlib.Path`、`str`、`wait_until`、`status.read_text`、`inventory(os.getuid()).items`、`inventory`、`os.getuid`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_system_interpreter_runs_complete_pause_snapshot_resume`（L210–L273）：接收`owned_writer`、`tmp_path`。 控制顺序：L217按`not interpreter.is_file()`分支；L269断言`result.returncode == 0`；L270断言`json.loads(result.stdout) == [{"title": "retained-random"}]`；L272断言`list(private.iterdir()) == []`。 调用`pathlib.Path`、`interpreter.is_file`、`pytest.skip`、`private.mkdir`、`sqlite3.connect`、`connection.execute`、`pathlib.Path(supervisor.__file__).read_text`、`source.replace`、`os.getuid`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cmdline_scraper_cannot_reconstruct_erased_row_before_pause`（L276–L396）：接收`tmp_path`。 源码说明：A real owned app scrapes only explicitly supplied owned supervisor PIDs.。 控制顺序：L339断言`connection.execute("SELECT title FROM entries").fetchone() == (challenge,)`；L377断言`challenge not in " ".join(argv)`；L381断言`secured.returncode == 0`；L382断言`json.loads(stdout) == []`；L385断言`not found.exists()`；L387断言`connection.execute("SELECT COUNT(*) FROM entries").fetchone() == (0,)`；L388断言`app.poll() is None`；L390断言`list(private.iterdir()) == []`。后续分支沿下方源码相同行号继续阅读。 调用`sqlite3.connect`、`connection.execute`、`watch.write_text`、`subprocess.Popen`、`str`、`uuid.uuid4`、`json.dumps`、`wait_until`、`connection.execute("SELECT title FROM entries").fetchone`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_sqlite_quiescence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L396。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15262`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_sqlite_quiescence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "67ef9b9ca2898942b80d5af904a1984eb9eea9c84a9a8c044cce85f2a7f7a01a"} -->
````python
# tests/test_capability_sqlite_quiescence.py
"""Pause only explicitly owned synthetic children, never a test-host UID."""

import os
import pathlib
import signal
import subprocess
import sys
import time

import pytest

from scripts import capability_sqlite_quiescence as supervisor

pytestmark = pytest.mark.skipif(
    sys.platform != "linux" or not hasattr(os, "pidfd_open"),
    reason="Sandbox supervisor requires Linux pidfds and /proc",
)


def wait_until(predicate):
    end = time.monotonic() + 3
    while not predicate():
        assert time.monotonic() < end, "Owned child did not reach the expected state"
        time.sleep(0.01)


@pytest.fixture
def owned_writer(tmp_path, monkeypatch):
    heartbeat = tmp_path / "heartbeat"
    code = (
        "import pathlib,time; p=pathlib.Path(" + repr(str(heartbeat)) + "); i=0\n"
        "while True:\n i+=1;p.write_text(str(i));time.sleep(.005)\n"
    )
    child = subprocess.Popen([sys.executable, "-I", "-S", "-c", code])
    wait_until(heartbeat.exists)
    inventory = supervisor.task_inventory
    pause = supervisor.ApplicationPause

    def only_our_child(uid):
        return {key: value for key, value in inventory(uid).items() if key[0] == child.pid}

    monkeypatch.setattr(supervisor, "task_inventory", only_our_child)
    monkeypatch.setattr(
        supervisor, "ApplicationPause", lambda deadline: pause(deadline, uid=os.getuid())
    )
    try:
        yield child, heartbeat, only_our_child
    finally:
        # Cleanup is pinned to this Popen-owned child, independent of the code
        # under test. It cannot target another host process or application UID.
        child.kill()
        child.wait(timeout=5)


def assert_same_writer_resumed(child, heartbeat, inventory):
    previous = heartbeat.read_text()
    wait_until(lambda: heartbeat.read_text() not in {"", previous})
    assert child.poll() is None
    assert all(row[0] != "T" for row in inventory(os.getuid()).values())


def test_probe_pauses_then_resumes_same_live_writer(owned_writer):
    child, heartbeat, inventory = owned_writer
    code = (
        "import pathlib,time; p=pathlib.Path(" + repr(str(heartbeat)) + "); "
        "before=p.read_bytes();time.sleep(.05);assert p.read_bytes()==before;print('retained')"
    )
    assert supervisor.supervise([sys.executable, "-I", "-S", "-c", code], 2) == b"retained\n"
    assert_same_writer_resumed(child, heartbeat, inventory)


@pytest.mark.parametrize("failure", ["reader-exit", "reader-timeout", "reader-launch"])
def test_supervisor_resumes_writer_when_reader_fails(owned_writer, failure):
    child, heartbeat, inventory = owned_writer
    command = [sys.executable, "-I", "-S", "-c"]
    if failure == "reader-exit":
        command += ["raise SystemExit(7)"]
        error, budget = RuntimeError, 2
    elif failure == "reader-timeout":
        command += ["import time;time.sleep(20)"]
        error, budget = subprocess.TimeoutExpired, 0.2
    else:
        command = ["/deliberately-missing-owned-reader"]
        error, budget = FileNotFoundError, 2
    with pytest.raises(error):
        supervisor.supervise(command, budget)
    assert_same_writer_resumed(child, heartbeat, inventory)


def test_failed_pause_acquisition_still_resumes_already_stopped_groups(owned_writer, monkeypatch):
    child, heartbeat, inventory = owned_writer
    calls = 0

    def partial(uid):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise RuntimeError("injected inventory failure")
        return inventory(uid)

    monkeypatch.setattr(supervisor, "task_inventory", partial)
    with pytest.raises(RuntimeError, match="inventory"):
        supervisor.supervise([sys.executable, "-c", "print('must not run')"], 2)
    assert_same_writer_resumed(child, heartbeat, inventory)


def test_resume_write_restop_race_cannot_forge_a_stopped_physical_observation(owned_writer):
    child, heartbeat, inventory = owned_writer
    code = (
        "import os,signal,time,pathlib;pid=" + str(child.pid) + ";"
        "os.kill(pid,signal.SIGCONT);time.sleep(.04);os.kill(pid,signal.SIGSTOP);"
        "time.sleep(.04);print('forged')"
    )
    with pytest.raises(RuntimeError, match="ran or changed"):
        supervisor.supervise([sys.executable, "-I", "-S", "-c", code], 2)
    assert_same_writer_resumed(child, heartbeat, inventory)


def test_supervisor_termination_resumes_writer_and_reaps_reader(owned_writer):
    child, heartbeat, inventory = owned_writer
    # Execute the actual trusted script with only its inventory restricted to
    # our explicit child. Do not run its production UID-wide selection locally.
    source = pathlib.Path(supervisor.__file__).read_text()
    source = source.replace("APP_UID = 20000", f"APP_UID = {os.getuid()}")
    source = source.replace(
        'pathlib.Path("/proc").glob("[0-9]*/task/[0-9]*/status")',
        f'pathlib.Path("/proc/{child.pid}").glob("task/[0-9]*/status")',
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            source,
            "unused.db",
            "8",
            "import time;time.sleep(20)",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        wait_until(lambda: all(row[0] == "T" for row in inventory(os.getuid()).values()))
        process.send_signal(signal.SIGTERM)
        stdout, _ = process.communicate(timeout=5)
        assert process.returncode != 0
        assert stdout == b""
        assert_same_writer_resumed(child, heartbeat, inventory)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)


def test_resume_error_closes_all_pidfds_and_never_yields_a_receipt(monkeypatch):
    pause = supervisor.ApplicationPause(time.monotonic() + 1)
    pause.handles = {100: 31, 101: 32}
    closed, signaled = [], []

    def resume(fd, sig):
        signaled.append((fd, sig))
        if fd == 31:
            raise PermissionError("injected resume failure")

    monkeypatch.setattr(supervisor.signal, "pidfd_send_signal", resume)
    monkeypatch.setattr(supervisor.os, "close", closed.append)
    with pytest.raises(RuntimeError, match="resume"):
        pause.resume()
    assert signaled == [(31, signal.SIGCONT), (32, signal.SIGCONT)]
    assert closed == [31, 32]
    assert pause.handles == {}


def test_zombie_leader_does_not_hide_still_running_worker_thread(monkeypatch):
    source = (
        "import threading,time,ctypes; "
        "threading.Thread(target=lambda:time.sleep(20),daemon=True).start(); "
        "ctypes.CDLL(None).pthread_exit(None)"
    )
    child = subprocess.Popen([sys.executable, "-I", "-S", "-c", source])
    inventory = supervisor.task_inventory
    try:
        status = pathlib.Path("/proc", str(child.pid), "status")
        wait_until(lambda: "State:\tZ" in status.read_text())
        selected = {
            key: value for key, value in inventory(os.getuid()).items() if key[0] == child.pid
        }
        assert selected and all(key[1] != child.pid for key in selected)
        monkeypatch.setattr(
            supervisor,
            "task_inventory",
            lambda uid: {
                key: value for key, value in inventory(uid).items() if key[0] == child.pid
            },
        )
        with supervisor.ApplicationPause(time.monotonic() + 2, uid=os.getuid()) as pause:
            assert all(value[0] == "T" for value in pause.baseline.values())
            pause.verify()
        wait_until(
            lambda: all(
                value[0] != "T" for value in supervisor.task_inventory(os.getuid()).values()
            )
        )
    finally:
        child.kill()
        child.wait(timeout=5)


def test_system_interpreter_runs_complete_pause_snapshot_resume(owned_writer, tmp_path):
    import json
    import sqlite3

    from workbench.capability_obligations import SQLITE_PROBE

    interpreter = pathlib.Path("/usr/bin/python3")
    if not interpreter.is_file():
        pytest.skip("Sandbox system interpreter is not installed on this test host")
    child, heartbeat, inventory = owned_writer
    private = tmp_path / "controller-private"
    private.mkdir(mode=0o700)
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'retained-random')")
    source = pathlib.Path(supervisor.__file__).read_text()
    source = source.replace("APP_UID = 20000", f"APP_UID = {os.getuid()}")
    source = source.replace(
        'pathlib.Path("/proc").glob("[0-9]*/task/[0-9]*/status")',
        f'pathlib.Path("/proc/{child.pid}").glob("task/[0-9]*/status")',
    )
    probe = (
        SQLITE_PROBE.replace(
            "pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(tmp_path)!r})"
        )
        .replace(
            "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
        )
        .replace("control_uid=0", f"control_uid={os.getuid()}")
    )
    request = private / ("obligation-" + "a" * 32 + ".json")
    request.write_text(
        json.dumps(
            {
                "database_path": database.name,
                "assertion": {
                    "table": "entries",
                    "key": {"id": 7},
                    "values": {"title": "retained-random"},
                },
            }
        )
    )
    result = subprocess.run(
        [
            str(interpreter),
            "-I",
            "-S",
            "-c",
            source,
            str(request),
            "8",
            probe,
        ],
        capture_output=True,
        text=True,
        timeout=12,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [{"title": "retained-random"}]
    request.unlink()
    assert list(private.iterdir()) == []
    assert_same_writer_resumed(child, heartbeat, inventory)


def test_cmdline_scraper_cannot_reconstruct_erased_row_before_pause(tmp_path):
    """A real owned app scrapes only explicitly supplied owned supervisor PIDs."""
    import json
    import sqlite3
    import uuid

    from workbench.capability_obligations import SQLITE_PROBE, assert_physical_rows
    from workbench.capability_verification import CheckFailure

    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
    watch, scanned, found = (tmp_path / name for name in ("watch", "scanned", "found"))
    watch.write_text("")
    scraper = r"""
import json,pathlib,sqlite3,sys,time
store,watch,scanned,found=map(pathlib.Path,sys.argv[1:])
while True:
 try:
  raw=watch.read_text()
  if raw:
   pid=int(raw)
   for argument in pathlib.Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0'):
    try:
     value=json.loads(argument)
     if type(value) is not dict:continue
     assertion=value.get('assertion',value)
     if assertion.get('table')!='entries':continue
     key=assertion['key']['id'];title=assertion['values']['title']
     with sqlite3.connect(store) as connection:
      connection.execute('DELETE FROM entries')
      connection.execute('INSERT INTO entries VALUES(?,?)',(key,title))
     found.write_text('reconstructed')
    except (ValueError,KeyError,TypeError):pass
   scanned.write_text(str(pid))
 except (FileNotFoundError,ProcessLookupError,ValueError):pass
 time.sleep(.002)
"""
    app = subprocess.Popen(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            scraper,
            str(database),
            str(watch),
            str(scanned),
            str(found),
        ]
    )
    leaky = secured = None
    challenge = "fresh-secret-" + uuid.uuid4().hex
    assertion = {"table": "entries", "key": {"id": 7}, "values": {"title": challenge}}
    try:
        # Positive attack control: the old command-line transport exposes enough
        # information to repopulate an empty DB before any freeze is attempted.
        leaky = subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", "import time;time.sleep(20)", json.dumps(assertion)]
        )
        watch.write_text(str(leaky.pid))
        wait_until(found.exists)
        with sqlite3.connect(database) as connection:
            assert connection.execute("SELECT title FROM entries").fetchone() == (challenge,)
        watch.write_text("")
        leaky.kill()
        leaky.wait(timeout=5)
        with sqlite3.connect(database) as connection:
            connection.execute("DELETE FROM entries")
        found.unlink()
        scanned.unlink(missing_ok=True)

        private = tmp_path / "controller-private"
        private.mkdir(mode=0o700)
        request = private / ("obligation-" + uuid.uuid4().hex + ".json")
        request.write_text(json.dumps({"database_path": database.name, "assertion": assertion}))
        source = pathlib.Path(supervisor.__file__).read_text()
        source = source.replace("APP_UID = 20000", f"APP_UID = {os.getuid()}").replace(
            'pathlib.Path("/proc").glob("[0-9]*/task/[0-9]*/status")',
            f'pathlib.Path("/proc/{app.pid}").glob("task/[0-9]*/status")',
        )
        # Give the scraper a deterministic pre-pause observation window. No
        # secrets occur in this hook, the supervisor source, or its child argv.
        barrier = f"""if __name__ == "__main__":
    until=time.monotonic()+3
    acknowledge=pathlib.Path({str(scanned)!r})
    while not acknowledge.exists() or acknowledge.read_text()!=str(os.getpid()):
        if time.monotonic()>until:raise TimeoutError('scraper did not inspect owned cmdline')
        time.sleep(.002)
"""
        source = source.replace('if __name__ == "__main__":\n', barrier)
        probe = (
            SQLITE_PROBE.replace(
                "pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(tmp_path)!r})"
            )
            .replace(
                "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
            )
            .replace("control_uid=0", f"control_uid={os.getuid()}")
        )
        argv = [sys.executable, "-I", "-S", "-c", source, str(request), "8", probe]
        assert challenge not in " ".join(argv)
        secured = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        watch.write_text(str(secured.pid))
        stdout, stderr = secured.communicate(timeout=12)
        assert secured.returncode == 0, stderr.decode()
        assert json.loads(stdout) == []
        with pytest.raises(CheckFailure, match="物理值"):
            assert_physical_rows(json.loads(stdout), assertion)
        assert not found.exists()
        with sqlite3.connect(database) as connection:
            assert connection.execute("SELECT COUNT(*) FROM entries").fetchone() == (0,)
        assert app.poll() is None
        request.unlink()
        assert list(private.iterdir()) == []
    finally:
        for process in (secured, leaky, app):
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
````
