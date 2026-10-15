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
    report = {
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
    conflicts = data.get("capability_conflicts", [])
    if conflicts:
        report["capability_conflicts"] = conflicts
        report["retry_without_changes"] = False
        report["alternatives"] = list(
            dict.fromkeys(option for conflict in conflicts for option in conflict["alternatives"])
        )
    return report
