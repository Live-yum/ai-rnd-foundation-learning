# tests/test_handbook_runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_only_full_suite_has_the_expanded_explicit_budget`（L17–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L18断言`ci_handbook.FULL_SUITE_TIMEOUT == 1800`；L19断言`inspect.signature(ci_handbook.run_full_tests).parameters["timeout"].default == 1800`；L20断言`inspect.signature(ci_handbook.run).parameters["timeout"].default == 900`；L23断言`"timeout-minutes: 40" in section`；L24断言`"--prepare-artifact reports/restored-source" in section`；L25断言`" restored-tests:" in section`；L26断言`"shard: [0, 1, 2, 3]" in section`；L27断言`"timeout-minutes: ${{ matrix.os == 'windows-latest' && 60 \|\| 35 }}" in workflow`。 调用`inspect.signature`、`(ci_handbook.ROOT / ".github/workflows/test.yml").read_text`、`workflow.split(" handbook-only:", 1)[1].split`、`workflow.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_completed_child_preserves_xml_and_exact_exit_status`（L31–L51）：接收`tmp_path`、`code`。 控制顺序：L42按`code`分支；L45断言`failure.value.returncode == code`；L49断言`status["timed_out"] is False and status["returncode"] == code`；L50断言`status["junit_available"] is True`；L51断言`(reports / "handbook-tests.xml").read_text(encoding="utf-8") == body`。 调用`str`、`pytest.raises`、`ci_handbook.run_full_tests`、`dict`、`json.loads`、`(reports / "handbook-test-status.json").read_text`、`(reports / "handbook-tests.xml").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deadline_remains_failure_even_when_interrupt_writes_success_xml`（L55–L94）：接收`tmp_path`、`monkeypatch`、`exit_during_grace`。 控制顺序：L88断言`failure.value.timeout == 1800`；L89断言`waits == [1800, 15] and len(signals) == 1`；L90断言`stopped == ([] if exit_during_grace else [321])`；L91断言`cleaned == [{321: "parent", 322: "child"}]`；L93断言`status["timed_out"] is True and status["timeout_seconds"] == 1800`；L94断言`status["junit_available"] is exit_during_grace`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`cleaned.append`、`pytest.raises`、`ci_handbook.run_full_tests`、`len`、`json.loads`、`(reports / "handbook-test-status.json").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deadline_remains_failure_even_when_interrupt_writes_success_xml.wait`（L62–L68）：接收`timeout`。 控制顺序：L64按`len(waits) == 2 and exit_during_grace`分支；L68抛异常，停止当前正常路径。 调用`waits.append`、`len`、`junit.write_text`、`subprocess.TimeoutExpired`。 返回路径：L67的`0`。
- `test_deadline_remains_failure_even_when_interrupt_writes_success_xml.stop`（L70–L73）：接收`owned`。 控制顺序：L71断言`owned is process`。 调用`stopped.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_receipt_survives_owned_cleanup_failure`（L97–L120）：接收`tmp_path`、`monkeypatch`。 控制顺序：L119断言`status["timed_out"] is True and status["cleanup_error_type"] == "RuntimeError"`；L120断言`status["junit_available"] is False`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`pytest.raises`、`ci_handbook.run_full_tests`、`json.loads`、`(tmp_path / "reports/handbook-test-status.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_receipt_survives_owned_cleanup_failure.wait`（L98–L99）：接收`**kwargs`。 控制顺序：L99抛异常，停止当前正常路径。 调用`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_receipt_survives_owned_cleanup_failure.stop`（L108–L109）：接收`_`。 控制顺序：L109抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_launch_failure_is_retained_without_claiming_tests_ran`（L123–L136）：接收`tmp_path`、`monkeypatch`。 控制顺序：L135断言`status["error_type"] == "OSError" and status["returncode"] is None`；L136断言`status["junit_available"] is False and status["timed_out"] is False`。 调用`monkeypatch.setattr`、`pytest.raises`、`ci_handbook.run_full_tests`、`json.loads`、`(tmp_path / "reports/handbook-test-status.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_launch_failure_is_retained_without_claiming_tests_ran.launch`（L124–L125）：接收`*args`、`**kwargs`。 控制顺序：L125抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_grace_exit_cleans_proven_surviving_child_not_foreign_or_recycled_pid`（L139–L147）：接收`monkeypatch`。 控制顺序：L147断言`killed == [(322, ci_handbook.signal.SIGKILL)]`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`killed.append`、`ci_handbook.cleanup_owned_descendants`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_snapshot_stops_live_owned_tree_without_grace_or_expired_pid_lookup`（L150–L174）：接收`tmp_path`、`monkeypatch`。 控制顺序：L174断言`waits == [1800] and stopped == [321]`。 调用`SimpleNamespace`、`pytest.fail`、`monkeypatch.setattr`、`pytest.raises`、`ci_handbook.run_full_tests`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_snapshot_stops_live_owned_tree_without_grace_or_expired_pid_lookup.wait`（L156–L158）：接收`timeout`。 控制顺序：L158抛异常，停止当前正常路径。 调用`waits.append`、`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_snapshot_stops_live_owned_tree_without_grace_or_expired_pid_lookup.stop`（L160–L163）：接收`owned`。 控制顺序：L161断言`owned is process`。 调用`stopped.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_grace_exit_cleans_detached_owned_child_and_preserves_foreign_process`（L180–L237）：接收`tmp_path`。 控制顺序：L211遍历`range(50)`；L218按`fields[0] == "Z" or fields[19] != owned_child["started"]`分支；L223断言`foreign.poll() is None`；L225断言`status["timed_out"] is True and status["returncode"] == 0`；L226断言`status["junit_available"] is True and status["owned_processes_at_timeout"] >= 2`；L228按`child_file.is_file()`分支；L231按`current is not None and current[1] == owned["started"]`分支。 调用`subprocess.Popen`、`pytest.raises`、`ci_handbook.run_full_tests`、`str`、`dict`、`json.loads`、`child_file.read_text`、`range`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook_runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L237。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10342`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook_runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "826ff48c01533eb49d65769922f074fef578de727a2d7e69746d793b7d797787"} -->
````python
# tests/test_handbook_runtime.py
"""Bounded clean-room suite orchestration, not a substitute for the full suite."""

import inspect
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ci_handbook


def test_only_full_suite_has_the_expanded_explicit_budget():
    assert ci_handbook.FULL_SUITE_TIMEOUT == 1800
    assert inspect.signature(ci_handbook.run_full_tests).parameters["timeout"].default == 1800
    assert inspect.signature(ci_handbook.run).parameters["timeout"].default == 900
    workflow = (ci_handbook.ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
    section = workflow.split("  handbook-only:", 1)[1].split("  browser:", 1)[0]
    assert "timeout-minutes: 40" in section
    assert "--prepare-artifact reports/restored-source" in section
    assert "  restored-tests:" in section
    assert "shard: [0, 1, 2, 3]" in section
    assert "timeout-minutes: ${{ matrix.os == 'windows-latest' && 60 || 35 }}" in workflow


@pytest.mark.parametrize("code", [0, 3])
def test_completed_child_preserves_xml_and_exact_exit_status(tmp_path, code):
    junit, reports = tmp_path / "student.xml", tmp_path / "reports"
    body = "<testsuites><testsuite><testcase name='unit-only'/></testsuite></testsuites>"
    argv = [
        sys.executable,
        "-c",
        "from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2], encoding='utf-8'); sys.exit(int(sys.argv[3]))",
        str(junit),
        body,
        str(code),
    ]
    if code:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            ci_handbook.run_full_tests(argv, tmp_path, dict(os.environ), junit, reports, timeout=10)
        assert failure.value.returncode == code
    else:
        ci_handbook.run_full_tests(argv, tmp_path, dict(os.environ), junit, reports, timeout=10)
    status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
    assert status["timed_out"] is False and status["returncode"] == code
    assert status["junit_available"] is True
    assert (reports / "handbook-tests.xml").read_text(encoding="utf-8") == body


@pytest.mark.parametrize("exit_during_grace", [True, False])
def test_deadline_remains_failure_even_when_interrupt_writes_success_xml(
    tmp_path, monkeypatch, exit_during_grace
):
    junit, reports = tmp_path / "student.xml", tmp_path / "reports"
    waits, signals, stopped, cleaned = [], [], [], []
    process = SimpleNamespace(pid=321, returncode=None)

    def wait(*, timeout):
        waits.append(timeout)
        if len(waits) == 2 and exit_during_grace:
            junit.write_text("<testsuites/>", encoding="utf-8")
            process.returncode = 0
            return 0
        raise subprocess.TimeoutExpired("unit-owned-pytest", timeout)

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        owned.returncode = -9

    process.wait = wait
    process.send_signal = signals.append
    process.poll = lambda: process.returncode
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    monkeypatch.setattr(
        ci_handbook, "capture_owned_descendants", lambda _: {321: "parent", 322: "child"}
    )
    monkeypatch.setattr(
        ci_handbook, "cleanup_owned_descendants", lambda owned: cleaned.append(owned)
    )
    with pytest.raises(subprocess.TimeoutExpired) as failure:
        ci_handbook.run_full_tests(["unit-only"], tmp_path, {}, junit, reports)
    assert failure.value.timeout == 1800
    assert waits == [1800, 15] and len(signals) == 1
    assert stopped == ([] if exit_during_grace else [321])
    assert cleaned == [{321: "parent", 322: "child"}]
    status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
    assert status["timed_out"] is True and status["timeout_seconds"] == 1800
    assert status["junit_available"] is exit_during_grace


def test_timeout_receipt_survives_owned_cleanup_failure(tmp_path, monkeypatch):
    def wait(**kwargs):
        raise subprocess.TimeoutExpired("unit-owned-pytest", kwargs["timeout"])

    process = SimpleNamespace(
        returncode=None, wait=wait, poll=lambda: None, send_signal=lambda _: None
    )
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "capture_owned_descendants", lambda _: {321: "owned"})
    monkeypatch.setattr(ci_handbook, "cleanup_owned_descendants", lambda _: None)

    def stop(_):
        raise RuntimeError("owned cleanup canary")

    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    with pytest.raises(subprocess.TimeoutExpired):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    status = json.loads(
        (tmp_path / "reports/handbook-test-status.json").read_text(encoding="utf-8")
    )
    assert status["timed_out"] is True and status["cleanup_error_type"] == "RuntimeError"
    assert status["junit_available"] is False


def test_launch_failure_is_retained_without_claiming_tests_ran(tmp_path, monkeypatch):
    def launch(*args, **kwargs):
        raise OSError("unit launch canary")

    monkeypatch.setattr(ci_handbook.subprocess, "Popen", launch)
    with pytest.raises(OSError, match="unit launch canary"):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    status = json.loads(
        (tmp_path / "reports/handbook-test-status.json").read_text(encoding="utf-8")
    )
    assert status["error_type"] == "OSError" and status["returncode"] is None
    assert status["junit_available"] is False and status["timed_out"] is False


def test_grace_exit_cleans_proven_surviving_child_not_foreign_or_recycled_pid(monkeypatch):
    identities = {321: None, 322: (1, "child"), 323: (1, "recycled"), 999: (1, "foreign")}
    killed = []
    # This is a POSIX ownership simulation even when the test host is Windows.
    monkeypatch.setattr(ci_handbook, "signal", SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(ci_handbook, "process_identity", identities.get)
    monkeypatch.setattr(ci_handbook.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    ci_handbook.cleanup_owned_descendants({321: "parent", 322: "child", 323: "old-child"})
    assert killed == [(322, ci_handbook.signal.SIGKILL)]


def test_no_snapshot_stops_live_owned_tree_without_grace_or_expired_pid_lookup(
    tmp_path, monkeypatch
):
    process = SimpleNamespace(pid=321, returncode=None)
    waits, stopped = [], []

    def wait(*, timeout):
        waits.append(timeout)
        raise subprocess.TimeoutExpired("unit-owned-pytest", timeout)

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        owned.returncode = -9

    process.wait, process.poll = wait, lambda: process.returncode
    process.send_signal = lambda _: pytest.fail("No unverifiable grace-period cleanup")
    monkeypatch.setattr(ci_handbook.subprocess, "Popen", lambda *args, **kw: process)
    monkeypatch.setattr(ci_handbook, "capture_owned_descendants", lambda _: None)
    monkeypatch.setattr(ci_handbook, "stop_process", stop)
    with pytest.raises(subprocess.TimeoutExpired):
        ci_handbook.run_full_tests(
            ["unit-only"], tmp_path, {}, tmp_path / "absent.xml", tmp_path / "reports"
        )
    assert waits == [1800] and stopped == [321]


@pytest.mark.skipif(
    os.name == "nt" or not Path("/proc").is_dir(), reason="Linux process identity integration"
)
def test_real_grace_exit_cleans_detached_owned_child_and_preserves_foreign_process(tmp_path):
    junit, child_file, reports = (
        tmp_path / "student.xml",
        tmp_path / "child.pid",
        tmp_path / "reports",
    )
    script = """
import json, signal, subprocess, sys, time
from pathlib import Path
def interrupt(*_):
    Path(sys.argv[1]).write_text('<testsuites/>', encoding='utf-8')
    raise SystemExit(0)
signal.signal(signal.SIGINT, interrupt)
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
started = Path(f'/proc/{child.pid}/stat').read_text(encoding='utf-8').rsplit(') ', 1)[1].split()[19]
Path(sys.argv[2]).write_text(json.dumps({'pid': child.pid, 'started': started}), encoding='utf-8')
time.sleep(30)
"""
    foreign = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            ci_handbook.run_full_tests(
                [sys.executable, "-c", script, str(junit), str(child_file)],
                tmp_path,
                dict(os.environ),
                junit,
                reports,
                timeout=2,
            )
        owned_child = json.loads(child_file.read_text(encoding="utf-8"))
        child = owned_child["pid"]
        for _ in range(50):
            path = Path(f"/proc/{child}/stat")
            try:
                fields = path.read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
            except FileNotFoundError, ProcessLookupError:
                # Exit/reaping can occur during read(), not only before exists().
                break
            if fields[0] == "Z" or fields[19] != owned_child["started"]:
                break
            time.sleep(0.02)
        else:
            pytest.fail("Proven detached child survived the exited leader")
        assert foreign.poll() is None
        status = json.loads((reports / "handbook-test-status.json").read_text(encoding="utf-8"))
        assert status["timed_out"] is True and status["returncode"] == 0
        assert status["junit_available"] is True and status["owned_processes_at_timeout"] >= 2
    finally:
        if child_file.is_file():
            owned = json.loads(child_file.read_text(encoding="utf-8"))
            current = ci_handbook.process_identity(owned["pid"])
            if current is not None and current[1] == owned["started"]:
                try:
                    os.kill(owned["pid"], ci_handbook.signal.SIGKILL)
                except ProcessLookupError:
                    pass
        foreign.terminate()
        foreign.wait(timeout=3)
````
