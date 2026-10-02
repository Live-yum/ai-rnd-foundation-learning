"""Run original native acceptance AND standalone empty-database deployment from vendored code."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from workbench.domain import Plan, digest
from workbench.filesystem import manifest, sha, write_json
from workbench.native import prepare_sources
from workbench.native_delivery import (
    require_native_business,
    require_native_runtime,
    require_native_style,
)
from workbench.native_evidence import MAX_ACCEPTANCE_BYTES, native_review_evidence
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings

APPROVED_CUSTOMER_REPLAYS = {
    "yudao-1d7": {
        "template": "yudao-vben",
        "path": "tests/fixtures/customer_approved_replays/yudao-1d7.json",
        "sha256": "16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5",
    },
    "fastapi-0e8": {
        "template": "fastapiadmin",
        "path": "tests/fixtures/customer_approved_replays/fastapi-0e8.json",
        "sha256": "023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4",
    },
}


def approved_customer_replay(name, template):
    """Only the recorded approved synthetic Plan, never a diagnostic candidate."""
    from scripts.ci_real_model import MAX_REPLAY_PLAN_BYTES, DiagnosticTextBudget

    record = APPROVED_CUSTOMER_REPLAYS[name]
    path = ROOT / record["path"]
    if template != record["template"] or path.is_symlink():
        raise ValueError("Approved replay template/path mismatch")
    if path.stat().st_size > MAX_REPLAY_PLAN_BYTES:
        raise ValueError("Approved replay exceeds size limit")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("Approved replay digest mismatch")
    text = raw.decode("utf-8")
    if DiagnosticTextBudget().scrub(text) != text:
        raise ValueError("Approved replay contains credential-like content")
    return Plan.model_validate_json(text)


def verify_review_projection(template, plan, product, reports, report):
    """Exercise production review projection using only this execution's saved proof."""
    status = {
        "version": 1,
        "template": template,
        "model_calls": 0,
        "spec_digest": digest(plan.model_dump()),
        "phase": "saved-execution-evidence",
        "passed": False,
    }
    status_path = reports / "review-projection-status.json"
    projection_path = reports / "review-projection.json"
    projection_path.unlink(missing_ok=True)
    write_json(status_path, status)
    try:
        path = reports / "acceptance.json"
        if path.is_symlink() or path.stat().st_size > MAX_ACCEPTANCE_BYTES:
            raise ValueError("Unsafe native acceptance artifact")
        with path.open("rb") as handle:
            raw = handle.read(MAX_ACCEPTANCE_BYTES + 1)
        if len(raw) > MAX_ACCEPTANCE_BYTES:
            raise ValueError("Native acceptance exceeds size limit")
        saved = json.loads(raw)
        if (
            saved != report
            or saved.get("template") != template
            or saved.get("spec_digest") != status["spec_digest"]
        ):
            raise ValueError("Native acceptance is not bound to this execution")
        status["acceptance_sha256"] = hashlib.sha256(raw).hexdigest()
        files = manifest(product)
        status["source_digest"] = digest(files)
        receipt = {"template": template, "spec_digest": status["spec_digest"]}
        status["phase"] = "native-runtime-deployment"
        require_native_runtime(saved)
        status["phase"] = "native-style-and-business"
        require_native_style(saved, receipt, files)
        require_native_business(saved, receipt, reports / "approved-spec.json")
        status["phase"] = "production-review-projection"
        projection = native_review_evidence(saved, plan, files, status["acceptance_sha256"])
        if sha(path) != status["acceptance_sha256"] or manifest(product) != files:
            raise ValueError("Native evidence or source changed during projection")
        write_json(projection_path, projection)
        status.update(phase="complete", passed=True)
        print("Native production review projection PASS (zero model calls)", flush=True)
        return projection
    finally:
        # Preserve a bounded allowlisted phase and hashes, never exception text,
        # environment variables, copied runtime folders or fabricated proof rows.
        write_json(status_path, status)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--spec", type=Path)
    inputs.add_argument("--approved-replay", choices=sorted(APPROVED_CUSTOMER_REPLAYS))
    args = parser.parse_args()
    plan = (
        approved_customer_replay(args.approved_replay, args.template)
        if args.approved_replay
        else Plan.model_validate_json(args.spec.read_text(encoding="utf-8"))
        if args.spec
        else acceptance_spec()
    )
    s = Settings(data_dir=ROOT / ".data/native-ci", _env_file=None)
    rows = prepare_sources(s, args.template)
    sources = {r["slot"]: Path(r["path"]) for r in rows}
    reports = ROOT / "reports/native"
    write_json(reports / "bundled-sources.json", rows)
    output = ROOT / ".native/product"
    report = run_acceptance(
        args.template,
        sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
        output if args.template == "fastapiadmin" else output / "backend",
        sources.get("frontend"),
        os.environ["NATIVE_TEST_DATABASE_URL"],
        reports,
        plan,
    )
    verify_review_projection(args.template, plan, output, reports, report)


if __name__ == "__main__":
    main()
