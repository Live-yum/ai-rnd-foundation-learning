# tests/test_native.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.native`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `zip_bytes`（L19–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`io.BytesIO`、`zipfile.ZipFile`、`archive.writestr`、`zipfile.ZipInfo`、`buffer.getvalue`。 返回路径：L27的`buffer.getvalue()`。
- `test_native_zip_fixture_does_not_read_wall_clock`（L30–L40）：接收`monkeypatch`。 控制顺序：L36断言`first == zip_bytes()`；L38断言`archive.namelist() == ["sample.py"]`；L39断言`archive.getinfo("sample.py").date_time == (1980, 1, 1, 0, 0, 0)`；L40断言`archive.read("sample.py") == b"value = 1\n"`。 调用`monkeypatch.setattr`、`zip_bytes`、`zipfile.ZipFile`、`io.BytesIO`、`archive.namelist`、`archive.getinfo`、`archive.read`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_zip_fixture_does_not_read_wall_clock.forbidden_clock`（L31–L32）：接收`*args`。 控制顺序：L32抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_protocol_adapter_with_mock_server`（L44–L120）：接收`template`、`plan`。 源码说明：Only protocol tested here, NOT native runtime certification.。 控制顺序：L117断言`result[0][1] == zip_bytes()`；L120断言`any(c[0] == "PUT" for c in calls)`。 调用`NativeConfig`、`NativeClient`、`httpx.MockTransport`、`native_export`、`zip_bytes`、`client.close`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_protocol_adapter_with_mock_server.handler`（L64–L106）：接收`request`。 控制顺序：L69断言`request.headers["authorization"] == "Bearer test-token"`；L70按`path == "/openapi.json"`分支；L74按`path.endswith("/list")`分支；L88按`path.endswith(("/import", "/create-list"))`分支；L91按`"/detail" in path`分支；L96按`template == "yudao-vben"`分支；L102按`"/update" in path`分支；L103按`template == "yudao-vben"`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`calls.append`、`httpx.Response`、`path.endswith`、`zip_bytes`。 返回路径：L71的`httpx.Response( 200, json={"paths": fastapi if template == "fastapiadmin" else yudao} )`；L84的`httpx.Response( 200, json={"code": 0, "data": {"items": rows} if template == "fastapiadmin…`；L90的`httpx.Response(200, json={"code": 0, "data": [1]})`。
- `test_dedicated_database_and_replay`（L123–L133）：接收`tmp_path`、`plan`。 控制顺序：L127断言`"CREATE TABLE" in ddl`；L128断言`create_codegen_tables(plan, url, "run-1")[0] == mapping`；L131断言`set(inspect(engine).get_table_names()) == set(mapping.values())`。 调用`database.as_posix`、`create_codegen_tables`、`create_engine`、`set`、`inspect(engine).get_table_names`、`inspect`、`mapping.values`、`engine.dispose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_production_database_denied`（L145–L147）：接收`plan`、`url`。 调用`pytest.raises`、`create_codegen_tables`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_sources_pinned`（L150–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L151遍历`SOURCES.values()`；L152遍历`sources`；L153断言`len(source["sha"]) == 40`；L154断言`source["required"]`。 调用`SOURCES.values`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L154。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5527`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3f63dcdcd41f3e575efcf43c8eb9f0ec4250033145759133c56315ede79c6b28"} -->
````python
# tests/test_native.py
import io
import json
import zipfile

import httpx
import pytest
from sqlalchemy import create_engine, inspect

from workbench.generator import PrerequisiteError
from workbench.native import (
    SOURCES,
    NativeClient,
    NativeConfig,
    create_codegen_tables,
    native_export,
)


def zip_bytes():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        # The protocol test compares raw export bytes, not just extracted text.
        # Explicit metadata avoids flaky failures across ZIP two-second clock ticks.
        archive.writestr(
            zipfile.ZipInfo("sample.py", date_time=(1980, 1, 1, 0, 0, 0)), "value = 1\n"
        )
    return buffer.getvalue()


def test_native_zip_fixture_does_not_read_wall_clock(monkeypatch):
    def forbidden_clock(*args):
        raise AssertionError("ZIP protocol fixtures must have deterministic metadata")

    monkeypatch.setattr(zipfile.time, "localtime", forbidden_clock)
    first = zip_bytes()
    assert first == zip_bytes()
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        assert archive.namelist() == ["sample.py"]
        assert archive.getinfo("sample.py").date_time == (1980, 1, 1, 0, 0, 0)
        assert archive.read("sample.py") == b"value = 1\n"


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_real_protocol_adapter_with_mock_server(template, plan):
    """Only protocol tested here, NOT native runtime certification."""
    table = "wb_12345678_task"
    calls = []
    fastapi = {
        "/api/v1/gencode/list": {"get": {}},
        "/api/v1/gencode/import": {"post": {}},
        "/api/v1/gencode/detail/{table_id}": {"get": {}},
        "/api/v1/gencode/update/{table_id}": {"put": {}},
        "/api/v1/gencode/batch/output": {"patch": {}},
    }
    yudao = {
        "/admin-api/infra/codegen/table/list": {"get": {}},
        "/admin-api/infra/codegen/create-list": {"post": {}},
        "/admin-api/infra/codegen/detail": {"get": {}},
        "/admin-api/infra/codegen/update": {"put": {}},
        "/admin-api/infra/codegen/download": {"get": {}},
    }
    imported = False

    def handler(request):
        nonlocal imported
        path = request.url.path
        data = json.loads(request.content) if request.content else None
        calls.append((request.method, path, data))
        assert request.headers["authorization"] == "Bearer test-token"
        if path == "/openapi.json":
            return httpx.Response(
                200, json={"paths": fastapi if template == "fastapiadmin" else yudao}
            )
        if path.endswith("/list"):
            rows = (
                (
                    [{"table_name": table, "id": 1}]
                    if template == "fastapiadmin"
                    else [{"tableName": table, "id": 1}]
                )
                if imported
                else []
            )
            return httpx.Response(
                200,
                json={"code": 0, "data": {"items": rows} if template == "fastapiadmin" else rows},
            )
        if path.endswith(("/import", "/create-list")):
            imported = True
            return httpx.Response(200, json={"code": 0, "data": [1]})
        if "/detail" in path:
            detail = {
                "table_name": table,
                "columns": [{"column_name": x.name} for x in plan.entities[0].fields],
            }
            if template == "yudao-vben":
                detail = {
                    "table": {"id": 1, "tableName": table, "frontType": 30},
                    "columns": [{"columnName": x.name} for x in plan.entities[0].fields],
                }
            return httpx.Response(200, json={"code": 0, "data": detail})
        if "/update" in path:
            if template == "yudao-vben":
                assert data["table"]["frontType"] == 40
            return httpx.Response(200, json={"code": 0, "data": True})
        return httpx.Response(200, content=zip_bytes(), headers={"Content-Type": "application/zip"})

    config = NativeConfig(
        base_url="http://127.0.0.1:8001",
        openapi_path="/openapi.json",
        token_env="NATIVE_TOKEN",
        database_url_env="NATIVE_DB",
    )
    client = NativeClient(config, "test-token", httpx.MockTransport(handler))
    try:
        result = native_export(client, template, {"task": table}, plan)
        assert result[0][1] == zip_bytes()
    finally:
        client.close()
    assert any(c[0] == "PUT" for c in calls)


def test_dedicated_database_and_replay(tmp_path, plan):
    database = tmp_path / "test-codegen.db"
    url = "sqlite:///" + database.as_posix()
    mapping, ddl = create_codegen_tables(plan, url, "run-1")
    assert "CREATE TABLE" in ddl
    assert create_codegen_tables(plan, url, "run-1")[0] == mapping
    engine = create_engine(url)
    try:
        assert set(inspect(engine).get_table_names()) == set(mapping.values())
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "url",
    [
        "sqlite:///relative-codegen.db",
        "sqlite:////tmp/production.db",
        "postgresql://x@remote.test/prod_codegen",
        "mysql://x@localhost/test_codegen",
    ],
)
def test_production_database_denied(plan, url):
    with pytest.raises(PrerequisiteError):
        create_codegen_tables(plan, url, "run")


def test_all_sources_pinned():
    for sources in SOURCES.values():
        for source in sources:
            assert len(source["sha"]) == 40
            assert source["required"]
````
