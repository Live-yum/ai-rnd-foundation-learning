"""Data-only dependency graph tests. These are not live noexec/runtime proof."""

import copy
import hashlib
import json
import os

import pytest

from scripts import daytona_capability_profile as profile
from scripts import daytona_dependency_image as image

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
