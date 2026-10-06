# tests/test_planning_transcript.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.catalog`、`workbench.feature_planning`、`workbench.llm`、`workbench.streaming`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `feature_design`（L18–L36）：接收`plan`。 调用`FeatureDesign`、`FeatureOutline`、`Selection`。 返回路径：L19的`FeatureDesign( outline=FeatureOutline( summary="登录后提交报名，学生查看本人记录，管理员审核。", selection=Select…`。
- `response`（L39–L51）：接收`raw`、`streaming`。 控制顺序：L40按`streaming`分支。 调用`httpx.Response`、`Bytes`、`stream_body`。 返回路径：L41的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Bytes(stream_bo…`；L46的`httpx.Response( 200, json={ "choices": [{"message": {"role": "assistant", "content": raw},…`。
- `test_feature_summary_is_shown_after_validation_and_replays_once`（L55–L77）：接收`store`、`plan`、`streaming`。 控制顺序：L66遍历`range(2)`；L67断言`model.complete(run, "plan:features:1", "JSON", {}, FeatureDesign) == value`；L69断言`final["content"] == value.outline.summary`；L70断言`final["validation"] == "validated"`；L71断言`final["transport"] == ("streaming" if streaming else "non_streaming")`；L73断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L74断言`len([e for e in events if e["kind"] == "assistant_completed"]) == 1`；L76断言`not any(e["kind"] == "assistant_delta" for e in events)`。后续分支沿下方源码相同行号继续阅读。 调用`feature_design`、`value.model_dump_json`、`gateway`、`new_run`、`range`、`model.complete`、`store.transcript`、`assistant_events`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_summary_is_shown_after_validation_and_replays_once.handler`（L60–L62）：接收`request`。 调用`calls.append`、`response`。 返回路径：L62的`response(raw, streaming)`。
- `test_invalid_feature_design_never_exposes_its_nested_summary`（L80–L90）：接收`store`、`plan`。 控制顺序：L88断言`store.get_run(run)["model_calls"] == 2`；L89断言`not any(e["kind"] in {"assistant_completed", "assistant_delta"} for e in events)`；L90断言`raw["outline"]["summary"] not in json.dumps(events, ensure_ascii=False)`。 调用`feature_design(plan).model_dump`、`feature_design`、`gateway`、`response`、`json.dumps`、`new_run`、`pytest.raises`、`model.complete`、`assistant_events`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_summary_redacts_current_and_rotated_keys_including_cached_replay`（L94–L120）：接收`store`、`plan`、`cached`。 控制顺序：L112按`cached`分支；L113断言`not assistant_events(store, run)`；L117断言`final["content"] == "报名方案 [redacted] [redacted]"`；L118断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L120断言`"old-key-canary" not in events and "current-key-canary" not in events`。 调用`feature_design`、`gateway`、`SecretStr`、`store.settings._remember_model_keys`、`store.settings.model_configuration`、`new_run`、`model.complete`、`assistant_events`、`store.transcript`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_summary_redacts_current_and_rotated_keys_including_cached_replay.handler`（L101–L103）：接收`request`。 调用`calls.append`、`response`、`value.model_dump_json`。 返回路径：L103的`response(value.model_dump_json(), model.streaming)`。
- `test_capability_edit_explanation_does_not_expose_source`（L123–L132）：接收`store`。 控制顺序：L131断言`store.transcript(run)["messages"][-1]["content"] == value.explanation`；L132断言`"private-source-canary" not in json.dumps(assistant_events(store, run))`。 调用`CapabilityEdits`、`gateway`、`response`、`value.model_dump_json`、`new_run`、`model.complete`、`store.transcript`、`json.dumps`、`assistant_events`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_same_named_external_schemas_cannot_select_public_fields`（L143–L151）：接收`module`、`name`。 控制顺序：L150断言`public_field(schema) is None`；L151断言`public_text(schema(), schema) == ""`。 调用`create_model`、`public_field`、`public_text`、`schema`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_planning_transcript.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L151。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5786`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_planning_transcript.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "28c089c3a7a1e42c720bc6212ee9e956c9c0468f2bb4b94a6682d361fcafed21"} -->
````python
# tests/test_planning_transcript.py
"""Planning summaries use real schemas, never a recursive search of model output."""

import json

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr, create_model
from test_streaming_backend import Bytes, assistant_events, gateway, stream_body

from workbench.capability_contracts import CapabilityEdits
from workbench.catalog import Selection
from workbench.feature_planning import FeatureDesign, FeatureOutline
from workbench.llm import ModelFailure
from workbench.streaming import public_field, public_text


def feature_design(plan):
    return FeatureDesign(
        outline=FeatureOutline(
            summary="登录后提交报名，学生查看本人记录，管理员审核。",
            selection=Selection(),
            source_digest="a" * 64,
            features=[
                {
                    "id": "registration",
                    "title": "private-feature-title",
                    "requirements": ["source-0-0"],
                    "route": "native",
                    "capability": "typed-crud",
                    "entity": "task",
                }
            ],
        ),
        baseline=plan,
    )


def response(raw, streaming):
    if streaming:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw), size=100),
        )
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"role": "assistant", "content": raw}, "finish_reason": "stop"}]
        },
    )


