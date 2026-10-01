"""Analysis conflicts stay diagnosable without publishing raw analysis or user history."""

import json
from copy import deepcopy

import pytest

from scripts import ci_real_model as harness


def conflict():
    return {
        "code": "requirement_source_conflict",
        "target": {"entity": "requests", "field": "title"},
        "attribute": "max_length",
        "message": "raw-provider-canary",
        "sources": [
            {
                "source": {"section": "user_messages", "index": 0},
                "origin": "user_input",
                "expected": 200,
                "text": "requests.title 最长200，token=credential-canary",
                "user_sources": [{"text": "private-full-history-canary"}],
            },
            {
                "source": {"section": "field_requirements", "index": 4},
                "origin": "model_analysis",
                "expected": 120,
                "text": "requests.title max_length=120",
                "raw_response": "private-provider-canary",
            },
        ],
    }


def test_atomic_analysis_conflicts_export_only_selected_values_and_origins():
    raw = conflict()
    before = deepcopy(raw)
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert len(out) == 1
    assert out[0]["target"] == raw["target"]
    assert [source["expected"] for source in out[0]["sources"]] == [200, 120]
    assert [source["origin"] for source in out[0]["sources"]] == ["user_input", "model_analysis"]
    assert out[0]["sources"][0]["source"] == {"section": "user_messages", "index": 0}
    rendered = json.dumps(out)
    for secret in (
        "credential-canary",
        "raw-provider-canary",
        "private-full-history-canary",
        "private-provider-canary",
    ):
        assert secret not in rendered
    assert raw == before


@pytest.mark.parametrize("bad", [None, {}, "not-a-list", [None], [{"attribute": []}]])
def test_malformed_conflict_collection_is_not_exported(bad):
    assert harness.safe_analysis_conflict_details(bad, harness.DiagnosticTextBudget()) == []


@pytest.mark.parametrize(
    "change", ["section", "index", "origin", "expected", "target", "attribute"]
)
def test_untrusted_conflict_fields_are_not_echoed(change):
    raw = conflict()
    source = raw["sources"][0]
    if change == "attribute":
        raw["attribute"] = ["private-canary"]
    elif change == "section":
        source["source"]["section"] = ["private-canary"]
    elif change == "index":
        source["source"]["index"] = "private-canary"
    elif change == "origin":
        source["origin"] = ["private-canary"]
    elif change == "expected":
        source["expected"] = {"payload": "private-canary"}
    else:
        raw["target"]["field"] = "private-canary"
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert "private-canary" not in json.dumps(out)


def test_conflict_text_uses_shared_budget_and_scrubs_before_clipping():
    raw = conflict()
    raw["sources"][0]["text"] = "a" * 590 + "known-secret-canary" + "z" * 5000
    raw["sources"] *= 20
    budget = harness.DiagnosticTextBudget(("known-secret-canary",), limit=700)
    out = harness.safe_analysis_conflict_details([raw] * 100, budget)
    assert len(out) == 20
    assert all(len(item["sources"]) <= 8 for item in out)
    assert sum(len(s.get("source_excerpt", "")) for item in out for s in item["sources"]) <= 700
    assert "known-secret" not in json.dumps(out)
    assert budget.remaining == 0


def test_choices_export_cardinality_without_arbitrary_literals():
    raw = conflict()
    raw["attribute"] = "choices"
    raw["sources"][0]["expected"] = ["private-choice-a", "private-choice-b"]
    raw["sources"][1]["expected"] = ["private-choice-c"]
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert [s["expected_count"] for s in out[0]["sources"]] == [2, 1]
    assert "private-choice" not in json.dumps(out)


def test_failed_analysis_without_any_plan_preserves_safe_conflict_details():
    class Store:
        def get_run(self, run_id):
            return {
                "status": "BLOCKED",
                "template": "python-basic",
                "model_calls": 3,
                "error": "需求分析来源冲突：requests.title.max_length",
                "pending": {
                    "stage": "clarification",
                    "data": {"blocked": ["需求分析来源冲突"], "analysis_diagnostics": [conflict()]},
                },
            }

        def latest_revision(self, run_id, stage):
            return None

    details = harness.safe_workflow_details(Store(), "run", [])
    assert details["valid_plan_present"] is False
    assert details["pending_stage"] == "clarification"
    assert details["analysis_source_conflicts"][0]["sources"][1]["expected"] == 120
    assert "requirement_source_conflict" in details["error_categories"]
    assert "private-provider-canary" not in json.dumps(details)
