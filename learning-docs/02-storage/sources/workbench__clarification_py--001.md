# workbench/clarification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把当前澄清关卡的选择可靠还原为用户回答。** 在Store.submit事务内，用服务器当前问题与选项ID取回标签，拒绝过期问题、未知选项、漏答必填和单选多选混用。保留用户自定义文字；不信任浏览器发来的标签，也不把一次回答当作批准。

**对应关系：** ResumeRequest.answers + 当前pending/gate_id → render_answer → 用户Message及排队Job；无选择项的CLI纯文字仍原样保留。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 当前问题Q的选项O1标签是‘内部团队’，浏览器提交的是Q/O1。render_answer从当前pending取标签，不以客户端伪造标签为准；Q已被下一版替换或单选提交两个选项时，在同一事务里拒绝且不排队。合法回答成为用户原文，仍不等于需求/计划批准。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `render_answer`（L6–L59）：接收`pending`、`data`。 源码说明：Render selected *current* option labels; never trust labels sent by a client. The raw submission remains the request's idempotency fingerprint. This helper is called inside Store.submit's locked trans。 控制顺序：L16按`not answers`分支；L18按`pending.get("stage") != "clarification"`分支；L19抛异常，停止当前正常路径；L29按`not questions or set(submitted) - set(questions)`分支；L30抛异常，停止当前正常路径；L32遍历`questions.items()`；L37按`set(selected) - set(options)`分支；L38抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`data.get`、`pending.get`、`Conflict`、`pending.get("data", {}).get`、`ClarificationQuestion.model_validate`、`requirement.get`、`set`、`questions.items`、`submitted.get`等。 返回路径：L17的`data["text"]`；L59的`result`。

</details>

**创建路径：** `workbench/clarification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L59。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2822`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/clarification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ea794fb1e2ee487a4159f338009f7da4c8154813b091a35e17ac0a4d085ee760"} -->
````python
# workbench/clarification.py
"""Validate current-gate choices and preserve the operator's explicit answer text."""

from workbench.domain import ClarificationQuestion


def render_answer(pending, data):
    """Render selected *current* option labels; never trust labels sent by a client.

    The raw submission remains the request's idempotency fingerprint. This helper is
    called inside Store.submit's locked transaction, after the gate identity check.
    CLI/free-text answers remain unchanged, including when no choice UI is available.
    """
    from workbench.store import Conflict

    answers = data.get("answers", [])
    if not answers:
        return data["text"]
    if pending.get("stage") != "clarification":
        raise Conflict("当前阶段没有可提交的澄清选项，请重新查看运行")
    requirement = pending.get("data", {}).get("requirement", {})
    questions = {
        item.id: item
        for item in (
            ClarificationQuestion.model_validate(value)
            for value in requirement.get("question_items", [])
        )
    }
    submitted = {answer["question_id"]: answer for answer in answers}
    if not questions or set(submitted) - set(questions):
        raise Conflict("问题已变化或选项不属于当前版本，请重新查看问题")
    lines = []
    for question_id, question in questions.items():
        answer = submitted.get(question_id, {})
        selected = answer.get("option_ids", [])
        custom = answer.get("text", "")
        options = {option.id: option.label for option in question.options}
        if set(selected) - set(options):
            raise Conflict("提交包含当前问题不存在的选项，请重新选择")
        if question.kind == "single" and len(selected) > 1:
            raise Conflict("单选问题只能选择一个选项")
        if question.kind == "text" and selected:
            raise Conflict("文本问题不能提交选择项")
        if custom and not question.allow_other and question.kind != "text":
            raise Conflict("这个问题不接受自定义选项，请在整体补充中说明")
        if question.required and not selected and not custom.strip():
            raise Conflict("请完成所有必答问题，也可以使用自定义文字回答")
        if selected or custom:
            lines.append(question.prompt)
            lines.extend("- " + options[option_id] for option_id in selected)
            if custom:
                lines.append("补充：" + custom)
    if data.get("text"):
        lines.append("其他补充：" + data["text"])
    result = "\n".join(lines)
    if len(result) > 20000:
        raise Conflict("本组回答过长，请缩短补充内容后重试")
    if not result.strip():
        raise Conflict("请至少回答一个问题或补充文字")
    return result
````
