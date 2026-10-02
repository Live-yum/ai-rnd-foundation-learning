# tests/test_requirement_source_conflicts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.flow`、`workbench.requirement_coverage`、`workbench.requirement_sources`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `source_requirement`（L22–L31）：接收`questions`。 调用`requirement(questions).model_copy`、`requirement`、`FieldRequirement`。 返回路径：L23的`requirement(questions).model_copy( update={ "features": ["CRUD", "task.title 最长200"], "acc…`。
- `conflicting`（L34–L37）：接收`old`。 调用`old.model_copy`、`proposed.features.append`。 返回路径：L37的`proposed`。
- `test_recorded_200_vs_120_retains_original_sources_without_changing_fixture`（L40–L67）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L47断言`data["approval_status"] == "unapproved"`；L48断言`data["execution_authorized"] is False`；L55断言`len(diagnostics) == 1`；L57断言`conflict["target"] == {"entity": "requests", "field": "title"}`；L58断言`conflict["attribute"] == "max_length"`；L59断言`{source["expected"] for source in conflict["sources"]} == {120, 200}`；L60断言`{(s["source"]["section"], s["source"]["index"]) for s in conflict["sources"]} == { ("…`；L65断言`conflict["sources"][-1]["text"] == old.acceptance[1]`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`path.read_bytes`、`json.loads`、`Requirement.model_validate`、`old.model_dump`、`old.model_copy`、`proposed.features.append`、`reconcile`、`old.gate_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_equivalent_restatement_is_not_a_conflict`（L71–L77）：接收`text`。 控制顺序：L76断言`analysis_source_conflicts(old.gate_dump(), merged, []) == []`；L77断言`text in merged.features`。 调用`source_requirement`、`old.model_copy`、`proposed.features.append`、`reconcile`、`old.gate_dump`、`analysis_source_conflicts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ungrounded_description_has_no_user_authority_and_unknown_text_survives`（L80–L96）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L90断言`injected["origin"] == "model_analysis"`；L91断言`injected["user_sources"] == [] and injected["correction_sources"] == []`；L93断言`retained["user_sources"][0]["user_message_index"] == 0`；L94断言`retained["user_sources"][0]["sha256"] == digest(human[0])`；L95断言`"text" not in retained["user_sources"][0]`；L96断言`unknown in merged.features`。 调用`source_requirement`、`conflicting`、`proposed.features.append`、`reconcile`、`old.gate_dump`、`analysis_source_conflicts`、`next`、`digest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_first_analysis_cannot_override_unambiguous_original_user_constraint`（L99–L109）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L105断言`len(diagnostics) == 1`；L107断言`source["source"] == {"section": "user_messages", "index": 0}`；L108断言`source["expected"] == 200 and source["text"] == "task.title 最长200"`；L109断言`candidate.field_requirements[0].max_length == 120`。 调用`source_requirement`、`analysis_source_conflicts`、`len`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_first_analysis_accepts_equivalent_original_constraint`（L115–L123）：接收`original`。 控制顺序：L116断言`analysis_source_conflicts(None, source_requirement(), [original], cursor=1) == []`；L123断言`any(s["origin"] == "user_input" for s in diagnostics[0]["sources"])`。 调用`analysis_source_conflicts`、`source_requirement`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_first_analysis_fresh_explicit_correction_has_same_strict_authorization`（L126–L138）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L131断言`analysis_source_conflicts(None, candidate, human, cursor=1) == []`；L135断言`{s["expected"] for s in diagnostics[0]["sources"]} == {120, 150, 200}`；L136断言`{ s["source"]["index"] for s in diagnostics[0]["sources"] if s["origin"] == "user_inp…`。 调用`source_requirement`、`analysis_source_conflicts`、`human.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unreliable_user_prose_is_not_marked_source_verified`（L141–L149）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L144断言`diagnostics`；L145断言`all(not s["user_sources"] for s in diagnostics[0]["sources"])`；L146断言`all(s["origin"] != "user_input" for s in diagnostics[0]["sources"])`；L147断言`analysis_source_conflicts(None, source_requirement(), ["title 应该短一些"], cursor=1) == […`。 调用`conflicting`、`source_requirement`、`analysis_source_conflicts`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ambiguous_cross_entity_title_is_not_guessed`（L152–L156）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L156断言`analysis_source_conflicts(None, old, []) == []`。 调用`source_requirement`、`old.field_requirements.append`、`FieldRequirement`、`old.features.append`、`analysis_source_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_backed_correction_updates_all_obligations_without_guard_override`（L159–L186）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L182断言`all(change["authorized"] for change in changes)`；L183断言`merged.field_requirements[0].max_length == 120`；L184断言`"task.title 最长200" not in merged.features + merged.acceptance`；L185断言`analysis_source_conflicts(old.gate_dump(), merged, [quote], changes=changes) == []`；L186断言`old.field_requirements[0].max_length == 200`。 调用`source_requirement`、`old.model_dump`、`reconcile`、`old.gate_dump`、`Requirement.model_validate`、`all`、`analysis_source_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_source_correction_keeps_compound_acceptance_and_plan_converges`（L189–L250）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L196断言`data["approval_status"] == "unapproved" and not data["execution_authorized"]`；L204断言`new_text != old_text`；L226断言`all(change["authorized"] and change["source_quote"] == quote for change in audit)`；L227断言`audit[1]["before"][1] == old_text`；L228断言`old_text not in merged.acceptance and new_text in merged.acceptance`；L229断言`merged.features == old.features and merged.facts == old.facts`；L230遍历`zip(old.field_requirements, merged.field_requirements)`；L232按`before_field.entity == "requests" and before_field.field == "title"`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`path.read_bytes`、`json.loads`、`Requirement.model_validate`、`old.model_dump`、`old_text.replace`、`reconcile`、`old.gate_dump`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejected_candidate_does_not_pollute_baseline_or_consume_fresh_source`（L253–L293）：接收`settings`、`store`、`plan`。 控制顺序：L276断言`state == before`；L277断言`rejected["requirement"] == old.gate_dump()`；L278断言`rejected["requirement_analysis_baseline"] == old.gate_dump()`；L279断言`rejected["requirement_source_count"] == 0`；L281断言`entry["before"] == entry["after"] == old.gate_dump()`；L282断言`"task.title 最长120" in entry["reconciled_candidate"]["features"]`；L284断言`seen[0]["fresh_user_corrections"] == seen[1]["fresh_user_corrections"]`；L285断言`seen[1]["current_requirement"] == old.gate_dump()`。后续分支沿下方源码相同行号继续阅读。 调用`source_requirement`、`new_run`、`Workflow`、`Gateway`、`old.gate_dump`、`json.loads`、`json.dumps`、`workflow.analyse`、`digest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejected_candidate_does_not_pollute_baseline_or_consume_fresh_source.Gateway`（L259–L263）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_rejected_candidate_does_not_pollute_baseline_or_consume_fresh_source.Gateway.complete`（L260–L263）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L261断言`schema is Requirement`。 调用`seen.append`、`len`、`conflicting`。 返回路径：L263的`conflicting(old) if len(seen) == 1 else old`。
- `test_autonomous_conflict_stops_in_existing_two_repair_budget_before_plan`（L297–L340）：接收`settings`、`store`、`plan`、`first_source_only`。 控制顺序：L314按`first_source_only`分支；L329断言`result["status"] == "BLOCKED"`；L330断言`result["pending"]["stage"] == "clarification"`；L331断言`result["pending"]["can_approve"] is False`；L332断言`gateway.calls == ["recommend:1", "recommend:2", "recommend:3"]`；L333断言`state["requirement_analysis_baseline"] == {}`；L334断言`state["requirement_source_count"] == 1`；L335断言`all(entry["after"] == {} for entry in state["requirement_ledger"])`。后续分支沿下方源码相同行号继续阅读。 调用`store.create_project`、`store.create_run`、`new_run`、`store.set_automation`、`Gateway`、`Runtime`、`runtime.tick`、`runtime.graph.get_state`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_autonomous_conflict_stops_in_existing_two_repair_budget_before_plan.Gateway`（L300–L312）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_autonomous_conflict_stops_in_existing_two_repair_budget_before_plan.Gateway.complete`（L301–L312）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L303断言`schema is Requirement`；L304按`len(self.calls) > 1`分支；L305断言`payload["resolution_feedback"]["stage"] == "clarification"`；L306断言`payload["resolution_feedback"]["analysis_diagnostics"]`；L307断言`payload["current_requirement"] == {}`；L309按`first_source_only`分支。 调用`self.calls.append`、`len`、`conflicting`、`source_requirement`。 返回路径：L312的`candidate`。
- `test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate`（L343–L380）：接收`settings`、`store`、`plan`。 控制顺序：L355断言`pending["stage"] == "clarification" and not pending["can_approve"]`；L372断言`result["status"] == "WAITING_REQUIREMENTS"`；L373断言`result["pending"]["can_approve"] is True`；L374断言`result["auto_mode"] is False`；L375断言`gateway.calls == ["requirement:2"]`；L376断言`state["requirement_analysis_diagnostics"] == []`；L377断言`state["requirement_source_count"] == 2`；L378断言`"task.title 最长120" not in state["requirement"]["features"]`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`Runtime`、`Bad`、`runtime.tick`、`store.get_run`、`decision`、`Fixed`、`runtime.graph.get_state`、`store.tx`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate.Bad`（L346–L349）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate.Bad.complete`（L347–L349）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L348断言`schema is Requirement`。 调用`conflicting`、`source_requirement`。 返回路径：L349的`conflicting(source_requirement())`。
- `test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate.Fixed`（L358–L365）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate.Fixed.complete`（L359–L365）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L361断言`schema is Requirement`；L362断言`payload["current_requirement"] == {}`；L363断言`payload["fresh_user_corrections"] == ["task.title 最长200，请修正分析"]`；L364断言`payload["resolution_feedback"]["analysis_diagnostics"]`。 调用`self.calls.append`、`source_requirement`。 返回路径：L365的`source_requirement()`。
- `test_legacy_checkpoint_keeps_gate_digest_and_confirmation_state`（L383–L414）：接收`settings`、`store`、`plan`、`monkeypatch`。 控制顺序：L409断言`result["status"] == "WAITING_REQUIREMENTS"`；L410断言`result["auto_mode"] is False`；L411断言`result["pending"]["gate_id"] != pending["gate_id"]`；L412断言`"analysis_diagnostics" not in result["pending"]["data"]`；L414断言`session.scalars(select(Approval)).all() == []`。 调用`source_requirement`、`new_run`、`monkeypatch.context`、`patch.setattr`、`Runtime`、`FixtureGateway`、`runtime.tick`、`store.get_run`、`decision`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_checkpoint_keeps_gate_digest_and_confirmation_state.legacy_analyse`（L388–L389）：接收`state`。 调用`old.gate_dump`。 返回路径：L389的`{"requirement": old.gate_dump()}`。
- `test_legacy_checkpoint_keeps_gate_digest_and_confirmation_state.Gateway`（L399–L404）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_legacy_checkpoint_keeps_gate_digest_and_confirmation_state.Gateway.complete`（L400–L404）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L401断言`schema is Requirement`；L402断言`payload["current_requirement"] == old.gate_dump()`；L403断言`payload["fresh_user_corrections"] == ["不修改，继续"]`。 调用`old.gate_dump`、`source_requirement`。 返回路径：L404的`source_requirement()`。
- `test_many_conflicts_keep_full_ledger_but_fit_existing_model_context`（L417–L471）：接收`settings`、`store`、`plan`。 控制顺序：L450断言`len(diagnostics) == 12`；L451断言`all(any(s["text"] == original for s in d["sources"]) for d in diagnostics)`；L453断言`len(json.dumps(feedback, ensure_ascii=False)) <= settings.max_context_chars // 5`；L454断言`original not in json.dumps(feedback, ensure_ascii=False)`；L455断言`all( "text" not in ref for d in diagnostics for s in d["sources"] for ref in s["user_…`；L460断言`len(json.dumps(outcome["resolution_feedback"]["analysis_diagnostics"], ensure_ascii=F…`；L465断言`seen[1]["rejected_analysis"]["sha256"] == digest(candidate.gate_dump())`；L466断言`seen[1]["current_requirement"] == {}`。后续分支沿下方源码相同行号继续阅读。 调用`requirement().model_copy`、`requirement`、`range`、`FieldRequirement`、`";".join`、`store.create_project`、`store.create_run`、`Workflow`、`Gateway`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_many_conflicts_keep_full_ledger_but_fit_existing_model_context.Gateway`（L435–L444）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_many_conflicts_keep_full_ledger_but_fit_existing_model_context.Gateway.complete`（L436–L444）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L438按`len(seen) == 2`分支；L443断言`len(request) < settings.max_context_chars == 100000`。 调用`seen.append`、`len`、`json.dumps`、`schema.model_json_schema`。 返回路径：L444的`candidate`。

