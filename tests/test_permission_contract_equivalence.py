"""Pure permission validators; recorded unapproved candidates are never executed."""

import hashlib
import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

FIXTURES = ROOT / "tests/fixtures/customer_design_diagnostics/dd7e5f2"
RECORDED = {
    "fastapi-unapproved-design.json": (
        49980,
        "9c8cdc4576208ee3f3954d724a7789e2f635e50ae25b66f65d75e34d0e41b5f5",
    ),
    "fastapi-summary.json": (
        17671,
        "a7782be7e86a74cfae44ca9ccad835107ac4a7de2e7fff9ebcb4d747b6138e7a",
    ),
}


def recorded():
    values = {}
    for filename, (size, digest) in RECORDED.items():
        raw = (FIXTURES / filename).read_bytes()
        assert len(raw) == size
        assert hashlib.sha256(raw).hexdigest() == digest
        values[filename] = json.loads(raw)
    data = values["fastapi-unapproved-design.json"]
    summary = values["fastapi-summary.json"]
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    assert summary["passed"] is False
    assert summary["run_identity"] == [
        "36840557604",
        "1",
        "dd7e5f2135fdfe8b84f36dd1de5ab6e090c6a45a",
    ]
    assert summary["failure_details"]["coverage_block_count"] == 2
    assert (
        sum(receipt.get("schema_valid") is False for receipt in summary["provider_receipts"]) == 2
    )
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


def grant(role="service", entity="customers", scope="all", actions=None, **restrictions):
    return {
        "role": role,
        "entity": entity,
        "scope": scope,
        "actions": actions if actions is not None else ["read"],
        **restrictions,
    }


def case():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    permission(plan).actions = ["read", "read_metrics"]
    requirement = Requirement(
        summary="客服", users=[], data_scope="shared", features=[], acceptance=[], facts={}
    )
    requirement.facts = {"permissions": [grant(), grant(actions=["read_metrics"])]}
    return requirement, plan


def permission(plan, role="service", entity="customers"):
    return next(
        item for item in plan.business.permissions if item.role == role and item.entity == entity
    )


def test_exact_unapproved_fastapi_split_grants_are_covered_without_rewriting_either_contract():
    requirement, plan = recorded()
    original = (requirement.model_dump(), plan.model_dump())
    rows = requirement.facts["business"]["permissions"]
    assert [
        row["actions"] for row in rows if row["role"] == "service" and row["entity"] == "customers"
    ] == [
        ["read"],
        ["read_metrics"],
    ]
    assert permission(plan).actions == ["read", "read_metrics"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics) == diagnostics == []
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == original
    recorded()  # Raw hashes, unapproved status, and original failing receipts stay unchanged.


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_read",
        "missing_metrics",
        "missing_row",
        "scope",
        "scope_widening",
        "foreign_role",
        "foreign_entity",
        "extra_row",
        "unknown_action",
    ],
)
def test_recorded_permission_losses_and_authorization_expansion_remain_blocked(mutation):
    requirement, original = recorded()
    value = original.model_dump()
    rows = value["business"]["permissions"]
    target = next(row for row in rows if row["role"] == "service" and row["entity"] == "customers")
    if mutation.startswith("missing_") and mutation != "missing_row":
        target["actions"].remove("read" if mutation == "missing_read" else "read_metrics")
    elif mutation == "missing_row":
        rows.remove(target)
    elif mutation == "scope":
        target["scope"] = "own"
    elif mutation == "scope_widening":
        next(row for row in rows if row["role"] == "employee" and row["entity"] == "requests")[
            "scope"
        ] = "all"
    elif mutation == "foreign_role":
        value["business"]["roles"].append({"name": "outsider", "label": "Outsider"})
        target["role"] = "outsider"
    elif mutation == "foreign_entity":
        target["entity"] = "foreign_resource"
    elif mutation == "extra_row":
        rows.append(grant(role="employee", entity="tasks"))
    else:
        target["actions"].append("delete_everything")
    try:
        candidate = Plan.model_validate(value)
    except ValidationError:
        assert mutation in {"foreign_entity", "unknown_action"}
    else:
        assert business_gaps(requirement, candidate), mutation


