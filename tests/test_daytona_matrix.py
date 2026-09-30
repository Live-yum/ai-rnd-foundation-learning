"""Fail-closed registered runtime profiles; actual services run in the matrix Action."""

import io
import json
import zipfile
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from scripts.daytona_bootstrap import snapshot_resources
from workbench.daytona_profiles import (
    dependency_identity,
    profile_key,
    require_runtime_report,
    snapshot_for,
)
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest
from workbench.generator import PrerequisiteError
from workbench.sandbox import checks_for, harness_archive, params_for, verify_in_daytona
from workbench.tools import clean_env


@pytest.mark.parametrize(
    "template,database",
    [
        ("python-basic", "sqlite"),
        ("python-basic", "postgresql"),
        ("fastapiadmin", "postgresql"),
        ("yudao-vben", "postgresql"),
    ],
)
def test_exact_registered_profiles(template, database, settings):
    assert profile_key(template, {"database": database}) == template + "/" + database
    settings.daytona_snapshot = "fallback-local-snapshot"
    settings.daytona_snapshots = {template + "/" + database: "selected-local-snapshot"}
    assert snapshot_for(settings, template, {"database": database}) == "selected-local-snapshot"
    params = params_for(settings, "test-local", template, {"database": database})
    assert params.network_block_all is True and params.public is False
    assert params.snapshot == "selected-local-snapshot"
    assert params.auto_stop_interval >= (
        5 if database == "sqlite" else settings.daytona_runtime_timeout // 60
    )


@pytest.mark.parametrize(
    "template,database",
    [("yudao-vben", "sqlite"), ("fastapiadmin", "mysql"), ("shell", "postgresql")],
)
def test_unregistered_profiles_are_not_guessed(template, database):
    with pytest.raises(ValueError):
        profile_key(template, {"database": database})
    with pytest.raises(PrerequisiteError):
        checks_for(template, {"database": database})


def report(template="yudao-vben"):
    return {
        key: True
        for key in (
            "passed",
            "http",
            "restart",
            "fresh_database",
            "locked_install",
            "offline",
            "services_stopped",
            "frontend_build",
            "frontend_typecheck",
            "browser",
            "permissions",
            "standalone_launcher",
            "business_rules",
        )
    } | {
        "template": template,
        "database": "postgresql",
        "source_digest": "f" * 64,
        "host_database_used": False,
        "host_credentials_used": False,
    }


@pytest.mark.parametrize(
    "key",
    [
        "passed",
        "http",
        "restart",
        "fresh_database",
        "locked_install",
        "offline",
        "services_stopped",
        "frontend_build",
        "frontend_typecheck",
        "browser",
        "permissions",
        "standalone_launcher",
        "business_rules",
    ],
)
@pytest.mark.parametrize("bad", [None, False, "true", 1])
def test_every_runtime_gate_requires_actual_boolean_success(key, bad):
    value = report()
    value[key] = bad
    with pytest.raises(ValueError):
        require_runtime_report(value, "yudao-vben", {"database": "postgresql"}, "f" * 64)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("template", "fastapiadmin"),
        ("database", "sqlite"),
        ("source_digest", "wrong"),
        ("host_database_used", True),
        ("host_credentials_used", True),
        ("host_database_used", 0),
    ],
)
def test_runtime_identity_and_no_host_database_must_match(key, bad):
    value = report()
    value[key] = bad
    with pytest.raises(ValueError):
        require_runtime_report(value, "yudao-vben", {"database": "postgresql"}, "f" * 64)


def test_runtime_accepts_complete_matching_report_only():
    require_runtime_report(report(), "yudao-vben", {"database": "postgresql"}, "f" * 64)


def test_dependency_identity_does_not_use_host_keys_or_cached_binaries(tmp_path):
    atomic_text(tmp_path / "pyproject.toml", "project")
    atomic_text(tmp_path / "uv.lock", "locked")
    initial = dependency_identity(tmp_path)
    atomic_text(tmp_path / ".env", "secret")
    atomic_text(tmp_path / "target/pom.xml", "cache")
    assert dependency_identity(tmp_path) == initial
    atomic_text(tmp_path / "uv.lock", "different")
    assert dependency_identity(tmp_path) != initial


def snapshot_metadata():
    return {
        "image": "registry:6000/rnd-yudao-vben:" + "a" * 16,
        "snapshot": "rnd-yudao-vben-" + "a" * 16,
        "source_hash": "a" * 16,
        "profile": {
            "template": "yudao-vben",
            "database": "postgresql",
            "dependency_identity": "b" * 64,
        },
        "resources": {"cpu": 2, "memory": 10, "disk": 30},
        "wait_for_default": False,
        "image_id": "sha256:" + "c" * 64,
    }


def test_matrix_snapshot_is_independent_of_the_default_python_warmup():
    resources, wait = snapshot_resources(snapshot_metadata())
    assert resources == {"cpu": 2, "memory": 10, "disk": 30}
    assert wait is False


