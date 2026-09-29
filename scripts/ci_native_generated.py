"""CI fixtures exercise the same native lab implementation used by the platform."""

import argparse
import os
from pathlib import Path

from workbench.domain import Plan
from workbench.native_lab import run_acceptance


def acceptance_spec():
    return Plan(
        title="Native generated management",
        data_scope="shared",
        entities=[
            {
                "name": "device",
                "description": "设备台账",
                "fields": [
                    {"name": "name", "kind": "text"},
                    {"name": "quantity", "kind": "integer"},
                    {"name": "active", "kind": "boolean"},
                ],
            },
            {
                "name": "category",
                "description": "分类台账",
                "fields": [
                    {"name": "name", "kind": "text"},
                    {"name": "position", "kind": "integer"},
                ],
            },
        ],
        acceptance=[
            "Two separate native modules support CRUD",
            "Role grants and revocation are enforced",
            "Native frontend renders both generated modules",
            "Records persist across process restart",
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--source", type=Path, default=Path(".native/source"))
    parser.add_argument("--output", type=Path, default=Path(".native/product"))
    parser.add_argument("--frontend-source", type=Path, default=Path(".native/frontend"))
    parser.add_argument("--reports", type=Path, default=Path("reports/native"))
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args()
    plan = (
        Plan.model_validate_json(args.spec.read_text(encoding="utf-8"))
        if args.spec
        else acceptance_spec()
    )
    run_acceptance(
        args.template,
        args.source,
        args.output,
        args.frontend_source,
        os.environ["NATIVE_TEST_DATABASE_URL"],
        args.reports,
        plan,
    )


if __name__ == "__main__":
    main()
