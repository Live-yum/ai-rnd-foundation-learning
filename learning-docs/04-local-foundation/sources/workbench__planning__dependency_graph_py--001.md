# workbench/planning/dependency_graph.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `serial_order`（L4–L18）：接收`tasks`。 控制顺序：L6按`len(by_id) != len(tasks)`分支；L7抛异常，停止当前正常路径；L11在`pending`成立时循环；L13按`task is None`分支；L14抛异常，停止当前正常路径。 调用`len`、`ValueError`、`list`、`set`、`next`、`result.append`、`done.add`、`pending.remove`。 返回路径：L18的`result`。

</details>

**创建路径：** `workbench/planning/dependency_graph.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L18。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`583`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/planning/dependency_graph.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "99de955535484a486821532c83462fb3c51190c8e32893515d3df77da4f66799"} -->
````python
# workbench/planning/dependency_graph.py
"""Stable serial DAG order used by planners and durable dispatchers."""


def serial_order(tasks):
    by_id = {task.id: task for task in tasks}
    if len(by_id) != len(tasks):
        raise ValueError("duplicate task identifier")
    pending = list(tasks)
    done = set()
    result = []
    while pending:
        task = next((task for task in pending if set(task.depends_on) <= done), None)
        if task is None:
            raise ValueError("cyclic or unknown dependency")
        result.append(task)
        done.add(task.id)
        pending.remove(task)
    return result
````
