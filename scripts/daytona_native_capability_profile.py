"""Prepare/register the opt-in native profile without changing the base installation.

Only dependency descriptors reach the build context. Candidate source, frontend lifecycle hooks,
credentials and deployment control modules are never executed during preparation.
The warmed image is not runtime, browser, database or isolation acceptance evidence.
"""

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import SecretStr

from scripts import daytona_capability_profile as base
from scripts import daytona_dependency_build as dependencies
from scripts import daytona_local as local
from scripts.daytona_bootstrap import snapshot_named
from workbench.catalog import Selection
from workbench.daytona_profiles import dependency_identity
from workbench.domain import digest
from workbench.filesystem import files, inside, manifest, sha
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings
from workbench.tools import ToolFailure, run_command

HOME = base.HOME
PROFILE = "native-fastapiadmin-postgresql-v1"
LOCK = "native-fastapiadmin-profile.json"
ENVIRONMENT = "fastapiadmin.env"
FAMILY = "rnd-native-fastapiadmin"
RESOURCES = {"cpu": 2, "memory": 6, "disk": 30}
DOCKERFILE = "tools/daytona/capability-native-snapshot.Dockerfile"
RECIPE_PATHS = (
    "scripts/daytona_native_capability_profile.py",
    "scripts/daytona_dependency_image.py",
    "scripts/daytona_dependency_build.py",
    "scripts/daytona_dependency_build.lock.json",
    DOCKERFILE,
    # Record the matrix recipe lineage as well as the distinct safe warming recipe.
    "scripts/daytona_matrix_image.py",
    "tools/daytona/matrix.Dockerfile",
    "tools/daytona/warm.py",
    "workbench/daytona_profiles.py",
    "workbench/filesystem.py",
    "workbench/catalog.py",
    "workbench/template_adapters.py",
    "pyproject.toml",
    "uv.lock",
)
DESCRIPTORS = (
    "backend/pyproject.toml",
    "backend/uv.lock",
    "deployment/pyproject.toml",
    "deployment/uv.lock",
    "frontend/web/package.json",
    "frontend/web/pnpm-lock.yaml",
)
DIAGNOSTIC_SCAN_BYTES = 65536
DIAGNOSTIC_REPORT_BYTES = 4096
REVIEWED_DOCKERFILE_SHA256 = "1e9aa22679e06236a0c5f5cfbafe5fc2ff7f128f3f8e96aa38e398364e2bf5db"
DIAGNOSTIC_STAGES = {
    "prepare-profile-validation",
    "prepare-input-validation",
    "prepare-context",
    "prepare-docker-build",
    "prepare-image-validation",
    "prepare-registry-start",
    "prepare-image-push",
    "prepare-published-image-validation",
    "prepare-manifest-validation",
    "prepare-final-identity-validation",
    "prepare-readiness-write",
    "register-profile-validation",
    "register-worker-execution",
    "register-worker-profile-validation",
    "register-worker-credential-read",
    "register-worker-environment-validation",
    "register-worker-loopback-guard",
    "register-worker-client-create",
    "register-worker-snapshot-lookup",
    "register-worker-snapshot-create",
    "register-worker-snapshot-validation",
    "register-worker-client-close",
    "register-worker-final-identity-validation",
    "register-worker-environment-write",
}
REVIEWED_RUNS = (
    ("native-system", "system-packages"),
    ("native-system", "node-tooling"),
    ("dependency-builder", "build-system-packages"),
    ("dependency-builder", "fetch-native-sources"),
    ("dependency-builder", "seal-build-tools"),
    ("dependency-builder", "build-native-sources"),
    ("dependency-builder", "prepare-install-directories"),
    ("dependency-builder", "install-python-dependencies"),
    ("dependency-builder", "install-node-dependencies"),
    ("dependency-builder", "collect-dependency-metadata"),
    ("stage-3", "seal-runtime-image"),
)


