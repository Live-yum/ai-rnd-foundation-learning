"""Actual self-hosted sandbox profiles; failures never become local-success fallbacks."""

import argparse
import json
from pathlib import Path

from scripts.daytona_local import HOME
from scripts.news_fixture import news_spec
from workbench.catalog import Selection
from workbench.domain import Plan
from workbench.filesystem import write_json
from workbench.generator import generate_basic
from workbench.sandbox import verify_in_daytona
from workbench.settings import ROOT, Settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare-basic", "verify"])
    parser.add_argument("template", choices=["python-basic", "fastapiadmin", "yudao-vben"])
    parser.add_argument("--product", type=Path, default=ROOT / ".native/tool-product")
    args = parser.parse_args()
    if args.action == "prepare-basic":
        if args.template != "python-basic":
            raise ValueError("Only the native generator may prepare a native product")
        plan = Plan.model_validate(news_spec())
        selection = Selection(template="python-basic", backend="fastapi", frontend="simple-admin", database="postgresql")
        generate_basic(plan, args.product, selection=selection)
        return
    settings = Settings(_env_file=HOME / "workbench.env", daytona_runtime_timeout=3600)
    result = verify_in_daytona(args.product, args.template, settings)
    assert result["passed"] is True and result["cleanup"] == "deleted"
    assert result["runtime"]["host_credentials_used"] is False
    assert result["runtime"]["host_database_used"] is False
    write_json(ROOT / "reports/daytona-matrix.json", result)
    print(json.dumps({"passed": True, "template": args.template, "database": result["database"], "cleanup": result["cleanup"], "network_block_all": True}))


if __name__ == "__main__":
    main()
