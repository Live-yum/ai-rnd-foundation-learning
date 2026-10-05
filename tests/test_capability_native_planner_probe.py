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
