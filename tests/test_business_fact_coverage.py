"""Structured business facts use business semantics, never field-name heuristics."""

import json

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT

DOMAINS = ("metrics", "relations", "permissions", "notifications", "workflows", "resources")


def case(facts):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    requirement = Requirement(
        summary="客服", users=["员工"], data_scope="shared", features=[], acceptance=[], facts=facts
    )
    return requirement, plan


@pytest.mark.parametrize("domain", DOMAINS)
@pytest.mark.parametrize("encoding", ["native", "nested", "json_list", "json_item", "json_wrapper"])
def test_business_declarations_keep_semantics_in_all_structural_encodings(domain, encoding):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[0].model_dump()
    value = [descriptor]
    if encoding == "json_list":
        value = json.dumps(value)
    elif encoding == "json_item":
        value = [json.dumps(descriptor)]
    requirement.facts = {domain: value}
    if encoding == "nested":
        requirement.facts = {"confirmed": {"business": requirement.facts}}
    elif encoding == "json_wrapper":
        requirement.facts = {"confirmed": json.dumps(requirement.facts)}
    assert business_gaps(requirement, plan) == []
    getattr(plan.business, domain).pop(0)
    assert business_gaps(requirement, plan), (domain, encoding)
    plan.business = None
    assert business_gaps(requirement, plan), (domain, encoding, "business omitted")


@pytest.mark.parametrize(
    "domain,index,attribute,value",
    [
        ("metrics", 0, "entity", "tasks"),
        ("metrics", 0, "kind", "time_count"),
        ("metrics", 1, "filters", []),
        ("metrics", 2, "end_field", "due_at"),
        ("metrics", 3, "group_by", "priority"),
        ("metrics", 4, "time_field", "updated_at"),
        ("relations", 0, "target_entity", "tasks"),
        ("relations", 0, "field", "assignee_id"),
        ("permissions", 4, "scope", "all"),
        ("permissions", 4, "actions", ["read"]),
        ("notifications", 0, "recipient", "creator"),
        ("notifications", 1, "transition", "start"),
        ("notifications", 2, "due_field", "resolved_at"),
        ("workflows", 0, "initial", "active"),
        ("workflows", 0, "status_field", "priority"),
        ("resources", 1, "assignee_field", None),
        ("resources", 1, "notes", False),
    ],
)
def test_changed_domain_meaning_is_not_satisfied_by_same_name(domain, index, attribute, value):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[index].model_dump()
    requirement.facts = {domain: [descriptor]}
    assert business_gaps(requirement, plan) == []
    setattr(getattr(plan.business, domain)[index], attribute, value)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "scope", [["manager", "service"], {"manager": "all", "service": "assigned"}]
)
@pytest.mark.parametrize("encoding", [False, True])
def test_metric_role_scopes_are_actual_read_metrics_grants(scope, encoding):
    requirement, plan = case(
        {"metrics": [{"name": "total", "role_scope": json.dumps(scope) if encoding else scope}]}
    )
    assert business_gaps(requirement, plan) == []
    permission = next(
        p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
    )
    permission.actions.remove("read_metrics")
    gaps = business_gaps(requirement, plan)
    assert len(gaps) == 1 and "role_scope" in gaps[0]


def test_metric_role_scope_mapping_cannot_widen_row_access():
    requirement, plan = case(
        {"metrics": [{"name": "total", "role_scope": {"service": "assigned"}}]}
    )
    assert business_gaps(requirement, plan) == []
    next(
        p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
    ).scope = "all"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "scope",
    [
        None,
        True,
        "all",
        [],
        {},
        ["manager", "manager"],
        ["管理人员"],
        {"service": "team"},
        [{"role": "manager", "scope": "all"}],
    ],
)
def test_unknown_explicit_metric_scope_blocks_without_guessing(scope):
    requirement, plan = case({"metrics": [{"name": "total", "role_scope": scope}]})
    gaps = business_gaps(requirement, plan)
    assert len(gaps) == 1 and "形状不支持" in gaps[0] and "metrics.0.role_scope" in gaps[0]


