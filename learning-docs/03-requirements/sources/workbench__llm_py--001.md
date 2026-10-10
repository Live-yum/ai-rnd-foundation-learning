# workbench/llm.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：唯一的对话模型调用网关。** 网关集中选择阶段模型、计算调用预算、发送HTTP请求和校验结构化结果。重试有上限；没有真实配置时应报错，而不是暗中返回演示答案。测试由调用者显式注入协议夹具。

**对应关系：** Workflow/coding/aider_tool → ModelGateway → 大模型；test_llm、test_guided_models。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.infrastructure.llm`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**带着一个具体问题阅读：** complete先选阶段模型并检查预算，构造受约束请求，再通过协议层解析、验证响应并保存使用回执。HTTP成功却返回不符合schema的JSON仍应失败；传输错误的有限重试也不能变成无上限重复收费。测试显式注入MockTransport，生产缺少模型配置时不会静默换成样例答案。

**创建路径：** `workbench/llm.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`191`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/llm.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2ea18b1c828f59fd6c7e0a7f4f3de13011973adc2468f426b49367489a378c68"} -->
````python
# workbench/llm.py
"""Compatibility import for workbench.infrastructure.llm.gateway."""

import sys

from workbench.infrastructure.llm import gateway as _implementation

sys.modules[__name__] = _implementation
````