</details>

**创建路径：** `tests/test_requirement_source_conflicts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L471。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20965`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_requirement_source_conflicts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3a5e22d35ba24e5de1c6251f0218d7458a02fee488f7b313ab62ae12daae6954"} -->
````python
# tests/test_requirement_source_conflicts.py
"""Analysis conflicts use clarification repair, never impossible Plan repair.

Recorded customer inputs are unapproved, read-only validator fixtures. Workflow
regressions below use independent synthetic requirements and a fixture gateway.
"""

import json
from pathlib import Path

import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from sqlalchemy import select

from workbench.domain import FieldRequirement, Plan, Requirement, digest
from workbench.flow import Workflow
from workbench.requirement_coverage import coverage_gaps, reconcile
from workbench.requirement_sources import analysis_feedback, analysis_source_conflicts
from workbench.runtime import Runtime
from workbench.store import Approval, Conflict


def source_requirement(*, questions=None):
    return requirement(questions).model_copy(
        update={
            "features": ["CRUD", "task.title 最长200"],
            "acceptance": ["task.title 最长200"],
            "field_requirements": [
                FieldRequirement(entity="task", field="title", kind="text", max_length=200)
            ],
        }
    )


def conflicting(old):
    proposed = old.model_copy(deep=True)
    proposed.features.append("task.title 最长120")
    return proposed


