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
