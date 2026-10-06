"""Generated HTTP query matrices and real implementation faults, never model substitutes."""

import json

import pytest
from test_business_acceptance_evidence import customer_plan, execute
from test_business_python import runtime_plan

from workbench.domain import Plan
from workbench.generator import generate_basic


def test_customer_api_query_matrix_is_field_specific_and_role_scoped(tmp_path):
    plan = customer_plan()
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    proof = report["business"]["evidence"]["query_matrix"]
    assert "business-query-matrix" in report["business"]["checks"]
    for entity in plan.entities:
        for field in entity.fields:
            if field.searchable:
                records = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"]) == (entity.name, field.name, "keyword")
                ]
                assert records and all(p["other_matches"] == 0 for p in records)
                assert any(p["isolated_matches"] > 0 for p in records)
            if field.filterable:
                records = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"])
                    == (entity.name, field.name, "exact_filter")
                ]
                assert records and all(
                    p["positive_matches"] > 0 and p["excluded_records"] > 0 for p in records
                )
                combined = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"]) == (entity.name, field.name, "combined")
                ]
                assert combined and all(p["excluded_records"] > 0 for p in combined)
    assert all(p["foreign_matches"] > 0 for p in proof if p["scope"] != "all")
    assert all(p["cases"] == 2 and p["exact_results"] and p["role_scope"] for p in proof)
    assert len(json.dumps(proof).encode()) < 20000
    assert not any(
        key in json.dumps(proof) for key in ("expected_ids", "params", "Bearer", "password")
    )


FLAGGED_FIELDS = [
    (entity.name, field.name, "keyword" if field.searchable else "exact_filter")
    for entity in customer_plan().entities
    for field in entity.fields
    if field.searchable or field.filterable
]


@pytest.mark.parametrize("maximum", [8, 2])
def test_bounded_integer_query_controls_use_valid_values_including_singleton(tmp_path, maximum):
    raw = runtime_plan().model_dump()
    raw["entities"][0]["fields"].append(
        {
            "name": "quantity",
            "kind": "integer",
            "required": True,
            "minimum": 2,
            "maximum": maximum,
            "filterable": True,
        }
    )
    product = tmp_path / "product"
    generate_basic(
        Plan.model_validate(raw),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    evidence = json.loads(result.stdout.splitlines()[-1])["business"]["evidence"]
    validation = next(item for item in evidence["field_validation"] if item["field"] == "quantity")
    assert validation["minimum"] == 2 and validation["maximum"] == maximum
    assert validation["below_minimum_rejected"] and validation["above_maximum_rejected"]
    controls = [item for item in evidence["query_matrix"] if item["field"] == "quantity"]
    assert controls and all(
        item["positive_matches"] > 0 and item["excluded_records"] > 0 for item in controls
    )


@pytest.mark.parametrize("maximum", [1, 2])
def test_short_keyword_fields_keep_independent_positive_controls(tmp_path, maximum):
    raw = runtime_plan().model_dump()
    raw["entities"][0]["fields"].append(
        {
            "name": "short_code",
            "kind": "text",
            "required": True,
            "max_length": maximum,
            "searchable": True,
        }
    )
    product = tmp_path / "product"
    generate_basic(
        Plan.model_validate(raw),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout.splitlines()[-1])["business"]["evidence"]["query_matrix"]
    short = [entry for entry in proof if entry["field"] == "short_code"]
    assert short and all(entry["isolated_matches"] > 0 for entry in short)


@pytest.mark.parametrize("entity,field,kind", FLAGGED_FIELDS)
def test_query_matrix_rejects_each_disabled_declared_query_field(tmp_path, entity, field, kind):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    path = product / "querying.py"
    source = path.read_text(encoding="utf-8")
    if kind == "keyword":
        before = 'if field.get("searchable")'
        after = f'if field.get("searchable") and not (entity["name"] == {entity!r} and name == {field!r})'
    else:
        before = "if key in query:"
        after = f'if key in query and not (entity["name"] == {entity!r} and name == {field!r}):'
    assert before in source
    path.write_text(source.replace(before, after), encoding="utf-8")
    result = execute(product)
    report = json.loads(result.stdout.splitlines()[-1])
    assert result.returncode == 1 and report["passed"] is False, report
    assert "Query matrix differs" in report["message"], report
    assert f"/{entity}/{field}/" in report["message"], report


@pytest.mark.parametrize(
    "fault", ["ignored_combined_filter", "query_scope_bypass", "keyword_requires_full_value"]
)
def test_query_matrix_rejects_broken_and_or_row_scope(tmp_path, fault):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    if fault in {"ignored_combined_filter", "keyword_requires_full_value"}:
        path = product / "querying.py"
        source = path.read_text(encoding="utf-8")
        before, after = (
            ("if key in query:", 'if key in query and not query.get("q"):')
            if fault == "ignored_combined_filter"
            else ("table.c[name].icontains(q, autoescape=True)", "table.c[name].ilike(q)")
        )
    else:
        path = product / "business_runtime.py"
        source = path.read_text(encoding="utf-8")
        before = 'expressions += [target.c.archived_at.is_(None), *scope(actor, entity, "read")]'
        after = 'expressions += [target.c.archived_at.is_(None), *([] if request.query_params.get("q") else scope(actor, entity, "read"))]'
    assert before in source
    path.write_text(source.replace(before, after), encoding="utf-8")
    result = execute(product)
    report = json.loads(result.stdout.splitlines()[-1])
    assert result.returncode == 1 and report["passed"] is False, report
    assert "Query matrix differs" in report["message"], report
