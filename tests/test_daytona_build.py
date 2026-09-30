"""Installation contracts; live service evidence is produced by ci_daytona_local."""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import daytona_build as build
from scripts import daytona_local as local


def test_release_recipe_requires_exact_preimage_and_disables_cloud_builders(tmp_path, monkeypatch):
    dockerfile = tmp_path / "apps/api/Dockerfile"
    dockerfile.parent.mkdir(parents=True)
    content = b"FROM node:24-slim AS daytona\nENV CI=true\nRUN echo build\n"
    dockerfile.write_bytes(content)
    digest = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    monkeypatch.setitem(build.SOURCE_RECIPES, "api", ("daytona", digest))
    target, result = build.recipe("api", tmp_path)
    assert target == "daytona" and "RUN echo build" in result
    for setting in ("NX_NO_CLOUD=true", "NX_SKIP_REMOTE_CACHE=true", "DO_NOT_TRACK=1"):
        assert setting in result
    dockerfile.write_bytes(content + b"RUN echo unexpected\n")
    with pytest.raises(ValueError, match="不匹配"):
        build.recipe("api", tmp_path)


def test_runner_corruption_is_rejected_without_network_or_execution(tmp_path, monkeypatch):
    destination = tmp_path / "runner-amd64"
    destination.write_bytes(b"corrupt")
    monkeypatch.setattr(
        build.urllib.request, "build_opener", lambda *args: pytest.fail("unexpected network")
    )
    with pytest.raises(ValueError, match="校验失败"):
        build.download_runner(destination)
    assert destination.read_bytes() == b"corrupt"


def test_existing_verified_runner_does_not_download_again(tmp_path, monkeypatch):
    destination = tmp_path / "runner-amd64"
    content = b"explicit local fixture; not executable"
    destination.write_bytes(content)
    monkeypatch.setattr(build, "RUNNER_BYTES", len(content))
    monkeypatch.setattr(build, "RUNNER_SHA256", hashlib.sha256(content).hexdigest())
    monkeypatch.setattr(
        build.urllib.request, "build_opener", lambda *args: pytest.fail("unexpected network")
    )
    build.download_runner(destination)


def test_git_export_ignores_worktree_changes_and_untracked_credentials(tmp_path, monkeypatch):
    source = tmp_path / "upstream"
    source.mkdir()

    def command(argv, *, cwd):
        return subprocess.check_output(argv, cwd=cwd, text=True).strip()

    command(["git", "init", "--template=", "."], cwd=source)
    command(["git", "config", "user.email", "test@example.invalid"], cwd=source)
    command(["git", "config", "user.name", "Explicit test"], cwd=source)
    (source / "code.txt").write_text("committed\n")
    command(["git", "add", "code.txt"], cwd=source)
    command(["git", "commit", "-m", "fixture"], cwd=source)
    revision = command(["git", "rev-parse", "HEAD"], cwd=source)
    monkeypatch.setattr(build, "DAYTONA_SOURCE", revision)
    (source / "code.txt").write_text("modified worktree\n")
    (source / ".env").write_text("API_KEY=must-not-enter-build\n")
    context = tmp_path / "context"
    context.mkdir()
    build.export_source(tmp_path, command, context)
    assert (context / "code.txt").read_text() == "committed\n"
    assert not (context / ".env").exists() and not (context / ".git").exists()
    assert not (tmp_path / "build-source.tar").exists()


def test_images_build_locally_and_lock_service_ids(tmp_path, monkeypatch):
    services = {
        name: {"image": tag, "environment": {"OTEL_ENABLED": "false"}}
        for name, tag in local.IMAGES.items()
    }
    config = {
        "services": services,
        "networks": {"daytona-network": {"driver": "bridge", "internal": True}},
    }
    (tmp_path / "compose.yaml").write_text(yaml.safe_dump(config))
    calls = []

    def docker(*args, **kwargs):
        calls.append(args)
        if args[:2] == ("image", "inspect"):
            prefix = args[2].rsplit(":", 1)[0]
            return json.dumps([{"RepoDigests": [prefix + "@sha256:" + "b" * 64]}])
        return ""

    monkeypatch.setattr(local, "docker", docker)
    built = {
        name: {"tag": build.local_tag(name), "image_id": "sha256:" + "a" * 64}
        for name in build.BUILT
    }
    monkeypatch.setattr(local, "build_images", lambda *args: built.copy())
    local.images(tmp_path)
    assert all(not args[1].startswith("rnd-local/") for args in calls if args[0] == "pull")
    locked = yaml.safe_load((tmp_path / "compose.lock.yaml").read_text())
    assert locked["services"]["api"]["image"] == "sha256:" + "a" * 64
    local.compose(tmp_path, "ps")
    locked["services"]["api"]["image"] = "sha256:" + "c" * 64
    (tmp_path / "compose.lock.yaml").write_text(yaml.safe_dump(locked))
    with pytest.raises(ValueError, match="不一致"):
        local.compose(tmp_path, "ps")


def test_nonlocal_registry_and_runtime_egress_are_rejected(tmp_path):
    config = {
        "services": {
            name: {"image": tag, "environment": {"OTEL_ENABLED": "false"}}
            for name, tag in local.IMAGES.items()
        },
        "networks": {"daytona-network": {"internal": True}},
    }
    local.assert_local_compose(config)
    config["services"]["db"]["image"] = "unapproved.example/postgres@sha256:" + "d" * 64
    with pytest.raises(ValueError, match="镜像未固定"):
        local.assert_local_compose(config)
    config["services"]["db"]["image"] = local.IMAGES["db"]
    config["networks"]["daytona-network"]["internal"] = False
    with pytest.raises(ValueError, match="出口"):
        local.assert_local_compose(config)


def test_snapshot_identity_covers_all_dependency_inputs():
    assert len(local.snapshot_stamp()) == 16
    recipe = (Path(local.ROOT) / "tools/daytona/runner.Dockerfile").read_text()
    assert "28.5.2-dind-alpine3.22" in recipe
    assert "latest" not in recipe and "runner-amd64" in recipe


def test_installation_repositories_and_non_runner_privileges_are_explicit():
    assert local.IMAGES["minio"] == "quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z"
    assert all(not name.endswith(":latest") for name in local.IMAGES.values())


def test_snapshot_registration_uses_a_bounded_child_without_key_arguments(tmp_path, monkeypatch):
    from scripts import daytona_bootstrap as bootstrap
    from workbench.tools import ToolFailure

    seen = []

    def run(argv, cwd, **kwargs):
        seen.append((argv, cwd, kwargs))
        return {"log": ""}

    monkeypatch.setattr(bootstrap, "run_command", run)
    bootstrap.snapshot(tmp_path)
    argv, cwd, options = seen[0]
    assert argv[3] == "snapshot-worker" and argv[-1] == str(tmp_path.resolve())
    assert cwd == local.ROOT and options["timeout"] == 720
    assert not any("key" in value.lower() for value in argv)

    def failed(*args, **kwargs):
        raise ToolFailure("explicit timeout fixture")

    monkeypatch.setattr(bootstrap, "run_command", failed)
    with pytest.raises(ToolFailure, match="timeout"):
        bootstrap.snapshot(tmp_path)
