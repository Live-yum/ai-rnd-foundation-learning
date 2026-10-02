# tests/test_guided_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.conversation`、`workbench.domain`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_control_words_are_not_sent_as_user_answers`（L14–L15）：接收`value`。 控制顺序：L15断言`command_word(value) == "批准"`。 调用`command_word`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_intelligent_action_is_an_explicit_permission`（L18–L22）：接收`store`。 控制顺序：L22断言`not store.get_run(run)["auto_mode"]`。 调用`new_run`、`pytest.raises`、`store.set_automation`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_more_than_ten_manual_rounds_then_continue_same_run`（L25–L43）：接收`settings`、`store`、`plan`。 控制顺序：L36遍历`range(13)`；L38断言`store.get_run(run)["status"] == "WAITING_CLARIFICATION"`；L41断言`store.get_run(run)["status"] == "WAITING_REQUIREMENTS"`；L42断言`len(store.messages(run)) == 14`；L43断言`store.get_run(run)["error"] is None`。 调用`Questions`、`new_run`、`Runtime`、`range`、`worker.tick`、`store.get_run`、`decision`、`len`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_more_than_ten_manual_rounds_then_continue_same_run.Questions`（L26–L31）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_more_than_ten_manual_rounds_then_continue_same_run.Questions.complete`（L27–L31）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L28按`schema is Requirement`分支。 调用`self.calls.append`、`requirement`、`len`、`super().complete`、`super`。 返回路径：L30的`requirement(["补充核心边界"] if len(self.calls) <= 13 else [])`；L31的`super().complete(run, key, instruction, payload, schema)`。
- `test_smart_from_any_gate_finishes_without_another_user_input`（L47–L71）：接收`settings`、`store`、`plan`、`stage`。 控制顺序：L52按`stage in {"design", "delivery"}`分支；L55按`stage == "delivery"`分支；L58断言`store.get_run(run)["pending"]["stage"] == stage`；L64断言`state["status"] == "READY"`；L65断言`state["auto_mode"] is True and state["pending"] is None`；L66断言`state["result"]["cleanroom"]["passed"] is True`；L69断言`any(x.actor == "delegated-ai" for x in approvals)`；L71断言`not any(m["content"] == "智能推荐" for m in store.messages(run))`。 调用`FixtureGateway`、`new_run`、`Runtime`、`worker.tick`、`decision`、`store.get_run`、`store.set_automation`、`str`、`uuid.uuid4`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_initial_smart_selection_is_retained`（L74–L95）：接收`settings`、`store`、`plan`。 控制顺序：L94断言`state["status"] == "READY"`；L95断言`state["options"]["frontend"] == "api-only"`。 调用`store.create_project`、`store.create_run`、`Runtime`、`FixtureGateway`、`worker.tick`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smart_does_not_loop_or_hide_unsupported_requirements`（L98–L113）：接收`settings`、`store`、`plan`。 控制顺序：L111断言`store.get_run(run)["status"] == "BLOCKED"`；L112断言`len(g.calls) <= 3`；L113断言`not (settings.data_dir / "runs" / run / "delivery.zip").exists()`。 调用`Unsupported`、`new_run`、`store.set_automation`、`str`、`uuid.uuid4`、`Runtime`、`worker.tick`、`store.get_run`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smart_does_not_loop_or_hide_unsupported_requirements.Unsupported`（L99–L104）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_smart_does_not_loop_or_hide_unsupported_requirements.Unsupported.complete`（L100–L104）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 调用`self.calls.append`、`requirement().model_copy`、`requirement`。 返回路径：L102的`requirement().model_copy( update={"questions": ["外部付费采集"], "unsupported": ["payment-system…`。
- `test_optional_positive_round_limit_pauses_and_resumes_without_loss`（L116–L130）：接收`settings`、`store`、`plan`。 控制顺序：L124断言`store.get_run(run)["status"] == "PAUSED_LIMIT"`；L129断言`store.get_run(run)["status"] == "WAITING_REQUIREMENTS"`；L130断言`store.messages(run)[-1]["content"] == "最后明确的回答必须保留"`。 调用`FixtureGateway`、`new_run`、`Runtime`、`worker.tick`、`decision`、`store.get_run`、`store.retry`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_review_model_does_not_replace_executable_tests`（L133–L154）：接收`settings`、`store`、`plan`。 控制顺序：L152断言`state["status"] == "READY"`；L153断言`any(key.startswith("review:") for key in g.calls)`；L154断言`state["result"]["cleanroom"]["passed"]`。 调用`Reviewer`、`new_run`、`store.set_automation`、`Runtime`、`worker.tick`、`store.get_run`、`any`、`key.startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_review_model_does_not_replace_executable_tests.Reviewer`（L136–L144）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_optional_review_model_does_not_replace_executable_tests.Reviewer.complete`（L137–L144）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L138按`schema is ModelReview`分支；L139断言`payload["independent_evidence"]["passed"] is True`。 调用`self.calls.append`、`ModelReview`、`super().complete`、`super`。 返回路径：L141的`ModelReview( summary="审阅备注，不假装执行测试", observations=[], uncovered_requirements=[] )`；L144的`super().complete(run, key, instruction, payload, schema)`。

