"""Native preparation contracts use explicit fakes, never live Docker/runtime proof."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import daytona_native_capability_profile as native
from workbench.filesystem import atomic_text

RUNNER = "sha256:" + "a" * 64
BASE_IMAGE = "sha256:" + "b" * 64
IMAGE = "sha256:" + "c" * 64
DIGEST = "sha256:" + "d" * 64
KEY = "existing-local-account-fixture"


@pytest.fixture
def product(tmp_path):
    root = tmp_path / "product"
    atomic_text(root / "deployment/manifest.json", json.dumps({"template": "fastapiadmin"}))
    for folder in ("backend", "deployment"):
        atomic_text(
            root / folder / "pyproject.toml",
            '[project]\nname = "fixture"\nversion = "1"\n',
        )
        atomic_text(
            root / folder / "uv.lock",
            'version = 1\nregistry = "https://pypi.tuna.tsinghua.edu.cn/simple"\n',
        )
    atomic_text(
        root / "frontend/web/package.json",
        '{"name":"fixture","scripts":{"prepare":"DO_NOT_RUN"}}',
    )
    atomic_text(root / "frontend/web/pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
    atomic_text(
        root / "backend/main.py",
        "raise RuntimeError('never execute candidate source')\n",
    )
    atomic_text(
        root / "deployment/workbench/native_environment.py",
        "raise RuntimeError('untrusted control')\n",
    )
    atomic_text(root / "frontend/web/.pnpmfile.cjs", "throw Error('untrusted package hook')")
    atomic_text(root / ".env", "API_KEY=must-not-be-copied\n")
    return root


@pytest.fixture
def foundation():
    return {
        "profile": native.base.PROFILE,
        "recipe_identity": "e" * 64,
        "runner": {
            "image_id": RUNNER,
            "tag": "fixed-base-runner",
            "recipe_sha256": "f" * 64,
        },
        "snapshot": {
            "image_id": BASE_IMAGE,
            "digest": "registry:6000/rnd-python@" + DIGEST,
        },
        "bases": {
            "RUST_IMAGE": {
                "tag": "rust:1.85.1-bookworm",
                "digest": "rust@" + DIGEST,
                "image_id": BASE_IMAGE,
            }
        },
    }


def image_for(record):
    return {
        "Id": IMAGE,
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["127.0.0.1:6000/" + native.FAMILY + "@" + DIGEST],
        "Config": {
            "User": "0:0",
            "WorkingDir": native.base.CONTROL_WORKDIR,
            "Entrypoint": [],
            "Cmd": [],
            "Labels": {
                "org.opencontainers.image.revision": native.base.DAYTONA_SOURCE,
                "rnd.capability.profile": native.PROFILE,
                "rnd.capability.recipe": record["recipe_identity"],
                "rnd.capability.base-recipe": record["base"]["recipe_identity"],
                "rnd.capability.base-image": record["base"]["snapshot_image_id"],
                "rnd.capability.base-digest": record["base"]["snapshot_digest"],
                "rnd.capability.dependencies": record["dependency_identity"],
                "rnd.capability.input": record["inputs"]["source_identity"],
            },
        },
    }


@pytest.fixture
def prepared(tmp_path, product, foundation, monkeypatch):
    directory = tmp_path / "profile"
    directory.mkdir()
    inputs = native.product_inputs(product)
    identity, recipes = native.recipe_identity()
    base = native.base_identity(foundation)
    stamp = native.native_stamp(identity, base, inputs)
    record = {
        "profile": native.PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "selection": native.selection(),
        "base": base,
        "runner": copy.deepcopy(foundation["runner"]),
        "inputs": inputs,
        "dependency_identity": inputs["dependency_identity"],
        "resources": dict(native.RESOURCES),
        "snapshot": {
            "image": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "digest": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "image_id": IMAGE,
            "local_tag": "127.0.0.1:6000/" + native.FAMILY + ":" + stamp,
            "source_hash": stamp,
            "snapshot": native.FAMILY + "-" + stamp,
            "user": "0:0",
            "working_dir": native.base.CONTROL_WORKDIR,
            "recipe_sha256": recipes[native.DOCKERFILE],
        },
    }
    dependency_record = {
        "schema": 1,
        "profile": "fastapiadmin",
        "image_id": IMAGE,
        "manifest_sha256": "1" * 64,
        "installed_tree_sha256": "2" * 64,
        "original_descriptors": inputs["descriptors"],
    }
    record["snapshot"]["dependency_manifest"] = dependency_record
    monkeypatch.setattr(
        native.base,
        "inspect_dependency_manifest",
        lambda *args: copy.deepcopy(dependency_record),
    )
    image = image_for(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    monkeypatch.setattr(native.base, "require_profile", lambda path: copy.deepcopy(foundation))
    monkeypatch.setattr(native.base, "inspect_image", lambda reference: copy.deepcopy(image))
    return directory, record, image


def test_filtered_dependency_context_never_copies_product_code_secrets_or_hooks(product, tmp_path):
    expected = native.product_inputs(product)
    context = tmp_path / "context"
    context.mkdir()
    native.prepare_context(product, context, expected)
    paths = {path.relative_to(context).as_posix() for path in context.rglob("*") if path.is_file()}
    assert paths == {"product/" + name for name in native.DESCRIPTORS} | {
        "Dockerfile",
        "harness/pyproject.toml",
        "harness/uv.lock",
        "dependency-image.py",
        "dependency-build.py",
        "dependency-build.lock.json",
        "dependency-inputs.json",
    }
    assert "https://pypi.org/simple" in (context / "product/backend/uv.lock").read_text()
    assert "tuna.tsinghua" in (product / "backend/uv.lock").read_text()
    assert native.product_inputs(product) == expected
    assert not any(
        "must-not-be-copied" in path.read_text() for path in context.rglob("*") if path.is_file()
    )


@pytest.mark.parametrize(
    "value",
    [
        "_authToken=secret",
        "registry=https://person:secret@registry.npmjs.org/",
        "password=${TOKEN}",
    ],
)
def test_registry_credentials_are_rejected_before_build(product, value):
    atomic_text(product / "frontend/web/.npmrc", value)
    with pytest.raises(ValueError, match="configuration|URLs"):
        native.product_inputs(product)


def test_secret_files_are_filtered_but_dependency_and_source_drift_are_distinct(
    product,
):
    original = native.product_inputs(product)
    atomic_text(product / ".env", "CHANGED_PRIVATE_SECRET=ignored\n")
    assert native.product_inputs(product) == original
    atomic_text(product / "backend/main.py", "changed source\n")
    changed = native.product_inputs(product)
    assert changed["dependency_identity"] == original["dependency_identity"]
    assert changed["source_identity"] != original["source_identity"]
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    assert native.product_inputs(product)["dependency_identity"] != original["dependency_identity"]


@pytest.mark.parametrize(
    "metadata",
    [
        {"template": "python-basic"},
        {"template": "fastapiadmin", "database": "sqlite"},
        {"template": "fastapiadmin", "selection": {"template": "python-basic"}},
    ],
)
def test_only_exact_native_manifest_selection_is_supported(product, metadata):
    atomic_text(product / "deployment/manifest.json", json.dumps(metadata))
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_missing_locks_and_symlinks_are_rejected(product, tmp_path):
    (product / "backend/uv.lock").unlink()
    with pytest.raises(ValueError, match="missing a dependency descriptor"):
        native.product_inputs(product)
    (product / "backend/uv.lock").symlink_to(tmp_path / "not-a-lock")
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_context_rejects_source_drift(product, tmp_path):
    expected = native.product_inputs(product)
    atomic_text(product / "backend/main.py", "changed")
    with pytest.raises(ValueError, match="input changed"):
        native.prepare_context(product, tmp_path / "context", expected)


def test_readonly_check_revalidates_base_snapshot_and_normalizes_native_record(
    prepared, monkeypatch, foundation
):
    directory, record, _ = prepared
    checked = []
    monkeypatch.setattr(
        native.base, "require_profile", lambda path: checked.append(path) or foundation
    )
    assert native.require_native_profile(directory, record["snapshot"]["snapshot"]) == record
    assert checked == [directory]
    assert record["runner"] == foundation["runner"]
    assert record["selection"]["database"] == "postgresql"
    assert record["resources"] == {"cpu": 2, "memory": 6, "disk": 30}
    with pytest.raises(ValueError, match="derived identity"):
        native.require_native_profile(directory, "wrong-snapshot")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(profile="arbitrary-profile"),
        lambda record: record.update(recipe_identity="0" * 64),
        lambda record: record.update(resources={"cpu": 99, "memory": 6, "disk": 30}),
        lambda record: record["runner"].update(image_id="sha256:" + "0" * 64),
        lambda record: record["base"].update(recipe_identity="0" * 64),
        lambda record: record.update(dependency_identity="0" * 64),
        lambda record: record["snapshot"].update(user="daytona"),
        lambda record: record["snapshot"].update(working_dir="/tmp"),
        lambda record: record["snapshot"].update(local_tag="remote:latest"),
        lambda record: record["snapshot"].update(image_id="mutable"),
        lambda record: record["snapshot"].update(image="remote:latest"),
        lambda record: record["snapshot"].update(source_hash="0" * 16),
    ],
)
def test_native_record_tampering_fails_closed(prepared, mutation):
    directory, record, _ = prepared
    mutation(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda image: image.update(Id="sha256:" + "0" * 64),
        lambda image: image.update(RepoDigests=[]),
        lambda image: image.update(Architecture="arm64"),
        lambda image: image["Config"].update(User="daytona"),
        lambda image: image["Config"].update(WorkingDir="/tmp"),
        lambda image: image["Config"].update(Entrypoint=["untrusted"]),
        lambda image: image["Config"].update(Cmd=["untrusted"]),
        lambda image: image["Config"]["Labels"].update({"rnd.capability.input": "0" * 64}),
    ],
)
def test_live_image_drift_is_rejected(prepared, mutation):
    directory, _, image = prepared
    mutation(image)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


def test_product_lock_drift_prevents_reusing_native_profile(prepared, product):
    directory, _, _ = prepared
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    with pytest.raises(ValueError, match="input or base identity changed"):
        native.require_native_profile(directory)


@pytest.mark.parametrize("diagnostics", [False, True])
@pytest.mark.parametrize("failure", [None, "push", "image", "input"])
def test_prepare_uses_only_owned_base_and_separate_ready_record(
    prepared, product, monkeypatch, failure, diagnostics
):
    directory, expected, image = prepared
    (directory / native.LOCK).unlink()
    protected = (
        "snapshot-image.json",
        "workbench.env",
        "api-key.json",
        native.base.LOCK,
        native.base.COMPOSE,
    )
    for name in protected:
        atomic_text(directory / name, "base-must-stay-unchanged")
    calls = []

    def docker(*args, **kwargs):
        calls.append((args, kwargs))
        if args[0] == "build":
            context = Path(args[-1])
            assert not (context / "product/.env").exists()
            assert not (context / "product/backend/main.py").exists()
            assert "BASE_IMAGE=127.0.0.1:6000/rnd-python@" + DIGEST in args
            assert "--pull=false" in args
            if failure == "input":
                atomic_text(product / "backend/main.py", "changed during build")
        if args[0] == "push":
            if failure == "push":
                raise RuntimeError("explicit publication failure")
            if failure == "image":
                image["Id"] = "sha256:" + "0" * 64
        return ""

    monkeypatch.setattr(native.local, "docker", docker)
    monkeypatch.setattr(
        native.base, "compose", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    monkeypatch.setattr(native.local, "wait_for_registry", lambda: None)
    report = directory / "diagnostic.json"
    options = {"diagnostics": report} if diagnostics else {}
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.prepare(product, directory, **options)
        assert not (directory / native.LOCK).exists()
        if diagnostics:
            value = json.loads(report.read_text())
            assert (
                value["stage"]
                == {
                    "push": "prepare-image-push",
                    "image": "prepare-published-image-validation",
                    "input": "prepare-final-identity-validation",
                }[failure]
            )
            assert value["passed"] is False and value["affects_acceptance"] is False
    else:
        result = native.prepare(product, directory, **options)
        assert result == expected
        assert native.require_native_profile(directory) == result
        assert not (directory / native.ENVIRONMENT).exists()
        if os.name != "nt":
            assert (directory / native.LOCK).stat().st_mode & 0o777 == 0o600
        assert not report.exists()
    if not diagnostics:
        assert not report.exists()
    assert all((directory / name).read_text() == "base-must-stay-unchanged" for name in protected)
    assert any(args[0] == "build" for args, _ in calls)


def test_prepare_refuses_overwrite_before_docker(prepared, product, monkeypatch):
    directory, _, _ = prepared
    monkeypatch.setattr(
        native.local,
        "docker",
        lambda *args, **kwargs: pytest.fail("Docker must not run"),
    )
    with pytest.raises(ValueError, match="refuses to overwrite"):
        native.prepare(product, directory)


@pytest.mark.parametrize("diagnostics", [False, True])
@pytest.mark.parametrize("failure", [None, "source", "state", "resources", "close"])
def test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base(
    prepared, monkeypatch, failure, diagnostics
):
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    atomic_text(directory / "workbench.env", "base-environment-unchanged")
    calls = []
    snapshot = record["snapshot"]
    existing = SimpleNamespace(
        name=snapshot["snapshot"],
        image_name=snapshot["digest"],
        state="active",
        cpu=2,
        mem=6,
        disk=30,
        entrypoint=[],
    )
    if failure == "source":
        existing.image_name = "mutable:tag"
    if failure == "state":
        existing.state = "failed"
    if failure == "resources":
        existing.mem = 12

    class Snapshots:
        def create(self, params, **kwargs):
            calls.append("create")
            assert params.image == snapshot["digest"]
            assert {
                name: getattr(params.resources, name) for name in native.RESOURCES
            } == native.RESOURCES
            assert params.region_id == "local" and kwargs["timeout"] == 600
            return existing

    client = SimpleNamespace(snapshot=Snapshots())

    def factory(settings):
        assert settings.daytona_api_key.get_secret_value() == KEY
        assert settings.daytona_api_url == "http://127.0.0.1:3000/api"
        assert settings.daytona_target == "local"
        return client

    def close(value):
        assert value is client
        calls.append("close")
        if failure == "close":
            raise RuntimeError("explicit close failure")

    monkeypatch.setattr(native, "install_loopback_guard", lambda: calls.append("guard"))
    monkeypatch.setattr(native, "client_for", factory)
    monkeypatch.setattr(native, "close_client", close)
    monkeypatch.setattr(native, "snapshot_named", lambda service, name: None)
    report = directory / "diagnostic.json"
    options = {"diagnostics": report} if diagnostics else {}
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.register_worker(directory, **options)
        assert not (directory / native.ENVIRONMENT).exists()
        if diagnostics:
            value = json.loads(report.read_text())
            assert value["stage"] == (
                "register-worker-client-close"
                if failure == "close"
                else "register-worker-snapshot-validation"
            )
            assert KEY not in report.read_text()
    else:
        native.register_worker(directory, **options)
        content = (directory / native.ENVIRONMENT).read_text()
        assert KEY in content and "fastapiadmin/postgresql" in content
        assert "CAPABILITY_EXECUTION_ENABLED" not in content
        assert "local" in content
        monkeypatch.setattr(native, "snapshot_named", lambda service, name: existing)
        native.register_worker(directory, **options)
        assert calls.count("create") == 1
        if os.name != "nt":
            assert (directory / native.ENVIRONMENT).stat().st_mode & 0o777 == 0o600
        assert not report.exists()
    if not diagnostics:
        assert not report.exists()
    assert calls[-1] == "close"
    assert (directory / "workbench.env").read_text() == "base-environment-unchanged"
    assert json.loads((directory / "api-key.json").read_text()) == {"value": KEY}


def test_registration_has_bounded_subprocess_and_no_key_in_argv(prepared, monkeypatch):
    directory, _, _ = prepared
    calls = []
    monkeypatch.setattr(native, "run_command", lambda *args, **kwargs: calls.append((args, kwargs)))
    native.register(directory)
    args, kwargs = calls[0]
    assert args[0][1:4] == [
        "-m",
        "scripts.daytona_native_capability_profile",
        "register-worker",
    ]
    assert kwargs["timeout"] == 720
    assert KEY not in repr(calls)


def test_registration_does_not_overwrite_other_native_credentials(prepared, monkeypatch):
    directory, _, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    native.write_private_new(directory / native.ENVIRONMENT, "different credentials")
    monkeypatch.setattr(
        native, "client_for", lambda settings: pytest.fail("No SDK request allowed")
    )
    with pytest.raises(ValueError, match="refusing overwrite"):
        native.register_worker(directory)


def test_native_recipe_keeps_control_identity_pinned_tools_and_no_product_execution():
    recipe = (native.ROOT / native.DOCKERFILE).read_text()
    for text in (
        "ARG BASE_IMAGE",
        "FROM ${BASE_IMAGE}",
        "libseccomp2 procps",
        "postgresql-17",
        "redis-server",
        "pnpm@9.15.3",
        "dependency-build.py install",
        "RUN --network=none",
        "USER daytona",
        "--package-import-method=copy",
        "--ignore-scripts",
        "--frozen-lockfile",
        "--store-dir /opt/rnd/pnpm-store",
        "node_modules/vue/package.json",
        "UV_OFFLINE=1",
        "WORKDIR /opt/rnd/control",
        "ENTRYPOINT []",
        "CMD []",
    ):
        assert text in recipe
    assert recipe.rstrip().endswith("USER 0:0")
    assert "warm.py" not in recipe and "vite build" not in recipe
    assert "CAPABILITY_EXECUTION_ENABLED" not in recipe


@pytest.mark.parametrize(
    "key",
    ["key\nREMOTE=x", "key;touch-payload", "key$(payload)", "key'quoted", "", None],
)
def test_existing_key_cannot_inject_environment_or_shell_syntax(key):
    with pytest.raises(ValueError, match="safely written"):
        native.environment_text(key, "rnd-native-fastapiadmin-" + "a" * 16)


def test_existing_native_environment_must_remain_private(prepared):
    if os.name == "nt":
        pytest.skip("POSIX file-mode contract")
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    path = directory / native.ENVIRONMENT
    atomic_text(path, native.environment_text(KEY, record["snapshot"]["snapshot"]))
    path.chmod(0o644)
    with pytest.raises(ValueError, match="private permissions"):
        native.register_worker(directory)


def test_native_metadata_cannot_be_adopted_through_a_symlink(prepared, tmp_path):
    directory, record, _ = prepared
    outside = tmp_path / "other-record.json"
    atomic_text(outside, json.dumps(record))
    (directory / native.LOCK).unlink()
    (directory / native.LOCK).symlink_to(outside)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


@pytest.mark.parametrize("form", ["header", "footer", "process", "continued-process"])
@pytest.mark.parametrize("run", [row[1] for row in native.REVIEWED_RUNS])
def test_build_diagnostics_match_only_complete_reviewed_run_commands(form, run):
    (stage, command), _ = next(
        (key, value) for key, value in native.reviewed_run_commands().items() if value == run
    )
    if form == "header":
        log = f"#19 [{stage} 7/16] RUN {command}\n#19 ERROR: private failure"
    elif form == "footer":
        log = f" > [{stage} 7/16] RUN {command}:\nprivate failure"
    else:
        if form == "continued-process":
            command = command.replace(" && ", " \\\n    && ")
        process = json.dumps("/bin/sh -c " + command)
        log = (
            f"ERROR: failed to solve: process {process} did not complete successfully: exit code: 1"
        )
    facts = native.build_failure_facts(log)
    assert (facts["stage"], facts["run"]) == (stage, run)
    assert "private" not in json.dumps(facts)
    assert command not in json.dumps(facts)


@pytest.mark.parametrize(
    "signature,category",
    [
        ("Permission denied (os error 13) at cache", "cache-permission-denied"),
        ("error: unexpected argument\nUsage: uv pip sync", "uv-cli-rejected"),
        ("Failed to build a private source", "source-build-failed"),
        ("error: could not compile a private crate", "compiler-failed"),
        ("failed to get private as a dependency of package private", "rust-dependency-failed"),
        ("configured Python interpreter version is newer than PyO3", "python-version-unsupported"),
        ("no matching package named private found in offline mode", "offline-dependency-missing"),
        ("private wheel hash mismatch", "dependency-hash-mismatch"),
        ("failed to download https://private.invalid", "registry-fetch-failed"),
        ("ERR_PNPM_OUTDATED_LOCKFILE private contents", "node-install-failed"),
        ("Dependency symlink escapes the complete image graph", "image-seal-rejected"),
    ],
)
def test_build_diagnostics_emit_only_fixed_known_error_categories(signature, category):
    (stage, command), _ = next(
        (key, value)
        for key, value in native.reviewed_run_commands().items()
        if value == "build-native-sources"
    )
    log = f"#12 [{stage} 6/16] RUN {command}\n#12 ERROR: {signature}"
    value = native.build_failure_facts(log)
    assert category in value["categories"]
    assert signature not in json.dumps(value)
    assert "private" not in json.dumps(value)


def test_build_diagnostics_do_not_adopt_unreviewed_commands_or_ambient_text():
    command = next(iter(native.reviewed_run_commands()))[1] + " && echo private-secret"
    for log in (
        f"#12 [native-system 1/2] RUN {command}\n#12 ERROR: private-secret",
        f"ERROR: process {json.dumps('/bin/sh -c ' + command)} did not complete successfully: exit code: 1",
        "private-package private-path https://private.invalid API_KEY=private-secret\n",
    ):
        assert native.build_failure_facts(log) == {
            "stage": "unknown",
            "run": "unknown",
            "categories": ["unknown"],
        }


@pytest.mark.parametrize("mutation", ["same-count-edit", "reordered", "missing", "oversized"])
def test_diagnostic_run_mapping_requires_exact_reviewed_recipe(tmp_path, monkeypatch, mutation):
    recipe = (native.ROOT / native.DOCKERFILE).read_text()
    commands = list(native.reviewed_run_commands())
    if mutation == "same-count-edit":
        recipe = recipe.replace("libseccomp2 procps", "libseccomp2 unreviewed", 1)
    elif mutation == "reordered":
        first = recipe.index("RUN ")
        second = recipe.index("\nRUN ", first) + 1
        end = recipe.index("\nENV ", second)
        recipe = recipe[:first] + recipe[second:end] + "\n" + recipe[first:second] + recipe[end:]
    elif mutation == "oversized":
        recipe += "#" * (native.DIAGNOSTIC_SCAN_BYTES + 1)
    if mutation != "missing":
        (tmp_path / "Dockerfile").write_text(recipe)
    monkeypatch.setattr(native, "ROOT", tmp_path)
    monkeypatch.setattr(native, "DOCKERFILE", "Dockerfile")
    assert native.reviewed_run_commands() == {}
    stage, command = commands[0]
    result = native.build_failure_facts(f"#1 [{stage} 1/2] RUN {command}\n#1 ERROR: failure")
    assert result == {"stage": "unknown", "run": "unknown", "categories": ["unknown"]}


@pytest.mark.parametrize("code", [-9, 1, True, 1.5, 2**40, "private-secret"])
def test_failure_diagnostics_are_bounded_and_never_serialize_hostile_payloads(code):
    secret = 'private-secret\n"token":"value"\r\x00https://person:password@private.invalid?key=x'
    error = subprocess.CalledProcessError(
        code, [secret], output=(secret + "界") * 20000, stderr=(secret + "\ud800") * 20000
    )
    report = native.failure_diagnostic(
        {"action": "prepare", "stage": "prepare-docker-build"}, error
    )
    encoded = json.dumps(report).encode()
    assert len(encoded) <= native.DIAGNOSTIC_REPORT_BYTES
    assert report["build"]["scanned_bytes"] <= native.DIAGNOSTIC_SCAN_BYTES
    assert report["build"]["truncated"] is True
    assert report["error"]["returncode"] == (
        code if type(code) is int and abs(code) < 2**31 else None
    )
    assert report["error"]["timed_out"] is False
    for fragment in ("private-secret", "password", "private.invalid", "token", "界"):
        assert fragment.encode() not in encoded
    assert (
        native.failure_diagnostic({"action": secret, "stage": secret}, RuntimeError(secret))[
            "stage"
        ]
        == "unknown"
    )


def test_prepare_build_failure_preserves_failure_and_never_writes_readiness(
    prepared, product, monkeypatch
):
    directory, _, _ = prepared
    (directory / native.LOCK).unlink()
    report = directory / "diagnostic.json"
    error = subprocess.CalledProcessError(23, ["private command"], stderr=b"Permission denied")

    def fail(*args, **kwargs):
        assert args[0] == "build" and kwargs == {"timeout": 3600}
        raise error

    monkeypatch.setattr(native.local, "docker", fail)
    with pytest.raises(subprocess.CalledProcessError) as caught:
        native.prepare(product, directory, diagnostics=report)
    assert caught.value is error
    value = json.loads(report.read_text())
    assert value["stage"] == "prepare-docker-build"
    assert value["error"]["returncode"] == 23
    assert not (directory / native.LOCK).exists()
    assert not (directory / native.ENVIRONMENT).exists()
    assert not list(directory.glob("native-capability-build-*"))
    if os.name != "nt":
        assert report.stat().st_mode & 0o777 == 0o600


def test_stale_ready_profile_and_existing_report_cannot_be_overwritten(
    prepared, product, monkeypatch
):
    directory, _, _ = prepared
    before = (directory / native.LOCK).read_bytes()
    monkeypatch.setattr(native.local, "docker", lambda *a, **k: pytest.fail("No build permitted"))
    with pytest.raises(ValueError, match="refuses to overwrite"):
        native.prepare(product, directory, diagnostics=directory / native.LOCK)
    assert (directory / native.LOCK).read_bytes() == before


def test_register_parent_preserves_exact_worker_report_and_failure(prepared, monkeypatch):
    directory, _, _ = prepared
    report = directory / "diagnostic.json"
    error = native.ToolFailure("private parent log")
    error.log = "token=private-child-secret"
    error.returncode = 1
    expected = {}

    def worker(command, cwd, **kwargs):
        assert command[-2:] == ["--diagnostics", str(report.absolute())]
        assert kwargs["timeout"] == 720
        with pytest.raises(subprocess.TimeoutExpired):
            with native.diagnostic_scope(report, "register-worker") as progress:
                progress["stage"] = "register-worker-snapshot-create"
                raise subprocess.TimeoutExpired(
                    "private SDK request", 600, output=b"private-secret"
                )
        expected.update(json.loads(report.read_text()))
        raise error

    monkeypatch.setattr(native, "run_command", worker)
    with pytest.raises(native.ToolFailure) as caught:
        native.register(directory, diagnostics=report)
    assert caught.value is error
    assert json.loads(report.read_text()) == expected
    assert expected["stage"] == "register-worker-snapshot-create"
    assert expected["error"]["timed_out"] is True
    assert "private" not in report.read_text()
    assert not (directory / native.ENVIRONMENT).exists()


@pytest.mark.parametrize("action", ["prepare", "register", "register-worker"])
@pytest.mark.parametrize("diagnostics", [False, True])
def test_native_cli_remains_compatible_and_success_does_not_emit_diagnostics(
    tmp_path, monkeypatch, capsys, action, diagnostics
):
    calls = []
    report = tmp_path / "diagnostic.json"
    command = ["native-profile", action, "--directory", str(tmp_path)]
    if action == "prepare":
        command += ["--product", str(tmp_path / "product")]
    if diagnostics:
        command += ["--diagnostics", str(report)]
    monkeypatch.setattr(sys, "argv", command)
    monkeypatch.setattr(native, action.replace("-", "_"), lambda *a, **k: calls.append((a, k)))
    native.main()
    assert calls[0][1] == ({"diagnostics": report} if diagnostics else {})
    assert not report.exists()
    assert capsys.readouterr().out == (
        "Native snapshot identity step completed; runtime/isolation acceptance is still required.\n"
    )


def test_native_workflow_collects_separate_bounded_prepare_and_register_diagnostics():
    import yaml

    workflow = yaml.safe_load(
        (native.ROOT / ".github/workflows/native-capability-profile.yml").read_text()
    )
    steps = workflow["jobs"]["local-service"]["steps"]
    build = next(
        step
        for step in steps
        if step.get("name") == "Build and register exact native offline dependency profile"
    )
    upload = next(
        step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    assert "--diagnostics reports/native-profile-prepare-diagnostic.json" in build["run"]
    assert "--diagnostics reports/native-profile-register-diagnostic.json" in build["run"]
    assert upload["if"] == "always()"
    assert "reports/native-profile-*-diagnostic.json" in upload["with"]["path"]
