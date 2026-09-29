import json
from types import SimpleNamespace

import pytest

from workbench.daytona_tools import SandboxFailure, require_daytona, verify_daytona
from workbench.generator import generate_basic
from workbench.settings import Settings


def authorized(settings):
    return settings.model_copy(
        update={
            "sandbox_backend": "daytona",
            "daytona_upload_authorized": True,
            "daytona_api_url": "https://sandbox.example.test/api",
            "daytona_snapshot": "operator-offline-snapshot",
            "daytona_api_key": Settings(
                daytona_api_key="own-daytona-key", _env_file=None
            ).daytona_api_key,
        }
    )


@pytest.mark.parametrize(
    "updates",
    [
        {},
        {"sandbox_backend": "daytona"},
        {"sandbox_backend": "daytona", "daytona_upload_authorized": True},
    ],
)
def test_no_implicit_cloud_or_key_inheritance(settings, updates):
    configured = settings.model_copy(update=updates)
    with pytest.raises(SandboxFailure):
        require_daytona(configured, "python-basic", "sqlite")
    assert configured.daytona_api_key.get_secret_value() == ""


def test_native_database_and_insecure_endpoints_fail_closed(settings):
    settings = authorized(settings)
    for template, database in (("yudao-vben", "postgresql"), ("python-basic", "postgresql")):
        with pytest.raises(SandboxFailure):
            require_daytona(settings, template, database)
    for url in ("http://evil.test", "https://key@host.test", "https://host.test?token=x"):
        with pytest.raises(SandboxFailure):
            require_daytona(
                settings.model_copy(update={"daytona_api_url": url}), "python-basic", "sqlite"
            )
    assert "own-daytona-key" not in settings.redact("own-daytona-key")


@pytest.mark.parametrize(
    "mode", ["success", "command-failure", "delete-failure", "create-failure", "bad-report"]
)
def test_sdk_contract_cleanup_and_evidence(tmp_path, settings, plan, mode):
    product = tmp_path / "product"
    generate_basic(plan, product)
    (product / ".env").write_text("API_KEY=never-upload", encoding="utf-8")
    uploads, commands, deleted = [], [], []
    report = {"passed": mode != "bad-report", "http": True, "restart": True}

    class FakeClient:
        def create(self, params, timeout):
            assert params["network_block_all"] is True and timeout == 90
            if mode == "create-failure":
                raise OSError("token=own-daytona-key")
            return SimpleNamespace(
                id="owned-test-sandbox",
                fs=SimpleNamespace(
                    create_folder=lambda *a, **kw: None,
                    upload_file=lambda data, path, **kw: uploads.append((data, path)),
                    download_file_stream=lambda *a, **kw: iter([json.dumps(report).encode()]),
                ),
                process=SimpleNamespace(exec=self.execute),
            )

        def execute(self, command, **kwargs):
            commands.append(command)
            return SimpleNamespace(exit_code=1 if mode == "command-failure" else 0)

        def delete(self, sandbox, **kwargs):
            deleted.append((sandbox.id, kwargs))
            if mode == "delete-failure":
                raise OSError("token=own-daytona-key")

    kwargs = {
        "client_factory": lambda s: FakeClient(),
        "params_factory": lambda s, op: {"network_block_all": True},
    }
    if mode == "success":
        evidence = verify_daytona(product, authorized(settings), **kwargs)
        assert evidence["passed"] and evidence["cleanup_confirmed"]
    else:
        with pytest.raises(SandboxFailure):
            verify_daytona(product, authorized(settings), **kwargs)
    evidence = json.loads((tmp_path / "daytona-0.json").read_text(encoding="utf-8"))
    assert evidence["passed"] is (mode == "success")
    assert all(b"never-upload" not in data for data, _ in uploads)
    assert "own-daytona-key" not in json.dumps(evidence)
    if mode != "create-failure":
        assert deleted == [("owned-test-sandbox", {"timeout": 60, "wait": True})]
    if commands:
        assert "--offline" in commands[0]
