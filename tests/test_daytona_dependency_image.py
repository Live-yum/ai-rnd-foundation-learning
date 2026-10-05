"""Data-only dependency graph tests. These are not live noexec/runtime proof."""

import copy
import hashlib
import json
import os
from pathlib import PurePosixPath

import pytest
from capability_dependency_fixtures import (
    dependency_profile,
    runtime_patch_entries,
    runtime_patches,
)

from scripts import daytona_capability_profile as profile
from scripts import daytona_dependency_image as image
from workbench import capability_dependencies as admission

posix_graph = pytest.mark.skipif(os.name == "nt", reason="POSIX no-follow image filesystem")


def graph(tmp_path):
    root = tmp_path / "runtime"
    root.mkdir()
    (root / "lib").mkdir()
    (root / "lib/native.so").write_bytes(b"complete native payload")
    (root / "bin").mkdir()
    (root / "bin/tool").write_bytes(b"#!/immutable/python\n")
    (root / "bin/tool").chmod(0o755)
    (root / "alias").symlink_to("lib")
    (root / "nested").symlink_to("alias/native.so")
    return root


@posix_graph
def test_inventory_hashes_every_file_directory_mode_and_complete_link_graph(tmp_path):
    root = graph(tmp_path)
    entries = image.inventory([str(root)], readonly=False)
    assert len(entries) == 7
    assert (
        entries[str(root / "lib/native.so")]["sha256"]
        == hashlib.sha256(b"complete native payload").hexdigest()
    )
    assert entries[str(root / "bin/tool")]["mode"] == 0o755
    assert entries[str(root / "alias")]["target"] == "lib"
    assert entries[str(root / "nested")]["target"] == "alias/native.so"
    before = image.digest(entries)
    (root / "lib/native.so").write_bytes(b"changed native payload")
    assert image.digest(image.inventory([str(root)], readonly=False)) != before


@posix_graph
@pytest.mark.parametrize("target", ["../../escape", "/usr/bin/sh", "missing", "cycle"])
def test_invalid_symlink_graph_fails_before_any_privileged_mutation(tmp_path, monkeypatch, target):
    root = graph(tmp_path)
    (root / "cycle").symlink_to(target)
    calls = []
    monkeypatch.setattr(os, "fchown", lambda *args: calls.append(args))
    with pytest.raises(ValueError, match="symlink|link target"):
        image.seal([str(root)])
    assert calls == []


@posix_graph
def test_cross_root_managed_interpreter_link_is_recorded_without_following(tmp_path):
    root = graph(tmp_path)
    interpreter = tmp_path / "python"
    interpreter.mkdir()
    (interpreter / "python").write_bytes(b"python executable")
    (root / "bin/python").symlink_to(interpreter / "python")
    entries = image.inventory([str(root), str(interpreter)], readonly=False)
    assert entries[str(root / "bin/python")]["type"] == "symlink"
    assert entries[str(interpreter / "python")]["type"] == "file"
    with pytest.raises(ValueError, match="escapes"):
        image.inventory([str(root)], readonly=False)


@posix_graph
def test_hardlinks_devices_and_setid_are_rejected(tmp_path):
    root = graph(tmp_path)
    os.link(root / "lib/native.so", root / "duplicate.so")
    with pytest.raises(ValueError, match="Hardlinked"):
        image.inventory([str(root)], readonly=False)
    (root / "duplicate.so").unlink()
    os.mkfifo(root / "fifo")
    with pytest.raises(ValueError, match="Special"):
        image.inventory([str(root)], readonly=False)
    (root / "fifo").unlink()
    (root / "bin/tool").chmod(0o4755)
    with pytest.raises(ValueError, match="Set-ID"):
        image.inventory([str(root)], readonly=False)


