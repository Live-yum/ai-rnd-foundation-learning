# workbench/flow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：需求到交付的LangGraph状态机。** State是节点共享的数据合同，Workflow注册节点和转移。需求确认后才能整理源码上下文并规划；批准方案后才能生成和验收；通过真实检查后才进入交付确认。interrupt把人工关口持久化，自动模式只委托选择，不绕过验收。

**对应关系：** Runtime驱动 → 需求/上下文/规划/生成/验证/本机沙箱/审阅/打包 → Store保存证据；test_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.production`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** Workflow把需求确认、设计、生成、验证和交付排成有条件的图。gate先保存本版审批内容，再interrupt等待；恢复必须提交当前gate_id。智能推荐可以替用户补普通未知项并留下委托记录，但代码验证失败时仍不得进入READY。请沿第07阶段的三次等待状态走一次，而非假设所有节点每次都会执行。

**创建路径：** `workbench/flow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`171`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/flow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3cdc68c71334a7e2cf39a2bd00a4750085b56561bdaff7a37ae93c14eac7d29e"} -->
````python
# workbench/flow.py
"""Compatibility import for workbench.production.graph."""

import sys

from workbench.production import graph as _implementation

sys.modules[__name__] = _implementation
````
