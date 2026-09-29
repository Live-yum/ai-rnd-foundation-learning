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


def code_rules(run_id, plan, product, gateway, attempt, error="", *, settings=None):
    knowledge = Path(product).parent / "knowledge"
    build_index(product, knowledge, source_version="generated-product")
    context = context_for(product, knowledge, ["custom_rules.py", "approved-spec.json"])
    payload = {"plan": plan.model_dump(), "context": context, "previous_error": error}
    if settings and settings.coding_engine == "aider":
        from workbench.aider_tools import Edits, apply_edits

        result = gateway.complete(
            run_id,
            f"coding:{attempt}:aider",
            INSTRUCTION.replace("必须返回 patches JSON", "必须返回 Edits JSON")
            + "\n本次只返回before_sha256、edits(search/replace)、explanation；不返回完整文件。"
            "每个search精确唯一匹配当前文件，search/replace均为完整行并保留末尾换行。",
            payload,
            Edits,
        )
        receipt = apply_edits(product, result, settings, attempt)
    else:
        result = gateway.complete(run_id, f"coding:{attempt}", INSTRUCTION, payload, Patches)
        receipt = apply_patch(product, result.patches[0])
    receipt.update(attempt=attempt, explanation=result.explanation)
    write_json(Path(product).parent / f"coding-{attempt}.json", receipt)
    build_index(product, knowledge, source_version="generated-product")
    return receipt
