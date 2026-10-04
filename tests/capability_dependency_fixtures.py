"""Synthetic provenance for contract tests only; never a live image attestation."""

from pathlib import Path

from scripts.daytona_native_capability_profile import DESCRIPTORS
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.filesystem import manifest


def dependency_profile(template="python-basic", descriptors=None):
    names = DESCRIPTORS if template == "fastapiadmin" else ("pyproject.toml", "uv.lock")
    return {
        "schema": 1,
        "profile": template,
        "image_id": "sha256:" + "3" * 64,
        "manifest_sha256": "6" * 64,
        "installed_tree_sha256": "7" * 64,
        "original_descriptors": descriptors or dict.fromkeys(names, "8" * 64),
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
    }


def container_binding(record):
    return {
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "dependency_manifest": record["snapshot"]["dependency_manifest"],
    }
