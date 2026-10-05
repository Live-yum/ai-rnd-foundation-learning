# scripts/ci_process_supervisor.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_process_supervisor；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `identity`（L16–L21）：接收`pid`。 调用`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") "…`、`Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit`、`Path(f"/proc/{pid}/stat").read_text`、`Path`、`int`。 返回路径：L19的`int(fields[1]), fields[19]`；L21的`None`。
- `descendants`（L24–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L27遍历`Path("/proc").iterdir()`；L28按`path.name.isdecimal() and (value := identity(int(path.name)))`分支；L31在`children := { pid for pid, value in snapshot.items() if value[0] …`成立时循环。 调用`os.getpid`、`Path("/proc").iterdir`、`Path`、`path.name.isdecimal`、`identity`、`int`、`snapshot.items`、`owned.update`。 返回路径：L35的`{pid: snapshot[pid][1] for pid in owned if pid != root}`。
- `cleanup`（L38–L59）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L40在`True`成立时循环；L43遍历`descendants().items()`；L45按`current is not None and current[1] == started`分支；L50在`True`成立时循环；L55按`pid == 0`分支；L57按`time.monotonic() >= deadline`分支；L58抛异常，停止当前正常路径。 调用`time.monotonic`、`descendants().items`、`descendants`、`identity`、`os.kill`、`os.waitpid`、`RuntimeError`、`time.sleep`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L62–L80）：接收`argv`。 控制顺序：L63按`sys.platform != "linux" or not argv`分支；L64抛异常，停止当前正常路径；L68按`libc.prctl(36, 1, 0, 0, 0) != 0`分支；L69抛异常，停止当前正常路径；L76按`returncode < 0`分支；L77按`-returncode not in {signal.SIGKILL, signal.SIGSTOP}`分支。 调用`RuntimeError`、`ctypes.CDLL`、`libc.prctl`、`OSError`、`ctypes.get_errno`、`subprocess.Popen`、`child.wait`、`cleanup`、`signal.signal`等。 返回路径：L80的`returncode`。

</details>

**创建路径：** `scripts/ci_process_supervisor.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L84。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2788`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_process_supervisor.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0ea193c2fa74ef2b8a1a2e9f555f3c1026fa7486056a9fbc8a01fb63d4e7ef68"} -->
````python
# scripts/ci_process_supervisor.py
"""Linux-only stdlib child supervisor; no project/runtime imports or global settings.

An independent process-local subreaper keeps even double-forked descendants owned
until cleanup. It launches exactly one supplied argv, never a shell command.
"""

import ctypes
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
        return int(fields[1]), fields[19]
    except OSError, ValueError, IndexError:
        return None


def descendants():
    root = os.getpid()
    snapshot = {}
    for path in Path("/proc").iterdir():
        if path.name.isdecimal() and (value := identity(int(path.name))):
            snapshot[int(path.name)] = value
    owned = {root}
    while children := {
        pid for pid, value in snapshot.items() if value[0] in owned and pid not in owned
    }:
        owned.update(children)
    return {pid: snapshot[pid][1] for pid in owned if pid != root}


def cleanup():
    deadline = time.monotonic() + 10
    while True:
        # Every adopted child belongs to this dedicated supervisor's only target.
        # Keep start identity checks even though PID recycling is unlikely here.
        for pid, started in descendants().items():
            current = identity(pid)
            if current is not None and current[1] == started:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                return
            if pid == 0:
                break
        if time.monotonic() >= deadline:
            raise RuntimeError("Owned supervisor descendants did not exit")
        time.sleep(0.01)


def main(argv):
    if sys.platform != "linux" or not argv:
        raise RuntimeError("The subreaper supervisor requires Linux and an explicit argv")
    libc = ctypes.CDLL(None, use_errno=True)
    # PR_SET_CHILD_SUBREAPER applies only to this disposable process, not its
    # parent, other jobs, host policy, credentials, or future processes.
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "Cannot establish owned child supervision")
    child = None
    try:
        child = subprocess.Popen(argv)
        returncode = child.wait()
    finally:
        cleanup()
    if returncode < 0:
        if -returncode not in {signal.SIGKILL, signal.SIGSTOP}:
            signal.signal(-returncode, signal.SIG_DFL)
        os.kill(os.getpid(), -returncode)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
````