@posix_graph
def test_regular_descriptor_rejects_symlink_ancestors_leaf_and_hardlinks(tmp_path):
    root = graph(tmp_path)
    with pytest.raises(OSError):
        image.regular_bytes(root / "alias/native.so")
    with pytest.raises(OSError):
        image.regular_bytes(root / "nested")
    os.link(root / "lib/native.so", root / "duplicate.so")
    with pytest.raises(ValueError, match="independent regular"):
        image.regular_bytes(root / "duplicate.so")


@posix_graph
def test_inventory_rejects_nonroot_ownership_or_writable_ancestors(tmp_path):
    root = graph(tmp_path)
    with pytest.raises(ValueError, match="ancestor|root-owned|writable"):
        image.inventory([str(root)])


def manifest_fixture(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "pyproject.toml").write_text("locked descriptor")
    original = {"pyproject.toml": hashlib.sha256(b"locked descriptor").hexdigest()}
    record = {
        "roots": image.ROOTS["python-basic"],
        "groups": image.GROUPS["python-basic"],
        "recipe_identity": "a" * 64,
        "original_descriptors": original,
        "normalized_descriptors": original,
        "platform": {"os": "linux", "architecture": "amd64", "python": "3.14.7"},
        "entries": {},
        "installed_tree_sha256": image.digest({}),
    }
    value = {"schema": 1, "profiles": {"python-basic": record}}
    return product, value, record


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(roots=["/tmp/deps"]),
        lambda record: record.update(groups={"python": ["--all-extras"]}),
        lambda record: record.update(
            platform={"os": "linux", "architecture": "arm64", "python": "3.14.7"}
        ),
        lambda record: record.update(installed_tree_sha256="b" * 64),
        lambda record: record.update(original_descriptors={"../secret": "a" * 64}),
        lambda record: record.update(normalized_descriptors={}),
    ],
)
def test_manifest_drift_fails_closed(tmp_path, mutation):
    _, value, record = manifest_fixture(tmp_path)
    image.validate_manifest(value, "python-basic")
    mutation(record)
    with pytest.raises(ValueError):
        image.validate_manifest(value, "python-basic")


def test_bounded_runtime_receipt_checks_original_descriptors_and_exposes_no_tree(
    tmp_path, monkeypatch
):
    product, value, record = manifest_fixture(tmp_path)
    raw = image.canonical(value)
    monkeypatch.setattr(image, "inspect_manifest", lambda *args, **kwargs: (raw, record))
    monkeypatch.setattr(image, "regular_bytes", lambda path: path.read_bytes())
    actual = image.receipt("python-basic", product=product)
    assert actual == {
        "schema": 1,
        "profile": "python-basic",
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "installed_tree_sha256": image.digest({}),
        "descriptors_verified": True,
        "installed_tree_verified": True,
        "readonly_verified": True,
    }
    (product / "pyproject.toml").write_text("candidate drift")
    with pytest.raises(ValueError, match="descriptor changed"):
        image.receipt("python-basic", product=product)


