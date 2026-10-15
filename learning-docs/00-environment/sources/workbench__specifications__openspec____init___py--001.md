# workbench/specifications/openspec/__init__.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：功能目录包入口。** 让分阶段恢复的源码具备可导入的父包；轻量初始化不提前加载后续实现或启动服务。

**对应关系：** 父包初始化 → 当前阶段显式导入的实现。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/specifications/openspec/__init__.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L1。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`50`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/specifications/openspec/__init__.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e6cfa6f2a09885bc027ee1ad4f869ae6bfd03df6fba71823b70dda715cb0feb1"} -->
````python
# workbench/specifications/openspec/__init__.py
"""Pinned, document-only OpenSpec integration."""
````
