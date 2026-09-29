"""Local regressions are contracts, not native browser acceptance evidence."""

import pytest
from dotenv import dotenv_values

from workbench import native_frontend
from workbench.generator import PrerequisiteError
from workbench.native import catalog
from workbench.native_delivery import (
    check_database_identity,
    database_identity,
    write_runtime_example,
)
from workbench.settings import Settings


def test_database_identity_does_not_retain_credentials():
    original = "postgresql+psycopg://alice:oldpassword@127.0.0.1:5432/product_codegen"
    identity = database_identity(original)
    assert "oldpassword" not in identity
    receipt = {"database_identity": identity}
    check_database_identity(receipt, original.replace("oldpassword", "newpassword"))
    with pytest.raises(PrerequisiteError, match="数据库"):
        check_database_identity(receipt, original.replace("product_codegen", "other_codegen"))


def test_catalog_config_does_not_claim_acceptance(tmp_path):
    settings = Settings(data_dir=tmp_path, _env_file=None)
    write_runtime_example(settings, "fastapiadmin")
    entry = next(item for item in catalog(settings) if item["id"] == "fastapiadmin")
    assert entry["level"] == "managed-runtime"
    assert entry["configured"] is True
    assert entry["runtime_verified"] is False


def test_vben_public_build_config_excludes_credentials(tmp_path, monkeypatch):
    root = tmp_path / "frontend"
    app = root / "apps/web-antd"
    app.mkdir(parents=True)
    (root / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
    (app / "dist").mkdir()
    (app / "dist/index.html").write_text("<html></html>")
    commands = []

    def tool(command, cwd, timeout, env, **kwargs):
        commands.append(command)
        return {"log": "fixture only", "returncode": 0}

    monkeypatch.setattr(native_frontend, "run_command", tool)
    env = native_frontend.frontend_environment("yudao-vben", "http://127.0.0.1:48080")
    env["API_KEY"] = "never-serialize-this"
    native_frontend.build_frontend("yudao-vben", root, env, tmp_path / "reports")
    data = dotenv_values(app / ".env.production")
    assert data["VITE_GLOB_API_URL"] == "/admin-api"
    assert data["VITE_NITRO_MOCK"] == "false"
    assert "API_KEY" not in data
    assert "never-serialize-this" not in (app / ".env.production.example").read_text()
    assert len(commands) == 3


def test_full_vben_build_has_bounded_rust_parallelism():
    env = native_frontend.frontend_environment("yudao-vben", "http://127.0.0.1:48080")
    assert env["RAYON_NUM_THREADS"] == "2"
    assert "8192" in env["NODE_OPTIONS"]
