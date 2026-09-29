"""Manual-only live sandbox acceptance on synthetic data after explicit owner authorization."""

import tempfile
from pathlib import Path

from workbench.daytona_tools import verify_daytona
from workbench.domain import Plan
from workbench.filesystem import write_json
from workbench.generator import generate_basic
from workbench.settings import ROOT, Settings
from workbench.verification import package_basic, verify_basic


def main():
    settings = Settings(_env_file=None)
    plan = Plan.model_validate(
        {
            "title": "人工授权沙箱验收",
            "data_scope": "per_user",
            "acceptance": ["CRUD"],
            "entities": [
                {
                    "name": "note",
                    "description": "演示笔记",
                    "fields": [{"name": "title", "kind": "text", "max_length": 250}],
                }
            ],
        }
    )
    with tempfile.TemporaryDirectory(prefix="rnd-live-daytona-") as directory:
        product = Path(directory) / "product"
        generate_basic(plan, product)
        local = verify_basic(plan, product, settings)
        if local.get("passed") is not True:
            raise RuntimeError("Local verification failed before sandbox upload")
        try:
            remote = verify_daytona(product, settings)
            delivery = package_basic(plan, product, settings, local)
            write_json(
                ROOT / "reports/daytona-live/delivery.json",
                {"local": local, "remote": remote, "cleanroom": delivery["cleanroom"]},
            )
        finally:
            receipt = product.parent / "daytona-0.json"
            if receipt.exists():
                target = ROOT / "reports/daytona-live/daytona.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(receipt.read_bytes())


if __name__ == "__main__":
    main()
