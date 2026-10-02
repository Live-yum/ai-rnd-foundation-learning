# tests/test_real_model_source_conflict_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `conflict`（L11–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L12的`{ "code": "requirement_source_conflict", "target": {"entity": "requests", "field": "title"…`。
- `test_atomic_analysis_conflicts_export_only_selected_values_and_origins`（L36–L53）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L40断言`len(out) == 1`；L41断言`out[0]["target"] == raw["target"]`；L42断言`[source["expected"] for source in out[0]["sources"]] == [200, 120]`；L43断言`[source["origin"] for source in out[0]["sources"]] == ["user_input", "model_analysis"…`；L44断言`out[0]["sources"][0]["source"] == {"section": "user_messages", "index": 0}`；L46遍历`( "credential-canary", "raw-provider-canary", "private-full-histo…`；L52断言`secret not in rendered`；L53断言`raw == before`。 调用`conflict`、`deepcopy`、`harness.safe_analysis_conflict_details`、`harness.DiagnosticTextBudget`、`len`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_conflict_collection_is_not_exported`（L57–L58）：接收`bad`。 控制顺序：L58断言`harness.safe_analysis_conflict_details(bad, harness.DiagnosticTextBudget()) == []`。 调用`harness.safe_analysis_conflict_details`、`harness.DiagnosticTextBudget`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_untrusted_conflict_fields_are_not_echoed`（L64–L80）：接收`change`。 控制顺序：L67按`change == "attribute"`分支；L69按`change == "section"`分支；L71按`change == "index"`分支；L73按`change == "origin"`分支；L75按`change == "expected"`分支；L80断言`"private-canary" not in json.dumps(out)`。 调用`conflict`、`harness.safe_analysis_conflict_details`、`harness.DiagnosticTextBudget`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_conflict_text_uses_shared_budget_and_scrubs_before_clipping`（L83–L93）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L89断言`len(out) == 20`；L90断言`all(len(item["sources"]) <= 8 for item in out)`；L91断言`sum(len(s.get("source_excerpt", "")) for item in out for s in item["sources"]) <= 700`；L92断言`"known-secret" not in json.dumps(out)`；L93断言`budget.remaining == 0`。 调用`conflict`、`harness.DiagnosticTextBudget`、`harness.safe_analysis_conflict_details`、`len`、`all`、`sum`、`s.get`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_choices_export_cardinality_without_arbitrary_literals`（L96–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102断言`[s["expected_count"] for s in out[0]["sources"]] == [2, 1]`；L103断言`"private-choice" not in json.dumps(out)`。 调用`conflict`、`harness.safe_analysis_conflict_details`、`harness.DiagnosticTextBudget`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_analysis_without_any_plan_preserves_safe_conflict_details`（L106–L128）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L124断言`details["valid_plan_present"] is False`；L125断言`details["pending_stage"] == "clarification"`；L126断言`details["analysis_source_conflicts"][0]["sources"][1]["expected"] == 120`；L127断言`"requirement_source_conflict" in details["error_categories"]`；L128断言`"private-provider-canary" not in json.dumps(details)`。 调用`harness.safe_workflow_details`、`Store`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_analysis_without_any_plan_preserves_safe_conflict_details.Store`（L107–L121）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_failed_analysis_without_any_plan_preserves_safe_conflict_details.Store.get_run`（L108–L118）：接收`run_id`。 调用`conflict`。 返回路径：L109的`{ "status": "BLOCKED", "template": "python-basic", "model_calls": 3, "error": "需求分析来源冲突：re…`。
- `test_failed_analysis_without_any_plan_preserves_safe_conflict_details.Store.latest_revision`（L120–L121）：接收`run_id`、`stage`。 返回路径：L121的`None`。

</details>

**创建路径：** `tests/test_real_model_source_conflict_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5043`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_real_model_source_conflict_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0ae05cadedbf2e0adb7716958ed4aacfdcb91feb06da09e49da7456a916c41b6"} -->
````python
# tests/test_real_model_source_conflict_diagnostics.py
"""Analysis conflicts stay diagnosable without publishing raw analysis or user history."""

import json
from copy import deepcopy

import pytest

from scripts import ci_real_model as harness


def conflict():
    return {
        "code": "requirement_source_conflict",
        "target": {"entity": "requests", "field": "title"},
        "attribute": "max_length",
        "message": "raw-provider-canary",
        "sources": [
            {
                "source": {"section": "user_messages", "index": 0},
                "origin": "user_input",
                "expected": 200,
                "text": "requests.title 最长200，token=credential-canary",
                "user_sources": [{"text": "private-full-history-canary"}],
            },
            {
                "source": {"section": "field_requirements", "index": 4},
                "origin": "model_analysis",
                "expected": 120,
                "text": "requests.title max_length=120",
                "raw_response": "private-provider-canary",
            },
        ],
    }


def test_atomic_analysis_conflicts_export_only_selected_values_and_origins():
    raw = conflict()
    before = deepcopy(raw)
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert len(out) == 1
    assert out[0]["target"] == raw["target"]
    assert [source["expected"] for source in out[0]["sources"]] == [200, 120]
    assert [source["origin"] for source in out[0]["sources"]] == ["user_input", "model_analysis"]
    assert out[0]["sources"][0]["source"] == {"section": "user_messages", "index": 0}
    rendered = json.dumps(out)
    for secret in (
        "credential-canary",
        "raw-provider-canary",
        "private-full-history-canary",
        "private-provider-canary",
    ):
        assert secret not in rendered
    assert raw == before


@pytest.mark.parametrize("bad", [None, {}, "not-a-list", [None], [{"attribute": []}]])
def test_malformed_conflict_collection_is_not_exported(bad):
    assert harness.safe_analysis_conflict_details(bad, harness.DiagnosticTextBudget()) == []


@pytest.mark.parametrize(
    "change", ["section", "index", "origin", "expected", "target", "attribute"]
)
def test_untrusted_conflict_fields_are_not_echoed(change):
    raw = conflict()
    source = raw["sources"][0]
    if change == "attribute":
        raw["attribute"] = ["private-canary"]
    elif change == "section":
        source["source"]["section"] = ["private-canary"]
    elif change == "index":
        source["source"]["index"] = "private-canary"
    elif change == "origin":
        source["origin"] = ["private-canary"]
    elif change == "expected":
        source["expected"] = {"payload": "private-canary"}
    else:
        raw["target"]["field"] = "private-canary"
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert "private-canary" not in json.dumps(out)


def test_conflict_text_uses_shared_budget_and_scrubs_before_clipping():
    raw = conflict()
    raw["sources"][0]["text"] = "a" * 590 + "known-secret-canary" + "z" * 5000
    raw["sources"] *= 20
    budget = harness.DiagnosticTextBudget(("known-secret-canary",), limit=700)
    out = harness.safe_analysis_conflict_details([raw] * 100, budget)
    assert len(out) == 20
    assert all(len(item["sources"]) <= 8 for item in out)
    assert sum(len(s.get("source_excerpt", "")) for item in out for s in item["sources"]) <= 700
    assert "known-secret" not in json.dumps(out)
    assert budget.remaining == 0


def test_choices_export_cardinality_without_arbitrary_literals():
    raw = conflict()
    raw["attribute"] = "choices"
    raw["sources"][0]["expected"] = ["private-choice-a", "private-choice-b"]
    raw["sources"][1]["expected"] = ["private-choice-c"]
    out = harness.safe_analysis_conflict_details([raw], harness.DiagnosticTextBudget())
    assert [s["expected_count"] for s in out[0]["sources"]] == [2, 1]
    assert "private-choice" not in json.dumps(out)


def test_failed_analysis_without_any_plan_preserves_safe_conflict_details():
    class Store:
        def get_run(self, run_id):
            return {
                "status": "BLOCKED",
                "template": "python-basic",
                "model_calls": 3,
                "error": "需求分析来源冲突：requests.title.max_length",
                "pending": {
                    "stage": "clarification",
                    "data": {"blocked": ["需求分析来源冲突"], "analysis_diagnostics": [conflict()]},
                },
            }

        def latest_revision(self, run_id, stage):
            return None

    details = harness.safe_workflow_details(Store(), "run", [])
    assert details["valid_plan_present"] is False
    assert details["pending_stage"] == "clarification"
    assert details["analysis_source_conflicts"][0]["sources"][1]["expected"] == 120
    assert "requirement_source_conflict" in details["error_categories"]
    assert "private-provider-canary" not in json.dumps(details)
````
