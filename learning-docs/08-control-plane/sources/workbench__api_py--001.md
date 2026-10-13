# workbench/api.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：网页及CLI调用的HTTP接口。** create_app是应用工厂，先准备依赖和生命周期，再定义路由。路由校验本机访问令牌和请求合同，调用Store/Runtime；下载与报告只允许受控目录内的文件。内层函数就是具体HTTP处理器，不是另一个服务。

**对应关系：** web/app.js或cli → FastAPI路由 → Store/Runtime；test_api。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.interfaces`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/api.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`169`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/api.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db83afe2492d058b88ec640762ba9c2185e325bf84dc107f938fbaedac48e9ad"} -->
````python
# workbench/api.py
"""Compatibility import for workbench.interfaces.http."""

import sys

from workbench.interfaces import http as _implementation

sys.modules[__name__] = _implementation
````
