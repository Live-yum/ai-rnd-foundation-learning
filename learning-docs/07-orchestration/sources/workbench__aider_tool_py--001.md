# workbench/aider_tool.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：隔离的Aider命令行适配。** Repo Map与SEARCH/REPLACE调用真实Aider CLI，但CLI不持有大模型Key。先用原文唯一匹配算出期望结果，再在临时Git工作区应用，检查实际结果和变更文件集合；只把批准的规则文件放回产品。

**对应关系：** coding_engine=aider → code_rules_with_aider → gateway/preview_blocks/apply_blocks；ci_aider_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.coding`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/aider_tool.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`184`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/aider_tool.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "de5b156ddcb7a47c2463738001cfef4e3d17624351f3d9b39cc6346ca2bc8053"} -->
````python
# workbench/aider_tool.py
"""Compatibility import; implementation lives in workbench.coding.aider."""

import sys

from workbench.coding import aider as _implementation

sys.modules[__name__] = _implementation
````