def diagnostic_log(exc):
    """Inspect bounded subprocess output only; never stringify arbitrary errors."""
    if isinstance(exc, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
        streams = (exc.stdout, exc.stderr)
    elif isinstance(exc, ToolFailure):
        streams = (getattr(exc, "log", None),)
    else:
        streams = ()
    budget = DIAGNOSTIC_SCAN_BYTES // max(1, len(streams))
    chunks, truncated = [], False
    for value in streams:
        if type(value) not in (bytes, str):
            continue
        truncated |= len(value) > budget
        value = value[-budget:]
        raw = value.encode("utf-8", errors="replace") if type(value) is str else value
        truncated |= len(raw) > budget
        chunks.append(raw[-budget:])
    raw = b"".join(chunks)
    return raw.decode("utf-8", errors="replace"), len(raw), truncated


def reviewed_run_commands():
    """Match complete commands from the fixed reviewed recipe, never log text."""
    try:
        with (ROOT / DOCKERFILE).open("rb") as source:
            raw = source.read(DIAGNOSTIC_SCAN_BYTES + 1)
    except OSError:
        return {}
    if (
        len(raw) > DIAGNOSTIC_SCAN_BYTES
        or hashlib.sha256(raw).hexdigest() != REVIEWED_DOCKERFILE_SHA256
    ):
        return {}
    lines = raw.decode("utf-8").replace("\\\n", " ").splitlines()
    commands = [line.removeprefix("RUN ") for line in lines if line.startswith("RUN ")]
    if len(commands) != len(REVIEWED_RUNS):
        return {}
    return {
        (stage, normalized_run(command)): identifier
        for (stage, identifier), command in zip(REVIEWED_RUNS, commands, strict=True)
    }


def normalized_run(command):
    return " ".join(command.removeprefix("--network=none ").replace("\\\n", " ").split())


def build_failure_facts(text):
    """Return finite labels only, never captured paths, commands, versions or URLs."""
    commands = reviewed_run_commands()
    result = {"stage": "unknown", "run": "unknown", "categories": []}
    headers = {}
    for line in text.splitlines():
        match = re.fullmatch(r"#([0-9]{1,6}) \[([^\]]{1,64}) [0-9]+/[0-9]+\] RUN (.{1,4096})", line)
        if match:
            number, stage, command = match.groups()
            identifier = commands.get((stage, normalized_run(command)))
            if identifier:
                headers[number] = (stage, identifier)
        failed = re.match(r"#([0-9]{1,6}) ERROR:", line)
        if failed and failed[1] in headers:
            result["stage"], result["run"] = headers[failed[1]]
        footer = re.fullmatch(r"\s*> \[([^\]]{1,64}) [0-9]+/[0-9]+\] RUN (.{1,4096}):", line)
        if footer:
            stage, command = footer.groups()
            identifier = commands.get((stage, normalized_run(command)))
            if identifier:
                result["stage"], result["run"] = stage, identifier
        # BuildKit's terminal process error uses a quoted/escaped shell command.
        # Decode only that bounded string, then require a unique full recipe match.
        marker = 'process "'
        start = line.find(marker)
        end = line.rfind('" did not complete successfully: exit code: ')
        if start >= 0 and end > start and end - start <= 8192:
            try:
                process = json.loads(line[start + len("process ") : end + 1])
            except ValueError, UnicodeError:
                continue
            if type(process) is str and process.startswith("/bin/sh -c "):
                command = normalized_run(process.removeprefix("/bin/sh -c "))
                matches = [
                    (stage, run) for (stage, text), run in commands.items() if text == command
                ]
                if len(matches) == 1:
                    result["stage"], result["run"] = matches[0]
    lower = text.lower()
    permission = "permission denied" in lower or "os error 13" in lower
    signatures = {
        "permission-denied": permission,
        "cache-permission-denied": permission and "cache" in lower,
        "uv-cli-rejected": "unexpected argument" in lower and "usage: uv " in lower,
        "source-build-failed": result["run"] == "build-native-sources"
        and any(
            value in lower
            for value in ("failed to build", "build backend failed", "failed building wheel")
        ),
        "compiler-failed": "could not compile" in lower
        or bool(re.search(r"error: command .{0,128}(?:gcc|cc|clang).{0,128}failed", lower)),
        "rust-dependency-failed": "failed to get" in lower
        and "as a dependency of package" in lower,
        "python-version-unsupported": "configured python interpreter version" in lower
        and "newer than pyo3" in lower,
        "offline-dependency-missing": "offline" in lower
        and any(
            value in lower for value in ("no matching package named", "not found in the cache")
        ),
        "dependency-hash-mismatch": any(
            value in lower for value in ("hash mismatch", "checksum mismatch")
        ),
        "registry-fetch-failed": "failed to download" in lower or "failed to fetch" in lower,
        "node-install-failed": any(
            value in lower
            for value in ("err_pnpm_fetch_", "err_pnpm_offline_", "err_pnpm_outdated_lockfile")
        ),
        "image-seal-rejected": any(
            value in lower
            for value in (
                "dependency symlink escapes",
                "hardlinked dependency",
                "unsafe entry during dependency sealing",
                "dependency must be root-owned",
                "dependency is application-writable",
            )
        ),
    }
    result["categories"] = [name for name, matched in signatures.items() if matched] or ["unknown"]
    return result


def failure_diagnostic(progress, exc):
    code = getattr(exc, "returncode", None)
    code = code if type(code) is int and -(2**31) <= code < 2**31 else None
    timed_out = (
        isinstance(exc, subprocess.TimeoutExpired) or getattr(exc, "timed_out", None) is True
    )
    category = "unexpected"
    for error_type, label in (
        (subprocess.TimeoutExpired, "timeout"),
        (subprocess.CalledProcessError, "subprocess-exit"),
        (ToolFailure, "tool-exit"),
        (ValueError, "validation"),
        (OSError, "os-error"),
    ):
        if isinstance(exc, error_type):
            category = label
            break
    stage = progress.get("stage")
    stage = stage if type(stage) is str and stage in DIAGNOSTIC_STAGES else "unknown"
    action = progress.get("action")
    action = (
        action
        if type(action) is str and action in {"prepare", "register", "register-worker"}
        else "unknown"
    )
    report = {
        "schema": 1,
        "action": action,
        "stage": stage,
        "status": "failed",
        "passed": False,
        "affects_acceptance": False,
        "error": {"category": category, "returncode": code, "timed_out": timed_out},
    }
    if stage == "prepare-docker-build":
        text, scanned, truncated = diagnostic_log(exc)
        report["build"] = {
            **build_failure_facts(text),
            "scanned_bytes": scanned,
            "truncated": truncated,
        }
    return report


@contextmanager
def diagnostic_scope(path, action):
    progress = {"action": action, "stage": action + "-profile-validation"}
    try:
        yield progress
    except Exception as exc:
        if path is not None:
            try:
                body = json.dumps(failure_diagnostic(progress, exc), sort_keys=True) + "\n"
                if len(body.encode("utf-8")) > DIAGNOSTIC_REPORT_BYTES:
                    raise ValueError("Native diagnostic exceeds its fixed budget")
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                # Preserve a more precise worker report; never overwrite readiness,
                # credentials, symlinks, or any pre-existing diagnostic file.
                write_private_new(path, body)
            except Exception:
                print("Native diagnostic could not be saved; the original failure is preserved.")
        raise


def recipe_identity():
    recipes = {name: sha(ROOT / name) for name in RECIPE_PATHS}
    return digest(recipes), recipes


def selection():
    return Selection(template="fastapiadmin").model_dump()


def reject_credentials(text):
    """Never send authenticated registry configuration into Docker build layers."""
    if re.search(r"(?:_auth|authToken|password|username)\s*[=:]|\$\{", text, re.IGNORECASE):
        raise ValueError("Authenticated dependency configuration is not a native build input")
    for url in re.findall(r"https?://[^\s\"'<>]+", text):
        parsed = urlsplit(url)
        if parsed.username is not None or parsed.password is not None or parsed.query:
            raise ValueError("Credential-bearing dependency URLs are not native build inputs")


def product_inputs(product):
    product = Path(product).resolve()
    before = manifest(product)
    metadata_path = inside(product, "deployment/manifest.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or metadata.get("template") != "fastapiadmin":
        raise ValueError("Native snapshot requires an exact fastapiadmin deployment manifest")
    if (
        "selection" in metadata
        and Selection.model_validate(metadata["selection"]).model_dump() != selection()
    ):
        raise ValueError("Native snapshot requires the registered PostgreSQL selection")
    if "database" in metadata and metadata["database"] != "postgresql":
        raise ValueError("Native snapshot requires PostgreSQL")
    for name, path in files(product):
        if path.name == ".npmrc":
            reject_credentials(path.read_text(encoding="utf-8"))
    for name in DESCRIPTORS:
        if name not in before:
            raise ValueError("Native snapshot is missing a dependency descriptor: " + name)
        reject_credentials(inside(product, name).read_text(encoding="utf-8"))
    identity = dependency_identity(product)
    if manifest(product) != before:
        raise ValueError("Native input changed while computing its identity")
    return {
        "product": str(product),
        "source_identity": digest(before),
        "manifest_sha256": before["deployment/manifest.json"],
        "descriptors": {name: before[name] for name in DESCRIPTORS},
        "dependency_identity": identity,
    }


def prepare_context(product, context, expected):
    """Copy allowlisted lock inputs only, never executable product sources/hooks."""
    product, context = Path(product), Path(context)
    if product_inputs(product) != expected:
        raise ValueError("Native input changed before preparing the build context")
    for name in DESCRIPTORS:
        target = inside(context / "product", name)
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = inside(product, name).read_bytes()
        if base.sha256(raw) != expected["descriptors"][name]:
            raise ValueError("Native dependency input changed during copy")
        if name.startswith("backend/"):
            # Same exact public-mirror substitutions as prepare_fastapi_registry.
            # Do not import or copy product/deployment/workbench to perform them.
            text = raw.decode("utf-8")
            tomllib.loads(text)
            text = text.replace(
                "https://pypi.tuna.tsinghua.edu.cn/simple", "https://pypi.org/simple"
            )
            text = text.replace(
                "https://pypi.tuna.tsinghua.edu.cn/packages/",
                "https://files.pythonhosted.org/packages/",
            )
            tomllib.loads(text)
            raw = text.encode("utf-8")
        target.write_bytes(raw)
    dependencies.validate_python(
        (context / "product/backend/pyproject.toml").read_bytes(),
        (context / "product/backend/uv.lock").read_bytes(),
    )
    dependencies.validate_node(
        (context / "product/frontend/web/package.json").read_bytes(),
        (context / "product/frontend/web/pnpm-lock.yaml").read_bytes(),
    )
    harness = context / "harness"
    harness.mkdir()
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, harness / name)
    dependencies.validate_python(
        (harness / "pyproject.toml").read_bytes(),
        (harness / "uv.lock").read_bytes(),
        trusted_project=True,
    )
    for name in ("image", "build"):
        shutil.copyfile(
            ROOT / f"scripts/daytona_dependency_{name}.py",
            context / f"dependency-{name}.py",
        )
    shutil.copyfile(
        ROOT / "scripts/daytona_dependency_build.lock.json",
        context / "dependency-build.lock.json",
    )
    (context / "dependency-inputs.json").write_text(
        json.dumps(
            {
                "recipe_identity": recipe_identity()[0],
                "original_descriptors": expected["descriptors"],
                "harness_descriptors": {
                    name: sha(harness / name) for name in ("pyproject.toml", "uv.lock")
                },
                "normalized_descriptors": {
                    name: sha(context / "product" / name) for name in DESCRIPTORS
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / DOCKERFILE, context / "Dockerfile")
    if product_inputs(product) != expected:
        raise ValueError("Native input changed while preparing the build context")


def base_identity(record):
    return {
        "profile": record["profile"],
        "recipe_identity": record["recipe_identity"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "runner": copy.deepcopy(record["runner"]),
        "rust_image": copy.deepcopy(record["bases"]["RUST_IMAGE"]),
    }


def native_stamp(identity, foundation, inputs):
    return digest(
        {
            "recipe_identity": identity,
            "base": foundation,
            "inputs": inputs,
            "selection": selection(),
            "resources": RESOURCES,
        }
    )[:16]


def validate_image(image, record):
    config = image.get("Config") or {}
    labels = config.get("Labels") or {}
    if (
        image.get("Os") != "linux"
        or image.get("Architecture") != "amd64"
        or labels.get("org.opencontainers.image.revision") != base.DAYTONA_SOURCE
        or labels.get("rnd.capability.profile") != PROFILE
        or labels.get("rnd.capability.recipe") != record["recipe_identity"]
        or labels.get("rnd.capability.base-recipe") != record["base"]["recipe_identity"]
        or labels.get("rnd.capability.base-image") != record["base"]["snapshot_image_id"]
        or labels.get("rnd.capability.base-digest") != record["base"]["snapshot_digest"]
        or labels.get("rnd.capability.dependencies") != record["dependency_identity"]
        or labels.get("rnd.capability.input") != record["inputs"]["source_identity"]
        or config.get("User") != "0:0"
        or config.get("WorkingDir") != base.CONTROL_WORKDIR
        or config.get("Entrypoint")
        or config.get("Cmd")
    ):
        raise ValueError("Native image does not match its reviewed root-control recipe")


def write_private_new(path, text):
    """Exclusive creation prevents replacing base metadata or an existing credential."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
        output.write(text)
        output.flush()
        os.fsync(output.fileno())


def prepare(product, directory=HOME, *, diagnostics=None):
    with diagnostic_scope(diagnostics, "prepare") as progress:
        return _prepare(product, directory, progress)


def _prepare(product, directory, progress):
    directory = base.profile_directory(directory)
    # The verified root-control Runner is reused unchanged, never rebuilt here.
    foundation = base_identity(base.require_profile(directory))
    if any((directory / name).exists() for name in (LOCK, ENVIRONMENT)):
        raise ValueError("Native setup refuses to overwrite an existing profile or environment")
    progress["stage"] = "prepare-input-validation"
    inputs = product_inputs(product)
    identity, recipes = recipe_identity()
    stamp = native_stamp(identity, foundation, inputs)
    tag = "127.0.0.1:6000/" + FAMILY + ":" + stamp
    record = {
        "profile": PROFILE,
        "selection": selection(),
        "recipe_identity": identity,
        "recipes": recipes,
        "base": foundation,
        "runner": copy.deepcopy(foundation["runner"]),
        "inputs": inputs,
        "dependency_identity": inputs["dependency_identity"],
        "resources": dict(RESOURCES),
    }
    with tempfile.TemporaryDirectory(prefix="native-capability-build-", dir=directory) as temporary:
        progress["stage"] = "prepare-context"
        context = Path(temporary)
        prepare_context(product, context, inputs)
        argv = [
            "build",
            "--progress=plain",
            "--platform=linux/amd64",
            "--pull=false",
            "--build-arg",
            "BASE_IMAGE="
            + foundation["snapshot_digest"].replace("registry:6000/", "127.0.0.1:6000/", 1),
            "--build-arg",
            "RUST_IMAGE=" + foundation["rust_image"]["digest"],
        ]
        labels = {
            "org.opencontainers.image.revision": base.DAYTONA_SOURCE,
            "rnd.capability.profile": PROFILE,
            "rnd.capability.recipe": identity,
            "rnd.capability.base-recipe": foundation["recipe_identity"],
            "rnd.capability.base-image": foundation["snapshot_image_id"],
            "rnd.capability.base-digest": foundation["snapshot_digest"],
            "rnd.capability.dependencies": inputs["dependency_identity"],
            "rnd.capability.input": inputs["source_identity"],
        }
        for name, value in labels.items():
            argv += ["--label", name + "=" + value]
        argv += ["--tag", tag, str(context)]
        progress["stage"] = "prepare-docker-build"
        local.docker(*argv, timeout=3600)
    progress["stage"] = "prepare-image-validation"
    image = base.inspect_image(tag)
    validate_image(image, record)
    progress["stage"] = "prepare-registry-start"
    base.compose(directory, "up", "-d", "--pull", "never", "registry", "gateway")
    local.wait_for_registry()
    progress["stage"] = "prepare-image-push"
    local.docker("push", tag, timeout=1200)
    progress["stage"] = "prepare-published-image-validation"
    published = base.inspect_image(tag)
    validate_image(published, record)
    prefix = "127.0.0.1:6000/" + FAMILY + "@sha256:"
    digests = [
        value
        for value in published.get("RepoDigests", [])
        if re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", value)
    ]
    if len(digests) != 1 or published["Id"] != image["Id"]:
        raise ValueError("Native publication changed image identity or has no unique digest")
    immutable = digests[0].replace("127.0.0.1:6000/", "registry:6000/", 1)
    record["snapshot"] = {
        "image": immutable,
        "digest": immutable,
        "image_id": image["Id"],
        "local_tag": tag,
        "source_hash": stamp,
        "snapshot": FAMILY + "-" + stamp,
        "user": "0:0",
        "working_dir": base.CONTROL_WORKDIR,
        "recipe_sha256": recipes[DOCKERFILE],
    }
    progress["stage"] = "prepare-manifest-validation"
    record["snapshot"]["dependency_manifest"] = base.inspect_dependency_manifest(
        image["Id"], "fastapiadmin", inputs["descriptors"]
    )
    progress["stage"] = "prepare-final-identity-validation"
    if (
        base_identity(base.require_profile(directory)) != foundation
        or product_inputs(product) != inputs
        or recipe_identity() != (identity, recipes)
    ):
        raise ValueError("Native build inputs or base profile changed during preparation")
    # Publish readiness last. Base snapshot-image.json/workbench.env are untouched.
    progress["stage"] = "prepare-readiness-write"
    write_private_new(directory / LOCK, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


def require_native_profile(directory=HOME, snapshot=None):
    """Read-only identity proof; runtime isolation/resource evidence is separate."""
    directory = base.profile_directory(directory)
    foundation = base_identity(base.require_profile(directory))
    record = json.loads(inside(directory, LOCK).read_text(encoding="utf-8"))
    identity, recipes = recipe_identity()
    inputs = record.get("inputs", {})
    if (
        record.get("profile") != PROFILE
        or record.get("selection") != selection()
        or record.get("recipe_identity") != identity
        or record.get("recipes") != recipes
        or record.get("base") != foundation
        or record.get("runner") != foundation["runner"]
        or record.get("resources") != RESOURCES
        or not inputs.get("product")
        or inputs != product_inputs(inputs["product"])
        or record.get("dependency_identity") != inputs.get("dependency_identity")
    ):
        raise ValueError("Native profile recipe, dependency input or base identity changed")
    stamp = native_stamp(identity, foundation, inputs)
    image = record.get("snapshot", {})
    expected_digest = image.get("digest", "")
    if (
        image.get("source_hash") != stamp
        or image.get("local_tag") != "127.0.0.1:6000/" + FAMILY + ":" + stamp
        or image.get("snapshot") != FAMILY + "-" + stamp
        or image.get("image") != expected_digest
        or not re.fullmatch(r"registry:6000/" + FAMILY + r"@sha256:[a-f0-9]{64}", expected_digest)
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", image.get("image_id", ""))
        or image.get("user") != "0:0"
        or image.get("working_dir") != base.CONTROL_WORKDIR
        or image.get("recipe_sha256") != recipes[DOCKERFILE]
        or (snapshot is not None and snapshot != image.get("snapshot"))
    ):
        raise ValueError("Native snapshot lock differs from its exact derived identity")
    inspected = base.inspect_image(image["local_tag"])
    validate_image(inspected, record)
    local_digest = expected_digest.replace("registry:6000/", "127.0.0.1:6000/", 1)
    if inspected["Id"] != image["image_id"] or local_digest not in inspected.get("RepoDigests", []):
        raise ValueError("Native snapshot tag no longer matches its immutable ID and digest")
    base.require_dependency_manifest(record, "fastapiadmin", inputs["descriptors"])
    return record


def environment_text(key, snapshot):
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,4096}", key):
        raise ValueError("Existing local account key cannot be safely written as environment data")
    return (
        "SANDBOX_PROVIDER=daytona\nDAYTONA_ALLOW_LOCAL_EXECUTION=true\n"
        "DAYTONA_API_URL=http://127.0.0.1:3000/api\nDAYTONA_TARGET=local\n"
        f"DAYTONA_API_KEY={key}\nDAYTONA_SNAPSHOT={snapshot}\n"
        + "DAYTONA_SNAPSHOTS='"
        + json.dumps({"fastapiadmin/postgresql": snapshot}, separators=(",", ":"))
        + "'\n"
        + "TOOL_TIMEOUT=300\n"
    )


def register(directory=HOME, *, diagnostics=None):
    with diagnostic_scope(diagnostics, "register") as progress:
        return _register(directory, progress, diagnostics)


def _register(directory, progress, diagnostics):
    directory = base.profile_directory(directory)
    require_native_profile(directory)
    command = [
        sys.executable,
        "-m",
        "scripts.daytona_native_capability_profile",
        "register-worker",
        "--directory",
        str(directory),
    ]
    if diagnostics is not None:
        command += ["--diagnostics", str(Path(diagnostics).absolute())]
    progress["stage"] = "register-worker-execution"
    run_command(
        command,
        ROOT,
        timeout=720,
        heartbeat="Local native snapshot registration",
    )


def register_worker(directory=HOME, *, diagnostics=None):
    with diagnostic_scope(diagnostics, "register-worker") as progress:
        return _register_worker(directory, progress)


def _register_worker(directory, progress):
    directory = base.profile_directory(directory)
    record = require_native_profile(directory)
    metadata = record["snapshot"]
    progress["stage"] = "register-worker-credential-read"
    key = json.loads((directory / "api-key.json").read_text(encoding="utf-8"))["value"]
    content = environment_text(key, metadata["snapshot"])
    progress["stage"] = "register-worker-environment-validation"
    path = inside(directory, ENVIRONMENT)
    if path.exists() and os.name != "nt" and path.stat().st_mode & 0o777 != 0o600:
        raise ValueError("Existing native environment does not have private permissions")
    if path.exists() and path.read_text(encoding="utf-8") != content:
        raise ValueError(
            "Native environment already exists with different values; refusing overwrite"
        )
    progress["stage"] = "register-worker-loopback-guard"
    install_loopback_guard()
    from daytona import CreateSnapshotParams, Resources

    progress["stage"] = "register-worker-client-create"
    settings = Settings(
        _env_file=None,
        daytona_api_key=SecretStr(key),
        daytona_api_url="http://127.0.0.1:3000/api",
        daytona_target="local",
    )
    client = client_for(settings)
    try:
        progress["stage"] = "register-worker-snapshot-lookup"
        existing = snapshot_named(client.snapshot, metadata["snapshot"])
        if existing is None:
            progress["stage"] = "register-worker-snapshot-create"
            existing = client.snapshot.create(
                CreateSnapshotParams(
                    name=metadata["snapshot"],
                    image=metadata["digest"],
                    region_id="local",
                    resources=Resources(**RESOURCES),
                ),
                timeout=600,
            )
        progress["stage"] = "register-worker-snapshot-validation"
        if (
            existing.name != metadata["snapshot"]
            or existing.image_name != metadata["digest"]
            or str(getattr(existing.state, "value", existing.state)).lower() != "active"
            or existing.cpu != RESOURCES["cpu"]
            or existing.mem != RESOURCES["memory"]
            or existing.disk != RESOURCES["disk"]
            or existing.entrypoint
        ):
            raise ValueError("Existing native snapshot differs in identity, state or resources")
    finally:
        previous = progress["stage"]
        progress["stage"] = "register-worker-client-close"
        close_client(client)
        progress["stage"] = previous
    progress["stage"] = "register-worker-final-identity-validation"
    require_native_profile(directory, metadata["snapshot"])
    if not path.exists():
        progress["stage"] = "register-worker-environment-write"
        write_private_new(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "register", "register-worker", "check"])
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path)
    parser.add_argument("--diagnostics", type=Path)
    args = parser.parse_args()
    options = {"diagnostics": args.diagnostics} if args.diagnostics is not None else {}
    if args.action == "prepare":
        if args.product is None:
            parser.error("prepare requires --product pointing to an already-generated product")
        prepare(args.product, args.directory, **options)
    elif args.action == "check":
        require_native_profile(args.directory)
    else:
        {"register": register, "register-worker": register_worker}[args.action](
            args.directory, **options
        )
    print(
        "Native snapshot identity step completed; runtime/isolation acceptance is still required."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # SDK/build exceptions can contain registry or account data. Never print them.
        raise SystemExit(
            "Native profile step failed; no new readiness assertion was made."
        ) from None
