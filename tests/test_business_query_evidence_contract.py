"""Exact per-field/role API and real-browser query proof cannot be omitted or forged."""

import pytest
from test_business_receipt import receipt

from workbench.generator import PrerequisiteError
from workbench.verification import require_business_evidence


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize("mutation", ["missing", "empty", "duplicate", "partial", "extra"])
def test_query_matrix_requires_exact_complete_unique_plan_targets(section, mutation):
    spec, report = receipt()
    rows = report[section]["evidence"]["query_matrix"]
    if mutation == "missing":
        report[section]["evidence"].pop("query_matrix")
    elif mutation == "empty":
        rows.clear()
    elif mutation == "partial":
        rows.pop()
    else:
        row = dict(rows[0])
        if mutation == "extra":
            row["field"] = "not_declared"
        rows.append(row)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize(
    "field,bad",
    [
        ("role", "unapproved_role"),
        ("entity", "unapproved_entity"),
        ("scope", "own"),
        ("field", "category"),
        ("kind", "unsupported"),
        ("keyword_field", "name"),
        ("cases", 1),
        ("cases", True),
        ("positive_matches", True),
        ("positive_matches", -1),
        ("positive_matches", 101),
        ("other_matches", 1),
        ("excluded_records", True),
        ("excluded_records", 201),
        ("foreign_matches", 1),
        ("foreign_matches", 201),
        ("isolated_matches", 101),
        ("exact_results", 1),
        ("exact_results", False),
        ("role_scope", False),
    ],
)
def test_query_matrix_rejects_substitution_unbounded_or_non_typed_observations(section, field, bad):
    spec, report = receipt()
    report[section]["evidence"]["query_matrix"][0][field] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "field", ["query_values_verified", "response_ids_exact", "rendered_ids_exact", "controls_reset"]
)
@pytest.mark.parametrize("bad", [False, 1, None])
def test_browser_query_requires_executed_values_exact_sets_and_reset(field, bad):
    spec, report = receipt()
    report["browser"]["evidence"]["query_matrix"][0][field] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "kind,count",
    [
        ("keyword", "isolated_matches"),
        ("keyword", "positive_matches"),
        ("exact_filter", "positive_matches"),
        ("combined", "positive_matches"),
        ("exact_filter", "excluded_records"),
    ],
)
def test_zero_only_query_cases_cannot_prove_declared_capability(kind, count):
    spec, report = receipt()
    target = next(r for r in report["business"]["evidence"]["query_matrix"] if r["kind"] == kind)
    for section in ("business", "browser"):
        for row in report[section]["evidence"]["query_matrix"]:
            if (row["entity"], row["field"], row["kind"]) == (
                target["entity"],
                target["field"],
                kind,
            ):
                row[count] = 0
                if count == "positive_matches":
                    row["isolated_matches"] = 0
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_zero_visible_rows_for_one_role_are_valid_without_inventing_access():
    spec, report = receipt()
    for section in ("business", "browser"):
        for row in report[section]["evidence"]["query_matrix"]:
            if row["role"] == "employee" and row["entity"] == "requests":
                row["positive_matches"] = row["other_matches"] = row["isolated_matches"] = 0
    require_business_evidence(spec, report, True)


def test_browser_counts_must_equal_independent_api_expectations():
    spec, report = receipt()
    report["browser"]["evidence"]["query_matrix"][0]["excluded_records"] += 1
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,marker",
    [("business", "business-query-matrix"), ("browser", "business-browser-query-matrix")],
)
def test_query_execution_marker_cannot_be_omitted(section, marker):
    spec, report = receipt()
    report[section]["checks"].remove(marker)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_query_proof_does_not_accept_raw_terms_or_record_ids():
    for section in ("business", "browser"):
        spec, report = receipt()
        report[section]["evidence"]["query_matrix"][0]["raw_query"] = "unneeded private term"
        with pytest.raises(PrerequisiteError):
            require_business_evidence(spec, report, True)


def test_combined_alternate_value_may_have_real_matches_without_weakening_exact_sets():
    spec, report = receipt()
    for section in ("business", "browser"):
        row = next(
            r for r in report[section]["evidence"]["query_matrix"] if r["kind"] == "combined"
        )
        row["other_matches"] = 1
    require_business_evidence(spec, report, True)


def test_required_singleton_filter_has_no_legal_unequal_choice():
    from workbench.domain import digest

    spec, report = receipt()
    field = next(
        f
        for e in spec["entities"]
        if e["name"] == "customers"
        for f in e["fields"]
        if f["name"] == "category"
    )
    field["choices"] = [field["choices"][0]]
    field["choice_labels"] = {
        k: v for k, v in field["choice_labels"].items() if k in field["choices"]
    }
    next(
        p
        for p in report["business"]["evidence"]["field_validation"]
        if (p["entity"], p["field"]) == ("customers", "category")
    )["declared_choices"] = 1
    for section in ("business", "browser"):
        report[section]["spec_digest"] = digest(spec)
        for row in report[section]["evidence"]["query_matrix"]:
            if (row["entity"], row["field"], row["kind"]) == (
                "customers",
                "category",
                "exact_filter",
            ):
                row["excluded_records"] = 0
    require_business_evidence(spec, report, True)
