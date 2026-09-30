"""Bounded declarative business capabilities and executable requirement coverage."""

import json
import re

_FACT_COLLECTIONS = {
    "metrics": {
        "name",
        "entity",
        "kind",
        "group_by",
        "start_field",
        "end_field",
        "time_field",
        "filters",
        "unit",
        "bucket",
        "timezone",
    },
    "relations": {"entity", "field", "target_entity", "on_delete"},
    "permissions": {"role", "entity", "actions", "scope"},
    "notifications": {"entity", "event", "recipient", "transition", "due_field", "channel"},
    "workflows": {"entity", "status_field", "initial", "transitions"},
    "resources": {"entity", "assignee_field", "archive", "notes", "audit"},
}
_FIELD_COLLECTIONS = {"fields", "field_requirements", "field_constraints", "字段", "字段约束"}
_FACT_METADATA = {"可用能力", "模板", "前端", "数据库", "数据范围", "template_capabilities"}
_TRANSITION_KEYS = {"name", "from_states", "to_state", "roles", "set_timestamp"}
_PREDICATE_KEYS = {"field", "op", "value"}
_SCOPES = {"all", "own", "assigned"}
_FIELD_KINDS = {"text", "integer", "boolean", "date", "datetime", "enum"}
_FIELD_ATTRIBUTES = {
    "required",
    "min_length",
    "max_length",
    "choices",
    "searchable",
    "filterable",
    "date_range",
}


def _decode(value):
    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            result = json.loads(value)
        except ValueError:
            return value
        if isinstance(result, (dict, list)):
            return result
    return value


