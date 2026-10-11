"""Authored module fixture with real Worker/API/ZIP/restart; no live-model claim."""

import json
import os
import subprocess
from contextlib import contextmanager

import pytest
from test_capability_consumer import extract_consumer, free_port, running_consumer

from scripts.sla_fixture import authored_files, design
from workbench.coding.candidates import apply_candidate
from workbench.coding.mini_swe import run_agent, worker_python
from workbench.coding.ports import AgentTurn
from workbench.core.contracts import digest
from workbench.filesystem import manifest
from workbench.generator import generate_basic


def fixture_product(settings, tmp_path):
    selected = design()
    base = tmp_path / "baseline"
    generate_basic(selected.baseline, base, selected.outline.selection.model_dump())
    frozen = manifest(base)
    product = base
    settings = settings.model_copy(
        update={"mini_swe_enabled": True, "mini_swe_max_tokens": 2000000}
    )
    for index, task in enumerate(selected.implementation.tasks, 1):

        class Gateway:
            calls = 0

            def complete(self, run_id, key, instruction, payload, schema):
                self.calls += 1
                if self.calls == 2:
                    return AgentTurn(operation="submit")
                source = authored_files(task, payload["context"]["app.py"]["content"])
                return AgentTurn.model_validate(
                    {
                        "operation": "edit",
                        "edits": {
                            "explanation": "audited authored fixture",
                            "files": [
                                {
                                    "path": name,
                                    "before_sha256": payload["context"][name]["sha256"],
                                    "content": source[name],
                                }
                                for name in task.files
                            ],
                        },
                    }
                )

        class Environment:
            contents = {}

            def write(self, edits):
                self.contents = {edit.path: edit.content for edit in edits.files}

            def snapshot(self, paths):
                return self.contents

        @contextmanager
        def environment(*args):
            yield Environment()

        edits = run_agent(
            settings,
            Gateway(),
            "sla-fixture",
            task,
            selected.implementation,
            product,
            tmp_path / f"worker-{index}",
            {},
            environment_factory=environment,
        )
        candidate = tmp_path / f"candidate-{index}"
        apply_candidate(product, edits, task, selected.outline.selection.model_dump(), candidate)
        product = candidate
    assert manifest(base) == frozen
    assert (product / "web/index.html").read_bytes() == (base / "web/index.html").read_bytes()
    return product


def test_authored_sla_worker_zip_api_restart(settings, tmp_path, monkeypatch):
    # Authored local fixture only; real checkpoint isolation is not asserted here.
    monkeypatch.setattr(
        "workbench.coding.mini_swe.check_candidate",
        lambda s, t, p, c, d: {"passed": True, "source_digest": digest(manifest(c))},
    )
    if not worker_python().exists():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory Worker missing"
        pytest.skip("locked optional mini-SWE worker not installed")
    product = fixture_product(settings, tmp_path)
    clean = extract_consumer(product, tmp_path)
    port = free_port()
    with running_consumer(clean, tmp_path, port, extra_args=("--port", str(port))) as client:
        assert client.get("/").status_code == 200
        registered = client.post(
            "/auth/register", json={"username": "owner", "password": "authored-fixture-password"}
        )
        assert registered.status_code == 201
        token = registered.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        assert (
            client.post("/api/customers", headers=headers, json={"name": "客户A"}).status_code
            == 201
        )
        for title, due, status, priority in [
            ("逾期紧急", "2000-01-01T00:00:00Z", "open", "urgent"),
            ("已解决", "2000-01-01T00:00:00Z", "resolved", "urgent"),
            ("未来", "2099-01-01T00:00:00Z", "open", "normal"),
        ]:
            result = client.post(
                "/api/tickets",
                headers=headers,
                json={
                    "title": title,
                    "customer": "客户A",
                    "due_at": due,
                    "status": status,
                    "priority": priority,
                },
            )
            assert result.status_code == 201, result.text
        assert client.get("/sla/summary", headers=headers).json() == {
            "overdue": 1,
            "urgent_overdue": 1,
        }
        assert client.get("/sla/summary").status_code == 401
        stranger = client.post(
            "/auth/register", json={"username": "outsider", "password": "authored-fixture-password"}
        ).json()["access_token"]
        assert client.get(
            "/sla/summary", headers={"Authorization": "Bearer " + stranger}
        ).json() == {"overdue": 0, "urgent_overdue": 0}
        assert client.get("/sla-dashboard").status_code == 200
        browser = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
        if browser:
            script = """const {chromium}=require(process.argv[1]);(async()=>{const b=await chromium.launch({headless:true,args:['--no-sandbox']});try{const p=await b.newPage();await p.goto(process.argv[2]+'/sla-dashboard');await p.fill('#username','owner');await p.fill('#password','authored-fixture-password');await p.click('#login');await p.waitForFunction(()=>document.querySelector('#result').textContent==='逾期 1；紧急逾期 1');}finally{await b.close();}})().catch(()=>process.exit(1));"""
            # Synthetic fixture token only, never a model/provider credential.
            run = subprocess.run(
                ["node", "-e", script, browser, f"http://127.0.0.1:{port}", token],
                capture_output=True,
                timeout=30,
            )
            assert run.returncode == 0, "authored browser fixture failed"
    with running_consumer(clean, tmp_path, port, extra_args=("--port", str(port))) as client:
        assert client.get("/sla/summary", headers=headers).json() == {
            "overdue": 1,
            "urgent_overdue": 1,
        }
    (tmp_path / "fixture-evidence.json").write_text(
        json.dumps(
            {
                "authored_fixture": True,
                "real_worker": True,
                "model": "mock",
                "daytona": "mock",
                "api": True,
                "restart": True,
                "zip_new_directory": True,
                "browser": bool(browser),
                "real_model_acceptance": False,
            }
        )
    )
