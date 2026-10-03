# tests/test_daytona_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_bootstrap`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `base_config`（L21–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`local.IMAGES.items`、`local.gateway_service`、`copy.deepcopy`。 返回路径：L33的`{"services": services, "networks": copy.deepcopy(local.NETWORKS)}`。
- `test_profile_transformation_preserves_general_defaults_and_all_other_fields`（L36–L52）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L41断言`original == untouched`；L42断言`result["name"] == profile.PROJECT`；L43断言`result["services"]["runner"]["image"] == RUNNER`；L44断言`result["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] == "false"`；L45断言`result["services"]["runner"]["privileged"] is True`；L46断言`result["services"]["api"]["environment"]["DEFAULT_SNAPSHOT"] == image`；L48断言`"USE_SNAPSHOT_ENTRYPOINT" not in original["services"]["runner"]["environment"]`；L49断言`local.IMAGES["runner"].startswith("rnd-local/daytona-runner:")`。后续分支沿下方源码相同行号继续阅读。 调用`base_config`、`copy.deepcopy`、`profile.render_profile`、`local.IMAGES["runner"].startswith`、`snapshot_resources`、`pytest.raises`、`profile.profile_directory`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `snapshot_inspect`（L55–L73）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`profile.recipe_identity`。 返回路径：L57的`{ "Id": SNAPSHOT, "Os": "linux", "Architecture": "amd64", "RepoDigests": ["127.0.0.1:6000/…`。
- `test_snapshot_requires_declared_control_identity_and_no_inherited_command`（L86–L92）：接收`field`、`value`。 调用`snapshot_inspect`、`profile.recipe_identity`、`profile.validate_image`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runner_requires_the_explicit_normal_daemon_entrypoint`（L95–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L98遍历`([], ["USE_SNAPSHOT_ENTRYPOINT=true"])`。 调用`snapshot_inspect`、`profile.recipe_identity`、`pytest.raises`、`profile.validate_image`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_fixture`（L106–L141）：接收`tmp_path`、`monkeypatch`。 控制顺序：L115遍历`profile.RECIPE_PATHS`。 调用`context.mkdir`、`path.parent.mkdir`、`path.write_text`、`"".join`、`difflib.unified_diff`、`source.splitlines`、`source.replace(profile.OLD, profile.NEW).splitlines`、`source.replace`、`(root / "tools/daytona/capability-runner.patch").write_text`等。 返回路径：L141的`root, context, source, workspace`。
- `source_fixture.export`（L129–L135）：接收`directory`、`command`、`target`。 调用`Path`、`path.parent.mkdir`、`path.write_text`、`(Path(target) / "go.work").write_text`、`(Path(target) / "apps/runner/go.mod").write_text`、`(Path(target) / "apps/runner/go.sum").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_preimage_and_patch_are_exact_and_module_inputs_are_preserved`（L144–L152）：接收`tmp_path`、`monkeypatch`。 控制顺序：L147断言`(context / profile.SOURCE_FILE).read_text() == source.replace(profile.OLD, profile.NE…`；L148断言`(context / "go.work").read_text() == workspace`；L149断言`(context / "apps/runner/go.mod").read_text() == "module fixture\ngo 1.25.5\n"`；L150断言`(context / "go.work.sum").read_text() == "fixture v1 h1:fixture\n"`；L151断言`record["source_sha"] == profile.DAYTONA_SOURCE`；L152断言`(context / "capability-build/NOTICE").is_file()`。 调用`source_fixture`、`profile.source_context`、`(context / profile.SOURCE_FILE).read_text`、`source.replace`、`(context / "go.work").read_text`、`(context / "apps/runner/go.mod").read_text`、`(context / "go.work.sum").read_text`、`(context / "capability-build/NOTICE").is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_drift_fails_closed_before_any_build`（L156–L166）：接收`tmp_path`、`monkeypatch`、`changed`。 控制顺序：L158按`changed == "source"`分支；L160按`changed == "workspace"`分支。 调用`source_fixture`、`monkeypatch.setattr`、`(root / "tools/daytona/capability-runner.patch").open`、`file.write`、`pytest.raises`、`profile.source_context`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `application_inspect`（L169–L196）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L170的`{ "Name": "/" + SANDBOX, "Image": SNAPSHOT, "State": {"Running": True}, "Config": { "User"…`。
- `inspection`（L200–L229）：接收`tmp_path`、`monkeypatch`。 调用`application_inspect`、`monkeypatch.setattr`。 返回路径：L229的`tmp_path, outer, inner, calls`。
- `inspection.docker`（L222–L226）：接收`*args`、`**kwargs`。 控制顺序：L224按`"info" in args`分支。 调用`calls.append`、`json.dumps`、`inner.get`。 返回路径：L225的`json.dumps(inner.get("engine_security", ["name=seccomp,profile=builtin"]))`；L226的`json.dumps([outer if args[0] == "container" else inner])`。
- `test_readonly_inspection_is_scoped_to_owned_uuid_and_redacts_everything_else`（L232–L263）：接收`inspection`。 控制顺序：L235断言`proof["privileged"] is False and proof["seccomp"] == "docker-default"`；L236断言`proof["snapshot_image_id"] == SNAPSHOT`；L237断言`calls == [ ("container", "inspect", OUTER), ( "exec", OUTER, "docker", "--host", "uni…`；L260断言`"SECRET" not in json.dumps(proof) and "TOKEN" not in json.dumps(proof)`；L263断言`len(calls) == 3`。 调用`profile.inspect_created_sandbox`、`json.dumps`、`pytest.raises`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_created_application_rejects_real_inspect_drift`（L290–L294）：接收`inspection`、`mutation`。 调用`mutation`、`pytest.raises`、`profile.inspect_created_sandbox`、`pytest.mark.parametrize`、`row.update`、`row["Config"].update`、`row["HostConfig"].update`、`row["Mounts"][0].update`、`row["Mounts"].append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_wrong_runner_is_rejected_before_an_inner_exec`（L297–L302）：接收`inspection`。 控制顺序：L302断言`len(calls) == 1`。 调用`pytest.raises`、`profile.inspect_created_sandbox`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recipe_keeps_real_embeds_glibc_smoke_license_and_locked_go_inputs`（L305–L332）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L307遍历`( "./apps/daemon/cmd/daemon", "./libs/computer-use", "./apps/runn…`；L322断言`text in recipe`；L323断言`"go mod edit" not in recipe and "yarn" not in recipe`；L325断言`snapshot.rstrip().endswith("USER 0:0")`；L326断言`"WORKDIR /opt/rnd/control" in snapshot`；L327断言`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip() .endswith("WORKDIR…`。 调用`(profile.ROOT / "tools/daytona/capability-runner.Dockerfile").rea…`、`(profile.ROOT / "tools/daytona/capability-snapshot.Dockerfile").r…`、`snapshot.rstrip().endswith`、`snapshot.rstrip`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip(…`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `locked_profile`（L336–L391）：接收`tmp_path`。 控制顺序：L339遍历`base["services"].items()`。 调用`base_config`、`base["services"].items`、`tag.rsplit`、`profile.write_compose`、`local.private_json`、`profile.recipe_identity`、`profile.BASES.items`、`profile.sha256`、`(identity + json.dumps(bases, sort_keys=True)).encode`等。 返回路径：L391的`tmp_path, record`。
- `test_profile_lock_roundtrip_preserves_ordinary_lock_and_rejects_compose_changes`（L394–L403）：接收`locked_profile`。 控制顺序：L398断言`actual == record`；L403断言`(directory / "compose.lock.yaml").read_bytes() == ordinary`。 调用`(directory / "compose.lock.yaml").read_bytes`、`profile.load_profile`、`profile.write_compose`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_edited_lock_cannot_select_general_or_unpinned_images`（L416–L422）：接收`locked_profile`、`mutation`。 调用`mutation`、`local.private_json`、`pytest.raises`、`profile.load_profile`、`pytest.mark.parametrize`、`record["bases"]["GO_IMAGE"].update`、`record["snapshot"].update`、`record["runner"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_profile_verifies_image_id_and_registry_digest`（L425–L439）：接收`locked_profile`、`monkeypatch`。 控制顺序：L434断言`profile.require_profile(directory, record["snapshot"]["snapshot"]) == record`。 调用`snapshot_inspect`、`copy.deepcopy`、`monkeypatch.setattr`、`profile.require_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_never_overwrites_existing_profile_or_credentials`（L442–L448）：接收`locked_profile`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`profile.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_actual_engine_seccomp_is_not_default_filter_evidence`（L454–L459）：接收`inspection`、`options`。 控制顺序：L459断言`len(calls) == 2`。 调用`pytest.raises`、`profile.inspect_created_sandbox`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L459。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17926`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e7f63a428d6f105c5ed3b43efeaea9f46d2d46aecb7f1bbcf7e2336cdd9b376d"} -->
````python
# tests/test_daytona_capability_profile.py
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
    )
    workspace = "go 1.25.5\n\nuse ./apps/runner\n"
    for name in profile.RECIPE_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("recipe fixture\n")
    patch = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            source.replace(profile.OLD, profile.NEW).splitlines(keepends=True),
            fromfile="a/" + profile.SOURCE_FILE,
            tofile="b/" + profile.SOURCE_FILE,
        )
    )
    (root / "tools/daytona/capability-runner.patch").write_text(patch)

    def export(directory, command, target):
        path = Path(target) / profile.SOURCE_FILE
        path.parent.mkdir(parents=True)
        path.write_text(source)
        (Path(target) / "go.work").write_text(workspace)
        (Path(target) / "apps/runner/go.mod").write_text("module fixture\ngo 1.25.5\n")
        (Path(target) / "apps/runner/go.sum").write_text("fixture v1 h1:fixture\n")

    monkeypatch.setattr(profile, "ROOT", root)
    monkeypatch.setattr(profile, "export_source", export)
    monkeypatch.setattr(profile, "SOURCE_BLOB", profile.blob(source.encode()))
    monkeypatch.setattr(profile, "WORKSPACE_BLOB", profile.blob(workspace.encode()))
    return root, context, source, workspace


def test_source_preimage_and_patch_are_exact_and_module_inputs_are_preserved(tmp_path, monkeypatch):
    _, context, source, workspace = source_fixture(tmp_path, monkeypatch)
    record = profile.source_context(tmp_path, context)
    assert (context / profile.SOURCE_FILE).read_text() == source.replace(profile.OLD, profile.NEW)
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
````
