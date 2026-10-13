# workbench/specifications/artifact_writer.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.specifications.openspec.cli`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `initialize_workspace`（L17–L54）：接收`root`。 控制顺序：L22遍历`ARTIFACTS`。 调用`Path`、`root.mkdir`、`inside`、`atomic_text`、`artifacts.append`、`json.dumps`。 返回路径：L54的`root`。
- `write_artifacts`（L57–L68）：接收`workspace`、`bundle`。 控制顺序：L59遍历`OUTPUTS.items()`。 调用`inside`、`OUTPUTS.items`、`atomic_text`、`getattr`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/specifications/artifact_writer.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L68。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2195`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/specifications/artifact_writer.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "78c930a997fe0f6826bf5b512ecf6846a4cea34bf00e0f6a289e1524acae5bdd"} -->
````python
# workbench/specifications/artifact_writer.py
"""Each run and source revision owns its separate document-only workspace."""

import json
from pathlib import Path

from workbench.filesystem import atomic_text, inside, write_json
from workbench.specifications.openspec.cli import ARTIFACTS, SCHEMA

OUTPUTS = {
    "proposal": "proposal.md",
    "specs": "specs/product/spec.md",
    "design": "design.md",
    "tasks": "tasks.md",
}


def initialize_workspace(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    schema = inside(root, "openspec/schemas/" + SCHEMA)
    artifacts = []
    for name in ARTIFACTS:
        atomic_text(
            inside(schema, "templates/" + name + ".md"),
            "# "
            + name
            + "\n\nPreserve exact source IDs. This document grants no execution authority.\n",
        )
        artifacts.append(
            {
                "id": name,
                "generates": OUTPUTS[name],
                "description": "Unapproved " + name,
                "template": name + ".md",
                "instruction": "Document requirements only. Never execute or edit product code.",
                "requires": []
                if name == "proposal"
                else (["proposal"] if name != "tasks" else ["specs", "design"]),
            }
        )
    # JSON is a YAML subset; no model-controlled schema or executable hooks.
    atomic_text(
        inside(schema, "schema.yaml"),
        json.dumps(
            {
                "name": SCHEMA,
                "version": 1,
                "description": "RND document-only specification",
                "artifacts": artifacts,
            }
        ),
    )
    atomic_text(inside(root, "openspec/config.yaml"), "schema: rnd-factory\n")
    return root


def write_artifacts(workspace, bundle):
    change = inside(workspace, "openspec/changes/product")
    for name, output in OUTPUTS.items():
        atomic_text(inside(change, output), getattr(bundle, name))
    write_json(
        inside(change, "source-binding.json"),
        {
            "source_digest": bundle.source_digest,
            "requirement_ids": bundle.requirement_ids,
            "execution_authorized": False,
        },
    )
````
