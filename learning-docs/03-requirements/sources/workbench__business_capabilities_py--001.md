# workbench/business_capabilities.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__business_capabilities_py--002.md)

**作用：业务合同的可执行能力边界。** 按实际模板及已实现适配判断合同是否能执行，不根据模型声称动态开启能力；未登记功能保留阻塞。

**对应关系：** 选择器/规划门 → 合同检查 → 对应业务运行时。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_contracts`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_decode`（L98–L106）：接收`value`。 控制顺序：L99按`isinstance(value, str) and value.lstrip().startswith(("{", "["))`分支；L104按`isinstance(result, (dict, list))`分支。 调用`isinstance`、`value.lstrip().startswith`、`value.lstrip`、`json.loads`。 返回路径：L103的`value`；L105的`result`；L106的`value`。
- `_fact_domain`（L109–L124）：接收`key`、`value`、`domain`、`entity_position`。 源码说明：Collection names inside UI dictionaries remain display vocabulary. Re-enter business interpretation only through a structural, explicitly named business contract, not a caption mentioning permissions 。 控制顺序：L116按`_presentation_namespace(key) and not entity_position`分支；L118按`domain == "presentation" and key in BUSINESS_CONSTRAINT_CONTAINERS and _business_sche…`分支。 调用`_presentation_namespace`、`_business_schema`。 返回路径：L117的`"presentation"`；L123的`"business"`；L124的`domain`。
- `_business_facts`（L127–L231）：接收`facts`、`entity_names`。 源码说明：Read business positions without reinterpreting field names or prose. Facts remain independent of the implementation. Only an explicit entity descriptor (or an existing entity-keyed section) supplies i。 调用`walk`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_business_facts.entries`（L137–L179）：接收`kind`、`value`、`path`、`entity`、`metric_defaults`、`collection`。 控制顺序：L138按`collection is None`分支；L141按`isinstance(value, list)`分支；L142遍历`enumerate(value)`；L146按`isinstance(value, dict)`分支；L159按`not metric_mapping and set(value) & keys`分支；L161按`kind == "metrics" and metric_defaults`分支；L163按`entity is not None and "entity" not in descriptor`分支；L167遍历`value.items()`。后续分支沿下方源码相同行号继续阅读。 调用`object`、`_decode`、`isinstance`、`enumerate`、`entries`、`all`、`set`、`value.values`、`_ALIASES.get`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_business_facts.walk`（L181–L229）：接收`value`、`path`、`entity`、`entity_container`、`domain`。 控制顺序：L183按`isinstance(value, list)`分支；L184遍历`enumerate(value)`；L186按`isinstance(value, dict)`分支；L187按`entity_container and isinstance(value.get("name"), str)`分支；L189遍历`value.items()`；L190按`key in _FIELD_COLLECTIONS or key in _FACT_METADATA`分支；L196按`domain == "presentation" or child_domain == "presentation"`分支；L200按`kind in _FACT_COLLECTIONS`分支。后续分支沿下方源码相同行号继续阅读。 调用`_decode`、`isinstance`、`enumerate`、`walk`、`value.get`、`value.items`、`_fact_domain`、`decoded.get`、`bool`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_same_fact`（L234–L252）：接收`expected`、`actual`。 源码说明：Exact typed values; declaration lists are unordered but cannot broaden.。 控制顺序：L236按`isinstance(expected, dict)`分支；L240按`isinstance(expected, list)`分支；L241按`not isinstance(actual, list) or len(expected) != len(actual)`分支；L244遍历`expected`；L248按`match is None`分支。 调用`isinstance`、`all`、`_same_fact`、`expected.items`、`len`、`list`、`next`、`enumerate`、`remaining.pop`等。 返回路径：L237的`isinstance(actual, dict) and all( key in actual and _same_fact(value, actual[key]) for key…`；L242的`False`；L249的`False`。
- `_aliases`（L255–L263）：接收`descriptor`、`aliases`。 控制顺序：L257遍历`aliases.items()`；L258按`alias not in result`分支；L260按`canonical in result and not _same_fact(result[alias], result[canonical])`分支；L261抛异常，停止当前正常路径。 调用`dict`、`aliases.items`、`_same_fact`、`ValueError`、`result.pop`。 返回路径：L263的`result`。
- `_actions`（L266–L275）：接收`value`。 控制顺序：L268按`not isinstance(value, list) or not all(isinstance(item, str) for item in value)`分支；L269抛异常，停止当前正常路径；L271按`len(result) != len(set(result))`分支；L272抛异常，停止当前正常路径；L273按`set(result) - set(get_args(Action))`分支；L274抛异常，停止当前正常路径。 调用`_decode`、`isinstance`、`all`、`ValueError`、`_ACTION_ALIASES.get`、`len`、`set`、`get_args`。 返回路径：L275的`result`。
- `_permission_key`（L278–L283）：接收`descriptor`。 源码说明：Only an explicit role/resource/row scope can authorize action pooling.。 控制顺序：L281按`all(isinstance(item, str) for item in key) and key[2] in _SCOPES`分支。 调用`tuple`、`descriptor.get`、`all`、`isinstance`。 返回路径：L282的`key`；L283的`None`。
- `_permission_action_sets`（L286–L305）：接收`records`。 源码说明：Split positive grants are one action set, never an arbitrary superset. Keep the source records intact: every restriction and malformed declaration must still be checked independently, and diagnostics 。 控制顺序：L295遍历`records`；L296按`kind != "permissions" or (key := _permission_key(descriptor)) is None`分支；L298按`"actions" not in descriptor`分支。 调用`_permission_key`、`_actions`、`result.setdefault((collection, key), set()).update`、`result.setdefault`、`set`。 返回路径：L305的`result`。
- `_semantic_descriptor`（L308–L379）：接收`kind`、`descriptor`。 控制顺序：L310按`kind == "permissions" and "actions" in descriptor`分支；L312按`kind == "metrics" and "filter" in descriptor`分支；L314按`not isinstance(value, dict) or not value`分支；L315抛异常，停止当前正常路径；L316按`"field" in value`分支；L320按`"filters" in descriptor and not _same_fact(predicates, _decode(descriptor["filters"])…`分支；L321抛异常，停止当前正常路径；L323按`kind == "resources" and "audit_history" in descriptor`分支。后续分支沿下方源码相同行号继续阅读。 调用`_aliases`、`_ALIASES.get`、`_actions`、`_decode`、`isinstance`、`ValueError`、`value.items`、`_same_fact`、`descriptor.get`等。 返回路径：L379的`expected`。
- `_metric_scope`（L382–L401）：接收`descriptor`。 源码说明：Return only unambiguous role grants; never guess an unknown scope form.。 控制顺序：L389按`isinstance(value, list) and value and all(identifier(role) for role in value)`分支；L390按`len(value) == len(set(value))`分支；L392按`isinstance(value, dict) and value and all( identifier(role) and isinstance(scope, str…`分支。 调用`_decode`、`isinstance`、`all`、`identifier`、`len`、`set`、`dict.fromkeys`、`value.items`。 返回路径：L391的`dict.fromkeys(value)`；L400的`value`；L401的`None`。
- `_metric_scope.identifier`（L386–L387）：接收`item`。 调用`isinstance`、`bool`、`re.fullmatch`。 返回路径：L387的`isinstance(item, str) and bool(re.fullmatch(r"[a-z][a-z0-9_]{0,39}", item))`。
- `_global_metric_scope`（L404–L421）：接收`value`。 控制顺序：L406按`isinstance(value, dict)`分支；L408按`result is not None`分支；L410按`isinstance(value, str)`分支；L413遍历`re.split(r"[;；,，]", value)`；L415按`not match or match[1] in result`分支；L419按`result`分支；L421抛异常，停止当前正常路径。 调用`_decode`、`isinstance`、`_metric_scope`、`re.sub`、`re.split`、`re.fullmatch`、`ValueError`。 返回路径：L409的`result`；L420的`result`。
- `_notification_match`（L424–L546）：接收`descriptor`、`business`。 源码说明：Aggregate trigger/recipient catalogs are unions, not a Cartesian policy. An event-specific recipients list, by contrast, applies to that event on one matching resource. An explicit entity always binds。 控制顺序：L432按`not isinstance(channel, str) or channel not in {"in_app", "in-app", "in_app_persisten…`分支；L433抛异常，停止当前正常路径；L434按`"persistent" in value and value["persistent"] is not True`分支；L435抛异常，停止当前正常路径；L438按`not isinstance(triggers, list) or not triggers or not all(item is None or isinstance(…`分支；L443抛异常，停止当前正常路径；L447按`not isinstance(recipients, list) or not all(isinstance(item, str) for item in recipie…`分支；L448抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`dict`、`value.get`、`isinstance`、`ValueError`、`_decode`、`all`、`_RECIPIENT_ALIASES.get`、`any`、`re.fullmatch`等。 返回路径：L533的`False`；L538的`False`；L545的`False`。
- `_notification_match.covers`（L471–L530）：接收`trigger`、`requested_recipients`。 控制顺序：L473按`event == "resolved"`分支；L475按`event not in {None, "created", "assigned", "transitioned", "note_added", "due"}`分支；L476抛异常，停止当前正常路径；L491遍历`{item.entity for item in candidates}`；L495按`trigger == "resolved"`分支；L501按`generic_transition`分支；L503按`event == "transitioned"`分支；L509按`condition_field and event == "due"`分支。后续分支沿下方源码相同行号继续阅读。 调用`_EVENT_ALIASES.get`、`ValueError`、`str`、`value.get`、`workflows.get`、`any`、`all`。 返回路径：L529的`True`；L530的`False`。
- `_resource_matches`（L549–L614）：接收`descriptor`、`resource`、`business`、`plan`。 控制顺序：L551按`"assignment" in descriptor`分支；L557按`type(expected) is not bool or expected is not actual`分支；L559按`"initial_state" in descriptor and ( not workflow or workflow.initial != descriptor["i…`分支；L563按`"state_transitions" in descriptor and not _same_fact( _decode(descriptor["state_trans…`分支；L568遍历`("features", "capabilities")`；L569按`key not in descriptor`分支；L572按`not isinstance(names, list) or not all(isinstance(name, str) for name in names)`分支；L573抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`next`、`bool`、`any`、`type`、`_same_fact`、`_decode`、`isinstance`、`all`、`ValueError`。 返回路径：L558的`False`；L562的`False`；L567的`False`。
- `_bounded`（L617–L626）：接收`value`、`depth`。 控制顺序：L618按`depth > 6`分支；L620按`isinstance(value, str)`分支；L622按`isinstance(value, dict)`分支；L624按`isinstance(value, list)`分支。 调用`isinstance`、`str`、`_bounded`、`list`、`value.items`。 返回路径：L619的`"[nested]"`；L621的`value[:160]`；L623的`{str(key)[:80]: _bounded(item, depth + 1) for key, item in list(value.items())[:20]}`。
- `_policy_roots`（L629–L652）：接收`facts`、`path`、`domain`、`entity_container`。 控制顺序：L631按`isinstance(value, list)`分支；L632遍历`enumerate(value)`；L634按`isinstance(value, dict)`分支；L635按`domain != "presentation" and "permissions" in value and ( "resources" in value or "ro…`分支；L645遍历`value.items()`；L646按`key not in _FIELD_COLLECTIONS \| _FACT_METADATA`分支。 调用`_decode`、`isinstance`、`enumerate`、`_policy_roots`、`value.get`、`value.items`、`_fact_domain`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_business_fact_gaps`（L655–L1139）：接收`requirement`、`plan`、`diagnostics`。 控制顺序：L663遍历`records`；L664按`kind == "permissions" and isinstance(descriptor.get("role"), str) and isinstance(desc…`分支；L670按`kind == "metrics"`分支；L675按`"role_scope" in descriptor`分支；L677按`scopes and isinstance(descriptor.get("entity"), str)`分支；L691遍历`virtual_permissions`；L692按`isinstance(descriptor.get("role"), str)`分支；L751遍历`_policy_roots(requirement.facts)`。后续分支沿下方源码相同行号继续阅读。 调用`list`、`_business_facts`、`_permission_action_sets`、`set`、`isinstance`、`descriptor.get`、`_aliases`、`_metric_scope`、`metric_access.update`等。 返回路径：L1139的`gaps`。
- `_business_fact_gaps.report`（L695–L712）：接收`kind`、`path`、`expected`、`actual`、`code`、`reason`。 控制顺序：L704按`diagnostics is not None`分支。 调用`_bounded`、`json.dumps`、`gaps.append`、`diagnostics.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/business_capabilities.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L713。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`29431`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_capabilities.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "f8946719150dc8a4b3c278898e7e0c139c9d7894cef281acb17ec9730ec0f0bc"} -->
````python
# workbench/business_capabilities.py
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
    if kind == "permissions" and "actions" in descriptor:
        descriptor["actions"] = _actions(descriptor["actions"])
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

````
