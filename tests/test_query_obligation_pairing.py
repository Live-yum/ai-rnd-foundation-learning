"""Field × query-property pairing, using typed facts before a legacy fallback.

The recorded candidate is unapproved and used only by pure validators.
"""

import hashlib
import json
from pathlib import Path

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps

FIXTURES = Path(__file__).parent / "fixtures/customer_design_diagnostics/d3ea684"
HASHES = {
    "fastapi-unapproved-design.json": "142534113f2fbf6a0f1dd6e1593279aac23ca2468ba733dab08cc85a9a6a9d4e",
    "fastapi-summary.json": "88434c888fb9a6dbe2f219f711163c2819ce72dce9c4ed6f1acaa33267f3ea76",
}
FLAGS = ("searchable", "filterable", "date_range")


def recorded():
    d = json.loads((FIXTURES / "fastapi-unapproved-design.json").read_bytes())
    assert d["approval_status"] == "unapproved"
    assert d["execution_authorized"] is False
    assert d["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(d["requirement"]), Plan.model_validate(d["candidate_plan"])


@pytest.mark.parametrize("name,digest", HASHES.items())
def test_recorded_failure_and_input_are_byte_exact(name, digest):
    assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest
    summary = json.loads((FIXTURES / "fastapi-summary.json").read_bytes())
    assert summary["passed"] is False
    assert summary["failure_details"]["coverage_block_count"] == 3
    assert {d["code"] for d in summary["failure_details"]["coverage_sources"]} == {
        "uncovered_operation"
    }


def test_exact_recorded_mixed_queries_do_not_override_typed_pairs():
    requirement, plan = recorded()
    before = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    for name in ("name", "organization", "contact"):
        field = next(f for f in requirement.field_requirements if f.field == name)
        assert field.filterable is None


def typed_cases():
    requirement, _ = recorded()
    return [
        (i, flag)
        for i, field in enumerate(requirement.field_requirements)
        for flag in FLAGS
        if getattr(field, flag) is not None
    ]


@pytest.mark.parametrize("index,flag", typed_cases())
def test_every_explicit_typed_query_value_remains_binding(index, flag):
    requirement, plan = recorded()
    expected = requirement.field_requirements[index]
    entity = next(e for e in plan.entities if e.name == expected.entity)
    field = next(f for f in entity.fields if f.name == expected.field)
    setattr(field, flag, not getattr(expected, flag))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["source"] == {"section": "field_requirements", "index": index}
        and d["attribute"] == flag
        and d["expected"] is getattr(expected, flag)
        for d in diagnostics
    )


def case(text, *, typed=True):
    plan = Plan(
        title="Record queries",
        data_scope="shared",
        acceptance=["Query records"],
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "short_text", "kind": "text", "searchable": True},
                    {"name": "long_text", "kind": "text", "searchable": True},
                    {
                        "name": "priority",
                        "kind": "enum",
                        "choices": ["low", "high"],
                        "filterable": True,
                    },
                ],
            }
        ],
    )
    requirement = Requirement(
        summary="Record queries",
        users=["staff"],
        data_scope="shared",
        features=[text],
        acceptance=[],
        field_requirements=[
            FieldRequirement(entity="records", field="short_text", searchable=True),
            FieldRequirement(entity="records", field="long_text", searchable=True),
            FieldRequirement(entity="records", field="priority", searchable=False, filterable=True),
        ]
        if typed
        else [],
    )
    return requirement, plan


@pytest.mark.parametrize("typed", [True, False])
@pytest.mark.parametrize(
    "text",
    [
        "records: 关键词搜索覆盖 short_text/long_text，priority 精确筛选",
        "records: short_text/long_text 关键词搜索，priority 精确筛选",
        "records: 关键词搜索 short_text、long_text，精确筛选 priority",
        "records: search short_text, long_text, filter priority",
        "records: short_text, long_text search, priority filter",
        "records: priority filter, search short_text, long_text",
        "records: filter priority, short_text and long_text search",
        "records: short_text/long_text 搜索；priority 精确筛选",
    ],
)
def test_prefix_suffix_lists_and_clause_order_keep_independent_pairs(text, typed):
    requirement, plan = case(text, typed=typed)
    assert coverage_gaps(requirement, plan) == []
    for name, flag in (
        ("short_text", "searchable"),
        ("long_text", "searchable"),
        ("priority", "filterable"),
    ):
        changed = plan.model_copy(deep=True)
        setattr(next(f for f in changed.entities[0].fields if f.name == name), flag, False)
        assert coverage_gaps(requirement, changed)


@pytest.mark.parametrize("typed", [True, False, None, "absent"])
@pytest.mark.parametrize("prose", [True, False])
@pytest.mark.parametrize("actual", [True, False])
@pytest.mark.parametrize(
    "flag,operation,kind",
    [
        ("searchable", "搜索", "text"),
        ("filterable", "精确筛选", "text"),
        ("date_range", "日期范围查询", "date"),
    ],
)
def test_true_false_none_and_missing_typed_values_are_not_conflated(
    typed, prose, actual, flag, operation, kind
):
    text = "records: short_text " + ("必须" if prose else "禁止") + operation
    requirement, plan = case(text, typed=False)
    if typed != "absent":
        requirement.field_requirements = [
            FieldRequirement(entity="records", field="short_text", required=True, **{flag: typed})
        ]
    field = plan.entities[0].fields[0]
    field.kind = kind
    if kind == "date":
        field.searchable = False
    setattr(field, flag, actual)
    diagnostics = []
    gaps = coverage_gaps(requirement, plan, diagnostics=diagnostics)
    expected = actual is prose and (typed in (None, "absent") or typed is actual)
    assert bool(gaps) is not expected
    if typed in (None, "absent") and actual is not prose:
        assert any(d["source"]["section"] == "features" for d in diagnostics)


def test_another_typed_property_does_not_suppress_an_uncovered_query():
    requirement, plan = case("records: short_text 必须精确筛选")
    assert requirement.field_requirements[0].searchable is True
    assert requirement.field_requirements[0].filterable is None
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].filterable = True
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "text",
    [
        "records: search short_text, long_text, filter priority",
        "records: filter priority, short_text and long_text search",
    ],
)
def test_each_local_group_inherits_the_explicit_entity_without_fanning_out(text):
    requirement, plan = case(text, typed=False)
    archive = plan.entities[0].model_copy(deep=True, update={"name": "archive"})
    for field in archive.fields:
        field.searchable = False
        field.filterable = False
    plan.entities.append(archive)
    assert coverage_gaps(requirement, plan) == []
    for name, flag in (("short_text", "searchable"), ("priority", "filterable")):
        changed = plan.model_copy(deep=True)
        setattr(next(f for f in changed.entities[0].fields if f.name == name), flag, False)
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            d["attribute"] == flag
            and any(t == {"entity": "records", "field": name} for t in d["targets"])
            for d in diagnostics
        )
        assert all(t["entity"] == "records" for d in diagnostics for t in d["targets"])
