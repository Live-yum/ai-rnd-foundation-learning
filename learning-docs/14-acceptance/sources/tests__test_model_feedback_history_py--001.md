# tests/test_model_feedback_history.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_failed_schema_has_safe_paths_trace_attempt_and_no_provider_values`（L15–L65）：接收`store`。 控制顺序：L50断言`len(failed) == 2`；L51断言`[item["diagnostic"]["attempt"] for item in failed] == [1, 2]`；L52遍历`failed`；L53断言`item["content"] == ""`；L55断言`diagnostic["trace_id"] == item["response_id"]`；L56断言`diagnostic["phase"] == "response_validation"`；L57断言`diagnostic["retry_hint"]`；L58断言`any( item["path"] == ["summary"] and item["type"] == "string_type" for item in diagno…`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`SecretStr`、`ModelGateway`、`httpx.MockTransport`、`pytest.raises`、`gateway.complete`、`store.transcript`、`item.get`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_schema_has_safe_paths_trace_attempt_and_no_provider_values.handler`（L21–L43）：接收`request`。 调用`httpx.Response`、`json.dumps`。 返回路径：L23的`httpx.Response( 200, json={ "id": "fixture", "model": "offline", "object": "chat.completio…`。
- `test_gate_questions_choices_gaps_and_exact_answer_survive_submit_failure_and_restart`（L68–L125）：接收`store`。 控制顺序：L98断言`store.submit(run, payload, "answer-once") == first`；L105断言`len(historical) == 1`；L107遍历`[ "参与者将通过哪种入口报名？", "登录后报名", "模板不支持匿名公开报名页", "原始报名目标需要明确入口", "已认证业…`；L114断言`expected in text`；L115断言`sum(item["content"] == answer for item in messages) == 1`；L116断言`messages.index(historical[0]) < next( index for index, item in enumerate(messages) if…`；L119断言`restored.get_run(run)["pending"] is None`；L120断言`"不代表当前仍未解决" in text`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`store.gate`、`store.claim`、`store.finish`、`store.submit`、`Store`、`restored.transcript`、`item.get`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_root_schema_failure_reports_only_allowlisted_validator_message`（L128–L147）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L146断言`details[0]["message"] == "结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题"`；L147断言`details[0]["path"] == []`。 调用`pytest.raises`、`Requirement.model_validate`、`schema_diagnostics`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_feedback_history.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L147。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5811`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_feedback_history.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "87daf731b2709c45e3aeb19ce279b92d8edf7076eb06fe173f15e2ed99c29433"} -->
````python
# tests/test_model_feedback_history.py
"""Provider failures and gate history remain actionable without exposing raw responses."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from workbench.domain import ModelReview
from workbench.llm import ModelFailure, ModelGateway
from workbench.store import Store


def test_failed_schema_has_safe_paths_trace_attempt_and_no_provider_values(store):
    run = new_run(store)
    store.settings.base_url = "https://api.openai.com/v1"
    store.settings.model = "offline"
    store.settings.api_key = SecretStr("secret-fixture-value")

    def handler(request):
        # Both arbitrary extra-field names and invalid values are private.
        return httpx.Response(
            200,
            json={
                "id": "fixture",
                "model": "offline",
                "object": "chat.completion",
                "created": 0,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(
                                {"summary": 123, "secret-fixture-value": "private-response-canary"}
                            ),
                        },
                    }
                ],
            },
        )

    gateway = ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True)
    with pytest.raises(ModelFailure):
        gateway.complete(run, "review:diagnostic", "JSON", {}, ModelReview)
    messages = store.transcript(run)["messages"]
    failed = [item for item in messages if item.get("validation") == "failed"]
    assert len(failed) == 2
    assert [item["diagnostic"]["attempt"] for item in failed] == [1, 2]
    for item in failed:
        assert item["content"] == ""
        diagnostic = item["diagnostic"]
        assert diagnostic["trace_id"] == item["response_id"]
        assert diagnostic["phase"] == "response_validation"
        assert diagnostic["retry_hint"]
        assert any(
            item["path"] == ["summary"] and item["type"] == "string_type"
            for item in diagnostic["details"]
        )
    safe = json.dumps(messages)
    assert "secret-fixture-value" not in safe
    assert "private-response-canary" not in safe
    assert not any(item.get("validation") == "validated" for item in messages)


def test_gate_questions_choices_gaps_and_exact_answer_survive_submit_failure_and_restart(store):
    run = new_run(store)
    gate = store.gate(
        run,
        "clarification",
        1,
        {
            "requirement": {
                "questions": ["参与者将通过哪种入口报名？"],
                "question_items": [
                    {
                        "id": "registration_scope",
                        "prompt": "参与者将通过哪种入口报名？",
                        "options": [{"id": "authenticated", "label": "登录后报名"}],
                    }
                ],
                "unsupported": ["模板不支持匿名公开报名页"],
            },
            "capability_conflicts": [
                {"message": "原始报名目标需要明确入口", "alternatives": ["已认证业务入口"]}
            ],
        },
        ["answer"],
        can_approve=False,
    )
    job = store.claim()
    store.finish(job, "WAITING_CLARIFICATION", pending=gate)
    answer = "参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录"
    payload = {"gate_id": gate["gate_id"], "action": "answer", "text": answer}
    first = store.submit(run, payload, "answer-once")
    assert store.submit(run, payload, "answer-once") == first
    job = store.claim()
    store.finish(job, "FAILED", error="结构化响应未通过校验")
    restored = Store(store.settings)
    try:
        messages = restored.transcript(run)["messages"]
        historical = [item for item in messages if item.get("validation") == "historical_gate"]
        assert len(historical) == 1
        text = historical[0]["content"]
        for expected in [
            "参与者将通过哪种入口报名？",
            "登录后报名",
            "模板不支持匿名公开报名页",
            "原始报名目标需要明确入口",
            "已认证业务入口",
        ]:
            assert expected in text
        assert sum(item["content"] == answer for item in messages) == 1
        assert messages.index(historical[0]) < next(
            index for index, item in enumerate(messages) if item["content"] == answer
        )
        assert restored.get_run(run)["pending"] is None
        assert "不代表当前仍未解决" in text
        assert (
            len(restored.messages(run)) == 2
        )  # Historical model questions never become human facts.
    finally:
        restored.engine.dispose()


def test_root_schema_failure_reports_only_allowlisted_validator_message():
    from pydantic import ValidationError

    from workbench.domain import Requirement
    from workbench.model_diagnostics import schema_diagnostics

    value = {
        "summary": "报名",
        "users": ["参赛者"],
        "data_scope": "per_user",
        "features": ["报名"],
        "acceptance": [],
        "questions": ["已回答的问题"],
        "question_items": [{"id": "scope", "prompt": "另一个问题", "kind": "text"}],
    }
    with pytest.raises(ValidationError) as error:
        Requirement.model_validate(value)
    details = schema_diagnostics(error.value, Requirement)
    assert details[0]["message"] == "结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题"
    assert details[0]["path"] == []
````