def test_recorded_200_vs_120_retains_original_sources_without_changing_fixture():
    path = (
        Path(__file__).parent
        / "fixtures/customer_design_diagnostics/dd7e5f2/python-unapproved-design.json"
    )
    original = path.read_bytes()
    data = json.loads(original)
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    old = Requirement.model_validate(data["requirement"])
    before = old.model_dump()
    proposed = old.model_copy(deep=True)
    proposed.features.append("requests.title 最长120")
    merged = reconcile(old.gate_dump(), proposed, [])
    diagnostics = analysis_source_conflicts(old.gate_dump(), merged, [])
    assert len(diagnostics) == 1
    conflict = diagnostics[0]
    assert conflict["target"] == {"entity": "requests", "field": "title"}
    assert conflict["attribute"] == "max_length"
    assert {source["expected"] for source in conflict["sources"]} == {120, 200}
    assert {(s["source"]["section"], s["source"]["index"]) for s in conflict["sources"]} == {
        ("field_requirements", 4),
        ("features", len(old.features)),
        ("acceptance", 1),
    }
    assert conflict["sources"][-1]["text"] == old.acceptance[1]
    assert old.model_dump() == before
    assert path.read_bytes() == original


@pytest.mark.parametrize("text", ["task.title 最大200字符", "task.title ≤200"])
def test_equivalent_restatement_is_not_a_conflict(text):
    old = source_requirement()
    proposed = old.model_copy(deep=True)
    proposed.features.append(text)
    merged = reconcile(old.gate_dump(), proposed, [])
    assert analysis_source_conflicts(old.gate_dump(), merged, []) == []
    assert text in merged.features


