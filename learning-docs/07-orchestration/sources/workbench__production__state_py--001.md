# workbench/production/state.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `State`（L6–L47）：继承`TypedDict`。声明的数据项为`run_id`、`template`、`round`、`requirement`、`requirement_source_count`、`requirement_ledger`、`requirement_analysis_diagnostics`、`requirement_analysis_baseline`、`requirement_capability_conflicts`、`requirement_intent_version`、`resolution_feedback`、`plan`、`decision`、`last_job_id`、`attempt`、`verification`、`delivery`、`status`、`model_review`、`code_context`、`sandbox`、`native_normalization`、`extension_requested_mode`、`extension_design`、`extension_scope`、`extension_errors`、`extension_completed`、`extension_attempt`、`extension_candidate`、`extension_product`、`extension_baseline`、`extension_error`、`extension_edit_receipt`、`extension_candidate_passed`、`extension_proof`、`extension_integration_attempt`、`extension_policy`、`extension_aggregate_passed`、`extension_coverage`、`feature_requested_mode`、`feature_design`；类型约束/数据库列参数以完整定义为准。

</details>

**创建路径：** `workbench/production/state.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L47。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1291`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/production/state.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "898a895a26a7cf506bfb80102de2418598403f860d86aa576af86aa10974925d"} -->
````python
# workbench/production/state.py
"""Persisted graph state. Legacy fields retain their names and meaning."""

from typing import TypedDict


class State(TypedDict, total=False):
    run_id: str
    template: str
    round: int
    requirement: dict
    requirement_source_count: int
    requirement_ledger: list[dict]
    requirement_analysis_diagnostics: list[dict]
    requirement_analysis_baseline: dict
    requirement_capability_conflicts: list[dict]
    requirement_intent_version: int
    resolution_feedback: dict
    plan: dict
    decision: str
    last_job_id: str
    attempt: int
    verification: dict
    delivery: dict
    status: str
    model_review: dict
    code_context: dict
    sandbox: dict
    native_normalization: dict
    extension_requested_mode: bool
    extension_design: dict
    extension_scope: dict
    extension_errors: list[str]
    extension_completed: list[dict]
    extension_attempt: int
    extension_candidate: str
    extension_product: str
    extension_baseline: dict
    extension_error: str
    extension_edit_receipt: dict
    extension_candidate_passed: bool
    extension_proof: dict
    extension_integration_attempt: int
    extension_policy: dict
    extension_aggregate_passed: bool
    extension_coverage: dict
    feature_requested_mode: bool
    feature_design: dict
````
