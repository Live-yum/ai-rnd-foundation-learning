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
    report["spec_digest"] = digest(acceptance_spec().model_dump())
    target = tmp_path / "native-evidence/acceptance.json"
    write_json(target, report)
    receipt = {
        "execution": "managed-runtime",
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
    assert result["database_delivery"] == "existing-dedicated-lab-database-required"
    assert (tmp_path / result["package"]).is_file()