def test_ungrounded_description_has_no_user_authority_and_unknown_text_survives():
    old = source_requirement()
    proposed = conflicting(old)
    unknown = "标题沿用北极星规范，具体规则等待人工核对"
    proposed.features.append(unknown)
    human = ["task.title 最长200", "请智能推荐普通细节"]
    merged = reconcile(old.gate_dump(), proposed, [], [])
    diagnostics = analysis_source_conflicts(old.gate_dump(), merged, human, cursor=2)
    sources = diagnostics[0]["sources"]
    injected = next(s for s in sources if s["expected"] == 120)
    assert injected["origin"] == "model_analysis"
    assert injected["user_sources"] == [] and injected["correction_sources"] == []
    retained = next(s for s in sources if s["source"]["section"] == "acceptance")
    assert retained["user_sources"][0]["user_message_index"] == 0
    assert retained["user_sources"][0]["sha256"] == digest(human[0])
    assert "text" not in retained["user_sources"][0]
    assert unknown in merged.features


def test_first_analysis_cannot_override_unambiguous_original_user_constraint():
    candidate = source_requirement()
    candidate.field_requirements[0].max_length = 120
    candidate.features = ["CRUD", "task.title 最长120"]
    candidate.acceptance = ["task.title 最长120"]
    diagnostics = analysis_source_conflicts(None, candidate, ["task.title 最长200"], cursor=1)
    assert len(diagnostics) == 1
    source = next(s for s in diagnostics[0]["sources"] if s["origin"] == "user_input")
    assert source["source"] == {"section": "user_messages", "index": 0}
    assert source["expected"] == 200 and source["text"] == "task.title 最长200"
    assert candidate.field_requirements[0].max_length == 120


