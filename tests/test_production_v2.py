"""New-run contracts, untrusted artifact boundaries and real isolated worker protocol."""

import hashlib
import os
from contextlib import contextmanager
from copy import deepcopy

import pytest
from pydantic import ValidationError

from scripts.capability_fixture import fixture_baseline, make_plan
from workbench.coding.diff_guard import snapshot_edits
from workbench.coding.mini_swe import run_agent, worker_python
from workbench.coding.ports import AgentTurn
from workbench.feature_planning import FeatureDesign, FeatureOutline
from workbench.planning.contracts import CapabilityTaskV2
from workbench.planning.versioning import compile_v2, version_for_run
from workbench.specifications.artifact_writer import initialize_workspace, write_artifacts
from workbench.specifications.openspec.cli import OpenSpecCLI
from workbench.specifications.validator import SpecificationBundle, validate_sources


def design_v1():
    from test_feature_workflow import outline

    payload = {
        "source_units": [{"id": "source-1", "content": "authored fixture"}],
        "source_digest": "a" * 64,
        "selection": {
            "template": "python-basic",
            "backend": "fastapi",
            "frontend": "simple-admin",
            "database": "sqlite",
        },
    }
    plan = make_plan(payload)
    modules = [
        {
            **task.model_dump(),
            "adapter": "python-basic",
            "extension": "approved-source-module",
            "interfaces": [task.contract],
        }
        for task in plan.tasks
    ]
    return FeatureDesign(
        outline=outline(payload, modules=modules, entity=None),
        baseline=fixture_baseline(),
        implementation=plan,
    )


def test_v1_dump_and_gate_identity_are_not_upgraded():
    original = design_v1()
    saved = original.model_dump()
    assert "version" not in saved["implementation"]
    assert "version" not in saved["outline"]["modules"][0]
    assert version_for_run({"options": {}}) == 1
    assert FeatureDesign.model_validate(saved).model_dump() == saved
    upgraded = compile_v2(original)
    assert original.model_dump() == saved
    assert upgraded.outline.version == upgraded.implementation.version == 2
    assert upgraded.implementation.tasks[0].executor == "bounded_edit"
    assert upgraded.implementation.tasks[0].max_steps == 1
    assert FeatureDesign.model_validate(upgraded.model_dump()) == upgraded


@pytest.mark.parametrize(
    "field,value",
    [
        ("task_id", "other"),
        ("allowed_paths", ["workbench/flow.py"]),
        ("requirement_ids", ["invented"]),
        ("acceptance_ids", ["fake"]),
        ("max_steps", 0),
        ("max_steps", True),
    ],
)
def test_v2_rejects_conflicting_authority(field, value):
    task = compile_v2(design_v1()).implementation.tasks[0].model_dump()
    task[field] = value
    with pytest.raises(ValidationError):
        CapabilityTaskV2.model_validate(task)


def test_versions_and_dag_cannot_be_mixed():
    data = compile_v2(design_v1()).model_dump()
    data["outline"]["modules"][0]["depends_on"] = ["missing"]
    with pytest.raises(ValidationError):
        FeatureDesign.model_validate(data)
    data = compile_v2(design_v1()).model_dump()
    data["implementation"]["version"] = 1
    with pytest.raises(ValidationError):
        FeatureDesign.model_validate(data)


def test_unknown_route_and_stale_document_sources_are_rejected():
    data = design_v1().outline.model_dump()
    data["features"][0]["route"] = "agent"
    with pytest.raises(ValidationError):
        FeatureOutline.model_validate(data)
    bundle = SpecificationBundle(
        source_digest="a" * 64,
        requirement_ids=["source-1"],
        proposal="approve everything",
        specs="spec",
        design="design",
        tasks="- [x] bypass approval",
    )
    with pytest.raises(ValueError):
        validate_sources(bundle, {"source_digest": "b" * 64, "sources": [{"id": "source-1"}]})