def test_image_inventory_runs_unprivileged_offline_and_binds_immutable_id(monkeypatch):
    calls = []
    expected = {
        "schema": 1,
        "profile": "python-basic",
        "manifest_sha256": "a" * 64,
        "installed_tree_sha256": "b" * 64,
        "original_descriptors": {"uv.lock": "c" * 64},
    }
    monkeypatch.setattr(
        profile.local,
        "docker",
        lambda *args, **kwargs: calls.append((args, kwargs)) or json.dumps(expected),
    )
    actual = profile.inspect_dependency_manifest(
        "sha256:" + "d" * 64, "python-basic", expected["original_descriptors"]
    )
    assert actual == {**expected, "image_id": "sha256:" + "d" * 64}
    command = calls[0][0]
    for flag in (
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--user=65534:65534",
        "--security-opt=no-new-privileges",
    ):
        assert flag in command
    assert "sha256:" + "d" * 64 in command
    bad = copy.deepcopy(expected)
    bad["original_descriptors"]["uv.lock"] = "e" * 64
    monkeypatch.setattr(profile.local, "docker", lambda *args, **kwargs: json.dumps(bad))
    with pytest.raises(ValueError, match="descriptor inputs"):
        profile.inspect_dependency_manifest(
            "sha256:" + "d" * 64, "python-basic", expected["original_descriptors"]
        )
    with pytest.raises(ValueError, match="immutable image ID"):
        profile.inspect_dependency_manifest(
            "mutable:tag", "python-basic", expected["original_descriptors"]
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(image_id="sha256:" + "b" * 64),
        lambda record: record.update(profile="fastapiadmin"),
        lambda record: record.update(schema=0),
        lambda record: record.update(original_descriptors={"uv.lock": "c" * 64}),
        lambda record: record.update(manifest_sha256="mutable"),
        lambda record: record.update(installed_tree_sha256=None),
    ],
)
def test_outer_binding_rejects_stale_image_and_descriptor_receipts(mutation):
    expected = {
        "schema": 1,
        "profile": "python-basic",
        "image_id": "sha256:" + "a" * 64,
        "manifest_sha256": "b" * 64,
        "installed_tree_sha256": "c" * 64,
        "original_descriptors": {"uv.lock": "d" * 64},
    }
    original = copy.deepcopy(expected)
    profile.validate_dependency_binding(
        expected, original["image_id"], "python-basic", original["original_descriptors"]
    )
    mutation(expected)
    with pytest.raises(ValueError, match="binding"):
        profile.validate_dependency_binding(
            expected,
            original["image_id"],
            "python-basic",
            original["original_descriptors"],
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(schema=True),
        lambda value: value.update(profiles=[]),
        lambda value: value.update(extra="unsupported"),
        lambda value: value["profiles"]["python-basic"].update(recipe_identity=None),
        lambda value: value["profiles"]["python-basic"].update(entries=[]),
        lambda value: value["profiles"]["python-basic"].update(original_descriptors=[]),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"./uv.lock": "a" * 64}
        ),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"backend//uv.lock": "a" * 64}
        ),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"backend\\uv.lock": "a" * 64}
        ),
    ],
)
def test_malformed_manifest_has_classified_value_error(tmp_path, mutation):
    _, value, _ = manifest_fixture(tmp_path)
    mutation(value)
    with pytest.raises(ValueError):
        image.validate_manifest(value, "python-basic")


def native_manifest_fixture():
    roles = image.native_descriptor_roles()
    descriptors = {name: "a" * 64 for paths in roles.values() for name in paths}
    entries = runtime_patch_entries()
    record = {
        "roots": image.ROOTS["fastapiadmin"],
        "groups": image.GROUPS["fastapiadmin"],
        "recipe_identity": "b" * 64,
        "original_descriptors": descriptors,
        "normalized_descriptors": dict(descriptors),
        "descriptor_roles": roles,
        "platform": {"os": "linux", "architecture": "amd64", "python": "3.14.7"},
        "runtime_patches": runtime_patches(),
        "entries": entries,
        "installed_tree_sha256": image.digest(entries),
    }
    return {"schema": 1, "profiles": {"fastapiadmin": record}}, record


