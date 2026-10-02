# tests/test_native_managed.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.native_acceptance`、`workbench.native_delivery`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_runtime_configuration_requires_explicit_empty_database_authorization`（L22–L39）：接收`tmp_path`、`monkeypatch`。 控制顺序：L27断言`runtime_enabled(settings, "fastapiadmin")`；L37断言`url.endswith("owned_codegen")`。 调用`Settings`、`write_runtime_example`、`runtime_enabled`、`monkeypatch.setenv`、`pytest.raises`、`runtime_config`、`json.loads`、`path.read_text`、`write_json`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_export_is_not_implicitly_managed`（L42–L46）：接收`tmp_path`。 控制顺序：L46断言`not runtime_enabled(settings, "fastapiadmin")`。 调用`Settings`、`settings.prepare`、`write_json`、`runtime_enabled`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_cannot_read_arbitrary_secret_environment`（L49–L54）：接收`tmp_path`。 调用`Settings`、`write_runtime_example`、`write_json`、`pytest.raises`、`runtime_config`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_java_json_field_names_follow_generator_camel_case`（L57–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L58断言`wire_name("yudao-vben", "display_name") == "displayName"`；L59断言`wire_name("fastapiadmin", "display_name") == "display_name"`；L62断言`"displayName" in sample_record(entity, template="yudao-vben")`。 调用`wire_name`、`acceptance_spec().entities[0].model_copy`、`acceptance_spec`、`sample_record`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verified_fixture`（L65–L143）：接收`tmp_path`。 控制顺序：L102遍历`PROFILES["fastapiadmin"]["protected"]`；L109遍历`report["entities"]`。 调用`product.mkdir`、`(product / "example.py").write_text`、`acceptance_spec`、`prefix.endswith`、`path.parent.mkdir`、`path.write_text`、`sha`、`pages.append`、`digest`等。 返回路径：L143的`product, receipt, target`。
- `test_managed_verify_binds_exact_source_and_evidence`（L146–L153）：接收`tmp_path`。 控制顺序：L149断言`report["validation_level"] == "runtime"`；L150断言`report["production_ready"] is False`。 调用`verified_fixture`、`managed_verify`、`(product / "example.py").write_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_managed_verify_rejects_incomplete_or_modified_evidence`（L156–L165）：接收`tmp_path`。 调用`verified_fixture`、`json.loads`、`target.read_text`、`write_json`、`pytest.raises`、`managed_verify`、`sha`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_runtime_package_preserves_validation_level`（L168–L175）：接收`tmp_path`。 控制顺序：L172断言`result["runtime_verified"] is True`；L173断言`result["package"] == "native-runtime.zip"`；L174断言`result["database_delivery"] == "standalone-fresh-database-bootstrap"`；L175断言`(tmp_path / result["package"]).is_file()`。 调用`verified_fixture`、`managed_verify`、`managed_package`、`(tmp_path / result["package"]).is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_managed.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L175。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6673`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_managed.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c3d1c427937c59203173a1f4bc86232450b63b770843558415c7c19aa0197ebd"} -->
````python
# tests/test_native_managed.py
"""Local unit checks are not native runtime evidence; Actions executes the real engines."""

import json

import pytest

from scripts.ci_native_generated import acceptance_spec
from workbench.domain import digest
from workbench.filesystem import manifest, sha, write_json
from workbench.generator import PrerequisiteError
from workbench.native_acceptance import sample_record, wire_name
from workbench.native_delivery import (
    managed_package,
    managed_verify,
    runtime_config,
    runtime_enabled,
    write_runtime_example,
)
from workbench.settings import Settings


def test_runtime_configuration_requires_explicit_empty_database_authorization(
    tmp_path, monkeypatch
):
    settings = Settings(data_dir=tmp_path, _env_file=None)
    path = write_runtime_example(settings, "fastapiadmin")
    assert runtime_enabled(settings, "fastapiadmin")
    monkeypatch.setenv(
        "NATIVE_FASTAPIADMIN_DATABASE_URL", "postgresql+psycopg://u:p@127.0.0.1/owned_codegen"
    )
    with pytest.raises(PrerequisiteError, match="批准"):
        runtime_config(settings, "fastapiadmin")
    data = json.loads(path.read_text())
    data["initialize_empty_database"] = True
    write_json(path, data)
    _, url = runtime_config(settings, "fastapiadmin")
    assert url.endswith("owned_codegen")
    with pytest.raises(FileExistsError):
        write_runtime_example(settings, "fastapiadmin")


def test_source_export_is_not_implicitly_managed(tmp_path):
    settings = Settings(data_dir=tmp_path, _env_file=None)
    settings.prepare()
    write_json(tmp_path / "native/fastapiadmin.json", {})
    assert not runtime_enabled(settings, "fastapiadmin")


def test_runtime_cannot_read_arbitrary_secret_environment(tmp_path):
    settings = Settings(data_dir=tmp_path, _env_file=None)
    path = write_runtime_example(settings, "yudao-vben")
    write_json(path, {"database_url_env": "API_KEY", "initialize_empty_database": True})
    with pytest.raises(PrerequisiteError, match="NATIVE_"):
        runtime_config(settings, "yudao-vben")


def test_java_json_field_names_follow_generator_camel_case():
    assert wire_name("yudao-vben", "display_name") == "displayName"
    assert wire_name("fastapiadmin", "display_name") == "display_name"
    entity = acceptance_spec().entities[0].model_copy(deep=True)
    entity.fields[0].name = "display_name"
    assert "displayName" in sample_record(entity, template="yudao-vben")


def verified_fixture(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "example.py").write_text("x = 1\n")
    report = {
        name: True
        for name in (
            "generated_runtime_verified",
            "native_codegen",
            "automatic_mount",
            "menu_and_permissions",
            "real_crud",
            "restart_persistence",
            "frontend_build",
            "frontend_typecheck",
            "real_browser",
            "source_unmodified",
        )
    }
    report["portable_restored"] = {
        "passed": True,
        "fresh_database": True,
        "frontend_started": True,
        "installed_from_lock": True,
        "standalone_launcher": True,
        "restart": True,
        "source_database_reused": False,
        "original_platform_imported": False,
        "model_required": False,
    }
    # Explicit unit-test evidence; actual UI is exercised by native Actions.
    from workbench.native_style import PROFILES

    report["template"] = "fastapiadmin"
    report["entities"] = [entity.name for entity in acceptance_spec().entities]
    root = product / "frontend/web"
    protected = {}
    for prefix in PROFILES["fastapiadmin"]["protected"]:
        name = prefix + "fixture.vue" if prefix.endswith("/") else prefix
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("explicit-unit-fixture", encoding="utf-8")
        protected[name] = sha(path)
    pages = []
    for entity in report["entities"]:
        name = f"src/views/module_rnd/{entity}/index.vue"
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("explicit-unit-page-fixture", encoding="utf-8")
        pages.append(
            {
                "path": name,
                "sha256": sha(path),
                "native_components": ["FaSearchBar", "FaTable", "FaDialog", "FaForm"],
            }
        )
    report["native_style"] = {
        "template": "fastapiadmin",
        "ui_family": PROFILES["fastapiadmin"]["family"],
        "passed": True,
        "shell_and_theme_unchanged": True,
        "generic_frontend_substitution": False,
        "protected_files": protected,
        "protected_source_digest": digest(protected),
        "generated_pages": pages,
    }
    report["spec_digest"] = digest(acceptance_spec().model_dump())
    target = tmp_path / "native-evidence/acceptance.json"
    write_json(target.with_name("approved-spec.json"), acceptance_spec().model_dump())
    write_json(target, report)
    receipt = {
        "execution": "managed-runtime",
        "template": "fastapiadmin",
        "files": manifest(product),
        "spec_digest": report["spec_digest"],
        "evidence_sha256": sha(target),
    }
    write_json(tmp_path / "native-generation.json", receipt)
    return product, receipt, target


def test_managed_verify_binds_exact_source_and_evidence(tmp_path):
    product, receipt, target = verified_fixture(tmp_path)
    report = managed_verify(product, receipt)
    assert report["validation_level"] == "runtime"
    assert report["production_ready"] is False
    (product / "example.py").write_text("x = 2\n")
    with pytest.raises(PrerequisiteError, match="变化"):
        managed_verify(product, receipt)


def test_managed_verify_rejects_incomplete_or_modified_evidence(tmp_path):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text())
    data["real_browser"] = False
    write_json(target, data)
    with pytest.raises(PrerequisiteError):
        managed_verify(product, receipt)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="门槛"):
        managed_verify(product, receipt)


def test_native_runtime_package_preserves_validation_level(tmp_path):
    product, receipt, _ = verified_fixture(tmp_path)
    report = managed_verify(product, receipt)
    result = managed_package(product, report)
    assert result["runtime_verified"] is True
    assert result["package"] == "native-runtime.zip"
    assert result["database_delivery"] == "standalone-fresh-database-bootstrap"
    assert (tmp_path / result["package"]).is_file()
````