@pytest.mark.parametrize(
    "original", ["长度上限：task.title≤200", "task.标题最长200", "task.title最大200字符"]
)
def test_first_analysis_accepts_equivalent_original_constraint(original):
    assert analysis_source_conflicts(None, source_requirement(), [original], cursor=1) == []
    # Prove the alias really parsed; a positive result must not be an accidental
    # pass because the user source was ignored.
    wrong = source_requirement()
    wrong.field_requirements[0].max_length = 120
    wrong.features = wrong.acceptance = ["task.title 最长120"]
    diagnostics = analysis_source_conflicts(None, wrong, [original], cursor=1)
    assert any(s["origin"] == "user_input" for s in diagnostics[0]["sources"])


def test_first_analysis_fresh_explicit_correction_has_same_strict_authorization():
    candidate = source_requirement()
    candidate.field_requirements[0].max_length = 120
    candidate.features = candidate.acceptance = ["task.title 最长120"]
    human = ["task.title 最长200", "task.title max_length 改为120，task.title 最长120"]
    assert analysis_source_conflicts(None, candidate, human, cursor=1) == []
    # Two disagreeing fresh corrections are retained; their order picks no winner.
    human.append("task.title max_length 改为150，task.title 最长150")
    diagnostics = analysis_source_conflicts(None, candidate, human, cursor=1)
    assert {s["expected"] for s in diagnostics[0]["sources"]} == {120, 150, 200}
    assert {
        s["source"]["index"] for s in diagnostics[0]["sources"] if s["origin"] == "user_input"
    } == {0, 1, 2}


def test_unreliable_user_prose_is_not_marked_source_verified():
    candidate = conflicting(source_requirement())
    diagnostics = analysis_source_conflicts(None, candidate, ["请按团队标题约定处理"], cursor=1)
    assert diagnostics
    assert all(not s["user_sources"] for s in diagnostics[0]["sources"])
    assert all(s["origin"] != "user_input" for s in diagnostics[0]["sources"])
    assert (
        analysis_source_conflicts(None, source_requirement(), ["title 应该短一些"], cursor=1) == []
    )


