"""Real local-service safety acceptance; never accepts candidate/source inputs.

The fixed positive app establishes liveness after independent adversarial
identity/resource checks. A successful result permits only this exact profile,
verifier revision and SQLite selection, never general native stack execution.
No receipt is published until cleanup is confirmed. Missing quotas fail closed.
"""

import tempfile
from pathlib import Path

from scripts.capability_security_probe import run_security_probe
from scripts.ci_capability_profile import (
    fixed_application,
    require_atomic_consumer_evidence,
    require_profile_evidence,
)
from scripts.daytona_capability_profile import HOME, inspect_created_sandbox, require_profile
from workbench.capability_execution import (
    PROTOCOL,
    RECEIPT,
    profile_binding,
    require_security_receipt,
    verifier_identity,
)
from workbench.capability_sandbox import _verify
from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client, validate_configuration
from workbench.settings import ROOT, Settings


def main():
    install_loopback_guard()
    settings = Settings(_env_file=HOME / "workbench.env", tool_timeout=300)
    destination = HOME / RECEIPT
    summary_path = ROOT / "reports/capability-security.json"
    summary = {
        "passed": False,
        "paid_model_calls": 0,
        "scope": "real-local-security-and-fixed-positive",
    }
    # Invalidate an older acceptance before testing; failure never leaves a
    # stale successful entry under the current installation's admission path.
    write_json(destination, summary)
    write_json(summary_path, summary)
    if settings.sandbox_provider != "daytona":
        raise ValueError("Security acceptance requires real local Daytona")
    record = require_profile(HOME, settings.daytona_snapshot)
    from workbench.capability_browser_isolation import require_browser_acceptance

    browser_image = require_browser_acceptance(settings.capability_browser_image)
    verifier = verifier_identity()
    client = client_for(settings)
    try:
        with tempfile.TemporaryDirectory(prefix="rnd-security-positive-") as directory:
            product = Path(directory) / "product"
            plan = fixed_application(product, atomic_consumer=True)
            selected = plan.selection.model_dump()
            validate_configuration(settings, selected["template"], selected)
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selected,
                ROOT / "reports/capability-security-detail.json",
                client=client,
                aggregate=True,
                profile_record=record,
                control_observer=lambda sandbox_id: inspect_created_sandbox(
                    HOME, sandbox_id, require_resources=True
                ),
                security_probe=run_security_probe,
            )
            require_profile_evidence(
                proof,
                aggregate=True,
                source_digest=digest(manifest(product)),
                plan_digest=digest(plan.model_dump()),
                scenarios=plan.scenarios,
                selection=selected,
                database_tables=plan.runtime.database_tables,
            )
            require_atomic_consumer_evidence(product, plan, proof)
            if proof.get("restart_security_checks") != proof.get("security_checks"):
                raise ValueError("Restart did not preserve the complete security boundary")
            acceptance = {
                "protocol": PROTOCOL,
                "passed": True,
                "verifier_identity": verifier,
                "profile": profile_binding(record),
                "selection": selected,
                "checks": proof["security_checks"],
                "positive_product": True,
                "cleanup": proof["cleanup"],
                "paid_model_calls": 0,
                "restart_kind": proof.get("restart_kind"),
                "browser_image": browser_image,
                "preinstalled_dependencies": proof["preinstalled_dependencies"],
                "positive_source_digest": proof["source_digest"],
            }
            require_security_receipt(acceptance, record, browser_image=browser_image)
        close_client(client)
        client = None
        # Bind the exact revision tested, then recheck the live installation
        # after transport cleanup. A mid-run code/image change cannot certify
        # a different verifier or immutable dependency image.
        if require_profile(HOME, record["snapshot"]["snapshot"]) != record:
            raise ValueError("Profile changed during live certification")
        if require_browser_acceptance(settings.capability_browser_image) != browser_image:
            raise ValueError("Accepted browser image changed during live certification")
        require_security_receipt(acceptance, record, browser_image=browser_image)
        write_json(destination, acceptance)
        summary.update(acceptance)
    finally:
        if client is not None:
            close_client(client)
        write_json(summary_path, summary)


if __name__ == "__main__":
    main()
