# workbench/__init__.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：包入口。** 导入workbench时关闭继承的托管遥测并注册惰性旧名映射，不加载映射目标，不立即启动HTTP服务、创建数据库或调用模型。

**对应关系：** 所有workbench子模块首先经过此入口；数据库初学步骤因此不依赖未来API骨架。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench._compat`、`workbench.local_only`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/__init__.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L11。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`373`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/__init__.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8f9d4a8652ccf08b8578cce354a3472d43bb62d3c0da6c32aab7865a9eef6c36"} -->
````python
# workbench/__init__.py
"""Approval-gated workbench; hosted telemetry is disabled before library imports."""

from workbench.local_only import disable_telemetry

disable_telemetry()

# Keep optional providers and workflow modules unloaded during package startup.
from workbench._compat import install as _install_legacy_imports  # noqa: E402

_install_legacy_imports()
del _install_legacy_imports
````
