# tests/test_customer_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.runtime`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_customer_smart_workflow_reaches_independent_delivery`（L10–L50）：接收`settings`、`store`。 控制顺序：L47断言`state["status"] == "READY"`；L48断言`state["auto_mode"] is True`；L49断言`state["result"]["cleanroom"]["business"]["passed"] is True`；L50断言`state["result"]["cleanroom"]["browser"]["real_browser"] is True`。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`(ROOT / "examples/requirements/customer-service.md").read_text`、`Requirement`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`Runtime`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_smart_workflow_reaches_independent_delivery.Fixture`（L23–L36）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_customer_smart_workflow_reaches_independent_delivery.Fixture.complete`（L26–L36）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L28按`schema is Requirement`分支；L30按`schema is Plan`分支；L32按`schema is ModelReview`分支；L36抛异常，停止当前正常路径。 调用`self.calls.append`、`ModelReview`、`AssertionError`。 返回路径：L29的`requirement`；L31的`plan`；L33的`ModelReview( summary="Explicit fixture review", observations=[], uncovered_requirements=[]…`。

</details>

**创建路径：** `tests/test_customer_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L50。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1920`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0cefdacc5941bcd21b901ab423affd281c75b31ed7b501a48fd072c15e02b656"} -->
````python
# tests/test_customer_workflow.py
"""Explicit model fixtures test orchestration, with real generated HTTP and browser gates."""

import uuid

from workbench.domain import ModelReview, Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import ROOT


def test_customer_smart_workflow_reaches_independent_delivery(settings, store):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    prose = (ROOT / "examples/requirements/customer-service.md").read_text(encoding="utf-8")
    requirement = Requirement(
        summary=prose,
        users=["管理人员", "服务人员", "普通员工"],
        data_scope="shared",
        features=["客户、服务请求与协作任务，角色权限、提醒和统计"],
        acceptance=plan.acceptance,
    )

    class Fixture:
        calls = []

        def complete(self, run, key, instruction, payload, schema):
            self.calls.append(key)
            if schema is Requirement:
                return requirement
            if schema is Plan:
                return plan
            if schema is ModelReview:
                return ModelReview(
                    summary="Explicit fixture review", observations=[], uncovered_requirements=[]
                )
            raise AssertionError(schema)

    project = store.create_project("客服流程验收", str(uuid.uuid4()))
    run = store.create_run(
        project["id"],
        {"requirement": prose, "template": "python-basic", "intelligent": True},
        str(uuid.uuid4()),
    )["run_id"]
    with Runtime(settings, store, Fixture()) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["auto_mode"] is True
    assert state["result"]["cleanroom"]["business"]["passed"] is True
    assert state["result"]["cleanroom"]["browser"]["real_browser"] is True
````
