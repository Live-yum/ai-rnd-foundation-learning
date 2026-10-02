# tests/test_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_complete_default_flow`（L12–L25）：接收`settings`、`store`、`plan`。 控制顺序：L16遍历`("REQUIREMENTS", "DESIGN", "DELIVERY")`；L17断言`worker.tick()`；L18断言`store.get_run(run)["status"] == "WAITING_" + stage`；L22断言`result["status"] == "READY"`；L23断言`result["result"]["cleanroom"]["passed"] is True`；L24断言`result["result"]["cleanroom"]["restart"] is True`；L25断言`gateway.calls == ["requirement:1", "plan:1"]`。 调用`new_run`、`FixtureGateway`、`Runtime`、`worker.tick`、`store.get_run`、`decision`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_questions_revise_stale_gate_and_restart`（L28–L52）：接收`settings`、`store`、`plan`。 控制顺序：L34断言`old["stage"] == "clarification"`；L40断言`store.get_run(run)["pending"]["stage"] == "requirements"`；L51断言`store.get_run(run)["status"] == "REJECTED"`；L52断言`not (settings.data_dir / "runs" / run / "product").exists()`。 调用`new_run`、`FixtureGateway`、`Runtime`、`worker.tick`、`store.get_run`、`pytest.raises`、`decision`、`store.submit`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_crash_after_graph_progress_does_not_consume_next_gate`（L55–L75）：接收`settings`、`store`、`plan`、`monkeypatch`。 控制顺序：L69断言`worker.tick()`；L71断言`result["status"] == "WAITING_DESIGN"`；L72断言`gateway.calls.count("plan:1") == 1`；L75断言`store.get_run(run)["status"] == "REJECTED"`。 调用`new_run`、`FixtureGateway`、`Runtime`、`worker.tick`、`decision`、`monkeypatch.setattr`、`(_ for _ in ()).throw`、`SystemExit`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_one_worker`（L78–L81）：接收`settings`、`store`、`plan`。 调用`Runtime`、`FixtureGateway`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rule_coding_repair_is_bounded`（L84–L106）：接收`settings`、`store`、`plan`。 控制顺序：L101断言`store.get_run(run)["status"] == "WAITING_DELIVERY"`；L104断言`store.get_run(run)["status"] == "READY"`；L105断言`"coding:0" in gateway.calls and "coding:1" in gateway.calls`；L106断言`"coding:2" not in gateway.calls`。 调用`CustomRule`、`FixtureGateway`、`new_run`、`Runtime`、`worker.tick`、`decision`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tampered_delivery_not_released`（L109–L120）：接收`settings`、`store`、`plan`。 控制顺序：L120断言`store.get_run(run)["status"] == "FAILED"`。 调用`new_run`、`Runtime`、`FixtureGateway`、`worker.tick`、`decision`、`(settings.data_dir / "runs" / run / "delivery.zip").write_bytes`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L120。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4468`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "24a32db18086769519fb4034d80c64c61d2dadcf0f34740a82f2227fbba96f26"} -->
````python
# tests/test_workflow.py
import uuid

import pytest
from conftest import FixtureGateway, decision, new_run
from filelock import Timeout

from workbench.domain import CustomRule
from workbench.runtime import Runtime
from workbench.store import Conflict


def test_complete_default_flow(settings, store, plan):
    run = new_run(store)
    gateway = FixtureGateway(plan)
    with Runtime(settings, store, gateway) as worker:
        for stage in ("REQUIREMENTS", "DESIGN", "DELIVERY"):
            assert worker.tick()
            assert store.get_run(run)["status"] == "WAITING_" + stage
            decision(store, run)
        worker.tick()
    result = store.get_run(run)
    assert result["status"] == "READY", result
    assert result["result"]["cleanroom"]["passed"] is True
    assert result["result"]["cleanroom"]["restart"] is True
    assert gateway.calls == ["requirement:1", "plan:1"]  # CRUD never calls the coder.


def test_questions_revise_stale_gate_and_restart(settings, store, plan):
    run = new_run(store)
    gateway = FixtureGateway(plan, require_question=True)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        old = store.get_run(run)["pending"]
        assert old["stage"] == "clarification"
        with pytest.raises(Conflict):
            decision(store, run)
        decision(store, run, "answer", "个人用户")
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        assert store.get_run(run)["pending"]["stage"] == "requirements"
        with pytest.raises(Conflict):
            store.submit(
                run,
                {"gate_id": old["gate_id"], "action": "answer", "text": "again"},
                str(uuid.uuid4()),
            )
        decision(store, run, "revise", "明确只是个人 CRUD")
        worker.tick()
        decision(store, run, "reject")
        worker.tick()
    assert store.get_run(run)["status"] == "REJECTED"
    assert not (settings.data_dir / "runs" / run / "product").exists()


def test_crash_after_graph_progress_does_not_consume_next_gate(settings, store, plan, monkeypatch):
    run = new_run(store)
    gateway = FixtureGateway(plan)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        decision(store, run)
        original = store.finish
        monkeypatch.setattr(
            store, "finish", lambda *a, **kw: (_ for _ in ()).throw(SystemExit("crash"))
        )
        with pytest.raises(SystemExit):
            worker.tick()
        monkeypatch.setattr(store, "finish", original)
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        result = store.get_run(run)
        assert result["status"] == "WAITING_DESIGN"
        assert gateway.calls.count("plan:1") == 1
        decision(store, run, "reject")
        worker.tick()
    assert store.get_run(run)["status"] == "REJECTED"


def test_only_one_worker(settings, store, plan):
    with Runtime(settings, store, FixtureGateway(plan)), pytest.raises(Timeout):
        with Runtime(settings, store, FixtureGateway(plan)):
            pass


def test_rule_coding_repair_is_bounded(settings, store, plan):
    plan.custom_rules = [
        CustomRule(
            description="priority >= 0",
            entity="task",
            accept_examples=[{"title": "ok", "priority": 1, "done": False}],
            reject_examples=[{"title": "bad", "priority": -1, "done": False}],
        )
    ]
    gateway = FixtureGateway(plan, fail_first_code=True)
    run = new_run(store)
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        decision(store, run)
        worker.tick()
        decision(store, run)
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_DELIVERY", store.get_run(run)
        decision(store, run)
        worker.tick()
    assert store.get_run(run)["status"] == "READY"
    assert "coding:0" in gateway.calls and "coding:1" in gateway.calls
    assert "coding:2" not in gateway.calls


def test_tampered_delivery_not_released(settings, store, plan):
    run = new_run(store)
    with Runtime(settings, store, FixtureGateway(plan)) as worker:
        worker.tick()
        decision(store, run)
        worker.tick()
        decision(store, run)
        worker.tick()
        (settings.data_dir / "runs" / run / "delivery.zip").write_bytes(b"tampered")
        decision(store, run)
        worker.tick()
    assert store.get_run(run)["status"] == "FAILED"
````
