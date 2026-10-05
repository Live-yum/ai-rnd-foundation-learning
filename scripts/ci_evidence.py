"""Small, fail-closed CI evidence and clean-room source transfer primitives."""

import hashlib
import json
import ntpath
import os
import re
import stat
import zipfile
from pathlib import PurePosixPath

FORBIDDEN = {
    ".venv",
    "node_modules",
    ".data",
    ".git",
    ".native",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".aws",
    ".ssh",
    ".azure",
    ".config",
    "credentials",
    ".env",
    ".env.local",
}
MAX_FILES = 30000
MAX_BYTES = 400 * 1024 * 1024


def digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def run_binding():
    result = {
        key: os.environ.get(env, "")
        for key, env in (
            ("head", "GITHUB_SHA"),
            ("run", "GITHUB_RUN_ID"),
            ("attempt", "GITHUB_RUN_ATTEMPT"),
        )
    }
    if not re.fullmatch("[0-9a-f]{40}", result["head"]) or any(
        not re.fullmatch("[1-9][0-9]*", result[key]) for key in ("run", "attempt")
    ):
        raise ValueError("CI evidence requires exact head/run/attempt identity")
    return result


def safe_name(name):
    if (
        not isinstance(name, str)
        or not name
        or "\\" in name
        or ":" in name
        or any(ord(c) < 32 or ord(c) == 127 or c in '<>"|?*' for c in name)
        or name.endswith(("/", ".", " "))
    ):
        raise ValueError("Unsafe artifact path")
    parts = name.split("/")
    if any(
        part in {"", ".", ".."}
        or part.lower() in FORBIDDEN
        or part.endswith((".", " "))
        or part.lower().startswith(".env.")
        and part != ".env.example"
        for part in parts
    ):
        raise ValueError("Unsafe or private artifact path: " + name)
    if ntpath.isreserved(name):
        raise ValueError("Windows device artifact path")
    if PurePosixPath(name).is_absolute():
        raise ValueError("Absolute artifact path")
    return name


def regular_file(root, name):
    safe_name(name)
    if root.is_symlink():
        raise ValueError("Symlink source root")
    target = root / name
    for path in (target, *target.parents):
        if path == root:
            break
        if path.is_symlink():
            raise ValueError("Symlink in source artifact: " + name)
    if not target.is_file() or target.stat().st_nlink != 1:
        raise ValueError("Artifact source must be a regular, unlinked file: " + name)
    return target


def create_source_artifact(root, names, output, binding):
    """Only an explicit verified source inventory may cross the clean-room boundary."""
    names = sorted(names)
    if not names or len(names) > MAX_FILES or len(set(names)) != len(names):
        raise ValueError("Invalid source inventory")
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("Case-colliding source inventory")
    rows, total = [], 0
    for name in names:
        data = regular_file(root, name).read_bytes()
        total += len(data)
        rows.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if total > MAX_BYTES:
        raise ValueError("Source artifact too large")
    output.mkdir(parents=True, exist_ok=False)
    archive = output / "source.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for row in rows:
            bundle.write(regular_file(root, row["path"]), row["path"])
    manifest = {
        "version": 1,
        "binding": binding,
        "files": rows,
        "source_digest": digest(rows),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def restore_source_artifact(artifact, destination, binding):
    """Validate every path, size, byte and identity before creating destination files."""
    if any(path.is_symlink() for path in (destination, *destination.parents)):
        raise ValueError("Symlink restored destination ancestor")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Restored destination must be fresh")
    manifest = read_json(artifact / "manifest.json")
    if (
        not isinstance(manifest, dict)
        or type(manifest.get("version")) is not int
        or manifest["version"] != 1
        or manifest.get("binding") != binding
    ):
        raise ValueError("Wrong source artifact head/run/attempt")
    rows = manifest.get("files")
    if (
        not isinstance(rows, list)
        or not rows
        or len(rows) > MAX_FILES
        or digest(rows) != manifest.get("source_digest")
    ):
        raise ValueError("Malformed source manifest")
    names, total = [], 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise ValueError("Malformed source row")
        names.append(safe_name(row["path"]))
        if (
            type(row["bytes"]) is not int
            or row["bytes"] < 0
            or not isinstance(row["sha256"], str)
            or not re.fullmatch("[0-9a-f]{64}", row["sha256"])
        ):
            raise ValueError("Malformed source byte binding")
        total += row["bytes"]
    if (
        names != sorted(set(names))
        or len({name.casefold() for name in names}) != len(names)
        or total > MAX_BYTES
    ):
        raise ValueError("Duplicate, unordered or oversized source inventory")
    paths = {name.casefold() for name in names}
    if any(
        str(parent).casefold() in paths for name in names for parent in PurePosixPath(name).parents
    ):
        raise ValueError("File/directory source collision")
    archive = artifact / "source.zip"
    if archive.is_symlink() or hashlib.sha256(archive.read_bytes()).hexdigest() != manifest.get(
        "archive_sha256"
    ):
        raise ValueError("Source archive byte mismatch")
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if [entry.filename for entry in entries] != names:
            raise ValueError("Archive inventory mismatch")
        for row, entry in zip(rows, entries, strict=True):
            mode = entry.external_attr >> 16
            if (
                entry.is_dir()
                or stat.S_ISLNK(mode)
                or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                or entry.file_size != row["bytes"]
            ):
                raise ValueError("Unsafe archive entry")
            if hashlib.sha256(bundle.read(entry)).hexdigest() != row["sha256"]:
                raise ValueError("Source file byte mismatch")
        destination.mkdir(parents=True)
        for entry in entries:
            target = destination / entry.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.read(entry))
    return manifest
