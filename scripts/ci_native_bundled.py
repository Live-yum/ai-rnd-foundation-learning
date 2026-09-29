"""Run original native acceptance AND standalone empty-database deployment from vendored code."""

import argparse
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from workbench.filesystem import write_json
from workbench.native import prepare_sources
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    args = parser.parse_args()
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
        acceptance_spec(),
    )


if __name__ == "__main__":
    main()
