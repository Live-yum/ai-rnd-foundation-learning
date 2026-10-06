# tests/test_store.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_migration_and_foreign_key`（L12–L17）：接收`store`。 控制顺序：L14断言`c.scalar(text("PRAGMA foreign_keys")) == 1`；L15断言`c.scalar(text("SELECT version_num FROM alembic_version")) == "0002"`。 调用`store.engine.connect`、`c.scalar`、`text`、`pytest.raises`、`store.tx`、`s.add`、`Message`、`str`、`uuid.uuid4`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rollback`（L20–L24）：接收`store`。 控制顺序：L23抛异常，停止当前正常路径；L24断言`store.list_projects() == []`。 调用`pytest.raises`、`store.tx`、`s.add`、`Project`、`RuntimeError`、`store.list_projects`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_idempotency_and_conflict`（L27–L32）：接收`store`。 控制顺序：L29断言`store.create_project("same", "key") == first`；L32断言`len(store.list_projects()) == 1`。 调用`store.create_project`、`pytest.raises`、`len`、`store.list_projects`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_concurrent_duplicate_requests`（L35–L38）：接收`store`。 控制顺序：L38断言`len({x["id"] for x in results}) == 1`。 调用`ThreadPoolExecutor`、`list`、`pool.map`、`store.create_project`、`range`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_persistence`（L41–L48）：接收`settings`、`store`。 控制顺序：L45断言`other.get_run(run_id)["status"] == "QUEUED"`；L46断言`other.messages(run_id)[0]["role"] == "user"`。 调用`new_run`、`Store`、`other.get_run`、`other.messages`、`other.engine.dispose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_step_reuses_receipt`（L51–L60）：接收`store`。 控制顺序：L59断言`store.step(run, "same", fn) == store.step(run, "same", fn)`；L60断言`len(calls) == 1`。 调用`new_run`、`store.step`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_step_reuses_receipt.fn`（L55–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`calls.append`。 返回路径：L57的`{"answer": 42}`。
- `test_gate_cannot_bypass_approval`（L63–L69）：接收`store`。 调用`new_run`、`store.gate`、`pytest.raises`、`store.check_decision`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_budget`（L72–L80）：接收`store`。 控制顺序：L77遍历`range(store.settings.max_model_calls)`。 调用`new_run`、`range`、`store.reserve_model_call`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_run_pagination_and_project_history_are_independent`（L83–L112）：接收`store`。 控制顺序：L98遍历`range(105)`；L109断言`len(first) == 100 and len(second) == 6`；L110断言`not {row["id"] for row in first} & {row["id"] for row in second}`；L111断言`store.list_runs(older["id"])[0]["id"] == "old-run"`；L112断言`store.list_runs(statuses=["WAITING_EXTENSION_DELIVERY"])[0]["id"] == "old-run"`。 调用`store.create_project`、`store.tx`、`session.add`、`Run`、`session.flush`、`range`、`store.list_runs`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_capabilities_are_server_owned_even_for_saved_gates`（L115–L124）：接收`store`。 控制顺序：L118断言`gate["needs_model"] == {"approve": False, "reject": False}`；L124断言`store.get_run(run)["pending"]["needs_model"] == gate["needs_model"]`。 调用`new_run`、`store.gate`、`store.tx`、`session.get`、`gate.items`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_store.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L124。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4127`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_store.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d9ff34b47559bf284d68f34180a1ff6fb544879d9332e5788afd6aa98aa36cd2"} -->
````python
# tests/test_store.py
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import new_run
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from workbench.store import Conflict, Message, Project, Store


def test_migration_and_foreign_key(store):
    with store.engine.connect() as c:
        assert c.scalar(text("PRAGMA foreign_keys")) == 1
        assert c.scalar(text("SELECT version_num FROM alembic_version")) == "0002"
    with pytest.raises(IntegrityError), store.tx() as s:
        s.add(Message(run_id=str(uuid.uuid4()), role="user", content="orphan"))


def test_rollback(store):
    with pytest.raises(RuntimeError), store.tx() as s:
        s.add(Project(title="rolled back"))
        raise RuntimeError("abort")
    assert store.list_projects() == []


def test_idempotency_and_conflict(store):
    first = store.create_project("same", "key")
    assert store.create_project("same", "key") == first
    with pytest.raises(Conflict):
        store.create_project("different", "key")
    assert len(store.list_projects()) == 1


def test_concurrent_duplicate_requests(store):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store.create_project("same", "thread-key"), range(4)))
    assert len({x["id"] for x in results}) == 1


def test_persistence(settings, store):
    run_id = new_run(store)
    other = Store(settings)
    try:
        assert other.get_run(run_id)["status"] == "QUEUED"
        assert other.messages(run_id)[0]["role"] == "user"
    finally:
        other.engine.dispose()


def test_step_reuses_receipt(store):
    run = new_run(store)
    calls = []

    def fn():
        calls.append(1)
        return {"answer": 42}

    assert store.step(run, "same", fn) == store.step(run, "same", fn)
    assert len(calls) == 1


def test_gate_cannot_bypass_approval(store):
    run = new_run(store)
    gate = store.gate(run, "design", 1, {"x": 1}, ["approve", "reject"])
    with pytest.raises(Conflict):
        store.check_decision(
            run, gate, {"gate_id": gate["gate_id"], "action": "approve", "approved": True}
        )


def test_model_budget(store):
    from workbench.errors import PausedLimit

    store.settings.max_model_calls = 2
    run = new_run(store)
    for _ in range(store.settings.max_model_calls):
        store.reserve_model_call(run)
    with pytest.raises(PausedLimit):
        store.reserve_model_call(run)


def test_run_pagination_and_project_history_are_independent(store):
    from workbench.store import Run

    older = store.create_project("older", "older-project")
    newer = store.create_project("newer", "newer-project")
    with store.tx() as session:
        session.add(
            Run(
                id="old-run",
                project_id=older["id"],
                template="python-basic",
                status="WAITING_EXTENSION_DELIVERY",
            )
        )
        session.flush()
        for index in range(105):
            session.add(
                Run(
                    id=f"new-{index:03}",
                    project_id=newer["id"],
                    template="python-basic",
                    status="READY",
                )
            )
    first = store.list_runs(limit=100)
    second = store.list_runs(limit=100, offset=100)
    assert len(first) == 100 and len(second) == 6
    assert not {row["id"] for row in first} & {row["id"] for row in second}
    assert store.list_runs(older["id"])[0]["id"] == "old-run"
    assert store.list_runs(statuses=["WAITING_EXTENSION_DELIVERY"])[0]["id"] == "old-run"


def test_model_capabilities_are_server_owned_even_for_saved_gates(store):
    run = new_run(store)
    gate = store.gate(run, "delivery", 1, {}, ["approve", "reject"])
    assert gate["needs_model"] == {"approve": False, "reject": False}
    from workbench.store import Run

    with store.tx() as session:
        record = session.get(Run, run)
        record.pending = {key: value for key, value in gate.items() if key != "needs_model"}
    assert store.get_run(run)["pending"]["needs_model"] == gate["needs_model"]
````
