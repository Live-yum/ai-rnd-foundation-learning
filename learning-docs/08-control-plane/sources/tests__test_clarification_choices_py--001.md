# tests/test_clarification_choices.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `question`（L13–L27）：接收`kind`、`**updates`。 返回路径：L14的`{ "id": "audience", "prompt": "谁会使用第一版？", "kind": kind, "options": [ {"id": "team", "label…`。
- `waiting`（L30–L45）：接收`store`、`questions`。 调用`new_run`、`store.claim`、`question`、`requirement([item["prompt"] for item in items]).model_dump`、`requirement`、`store.gate`、`store.finish`。 返回路径：L45的`run_id, gate`。
- `submission`（L48–L57）：接收`gate`、`answers`、`**updates`。 返回路径：L49的`{ "gate_id": gate["gate_id"], "version": gate["version"], "digest": gate["digest"], "actio…`。
- `test_selected_labels_custom_text_and_idempotence_are_durable`（L60–L83）：接收`store`。 控制顺序：L74断言`store.submit(run_id, body, key) == first`；L76断言`len(history) == 2`；L77断言`history[-1] == { "role": "user", "content": "谁会使用第一版？\n- 客服成员 + 团队主管\n补充：主管只能查看自己团队 👋…`；L83断言`len(store.messages(run_id)) == 2`。 调用`waiting`、`submission`、`str`、`uuid.uuid4`、`store.submit`、`store.messages`、`len`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_identity_never_consumes_current_gate`（L87–L92）：接收`store`、`updates`。 控制顺序：L91断言`store.get_run(run_id)["pending"] == gate`；L92断言`len(store.messages(run_id)) == 1`。 调用`waiting`、`pytest.raises`、`store.submit`、`submission`、`str`、`uuid.uuid4`、`store.get_run`、`len`、`store.messages`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_selections_do_not_queue_or_approve`（L104–L110）：接收`store`、`answer`。 控制顺序：L108断言`store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"`；L109断言`len(store.messages(run_id)) == 1`；L110断言`store.claim() is None`。 调用`waiting`、`pytest.raises`、`store.submit`、`submission`、`str`、`uuid.uuid4`、`store.get_run`、`len`、`store.messages`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_multiselect_preserves_selected_labels_and_custom_answer`（L113–L132）：接收`store`。 控制顺序：L129断言`"- 客服成员 + 团队主管\n- 只有我自己\n补充：分两期上线" in store.messages(run_id)[-1]["content"]`。 调用`waiting`、`question`、`store.submit`、`submission`、`str`、`uuid.uuid4`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_text_only_answer_remains_supported_for_legacy_and_open_intent`（L135–L139）：接收`store`。 控制顺序：L139断言`store.messages(run_id)[-1]["content"] == body["text"]`。 调用`waiting`、`store.submit`、`str`、`uuid.uuid4`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_question_and_optional_question_rules`（L142–L146）：接收`store`。 控制顺序：L146断言`"其他补充\n" not in store.messages(run_id)[-1]["content"]`。 调用`question`、`waiting`、`store.submit`、`submission`、`str`、`uuid.uuid4`、`store.messages`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_question_is_not_a_valid_model_result`（L157–L159）：接收`value`。 调用`pytest.raises`、`ClarificationQuestion.model_validate`、`question`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structured_question_must_match_real_blocking_question`（L162–L171）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L169断言`not req.ready`；L170断言`req.gate_dump()["question_items"][0]["prompt"] == req.questions[0]`；L171断言`"question_items" not in requirement().gate_dump()`。 调用`requirement().model_dump`、`requirement`、`pytest.raises`、`Requirement.model_validate`、`question`、`req.gate_dump`、`requirement().gate_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_answers_cannot_be_control_action_or_forged_label`（L174–L193）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`ResumeInput`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_answered_choices_do_not_drop_existing_explicit_scope`（L196–L203）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L202断言`{"审计", "工单分配"} <= set(result.features)`；L203断言`result.facts["roles"] == ["成员", "主管"]`。 调用`requirement().model_dump`、`requirement`、`reconcile`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stage_events_are_actual_serial_nodes_and_waiting_gate`（L206–L217）：接收`settings`、`store`、`plan`。 控制顺序：L209断言`worker.tick()`；L211断言`[(event["name"], event["phase"]) for event in events] == [ ("analyse", "started"), ("…`；L217断言`store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"`。 调用`new_run`、`Runtime`、`FixtureGateway`、`worker.tick`、`store.events`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_structured_questions_cannot_hide_another_blocking_question`（L220–L223）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`requirement([question()["prompt"], "数据由谁访问？"]).model_dump`、`requirement`、`question`、`pytest.raises`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_clarification_choices.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L223。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7930`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_clarification_choices.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2819e98f5dab64b1238bfd9c19b6f1c26b239616f78dc34d113c024294fb2180"} -->
````python
# tests/test_clarification_choices.py
import uuid

import pytest
from conftest import FixtureGateway, new_run, requirement
from pydantic import ValidationError

from workbench.domain import ClarificationQuestion, Requirement, ResumeInput
from workbench.requirement_coverage import reconcile
from workbench.runtime import Runtime
from workbench.store import Conflict


def question(kind="single", **updates):
    return {
        "id": "audience",
        "prompt": "谁会使用第一版？",
        "kind": kind,
        "options": [
            {"id": "team", "label": "客服成员 + 团队主管", "description": "内部团队"},
            {"id": "personal", "label": "只有我自己", "description": ""},
        ]
        if kind != "text"
        else [],
        "required": True,
        "allow_other": True,
        **updates,
    }


def waiting(store, questions=None):
    run_id = new_run(store)
    job = store.claim()
    items = questions or [question()]
    req = requirement([item["prompt"] for item in items]).model_dump()
    req["question_items"] = items
    gate = store.gate(
        run_id,
        "clarification",
        1,
        {"requirement": req, "ready": False},
        ["answer", "reject", "recommend"],
        False,
    )
    store.finish(job, "WAITING_CLARIFICATION", pending=gate)
    return run_id, gate


def submission(gate, answers=None, **updates):
    return {
        "gate_id": gate["gate_id"],
        "version": gate["version"],
        "digest": gate["digest"],
        "action": "answer",
        "text": "保留原来已确定的审计功能",
        "answers": answers or [{"question_id": "audience", "option_ids": ["team"], "text": ""}],
        **updates,
    }


def test_selected_labels_custom_text_and_idempotence_are_durable(store):
    run_id, gate = waiting(store)
    body = submission(
        gate,
        [
            {
                "question_id": "audience",
                "option_ids": ["team"],
                "text": "主管只能查看自己团队 👋",
            }
        ],
    )
    key = str(uuid.uuid4())
    first = store.submit(run_id, body, key)
    assert store.submit(run_id, body, key) == first
    history = store.messages(run_id)
    assert len(history) == 2
    assert history[-1] == {
        "role": "user",
        "content": "谁会使用第一版？\n- 客服成员 + 团队主管\n补充：主管只能查看自己团队 👋\n其他补充：保留原来已确定的审计功能",
    }
    with pytest.raises(Conflict):
        store.submit(run_id, {**body, "text": "changed"}, key)
    assert len(store.messages(run_id)) == 2


@pytest.mark.parametrize("updates", [{"version": 2}, {"digest": "f" * 64}, {"gate_id": "a" * 64}])
def test_stale_identity_never_consumes_current_gate(store, updates):
    run_id, gate = waiting(store)
    with pytest.raises(Conflict):
        store.submit(run_id, submission(gate, **updates), str(uuid.uuid4()))
    assert store.get_run(run_id)["pending"] == gate
    assert len(store.messages(run_id)) == 1


@pytest.mark.parametrize(
    "answer",
    [
        {"question_id": "attacker", "option_ids": ["team"]},
        {"question_id": "audience", "option_ids": ["unknown"]},
        {"question_id": "audience", "option_ids": ["team", "personal"]},
        {"question_id": "audience", "option_ids": []},
    ],
)
def test_invalid_selections_do_not_queue_or_approve(store, answer):
    run_id, gate = waiting(store)
    with pytest.raises(Conflict):
        store.submit(run_id, submission(gate, [answer]), str(uuid.uuid4()))
    assert store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"
    assert len(store.messages(run_id)) == 1
    assert store.claim() is None


def test_multiselect_preserves_selected_labels_and_custom_answer(store):
    run_id, gate = waiting(store, [question("multiple")])
    store.submit(
        run_id,
        submission(
            gate,
            [
                {
                    "question_id": "audience",
                    "option_ids": ["team", "personal"],
                    "text": "分两期上线",
                }
            ],
        ),
        str(uuid.uuid4()),
    )
    assert (
        "- 客服成员 + 团队主管\n- 只有我自己\n补充：分两期上线"
        in store.messages(run_id)[-1]["content"]
    )


def test_text_only_answer_remains_supported_for_legacy_and_open_intent(store):
    run_id, gate = waiting(store)
    body = {"gate_id": gate["gate_id"], "action": "answer", "text": "我想要完全不同的第三种方案"}
    store.submit(run_id, body, str(uuid.uuid4()))
    assert store.messages(run_id)[-1]["content"] == body["text"]


def test_required_question_and_optional_question_rules(store):
    optional = question("text", id="extra", prompt="其他补充", required=False)
    run_id, gate = waiting(store, [question(), optional])
    store.submit(run_id, submission(gate), str(uuid.uuid4()))
    assert "其他补充\n" not in store.messages(run_id)[-1]["content"]


@pytest.mark.parametrize(
    "value",
    [
        {"kind": "single", "options": [{"id": "only", "label": "只有一个"}]},
        {"options": [{"id": "same", "label": "一"}, {"id": "same", "label": "二"}]},
        {"kind": "text"},
    ],
)
def test_malformed_question_is_not_a_valid_model_result(value):
    with pytest.raises(ValidationError):
        ClarificationQuestion.model_validate({**question(), **value})


def test_structured_question_must_match_real_blocking_question():
    data = requirement().model_dump()
    with pytest.raises(ValidationError):
        Requirement.model_validate({**data, "question_items": [question()]})
    req = Requirement.model_validate(
        {**data, "questions": [question()["prompt"]], "question_items": [question()]}
    )
    assert not req.ready
    assert req.gate_dump()["question_items"][0]["prompt"] == req.questions[0]
    assert "question_items" not in requirement().gate_dump()


def test_answers_cannot_be_control_action_or_forged_label():
    with pytest.raises(ValidationError):
        ResumeInput(
            gate_id="a" * 64,
            action="approve",
            approved=True,
            answers=[{"question_id": "audience", "option_ids": ["team"]}],
        )
    with pytest.raises(ValidationError):
        ResumeInput(
            gate_id="a" * 64,
            action="answer",
            answers=[
                {
                    "question_id": "audience",
                    "option_ids": ["team"],
                    "label": "替换服务端标签",
                }
            ],
        )


def test_answered_choices_do_not_drop_existing_explicit_scope():
    before = requirement().model_dump()
    before["features"] = ["审计", "工单分配"]
    before["facts"] = {"roles": ["成员", "主管"]}
    candidate = requirement()
    result = reconcile(before, candidate, ["谁会使用第一版？\n- 客服成员 + 团队主管"])
    assert {"审计", "工单分配"} <= set(result.features)
    assert result.facts["roles"] == ["成员", "主管"]


def test_stage_events_are_actual_serial_nodes_and_waiting_gate(settings, store, plan):
    run_id = new_run(store)
    with Runtime(settings, store, FixtureGateway(plan, require_question=True)) as worker:
        assert worker.tick()
    events = [event["data"] for event in store.events(run_id) if event["kind"] == "stage"]
    assert [(event["name"], event["phase"]) for event in events] == [
        ("analyse", "started"),
        ("analyse", "completed"),
        ("requirements", "started"),
        ("requirements", "waiting"),
    ]
    assert store.get_run(run_id)["status"] == "WAITING_CLARIFICATION"


def test_partial_structured_questions_cannot_hide_another_blocking_question():
    data = requirement([question()["prompt"], "数据由谁访问？"]).model_dump()
    with pytest.raises(ValidationError):
        Requirement.model_validate({**data, "question_items": [question()]})
````