</details>

**创建路径：** `tests/test_guided_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L154。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6181`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_guided_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "80926e09aafc08296c2314f10a402f5a23f61005bbb3a6bc1fbb86c57a004968"} -->
````python
# tests/test_guided_workflow.py
import uuid

import pytest
from conftest import FixtureGateway, decision, new_run, requirement
from sqlalchemy import select

from workbench.conversation import command_word
from workbench.domain import ModelReview, Requirement
from workbench.runtime import Runtime
from workbench.store import Approval, Conflict


@pytest.mark.parametrize("value", ["批准", "“批准”", '"批准"', "'批准'", "「批准」", " `批准` "])
def test_control_words_are_not_sent_as_user_answers(value):
    assert command_word(value) == "批准"


def test_intelligent_action_is_an_explicit_permission(store):
    run = new_run(store)
    with pytest.raises(Conflict):
        store.set_automation(run, True, "")
    assert not store.get_run(run)["auto_mode"]


def test_more_than_ten_manual_rounds_then_continue_same_run(settings, store, plan):
    class Questions(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is Requirement:
                self.calls.append(key)
                return requirement(["补充核心边界"] if len(self.calls) <= 13 else [])
            return super().complete(run, key, instruction, payload, schema)

    gateway = Questions(plan)
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        for index in range(13):
            worker.tick()
            assert store.get_run(run)["status"] == "WAITING_CLARIFICATION"
            decision(store, run, "answer", f"具体补充 {index}")
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
    assert len(store.messages(run)) == 14
    assert store.get_run(run)["error"] is None


@pytest.mark.parametrize("stage", ["clarification", "requirements", "design", "delivery"])
def test_smart_from_any_gate_finishes_without_another_user_input(settings, store, plan, stage):
    gateway = FixtureGateway(plan, require_question=stage == "clarification")
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        if stage in {"design", "delivery"}:
            decision(store, run)
            worker.tick()
        if stage == "delivery":
            decision(store, run)
            worker.tick()
        assert store.get_run(run)["pending"]["stage"] == stage
        store.set_automation(run, True, str(uuid.uuid4()))
    # Close/reopen to prove automation consent and the human interrupt persist.
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["auto_mode"] is True and state["pending"] is None
    assert state["result"]["cleanroom"]["passed"] is True
    with store.tx() as s:
        approvals = list(s.scalars(select(Approval)))
        assert any(x.actor == "delegated-ai" for x in approvals)
    # Recommend is not a fake user natural-language message.
    assert not any(m["content"] == "智能推荐" for m in store.messages(run))


def test_initial_smart_selection_is_retained(settings, store, plan):
    project = store.create_project("smart", "project")
    run = store.create_run(
        project["id"],
        {
            "requirement": "个人CRUD",
            "template": "python-basic",
            "selection": {
                "template": "python-basic",
                "backend": "fastapi",
                "frontend": "api-only",
                "database": "sqlite",
            },
            "intelligent": True,
        },
        "run",
    )["run_id"]
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["options"]["frontend"] == "api-only"


def test_smart_does_not_loop_or_hide_unsupported_requirements(settings, store, plan):
    class Unsupported(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            return requirement().model_copy(
                update={"questions": ["外部付费采集"], "unsupported": ["payment-system"]}
            )

    g = Unsupported(plan)
    run = new_run(store)
    store.set_automation(run, True, str(uuid.uuid4()))
    with Runtime(settings, store, g) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "BLOCKED"
    assert len(g.calls) <= 3
    assert not (settings.data_dir / "runs" / run / "delivery.zip").exists()


def test_optional_positive_round_limit_pauses_and_resumes_without_loss(settings, store, plan):
    settings.max_rounds = 1
    g = FixtureGateway(plan, require_question=True)
    run = new_run(store)
    with Runtime(settings, store, g) as worker:
        worker.tick()
        decision(store, run, "answer", "最后明确的回答必须保留")
        worker.tick()
        assert store.get_run(run)["status"] == "PAUSED_LIMIT"
    settings.max_rounds = 0
    store.retry(run, "resume-same-run")
    with Runtime(settings, store, g) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
    assert store.messages(run)[-1]["content"] == "最后明确的回答必须保留"


def test_optional_review_model_does_not_replace_executable_tests(settings, store, plan):
    settings.model_review = True

    class Reviewer(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is ModelReview:
                assert payload["independent_evidence"]["passed"] is True
                self.calls.append(key)
                return ModelReview(
                    summary="审阅备注，不假装执行测试", observations=[], uncovered_requirements=[]
                )
            return super().complete(run, key, instruction, payload, schema)

    g = Reviewer(plan)
    run = new_run(store)
    store.set_automation(run, True, "consent")
    with Runtime(settings, store, g) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert any(key.startswith("review:") for key in g.calls)
    assert state["result"]["cleanroom"]["passed"]
````
