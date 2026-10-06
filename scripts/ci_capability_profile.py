"""Positive isolation acceptance with only the repository's fixed authored app.

No model, arbitrary source directory, or task argument is accepted. Unsupported
kernel/profile prerequisites fail this command; exit 78 is never a passing proof.
Production source execution remains separately disabled pending review.
"""

import shutil
import tempfile
from pathlib import Path

from scripts.capability_fixture import APP, GOAL, SHARED_ROUTES, make_plan
from scripts.daytona_capability_profile import HOME, inspect_created_sandbox, require_profile
from workbench.capability_contracts import CapabilityPlan, scope_sources
from workbench.capability_sandbox import _verify
from workbench.capability_verification import (
    BROWSER_ERROR_CODES,
    BROWSER_PHASES,
    CheckFailure,
    require_evidence,
)
from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client, validate_configuration
from workbench.settings import ROOT, Settings


def fixed_application(product, *, atomic_consumer=False):
    product.mkdir(parents=True)
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / "templates/product" / name, product / name)
    (product / "app.py").write_text(
        APP.replace(
            "    # CUSTOM_ACCESS",
            "    from access import readable\n    allowed = readable(row['owner'],name,member)",
        ).replace("# CUSTOM_ROUTES", SHARED_ROUTES),
        encoding="utf-8",
    )
    (product / "access.py").write_text(
        "def readable(owner, actor, member):\n    return owner == actor or member\n",
        encoding="utf-8",
    )
    sources = scope_sources([GOAL])
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": digest([GOAL]),
            "selection": {"template": "python-basic"},
        }
    )
    if atomic_consumer:
        from workbench.capability_consumer import prepare_consumer

        plan = CapabilityPlan.model_validate(
            {
                **plan.model_dump(),
                "obligations": [
                    {
                        "id": "authored-retained-profile",
                        "source_id": sources[0]["id"],
                        "source_sha256": sources[0]["sha256"],
                        "assertion": "Authored fixture profile title is physically retained before restart replay",
                        "scenario_id": "private_records",
                        "physical": {
                            "table": "entries",
                            "key": {"id": "${entry}"},
                            "values": {"title": "持久化资料-${nonce}"},
                        },
                    }
                ],
            }
        )
        # This is an authored verifier fixture, never a model-produced product
        # or a declaration that all clauses of GOAL have been completed.
        shutil.copyfile(ROOT / "templates/product/start.py", product / "start.py")
        write_json(product / "selection.json", plan.selection.model_dump())
        prepare_consumer(product, plan)
    return plan


def require_atomic_consumer_evidence(product, plan, proof):
    from workbench.capability_consumer import require_consumer_evidence
    from workbench.capability_obligations import require_obligation_evidence

    if not plan.obligations:
        raise CheckFailure("Live authored acceptance must exercise pre-replay physical retention")
    require_obligation_evidence(plan, proof, aggregate=True)
    require_consumer_evidence(product, plan, proof)


def require_profile_evidence(proof, **bindings):
    """Keep strict validation; explain only an allowlisted browser failure."""
    try:
        require_evidence(proof, **bindings)
    except CheckFailure:
        diagnostic = proof.get("browser_diagnostic", {})
        phase, code = diagnostic.get("phase"), diagnostic.get("error_code")
        if (
            proof.get("passed") is False
            and isinstance(phase, str)
            and phase in BROWSER_PHASES
            and isinstance(code, str)
            and code in BROWSER_ERROR_CODES
        ):
            raise CheckFailure(
                f"Browser acceptance failed: {phase}/{code}; "
                "see capability-profile-detail.json; strict evidence rejected"
            ) from None
        raise


def main():
    install_loopback_guard()
    settings = Settings(_env_file=HOME / "workbench.env", tool_timeout=300)
    report_path = ROOT / "reports/capability-profile.json"
    summary = {
        "passed": False,
        "authored_fixture": True,
        "paid_model_calls": 0,
        "production_execution_enabled": False,
    }
    write_json(report_path, summary)
    if settings.sandbox_provider != "daytona":
        raise ValueError("Positive profile acceptance requires the real local Daytona service")
    record = require_profile(HOME, settings.daytona_snapshot)
    with tempfile.TemporaryDirectory(prefix="rnd-fixed-profile-") as directory:
        product = Path(directory) / "product"
        plan = fixed_application(product, atomic_consumer=True)
        selected = plan.selection.model_dump()
        validate_configuration(settings, selected["template"], selected)
        client = client_for(settings)
        try:
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selected,
                ROOT / "reports/capability-profile-detail.json",
                client=client,
                aggregate=True,
                profile_record=record,
                control_observer=lambda sandbox_id: inspect_created_sandbox(HOME, sandbox_id),
            )
            summary["proof"] = settings.redact_data(proof)
            require_profile_evidence(
                proof,
                source_digest=digest(manifest(product)),
                plan_digest=digest(plan.model_dump()),
                scenarios=plan.scenarios,
                selection=selected,
                database_tables=plan.runtime.database_tables,
                aggregate=True,
            )
            require_atomic_consumer_evidence(product, plan, proof)
            summary["passed"] = True
        finally:
            try:
                close_client(client)
            except Exception:
                summary["passed"] = False
                raise
            finally:
                write_json(report_path, summary)


if __name__ == "__main__":
    main()
