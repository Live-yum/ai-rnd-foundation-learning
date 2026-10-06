# tests/test_capability_model_free_delivery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.runtime`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `waiting_run`（L14–L24）：接收`store`、`stage`。 调用`store.create_project`、`store.create_run`、`store.gate`、`store.tx`、`session.get`、`stage.upper`。 返回路径：L24的`run, gate`。
- `test_api_allows_only_exact_model_free_approval_and_its_idempotent_replay`（L28–L58）：接收`settings`、`store`、`stage`。 控制顺序：L31断言`settings.models_ready() is False`；L45按`stage == "extension_design"`分支；L46断言`response.status_code == 503`；L47断言`store.claim(only_rejections=True, include_model_free=True) is None`；L49断言`response.status_code == 202`；L53断言`replay.status_code == 202`；L54断言`replay.json() == response.json()`；L56断言`job["id"] == response.json()["job_id"]`。后续分支沿下方源码相同行号继续阅读。 调用`settings.models_ready`、`waiting_run`、`TestClient`、`create_app`、`client.post`、`store.claim`、`replay.json`、`response.json`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_free_admission_uses_persisted_same_run_gate_not_payload_stage`（L61–L71）：接收`store`。 控制顺序：L65断言`store.is_model_free_approval(run, body)`；L66断言`not store.is_model_free_approval(other, body)`；L67断言`not store.is_model_free_approval(run, {**body, "approved": False})`；L68断言`not store.is_model_free_approval(run, {**body, "action": "recommend"})`；L71断言`store.claim(only_rejections=True, include_model_free=True) is None`。 调用`waiting_run`、`store.is_model_free_approval`、`store.tx`、`session.add`、`Job`、`store.claim`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_resumes_saved_final_approval_without_model_calls`（L74–L100）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L97断言`runtime.tick() is True`；L100断言`store.get_run(run)["status"] == "SOURCE_READY"`。 调用`waiting_run`、`store.submit`、`Mock`、`AssertionError`、`monkeypatch.setattr`、`Runtime`、`SimpleNamespace`、`runtime.tick`、`runtime.graph.invoke.assert_called_once`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_missing_checkpoint_cannot_turn_approval_into_model_work`（L103–L120）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L117断言`runtime.tick() is True`；L120断言`store.get_run(run)["status"] == "FAILED"`。 调用`waiting_run`、`store.submit`、`Mock`、`monkeypatch.setattr`、`Runtime`、`SimpleNamespace`、`runtime.tick`、`runtime.graph.invoke.assert_not_called`、`gateway.complete.assert_not_called`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_offline_transient_package_retry_stays_bound_to_model_free_checkpoint`（L124–L170）：接收`settings`、`store`、`monkeypatch`、`next_node`。 控制顺序：L136断言`store.get_run(run)["model_free_retry"] is True`；L142断言`response.status_code == 202`；L146断言`replay.status_code == 202`；L147断言`replay.json() == response.json()`；L154按`next_node == "waiting_scope"`分支；L162断言`runtime.tick() is True`；L164按`next_node == "extension_package"`分支；L166断言`runtime.graph.invoke.call_args.args[0] is None`。后续分支沿下方源码相同行号继续阅读。 调用`waiting_run`、`store.submit`、`store.claim`、`store.record_event`、`store.finish`、`store.get_run`、`TestClient`、`create_app`、`client.post`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_scope_approval_is_not_misclassified_as_package_retry`（L173–L188）：接收`settings`、`store`。 控制顺序：L183断言`store.get_run(run)["model_free_retry"] is False`；L184断言`store.is_model_free_retry(run) is False`；L188断言`response.status_code == 503`。 调用`waiting_run`、`store.submit`、`store.claim`、`store.record_event`、`store.finish`、`store.get_run`、`store.is_model_free_retry`、`TestClient`、`create_app`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_model_free_delivery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L188。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8155`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_model_free_delivery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bd31c2e6b4a402bcad107d0d0467e592e84bcdab7d4afee3f753685418676104"} -->
````python
# tests/test_capability_model_free_delivery.py
"""Final retained-candidate approvals require no model, but no planning is waived."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from workbench.api import create_app
from workbench.runtime import Runtime
from workbench.store import Job, Run


def waiting_run(store, stage):
    project = store.create_project("offline approval", "project-" + stage)
    run = store.create_run(
        project["id"], {"requirement": "测试资料保存；全部自己实现"}, "run-" + stage
    )["run_id"]
    gate = store.gate(run, stage, 1, {"requires_explicit_review": True}, ["approve", "reject"])
    with store.tx() as session:
        record = session.get(Run, run)
        record.pending = gate
        record.status = "WAITING_" + stage.upper()
    return run, gate


@pytest.mark.parametrize("stage", ["extension_scope", "extension_delivery", "extension_design"])
def test_api_allows_only_exact_model_free_approval_and_its_idempotent_replay(
    settings, store, stage
):
    assert settings.models_ready() is False
    run, gate = waiting_run(store, stage)
    body = {
        "action": "approve",
        "approved": True,
        "gate_id": gate["gate_id"],
        "version": gate["version"],
        "digest": gate["digest"],
    }
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "offline-approval"}
        )
        if stage == "extension_design":
            assert response.status_code == 503
            assert store.claim(only_rejections=True, include_model_free=True) is None
            return
        assert response.status_code == 202, response.text
        replay = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "offline-approval"}
        )
        assert replay.status_code == 202
        assert replay.json() == response.json()
    job = store.claim(only_rejections=True, include_model_free=True)
    assert job["id"] == response.json()["job_id"]
    assert job["payload"]["action"] == "approve"
    assert store.claim(only_rejections=True, include_model_free=True) is None


def test_model_free_admission_uses_persisted_same_run_gate_not_payload_stage(store):
    run, gate = waiting_run(store, "extension_scope")
    other, _ = waiting_run(store, "extension_design")
    body = {"action": "approve", "approved": True, "gate_id": gate["gate_id"]}
    assert store.is_model_free_approval(run, body)
    assert not store.is_model_free_approval(other, body)
    assert not store.is_model_free_approval(run, {**body, "approved": False})
    assert not store.is_model_free_approval(run, {**body, "action": "recommend"})
    with store.tx() as session:
        session.add(Job(run_id=other, payload=body))
    assert store.claim(only_rejections=True, include_model_free=True) is None


def test_worker_resumes_saved_final_approval_without_model_calls(settings, store, monkeypatch):
    run, gate = waiting_run(store, "extension_scope")
    reply = store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "worker-offline-approval",
    )
    gateway = Mock()
    gateway.complete.side_effect = AssertionError("no model call is authorized by final approval")
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    waiting = SimpleNamespace(
        values={"run_id": run},
        next=("extension_scope",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value=gate)])],
    )
    completed = SimpleNamespace(
        values={"status": "SOURCE_READY", "delivery": {}, "last_job_id": reply["job_id"]},
        next=(),
        tasks=[],
    )
    runtime.graph = Mock()
    runtime.graph.get_state.side_effect = [waiting, completed]
    assert runtime.tick() is True
    runtime.graph.invoke.assert_called_once()
    gateway.complete.assert_not_called()
    assert store.get_run(run)["status"] == "SOURCE_READY"


def test_worker_missing_checkpoint_cannot_turn_approval_into_model_work(
    settings, store, monkeypatch
):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "missing-checkpoint",
    )
    gateway = Mock()
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    runtime.graph = Mock()
    runtime.graph.get_state.return_value = SimpleNamespace(values={}, next=(), tasks=[])
    assert runtime.tick() is True
    runtime.graph.invoke.assert_not_called()
    gateway.complete.assert_not_called()
    assert store.get_run(run)["status"] == "FAILED"


@pytest.mark.parametrize("next_node", ["extension_package", "extension_code", "waiting_scope"])
def test_offline_transient_package_retry_stays_bound_to_model_free_checkpoint(
    settings, store, monkeypatch, next_node
):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "scope-before-failure",
    )
    failed = store.claim(only_rejections=True, include_model_free=True)
    store.record_event(run, "stage", {"name": "extension_package", "phase": "failed"})
    store.finish(failed, "FAILED", error="authored transient cleanroom outage")
    assert store.get_run(run)["model_free_retry"] is True
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/retry", headers={"Idempotency-Key": "offline-package-retry"}
        )
        assert response.status_code == 202
        replay = client.post(
            f"/runs/{run}/retry", headers={"Idempotency-Key": "offline-package-retry"}
        )
        assert replay.status_code == 202
        assert replay.json() == response.json()
    gateway = Mock()
    monkeypatch.setattr("workbench.runtime.ModelGateway", lambda *a, **k: gateway)
    runtime = Runtime(settings, store)
    resume = SimpleNamespace(
        values={"run_id": run, "last_job_id": failed["id"]}, next=(next_node,), tasks=[]
    )
    if next_node == "waiting_scope":
        resume.next = ("extension_scope",)
        resume.tasks = [SimpleNamespace(interrupts=[SimpleNamespace(value=gate)])]
    completed = SimpleNamespace(
        values={"status": "SOURCE_READY", "delivery": {}}, next=(), tasks=[]
    )
    runtime.graph = Mock()
    runtime.graph.get_state.side_effect = [resume, completed]
    assert runtime.tick() is True
    gateway.complete.assert_not_called()
    if next_node == "extension_package":
        runtime.graph.invoke.assert_called_once()
        assert runtime.graph.invoke.call_args.args[0] is None
        assert store.get_run(run)["status"] == "SOURCE_READY"
    else:
        runtime.graph.invoke.assert_not_called()
        assert store.get_run(run)["status"] == "FAILED"


def test_failed_scope_approval_is_not_misclassified_as_package_retry(settings, store):
    run, gate = waiting_run(store, "extension_scope")
    store.submit(
        run,
        {"action": "approve", "approved": True, "gate_id": gate["gate_id"]},
        "scope-failed-before-return",
    )
    failed = store.claim(only_rejections=True, include_model_free=True)
    store.record_event(run, "stage", {"name": "extension_scope", "phase": "failed"})
    store.finish(failed, "FAILED", error="authored stale scope rejection")
    assert store.get_run(run)["model_free_retry"] is False
    assert store.is_model_free_retry(run) is False
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(f"/runs/{run}/retry", headers={"Idempotency-Key": "not-package"})
        assert response.status_code == 503
````
