"""Business packaging cannot reuse classic CRUD or mismatched browser evidence."""

import json
from copy import deepcopy

import pytest

from workbench.domain import Plan
from workbench.generator import PrerequisiteError
from workbench.settings import ROOT
from workbench.verification import require_business_evidence


def receipt():
    # This fixture only exercises receipt validation; live generated HTTP/browser
    # tests separately execute the complete workflow and reject injected faults.
    spec = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    ).model_dump()
    report = json.loads(
        (ROOT / "tests/fixtures/customer_evidence_receipt_unit_only.json").read_text(
            encoding="utf-8"
        )
    )
    assert report.pop("unit_test_fixture_only") is True
    report.pop("source")
    return spec, report


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
