# tests/test_workbench_startup.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_missing_models_serves_shell_but_prevents_new_work`（L6–L21）：接收`settings`。 控制顺序：L8断言`client.get("/").status_code == 200`；L13断言`project.status_code == 201`；L19断言`result.status_code == 503`；L20断言`"配置" in result.json()["detail"]`；L21断言`client.get("/runs").json() == []`。 调用`TestClient`、`create_app`、`client.get`、`client.post`、`project.json`、`result.json`、`client.get("/runs").json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_api_body_never_echoes_private_user_input`（L24–L33）：接收`settings`。 控制顺序：L32断言`result.status_code == 422`；L33断言`"dummy-secret-private" not in result.text`。 调用`TestClient`、`create_app`、`client.post`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupt_config_models_endpoint_fails_safely`（L36–L46）：接收`settings`。 控制顺序：L44断言`response.status_code == 503`；L45断言`"dummy-private-secret" not in response.text`；L46断言`client.get("/").status_code == 200`。 调用`settings.prepare`、`path.write_text`、`path.chmod`、`TestClient`、`create_app`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shell_has_local_resource_and_frame_security_policy`（L49–L57）：接收`settings`。 控制顺序：L52断言`client.get("/ui").content == response.content`；L53断言`client.get("/ui/").content == response.content`；L54断言`response.headers["cache-control"] == "no-store"`；L55断言`response.headers["x-content-type-options"] == "nosniff"`；L56断言`"script-src 'self'" in response.headers["content-security-policy"]`；L57断言`"frame-ancestors 'none'" in response.headers["content-security-policy"]`。 调用`TestClient`、`create_app`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_workbench_startup.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L57。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2551`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_workbench_startup.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5b59983721c5de4f79b64238e2940e9b397a7d38b0ee2315a3c082bbc2b06feb"} -->
````python
# tests/test_workbench_startup.py
from fastapi.testclient import TestClient

from workbench.api import create_app


def test_missing_models_serves_shell_but_prevents_new_work(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        assert client.get("/").status_code == 200
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        project = client.post(
            "/projects", json={"title": "尚未配置"}, headers={"Idempotency-Key": "p"}
        )
        assert project.status_code == 201
        result = client.post(
            f"/projects/{project.json()['id']}/runs",
            json={"requirement": "任务管理"},
            headers={"Idempotency-Key": "r"},
        )
        assert result.status_code == 503
        assert "配置" in result.json()["detail"]
        assert client.get("/runs").json() == []


def test_invalid_api_body_never_echoes_private_user_input(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        result = client.post(
            "/projects",
            json={"title": "ok", "api_key": "dummy-secret-private"},
            headers={"Idempotency-Key": "x"},
        )
        assert result.status_code == 422
        assert "dummy-secret-private" not in result.text


def test_corrupt_config_models_endpoint_fails_safely(settings):
    settings.prepare()
    path = settings.data_dir / "model-settings.json"
    path.write_text('{"api_key":"dummy-private-secret",broken}', encoding="utf-8")
    path.chmod(0o600)
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.get("/models")
        assert response.status_code == 503
        assert "dummy-private-secret" not in response.text
        assert client.get("/").status_code == 200


def test_shell_has_local_resource_and_frame_security_policy(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        response = client.get("/")
        assert client.get("/ui").content == response.content
        assert client.get("/ui/").content == response.content
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "script-src 'self'" in response.headers["content-security-policy"]
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
````