def test_ambiguous_cross_entity_title_is_not_guessed():
    old = source_requirement()
    old.field_requirements.append(FieldRequirement(entity="other", field="title", max_length=120))
    old.features.append("title 最长150")
    assert analysis_source_conflicts(None, old, []) == []


def test_source_backed_correction_updates_all_obligations_without_guard_override():
    old = source_requirement()
    quote = "task.title max_length 改为120，task.title 最长120"
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "field_requirements",
            "key": "task.title.max_length",
            "replacement": 120,
            "source_quote": quote,
        },
        *[
            {
                "section": section,
                "key": "task.title 最长200",
                "replacement": "task.title 最长120",
                "source_quote": quote,
            }
            for section in ("features", "acceptance")
        ],
    ]
    changes = []
    merged = reconcile(old.gate_dump(), Requirement.model_validate(proposed), [quote], changes)
    assert all(change["authorized"] for change in changes)
    assert merged.field_requirements[0].max_length == 120
    assert "task.title 最长200" not in merged.features + merged.acceptance
    assert analysis_source_conflicts(old.gate_dump(), merged, [quote], changes=changes) == []
    assert old.field_requirements[0].max_length == 200


def test_recorded_source_correction_keeps_compound_acceptance_and_plan_converges():
    path = (
        Path(__file__).parent
        / "fixtures/customer_design_diagnostics/dd7e5f2/python-unapproved-design.json"
    )
    original = path.read_bytes()
    data = json.loads(original)
    assert data["approval_status"] == "unapproved" and not data["execution_authorized"]
    old = Requirement.model_validate(data["requirement"])
    before = old.model_dump()
    old_text = old.acceptance[1]
    new_text = old_text.replace(
        "requests/tasks 的 title≤200、detail≤3000",
        "requests 的 title≤120、detail≤3000；tasks 的 title≤200、detail≤3000",
    )
    assert new_text != old_text
    quote = (
        "将 requests.title max_length 改为120，tasks.title仍为200，其他限制不变。将验收文本改为："
        + new_text
    )
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "field_requirements",
            "key": "requests.title.max_length",
            "replacement": 120,
            "source_quote": quote,
        },
        {
            "section": "acceptance",
            "key": old_text,
            "replacement": new_text,
            "source_quote": quote,
        },
    ]
    audit = []
    merged = reconcile(old.gate_dump(), Requirement.model_validate(proposed), [quote], audit)
    assert all(change["authorized"] and change["source_quote"] == quote for change in audit)
    assert audit[1]["before"][1] == old_text
    assert old_text not in merged.acceptance and new_text in merged.acceptance
    assert merged.features == old.features and merged.facts == old.facts
    for before_field, after_field in zip(old.field_requirements, merged.field_requirements):
        expected = before_field.model_dump()
        if before_field.entity == "requests" and before_field.field == "title":
            expected["max_length"] = 120
        assert after_field.model_dump() == expected
    assert analysis_source_conflicts(old.gate_dump(), merged, [quote], changes=audit) == []
    recorded_plan = Plan.model_validate(data["candidate_plan"])
    corrected_plan = recorded_plan.model_copy(deep=True)
    next(
        field
        for entity in corrected_plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "title"
    ).max_length = 120
    # Both inputs remain offline validator data; no fixture is approved/executed.
    diagnostics = []
    residual = coverage_gaps(merged, corrected_plan, diagnostics=diagnostics)
    assert residual == coverage_gaps(old, recorded_plan) == []
    assert not any(item.get("attribute") == "max_length" for item in diagnostics)
    assert old.model_dump() == before and path.read_bytes() == original


