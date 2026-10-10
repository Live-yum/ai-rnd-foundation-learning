# workbench/coding/diff_guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.coding.candidates`、`workbench.filesystem`、`workbench.planning.contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot_edits`（L8–L30）：接收`product`、`snapshot`、`task`、`selection`。 控制顺序：L10按`errors`分支；L11抛异常，停止当前正常路径；L12按`set(snapshot) != set(task.allowed_paths) or len(snapshot) > 64`分支；L13抛异常，停止当前正常路径；L14按`any(type(value) is not str for value in snapshot.values())`分支；L15抛异常，停止当前正常路径；L16按`sum(len(value.encode()) for value in snapshot.values()) > 1_000_000`分支；L17抛异常，停止当前正常路径。 调用`task_path_errors`、`ValueError`、`"; ".join`、`set`、`len`、`any`、`type`、`snapshot.values`、`sum`等。 返回路径：L18的`CapabilityEdits( explanation="mini-SWE isolated candidate; independent acceptance pending"…`。

</details>

**创建路径：** `workbench/coding/diff_guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L30。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1271`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/coding/diff_guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fc0afcc19d32dfaffaabb36003d260c8d5201c2ba823818344d16c7c34a3f184"} -->
````python
# workbench/coding/diff_guard.py
"""Convert an untrusted sandbox snapshot to existing SHA-bound CapabilityEdits."""

from workbench.coding.candidates import task_path_errors
from workbench.filesystem import inside, sha
from workbench.planning.contracts import CapabilityEdits, SourceEdit


def snapshot_edits(product, snapshot, task, selection):
    errors = task_path_errors(task, selection)
    if errors:
        raise ValueError("; ".join(errors))
    if set(snapshot) != set(task.allowed_paths) or len(snapshot) > 64:
        raise ValueError("sandbox snapshot must contain exactly the approved business files")
    if any(type(value) is not str for value in snapshot.values()):
        raise ValueError("only UTF-8 text source is supported")
    if sum(len(value.encode()) for value in snapshot.values()) > 1_000_000:
        raise ValueError("sandbox diff exceeds 1MB")
    return CapabilityEdits(
        explanation="mini-SWE isolated candidate; independent acceptance pending",
        files=[
            SourceEdit(
                path=name,
                before_sha256=sha(inside(product, name))
                if inside(product, name).is_file()
                else None,
                content=snapshot[name],
            )
            for name in task.allowed_paths
        ],
    )
````