@pytest.mark.parametrize(
    "key,value",
    [
        ("image", "docker.io/remote:latest"),
        ("snapshot", "rnd-python-old"),
        ("source_hash", "unlocked"),
        ("image_id", "latest"),
        ("resources", {"cpu": 999}),
        ("wait_for_default", 0),
    ],
)
def test_matrix_snapshot_cannot_select_cloud_or_unbounded_resources(key, value):
    item = snapshot_metadata()
    item[key] = value
    with pytest.raises(ValueError):
        snapshot_resources(item)


def test_offline_subprocess_policy_preserves_only_explicit_local_cache(monkeypatch):
    monkeypatch.setenv("RND_OFFLINE_TOOLS", "1")
    monkeypatch.setenv("UV_CACHE_DIR", "/local/cache")
    monkeypatch.setenv("API_KEY", "private-model-key")
    monkeypatch.setenv("HTTP_PROXY", "https://not-allowed")
    value = clean_env()
    assert value["UV_OFFLINE"] == "1" and value["COREPACK_ENABLE_NETWORK"] == "0"
    assert value["UV_CACHE_DIR"] == "/local/cache"
    assert "API_KEY" not in value and "HTTP_PROXY" not in value


def test_trusted_harness_contains_only_allowlisted_source():
    with zipfile.ZipFile(io.BytesIO(harness_archive())) as archive:
        names = archive.namelist()
        assert "harness/scripts/daytona_matrix_probe.py" in names
        assert "harness/scripts/native_browser.cjs" in names
        assert all(name.endswith((".py", ".cjs")) for name in names)
        assert not any(
            ".env" in name or "node_modules" in name or "/.git/" in name for name in names
        )


@pytest.mark.parametrize("failure", [None, "exec", "report", "cleanup"])
def test_matrix_always_deletes_its_sandbox_and_never_falls_back(settings, tmp_path, failure):
    product = tmp_path / "product"
    product.mkdir()
    atomic_text(product / "pyproject.toml", "project")
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = True
    settings.daytona_api_key = SecretStr("local-test-token")
    settings.daytona_snapshot = "registered-matrix"
    events = []
    value = report("fastapiadmin")
    value["source_digest"] = digest(manifest(product))
    if failure == "report":
        value["browser"] = False

    class Files:
        def create_folder(self, *args):
            pass

        def upload_file(self, data, path, **kwargs):
            assert b"local-test-token" not in data
            events.append("upload")

        def download_file_stream(self, *args, **kwargs):
            yield json.dumps(value).encode()

    class Process:
        def exec(self, command, **kwargs):
            events.append(command)
            return SimpleNamespace(
                exit_code=1 if failure == "exec" else 0, result="explicit-protocol-fixture"
            )

    class Client:
        def create(self, params, **kwargs):
            assert params.network_block_all and params.snapshot == "registered-matrix"
            events.append("create")
            return SimpleNamespace(id="owned", fs=Files(), process=Process())

        def delete(self, sandbox, **kwargs):
            assert sandbox.id == "owned"
            events.append("delete")
            if failure == "cleanup":
                raise RuntimeError("explicit fixture cleanup failure")

    if failure:
        with pytest.raises(PrerequisiteError):
            verify_in_daytona(product, "fastapiadmin", settings, client=Client())
    else:
        result = verify_in_daytona(product, "fastapiadmin", settings, client=Client())
        assert result["passed"] and result["scope"] == "independent-runtime"
    assert events[-1] == "delete"
    saved = json.loads((tmp_path / "daytona-verification.json").read_text(encoding="utf-8"))
    assert saved["passed"] is (failure is None)


@pytest.mark.parametrize("database", ["sqlite", "postgresql"])
def test_python_runtime_descriptor_does_not_replace_matrix_database_identity(database):
    from scripts.daytona_matrix_probe import basic_runtime_evidence

    raw = {"passed": True, "http": True, "restart": True, "database": "real-isolated-" + database}
    result = basic_runtime_evidence(raw, database)
    assert result["database"] == database
    assert result["runtime_database"] == "real-isolated-" + database
    assert result["fresh_database"] is True
    assert raw["database"] == "real-isolated-" + database
    with pytest.raises(ValueError, match="does not match"):
        basic_runtime_evidence({**raw, "database": "real-isolated-mysql"}, database)


@pytest.mark.parametrize("key", ["passed", "http", "restart"])
@pytest.mark.parametrize("bad", [False, "true", 1, None])
def test_python_runtime_descriptor_normalization_never_hides_failed_checks(key, bad):
    from scripts.daytona_matrix_probe import basic_runtime_evidence

    raw = {
        "passed": True,
        "http": True,
        "restart": True,
        "database": "real-isolated-postgresql",
        key: bad,
    }
    with pytest.raises(ValueError):
        basic_runtime_evidence(raw, "postgresql")
