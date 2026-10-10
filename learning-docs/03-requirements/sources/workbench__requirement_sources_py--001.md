# workbench/requirement_sources.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：在规划前拒绝明确来源互相冲突的分析候选。** 对能可靠定位的同一原子义务比较明确值，保留用户原文、已确认契约和模型候选来源；矛盾走已有有界分析纠错，不替用户选值或批准，未知旧文本仍保守校验。

**对应关系：** Workflow.analyse → 来源冲突诊断与需求账本 → 原有clarification关口；有效分析才进入设计。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.requirements`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 先把用户原文、已确认合同和模型候选放在各自来源中比较。若同一字段被明确要求为必填，而候选却明确写成可选，应返回冲突诊断交回分析纠错；函数不替用户选择哪项约束获胜。无法可靠定位的旧文本继续保守校验，不能把猜测写成已批准事实。

**创建路径：** `workbench/requirement_sources.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`212`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_sources.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "65616b8ba9c47aec8e5d651478faafc0758fb6e5f63044d86f76eaf2ed829aa3"} -->
````python
# workbench/requirement_sources.py
"""Compatibility import; implementation lives in workbench.requirements.source_ledger."""

import sys

from workbench.requirements import source_ledger as _implementation

sys.modules[__name__] = _implementation
````