def test_undeclared_role_cannot_receive_metric_access_through_other_roles():
    requirement, plan = case({"metrics": [{"name": "total", "role_scope": ["missing"]}]})
    assert business_gaps(requirement, plan)


def test_metric_keyed_dictionary_and_entity_container_preserve_identity():
    requirement, plan = case(
        {"entities": [{"name": "requests", "metrics": {"total": {"kind": "count"}}}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.metrics[0].entity = "customers"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("name", ["name", "kind", "entity", "filters", "role_scope"])
def test_keyed_metric_names_can_be_descriptor_keywords(name):
    requirement, plan = case({"metrics": {name: {"entity": "requests", "kind": "count"}}})
    plan.business.metrics[0].name = name
    assert business_gaps(requirement, plan) == []
    plan.business.metrics.pop(0)
    assert business_gaps(requirement, plan)


def test_explicit_entity_mapping_does_not_derive_its_scope_from_surviving_plan_entities():
    requirement, plan = case(
        {"entities": {"missing": {"metrics": [{"name": "total", "kind": "count"}]}}}
    )
    assert business_gaps(requirement, plan)


def test_entity_keyed_field_named_metrics_is_not_a_metric_declaration():
    requirement, plan = case({"requests": {"metrics": {"kind": "text", "required": True}}})
    plan.business = None
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize("name", ["title", "category", "required", "name", "searchable"])
def test_business_names_that_are_field_keywords_remain_business_identifiers(name):
    requirement, plan = case({"metrics": [{"name": name, "entity": "requests", "kind": "count"}]})
    plan.business.metrics[0].name = name
    assert business_gaps(requirement, plan) == []
    plan.business.metrics.pop(0)
    assert business_gaps(requirement, plan)


def test_field_containers_and_display_metadata_do_not_invent_business_obligations():
    requirement, plan = case(
        {
            "fields": [{"name": "metrics", "required": True, "metrics": [{"name": "missing"}]}],
            "metrics": [{"label": "title必填搜索", "description": "权限提醒"}],
            "nested": {"metrics": {"display": {"label": "显示文字"}}},
            "template_capabilities": {"metrics": [{"name": "missing"}]},
        }
    )
    plan.business = None
    assert business_gaps(requirement, plan) == []


def test_metric_filters_default_eq_and_preserve_literal_json_looking_values():
    requirement, plan = case(
        {
            "metrics": [
                {
                    "name": "resolved_total",
                    "filters": [{"field": "request_state", "value": "resolved"}],
                }
            ]
        }
    )
    assert business_gaps(requirement, plan) == []
    predicate = plan.business.metrics[1].filters[0]
    predicate.field, predicate.value = "title", '["urgent"]'
    requirement.facts = {
        "metrics": [
            {"name": "resolved_total", "filters": [{"field": "title", "value": '["urgent"]'}]}
        ]
    }
    assert business_gaps(requirement, plan) == []
    predicate.value = "urgent"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "filters", [[{}], [{"label": "filter"}], [{"field": "priority"}], {"request_state": "resolved"}]
)
def test_malformed_explicit_filters_cannot_match_any_existing_predicate(filters):
    requirement, plan = case({"metrics": [{"name": "resolved_total", "filters": filters}]})
    assert business_gaps(requirement, plan)


def test_workflow_transition_roles_and_timestamps_remain_semantic_obligations():
    requirement, plan = case({})
    workflow = plan.business.workflows[0]
    requirement.facts = {"workflows": [workflow.model_dump()]}
    assert business_gaps(requirement, plan) == []
    workflow.transitions[-1].roles = ["manager"]
    assert business_gaps(requirement, plan)


def test_scalar_business_prose_is_not_flattened_into_field_or_business_descriptors():
    requirement, plan = case(
        {"metrics": "title count filter", "permissions": ["manager", "service"]}
    )
    plan.business = None
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "domain,index,aliases",
    [
        ("relations", 0, {"entity": "from", "target_entity": "to"}),
        ("relations", 0, {"target_entity": "target"}),
        ("workflows", 0, {"status_field": "field", "initial": "initial_state"}),
        ("metrics", 3, {"kind": "type", "group_by": "group_field"}),
        ("metrics", 4, {"kind": "type", "bucket": "interval"}),
        ("resources", 1, {"entity": "name", "notes": "handling_notes"}),
    ],
)
@pytest.mark.parametrize("encoded", [False, True])
def test_structural_aliases_preserve_exact_domain_meaning(domain, index, aliases, encoded):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[index].model_dump()
    for canonical, alias in aliases.items():
        descriptor[alias] = descriptor.pop(canonical)
    requirement.facts = {domain: [json.dumps(descriptor) if encoded else descriptor]}
    before = requirement.model_dump_json()
    assert business_gaps(requirement, plan) == []
    getattr(plan.business, domain).pop(index)
    assert business_gaps(requirement, plan)
    assert requirement.model_dump_json() == before


@pytest.mark.parametrize("alias", ["set", "sets", "set_fields"])
def test_workflow_state_and_timestamp_aliases_are_checked(alias):
    requirement, plan = case({})
    descriptor = plan.business.workflows[0].model_dump()
    for transition in descriptor["transitions"]:
        transition["from"] = transition.pop("from_states")[0]
        transition["to"] = transition.pop("to_state")
        timestamp = transition.pop("set_timestamp")
        if timestamp:
            transition[alias] = {timestamp: "now"}
    requirement.facts = {"workflows": [descriptor]}
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions[-1].set_timestamp = None
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "predicate", [{"field": "request_state", "value": "resolved"}, {"request_state": "resolved"}]
)
def test_metric_filter_aliases_cannot_lose_the_actual_predicate(predicate):
    requirement, plan = case(
        {"metrics": [{"name": "resolved_total", "type": "count", "filter": predicate}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.metrics[1].filters = []
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "alias,action",
    [
        ("comment", "add_note"),
        ("note", "add_note"),
        ("view_audit", "read_audit"),
        ("view_metrics", "read_metrics"),
        ("view_history", "read_history"),
    ],
)
def test_permission_action_aliases_still_require_real_action(alias, action):
    requirement, plan = case({})
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    )
    descriptor = permission.model_dump()
    descriptor["actions"] = [alias if item == action else item for item in descriptor["actions"]]
    requirement.facts = {"permissions": [descriptor]}
    assert business_gaps(requirement, plan) == []
    permission.actions.remove(action)
    assert business_gaps(requirement, plan)


def test_read_only_allows_independently_approved_metrics_but_never_writes():
    requirement, plan = case(
        {
            "permissions": [
                {
                    "role": "service",
                    "entity": "customers",
                    "scope": "all",
                    "actions": ["read"],
                    "read_only": True,
                }
            ],
            "metrics": [
                {
                    "name": "customer_total",
                    "entity": "customers",
                    "allowed_roles": ["manager", "service"],
                }
            ],
        }
    )
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "customers"
    )
    permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan) == []
    permission.actions.append("update")
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "restriction",
    [
        {"only_actions": ["read"]},
        {"denied_actions": ["read_metrics"]},
        {"forbidden_actions": ["view_metrics"]},
    ],
)
def test_explicit_action_restrictions_override_other_positive_grants(restriction):
    requirement, plan = case(
        {
            "permissions": [
                {
                    "role": "service",
                    "entity": "customers",
                    "scope": "all",
                    "actions": ["read"],
                    **restriction,
                }
            ],
            "metrics": [
                {"name": "customer_total", "entity": "customers", "role_scope": ["service"]}
            ],
        }
    )
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "customers"
    )
    permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan)


