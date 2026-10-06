# tests/test_capability_policy.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`scripts.extension_oracles`、`workbench.capability_contracts`、`workbench.capability_policy`、`workbench.capability_verification`、`workbench.catalog`、`workbench.domain`、`workbench.errors`、`workbench.filesystem`、`workbench.flow`、`workbench.orchestration`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `scope`（L22–L23）：接收`text`。 调用`digest`、`scope_sources`。 返回路径：L23的`{"messages": [text], "source_digest": digest([text]), "sources": scope_sources([text])}`。
- `original`（L26–L30）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`json.loads`、`(Path(__file__).parent / "fixtures/contest_oracle/original_requir…`、`Path`、`scope`。 返回路径：L30的`scope(data["requirement_text"])`。
- `policy`（L33–L34）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`scope_policy`、`original`、`Selection(template="fastapiadmin").model_dump`、`Selection`。 返回路径：L34的`scope_policy(original(), Selection(template="fastapiadmin").model_dump())`。
- `business_proof`（L37–L48）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`list`。 返回路径：L38的`{ "business_oracle": { "protocol": contest.CONTRACT_VERSION, "witnesses": {name: True for …`。
- `test_registered_original_keeps_all_35_units_even_after_bounded_success`（L51–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L53断言`len(current["sources"]) == 35`；L55断言`selected["trusted_oracle"] == contest.CONTRACT_VERSION`；L57断言`{g["source_id"] for g in result["obligations"]} == {s["id"] for s in current["sources…`；L58断言`result["complete_source_ids"] == []`；L59断言`result["full_request_complete"] is False`；L60断言`len([g for g in result["obligations"] if g["status"] == "verified"]) == 4`；L61断言`all( g["status"] == "remaining" for g in result["obligations"] if g["semantic"] == "o…`；L68遍历`renamed["sources"]`。后续分支沿下方源码相同行号继续阅读。 调用`original`、`len`、`policy`、`business_coverage`、`business_proof`、`all`、`deepcopy`、`scope_policy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oracle_missing_or_candidate_claimed_completion_fails_closed`（L87–L91）：接收`key`、`value`。 调用`business_proof`、`pytest.raises`、`business_coverage`、`policy`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_extensions_remain_available_but_health_ids_are_not_acceptance`（L94–L112）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103断言`contract_errors(plan) == []`；L105断言`generic["trusted_oracle"] is None`；L106断言`business_coverage(generic, {})["coverage_level"] == "reviewed-executable-contract"`；L107遍历`plan.scenarios`；L111断言`any("健康" in error for error in errors)`；L112断言`any("重启" in error for error in errors)`。 调用`scope`、`make_plan`、`Selection().model_dump`、`Selection`、`contract_errors`、`scope_policy`、`plan.selection.model_dump`、`business_coverage`、`HttpStep`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `aggregate_state`（L115–L136）：接收`tmp_path`。 调用`scope`、`make_plan`、`Selection().model_dump`、`Selection`、`ExtensionDesign`、`fixture_baseline`、`product.mkdir`、`(product / "app.py").write_text`、`str`等。 返回路径：L128的`design, { "run_id": "authored", "round": 1, "extension_product": str(product), "extension_…`。
- `test_workflow_routes_registered_oracle_and_requires_explicit_partial_scope`（L139–L169）：接收`settings`、`store`、`tmp_path`、`monkeypatch`。 控制顺序：L158断言`data["requires_explicit_review"] is True`；L159断言`data["delivery_kind"] == "partial"`；L160断言`data["full_request_complete"] is False`；L165断言`calls[0]["trusted_oracle"] == contest.CONTRACT_VERSION`；L166断言`calls[0]["aggregate"] is True`；L168断言`len({g["source_id"] for g in report["obligations"]}) == 35`；L169断言`not list((settings.data_dir / "runs/authored").glob("*.zip"))`。 调用`aggregate_state`、`policy`、`Workflow`、`monkeypatch.setattr`、`state.update`、`workflow.extension_aggregate`、`original`、`workflow.extension_scope_data`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_routes_registered_oracle_and_requires_explicit_partial_scope.verify`（L148–L150）：接收`*args`、`**kwargs`。 调用`calls.append`、`business_proof`。 返回路径：L150的`business_proof()`。
- `test_aggregate_failure_routes_bounded_repair_without_losing_candidate`（L172–L189）：接收`settings`、`store`、`tmp_path`、`monkeypatch`。 控制顺序：L185断言`workflow.extension_after_aggregate(state) == "extension_integration_repair"`；L186断言`manifest(Path(state["extension_product"])) == before`。 调用`aggregate_state`、`Workflow`、`monkeypatch.setattr`、`manifest`、`Path`、`state.update`、`workflow.extension_aggregate`、`workflow.extension_after_aggregate`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_aggregate_failure_routes_bounded_repair_without_losing_candidate.failure`（L179–L180）：接收`*args`、`**kwargs`。 控制顺序：L180抛异常，停止当前正常路径。 调用`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_scope_and_zip_preserve_review_conflicts_and_invalidate_old_approval`（L193–L273）：接收`settings`、`store`、`tmp_path`、`monkeypatch`、`previously_complete`。 控制顺序：L246断言`data["model_review"] == state["model_review"]`；L247断言`data["review_conflicts"] == state["model_review"]["uncovered_requirements"]`；L248断言`data["requires_explicit_review"] is True`；L249断言`data["delivery_kind"] == "partial" and data["full_request_complete"] is False`；L250断言`data["coverage"]["complete_source_ids"] == []`；L251断言`data["coverage"]["pre_review_complete_source_ids"] == base["complete_source_ids"]`；L252断言`data["coverage"]["remaining_obligations"] == ["full-a", "full-b"]`；L253断言`data["coverage"]["obligations"][-1]["status"] == "verified"`。后续分支沿下方源码相同行号继续阅读。 调用`aggregate_state`、`store.create_project`、`store.create_run`、`state.update`、`scope`、`root.mkdir`、`Workflow`、`monkeypatch.setattr`、`deepcopy`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_policy.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L273。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11096`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_policy.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0671f839af9b44b5808ac9881fff88b9d1f07fb20e545e88fa7c9a635ccee941"} -->
````python
# tests/test_capability_policy.py
"""Authored policy/routing tests only; never a live sandbox or model attestation."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.capability_fixture import GOAL, fixture_baseline, make_plan
from scripts.extension_oracles import contest
from workbench.capability_contracts import HttpStep, scope_sources
from workbench.capability_policy import business_coverage, contract_errors, scope_policy
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest
from workbench.flow import Workflow
from workbench.orchestration import ExtensionDesign


def scope(text):
    return {"messages": [text], "source_digest": digest([text]), "sources": scope_sources([text])}


def original():
    data = json.loads(
        (Path(__file__).parent / "fixtures/contest_oracle/original_requirement.json").read_text()
    )
    return scope(data["requirement_text"])


def policy():
    return scope_policy(original(), Selection(template="fastapiadmin").model_dump())


def business_proof():
    return {
        "business_oracle": {
            "protocol": contest.CONTRACT_VERSION,
            "witnesses": {name: True for name in contest.SEMANTICS},
            "full_request_complete": False,
            "remaining_obligations": list(contest.REMAINING),
            "fresh_replay": True,
            "same_cluster": True,
            "distinct_database_oid": True,
        }
    }


def test_registered_original_keeps_all_35_units_even_after_bounded_success():
    current = original()
    assert len(current["sources"]) == 35
    selected = policy()
    assert selected["trusted_oracle"] == contest.CONTRACT_VERSION
    result = business_coverage(selected, business_proof())
    assert {g["source_id"] for g in result["obligations"]} == {s["id"] for s in current["sources"]}
    assert result["complete_source_ids"] == []
    assert result["full_request_complete"] is False
    assert len([g for g in result["obligations"] if g["status"] == "verified"]) == 4
    assert all(
        g["status"] == "remaining"
        for g in result["obligations"]
        if g["semantic"] == "original.full_source"
    )
    # Human IDs and planner text cannot select/deselect the registry.
    renamed = deepcopy(current)
    for row in renamed["sources"]:
        row["id"] = "renamed-" + row["id"]
    assert (
        scope_policy(renamed, selected["selection"])["trusted_oracle"] == contest.CONTRACT_VERSION
    )


@pytest.mark.parametrize(
    "key,value",
    [
        ("protocol", "health-only"),
        ("witnesses", {}),
        ("full_request_complete", True),
        ("remaining_obligations", []),
        ("fresh_replay", False),
        ("same_cluster", False),
        ("distinct_database_oid", False),
    ],
)
def test_oracle_missing_or_candidate_claimed_completion_fails_closed(key, value):
    proof = business_proof()
    proof["business_oracle"][key] = value
    with pytest.raises(CheckFailure):
        business_coverage(policy(), proof)


def test_generic_extensions_remain_available_but_health_ids_are_not_acceptance():
    current = scope(GOAL)
    plan = make_plan(
        {
            "source_units": current["sources"],
            "source_digest": current["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    assert contract_errors(plan) == []
    generic = scope_policy(current, plan.selection.model_dump())
    assert generic["trusted_oracle"] is None
    assert business_coverage(generic, {})["coverage_level"] == "reviewed-executable-contract"
    for scenario in plan.scenarios:
        scenario.steps = [HttpStep(path="/health", status=200, equals={"$.ok": True})]
        scenario.after_restart = scenario.steps
    errors = contract_errors(plan)
    assert any("健康" in error for error in errors)
    assert any("重启" in error for error in errors)


def aggregate_state(tmp_path):
    current = scope(GOAL)
    plan = make_plan(
        {
            "source_units": current["sources"],
            "source_digest": current["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    design = ExtensionDesign(baseline=fixture_baseline(), implementation=plan)
    product = tmp_path / "candidate"
    product.mkdir()
    (product / "app.py").write_text("# authored source, never executed\n")
    return design, {
        "run_id": "authored",
        "round": 1,
        "extension_product": str(product),
        "extension_completed": [{"task": t.id} for t in plan.tasks],
        "extension_policy": scope_policy(current, plan.selection.model_dump()),
        "extension_design": design.model_dump(),
        "extension_integration_attempt": 0,
    }


def test_workflow_routes_registered_oracle_and_requires_explicit_partial_scope(
    settings, store, tmp_path, monkeypatch
):
    design, state = aggregate_state(tmp_path)
    state["extension_policy"] = policy()
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)
    calls = []

    def verify(*args, **kwargs):
        calls.append(kwargs)
        return business_proof()

    monkeypatch.setattr("workbench.capability_sandbox.verify_capabilities", verify)
    # Routing simulation explicitly excludes the already separately tested real proof validator.
    monkeypatch.setattr("workbench.orchestration.require_evidence", lambda *a, **k: None)
    state.update(workflow.extension_aggregate(state))
    state["extension_scope"] = original()
    data = workflow.extension_scope_data(state, design)
    assert data["requires_explicit_review"] is True
    assert data["delivery_kind"] == "partial"
    assert data["full_request_complete"] is False
    from workbench.store import Conflict

    with pytest.raises(Conflict, match="人工审批"):
        workflow.extension_package(state)
    assert calls[0]["trusted_oracle"] == contest.CONTRACT_VERSION
    assert calls[0]["aggregate"] is True
    report = json.loads((settings.data_dir / "runs/authored/extension-coverage.json").read_text())
    assert len({g["source_id"] for g in report["obligations"]}) == 35
    assert not list((settings.data_dir / "runs/authored").glob("*.zip"))


def test_aggregate_failure_routes_bounded_repair_without_losing_candidate(
    settings, store, tmp_path, monkeypatch
):
    design, state = aggregate_state(tmp_path)
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)

    def failure(*args, **kwargs):
        raise CheckFailure("business assertion failed")

    monkeypatch.setattr("workbench.capability_sandbox.verify_capabilities", failure)
    before = manifest(Path(state["extension_product"]))
    state.update(workflow.extension_aggregate(state))
    assert workflow.extension_after_aggregate(state) == "extension_integration_repair"
    assert manifest(Path(state["extension_product"])) == before
    state["extension_integration_attempt"] = settings.max_repair_attempts
    with pytest.raises(UnsupportedScope, match="预算"):
        workflow.extension_after_aggregate(state)


@pytest.mark.parametrize("previously_complete", [False, True])
def test_scope_and_zip_preserve_review_conflicts_and_invalidate_old_approval(
    settings, store, tmp_path, monkeypatch, previously_complete
):
    import zipfile

    from workbench.store import Approval, Conflict

    design, state = aggregate_state(tmp_path)
    project = store.create_project("review disagreement", "review-disagreement")
    run = store.create_run(project["id"], {"requirement": "authored"}, "disagreement-run")["run_id"]
    state.update(
        run_id=run,
        extension_proof={"passed": True},
        extension_scope=scope(GOAL),
        model_review={
            "enabled": True,
            "uncovered_requirements": ["第一条原文中的人数约束未验证"],
            "observations": ["独立运行证明不能覆盖遗漏的子句"],
        },
    )
    root = settings.data_dir / "runs" / run
    root.mkdir(parents=True)
    base = {
        "coverage_level": "operator-reviewed-atomic-contracts",
        "full_request_complete": previously_complete,
        "complete_source_ids": ["source-0-0", "source-0-1"]
        if previously_complete
        else ["source-0-0"],
        "obligations": [
            {
                "goal_id": "full-a",
                "source_id": "source-0-0",
                "semantic": "original.full_source",
                "status": "verified",
            },
            {
                "goal_id": "full-b",
                "source_id": "source-0-1",
                "semantic": "original.full_source",
                "status": "verified" if previously_complete else "remaining",
            },
            {
                "goal_id": "atom-a",
                "source_id": "source-0-0",
                "semantic": "authored observed value",
                "status": "verified",
            },
        ],
    }
    workflow = Workflow(settings, store, None)
    monkeypatch.setattr(workflow, "checked_extension", lambda _: design)
    monkeypatch.setattr(workflow, "extension_coverage", lambda *args: deepcopy(base))
    data = workflow.extension_scope_data(state, design)
    assert data["model_review"] == state["model_review"]
    assert data["review_conflicts"] == state["model_review"]["uncovered_requirements"]
    assert data["requires_explicit_review"] is True
    assert data["delivery_kind"] == "partial" and data["full_request_complete"] is False
    assert data["coverage"]["complete_source_ids"] == []
    assert data["coverage"]["pre_review_complete_source_ids"] == base["complete_source_ids"]
    assert data["coverage"]["remaining_obligations"] == ["full-a", "full-b"]
    assert data["coverage"]["obligations"][-1]["status"] == "verified"
    gate = store.gate(run, "extension_scope", 1, data, ["approve"])
    with store.tx() as session:
        session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="local-operator"))
    monkeypatch.setattr("workbench.orchestration.require_evidence", lambda *a, **k: None)
    monkeypatch.setattr(
        "workbench.capability_sandbox.verify_capabilities", lambda *a, **k: {"passed": True}
    )
    monkeypatch.setattr(
        "workbench.capability_consumer.require_consumer_evidence", lambda *a, **k: None
    )
    packaged = workflow.extension_package(state)["delivery"]
    assert packaged["model_review"] == state["model_review"]
    assert packaged["review_conflicts"] == data["review_conflicts"]
    assert packaged["full_request_complete"] is False
    with zipfile.ZipFile(root / packaged["package"]) as archive:
        declared = json.loads(archive.read("RND-DELIVERY.json"))
    assert declared == data
    state["model_review"]["uncovered_requirements"].append("后来发现的另一个遗漏")
    with pytest.raises(Conflict, match="人工审批"):
        workflow.extension_package(state)
````
