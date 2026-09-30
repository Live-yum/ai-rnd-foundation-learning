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
