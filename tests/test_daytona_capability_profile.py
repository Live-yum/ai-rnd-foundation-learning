"""Owned build/inspection contracts, not live isolation or privilege experiments."""

import copy
import difflib
import json
from pathlib import Path

import pytest

from scripts import daytona_capability_profile as profile
from scripts import daytona_local as local
from scripts.daytona_bootstrap import snapshot_resources

RUNNER = "sha256:" + "a" * 64
SNAPSHOT = "sha256:" + "b" * 64
DIGEST = "sha256:" + "c" * 64
OUTER = "d" * 64
SANDBOX = "ea997c7d-cbb9-45eb-8352-3f8bc9e2a512"


def base_config():
    services = {
        name: {
            "image": tag,
            "environment": {"OTEL_ENABLED": "false"},
            "networks": ["daytona-network"],
        }
        for name, tag in local.IMAGES.items()
    }
    services["gateway"] = local.gateway_service()
    services["runner"]["privileged"] = True  # Existing local DinD control plane.
    services["runner"]["environment"]["INTER_SANDBOX_NETWORK_ENABLED"] = "false"
    return {"services": services, "networks": copy.deepcopy(local.NETWORKS)}


def test_profile_transformation_preserves_general_defaults_and_all_other_fields():
    original = base_config()
    untouched = copy.deepcopy(original)
    image = "registry:6000/rnd-python:0123456789abcdef"
    result = profile.render_profile(original, RUNNER, image)
    assert original == untouched
    assert result["name"] == profile.PROJECT
    assert result["services"]["runner"]["image"] == RUNNER
    assert result["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] == "false"
    assert result["services"]["runner"]["privileged"] is True
    assert result["services"]["api"]["environment"]["DEFAULT_SNAPSHOT"] == image
    # The owned app-container patch does not alter DinD or general defaults.
    assert "USE_SNAPSHOT_ENTRYPOINT" not in original["services"]["runner"]["environment"]
    assert local.IMAGES["runner"].startswith("rnd-local/daytona-runner:")
    assert snapshot_resources({"image": image}) == ({"cpu": 1, "memory": 2, "disk": 5}, True)
    with pytest.raises(ValueError, match="own disposable"):
        profile.profile_directory(local.HOME)


def snapshot_inspect():
    identity, _ = profile.recipe_identity()
    return {
        "Id": SNAPSHOT,
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["127.0.0.1:6000/rnd-python@" + DIGEST],
        "Config": {
            "User": "0:0",
            "WorkingDir": profile.CONTROL_WORKDIR,
            "Entrypoint": None,
            "Cmd": None,
            "Labels": {
                "org.opencontainers.image.revision": profile.DAYTONA_SOURCE,
                "rnd.capability.profile": profile.PROFILE,
                "rnd.capability.recipe": identity,
            },
        },
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("User", "daytona"),
        ("User", ""),
        ("WorkingDir", "/home/daytona"),
        ("Entrypoint", ["unapproved"]),
        ("Cmd", ["unapproved"]),
    ],
)
def test_snapshot_requires_declared_control_identity_and_no_inherited_command(field, value):
    image = snapshot_inspect()
    identity, _ = profile.recipe_identity()
    profile.validate_image(image, identity, snapshot=True)
    image["Config"][field] = value
    with pytest.raises(ValueError, match="Snapshot must declare"):
        profile.validate_image(image, identity, snapshot=True)


def test_runner_requires_the_explicit_normal_daemon_entrypoint():
    image = snapshot_inspect()
    identity, _ = profile.recipe_identity()
    for env in ([], ["USE_SNAPSHOT_ENTRYPOINT=true"]):
        image["Config"]["Env"] = env
        with pytest.raises(ValueError, match="normal daemon"):
            profile.validate_image(image, identity, snapshot=False)
    image["Config"]["Env"] = ["USE_SNAPSHOT_ENTRYPOINT=false"]
    profile.validate_image(image, identity, snapshot=False)


