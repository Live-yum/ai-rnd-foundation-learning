"""Real local HTTP/Chromium proof of the registration scope correction UI.

The requirements gateway is an explicit in-process test fixture. The worker,
Store, gates, HTTP API, SSE updates and compiled Vue application are real.
"""

import hashlib
import json
import os
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import uvicorn
from sqlalchemy import select

from workbench.api import create_app
from workbench.domain import Plan, Requirement
from workbench.filesystem import write_json
from workbench.flow import Workflow
from workbench.requirement_intent import ADMIN_SCOPE, AUTHENTICATED_SCOPE
from workbench.runtime import Runtime, pending_interrupt
from workbench.settings import ROOT, Settings
from workbench.store import Approval, Revision, Store
from workbench.tools import clean_env

ORIGINAL = "大学生计算机设计大赛报名网站"


def ui_snapshot():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ("workbench/web/index.html", "workbench/web/app.js", "workbench/web/style.css")
    }


class ScopeFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        assert schema is Requirement, "Browser correction must stop before native planning"
        assert payload["original_request"] == ORIGINAL
        assert len(payload["fresh_user_corrections"]) == 1
        assert AUTHENTICATED_SCOPE in payload["fresh_user_corrections"][0]
        assert ADMIN_SCOPE not in payload["fresh_user_corrections"][0]
        self.calls.append({"run_id": run_id, "key": key})
        return Requirement(
            summary=ORIGINAL,
            users=["参赛者", "管理员"],
            data_scope="shared",
            features=[AUTHENTICATED_SCOPE],
            acceptance=["参赛者仅可创建和维护本人报名，不能管理其他参赛者报名"],
        )


def legacy_failed_run(settings):
    """Write the real pre-upgrade checkpoint without importing optional drivers."""
    store = Store(settings)
    store.migrate()
    requirement = Requirement(
        summary="管理员维护竞赛报名记录",
        users=["管理员"],
        data_scope="shared",
        features=["管理员录入和维护报名记录"],
        acceptance=["管理员可维护报名记录"],
    )

    class LegacyFixture:
        def complete(self, run_id, key, instruction, payload, schema):
            assert schema is Plan and key == "plan:1"
            return Plan.model_validate(
                {
                    "title": "竞赛报名管理",
                    "data_scope": "shared",
                    "entities": [
                        {
                            "name": "registration",
                            "description": "报名记录",
                            "fields": [{"name": "title", "kind": "text", "max_length": 200}],
                        }
                    ],
                    "acceptance": ["管理员可维护报名记录"],
                }
            )

    def old_analyse(self, state):
        return {"requirement": requirement.gate_dump()}

    def old_requirements(self, state):
        return self.gate(
            state,
            "requirements",
            {"requirement": state["requirement"], "ready": True},
            ["approve", "revise", "reject"],
            True,
        )

    def old_import_failure(self, state):
        raise ModuleNotFoundError("No module named 'psycopg'", name="psycopg")

    try:
        project = store.create_project("旧版报名运行浏览器恢复验收", str(uuid.uuid4()))
        run = store.create_run(
            project["id"],
            {"requirement": ORIGINAL, "template": "fastapiadmin", "intelligent": True},
            str(uuid.uuid4()),
        )["run_id"]
        with (
            patch.object(Workflow, "analyse", old_analyse),
            patch.object(Workflow, "requirements", old_requirements),
            patch.object(Workflow, "source_context", lambda *_: {"code_context": {}}),
            patch.object(Workflow, "design", old_import_failure),
            patch.object(Workflow, "capability_recovery", lambda *a, **kw: None),
        ):
            with Runtime(settings, store, LegacyFixture()) as worker:
                assert worker.tick()
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
                assert snapshot.next == ("design",)
                assert pending_interrupt(snapshot) is None
        failed = store.get_run(run)
        assert failed["status"] == "FAILED" and failed["pending"] is None
        assert "ModuleNotFoundError" in failed["error"]
        with store.tx() as session:
            initial_approvals = list(
                session.scalars(
                    select(Approval)
                    .join(Revision, Revision.gate_id == Approval.gate_id)
                    .where(Revision.run_id == run)
                )
            )
        assert len(initial_approvals) == 1 and initial_approvals[0].actor == "delegated-ai"
        return run
    finally:
        store.engine.dispose()


