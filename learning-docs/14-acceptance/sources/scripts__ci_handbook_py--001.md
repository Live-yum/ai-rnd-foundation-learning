# scripts/ci_handbook.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：证明一本书足够重建平台。** 把教材单独复制进临时目录，恢复所有文本与二进制截图，确认导入来源，验证再次生成相同教材；再重建三个上游归档和Continue。完整非PG套件有明确1800秒预算，外层仍40分钟；超时中断自有测试进程、保留阶段与已有JUnit且仍失败，不增加单项等待。

**对应关系：** handbook-only工作流 → 本脚本 → handbook-test-status.json/JUnit；完整通过才产生handbook-clean-room.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`、`scripts.rebuild_from_handbook`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run`（L22–L24）：接收`argv`、`directory`、`env`、`timeout`。 调用`subprocess.run`。 返回路径：L24的`result.returncode`。
- `process_identity`（L27–L33）：接收`pid`。 源码说明：Only ancestry and start identity; never commands or process environment.。 调用`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") "…`、`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit`、`Path(f"/proc/{pid}/stat").read_text`、`Path`、`int`。 返回路径：L31的`int(fields[1]), fields[19]`；L33的`None`。
- `capture_owned_descendants`（L36–L53）：接收`process`。 控制顺序：L37按`os.name == "nt" or not Path("/proc").is_dir()`分支；L40按`root is None`分支；L43遍历`Path("/proc").iterdir()`；L44按`path.name.isdecimal() and (identity := process_identity(int(path.name)))`分支；L47在`added := { pid: identity for pid, identity in snapshot.items() if…`成立时循环。 调用`Path("/proc").is_dir`、`Path`、`process_identity`、`Path("/proc").iterdir`、`path.name.isdecimal`、`int`、`snapshot.items`、`owned.update`、`owned.items`。 返回路径：L38的`None`；L41的`None`；L53的`{pid: identity[1] for pid, identity in owned.items()}`。
- `cleanup_owned_descendants`（L56–L65）：接收`owned`。 控制顺序：L59遍历`reversed(list(owned.items()))`；L61按`current is not None and current[1] == started`分支。 调用`reversed`、`list`、`owned.items`、`process_identity`、`os.kill`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_full_tests`（L68–L142）：接收`argv`、`directory`、`env`、`junit`、`reports`、`timeout`。 源码说明：Bound the whole expanded suite, retain failure status, and own its cleanup. This is a suite orchestration budget, not a browser or individual-test wait. Crossing it always fails, even if an interrupt 。 控制顺序：L89按`owned is None`分支；L105按`owned is not None`分支；L110按`process is not None and process.poll() is None`分支；L127按`junit.is_file()`分支；L133按`timed_out`分支；L134抛异常，停止当前正常路径；L135按`failure`分支；L136抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`reports.mkdir`、`time.monotonic`、`print`、`subprocess.Popen`、`process_options`、`process.wait`、`capture_owned_descendants`、`stop_process`、`process.send_signal`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L145–L242）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L156断言`not list((destination / "templates/vendor").glob("*.zip"))`；L172断言`(destination / OUTPUT.name).read_bytes() == text`；L177遍历`zip(expected["sources"], actual["sources"], strict=True)`；L179遍历`("name", "sha", "source_digest", "files")`；L180断言`want[field] == got[field]`；L192按`not npm`分支；L193抛异常，停止当前正常路径；L218按`not cases or any( case.find("failure") is not None or case.find("error") is not None …`分支。后续分支沿下方源码相同行号继续阅读。 调用`OUTPUT.read_bytes`、`json.loads`、`(ROOT / "templates/vendor/manifest.json").read_text`、`tempfile.TemporaryDirectory`、`Path`、`book.write_bytes`、`restore`、`extract`、`text.decode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_handbook.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L246。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10252`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_handbook.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "62b10f10e8def98f52b32e2aca78419c905784e5d0b0a973f172dccda3fab03a"} -->
````python
# scripts/ci_handbook.py
"""Verify construction from the handbook alone, without original source/archive access."""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.build_handbook import OUTPUT, ROOT
from scripts.rebuild_from_handbook import extract, restore
from workbench.tools import process_options, stop_process

FULL_SUITE_TIMEOUT = 1800


def run(argv, directory, env, timeout=900):
    result = subprocess.run(argv, cwd=directory, env=env, timeout=timeout, check=True)
    return result.returncode


def process_identity(pid):
    """Only ancestry and start identity; never commands or process environment."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
        return int(fields[1]), fields[19]
    except OSError, ValueError, IndexError:
        return None


def capture_owned_descendants(process):
    if os.name == "nt" or not Path("/proc").is_dir():
        return None
    root = process_identity(process.pid)
    if root is None:
        return None
    snapshot = {}
    for path in Path("/proc").iterdir():
        if path.name.isdecimal() and (identity := process_identity(int(path.name))):
            snapshot[int(path.name)] = identity
    owned = {process.pid: root}
    while added := {
        pid: identity
        for pid, identity in snapshot.items()
        if identity[0] in owned and pid not in owned
    }:
        owned.update(added)
    return {pid: identity[1] for pid, identity in owned.items()}


def cleanup_owned_descendants(owned):
    # A leader can exit during SIGINT grace. Start ticks still identify its
    # proven descendants after reparenting, without targeting recycled PIDs.
    for pid, started in reversed(list(owned.items())):
        current = process_identity(pid)
        if current is not None and current[1] == started:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def run_full_tests(argv, directory, env, junit, reports, *, timeout=FULL_SUITE_TIMEOUT):
    """Bound the whole expanded suite, retain failure status, and own its cleanup.

    This is a suite orchestration budget, not a browser or individual-test wait.
    Crossing it always fails, even if an interrupt lets pytest finish writing XML.
    """
    reports.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    process = None
    failure = None
    cleanup_error = None
    timed_out = False
    owned = None
    print(f"Handbook full non-PostgreSQL suite: deadline {timeout}s", flush=True)
    try:
        process = subprocess.Popen(argv, cwd=directory, env=env, **process_options())
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            owned = capture_owned_descendants(process)
            if owned is None:
                # Stop the still-owned live tree (taskkill /T on Windows), not
                # an expired leader whose surviving descendants cannot be proven.
                stop_process(process)
            else:
                print("Handbook deadline reached; interrupting owned pytest for JUnit", flush=True)
                try:
                    process.send_signal(signal.SIGINT)
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    pass
                except ProcessLookupError:
                    pass
    except BaseException as error:
        failure = error
    finally:
        if owned is not None:
            try:
                cleanup_owned_descendants(owned)
            except Exception as error:
                cleanup_error = type(error).__name__
        if process is not None and process.poll() is None:
            try:
                stop_process(process)
            except Exception as error:
                cleanup_error = type(error).__name__
        status = {
            "version": 1,
            "phase": "full_non_postgres_tests",
            "timeout_seconds": timeout,
            "timed_out": timed_out,
            "returncode": process.returncode if process is not None else None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "error_type": type(failure).__name__ if failure else None,
            "cleanup_error_type": cleanup_error,
            "owned_processes_at_timeout": len(owned) if owned is not None else None,
            "junit_available": junit.is_file(),
        }
        if junit.is_file():
            (reports / "handbook-tests.xml").write_bytes(junit.read_bytes())
        (reports / "handbook-test-status.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(status), flush=True)
    if timed_out:
        raise subprocess.TimeoutExpired("handbook full non-PostgreSQL suite", timeout)
    if failure:
        raise failure
    if cleanup_error:
        raise RuntimeError("Handbook owned test process cleanup failed: " + cleanup_error)
    if process.returncode:
        raise subprocess.CalledProcessError(
            process.returncode, "handbook full non-PostgreSQL suite"
        )


def main():
    text = OUTPUT.read_bytes()
    expected = json.loads((ROOT / "templates/vendor/manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="rnd-book-only-") as folder:
        base = Path(folder)
        book = base / OUTPUT.name
        book.write_bytes(text)
        destination = base / "student-project"
        count = restore(book, destination)
        rows = extract(text.decode("utf-8"))
        binary_count = sum(isinstance(content, bytes) for content in rows.values())
        assert not list((destination / "templates/vendor").glob("*.zip"))
        env = dict(
            os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8"
        )
        # Installation packages may be reused; project imports MUST come from the restored tree.
        run(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; import workbench.store; "
                "assert Path(workbench.store.__file__).resolve().is_relative_to(Path.cwd())",
            ],
            destination,
            env,
        )
        run([sys.executable, "-m", "scripts.build_handbook"], destination, env)
        assert (destination / OUTPUT.name).read_bytes() == text
        run([sys.executable, "-m", "scripts.vendor_templates", "--fetch"], destination, env)
        actual = json.loads(
            (destination / "templates/vendor/manifest.json").read_text(encoding="utf-8")
        )
        for want, got in zip(expected["sources"], actual["sources"], strict=True):
            # ZIP deflate bytes can differ across zlib versions. Source digests verify content.
            for field in ("name", "sha", "source_digest", "files"):
                assert want[field] == got[field], (field, want["name"])
        # Repacking can change only archive compression metadata; synchronize that
        # locally before running the complete suite, including handbook consistency.
        # The exact original text roundtrip and all upstream source digests above
        # have already been independently checked, not weakened to fit new output.
        run([sys.executable, "-m", "scripts.build_handbook"], destination, env)
        # New staged-doc tests require the generated directory, which is rebuilt
        # from the restored source rather than embedded recursively in this book.
        run([sys.executable, "-m", "scripts.build_learning_docs"], destination, env)
        # Build the optional real Continue component from the textbook's restored files,
        # not from the original project's generated bundle or installed node_modules.
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError(
                "Complete handbook acceptance requires Node 22/npm; see the Node environment step"
            )
        run([npm, "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"], destination, env)
        run([npm, "run", "build", "--prefix", "tools/node"], destination, env)
        env["RND_REQUIRE_NODE_TESTS"] = "1"
        junit = base / "handbook-tests.xml"
        run_full_tests(
            [
                sys.executable,
                "-m",
                "pytest",
                "-m",
                "not postgres",
                "-v",
                "--tb=short",
                f"--junitxml={junit}",
            ],
            destination,
            env,
            junit,
            ROOT / "reports",
        )
        suites = ET.parse(junit).getroot()
        cases = suites.findall(".//testcase")
        if not cases or any(
            case.find("failure") is not None or case.find("error") is not None for case in cases
        ):
            raise AssertionError(
                "Handbook reconstruction must pass the actual full non-PostgreSQL suite"
            )
        report = {
            "passed": True,
            "files_restored": count,
            "text_files_restored": count - binary_count,
            "binary_files_restored": binary_count,
            "original_project_imported": False,
            "original_archives_copied": False,
            "continue_component_rebuilt_from_handbook": True,
            "test_selection": "all non-PostgreSQL tests, including smart recommendation and independent delivery",
            "tests_passed": sum(case.find("skipped") is None for case in cases),
            "tests_skipped": sum(case.find("skipped") is not None for case in cases),
            "third_party_fixed_revisions_rebuilt": len(actual["sources"]),
            "handbook_sha256": hashlib.sha256(text).hexdigest(),
        }
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports/handbook-clean-room.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
````
