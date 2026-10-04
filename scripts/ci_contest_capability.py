"""Authored native contest slice against trusted independent business assertions.

This is deliberately not model-generation evidence. The full original request
retains its unimplemented obligations regardless of this bounded slice result.
"""

import argparse
import shutil
import tempfile
from pathlib import Path

from scripts.capability_security_probe import security_probe_for_profile
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
from workbench.filesystem import write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings

FIXTURE = ROOT / "tests/fixtures/contest_native/module_contest"


def install_authored_fixture(product):
    destination = product / "backend/app/plugin/module_rnd/contest"
    if destination.exists() or destination.is_symlink():
        raise ValueError("Authored fixture must not overwrite another candidate module")
    destination.parent.mkdir(parents=True, exist_ok=True)
    marker = destination.parent / "__init__.py"
    if not marker.exists():
        marker.write_text("", encoding="utf-8")
    shutil.copytree(FIXTURE, destination)


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
    parser.add_argument("--product", type=Path, default=ROOT / ".native/tool-product")
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
        client = client_for(settings)
        with tempfile.TemporaryDirectory(prefix="rnd-authored-contest-") as temporary:
            product = Path(temporary) / "product"
            shutil.copytree(
                args.product,
                product,
                ignore=shutil.ignore_patterns(
                    ".venv", "node_modules", ".git", "__pycache__", ".env", ".env.*", "*.pyc"
                ),
            )
            install_authored_fixture(product)
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
                security_probe=security_probe_for_profile(directory, record),
                trusted_oracle=contest.CONTRACT_VERSION,
            )
            require_business_proof(proof)
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
