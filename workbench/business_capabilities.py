"""Bounded declarative business capabilities and executable requirement coverage."""

import re

BUSINESS = {
    "scope": "shared",
    "field_kinds": ["text", "integer", "boolean", "date", "datetime", "enum"],
    "features": [
        "foreign-key-relations",
        "role-row-permissions",
        "assignment",
        "named-state-transitions",
        "append-only-audit",
        "handling-notes",
        "in-app-reminders",
        "scoped-counts",
        "duration-analysis",
        "group-analysis",
        "daily-trends",
        "archive-history",
    ],
    "limits": [
        "in-app notifications only",
        "declared foreign keys and named transitions only",
        "no arbitrary scripts or network side effects",
        "business and custom_rules cannot be combined",
    ],
}


def business_gaps(requirement, plan):
    """Check recognized obligations; independent review/tests still assess prose semantics."""
    prose = "\n".join(
        [requirement.summary, *requirement.features, *requirement.acceptance, *requirement.users]
    )
    needs = {
        "relations": r"关联|客户历史服务|客户.*服务记录|foreign.key|relational",
        "assignment": r"分配负责人|任务分配|负责人分配|assignment|assign.*owner",
        "workflow": r"修改处理状态|状态变化|状态流转|处理过程|state.transition|workflow",
        "notes": r"添加处理记录|处理记录|处理备注|handling.note",
        "audit": r"操作记录|操作日志|审计|audit",
        "reminders": r"提醒|通知|reminder|notification",
        "count": r"数量统计|服务数量|count.*statistic",
        "duration": r"处理效率|解决时长|处理时长|resolution.time|duration.analysis",
        "groups": r"客户情况分析|分组统计|客户分布|group.analysis",
        "trends": r"趋势|trend",
        "roles": r"不同角色|角色权限|权限管理|role.based",
    }
    requested = {name for name, pattern in needs.items() if re.search(pattern, prose, re.I)}
    if not requested:
        return []
    business = plan.business
    if business is None:
        return [
            "已确认的团队关系、流程、权限或统计需要可执行 business 契约："
            + ", ".join(sorted(requested))
        ]
    actions = {action for policy in business.permissions for action in policy.actions}
    kinds = {metric.kind for metric in business.metrics}
    implemented = {
        "relations": any(r.target_entity != "$users" for r in business.relations),
        "assignment": any(r.assignee_field for r in business.resources) and "assign" in actions,
        "workflow": bool(business.workflows) and "transition" in actions,
        "notes": any(r.notes for r in business.resources) and "add_note" in actions,
        "audit": all(r.audit for r in business.resources) and "read_audit" in actions,
        "reminders": bool(business.notifications),
        "count": "count" in kinds,
        "duration": "average_duration" in kinds,
        "groups": "group_count" in kinds,
        "trends": "time_count" in kinds,
        "roles": len(business.roles) >= 2 and bool(business.permissions),
    }
    return [
        "业务设计缺少已确认的可执行能力：" + name
        for name in sorted(requested)
        if not implemented[name]
    ]
