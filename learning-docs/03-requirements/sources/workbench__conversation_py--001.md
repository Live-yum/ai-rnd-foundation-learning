# workbench/conversation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从持久化记录组织对话上下文。** context读取已经保存的消息和能力说明。command_word规范化简短控制指令；concise_requirements保留已确认事实。这里不直接调用模型，避免每个界面各自重新解释用户已经回答的内容。

**对应关系：** Store消息 → conversation → flow需求节点 → ModelGateway。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `command_word`（L6–L7）：接收`value`。 调用`value.strip().strip("\"'“”‘’「」『』`").strip().lower`、`value.strip().strip("\"'“”‘’「」『』`").strip`、`value.strip().strip`、`value.strip`。 返回路径：L7的`value.strip().strip("\"'“”‘’「」『』`").strip().lower()`。
- `context`（L10–L28）：接收`store`、`state`、`capabilities`。 调用`store.messages`、`state.get`、`store.get_run`。 返回路径：L15的`{ "original_request": human[0]["content"] if human else "", "current_requirement": state.g…`。
- `concise_requirements`（L31–L32）：接收`requirement`。 调用`json.dumps`。 返回路径：L32的`json.dumps(requirement, ensure_ascii=False, indent=2)`。

</details>

**创建路径：** `workbench/conversation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L32。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1526`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/conversation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "24d550b3bc14694c91256de6f57c9f0da03bebd6c68ddf3a46b6b74a245ff9a1"} -->
````python
# workbench/conversation.py
"""Structured context and command normalization: user control words are not chat answers."""

import json


def command_word(value: str) -> str:
    return value.strip().strip("\"'“”‘’「」『』`").strip().lower()


def context(store, state, capabilities):
    history = store.messages(state["run_id"])
    # The complete audit trail remains in messages. Retain first goal, structured current
    # requirements, and recent corrections rather than growing raw token history forever.
    human = [row for row in history if row["role"] == "user"]
    return {
        "original_request": human[0]["content"] if human else "",
        "current_requirement": state.get("requirement", {}),
        "recent_user_corrections": [r["content"] for r in human[-8:]],
        "template_capabilities": capabilities,
        "resolution_feedback": state.get("resolution_feedback", {}),
        "scope_policy": (
            "Only original_request and explicit user corrections establish requested scope. "
            "Previous model assumptions, questions and template not_supported are not user requests. "
            "Resolve unspecified choices within capabilities when delegated; never drop explicit requirements."
        ),
        "autonomous": store.get_run(state["run_id"])["auto_mode"],
        "policy": "Use prior explicit facts unchanged. Latest explicit correction wins. Never re-ask answered facts.",
    }


def concise_requirements(requirement):
    return json.dumps(requirement, ensure_ascii=False, indent=2)
````
