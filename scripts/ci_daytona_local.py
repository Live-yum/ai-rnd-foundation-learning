"""Real smart-news workflow through all local tools and Daytona, fixture LLM only."""

import json
import tempfile
from pathlib import Path

from scripts.news_fixture import LIMITATIONS, ORIGINAL_REQUEST, NewsFixture
from workbench.filesystem import write_json
from workbench.runtime import Runtime
from workbench.sandbox import validate_configuration
from workbench.settings import ROOT, Settings
from workbench.store import Store


def main():
    report = {"passed": False, "model_transport": "explicit-fixture", "model_api_calls": 0}
    with tempfile.TemporaryDirectory(prefix="rnd-daytona-workflow-") as temp:
        settings = Settings(
            data_dir=Path(temp),
            install_products=True,
            tool_timeout=600,
            repo_map_provider="aider",
            retrieval_engine="continue",
            _env_file=ROOT / ".data/daytona-local/workbench.env",
        )
        validate_configuration(settings, "python-basic", {"database": "sqlite"})
        if settings.sandbox_provider != "daytona":
            raise ValueError("Acceptance requires explicit local Daytona configuration")
        store = Store(settings)
        fixture = NewsFixture()
        run_id = None
        try:
            store.migrate()
            project = store.create_project("泰拉瑞亚游戏小助手", "project")
            run_id = store.create_run(
                project["id"],
                {
                    "template": "python-basic",
                    "selection": {
                        "template": "python-basic",
                        "frontend": "simple-admin",
                        "database": "sqlite",
                    },
                    "requirement": ORIGINAL_REQUEST,
                },
                "run",
            )["run_id"]
            with Runtime(settings, store, fixture) as worker:
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "WAITING_CLARIFICATION", run
                assert run["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS
                store.set_automation(run_id, True, "authorize-once")
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "READY", run
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run_id}})
                assert snapshot.values["sandbox"]["enabled"] is True
            assert run["auto_mode"] and not run["pending"] and not run["error"]
            result = run["result"]
            assert result["isolated_dependencies"] is True
            assert result["cleanroom"]["passed"] is True and result["cleanroom"]["restart"] is True
            assert (settings.data_dir / "runs" / run_id / "delivery.zip").is_file()
            assert fixture.calls == ["requirement:1", "recommend:2", "plan:2"], fixture.calls
            assert [row["content"] for row in store.messages(run_id)] == [ORIGINAL_REQUEST]
            report.update(
                passed=True,
                status="READY",
                initial_status="WAITING_CLARIFICATION",
                smart_authorizations=1,
                subsequent_manual_actions=0,
                explicit_facts_preserved=True,
                reported_boundary_list_regression=True,
                actual_continue_index=True,
                actual_aider_repo_map=True,
                isolated_dependencies=True,
                independent_zip=True,
                cleanroom=result["cleanroom"],
                model_fixture_calls=fixture.calls,
            )
        finally:
            if run_id:
                run = store.get_run(run_id)
                report["last_status"] = run["status"]
                report["error"] = settings.redact(run["error"] or "")
                root = settings.data_dir / "runs" / run_id
                for name in ("daytona-verification.json", "tool-failure.json"):
                    path = root / name
                    if path.is_file():
                        report[name] = json.loads(settings.redact(path.read_text(encoding="utf-8")))
            write_json(ROOT / "reports/daytona-local.json", report)
            store.engine.dispose()
    print(json.dumps({"passed": report["passed"], "status": report["last_status"]}))


if __name__ == "__main__":
    main()
