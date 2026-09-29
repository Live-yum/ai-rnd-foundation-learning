"""Self-hosted local service smoke: generated SQLite product, no hosted account."""

import json
import tempfile
from pathlib import Path

from workbench.domain import Plan
from workbench.filesystem import write_json
from workbench.generator import generate_basic
from workbench.sandbox import validate_configuration, verify_in_daytona
from workbench.settings import ROOT, Settings


def main():
    settings = Settings(_env_file=ROOT / ".data/daytona-local/workbench.env")
    validate_configuration(settings, "python-basic", {"database": "sqlite"})
    if settings.sandbox_provider != "daytona":
        raise ValueError("Self-hosted smoke requires explicit local Daytona configuration")
    plan = Plan.model_validate(
        {
            "title": "Sandbox smoke",
            "acceptance": ["CRUD and restart succeed"],
            "data_scope": "per_user",
            "entities": [
                {
                    "name": "note",
                    "description": "Notes",
                    "fields": [{"name": "title", "kind": "text", "required": True}],
                }
            ],
            "custom_rules": [],
            "unsupported": [],
        }
    )
    with tempfile.TemporaryDirectory(prefix="rnd-daytona-local-") as temp:
        root = Path(temp)
        product = root / "product"
        generate_basic(plan, product)
        try:
            receipt = verify_in_daytona(product, "python-basic", settings)
            print(json.dumps({"passed": receipt["passed"], "cleanup": receipt["cleanup"]}))
        finally:
            path = root / "daytona-verification.json"
            if path.exists():
                write_json(
                    ROOT / "reports/daytona-local.json",
                    json.loads(path.read_text(encoding="utf-8")),
                )


if __name__ == "__main__":
    main()
