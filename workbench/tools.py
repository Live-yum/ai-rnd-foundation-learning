"""Fixed-command execution for trusted tools, not a sandbox for arbitrary model code."""

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path


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
    env = {k: v for k, v in os.environ.items() if k.upper() in names}
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    env.update(extra or {})
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
