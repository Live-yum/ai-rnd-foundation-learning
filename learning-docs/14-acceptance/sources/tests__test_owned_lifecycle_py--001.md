# tests/test_owned_lifecycle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_shutdown_drains_launcher_before_port_check`（L12–L39）：接收`monkeypatch`、`running`。 控制顺序：L37断言`events[-2:] == [("127.0.0.1", 48080), ("127.0.0.1", 5173)]`；L38按`running`分支；L39断言`events[:2] == [(99, life.signal.SIGINT), "wait"]`。 调用`SimpleNamespace`、`events.append`、`monkeypatch.setattr`、`life.stop_native`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shutdown_drains_launcher_before_port_check.Connection`（L21–L33）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_shutdown_drains_launcher_before_port_check.Connection.__enter__`（L22–L23）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L23的`self`。
- `test_shutdown_drains_launcher_before_port_check.Connection.__exit__`（L25–L26）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shutdown_drains_launcher_before_port_check.Connection.settimeout`（L28–L29）：接收`value`。 控制顺序：L29断言`value <= 1`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shutdown_drains_launcher_before_port_check.Connection.connect_ex`（L31–L33）：接收`address`。 调用`events.append`。 返回路径：L33的`111`。
- `test_leftover_application_server_blocks_restart`（L42–L61）：接收`monkeypatch`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`pytest.raises`、`life.stop_native`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_leftover_application_server_blocks_restart.Connection`（L45–L56）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_leftover_application_server_blocks_restart.Connection.__enter__`（L46–L47）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L47的`self`。
- `test_leftover_application_server_blocks_restart.Connection.__exit__`（L49–L50）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_leftover_application_server_blocks_restart.Connection.settimeout`（L52–L53）：接收`value`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_leftover_application_server_blocks_restart.Connection.connect_ex`（L55–L56）：接收`address`。 返回路径：L56的`0`。
- `test_launcher_timeout_is_not_successful_cleanup`（L64–L74）：接收`monkeypatch`。 控制顺序：L74断言`killed == [99]`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`killed.append`、`pytest.raises`、`life.stop_native`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_launcher_timeout_is_not_successful_cleanup.wait`（L65–L66）：接收`**kwargs`。 控制顺序：L66抛异常，停止当前正常路径。 调用`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_owned_lifecycle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L74。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2252`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_owned_lifecycle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "feed73896c00e20b2ef3d6386f59c50d0541eb75fb6e7753306e7ce4ea5f261a"} -->
````python
# tests/test_owned_lifecycle.py
"""Restart cannot pass by accidentally reusing an orphaned application server."""

import subprocess
from types import SimpleNamespace

import pytest

from workbench import owned_lifecycle as life


@pytest.mark.parametrize("running", [False, True])
def test_shutdown_drains_launcher_before_port_check(monkeypatch, running):
    events = []
    process = SimpleNamespace(
        pid=99, poll=lambda: None if running else 0, wait=lambda **kw: events.append("wait")
    )
    monkeypatch.setattr(
        life.os, "killpg", lambda pid, sig: events.append((pid, sig)), raising=False
    )

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def settimeout(self, value):
            assert value <= 1

        def connect_ex(self, address):
            events.append(address)
            return 111

    monkeypatch.setattr(life.socket, "socket", Connection)
    life.stop_native(process, [48080, 5173])
    assert events[-2:] == [("127.0.0.1", 48080), ("127.0.0.1", 5173)]
    if running:
        assert events[:2] == [(99, life.signal.SIGINT), "wait"]


def test_leftover_application_server_blocks_restart(monkeypatch):
    process = SimpleNamespace(poll=lambda: 0)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def settimeout(self, value):
            pass

        def connect_ex(self, address):
            return 0

    monkeypatch.setattr(life.socket, "socket", Connection)
    monkeypatch.setattr(life.time, "sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="left an application server"):
        life.stop_native(process, [48080])


def test_launcher_timeout_is_not_successful_cleanup(monkeypatch):
    def wait(**kwargs):
        raise subprocess.TimeoutExpired("launcher", 30)

    process = SimpleNamespace(pid=99, poll=lambda: None, wait=wait)
    killed = []
    monkeypatch.setattr(life.os, "killpg", lambda *args: None, raising=False)
    monkeypatch.setattr(life, "stop_process", lambda p: killed.append(p.pid))
    with pytest.raises(RuntimeError, match="did not drain"):
        life.stop_native(process, [48080])
    assert killed == [99]
````