def test_rejected_candidate_does_not_pollute_baseline_or_consume_fresh_source(
    settings, store, plan
):
    old = source_requirement()
    seen = []

    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            assert schema is Requirement
            seen.append(payload)
            return conflicting(old) if len(seen) == 1 else old

    run = new_run(store)
    workflow = Workflow(settings, store, Gateway(plan))
    state = {
        "run_id": run,
        "template": "python-basic",
        "round": 2,
        "requirement": old.gate_dump(),
        "requirement_source_count": 0,
    }
    before = json.loads(json.dumps(state))
    rejected = workflow.analyse(state)
    assert state == before
    assert rejected["requirement"] == old.gate_dump()
    assert rejected["requirement_analysis_baseline"] == old.gate_dump()
    assert rejected["requirement_source_count"] == 0
    entry = rejected["requirement_ledger"][-1]
    assert entry["before"] == entry["after"] == old.gate_dump()
    assert "task.title 最长120" in entry["reconciled_candidate"]["features"]
    accepted = workflow.analyse({**state, **rejected, "round": 3})
    assert seen[0]["fresh_user_corrections"] == seen[1]["fresh_user_corrections"]
    assert seen[1]["current_requirement"] == old.gate_dump()
    assert seen[1]["rejected_analysis"] == {
        "ledger_round": 2,
        "sha256": digest(entry["reconciled_candidate"]),
    }
    assert accepted["requirement_analysis_diagnostics"] == []
    assert accepted["requirement_analysis_baseline"] == {}
    assert accepted["requirement_source_count"] == 1
    assert "task.title 最长120" not in accepted["requirement"]["features"]


