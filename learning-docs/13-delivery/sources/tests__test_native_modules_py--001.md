# tests/test_native_modules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`workbench.native_modules`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_two_native_entities_have_distinct_tables`（L16–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L17遍历`("fastapiadmin", "yudao-vben")`；L19断言`len(set(mapping.values())) == 2`；L20断言`len(tables) == 2`；L21断言`tables[0].name != tables[1].name`；L22遍历`tables`；L24断言`table.name in sql`；L25断言`table.c.name.nullable is False`。 调用`native_metadata`、`acceptance_spec`、`len`、`set`、`mapping.values`、`str`、`CreateTable(table).compile`、`CreateTable`、`postgresql.dialect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_framework_specific_audit_columns_and_sequences`（L28–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L30断言`{"uuid", "is_deleted", "created_time", "created_id", "status"} <= set(tables[0].c.key…`；L32断言`{"creator", "create_time", "deleted", "tenant_id"} <= set(tables[0].c.keys())`；L33断言`tables[0].c.id.default.name == tables[0].name + "_seq"`。 调用`native_metadata`、`acceptance_spec`、`set`、`tables[0].c.keys`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_label_cannot_be_code_or_path`（L39–L43）：接收`label`。 调用`acceptance_spec().model_dump`、`acceptance_spec`、`pytest.raises`、`validate_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shared_scope_never_silently_replaces_user_isolation`（L46–L50）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`acceptance_spec().model_dump`、`acceptance_spec`、`pytest.raises`、`validate_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_normalized_business_name_collision_rejected`（L53–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`acceptance_spec().model_dump`、`acceptance_spec`、`pytest.raises`、`validate_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_audit_field_collision_rejected`（L62–L66）：接收`name`。 调用`acceptance_spec().model_dump`、`acceptance_spec`、`pytest.raises`、`validate_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `zip_bytes`（L69–L74）：接收`contents`。 控制顺序：L72遍历`contents.items()`。 调用`io.BytesIO`、`zipfile.ZipFile`、`contents.items`、`archive.writestr`、`target.getvalue`。 返回路径：L74的`target.getvalue()`。
- `constants_file`（L77–L84）：接收`root`。 调用`path.parent.mkdir`、`path.write_text`。 返回路径：L84的`path`。
- `test_yudao_generated_source_is_mounted_in_real_native_modules`（L87–L106）：接收`tmp_path`。 控制顺序：L102断言`(backend / java).read_text() == "class WbDeviceController {}"`；L103断言`(frontend / "apps/web-antd/src/views/infra/wbdevice/index.vue").exists()`；L104断言`"WB_DEVICE_NOT_EXISTS" in constants.read_text(encoding="utf-8")`；L105断言`"TODO 补充编号" not in constants.read_text(encoding="utf-8")`；L106断言`result["error_constants"][0]["number"] > 1_900_000_000`。 调用`constants_file`、`zip_bytes`、`mount_yudao_export`、`acceptance_spec`、`set`、`(backend / java).read_text`、`(frontend / "apps/web-antd/src/views/infra/wbdevice/index.vue").e…`、`constants.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_export_cannot_overwrite_native_auth`（L109–L122）：接收`tmp_path`。 调用`pytest.raises`、`mount_yudao_export`、`zip_bytes`、`acceptance_spec`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_time_import_repair_records_original_export_hash`（L125–L152）：接收`tmp_path`。 控制顺序：L148断言`receipt["source_sha256"] == sha256(original.encode()).hexdigest()`；L149断言`receipt["sha256"] == sha256((backend / java).read_bytes()).hexdigest()`；L150断言`receipt["source_sha256"] != receipt["sha256"]`；L151断言`receipt["compatibility_applied"] is True`；L152断言`(backend / java).read_text().replace("\nimport java.time.LocalDate;", "") == original`。 调用`constants_file`、`mount_yudao_export`、`zip_bytes`、`acceptance_spec`、`set`、`sha256(original.encode()).hexdigest`、`sha256`、`original.encode`、`sha256((backend / java).read_bytes()).hexdigest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_http_response_is_decompressed_once`（L155–L185）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L183断言`client.paths == {}`。 调用`json.dumps({"openapi": "3.1.0", "paths": {}}).encode`、`json.dumps`、`NativeClient`、`NativeConfig`、`httpx.MockTransport`、`client.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_http_response_is_decompressed_once.handler`（L165–L170）：接收`request`。 调用`httpx.Response`、`gzip.compress`。 返回路径：L166的`httpx.Response( 200, headers={"content-encoding": "gzip", "content-type": "application/jso…`。
- `test_every_native_column_has_a_codegen_comment`（L188–L191）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L189遍历`("fastapiadmin", "yudao-vben")`；L191断言`all(column.comment for table in tables for column in table.c)`。 调用`native_metadata`、`acceptance_spec`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_logic_delete_matches_pinned_postgres_seed`（L194–L200）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L198断言`isinstance(tables[0].c.deleted.type, SmallInteger)`；L199断言`str(tables[0].c.deleted.server_default.arg) == "0"`；L200断言`"deleted SMALLINT" in str(CreateTable(tables[0]).compile(dialect=postgresql.dialect()…`。 调用`native_metadata`、`acceptance_spec`、`isinstance`、`str`、`CreateTable(tables[0]).compile`、`CreateTable`、`postgresql.dialect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_modules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L200。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7841`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_modules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4b75fee83b8186e5d633e4d0bb7e544a308a719298512fb643ff19ae51a77e32"} -->
````python
# tests/test_native_modules.py
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


def test_yudao_time_import_repair_records_original_export_hash(tmp_path):
    from hashlib import sha256

    backend, frontend, reports = (tmp_path / name for name in ("backend", "frontend", "reports"))
    constants_file(backend)
    java = (
        "yudao-module-infra/yudao-module-infra-server/src/main/java/demo/wbdevice/WbDeviceDO.java"
    )
    original = "package demo.wbdevice;\nclass WbDeviceDO { private LocalDate day; }\n"
    result = mount_yudao_export(
        zip_bytes(
            {
                java: original,
                "yudao-module-infra/yudao-module-infra-api/src/main/java/demo/ErrorCodeConstants_手动操作.java": 'ErrorCode WB_DEVICE_NOT_EXISTS = new ErrorCode(TODO 补充编号, "设备不存在");',
            }
        ),
        backend,
        frontend,
        acceptance_spec().entities[0],
        reports,
        set(),
    )
    receipt = result["files"][0]
    assert receipt["source_sha256"] == sha256(original.encode()).hexdigest()
    assert receipt["sha256"] == sha256((backend / java).read_bytes()).hexdigest()
    assert receipt["source_sha256"] != receipt["sha256"]
    assert receipt["compatibility_applied"] is True
    assert (backend / java).read_text().replace("\nimport java.time.LocalDate;", "") == original


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
````
