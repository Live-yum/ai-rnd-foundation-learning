# tests/test_recommendation_stage_budget.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_clarification_does_not_spend_design_repair_allowance`（L11–L50）：接收`settings`、`store`、`plan`、`design_converges`。 控制顺序：L38断言`gateway.calls[:4] == ["recommend:1", "recommend:2", "recommend:3", "plan:3"]`；L39按`design_converges`分支；L40断言`gateway.calls[4:] == ["plan:4"]`；L41断言`state["status"] == "READY"`；L42断言`state["result"]["cleanroom"]["passed"] is True`；L43断言`(settings.data_dir / "runs" / run_id / "delivery.zip").is_file()`；L45断言`gateway.calls[4:] == ["plan:4", "plan:5"]`；L46断言`state["status"] == "BLOCKED"`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`store.set_automation`、`StagedGateway`、`Runtime`、`runtime.tick`、`store.get_run`、`(settings.data_dir / "runs" / run_id / "delivery.zip").is_file`、`(settings.data_dir / "runs" / run_id / "delivery.zip").exists`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_clarification_does_not_spend_design_repair_allowance.StagedGateway`（L14–L30）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_clarification_does_not_spend_design_repair_allowance.StagedGateway.complete`（L15–L30）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L17按`schema is Requirement`分支；L19按`key in {"recommend:1", "recommend:2"}`分支；L21断言`key == "recommend:3"`；L23断言`schema is Plan`；L24断言`payload["approved_requirement"]["data_scope"] == "per_user"`；L25按`key != "plan:3"`分支；L26断言`payload["resolution_feedback"]["stage"] == "design"`；L27断言`payload["previous_plan"]["data_scope"] == "shared"`。后续分支沿下方源码相同行号继续阅读。 调用`self.calls.append`、`requirement`、`plan.model_copy`。 返回路径：L20的`requirement(["请决定一个尚未明确的细节"])`；L22的`requirement()`；L29的`plan`。

</details>

**创建路径：** `tests/test_recommendation_stage_budget.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L50。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2281`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_recommendation_stage_budget.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7975cdc11de135bb94f8d1559857928cd52a0a5421ac18dd08a99f5d17b1079b"} -->
````python
# tests/test_recommendation_stage_budget.py
"""One smart authorization covers both bounded clarification and design repair."""

import pytest
from conftest import FixtureGateway, new_run, requirement

from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime


@pytest.mark.parametrize("design_converges", [True, False])
def test_clarification_does_not_spend_design_repair_allowance(
    settings, store, plan, design_converges
):
    class StagedGateway(FixtureGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            self.calls.append(key)
            if schema is Requirement:
                # Exercise both clarification repairs before any planning.
                if key in {"recommend:1", "recommend:2"}:
                    return requirement(["请决定一个尚未明确的细节"])
                assert key == "recommend:3"
                return requirement()
            assert schema is Plan
            assert payload["approved_requirement"]["data_scope"] == "per_user"
            if key != "plan:3":
                assert payload["resolution_feedback"]["stage"] == "design"
                assert payload["previous_plan"]["data_scope"] == "shared"
            if design_converges and key == "plan:4":
                return plan
            return plan.model_copy(update={"data_scope": "shared"})

    run_id = new_run(store)
    store.set_automation(run_id, True, "single-smart-authorization")
    gateway = StagedGateway(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    state = store.get_run(run_id)
    assert gateway.calls[:4] == ["recommend:1", "recommend:2", "recommend:3", "plan:3"]
    if design_converges:
        assert gateway.calls[4:] == ["plan:4"]
        assert state["status"] == "READY", state
        assert state["result"]["cleanroom"]["passed"] is True
        assert (settings.data_dir / "runs" / run_id / "delivery.zip").is_file()
    else:
        assert gateway.calls[4:] == ["plan:4", "plan:5"]
        assert state["status"] == "BLOCKED", state
        assert state["pending"]["stage"] == "design"
        assert "本阶段两轮" in state["error"]
        assert not (settings.data_dir / "runs" / run_id / "delivery.zip").exists()
    assert len(store.messages(run_id)) == 1
````
