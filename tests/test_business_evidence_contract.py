"""Missing, substituted or partial detailed proof must never authorize delivery."""

import pytest
from test_business_receipt import receipt

from workbench.generator import PrerequisiteError
from workbench.verification import require_business_evidence


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize("mutation", ["missing", "empty", "true_version", "wrong_version"])
def test_business_delivery_requires_versioned_detailed_proof(section, mutation):
    spec, report = receipt()
    if mutation == "missing":
        report[section].pop("evidence")
    elif mutation == "empty":
        report[section]["evidence"] = {}
    else:
        report[section]["evidence"]["version"] = True if mutation == "true_version" else 0
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,proof,key,bad",
    [
        ("business", "field_validation", "entity", "wrong_resource"),
        ("business", "field_validation", "missing_required_rejected", False),
        ("business", "field_validation", "max_length", 999),
        ("business", "field_validation", "over_max_length_rejected", 1),
        ("business", "field_validation", "invalid_updates_rejected", True),
        ("business", "related_views", "target_row_acl", False),
        ("business", "related_views", "role", "unknown_role"),
        ("business", "related_views", "target_entities", []),
        ("business", "relation_labels", "references_checked", True),
        ("business", "relation_labels", "readable_labels_verified", False),
        ("business", "datetime_policy", "searchable", True),
        ("business", "datetime_policy", "timestamp_stored", False),
        ("business", "datetime_policy", "undeclared_query_parameters_rejected", ["filter"]),
        ("business", "due_notifications", "past_due_events_verified", 0),
        ("business", "due_notifications", "past_due_events_verified", True),
        ("business", "due_notifications", "recipient", "other"),
        ("business", "due_notifications", "future_deadline_no_event", False),
        ("business", "due_notifications", "event_and_read_state_persisted_after_restart", False),
        ("business", "audit_immutability", "entries_checked", True),
        ("business", "audit_immutability", "mutation_delete_attempts_rejected", 0),
        ("business", "audit_immutability", "archive_and_restart_preserved", False),
        ("browser", "relation_labels", "list", False),
        ("browser", "relation_labels", "records_checked", True),
        ("browser", "related_sources", "groups_checked", True),
        ("browser", "related_sources", "source_records", 99),
        ("browser", "related_views", "target_acl", False),
        ("browser", "related_views", "visible_records", 99),
        ("browser", "related_views", "navigation", None),
        ("browser", "datetime_controls", "controls_absent", False),
        ("browser", "datetime_controls", "date_range", True),
    ],
)
def test_detailed_proof_is_bound_to_plan_and_observed_counts(section, proof, key, bad):
    spec, report = receipt()
    report[section]["evidence"][proof][0][key] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,proof",
    [
        ("business", name)
        for name in (
            "field_validation",
            "related_views",
            "relation_labels",
            "datetime_policy",
            "due_notifications",
            "audit_immutability",
        )
    ]
    + [
        ("browser", name)
        for name in ("relation_labels", "related_sources", "related_views", "datetime_controls")
    ],
)
@pytest.mark.parametrize("mutation", ["omit", "duplicate", "missing_list"])
def test_empty_or_duplicated_proof_sets_cannot_replace_required_work(section, proof, mutation):
    spec, report = receipt()
    values = report[section]["evidence"][proof]
    if mutation == "omit":
        report[section]["evidence"][proof] = []
    elif mutation == "duplicate":
        values.append(dict(values[0]))
    else:
        report[section]["evidence"].pop(proof)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_missing_required_update_or_enum_rejection_cannot_be_hidden_by_create_checks():
    for attribute in (
        "invalid_updates_rejected",
        "invalid_enum_rejected",
        "protected_update_rejected",
    ):
        spec, report = receipt()
        proof = next(
            item for item in report["business"]["evidence"]["field_validation"] if attribute in item
        )
        proof.pop(attribute)
        with pytest.raises(PrerequisiteError):
            require_business_evidence(spec, report, True)
