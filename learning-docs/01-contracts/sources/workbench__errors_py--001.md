# workbench/errors.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：区分暂停预算和超出能力。** 这两个异常不是随意的报错字符串：调用方根据异常类型，把运行置为可恢复暂停或明确阻塞，而不是继续生成一个不满足要求的产品。

**对应关系：** llm/flow抛出 → runtime捕获；test_workflow及test_guided_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `PausedLimit`（L4–L5）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `UnsupportedScope`（L8–L9）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。

</details>

**创建路径：** `workbench/errors.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L9。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`174`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/errors.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a3ab1abf1fab3a56d9931fcc8cc216c859ee030771ba5fb9d05a32f960182c84"} -->
````python
# workbench/errors.py
"""Recoverable control states retain both user data and workflow checkpoints."""


class PausedLimit(RuntimeError):
    pass


class UnsupportedScope(RuntimeError):
    pass
````
