# tests/test_production_v2.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.coding.diff_guard`、`workbench.coding.mini_swe`、`workbench.coding.ports`、`workbench.feature_planning`、`workbench.planning.contracts`、`workbench.planning.versioning`、`workbench.specifications.artifact_writer`、`workbench.specifications.openspec.cli`、`workbench.specifications.validator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `design_v1`（L23–L50）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`make_plan`、`task.model_dump`、`FeatureDesign`、`outline`、`fixture_baseline`。 返回路径：L46的`FeatureDesign( outline=outline(payload, modules=modules, entity=None), baseline=fixture_ba…`。
- `test_v1_dump_and_gate_identity_are_not_upgraded`（L53–L65）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L56断言`"version" not in saved["implementation"]`；L57断言`"version" not in saved["outline"]["modules"][0]`；L58断言`version_for_run({"options": {}}) == 1`；L59断言`FeatureDesign.model_validate(saved).model_dump() == saved`；L61断言`original.model_dump() == saved`；L62断言`upgraded.outline.version == upgraded.implementation.version == 2`；L63断言`upgraded.implementation.tasks[0].executor == "bounded_edit"`；L64断言`upgraded.implementation.tasks[0].max_steps == 1`。后续分支沿下方源码相同行号继续阅读。 调用`design_v1`、`original.model_dump`、`version_for_run`、`FeatureDesign.model_validate(saved).model_dump`、`FeatureDesign.model_validate`、`compile_v2`、`upgraded.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_v2_rejects_conflicting_authority`（L79–L83）：接收`field`、`value`。 调用`compile_v2(design_v1()).implementation.tasks[0].model_dump`、`compile_v2`、`design_v1`、`pytest.raises`、`CapabilityTaskV2.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_versions_and_dag_cannot_be_mixed`（L86–L94）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`compile_v2(design_v1()).model_dump`、`compile_v2`、`design_v1`、`pytest.raises`、`FeatureDesign.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_route_and_stale_document_sources_are_rejected`（L97–L111）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`design_v1().outline.model_dump`、`design_v1`、`pytest.raises`、`FeatureOutline.model_validate`、`SpecificationBundle`、`validate_sources`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_openspec_document_only_commands`（L114–L139）：接收`tmp_path`。 控制顺序：L117按`not (ROOT / "tools/openspec/node_modules").exists()`分支；L118断言`not os.environ.get("RND_REQUIRE_V2_TOOLS")`；L123断言`cli.validate_schema()["valid"] is True`；L125遍历`("proposal", "specs", "design", "tasks")`；L126断言`cli.instructions(name)["artifactId"] == name`；L138断言`cli.status()["isComplete"] is True`；L139断言`not (tmp_path / "product.py").exists()`。 调用`(ROOT / "tools/openspec/node_modules").exists`、`os.environ.get`、`pytest.skip`、`initialize_workspace`、`OpenSpecCLI`、`cli.check_version`、`cli.validate_schema`、`cli.new_change`、`cli.instructions`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_agent_snapshot_guards_preimage_and_file_scope`（L142–L159）：接收`tmp_path`。 控制顺序：L144遍历`task.files`；L152断言`all(edit.before_sha256 == hashlib.sha256(b"before").hexdigest() for edit in edits.fil…`。 调用`compile_v2`、`design_v1`、`path.parent.mkdir`、`path.write_text`、`snapshot_edits`、`design_v1().implementation.selection.model_dump`、`all`、`hashlib.sha256(b"before").hexdigest`、`hashlib.sha256`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_python312_worker_mock_model_and_environment`（L162–L231）：接收`settings`、`tmp_path`。 控制顺序：L163按`not worker_python().exists()`分支；L164断言`not os.environ.get("RND_REQUIRE_V2_TOOLS")`；L223断言`gateway.calls == 2`；L224断言`set(snapshots) == set(task.files)`；L225断言`not list(product.iterdir())`；L226断言`all(edit.before_sha256 is None for edit in edits.files)`；L230断言`receipt["candidate_submitted"] is True`；L231断言`receipt["implementation_verified"] is False`。 调用`worker_python().exists`、`worker_python`、`os.environ.get`、`pytest.skip`、`compile_v2`、`design_v1`、`product.mkdir`、`settings.model_copy`、`Gateway`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_python312_worker_mock_model_and_environment.Gateway`（L176–L198）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_python312_worker_mock_model_and_environment.Gateway.complete`（L179–L198）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L181按`self.calls == 1`分支。 调用`AgentTurn.model_validate`、`AgentTurn`。 返回路径：L182的`AgentTurn.model_validate( { "operation": "edit", "edits": { "explanation": "authored test"…`；L198的`AgentTurn(operation="submit")`。
- `test_real_python312_worker_mock_model_and_environment.Environment`（L200–L205）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_python312_worker_mock_model_and_environment.Environment.write`（L201–L202）：接收`edits`。 调用`snapshots.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_python312_worker_mock_model_and_environment.Environment.snapshot`（L204–L205）：接收`paths`。 调用`deepcopy`。 返回路径：L205的`deepcopy(snapshots)`。
- `test_real_python312_worker_mock_model_and_environment.environment`（L208–L209）：接收`*args`。 调用`Environment`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_ledger_rejects_agent_success_as_acceptance`（L234–L248）：接收`tmp_path`。 控制顺序：L248断言`ledger._load()["version"] == 0`。 调用`compile_v2`、`design_v1`、`baseline.mkdir`、`(baseline / "app.py").write_text`、`ProductLedger`、`ledger.baseline`、`pytest.raises`、`ledger.promote`、`ledger._load`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ledger_atomic_pointer_replay_and_predecessor`（L251–L291）：接收`tmp_path`、`monkeypatch`。 控制顺序：L279断言`ledger._load()["version"] == 0`；L282断言`promoted["version"] == 1`；L283断言`ledger.promote(candidate, plan.tasks[0], {"fixture": True}, manifest(base)) == promot…`；L284断言`checked[-1]["plan_digest"] == ledger.identity`。 调用`compile_v2`、`design_v1`、`base.mkdir`、`(base / "app.py").write_text`、`candidate.mkdir`、`(candidate / "app.py").write_text`、`module.ProductLedger`、`ledger.baseline`、`monkeypatch.setattr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ledger_atomic_pointer_replay_and_predecessor.interrupted`（L271–L274）：接收`path`、`value`。 控制顺序：L272按`path == ledger.pointer`分支；L273抛异常，停止当前正常路径。 调用`OSError`、`original`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_planner_cannot_upgrade_configured_executor`（L294–L297）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`compile_v2`、`design_v1`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_run_pins_version_without_mutating_existing_runs`（L300–L304）：接收`store`。 控制顺序：L303断言`store.get_run(first)["options"]["production_version"] == 2`；L304断言`version_for_run({"options": {"template": "python-basic"}}) == 1`。 调用`store.create_project`、`store.create_run`、`store.get_run`、`version_for_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_rejects_platform_interpreter`（L307–L321）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L320断言`result.returncode != 0`；L321断言`b"Worker requires reviewed Python 3.12" in result.stderr`。 调用`subprocess.run`、`str`、`clean_env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restored_design_cannot_change_pinned_run_policy`（L325–L356）：接收`settings`、`monkeypatch`、`version`、`executor`。 调用`compile_v2`、`design_v1`、`proposal.outline.selection.model_dump`、`Workflow`、`SimpleNamespace`、`monkeypatch.setattr`、`pytest.raises`、`workflow.checked_feature`、`proposal.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_requires_an_explicit_output_token_limit`（L359–L395）：接收`settings`、`tmp_path`、`monkeypatch`。 调用`settings.model_copy`、`monkeypatch.setattr`、`type(tmp_path)`、`type`、`ModelGateway`、`httpx.MockTransport`、`compile_v2`、`design_v1`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_gateway_requires_an_explicit_output_token_limit.forbidden_request`（L380–L381）：接收`request`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_echo_preserves_context_and_candidate_bytes`（L401–L471）：接收`settings`、`tmp_path`、`original`。 控制顺序：L405按`not worker_python().is_file()`分支；L411遍历`task.files`；L470遍历`task.files`；L471断言`(candidate / name).read_bytes() == (product / name).read_bytes() == original`。 调用`worker_python().is_file`、`worker_python`、`pytest.skip`、`compile_v2`、`design_v1`、`product.mkdir`、`(product / name).parent.mkdir`、`(product / name).write_bytes`、`settings.model_copy`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.Gateway`（L416–L441）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.Gateway.complete`（L419–L441）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L421遍历`payload["context"].items()`；L422断言`value["content"].encode("utf-8") == original`；L423断言`value["sha256"] == sha(product / name)`；L424按`self.calls == 2`分支。 调用`payload["context"].items`、`value["content"].encode`、`sha`、`schema`、`schema.model_validate`。 返回路径：L425的`schema(operation="submit")`；L426的`schema.model_validate( { "operation": "edit", "edits": { "explanation": "offline unchanged…`。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.Environment`（L443–L448）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.Environment.write`（L444–L445）：接收`edits`。 调用`snapshots.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.Environment.snapshot`（L447–L448）：接收`paths`。 调用`dict`。 返回路径：L448的`dict(snapshots)`。
- `test_real_worker_echo_preserves_context_and_candidate_bytes.environment`（L451–L452）：接收`*args`。 调用`Environment`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `tests/test_production_v2.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L471。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16891`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_production_v2.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3f5b7f7521ad200efd3b4fe80eac4a98cc1c4c27d371d93a6f6d9a4425fab608"} -->
````python
# tests/test_production_v2.py
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
def test_real_worker_echo_preserves_context_and_candidate_bytes(settings, tmp_path, original):
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
````
