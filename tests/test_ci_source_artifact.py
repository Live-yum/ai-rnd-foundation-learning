"""Source transfer must verify complete bytes and fail before writing any project."""

import hashlib
import json
import os
import stat
import zipfile

import pytest

from scripts import ci_evidence as evidence

BINDING = {"head": "a" * 40, "run": "123", "attempt": "2"}
FILES = {
    ".github/workflows/test.yml": b"name: acceptance\n",
    ".python-version": b"3.14\n",
    ".env.example": b"PUBLIC_SETTING=example\n",
    "empty.txt": b"",
    "docs/中文说明.md": "原始字节：中文和 emoji 🧪\n\n".encode(),
    "docs/images/pixel.png": b"\x89PNG\r\n\x1a\n\x00\xff",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_files(root, files):
    root.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def inventory(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def save_manifest(artifact, manifest, *, bind_rows=True):
    if bind_rows and isinstance(manifest, dict) and "files" in manifest:
        manifest["source_digest"] = evidence.digest(manifest["files"])
    (artifact / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def replace_archive(artifact, manifest, entries):
    """Construct adversarial ZIPs without the production archive creator."""
    with zipfile.ZipFile(artifact / "source.zip", "w") as archive:
        for name, data, mode in entries:
            entry = zipfile.ZipInfo(name)
            entry.create_system = 3
            entry.external_attr = mode << 16
            archive.writestr(entry, data)
    manifest["archive_sha256"] = sha((artifact / "source.zip").read_bytes())
    save_manifest(artifact, manifest)


def independent_artifact(tmp_path, files=None):
    """Publish a tiny independent fixture, including deliberately unsafe paths."""
    if files is None:
        files = {"a.txt": b"first", "b.txt": b"second"}
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    rows = [
        {"path": name, "bytes": len(data), "sha256": sha(data)}
        for name, data in sorted(files.items())
    ]
    manifest = {"version": 1, "binding": dict(BINDING), "files": rows}
    replace_archive(
        artifact,
        manifest,
        [(name, data, stat.S_IFREG | 0o644) for name, data in sorted(files.items())],
    )
    return artifact, manifest


def reject_restore(artifact, destination, binding=None):
    with pytest.raises((ValueError, FileNotFoundError, zipfile.BadZipFile)):
        evidence.restore_source_artifact(artifact, destination, binding or BINDING)
    assert not destination.exists(), "Invalid evidence wrote a partial restored project"
    assert not destination.is_symlink()


def symlink(target, link, *, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"Symlinks are unavailable on this runner: {error}")


def test_unicode_dotfiles_empty_and_binary_files_roundtrip_with_exact_inventory(tmp_path):
    root, artifact, restored = tmp_path / "source", tmp_path / "artifact", tmp_path / "restored"
    write_files(root, {**FILES, "not-selected.txt": b"must not be copied"})
    created = evidence.create_source_artifact(root, list(reversed(FILES)), artifact, BINDING)
    received = evidence.restore_source_artifact(artifact, restored, dict(BINDING))
    assert created == received
    assert inventory(restored) == FILES
    assert received["binding"] == BINDING
    assert [row["path"] for row in received["files"]] == sorted(FILES)
    assert received["source_digest"] == evidence.digest(received["files"])
    assert received["archive_sha256"] == sha((artifact / "source.zip").read_bytes())
    for row in received["files"]:
        assert row == {
            "path": row["path"],
            "bytes": len(FILES[row["path"]]),
            "sha256": sha(FILES[row["path"]]),
        }


@pytest.mark.parametrize("key,value", [("head", "b" * 40), ("run", "456"), ("attempt", "3")])
def test_identity_mismatch_rejects_before_write(tmp_path, key, value):
    artifact, _ = independent_artifact(tmp_path)
    reject_restore(artifact, tmp_path / "restored", {**BINDING, key: value})


@pytest.mark.parametrize("missing", ["manifest.json", "source.zip"])
def test_missing_artifact_file_rejects_before_write(tmp_path, missing):
    artifact, _ = independent_artifact(tmp_path)
    (artifact / missing).unlink()
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("damage", ["missing", "extra", "duplicate", "changed", "reordered"])
def test_archive_inventory_and_every_file_byte_are_required(tmp_path, damage):
    artifact, manifest = independent_artifact(tmp_path)
    entries = [("a.txt", b"first", stat.S_IFREG), ("b.txt", b"second", stat.S_IFREG)]
    if damage == "missing":
        entries.pop()
    elif damage == "extra":
        entries.append(("extra.txt", b"not inventoried", stat.S_IFREG))
    elif damage == "duplicate":
        entries.append(entries[0])
    elif damage == "changed":
        entries[1] = ("b.txt", b"CHANGE", stat.S_IFREG)
    else:
        entries.reverse()
    if damage == "duplicate":
        with pytest.warns(UserWarning, match="Duplicate name"):
            replace_archive(artifact, manifest, entries)
    else:
        replace_archive(artifact, manifest, entries)
    reject_restore(artifact, tmp_path / "restored")


def test_archive_hash_is_checked_independently_of_file_hashes(tmp_path):
    artifact, _ = independent_artifact(tmp_path)
    with (artifact / "source.zip").open("ab") as archive:
        archive.write(b"changed archive container bytes")
    reject_restore(artifact, tmp_path / "restored")


def test_malformed_archive_is_rejected_even_with_matching_archive_hash(tmp_path):
    artifact, manifest = independent_artifact(tmp_path)
    (artifact / "source.zip").write_bytes(b"not a ZIP")
    manifest["archive_sha256"] = sha(b"not a ZIP")
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("document", [[], None, 1, "not an object"])
def test_nonobject_manifest_is_rejected_as_invalid_input(tmp_path, document):
    artifact, _ = independent_artifact(tmp_path)
    save_manifest(artifact, document)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("version", [True, False, 0, 2, "1", None])
def test_manifest_version_is_an_exact_supported_integer(tmp_path, version):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["version"] = version
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize(
    "field", ["version", "binding", "files", "source_digest", "archive_sha256"]
)
def test_required_manifest_fields_cannot_be_omitted(tmp_path, field):
    artifact, manifest = independent_artifact(tmp_path)
    manifest.pop(field)
    save_manifest(artifact, manifest, bind_rows=False)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("rows", [[], None, {}, "not a list", [None], [1], ["a.txt"]])
def test_malformed_inventory_fails_before_write(tmp_path, rows):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["files"] = rows
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize(
    "change",
    [
        {"bytes": True},
        {"bytes": -1},
        {"bytes": "5"},
        {"bytes": 6},
        {"sha256": "f" * 64},
        {"sha256": "A" * 64},
        {"sha256": "a" * 63},
        {"sha256": None},
        {"path": None},
        {"path": 1},
        {"extra": "unexpected row field"},
    ],
)
def test_malformed_or_incorrect_file_bindings_fail_before_write(tmp_path, change):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["files"][0].update(change)
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("field", ["path", "bytes", "sha256"])
def test_source_row_requires_every_binding_field(tmp_path, field):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["files"][0].pop(field)
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


def test_source_digest_cannot_be_reused_after_manifest_change(tmp_path):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["files"][0]["bytes"] += 1
    save_manifest(artifact, manifest, bind_rows=False)
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize(
    "damage", ["duplicate", "unordered", "casefold", "ancestor", "casefold_ancestor"]
)
def test_colliding_or_noncanonical_manifest_paths_fail_before_write(tmp_path, damage):
    files = {"a.txt": b"first", "b.txt": b"second"}
    if damage == "casefold":
        files = {"A.txt": b"first", "a.txt": b"second"}
    elif damage == "ancestor":
        files = {"a": b"first", "a/b.txt": b"second"}
    elif damage == "casefold_ancestor":
        files = {"A": b"first", "a/b.txt": b"second"}
    artifact, manifest = independent_artifact(tmp_path, files)
    if damage == "duplicate":
        manifest["files"].append(dict(manifest["files"][0]))
    elif damage == "unordered":
        manifest["files"].reverse()
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")


UNSAFE_NAMES = [
    None,
    1,
    True,
    "",
    "/absolute.txt",
    "../escape.txt",
    "a/../escape.txt",
    "./alias.txt",
    "a//alias.txt",
    "a/./alias.txt",
    "C:drive.txt",
    "C:/absolute.txt",
    "a\\windows.txt",
    "a\ncontrol.txt",
    "a\x00control.txt",
    "a\x1fcontrol.txt",
    "a\x7fcontrol.txt",
    "trailing.",
    "trailing ",
    "directory./child.txt",
    "directory /child.txt",
    "directory/",
    ".venv/secret.txt",
    "nested/.VENV/secret.txt",
    "node_modules/module.js",
    ".data/state.db",
    ".git/config",
    ".native/browser.js",
    "__pycache__/module.pyc",
    ".pytest_cache/cache",
    ".ruff_cache/cache",
    ".aws/config",
    ".ssh/id_rsa",
    ".azure/token",
    ".config/token",
    "credentials",
    "nested/CREDENTIALS/token",
    ".env",
    ".env.local",
    ".env.production",
    "nested/.env.secret",
    "CON",
    "con.txt",
    "CON .txt",
    "CONIN$",
    "CONOUT$",
    "AUX.json",
    "nested/NUL",
    "PRN.txt",
    "COM1.txt",
    "LPT9.log",
    "COM¹.txt",
    "LPT².log",
    'quote".txt',
    "less<than.txt",
    "greater>than.txt",
    "pipe|name.txt",
    "wild*.txt",
    "question?.txt",
]


@pytest.mark.parametrize("name", UNSAFE_NAMES)
def test_private_and_nonportable_paths_are_rejected(name):
    with pytest.raises(ValueError):
        evidence.safe_name(name)


@pytest.mark.parametrize("name", ["../escape.txt", "/absolute.txt", "nested/.env", "CON.txt"])
def test_unsafe_manifest_path_is_rejected_before_any_write(tmp_path, name):
    artifact, manifest = independent_artifact(tmp_path)
    manifest["files"][0]["path"] = name
    save_manifest(artifact, manifest)
    reject_restore(artifact, tmp_path / "restored")
    assert not (tmp_path / "escape.txt").exists()


@pytest.mark.parametrize("name", ["nested/.env", ".venv/config", "credentials/token"])
def test_creator_cannot_transfer_private_files_even_if_explicitly_listed(tmp_path, name):
    root, artifact = tmp_path / "source", tmp_path / "artifact"
    write_files(root, {name: b"private fixture, never real credentials"})
    with pytest.raises(ValueError):
        evidence.create_source_artifact(root, [name], artifact, BINDING)
    assert not artifact.exists()


@pytest.mark.parametrize("mode", [stat.S_IFLNK, stat.S_IFDIR, stat.S_IFIFO, stat.S_IFCHR])
def test_archive_links_and_special_entries_are_rejected(tmp_path, mode):
    artifact, manifest = independent_artifact(tmp_path)
    replace_archive(
        artifact,
        manifest,
        [("a.txt", b"first", stat.S_IFREG), ("b.txt", b"second", mode)],
    )
    reject_restore(artifact, tmp_path / "restored")


def test_source_archive_cannot_be_a_symlink(tmp_path):
    artifact, _ = independent_artifact(tmp_path)
    original = tmp_path / "external.zip"
    (artifact / "source.zip").rename(original)
    symlink(original, artifact / "source.zip")
    reject_restore(artifact, tmp_path / "restored")


@pytest.mark.parametrize("kind", ["file", "ancestor", "root"])
def test_creator_rejects_source_symlinks_before_creating_artifact(tmp_path, kind):
    root, outside = tmp_path / "source", tmp_path / "outside"
    write_files(outside, {"value.txt": b"outside source boundary"})
    if kind == "root":
        symlink(outside, root, directory=True)
        name = "value.txt"
    else:
        root.mkdir()
        if kind == "file":
            symlink(outside / "value.txt", root / "value.txt")
            name = "value.txt"
        else:
            symlink(outside, root / "nested", directory=True)
            name = "nested/value.txt"
    artifact = tmp_path / "artifact"
    with pytest.raises(ValueError):
        evidence.create_source_artifact(root, [name], artifact, BINDING)
    assert not artifact.exists()


def test_creator_rejects_hardlinked_source(tmp_path):
    root = tmp_path / "source"
    write_files(root, {"first.txt": b"linked source"})
    try:
        os.link(root / "first.txt", root / "second.txt")
    except OSError as error:
        pytest.skip(f"Hardlinks are unavailable on this runner: {error}")
    with pytest.raises(ValueError):
        evidence.create_source_artifact(root, ["first.txt"], tmp_path / "artifact", BINDING)
    assert not (tmp_path / "artifact").exists()


@pytest.mark.parametrize("names", [[], ["a.txt", "a.txt"], ["A.txt", "a.txt"], ["missing.txt"]])
def test_creator_rejects_missing_duplicate_or_casefold_inventory(tmp_path, names):
    root = tmp_path / "source"
    write_files(root, {"a.txt": b"first"})
    with pytest.raises(ValueError):
        evidence.create_source_artifact(root, names, tmp_path / "artifact", BINDING)
    assert not (tmp_path / "artifact").exists()


@pytest.mark.parametrize("limit", ["MAX_FILES", "MAX_BYTES"])
def test_creation_and_restore_enforce_inventory_limits_before_write(tmp_path, monkeypatch, limit):
    artifact, _ = independent_artifact(tmp_path)
    root = tmp_path / "source"
    write_files(root, {"a.txt": b"first", "b.txt": b"second"})
    monkeypatch.setattr(evidence, limit, 1)
    reject_restore(artifact, tmp_path / "restored")
    with pytest.raises(ValueError):
        evidence.create_source_artifact(root, ["a.txt", "b.txt"], tmp_path / "created", BINDING)
    assert not (tmp_path / "created").exists()


def test_exact_inventory_size_boundaries_are_permitted(tmp_path, monkeypatch):
    root, artifact, restored = tmp_path / "source", tmp_path / "artifact", tmp_path / "restored"
    files = {"a.txt": b"first", "b.txt": b"second"}
    write_files(root, files)
    monkeypatch.setattr(evidence, "MAX_FILES", 2)
    monkeypatch.setattr(evidence, "MAX_BYTES", 11)
    evidence.create_source_artifact(root, files, artifact, BINDING)
    evidence.restore_source_artifact(artifact, restored, BINDING)
    assert inventory(restored) == files


@pytest.mark.parametrize("kind", ["directory", "file", "dangling_symlink"])
def test_restore_requires_fresh_destination_and_preserves_existing_contents(tmp_path, kind):
    artifact, _ = independent_artifact(tmp_path)
    destination = tmp_path / "restored"
    if kind == "directory":
        write_files(destination, {"keep.txt": b"existing project"})
    elif kind == "file":
        destination.write_bytes(b"existing file")
    else:
        symlink(tmp_path / "absent", destination, directory=True)
    with pytest.raises(ValueError):
        evidence.restore_source_artifact(artifact, destination, BINDING)
    if kind == "directory":
        assert inventory(destination) == {"keep.txt": b"existing project"}
    elif kind == "file":
        assert destination.read_bytes() == b"existing file"
    else:
        assert destination.is_symlink() and not (tmp_path / "absent").exists()


def test_restore_cannot_follow_a_destination_ancestor_symlink(tmp_path):
    artifact, _ = independent_artifact(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    symlink(outside, tmp_path / "linked", directory=True)
    reject_restore(artifact, tmp_path / "linked" / "restored")
    assert list(outside.iterdir()) == []


def test_creator_preserves_existing_output(tmp_path):
    root, output = tmp_path / "source", tmp_path / "artifact"
    write_files(root, {"a.txt": b"first"})
    write_files(output, {"keep.txt": b"existing artifact"})
    with pytest.raises(FileExistsError):
        evidence.create_source_artifact(root, ["a.txt"], output, BINDING)
    assert inventory(output) == {"keep.txt": b"existing artifact"}


@pytest.mark.parametrize("text", ['{"head":1,"head":2}', '{"nested":{"run":1,"run":2}}'])
def test_duplicate_json_keys_are_rejected_at_every_depth(tmp_path, text):
    path = tmp_path / "manifest.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        evidence.read_json(path)


@pytest.mark.parametrize("text", ["{", "", '{"version":1,}'])
def test_malformed_json_fails_before_write(tmp_path, text):
    artifact, _ = independent_artifact(tmp_path)
    (artifact / "manifest.json").write_text(text, encoding="utf-8")
    reject_restore(artifact, tmp_path / "restored")


def test_run_binding_reads_exact_head_run_and_attempt(monkeypatch):
    for key, value in zip(
        ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"), BINDING.values(), strict=True
    ):
        monkeypatch.setenv(key, value)
    assert evidence.run_binding() == BINDING


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_SHA", ""),
        ("GITHUB_SHA", "a" * 39),
        ("GITHUB_SHA", "A" * 40),
        ("GITHUB_SHA", "g" * 40),
        ("GITHUB_RUN_ID", ""),
        ("GITHUB_RUN_ID", "0"),
        ("GITHUB_RUN_ID", "01"),
        ("GITHUB_RUN_ID", "-1"),
        ("GITHUB_RUN_ATTEMPT", ""),
        ("GITHUB_RUN_ATTEMPT", "0"),
        ("GITHUB_RUN_ATTEMPT", "1.0"),
        ("GITHUB_RUN_ATTEMPT", " 1"),
    ],
)
def test_run_binding_rejects_missing_or_noncanonical_identity(monkeypatch, key, value):
    for name, valid in zip(
        ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"), BINDING.values(), strict=True
    ):
        monkeypatch.setenv(name, valid)
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError):
        evidence.run_binding()
