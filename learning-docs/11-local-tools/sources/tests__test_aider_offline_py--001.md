# tests/test_aider_offline.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_aider_guard_blocks_dns_tcp_udp_and_listening`（L21–L29）：接收`operation`。 控制顺序：L29断言`run_command([sys.executable, "-c", script], ROOT, 20)["returncode"] == 0`。 调用`str`、`run_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_aider_offline.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L29。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1080`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_aider_offline.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9367bda3bdd082920851db152120cad025642cf52f4877cdace677c1aec0441f"} -->
````python
# tests/test_aider_offline.py
"""The child guard is tested in a fresh interpreter; it never changes pytest's networking."""

import sys

import pytest

from workbench.settings import ROOT
from workbench.tools import run_command


@pytest.mark.parametrize(
    "operation",
    [
        "socket.getaddrinfo('example.com',443)",
        "socket.gethostbyname('localhost')",
        "socket.socket().connect(('127.0.0.1',80))",
        "socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b'x',('127.0.0.1',9))",
        "socket.socket().bind(('127.0.0.1',0))",
    ],
)
def test_aider_guard_blocks_dns_tcp_udp_and_listening(operation):
    runner = ROOT / "tools/aider/offline_runner.py"
    script = (
        f"import runpy,socket; ns=runpy.run_path({str(runner)!r},run_name='guard-test'); "
        "ns['install_offline_guard']()\n"
        f"try:\n {operation}\nexcept PermissionError as e:\n assert 'network access is disabled' in str(e)\n"
        "else:\n raise AssertionError('unguarded network operation')\n"
    )
    assert run_command([sys.executable, "-c", script], ROOT, 20)["returncode"] == 0
````
