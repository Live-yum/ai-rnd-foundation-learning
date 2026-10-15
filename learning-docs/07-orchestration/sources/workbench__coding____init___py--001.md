# workbench/coding/__init__.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：不依赖Aider的受限规则编辑。** apply_patch只接收允许文件的替换内容，校验旧内容和新规则。code_rules向网关请求结构化补丁并保存每轮证据。它不执行任意shell，也不能越权修改认证、路由和依赖锁。

**对应关系：** flow → coding → ModelGateway + Rules → verification；test_safety。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.coding.bounded`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/coding/__init__.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L5。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`220`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/coding/__init__.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "37372dc35a4e9a3c4cb3d981570a6ec26e70f29411216dd0070978fd1c1eb5fc"} -->
````python
# workbench/coding/__init__.py
"""Coding ports and bounded compatibility entry points."""

from workbench.coding.bounded import INSTRUCTION, apply_patch, code_rules, rule_context

__all__ = ["INSTRUCTION", "apply_patch", "code_rules", "rule_context"]
````