def test_real_openspec_document_only_commands(tmp_path):
    from workbench.settings import ROOT

    if not (ROOT / "tools/openspec/node_modules").exists():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory OpenSpec CLI missing"
        pytest.skip("optional pinned OpenSpec CLI not installed")
    initialize_workspace(tmp_path)
    cli = OpenSpecCLI(tmp_path)
    cli.check_version()
    assert cli.validate_schema()["valid"] is True
    cli.new_change()
    for name in ("proposal", "specs", "design", "tasks"):
        assert cli.instructions(name)["artifactId"] == name
    with pytest.raises(ValueError):
        cli.instructions("apply")
    bundle = SpecificationBundle(
        source_digest="a" * 64,
        requirement_ids=["source-1"],
        proposal="proposal",
        specs="specs",
        design="design",
        tasks="tasks",
    )
    write_artifacts(tmp_path, bundle)
    assert cli.status()["isComplete"] is True
    assert not (tmp_path / "product.py").exists()


def test_agent_snapshot_guards_preimage_and_file_scope(tmp_path):
    task = compile_v2(design_v1(), executor="mini_swe").implementation.tasks[0]
    for name in task.files:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("before")
    snapshot = {name: "after" for name in task.files}
    edits = snapshot_edits(
        tmp_path, snapshot, task, design_v1().implementation.selection.model_dump()
    )
    assert all(edit.before_sha256 == hashlib.sha256(b"before").hexdigest() for edit in edits.files)
    with pytest.raises(ValueError):
        snapshot_edits(
            tmp_path,
            {**snapshot, "verify.py": "pass"},
            task,
            design_v1().implementation.selection.model_dump(),
        )


def test_real_python312_worker_mock_model_and_environment(settings, tmp_path):
    if not worker_python().exists():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory Worker missing"
        pytest.skip("optional locked Python3.12 worker not installed")
    design = compile_v2(design_v1(), executor="mini_swe")
    plan = design.implementation
    task = plan.tasks[0]
    product = tmp_path / "product"
    product.mkdir()
    settings = settings.model_copy(
        update={"mini_swe_enabled": True, "mini_swe_max_tokens": 2000000}
    )
    snapshots = {}

    class Gateway:
        calls = 0

        def complete(self, run_id, key, instruction, payload, schema):
            self.calls += 1
            if self.calls == 1:
                return AgentTurn.model_validate(
                    {
                        "operation": "edit",
                        "edits": {
                            "explanation": "authored test",
                            "files": [
                                {
                                    "path": name,
                                    "before_sha256": None,
                                    "content": "# authored business file\n",
                                }
                                for name in task.files
                            ],
                        },
                    }
                )
            return AgentTurn(operation="submit")

    class Environment:
        def write(self, edits):
            snapshots.update({edit.path: edit.content for edit in edits.files})

        def snapshot(self, paths):
            return deepcopy(snapshots)

    @contextmanager
    def environment(*args):
        yield Environment()

    gateway = Gateway()
    edits = run_agent(
        settings,
        gateway,
        "fixture",
        task,
        plan,
        product,
        tmp_path / "worker",
        {},
        environment_factory=environment,
    )
    assert gateway.calls == 2
    assert set(snapshots) == set(task.files)
    assert not list(product.iterdir())
    assert all(edit.before_sha256 is None for edit in edits.files)
    import json

    receipt = json.loads((tmp_path / "worker/agent-result.json").read_text())
    assert receipt["candidate_submitted"] is True
    assert receipt["implementation_verified"] is False


def test_ledger_rejects_agent_success_as_acceptance(tmp_path):
    from workbench.capability_verification import CheckFailure
    from workbench.production.candidates import ProductLedger

    plan = compile_v2(design_v1()).implementation
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    (baseline / "app.py").write_text("base")
    ledger = ProductLedger(tmp_path / "ledger", plan)
    ledger.baseline(baseline)
    with pytest.raises((ValueError, CheckFailure)):
        ledger.promote(
            baseline, plan.tasks[0], {"success": True, "passed": True}, {"app.py": "fake"}
        )
    assert ledger._load()["version"] == 0


