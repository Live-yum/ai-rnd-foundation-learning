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
from workbench.core.contracts import digest
from workbench.feature_planning import FeatureDesign, FeatureOutline
from workbench.filesystem import manifest
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


@pytest.mark.parametrize("executor", ["mini_swe", "bounded_edit"])
@pytest.mark.parametrize("unavailable", ["build_index", "repo_map", "query"])
def test_dispatcher_only_prepares_retrieval_for_the_executor_using_it(
    settings, tmp_path, monkeypatch, executor, unavailable
):
    from types import SimpleNamespace

    from workbench.production.dispatcher import ExtensionWorkflow

    selected = compile_v2(design_v1(), executor=executor)
    task = selected.implementation.tasks[0]
    product = tmp_path / "product"
    product.mkdir()
    calls = []

    class AgentReached(Exception):
        pass

    def prepare(name, result):
        def invoke(*args, **kwargs):
            calls.append(name)
            if name == unavailable:
                raise RuntimeError("optional retrieval unavailable")
            return result

        return invoke

    monkeypatch.setattr("workbench.knowledge.build_index", prepare("build_index", None))
    monkeypatch.setattr("workbench.aider_tool.repo_map", prepare("repo_map", "fixture map"))
    monkeypatch.setattr("workbench.retrieval.query", prepare("query", []))

    def agent(*args):
        assert args[3] == task and args[4] == selected.implementation
        assert args[5] == product
        assert args[7]["source_units"] == [{"id": "source-1"}]
        raise AgentReached

    monkeypatch.setattr("workbench.coding.mini_swe.run_agent", agent)
    workflow = SimpleNamespace(
        settings=settings.model_copy(update={"repo_map_provider": "aider"}),
        gateway=None,
        checked_extension=lambda state: selected,
        extension_task=lambda state, design: task,
    )
    state = {
        "extension_product": str(product),
        "extension_scope": {"sources": [{"id": "source-1"}]},
        "extension_policy": {},
        "run_id": "offline-dispatch",
        "round": 1,
    }
    if executor == "mini_swe":
        with pytest.raises(AgentReached):
            ExtensionWorkflow.extension_code(workflow, state)
        assert calls == []
    else:
        with pytest.raises(RuntimeError, match="optional retrieval unavailable"):
            ExtensionWorkflow.extension_code(workflow, state)
        assert calls[-1] == unavailable


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
        ("allowed_paths", ["workbench/production/graph.py"]),
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


def test_real_python312_worker_mock_model_and_environment(settings, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "workbench.coding.mini_swe.check_candidate",
        lambda s, t, p, c, d: {"passed": True, "source_digest": digest(manifest(c))},
    )
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


def test_real_gateway_requires_an_explicit_output_token_limit(settings, tmp_path, monkeypatch):
    import sys

    import httpx

    import workbench.coding.mini_swe as controller
    from workbench.errors import UnsupportedScope
    from workbench.llm import ModelGateway

    settings = settings.model_copy(
        update={
            "mini_swe_enabled": True,
            "mini_swe_usd_per_million_tokens": 1,
            "base_url": "https://fixture.invalid/v1",
            "model": "fixture",
            "max_output_tokens": None,
            "coding_max_output_tokens": None,
        }
    )
    monkeypatch.setattr(controller, "worker_python", lambda: type(tmp_path)(sys.executable))

    def forbidden_request(request):
        pytest.fail("unbounded request must not reach the model transport")

    gateway = ModelGateway(settings, None, httpx.MockTransport(forbidden_request))
    selected = compile_v2(design_v1(), executor="mini_swe")
    with pytest.raises(UnsupportedScope, match="max_output_tokens"):
        run_agent(
            settings,
            gateway,
            "fixture",
            selected.implementation.tasks[0],
            selected.implementation,
            tmp_path,
            tmp_path / "worker",
            {},
        )


@pytest.mark.parametrize(
    "original", [b"# preserved\n", b"# preserved\r\n", b"# first\r\n# second\n"]
)
def test_real_worker_echo_preserves_context_and_candidate_bytes(
    settings, tmp_path, original, monkeypatch
):
    monkeypatch.setattr(
        "workbench.coding.mini_swe.check_candidate",
        lambda s, t, p, c, d: {"passed": True, "source_digest": digest(manifest(c))},
    )
    from workbench.coding.candidates import apply_candidate
    from workbench.filesystem import sha

    if not worker_python().is_file():
        pytest.skip("optional locked Python3.12 worker not installed")
    plan = compile_v2(design_v1(), executor="mini_swe").implementation
    task = plan.tasks[0]
    product = tmp_path / "product"
    product.mkdir()
    for name in task.files:
        (product / name).parent.mkdir(parents=True, exist_ok=True)
        (product / name).write_bytes(original)
    snapshots = {}

    class Gateway:
        calls = 0

        def complete(self, run_id, key, instruction, payload, schema):
            self.calls += 1
            for name, value in payload["context"].items():
                assert value["content"].encode("utf-8") == original
                assert value["sha256"] == sha(product / name)
            if self.calls == 2:
                return schema(operation="submit")
            return schema.model_validate(
                {
                    "operation": "edit",
                    "edits": {
                        "explanation": "offline unchanged echo",
                        "files": [
                            {
                                "path": name,
                                "content": value["content"],
                                "before_sha256": value["sha256"],
                            }
                            for name, value in payload["context"].items()
                        ],
                    },
                }
            )

    class Environment:
        def write(self, edits):
            snapshots.update({edit.path: edit.content for edit in edits.files})

        def snapshot(self, paths):
            return dict(snapshots)

    @contextmanager
    def environment(*args):
        yield Environment()

    settings = settings.model_copy(
        update={"mini_swe_enabled": True, "mini_swe_max_tokens": 2000000}
    )
    edits = run_agent(
        settings,
        Gateway(),
        "offline",
        task,
        plan,
        product,
        tmp_path / "worker",
        {},
        environment_factory=environment,
    )
    candidate = tmp_path / "candidate"
    apply_candidate(product, edits, task, plan.selection.model_dump(), candidate)
    for name in task.files:
        assert (candidate / name).read_bytes() == (product / name).read_bytes() == original
