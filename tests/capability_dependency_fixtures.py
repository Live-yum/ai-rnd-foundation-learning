"""Synthetic provenance for contract tests only; never a live image attestation."""

from pathlib import Path, PurePosixPath

from scripts.daytona_dependency_build import native_descriptor_roles
from scripts.daytona_native_capability_profile import DESCRIPTORS
from workbench.capability_dependencies import NATIVE_NODE_ROOT, native_runtime_patch_identity
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.filesystem import manifest


def runtime_patches():
    return [
        {
            **native_runtime_patch_identity(),
            "relative_path": ".pnpm/vite@7.3.3/node_modules/vite/dist/node/chunks/config.js",
        }
    ]


def runtime_patch_entries():
    """Synthetic complete physical path and its one public package link."""
    patch = runtime_patches()[0]
    path = PurePosixPath(NATIVE_NODE_ROOT) / patch["relative_path"]
    metadata = {"uid": 0, "gid": 0, "mode": 0o555}
    entries = {
        str(path): {**metadata, "type": "file", "sha256": patch["patched_sha256"], "size": 1}
    }
    for parent in path.parents:
        if parent.is_relative_to(NATIVE_NODE_ROOT):
            entries[str(parent)] = {**metadata, "type": "directory"}
    entries[NATIVE_NODE_ROOT + "/vite"] = {
        **metadata,
        "type": "symlink",
        "target": patch["relative_path"].removesuffix("/dist/node/chunks/config.js"),
    }
    return entries


def dependency_profile(template="python-basic", descriptors=None):
    names = DESCRIPTORS if template == "fastapiadmin" else ("pyproject.toml", "uv.lock")
    return {
        "schema": 1,
        "profile": template,
        "image_id": "sha256:" + "3" * 64,
        "manifest_sha256": "6" * 64,
        "installed_tree_sha256": "7" * 64,
        "original_descriptors": descriptors or dict.fromkeys(names, "8" * 64),
        **(
            {"descriptor_roles": native_descriptor_roles(), "runtime_patches": runtime_patches()}
            if template == "fastapiadmin"
            else {}
        ),
    }


def profile_record(product=None, template="python-basic"):
    descriptors = None
    if product is not None:
        descriptors = {
            name: value
            for name, value in manifest(product).items()
            if Path(name).name
            in {"pyproject.toml", "uv.lock", "package.json", "pnpm-lock.yaml", "pom.xml"}
        }
    profile = dependency_profile(template, descriptors)
    return {
        "recipe_identity": "1" * 64,
        "selection": Selection(template=template).model_dump(),
        "runner": {"image_id": "sha256:" + "2" * 64},
        "snapshot": {
            "image_id": profile["image_id"],
            "digest": "registry:6000/"
            + ("rnd-native-fastapiadmin" if template == "fastapiadmin" else "rnd-python")
            + "@sha256:"
            + "4" * 64,
            "snapshot": "rnd-python-test",
            "dependency_manifest": profile,
        },
    }


def dependency_evidence(profile=None, inventory=None):
    profile = profile or dependency_profile()
    return {
        **{
            name: profile[name]
            for name in ("schema", "profile", "manifest_sha256", "installed_tree_sha256")
        },
        "descriptors_verified": True,
        "installed_tree_verified": True,
        "readonly_verified": True,
        "product_links_verified": True,
        "source_inventory_verified": True,
        "source_inventory_sha256": digest(inventory or {}),
        **(
            {"runtime_patches": profile["runtime_patches"]}
            if profile["profile"] == "fastapiadmin"
            else {}
        ),
    }


def container_binding(record):
    return {
        **(
            {
                "profile": "native-fastapiadmin-postgresql-v1",
                "shared_memory": {"ipc_mode": "private", "size_bytes": 67108864},
            }
            if record.get("selection", {}).get("template") == "fastapiadmin"
            else {}
        ),
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "dependency_manifest": record["snapshot"]["dependency_manifest"],
    }
