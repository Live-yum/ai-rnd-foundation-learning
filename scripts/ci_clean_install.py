"""CI acceptance with genuine independent uv environments. Model input is an explicit fixture."""

import json
import tempfile
from pathlib import Path

from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import ROOT, Settings
from workbench.store import Store


class AcceptanceFixture:
    def complete(self, run_id, key, instruction, payload, schema):
        if schema is Requirement:
            return Requirement(
                summary="个人便签",
                users=["个人"],
                data_scope="per_user",
                features=["CRUD"],
                acceptance=["重启和数据隔离"],
            )
        if schema is Plan:
            return Plan.model_validate(
                {
                    "title": "便签",
                    "data_scope": "per_user",
                    "entities": [
                        {
                            "name": "note",
                            "description": "便签",
                            "fields": [{"name": "title", "kind": "text"}],
                        }
                    ],
                    "acceptance": ["CRUD、重启和数据隔离"],
                }
            )
        raise AssertionError("No coding call permitted for CRUD")


def main():
    with tempfile.TemporaryDirectory(prefix="rnd-acceptance-") as directory:
        settings = Settings(
            data_dir=Path(directory), install_products=True, tool_timeout=600, _env_file=None
        )
        store = Store(settings)
        try:
            store.migrate()
            project = store.create_project("acceptance", "project")
            run_id = store.create_run(
                project["id"], {"template": "python-basic", "requirement": "便签 CRUD"}, "run"
            )["run_id"]
            with Runtime(settings, store, AcceptanceFixture()) as worker:
                for stage in ["requirements", "design", "delivery"]:
                    worker.tick()
                    run = store.get_run(run_id)
                    assert run["pending"] and run["pending"]["stage"] == stage, run
                    store.submit(
                        run_id,
                        {
                            "gate_id": run["pending"]["gate_id"],
                            "action": "approve",
                            "approved": True,
                        },
                        stage,
                    )
                worker.tick()
            result = store.get_run(run_id)
            assert result["status"] == "READY", result
            assert result["result"]["isolated_dependencies"] is True
            assert result["result"]["cleanroom"]["passed"] is True
            destination = ROOT / "reports"
            destination.mkdir(exist_ok=True)
            (destination / "clean-install.json").write_text(
                json.dumps(result["result"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(
                "PASS: genuine product venv + separate clean-room venv; HTTP CRUD/isolation/restart; fixture model only"
            )
        finally:
            store.engine.dispose()


if __name__ == "__main__":
    main()
