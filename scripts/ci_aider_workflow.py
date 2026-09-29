"""Actual LangGraph -> Aider CLI -> independent product verification, fixture LLM only."""

import json
import tempfile
from pathlib import Path

from workbench.aider_tool import EditBlocks
from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import Settings
from workbench.store import Store


class ApprovedFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is Requirement:
            return Requirement(
                summary="个人任务",
                users=["个人"],
                data_scope="per_user",
                features=["CRUD", "priority不能为负"],
                acceptance=["规则和重启"],
            )
        if schema is Plan:
            assert (
                payload["code_context"]["contexts"][0]["repo_map"]["provider"]
                == "aider-cli-repo-map"
            )
            return Plan.model_validate(
                {
                    "title": "任务",
                    "data_scope": "per_user",
                    "acceptance": ["CRUD与非负校验"],
                    "entities": [
                        {
                            "name": "task",
                            "description": "任务",
                            "fields": [
                                {"name": "title", "kind": "text"},
                                {"name": "priority", "kind": "integer"},
                            ],
                        }
                    ],
                    "custom_rules": [
                        {
                            "description": "priority不能为负",
                            "entity": "task",
                            "accept_examples": [{"title": "ok", "priority": 1}],
                            "reject_examples": [{"title": "bad", "priority": -1}],
                        }
                    ],
                }
            )
        if schema is EditBlocks:
            return EditBlocks(
                before_sha256=payload["context"]["files"]["custom_rules.py"]["sha256"],
                explanation="Explicit fixture, no model API called",
                blocks="custom_rules.py\n<<<<<<< SEARCH\n    return None\n=======\n"
                "    if entity == 'task' and data.get('priority', 0) < 0:\n"
                "        raise ValueError('nonnegative')\n    return None\n>>>>>>> REPLACE\n",
            )
        raise AssertionError(schema)


def verify_workflow():
    with tempfile.TemporaryDirectory(prefix="rnd-aider-flow-") as directory:
        settings = Settings(
            data_dir=Path(directory),
            install_products=True,
            tool_timeout=600,
            coding_engine="aider",
            repo_map_provider="aider",
            _env_file=None,
        )
        store = Store(settings)
        fixture = ApprovedFixture()
        try:
            store.migrate()
            project = store.create_project("aider-acceptance", "project")
            run_id = store.create_run(
                project["id"],
                {"template": "python-basic", "requirement": "个人任务与非负优先级"},
                "run",
            )["run_id"]
            with Runtime(settings, store, fixture) as worker:
                for stage in ("requirements", "design", "delivery"):
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
            assert result["result"]["cleanroom"]["restart"] is True
            assert fixture.calls == ["requirement:1", "plan:1", "coding:aider:0"], fixture.calls
            edit = json.loads(
                (Path(directory) / "runs" / run_id / "coding-0.json").read_text(encoding="utf-8")
            )
            assert (
                edit["provider"] == "aider-cli-apply"
                and edit["before_commit"] != edit["after_commit"]
            )
            return {
                "ready": True,
                "isolated_dependencies": True,
                "cleanroom_passed": True,
                "restart_passed": True,
                "actual_aider_edit": True,
                "actual_langgraph": True,
                "model_transport": "explicit-fixture",
                "model_api_calls": 0,
            }
        except Exception:
            directory = Path(directory)
            reports = Path("reports")
            reports.mkdir(exist_ok=True)
            for failure in directory.glob("runs/*/tool-failure.json"):
                text = failure.read_text(encoding="utf-8")
                (reports / "aider-workflow-failure.json").write_text(text, encoding="utf-8")
                print(text, flush=True)
            raise
        finally:
            store.engine.dispose()


if __name__ == "__main__":
    print(json.dumps(verify_workflow(), ensure_ascii=False, indent=2))
