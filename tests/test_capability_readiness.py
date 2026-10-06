"""Status accounting cannot turn fixture/manual claims into live service proof."""

from test_capability_obligations import proposed

from scripts.capability_fixture import fixture_baseline
from workbench.capability_contracts import ExternalPrerequisite
from workbench.capability_readiness import readiness_report
from workbench.domain import digest
from workbench.orchestration import ExtensionDesign


def test_matching_pinned_dependency_proof_closes_only_exact_supported_profile():
    plan, _, _ = proposed()
    design = ExtensionDesign(baseline=fixture_baseline(), implementation=plan)
    listing = {"app.py": "a" * 64}
    before = readiness_report(design, listing)
    assert before["items"][0]["status"] == "awaiting-matching-isolation-profile"
    proof = {
        "passed": True,
        "plan_digest": digest(plan.model_dump()),
        "source_digest": digest(listing),
        "dependency_profile": {"pinned": "image"},
        "consumer": {"cold_start": True, "restart": True},
    }
    after = readiness_report(design, listing, proof)
    assert after["items"][0]["status"] == "verified"
    migration = next(item for item in after["items"] if item["kind"] == "migration")
    assert migration["status"] == "unverified"
    assert migration["bootstrap_and_restart_observed"] is True
    stale = readiness_report(design, {"app.py": "b" * 64}, proof)
    assert stale["items"][0]["status"] != "verified"


def test_external_fixture_or_model_claim_never_closes_external_prerequisite():
    plan, scope, _ = proposed()
    plan.prerequisites = [
        ExternalPrerequisite(
            id="email",
            kind="service",
            description="real email service",
            requirements=[scope["sources"][0]["id"]],
            provider="manual",
        )
    ]
    design = ExtensionDesign(
        baseline=fixture_baseline(),
        implementation=plan,
        dependency_requests=["new unreviewed package"],
    )
    proof = {
        "passed": True,
        "plan_digest": digest(plan.model_dump()),
        "source_digest": digest({}),
        "checks": [
            {
                "id": "fixture",
                "external_service": "email",
                "passed": True,
                "evidence": "external_fixture",
            }
        ],
        "external_receipts": {"email": {"approved": True, "verified": True}},
    }
    result = readiness_report(design, {}, proof)
    service = next(item for item in result["items"] if item["id"] == "email")
    assert service["status"] == "awaiting-approved-independent-probe"
    assert service["adapter_fixture_scenarios"] == ["fixture"]
    assert service["evidence_digest"] is None
    assert (
        next(
            item for item in result["items"] if item.get("description") == "new unreviewed package"
        )["status"]
        == "awaiting-reviewed-locked-profile"
    )
