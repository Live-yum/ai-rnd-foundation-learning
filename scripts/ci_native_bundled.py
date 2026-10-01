"""Run original native acceptance AND standalone empty-database deployment from vendored code."""

import argparse
import hashlib
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from workbench.domain import Plan
from workbench.filesystem import write_json
from workbench.native import prepare_sources
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings

APPROVED_CUSTOMER_REPLAYS = {
    "yudao-1d7": {
        "template": "yudao-vben",
        "path": "tests/fixtures/customer_approved_replays/yudao-1d7.json",
        "sha256": "16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5",
    }
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
    run_acceptance(
        args.template,
        sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
        output if args.template == "fastapiadmin" else output / "backend",
        sources.get("frontend"),
        os.environ["NATIVE_TEST_DATABASE_URL"],
        reports,
        plan,
    )


if __name__ == "__main__":
    main()
