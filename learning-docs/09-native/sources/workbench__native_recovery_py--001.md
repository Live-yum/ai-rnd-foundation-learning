# workbench/native_recovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：身份绑定的原生中断检查点。** identity绑定模板、批准Plan、数据库身份和前后端来源；save记录实际文件清单与可恢复阶段；load只接受同一身份、完整且未篡改的可恢复现场。不可重放阶段中断不能自动重置数据库。

**对应关系：** native_lab保存/恢复 → 同一生成目录及本机数据库 → native_coding继续验证；test_native_recovery。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `NativeIntegrityError`（L12–L13）：继承`PrerequisiteError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `identity`（L16–L26）：接收`template`、`plan`、`url`、`source`、`frontend_source`。 调用`checked_database`、`digest`、`plan.model_dump`、`manifest`。 返回路径：L18的`{ "template": template, "spec_digest": digest(plan.model_dump()), "database": digest( {"ho…`。
- `save`（L29–L39）：接收`path`、`expected`、`product`、`targets`、`resumable`、`stage`。 调用`write_json`、`manifest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load`（L42–L55）：接收`path`、`expected`、`product`。 控制顺序：L44按`not path.is_file()`分支；L45抛异常，停止当前正常路径；L47按`state.get("identity") != expected`分支；L48抛异常，停止当前正常路径；L49按`state.get("resumable") is not True`分支；L50抛异常，停止当前正常路径；L53按`state.get("files") != manifest(product)`分支；L54抛异常，停止当前正常路径。 调用`Path`、`path.is_file`、`PrerequisiteError`、`json.loads`、`path.read_text`、`state.get`、`manifest`。 返回路径：L55的`state`。

</details>

**创建路径：** `workbench/native_recovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L55。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2018`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_recovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0a4fb4f96543b76627a976df2aa4b8a15736bcb82f37dcfd8b07f7d93c997094"} -->
````python
# workbench/native_recovery.py
"""Identity-bound native validation checkpoints; never re-bootstrap a retained database."""

import json
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.native_environment import checked_database


class NativeIntegrityError(PrerequisiteError):
    """An uncertain edit must not become a trusted retry checkpoint."""


def identity(template, plan, url, source, frontend_source):
    database = checked_database(url)
    return {
        "template": template,
        "spec_digest": digest(plan.model_dump()),
        "database": digest(
            {"host": database.host, "port": database.port or 5432, "database": database.database}
        ),
        "source": digest(manifest(source)),
        "frontend_source": digest(manifest(frontend_source)) if frontend_source else None,
    }


def save(path, expected, product, targets, *, resumable, stage):
    write_json(
        path,
        {
            "identity": expected,
            "files": manifest(product),
            "targets": targets,
            "resumable": resumable,
            "stage": stage,
        },
    )


def load(path, expected, product):
    path = Path(path)
    if not path.is_file():
        raise PrerequisiteError("原生中断现场缺少安全检查点；保留数据，请检查运行证据")
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("identity") != expected:
        raise PrerequisiteError("原生恢复的设计、数据库或模板来源已改变；保留现场并恢复原配置")
    if state.get("resumable") is not True:
        raise PrerequisiteError(
            "原生生成在不可重放步骤中断；保留数据库和源码，需要检查该阶段后恢复"
        )
    if state.get("files") != manifest(product):
        raise PrerequisiteError("原生中断后源码已被修改；不自动覆盖，先核对恢复检查点")
    return state
````
