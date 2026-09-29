"""Adapter contracts; real native services remain mandatory in native-runtime Actions."""

import io
import zipfile

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from scripts.ci_native_generated import acceptance_spec
from workbench.native_modules import mount_yudao_export, native_metadata, validate_plan

URL = "postgresql+psycopg://native:lab@127.0.0.1/native_codegen"


def test_two_native_entities_have_distinct_tables():
    for template in ("fastapiadmin", "yudao-vben"):
        _, tables, mapping = native_metadata(template, acceptance_spec(), URL, "two-entities")
        assert len(set(mapping.values())) == 2
        assert len(tables) == 2
        assert tables[0].name != tables[1].name
        for table in tables:
            sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
            assert table.name in sql
            assert table.c.name.nullable is False


def test_framework_specific_audit_columns_and_sequences():
    _, tables, _ = native_metadata("fastapiadmin", acceptance_spec(), URL, "audit")
    assert {"uuid", "is_deleted", "created_time", "created_id", "status"} <= set(tables[0].c.keys())
    _, tables, _ = native_metadata("yudao-vben", acceptance_spec(), URL, "audit")
    assert {"creator", "create_time", "deleted", "tenant_id"} <= set(tables[0].c.keys())
    assert tables[0].c.id.default.name == tables[0].name + "_seq"


@pytest.mark.parametrize(
    "label", ['bad"quote', "bad'quote", "line\nbreak", "tab\there", "../../path", "back\\slash"]
)
def test_native_label_cannot_be_code_or_path(label):
    data = acceptance_spec().model_dump()
    data["entities"][0]["description"] = label
    with pytest.raises(ValueError):
        validate_plan(data)


def test_native_shared_scope_never_silently_replaces_user_isolation():
    data = acceptance_spec().model_dump()
    data["data_scope"] = "per_user"
    with pytest.raises(ValueError, match="explicitly approved shared"):
        validate_plan(data)


def test_native_normalized_business_name_collision_rejected():
    data = acceptance_spec().model_dump()
    data["entities"][0]["name"] = "a_b"
    data["entities"][1]["name"] = "ab"
    with pytest.raises(ValueError, match="collide"):
        validate_plan(data)


@pytest.mark.parametrize("name", ["status", "uuid", "tenant_id", "creator", "is_deleted"])
def test_native_audit_field_collision_rejected(name):
    data = acceptance_spec().model_dump()
    data["entities"][0]["fields"][0]["name"] = name
    with pytest.raises(ValueError, match="audit"):
        validate_plan(data)


def zip_bytes(contents):
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w") as archive:
        for name, text in contents.items():
            archive.writestr(name, text)
    return target.getvalue()


def constants_file(root):
    path = (
        root
        / "yudao-module-infra/yudao-module-infra-api/src/main/java/cn/iocoder/yudao/module/infra/enums/ErrorCodeConstants.java"
    )
    path.parent.mkdir(parents=True)
    path.write_text("public interface ErrorCodeConstants {\n}\n", encoding="utf-8")
    return path


def test_yudao_generated_source_is_mounted_in_real_native_modules(tmp_path):
    backend, frontend, reports = (tmp_path / name for name in ("backend", "frontend", "reports"))
    constants = constants_file(backend)
    java = "yudao-module-infra/yudao-module-infra-server/src/main/java/cn/iocoder/yudao/module/infra/controller/admin/wbdevice/WbDeviceController.java"
    exported = zip_bytes(
        {
            java: "class WbDeviceController {}",
            "yudao-ui-admin-vben/src/views/infra/wbdevice/index.vue": "<template>Native</template>",
            "yudao-module-infra/yudao-module-infra-api/src/main/java/cn/iocoder/yudao/module/infra/enums/ErrorCodeConstants_手动操作.java": 'ErrorCode WB_DEVICE_NOT_EXISTS = new ErrorCode(TODO 补充编号, "设备不存在");',
            "sql/sql.sql": "-- Native menu SQL retained, not blindly executed",
        }
    )
    result = mount_yudao_export(
        exported, backend, frontend, acceptance_spec().entities[0], reports, set()
    )
    assert (backend / java).read_text() == "class WbDeviceController {}"
    assert (frontend / "apps/web-antd/src/views/infra/wbdevice/index.vue").exists()
    assert "WB_DEVICE_NOT_EXISTS" in constants.read_text(encoding="utf-8")
    assert "TODO 补充编号" not in constants.read_text(encoding="utf-8")
    assert result["error_constants"][0]["number"] > 1_900_000_000


def test_yudao_export_cannot_overwrite_native_auth(tmp_path):
    with pytest.raises(ValueError, match="Unexpected"):
        mount_yudao_export(
            zip_bytes(
                {
                    "yudao-module-infra/yudao-module-infra-server/src/main/java/security/Auth.java": "bad"
                }
            ),
            tmp_path / "backend",
            tmp_path / "frontend",
            acceptance_spec().entities[0],
            tmp_path / "reports",
            set(),
        )


def test_native_http_response_is_decompressed_once():
    import gzip
    import json

    import httpx

    from workbench.native import NativeClient, NativeConfig

    envelope = json.dumps({"openapi": "3.1.0", "paths": {}}).encode()

    def handler(request):
        return httpx.Response(
            200,
            headers={"content-encoding": "gzip", "content-type": "application/json"},
            content=gzip.compress(envelope),
        )

    client = NativeClient(
        NativeConfig(
            base_url="http://127.0.0.1:8001",
            openapi_path="/openapi.json",
            token_env="NATIVE_TOKEN",
            database_url_env="NATIVE_DATABASE_URL",
        ),
        "lab-token",
        transport=httpx.MockTransport(handler),
    )
    try:
        assert client.paths == {}
    finally:
        client.close()


def test_every_native_column_has_a_codegen_comment():
    for template in ("fastapiadmin", "yudao-vben"):
        _, tables, _ = native_metadata(template, acceptance_spec(), URL, "comments")
        assert all(column.comment for table in tables for column in table.c)


def test_yudao_logic_delete_matches_pinned_postgres_seed():
    from sqlalchemy import SmallInteger

    _, tables, _ = native_metadata("yudao-vben", acceptance_spec(), URL, "logic-delete")
    assert isinstance(tables[0].c.deleted.type, SmallInteger)
    assert str(tables[0].c.deleted.server_default.arg) == "0"
    assert "deleted SMALLINT" in str(CreateTable(tables[0]).compile(dialect=postgresql.dialect()))
