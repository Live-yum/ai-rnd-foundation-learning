"""Business packaging cannot reuse classic CRUD or mismatched browser evidence."""

from copy import deepcopy

import pytest
from test_business_contracts import business_plan

from workbench.domain import Plan, digest
from workbench.generator import PrerequisiteError
from workbench.verification import require_business_evidence


def receipt():
    spec = Plan.model_validate(business_plan()).model_dump()
    business = {
        "passed": True,
        "spec_digest": digest(spec),
        "resources_checked": [e["name"] for e in spec["entities"]],
        "roles_checked": [r["name"] for r in spec["business"]["roles"]],
        "checks": [
            "business-" + s
            for s in [
                "bootstrap",
                "role-default",
                "row-permissions",
                "protected-fields",
                "relations",
                "transitions",
                "notes-history",
                "notifications",
                "scoped-metrics",
                "archive",
            ]
        ],
    }
    browser = {
        "applicable": True,
        "real_browser": True,
        "passed": True,
        "spec_digest": digest(spec),
        "entities": business["resources_checked"],
        "errors": [],
        "checks": [
            "business-browser-" + s
            for s in [
                "auth",
                "role-navigation",
                "assignment",
                "transitions",
                "notes-history",
                "reminders",
                "metrics",
                "role-restrictions",
            ]
        ]
        + ["business-browser-records:" + e["name"] for e in spec["entities"]],
    }
    return spec, {"business": business, "browser": browser}


def test_complete_business_receipt_and_api_only():
    spec, report = receipt()
    require_business_evidence(spec, report, True)
    require_business_evidence(spec, {"business": report["business"]}, False)


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("business", "passed", 1),
        ("business", "spec_digest", "old"),
        ("business", "resources_checked", []),
        ("business", "roles_checked", []),
        ("business", "checks", []),
        ("browser", "real_browser", 1),
        ("browser", "spec_digest", "old"),
        ("browser", "entities", []),
        ("browser", "errors", ["page error"]),
        ("browser", "checks", []),
    ],
)
def test_missing_or_wrong_business_evidence_blocks(section, key, value):
    spec, report = receipt()
    report = deepcopy(report)
    report[section][key] = value
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)
