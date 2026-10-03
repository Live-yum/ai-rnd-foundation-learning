# tests/test_capability_guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_network_guard_cannot_silently_fall_back`（L10–L29）：接收`tmp_path`。 控制顺序：L28断言`process.returncode == 78`；L29断言`not marker.exists()`。 调用`subprocess.run`、`str`、`marker.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supported_kernel_restricts_real_daemon_port_or_fails_closed`（L32–L55）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L48按`process.returncode == 78`分支；L49断言`process.stdout == ""`；L50断言`"no product command was executed" in process.stderr`；L52断言`process.returncode == 0`；L54断言`result["landlock_abi"] >= 6`；L55断言`result["daemon_tcp_denied"] and result["no_new_privs"]`。 调用`subprocess.run`、`str`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L55。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1452`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "42871ef43f8ac86239869194f796f2f6e345bb008539bc7e07c02e290741f721"} -->
````python
# tests/test_capability_guard.py
"""No privileges or system policy changes: restrict only a disposable child."""

import json
import subprocess
import sys

from workbench.settings import ROOT


def test_network_guard_cannot_silently_fall_back(tmp_path):
    marker = tmp_path / "executed"
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            str(ROOT / "scripts/capability_guard.py"),
            "",
            "2280",
            "--",
            sys.executable,
            "-c",
            f"open({str(marker)!r}, 'w').write('unsafe')",
        ],
        capture_output=True,
        timeout=15,
    )
    assert process.returncode == 78
    assert not marker.exists()


def test_supported_kernel_restricts_real_daemon_port_or_fails_closed():
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            str(ROOT / "scripts/capability_guard.py"),
            "8123",
            "",
            "--probe",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if process.returncode == 78:
        assert process.stdout == ""
        assert "no product command was executed" in process.stderr
    else:
        assert process.returncode == 0
        result = json.loads(process.stdout)
        assert result["landlock_abi"] >= 6
        assert result["daemon_tcp_denied"] and result["no_new_privs"]
````
