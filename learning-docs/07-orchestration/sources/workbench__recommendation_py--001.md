# workbench/recommendation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：解释智能推荐为何暂停。** 把当前gate中的明确阻塞、未回答问题和能力说明分开，记录阶段、尝试次数及门身份；不会把所有暂停一律解释成模板不支持，也不会自行宣布已完成。

**对应关系：** runtime自动修正达到有界次数 → blocked_report → recommendation-blocked.json → 页面/CLI诊断。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `blocked_report`（L4–L25）：接收`gate`、`attempts`。 控制顺序：L8按`isinstance(blocked, str)`分支；L13按`not reasons`分支。 调用`gate.get`、`data.get`、`isinstance`、`list`、`requirement.get`、`reasons.extend`、`dict.fromkeys`。 返回路径：L15的`{ "passed": False, "stage": gate["stage"], "gate_id": gate["gate_id"], "attempts": attempt…`。

</details>

**创建路径：** `workbench/recommendation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L25。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`991`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/recommendation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e832e9df2a2b7a464fe2596544d549776eaeaf85bb95fcdf01b6c287d5a879f9"} -->
````python
# workbench/recommendation.py
"""Explain a paused automatic decision without treating every pause as unsupported scope."""


def blocked_report(gate, attempts):
    data = gate.get("data", {})
    requirement = data.get("requirement", {})
    blocked = data.get("blocked", [])
    if isinstance(blocked, str):
        blocked = [blocked]
    reasons = list(blocked) + list(requirement.get("unsupported", []))
    questions = list(requirement.get("questions", []))
    reasons.extend("尚未自动决定：" + text for text in questions)
    if not reasons:
        reasons = ["需求摘要、使用者、功能、验收条件或数据范围仍不完整"]
    return {
        "passed": False,
        "stage": gate["stage"],
        "gate_id": gate["gate_id"],
        "attempts": attempts,
        "reasons": list(dict.fromkeys(reasons)),
        "questions": questions,
        "limitations": requirement.get("limitations", []),
        "can_approve": gate.get("can_approve", False),
        "recoverable": True,
    }
````
