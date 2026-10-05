"""Authored native contest slice against trusted independent business assertions.

This is deliberately not model-generation evidence. The full original request
retains its unimplemented obligations regardless of this bounded slice result.
"""

import argparse
import tempfile
from pathlib import Path

from scripts.capability_security_probe import security_probe_for_profile
from scripts.ci_native_capability_source import (
    PRODUCT,
    RECEIPT,
    copy_exact_source,
    require_exact_source,
    require_handoff,
)
from scripts.daytona_capability_profile import inspect_created_sandbox
from scripts.daytona_native_capability_profile import (
    ENVIRONMENT,
    HOME,
    require_native_profile,
    selection,
)
from scripts.extension_oracles import contest
from workbench.capability_execution import capability_execution_prerequisites
from workbench.capability_sandbox import _verify
from workbench.domain import digest
from workbench.filesystem import manifest, sha, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings

FIXTURE = ROOT / "tests/fixtures/contest_native/module_contest"


def install_authored_fixture(product):
    expected = dict(require_exact_source(product, manifest(product)))
    destination = product / "backend/app/plugin/module_rnd/contest"
    if destination.exists() or destination.is_symlink():
        raise ValueError("Authored fixture must not overwrite another candidate module")
    destination.parent.mkdir(parents=True, exist_ok=True)
    marker = destination.parent / "__init__.py"
    if not marker.exists():
        marker.write_text("", encoding="utf-8")
        expected[marker.relative_to(product).as_posix()] = sha(marker)
    fixture = manifest(FIXTURE)
    copy_exact_source(FIXTURE, destination, fixture)
    prefix = destination.relative_to(product).as_posix() + "/"
    expected.update({prefix + name: value for name, value in fixture.items()})
    require_exact_source(product, expected)
    return expected


def require_business_proof(proof):
    business = proof.get("business_oracle", {})
    if (
        proof.get("passed") is not True
        or proof.get("cleanup") != "deleted"
        or business.get("protocol") != contest.CONTRACT_VERSION
        or business.get("full_request_complete") is not False
        or business.get("remaining_obligations") != list(contest.REMAINING)
        or business.get("fresh_replay") is not True
        or business.get("same_cluster") is not True
        or business.get("distinct_database_oid") is not True
        or business.get("witnesses") != {name: True for name in contest.SEMANTICS}
    ):
        raise ValueError("Independent native contest assertions did not all pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path, default=PRODUCT)
    parser.add_argument("--source-receipt", type=Path, default=RECEIPT)
    args = parser.parse_args()
    install_loopback_guard()
    settings = Settings(
        _env_file=args.directory / ENVIRONMENT,
        tool_timeout=900,
        capability_execution_enabled=True,
        capability_profile_directory=args.directory,
    )
    summary = {
        "passed": False,
        "model_transport": "authored-reference-fixture",
        "paid_model_calls": 0,
        "full_request_complete": False,
    }
    report = ROOT / "reports/contest-capability.json"
    write_json(report, summary)
    client = None
    try:
        directory, record = capability_execution_prerequisites(settings, selection())
        require_native_profile(directory)
        handoff = require_handoff(args.product, args.source_receipt)
        if (
            record["inputs"]["product"] != handoff["product"]
            or record["inputs"]["source_identity"] != handoff["source_identity"]
            or record["inputs"]["descriptors"] != handoff["descriptors"]
            or record["inputs"]["descriptor_roles"] != handoff["descriptor_roles"]
        ):
            raise ValueError("Authored contest must use the exact registered CI source baseline")
        client = client_for(settings)
        with tempfile.TemporaryDirectory(prefix="rnd-authored-contest-") as temporary:
            product = Path(temporary) / "product"
            copy_exact_source(args.product, product, handoff["inventory"])
            inventory = install_authored_fixture(product)
            from scripts.ci_native_capability_security import fixed_plan

            plan = fixed_plan(product)
            plan.runtime.database_tables.extend(
                ["rnd_contest_team", "rnd_contest_membership", "rnd_contest_invitation"]
            )
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selection(),
                ROOT / "reports/contest-capability-detail.json",
                client=client,
                aggregate=True,
                profile_record=record,
                control_observer=lambda sandbox_id: inspect_created_sandbox(
                    directory, sandbox_id, require_resources=True, selection=selection()
                ),
                security_probe=security_probe_for_profile(
                    directory, record, client=client, settings=settings
                ),
                trusted_oracle=contest.CONTRACT_VERSION,
            )
            require_business_proof(proof)
            require_exact_source(product, inventory)
            if proof["source_digest"] != digest(inventory):
                raise ValueError("Authored contest proof does not bind the exact augmented source")
            require_handoff(args.product, args.source_receipt)
            summary.update(
                passed=True,
                business_oracle=proof["business_oracle"],
                cleanup=proof["cleanup"],
                source_digest=proof["source_digest"],
            )
    finally:
        if client is not None:
            close_client(client)
        write_json(report, summary)


if __name__ == "__main__":
    main()
