# tests/test_source_candidate_workflow.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_source_candidate_workflow_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.generation.python_basic`、`workbench.production.graph`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_source_edit_derivation_is_bound_and_replay_safe`（L873–L1084）：接收`settings`、`plan`、`monkeypatch`、`failed_runtime`、`scenario`。 控制顺序：L892按`failed_runtime`分支；L980按`scenario == "after-apply"`分支；L987按`scenario == "after-derive"`分支；L994按`scenario == "during-derive"`分支；L1001按`scenario == "source-tamper"`分支；L1003按`scenario == "sidecar-tamper"`分支；L1011按`scenario in {"source-tamper", "during-model-tamper", "sidecar-tamper"}`分支；L1014断言`len(calls) == (1 if scenario == "during-model-tamper" else 0)`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`target.parent.mkdir`、`target.write_text`、`plan.model_copy`、`write_json`、`manifest`、`source_candidate.retain_failed_candidate`、`source_candidate.refresh_candidate`、`digest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.FixtureGateway`（L954–L959）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_edit_derivation_is_bound_and_replay_safe.FixtureGateway.complete`（L955–L959）：接收`*args`。 控制顺序：L957按`scenario == "during-model-tamper"`分支。 调用`calls.append`、`target.write_text`。 返回路径：L959的`edits`。
- `test_source_edit_derivation_is_bound_and_replay_safe.SimulatedCrash`（L974–L975）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_apply`（L982–L984）：接收`*args`、`**kwargs`。 控制顺序：L984抛异常，停止当前正常路径。 调用`apply`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_derive`（L989–L991）：接收`*args`、`**kwargs`。 控制顺序：L991抛异常，停止当前正常路径。 调用`derive`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_edit_derivation_is_bound_and_replay_safe.crashed_refresh`（L996–L998）：接收`*args`、`**kwargs`。 控制顺序：L998抛异常，停止当前正常路径。 调用`refresh`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_main_workflow_binds_native_checkpoint`（L1090–L1159）：接收`settings`、`plan`、`monkeypatch`、`origin`、`stage`、`attack`。 控制顺序：L1106按`origin == "failed-runtime"`分支；L1137按`attack in {"tree", "tree-and-receipt"}`分支；L1139按`attack == "tree-and-receipt"`分支；L1143按`attack == "receipt-only"`分支；L1147按`stage == "generate-cached"`分支；L1150按`attack`分支；L1153断言`not (product.parent / "native-source.zip").exists()`；L1155遍历`range(2)`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`plan.model_copy`、`Workflow`、`plan.model_dump`、`flow.product`、`product.mkdir`、`(product / "example.py").write_text`、`write_json`、`manifest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extension_generation_cache_binds_native_evidence`（L1163–L1215）：接收`settings`、`plan`、`monkeypatch`、`attack`。 控制顺序：L1193按`attack == "tree-and-receipt"`分支；L1198按`attack == "git"`分支；L1202按`attack == "status"`分支；L1208按`attack`分支；L1212遍历`range(2)`；L1214断言`result["native_generation"] == receipt`；L1215断言`result["extension_product"] == str(product)`。 调用`monkeypatch.setattr`、`plan.model_copy`、`SimpleNamespace`、`plan.model_dump`、`digest`、`design.model_dump`、`product.mkdir`、`(product / "example.py").write_text`、`source_candidate.refresh_candidate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_candidate_workflow.py`；**本文件共有 2 段**。本段覆盖源文件 L854–L1215。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14783`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_workflow.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "7c6b9edb2bd9ae49d7657eddd86066582839004211a2e90fffbba82820ca74a1"} -->
````python
# tests/test_source_candidate_workflow.py
@pytest.mark.parametrize("failed_runtime", [False, True])
@pytest.mark.parametrize(
    "scenario",
    [
        "fresh",
        "package-replay",
        "package-tamper",
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

    if scenario in {"package-replay", "package-tamper"}:
        package_state = {**state, **result}
        design.baseline = plan
        design.implementation.model_dump = lambda: {"tasks": [task.model_dump()]}
        bound_files = manifest(derived)
        receipt_path = derived.parent / "native-generation.json"
        bound_receipt = receipt_path.read_bytes()
        if scenario == "package-tamper":
            (derived / filename).write_text("VALUE = 999\n", encoding="utf-8")
            source_candidate.refresh_candidate(
                derived,
                {**result["native_generation"], "source_commit": {"status": "unavailable"}},
            )
            with pytest.raises(PrerequisiteError, match="批准状态"):
                flow.extension_package(package_state)
        else:
            for _ in range(2):
                delivered = flow.extension_package(package_state)["delivery"]
                assert delivered["acceptance_passed"] is False
                assert "Run isolated module and aggregate acceptance" in delivered["pending_steps"]
                assert manifest(derived) == bound_files
                assert receipt_path.read_bytes() == bound_receipt


@pytest.mark.parametrize("origin", ["ordinary", "failed-runtime"])
@pytest.mark.parametrize("stage", ["verify", "package", "generate-cached", "generate-state"])
@pytest.mark.parametrize("attack", [None, "tree", "tree-and-receipt", "receipt-only"])
def test_main_workflow_binds_native_checkpoint(settings, plan, monkeypatch, origin, stage, attack):
    from workbench.delivery import source_candidate
    from workbench.filesystem import manifest, write_json

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})
    plan = plan.model_copy(update={"data_scope": "shared"})
    flow = Workflow(settings, None, None)
    state = {
        "run_id": "main-native-binding",
        "template": "fastapiadmin",
        "plan": plan.model_dump(),
        "attempt": 0,
    }
    product = flow.product(state)
    product.mkdir(parents=True)
    (product / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    if origin == "failed-runtime":
        write_json(
            product.parent / "native-evidence/recovery.json",
            {
                "files": manifest(product),
                "stage": "validation-interrupted",
                "targets": {"demo": {}},
            },
        )
        receipt = source_candidate.retain_failed_candidate(
            "fastapiadmin", plan, product, [], "FixtureFailure"
        )
    else:
        receipt = source_candidate.refresh_candidate(
            product,
            {
                "execution": "source-candidate",
                "template": "fastapiadmin",
                "spec_digest": digest(plan.model_dump()),
                "generation_status": "complete",
                "verification_status": "unverified",
                "pending_steps": [],
                "runtime_unavailable_reason": "Fixture unavailable",
            },
        )
    state["native_generation"] = receipt
    state["verification"] = flow.verify(state)["verification"]
    original = manifest(product)
    saved = product.parent / "native-generation.json"
    approved_bytes = saved.read_bytes()
    flow.store = SimpleNamespace(step=lambda run, key, action: receipt)
    if attack in {"tree", "tree-and-receipt"}:
        (product / "example.py").write_text("VALUE = 999\n", encoding="utf-8")
    if attack == "tree-and-receipt":
        source_candidate.refresh_candidate(
            product, {**receipt, "source_commit": {"status": "unavailable"}}
        )
    elif attack == "receipt-only":
        write_json(
            saved, {**receipt, "source_commit": {"status": "unavailable", "note": "changed"}}
        )
    if stage == "generate-cached":
        del state["native_generation"]  # Crash after Store.step, before graph checkpoint.
    operation = flow.generate if stage.startswith("generate-") else getattr(flow, stage)
    if attack:
        with pytest.raises(PrerequisiteError):
            operation(state)
        assert not (product.parent / "native-source.zip").exists()
    else:
        for _ in range(2):
            result = operation(state)
            assert result
            assert manifest(product) == original
            assert saved.read_bytes() == approved_bytes


@pytest.mark.parametrize("attack", [None, "tree-and-receipt", "git", "status"])
def test_extension_generation_cache_binds_native_evidence(settings, plan, monkeypatch, attack):
    from workbench.delivery import source_candidate
    from workbench.filesystem import manifest, write_json

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})
    plan = plan.model_copy(update={"data_scope": "shared"})
    design = SimpleNamespace(
        baseline=plan,
        model_dump=lambda: {"approved": plan.model_dump()},
        implementation=SimpleNamespace(
            version=1, selection=SimpleNamespace(model_dump=lambda: {"template": "fastapiadmin"})
        ),
    )
    root = settings.data_dir / "runs" / "extension-cache-binding" / "extension-baselines"
    product = root / digest(design.model_dump())
    product.mkdir(parents=True)
    (product / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    receipt = source_candidate.refresh_candidate(
        product,
        {
            "execution": "source-candidate",
            "template": "fastapiadmin",
            "spec_digest": digest(plan.model_dump()),
            "generation_status": "complete",
            "verification_status": "unverified",
            "pending_steps": [],
            "runtime_unavailable_reason": "Fixture unavailable",
        },
    )
    cached = {"files": manifest(product), "native_generation": receipt}
    if attack == "tree-and-receipt":
        (product / "example.py").write_text("VALUE = 999\n", encoding="utf-8")
        source_candidate.refresh_candidate(product, receipt)
        # Exercise the receipt binding even if the outer inventory is current.
        cached["files"] = manifest(product)
    elif attack == "git":
        write_json(
            root / "native-generation.json", {**receipt, "source_commit": {"status": "failed"}}
        )
    elif attack == "status":
        write_json(product / "SOURCE-STATUS.json", {})
        cached["files"] = manifest(product)
    flow = Workflow(settings, SimpleNamespace(step=lambda *args: cached), None)
    flow.checked_extension = lambda state: design
    state = {"run_id": "extension-cache-binding"}
    if attack:
        with pytest.raises(PrerequisiteError):
            flow.extension_generate(state)
    else:
        for _ in range(2):
            result = flow.extension_generate(state)
            assert result["native_generation"] == receipt
            assert result["extension_product"] == str(product)
````
