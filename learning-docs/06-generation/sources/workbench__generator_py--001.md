# workbench/generator.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：确定性生成基础FastAPI产品。** generate_basic复制本项目编写的模板，再把Plan写入产品规格、路由信息和迁移文件。相同Plan使用同一套生成规则；模型不负责重写登录、数据库与整套骨架。代码字符串中的upgrade/downgrade是写入成品迁移的内容。

**对应关系：** flow生成节点 → generator → templates/product + product_sql → verification。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** generate_basic把批准Plan和已校验选择写成不可含糊的产物身份，再复制模板、生成迁移并登记每个文件SHA。第一次创建目标目录应得到完整产品；同一路径已经有文件却无相符回执时应停止并保留现场。这里不能用删除重建来伪装幂等，因为目录可能已包含用户修改或数据。

**创建路径：** `workbench/generator.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`185`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/generator.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "aa30a824b4be932454e6a01df76e8afd62c7f7d826b8cf101c7c10a9c3b3d16b"} -->
````python
# workbench/generator.py
"""Compatibility import for workbench.generation.python_basic."""

import sys

from workbench.generation import python_basic as _implementation

sys.modules[__name__] = _implementation
````
