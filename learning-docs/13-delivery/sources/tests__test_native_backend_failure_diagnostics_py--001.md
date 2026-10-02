# tests/test_native_backend_failure_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure`（L18–L134）：接收`tmp_path`、`monkeypatch`、`primary`、`cleanup`。 源码说明：Portable control-flow fakes, including the Windows unobservable-proc path.。 控制顺序：L49按`hasattr(native.os, "killpg")`分支；L89按`cleanup == "close"`分支；L97按`cleanup == "receipt"`分支；L110按`primary == "body"`分支；L111抛异常，停止当前正常路径；L112断言`primary is None`；L113断言`stopped == [process.pid]`；L114按`primary == "exit"`分支。后续分支沿下方源码相同行号继续阅读。 调用`Process`、`monkeypatch.setattr`、`itertools.count`、`next`、`hasattr`、`pytest.fail`、`LookupError`、`pytest.raises`、`native.running_backend`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Process`（L23–L28）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Process.poll`（L27–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L28的`self.returncode`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.stop`（L41–L46）：接收`owned`。 控制顺序：L42断言`owned is process`；L44按`cleanup == "stop"`分支；L45抛异常，停止当前正常路径。 调用`stopped.append`、`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client`（L54–L73）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.__init__`（L55–L56）：接收`**kwargs`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.__enter__`（L58–L59）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L59的`self`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.__exit__`（L61–L62）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.get`（L64–L73）：接收`url`。 控制顺序：L65断言`primary != "exit"`。 调用`Response`。 返回路径：L73的`Response()`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.get.Response`（L67–L71）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Client.get.Response.json`（L70–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L71的`{"paths": {}}`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Log`（L78–L87）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Log.__init__`（L79–L80）：接收`stream`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Log.tell`（L82–L83）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.stream.tell`。 返回路径：L83的`self.stream.tell()`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.Log.close`（L85–L87）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87抛异常，停止当前正常路径。 调用`self.stream.close`、`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.opened`（L91–L93）：接收`path`、`*args`、`**kwargs`。 调用`original_open`、`Log`。 返回路径：L93的`Log(stream) if path.name == "backend-runtime.log" else stream`。
- `test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure.write`（L99–L102）：接收`path`、`value`。 控制顺序：L100按`path.name == "backend-lifecycle.json" and value.get("phase") == "backend-cleanup"`分支；L101抛异常，停止当前正常路径。 调用`value.get`、`OSError`、`original_write`。 返回路径：L102的`original_write(path, value)`。
- `test_real_failed_child_retains_exit_code_and_never_kills_new_foreign_listener`（L140–L185）：接收`tmp_path`、`monkeypatch`。 控制顺序：L174断言`result["returncode_before_cleanup"] == result["returncode"] == 42`；L175断言`result["port_released"] is False`；L176断言`result["port_state_after_cleanup"]["owned_listener"] is False`；L177断言`result["port_state_after_cleanup"]["local_port_state_counts"]["0A"] == 1`；L178断言`result["port_state_after_cleanup"]["owned_group_pids"] == []`；L179断言`foreign.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) == 1`；L180断言`"specific child startup failure" in ( tmp_path / "report/backend-runtime.log" ).read_…`；L183断言`"port_released=False" in raised.value.__notes__[0]`。 调用`socket.socket`、`foreign.bind`、`foreign.getsockname`、`monkeypatch.setattr`、`pytest.fail`、`itertools.count`、`next`、`pytest.raises`、`native.running_backend`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_failed_child_retains_exit_code_and_never_kills_new_foreign_listener.start`（L149–L157）：接收`command`、`**kwargs`。 调用`original`、`child.wait`、`foreign.bind`、`foreign.listen`。 返回路径：L157的`child`。
- `test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset`（L188–L216）：接收`tmp_path`、`monkeypatch`。 控制顺序：L204遍历`(1, 2)`；L213断言`result["startup_attempt"] == attempt`；L214断言`result["runtime_log_start_bytes"] == (attempt - 1) * len( b"failure from this attempt…`。 调用`monkeypatch.setattr`、`pytest.raises`、`native.running_backend`、`pytest.fail`、`json.loads`、`(tmp_path / "report/backend-lifecycle.json").read_text`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset.Process`（L191–L195）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset.Process.poll`（L194–L195）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L195的`42`。
- `test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset.start`（L197–L199）：接收`command`、`**kwargs`。 调用`kwargs["stdout"].write`、`Process`。 返回路径：L199的`Process()`。

</details>

**创建路径：** `tests/test_native_backend_failure_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L216。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7776`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_backend_failure_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "eb4f3f4f48746bf14309c416f6ef29655aaa632dd2fb504cab09a0b0cce9f004"} -->
````python
# tests/test_native_backend_failure_diagnostics.py
"""Primary backend failures remain visible when owned cleanup also fails."""

import itertools
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from workbench import native_environment as native


