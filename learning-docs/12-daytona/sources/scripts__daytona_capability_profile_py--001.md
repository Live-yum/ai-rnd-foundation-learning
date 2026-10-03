# scripts/daytona_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_capability_profile；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_build`、`workbench.local_only`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `sha256`（L86–L87）：接收`raw`。 调用`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`。 返回路径：L87的`hashlib.sha256(raw).hexdigest()`。
- `blob`（L90–L91）：接收`raw`。 调用`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`。 返回路径：L91的`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()`。
- `recipe_identity`（L94–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha256`、`(ROOT / name).read_bytes`、`json.dumps(hashes, sort_keys=True).encode`、`json.dumps`。 返回路径：L97的`identity, hashes`。
- `profile_directory`（L100–L104）：接收`directory`。 控制顺序：L102按`directory == local.HOME.resolve()`分支；L103抛异常，停止当前正常路径。 调用`Path(directory).resolve`、`Path`、`local.HOME.resolve`、`ValueError`。 返回路径：L104的`directory`。
- `read_base`（L107–L124）：接收`directory`。 控制顺序：L112按`installation != { "source_sha": DAYTONA_SOURCE, "release": "v" + DAYTONA_VERSION, "de…`分支；L118抛异常，停止当前正常路径；L119遍历`config["services"].items()`；L122按`service["image"] != expected or record["tag"] != local.IMAGES[name]`分支；L123抛异常，停止当前正常路径。 调用`yaml.safe_load`、`(directory / "compose.lock.yaml").read_text`、`local.assert_local_compose`、`json.loads`、`(directory / "images.lock.json").read_text`、`(directory / "installation.json").read_text`、`ValueError`、`config["services"].items`、`record.get`。 返回路径：L124的`config`。
- `source_context`（L127–L175）：接收`directory`、`context`。 源码说明：Export committed source only; reject drift before applying the exact patch.。 控制顺序：L130按`DAYTONA_SOURCE != PINNED_SOURCE or DAYTONA_VERSION != "0.190.0"`分支；L131抛异常，停止当前正常路径；L135按`blob(raw) != SOURCE_BLOB or raw.count(OLD.encode()) != 1`分支；L136抛异常，停止当前正常路径；L137按`blob((context / "go.work").read_bytes()) != WORKSPACE_BLOB`分支；L138抛异常，停止当前正常路径；L148按`(ROOT / "tools/daytona/capability-runner.patch").read_text() != expected_patch`分支；L149抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`ValueError`、`export_source`、`target.read_bytes`、`blob`、`raw.count`、`OLD.encode`、`(context / "go.work").read_bytes`、`raw.decode().replace`等。 返回路径：L175的`{"source_sha": DAYTONA_SOURCE, "go_inputs": inputs, "patched_sha256": sha256(updated)}`。
- `download_assets`（L178–L185）：接收`context`。 控制顺序：L180遍历`ASSETS.items()`；L183按`len(raw) > 1_000_000 or sha256(raw) != expected`分支；L184抛异常，停止当前正常路径。 调用`urllib.request.build_opener`、`urllib.request.ProxyHandler`、`ASSETS.items`、`opener.open`、`response.read`、`len`、`sha256`、`ValueError`、`(Path(context) / "apps/daemon/pkg/terminal/static" / name).write_…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `inspect_image`（L188–L195）：接收`reference`。 控制顺序：L190按`len(rows) != 1 or not re.fullmatch(r"sha256:[a-f0-9]{64}", rows[0].get("Id", ""))`分支；L191抛异常，停止当前正常路径；L193按`image.get("Os") != "linux" or image.get("Architecture") != "amd64"`分支；L194抛异常，停止当前正常路径。 调用`json.loads`、`local.docker`、`len`、`re.fullmatch`、`rows[0].get`、`ValueError`、`image.get`。 返回路径：L195的`image`。
- `resolve_bases`（L198–L208）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L200遍历`BASES.items()`；L205按`len(digests) != 1 or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", digests[0]…`分支；L206抛异常，停止当前正常路径。 调用`BASES.items`、`local.docker`、`inspect_image`、`tag.rsplit`、`image.get`、`value.startswith`、`len`、`re.fullmatch`、`re.escape`等。 返回路径：L208的`result`。
- `build_image`（L211–L234）：接收`directory`、`context`、`recipe`、`tag`、`bases`、`identity`。 控制顺序：L213遍历`bases.items()`。 调用`bases.items`、`str`、`local.docker`、`(directory / (recipe + ".log")).write_text`、`inspect_image`、`validate_image`。 返回路径：L234的`image`。
- `validate_image`（L237–L257）：接收`image`、`identity`、`snapshot`。 控制顺序：L240按`labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE or labels.get("rnd.…`分支；L245抛异常，停止当前正常路径；L246按`snapshot`分支；L247按`config.get("User") != "0:0" or config.get("WorkingDir") != CONTROL_WORKDIR or config.…`分支；L253抛异常，停止当前正常路径；L256按`"USE_SNAPSHOT_ENTRYPOINT=false" not in config.get("Env", [])`分支；L257抛异常，停止当前正常路径。 调用`image.get`、`config.get`、`labels.get`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `render_profile`（L260–L267）：接收`base`、`runner_id`、`image`。 调用`copy.deepcopy`、`local.assert_local_compose`。 返回路径：L267的`config`。
- `write_compose`（L270–L273）：接收`path`、`config`。 控制顺序：L272按`os.name != "nt"`分支。 调用`path.write_text`、`yaml.safe_dump`、`path.chmod`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare`（L276–L388）：接收`directory`。 控制顺序：L279遍历`(COMPOSE, LOCK, "snapshot-image.json", "api-key.json", "workbench…`；L280按`(directory / name).exists()`分支；L281抛异常，停止当前正常路径；L285按`info.get("OSType") != "linux" or info.get("Architecture") not in {"amd64", "x86_64"}`分支；L286抛异常，停止当前正常路径；L297按`existing.strip()`分支；L298抛异常，停止当前正常路径；L306按`stamp == local.snapshot_stamp()`分支。后续分支沿下方源码相同行号继续阅读。 调用`profile_directory`、`read_base`、`(directory / name).exists`、`ValueError`、`json.loads`、`local.docker`、`info.get`、`str`、`existing.strip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_profile`（L391–L444）：接收`directory`。 控制顺序：L395按`record.get("profile") != PROFILE or record.get("recipe_identity") != identity or reco…`分支；L403抛异常，停止当前正常路径；L405按`set(bases) != set(BASES)`分支；L406抛异常，停止当前正常路径；L407遍历`BASES.items()`；L410按`entry.get("tag") != tag or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", entr…`分支；L415抛异常，停止当前正常路径；L418按`image.get("source_hash") != stamp or image.get("image") != "registry:6000/rnd-python:…`分支。后续分支沿下方源码相同行号继续阅读。 调用`profile_directory`、`json.loads`、`(directory / LOCK).read_text`、`recipe_identity`、`record.get`、`record.get("source", {}).get`、`sha256`、`(directory / "compose.lock.yaml").read_bytes`、`ValueError`等。 返回路径：L444的`config, record`。
- `compose`（L447–L457）：接收`directory`、`timeout`、`*args`。 调用`load_profile`、`local.docker`、`str`、`Path`。 返回路径：L449的`local.docker( "compose", "--project-name", PROJECT, "--file", str(Path(directory) / COMPOS…`。
- `require_profile`（L460–L474）：接收`directory`、`snapshot`。 源码说明：Read-only prerequisite check; never a substitute for the isolation receipt.。 控制顺序：L463按`snapshot is not None and snapshot != record["snapshot"]["snapshot"]`分支；L464抛异常，停止当前正常路径；L470按`image["Id"] != record["snapshot"]["image_id"] or expected_digest not in image.get( "R…`分支；L473抛异常，停止当前正常路径。 调用`load_profile`、`ValueError`、`inspect_image`、`validate_image`、`record["snapshot"]["digest"].replace`、`image.get`。 返回路径：L474的`record`。
- `inspect_created_sandbox`（L477–L585）：接收`directory`、`sandbox_id`。 源码说明：Inspect only the newly owned UUID inside the verified profile Runner. Upstream create.go names the Docker container sandboxDto.Id. No shell, caller-provided Docker options, executable, or general comm。 控制顺序：L486按`not isinstance(sandbox_id, str) or str(UUID(sandbox_id)) != sandbox_id`分支；L487抛异常，停止当前正常路径；L490按`not re.fullmatch(r"[a-f0-9]{64}", runner_id)`分支；L491抛异常，停止当前正常路径；L493按`len(rows) != 1`分支；L494抛异常，停止当前正常路径；L497按`runner.get("Image") != record["runner"]["image_id"] or runner.get("State", {}).get("R…`分支；L507抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`str`、`UUID`、`ValueError`、`require_profile`、`compose(directory, "ps", "--quiet", "runner").strip`、`compose`、`re.fullmatch`、`json.loads`等。 返回路径：L574的`{ "profile": PROFILE, "sandbox_id": sandbox_id, "runner_image_id": record["runner"]["image…`。
- `up`（L588–L626）：接收`directory`。 控制顺序：L600遍历`range(90)`；L607按`any(row.get("State") in {"exited", "dead", "removing"} for row in rows)`分支；L608抛异常，停止当前正常路径；L614按`ready == local.KEEP`分支；L616遍历`endpoints`；L624按`attempt < 89`分支；L626抛异常，停止当前正常路径。 调用`require_profile`、`compose`、`httpx.Client`、`range`、`raw.lstrip().startswith`、`raw.lstrip`、`json.loads`、`raw.splitlines`、`line.strip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L629–L642）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L634按`args.action == "prepare"`分支；L636按`args.action == "up"`分支；L638按`args.action == "check"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`prepare`、`up`、`require_profile`、`print`、`compose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L650。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`27362`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ab3f81449866762e1ae800bd20ec53752aa289ca612c47ff2516f758302688e3"} -->
````python
# scripts/daytona_capability_profile.py
"""Build the owned, fixed-authored capability profile before starting Daytona.

Use a fresh directory with daytona_local prepare/images first. This command never
changes the ordinary installation, production gates, Docker daemon policy, or
application security flags. Only the pinned Runner's privileged application
container default is removed. Live proof is still required by ci_capability_profile.
"""

import argparse
import copy
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import yaml

from scripts import daytona_local as local
from scripts.daytona_build import BUILT, export_source
from workbench.local_only import DAYTONA_SOURCE, DAYTONA_VERSION
from workbench.settings import ROOT

HOME = ROOT / ".data/daytona-capability"
PROJECT = "rnd-daytona-capability"
PROFILE = "fixed-authored-sqlite-v1"
PINNED_SOURCE = "01c502bb1f1ff8f2885d0cd490e043736083dca8"
COMPOSE = "compose.capability.lock.yaml"
LOCK = "capability-profile.lock.json"
CONTROL_WORKDIR = "/opt/rnd/control"
SOURCE_FILE = "apps/runner/pkg/docker/container_configs.go"
SOURCE_BLOB = "d5a97203afa87c3fa0065702723c41645bf284b6"
WORKSPACE_BLOB = "daf66a070fb41cdf12ecbbdb7dc4a20cf4b9bba0"
OLD = """		// Privileged mode exposes every /dev/nvidia* node and bypasses the
		// CDI cgroup rules, so GPU sandboxes have to opt out to keep their
		// allocated card isolated. Non-GPU sandboxes still need privileged
		// for their current workloads.
		Privileged: gpuIndex == nil,
"""
NEW = """		// Owned fixed-application profile: all application containers use
		// Docker's unprivileged defaults, including its default seccomp filter.
		Privileged: false,
"""
RECIPE_PATHS = (
    "scripts/daytona_capability_profile.py",
    "tools/daytona/capability-runner.Dockerfile",
    "tools/daytona/capability-snapshot.Dockerfile",
    "tools/daytona/capability-runner.patch",
    "tools/daytona/runner-entry.sh",
    "templates/product/pyproject.toml",
    "templates/product/uv.lock",
)
BASES = {
    "GO_IMAGE": "golang:1.25.11-bookworm",
    # The plugin's upstream CGO baseline is glibc 2.35, from Ubuntu 22.04.
    "BUILD_IMAGE": "ubuntu:22.04",
    "DOCKER_IMAGE": "docker:28.5.2-dind-alpine3.22",
    "RUNTIME_IMAGE": "debian:trixie-slim",
    "UV_IMAGE": "ghcr.io/astral-sh/uv:0.12.20",
    "NODE_IMAGE": "node:22.23.2-bookworm-slim",
    "SANDBOX_IMAGE": "daytonaio/sandbox:0.5.0-slim",
}
# Upstream apps/daemon/tools/xterm.go assets, now bounded and SHA-256 checked.
ASSETS = {
    "xterm.js": (
        "https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js",
        "f0aea0f75f48559013ae6643c2479dd737d26da42d5524e6d2b70915ae6523c7",
    ),
    "xterm.css": (
        "https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css",
        "832f3f2c603b43ad4351ff04970150cc7a873014276db126a6065c6dd81e4872",
    ),
    "xterm-addon-fit.js": (
        "https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js",
        "10f3194c5f17c1786fb7d5db865c1ec8539b6736a318063fd38bdaaf7c46848f",
    ),
}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def recipe_identity():
    hashes = {name: sha256((ROOT / name).read_bytes()) for name in RECIPE_PATHS}
    identity = sha256(json.dumps(hashes, sort_keys=True).encode())
    return identity, hashes


def profile_directory(directory):
    directory = Path(directory).resolve()
    if directory == local.HOME.resolve():
        raise ValueError("Capability profile requires its own disposable directory")
    return directory


def read_base(directory):
    config = yaml.safe_load((directory / "compose.lock.yaml").read_text(encoding="utf-8"))
    local.assert_local_compose(config)
    records = json.loads((directory / "images.lock.json").read_text(encoding="utf-8"))
    installation = json.loads((directory / "installation.json").read_text(encoding="utf-8"))
    if installation != {
        "source_sha": DAYTONA_SOURCE,
        "release": "v" + DAYTONA_VERSION,
        "deployment": "local-development-only",
        "cloud_account": False,
    }:
        raise ValueError("Capability profile requires the pinned local installation")
    for name, service in config["services"].items():
        record = records[name]
        expected = record.get("image_id") if name in BUILT else record.get("digest")
        if service["image"] != expected or record["tag"] != local.IMAGES[name]:
            raise ValueError("Original local image lock does not match Compose: " + name)
    return config


def source_context(directory, context):
    """Export committed source only; reject drift before applying the exact patch."""
    context = Path(context)
    if DAYTONA_SOURCE != PINNED_SOURCE or DAYTONA_VERSION != "0.190.0":
        raise ValueError("Capability profile supports only its exact reviewed upstream revision")
    export_source(directory, local.command, context)
    target = context / SOURCE_FILE
    raw = target.read_bytes()
    if blob(raw) != SOURCE_BLOB or raw.count(OLD.encode()) != 1:
        raise ValueError("Pinned Runner source preimage does not match")
    if blob((context / "go.work").read_bytes()) != WORKSPACE_BLOB:
        raise ValueError("Pinned Go workspace does not match")
    updated = raw.decode().replace(OLD, NEW)
    expected_patch = "".join(
        difflib.unified_diff(
            raw.decode().splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile="a/" + SOURCE_FILE,
            tofile="b/" + SOURCE_FILE,
        )
    )
    if (ROOT / "tools/daytona/capability-runner.patch").read_text() != expected_patch:
        raise ValueError("Profile patch does not exactly match the owned single-change recipe")
    target.write_text(updated, encoding="utf-8", newline="\n")
    updated = updated.encode()
    # Upstream excludes go.work.sum from Git. Seed with its committed checksums;
    # preserve the full workspace so its selected versions need no go.mod edit.
    sums = set()
    for path in sorted(context.glob("**/go.sum")):
        sums.update(path.read_text(encoding="utf-8").splitlines())
    (context / "go.work.sum").write_text("\n".join(sorted(sums)) + "\n", encoding="utf-8")
    inputs = {
        str(path.relative_to(context)): sha256(path.read_bytes())
        for path in sorted(context.glob("**/go.*"))
        if path.name in {"go.mod", "go.sum", "go.work", "go.work.sum"}
    }
    support = context / "capability-build"
    support.mkdir()
    for name in RECIPE_PATHS:
        shutil.copyfile(ROOT / name, support / Path(name).name)
    (support / "NOTICE").write_text(
        "Daytona, Copyright 2025 Daytona Platforms Inc.; AGPL-3.0.\n"
        f"Upstream: https://github.com/daytonaio/daytona/tree/{DAYTONA_SOURCE}\n"
        "Owned fixed-authored SQLite profile: container Privileged is always false.\n"
        "Complete corresponding source and build recipes: source.tar beside this notice.\n"
        "This is a local acceptance profile; it does not enable production source execution.\n",
        encoding="utf-8",
    )
    return {"source_sha": DAYTONA_SOURCE, "go_inputs": inputs, "patched_sha256": sha256(updated)}


def download_assets(context):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for name, (url, expected) in ASSETS.items():
        with opener.open(url, timeout=90) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000 or sha256(raw) != expected:
            raise ValueError("Pinned terminal asset checksum does not match: " + name)
        (Path(context) / "apps/daemon/pkg/terminal/static" / name).write_bytes(raw)


def inspect_image(reference):
    rows = json.loads(local.docker("image", "inspect", reference))
    if len(rows) != 1 or not re.fullmatch(r"sha256:[a-f0-9]{64}", rows[0].get("Id", "")):
        raise ValueError("Image must have one immutable local identity")
    image = rows[0]
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise ValueError("Capability profile only supports Linux amd64 images")
    return image


def resolve_bases():
    result = {}
    for name, tag in BASES.items():
        local.docker("pull", "--platform=linux/amd64", tag)
        image = inspect_image(tag)
        prefix = tag.rsplit(":", 1)[0] + "@sha256:"
        digests = [value for value in image.get("RepoDigests", []) if value.startswith(prefix)]
        if len(digests) != 1 or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", digests[0]):
            raise ValueError("Official builder image has no unique registry digest: " + name)
        result[name] = {"tag": tag, "digest": digests[0], "image_id": image["Id"]}
    return result


def build_image(directory, context, recipe, tag, bases, identity):
    argv = ["build", "--progress=plain", "--platform=linux/amd64", "--pull=false"]
    for name, record in bases.items():
        argv += ["--build-arg", name + "=" + record["digest"]]
    argv += [
        "--file",
        str(ROOT / "tools/daytona" / recipe),
        "--label",
        "org.opencontainers.image.revision=" + DAYTONA_SOURCE,
        "--label",
        "org.opencontainers.image.licenses=AGPL-3.0",
        "--label",
        "rnd.capability.profile=" + PROFILE,
        "--label",
        "rnd.capability.recipe=" + identity,
        "--tag",
        tag,
        str(context),
    ]
    log = local.docker(*argv, timeout=3000)
    (directory / (recipe + ".log")).write_text(log, encoding="utf-8")
    image = inspect_image(tag)
    validate_image(image, identity, snapshot=recipe == "capability-snapshot.Dockerfile")
    return image


def validate_image(image, identity, *, snapshot):
    config = image.get("Config") or {}
    labels = config.get("Labels") or {}
    if (
        labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE
        or labels.get("rnd.capability.profile") != PROFILE
        or labels.get("rnd.capability.recipe") != identity
    ):
        raise ValueError("Image does not identify the reviewed capability recipe")
    if snapshot:
        if (
            config.get("User") != "0:0"
            or config.get("WorkingDir") != CONTROL_WORKDIR
            or config.get("Entrypoint")
            or config.get("Cmd")
        ):
            raise ValueError(
                "Snapshot must declare root control identity and trusted working directory"
            )
    elif "USE_SNAPSHOT_ENTRYPOINT=false" not in config.get("Env", []):
        raise ValueError("Profile Runner must explicitly use its normal daemon entrypoint")


def render_profile(base, runner_id, image):
    config = copy.deepcopy(base)
    config["name"] = PROJECT
    config["services"]["runner"]["image"] = runner_id
    config["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] = "false"
    config["services"]["api"]["environment"]["DEFAULT_SNAPSHOT"] = image
    local.assert_local_compose(config)
    return config


def write_compose(path, config):
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)


def prepare(directory=HOME):
    directory = profile_directory(directory)
    base = read_base(directory)
    for name in (COMPOSE, LOCK, "snapshot-image.json", "api-key.json", "workbench.env"):
        if (directory / name).exists():
            raise ValueError(
                "Profile setup requires fresh local state; will not overwrite: " + name
            )
    info = json.loads(local.docker("info", "--format", "{{json .}}"))
    if info.get("OSType") != "linux" or info.get("Architecture") not in {"amd64", "x86_64"}:
        raise ValueError("Capability profile supports only a local Linux amd64 Docker daemon")
    existing = local.docker(
        "compose",
        "--project-name",
        PROJECT,
        "--file",
        str(directory / "compose.lock.yaml"),
        "ps",
        "--all",
        "--quiet",
    )
    if existing.strip():
        raise ValueError("Capability profile must be prepared before any profile containers exist")
    identity, recipes = recipe_identity()
    bases = resolve_bases()
    # Include resolved immutable dependency images in the snapshot tag identity.
    stamp = sha256((identity + json.dumps(bases, sort_keys=True)).encode())[:16]
    runner_tag = "rnd-local/daytona-capability-runner:" + stamp
    snapshot_tag = "127.0.0.1:6000/rnd-python:" + stamp
    image_ref = "registry:6000/rnd-python:" + stamp
    if stamp == local.snapshot_stamp():
        raise ValueError("Capability profile cannot overwrite the ordinary snapshot tag")
    with tempfile.TemporaryDirectory(prefix="capability-build-", dir=directory) as temporary:
        context = Path(temporary)
        source = source_context(directory, context)
        local.private_json(
            context / "capability-build/build-inputs.json",
            {
                "profile": PROFILE,
                "recipe_identity": identity,
                "recipes": recipes,
                "bases": bases,
                "source": source,
            },
        )
        download_assets(context)
        runner = build_image(
            directory, context, "capability-runner.Dockerfile", runner_tag, bases, identity
        )
    with tempfile.TemporaryDirectory(prefix="capability-snapshot-", dir=directory) as temporary:
        context = Path(temporary)
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(ROOT / "templates/product" / name, context / name)
        snapshot = build_image(
            directory, context, "capability-snapshot.Dockerfile", snapshot_tag, bases, identity
        )
    config = render_profile(base, runner["Id"], image_ref)
    # Registry startup uses the validated profile configuration, with an isolated
    # Compose project. No API, Runner, or application container starts here.
    temporary_compose = directory / COMPOSE
    write_compose(temporary_compose, config)
    local.docker(
        "compose",
        "--project-name",
        PROJECT,
        "--file",
        str(temporary_compose),
        "up",
        "-d",
        "--pull",
        "never",
        "registry",
        "gateway",
    )
    local.wait_for_registry()
    local.docker("push", snapshot_tag)
    published = inspect_image(snapshot_tag)
    prefix = "127.0.0.1:6000/rnd-python@sha256:"
    digests = [value for value in published.get("RepoDigests", []) if value.startswith(prefix)]
    if len(digests) != 1 or published["Id"] != snapshot["Id"]:
        raise ValueError("Snapshot publication changed identity or has no unique local digest")
    record = {
        "profile": PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "source": source,
        "bases": bases,
        "base_compose_sha256": sha256((directory / "compose.lock.yaml").read_bytes()),
        "runner": {
            "tag": runner_tag,
            "image_id": runner["Id"],
            "user": runner["Config"].get("User", ""),
            "recipe_sha256": recipes["tools/daytona/capability-runner.Dockerfile"],
        },
        "snapshot": {
            "image": image_ref,
            "snapshot": "rnd-python-" + stamp,
            "source_hash": stamp,
            "local_tag": snapshot_tag,
            "image_id": snapshot["Id"],
            "digest": "registry:6000/rnd-python@" + digests[0].split("@", 1)[1],
            "user": "0:0",
            "working_dir": CONTROL_WORKDIR,
            "recipe_sha256": recipes["tools/daytona/capability-snapshot.Dockerfile"],
        },
    }
    # Commit readiness last. A partial build never produces a passing profile lock.
    write_compose(directory / COMPOSE, config)
    local.private_json(directory / "snapshot-image.json", record["snapshot"])
    local.private_json(directory / LOCK, record)
    print(
        "Dedicated capability profile built; immutable Runner and root-control snapshot recorded."
    )


def load_profile(directory=HOME):
    directory = profile_directory(directory)
    record = json.loads((directory / LOCK).read_text(encoding="utf-8"))
    identity, recipes = recipe_identity()
    if (
        record.get("profile") != PROFILE
        or record.get("recipe_identity") != identity
        or record.get("recipes") != recipes
        or record.get("source", {}).get("source_sha") != DAYTONA_SOURCE
        or record.get("base_compose_sha256")
        != sha256((directory / "compose.lock.yaml").read_bytes())
    ):
        raise ValueError("Capability profile recipe or original installation changed; unsupported")
    bases = record.get("bases", {})
    if set(bases) != set(BASES):
        raise ValueError("Capability profile builder dependency lock is incomplete")
    for name, tag in BASES.items():
        entry = bases[name]
        prefix = tag.rsplit(":", 1)[0] + "@sha256:"
        if (
            entry.get("tag") != tag
            or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", entry.get("digest", ""))
            or not re.fullmatch(r"sha256:[a-f0-9]{64}", entry.get("image_id", ""))
        ):
            raise ValueError("Capability profile builder dependency is not digest-locked")
    stamp = sha256((identity + json.dumps(bases, sort_keys=True)).encode())[:16]
    image = record.get("snapshot", {})
    if (
        image.get("source_hash") != stamp
        or image.get("image") != "registry:6000/rnd-python:" + stamp
        or image.get("local_tag") != "127.0.0.1:6000/rnd-python:" + stamp
        or image.get("snapshot") != "rnd-python-" + stamp
        or image.get("user") != "0:0"
        or image.get("working_dir") != CONTROL_WORKDIR
        or image.get("recipe_sha256") != recipes["tools/daytona/capability-snapshot.Dockerfile"]
        or record.get("runner", {}).get("recipe_sha256")
        != recipes["tools/daytona/capability-runner.Dockerfile"]
        or not re.fullmatch(
            r"registry:6000/rnd-python@sha256:[a-f0-9]{64}", image.get("digest", "")
        )
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", image.get("image_id", ""))
        or record.get("runner", {}).get("tag") != "rnd-local/daytona-capability-runner:" + stamp
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", record.get("runner", {}).get("image_id", ""))
    ):
        raise ValueError("Capability profile image lock does not match its derived identity")
    base = read_base(directory)
    config = yaml.safe_load((directory / COMPOSE).read_text(encoding="utf-8"))
    expected = render_profile(base, record["runner"]["image_id"], record["snapshot"]["image"])
    if config != expected:
        raise ValueError("Profile Compose differs from its exact allowed transformation")
    metadata = json.loads((directory / "snapshot-image.json").read_text(encoding="utf-8"))
    if metadata != record["snapshot"]:
        raise ValueError("Profile snapshot metadata differs from its immutable lock")
    return config, record


def compose(directory, *args, timeout=900):
    load_profile(directory)
    return local.docker(
        "compose",
        "--project-name",
        PROJECT,
        "--file",
        str(Path(directory) / COMPOSE),
        *args,
        timeout=timeout,
    )


def require_profile(directory=HOME, snapshot=None):
    """Read-only prerequisite check; never a substitute for the isolation receipt."""
    _, record = load_profile(directory)
    if snapshot is not None and snapshot != record["snapshot"]["snapshot"]:
        raise ValueError("Fixed application must explicitly select the owned profile snapshot")
    runner = inspect_image(record["runner"]["image_id"])
    image = inspect_image(record["snapshot"]["local_tag"])
    validate_image(runner, record["recipe_identity"], snapshot=False)
    validate_image(image, record["recipe_identity"], snapshot=True)
    expected_digest = record["snapshot"]["digest"].replace("registry:6000/", "127.0.0.1:6000/", 1)
    if image["Id"] != record["snapshot"]["image_id"] or expected_digest not in image.get(
        "RepoDigests", []
    ):
        raise ValueError("Profile snapshot tag no longer matches the recorded ID and digest")
    return record


def inspect_created_sandbox(directory, sandbox_id):
    """Inspect only the newly owned UUID inside the verified profile Runner.

    Upstream create.go names the Docker container sandboxDto.Id. No shell,
    caller-provided Docker options, executable, or general command is accepted.
    The receipt contains no environment, paths, credentials, or user content.
    """
    from uuid import UUID

    if not isinstance(sandbox_id, str) or str(UUID(sandbox_id)) != sandbox_id:
        raise ValueError("Owned sandbox must have one canonical UUID")
    record = require_profile(directory)
    runner_id = compose(directory, "ps", "--quiet", "runner").strip()
    if not re.fullmatch(r"[a-f0-9]{64}", runner_id):
        raise ValueError("Profile requires exactly one running Runner container")
    rows = json.loads(local.docker("container", "inspect", runner_id))
    if len(rows) != 1:
        raise ValueError("Profile Runner container identity is ambiguous")
    runner = rows[0]
    labels = runner.get("Config", {}).get("Labels", {})
    if (
        runner.get("Image") != record["runner"]["image_id"]
        or runner.get("State", {}).get("Running") is not True
        or labels.get("com.docker.compose.project") != PROJECT
        or labels.get("com.docker.compose.service") != "runner"
        or "USE_SNAPSHOT_ENTRYPOINT=false" not in runner.get("Config", {}).get("Env", [])
        or runner.get("Config", {}).get("Entrypoint")
        != ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"]
        or runner.get("Config", {}).get("Cmd")
    ):
        raise ValueError("Running Runner does not match the owned profile")
    security = json.loads(
        local.docker(
            "exec",
            runner_id,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "info",
            "--format",
            "{{json .SecurityOptions}}",
            timeout=30,
        )
    )
    if not isinstance(security, list) or "name=seccomp,profile=builtin" not in security:
        raise ValueError("Inner Docker must report its enabled built-in seccomp filter")
    rows = json.loads(
        local.docker(
            "exec",
            runner_id,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "inspect",
            sandbox_id,
            timeout=30,
        )
    )
    if len(rows) != 1:
        raise ValueError("Owned application container identity is ambiguous")
    container = rows[0]
    config, host = container.get("Config", {}), container.get("HostConfig", {})
    if (
        container.get("Name") != "/" + sandbox_id
        or container.get("Image") != record["snapshot"]["image_id"]
        or container.get("State", {}).get("Running") is not True
        or config.get("User") != "0:0"
        or config.get("WorkingDir") != CONTROL_WORKDIR
        or config.get("Entrypoint") != ["/usr/local/bin/daytona"]
        or config.get("Cmd")
        or host.get("Privileged") is not False
        or host.get("CapAdd")
        or host.get("SecurityOpt")
        or host.get("Devices")
        or host.get("DeviceRequests")
        or host.get("PidMode") not in (None, "")
        or host.get("IpcMode") not in (None, "", "private")
        or host.get("NetworkMode") in {"host", "none"}
    ):
        raise ValueError("Created application container does not match the unprivileged profile")
    expected = {
        "/usr/local/bin/daytona": "/usr/local/bin/.tmp/binaries/daemon-amd64",
        "/usr/local/lib/daytona-computer-use": "/usr/local/bin/.tmp/binaries/daytona-computer-use",
    }
    mounts = container.get("Mounts", [])
    if (
        len(mounts) != len(expected)
        or any(
            mount.get("Type") != "bind"
            or mount.get("RW") is not False
            or expected.get(mount.get("Destination")) != mount.get("Source")
            for mount in mounts
        )
        or {mount.get("Destination") for mount in mounts} != set(expected)
    ):
        raise ValueError("Application mounts must be only the two trusted read-only binaries")
    return {
        "profile": PROFILE,
        "sandbox_id": sandbox_id,
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
    }


def up(directory=HOME):
    import httpx

    require_profile(directory)
    compose(directory, "up", "-d", "--pull", "never")
    endpoints = [
        "http://127.0.0.1:3000/api/config",
        "http://127.0.0.1:3003/",
        "http://127.0.0.1:5556/dex/.well-known/openid-configuration",
        "http://127.0.0.1:6000/v2/",
    ]
    with httpx.Client(timeout=3, trust_env=False, follow_redirects=False) as client:
        for attempt in range(90):
            raw = compose(directory, "ps", "--all", "--format", "json")
            rows = (
                json.loads(raw)
                if raw.lstrip().startswith("[")
                else [json.loads(line) for line in raw.splitlines() if line.strip()]
            )
            if any(row.get("State") in {"exited", "dead", "removing"} for row in rows):
                raise RuntimeError("Capability profile service exited before readiness")
            ready = {
                row["Service"]
                for row in rows
                if row.get("State") == "running" and row.get("Health", "") in {"", "healthy"}
            }
            if ready == local.KEEP:
                try:
                    for endpoint in endpoints:
                        client.get(endpoint).raise_for_status()
                    print(
                        "Dedicated capability API, Runner and local identity endpoints are ready."
                    )
                    return
                except httpx.HTTPError:
                    pass
            if attempt < 89:
                time.sleep(2)
    raise RuntimeError("Capability profile readiness timed out; no passing proof was produced")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "up", "check", "status", "down"])
    parser.add_argument("--directory", type=Path, default=HOME)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.directory)
    elif args.action == "up":
        up(args.directory)
    elif args.action == "check":
        require_profile(args.directory)
        print("Profile image and recipe identities match; application isolation is not yet proven.")
    else:
        print(compose(args.directory, *({"status": ["ps"], "down": ["down"]}[args.action])))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print((error.stderr or b"").decode("utf-8", errors="replace")[-12000:])
        raise
````