def source_fixture(tmp_path, monkeypatch):
    root, context = tmp_path / "recipes", tmp_path / "context"
    context.mkdir()
    source = (
        "// Copyright Daytona; AGPL-3.0\npackage docker\nvar host = container.HostConfig{\n"
        + profile.OLD
        + "}\n"
        + profile.LIMIT_ANCHOR
        + "\n"
    )
    workspace = "go 1.25.5\n\nuse ./apps/runner\n"
    for name in profile.RECIPE_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("recipe fixture\n")
    patch = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            source.replace(profile.OLD, profile.NEW)
            .replace(profile.LIMIT_ANCHOR, profile.LIMIT_INSERT + profile.LIMIT_ANCHOR, 1)
            .splitlines(keepends=True),
            fromfile="a/" + profile.SOURCE_FILE,
            tofile="b/" + profile.SOURCE_FILE,
        )
    )
    (root / "tools/daytona/capability-runner.patch").write_text(patch)

    def export(directory, command, target):
        path = Path(target) / profile.SOURCE_FILE
        path.parent.mkdir(parents=True)
        # These stand in for Git-exported, SHA-bound bytes, not host-native
        # text files. Windows newline conversion must not alter the preimage.
        path.write_bytes(source.encode("utf-8"))
        (Path(target) / "go.work").write_bytes(workspace.encode("utf-8"))
        (Path(target) / "apps/runner/go.mod").write_bytes(b"module fixture\ngo 1.25.5\n")
        (Path(target) / "apps/runner/go.sum").write_bytes(b"fixture v1 h1:fixture\n")

    monkeypatch.setattr(profile, "ROOT", root)
    monkeypatch.setattr(profile, "export_source", export)
    monkeypatch.setattr(profile, "SOURCE_BLOB", profile.blob(source.encode()))
    monkeypatch.setattr(profile, "WORKSPACE_BLOB", profile.blob(workspace.encode()))
    return root, context, source, workspace


def test_source_preimage_and_patch_are_exact_and_module_inputs_are_preserved(tmp_path, monkeypatch):
    _, context, source, workspace = source_fixture(tmp_path, monkeypatch)
    record = profile.source_context(tmp_path, context)
    assert (context / profile.SOURCE_FILE).read_text() == source.replace(
        profile.OLD, profile.NEW
    ).replace(profile.LIMIT_ANCHOR, profile.LIMIT_INSERT + profile.LIMIT_ANCHOR, 1)
    assert (context / "go.work").read_text() == workspace
    assert (context / "apps/runner/go.mod").read_text() == "module fixture\ngo 1.25.5\n"
    assert (context / "go.work.sum").read_text() == "fixture v1 h1:fixture\n"
    assert record["source_sha"] == profile.DAYTONA_SOURCE
    assert (context / "capability-build/NOTICE").is_file()


@pytest.mark.parametrize("changed", ["source", "workspace", "patch"])
def test_source_drift_fails_closed_before_any_build(tmp_path, monkeypatch, changed):
    root, context, _, _ = source_fixture(tmp_path, monkeypatch)
    if changed == "source":
        monkeypatch.setattr(profile, "SOURCE_BLOB", "0" * 40)
    elif changed == "workspace":
        monkeypatch.setattr(profile, "WORKSPACE_BLOB", "0" * 40)
    else:
        with (root / "tools/daytona/capability-runner.patch").open("a") as file:
            file.write("unreviewed change\n")
    with pytest.raises(ValueError, match="does not.*match"):
        profile.source_context(tmp_path, context)


def application_inspect():
    return {
        "Name": "/" + SANDBOX,
        "Image": SNAPSHOT,
        "State": {"Running": True},
        "Config": {
            "User": "0:0",
            "WorkingDir": profile.CONTROL_WORKDIR,
            "Entrypoint": ["/usr/local/bin/daytona"],
            "Cmd": None,
            "Env": ["SECRET=must-not-be-in-receipt"],
        },
        "HostConfig": {"Privileged": False, "NetworkMode": "runner-bridge", "SecurityOpt": None},
        "Mounts": [
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/usr/local/bin/daytona",
                "Source": "/usr/local/bin/.tmp/binaries/daemon-amd64",
            },
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/usr/local/lib/daytona-computer-use",
                "Source": "/usr/local/bin/.tmp/binaries/daytona-computer-use",
            },
        ],
    }


@pytest.fixture
def inspection(tmp_path, monkeypatch):
    record = {
        "profile": profile.PROFILE,
        "runner": {"image_id": RUNNER},
        "snapshot": {"image_id": SNAPSHOT, "digest": "registry:6000/rnd-python@" + DIGEST},
    }
    outer = {
        "Image": RUNNER,
        "State": {"Running": True},
        "Config": {
            "Labels": {
                "com.docker.compose.project": profile.PROJECT,
                "com.docker.compose.service": "runner",
            },
            "Env": ["USE_SNAPSHOT_ENTRYPOINT=false", "TOKEN=must-not-be-in-receipt"],
            "Entrypoint": ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"],
            "Cmd": None,
        },
    }
    inner, calls = application_inspect(), []
    monkeypatch.setattr(profile, "require_profile", lambda _: record)
    monkeypatch.setattr(profile, "compose", lambda *args: OUTER)

    def docker(*args, **kwargs):
        calls.append(args)
        if "info" in args:
            return json.dumps(inner.get("engine_security", ["name=seccomp,profile=builtin"]))
        return json.dumps([outer if args[0] == "container" else inner])

    monkeypatch.setattr(local, "docker", docker)
    return tmp_path, outer, inner, calls