def complete_policy_case():
    requirement, plan = case({})
    requirement.facts = {
        "business": {
            "roles": [item.model_dump() for item in plan.business.roles],
            "resources": [item.model_dump() for item in plan.business.resources],
            "permissions": [item.model_dump() for item in plan.business.permissions],
            "bootstrap_role": "manager",
            "role_admin_roles": ["manager"],
        }
    }
    return requirement, plan


@pytest.mark.parametrize(
    "mutation", ["extra_row", "extra_role", "admin_role", "scope", "extra_write"]
)
def test_complete_policy_rejects_new_rows_roles_admins_and_privilege_expansion(mutation):
    from workbench.business_contracts import BusinessRole, PermissionSpec

    requirement, plan = complete_policy_case()
    assert business_gaps(requirement, plan) == []
    if mutation == "extra_row":
        plan.business.permissions.append(
            PermissionSpec(role="employee", entity="tasks", actions=["read"], scope="all")
        )
    elif mutation == "extra_role":
        plan.business.roles.append(BusinessRole(name="intruder", label="其他角色"))
    elif mutation == "admin_role":
        plan.business.role_admin_roles.append("service")
    elif mutation == "scope":
        next(
            item
            for item in plan.business.permissions
            if item.role == "service" and item.entity == "requests"
        ).scope = "all"
    else:
        next(
            item
            for item in plan.business.permissions
            if item.role == "employee" and item.entity == "customers"
        ).actions.append("update")
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics and diagnostics[0]["expected"] != diagnostics[0]["actual"]