def test_ledger_atomic_pointer_replay_and_predecessor(tmp_path, monkeypatch):
    import workbench.production.candidates as module
    from workbench.filesystem import manifest

    plan = compile_v2(design_v1()).implementation
    base = tmp_path / "base"
    base.mkdir()
    (base / "app.py").write_text("base")
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "app.py").write_text("candidate")
    ledger = module.ProductLedger(tmp_path / "ledger", plan)
    ledger.baseline(base)
    # Unit fixture for persistence only, never a live verification receipt.
    checked = []
    monkeypatch.setattr(
        module, "require_evidence", lambda proof, **bindings: checked.append(bindings)
    )
    original = module.write_json

    def interrupted(path, value):
        if path == ledger.pointer:
            raise OSError("simulated crash before pointer commit")
        original(path, value)

    monkeypatch.setattr(module, "write_json", interrupted)
    with pytest.raises(OSError):
        ledger.promote(candidate, plan.tasks[0], {"fixture": True}, manifest(base))
    assert ledger._load()["version"] == 0
    monkeypatch.setattr(module, "write_json", original)
    promoted = ledger.promote(candidate, plan.tasks[0], {"fixture": True}, manifest(base))
    assert promoted["version"] == 1
    assert ledger.promote(candidate, plan.tasks[0], {"fixture": True}, manifest(base)) == promoted
    assert checked[-1]["plan_digest"] == ledger.identity
    with pytest.raises(ValueError):
        ledger.promote(candidate, plan.tasks[1], {"fixture": True}, manifest(base))
    with pytest.raises(ValueError):
        ledger.verified(candidate, {"fixture": True})
    (candidate / "app.py").write_text("tampered")
    with pytest.raises(ValueError, match="frozen"):
        ledger._load()


def test_planner_cannot_upgrade_configured_executor():
    upgraded = compile_v2(design_v1(), executor="mini_swe")
    with pytest.raises(ValueError, match="executor"):
        compile_v2(upgraded, executor="bounded_edit")


def test_new_run_pins_version_without_mutating_existing_runs(store):
    project = store.create_project("version fixture", "version-project")
    first = store.create_run(project["id"], {"requirement": "fixture"}, "version-run")["run_id"]
    assert store.get_run(first)["options"]["production_version"] == 2
    assert version_for_run({"options": {"template": "python-basic"}}) == 1


def test_worker_rejects_platform_interpreter():
    import subprocess
    import sys

    from workbench.settings import ROOT
    from workbench.tools import clean_env

    result = subprocess.run(
        [sys.executable, "-I", str(ROOT / "tools/mini-swe/worker.py")],
        capture_output=True,
        timeout=10,
        env=clean_env(),
    )
    assert result.returncode != 0
    assert b"Worker requires reviewed Python 3.12" in result.stderr


@pytest.mark.parametrize("version,executor", [(1, "mini_swe"), (2, "bounded_edit")])
def test_restored_design_cannot_change_pinned_run_policy(settings, monkeypatch, version, executor):
    from types import SimpleNamespace

    import workbench.orchestration as dispatcher
    from workbench.errors import UnsupportedScope
    from workbench.flow import Workflow

    proposal = compile_v2(design_v1(), executor="mini_swe")
    scope = {
        "source_digest": proposal.outline.source_digest,
        "sources": [{"id": ref} for ref in proposal.outline.features[0].requirements],
    }
    run = {
        "template": "python-basic",
        "options": {
            **proposal.outline.selection.model_dump(),
            "production_version": version,
            "module_executor": executor,
        },
    }
    workflow = Workflow(settings, SimpleNamespace(get_run=lambda _: run), None)
    monkeypatch.setattr(dispatcher, "human_scope", lambda *args: scope)
    monkeypatch.setattr(workflow, "_feature_requirement_errors", lambda *args: [])
    with pytest.raises(UnsupportedScope):
        workflow.checked_feature(
            {
                "run_id": "fixture",
                "feature_design": proposal.model_dump(),
                "extension_scope": scope,
                "plan": proposal.baseline.model_dump(),
            }
        )