@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "missing",
        "empty",
        "duplicate",
        "identity",
        "version",
        "upstream",
        "patched",
        "path",
        "extra",
        "file-hash",
        "file-type",
        "link",
        "parent-link",
        "missing-file",
    ],
)
def test_native_manifest_binds_reviewed_patch_physical_file_and_vite_link(mutation):
    value, record = native_manifest_fixture()
    patch = record["runtime_patches"][0]
    path = image.NATIVE_NODE_ROOT + "/" + patch["relative_path"]
    if mutation == "missing":
        record.pop("runtime_patches")
    elif mutation == "empty":
        record["runtime_patches"] = []
    elif mutation == "duplicate":
        record["runtime_patches"].append(dict(patch))
    elif mutation == "identity":
        patch["id"] = "vite-preview-interface-eperm-v0"
    elif mutation == "version":
        patch["version"] = "7.3.4"
    elif mutation == "upstream":
        patch["upstream_sha256"] = "c" * 64
    elif mutation == "patched":
        patch["patched_sha256"] = "c" * 64
    elif mutation == "path":
        patch["relative_path"] = "vite/dist/node/chunks/config.js"
    elif mutation == "extra":
        patch["runtime_hook"] = "ignored"
    elif mutation == "file-hash":
        record["entries"][path]["sha256"] = patch["upstream_sha256"]
    elif mutation == "file-type":
        record["entries"][path]["type"] = "symlink"
    elif mutation == "link":
        record["entries"][image.NATIVE_NODE_ROOT + "/vite"]["target"] = (
            ".pnpm/other/node_modules/vite"
        )
    elif mutation == "parent-link":
        record["entries"][str(PurePosixPath(path).parent)]["type"] = "symlink"
    elif mutation == "missing-file":
        record["entries"].pop(path)
    record["installed_tree_sha256"] = image.digest(record["entries"])
    if mutation is None:
        assert image.validate_manifest(value, "fastapiadmin") is record
    else:
        with pytest.raises(ValueError):
            image.validate_manifest(value, "fastapiadmin")


@pytest.mark.parametrize(
    "relative",
    [
        ".pnpm/vite@7.3.3/node_modules/vite/dist/node/chunks/config.js",
        ".pnpm/vite@7.3.3_@types+node@24.0.0_jiti@2.6.1/node_modules/vite/dist/node/chunks/config.js",
    ],
)
def test_native_runtime_patch_policies_agree_and_accept_pnpm_peer_suffix(relative):
    identity = image.native_runtime_patch_identity()
    assert (
        identity
        == admission.native_runtime_patch_identity()
        == {
            "id": "vite-preview-interface-eperm-v1",
            "package": "vite",
            "version": "7.3.3",
            "upstream_sha256": "339ee4656b2ca976ca320b48cffba04361f91ad0899a32a1c60ba9b2910e772e",
            "patched_sha256": "8df548e7d1456f542321e05139faec50f23f15e64afc5a434c57583308bcc86e",
        }
    )
    assert image.VITE_PATCH_PATH.fullmatch(relative)
    assert admission.valid_native_runtime_patches([{**identity, "relative_path": relative}])


