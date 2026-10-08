# tests/test_batches.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.domain`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `batch`（L13–L30）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L14的`{ "items": [ {"title": "个人书架", "requirement": " 记录读书进度\n", "intelligent": False}, {"title"…`。
- `test_batch_is_idempotent_and_keeps_independent_run_policies`（L33–L51）：接收`store`。 控制顺序：L36断言`store.create_batch(payload, "batch-once") == result`；L37断言`len(result["items"]) == 3`；L38断言`len({item["run_id"] for item in result["items"]}) == 3`；L39断言`len({item["project_id"] for item in result["items"]}) == 3`；L40遍历`zip(payload["items"], result["items"], strict=True)`；L42断言`item["status"] == run["status"] == "QUEUED"`；L43断言`run["auto_mode"] is source.get("intelligent", False)`；L44断言`store.messages(run["id"])[0]["content"] == source["requirement"]`。后续分支沿下方源码相同行号继续阅读。 调用`batch`、`store.create_batch`、`len`、`zip`、`store.get_run`、`source.get`、`store.messages`、`store.tx`、`session.scalar`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_batch_failure_rolls_back_every_item_and_allows_retry`（L54–L72）：接收`store`、`monkeypatch`。 控制顺序：L69遍历`(Project, Run, Message, Job, Event, Request)`；L70断言`session.scalar(select(func.count()).select_from(table)) == 0`；L72断言`len(store.create_batch(batch(), "atomic-batch")["items"]) == 3`。 调用`monkeypatch.setattr`、`pytest.raises`、`store.create_batch`、`batch`、`store.tx`、`session.scalar`、`select(func.count()).select_from`、`select`、`func.count`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_batch_failure_rolls_back_every_item_and_allows_retry.interrupted`（L58–L63）：接收`session`、`project_id`、`data`。 控制顺序：L61按`calls == 2`分支；L62抛异常，停止当前正常路径。 调用`RuntimeError`、`enqueue`。 返回路径：L63的`enqueue(session, project_id, data)`。
- `test_batch_validates_every_item_before_mutating`（L92–L95）：接收`store`、`items`。 控制顺序：L95断言`store.list_projects() == []`。 调用`pytest.raises`、`store.create_batch`、`store.list_projects`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_batch_accepts_ten_projects`（L98–L99）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99断言`len(BatchInput(items=[{"title": "x", "requirement": "y"}] * 10).items) == 10`。 调用`len`、`BatchInput`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_batch_api_auth_model_configuration_and_atomic_validation`（L102–L121）：接收`settings`。 控制顺序：L106断言`client.post("/batches", json=batch(), headers=headers).status_code == 401`；L108断言`client.post("/batches", json=batch(), headers=headers).status_code == 503`；L109断言`app.state.store.list_projects() == []`；L113断言`client.post("/batches", json=batch()).status_code == 422`；L116断言`client.post("/batches", json=payload, headers=headers).status_code == 422`；L117断言`app.state.store.list_projects() == []`；L119断言`response.status_code == 202`；L120断言`client.post("/batches", json=batch(), headers=headers).json() == response.json()`。后续分支沿下方源码相同行号继续阅读。 调用`create_app`、`TestClient`、`client.post`、`batch`、`app.state.store.list_projects`、`SecretStr`、`client.post("/batches", json=batch(), headers=headers).json`、`response.json`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_batches.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L121。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5060`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_batches.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d9b344068d4b8cc62dc9104d5efa316eaf377799e9220c235d357275b74b718f"} -->
````python
# tests/test_batches.py
"""Batch submission is atomic, replayable, and uses ordinary isolated runs."""

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError
from sqlalchemy import func, select

from workbench.api import create_app
from workbench.domain import BatchInput
from workbench.store import Conflict, Event, Job, Message, Project, Request, Run


def batch():
    return {
        "items": [
            {"title": "个人书架", "requirement": "  记录读书进度\n", "intelligent": False},
            {"title": "采购协作", "requirement": "采购审批与收货", "intelligent": True},
            {
                "title": "设施维护",
                "requirement": "设备与工单",
                "template": "fastapiadmin",
                "selection": {
                    "template": "fastapiadmin",
                    "backend": "fastapiadmin",
                    "frontend": "fastapiadmin-vue",
                    "database": "postgresql",
                },
            },
        ]
    }


def test_batch_is_idempotent_and_keeps_independent_run_policies(store):
    payload = batch()
    result = store.create_batch(payload, "batch-once")
    assert store.create_batch(payload, "batch-once") == result
    assert len(result["items"]) == 3
    assert len({item["run_id"] for item in result["items"]}) == 3
    assert len({item["project_id"] for item in result["items"]}) == 3
    for source, item in zip(payload["items"], result["items"], strict=True):
        run = store.get_run(item["run_id"])
        assert item["status"] == run["status"] == "QUEUED"
        assert run["auto_mode"] is source.get("intelligent", False)
        assert store.messages(run["id"])[0]["content"] == source["requirement"]
        assert run["template"] == source.get("template", "python-basic")
    with store.tx() as session:
        assert session.scalar(select(func.count()).select_from(Job)) == 3
        assert session.scalar(select(func.count()).select_from(Event)) == 1
    payload["items"][0]["requirement"] = "变更需求"
    with pytest.raises(Conflict, match="Idempotency-Key"):
        store.create_batch(payload, "batch-once")


def test_batch_failure_rolls_back_every_item_and_allows_retry(store, monkeypatch):
    enqueue = store._enqueue_run
    calls = 0

    def interrupted(session, project_id, data):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated database failure")
        return enqueue(session, project_id, data)

    monkeypatch.setattr(store, "_enqueue_run", interrupted)
    with pytest.raises(RuntimeError):
        store.create_batch(batch(), "atomic-batch")
    with store.tx() as session:
        for table in (Project, Run, Message, Job, Event, Request):
            assert session.scalar(select(func.count()).select_from(table)) == 0
    monkeypatch.setattr(store, "_enqueue_run", enqueue)
    assert len(store.create_batch(batch(), "atomic-batch")["items"]) == 3


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{"title": "x", "requirement": "y"}] * 11,
        [{"title": "x", "requirement": "   "}],
        [{"title": "x", "requirement": "y", "intelligent": "true"}],
        [{"title": "x", "requirement": "y", "approved": True}],
        [
            {
                "title": "x",
                "requirement": "y",
                "selection": {"template": "python-basic", "frontend": "vben-antd"},
            }
        ],
    ],
)
def test_batch_validates_every_item_before_mutating(store, items):
    with pytest.raises(ValidationError):
        store.create_batch({"items": items}, "invalid-batch")
    assert store.list_projects() == []


def test_batch_accepts_ten_projects():
    assert len(BatchInput(items=[{"title": "x", "requirement": "y"}] * 10).items) == 10


def test_batch_api_auth_model_configuration_and_atomic_validation(settings):
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        headers = {"Idempotency-Key": "api-batch"}
        assert client.post("/batches", json=batch(), headers=headers).status_code == 401
        client.headers["Authorization"] = "Bearer " + app.state.token
        assert client.post("/batches", json=batch(), headers=headers).status_code == 503
        assert app.state.store.list_projects() == []
        settings.base_url = "https://model.example/v1"
        settings.model = "dummy-model"
        settings.api_key = SecretStr("dummy-batch-key")
        assert client.post("/batches", json=batch()).status_code == 422
        payload = batch()
        payload["items"][1]["role"] = "system"
        assert client.post("/batches", json=payload, headers=headers).status_code == 422
        assert app.state.store.list_projects() == []
        response = client.post("/batches", json=batch(), headers=headers)
        assert response.status_code == 202
        assert client.post("/batches", json=batch(), headers=headers).json() == response.json()
        assert len(client.get("/runs").json()) == 3
````
