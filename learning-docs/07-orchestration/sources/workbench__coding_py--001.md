# workbench/coding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：不依赖Aider的受限规则编辑。** apply_patch只接收允许文件的替换内容，校验旧内容和新规则。code_rules向网关请求结构化补丁并保存每轮证据。它不执行任意shell，也不能越权修改认证、路由和依赖锁。

**对应关系：** flow → coding → ModelGateway + Rules → verification；test_safety。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.knowledge`、`workbench.rules`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `apply_patch`（L22–L51）：接收`product`、`patch`。 控制顺序：L27按`sha(path) == content_sha`分支；L35按`sha(path) != patch.before_sha256`分支；L36抛异常，停止当前正常路径。 调用`Path`、`Rules`、`path.read_text`、`hashlib.sha256(patch.content.encode()).hexdigest`、`hashlib.sha256`、`patch.content.encode`、`sha`、`ValueError`、`atomic_text`等。 返回路径：L28的`{ "path": patch.path, "before": patch.before_sha256, "after": content_sha, "replayed": Tru…`；L38的`{ "path": patch.path, "before": patch.before_sha256, "after": sha(path), "diff": "".join( …`。
- `code_rules`（L54–L69）：接收`run_id`、`plan`、`product`、`gateway`、`attempt`、`error`。 调用`Path`、`build_index`、`context_for`、`gateway.complete`、`plan.model_dump`、`apply_patch`、`receipt.update`、`write_json`。 返回路径：L69的`receipt`。

</details>

**创建路径：** `workbench/coding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L69。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2971`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/coding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0fb1edaf8fdd138abe5bdd932b477cacc3ecc97af6f3754541ee937dea16d425"} -->
````python
# workbench/coding.py
"""Bounded coding: one SHA-guarded rule file, parsed/interpreted instead of exec."""

import difflib
import hashlib
from pathlib import Path

from workbench.domain import Patches
from workbench.filesystem import atomic_text, sha, write_json
from workbench.knowledge import build_index, context_for
from workbench.rules import Rules

INSTRUCTION = """你只实现已批准的逐实体字段验证规则，不生成 CRUD 或测试代码。
只修改 custom_rules.py，必须返回 patches JSON，before_sha256 必须等于上下文文件的哈希。
文件只能包含一个无注解、无装饰器、无默认参数的 def validate(entity, data): 函数。
只允许 if/elif/else、and/or/not、比较、in/not in、整数/字符串/布尔/None、列表/元组、
data.get('固定字段名', 默认常量)、data['固定字段名']、len(...)、raise ValueError('固定文本')、return None。
禁止 import、赋值、循环、任意属性访问、网络、文件、函数定义嵌套、算术运算、exec/eval。
无匹配规则返回 None。所有 accept_examples 必须通过，reject_examples 必须被拒绝。
不要改变已经批准的规则含义，也不要根据测试失败删除规则。"""


def apply_patch(product, patch):
    path = Path(product) / "custom_rules.py"
    Rules(patch.content)
    before = path.read_text(encoding="utf-8")
    content_sha = hashlib.sha256(patch.content.encode()).hexdigest()
    if sha(path) == content_sha:
        return {
            "path": patch.path,
            "before": patch.before_sha256,
            "after": content_sha,
            "replayed": True,
            "diff": "",
        }
    if sha(path) != patch.before_sha256:
        raise ValueError("文件已变化，拒绝应用过期补丁")
    atomic_text(path, patch.content)
    return {
        "path": patch.path,
        "before": patch.before_sha256,
        "after": sha(path),
        "diff": "".join(
            difflib.unified_diff(
                before.splitlines(True),
                patch.content.splitlines(True),
                fromfile="a/custom_rules.py",
                tofile="b/custom_rules.py",
            )
        ),
        "replayed": False,
    }


def code_rules(run_id, plan, product, gateway, attempt, error=""):
    knowledge = Path(product).parent / "knowledge"
    build_index(product, knowledge, source_version="generated-product")
    context = context_for(product, knowledge, ["custom_rules.py", "approved-spec.json"])
    result = gateway.complete(
        run_id,
        f"coding:{attempt}",
        INSTRUCTION,
        {"plan": plan.model_dump(), "context": context, "previous_error": error},
        Patches,
    )
    receipt = apply_patch(product, result.patches[0])
    receipt.update(attempt=attempt, explanation=result.explanation)
    write_json(Path(product).parent / f"coding-{attempt}.json", receipt)
    build_index(product, knowledge, source_version="generated-product")
    return receipt
````