def test_audit_derives_only_information_subset_history_not_other_permissions():
    requirement, plan = case({})
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    )
    permission.actions = ["read", "read_audit", "read_history"]
    requirement.facts = {
        "permissions": [
            {
                "role": "service",
                "entity": "requests",
                "actions": ["read", "view_audit"],
                "scope": "assigned",
            }
        ]
    }
    assert business_gaps(requirement, plan) == []
    permission.actions.append("assign")
    assert business_gaps(requirement, plan)


def test_virtual_metrics_permissions_use_explicit_resource_scopes():
    requirement, plan = case(
        {
            "business": {
                "permissions": [
                    {"role": "service", "entity": "customers", "actions": ["read"], "scope": "all"},
                    {
                        "role": "service",
                        "entity": "requests",
                        "actions": ["read"],
                        "scope": "assigned",
                    },
                    {
                        "role": "service",
                        "entity": "metrics",
                        "actions": ["read"],
                        "scope": "assigned",
                    },
                ],
                "metrics": [
                    {"name": "customer_total", "entity": "customers"},
                    {"name": "total", "entity": "requests"},
                ],
            }
        }
    )
    for permission in plan.business.permissions:
        if permission.role == "service" and permission.entity in {"customers", "requests"}:
            permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan) == []
    next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    ).scope = "all"
    assert business_gaps(requirement, plan)


