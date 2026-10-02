# tests/test_api.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `client`（L9–L16）：接收`settings`。 调用`SecretStr`、`create_app`、`TestClient`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_auth_and_host`（L19–L23）：接收`client`。 控制顺序：L20断言`client.get("/health").json() == {"status": "ok"}`；L21断言`client.get("/ready").status_code == 200`；L22断言`client.get("/projects", headers={"Authorization": "Bearer wrong"}).status_code == 401`；L23断言`client.get("/health", headers={"Host": "attacker.example"}).status_code == 400`。 调用`client.get("/health").json`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_project_run_idempotency_roles`（L26–L49）：接收`client`。 控制顺序：L29断言`project.status_code == 201`；L30断言`client.post("/projects", json={"title": "test"}, headers=headers).json() == project.j…`；L33断言`client.post("/projects", json={"title": "changed"}, headers=headers).status_code == 4…`；L34断言`client.post("/projects", json={"title": "x"}).status_code == 422`；L38断言`run.status_code == 202`；L39断言`client.post( url, json={**payload, "role": "system"}, headers={"Idempotency-Key": "ba…`；L46断言`client.get("/runs/" + run_id + "/messages").json()[0]["role"] == "user"`；L47断言`client.get("/runs/" + run_id + "/download").status_code == 409`。后续分支沿下方源码相同行号继续阅读。 调用`client.post`、`client.post("/projects", json={"title": "test"}, headers=headers)…`、`project.json`、`run.json`、`client.get("/runs/" + run_id + "/messages").json`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_report_exposes_bounded_toolchain_receipts_without_arbitrary_files`（L52–L74）：接收`client`、`settings`。 控制顺序：L64遍历`evidence.items()`；L68断言`response.status_code == 200`；L69断言`response.json() == evidence`；L70断言`"must-not-be-exposed" not in response.text`；L71断言`client.get(f"/runs/{run_id}/report", headers={"Authorization": "Bearer wrong"}).statu…`。 调用`new_run`、`evidence.items`、`write_json`、`client.get`、`response.json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_api.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L74。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3025`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_api.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7db5b3629a9abbef4cd1fd6a2370456f99f6330cf26c6b66e927f66762987339"} -->
````python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from workbench.api import create_app


@pytest.fixture
def client(settings):
    settings.base_url = "https://model.example.test/v1"
    settings.model = "test-model"
    settings.api_key = SecretStr("dummy-api-test-key")
    app = create_app(settings, start_worker=False)
    with TestClient(app) as c:
        c.headers["Authorization"] = "Bearer " + app.state.token
        yield c


def test_auth_and_host(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    assert client.get("/projects", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/health", headers={"Host": "attacker.example"}).status_code == 400


def test_project_run_idempotency_roles(client):
    headers = {"Idempotency-Key": "project-key"}
    project = client.post("/projects", json={"title": "test"}, headers=headers)
    assert project.status_code == 201
    assert (
        client.post("/projects", json={"title": "test"}, headers=headers).json() == project.json()
    )
    assert client.post("/projects", json={"title": "changed"}, headers=headers).status_code == 409
    assert client.post("/projects", json={"title": "x"}).status_code == 422
    url = "/projects/" + project.json()["id"] + "/runs"
    payload = {"requirement": "个人任务 CRUD"}
    run = client.post(url, json=payload, headers={"Idempotency-Key": "run-key"})
    assert run.status_code == 202
    assert (
        client.post(
            url, json={**payload, "role": "system"}, headers={"Idempotency-Key": "bad"}
        ).status_code
        == 422
    )
    run_id = run.json()["run_id"]
    assert client.get("/runs/" + run_id + "/messages").json()[0]["role"] == "user"
    assert client.get("/runs/" + run_id + "/download").status_code == 409
    assert client.get("/runs/missing").status_code == 404
    assert client.get("/templates").status_code == 200


def test_report_exposes_bounded_toolchain_receipts_without_arbitrary_files(client, settings):
    from conftest import new_run

    from workbench.filesystem import write_json

    run_id = new_run(client.app.state.store)
    directory = settings.data_dir / "runs" / run_id
    evidence = {
        "source-context/context-receipt.json": {"source_is_untrusted_data": True},
        "daytona-verification.json": {"passed": False, "cleanup": "deleted"},
        "tool-failure.json": {"passed": False, "log": "redacted diagnostic"},
    }
    for name, value in evidence.items():
        write_json(directory / name, value)
    write_json(directory / "private.json", {"secret": "must-not-be-exposed"})
    response = client.get(f"/runs/{run_id}/report")
    assert response.status_code == 200
    assert response.json() == evidence
    assert "must-not-be-exposed" not in response.text
    assert (
        client.get(f"/runs/{run_id}/report", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
````
