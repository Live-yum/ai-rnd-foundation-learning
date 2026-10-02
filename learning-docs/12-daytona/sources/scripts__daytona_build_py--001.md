# scripts/daytona_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从固定来源构建并锁定本机镜像。** 验证源码Git对象、Runner发布字节与许可证，在干净构建上下文编译控制面和存储，记录不可变镜像身份；不猜测latest标签或切换云端服务。

**对应关系：** daytona_local images → Docker本机构建 → images.lock/compose.lock。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.local_only`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `local_tag`（L34–L39）：接收`service`。 控制顺序：L35按`service == "minio"`分支；L37按`service not in BUILT`分支；L38抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L36的`f"rnd-local/minio:{MINIO_RELEASE}-{MINIO_SOURCE[:12]}"`；L39的`f"rnd-local/daytona-{service}:{DAYTONA_VERSION}-{DAYTONA_SOURCE[:12]}"`。
- `recipe`（L42–L52）：接收`service`、`source`。先验证上游Dockerfile完整前像的Git对象哈希，再加入禁用云构建、远程缓存和遥测的环境变量；不匹配即停止。 源码说明：Verify the complete upstream preimage before disabling hosted build caches.。 控制顺序：L47按`identity != expected`分支；L48抛异常，停止当前正常路径；L50按`"ENV CI=true\n" not in text`分支；L51抛异常，停止当前正常路径。 调用`(Path(source) / f"apps/{service}/Dockerfile").read_bytes`、`Path`、`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`、`ValueError`、`raw.decode`等。 返回路径：L52的`target, text.replace("ENV CI=true\n", "ENV CI=true\n" + BUILD_ENV)`。
- `download_runner`（L55–L81）：接收`destination`。发布文件大小与SHA256固定写在源码中，下载时逐块累计、校验通过才原子落盘；已有损坏文件不能执行。 源码说明：The expected hash is committed, not trusted from a newly downloaded manifest.。 控制顺序：L58按`destination.exists()`分支；L61按`destination.stat().st_size == RUNNER_BYTES and valid`分支；L63抛异常，停止当前正常路径；L70在`block := response.read(1024 * 1024)`成立时循环；L72按`total > RUNNER_BYTES`分支；L73抛异常，停止当前正常路径；L76按`total != RUNNER_BYTES or digest.hexdigest() != RUNNER_SHA256`分支；L77抛异常，停止当前正常路径。 调用`Path`、`destination.exists`、`destination.open`、`hashlib.file_digest(existing, "sha256").hexdigest`、`hashlib.file_digest`、`destination.stat`、`ValueError`、`destination.with_suffix`、`urllib.request.build_opener`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `export_source`（L84–L104）：接收`directory`、`command`、`context`、`revision`、`source_name`。 源码说明：Git archive excludes untracked files, local .env and .git credentials.。 控制顺序：L89按`command(["git", "rev-parse", "HEAD"], cwd=source) != revision`分支；L90抛异常，停止当前正常路径；L102按`source_name == "upstream"`分支。 调用`Path`、`command`、`ValueError`、`str`、`tarfile.open`、`stream.extractall`、`archive.unlink`、`(context / "go.work.sum").touch`。 返回路径：L104的`context`。
- `build_images`（L107–L116）：接收`directory`、`command`、`docker`。确认Docker是本机Linux x86_64后，从固定Git对象导出临时上下文；构建在本机进行，返回可审计的镜像ID与来源哈希。 源码说明：All builds execute on the explicitly selected local Docker daemon.。 控制顺序：L111按`info.get("OSType") != "linux" or info.get("Architecture") not in {"x86_64", "amd64"}`分支；L112抛异常，停止当前正常路径。 调用`Path(directory).resolve`、`Path`、`json.loads`、`docker`、`info.get`、`ValueError`、`build_storage`、`tempfile.TemporaryDirectory`、`export_source`等。 返回路径：L116的`{"minio": storage, **build_exported(directory, context, docker)}`。
- `build_exported`（L119–L178）：接收`directory`、`context`、`docker`。 控制顺序：L130遍历`("api", "proxy", "runner")`；L131按`service in SOURCE_RECIPES`分支；L165按`labels.get("org.opencontainers.image.revision") != DAYTONA_SOURCE or labels.get("org.…`分支；L169抛异常，停止当前正常路径；L176按`service == "runner"`分支。 调用`recipes.mkdir`、`runner_context.mkdir`、`download_runner`、`(runner_context / "runner-entry.sh").write_bytes`、`(ROOT / "tools/daytona/runner-entry.sh").read_bytes`、`recipe`、`dockerfile.write_text`、`run_command`、`str`等。 返回路径：L178的`metadata`。
- `build_storage`（L181–L242）：接收`directory`、`command`、`docker`。从MinIO独立的固定提交导出干净源码，在本机编译对象存储，镜像附上对应源码与许可证；返回来源指纹而不是信任可变的在线镜像标签。 源码说明：Build the local object store from its own fixed release, not a mutable image.。 控制顺序：L184按`not source.exists()`分支；L231按`labels.get("org.opencontainers.image.revision") != MINIO_SOURCE or labels.get("org.op…`分支；L235抛异常，停止当前正常路径。 调用`source.exists`、`source.mkdir`、`command`、`tempfile.TemporaryDirectory`、`export_source`、`str`、`run_command`、`local_tag`、`(directory / "minio-build.log").write_text`等。 返回路径：L236的`{ "tag": local_tag("minio"), "image_id": image["Id"], "source_sha": MINIO_SOURCE, "release…`。

</details>

**创建路径：** `scripts/daytona_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L242。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10200`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fd5280c2312b9f38e00e92400d1e51fd43158ce4b1ee317e2765733acc2bf7a8"} -->
````python
# scripts/daytona_build.py
"""Build v0.190.0 locally; no hosted builder, mutable release fallback or credentials.

API/Proxy use verified Dockerfiles from the fixed Git revision. Runner embeds the
SHA-256-verified official binary from the SAME release (which includes its daemon).
Only installation downloads public dependencies. Runtime never uses these URLs.
"""

import hashlib
import json
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
