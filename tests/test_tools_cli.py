import sys

import pytest
from typer.testing import CliRunner

from workbench.cli import app
from workbench.tools import ToolFailure, clean_env, run_command


def test_clean_environment(monkeypatch):
    for key in ["API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"]:
        monkeypatch.setenv(key, "sensitive")
    assert not {"API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"} & clean_env().keys()


def test_fixed_command_exit_and_timeout(tmp_path):
    assert run_command([sys.executable, "-c", "print(42)"], tmp_path)["returncode"] == 0
    with pytest.raises(ToolFailure):
        run_command([sys.executable, "-c", "raise SystemExit(7)"], tmp_path)
    with pytest.raises(ToolFailure):
        run_command([sys.executable, "-c", "import time; time.sleep(10)"], tmp_path, timeout=0.1)


def test_cli_discovery():
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "native-source-export" in result.output


def test_clean_environment_preserves_windows_runtime_without_model_credentials(monkeypatch):
    monkeypatch.setenv("SystemRoot", r"C:\Windows")
    monkeypatch.setenv("WINDIR", r"C:\Windows")
    monkeypatch.setenv("API_KEY", "must-not-enter-product-process")
    env = clean_env({"PRODUCT_DATA_DIR": "isolated-product-data"})
    assert next(value for key, value in env.items() if key.upper() == "SYSTEMROOT") == r"C:\Windows"
    assert env["WINDIR"] == r"C:\Windows"
    assert env["PRODUCT_DATA_DIR"] == "isolated-product-data"
    assert "API_KEY" not in env
