"""Small offline fixtures verify Java packaging guards; Maven/boot is tested separately in CI."""

import io
import zipfile

import pytest

from workbench.native_environment import prepare_yudao_postgres, verify_aggregate_jars


def fixture_jar(root, *, executable_dependency=False, driver=True):
    target = root / "yudao-server/target/yudao-server.jar"
    target.parent.mkdir(parents=True)
    with zipfile.ZipFile(target, "w") as archive:
        for name in ("infra", "system"):
            nested = io.BytesIO()
            prefix = "BOOT-INF/classes/" if executable_dependency else ""
            with zipfile.ZipFile(nested, "w") as dependency:
                dependency.writestr(prefix + f"cn/iocoder/yudao/module/{name}/Example.class", b"fixture")
            archive.writestr(f"BOOT-INF/lib/yudao-module-{name}-server-test.jar", nested.getvalue())
        if driver:
            archive.writestr("BOOT-INF/lib/postgresql-test.jar", b"fixture")


def test_ordinary_dependency_jars_accepted(tmp_path):
    fixture_jar(tmp_path)
    verify_aggregate_jars(tmp_path)


def test_executable_dependency_jars_rejected(tmp_path):
    fixture_jar(tmp_path, executable_dependency=True)
    with pytest.raises(ValueError, match="executable service jar"):
        verify_aggregate_jars(tmp_path)


def test_missing_postgres_driver_rejected(tmp_path):
    fixture_jar(tmp_path, driver=False)
    with pytest.raises(ValueError, match="PostgreSQL JDBC"):
        verify_aggregate_jars(tmp_path)


def test_jdbc_declaration_is_idempotent_and_preserves_source(tmp_path):
    backend = tmp_path / "backend"
    pom = backend / "yudao-server/pom.xml"
    pom.parent.mkdir(parents=True)
    original = '<project xmlns="http://maven.apache.org/POM/4.0.0"><dependencies></dependencies></project>\n'
    pom.write_text(original, encoding="utf-8")
    reports = tmp_path / "reports"
    prepare_yudao_postgres(backend, reports)
    first = pom.read_text(encoding="utf-8")
    prepare_yudao_postgres(backend, reports)
    assert pom.read_text(encoding="utf-8") == first
    assert first.count("<artifactId>postgresql</artifactId>") == 1
    assert "<scope>runtime</scope>" in first
    assert (reports / "jdbc-configuration.json").exists()


def test_unexpected_pom_fails_without_write(tmp_path):
    pom = tmp_path / "yudao-server/pom.xml"
    pom.parent.mkdir()
    original = '<project xmlns="http://maven.apache.org/POM/4.0.0"></project>'
    pom.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError, match="no dependency section"):
        prepare_yudao_postgres(tmp_path, tmp_path / "reports")
    assert pom.read_text(encoding="utf-8") == original
