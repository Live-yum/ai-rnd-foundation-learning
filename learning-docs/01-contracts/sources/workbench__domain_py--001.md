# workbench/domain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：模型、网页、数据库之间的数据合同。** Pydantic模型定义哪些字段可以进入系统；校验在业务处理前发生。FieldSpec约束字段类型，Entity组合字段，Plan组合实体与规则；digest把规范化JSON变成稳定指纹，审批只对该指纹有效。

**对应关系：** api/llm解析 → Requirement/Plan → knowledge/generator/verification；test_contracts。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 以批准为例：网页传入的是ResumeInput，不是任意字典。action=approve必须携带严格布尔true，字符串true不能当批准；gate_id随后还要与数据库当前关口相符。Plan的字段、关系和业务合同先完成交叉校验，再允许生成器接收，所以模型写出一段JSON并不是绕过边界的办法。

**创建路径：** `workbench/domain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`188`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/domain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "826f412f0cc8b7f43dde69261b56b1b4f2e7115a1553d4b22eb50b040d6710b8"} -->
````python
# workbench/domain.py
"""Compatibility import; implementation lives in workbench.core.contracts."""

import sys

from workbench.core import contracts as _implementation

sys.modules[__name__] = _implementation
````