def _business_facts(facts, entity_names):
    """Read business positions without reinterpreting field names or prose.

    Facts remain independent of the implementation. Only an explicit entity
    descriptor (or an existing entity-keyed section) supplies inherited scope.
    Collection entries may be objects, arrays, keyed objects or JSON strings.
    """

    def entries(kind, value, path, entity=None):
        value = _decode(value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from entries(kind, item, f"{path}.{index}", entity)
        elif isinstance(value, dict):
            metric_mapping = (
                kind == "metrics"
                and value
                and all(
                    isinstance(_decode(item), dict)
                    and set(_decode(item)) & {"name", "entity", "kind", "role_scope"}
                    for item in value.values()
                )
            )
            if not metric_mapping and set(value) & (_FACT_COLLECTIONS[kind] | {"role_scope"}):
                descriptor = dict(value)
                if entity is not None and "entity" not in descriptor:
                    descriptor["entity"] = entity
                yield kind, path, descriptor
            else:
                for key, item in value.items():
                    item = _decode(item)
                    if (
                        isinstance(item, dict)
                        and kind == "metrics"
                        and "name" not in item
                        and set(item) & (_FACT_COLLECTIONS[kind] | {"role_scope"})
                    ):
                        # A keyed metric object declares its stable identifier.
                        item = {"name": key, **item}
                    yield from entries(kind, item, f"{path}.{key}", entity)

    def walk(value, path="", entity=None, entity_container=False):
        value = _decode(value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from walk(item, f"{path}.{index}", entity, entity_container)
        elif isinstance(value, dict):
            if entity_container and isinstance(value.get("name"), str):
                entity = value["name"]
            for key, item in value.items():
                if key in _FIELD_COLLECTIONS or key in _FACT_METADATA:
                    continue
                target = f"{path}.{key}" if path else key
                if key in _FACT_COLLECTIONS:
                    decoded = _decode(item)
                    # A field literally named metrics may use the documented
                    # entity-keyed field grammar, outside a fields container.
                    field_value = (
                        isinstance(decoded, dict)
                        and isinstance(decoded.get("kind"), str)
                        and decoded.get("kind") in _FIELD_KINDS
                        and (entity is not None or bool(set(decoded) & _FIELD_ATTRIBUTES))
                        and ("name" not in decoded or "field" in decoded)
                    )
                    if not field_value:
                        yield from entries(key, item, target, entity)
                else:
                    yield from walk(
                        item,
                        target,
                        key
                        if key in entity_names or (entity_container and "name" not in value)
                        else entity,
                        key == "entities",
                    )

    yield from walk(facts)


def _same_fact(expected, actual):
    """Exact typed values; declaration lists are unordered but cannot broaden."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _same_fact(value, actual[key]) for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return False
        remaining = list(actual)
        for item in expected:
            match = next(
                (i for i, candidate in enumerate(remaining) if _same_fact(item, candidate)), None
            )
            if match is None:
                return False
            remaining.pop(match)
        return True
    return type(expected) is type(actual) and expected == actual


def _semantic_descriptor(kind, descriptor):
    expected = {
        key: _decode(value) if key in {"actions", "filters", "transitions"} else value
        for key, value in descriptor.items()
        if key in _FACT_COLLECTIONS[kind]
    }
    if kind == "metrics" and "filters" in expected:
        predicates = expected["filters"]
        if isinstance(predicates, list):
            expected["filters"] = [
                {"op": "eq", **{k: v for k, v in _decode(item).items() if k in _PREDICATE_KEYS}}
                if isinstance(_decode(item), dict) and {"field", "value"} <= set(_decode(item))
                else None
                for item in predicates
            ]
    if kind == "workflows" and "transitions" in expected:
        transitions = expected["transitions"]
        if isinstance(transitions, list):
            expected["transitions"] = [
                {
                    k: _decode(v) if k in {"roles", "from_states"} else v
                    for k, v in _decode(item).items()
                    if k in _TRANSITION_KEYS
                }
                if isinstance(_decode(item), dict) and set(_decode(item)) & _TRANSITION_KEYS
                else None
                for item in transitions
            ]
    return expected


def _metric_scope(descriptor):
    """Return only unambiguous role grants; never guess an unknown scope form."""
    value = _decode(descriptor["role_scope"])

    def identifier(item):
        return isinstance(item, str) and bool(re.fullmatch(r"[a-z][a-z0-9_]{0,39}", item))

    if isinstance(value, list) and value and all(identifier(role) for role in value):
        if len(value) == len(set(value)):
            return dict.fromkeys(value)
    if (
        isinstance(value, dict)
        and value
        and all(
            identifier(role) and isinstance(scope, str) and scope in _SCOPES
            for role, scope in value.items()
        )
    ):
        return value
    return None


def _business_fact_gaps(requirement, plan):
    gaps = []
    entities = {entity.name for entity in plan.entities}
    for kind, path, descriptor in _business_facts(requirement.facts, entities):
        expected = _semantic_descriptor(kind, descriptor)
        scopes = None
        if kind == "metrics" and "role_scope" in descriptor:
            scopes = _metric_scope(descriptor)
            if scopes is None:
                gaps.append(
                    "业务事实形状不支持 "
                    + path
                    + ".role_scope：需要角色ID列表或角色到all/own/assigned的映射"
                )
                continue
        if not expected and scopes is None:
            continue
        business = plan.business
        candidates = getattr(business, kind) if business else []
        matches = [item for item in candidates if _same_fact(expected, item.model_dump())]
        if not matches:
            gaps.append("业务设计缺少已确认的业务事实：" + path)
            continue
        if scopes is not None and not any(
            all(
                any(
                    permission.role == role
                    and permission.entity == metric.entity
                    and "read_metrics" in permission.actions
                    and (scope is None or permission.scope == scope)
                    for permission in business.permissions
                )
                for role, scope in scopes.items()
            )
            for metric in matches
        ):
            gaps.append("业务指标缺少已确认的角色统计范围：" + path + ".role_scope")
    return gaps


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
    gaps = _business_fact_gaps(requirement, plan)
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
        return gaps
    business = plan.business
    if business is None:
        return gaps + [
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
    return gaps + [
        "业务设计缺少已确认的可执行能力：" + name
        for name in sorted(requested)
        if not implemented[name]
    ]
