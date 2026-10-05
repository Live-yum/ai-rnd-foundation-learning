# scripts/daytona_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从固定来源构建并锁定本机镜像。** 验证源码Git对象、Runner发布字节与许可证，在干净构建上下文编译控制面和存储；API摘要分隔符修复只匹配固定源码blob及完整补丁，镜像标签和锁记录补丁与修改后源码SHA256。运行准入核对当前来源及实际API镜像ID/标签，拒绝旧锁或漂移，不猜测latest标签或切换云端服务。

**对应关系：** daytona_local images → Docker本机构建 → images.lock/compose.lock。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.local_only`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `local_tag`（L47–L52）：接收`service`。 控制顺序：L48按`service == "minio"`分支；L50按`service not in BUILT`分支；L51抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L49的`f"rnd-local/minio:{MINIO_RELEASE}-{MINIO_SOURCE[:12]}"`；L52的`f"rnd-local/daytona-{service}:{DAYTONA_VERSION}-{DAYTONA_SOURCE[:12]}"`。
- `recipe`（L55–L65）：接收`service`、`source`。先验证上游Dockerfile完整前像的Git对象哈希，再加入禁用云构建、远程缓存和遥测的环境变量；不匹配即停止。 源码说明：Verify the complete upstream preimage before disabling hosted build caches.。 控制顺序：L60按`identity != expected`分支；L61抛异常，停止当前正常路径；L63按`"ENV CI=true\n" not in text`分支；L64抛异常，停止当前正常路径。 调用`(Path(source) / f"apps/{service}/Dockerfile").read_bytes`、`Path`、`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`、`ValueError`、`raw.decode`等。 返回路径：L65的`target, text.replace("ENV CI=true\n", "ENV CI=true\n" + BUILD_ENV)`。
- `api_patch_identity`（L68–L79）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：The current reviewed API provenance, also required by runtime lock readers.。 控制顺序：L70按`DAYTONA_SOURCE != API_PATCH_SOURCE or DAYTONA_VERSION != "0.190.0"`分支；L71抛异常，停止当前正常路径；L72按`hashlib.sha256((ROOT / API_IMAGE_PATCH).read_bytes()).hexdigest() != API_IMAGE_PATCH_…`分支；L73抛异常，停止当前正常路径。 调用`ValueError`、`hashlib.sha256((ROOT / API_IMAGE_PATCH).read_bytes()).hexdigest`、`hashlib.sha256`、`(ROOT / API_IMAGE_PATCH).read_bytes`。 返回路径：L74的`{ "path": API_IMAGE_FILE, "preimage_blob": API_IMAGE_BLOB, "patched_sha256": API_IMAGE_PAT…`。
- `api_patch_labels`（L82–L86）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L83的`{ "rnd.daytona.api-source-sha256": API_IMAGE_PATCHED_SHA256, "rnd.daytona.api-patch-sha256…`。
- `require_api_image`（L89–L113）：接收`record`、`docker`。 源码说明：Reject old/tampered locks and inspect the exact API ID before service admission.。 控制顺序：L92按`type(record) is not dict or record.get("source_patch") != expected or record.get("sou…`分支；L99抛异常，停止当前正常路径；L101按`type(inspected) is not list or len(inspected) != 1 or type(inspected[0]) is not dict`分支；L102抛异常，停止当前正常路径；L105按`image.get("Id") != record["image_id"] or any( labels.get(key) != value for key, value…`分支；L113抛异常，停止当前正常路径。 调用`api_patch_identity`、`type`、`record.get`、`local_tag`、`re.fullmatch`、`str`、`ValueError`、`json.loads`、`docker`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `patch_api_image_reference`（L116–L140）：接收`source`。 源码说明：Preserve immutable digest separators in the pinned API's exported source only.。 控制顺序：L122按`identity != API_IMAGE_BLOB or raw.count(API_IMAGE_OLD.encode()) != 1`分支；L123抛异常，停止当前正常路径；L134按`patch != expected_patch or hashlib.sha256(updated.encode()).hexdigest() != expected["…`分支；L138抛异常，停止当前正常路径。 调用`api_patch_identity`、`Path`、`target.read_bytes`、`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`、`raw.count`等。 返回路径：L140的`expected`。
- `download_runner`（L143–L169）：接收`destination`。发布文件大小与SHA256固定写在源码中，下载时逐块累计、校验通过才原子落盘；已有损坏文件不能执行。 源码说明：The expected hash is committed, not trusted from a newly downloaded manifest.。 控制顺序：L146按`destination.exists()`分支；L149按`destination.stat().st_size == RUNNER_BYTES and valid`分支；L151抛异常，停止当前正常路径；L158在`block := response.read(1024 * 1024)`成立时循环；L160按`total > RUNNER_BYTES`分支；L161抛异常，停止当前正常路径；L164按`total != RUNNER_BYTES or digest.hexdigest() != RUNNER_SHA256`分支；L165抛异常，停止当前正常路径。 调用`Path`、`destination.exists`、`destination.open`、`hashlib.file_digest(existing, "sha256").hexdigest`、`hashlib.file_digest`、`destination.stat`、`ValueError`、`destination.with_suffix`、`urllib.request.build_opener`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `export_source`（L172–L192）：接收`directory`、`command`、`context`、`revision`、`source_name`。 源码说明：Git archive excludes untracked files, local .env and .git credentials.。 控制顺序：L177按`command(["git", "rev-parse", "HEAD"], cwd=source) != revision`分支；L178抛异常，停止当前正常路径；L190按`source_name == "upstream"`分支。 调用`Path`、`command`、`ValueError`、`str`、`tarfile.open`、`stream.extractall`、`archive.unlink`、`(context / "go.work.sum").touch`。 返回路径：L192的`context`。
- `build_images`（L195–L204）：接收`directory`、`command`、`docker`。确认Docker是本机Linux x86_64后，从固定Git对象导出临时上下文；构建在本机进行，返回可审计的镜像ID与来源哈希。 源码说明：All builds execute on the explicitly selected local Docker daemon.。 控制顺序：L199按`info.get("OSType") != "linux" or info.get("Architecture") not in {"x86_64", "amd64"}`分支；L200抛异常，停止当前正常路径。 调用`Path(directory).resolve`、`Path`、`json.loads`、`docker`、`info.get`、`ValueError`、`build_storage`、`tempfile.TemporaryDirectory`、`export_source`等。 返回路径：L204的`{"minio": storage, **build_exported(directory, context, docker)}`。
- `build_exported`（L207–L277）：接收`directory`、`context`、`docker`。 控制顺序：L221遍历`("api", "proxy", "runner")`；L222按`service in SOURCE_RECIPES`分支；L261按`labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE or labels.get("org.…`分支；L266抛异常，停止当前正常路径；L273按`service == "runner"`分支；L275按`service == "api"`分支。 调用`patch_api_image_reference`、`recipes.mkdir`、`runner_context.mkdir`、`download_runner`、`(runner_context / "runner-entry.sh").write_bytes`、`(ROOT / "tools/daytona/runner-entry.sh").read_bytes`、`recipe`、`dockerfile.write_text`、`api_patch_labels`等。 返回路径：L277的`metadata`。
- `build_storage`（L280–L341）：接收`directory`、`command`、`docker`。从MinIO独立的固定提交导出干净源码，在本机编译对象存储，镜像附上对应源码与许可证；返回来源指纹而不是信任可变的在线镜像标签。 源码说明：Build the local object store from its own fixed release, not a mutable image.。 控制顺序：L283按`not source.exists()`分支；L330按`labels.get("org.opencontainers.image.revision") != MINIO_SOURCE or labels.get("org.op…`分支；L334抛异常，停止当前正常路径。 调用`source.exists`、`source.mkdir`、`command`、`tempfile.TemporaryDirectory`、`export_source`、`str`、`run_command`、`local_tag`、`(directory / "minio-build.log").write_text`等。 返回路径：L335的`{ "tag": local_tag("minio"), "image_id": image["Id"], "source_sha": MINIO_SOURCE, "release…`。

</details>

**创建路径：** `scripts/daytona_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L341。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14784`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b200039a1ba2e28c2b09da4434d614f9cdeb26a98e488ca8ea5adc317d2821a2"} -->
````python
# scripts/daytona_build.py
"""Build v0.190.0 locally; no hosted builder, mutable release fallback or credentials.

API/Proxy use verified Dockerfiles from the fixed Git revision. Runner embeds the
SHA-256-verified official binary from the SAME release (which includes its daemon).
Only installation downloads public dependencies. Runtime never uses these URLs.
"""

import difflib
import hashlib
import json
import re
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from workbench.local_only import DAYTONA_SOURCE, DAYTONA_VERSION
from workbench.settings import ROOT
from workbench.tools import run_command

BUILT = frozenset({"api", "proxy", "runner", "minio"})
MINIO_SOURCE = "9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a"
MINIO_RELEASE = "RELEASE.2025-10-15T17-29-55Z"
SOURCE_RECIPES = {
    "api": ("daytona", "2033dac0951f6e7aedb435824cfc1396959f8b5e"),
    "proxy": ("proxy", "bceb07f8bcad800fc5b32f0b2d6ebaab8c5b44f8"),
}
API_PATCH_SOURCE = "01c502bb1f1ff8f2885d0cd490e043736083dca8"
API_IMAGE_FILE = "apps/api/src/common/utils/docker-image.util.ts"
API_IMAGE_BLOB = "b0b03b28ce08b2865db9d2dc291c1745cb6492cf"
API_IMAGE_PATCH = "tools/daytona/api-digest-reference.patch"
API_IMAGE_PATCH_SHA256 = "d547f0e6dc75aea73b1fd907fd7cebe928d11782f18230ffec212c4cbc31a437"
API_IMAGE_PATCHED_SHA256 = "28a51752e5a1d12a6172723b27612b07917fd4612b49d48874dcc18a1b7736b9"
API_IMAGE_OLD = "      name = `${name}:${this.tag}`\n"
API_IMAGE_NEW = (
    "      const separator = this.tag.startsWith('sha256:') ? '@' : ':'\n"
    "      name = `${name}${separator}${this.tag}`\n"
)
RUNNER_SHA256 = "4265d2bb58ad6375b3c4c526ffa2bc2e1d197d94b92b431e532bf827c8f4dfa9"
RUNNER_BYTES = 156006775
BUILD_ENV = (
    "ENV NX_NO_CLOUD=true NX_SKIP_NX_CACHE=true NX_SKIP_REMOTE_CACHE=true "
    "NX_DAEMON=false DO_NOT_TRACK=1 OTEL_SDK_DISABLED=true\n"
)


def local_tag(service):
    if service == "minio":
        return f"rnd-local/minio:{MINIO_RELEASE}-{MINIO_SOURCE[:12]}"
    if service not in BUILT:
        raise ValueError("Unknown locally built Daytona service")
    return f"rnd-local/daytona-{service}:{DAYTONA_VERSION}-{DAYTONA_SOURCE[:12]}"


def recipe(service, source):
    """Verify the complete upstream preimage before disabling hosted build caches."""
    target, expected = SOURCE_RECIPES[service]
    raw = (Path(source) / f"apps/{service}/Dockerfile").read_bytes()
    identity = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if identity != expected:
        raise ValueError("固定Daytona构建文件不匹配，拒绝猜测适配：" + service)
    text = raw.decode("utf-8")
    if "ENV CI=true\n" not in text:
        raise ValueError("Daytona构建环境标记缺失")
    return target, text.replace("ENV CI=true\n", "ENV CI=true\n" + BUILD_ENV)


def api_patch_identity():
    """The current reviewed API provenance, also required by runtime lock readers."""
    if DAYTONA_SOURCE != API_PATCH_SOURCE or DAYTONA_VERSION != "0.190.0":
        raise ValueError("API digest patch requires its exact reviewed upstream revision")
    if hashlib.sha256((ROOT / API_IMAGE_PATCH).read_bytes()).hexdigest() != API_IMAGE_PATCH_SHA256:
        raise ValueError("API digest patch differs from its exact reviewed change")
    return {
        "path": API_IMAGE_FILE,
        "preimage_blob": API_IMAGE_BLOB,
        "patched_sha256": API_IMAGE_PATCHED_SHA256,
        "patch_sha256": API_IMAGE_PATCH_SHA256,
    }


def api_patch_labels():
    return {
        "rnd.daytona.api-source-sha256": API_IMAGE_PATCHED_SHA256,
        "rnd.daytona.api-patch-sha256": API_IMAGE_PATCH_SHA256,
    }


def require_api_image(record, docker):
    """Reject old/tampered locks and inspect the exact API ID before service admission."""
    expected = api_patch_identity()
    if (
        type(record) is not dict
        or record.get("source_patch") != expected
        or record.get("source_sha") != API_PATCH_SOURCE
        or record.get("tag") != local_tag("api")
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", str(record.get("image_id", "")))
    ):
        raise ValueError("API image lock lacks the exact current source patch provenance")
    inspected = json.loads(docker("image", "inspect", record["image_id"]))
    if type(inspected) is not list or len(inspected) != 1 or type(inspected[0]) is not dict:
        raise ValueError("API image inspection has no unique immutable image identity")
    image = inspected[0]
    labels = image.get("Config", {}).get("Labels") or {}
    if image.get("Id") != record["image_id"] or any(
        labels.get(key) != value
        for key, value in {
            "org.opencontainers.image.revision": API_PATCH_SOURCE,
            "org.opencontainers.image.version": DAYTONA_VERSION,
            **api_patch_labels(),
        }.items()
    ):
        raise ValueError("API image ID or labels differ from the exact current source patch")


def patch_api_image_reference(source):
    """Preserve immutable digest separators in the pinned API's exported source only."""
    expected = api_patch_identity()
    target = Path(source) / API_IMAGE_FILE
    raw = target.read_bytes()
    identity = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if identity != API_IMAGE_BLOB or raw.count(API_IMAGE_OLD.encode()) != 1:
        raise ValueError("Pinned API image reference source preimage does not match")
    updated = raw.decode("utf-8").replace(API_IMAGE_OLD, API_IMAGE_NEW)
    expected_patch = "".join(
        difflib.unified_diff(
            raw.decode("utf-8").splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile="a/" + API_IMAGE_FILE,
            tofile="b/" + API_IMAGE_FILE,
        )
    ).encode()
    patch = (ROOT / API_IMAGE_PATCH).read_bytes()
    if (
        patch != expected_patch
        or hashlib.sha256(updated.encode()).hexdigest() != expected["patched_sha256"]
    ):
        raise ValueError("API digest patch differs from its exact reviewed change")
    target.write_text(updated, encoding="utf-8", newline="\n")
    return expected


def download_runner(destination):
    """The expected hash is committed, not trusted from a newly downloaded manifest."""
    destination = Path(destination)
    if destination.exists():
        with destination.open("rb") as existing:
            valid = hashlib.file_digest(existing, "sha256").hexdigest() == RUNNER_SHA256
        if destination.stat().st_size == RUNNER_BYTES and valid:
            return
        raise ValueError("已有Runner文件校验失败；不执行、不静默覆盖")
    url = f"https://github.com/daytonaio/daytona/releases/download/v{DAYTONA_VERSION}/runner-amd64"
    temporary = destination.with_suffix(".partial")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    total, digest = 0, hashlib.sha256()
    try:
        with opener.open(url, timeout=120) as response, temporary.open("wb") as output:
            while block := response.read(1024 * 1024):
                total += len(block)
                if total > RUNNER_BYTES:
                    raise ValueError("Runner下载超过固定发布文件大小")
                digest.update(block)
                output.write(block)
        if total != RUNNER_BYTES or digest.hexdigest() != RUNNER_SHA256:
            raise ValueError("Runner发布文件SHA256不匹配；停止安装")
        temporary.replace(destination)
        destination.chmod(0o755)
    finally:
        temporary.unlink(missing_ok=True)


def export_source(directory, command, context, *, revision=None, source_name="upstream"):
    """Git archive excludes untracked files, local .env and .git credentials."""
    directory, context = Path(directory), Path(context)
    revision = revision or DAYTONA_SOURCE
    source = directory / source_name
    if command(["git", "rev-parse", "HEAD"], cwd=source) != revision:
        raise ValueError("固定Daytona源码SHA不匹配")
    archive = directory / "build-source.tar"
    command(
        ["git", "archive", "--format=tar", "--output=" + str(archive), revision],
        cwd=source,
    )
    try:
        with tarfile.open(archive) as stream:
            stream.extractall(context, filter="data")
    finally:
        archive.unlink(missing_ok=True)
    # Upstream release builds generate this workspace checksum file before Docker.
    if source_name == "upstream":
        (context / "go.work.sum").touch(exist_ok=True)
    return context


def build_images(directory, command, docker):
    """All builds execute on the explicitly selected local Docker daemon."""
    directory = Path(directory).resolve()
    info = json.loads(docker("info", "--format", "{{json .}}"))
    if info.get("OSType") != "linux" or info.get("Architecture") not in {"x86_64", "amd64"}:
        raise ValueError("固定Runner发布文件仅支持Linux x86_64；Windows请使用WSL2的x86_64 Docker")
    storage = build_storage(directory, command, docker)
    with tempfile.TemporaryDirectory(prefix="source-build-", dir=directory) as temporary:
        context = export_source(directory, command, temporary)
        return {"minio": storage, **build_exported(directory, context, docker)}


def build_exported(directory, context, docker):
    # Fail before any builds/downloads if the reviewed API source or patch drifted.
    # Never repair the request by substituting a mutable tag for its digest.
    api_patch = patch_api_image_reference(context)
    recipes = directory / "build-recipes"
    recipes.mkdir(exist_ok=True)
    runner_context = directory / "runner-context"
    runner_context.mkdir(exist_ok=True)
    download_runner(runner_context / "runner-amd64")
    (runner_context / "runner-entry.sh").write_bytes(
        (ROOT / "tools/daytona/runner-entry.sh").read_bytes()
    )
    runner_recipe = ROOT / "tools/daytona/runner.Dockerfile"
    metadata = {}
    for service in ("api", "proxy", "runner"):
        if service in SOURCE_RECIPES:
            target, text = recipe(service, context)
            dockerfile = recipes / (service + ".Dockerfile")
            dockerfile.write_text(text, encoding="utf-8", newline="\n")
            build_context = context
        else:
            target, dockerfile, build_context = "runner", runner_recipe, runner_context
        patch_labels = api_patch_labels() if service == "api" else {}
        label_args = [
            arg for key, value in patch_labels.items() for arg in ("--label", key + "=" + value)
        ]
        log = run_command(
            [
                "docker",
                "build",
                "--progress=plain",
                "--platform=linux/amd64",
                "--file",
                str(dockerfile),
                "--target",
                target,
                "--build-arg",
                "VERSION=" + DAYTONA_VERSION,
                "--label",
                "org.opencontainers.image.revision=" + DAYTONA_SOURCE,
                "--label",
                "org.opencontainers.image.version=" + DAYTONA_VERSION,
                *label_args,
                "--tag",
                local_tag(service),
                str(build_context),
            ],
            ROOT,
            timeout=2400,
            heartbeat="Local Daytona " + service,
        )
        (directory / (service + "-build.log")).write_text(log["log"], encoding="utf-8")
        details = json.loads(docker("image", "inspect", local_tag(service)))[0]
        labels = details.get("Config", {}).get("Labels") or {}
        if (
            labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE
            or labels.get("org.opencontainers.image.version") != DAYTONA_VERSION
            or any(labels.get(key) != value for key, value in patch_labels.items())
        ):
            raise ValueError("构建镜像缺少固定源码或版本标签：" + service)
        metadata[service] = {
            "tag": local_tag(service),
            "image_id": details["Id"],
            "source_sha": DAYTONA_SOURCE,
            "recipe_sha256": hashlib.sha256(dockerfile.read_bytes()).hexdigest(),
        }
        if service == "runner":
            metadata[service]["release_binary_sha256"] = RUNNER_SHA256
        if service == "api":
            metadata[service]["source_patch"] = api_patch
    return metadata


def build_storage(directory, command, docker):
    """Build the local object store from its own fixed release, not a mutable image."""
    source = directory / "upstream-minio"
    if not source.exists():
        source.mkdir()
        command(["git", "init", "--template=", "."], cwd=source)
        command(
            ["git", "fetch", "--depth", "1", "https://github.com/minio/minio.git", MINIO_SOURCE],
            cwd=source,
        )
        command(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=source)
    dockerfile = ROOT / "tools/daytona/minio.Dockerfile"
    with tempfile.TemporaryDirectory(prefix="storage-build-", dir=directory) as temporary:
        context = export_source(
            directory, command, temporary, revision=MINIO_SOURCE, source_name="upstream-minio"
        )
        # Include the exact corresponding source plus license in the locally built image.
        command(
            [
                "git",
                "archive",
                "--format=tar",
                "--output=" + str(context / "source.tar"),
                MINIO_SOURCE,
            ],
            cwd=source,
        )
        result = run_command(
            [
                "docker",
                "build",
                "--platform=linux/amd64",
                "--progress=plain",
                "--file",
                str(dockerfile),
                "--tag",
                local_tag("minio"),
                "--label",
                "org.opencontainers.image.revision=" + MINIO_SOURCE,
                "--label",
                "org.opencontainers.image.version=" + MINIO_RELEASE,
                str(context),
            ],
            ROOT,
            timeout=1800,
            heartbeat="Local MinIO build",
        )
    (directory / "minio-build.log").write_text(result["log"], encoding="utf-8")
    image = json.loads(docker("image", "inspect", local_tag("minio")))[0]
    labels = image.get("Config", {}).get("Labels") or {}
    if (
        labels.get("org.opencontainers.image.revision") != MINIO_SOURCE
        or labels.get("org.opencontainers.image.version") != MINIO_RELEASE
    ):
        raise ValueError("本机MinIO镜像来源标签不匹配")
    return {
        "tag": local_tag("minio"),
        "image_id": image["Id"],
        "source_sha": MINIO_SOURCE,
        "release": MINIO_RELEASE,
        "recipe_sha256": hashlib.sha256(dockerfile.read_bytes()).hexdigest(),
    }
````
