# workbench/requirement_coverage.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.requirements`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`202`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2740f0d1226877977ac299511dfb89bd1c8f929ebb0380430cbcb0dd7830bbbe"} -->
````python
# workbench/requirement_coverage.py
"""Compatibility import; implementation lives in workbench.requirements.coverage."""

import sys

from workbench.requirements import coverage as _implementation

sys.modules[__name__] = _implementation
````
