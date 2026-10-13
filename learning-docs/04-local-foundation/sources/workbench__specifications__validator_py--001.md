# workbench/specifications/validator.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.planning.contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `SpecificationBundle`（L9–L21）：继承`Contract`。声明的数据项为`source_digest`、`requirement_ids`、`proposal`、`specs`、`design`、`tasks`；类型约束/数据库列参数以完整定义为准。
- `SpecificationBundle.unique_sources`（L18–L21）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L19按`len(self.requirement_ids) != len(set(self.requirement_ids))`分支；L20抛异常，停止当前正常路径。 调用`len`、`set`、`ValueError`、`model_validator`。 返回路径：L21的`self`。
- `validate_sources`（L24–L28）：接收`bundle`、`scope`。 控制顺序：L25按`bundle.source_digest != scope["source_digest"] or set(bundle.requirement_ids) != { so…`分支；L28抛异常，停止当前正常路径。 调用`set`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_mapping`（L31–L44）：接收`bundle`、`design`、`scope`、`selection`。 控制顺序：L36按`errors`分支；L37抛异常，停止当前正常路径。 调用`validate_sources`、`feature_design_errors`、`ValueError`、`"; ".join`。 返回路径：L38的`{ "source_digest": bundle.source_digest, "requirement_ids": bundle.requirement_ids, "task_…`。

</details>

**创建路径：** `workbench/specifications/validator.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L44。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1709`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/specifications/validator.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2b27329d62a995bcbd41b783e2f6ae9dc640c45f35b526bee4e50ebbf4fdc900"} -->
````python
# workbench/specifications/validator.py
"""Strict source-bound document contracts; Markdown cannot authorize execution."""

from pydantic import Field, model_validator

from workbench.core.contracts import Contract
from workbench.planning.contracts import Identifier


class SpecificationBundle(Contract):
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    requirement_ids: list[Identifier] = Field(min_length=1, max_length=256)
    proposal: str = Field(min_length=1, max_length=20000)
    specs: str = Field(min_length=1, max_length=40000)
    design: str = Field(min_length=1, max_length=20000)
    tasks: str = Field(min_length=1, max_length=20000)

    @model_validator(mode="after")
    def unique_sources(self):
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("specification source IDs must be unique")
        return self


def validate_sources(bundle, scope):
    if bundle.source_digest != scope["source_digest"] or set(bundle.requirement_ids) != {
        source["id"] for source in scope["sources"]
    }:
        raise ValueError("specification must bind every exact original source")


def validate_mapping(bundle, design, scope, selection):
    from workbench.planning.feature_planner import feature_design_errors

    validate_sources(bundle, scope)
    errors = feature_design_errors(design, scope, selection)
    if errors:
        raise ValueError("specification mapping failed: " + "; ".join(errors))
    return {
        "source_digest": bundle.source_digest,
        "requirement_ids": bundle.requirement_ids,
        "task_ids": [module.id for module in design.outline.modules],
        "authority": "FeatureDesign",
        "execution_authorized": False,
    }
````