@pytest.mark.parametrize("primary", ["exit", "body", None])
@pytest.mark.parametrize("cleanup", ["occupied", "stop", "close", "receipt"])
def test_backend_primary_error_survives_cleanup_without_accepting_cleanup_failure(
    tmp_path, monkeypatch, primary, cleanup
):
    """Portable control-flow fakes, including the Windows unobservable-proc path."""

    class Process:
        pid = 12345678
        returncode = 42 if primary == "exit" else None

        def poll(self):
            return self.returncode

    process = Process()
    monkeypatch.setattr(native.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(native, "backend_port_state", lambda *args: {"observable": False})
    binds = itertools.count()
    monkeypatch.setattr(
        native, "loopback_port_bindable", lambda port: next(binds) == 0 or cleanup != "occupied"
    )
    times = itertools.count(0, 6)
    monkeypatch.setattr(native.time, "monotonic", lambda: next(times))
    stopped = []

    def stop(owned):
        assert owned is process
        stopped.append(owned.pid)
        if cleanup == "stop":
            raise OSError("explicit synthetic stop error")
        process.returncode = process.returncode if process.returncode is not None else -9

    monkeypatch.setattr(native, "stop_process", stop)
    if hasattr(native.os, "killpg"):
        monkeypatch.setattr(
            native.os, "killpg", lambda *args: pytest.fail("no observed group to kill")
        )

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url):
            assert primary != "exit"

            class Response:
                status_code = 200

                def json(self):
                    return {"paths": {}}

            return Response()

    monkeypatch.setattr(native.httpx, "Client", Client)
    original_open = Path.open

    class Log:
        def __init__(self, stream):
            self.stream = stream

        def tell(self):
            return self.stream.tell()

        def close(self):
            self.stream.close()
            raise OSError("explicit synthetic log close error")

    if cleanup == "close":

        def opened(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            return Log(stream) if path.name == "backend-runtime.log" else stream

        monkeypatch.setattr(Path, "open", opened)
    original_write = native.write_json
    if cleanup == "receipt":

        def write(path, value):
            if path.name == "backend-lifecycle.json" and value.get("phase") == "backend-cleanup":
                raise OSError("explicit synthetic receipt error")
            return original_write(path, value)

        monkeypatch.setattr(native, "write_json", write)
    body_failure = LookupError("original body error")
    with pytest.raises((RuntimeError, LookupError, OSError)) as raised:
        with native.running_backend(
            "fastapiadmin", tmp_path, {"SERVER_PORT": "18080"}, tmp_path / "report"
        ):
            if primary == "body":
                raise body_failure
            assert primary is None
    assert stopped == [process.pid]
    if primary == "exit":
        assert str(raised.value) == "Native backend exited; inspect backend-runtime.log"
    elif primary == "body":
        assert raised.value is body_failure
    elif cleanup == "occupied":
        assert "port remained occupied" in str(raised.value)
    else:
        assert isinstance(raised.value, OSError)
    if primary:
        assert any("cleanup also failed" in note for note in raised.value.__notes__)
    if cleanup != "receipt":
        report = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert report["cleanup_failure"]
        assert report["port_released"] is (cleanup == "close")
        assert report["returncode_before_cleanup"] == (42 if primary == "exit" else None)
        if primary:
            assert report["failure"]["phase"] == (
                "backend-readiness" if primary == "exit" else "backend-running"
            )


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/net/tcp").is_file(), reason="Linux /proc ownership facts"
)
def test_real_failed_child_retains_exit_code_and_never_kills_new_foreign_listener(
    tmp_path, monkeypatch
):
    with socket.socket() as foreign:
        foreign.bind(("127.0.0.1", 0))
        port = foreign.getsockname()[1]
    original = subprocess.Popen
    foreign = socket.socket()

    def start(command, **kwargs):
        child = original(
            [sys.executable, "-c", "print('specific child startup failure'); raise SystemExit(42)"],
            **kwargs,
        )
        child.wait(timeout=10)
        foreign.bind(("127.0.0.1", port))
        foreign.listen()
        return child

    monkeypatch.setattr(native.subprocess, "Popen", start)
    monkeypatch.setattr(
        native.os, "killpg", lambda *args: pytest.fail("foreign process must survive")
    )
    times = itertools.count(0, 6)
    monkeypatch.setattr(native.time, "monotonic", lambda: next(times))
    try:
        with pytest.raises(RuntimeError, match="Native backend exited") as raised:
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": str(port)}, tmp_path / "report"
            ):
                pytest.fail("child exited before readiness")
        result = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert result["returncode_before_cleanup"] == result["returncode"] == 42
        assert result["port_released"] is False
        assert result["port_state_after_cleanup"]["owned_listener"] is False
        assert result["port_state_after_cleanup"]["local_port_state_counts"]["0A"] == 1
        assert result["port_state_after_cleanup"]["owned_group_pids"] == []
        assert foreign.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) == 1
        assert "specific child startup failure" in (
            tmp_path / "report/backend-runtime.log"
        ).read_text(encoding="utf-8")
        assert "port_released=False" in raised.value.__notes__[0]
    finally:
        foreign.close()


def test_repeated_backend_attempts_preserve_attempt_number_and_runtime_log_offset(
    tmp_path, monkeypatch
):
    class Process:
        pid = 12345678

        def poll(self):
            return 42

    def start(command, **kwargs):
        kwargs["stdout"].write(b"failure from this attempt\n")
        return Process()

    monkeypatch.setattr(native.subprocess, "Popen", start)
    monkeypatch.setattr(native, "loopback_port_bindable", lambda port: True)
    monkeypatch.setattr(native, "backend_port_state", lambda *args: {"observable": False})
    for attempt in (1, 2):
        with pytest.raises(RuntimeError, match="Native backend exited"):
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": "18080"}, tmp_path / "report"
            ):
                pytest.fail("explicit exited process fake")
        result = json.loads(
            (tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8")
        )
        assert result["startup_attempt"] == attempt
        assert result["runtime_log_start_bytes"] == (attempt - 1) * len(
            b"failure from this attempt\n"
        )
````