def test_readonly_inspection_is_scoped_to_owned_uuid_and_redacts_everything_else(inspection):
    directory, _, _, calls = inspection
    proof = profile.inspect_created_sandbox(directory, SANDBOX)
    assert proof["privileged"] is False and proof["seccomp"] == "docker-default"
    assert proof["snapshot_image_id"] == SNAPSHOT
    assert calls == [
        ("container", "inspect", OUTER),
        (
            "exec",
            OUTER,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "info",
            "--format",
            "{{json .SecurityOptions}}",
        ),
        (
            "exec",
            OUTER,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "inspect",
            SANDBOX,
        ),
    ]
    assert "SECRET" not in json.dumps(proof) and "TOKEN" not in json.dumps(proof)
    with pytest.raises(ValueError):
        profile.inspect_created_sandbox(directory, "--privileged")
    assert len(calls) == 3


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update(Image="sha256:" + "f" * 64),
        lambda row: row["Config"].update(User="daytona"),
        lambda row: row["Config"].update(Entrypoint=["other"]),
        lambda row: row["Config"].update(Cmd=["other"]),
        lambda row: row["HostConfig"].update(Privileged=True),
        lambda row: row["HostConfig"].update(SecurityOpt=["seccomp=unconfined"]),
        lambda row: row["HostConfig"].update(CapAdd=["SYS_ADMIN"]),
        lambda row: row["HostConfig"].update(NetworkMode="host"),
        lambda row: row["HostConfig"].update(PidMode="host"),
        lambda row: row["Mounts"][0].update(RW=True),
        lambda row: row["Mounts"][0].update(Source="/var/run/docker.sock"),
        lambda row: row["Mounts"].append(
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/docker.sock",
                "Source": "/var/run/docker.sock",
            }
        ),
    ],
)
def test_created_application_rejects_real_inspect_drift(inspection, mutation):
    directory, _, inner, _ = inspection
    mutation(inner)
    with pytest.raises(ValueError, match="container|mounts"):
        profile.inspect_created_sandbox(directory, SANDBOX)


def test_wrong_runner_is_rejected_before_an_inner_exec(inspection):
    directory, outer, _, calls = inspection
    outer["Image"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="Running Runner"):
        profile.inspect_created_sandbox(directory, SANDBOX)
    assert len(calls) == 1


