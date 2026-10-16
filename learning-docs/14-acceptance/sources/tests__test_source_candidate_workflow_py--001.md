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
- `test_extension_source_package_keeps_pending_tasks_and_checks_integrity`（L145–L201）：接收`settings`、`plan`、`monkeypatch`、`tampered`。 控制顺序：L185按`tampered`分支；L191断言`result["generation_status"] == "partial"`；L192断言`result["verification_status"] == "unverified"`；L193断言`result["acceptance_passed"] is False`；L194断言`"Implement module task: isolated-task" in result["pending_steps"]`；L197断言`scope["pending_steps"] == result["pending_steps"]`；L198断言`scope["full_request_complete"] is False`；L200断言`flow.extension_package(state)["delivery"]["verification_status"] == "unverified"`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`product.mkdir`、`(product / "example.py").write_text`、`source_candidate.refresh_candidate`、`Workflow`、`SimpleNamespace`、`str`、`pytest.raises`、`flow.extension_package`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `rule_plan`（L205–L221）：接收`plan`。 调用`Plan.model_validate`、`plan.model_dump`。 返回路径：L208的`Plan.model_validate( { **plan.model_dump(), "data_scope": "shared", "custom_rules": [ { "e…`。
- `test_native_design_keeps_rules_without_requiring_aider`（L225–L261）：接收`settings`、`rule_plan`、`monkeypatch`、`coding_enabled`。 控制顺序：L259断言`result["decision"] == "approve"`；L260断言`gates[0][1] is True`；L261断言`gates[0][0]["plan"]["custom_rules"] == rule_plan.model_dump()["custom_rules"]`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`Workflow`、`flow.design`、`rule_plan.model_dump`、`requirement().model_dump`、`requirement`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_design_keeps_rules_without_requiring_aider.gate`（L245–L247）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L247的`{"decision": "approve"}`。
- `test_native_rule_source_fallback_is_lazy_and_keeps_rule_pending`（L265–L315）：接收`settings`、`rule_plan`、`monkeypatch`、`coding_enabled`。 控制顺序：L305断言`callable(callback)`；L310断言`receipt["generation_status"] == "partial"`；L311断言`receipt["verification_status"] == "unverified"`；L312断言`any(rule_plan.custom_rules[0].description in step for step in receipt["pending_steps"…`；L314断言`spec["custom_rules"] == rule_plan.model_dump()["custom_rules"]`；L315断言`source_candidate.verify_candidate(flow.product(state), receipt)["passed"] is False`。 调用`monkeypatch.setattr`、`Workflow`、`SimpleNamespace`、`action`、`rule_plan.model_dump`、`flow.native_customization`、`callable`、`pytest.raises`、`callback`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_source_fallback_is_lazy_and_keeps_rule_pending.generate_candidate`（L281–L294）：接收`settings`、`template`、`plan`、`destination`、`reason`。 调用`destination.mkdir`、`(destination / "approved-spec.json").write_text`、`plan.model_dump_json`、`source_candidate.refresh_candidate`。 返回路径：L284的`source_candidate.refresh_candidate( destination, { "template": template, "execution": "sou…`。
- `test_resumed_source_code_node_never_runs_mini_swe_without_isolation`（L318–L333）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L329断言`flow.extension_code(state) == { "extension_candidate": "", "extension_candidate_passe…`；L333断言`flow.extension_after_code(state) == "extension_package"`。 调用`workflow`、`SimpleNamespace`、`flow.extension_code`、`flow.extension_after_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_runtime_factory_runs_only_when_callback_invoked`（L336–L357）：接收`settings`、`rule_plan`、`monkeypatch`。 控制顺序：L352断言`calls == []`；L354断言`calls == [ ("factory", "runtime-rule-test"), ("customize", ("template",), {"plan": ru…`。 调用`monkeypatch.setattr`、`Workflow`、`flow.native_customization`、`callback`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_runtime_factory_runs_only_when_callback_invoked.factory`（L345–L347）：接收`settings`、`gateway`、`run_id`。 调用`calls.append`。 返回路径：L347的`lambda *args, **kwargs: calls.append(("customize", args, kwargs))`。

</details>

**创建路径：** `tests/test_source_candidate_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L357。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13863`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d82eb9593db03f6ad3311ab17d9d15612bdb950b5d31295a41c1ed4d18310e1f"} -->
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


@pytest.mark.parametrize("tampered", [False, True])
def test_extension_source_package_keeps_pending_tasks_and_checks_integrity(
    settings, plan, monkeypatch, tampered
):
    import json
    import zipfile

    from workbench.delivery import source_candidate

    monkeypatch.setattr(source_candidate, "source_snapshot", lambda path: {"status": "unavailable"})
    root = settings.data_dir / "runs" / "extension-source-test"
    product = root / "baseline" / "product"
    product.mkdir(parents=True)
    (product / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
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
    if tampered:
        (product / "example.py").write_text("VALUE = 2\n", encoding="utf-8")
        with pytest.raises(PrerequisiteError):
            flow.extension_package(state)
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

    from workbench.production import graph

    settings.coding_engine = "bounded"
    settings.enable_coding = coding_enabled
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
````