def main():
    build_before = ui_snapshot()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    reports = ROOT / "reports/signup-scope-browser"
    reports.mkdir(parents=True, exist_ok=True)
    # A failed rerun must never leave a prior successful receipt/screenshot.
    for name in (
        "browser.log",
        "scope-blocked.png",
        "scope-blocked-mobile.png",
        "scope-options-mobile.png",
        "scope-corrected.png",
        "scope-failed.png",
    ):
        (reports / name).unlink(missing_ok=True)
    write_json(
        reports / "browser.json",
        {"passed": False, "status": "started", "fixture_mode": "in-process-requirement-gateway"},
    )
    fixture = ScopeFixture()
    with tempfile.TemporaryDirectory(prefix="signup-scope-browser-") as directory:
        directory = Path(directory)
        settings = Settings(
            data_dir=directory / "platform",
            base_url="http://127.0.0.1:1/v1",
            api_key="explicit-in-process-fixture-only",
            model="explicit-in-process-fixture",
            install_products=False,
            _env_file=None,
        )
        legacy_run_id = legacy_failed_run(settings)
        application = create_app(settings, gateway_factory=lambda _: fixture)
        server = uvicorn.Server(
            uvicorn.Config(application, host="127.0.0.1", port=port, log_level="error")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Local browser fixture did not start")
                time.sleep(0.05)
            inputs = directory / "input.json"
            write_json(
                inputs,
                {
                    "platform": f"http://127.0.0.1:{port}",
                    "token": application.state.token,
                    "reports": str(reports),
                    "original": ORIGINAL,
                    "admin_scope": ADMIN_SCOPE,
                    "authenticated_scope": AUTHENTICATED_SCOPE,
                    "legacy_run_id": legacy_run_id,
                },
            )
            browser = os.getenv(
                "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
            )
            result = subprocess.run(
                ["node", str(ROOT / "scripts/signup_scope_browser.cjs"), str(inputs), browser],
                cwd=ROOT,
                env=clean_env(
                    {"PLAYWRIGHT_BROWSERS_PATH": os.getenv("PLAYWRIGHT_BROWSERS_PATH", "0")}
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=90,
            )
            (reports / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
            assert result.returncode == 0, result.stdout + result.stderr
            evidence = json.loads((reports / "browser.json").read_text(encoding="utf-8"))
            run_id = evidence["run_id"]
            assert run_id == legacy_run_id
            run = application.state.store.get_run(run_id)
            assert run["status"] == "WAITING_REQUIREMENTS"
            assert run["pending"]["can_approve"] and not run["auto_mode"]
            assert len(fixture.calls) == 1
            with application.state.store.tx() as session:
                approval_rows = list(
                    session.scalars(
                        select(Approval)
                        .join(Revision, Revision.gate_id == Approval.gate_id)
                        .where(Revision.run_id == run_id)
                    )
                )
            assert len(approval_rows) == 1 and approval_rows[0].actor == "delegated-ai"
            messages = application.state.store.messages(run_id)
            assert len(messages) == 2 and messages[0]["content"] == ORIGINAL
            assert AUTHENTICATED_SCOPE in messages[1]["content"]
            assert ADMIN_SCOPE not in messages[1]["content"]
            assert not (settings.data_dir / "runs" / run_id / "product").exists()
            assert ui_snapshot() == build_before, "UI assets changed during browser verification"
            screenshot_names = (
                "scope-blocked.png",
                "scope-blocked-mobile.png",
                "scope-options-mobile.png",
                "scope-corrected.png",
            )
            assert set(evidence["screenshots"]) == set(screenshot_names)
            evidence.update(
                passed=True,
                fixture_model_calls=fixture.calls,
                same_run_id=True,
                original_request_preserved=True,
                no_default_scope_selection=True,
                discarded_admin_selection_not_submitted=True,
                authenticated_entrant_goal_preserved=True,
                native_generation_attempted=False,
                legacy_failed_import_checkpoint=True,
                original_approval_count=1,
                recovered_approval_count=len(approval_rows),
                fixture_mode="in-process-requirement-gateway",
                external_provider_calls=False,
                ui_bundle_sha256=build_before,
                screenshot_sha256={
                    name: hashlib.sha256((reports / name).read_bytes()).hexdigest()
                    for name in screenshot_names
                },
            )
            write_json(reports / "browser.json", evidence)
            print(json.dumps(evidence, ensure_ascii=False, indent=2))
        finally:
            server.should_exit = True
            thread.join(timeout=15)
            if thread.is_alive():
                raise RuntimeError("Local browser fixture did not stop")


if __name__ == "__main__":
    main()
