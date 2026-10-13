# workbench/runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：持久化Worker和断点恢复。** Runtime把数据库任务和LangGraph检查点连接起来。它按run_id恢复同一流程，认领任务后执行，遇到中断等待回答；异常转成明确状态并保留报告。数据库与checkpoint连接均须在退出时关闭。

**对应关系：** api/cli启动Worker → Runtime → Workflow → Store；test_postgres及test_guided_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.production`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 队列任务只是唤醒同一run_id的理由，LangGraph检查点才说明流程停在哪。Runtime认领任务并恢复原图，遇到interrupt保存等待状态；崩溃后不能把上个任务误当下一关的新批准。一个控制库只允许一个Worker，退出时关闭锁与检查点连接，才能在Windows等平台安全恢复。

**创建路径：** `workbench/runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`173`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "867aa51caaa067a3ff410e1660d780977b6b2317b26493499a41a05027fda4a4"} -->
````python
# workbench/runtime.py
"""Compatibility import for workbench.production.worker."""

import sys

from workbench.production import worker as _implementation

sys.modules[__name__] = _implementation
````