def test_reverse_relation_is_implemented_by_correct_child_foreign_key():
    requirement, plan = case(
        {
            "relations": [
                {
                    "entity": "customers",
                    "field": "requests",
                    "target": "requests",
                    "kind": "reverse",
                }
            ]
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.relations[0].target_entity = "tasks"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("alias", ["in-app", "in_app_persistent", "in_app"])
def test_aggregate_notification_catalog_is_not_a_cartesian_recipient_policy(alias):
    requirement, plan = case(
        {
            "notifications": {
                "channel": alias,
                "persistent": True,
                "triggers": ["assignment", "handling_note", "state_change", "resolved", "overdue"],
                "recipients": ["assignee", "request_submitter"],
            }
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (
            item.event == "transitioned"
            and item.transition == "resolve"
            and item.recipient == "creator"
        )
    ]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "event,canonical",
    [
        ("assignment", "assigned"),
        ("comment_added", "note_added"),
        ("handling_note", "note_added"),
        ("overdue", "due"),
    ],
)
def test_event_aliases_preserve_explicit_entity_and_recipient(event, canonical):
    recipient = "created_by" if canonical == "note_added" else "assignee_id"
    requirement, plan = case(
        {"notifications": [{"entity": "requests", "event": event, "recipients": [recipient]}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (item.entity == "requests" and item.event == canonical)
    ]
    assert business_gaps(requirement, plan)


def test_resolved_notification_uses_target_state_not_a_hard_coded_action_name():
    requirement, plan = case(
        {"reminders": [{"entity": "requests", "event": "resolved", "recipient": "creator"}]}
    )
    plan.business.workflows[0].transitions[-1].name = "finish"
    for notice in plan.business.notifications:
        if notice.entity == "requests" and notice.transition == "resolve":
            notice.transition = "finish"
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions[-1].to_state = "closed"
    assert business_gaps(requirement, plan)


def test_event_specific_recipient_list_requires_all_on_same_resource():
    requirement, plan = case(
        {
            "notifications": [
                {
                    "entity": "requests",
                    "event": "note_added",
                    "recipients": ["created_by", "assignee_id"],
                }
            ]
        }
    )
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "descriptor",
    [
        {"name": "total", "type": "count", "kind": "time_count"},
        {"name": "total", "allowed_roles": ["manager"], "role_scope": ["service"]},
    ],
)
def test_conflicting_aliases_block_without_crashing_or_changing_facts(descriptor):
    requirement, plan = case({"metrics": [descriptor]})
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "business_unsupported_shape"


def test_handling_history_requirement_keeps_entity_scope_and_independent_action():
    requirement, plan = case(
        {
            "resources": [
                {"entity": "requests", "label": "服务请求"},
                {"entity": "tasks", "label": "协作任务"},
            ]
        }
    )
    requirement.features = ["服务请求：查看处理过程"]
    for permission in plan.business.permissions:
        if "read_history" in permission.actions:
            permission.actions.remove("read_history")
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    history = [item for item in diagnostics if item["code"] == "business_missing_history_grant"]
    assert history and {item["expected"]["entity"] for item in history} == {"requests"}


@pytest.mark.parametrize(
    "capability,attribute", [("keyword_search", "searchable"), ("exact_filter", "filterable")]
)
def test_resource_query_capabilities_are_scoped_without_inventing_target_fields(
    capability, attribute
):
    requirement, plan = case({"resources": [{"name": "customers", "capabilities": [capability]}]})
    assert business_gaps(requirement, plan) == []
    for field in plan.entities[0].fields:
        setattr(field, attribute, False)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("entity", [None, [], {}, True])
def test_malformed_resource_scope_cannot_crash_history_review(entity):
    requirement, plan = case(
        {"resources": [{"entity": entity, "label": "服务请求", "notes": True}]}
    )
    requirement.features = ["查看处理过程"]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "entity,name,explicit_scope",
    [("customers", "customer_total", "own"), ("requests", "total", "all")],
)
def test_global_metric_scope_cannot_overwrite_explicit_per_metric_scope(
    entity, name, explicit_scope
):
    requirement, plan = case({})
    permissions = [
        item.model_dump()
        for item in plan.business.permissions
        if item.entity == entity and item.role in {"manager", "service"}
    ]
    requirement.facts = {
        "business": {
            "permissions": permissions,
            "metrics_roles": ["manager", "service"],
            "metrics_scope": "manager=all；service=assigned（只按本人可见行计算）",
            "metrics": [
                {
                    "name": name,
                    "entity": entity,
                    "role_scope": {"manager": "all", "service": explicit_scope},
                }
            ],
        }
    }
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


@pytest.mark.parametrize("name", DOMAINS)
@pytest.mark.parametrize("encoded", [False, True])
def test_entity_keyed_kind_only_fields_do_not_become_business_collections(name, encoded):
    from workbench.domain import FieldSpec
    from workbench.requirement_coverage import coverage_gaps

    requirement, plan = case({})
    plan.entities[0].fields.append(FieldSpec(name=name, kind="text"))
    definition = {name: {"kind": "text"}}
    requirement.facts = {"customers": json.dumps(definition) if encoded else definition}
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].kind = "integer"
    assert coverage_gaps(requirement, plan), "The field kind obligation must stay binding"
    plan.entities[0].fields.pop()
    assert coverage_gaps(requirement, plan), "A missing explicit field must still block"


def transition_notification_case(descriptor):
    requirement, plan = case({"notifications": [descriptor]})
    raw = plan.model_dump()
    raw["business"]["notifications"] = [
        {
            "entity": workflow.entity,
            "event": "transitioned",
            "recipient": recipient,
            "transition": transition.name,
        }
        for workflow in plan.business.workflows
        for transition in workflow.transitions
        for recipient in ("assignee", "creator")
    ]
    return requirement, Plan.model_validate(raw)


@pytest.mark.parametrize("event", ["transitioned", "state_change", "state_changed"])
@pytest.mark.parametrize("selector", ["omitted", None, "*"])
@pytest.mark.parametrize("encoded", [False, True])
@pytest.mark.parametrize("missing", ["start", "resolve"])
def test_generic_state_change_facts_require_every_declared_transition(
    event, selector, encoded, missing
):
    descriptor = {
        "entity": "requests",
        "event": event,
        "recipient": "assignee",
        "due_field": None,
        "channel": "in_app",
    }
    if selector != "omitted":
        descriptor["transition"] = selector
    requirement, plan = transition_notification_case(descriptor)
    if encoded:
        requirement.facts = {"notifications": json.dumps([descriptor])}
    before = requirement.model_dump_json()
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (
            item.entity == "requests"
            and item.recipient == "assignee"
            and item.transition == missing
        )
    ]
    # The same transition remains on the wrong entity and wrong recipient.
    assert business_gaps(requirement, plan)
    assert requirement.model_dump_json() == before