@pytest.mark.parametrize("first_source_only", [False, True])
def test_autonomous_conflict_stops_in_existing_two_repair_budget_before_plan(
    settings, store, plan, first_source_only
):
    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement, "Contradictory analysis must never reach Plan"
            if len(self.calls) > 1:
                assert payload["resolution_feedback"]["stage"] == "clarification"
                assert payload["resolution_feedback"]["analysis_diagnostics"]
                assert payload["current_requirement"] == {}
            candidate = conflicting(source_requirement())
            if first_source_only:
                candidate.field_requirements[0].max_length = 120
                candidate.features = candidate.acceptance = ["task.title 最长120"]
            return candidate

    if first_source_only:
        project = store.create_project("explicit-source", "explicit-source-project")
        run = store.create_run(
            project["id"],
            {"requirement": "task.title 最长200", "template": "python-basic"},
            "explicit-source-run",
        )["run_id"]
    else:
        run = new_run(store)
    store.set_automation(run, True, "smart")
    gateway = Gateway(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        state = runtime.graph.get_state({"configurable": {"thread_id": run}}).values
    result = store.get_run(run)
    assert result["status"] == "BLOCKED", result
    assert result["pending"]["stage"] == "clarification"
    assert result["pending"]["can_approve"] is False
    assert gateway.calls == ["recommend:1", "recommend:2", "recommend:3"]
    assert state["requirement_analysis_baseline"] == {}
    assert state["requirement_source_count"] == 1
    assert all(entry["after"] == {} for entry in state["requirement_ledger"])
    with store.tx() as session:
        assert session.scalars(select(Approval)).all() == []
    with pytest.raises(Conflict):
        decision(store, run)
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()


def test_checkpoint_resume_repairs_rejected_first_candidate_and_returns_manual_gate(
    settings, store, plan
):
    class Bad(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            assert schema is Requirement
            return conflicting(source_requirement())

    run = new_run(store)
    with Runtime(settings, store, Bad(plan)) as runtime:
        runtime.tick()
    pending = store.get_run(run)["pending"]
    assert pending["stage"] == "clarification" and not pending["can_approve"]
    decision(store, run, "answer", "task.title 最长200，请修正分析")

    class Fixed(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            assert schema is Requirement
            assert payload["current_requirement"] == {}
            assert payload["fresh_user_corrections"] == ["task.title 最长200，请修正分析"]
            assert payload["resolution_feedback"]["analysis_diagnostics"]
            return source_requirement()

    gateway = Fixed(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        state = runtime.graph.get_state({"configurable": {"thread_id": run}}).values
    result = store.get_run(run)
    assert result["status"] == "WAITING_REQUIREMENTS", result
    assert result["pending"]["can_approve"] is True
    assert result["auto_mode"] is False
    assert gateway.calls == ["requirement:2"]
    assert state["requirement_analysis_diagnostics"] == []
    assert state["requirement_source_count"] == 2
    assert "task.title 最长120" not in state["requirement"]["features"]
    with store.tx() as session:
        assert session.scalars(select(Approval)).all() == []


def test_legacy_checkpoint_keeps_gate_digest_and_confirmation_state(
    settings, store, plan, monkeypatch
):
    old = source_requirement(questions=["是否修改？"])

    def legacy_analyse(self, state):
        return {"requirement": old.gate_dump()}

    run = new_run(store)
    with monkeypatch.context() as patch:
        patch.setattr(Workflow, "analyse", legacy_analyse)
        with Runtime(settings, store, FixtureGateway(plan)) as runtime:
            runtime.tick()
    pending = store.get_run(run)["pending"]
    decision(store, run, "answer", "不修改，继续")

    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            assert schema is Requirement
            assert payload["current_requirement"] == old.gate_dump()
            assert payload["fresh_user_corrections"] == ["不修改，继续"]
            return source_requirement()

    with Runtime(settings, store, Gateway(plan)) as runtime:
        runtime.tick()
    result = store.get_run(run)
    assert result["status"] == "WAITING_REQUIREMENTS", result
    assert result["auto_mode"] is False
    assert result["pending"]["gate_id"] != pending["gate_id"]
    assert "analysis_diagnostics" not in result["pending"]["data"]
    with store.tx() as session:
        assert session.scalars(select(Approval)).all() == []


def test_many_conflicts_keep_full_ledger_but_fit_existing_model_context(settings, store, plan):
    candidate = requirement().model_copy(
        update={
            "features": [f"task.field_{index} 最长120" for index in range(12)],
            "acceptance": ["录入字段值"],
            "field_requirements": [
                FieldRequirement(entity="task", field=f"field_{index}", max_length=120)
                for index in range(12)
            ],
        }
    )
    original = "背景说明。" * 3800 + ";".join(f"task.field_{index} 最长200" for index in range(12))
    project = store.create_project("bounded-analysis", "bounded-project")
    run = store.create_run(
        project["id"], {"requirement": original, "template": "python-basic"}, "bounded-run"
    )["run_id"]
    seen = []

    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            seen.append(payload)
            if len(seen) == 2:
                # Match the gateway's complete-request accounting, including
                # schema/instruction, without a provider call or raising limits.
                request = instruction + json.dumps(schema.model_json_schema(), ensure_ascii=False)
                request += json.dumps(payload, ensure_ascii=False)
                assert len(request) < settings.max_context_chars == 100000
            return candidate

    workflow = Workflow(settings, store, Gateway(plan))
    state = {"run_id": run, "template": "python-basic", "round": 1}
    rejected = workflow.analyse(state)
    diagnostics = rejected["requirement_analysis_diagnostics"]
    assert len(diagnostics) == 12
    assert all(any(s["text"] == original for s in d["sources"]) for d in diagnostics)
    feedback = analysis_feedback(diagnostics, max_chars=settings.max_context_chars // 5)
    assert len(json.dumps(feedback, ensure_ascii=False)) <= settings.max_context_chars // 5
    assert original not in json.dumps(feedback, ensure_ascii=False)
    assert all(
        "text" not in ref for d in diagnostics for s in d["sources"] for ref in s["user_sources"]
    )
    workflow.gate = lambda *args, **kwargs: {"decision": "recommend"}
    outcome = workflow.requirements({**state, **rejected})
    assert (
        len(json.dumps(outcome["resolution_feedback"]["analysis_diagnostics"], ensure_ascii=False))
        <= 16000
    )
    workflow.analyse({**state, **rejected, **outcome})
    assert seen[1]["rejected_analysis"]["sha256"] == digest(candidate.gate_dump())
    assert seen[1]["current_requirement"] == {}
    assert store.messages(run)[0]["content"] == original
    ledger = json.loads(
        (workflow.product(state).parent / "requirement-ledger.json").read_text(encoding="utf-8")
    )
    assert len(ledger[-1]["analysis_diagnostics"]) == 12
````
