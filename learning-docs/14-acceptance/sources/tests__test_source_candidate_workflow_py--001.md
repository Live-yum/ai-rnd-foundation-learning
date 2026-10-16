# tests/test_source_candidate_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generation.python_basic`、`workbench.production.graph`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `workflow`（L11–L14）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Workflow.__new__`、`SimpleNamespace`。 返回路径：L14的`flow`。
- `test_source_candidate_routes_only_source_checks_to_package`（L17–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23断言`flow.after_verify(state) == "package"`；L24断言`state["verification"]["passed"] is False`。 调用`workflow`、`flow.after_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_candidate_does_not_waive_invalid_source_checks`（L27–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`workflow`、`pytest.raises`、`flow.after_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_runtime_does_not_take_source_candidate_route`（L38–L46）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`workflow`、`pytest.raises`、`flow.after_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_drafted_tasks_unlock_bounded_source_edits_without_promotion`（L49–L67）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L63断言`flow.extension_task(state, design).id == "second"`；L64断言`flow.extension_after_generate(state) == "extension_code"`；L66断言`flow.extension_after_code(state) == "extension_package"`；L67断言`state["extension_completed"] == []`。 调用`workflow`、`SimpleNamespace`、`flow.extension_task`、`flow.extension_after_generate`、`state["extension_drafted"].append`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_task_selection_ignores_draft_records`（L70–L79）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78断言`flow.extension_task(state, design).id == "first"`；L79断言`flow.extension_after_code(state) == "extension_verify"`。 调用`workflow`、`SimpleNamespace`、`flow.extension_task`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_bounded_edit_keeps_source_candidate_without_sandbox`（L82–L88）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L88断言`flow.extension_after_code(state) == "extension_package"`。 调用`workflow`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_source_generation_reaches_download_without_runtime`（L91–L141）：接收`settings`、`plan`、`monkeypatch`。 控制顺序：L115遍历`("analyse", "source_context", "plan")`；L117遍历`("requirements", "design")`；L136断言`result["status"] == "SOURCE_READY"`；L137断言`result["verification"]["passed"] is False`；L138断言`result["delivery"]["verification_status"] == "unverified"`；L139断言`result["delivery"]["runtime_verified"] is False`；L140断言`result["delivery"]["acceptance_passed"] is False`；L141断言`(flow.product(result).parent / result["delivery"]["package"]).is_file()`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`action`、`Workflow`、`getattr`、`flow.compile(None).invoke`、`flow.compile`、`plan.model_dump`、`(flow.product(result).parent / result["delivery"]["package"]).is_…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_source_generation_reaches_download_without_runtime.generate`（L97–L110）：接收`settings`、`template`、`plan`、`destination`、`**kwargs`。 调用`destination.mkdir`、`(destination / "example.py").write_text`、`source_candidate.refresh_candidate`。 返回路径：L100的`source_candidate.refresh_candidate( destination, { "execution": "source-candidate", "templ…`。
- `test_workflow_source_generation_reaches_download_without_runtime.forbidden`（L122–L123）：接收`state`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extension_source_package_keeps_pending_tasks_and_checks_integrity`（L145–L223）：接收`settings`、`plan`、`monkeypatch`、`attack`。 控制顺序：L159按`attack == "casefold"`分支；L188按`attack == "tampered"`分支；L190按`attack == "entry-limit"`分支；L194按`attack == "scope-size"`分支；L197按`attack`分支；L203断言`prior.read_bytes() == b"previous verified artifact"`；L204断言`not (root / "extension-source.zip.tmp").exists()`；L207断言`result["generation_status"] == "partial"`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`product.mkdir`、`(product / "example.py").write_text`、`(product / "rnd-source-scope.json").write_text`、`source_candidate.refresh_candidate`、`Workflow`、`SimpleNamespace`、`str`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `rule_plan`（L227–L243）：接收`plan`。 调用`Plan.model_validate`、`plan.model_dump`。 返回路径：L230的`Plan.model_validate( { **plan.model_dump(), "data_scope": "shared", "custom_rules": [ { "e…`。
- `test_native_design_keeps_rules_without_requiring_aider`（L247–L293）：接收`settings`、`rule_plan`、`monkeypatch`、`coding_enabled`。 控制顺序：L291断言`result["decision"] == "approve"`；L292断言`gates[0][1] is True`；L293断言`gates[0][0]["plan"]["custom_rules"] == rule_plan.model_dump()["custom_rules"]`。 调用`native.write_runtime_example`、`monkeypatch.setattr`、`SimpleNamespace`、`Workflow`、`flow.design`、`rule_plan.model_dump`、`requirement().model_dump`、`requirement`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_design_keeps_rules_without_requiring_aider.gate`（L277–L279）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L279的`{"decision": "approve"}`。
- `test_native_rule_source_fallback_is_lazy_and_keeps_rule_pending`（L297–L347）：接收`settings`、`rule_plan`、`monkeypatch`、`coding_enabled`。 控制顺序：L337断言`callable(callback)`；L342断言`receipt["generation_status"] == "partial"`；L343断言`receipt["verification_status"] == "unverified"`；L344断言`any(rule_plan.custom_rules[0].description in step for step in receipt["pending_steps"…`；L346断言`spec["custom_rules"] == rule_plan.model_dump()["custom_rules"]`；L347断言`source_candidate.verify_candidate(flow.product(state), receipt)["passed"] is False`。 调用`monkeypatch.setattr`、`Workflow`、`SimpleNamespace`、`action`、`rule_plan.model_dump`、`flow.native_customization`、`callable`、`pytest.raises`、`callback`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_source_fallback_is_lazy_and_keeps_rule_pending.generate_candidate`（L313–L326）：接收`settings`、`template`、`plan`、`destination`、`reason`。 调用`destination.mkdir`、`(destination / "approved-spec.json").write_text`、`plan.model_dump_json`、`source_candidate.refresh_candidate`。 返回路径：L316的`source_candidate.refresh_candidate( destination, { "template": template, "execution": "sou…`。
- `test_resumed_source_code_node_never_runs_mini_swe_without_isolation`（L350–L365）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L361断言`flow.extension_code(state) == { "extension_candidate": "", "extension_candidate_passe…`；L365断言`flow.extension_after_code(state) == "extension_package"`。 调用`workflow`、`SimpleNamespace`、`flow.extension_code`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_runtime_factory_runs_only_when_callback_invoked`（L368–L389）：接收`settings`、`rule_plan`、`monkeypatch`。 控制顺序：L384断言`calls == []`；L386断言`calls == [ ("factory", "runtime-rule-test"), ("customize", ("template",), {"plan": ru…`。 调用`monkeypatch.setattr`、`Workflow`、`flow.native_customization`、`callback`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_runtime_factory_runs_only_when_callback_invoked.factory`（L377–L379）：接收`settings`、`gateway`、`run_id`。 调用`calls.append`。 返回路径：L379的`lambda *args, **kwargs: calls.append(("customize", args, kwargs))`。
- `test_source_task_selection_skips_isolated_task_but_preserves_dependencies`（L392–L417）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L407断言`flow.extension_task(state, design).id == "independent"`；L408断言`flow.extension_after_generate(state) == "extension_code"`；L410断言`flow.extension_task(state, design).id == "followup"`；L411断言`flow.extension_after_code(state) == "extension_code"`；L413断言`flow.extension_task(state, design) is None`；L414断言`flow.extension_after_code(state) == "extension_package"`；L415断言`state["extension_completed"] == []`；L417断言`flow.extension_task({"extension_completed": []}, design).id == "isolated"`。 调用`workflow`、`SimpleNamespace`、`flow.extension_task`、`flow.extension_after_generate`、`state["extension_drafted"].append`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_code_retrieval_is_local_despite_optional_provider_settings`（L421–L501）：接收`settings`、`tmp_path`、`monkeypatch`、`reserved_edit`。 控制顺序：L488按`reserved_edit`分支；L491断言`"控制端" in result["extension_error"]`；L492断言`"extension_drafted" not in result`；L493断言`result["extension_candidate_passed"] is False`；L494断言`not (product / reserved_edit).exists()`；L496遍历`range(2)`；L499断言`captured[0]["retrieval"] == captured[1]["retrieval"]`；L500断言`captured[0]["retrieval"]["mode"] == "ast+fts5"`。后续分支沿下方源码相同行号继续阅读。 调用`product.mkdir`、`(product / "example.py").write_text`、`monkeypatch.setattr`、`SimpleNamespace`、`Workflow`、`NoModelGateway`、`str`、`flow.extension_code`、`(product / reserved_edit).exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_code_retrieval_is_local_despite_optional_provider_settings.forbidden`（L437–L438）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_code_retrieval_is_local_despite_optional_provider_settings.CapturedContext`（L468–L469）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_code_retrieval_is_local_despite_optional_provider_settings.NoModelGateway`（L471–L476）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_code_retrieval_is_local_despite_optional_provider_settings.NoModelGateway.complete`（L472–L476）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L474按`reserved_edit`分支；L476抛异常，停止当前正常路径。 调用`captured.append`、`SimpleNamespace`。 返回路径：L475的`SimpleNamespace(files=[SimpleNamespace(path=reserved_edit)])`。
- `test_source_code_rejects_controller_paths_before_model_or_draft`（L514–L540）：接收`settings`、`tmp_path`、`name`。 控制顺序：L535断言`result["extension_candidate_passed"] is False`；L536断言`result["extension_error"]`；L537断言`"extension_drafted" not in result`；L538断言`state["extension_drafted"] == []`；L539断言`original.read_text(encoding="utf-8") == '{"runtime_verified": false}'`；L540断言`not list(settings.data_dir.glob("runs/*/candidates"))`。 调用`product.mkdir`、`original.write_text`、`SimpleNamespace`、`Workflow`、`NoModel`、`str`、`flow.extension_code`、`original.read_text`、`list`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_code_rejects_controller_paths_before_model_or_draft.NoModel`（L522–L524）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_code_rejects_controller_paths_before_model_or_draft.NoModel.complete`（L523–L524）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_route_does_not_require_runtime_database_approval`（L548–L628）：接收`settings`、`plan`、`monkeypatch`、`template`、`capability`、`config_state`。 控制顺序：L618断言`gates[0][1] is not available`；L619按`available`分支；L620断言`"native_validation_or_runtime" in gates[0][0]["block_sources"]`；L623断言`source_calls == []`；L626断言`result["execution"] == "source-candidate"`；L627断言`result["runtime_verified"] is False`；L628断言`source_calls == [capability]`。 调用`plan.model_copy`、`monkeypatch.delenv`、`write_json`、`native.runtime_path`、`monkeypatch.setattr`、`monkeypatch.setitem`、`SimpleNamespace`、`Workflow`、`native_plan.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_route_does_not_require_runtime_database_approval.source_only`（L579–L581）：接收`settings`、`template`、`plan`、`destination`、`reason`。 调用`source_calls.append`。 返回路径：L581的`{"execution": "source-candidate", "runtime_verified": False}`。
- `test_source_route_does_not_require_runtime_database_approval.no_runtime`（L583–L584）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_route_does_not_require_runtime_database_approval.gate`（L605–L607）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L607的`{"decision": "reject"}`。
- `test_unavailable_runtime_cannot_downgrade_or_replace_saved_runtime`（L632–L667）：接收`settings`、`plan`、`monkeypatch`、`mismatch`。 控制顺序：L667断言`source.read_text(encoding="utf-8") == "VALUE = 1\n"`。 调用`plan.model_copy`、`product.mkdir`、`source.write_text`、`write_json`、`digest`、`native_plan.model_dump`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_candidate_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L667。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26215`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8f7436ade5e234e79a2ae693d5134e935104db004744f626806f3d79b25f5f60"} -->
````python
# tests/test_source_candidate_workflow.py
"""Source drafts never become runtime acceptance or verified module progress."""

from types import SimpleNamespace

import pytest

from workbench.generation.python_basic import PrerequisiteError
from workbench.production.graph import Workflow


def workflow():
    flow = Workflow.__new__(Workflow)
    flow.settings = SimpleNamespace(max_repair_attempts=0)
    return flow


def test_source_candidate_routes_only_source_checks_to_package():
    flow = workflow()
    state = {
        "native_generation": {"execution": "source-candidate"},
        "verification": {"passed": False, "source_checks_passed": True},
    }
    assert flow.after_verify(state) == "package"
    assert state["verification"]["passed"] is False


def test_source_candidate_does_not_waive_invalid_source_checks():
    flow = workflow()
    state = {
        "native_generation": {"execution": "source-candidate"},
        "verification": {"passed": False, "source_checks_passed": False},
        "plan": {},
    }
    with pytest.raises(PrerequisiteError):
        flow.after_verify(state)


def test_failed_runtime_does_not_take_source_candidate_route():
    flow = workflow()
    state = {
        "native_generation": {"execution": "managed-runtime"},
        "verification": {"passed": False, "source_checks_passed": True},
        "plan": {},
    }
    with pytest.raises(PrerequisiteError):
        flow.after_verify(state)


def test_drafted_tasks_unlock_bounded_source_edits_without_promotion():
    flow = workflow()
    tasks = [
        SimpleNamespace(id="first", depends_on=[], executor="bounded_edit"),
        SimpleNamespace(id="second", depends_on=["first"], executor="bounded_edit"),
        SimpleNamespace(id="isolated", depends_on=["second"], executor="mini_swe"),
    ]
    design = SimpleNamespace(implementation=SimpleNamespace(tasks=tasks))
    flow.checked_extension = lambda state: design
    state = {
        "native_generation": {"execution": "source-candidate"},
        "extension_completed": [],
        "extension_drafted": ["first"],
    }
    assert flow.extension_task(state, design).id == "second"
    assert flow.extension_after_generate(state) == "extension_code"
    state["extension_drafted"].append("second")
    assert flow.extension_after_code(state) == "extension_package"
    assert state["extension_completed"] == []


def test_runtime_task_selection_ignores_draft_records():
    flow = workflow()
    design = SimpleNamespace(
        implementation=SimpleNamespace(
            tasks=[SimpleNamespace(id="first", depends_on=[], executor="bounded_edit")]
        )
    )
    state = {"extension_drafted": ["first"], "extension_completed": []}
    assert flow.extension_task(state, design).id == "first"
    assert flow.extension_after_code(state) == "extension_verify"


def test_failed_bounded_edit_keeps_source_candidate_without_sandbox():
    flow = workflow()
    state = {
        "native_generation": {"execution": "source-candidate"},
        "extension_error": "Preimage mismatch",
    }
    assert flow.extension_after_code(state) == "extension_package"


def test_workflow_source_generation_reaches_download_without_runtime(settings, plan, monkeypatch):
    from workbench.delivery import source_candidate
    from workbench.generation.native import service

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})

    def generate(settings, template, plan, destination, **kwargs):
        destination.mkdir(parents=True)
        (destination / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
        return source_candidate.refresh_candidate(
            destination,
            {
                "execution": "source-candidate",
                "template": template,
                "generation_status": "complete",
                "verification_status": "unverified",
                "pending_steps": ["Run isolated runtime acceptance"],
                "runtime_unavailable_reason": "Test runtime unavailable",
            },
        )

    monkeypatch.setattr(service, "generate_native", generate)
    store = SimpleNamespace(step=lambda run, key, action: action())
    flow = Workflow(settings, store, None)
    for name in ("analyse", "source_context", "plan"):
        monkeypatch.setattr(flow, name, lambda state: {})
    for name in ("requirements", "design"):
        monkeypatch.setattr(flow, name, lambda state: {"decision": "approve"})
    monkeypatch.setattr(flow, "gate", lambda *args, **kwargs: {"decision": "approve"})
    monkeypatch.setattr(flow, "observed_node", lambda name: getattr(flow, name))

    def forbidden(state):
        pytest.fail("Unverified source must not invoke runtime sandbox or model acceptance")

    monkeypatch.setattr(flow, "sandbox", forbidden)
    monkeypatch.setattr(flow, "model_review", forbidden)
    result = flow.compile(None).invoke(
        {
            "run_id": "source-test",
            "template": "fastapiadmin",
            "plan": plan.model_dump(),
            "attempt": 0,
            "round": 1,
        }
    )
    assert result["status"] == "SOURCE_READY"
    assert result["verification"]["passed"] is False
    assert result["delivery"]["verification_status"] == "unverified"
    assert result["delivery"]["runtime_verified"] is False
    assert result["delivery"]["acceptance_passed"] is False
    assert (flow.product(result).parent / result["delivery"]["package"]).is_file()


@pytest.mark.parametrize("attack", [None, "tampered", "casefold", "entry-limit", "scope-size"])
def test_extension_source_package_keeps_pending_tasks_and_checks_integrity(
    settings, plan, monkeypatch, attack
):
    import json
    import zipfile

    from workbench import filesystem
    from workbench.delivery import source_candidate

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})
    root = settings.data_dir / "runs" / "extension-source-test"
    product = root / "baseline" / "product"
    product.mkdir(parents=True)
    (product / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    if attack == "casefold":
        (product / "rnd-source-scope.json").write_text("{}", encoding="utf-8")
    receipt = source_candidate.refresh_candidate(
        product,
        {
            "execution": "source-candidate",
            "template": "fastapiadmin",
            "generation_status": "complete",
            "verification_status": "unverified",
            "pending_steps": ["Run runtime acceptance"],
            "runtime_unavailable_reason": "Test runtime unavailable",
        },
    )
    flow = Workflow(settings, None, None)
    implementation = SimpleNamespace(
        tasks=[SimpleNamespace(id="isolated-task")],
        model_dump=lambda: {"task": "isolated-task"},
    )
    flow.checked_extension = lambda state: SimpleNamespace(
        implementation=implementation, baseline=plan
    )
    state = {
        "run_id": "extension-source-test",
        "native_generation": receipt,
        "extension_product": str(product),
        "extension_drafted": [],
        "extension_completed": [],
        "extension_scope": {"sources": []},
    }
    if attack == "tampered":
        (product / "example.py").write_text("VALUE = 2\n", encoding="utf-8")
    elif attack == "entry-limit":
        monkeypatch.setattr(
            filesystem, "archive_entry_limit", lambda template: len(receipt["files"])
        )
    elif attack == "scope-size":
        monkeypatch.setattr(filesystem, "ARCHIVE_MAX_FILE_BYTES", 2000)
        state["extension_scope"]["sources"] = ["oversized-scope" * 1000]
    if attack:
        # Keep a previous delivery intact if a new final archive is unsafe.
        prior = root / "extension-source.zip"
        prior.write_bytes(b"previous verified artifact")
        with pytest.raises((PrerequisiteError, ValueError)):
            flow.extension_package(state)
        assert prior.read_bytes() == b"previous verified artifact"
        assert not (root / "extension-source.zip.tmp").exists()
        return
    result = flow.extension_package(state)["delivery"]
    assert result["generation_status"] == "partial"
    assert result["verification_status"] == "unverified"
    assert result["acceptance_passed"] is False
    assert "Implement module task: isolated-task" in result["pending_steps"]
    with zipfile.ZipFile(root / result["package"]) as archive:
        scope = json.loads(archive.read("RND-SOURCE-SCOPE.json"))
        assert scope["pending_steps"] == result["pending_steps"]
        assert scope["full_request_complete"] is False
        assert "archive" not in scope  # No stale or self-referential ZIP metadata.
        assert result["archive"]["entry_count"] == len(archive.infolist())
        assert result["archive"]["uncompressed_bytes"] == sum(
            item.file_size for item in archive.infolist()
        )
    assert result["archive"]["compressed_bytes"] == (root / result["package"]).stat().st_size
    # Metadata refresh is replay-safe and does not promote tasks.
    assert flow.extension_package(state)["delivery"]["verification_status"] == "unverified"
    assert state["extension_completed"] == []


@pytest.fixture
def rule_plan(plan):
    from workbench.core.contracts import Plan

    return Plan.model_validate(
        {
            **plan.model_dump(),
            "data_scope": "shared",
            "custom_rules": [
                {
                    "entity": "task",
                    "description": "Priority must be nonnegative",
                    "accept_examples": [{"title": "ok", "priority": 1, "done": False}],
                    "reject_examples": [{"title": "bad", "priority": -1, "done": False}],
                }
            ],
        }
    )


@pytest.mark.parametrize("coding_enabled", [True, False])
def test_native_design_keeps_rules_without_requiring_aider(
    settings, rule_plan, monkeypatch, coding_enabled
):
    from conftest import requirement

    from workbench.delivery import native
    from workbench.production import graph

    settings.coding_engine = "bounded"
    settings.enable_coding = coding_enabled
    native.write_runtime_example(settings, "fastapiadmin")
    monkeypatch.setattr(
        native,
        "runtime_capability",
        lambda template: {
            "available": True,
            "reason": "",
        },
    )
    selection = SimpleNamespace(
        capabilities=lambda: {"field_kinds": ["text", "integer", "boolean"]},
        model_dump=lambda: {"template": "fastapiadmin"},
    )
    monkeypatch.setattr(graph, "options_for_run", lambda run: selection)
    monkeypatch.setattr(graph, "coverage_gaps", lambda *a, **k: [])
    monkeypatch.setattr(graph, "business_gaps", lambda *a, **k: [])
    monkeypatch.setattr(graph, "design_pack", lambda *a, **k: {"tasks": []})
    flow = Workflow(settings, SimpleNamespace(get_run=lambda run: {}), None)
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((data, can_approve))
        return {"decision": "approve"}

    flow.gate = gate
    result = flow.design(
        {
            "run_id": "native-rule-design",
            "template": "fastapiadmin",
            "round": 1,
            "plan": rule_plan.model_dump(),
            "requirement": requirement().model_dump(),
        }
    )
    assert result["decision"] == "approve"
    assert gates[0][1] is True, gates[0][0]
    assert gates[0][0]["plan"]["custom_rules"] == rule_plan.model_dump()["custom_rules"]


@pytest.mark.parametrize("coding_enabled", [True, False])
def test_native_rule_source_fallback_is_lazy_and_keeps_rule_pending(
    settings, rule_plan, monkeypatch, coding_enabled
):
    import json

    from workbench.delivery import native, source_candidate

    settings.coding_engine = "bounded"
    settings.enable_coding = coding_enabled
    monkeypatch.setattr(
        native,
        "runtime_capability",
        lambda template: {"available": False, "reason": "Runtime unavailable in source-only test"},
    )
    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})

    def generate_candidate(settings, template, plan, destination, reason):
        destination.mkdir(parents=True)
        (destination / "approved-spec.json").write_text(plan.model_dump_json(), encoding="utf-8")
        return source_candidate.refresh_candidate(
            destination,
            {
                "template": template,
                "execution": "source-candidate",
                "generation_status": "partial",
                "verification_status": "unverified",
                "pending_steps": ["Run isolated acceptance"],
                "runtime_unavailable_reason": reason,
            },
        )

    monkeypatch.setattr(source_candidate, "generate_candidate", generate_candidate)
    flow = Workflow(settings, SimpleNamespace(step=lambda run, key, action: action()), None)
    state = {
        "run_id": "native-rule-source",
        "template": "fastapiadmin",
        "plan": rule_plan.model_dump(),
    }
    # Constructing the callback must not check Aider or import its runtime tools.
    callback = flow.native_customization(state, rule_plan)
    assert callable(callback)
    # Actual runtime customization still rejects unavailable/disabled Aider.
    with pytest.raises(PrerequisiteError, match="CODING_ENGINE=aider"):
        callback()
    receipt = flow.generate(state)["native_generation"]
    assert receipt["generation_status"] == "partial"
    assert receipt["verification_status"] == "unverified"
    assert any(rule_plan.custom_rules[0].description in step for step in receipt["pending_steps"])
    spec = json.loads((flow.product(state) / "approved-spec.json").read_text(encoding="utf-8"))
    assert spec["custom_rules"] == rule_plan.model_dump()["custom_rules"]
    assert source_candidate.verify_candidate(flow.product(state), receipt)["passed"] is False


def test_resumed_source_code_node_never_runs_mini_swe_without_isolation():
    flow = workflow()
    design = SimpleNamespace(
        implementation=SimpleNamespace(
            tasks=[
                SimpleNamespace(id="isolated", depends_on=[], executor="mini_swe"),
            ]
        )
    )
    flow.checked_extension = lambda state: design
    state = {"native_generation": {"execution": "source-candidate"}}
    assert flow.extension_code(state) == {
        "extension_candidate": "",
        "extension_candidate_passed": False,
    }
    assert flow.extension_after_code(state) == "extension_package"


def test_native_rule_runtime_factory_runs_only_when_callback_invoked(
    settings, rule_plan, monkeypatch
):
    from workbench.generation.native import coding

    settings.coding_engine = "aider"
    settings.enable_coding = True
    calls = []

    def factory(settings, gateway, run_id):
        calls.append(("factory", run_id))
        return lambda *args, **kwargs: calls.append(("customize", args, kwargs))

    monkeypatch.setattr(coding, "native_rule_customizer", factory)
    flow = Workflow(settings, None, None)
    callback = flow.native_customization({"run_id": "runtime-rule-test"}, rule_plan)
    assert calls == []
    callback("template", plan=rule_plan)
    assert calls == [
        ("factory", "runtime-rule-test"),
        ("customize", ("template",), {"plan": rule_plan}),
    ]


def test_source_task_selection_skips_isolated_task_but_preserves_dependencies():
    flow = workflow()
    tasks = [
        SimpleNamespace(id="isolated", depends_on=[], executor="mini_swe"),
        SimpleNamespace(id="blocked", depends_on=["isolated"], executor="bounded_edit"),
        SimpleNamespace(id="independent", depends_on=[], executor="bounded_edit"),
        SimpleNamespace(id="followup", depends_on=["independent"], executor="bounded_edit"),
    ]
    design = SimpleNamespace(implementation=SimpleNamespace(tasks=tasks))
    flow.checked_extension = lambda state: design
    state = {
        "native_generation": {"execution": "source-candidate"},
        "extension_completed": [],
        "extension_drafted": [],
    }
    assert flow.extension_task(state, design).id == "independent"
    assert flow.extension_after_generate(state) == "extension_code"
    state["extension_drafted"].append("independent")
    assert flow.extension_task(state, design).id == "followup"
    assert flow.extension_after_code(state) == "extension_code"
    state["extension_drafted"].append("followup")
    assert flow.extension_task(state, design) is None
    assert flow.extension_after_code(state) == "extension_package"
    assert state["extension_completed"] == []
    # Runtime task order and dependency semantics are unchanged.
    assert flow.extension_task({"extension_completed": []}, design).id == "isolated"


@pytest.mark.parametrize("reserved_edit", [None, "SOURCE-STATUS.json", "source-status.md"])
def test_source_code_retrieval_is_local_despite_optional_provider_settings(
    settings, tmp_path, monkeypatch, reserved_edit
):
    from workbench.knowledge_services import continue_index, retrieval
    from workbench.production import dispatcher

    settings.repo_map_provider = "aider"
    settings.retrieval_engine = "continue"
    settings.embedding_enabled = True
    settings.embedding_model = "offline-must-not-call"
    product = tmp_path / "source"
    product.mkdir()
    (product / "example.py").write_text(
        "def example():\n    return 'deterministic source'\n", encoding="utf-8"
    )

    def forbidden(*args, **kwargs):
        pytest.fail("Source-only retrieval invoked an optional tool or embedding service")

    monkeypatch.setattr(continue_index, "rank", forbidden)
    monkeypatch.setattr(retrieval, "embedding_profile", forbidden)
    monkeypatch.setattr(retrieval, "embed", forbidden)
    from workbench.coding import aider

    monkeypatch.setattr(aider, "repo_map", forbidden)
    monkeypatch.setattr(
        dispatcher,
        "get_adapter",
        lambda template: SimpleNamespace(coding_standard=lambda: {"source_only": True}),
    )
    task_data = {
        "id": "draft",
        "title": "example",
        "contract": "Update example",
        "files": ["example.py"],
        "depends_on": [],
        "executor": "bounded_edit",
    }
    task = SimpleNamespace(**task_data, model_dump=lambda: task_data)
    design = SimpleNamespace(
        implementation=SimpleNamespace(
            tasks=[task], selection=SimpleNamespace(template="fastapiadmin")
        ),
        model_dump=lambda: {"tasks": [task_data]},
    )
    captured = []

    class CapturedContext(Exception):
        pass

    class NoModelGateway:
        def complete(self, run_id, key, instruction, payload, schema):
            captured.append(payload)
            if reserved_edit:
                return SimpleNamespace(files=[SimpleNamespace(path=reserved_edit)])
            raise CapturedContext

    flow = Workflow(settings, None, NoModelGateway())
    flow.checked_extension = lambda state: design
    state = {
        "native_generation": {"execution": "source-candidate"},
        "extension_product": str(product),
        "run_id": "local-retrieval",
        "round": 1,
        "extension_policy": {},
        "extension_scope": {"sources": []},
    }
    if reserved_edit:
        monkeypatch.setattr(dispatcher, "apply_candidate", forbidden)
        result = flow.extension_code(state)
        assert "控制端" in result["extension_error"]
        assert "extension_drafted" not in result
        assert result["extension_candidate_passed"] is False
        assert not (product / reserved_edit).exists()
        return
    for _ in range(2):
        with pytest.raises(CapturedContext):
            flow.extension_code(state)
    assert captured[0]["retrieval"] == captured[1]["retrieval"]
    assert captured[0]["retrieval"]["mode"] == "ast+fts5"
    assert captured[0]["retrieval"]["matches"]


@pytest.mark.parametrize(
    "name",
    [
        "SOURCE-STATUS.json",
        "SOURCE-STATUS.md",
        "source-status.JSON",
        "./source-status.md",
        "RND-SOURCE-SCOPE.json",
    ],
)
def test_source_code_rejects_controller_paths_before_model_or_draft(settings, tmp_path, name):
    product = tmp_path / "source"
    product.mkdir()
    original = product / "SOURCE-STATUS.json"
    original.write_text('{"runtime_verified": false}', encoding="utf-8")
    task = SimpleNamespace(id="bad-edit", depends_on=[], executor="bounded_edit", files=[name])
    design = SimpleNamespace(implementation=SimpleNamespace(tasks=[task]))

    class NoModel:
        def complete(self, *args, **kwargs):
            pytest.fail("Controller-owned edit reached the model")

    flow = Workflow(settings, None, NoModel())
    flow.checked_extension = lambda state: design
    state = {
        "native_generation": {"execution": "source-candidate"},
        "extension_product": str(product),
        "extension_drafted": [],
        "extension_completed": [],
    }
    result = flow.extension_code(state)
    assert result["extension_candidate_passed"] is False
    assert result["extension_error"]
    assert "extension_drafted" not in result
    assert state["extension_drafted"] == []
    assert original.read_text(encoding="utf-8") == '{"runtime_verified": false}'
    assert not list(settings.data_dir.glob("runs/*/candidates"))


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "capability", ["windows", "macos-missing-tools", "missing-toolchain", "runtime"]
)
@pytest.mark.parametrize("config_state", ["unapproved", "missing-env"])
def test_source_route_does_not_require_runtime_database_approval(
    settings, plan, monkeypatch, template, capability, config_state
):
    import sys

    from conftest import requirement

    from workbench.delivery import native, source_candidate
    from workbench.filesystem import write_json
    from workbench.production import graph

    native_plan = plan.model_copy(update={"data_scope": "shared"})
    monkeypatch.delenv("NATIVE_TEST_ROUTING_DATABASE_URL", raising=False)
    write_json(
        native.runtime_path(settings, template),
        {
            "database_url_env": "NATIVE_TEST_ROUTING_DATABASE_URL",
            "initialize_empty_database": config_state == "missing-env",
        },
    )
    available = capability == "runtime"
    monkeypatch.setattr(
        native,
        "runtime_capability",
        lambda template: {
            "available": available,
            "reason": capability,
        },
    )
    source_calls = []

    def source_only(settings, template, plan, destination, reason):
        source_calls.append(reason)
        return {"execution": "source-candidate", "runtime_verified": False}

    def no_runtime(*args, **kwargs):
        pytest.fail("Runtime execution must not occur without database authorization")

    monkeypatch.setattr(source_candidate, "generate_candidate", source_only)
    monkeypatch.setitem(
        sys.modules,
        "workbench.acceptance.native_lab",
        SimpleNamespace(
            run_acceptance=no_runtime,
        ),
    )
    selection = SimpleNamespace(
        capabilities=lambda: {"field_kinds": ["text", "integer", "boolean"]},
        model_dump=lambda: {"template": template},
    )
    monkeypatch.setattr(graph, "options_for_run", lambda run: selection)
    monkeypatch.setattr(graph, "coverage_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "business_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "design_pack", lambda *args, **kwargs: {"tasks": []})
    flow = Workflow(settings, SimpleNamespace(get_run=lambda run: {}), None)
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((data, can_approve))
        return {"decision": "reject"}

    flow.gate = gate
    state = {
        "run_id": "source-routing",
        "template": template,
        "round": 1,
        "plan": native_plan.model_dump(),
        "requirement": requirement().model_dump(),
    }
    flow.design(state)
    assert gates[0][1] is not available, gates[0][0]
    if available:
        assert "native_validation_or_runtime" in gates[0][0]["block_sources"]
        with pytest.raises(PrerequisiteError):
            native.managed_generate(settings, template, native_plan, flow.product(state))
        assert source_calls == []
    else:
        result = native.managed_generate(settings, template, native_plan, flow.product(state))
        assert result["execution"] == "source-candidate"
        assert result["runtime_verified"] is False
        assert source_calls == [capability]


@pytest.mark.parametrize("mismatch", [None, "plan", "template"])
def test_unavailable_runtime_cannot_downgrade_or_replace_saved_runtime(
    settings, plan, monkeypatch, mismatch
):
    from workbench.core.contracts import digest
    from workbench.delivery import native, source_candidate
    from workbench.filesystem import write_json

    native_plan = plan.model_copy(update={"data_scope": "shared"})
    product = settings.data_dir / "runs" / "retained-runtime" / "product"
    product.mkdir(parents=True)
    source = product / "approved.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    write_json(
        product.parent / "native-generation.json",
        {
            "execution": "managed-runtime",
            "template": "yudao-vben" if mismatch == "template" else "fastapiadmin",
            "spec_digest": "old-plan" if mismatch == "plan" else digest(native_plan.model_dump()),
        },
    )
    monkeypatch.setattr(
        native,
        "runtime_capability",
        lambda template: {
            "available": False,
            "reason": "runtime unavailable",
        },
    )
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *a, **k: pytest.fail("A saved runtime must not become a source candidate"),
    )
    with pytest.raises(PrerequisiteError, match="覆盖" if mismatch else "降级"):
        native.managed_generate(settings, "fastapiadmin", native_plan, product)
    assert source.read_text(encoding="utf-8") == "VALUE = 1\n"
````
