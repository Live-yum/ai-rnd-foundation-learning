# workbench/specifications/service.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.filesystem`、`workbench.specifications.artifact_writer`、`workbench.specifications.openspec.cli`、`workbench.specifications.validator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `prepare_specifications`（L14–L38）：接收`settings`、`gateway`、`run_id`、`scope`、`selection`、`round_number`。 控制顺序：L22按`not inside(workspace, "openspec/changes/product/.openspec.yaml").exists()`分支；L36按`status.get("schemaName") != "rnd-factory" or status.get("isComplete") is not True`分支；L37抛异常，停止当前正常路径。 调用`inside`、`initialize_workspace`、`OpenSpecCLI`、`cli.check_version`、`cli.validate_schema`、`inside(workspace, "openspec/changes/product/.openspec.yaml").exis…`、`cli.new_change`、`cli.instructions`、`gateway.complete`等。 返回路径：L38的`bundle, workspace`。
- `bind_feature_design`（L41–L50）：接收`workspace`、`bundle`、`design`、`scope`、`selection`。 调用`validate_mapping`、`write_json`、`inside`、`digest`、`bundle.model_dump`、`design.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/specifications/service.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L50。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2089`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/specifications/service.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2875e762130519b2e7e944553484c2a7b16859e3a1cb173746789be18418adbd"} -->
````python
# workbench/specifications/service.py
"""OpenSpec produces documents; Feature Planner still owns executable contracts."""

from workbench.core.contracts import digest
from workbench.filesystem import inside, write_json
from workbench.specifications.artifact_writer import initialize_workspace, write_artifacts
from workbench.specifications.openspec.cli import ARTIFACTS, OpenSpecCLI
from workbench.specifications.validator import (
    SpecificationBundle,
    validate_mapping,
    validate_sources,
)


def prepare_specifications(settings, gateway, run_id, scope, selection, round_number):
    workspace = inside(
        settings.data_dir, f"runs/{run_id}/specifications/{scope['source_digest']}/{round_number}"
    )
    initialize_workspace(workspace)
    cli = OpenSpecCLI(workspace)
    cli.check_version()
    cli.validate_schema()
    if not inside(workspace, "openspec/changes/product/.openspec.yaml").exists():
        cli.new_change()
    # Instructions are data, and cannot select apply/archive or a coding workflow.
    instructions = {name: cli.instructions(name) for name in ARTIFACTS}
    bundle = gateway.complete(
        run_id,
        f"plan:specifications:{scope['source_digest']}:{round_number}",
        "生成 proposal/specs/design/tasks 文档。完整保留来源、验收与阻塞；文档不授权执行。",
        {"scope": scope, "selection": selection, "instructions": instructions},
        SpecificationBundle,
    )
    validate_sources(bundle, scope)
    write_artifacts(workspace, bundle)
    status = cli.status()
    if status.get("schemaName") != "rnd-factory" or status.get("isComplete") is not True:
        raise ValueError("OpenSpec document artifacts are incomplete")
    return bundle, workspace


def bind_feature_design(workspace, bundle, design, scope, selection):
    mapping = validate_mapping(bundle, design, scope, selection)
    write_json(
        inside(workspace, "feature-mapping.json"),
        {
            **mapping,
            "documents_digest": digest(bundle.model_dump()),
            "feature_design_digest": digest(design.model_dump()),
        },
    )
````