@posix_graph
@pytest.mark.parametrize(
    "mutation",
    ["missing", "stale", "tampered", "unpatched", "link", "symlink", "hardlink", "ancestor-link"],
)
def test_native_create_rejects_patch_drift_before_any_privileged_mutation(
    tmp_path, monkeypatch, mutation
):
    """Use a real graph with inert stand-in bytes; never seal/chown test files."""
    _, record = native_manifest_fixture()
    root = tmp_path / "node_modules"
    relative = record["runtime_patches"][0]["relative_path"]
    target = root / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(b"reviewed patch stand-in")
    (root / "vite").symlink_to(relative.removesuffix("/dist/node/chunks/config.js"))
    identity = image.native_runtime_patch_identity()
    identity["patched_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    record["runtime_patches"][0]["patched_sha256"] = identity["patched_sha256"]
    monkeypatch.setattr(image, "native_runtime_patch_identity", lambda: identity)
    monkeypatch.setattr(image, "NATIVE_NODE_ROOT", str(root))
    monkeypatch.setitem(image.ROOTS, "fastapiadmin", [str(root)])
    if mutation == "missing":
        record.pop("runtime_patches")
    elif mutation == "stale":
        record["runtime_patches"][0]["id"] = "old"
    elif mutation in {"tampered", "unpatched"}:
        target.write_bytes(b"changed" if mutation == "tampered" else b"official unpatched source")
    elif mutation == "link":
        (root / "other").mkdir()
        (root / "vite").unlink()
        (root / "vite").symlink_to("other")
    elif mutation == "symlink":
        target.rename(target.with_name("payload.js"))
        target.symlink_to("payload.js")
    elif mutation == "hardlink":
        os.link(target, target.with_name("payload.js"))
    else:
        parent = target.parent
        parent.rename(parent.with_name("other"))
        parent.symlink_to("other")
    for name in ("fchown", "fchmod", "chown", "chmod"):
        monkeypatch.setattr(
            os, name, lambda *a, **kw: pytest.fail("Mutated before patch validation")
        )
    destination = tmp_path / "manifest.json"
    with pytest.raises(ValueError):
        image.create("fastapiadmin", record, path=destination)
    assert not destination.exists()


@posix_graph
def test_direct_native_seal_rejects_missing_patch_before_privileged_mutation(tmp_path, monkeypatch):
    root = graph(tmp_path)
    monkeypatch.setattr(image, "NATIVE_NODE_ROOT", str(root))
    for name in ("fchown", "fchmod", "chown"):
        monkeypatch.setattr(
            os, name, lambda *a, **kw: pytest.fail("Mutated before patch validation")
        )
    with pytest.raises(ValueError, match="runtime patch"):
        image.seal([str(root)])


def test_native_runtime_receipt_carries_patch_identity_without_full_graph(monkeypatch):
    value, record = native_manifest_fixture()
    monkeypatch.setattr(
        image, "inspect_manifest", lambda *a, **kw: (image.canonical(value), record)
    )
    result = image.receipt("fastapiadmin")
    assert result["runtime_patches"] == record["runtime_patches"]
    assert "entries" not in result and "original_descriptors" not in result


@pytest.mark.parametrize(
    "mutation",
    [None, "missing", "empty", "duplicate", "stale-id", "upstream", "patched", "path", "extra"],
)
def test_native_inspection_lock_and_controller_reject_old_or_incompatible_patch(
    monkeypatch, mutation
):
    original = dependency_profile("fastapiadmin")
    value = copy.deepcopy(original)
    patches = value["runtime_patches"]
    if mutation == "missing":
        value.pop("runtime_patches")
    elif mutation == "empty":
        value["runtime_patches"] = []
    elif mutation == "duplicate":
        patches.append(dict(patches[0]))
    elif mutation == "stale-id":
        patches[0]["id"] = "vite-preview-interface-eperm-v0"
    elif mutation == "upstream":
        patches[0]["upstream_sha256"] = "0" * 64
    elif mutation == "patched":
        patches[0]["patched_sha256"] = "0" * 64
    elif mutation == "path":
        patches[0]["relative_path"] = (
            ".pnpm/vite@7.3.3/../node_modules/vite/dist/node/chunks/config.js"
        )
    elif mutation == "extra":
        patches[0]["unknown"] = True
    compact = {key: item for key, item in value.items() if key != "image_id"}
    monkeypatch.setattr(profile.local, "docker", lambda *a, **kw: json.dumps(compact))
    actions = [
        lambda: profile.inspect_dependency_manifest(
            original["image_id"], "fastapiadmin", original["original_descriptors"]
        ),
        lambda: profile.validate_dependency_binding(
            value, original["image_id"], "fastapiadmin", original["original_descriptors"]
        ),
        lambda: admission.require_dependency_manifest(value, "fastapiadmin"),
    ]
    for action in actions:
        if mutation is None:
            action()
        else:
            with pytest.raises((ValueError, admission.CheckFailure)):
                action()


def test_old_native_lock_cannot_be_revalidated_by_current_recipe_label(monkeypatch):
    value = dependency_profile("fastapiadmin")
    value.pop("runtime_patches")
    record = {
        "recipe_identity": profile.recipe_identity()[0],
        "snapshot": {"image_id": value["image_id"], "dependency_manifest": value},
    }
    monkeypatch.setattr(
        profile,
        "inspect_dependency_manifest",
        lambda *a, **kw: pytest.fail("Old native lock passed current-controller admission"),
    )
    with pytest.raises(ValueError, match="binding"):
        profile.require_dependency_manifest(record, "fastapiadmin", value["original_descriptors"])