@pytest.mark.parametrize("streaming", [False, True])
def test_feature_summary_is_shown_after_validation_and_replays_once(store, plan, streaming):
    value = feature_design(plan)
    raw = value.model_dump_json()
    calls = []

    def handler(request):
        calls.append(request)
        return response(raw, streaming)

    model = gateway(store, handler)
    run = new_run(store)
    for _ in range(2):
        assert model.complete(run, "plan:features:1", "JSON", {}, FeatureDesign) == value
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == value.outline.summary
    assert final["validation"] == "validated"
    assert final["transport"] == ("streaming" if streaming else "non_streaming")
    events = assistant_events(store, run)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    assert len([e for e in events if e["kind"] == "assistant_completed"]) == 1
    # Nested summaries must not appear as partial JSON or a draft result.
    assert not any(e["kind"] == "assistant_delta" for e in events)
    assert "private-feature-title" not in json.dumps(events)


def test_invalid_feature_design_never_exposes_its_nested_summary(store, plan):
    raw = feature_design(plan).model_dump()
    raw["outline"]["features"][0]["id"] = "invalid feature id"
    model = gateway(store, lambda _: response(json.dumps(raw), True))
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "plan:features:invalid", "JSON", {}, FeatureDesign)
    events = assistant_events(store, run)
    assert store.get_run(run)["model_calls"] == 2
    assert not any(e["kind"] in {"assistant_completed", "assistant_delta"} for e in events)
    assert raw["outline"]["summary"] not in json.dumps(events, ensure_ascii=False)


@pytest.mark.parametrize("cached", [False, True])
def test_nested_summary_redacts_current_and_rotated_keys_including_cached_replay(
    store, plan, cached
):
    value = feature_design(plan)
    value.outline.summary = "报名方案 old-key-canary current-key-canary"
    calls = []

    def handler(request):
        calls.append(request)
        return response(value.model_dump_json(), model.streaming)

    model = gateway(store, handler)
    store.settings.api_key = SecretStr("old-key-canary")
    store.settings._remember_model_keys(store.settings.model_configuration())
    store.settings.api_key = SecretStr("current-key-canary")
    model.streaming = not cached
    run = new_run(store)
    model.complete(run, "plan:features:secrets", "JSON", {}, FeatureDesign)
    if cached:
        assert not assistant_events(store, run)
        model.streaming = True
        model.complete(run, "plan:features:secrets", "JSON", {}, FeatureDesign)
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == "报名方案 [redacted] [redacted]"
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    events = json.dumps(assistant_events(store, run))
    assert "old-key-canary" not in events and "current-key-canary" not in events


def test_capability_edit_explanation_does_not_expose_source(store):
    value = CapabilityEdits(
        explanation="已生成本轮业务修改，等待独立验收。",
        files=[{"path": "app.py", "content": "private-source-canary"}],
    )
    model = gateway(store, lambda _: response(value.model_dump_json(), True))
    run = new_run(store)
    model.complete(run, "coding:extension:1", "JSON", {}, CapabilityEdits)
    assert store.transcript(run)["messages"][-1]["content"] == value.explanation
    assert "private-source-canary" not in json.dumps(assistant_events(store, run))


@pytest.mark.parametrize(
    ("module", "name"),
    [
        ("workbench.domain", "Requirement"),
        ("workbench.feature_planning", "FeatureDesign"),
        ("workbench.capability_contracts", "CapabilityEdits"),
    ],
)
def test_same_named_external_schemas_cannot_select_public_fields(module, name):
    schema = create_model(
        name,
        __module__=module,
        summary=(str, "private-summary"),
        explanation=(str, "private-source"),
    )
    assert public_field(schema) is None
    assert public_text(schema(), schema) == ""
````
