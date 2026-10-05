# scripts/daytona_capability_profile.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](scripts__daytona_capability_profile_py--002.md)

**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_capability_profile；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_build`、`workbench.capability_isolation`、`workbench.local_only`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `sha256`（L117–L118）：接收`raw`。 调用`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`。 返回路径：L118的`hashlib.sha256(raw).hexdigest()`。
- `blob`（L121–L122）：接收`raw`。 调用`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`。 返回路径：L122的`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()`。
- `recipe_identity`（L125–L128）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha256`、`(ROOT / name).read_bytes`、`json.dumps(hashes, sort_keys=True).encode`、`json.dumps`。 返回路径：L128的`identity, hashes`。
- `profile_directory`（L131–L135）：接收`directory`。 控制顺序：L133按`directory == local.HOME.resolve()`分支；L134抛异常，停止当前正常路径。 调用`Path(directory).resolve`、`Path`、`local.HOME.resolve`、`ValueError`。 返回路径：L135的`directory`。
- `read_base`（L138–L156）：接收`directory`。 控制顺序：L143按`installation != { "source_sha": DAYTONA_SOURCE, "release": "v" + DAYTONA_VERSION, "de…`分支；L149抛异常，停止当前正常路径；L150遍历`config["services"].items()`；L153按`service["image"] != expected or record["tag"] != local.IMAGES[name]`分支；L154抛异常，停止当前正常路径。 调用`yaml.safe_load`、`(directory / "compose.lock.yaml").read_text`、`local.assert_local_compose`、`json.loads`、`(directory / "images.lock.json").read_text`、`(directory / "installation.json").read_text`、`ValueError`、`config["services"].items`、`record.get`等。 返回路径：L156的`config`。
- `source_context`（L159–L214）：接收`directory`、`context`。 源码说明：Export committed source only; reject drift before applying the exact patch.。 控制顺序：L162按`DAYTONA_SOURCE != PINNED_SOURCE or DAYTONA_VERSION != "0.190.0"`分支；L163抛异常，停止当前正常路径；L167按`blob(raw) != SOURCE_BLOB or raw.count(OLD.encode()) != 1`分支；L168抛异常，停止当前正常路径；L169按`blob((context / "go.work").read_bytes()) != WORKSPACE_BLOB`分支；L170抛异常，停止当前正常路径；L172按`updated.count(LIMIT_ANCHOR) != 1`分支；L173抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`ValueError`、`export_source`、`target.read_bytes`、`blob`、`raw.count`、`OLD.encode`、`(context / "go.work").read_bytes`、`raw.decode().replace`等。 返回路径：L210的`{ "source_sha": DAYTONA_SOURCE, "go_inputs": inputs, "patched_sha256": sha256(updated), }`。
- `download_assets`（L217–L224）：接收`context`。 控制顺序：L219遍历`ASSETS.items()`；L222按`len(raw) > 1_000_000 or sha256(raw) != expected`分支；L223抛异常，停止当前正常路径。 调用`urllib.request.build_opener`、`urllib.request.ProxyHandler`、`ASSETS.items`、`opener.open`、`response.read`、`len`、`sha256`、`ValueError`、`(Path(context) / "apps/daemon/pkg/terminal/static" / name).write_…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `inspect_image`（L227–L234）：接收`reference`。 控制顺序：L229按`len(rows) != 1 or not re.fullmatch(r"sha256:[a-f0-9]{64}", rows[0].get("Id", ""))`分支；L230抛异常，停止当前正常路径；L232按`image.get("Os") != "linux" or image.get("Architecture") != "amd64"`分支；L233抛异常，停止当前正常路径。 调用`json.loads`、`local.docker`、`len`、`re.fullmatch`、`rows[0].get`、`ValueError`、`image.get`。 返回路径：L234的`image`。
- `resolve_bases`（L237–L247）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L239遍历`BASES.items()`；L244按`len(digests) != 1 or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", digests[0]…`分支；L245抛异常，停止当前正常路径。 调用`BASES.items`、`local.docker`、`inspect_image`、`tag.rsplit`、`image.get`、`value.startswith`、`len`、`re.fullmatch`、`re.escape`等。 返回路径：L247的`result`。
- `build_image`（L250–L273）：接收`directory`、`context`、`recipe`、`tag`、`bases`、`identity`。 控制顺序：L252遍历`bases.items()`。 调用`bases.items`、`str`、`local.docker`、`(directory / (recipe + ".log")).write_text`、`inspect_image`、`validate_image`。 返回路径：L273的`image`。
- `validate_image`（L276–L296）：接收`image`、`identity`、`snapshot`。 控制顺序：L279按`labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE or labels.get("rnd.…`分支；L284抛异常，停止当前正常路径；L285按`snapshot`分支；L286按`config.get("User") != "0:0" or config.get("WorkingDir") != CONTROL_WORKDIR or config.…`分支；L292抛异常，停止当前正常路径；L295按`"USE_SNAPSHOT_ENTRYPOINT=false" not in config.get("Env", [])`分支；L296抛异常，停止当前正常路径。 调用`image.get`、`config.get`、`labels.get`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `render_profile`（L299–L306）：接收`base`、`runner_id`、`image`。 调用`copy.deepcopy`、`local.assert_local_compose`。 返回路径：L306的`config`。
- `write_compose`（L309–L312）：接收`path`、`config`。 控制顺序：L311按`os.name != "nt"`分支。 调用`path.write_text`、`yaml.safe_dump`、`path.chmod`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare_dependency_context`（L315–L340）：接收`context`、`identity`。 控制顺序：L318遍历`("pyproject.toml", "uv.lock")`；L325遍历`("image", "build")`。 调用`Path`、`(ROOT / "templates/product" / name).read_bytes`、`(context / name).write_bytes`、`sha256`、`dependencies.validate_python`、`(context / "pyproject.toml").read_bytes`、`(context / "uv.lock").read_bytes`、`shutil.copyfile`、`(context / "dependency-inputs.json").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `inspect_dependency_manifest`（L343–L395）：接收`image_id`、`profile`、`descriptors`。 控制顺序：L344按`not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id)`分支；L345抛异常，停止当前正常路径；L367按`not isinstance(result, dict) or set(result) != { "schema", "profile", "manifest_sha25…`分支；L394抛异常，停止当前正常路径。 调用`re.fullmatch`、`ValueError`、`local.docker`、`json.loads`、`isinstance`、`set`、`type`、`result.get`、`dependencies.native_descriptor_roles`等。 返回路径：L395的`{**result, "image_id": image_id}`。
- `validate_dependency_binding`（L398–L427）：接收`value`、`image_id`、`profile`、`descriptors`。 控制顺序：L399按`not isinstance(value, dict) or set(value) != { "schema", "profile", "image_id", "mani…`分支；L427抛异常，停止当前正常路径。 调用`isinstance`、`set`、`type`、`value.get`、`dependencies.native_descriptor_roles`、`dependencies.native_descriptor_roles().values`、`any`、`re.fullmatch`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_dependency_manifest`（L430–L438）：接收`record`、`profile`、`descriptors`。 控制顺序：L436按`image.get("dependency_manifest") != expected`分支；L437抛异常，停止当前正常路径。 调用`validate_dependency_binding`、`image.get`、`inspect_dependency_manifest`、`ValueError`。 返回路径：L438的`expected`。
- `prepare`（L441–L573）：接收`directory`。 控制顺序：L444遍历`(COMPOSE, LOCK, "snapshot-image.json", "api-key.json", "workbench…`；L445按`(directory / name).exists()`分支；L446抛异常，停止当前正常路径；L450按`info.get("OSType") != "linux" or info.get("Architecture") not in { "amd64", "x86_64",…`分支；L454抛异常，停止当前正常路径；L465按`existing.strip()`分支；L466抛异常，停止当前正常路径；L474按`stamp == local.snapshot_stamp()`分支。后续分支沿下方源码相同行号继续阅读。 调用`profile_directory`、`read_base`、`(directory / name).exists`、`ValueError`、`json.loads`、`local.docker`、`info.get`、`str`、`existing.strip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_profile`（L576–L638）：接收`directory`。 控制顺序：L580按`record.get("profile") != PROFILE or record.get("recipe_identity") != identity or reco…`分支；L588抛异常，停止当前正常路径；L590按`set(bases) != set(BASES)`分支；L591抛异常，停止当前正常路径；L592遍历`BASES.items()`；L595按`entry.get("tag") != tag or not re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", entr…`分支；L600抛异常，停止当前正常路径；L603按`image.get("source_hash") != stamp or image.get("image") != "registry:6000/rnd-python:…`分支。后续分支沿下方源码相同行号继续阅读。 调用`profile_directory`、`json.loads`、`(directory / LOCK).read_text`、`recipe_identity`、`record.get`、`record.get("source", {}).get`、`sha256`、`(directory / "compose.lock.yaml").read_bytes`、`ValueError`等。 返回路径：L638的`config, record`。
- `compose`（L641–L651）：接收`directory`、`timeout`、`*args`。 调用`load_profile`、`local.docker`、`str`、`Path`。 返回路径：L643的`local.docker( "compose", "--project-name", PROJECT, "--file", str(Path(directory) / COMPOS…`。
- `require_profile`（L654–L676）：接收`directory`、`snapshot`。 源码说明：Read-only prerequisite check; never a substitute for the isolation receipt.。 控制顺序：L657按`snapshot is not None and snapshot != record["snapshot"]["snapshot"]`分支；L658抛异常，停止当前正常路径；L664按`image["Id"] != record["snapshot"]["image_id"] or expected_digest not in image.get( "R…`分支；L667抛异常，停止当前正常路径。 调用`load_profile`、`ValueError`、`inspect_image`、`validate_image`、`record["snapshot"]["digest"].replace`、`image.get`、`require_dependency_manifest`、`sha256`、`(ROOT / "templates/product" / name).read_bytes`。 返回路径：L676的`record`。
- `require_execution_resources`（L679–L728）：接收`host`、`native`。 源码说明：Production source needs enforced limits, not API-requested resources. Landlock confines candidate writes to the explicitly sized tmpfs. This does not depend on the host's XFS/overlay project-quota con。 控制顺序：L692按`type(memory) is not int or not 0 < memory <= memory_limit or type(swap) is not int or…`分支；L706抛异常，停止当前正常路径。 调用`host.get`、`type`、`isinstance`、`ContainerInspectionRejected`、`set`。 返回路径：L721的`{ "cpu_period": period, "cpu_quota": quota, "memory": memory, "memory_swap": swap, "tmpfs_…`。
- `require_native_shared_memory`（L731–L746）：接收`host`。 源码说明：Bind native execution to Docker's private, fixed-size default shm mount.。 控制顺序：L737按`not ipc_private or not size_matches`分支；L738抛异常，停止当前正常路径。 调用`host.get`、`type`、`ContainerInspectionRejected`。 返回路径：L746的`{"ipc_mode": "private", "size_bytes": NATIVE_SHARED_MEMORY_BYTES}`。

</details>

**创建路径：** `scripts/daytona_capability_profile.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L748。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`30273`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_capability_profile.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "2d6d3e1db120711d9e894537d01bc753aa260481a44faad3ec4f549320237117"} -->
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

from scripts import daytona_dependency_build as dependencies
from scripts import daytona_local as local
from scripts.daytona_build import BUILT, export_source, require_api_image
from workbench.capability_isolation import ContainerInspectionRejected
from workbench.local_only import DAYTONA_SOURCE, DAYTONA_VERSION
from workbench.settings import ROOT

HOME = ROOT / ".data/daytona-capability"
PROJECT = "rnd-daytona-capability"
PROFILE = "fixed-authored-sqlite-v1"
PINNED_SOURCE = "01c502bb1f1ff8f2885d0cd490e043736083dca8"
COMPOSE = "compose.capability.lock.yaml"
LOCK = "capability-profile.lock.json"
CONTROL_WORKDIR = "/opt/rnd/control"
NATIVE_SHARED_MEMORY_BYTES = 67108864
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
LIMIT_ANCHOR = "\tcontainerRuntime := config.GetContainerRuntime()"
LIMIT_INSERT = """\t// Custom-source executions get bounded writable storage on ordinary runners.
\t// Root control remains distinct; Landlock confines every product write here.
\tif strings.HasPrefix(sandboxDto.Name, "rnd-source-") {
\t\t// Bind the primary mode to the same sole bridge checked before source admission.
\t\thostConfig.NetworkMode = container.NetworkMode("runner-bridge")
\t\t// The local upstream disables ordinary quotas; custom source cannot inherit that.
\t\thostConfig.CPUPeriod = 100000
\t\thostConfig.CPUQuota = 100000
\t\thostConfig.Memory = 2 * 1024 * 1024 * 1024
\t\tpidLimit := int64(256)
\t\thostConfig.PidsLimit = &pidLimit
\t\thostConfig.Tmpfs = map[string]string{"/tmp": "rw,nosuid,nodev,size=1073741824,mode=1777"}
\t\tif strings.HasPrefix(sandboxDto.Name, "rnd-source-native-") {
\t\t\thostConfig.IpcMode = container.IpcMode("private")
\t\t\thostConfig.ShmSize = 67108864
\t\t\thostConfig.CPUQuota = 200000
\t\t\thostConfig.Memory = 6 * 1024 * 1024 * 1024
\t\t\tpidLimit = 384
\t\t\thostConfig.Tmpfs = map[string]string{"/tmp": "rw,nosuid,nodev,size=4294967296,mode=1777"}
\t\t}
\t\thostConfig.MemorySwap = hostConfig.Memory
\t}
"""
RECIPE_PATHS = (
    "scripts/daytona_capability_profile.py",
    "scripts/daytona_dependency_image.py",
    "scripts/daytona_dependency_build.py",
    "scripts/daytona_dependency_build.lock.json",
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
    "RUST_IMAGE": "rust:1.85.1-bookworm",
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
    require_api_image(records.get("api"), local.docker)
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
    if updated.count(LIMIT_ANCHOR) != 1:
        raise ValueError("Pinned Runner custom-source resource anchor changed")
    updated = updated.replace(LIMIT_ANCHOR, LIMIT_INSERT + LIMIT_ANCHOR, 1)
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
    return {
        "source_sha": DAYTONA_SOURCE,
        "go_inputs": inputs,
        "patched_sha256": sha256(updated),
    }


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


def prepare_dependency_context(context, identity):
    context = Path(context)
    descriptors = {}
    for name in ("pyproject.toml", "uv.lock"):
        raw = (ROOT / "templates/product" / name).read_bytes()
        (context / name).write_bytes(raw)
        descriptors[name] = sha256(raw)
    dependencies.validate_python(
        (context / "pyproject.toml").read_bytes(), (context / "uv.lock").read_bytes()
    )
    for name in ("image", "build"):
        shutil.copyfile(
            ROOT / f"scripts/daytona_dependency_{name}.py",
            context / f"dependency-{name}.py",
        )
    (context / "dependency-inputs.json").write_text(
        json.dumps(
            {
                "recipe_identity": identity,
                "original_descriptors": descriptors,
                "normalized_descriptors": descriptors,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def inspect_dependency_manifest(image_id, profile, descriptors):
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
        raise ValueError("Dependency inventory requires an immutable image ID")
    raw = local.docker(
        "run",
        "--rm",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--user=65534:65534",
        "--pids-limit=64",
        "--memory=512m",
        "--entrypoint=/usr/bin/python3",
        image_id,
        "-I",
        "-S",
        "/opt/rnd/bin/dependency-image.py",
        "inspect",
        "--profile",
        profile,
        timeout=300,
    )
    result = json.loads(raw)
    if (
        not isinstance(result, dict)
        or set(result)
        != {
            "schema",
            "profile",
            "manifest_sha256",
            "installed_tree_sha256",
            "original_descriptors",
        }
        | ({"descriptor_roles"} if profile == "fastapiadmin" else set())
        or type(result.get("schema")) is not int
        or result.get("schema") != 1
        or result.get("profile") != profile
        or result.get("original_descriptors") != descriptors
        or profile == "fastapiadmin"
        and (
            result.get("descriptor_roles") != dependencies.native_descriptor_roles()
            or set(descriptors)
            != {name for paths in dependencies.native_descriptor_roles().values() for name in paths}
        )
        or any(
            not isinstance(result.get(name), str)
            or not re.fullmatch(r"[a-f0-9]{64}", result.get(name, ""))
            for name in ("manifest_sha256", "installed_tree_sha256")
        )
    ):
        raise ValueError("Image dependency manifest does not match exact descriptor inputs")
    return {**result, "image_id": image_id}


def validate_dependency_binding(value, image_id, profile, descriptors):
    if (
        not isinstance(value, dict)
        or set(value)
        != {
            "schema",
            "profile",
            "image_id",
            "manifest_sha256",
            "installed_tree_sha256",
            "original_descriptors",
        }
        | ({"descriptor_roles"} if profile == "fastapiadmin" else set())
        or type(value.get("schema")) is not int
        or value.get("schema") != 1
        or value.get("profile") != profile
        or value.get("image_id") != image_id
        or value.get("original_descriptors") != descriptors
        or profile == "fastapiadmin"
        and (
            value.get("descriptor_roles") != dependencies.native_descriptor_roles()
            or set(descriptors)
            != {name for paths in dependencies.native_descriptor_roles().values() for name in paths}
        )
        or any(
            not isinstance(value.get(name), str) or not re.fullmatch(r"[a-f0-9]{64}", value[name])
            for name in ("manifest_sha256", "installed_tree_sha256")
        )
    ):
        raise ValueError("Dependency manifest lock lacks exact image/descriptor binding")


def require_dependency_manifest(record, profile, descriptors):
    image = record["snapshot"]
    validate_dependency_binding(
        image.get("dependency_manifest"), image["image_id"], profile, descriptors
    )
    expected = inspect_dependency_manifest(image["image_id"], profile, descriptors)
    if image.get("dependency_manifest") != expected:
        raise ValueError("Dependency manifest is not bound to the immutable profile image")
    return expected


def prepare(directory=HOME):
    directory = profile_directory(directory)
    base = read_base(directory)
    for name in (COMPOSE, LOCK, "snapshot-image.json", "api-key.json", "workbench.env"):
        if (directory / name).exists():
            raise ValueError(
                "Profile setup requires fresh local state; will not overwrite: " + name
            )
    info = json.loads(local.docker("info", "--format", "{{json .}}"))
    if info.get("OSType") != "linux" or info.get("Architecture") not in {
        "amd64",
        "x86_64",
    }:
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
            directory,
            context,
            "capability-runner.Dockerfile",
            runner_tag,
            bases,
            identity,
        )
    with tempfile.TemporaryDirectory(prefix="capability-snapshot-", dir=directory) as temporary:
        context = Path(temporary)
        prepare_dependency_context(context, identity)
        snapshot = build_image(
            directory,
            context,
            "capability-snapshot.Dockerfile",
            snapshot_tag,
            bases,
            identity,
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
    record["snapshot"]["dependency_manifest"] = inspect_dependency_manifest(
        snapshot["Id"],
        "python-basic",
        {
            name: sha256((ROOT / "templates/product" / name).read_bytes())
            for name in ("pyproject.toml", "uv.lock")
        },
    )
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
    validate_dependency_binding(
        image.get("dependency_manifest"),
        image["image_id"],
        "python-basic",
        {
            name: sha256((ROOT / "templates/product" / name).read_bytes())
            for name in ("pyproject.toml", "uv.lock")
        },
    )
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
    require_dependency_manifest(
        record,
        "python-basic",
        {
            name: sha256((ROOT / "templates/product" / name).read_bytes())
            for name in ("pyproject.toml", "uv.lock")
        },
    )
    return record


def require_execution_resources(host, *, native=False):
    """Production source needs enforced limits, not API-requested resources.

        Landlock confines candidate writes to the explicitly sized tmpfs. This
        does not depend on the host's XFS/overlay project-quota configuration.
    This never changes the user's daemon, disks or container settings.
    """
    memory, swap = host.get("Memory"), host.get("MemorySwap")
    period, quota = host.get("CpuPeriod"), host.get("CpuQuota")
    storage = host.get("Tmpfs", {})
    memory_limit = (6 if native else 2) * 1024**3
    tmpfs_bytes = 4294967296 if native else 1073741824
    pids = 384 if native else 256
    if (
        type(memory) is not int
        or not 0 < memory <= memory_limit
        or type(swap) is not int
        or swap != memory
        or type(period) is not int
        or not 0 < period <= 1000000
        or type(quota) is not int
        or not 0 < quota <= period * (2 if native else 1)
        or not isinstance(storage, dict)
        or storage != {"/tmp": f"rw,nosuid,nodev,size={tmpfs_bytes},mode=1777"}
        or type(host.get("PidsLimit")) is not int
        or host["PidsLimit"] != pids
    ):
        raise ContainerInspectionRejected(
            "Custom source requires actual bounded CPU, memory, swap and storage quota",
            category="resource_limits",
            facts={
                "native_resources": native,
                "memory": memory,
                "memory_swap": swap,
                "cpu_period": period,
                "cpu_quota": quota,
                "pids_limit": host.get("PidsLimit"),
                "tmpfs_keys_match": isinstance(storage, dict) and set(storage) == {"/tmp"},
                "tmpfs_options_match": storage
                == {"/tmp": f"rw,nosuid,nodev,size={tmpfs_bytes},mode=1777"},
            },
        )
    return {
        "cpu_period": period,
        "cpu_quota": quota,
        "memory": memory,
        "memory_swap": swap,
        "tmpfs_bytes": tmpfs_bytes,
        "pids": pids,
    }


def require_native_shared_memory(host):
    """Bind native execution to Docker's private, fixed-size default shm mount."""
    ipc_private = host.get("IpcMode") == "private"
    size_matches = (
        type(host.get("ShmSize")) is int and host["ShmSize"] == NATIVE_SHARED_MEMORY_BYTES
    )
    if not ipc_private or not size_matches:
        raise ContainerInspectionRejected(
            "Native source requires exact private IPC and 64 MiB shared memory",
            category="shared_memory",
            facts={
                "shared_memory_ipc_private": ipc_private,
                "shared_memory_size_match": size_matches,
            },
        )
    return {"ipc_mode": "private", "size_bytes": NATIVE_SHARED_MEMORY_BYTES}


````
