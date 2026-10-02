# workbench/business_capabilities.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__business_capabilities_py--001.md)

**作用：业务合同的可执行能力边界。** 按实际模板及已实现适配判断合同是否能执行，不根据模型声称动态开启能力；未登记功能保留阻塞。

**对应关系：** 选择器/规划门 → 合同检查 → 对应业务运行时。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_contracts`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_business_fact_gaps.permission_matches`（L714–L747）：接收`expected`、`descriptor`、`candidate`。 控制顺序：L716按`not _same_fact(base, candidate.model_dump())`分支；L720按`not requested <= actual`分支；L725按`"read_audit" in requested`分支；L727按`(candidate.role, candidate.entity) in metric_access`分支；L729按`"actions" in expected and not actual <= permitted`分支；L731按`"only_actions" in descriptor and not actual <= set(_actions(descriptor["only_actions"…`分支；L733按`descriptor.get("read_only") is True and actual & { "create", "update", "archive", "as…`分支；L742按`"read_only" in descriptor and type(descriptor["read_only"]) is not bool`分支。后续分支沿下方源码相同行号继续阅读。 调用`expected.items`、`_same_fact`、`candidate.model_dump`、`set`、`expected.get`、`permitted.add`、`_actions`、`descriptor.get`、`type`等。 返回路径：L717的`False`；L721的`False`；L730的`False`。
- `business_gaps`（L1168–L1294）：接收`requirement`、`plan`、`diagnostics`。 源码说明：Check recognized obligations; independent review/tests still assess prose semantics.。 控制顺序：L1188按`not requested`分支；L1191按`business is None`分支；L1199遍历`_business_facts(requirement.facts, set(resource_labels))`；L1200按`kind == "resources"`分支；L1202按`isinstance(entity, str) and entity in resource_labels and isinstance(descriptor.get("…`分支；L1209遍历`("summary", "features", "acceptance", "users")`；L1215遍历`enumerate(texts)`；L1216遍历`re.split(r"[；;。\n]", text)`。后续分支沿下方源码相同行号继续阅读。 调用`_business_fact_gaps`、`"\n".join`、`needs.items`、`re.search`、`", ".join`、`sorted`、`_business_facts`、`set`、`descriptor.get`等。 返回路径：L1189的`gaps`；L1192的`gaps + [ "已确认的团队关系、流程、权限或统计需要可执行 business 契约：" + ", ".join(sorted(requested)) ]`；L1290的`gaps + [ "业务设计缺少已确认的可执行能力：" + name for name in sorted(requested) if not implemented[name] …`。

</details>

**创建路径：** `workbench/business_capabilities.py`；**本文件共有 2 段**。本段覆盖源文件 L714–L1294。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26350`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_capabilities.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "e21985bee5a53c96dcfd91587051075d27f525047dba934174af3b47d6700b99"} -->
````python
# workbench/business_capabilities.py
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
        if "read_only" in descriptor and type(descriptor["read_only"]) is not bool:
            raise ValueError("read_only 需要布尔值")
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
                if not expected["actions"]:
                    raise ValueError("actions 需要非空动作标识列表")
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
````
