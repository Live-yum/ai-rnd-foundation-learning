# tests/test_source_candidate_workflow.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_source_candidate_workflow_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generation.python_basic`、`workbench.production.graph`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_source_edit_derivation_is_bound_and_replay_safe`（L821–L1009）：接收`settings`、`plan`、`monkeypatch`、`failed_runtime`、`scenario`。 控制顺序：L840按`failed_runtime`分支；L928按`scenario == "after-apply"`分支；L935按`scenario == "after-derive"`分支；L942按`scenario == "during-derive"`分支；L949按`scenario == "source-tamper"`分支；L951按`scenario == "sidecar-tamper"`分支；L959按`scenario in {"source-tamper", "during-model-tamper", "sidecar-tamper"}`分支；L962断言`len(calls) == (1 if scenario == "during-model-tamper" else 0)`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`target.parent.mkdir`、`target.write_text`、`plan.model_copy`、`write_json`、`manifest`、`source_candidate.retain_failed_candidate`、`source_candidate.refresh_candidate`、`digest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.FixtureGateway`（L902–L907）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_edit_derivation_is_bound_and_replay_safe.FixtureGateway.complete`（L903–L907）：接收`*args`。 控制顺序：L905按`scenario == "during-model-tamper"`分支。 调用`calls.append`、`target.write_text`。 返回路径：L907的`edits`。
- `test_source_edit_derivation_is_bound_and_replay_safe.SimulatedCrash`（L922–L923）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_apply`（L930–L932）：接收`*args`、`**kwargs`。 控制顺序：L932抛异常，停止当前正常路径。 调用`apply`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_derive`（L937–L939）：接收`*args`、`**kwargs`。 控制顺序：L939抛异常，停止当前正常路径。 调用`derive`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_refresh`（L944–L946）：接收`*args`、`**kwargs`。 控制顺序：L946抛异常，停止当前正常路径。 调用`refresh`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_candidate_workflow.py`；**本文件共有 2 段**。本段覆盖源文件 L804–L1009。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7791`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_workflow.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "b4c436cd35dc59fc967c345fb1402c22a85e7dc8914d6a693be0e20585be1fc8"} -->
````python
# tests/test_source_candidate_workflow.py
@pytest.mark.parametrize("failed_runtime", [False, True])
@pytest.mark.parametrize(
    "scenario",
    [
        "fresh",
        "replay",
        "after-apply",
        "after-derive",
        "during-derive",
        "source-tamper",
        "during-model-tamper",
        "raw-tamper",
        "raw-receipt-tamper",
        "derived-tamper",
        "sidecar-tamper",
    ],
)
def test_source_edit_derivation_is_bound_and_replay_safe(
    settings, plan, monkeypatch, failed_runtime, scenario
):
    from pathlib import Path

    from workbench.core.contracts import digest
    from workbench.delivery import source_candidate
    from workbench.filesystem import manifest, sha, write_json
    from workbench.planning.contracts import CapabilityEdits, CapabilityTask
    from workbench.production import dispatcher

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})
    root = settings.data_dir / "runs" / "source-state-machine"
    product = root / "baseline" / "product"
    filename = "backend/app/plugin/demo/service.py"
    target = product / filename
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    native_plan = plan.model_copy(update={"data_scope": "shared"})
    if failed_runtime:
        write_json(
            product.parent / "native-evidence/recovery.json",
            {
                "files": manifest(product),
                "stage": "validation-interrupted",
                "targets": {"demo": {}},
            },
        )
        receipt = source_candidate.retain_failed_candidate(
            "fastapiadmin", native_plan, product, [], "TestRuntimeFailure"
        )
    else:
        receipt = source_candidate.refresh_candidate(
            product,
            {
                "template": "fastapiadmin",
                "execution": "source-candidate",
                "spec_digest": digest(native_plan.model_dump()),
                "generation_status": "partial",
                "verification_status": "unverified",
                "pending_steps": ["Implement module task: draft"],
                "runtime_unavailable_reason": "Test missing runtime",
            },
        )
    original = manifest(product)
    sidecars = {
        path: path.read_bytes()
        for path in (
            product.parent / "source-candidate-status.json",
            product.parent / "native-evidence/recovery.json",
            product.parent / "native-generation.json",
        )
        if path.is_file()
    }
    task = CapabilityTask(
        id="draft",
        title="demo",
        requirements=["req"],
        files=[filename],
        contract="Update demo value",
        scenarios=["check"],
    )
    edits = CapabilityEdits(
        explanation="Test bounded edit",
        files=[
            {
                "path": filename,
                "before_sha256": sha(target),
                "content": "VALUE = 2\n",
            }
        ],
    )
    selection = SimpleNamespace(
        template="fastapiadmin", model_dump=lambda: {"template": "fastapiadmin"}
    )
    design = SimpleNamespace(
        implementation=SimpleNamespace(tasks=[task], selection=selection),
        model_dump=lambda: {"tasks": [task.model_dump()]},
    )
    calls = []

    class FixtureGateway:
        def complete(self, *args):
            calls.append("model-fixture")
            if scenario == "during-model-tamper":
                target.write_text("VALUE = 999\n", encoding="utf-8")
            return edits

    flow = Workflow(settings, SimpleNamespace(record_event=lambda *args: None), FixtureGateway())
    flow.checked_extension = lambda state: design
    state = {
        "run_id": "source-state-machine",
        "round": 1,
        "extension_policy": {},
        "extension_scope": {"sources": []},
        "extension_product": str(product),
        "native_generation": receipt,
        "extension_drafted": [],
        "extension_completed": [],
    }

    class SimulatedCrash(RuntimeError):
        pass

    derive = source_candidate.derive_candidate
    apply = dispatcher.apply_candidate
    refresh = source_candidate.refresh_candidate
    if scenario == "after-apply":

        def crashed_apply(*args, **kwargs):
            apply(*args, **kwargs)
            raise SimulatedCrash

        monkeypatch.setattr(dispatcher, "apply_candidate", crashed_apply)
    elif scenario == "after-derive":

        def crashed_derive(*args, **kwargs):
            derive(*args, **kwargs)
            raise SimulatedCrash

        monkeypatch.setattr(source_candidate, "derive_candidate", crashed_derive)
    elif scenario == "during-derive":

        def crashed_refresh(*args, **kwargs):
            refresh(*args, **kwargs)
            raise SimulatedCrash

        monkeypatch.setattr(source_candidate, "refresh_candidate", crashed_refresh)
    elif scenario == "source-tamper":
        target.write_text("VALUE = 999\n", encoding="utf-8")
    elif scenario == "sidecar-tamper":
        status = (
            product.parent / "source-candidate-status.json"
            if failed_runtime
            else product / "SOURCE-STATUS.json"
        )
        status.write_text("{}", encoding="utf-8")

    if scenario in {"source-tamper", "during-model-tamper", "sidecar-tamper"}:
        with pytest.raises(PrerequisiteError):
            flow.extension_code(state)
        assert len(calls) == (1 if scenario == "during-model-tamper" else 0)
        assert not list(root.glob("candidates/**/source-edits.json"))
        return
    if scenario in {"after-apply", "after-derive", "during-derive"}:
        with pytest.raises(SimulatedCrash):
            flow.extension_code(state)
        monkeypatch.setattr(dispatcher, "apply_candidate", apply)
        monkeypatch.setattr(source_candidate, "derive_candidate", derive)
        monkeypatch.setattr(source_candidate, "refresh_candidate", refresh)
    else:
        first = flow.extension_code(state)
        assert not first.get("extension_error"), first
        if scenario in {"raw-tamper", "raw-receipt-tamper", "derived-tamper"}:
            derived = Path(first["extension_product"])
            changed = (
                derived.parent.parent / "product"
                if scenario in {"raw-tamper", "raw-receipt-tamper"}
                else derived
            )
            (changed / filename).write_text("VALUE = 999\n", encoding="utf-8")
            if scenario == "raw-receipt-tamper":
                import json

                edit_path = changed.parent / "product-edit.json"
                changed_receipt = json.loads(edit_path.read_text(encoding="utf-8"))
                changed_receipt["files"] = manifest(changed)
                write_json(edit_path, changed_receipt)
            with pytest.raises(PrerequisiteError):
                flow.extension_code(state)
            assert len(calls) == 1
            return
    result = flow.extension_code(state)
    assert len(calls) == 1
    derived = Path(result["extension_product"])
    assert derived != product
    assert (derived / filename).read_text(encoding="utf-8") == "VALUE = 2\n"
    assert result["extension_drafted"] == ["draft"]
    assert result["extension_candidate_passed"] is False
    assert not result["native_generation"].get("preserve_runtime_files")
    assert result["native_generation"]["verification_status"] == (
        "failed" if failed_runtime else "unverified"
    )
    source_candidate.verify_candidate(derived, result["native_generation"])
    assert manifest(product) == original
    for path, content in sidecars.items():
        assert path.read_bytes() == content
    assert not (derived.parent / "native-evidence/recovery.json").exists()
    assert state["extension_completed"] == []
````
