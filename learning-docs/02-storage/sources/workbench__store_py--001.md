# workbench/store.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：持久化项目、会话、任务、版本、审批和证据。** SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run和create_batch共享入队逻辑；批量先整批校验再在同一幂等事务建立项目、运行和消息，失败全部回滚。任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。

**对应关系：** api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.infrastructure.persistence`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。

**创建路径：** `workbench/store.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`203`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/store.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c07b18a3433bed53131a6b16e0d0e1a7e47b7245a3acdf12df1173dcc9cda627"} -->
````python
# workbench/store.py
"""Compatibility import for workbench.infrastructure.persistence.store."""

import sys

from workbench.infrastructure.persistence import store as _implementation

sys.modules[__name__] = _implementation
````