@pytest.mark.parametrize("event", ["transitioned", "state_change", "state_changed"])
@pytest.mark.parametrize("selected", ["start", "resolve"])
def test_explicit_state_change_selector_is_exact_not_all_transitions(event, selected):
    requirement, plan = transition_notification_case(
        {"entity": "requests", "event": event, "recipient": "assignee", "transition": selected}
    )
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if item.entity != "requests" or item.recipient != "assignee" or item.transition == selected
    ]
    assert business_gaps(requirement, plan) == []
    requirement.facts["notifications"][0]["transition"] = (
        "resolve" if selected == "start" else "start"
    )
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("selected", ["all", "any"])
def test_ordinary_transition_identifiers_are_not_invented_wildcards(selected):
    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipient": "assignee",
            "transition": selected,
        }
    )
    plan.business.workflows[0].transitions[0].name = selected
    for item in plan.business.notifications:
        if item.entity == "requests" and item.transition == "start":
            item.transition = selected
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (item.entity == "requests" and item.transition == "resolve")
    ]
    assert business_gaps(requirement, plan) == []


def test_generic_state_change_obligation_expands_when_workflow_gains_transition():
    from workbench.business_contracts import NotificationSpec, TransitionSpec

    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipients": ["assignee", "creator"],
            "transition": None,
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions.append(
        TransitionSpec(
            name="reopen", from_states=["resolved"], to_state="active", roles=["manager"]
        )
    )
    assert business_gaps(requirement, plan)
    plan.business.notifications.append(
        NotificationSpec(
            entity="requests", event="transitioned", recipient="assignee", transition="reopen"
        )
    )
    assert business_gaps(requirement, plan), (
        "Every explicitly named recipient needs the new transition"
    )
    plan.business.notifications.append(
        NotificationSpec(
            entity="requests", event="transitioned", recipient="creator", transition="reopen"
        )
    )
    assert business_gaps(requirement, plan) == []


def test_generic_requirement_never_relaxes_executable_notification_validator():
    requirement, plan = transition_notification_case(
        {"entity": "requests", "event": "transitioned", "recipient": "assignee", "transition": None}
    )
    assert business_gaps(requirement, plan) == []
    raw = plan.model_dump()
    raw["business"]["notifications"][0]["transition"] = None
    with pytest.raises(ValueError, match="Notification requires a known transition"):
        Plan.model_validate(raw)


@pytest.mark.parametrize("selector", ["missing", "", [], {}, False])
def test_invalid_or_unknown_specific_transition_is_not_a_generic_requirement(selector):
    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipient": "assignee",
            "transition": selector,
        }
    )
    assert business_gaps(requirement, plan)


def test_transition_wildcard_does_not_change_non_transition_event_semantics():
    requirement, plan = case(
        {
            "notifications": [
                {
                    "entity": "requests",
                    "event": "assigned",
                    "recipient": "assignee",
                    "transition": "*",
                }
            ]
        }
    )
    assert business_gaps(requirement, plan)


def test_unscoped_generic_transition_does_not_invent_notifications_on_every_entity():
    requirement, plan = transition_notification_case(
        {"event": "transitioned", "recipient": "assignee", "transition": None}
    )
    plan.business.notifications = [
        item for item in plan.business.notifications if item.entity == "requests"
    ]
    assert business_gaps(requirement, plan) == []
    requirement.facts["notifications"][0]["entity"] = "tasks"
    assert business_gaps(requirement, plan)
