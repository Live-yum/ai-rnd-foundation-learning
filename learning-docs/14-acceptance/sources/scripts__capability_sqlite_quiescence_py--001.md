# scripts/capability_sqlite_quiescence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_sqlite_quiescence；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `task_inventory`（L23–L49）：接收`uid`。 源码说明：Include live worker threads even when their group leader is a zombie.。 控制顺序：L26按`len(paths) > MAX_TASKS`分支；L27抛异常，停止当前正常路径；L29遍历`paths`；L34按`uid not in uids or state in {"Z", "X"}`分支。 调用`list`、`pathlib.Path("/proc").glob`、`pathlib.Path`、`len`、`RuntimeError`、`dict`、`line.split`、`path.read_text().splitlines`、`path.read_text`等。 返回路径：L49的`tasks`。
- `ApplicationPause`（L52–L117）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ApplicationPause.__init__`（L53–L57）：接收`deadline`、`uid`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ApplicationPause._stop`（L59–L73）：接收`pid`。 控制顺序：L60按`pid not in self.handles`分支；L67按`self.uid not in [int(value) for value in fields["Uid"].split()]`分支；L68抛异常，停止当前正常路径；L71抛异常，停止当前正常路径。 调用`os.pidfd_open`、`dict`、`line.split`、`pathlib.Path("/proc", str(pid), "status").read_text().splitlines`、`pathlib.Path("/proc", str(pid), "status").read_text`、`pathlib.Path`、`str`、`int`、`fields["Uid"].split`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ApplicationPause.__enter__`（L75–L95）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78在`time.monotonic() < self.deadline`成立时循环；L80按`not current`分支；L81抛异常，停止当前正常路径；L82按`all(value[0] == "T" for value in current.values()) and current == previous`分支；L85遍历`{pid for pid, _ in current}`；L92抛异常，停止当前正常路径；L95抛异常，停止当前正常路径。 调用`time.monotonic`、`task_inventory`、`RuntimeError`、`all`、`current.values`、`self._stop`、`time.sleep`、`TimeoutError`、`self.resume`。 返回路径：L84的`self`。
- `ApplicationPause.verify`（L97–L99）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L98按`self.baseline is None or task_inventory(self.uid) != self.baseline`分支；L99抛异常，停止当前正常路径。 调用`task_inventory`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ApplicationPause.resume`（L101–L114）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103遍历`self.handles.values()`；L113按`failed`分支；L114抛异常，停止当前正常路径。 调用`self.handles.values`、`signal.pidfd_send_signal`、`os.close`、`self.handles.clear`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ApplicationPause.__exit__`（L116–L117）：接收`*exc`。 调用`self.resume`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `supervise`（L120–L138）：接收`argv`、`budget`。 控制顺序：L121按`not 0 < budget <= 12`分支；L122抛异常，停止当前正常路径；L126按`remaining <= 0`分支；L127抛异常，停止当前正常路径；L135按`result.returncode or len(result.stdout) > 65536`分支；L136抛异常，停止当前正常路径。 调用`ValueError`、`time.monotonic`、`ApplicationPause`、`min`、`TimeoutError`、`subprocess.run`、`pause.verify`、`len`、`RuntimeError`。 返回路径：L138的`result.stdout`。
- `main`（L141–L152）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`signal.signal`、`float`、`supervise`、`sys.stdout.buffer.write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.interrupted`（L142–L143）：接收`signum`、`frame`。 控制顺序：L143抛异常，停止当前正常路径。 调用`TimeoutError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/capability_sqlite_quiescence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L156。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5776`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_sqlite_quiescence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "361e89edb84869cef02466687d24f1f53603badf25251b7a5f54a03535f87922"} -->
````python
# scripts/capability_sqlite_quiescence.py
"""Bounded, resumable application pause inside an already isolated sandbox.

The controller sends this trusted stdlib-only source to the sandbox's root
control interpreter. It is never imported from the candidate product. Signals
target only its dedicated application identity, through pinned pidfds. The
reader is a separately bounded child so a failed SQLite read cannot strand the
application in a stopped state. Container deletion remains the outer fail-safe
if the supervisor itself is forcibly killed.
"""

import os
import pathlib
import signal
import subprocess
import sys
import time

APP_UID = 20000
MAX_TASKS = 4096
GONE_PROCESS = (FileNotFoundError, ProcessLookupError)


def task_inventory(uid=APP_UID):
    """Include live worker threads even when their group leader is a zombie."""
    paths = list(pathlib.Path("/proc").glob("[0-9]*/task/[0-9]*/status"))
    if len(paths) > MAX_TASKS:
        raise RuntimeError("Application task inventory budget exceeded")
    tasks = {}
    for path in paths:
        try:
            fields = dict(line.split(":", 1) for line in path.read_text().splitlines())
            uids = tuple(int(value) for value in fields["Uid"].split())
            state = fields["State"].split()[0]
            if uid not in uids or state in {"Z", "X"}:
                continue
            # Start time plus monotonic scheduling counters bind each stopped
            # thread. Rechecking these after the read detects even a cooperating
            # sibling's SIGCONT/write/SIGSTOP race that ended stopped again.
            start = int(path.with_name("stat").read_text().rsplit(")", 1)[1].split()[19])
            tasks[int(fields["Tgid"]), int(fields["Pid"])] = (
                state,
                uids,
                start,
                int(fields["voluntary_ctxt_switches"]),
                int(fields["nonvoluntary_ctxt_switches"]),
            )
        except GONE_PROCESS:
            pass
    return tasks


class ApplicationPause:
    def __init__(self, deadline, *, uid=APP_UID):
        self.deadline = deadline
        self.uid = uid
        self.handles = {}
        self.baseline = None

    def _stop(self, pid):
        if pid not in self.handles:
            fd = os.pidfd_open(pid)
            try:
                fields = dict(
                    line.split(":", 1)
                    for line in pathlib.Path("/proc", str(pid), "status").read_text().splitlines()
                )
                if self.uid not in [int(value) for value in fields["Uid"].split()]:
                    raise RuntimeError("Application identity changed during pause")
            except BaseException:
                os.close(fd)
                raise
            self.handles[pid] = fd
        signal.pidfd_send_signal(self.handles[pid], signal.SIGSTOP)

    def __enter__(self):
        try:
            previous = None
            while time.monotonic() < self.deadline:
                current = task_inventory(self.uid)
                if not current:
                    raise RuntimeError("No live application identity to pause")
                if all(value[0] == "T" for value in current.values()) and current == previous:
                    self.baseline = current
                    return self
                for pid in {pid for pid, _ in current}:
                    try:
                        self._stop(pid)
                    except GONE_PROCESS:
                        pass
                previous = current
                time.sleep(0.01)
            raise TimeoutError("Application did not reach stable quiescence")
        except BaseException:
            self.resume()
            raise

    def verify(self):
        if self.baseline is None or task_inventory(self.uid) != self.baseline:
            raise RuntimeError("Application ran or changed during physical observation")

    def resume(self):
        failed = False
        for fd in self.handles.values():
            try:
                signal.pidfd_send_signal(fd, signal.SIGCONT)
            except ProcessLookupError:
                pass
            except OSError:
                failed = True
            finally:
                os.close(fd)
        self.handles.clear()
        if failed:
            raise RuntimeError("Application resume was not confirmed")

    def __exit__(self, *exc):
        self.resume()


def supervise(argv, budget):
    if not 0 < budget <= 12:
        raise ValueError("Invalid quiescence deadline")
    end = time.monotonic() + budget
    with ApplicationPause(min(end, time.monotonic() + 3)) as pause:
        remaining = end - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Physical observation deadline expired")
        result = subprocess.run(
            argv,
            capture_output=True,
            timeout=min(remaining, 5),
            check=False,
        )
        pause.verify()
        if result.returncode or len(result.stdout) > 65536:
            raise RuntimeError("Physical reader failed")
    # No successful receipt escapes until all pinned process groups were resumed.
    return result.stdout


def main():
    def interrupted(signum, frame):
        raise TimeoutError("Physical observation interrupted")

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    # Only a random root-private request path crosses the process boundary.
    # The reader opens it after ApplicationPause succeeds; no challenge/key/
    # expected value is ever exposed through argv or the inherited environment.
    budget = float(sys.argv[2])
    output = supervise([sys.executable, "-I", "-S", "-c", sys.argv[3], sys.argv[1]], budget)
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
````
