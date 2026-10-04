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
