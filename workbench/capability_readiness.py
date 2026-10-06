"""Durable prerequisite accounting from existing trusted controller evidence.

This report is not an authorization, probe, installation or service credential.
It records what can be rechecked on the same retained candidate. Unsupported
external probes and old-schema upgrades cannot become green through approval.
"""

from workbench.domain import digest


def readiness_report(design, source_inventory, proof=None):
    proof = proof or {}
    plan = design.implementation
    binding = {
        "plan_digest": digest(plan.model_dump()),
        "source_digest": plan.source_digest,
        "source_inventory_digest": digest(source_inventory),
    }
    current = (
        proof.get("passed") is True
        and proof.get("source_digest") == binding["source_inventory_digest"]
        and proof.get("plan_digest") == binding["plan_digest"]
    )
    profile = proof.get("dependency_profile") if current else None
    items = [
        {
            "id": "locked-dependencies",
            "kind": "dependency",
            "status": "verified" if profile else "awaiting-matching-isolation-profile",
            "evidence_digest": digest(profile) if profile else None,
            "scope": "exact current readonly image and descriptors; no new dependency authorization",
        }
    ]
    for request in design.dependency_requests:
        items.append(
            {
                "id": "dependency-" + digest(request)[:24],
                "kind": "dependency",
                "description": request,
                "status": "awaiting-reviewed-locked-profile",
                "evidence_digest": None,
            }
        )
    consumer = proof.get("consumer", {}) if current else {}
    items.append(
        {
            "id": "existing-schema-migration",
            "kind": "migration",
            "status": "unverified",
            "evidence_digest": None,
            "bootstrap_and_restart_observed": bool(
                consumer.get("cold_start") is True and consumer.get("restart") is True
            ),
            "scope": "Cold bootstrap or unchanged-schema restart is not an old-version data migration.",
        }
    )
    for prerequisite in plan.prerequisites:
        fixtures = [
            check["id"]
            for check in proof.get("checks", [])
            if current
            and check.get("external_service") == prerequisite.id
            and check.get("evidence") == "external_fixture"
            and check.get("passed") is True
        ]
        items.append(
            {
                "id": prerequisite.id,
                "kind": prerequisite.kind,
                "description": prerequisite.description,
                "requirements": prerequisite.requirements,
                "contract_digest": digest(prerequisite.model_dump()),
                "status": "awaiting-approved-independent-probe",
                "adapter_fixture_scenarios": fixtures,
                "evidence_digest": None,
                "scope": "No supported live probe receipt exists; neither model claims nor manual acknowledgement verifies a service.",
            }
        )
    return {
        "protocol": "capability-readiness-v1",
        **binding,
        "items": items,
        "resume": "Retry the same run after the exact supported profile is verified; retain candidates and never silently regenerate or reduce scope.",
    }
