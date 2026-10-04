"""Prepare/register the opt-in native profile without changing the base installation.

Only dependency descriptors reach the build context. Candidate source, frontend lifecycle hooks,
credentials and deployment control modules are never executed during preparation.
The warmed image is not runtime, browser, database or isolation acceptance evidence.
"""

import argparse
import copy
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import SecretStr

from scripts import daytona_capability_profile as base
from scripts import daytona_local as local
from scripts.daytona_bootstrap import snapshot_named
from workbench.catalog import Selection
from workbench.daytona_profiles import dependency_identity
from workbench.domain import digest
from workbench.filesystem import files, inside, manifest, sha
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings
from workbench.tools import run_command

HOME = base.HOME
PROFILE = "native-fastapiadmin-postgresql-v1"
LOCK = "native-fastapiadmin-profile.json"
ENVIRONMENT = "fastapiadmin.env"
FAMILY = "rnd-native-fastapiadmin"
RESOURCES = {"cpu": 2, "memory": 6, "disk": 30}
DOCKERFILE = "tools/daytona/capability-native-snapshot.Dockerfile"
RECIPE_PATHS = (
    "scripts/daytona_native_capability_profile.py",
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


def recipe_identity():
    recipes = {name: sha(ROOT / name) for name in RECIPE_PATHS}
    return digest(recipes), recipes


def selection():
    return Selection(template="fastapiadmin").model_dump()


def reject_credentials(text):
    """Never send authenticated registry configuration into Docker build layers."""
    if re.search(r"(?:_auth|authToken|password|username)\s*[=:]|\$\{", text, re.I):
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
    harness = context / "harness"
    harness.mkdir()
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, harness / name)
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


def prepare(product, directory=HOME):
    directory = base.profile_directory(directory)
    # The verified root-control Runner is reused unchanged, never rebuilt here.
    foundation = base_identity(base.require_profile(directory))
    if any((directory / name).exists() for name in (LOCK, ENVIRONMENT)):
        raise ValueError("Native setup refuses to overwrite an existing profile or environment")
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
        local.docker(*argv, timeout=3600)
    image = base.inspect_image(tag)
    validate_image(image, record)
    base.compose(directory, "up", "-d", "--pull", "never", "registry", "gateway")
    local.wait_for_registry()
    local.docker("push", tag, timeout=1200)
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
    if (
        base_identity(base.require_profile(directory)) != foundation
        or product_inputs(product) != inputs
        or recipe_identity() != (identity, recipes)
    ):
        raise ValueError("Native build inputs or base profile changed during preparation")
    # Publish readiness last. Base snapshot-image.json/workbench.env are untouched.
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


def register(directory=HOME):
    directory = base.profile_directory(directory)
    require_native_profile(directory)
    run_command(
        [
            sys.executable,
            "-m",
            "scripts.daytona_native_capability_profile",
            "register-worker",
            "--directory",
            str(directory),
        ],
        ROOT,
        timeout=720,
        heartbeat="Local native snapshot registration",
    )


def register_worker(directory=HOME):
    directory = base.profile_directory(directory)
    record = require_native_profile(directory)
    metadata = record["snapshot"]
    key = json.loads((directory / "api-key.json").read_text(encoding="utf-8"))["value"]
    content = environment_text(key, metadata["snapshot"])
    path = inside(directory, ENVIRONMENT)
    if path.exists() and os.name != "nt" and path.stat().st_mode & 0o777 != 0o600:
        raise ValueError("Existing native environment does not have private permissions")
    if path.exists() and path.read_text(encoding="utf-8") != content:
        raise ValueError(
            "Native environment already exists with different values; refusing overwrite"
        )
    install_loopback_guard()
    from daytona import CreateSnapshotParams, Resources

    settings = Settings(
        _env_file=None,
        daytona_api_key=SecretStr(key),
        daytona_api_url="http://127.0.0.1:3000/api",
        daytona_target="local",
    )
    client = client_for(settings)
    try:
        existing = snapshot_named(client.snapshot, metadata["snapshot"])
        if existing is None:
            existing = client.snapshot.create(
                CreateSnapshotParams(
                    name=metadata["snapshot"],
                    image=metadata["digest"],
                    region_id="local",
                    resources=Resources(**RESOURCES),
                ),
                timeout=600,
            )
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
        close_client(client)
    require_native_profile(directory, metadata["snapshot"])
    if not path.exists():
        write_private_new(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "register", "register-worker", "check"])
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        if args.product is None:
            parser.error("prepare requires --product pointing to an already-generated product")
        prepare(args.product, args.directory)
    elif args.action == "check":
        require_native_profile(args.directory)
    else:
        {"register": register, "register-worker": register_worker}[args.action](args.directory)
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
