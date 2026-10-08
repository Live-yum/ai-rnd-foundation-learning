"""Entity-grouped field facts keep presence, scope and enum obligations distinct."""

import copy
import json

import pytest

from workbench.domain import EntityRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def case(*, typed=True):
    plan = Plan(
        title="Grouped field declarations",
        data_scope="per_user",
        entities=[
            {
                "name": "alpha",
                "description": "First resource",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80},
                    {"name": "category", "kind": "enum", "choices": ["first", "second"]},
                ],
            },
            {
                "name": "beta",
                "description": "Second resource",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80},
                    {"name": "note", "kind": "text", "required": False},
                ],
            },
        ],
        acceptance=["Declared fields remain present"],
    )
    requirement = Requirement(
        summary="Grouped field declarations",
        data_scope="per_user",
        users=[],
        features=[],
        acceptance=[],
        entity_requirements=[
            EntityRequirement(
                entity=e.name, fields=[f.name for f in e.fields], additional_fields=False
            )
            for e in plan.entities
        ]
        if typed
        else [],
        facts={
            "arbitrary_ledger": {
                "fields": {"alpha": ["title", "category"], "beta": ["title", "note"]}
            }
        },
    )
    return requirement, plan


@pytest.mark.parametrize("shape", ["native", "json", "nested", "resources"])
@pytest.mark.parametrize("typed", [True, False])
def test_grouped_field_names_are_scoped_presence_obligations(shape, typed):
    requirement, plan = case(typed=typed)
    value = requirement.facts["arbitrary_ledger"]
    if shape == "json":
        requirement.facts["arbitrary_ledger"] = json.dumps(value)
    elif shape == "nested":
        requirement.facts = {"wrapper": [{"details": json.dumps(value)}]}
    elif shape == "resources":
        requirement.facts = {
            "resources": [
                {"name": entity, "fields": fields} for entity, fields in value["fields"].items()
            ]
        }
    original = copy.deepcopy(requirement.model_dump())
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == original


@pytest.mark.parametrize("missing", ["field", "entity", "wrong_owner"])
def test_missing_inventory_members_cannot_borrow_another_entity(missing):
    requirement, plan = case()
    if missing == "entity":
        plan.entities.pop(0)
    else:
        plan.entities[0].fields = [f for f in plan.entities[0].fields if f.name != "title"]
        if missing == "wrong_owner":
            plan.entities[1].fields.append(FieldSpec(name="unrelated", kind="text"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["code"] == "structured_missing_field"
        and d["source"]["path"] == "arbitrary_ledger.fields.alpha.0"
        for d in diagnostics
    )
    assert not any(
        d["code"] == "structured_missing_field" and d["source"]["path"].endswith("fields.beta.0")
        for d in diagnostics
    )


@pytest.mark.parametrize("declaration", ["fields", "field_constraints"])
def test_grouped_descriptors_preserve_explicit_constraints(declaration):
    requirement, plan = case()
    requirement.facts = {
        declaration: {
            "alpha": {"title": {"required": True, "max_length": 80}},
            "beta": [{"field": "note", "required": False}],
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 81
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["code"] == "constraint_mismatch"
        and d["targets"] == [{"entity": "alpha", "field": "title"}]
        and d["attribute"] == "max_length"
        and d["expected"] == 80
        and d["actual"] == 81
        for d in diagnostics
    )


@pytest.mark.parametrize("members", [[], [None], [3], ["bad field"], [{"field": None}]])
def test_malformed_grouped_inventory_is_not_an_empty_success(members):
    requirement, plan = case()
    requirement.facts = {"fields": {"alpha": members}}
    assert coverage_gaps(requirement, plan)


def test_bare_enum_choices_keep_their_meaning_when_a_field_matches_an_entity_name():
    requirement, plan = case(typed=False)
    plan.entities[1].fields.append(
        FieldSpec(name="alpha", kind="enum", choices=["first", "second"])
    )
    requirement.facts = {"fields": {"alpha": ["first", "second"]}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[-1].choices = ["first", "third"]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["attribute"] == "choices" for d in diagnostics)


def test_display_field_maps_do_not_become_inventory_obligations():
    requirement, plan = case(typed=False)
    requirement.facts = {"presentation": requirement.facts}
    plan.entities.pop(0)
    assert coverage_gaps(requirement, plan) == []