@pytest.mark.parametrize(
    "action",
    [
        "create",
        "update",
        "archive",
        "assign",
        "transition",
        "add_note",
        "read_audit",
        "read_history",
    ],
)
def test_split_grants_never_allow_unapproved_action_supersets(action):
    requirement, plan = case()
    assert business_gaps(requirement, plan) == []
    permission(plan).actions.append(action)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "encoding",
    [
        "native",
        "nested",
        "json_list",
        "json_item",
        "json_wrapper",
        "keyed",
        "nested_list",
        "entity_inherited",
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_same_collection_split_grants_support_structural_encodings_and_order(encoding, reverse):
    requirement, plan = case()
    rows = requirement.facts["permissions"]
    if reverse:
        rows.reverse()
        permission(plan).actions.reverse()
    if encoding == "nested":
        requirement.facts = {"confirmed": {"business": requirement.facts}}
    elif encoding == "json_list":
        requirement.facts["permissions"] = json.dumps(rows)
    elif encoding == "json_item":
        requirement.facts["permissions"] = [json.dumps(row) for row in rows]
    elif encoding == "json_wrapper":
        requirement.facts = {"confirmed": json.dumps(requirement.facts)}
    elif encoding == "keyed":
        requirement.facts["permissions"] = {"first": rows[0], "second": rows[1]}
    elif encoding == "nested_list":
        requirement.facts["permissions"] = [[rows[0]], [rows[1]]]
    elif encoding == "entity_inherited":
        for row in rows:
            del row["entity"]
        requirement.facts = {"entities": [{"name": "customers", "permissions": rows}]}
    assert business_gaps(requirement, plan) == []


def test_duplicate_positive_rows_are_idempotent_but_duplicate_plan_rows_stay_invalid():
    requirement, plan = case()
    requirement.facts["permissions"].append(grant(actions=["read", "view_metrics"]))
    assert business_gaps(requirement, plan) == []
    value = plan.model_dump()
    value["business"]["permissions"].append(permission(plan).model_dump())
    with pytest.raises(ValidationError, match="Duplicate/contradictory business declaration"):
        Plan.model_validate(value)


@pytest.mark.parametrize("chunk_size", [1, 2, 3])
@pytest.mark.parametrize("reverse", [False, True])
def test_complete_matrix_preserves_all_permission_actions_under_arbitrary_partitioning(
    chunk_size, reverse
):
    requirement, plan = case()
    rows = []
    for item in plan.business.permissions:
        actions = item.actions[::-1] if reverse else item.actions
        for start in range(0, len(actions), chunk_size):
            rows.append({**item.model_dump(), "actions": actions[start : start + chunk_size]})
    requirement.facts = {
        "business": {
            "roles": [role.model_dump() for role in plan.business.roles],
            "resources": [resource.model_dump() for resource in plan.business.resources],
            "permissions": rows[::-1] if reverse else rows,
        }
    }
    assert business_gaps(requirement, plan) == []
    for item in plan.business.permissions:
        for action in item.actions:
            changed = plan.model_copy(deep=True)
            permission(changed, item.role, item.entity).actions.remove(action)
            assert business_gaps(requirement, changed), (item.role, item.entity, action)


@pytest.mark.parametrize(
    "key,value",
    [
        ("role", "employee"),
        ("entity", "requests"),
        ("scope", "own"),
        ("scope", "assigned"),
        ("scope", "team"),
    ],
)
def test_actions_cannot_be_borrowed_from_another_role_entity_or_scope(key, value):
    requirement, plan = case()
    requirement.facts["permissions"][1][key] = value
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("missing", ["role", "entity", "scope", "actions"])
def test_partial_descriptors_do_not_authorize_pooling(missing):
    requirement, plan = case()
    del requirement.facts["permissions"][1][missing]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "actions",
    [
        None,
        True,
        "read_metrics",
        {"read_metrics": True},
        [],
        ["read_metrics", "read_metrics"],
        ["read_metrics", "view_metrics"],
        ["unknown_action"],
        ["read_metrics", "unknown_action"],
    ],
)
def test_malformed_or_unknown_positive_actions_cannot_be_laundered_through_valid_row(actions):
    requirement, plan = case()
    requirement.facts["permissions"].append(grant(actions=actions))
    if actions is None:
        requirement.facts["permissions"][-1]["actions"] = None
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


@pytest.mark.parametrize(
    "restriction",
    [
        {"only_actions": ["read"]},
        {"denied_actions": ["read_metrics"]},
        {"forbidden_actions": ["view_metrics"]},
        {"read_only": "yes"},
    ],
)
@pytest.mark.parametrize("row", [0, 1])
def test_every_original_restriction_stays_binding_after_positive_union(restriction, row):
    requirement, plan = case()
    requirement.facts["permissions"][row].update(restriction)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("key", ["only_actions", "denied_actions", "forbidden_actions"])
def test_unknown_actions_in_restrictions_fail_closed(key):
    requirement, plan = case()
    requirement.facts["permissions"][0][key] = ["unknown_action"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


def test_read_only_allows_split_read_metrics_but_rejects_even_explicit_write_union():
    requirement, plan = case()
    requirement.facts["permissions"][0]["read_only"] = True
    assert business_gaps(requirement, plan) == []
    requirement.facts["permissions"].append(grant(actions=["update"]))
    permission(plan).actions.append("update")
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("complete", [False, True])
@pytest.mark.parametrize("placement", ["siblings", "nested", "colliding_display_path"])
def test_independent_permission_collections_cannot_authorize_each_others_extras(
    complete, placement
):
    requirement, plan = case()
    # Use a non-metric action so neither collection gets independent metric approval.
    permission(plan).actions = ["read", "update"]
    first = {"permissions": [row.model_dump() for row in plan.business.permissions]}
    next(
        row
        for row in first["permissions"]
        if row["role"] == "service" and row["entity"] == "customers"
    )["actions"] = ["read"]
    second = deepcopy(first)
    next(
        row
        for row in second["permissions"]
        if row["role"] == "service" and row["entity"] == "customers"
    )["actions"] = ["read", "update"]
    if complete:
        first["permissions_complete"] = second["permissions_complete"] = True
    if placement == "siblings":
        requirement.facts = {"business": first, "business_constraints": second}
    elif placement == "nested":
        requirement.facts = {"business": {**first, "business_constraints": second}}
    else:
        requirement.facts = {"confirmed.business": first, "confirmed": {"business": second}}
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["source"]["domain"] == "permissions" for item in diagnostics)


def test_presentation_only_permissions_never_add_authority():
    requirement, plan = case()
    rows = requirement.facts["permissions"]
    requirement.facts = {"permissions": [rows[0]], "labels": {"permissions": [rows[1]]}}
    assert business_gaps(requirement, plan)


def test_merged_failures_keep_original_source_indices_and_exact_required_action_set():
    requirement, plan = case()
    permission(plan).actions = ["read"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert {item["source"]["path"] for item in diagnostics} == {"permissions.0", "permissions.1"}
    assert all(item["expected"]["actions"] == ["read", "read_metrics"] for item in diagnostics)
