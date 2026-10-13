# workbench/infrastructure/sandbox/deadline.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `CheckpointExpired`（L10–L11）：继承`BaseException`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `CheckpointDeadline`（L14–L64）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `CheckpointDeadline.__init__`（L15–L27）：接收`deadline`。 控制顺序：L16按`type(deadline) not in (int, float) or not math.isfinite(deadline) or not 10 < deadlin…`分支；L23抛异常，停止当前正常路径。 调用`type`、`math.isfinite`、`time.monotonic`、`hasattr`、`threading.current_thread`、`threading.main_thread`、`ValueError`、`threading.Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CheckpointDeadline.enter_cleanup`（L29–L31）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.wake.set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CheckpointDeadline.expire`（L33–L42）：接收`signum`、`frame`。 控制顺序：L34按`self.closed`分支；L37按`time.monotonic() < end`分支；L39按`self.cleanup`分支；L42抛异常，停止当前正常路径。 调用`time.monotonic`、`self.enter_cleanup`、`CheckpointExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CheckpointDeadline.watch`（L44–L52）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L45在`not self.closed`成立时循环；L47按`self.wake.wait(max(0, end - time.monotonic()))`分支；L50按`not self.closed`分支。 调用`self.wake.wait`、`max`、`time.monotonic`、`self.wake.clear`、`os.kill`、`os.getpid`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CheckpointDeadline.__enter__`（L54–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`signal.signal`、`threading.Thread`、`self.thread.start`。 返回路径：L58的`self`。
- `CheckpointDeadline.__exit__`（L60–L64）：接收`*args`。 调用`self.wake.set`、`self.thread.join`、`signal.signal`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/infrastructure/sandbox/deadline.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L64。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2112`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/deadline.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5f903bab7a45a9cd460c85494d47636a746f472fd631fff1a41c760369299eef"} -->
````python
# workbench/infrastructure/sandbox/deadline.py
"""Deadline for a dedicated verifier process, independent of SDK SIGALRM timers."""

import math
import os
import signal
import threading
import time


class CheckpointExpired(BaseException):
    """Escape SDK Exception handlers into owned cleanup; never business feedback."""


class CheckpointDeadline:
    def __init__(self, deadline):
        if (
            type(deadline) not in (int, float)
            or not math.isfinite(deadline)
            or not 10 < deadline - time.monotonic() <= 180
            or not hasattr(signal, "SIGUSR1")
            or threading.current_thread() is not threading.main_thread()
        ):
            raise ValueError("Checkpoint requires a dedicated POSIX process and cleanup reserve")
        self.deadline = deadline
        self.cleanup = False
        self.closed = False
        self.wake = threading.Event()

    def enter_cleanup(self):
        self.cleanup = True
        self.wake.set()

    def expire(self, signum, frame):
        if self.closed:
            return
        end = self.deadline if self.cleanup else self.deadline - 10
        if time.monotonic() < end:
            return  # A queued soft signal cannot interrupt an already-started cleanup.
        if self.cleanup:
            self.closed = True
        self.enter_cleanup()
        raise CheckpointExpired("Checkpoint deadline exhausted")

    def watch(self):
        while not self.closed:
            end = self.deadline if self.cleanup else self.deadline - 10
            if self.wake.wait(max(0, end - time.monotonic())):
                self.wake.clear()
                continue
            if not self.closed:
                os.kill(os.getpid(), signal.SIGUSR1)
            self.wake.wait(0.01)

    def __enter__(self):
        self.previous = signal.signal(signal.SIGUSR1, self.expire)
        self.thread = threading.Thread(target=self.watch, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.closed = True
        self.wake.set()
        self.thread.join(timeout=0.2)
        signal.signal(signal.SIGUSR1, self.previous)
````
