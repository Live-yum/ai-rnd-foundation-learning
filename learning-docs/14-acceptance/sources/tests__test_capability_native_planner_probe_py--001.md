# tests/test_capability_native_planner_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_verification`、`workbench.catalog`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `setup`（L21–L43）：接收`monkeypatch`、`count`、`read`、`fail_create`、`fail_cleanup`。 调用`monkeypatch.setattr`、`SimpleNamespace`。 返回路径：L43的`calls`。
- `setup.guarded`（L27–L34）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L29按`argv[0] == "app-only"`分支；L33断言`argv[0] == "reader-only"`。 调用`calls.append`。 返回路径：L32的`(1, "") if failed else (0, probe.COMPLETE)`；L34的`0, read`。
- `setup.counts`（L36–L39）：接收`sandbox`、`plan`、`timeout`。 控制顺序：L38断言`plan.runtime.database_tables == [NAME]`。 调用`calls.append`。 返回路径：L39的`{NAME: count}`。
- `execute`（L46–L48）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`、`probe.verify_native_planner_identity`。 返回路径：L48的`probe.verify_native_planner_identity(None, plan, {"DATABASE_PASSWORD": "synthetic"}, 30)`。
- `test_owned_probe_uses_app_ddl_and_separate_reader_then_cleans_up`（L51–L68）：接收`monkeypatch`。 控制顺序：L53断言`execute() == {probe.CHECK: True}`；L54断言`[call[0] for call in calls] == [ "app-only", "production-count", "reader-only", "app-…`；L60断言`"CREATE INDEX" in calls[0][-1]`；L61断言`"IMMUTABLE" in calls[0][-1]`；L62断言`"privileged planner evaluation" in calls[0][-1]`；L63断言`"SET ROLE postgres" in calls[2][-1]`；L64断言`"insufficient_privilege" in calls[2][-1]`；L65断言`"END;\n$probe$" in calls[0][-1]`。后续分支沿下方源码相同行号继续阅读。 调用`setup`、`execute`、`probe.statements`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_probe_never_emits_success_and_still_cleans_up`（L72–L76）：接收`monkeypatch`、`updates`。 控制顺序：L76断言`calls[-1][0] == "app-only" and "DROP TABLE" in calls[-1][-1]`。 调用`setup`、`pytest.raises`、`execute`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_cleanup_prevents_certificate`（L79–L82）：接收`monkeypatch`。 调用`setup`、`pytest.raises`、`execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_failure_retains_only_fixed_primary_phase`（L94–L100）：接收`monkeypatch`、`updates`、`phase`。 控制顺序：L98断言`str(error.value) == ( f"本次规划器探针对象清理未确认，禁止交付（primary={phase}; cleanup=failed）" )`。 调用`setup`、`pytest.raises`、`execute`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_exception_does_not_expose_arbitrary_failure_text`（L103–L114）：接收`monkeypatch`。 控制顺序：L112断言`str(error.value).endswith("（primary=create; cleanup=failed）")`；L113断言`"synthetic-private" not in str(error.value)`；L114断言`error.value.__suppress_context__`。 调用`setup`、`monkeypatch.setattr`、`pytest.raises`、`execute`、`str(error.value).endswith`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_exception_does_not_expose_arbitrary_failure_text.fails`（L106–L107）：接收`*args`。 控制顺序：L107抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_controller_generated_probe_identifiers_are_allowed`（L120–L122）：接收`name`。 调用`pytest.raises`、`probe.statements`、`pytest.mark.parametrize`、`NAME.upper`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_native_database_is_rejected_before_any_command`（L125–L128）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`probe.verify_native_planner_identity`、`SimpleNamespace`、`Selection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `app_sql_child`（L131–L179）：接收`monkeypatch`、`source`、`launch_error`。 源码说明：Run the unchanged helper with a real synthetic child, never a database.。 控制顺序：L133按`sys.platform != "linux"`分支。 调用`pytest.skip`、`monkeypatch.setenv`、`monkeypatch.setattr`。 返回路径：L179的`children`。
- `app_sql_child.launch`（L138–L174）：接收`argv`、`**kwargs`。 控制顺序：L139断言`argv == [ "/usr/lib/postgresql/17/bin/psql", "-X", "-q", "-At", "-w", "-v", "ON_ERROR…`；L158断言`kwargs == { "env": { "PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "PGPASSWORD": "…`；L170按`launch_error`分支；L171抛异常，停止当前正常路径。 调用`PermissionError`、`original`、`children.append`。 返回路径：L174的`process`。
- `execute_app_sql`（L182–L187）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L187断言`time.monotonic() - started < 12`。 调用`time.monotonic`、`exec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_succeeds_without_reopening_devnull`（L190–L211）：接收`monkeypatch`、`capsys`。 控制顺序：L209断言`children[0].returncode == 0`；L210断言`children[0].stdout.closed`；L211断言`capsys.readouterr() == (probe.COMPLETE + "\n", "")`。 调用`monkeypatch.setattr`、`pytest.raises`、`subprocess.run`、`app_sql_child`、`execute_app_sql`、`capsys.readouterr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_succeeds_without_reopening_devnull.deny_devnull`（L193–L196）：接收`path`、`flags`、`*args`、`**kwargs`。 控制顺序：L194按`path == os.devnull and flags & (os.O_WRONLY \| os.O_RDWR)`分支；L195抛异常，停止当前正常路径。 调用`PermissionError`、`original_open`。 返回路径：L196的`original_open(path, flags, *args, **kwargs)`。
- `test_app_sql_failures_are_silent_and_children_reaped`（L222–L228）：接收`monkeypatch`、`capsys`、`source`、`launch_error`。 控制顺序：L226断言`error.value.code == 1`；L227断言`all(child.returncode is not None and child.stdout.closed for child in children)`；L228断言`capsys.readouterr() == ("", "")`。 调用`app_sql_child`、`pytest.raises`、`execute_app_sql`、`all`、`capsys.readouterr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_oversized_output_kills_and_reaps_still_running_child`（L231–L238）：接收`monkeypatch`、`capsys`。 控制顺序：L235断言`error.value.code == 1`；L236断言`len(children) == 1 and children[0].returncode < 0`；L237断言`children[0].stdout.closed`；L238断言`capsys.readouterr() == ("", "")`。 调用`app_sql_child`、`pytest.raises`、`execute_app_sql`、`len`、`capsys.readouterr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_read_exception_is_silent_and_child_reaped`（L241–L256）：接收`monkeypatch`、`capsys`。 控制顺序：L253断言`error.value.code == 1`；L254断言`len(children) == 1 and children[0].returncode is not None`；L255断言`children[0].stdout.closed`；L256断言`capsys.readouterr() == ("", "")`。 调用`app_sql_child`、`monkeypatch.setattr`、`pytest.raises`、`execute_app_sql`、`len`、`capsys.readouterr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_read_exception_is_silent_and_child_reaped.fail_pipe`（L245–L248）：接收`descriptor`、`size`。 控制顺序：L246按`children and descriptor == children[0].stdout.fileno()`分支；L247抛异常，停止当前正常路径。 调用`children[0].stdout.fileno`、`OSError`、`original_read`。 返回路径：L248的`original_read(descriptor, size)`。
- `test_app_sql_selector_exception_closes_pipe_and_reaps_child`（L260–L276）：接收`monkeypatch`、`capsys`、`operation`。 控制顺序：L267按`operation == "construct"`分支；L273断言`error.value.code == 1`；L274断言`len(children) == 1 and children[0].returncode < 0`；L275断言`children[0].stdout.closed`；L276断言`capsys.readouterr() == ("", "")`。 调用`app_sql_child`、`monkeypatch.setattr`、`pytest.raises`、`execute_app_sql`、`len`、`capsys.readouterr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_selector_exception_closes_pipe_and_reaps_child.fail`（L264–L265）：接收`*args`。 控制顺序：L265抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_deadline_covers_both_stream_read_and_child_wait`（L280–L293）：接收`monkeypatch`、`capsys`、`close_streams`。 控制顺序：L284按`close_streams`分支；L290断言`error.value.code == 1`；L291断言`len(children) == 1 and children[0].returncode is not None`；L292断言`children[0].stdout.closed`；L293断言`capsys.readouterr() == ("", "")`。 调用`app_sql_child`、`pytest.raises`、`execute_app_sql`、`len`、`capsys.readouterr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_sql_deadline_rejects_descendant_holding_pipe`（L297–L337）：接收`tmp_path`。 控制顺序：L336断言`process.returncode == 0`；L337断言`process.stdout == "owned-descendant-reaped\n" and process.stderr == ""`。 调用`str`、`subprocess.run`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_landlock_denies_devnull_but_allows_app_sql_pipe`（L341–L370）：接收`tmp_path`。 控制顺序：L367按`process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1"`分支；L369断言`process.returncode == 0`；L370断言`process.stdout == probe.COMPLETE + "\n" and process.stderr == ""`。 调用`str`、`subprocess.run`、`os.environ.get`、`pytest.skip`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_planner_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L370。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13907`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_planner_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "19dea61bcced430fe0833128d870bb96f3e978c1426efe75dde1793e99c3e9f3"} -->
````python
# tests/test_capability_native_planner_probe.py
"""Planner protocol and child-I/O regressions, not a PostgreSQL certificate."""

import errno
import os
import selectors
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from scripts import capability_native_planner_probe as probe
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.settings import ROOT

NAME = "rnd_planner_" + "a" * 32


def setup(monkeypatch, *, count=1, read="restricted", fail_create=False, fail_cleanup=False):
    calls = []
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex="a" * 32))
    monkeypatch.setattr(probe, "product_argv", lambda plan, argv, env: ["app-only", *argv])
    monkeypatch.setattr(probe, "pg_verifier_argv", lambda sql: ["reader-only", sql])

    def guarded(sandbox, argv, timeout):
        calls.append(argv)
        if argv[0] == "app-only":
            cleanup = "DROP TABLE" in argv[-1]
            failed = fail_cleanup if cleanup else fail_create
            return (1, "") if failed else (0, probe.COMPLETE)
        assert argv[0] == "reader-only"
        return 0, read

    def counts(sandbox, plan, timeout):
        calls.append(["production-count", *plan.runtime.database_tables])
        assert plan.runtime.database_tables == [NAME]
        return {NAME: count}

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    monkeypatch.setattr(probe, "database_counts", counts)
    return calls


def execute():
    plan = SimpleNamespace(selection=Selection(template="fastapiadmin"))
    return probe.verify_native_planner_identity(None, plan, {"DATABASE_PASSWORD": "synthetic"}, 30)


def test_owned_probe_uses_app_ddl_and_separate_reader_then_cleans_up(monkeypatch):
    calls = setup(monkeypatch)
    assert execute() == {probe.CHECK: True}
    assert [call[0] for call in calls] == [
        "app-only",
        "production-count",
        "reader-only",
        "app-only",
    ]
    assert "CREATE INDEX" in calls[0][-1]
    assert "IMMUTABLE" in calls[0][-1]
    assert "privileged planner evaluation" in calls[0][-1]
    assert "SET ROLE postgres" in calls[2][-1]
    assert "insufficient_privilege" in calls[2][-1]
    assert "END;\n$probe$" in calls[0][-1]
    assert "session_user='rnd_verify'" in calls[2][-1]
    assert calls[-1][-1] == probe.statements(NAME)[2]
    assert "TO PROGRAM" not in calls[0][-1] and "pg_read_file" not in calls[0][-1]


@pytest.mark.parametrize("updates", [{"count": 0}, {"read": "postgres"}, {"fail_create": True}])
def test_failed_probe_never_emits_success_and_still_cleans_up(monkeypatch, updates):
    calls = setup(monkeypatch, **updates)
    with pytest.raises(CheckFailure):
        execute()
    assert calls[-1][0] == "app-only" and "DROP TABLE" in calls[-1][-1]


def test_failed_cleanup_prevents_certificate(monkeypatch):
    setup(monkeypatch, fail_cleanup=True)
    with pytest.raises(CheckFailure, match="清理"):
        execute()


@pytest.mark.parametrize(
    "updates,phase",
    [
        ({"fail_create": True}, "create"),
        ({"count": 0}, "count"),
        ({"read": "postgres"}, "identity"),
        ({}, "none"),
    ],
)
def test_cleanup_failure_retains_only_fixed_primary_phase(monkeypatch, updates, phase):
    setup(monkeypatch, fail_cleanup=True, **updates)
    with pytest.raises(CheckFailure) as error:
        execute()
    assert str(error.value) == (
        f"本次规划器探针对象清理未确认，禁止交付（primary={phase}; cleanup=failed）"
    )


def test_cleanup_exception_does_not_expose_arbitrary_failure_text(monkeypatch):
    setup(monkeypatch)

    def fails(*args):
        raise RuntimeError("synthetic-private-diagnostic")

    monkeypatch.setattr(probe, "run_guarded_control", fails)
    with pytest.raises(CheckFailure) as error:
        execute()
    assert str(error.value).endswith("（primary=create; cleanup=failed）")
    assert "synthetic-private" not in str(error.value)
    assert error.value.__suppress_context__


@pytest.mark.parametrize(
    "name", ["user_table", "rnd_planner_" + "a" * 32 + ";DROP DATABASE x", NAME.upper()]
)
def test_only_controller_generated_probe_identifiers_are_allowed(name):
    with pytest.raises(CheckFailure):
        probe.statements(name)


def test_non_native_database_is_rejected_before_any_command(monkeypatch):
    monkeypatch.setattr(probe, "run_guarded_control", lambda *a: pytest.fail("command ran"))
    with pytest.raises(CheckFailure):
        probe.verify_native_planner_identity(None, SimpleNamespace(selection=Selection()), {}, 10)


def app_sql_child(monkeypatch, source, *, launch_error=False):
    """Run the unchanged helper with a real synthetic child, never a database."""
    if sys.platform != "linux":
        pytest.skip("The isolated PostgreSQL helper and its selectable pipes are Linux-only")
    original = subprocess.Popen
    children = []

    def launch(argv, **kwargs):
        assert argv == [
            "/usr/lib/postgresql/17/bin/psql",
            "-X",
            "-q",
            "-At",
            "-w",
            "-v",
            "ON_ERROR_STOP=1",
            "-h",
            "127.0.0.1",
            "-p",
            "55432",
            "-U",
            "rnd_app",
            "-d",
            "rnd_product",
            "-c",
            "SELECT 1",
        ]
        assert kwargs == {
            "env": {
                "PATH": "/usr/bin:/bin",
                "HOME": "/nonexistent",
                "PGPASSWORD": "synthetic",
                "PGOPTIONS": (
                    "-c search_path=pg_catalog -c statement_timeout=3000 -c lock_timeout=1000"
                ),
            },
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
        }
        if launch_error:
            raise PermissionError("synthetic-private-launch-error")
        process = original([sys.executable, "-I", "-S", "-c", source], **kwargs)
        children.append(process)
        return process

    monkeypatch.setenv("DATABASE_PASSWORD", "synthetic")
    monkeypatch.setattr(sys, "argv", ["owned-planner-probe", "SELECT 1"])
    monkeypatch.setattr(subprocess, "Popen", launch)
    return children


def execute_app_sql():
    started = time.monotonic()
    try:
        exec(probe.APP_SQL, {})
    finally:
        assert time.monotonic() - started < 12


def test_app_sql_succeeds_without_reopening_devnull(monkeypatch, capsys):
    original_open = os.open

    def deny_devnull(path, flags, *args, **kwargs):
        if path == os.devnull and flags & (os.O_WRONLY | os.O_RDWR):
            raise PermissionError(errno.EACCES, "synthetic-landlock-denial")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", deny_devnull)
    # The old DEVNULL pattern fails before it can execute even a harmless child.
    with pytest.raises(PermissionError):
        subprocess.run(
            [sys.executable, "-I", "-S", "-c", "pass"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
        )
    children = app_sql_child(monkeypatch, "import os;os.write(1,b'x'*2048);os.write(2,b'y'*2048)")
    execute_app_sql()
    assert children[0].returncode == 0
    assert children[0].stdout.closed
    assert capsys.readouterr() == (probe.COMPLETE + "\n", "")


@pytest.mark.parametrize(
    "source,launch_error",
    [
        ("import os\nwhile True:os.write(2,b'x'*4096)", False),
        ("import os;os.write(2,b'synthetic-private-sql-error');raise SystemExit(1)", False),
        ("pass", True),
    ],
)
def test_app_sql_failures_are_silent_and_children_reaped(monkeypatch, capsys, source, launch_error):
    children = app_sql_child(monkeypatch, source, launch_error=launch_error)
    with pytest.raises(SystemExit) as error:
        execute_app_sql()
    assert error.value.code == 1
    assert all(child.returncode is not None and child.stdout.closed for child in children)
    assert capsys.readouterr() == ("", "")


def test_app_sql_oversized_output_kills_and_reaps_still_running_child(monkeypatch, capsys):
    children = app_sql_child(monkeypatch, "import os,time;os.write(1,b'x'*4097);time.sleep(30)")
    with pytest.raises(SystemExit) as error:
        execute_app_sql()
    assert error.value.code == 1
    assert len(children) == 1 and children[0].returncode < 0
    assert children[0].stdout.closed
    assert capsys.readouterr() == ("", "")


def test_app_sql_read_exception_is_silent_and_child_reaped(monkeypatch, capsys):
    children = app_sql_child(monkeypatch, "import os,time;os.write(1,b'x');time.sleep(30)")
    original_read = os.read

    def fail_pipe(descriptor, size):
        if children and descriptor == children[0].stdout.fileno():
            raise OSError("synthetic-private-read-error")
        return original_read(descriptor, size)

    monkeypatch.setattr(os, "read", fail_pipe)
    with pytest.raises(SystemExit) as error:
        execute_app_sql()
    assert error.value.code == 1
    assert len(children) == 1 and children[0].returncode is not None
    assert children[0].stdout.closed
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("operation", ["construct", "register"])
def test_app_sql_selector_exception_closes_pipe_and_reaps_child(monkeypatch, capsys, operation):
    children = app_sql_child(monkeypatch, "import time;time.sleep(30)")
    original = selectors.DefaultSelector

    def fail(*args):
        raise OSError("synthetic-private-selector-error")

    if operation == "construct":
        monkeypatch.setattr(selectors, "DefaultSelector", fail)
    else:
        monkeypatch.setattr(original, "register", fail)
    with pytest.raises(SystemExit) as error:
        execute_app_sql()
    assert error.value.code == 1
    assert len(children) == 1 and children[0].returncode < 0
    assert children[0].stdout.closed
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("close_streams", [False, True])
def test_app_sql_deadline_covers_both_stream_read_and_child_wait(
    monkeypatch, capsys, close_streams
):
    source = "import os,time;"
    if close_streams:
        source += "os.close(1);os.close(2);"
    source += "time.sleep(30)"
    children = app_sql_child(monkeypatch, source)
    with pytest.raises(SystemExit) as error:
        execute_app_sql()
    assert error.value.code == 1
    assert len(children) == 1 and children[0].returncode is not None
    assert children[0].stdout.closed
    assert capsys.readouterr() == ("", "")


@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only owned child subreaper")
def test_app_sql_deadline_rejects_descendant_holding_pipe(tmp_path):
    pidfile = tmp_path / "owned-descendant"
    child = (
        "import pathlib,subprocess,sys;"
        "p=subprocess.Popen([sys.executable,'-I','-S','-c','import time;time.sleep(30)']);"
        f"pathlib.Path({str(pidfile)!r}).write_text(str(p.pid))"
    )
    # Only this disposable supervisor becomes a subreaper so it can explicitly
    # kill and reap its own orphan. The production helper kills its direct
    # child; deletion of the owned sandbox is the descendant cleanup boundary.
    source = f"""
import ctypes,os,pathlib,signal,subprocess,sys,time
assert ctypes.CDLL(None).prctl(36,1,0,0,0)==0
original=subprocess.Popen
children=[]
def launch(argv,**kwargs):
 p=original([sys.executable,'-I','-S','-c',{child!r}],**kwargs)
 children.append(p)
 return p
subprocess.Popen=launch
os.environ['DATABASE_PASSWORD']='synthetic'
sys.argv=['owned-planner-probe','SELECT 1']
started=time.monotonic()
try:
 try:exec({probe.APP_SQL!r},{{}})
 except SystemExit as error:assert error.code==1
 else:raise AssertionError('inherited writer was accepted')
 assert time.monotonic()-started<12
 assert len(children)==1 and children[0].returncode==0 and children[0].stdout.closed
finally:
 pid=int(pathlib.Path({str(pidfile)!r}).read_text())
 os.kill(pid,signal.SIGKILL)
 reaped,status=os.waitpid(pid,0)
 assert reaped==pid and os.WIFSIGNALED(status)
print('owned-descendant-reaped')
"""
    process = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=15
    )
    assert process.returncode == 0
    assert process.stdout == "owned-descendant-reaped\n" and process.stderr == ""


@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only child filesystem restriction")
def test_real_landlock_denies_devnull_but_allows_app_sql_pipe(tmp_path):
    source = f"""
import ctypes,errno,os,runpy,subprocess,sys
m=runpy.run_path({str(ROOT / "scripts/capability_guard.py")!r})
restrict=m['restrict_tcp'];restrict.__globals__['WRITABLE_ROOT']={str(tmp_path)!r}
libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
if libc.syscall(444,0,0,1)<6:sys.exit(78)
restrict(set(),set(),filesystem=True)
m['restrict_sockets'](allow_tcp_connect=True)
try:
 subprocess.run([sys.executable,'-I','-S','-c','pass'],
  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=1)
except OSError as error:assert error.errno in (errno.EACCES,errno.EPERM)
else:raise AssertionError('unexpected device write permission')
original=subprocess.Popen
def launch(argv,**kwargs):
 assert argv[0]=='/usr/lib/postgresql/17/bin/psql'
 return original([sys.executable,'-I','-S','-c','pass'],**kwargs)
subprocess.Popen=launch
os.environ['DATABASE_PASSWORD']='synthetic'
sys.argv=['owned-planner-probe','SELECT 1']
exec({probe.APP_SQL!r},{{}})
"""
    process = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=15
    )
    if process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1":
        pytest.skip("Kernel/security profile cannot run mandatory live Landlock checks")
    assert process.returncode == 0
    assert process.stdout == probe.COMPLETE + "\n" and process.stderr == ""
````
