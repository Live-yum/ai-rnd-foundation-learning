# workbench/tools.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：有界子进程、清洁环境与失败证据。** run_command只执行参数数组而非拼接shell，限定目录和时间；超时停止进程树。输出落入临时文件防止内存无限增长，读取尾部形成ToolFailure证据。clean_env过滤凭据并强制禁用遥测，Docker显式走本机。

**对应关系：** 生成/构建/测试适配器 → tools → 本机进程；runtime保存tool-failure报告。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.local_only`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ToolFailure`（L13–L14）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `clean_env`（L17–L51）：接收`extra`。 控制顺序：L34按`os.environ.get("RND_OFFLINE_TOOLS") == "1"`分支；L46按`os.environ.get("RND_OFFLINE_TOOLS") == "1"`分支。 调用`os.environ.get`、`names.update`、`os.environ.items`、`k.upper`、`env.update`。 返回路径：L51的`env`。
- `stop_process`（L54–L69）：接收`process`。 控制顺序：L55按`process.poll() is not None`分支；L57按`os.name == "nt"`分支。 调用`process.poll`、`subprocess.run`、`str`、`os.killpg`、`process.wait`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `process_options`（L72–L77）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L73的`{"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new…`。
- `memory_status`（L80–L91）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Non-sensitive Linux build diagnostics; no process environment or command lines.。 控制顺序：L83按`not path.is_file()`分支。 调用`Path`、`path.is_file`、`line.split`、`int`、`path.read_text().splitlines`、`path.read_text`。 返回路径：L84的`"memory unavailable"`；L89的`f"available MiB={values['MemAvailable'] // 1024}; swap free MiB={values['SwapFree'] // 102…`；L91的`"memory unavailable"`。
- `run_command`（L94–L155）：接收`command`、`cwd`、`timeout`、`extra_env`、`heartbeat`。 控制顺序：L95按`not command or not all(isinstance(v, str) for v in command)`分支；L96抛异常，停止当前正常路径；L111抛异常，停止当前正常路径；L115在`True`成立时循环；L117按`remaining <= 0`分支；L118抛异常，停止当前正常路径；L123按`not heartbeat`分支；L124抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`all`、`isinstance`、`ValueError`、`local_docker_command`、`tempfile.TemporaryFile`、`subprocess.Popen`、`Path`、`clean_env`、`process_options`等。 返回路径：L155的`{"command": command, "returncode": code, "log": log}`。

</details>

**创建路径：** `workbench/tools.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L155。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5279`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/tools.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6674521e19748a4a779874e9e6b772984ad1cc74a3a9854700446a1bebf0c232"} -->
````python
# workbench/tools.py
"""Fixed-command execution for trusted tools, not a sandbox for arbitrary model code."""

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from workbench.local_only import TELEMETRY_OFF, local_docker_command


class ToolFailure(RuntimeError):
    pass


def clean_env(extra=None):
    names = {
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "TEMP",
        "TMP",
        "HOME",
        "USERPROFILE",
        "LOCALAPPDATA",
        "APPDATA",
        "SSL_CERT_FILE",
    }
    # These controls are inherited only inside an explicitly prepared offline image.
    # Keep cloud credentials, proxy variables and arbitrary model environment excluded.
    if os.environ.get("RND_OFFLINE_TOOLS") == "1":
        names.update(
            {
                "RND_OFFLINE_TOOLS",
                "UV_CACHE_DIR",
                "UV_PYTHON_INSTALL_DIR",
                "UV_PYTHON_PREFERENCE",
                "PLAYWRIGHT_BROWSERS_PATH",
                "JAVA_HOME",
            }
        )
    env = {k: v for k, v in os.environ.items() if k.upper() in names}
    if os.environ.get("RND_OFFLINE_TOOLS") == "1":
        env.update(UV_OFFLINE="1", COREPACK_ENABLE_NETWORK="0")
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    env.update(extra or {})
    env.update(TELEMETRY_OFF)
    return env


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=15,
            check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=15)


def process_options():
    return (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )


def memory_status():
    """Non-sensitive Linux build diagnostics; no process environment or command lines."""
    path = Path("/proc/meminfo")
    if not path.is_file():
        return "memory unavailable"
    try:
        values = {
            line.split(":")[0]: int(line.split()[1]) for line in path.read_text().splitlines()
        }
        return f"available MiB={values['MemAvailable'] // 1024}; swap free MiB={values['SwapFree'] // 1024}"
    except OSError, ValueError, KeyError:
        return "memory unavailable"


def run_command(command, cwd, timeout=120, extra_env=None, *, heartbeat=None):
    if not command or not all(isinstance(v, str) for v in command):
        raise ValueError("工具参数必须是明确的字符串数组")
    command = local_docker_command(command)
    with tempfile.TemporaryFile() as output:
        try:
            process = subprocess.Popen(
                command,
                cwd=Path(cwd),
                env=clean_env(extra_env),
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.STDOUT,
                shell=False,
                **process_options(),
            )
        except OSError:
            raise ToolFailure("无法启动已登记工具，请检查其安装和 PATH") from None
        timed_out = False
        try:
            started = time.monotonic()
            while True:
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command[0], timeout)
                try:
                    code = process.wait(timeout=min(15, remaining) if heartbeat else remaining)
                    break
                except subprocess.TimeoutExpired:
                    if not heartbeat:
                        raise
                    print(
                        f"{heartbeat}: running {int(time.monotonic() - started)}s; "
                        f"log bytes={os.fstat(output.fileno()).st_size}; {memory_status()}",
                        flush=True,
                    )
        except subprocess.TimeoutExpired:
            stop_process(process)
            code, timed_out = process.returncode, True
        # Preserve the diagnostic tail (Maven/Vite usually print the failure last),
        # without loading an unbounded tool log into the platform process.
        size = output.seek(0, os.SEEK_END)
        output.seek(0)
        head = output.read(32000)
        if size > 64000:
            output.seek(-32000, os.SEEK_END)
            raw = head + b"\n... [middle omitted] ...\n" + output.read(32000)
        else:
            raw = head + output.read(32000)
        log = raw.decode("utf-8", errors="replace")
        if code or timed_out:
            message = (
                "工具执行超时，已终止进程组"
                if timed_out
                else f"工具退出码 {code}；检查本次运行的工具日志"
            )
            error = ToolFailure(message)
            error.log = log
            error.returncode = code
            error.timed_out = timed_out
            raise error
        return {"command": command, "returncode": code, "log": log}
````
