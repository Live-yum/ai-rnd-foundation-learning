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
        archive.writestr("sample.py", "value = 1\n")
    return buffer.getvalue()


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
