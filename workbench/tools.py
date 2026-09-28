"""Fixed-command execution for trusted tools, not a sandbox for arbitrary model code."""

import os
import signal
import subprocess
import tempfile
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


def run_command(command, cwd, timeout=120, extra_env=None):
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
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise ToolFailure("工具执行超时，已终止进程组") from None
        output.seek(0)
        log = output.read(64000).decode("utf-8", errors="replace")
        if code:
            error = ToolFailure(f"工具退出码 {code}；检查本次运行的工具日志")
            error.log = log
            error.returncode = code
            raise error
        return {"command": command, "returncode": code, "log": log}
