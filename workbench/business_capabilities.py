"""Bounded declarative business capabilities and executable requirement coverage."""

import json
import re
from typing import get_args

from workbench.business_contracts import Action
from workbench.requirement_coverage import (
    BUSINESS_CONSTRAINT_CONTAINERS,
    _business_schema,
    _presentation_namespace,
)

_ALIASES = {
    "metrics": {
        "type": "kind",
        "group_field": "group_by",
        "interval": "bucket",
        "allowed_roles": "role_scope",
    },
    "relations": {"from": "entity", "to": "target_entity", "target": "target_entity"},
    "workflows": {"field": "status_field", "initial_state": "initial"},
    "resources": {"name": "entity", "handling_notes": "notes"},
}
_EXTRA_KEYS = {
    "metrics": {"filter", "role_scope", "scope_aware"},
    "relations": {"kind"},
    "permissions": {"only_actions", "denied_actions", "forbidden_actions", "read_only"},
    "notifications": {"triggers", "recipients", "persistent", "condition", "overdue_rule"},
    "resources": {
        "capabilities",
        "features",
        "assignment",
        "audit_history",
        "initial_state",
        "state_transitions",
    },
    "workflows": {"protected_fields"},
}
_ACTION_ALIASES = {
    "view_audit": "read_audit",
    "view_metrics": "read_metrics",
    "view_history": "read_history",
    "note": "add_note",
    "comment": "add_note",
}
_EVENT_ALIASES = {
    "assignment": "assigned",
    "handling_note": "note_added",
    "comment_added": "note_added",
    "state_change": "transitioned",
    "state_changed": "transitioned",
    "overdue": "due",
}
_RECIPIENT_ALIASES = {
    "assignee_id": "assignee",
    "created_by": "creator",
    "request_submitter": "creator",
}

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


def _fact_domain(key, value, domain, *, entity_position=False):
    """Collection names inside UI dictionaries remain display vocabulary.

    Re-enter business interpretation only through a structural, explicitly
    named business contract, not a caption mentioning permissions or metrics.
    Entity/record positions retain their identifiers even if called 'labels'.
    """
    if _presentation_namespace(key) and not entity_position:
        return "presentation"
    if (
        domain == "presentation"
        and key in BUSINESS_CONSTRAINT_CONTAINERS
        and _business_schema(value)
    ):
        return "business"
    return domain


