# workbench/clarification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把当前澄清关卡的选择可靠还原为用户回答。** 在Store.submit事务内，用服务器当前问题与选项ID取回标签，拒绝过期问题、未知选项、漏答必填和单选多选混用。保留用户自定义文字；不信任浏览器发来的标签，也不把一次回答当作批准。

**对应关系：** ResumeRequest.answers + 当前pending/gate_id → render_answer → 用户Message及排队Job；无选择项的CLI纯文字仍原样保留。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.requirements`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** 当前问题Q的选项O1标签是‘内部团队’，浏览器提交的是Q/O1。render_answer从当前pending取标签，不以客户端伪造标签为准；Q已被下一版替换或单选提交两个选项时，在同一事务里拒绝且不排队。合法回答成为用户原文，仍不等于需求/计划批准。

**创建路径：** `workbench/clarification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`212`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/clarification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ff59e64784d07e6083a345448f08cbd04b4a02b188d4fe5f6694533c9317b3a8"} -->
````python
# workbench/clarification.py
"""Compatibility import; implementation lives in workbench.requirements.clarification."""

import sys

from workbench.requirements import clarification as _implementation

sys.modules[__name__] = _implementation
````