def test_recipe_keeps_real_embeds_glibc_smoke_license_and_locked_go_inputs():
    recipe = (profile.ROOT / "tools/daytona/capability-runner.Dockerfile").read_text()
    for text in (
        "./apps/daemon/cmd/daemon",
        "./libs/computer-use",
        "./apps/runner/cmd/runner",
        "GOTOOLCHAIN=local",
        "GOTELEMETRY=off",
        "-mod=readonly",
        "sha256sum -c",
        "source.tar",
        "COPY LICENSE",
        "API_PORT=invalid",
        "Failed to get config",
        "USE_SNAPSHOT_ENTRYPOINT=false",
        "rnd-runner-entry.sh",
    ):
        assert text in recipe
    assert "go mod edit" not in recipe and "yarn" not in recipe
    snapshot = (profile.ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text()
    assert snapshot.rstrip().endswith("USER 0:0")
    assert "WORKDIR /opt/rnd/control" in snapshot
    assert (
        (profile.ROOT / "tools/daytona/Dockerfile")
        .read_text()
        .rstrip()
        .endswith("WORKDIR /home/daytona")
    )


@pytest.fixture
def locked_profile(tmp_path):
    base = base_config()
    records = {}
    for name, service in base["services"].items():
        tag = service["image"]
        value = RUNNER if name in profile.BUILT else tag.rsplit(":", 1)[0] + "@" + DIGEST
        records[name] = {"tag": tag, "image_id" if name in profile.BUILT else "digest": value}
        service["image"] = value
    profile.write_compose(tmp_path / "compose.lock.yaml", base)
    local.private_json(tmp_path / "images.lock.json", records)
    local.private_json(
        tmp_path / "installation.json",
        {
            "source_sha": profile.DAYTONA_SOURCE,
            "release": "v" + profile.DAYTONA_VERSION,
            "deployment": "local-development-only",
            "cloud_account": False,
        },
    )
    identity, recipes = profile.recipe_identity()
    bases = {
        name: {"tag": tag, "digest": tag.rsplit(":", 1)[0] + "@" + DIGEST, "image_id": SNAPSHOT}
        for name, tag in profile.BASES.items()
    }
    stamp = profile.sha256((identity + json.dumps(bases, sort_keys=True)).encode())[:16]
    image = {
        "source_hash": stamp,
        "image": "registry:6000/rnd-python:" + stamp,
        "snapshot": "rnd-python-" + stamp,
        "local_tag": "127.0.0.1:6000/rnd-python:" + stamp,
        "image_id": SNAPSHOT,
        "digest": "registry:6000/rnd-python@" + DIGEST,
        "user": "0:0",
        "working_dir": profile.CONTROL_WORKDIR,
        "recipe_sha256": recipes["tools/daytona/capability-snapshot.Dockerfile"],
    }
    record = {
        "profile": profile.PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "source": {"source_sha": profile.DAYTONA_SOURCE},
        "bases": bases,
        "base_compose_sha256": profile.sha256((tmp_path / "compose.lock.yaml").read_bytes()),
        "runner": {
            "tag": "rnd-local/daytona-capability-runner:" + stamp,
            "image_id": RUNNER,
            "recipe_sha256": recipes["tools/daytona/capability-runner.Dockerfile"],
        },
        "snapshot": image,
    }
    profile.write_compose(
        tmp_path / profile.COMPOSE, profile.render_profile(base, RUNNER, image["image"])
    )
    local.private_json(tmp_path / profile.LOCK, record)
    local.private_json(tmp_path / "snapshot-image.json", image)
    return tmp_path, record


def test_profile_lock_roundtrip_preserves_ordinary_lock_and_rejects_compose_changes(locked_profile):
    directory, record = locked_profile
    ordinary = (directory / "compose.lock.yaml").read_bytes()
    config, actual = profile.load_profile(directory)
    assert actual == record
    config["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] = "true"
    profile.write_compose(directory / profile.COMPOSE, config)
    with pytest.raises(ValueError, match="exact allowed transformation"):
        profile.load_profile(directory)
    assert (directory / "compose.lock.yaml").read_bytes() == ordinary


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record["bases"]["GO_IMAGE"].update(digest="golang:latest"),
        lambda record: record["snapshot"].update(image="registry:6000/rnd-python:0000000000000000"),
        lambda record: record["snapshot"].update(user="daytona"),
        lambda record: record["snapshot"].update(digest="elsewhere.example/image@" + DIGEST),
        lambda record: record["runner"].update(tag=local.IMAGES["runner"]),
    ],
)
def test_edited_lock_cannot_select_general_or_unpinned_images(locked_profile, mutation):
    directory, record = locked_profile
    mutation(record)
    local.private_json(directory / profile.LOCK, record)
    local.private_json(directory / "snapshot-image.json", record["snapshot"])
    with pytest.raises(ValueError, match="lock|identity"):
        profile.load_profile(directory)


def test_required_profile_verifies_image_id_and_registry_digest(locked_profile, monkeypatch):
    directory, record = locked_profile
    image = snapshot_inspect()
    runner = copy.deepcopy(image)
    runner["Id"] = RUNNER
    runner["Config"]["Env"] = ["USE_SNAPSHOT_ENTRYPOINT=false"]
    monkeypatch.setattr(
        profile, "inspect_image", lambda value: runner if value == RUNNER else image
    )
    assert profile.require_profile(directory, record["snapshot"]["snapshot"]) == record
    with pytest.raises(ValueError, match="explicitly select"):
        profile.require_profile(directory, "ordinary-snapshot")
    image["RepoDigests"] = []
    with pytest.raises(ValueError, match="ID and digest"):
        profile.require_profile(directory)


def test_prepare_never_overwrites_existing_profile_or_credentials(locked_profile, monkeypatch):
    directory, _ = locked_profile
    monkeypatch.setattr(
        local, "docker", lambda *args, **kwargs: pytest.fail("No Docker mutation allowed")
    )
    with pytest.raises(ValueError, match="fresh local state"):
        profile.prepare(directory)


@pytest.mark.parametrize(
    "options", [None, [], ["name=seccomp,profile=unconfined"], ["name=apparmor"]]
)
def test_missing_actual_engine_seccomp_is_not_default_filter_evidence(inspection, options):
    directory, _, inner, calls = inspection
    inner["engine_security"] = options
    with pytest.raises(ValueError, match="built-in seccomp"):
        profile.inspect_created_sandbox(directory, SANDBOX)
    assert len(calls) == 2