def _business_facts(facts, entity_names):
    """Read business positions without reinterpreting field names or prose.

    Facts remain independent of the implementation. Only an explicit entity
    descriptor (or an existing entity-keyed section) supplies inherited scope.
    Collection entries may be objects, arrays, keyed objects or JSON strings.
    An opaque collection identity keeps independent permission matrices apart,
    even if untrusted dictionary keys happen to produce identical display paths.
    """

    def entries(kind, value, path, entity=None, metric_defaults=None, collection=None):
        if collection is None:
            collection = object()
        value = _decode(value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from entries(
                    kind, item, f"{path}.{index}", entity, metric_defaults, collection
                )
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
            keys = (
                _FACT_COLLECTIONS[kind] | set(_ALIASES.get(kind, {})) | _EXTRA_KEYS.get(kind, set())
            )
            if not metric_mapping and set(value) & keys:
                descriptor = dict(value)
                if kind == "metrics" and metric_defaults:
                    descriptor = {**metric_defaults, **descriptor}
                if entity is not None and "entity" not in descriptor:
                    descriptor["entity"] = entity
                yield kind, path, descriptor, collection
            else:
                for key, item in value.items():
                    item = _decode(item)
                    if (
                        isinstance(item, dict)
                        and kind == "metrics"
                        and "name" not in item
                        and set(item) & keys
                    ):
                        # A keyed metric object declares its stable identifier.
                        item = {"name": key, **item}
                    yield from entries(
                        kind, item, f"{path}.{key}", entity, metric_defaults, collection
                    )

    def walk(value, path="", entity=None, entity_container=False, domain=None):
        value = _decode(value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from walk(item, f"{path}.{index}", entity, entity_container, domain)
        elif isinstance(value, dict):
            if entity_container and isinstance(value.get("name"), str):
                entity = value["name"]
            for key, item in value.items():
                if key in _FIELD_COLLECTIONS or key in _FACT_METADATA:
                    continue
                target = f"{path}.{key}" if path else key
                child_domain = _fact_domain(
                    key, item, domain, entity_position=entity_container and domain != "presentation"
                )
                if domain == "presentation" or child_domain == "presentation":
                    yield from walk(item, target, entity, domain=child_domain)
                    continue
                kind = "notifications" if key == "reminders" else key
                if kind in _FACT_COLLECTIONS:
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
                        defaults = {}
                        if kind == "metrics":
                            if "metrics_roles" in value:
                                defaults["role_scope"] = value["metrics_roles"]
                                defaults["_exclusive_roles"] = True
                            if "metrics_scope" in value:
                                defaults["_global_scope"] = value["metrics_scope"]
                        yield from entries(kind, item, target, entity, defaults)
                else:
                    yield from walk(
                        item,
                        target,
                        key
                        if key in entity_names or (entity_container and "name" not in value)
                        else entity,
                        key == "entities",
                        child_domain,
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


def _aliases(descriptor, aliases):
    result = dict(descriptor)
    for alias, canonical in aliases.items():
        if alias not in result:
            continue
        if canonical in result and not _same_fact(result[alias], result[canonical]):
            raise ValueError(f"{alias}/{canonical} 冲突")
        result[canonical] = result.pop(alias)
    return result


def _actions(value):
    value = _decode(value)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("actions 需要动作标识列表")
    result = [_ACTION_ALIASES.get(item, item) for item in value]
    if len(result) != len(set(result)):
        raise ValueError("actions 包含重复或同义重复动作")
    if set(result) - set(get_args(Action)):
        raise ValueError("actions 包含未知动作")
    return result


def _permission_key(descriptor):
    """Only an explicit role/resource/row scope can authorize action pooling."""
    key = tuple(descriptor.get(name) for name in ("role", "entity", "scope"))
    if all(isinstance(item, str) for item in key) and key[2] in _SCOPES:
        return key
    return None


def _permission_action_sets(records):
    """Split positive grants are one action set, never an arbitrary superset.

    Keep the source records intact: every restriction and malformed declaration
    must still be checked independently, and diagnostics retain original paths.
    Missing selectors/scopes cannot borrow actions from another declaration;
    independent permission collections never authorize one another's extras.
    """
    result = {}
    for kind, _, descriptor, collection in records:
        if kind != "permissions" or (key := _permission_key(descriptor)) is None:
            continue
        if "actions" not in descriptor:
            continue
        try:
            actions = _actions(descriptor["actions"])
        except ValueError:
            continue  # The original record reports the unsupported shape below.
        result.setdefault((collection, key), set()).update(actions)
    return result


def _semantic_descriptor(kind, descriptor):
    descriptor = _aliases(descriptor, _ALIASES.get(kind, {}))
    if kind == "permissions":
        for key in ("actions", "only_actions", "denied_actions", "forbidden_actions"):
            if key in descriptor:
                descriptor[key] = _actions(descriptor[key])
        if "actions" in descriptor and not descriptor["actions"]:
            raise ValueError("actions 需要非空动作标识列表")
        if "read_only" in descriptor and type(descriptor["read_only"]) is not bool:
            raise ValueError("read_only 需要布尔值")
    if kind == "metrics" and "filter" in descriptor:
        value = _decode(descriptor["filter"])
        if not isinstance(value, dict) or not value:
            raise ValueError("filter 需要字段谓词或字段到值的映射")
        if "field" in value:
            predicates = [value]
        else:
            predicates = [{"field": key, "op": "eq", "value": item} for key, item in value.items()]
        if "filters" in descriptor and not _same_fact(predicates, _decode(descriptor["filters"])):
            raise ValueError("filter/filters 冲突")
        descriptor["filters"] = predicates
    if kind == "resources" and "audit_history" in descriptor:
        if descriptor["audit_history"] != "append-only":
            raise ValueError("audit_history 只支持 append-only")
        if descriptor.get("audit") is False:
            raise ValueError("audit/audit_history 冲突")
        descriptor["audit"] = True
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
            normalized = []
            for item in transitions:
                item = _decode(item)
                if not isinstance(item, dict):
                    normalized.append(None)
                    continue
                item = dict(item)
                if "from" in item and isinstance(item["from"], str):
                    item["from"] = [item["from"]]
                item = _aliases(item, {"from": "from_states", "to": "to_state"})
                for alias in ("set", "sets", "set_fields"):
                    if alias not in item:
                        continue
                    values = _decode(item[alias])
                    if (
                        not isinstance(values, dict)
                        or len(values) != 1
                        or list(values.values()) != ["now"]
                    ):
                        raise ValueError(alias + " 仅支持一个时间戳字段=now")
                    field = next(iter(values))
                    if "set_timestamp" in item and item["set_timestamp"] != field:
                        raise ValueError(alias + "/set_timestamp 冲突")
                    item["set_timestamp"] = field
                normalized.append(
                    {
                        k: _decode(v) if k in {"roles", "from_states"} else v
                        for k, v in item.items()
                        if k in _TRANSITION_KEYS
                    }
                    or None
                )
            expected["transitions"] = normalized
    return expected


def business_analysis_conflicts(requirement, *, previous=None):
    """Reject malformed fact expressions before they become approved obligations.

    Reuse the design validator's structural grammar. This does not compare a
    candidate Plan, infer permissions, or remove facts: the ordinary analysis
    repair gate must preserve the original request and correct its expression.
    """
    entities = {item.entity for item in requirement.entity_requirements}
    entities.update(item.entity for item in requirement.field_requirements if item.entity)
    previous = previous or {}
    previous_entities = entities | {
        item["entity"]
        for section in ("entity_requirements", "field_requirements")
        for item in previous.get(section, [])
        if item.get("entity")
    }

    def signature(kind, path, descriptor):
        return kind, path, json.dumps(descriptor, ensure_ascii=False, sort_keys=True)

    retained = {
        signature(kind, path, descriptor)
        for kind, path, descriptor, _ in _business_facts(
            previous.get("facts", {}), previous_entities
        )
    }
    diagnostics = []
    for kind, path, descriptor, _ in _business_facts(requirement.facts, entities):
        code = "requirement_business_shape"
        try:
            expected = _semantic_descriptor(kind, descriptor)
            if requirement.data_scope == "per_user" and expected:
                code = "requirement_business_scope"
                raise ValueError(
                    "per_user 与声明式业务义务冲突；业务契约要求 shared 和明确行权限。"
                    "依据原文区分普通本人记录 CRUD 与团队业务，不自动改范围或删除需求"
                )
        except ValueError as exc:
            source = {"section": "facts", "path": path, "domain": kind}
            old = signature(kind, path, descriptor) in retained
            diagnostics.append(
                {
                    "code": code,
                    "target": {"entity": descriptor.get("entity"), "field": None},
                    "attribute": kind,
                    "sources": [
                        {
                            "source": source,
                            "expected": descriptor,
                            "origin": "previous_requirement" if old else "model_analysis",
                            **({"previous_source": dict(source)} if old else {}),
                            "text": str(exc) + ": " + json.dumps(descriptor, ensure_ascii=False),
                            "user_sources": [],
                        }
                    ],
                    "message": f"需求分析的业务事实 {path} 表达无效：{exc}；依据原始需求修正分析后再设计",
                }
            )
    return diagnostics


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


def _global_metric_scope(value):
    value = _decode(value)
    if isinstance(value, dict):
        result = _metric_scope({"role_scope": value})
        if result is not None:
            return result
    if isinstance(value, str):
        value = re.sub(r"[（(]只按本人可见行计算[）)]", "", value)
        result = {}
        for part in re.split(r"[;；,，]", value):
            match = re.fullmatch(r"\s*([a-z][a-z0-9_]{0,39})\s*=\s*(all|own|assigned)\s*", part)
            if not match or match[1] in result:
                break
            result[match[1]] = match[2]
        else:
            if result:
                return result
    raise ValueError("metrics_scope 需要明确的角色=all/own/assigned映射")


def _notification_match(descriptor, business):
    """Aggregate trigger/recipient catalogs are unions, not a Cartesian policy.

    An event-specific recipients list, by contrast, applies to that event on
    one matching resource. An explicit entity always binds that resource.
    """
    value = dict(descriptor)
    channel = value.get("channel", "in_app")
    if not isinstance(channel, str) or channel not in {"in_app", "in-app", "in_app_persistent"}:
        raise ValueError("channel 仅支持持久化站内通知")
    if "persistent" in value and value["persistent"] is not True:
        raise ValueError("persistent 必须为 true")
    aggregate = "triggers" in value
    triggers = _decode(value.get("triggers", [value.get("event")]))
    if (
        not isinstance(triggers, list)
        or not triggers
        or not all(item is None or isinstance(item, str) for item in triggers)
    ):
        raise ValueError("triggers 需要非空事件列表")
    recipients = _decode(
        value.get("recipients", [value["recipient"]] if "recipient" in value else [])
    )
    if not isinstance(recipients, list) or not all(isinstance(item, str) for item in recipients):
        raise ValueError("recipients 需要接收者列表")
    recipients = [_RECIPIENT_ALIASES.get(item, item) for item in recipients]
    if any(item not in {"creator", "assignee"} for item in recipients):
        raise ValueError("未知通知接收者")
    condition = value.get("condition", value.get("overdue_rule"))
    condition_field = None
    if condition is not None:
        if not isinstance(condition, str):
            raise ValueError("逾期条件需要明确的截止时间与未解决状态")
        match = re.fullmatch(
            r"\s*([a-z][a-z0-9_]*)\s*<\s*now\s+and\s+state\s*!=\s*resolved\s*", condition
        )
        if match is None:
            match = re.fullmatch(
                r"\s*([a-z][a-z0-9_]*)\s*早于当前时间且状态非\s*resolved\s*时生成逾期提醒\s*",
                condition,
            )
        if match is None:
            raise ValueError("未支持的显式逾期条件")
        condition_field = match[1]
    notices = [] if business is None else business.notifications
    workflows = {} if business is None else {item.entity: item for item in business.workflows}

    def covers(trigger, requested_recipients):
        event = _EVENT_ALIASES.get(trigger, trigger)
        if event == "resolved":
            event = "transitioned"
        if event not in {None, "created", "assigned", "transitioned", "note_added", "due"}:
            raise ValueError("未知通知事件 " + str(trigger))
        selector = value.get("transition")
        # Requirement facts may describe every state change with no selector.
        # The executable contract still needs one concrete notification per
        # declared transition; a nullable fact must never become a null runtime
        # rule or weaken an explicitly named transition.
        generic_transition = event == "transitioned" and (selector is None or selector == "*")
        candidates = [
            item
            for item in notices
            if (event is None or item.event == event)
            and ("entity" not in value or item.entity == value["entity"])
            and (generic_transition or "transition" not in value or item.transition == selector)
            and ("due_field" not in value or item.due_field == value["due_field"])
        ]
        for entity in {item.entity for item in candidates}:
            matches = [item for item in candidates if item.entity == entity]
            workflow = workflows.get(entity)
            transitions = [None]
            if trigger == "resolved":
                transitions = (
                    [item.name for item in workflow.transitions if item.to_state == "resolved"]
                    if workflow
                    else []
                )
            elif generic_transition:
                transitions = [item.name for item in workflow.transitions] if workflow else []
            elif event == "transitioned":
                transitions = (
                    [selector]
                    if workflow and any(item.name == selector for item in workflow.transitions)
                    else []
                )
            if condition_field and event == "due":
                if not workflow:
                    continue
                terminal = {item.to_state for item in workflow.transitions} - {
                    state for item in workflow.transitions for state in item.from_states
                }
                if terminal != {"resolved"}:
                    continue
                matches = [item for item in matches if item.due_field == condition_field]
            if transitions and all(
                all(
                    any(
                        (transition is None or item.transition == transition)
                        and (recipient is None or item.recipient == recipient)
                        for item in matches
                    )
                    for recipient in (requested_recipients or [None])
                )
                for transition in transitions
            ):
                return True
        return False

    if not all(covers(trigger, [] if aggregate else recipients) for trigger in triggers):
        return False
    if aggregate:
        if not all(
            any(covers(trigger, [recipient]) for trigger in triggers) for recipient in recipients
        ):
            return False
        original = _decode(value.get("recipients", []))
        if (
            "request_submitter" in original
            and "resolved" in triggers
            and not covers("resolved", ["creator"])
        ):
            return False
    return True


def _resource_matches(descriptor, resource, business, plan):
    workflow = next((item for item in business.workflows if item.entity == resource.entity), None)
    if "assignment" in descriptor:
        expected = descriptor["assignment"]
        actual = bool(resource.assignee_field) and any(
            item.entity == resource.entity and "assign" in item.actions
            for item in business.permissions
        )
        if type(expected) is not bool or expected is not actual:
            return False
    if "initial_state" in descriptor and (
        not workflow or workflow.initial != descriptor["initial_state"]
    ):
        return False
    if "state_transitions" in descriptor and not _same_fact(
        _decode(descriptor["state_transitions"]),
        [item.name for item in workflow.transitions] if workflow else [],
    ):
        return False
    for key in ("features", "capabilities"):
        if key not in descriptor:
            continue
        names = _decode(descriptor[key])
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            raise ValueError(key + " 需要能力标识列表")
        actions = {
            action
            for item in business.permissions
            if item.entity == resource.entity
            for action in item.actions
        }
        implemented = {
            "crud": {"create", "read", "update", "archive"} <= actions,
            "native-crud": {"create", "read", "update", "archive"} <= actions,
            "archive": resource.archive,
            "archive-history": resource.archive,
            "audit": resource.audit,
            "append-only-audit": resource.audit,
            "handling_notes": resource.notes,
            "handling-notes": resource.notes,
            "assignment": bool(resource.assignee_field) and "assign" in actions,
            "named_transitions": bool(workflow),
            "named-state-transitions": bool(workflow),
            "relations": any(item.entity == resource.entity for item in business.relations),
            "foreign-key-relations": any(
                item.entity == resource.entity for item in business.relations
            ),
            "in-app-reminders": any(
                item.entity == resource.entity for item in business.notifications
            ),
            "keyword_search": any(
                field.searchable
                for entity in plan.entities
                if entity.name == resource.entity
                for field in entity.fields
            ),
            "exact_filter": any(
                field.filterable
                for entity in plan.entities
                if entity.name == resource.entity
                for field in entity.fields
            ),
        }
        if any(name in implemented and not implemented[name] for name in names):
            return False
    return True


def _bounded(value, depth=0):
    if depth > 6:
        return "[nested]"
    if isinstance(value, str):
        return value[:160]
    if isinstance(value, dict):
        return {str(key)[:80]: _bounded(item, depth + 1) for key, item in list(value.items())[:20]}
    if isinstance(value, list):
        return [_bounded(item, depth + 1) for item in value[:20]]
    return value


def _policy_roots(facts, path="", domain=None, entity_container=False):
    value = _decode(facts)
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from _policy_roots(item, f"{path}.{index}", domain, entity_container)
    elif isinstance(value, dict):
        if (
            domain != "presentation"
            and "permissions" in value
            and (
                "resources" in value
                or "roles" in value
                or value.get("permissions_complete") is True
            )
        ):
            yield path, value
        for key, item in value.items():
            if key not in _FIELD_COLLECTIONS | _FACT_METADATA:
                child_domain = _fact_domain(
                    key, item, domain, entity_position=entity_container and domain != "presentation"
                )
                yield from _policy_roots(
                    item, f"{path}.{key}" if path else key, child_domain, key == "entities"
                )


def _business_fact_gaps(requirement, plan, diagnostics=None):
    gaps = []
    entities = {entity.name for entity in plan.entities}
    records = list(_business_facts(requirement.facts, entities))
    permission_actions = _permission_action_sets(records)
    business = plan.business
    metric_access = set()
    approved_scopes = {}
    for kind, _, descriptor, _ in records:
        if (
            kind == "permissions"
            and isinstance(descriptor.get("role"), str)
            and isinstance(descriptor.get("entity"), str)
        ):
            approved_scopes[descriptor["role"], descriptor["entity"]] = descriptor.get("scope")
        if kind == "metrics":
            try:
                descriptor = _aliases(descriptor, _ALIASES[kind])
            except ValueError:
                continue  # The main pass emits the specific conflicting-alias diagnostic.
            if "role_scope" in descriptor:
                scopes = _metric_scope(descriptor)
                if scopes and isinstance(descriptor.get("entity"), str):
                    metric_access.update((role, descriptor["entity"]) for role in scopes)
    virtual_permissions = [
        descriptor
        for kind, _, descriptor, _ in records
        if kind == "permissions"
        and descriptor.get("entity") == "metrics"
        and "metrics" not in entities
    ]
    metric_entities = {
        descriptor["entity"]
        for kind, _, descriptor, _ in records
        if kind == "metrics" and isinstance(descriptor.get("entity"), str)
    }
    for descriptor in virtual_permissions:
        if isinstance(descriptor.get("role"), str):
            metric_access.update((descriptor["role"], entity) for entity in metric_entities)

    def report(kind, path, expected, actual, code="business_constraint_mismatch", reason=None):
        expected, actual = _bounded(expected), _bounded(actual)
        message = (
            "业务事实未覆盖 "
            + path
            + "："
            + (reason or json.dumps(expected, ensure_ascii=False, separators=(",", ":")))
        )
        gaps.append(message[:700])
        if diagnostics is not None:
            diagnostics.append(
                {
                    "code": code,
                    "source": {"section": "facts", "path": path[:240], "domain": kind},
                    "expected": expected,
                    "actual": actual,
                }
            )

    def permission_matches(expected, descriptor, candidate):
        base = {key: value for key, value in expected.items() if key != "actions"}
        if not _same_fact(base, candidate.model_dump()):
            return False
        actual = set(candidate.actions)
        requested = set(expected.get("actions", []))
        if not requested <= actual:
            return False
        permitted = set(requested)
        # History is a strict information subset of the explicitly approved
        # audit view, with the same immutable row scope. It is not implied by read.
        if "read_audit" in requested:
            permitted.add("read_history")
        if (candidate.role, candidate.entity) in metric_access:
            permitted.add("read_metrics")
        if "actions" in expected and not actual <= permitted:
            return False
        if "only_actions" in descriptor and not actual <= set(_actions(descriptor["only_actions"])):
            return False
        if descriptor.get("read_only") is True and actual & {
            "create",
            "update",
            "archive",
            "assign",
            "transition",
            "add_note",
        }:
            return False
        for key in ("denied_actions", "forbidden_actions"):
            if key in descriptor and actual & set(_actions(descriptor[key])):
                return False
        return True

    # A policy matrix co-declared with its roles/resources is complete. Rows
    # absent from it remain denied; a new role/row is not a harmless superset.
    for root_path, root in _policy_roots(requirement.facts):
        prefix = root_path + ".permissions" if root_path else "permissions"
        declarations = [
            item
            for kind, path, item, _ in records
            if kind == "permissions" and (path == prefix or path.startswith(prefix + "."))
        ]
        pairs = {
            (item.get("role"), item.get("entity"))
            for item in declarations
            if isinstance(item.get("role"), str) and isinstance(item.get("entity"), str)
        }
        if business:
            extra = [
                item.model_dump()
                for item in business.permissions
                if (item.role, item.entity) not in pairs
                and not (
                    (item.role, item.entity) in metric_access
                    and set(item.actions) == {"read_metrics"}
                )
            ]
            if extra:
                report(
                    "permissions",
                    prefix,
                    [{"role": role, "entity": entity} for role, entity in sorted(pairs)],
                    extra,
                    "business_unapproved_grant",
                )
            raw_roles = _decode(root.get("roles"))
            if isinstance(raw_roles, list):
                roles = {
                    item.get("name") if isinstance(item, dict) else item
                    for item in raw_roles
                    if isinstance(item, str)
                    or (isinstance(item, dict) and isinstance(item.get("name"), str))
                }
            else:
                roles = {role for role, _ in pairs}
            if roles and {item.name for item in business.roles} != roles:
                report(
                    "roles",
                    root_path + ".roles",
                    sorted(roles),
                    [item.name for item in business.roles],
                    "business_unapproved_role",
                )
            for key, actual in (
                ("bootstrap_role", business.bootstrap_role),
                ("scope", plan.data_scope),
            ):
                if key in root and not _same_fact(root[key], actual):
                    report("policy", root_path + "." + key, root[key], actual)
            for key in ("registration_default_role", "default_registration_role"):
                if key in root and root[key] != business.registration.default_role:
                    report(
                        "policy",
                        root_path + "." + key,
                        root[key],
                        business.registration.default_role,
                    )
            administrators = _decode(
                root.get(
                    "role_admin_roles",
                    [root["bootstrap_role"]] if "bootstrap_role" in root else None,
                )
            )
            if administrators is not None and not _same_fact(
                administrators, business.role_admin_roles
            ):
                report(
                    "policy",
                    root_path + ".role_admin_roles",
                    administrators,
                    business.role_admin_roles,
                    "business_unapproved_grant",
                )
            audit = _decode(root.get("audit"))
            if isinstance(audit, dict):
                required_entities = _decode(
                    audit.get("entities", [item.entity for item in business.resources])
                )
                if not isinstance(required_entities, list) or not all(
                    isinstance(item, str) for item in required_entities
                ):
                    report("audit", root_path + ".audit", audit, [], "business_unsupported_shape")
                elif any(
                    not any(
                        resource.entity == entity and resource.audit
                        for resource in business.resources
                    )
                    for entity in required_entities
                ):
                    report(
                        "audit",
                        root_path + ".audit",
                        audit,
                        [item.model_dump() for item in business.resources],
                    )
                for flag in ("immutable", "append_only"):
                    if flag in audit and audit[flag] is not True:
                        report("audit", root_path + ".audit." + flag, audit[flag], True)
            handling = _decode(root.get("handling_notes"))
            if isinstance(handling, list) and any(
                not any(
                    resource.entity == entity and resource.notes for resource in business.resources
                )
                for entity in handling
            ):
                report(
                    "resources",
                    root_path + ".handling_notes",
                    handling,
                    [item.model_dump() for item in business.resources],
                )
            assignment = _decode(root.get("assignment"))
            if isinstance(assignment, dict):
                targets = _decode(assignment.get("entities", []))
                if not isinstance(targets, list) or not all(
                    isinstance(item, str) for item in targets
                ):
                    report(
                        "resources",
                        root_path + ".assignment",
                        assignment,
                        [],
                        "business_unsupported_shape",
                    )
                elif any(
                    not any(
                        resource.entity == entity
                        and resource.assignee_field == assignment.get("assignee_field")
                        and any(
                            permission.entity == entity and "assign" in permission.actions
                            for permission in business.permissions
                        )
                        for resource in business.resources
                    )
                    for entity in targets
                ):
                    report(
                        "resources",
                        root_path + ".assignment",
                        assignment,
                        [item.model_dump() for item in business.resources],
                    )

    for kind, path, raw_descriptor, collection in records:
        candidates = getattr(business, kind) if business else []
        try:
            descriptor = _aliases(raw_descriptor, _ALIASES.get(kind, {}))
            expected = _semantic_descriptor(kind, raw_descriptor)
            if kind == "permissions" and "actions" in expected:
                key = (collection, _permission_key(expected))
                if key in permission_actions:
                    expected["actions"] = sorted(permission_actions[key])
            scopes = None
            if kind == "metrics" and "role_scope" in descriptor:
                scopes = _metric_scope(descriptor)
                if scopes is None:
                    raise ValueError("role_scope：需要角色ID列表或角色到all/own/assigned的映射")
            if kind == "metrics" and "_global_scope" in descriptor:
                global_scopes = _global_metric_scope(descriptor["_global_scope"])
                if scopes is not None and set(scopes) != set(global_scopes):
                    raise ValueError("metrics_roles/metrics_scope 角色范围冲突")
                resolved_scopes = {
                    role: approved_scopes.get((role, expected.get("entity")), scope)
                    if scope == "assigned"
                    else scope
                    for role, scope in global_scopes.items()
                }
                if scopes is not None and any(
                    scope is not None and scope != resolved_scopes[role]
                    for role, scope in scopes.items()
                ):
                    raise ValueError("role_scope/metrics_scope 显式行范围冲突")
                scopes = resolved_scopes
            if kind == "metrics" and "scope_aware" in descriptor:
                if descriptor["scope_aware"] is not True:
                    raise ValueError("scope_aware 必须为 true；统计始终遵守角色行权限")
                if scopes is not None:
                    scopes = {
                        role: approved_scopes.get((role, expected.get("entity")), scope)
                        if scope is None
                        else scope
                        for role, scope in scopes.items()
                    }
            if kind == "notifications":
                if not _notification_match(descriptor, business):
                    report(kind, path, descriptor, [item.model_dump() for item in candidates])
                continue
            if kind == "permissions" and descriptor in virtual_permissions:
                actions = _actions(descriptor.get("actions", []))
                if not actions or set(actions) - {"read", "read_metrics"}:
                    raise ValueError("虚拟 metrics 权限只支持 read/read_metrics")
                role = descriptor.get("role")
                actual = (
                    []
                    if business is None
                    else [
                        item.model_dump()
                        for item in business.permissions
                        if item.role == role and "read_metrics" in item.actions
                    ]
                )
                missing = []
                for entity in metric_entities:
                    scope = descriptor.get("scope")
                    # An aggregate assigned policy coexists with an explicit
                    # per-resource policy (e.g. shared customer read=all).
                    if scope == "assigned" and approved_scopes.get((role, entity)) == "all":
                        scope = "all"
                    if not business or not any(
                        item.role == role
                        and item.entity == entity
                        and "read_metrics" in item.actions
                        and (scope is None or item.scope == scope)
                        for item in business.permissions
                    ):
                        missing.append(
                            {
                                "role": role,
                                "entity": entity,
                                "action": "read_metrics",
                                "scope": scope,
                            }
                        )
                if not metric_entities or missing:
                    report(kind, path, missing or descriptor, actual, "business_scope_mismatch")
                continue
            if not expected and scopes is None:
                continue
            if kind == "relations" and descriptor.get("kind") == "reverse":
                target, owner = expected.get("target_entity"), expected.get("entity")
                if not target or not owner or expected.get("field", target) != target:
                    raise ValueError("reverse 需要明确父实体与目标子实体集合")
                reverse = {"entity": target, "target_entity": owner}
                if not any(_same_fact(reverse, item.model_dump()) for item in candidates):
                    report(kind, path, reverse, [item.model_dump() for item in candidates])
                continue
            matches = [
                item
                for item in candidates
                if (
                    permission_matches(expected, descriptor, item)
                    if kind == "permissions"
                    else _same_fact(expected, item.model_dump())
                )
            ]
            if kind == "resources":
                matches = [
                    item for item in matches if _resource_matches(descriptor, item, business, plan)
                ]
            if kind == "workflows" and "protected_fields" in descriptor:
                protected = _decode(descriptor["protected_fields"])
                if not isinstance(protected, list) or not all(
                    isinstance(item, str) for item in protected
                ):
                    raise ValueError("protected_fields 需要字段标识列表")
                matches = [
                    item
                    for item in matches
                    if set(protected)
                    <= {
                        item.status_field,
                        next(
                            (
                                resource.assignee_field
                                for resource in business.resources
                                if resource.entity == item.entity
                            ),
                            None,
                        ),
                    }
                ]
            if not matches:
                selectors = {
                    key: value
                    for key, value in expected.items()
                    if key in {"name", "entity", "role", "field"}
                }
                relevant = [item for item in candidates if _same_fact(selectors, item.model_dump())]
                expected_detail = {
                    **expected,
                    **{
                        key: descriptor[key]
                        for key in _EXTRA_KEYS.get(kind, set())
                        if key in descriptor
                    },
                }
                actual_detail = [item.model_dump() for item in relevant or candidates][:4]
                if kind == "resources":
                    for item in actual_detail:
                        item["field_queries"] = [
                            {
                                "field": field.name,
                                "searchable": field.searchable,
                                "filterable": field.filterable,
                            }
                            for entity in plan.entities
                            if entity.name == item["entity"]
                            for field in entity.fields
                        ]
                report(
                    kind,
                    path,
                    expected_detail,
                    actual_detail,
                    "business_constraint_mismatch" if relevant else "business_missing_record",
                )
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
                scope_expected = [
                    [
                        {
                            "role": role,
                            "entity": metric.entity,
                            "action": "read_metrics",
                            "scope": scope
                            if scope is not None
                            else approved_scopes.get((role, metric.entity)),
                        }
                        for role, scope in scopes.items()
                    ]
                    for metric in matches
                ]
                report(
                    kind,
                    path + ".role_scope",
                    scope_expected[0] if len(scope_expected) == 1 else {"any_of": scope_expected},
                    [
                        item.model_dump()
                        for item in business.permissions
                        if item.entity in {metric.entity for metric in matches}
                    ],
                    "business_scope_mismatch",
                )
            if scopes is not None and (
                "allowed_roles" in raw_descriptor or raw_descriptor.get("_exclusive_roles")
            ):
                extra = [
                    item.model_dump()
                    for item in business.permissions
                    if item.entity in {metric.entity for metric in matches}
                    and "read_metrics" in item.actions
                    and item.role not in scopes
                ]
                if extra:
                    report(
                        kind,
                        path + ".allowed_roles",
                        sorted(scopes),
                        extra,
                        "business_unapproved_grant",
                    )
        except ValueError as error:
            if str(error).startswith("role_scope"):
                path += ".role_scope"
            report(
                kind,
                path,
                {
                    key: value
                    for key, value in raw_descriptor.items()
                    if key
                    in _FACT_COLLECTIONS[kind]
                    | set(_ALIASES.get(kind, {}))
                    | _EXTRA_KEYS.get(kind, set())
                },
                [],
                "business_unsupported_shape",
                "业务事实形状不支持 " + str(error),
            )
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


def business_gaps(requirement, plan, *, diagnostics=None):
    """Check recognized obligations; independent review/tests still assess prose semantics."""
    gaps = _business_fact_gaps(requirement, plan, diagnostics)
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
    # Audit and ordinary read are different endpoint grants. Explicit handling
    # history must be usable by the actors whose declared role handles notes.
    resource_labels = {item.entity: {item.entity} for item in business.resources}
    for kind, _, descriptor, _ in _business_facts(requirement.facts, set(resource_labels)):
        if kind == "resources":
            entity = descriptor.get("entity", descriptor.get("name"))
            if (
                isinstance(entity, str)
                and entity in resource_labels
                and isinstance(descriptor.get("label"), str)
            ):
                resource_labels[entity].add(descriptor["label"])
    reported = set()
    for section in ("summary", "features", "acceptance", "users"):
        texts = (
            [getattr(requirement, section)]
            if section == "summary"
            else getattr(requirement, section)
        )
        for index, text in enumerate(texts):
            for clause in re.split(r"[；;。\n]", text):
                if not re.search(
                    r"查看处理过程|查看处理历史|按时间顺序(?:查看|.*出现在|.*显示)|handling.history",
                    clause,
                    re.I,
                ):
                    continue
                targets = {
                    entity
                    for entity, labels in resource_labels.items()
                    if any(
                        re.search(rf"(?<![a-z0-9_]){re.escape(label)}(?![a-z0-9_])", clause, re.I)
                        if label.isascii()
                        else label in clause
                        for label in labels
                    )
                }
                roles = {
                    role.name
                    for role in business.roles
                    if re.search(
                        rf"(?<![a-z0-9_]){re.escape(role.name)}(?![a-z0-9_])", clause, re.I
                    )
                    or role.label in clause
                }
                for permission in business.permissions:
                    key = (permission.role, permission.entity)
                    if (
                        key in reported
                        or "add_note" not in permission.actions
                        or "read_history" in permission.actions
                        or (targets and permission.entity not in targets)
                        or (roles and permission.role not in roles)
                    ):
                        continue
                    reported.add(key)
                    expected = {
                        "role": permission.role,
                        "entity": permission.entity,
                        "action": "read_history",
                        "scope": permission.scope,
                    }
                    gaps.append(
                        "业务处理历史缺少已确认的读取权限："
                        + json.dumps(expected, ensure_ascii=False)
                    )
                    if diagnostics is not None:
                        diagnostics.append(
                            {
                                "code": "business_missing_history_grant",
                                "source": {
                                    "section": section,
                                    "index": index,
                                    "domain": "permissions",
                                },
                                "expected": expected,
                                "actual": permission.model_dump(),
                            }
                        )
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
