# workbench/coding/ports.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.planning.contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `AgentTurn`（L11–L19）：继承`Contract`。声明的数据项为`operation`、`edits`；类型约束/数据库列参数以完整定义为准。
- `AgentTurn.action_shape`（L16–L19）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L17按`(self.operation == "edit") != (self.edits is not None)`分支；L18抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L19的`self`。
- `AgentBudget`（L22–L26）：继承`Contract`。声明的数据项为`max_requests`、`max_tokens`、`max_cost_usd`、`timeout_seconds`；类型约束/数据库列参数以完整定义为准。
- `CodingEnvironment`（L29–L31）：继承`Protocol`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `CodingEnvironment.write`（L30–L30）：接收`edits`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CodingEnvironment.snapshot`（L31–L31）：接收`paths`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/coding/ports.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L31。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1076`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/coding/ports.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e5e041354c369469496b63eb08b61d2aad269d440725e90f8d6bb1e9afe8798b"} -->
````python
# workbench/coding/ports.py
"""Reviewed agent actions are data; neither commands nor verifier replacements."""

from typing import Literal, Protocol

from pydantic import Field, model_validator

from workbench.core.contracts import Contract
from workbench.planning.contracts import CapabilityEdits


class AgentTurn(Contract):
    operation: Literal["edit", "submit"]
    edits: CapabilityEdits | None = None

    @model_validator(mode="after")
    def action_shape(self):
        if (self.operation == "edit") != (self.edits is not None):
            raise ValueError("edit requires files; submit cannot smuggle edits")
        return self


class AgentBudget(Contract):
    max_requests: int = Field(default=16, ge=1, le=64, strict=True)
    max_tokens: int = Field(default=200000, ge=1, le=2000000, strict=True)
    max_cost_usd: float = Field(default=10, gt=0, le=100)
    timeout_seconds: int = Field(default=180, ge=1, le=900, strict=True)


class CodingEnvironment(Protocol):
    def write(self, edits: CapabilityEdits) -> None: ...
    def snapshot(self, paths: list[str]) -> dict[str, str]: ...
````
