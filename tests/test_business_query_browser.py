"""Real Chromium query evidence, including failures the retained-row check missed.

Every case runs the generated product and its actual verification driver. Mutations
touch only the disposable generated UI and cannot supply passing evidence.
"""

import json
import re

import pytest
import test_business_browser_evidence as browser_evidence


def test_browser_proves_each_declared_query_field_and_role(tmp_path):
    plan = browser_evidence.customer_plan()
    result, report = browser_evidence.run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    browser = report["browser"]
    assert browser["real_browser"] is True
    assert "business-browser-query-matrix" in browser["checks"]
    matrix = browser["evidence"]["query_matrix"]
    api_matrix = report["business"]["evidence"]["query_matrix"]
    expected = set()
    for permission in plan.business.permissions:
        if "read" not in permission.actions:
            continue
        entity = next(entity for entity in plan.entities if entity.name == permission.entity)
        searchable = [field for field in entity.fields if field.searchable]
        for field in entity.fields:
            if field.searchable:
                expected.add((permission.role, entity.name, field.name, "keyword"))
            if field.filterable:
                expected.add((permission.role, entity.name, field.name, "exact_filter"))
                if searchable:
                    expected.add((permission.role, entity.name, field.name, "combined"))

    def key(item):
        return item["role"], item["entity"], item["field"], item["kind"]

    assert {key(item) for item in matrix} == expected
    assert len(matrix) == len(expected)
    api_by_key = {key(item): item for item in api_matrix}
    browser_flags = {
        "query_values_verified",
        "response_ids_exact",
        "rendered_ids_exact",
        "controls_reset",
    }
    for item in matrix:
        assert {name: value for name, value in item.items() if name not in browser_flags} == (
            api_by_key[key(item)]
        )
        assert all(item[name] is True for name in browser_flags)
        assert item["cases"] == 2
        assert item["exact_results"] is True and item["role_scope"] is True
        assert all(
            type(item[name]) is int and 0 <= item[name] <= 200
            for name in (
                "positive_matches",
                "other_matches",
                "excluded_records",
                "foreign_matches",
                "isolated_matches",
            )
        )
    for entity in plan.entities:
        for field in entity.fields:
            if field.searchable:
                assert any(
                    item["entity"] == entity.name
                    and item["field"] == field.name
                    and item["kind"] == "keyword"
                    and item["isolated_matches"] > 0
                    for item in matrix
                )
    # The summary carries approved field names and aggregate counts only.
    encoded = json.dumps(matrix, ensure_ascii=False)
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f-]{27,}", encoded, re.I)
    assert not any(
        private in encoded
        for private in ["password", "token", "verify-", "expected_ids", "params", "record_id"]
    )


@pytest.mark.parametrize(
    "before,after,failure",
    [
        (
            "if (value) query.set(key, value);",
            'if (value && key !== "q") query.set(key, value);',
            "query-control-values",
        ),
        (
            "if (value) query.set(key, value);",
            'if (value && !key.startsWith("filter_")) query.set(key, value);',
            "query-control-values",
        ),
        (
            'query.set("limit", "50");',
            'query.set("limit", "50");\n'
            '  if (query.has("q")) for (const key of [...query.keys()])\n'
            '    if (key.startsWith("filter_")) query.delete(key);',
            "query-control-values",
        ),
        (
            "for (const row of rows) {",
            'for (const row of query.has("q") ? rows.slice(1) : rows) {',
            "query-rendered-ids",
        ),
        (
            'HTMLFormElement.prototype.reset.call($("filters"));',
            "/* Fault injection: leave the submitted controls populated. */",
            "query-control-values",
        ),
    ],
    ids=["missing-keyword", "missing-filter", "ignored-and", "missing-rendered-row", "stale-reset"],
)
def test_browser_rejects_query_control_and_rendering_faults(
    tmp_path, monkeypatch, before, after, failure
):
    generate = browser_evidence.generate_basic

    def with_ui_fault(plan, product, selection):
        generate(plan, product, selection)
        app = product / "web/app.js"
        source = app.read_text(encoding="utf-8")
        assert source.count(before) == 1, "Fault must target the actual generated UI exactly once"
        app.write_text(source.replace(before, after), encoding="utf-8")

    monkeypatch.setattr(browser_evidence, "generate_basic", with_ui_fault)
    result, report = browser_evidence.run_browser_gate(tmp_path, browser_evidence.customer_plan())
    assert result.returncode != 0 and report["passed"] is False, report
    assert "business-browser-" + failure in report["message"], report
