# workbench/owned_lifecycle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：只控制本次启动的服务并核实退出。** 启动器、进程与端口属于一次明确生命周期；结束时先等待和检查，再验证端口关闭。重启必须是新进程，不能让残留服务冒充成功，也不能为释放端口终止别人的应用。

**对应关系：** Daytona矩阵和独立原生启动器复验 → 所拥有的进程 → services_stopped证据；test_owned_lifecycle。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `stop_native`（L12–L39）：接收`process`、`ports`。 源码说明：Drain the independent launcher's ExitStack before claiming a real restart. Backend and frontend own separate sessions. Killing only the parent can leave them alive. A restart is allowed only after all。 控制顺序：L18按`process.poll() is None`分支；L27抛异常，停止当前正常路径；L28遍历`range(40)`；L30遍历`ports`；L33按`connection.connect_ex(("127.0.0.1", port)) == 0`分支；L35按`not listening`分支；L37按`attempt == 39`分支；L38抛异常，停止当前正常路径。 调用`process.poll`、`os.killpg`、`process.wait`、`stop_process`、`RuntimeError`、`range`、`socket.socket`、`connection.settimeout`、`connection.connect_ex`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/owned_lifecycle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L39。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1330`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/owned_lifecycle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db84fbab1cfa381223fa8d1a452807fc4813ecc46c5f28892abff04e0970f963"} -->
````python
# workbench/owned_lifecycle.py
"""Linux sandbox ownership checks for independent launcher shutdown and real restart."""

import os
import signal
import socket
import subprocess
import time

from workbench.tools import stop_process


def stop_native(process, ports):
    """Drain the independent launcher's ExitStack before claiming a real restart.

    Backend and frontend own separate sessions. Killing only the parent can leave
    them alive. A restart is allowed only after all owned server ports are closed.
    """
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGINT)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise RuntimeError("Standalone launcher did not drain its child processes") from None
    for attempt in range(40):
        listening = []
        for port in ports:
            with socket.socket() as connection:
                connection.settimeout(0.2)
                if connection.connect_ex(("127.0.0.1", port)) == 0:
                    listening.append(port)
        if not listening:
            return
        if attempt == 39:
            raise RuntimeError("Standalone shutdown left an application server listening")
        time.sleep(0.25)
````
