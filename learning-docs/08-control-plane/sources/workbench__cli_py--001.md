# workbench/cli.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：终端入口和运维命令。** Typer把Python函数映射为rnd子命令。init建立本机数据和索引，start启动网页，chat/recommend调用与网页相同的API；index/tools等工具命令是独立的本机诊断入口。token只供本机使用，不应贴进公开日志。

**对应关系：** pyproject的project.scripts → cli.app → api/runtime/toolchain；test_tools_cli。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.interfaces`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 先在终端A保持rnd start运行，终端B的chat/show等才是HTTP客户端。client用contextmanager管理连接，按Settings.port取得地址，在进入模板或项目问题前先请求/health；初次或后续ConnectError都转成中文启动/PORT提示并以退出码1结束，连接仍会关闭。健康请求只能证明服务可连，不能代替/ready、批准关卡或产品验收。

**创建路径：** `workbench/cli.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L10。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`221`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/cli.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1070e82616eadde2993977c4cfab0a316ea8186b91b5eaad677ef06363cf63e1"} -->
````python
# workbench/cli.py
"""Compatibility import for workbench.interfaces.cli."""

import sys

from workbench.interfaces import cli as _implementation

sys.modules[__name__] = _implementation

if __name__ == "__main__":
    _implementation.app()
````
