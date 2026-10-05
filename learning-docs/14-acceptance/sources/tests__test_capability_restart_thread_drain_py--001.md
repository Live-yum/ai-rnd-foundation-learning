# tests/test_capability_restart_thread_drain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_restart_inventory_sees_live_thread_under_zombie_group_leader`（L18–L61）：接收`monkeypatch`。 控制顺序：L49在`True`成立时循环；L51按`status["State"].strip().startswith("Z")`分支；L53断言`time.monotonic() < deadline`；L56断言`len(tasks) >= 2`；L57断言`child.pid in namespace["live"]()`；L58断言`namespace["live"]().count(child.pid) == 1`。 调用`monkeypatch.setattr`、`capability_sandbox.restart_application_identity`、`ast.parse`、`next`、`isinstance`、`os.getuid`、`exec`、`compile`、`ast.Module`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restart_inventory_sees_live_thread_under_zombie_group_leader.capture`（L23–L25）：接收`_sandbox`、`argv`、`_timeout`。 调用`scripts.append`、`argv.index`、`SimpleNamespace`。 返回路径：L25的`SimpleNamespace(exit_code=0)`。

</details>

**创建路径：** `tests/test_capability_restart_thread_drain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L61。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2171`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_restart_thread_drain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b08a4efcabbfe39242e200cd904aa5276fcdd34163e978258f4639d885be5cc1"} -->
````python
# tests/test_capability_restart_thread_drain.py
"""Read-only process inventory regression; signal only our synthetic child.

Never execute the production UID-wide drain against the test host.
"""

import ast
import os
import pathlib
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest


@pytest.mark.skipif(sys.platform != "linux", reason="Linux thread-group /proc semantics")
def test_restart_inventory_sees_live_thread_under_zombie_group_leader(monkeypatch):
    from workbench import capability_sandbox

    scripts = []

    def capture(_sandbox, argv, _timeout):
        scripts.append(argv[argv.index("-c") + 1])
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(capability_sandbox, "control_exec", capture)
    capability_sandbox.restart_application_identity(None, 8123, 5)
    # Extract only the read-only inventory function, never the signal loop.
    tree = ast.parse(scripts[0])
    inventory = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "live"
    )
    namespace = {"pathlib": pathlib, "uid": os.getuid()}
    exec(
        compile(ast.Module(body=[inventory], type_ignores=[]), "<read-only-inventory>", "exec"),
        namespace,
    )

    source = (
        "import threading,time,ctypes; "
        "threading.Thread(target=lambda:time.sleep(30),daemon=True).start(); "
        "ctypes.CDLL(None).pthread_exit(None)"
    )
    child = subprocess.Popen([sys.executable, "-I", "-S", "-c", source])
    try:
        status_path = pathlib.Path("/proc") / str(child.pid) / "status"
        deadline = time.monotonic() + 5
        while True:
            status = dict(line.split(":", 1) for line in status_path.read_text().splitlines())
            if status["State"].strip().startswith("Z"):
                break
            assert time.monotonic() < deadline, "Synthetic main thread did not exit"
            time.sleep(0.01)
        tasks = list((status_path.parent / "task").glob("*/status"))
        assert len(tasks) >= 2
        assert child.pid in namespace["live"]()
        assert namespace["live"]().count(child.pid) == 1
    finally:
        child.kill()
        child.wait(timeout=5)
````
