"""Exact CI-authored source handoff, never a sanitizer for candidate input.

Capture only the clean ZIP-roundtrip-verified product before its independent
launcher installs/builds dependencies. The original native build tree is left
intact. Readiness is published only after the complete native-tools acceptance.
"""

import argparse
import hashlib
import json
import os
import re
import stat
from contextlib import contextmanager
from pathlib import Path, PurePosixPath

from scripts.daytona_native_capability_profile import DESCRIPTORS
from workbench.domain import digest
from workbench.filesystem import EXCLUDED_DIRS, manifest, secret_name, write_json
from workbench.settings import ROOT

PRODUCT = ROOT / ".native/capability-source"
RECEIPT = ROOT / "reports/native-tools/capability-source.json"
PROVENANCE = "verified-native-delivery-archive-before-independent-build"


def ordinary_path(path):
    """Do not resolve away a linked root or any linked parent."""
    if ".." in Path(path).parts:
        raise ValueError("CI source handoff rejects parent traversal in root paths")
    path = Path(path).absolute()
    for entry in [*reversed(path.parents), path]:
        if entry.is_symlink() or (hasattr(entry, "is_junction") and entry.is_junction()):
            raise ValueError("CI source handoff cannot use linked paths")
    return path


@contextmanager
def directory_fd(path, *, create=False):
    """Open every ancestor without following links, including the root argument."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("CI native source handoff requires no-follow directory descriptors")
    path = ordinary_path(path)
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        yield descriptor
    finally:
        os.close(descriptor)


def file_identity(value):
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_nlink,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def read_regular(directory, name, expected=None):
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > 32_000_000
            or expected is not None
            and file_identity(expected) != file_identity(before)
        ):
            raise ValueError("CI source handoff rejects nonregular, linked, or changed files")
        data = source.read(32_000_001)
        if (
            len(data) != before.st_size
            or file_identity(os.fstat(source.fileno())) != file_identity(before)
            or file_identity(os.stat(name, dir_fd=directory, follow_symlinks=False))
            != file_identity(before)
        ):
            raise ValueError("CI source handoff file changed while reading")
    return data


def validate_inventory(inventory):
    if type(inventory) is not dict or not inventory or len(inventory) > 10000:
        raise ValueError("CI source handoff requires the complete verified inventory")
    directories, canonical = set(), set()
    for name, value in inventory.items():
        path = PurePosixPath(name) if type(name) is str else None
        if (
            path is None
            or not name
            or path.as_posix() != name
            or path.is_absolute()
            or ".." in path.parts
            or "\\" in name
            or ":" in name
            or len(name) > 4096
            or any(ord(char) < 32 or ord(char) == 127 for char in name)
            or name.casefold() in canonical
            or any(part in EXCLUDED_DIRS for part in path.parts)
            or secret_name(name)
            or path.suffix in {".pyc", ".pyo"}
            or any(part.startswith(".writing-") for part in path.parts)
            or type(value) is not str
            or not re.fullmatch(r"[a-f0-9]{64}", value)
        ):
            raise ValueError("CI source handoff inventory contains a non-source path or hash")
        canonical.add(name.casefold())
        directories.update(parent.as_posix() for parent in path.parents if str(parent) != ".")
    canonical_directories = {name.casefold() for name in directories}
    if len(canonical_directories) != len(directories) or canonical_directories & canonical:
        raise ValueError("CI source handoff file and directory paths collide")
    return directories


def require_exact_source(product, inventory):
    """Inspect every physical entry; no ignore patterns or excluded subtrees."""
    directories = validate_inventory(inventory)
    product = ordinary_path(product)
    if not product.is_dir():
        raise ValueError("CI source handoff requires a regular source directory")
    observed, seen_directories, total_bytes = {}, set(), 0

    def walk_error(error):
        raise error

    with directory_fd(product) as root:
        for base, dirs, names, directory in os.fwalk(
            ".", dir_fd=root, follow_symlinks=False, onerror=walk_error
        ):
            for name in sorted([*dirs, *names]):
                relative = (PurePosixPath(base) / name).as_posix()
                mode = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if stat.S_ISDIR(mode.st_mode):
                    if relative not in directories:
                        raise ValueError(
                            "CI source handoff has an extra directory or dependency tree"
                        )
                    seen_directories.add(relative)
                elif stat.S_ISREG(mode.st_mode) and mode.st_nlink == 1:
                    if relative not in inventory:
                        raise ValueError("CI source handoff has an extra file")
                    observed[relative] = hashlib.sha256(
                        read_regular(directory, name, mode)
                    ).hexdigest()
                    total_bytes += mode.st_size
                    if total_bytes > 200_000_000:
                        raise ValueError("CI source handoff exceeds the source byte budget")
                else:
                    raise ValueError("CI source handoff rejects nonregular or linked files")
    if observed != inventory or seen_directories != directories:
        raise ValueError("CI source handoff path set or byte hashes changed")
    return inventory


def copy_exact_source(source, destination, inventory):
    """A new physical copy of an independently verified clean source, never a filter."""
    source, destination = ordinary_path(source), ordinary_path(destination)
    require_exact_source(source, inventory)
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("CI source handoff directories must be independent")
    with directory_fd(destination.parent, create=True) as parent:
        os.mkdir(destination.name, dir_fd=parent)
    for name in sorted(inventory):
        relative = PurePosixPath(name)
        with directory_fd(source / relative.parent) as original:
            data = read_regular(original, relative.name)
        if hashlib.sha256(data).hexdigest() != inventory[name]:
            raise ValueError("CI source handoff file changed before copying")
        with directory_fd(destination / relative.parent, create=True) as target:
            descriptor = os.open(
                relative.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o644,
                dir_fd=target,
            )
            with os.fdopen(descriptor, "wb") as output:
                output.write(data)
    require_exact_source(source, inventory)
    require_exact_source(destination, inventory)
    return destination


def descriptors(inventory):
    names = {"pyproject.toml", "uv.lock", "pnpm-lock.yaml", "package.json", "pom.xml"}
    observed = {name: value for name, value in inventory.items() if Path(name).name in names}
    if set(observed) != set(DESCRIPTORS):
        raise ValueError("CI source handoff requires exactly the six native descriptors")
    return observed


def run_identity():
    """Bind GitHub runs/attempts; local runs instead rely on fresh exclusive output."""
    return {
        name: os.environ.get(name, "")
        for name in ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")
    }


class SourceHandoff:
    def __init__(self, product, receipt):
        self.product, self.receipt = ordinary_path(product), ordinary_path(receipt)
        if self.receipt.is_relative_to(self.product):
            raise ValueError("CI source readiness must remain outside product source")
        # Invalidate stale readiness even when capture or the native run later fails.
        write_json(self.receipt, {"schema": 1, "passed": False, "provenance": PROVENANCE})
        if self.product.exists():
            raise FileExistsError("CI source handoff refuses to overwrite an existing product")
        self.inventory = None
        self.archive = None
        self.run = run_identity()

    def capture(self, clean_product, inventory, archive_sha256):
        if self.inventory is not None:
            raise ValueError("CI source handoff may capture only one verified archive")
        if type(archive_sha256) is not str or not re.fullmatch(r"[a-f0-9]{64}", archive_sha256):
            raise ValueError("CI source handoff requires its verified archive digest at capture")
        inventory = dict(inventory)
        descriptors(inventory)
        copy_exact_source(clean_product, self.product, inventory)
        self.inventory = inventory
        self.archive = archive_sha256

    def complete(self, report, original_product):
        restored = report.get("portable_restored", {})
        archive = restored.get("source_archive_sha256")
        if (
            self.inventory is None
            or self.run != run_identity()
            or report.get("generated_runtime_verified") is not True
            or any(
                restored.get(name) is not True
                for name in (
                    "passed",
                    "fresh_database",
                    "standalone_launcher",
                    "archive_round_trip",
                )
            )
            or type(archive) is not str
            or not re.fullmatch(r"[a-f0-9]{64}", archive)
            or archive != self.archive
            or manifest(original_product) != self.inventory
        ):
            raise ValueError("CI source readiness requires unchanged independently accepted source")
        require_exact_source(self.product, self.inventory)
        value = {
            "schema": 1,
            "passed": True,
            "provenance": PROVENANCE,
            "product": str(self.product),
            "source_identity": digest(self.inventory),
            "source_archive_sha256": archive,
            "inventory": self.inventory,
            "descriptors": descriptors(self.inventory),
            "run": self.run,
        }
        write_json(self.receipt, value)
        return value


def validate_receipt(value, product):
    product = ordinary_path(product)
    if (
        type(value) is not dict
        or set(value)
        != {
            "schema",
            "passed",
            "provenance",
            "product",
            "source_identity",
            "source_archive_sha256",
            "inventory",
            "descriptors",
            "run",
        }
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or value.get("passed") is not True
        or value.get("provenance") != PROVENANCE
        or value.get("product") != str(product)
        or value.get("run") != run_identity()
        or type(value.get("source_archive_sha256")) is not str
        or not re.fullmatch(r"[a-f0-9]{64}", value["source_archive_sha256"])
    ):
        raise ValueError("CI source handoff has no current successful readiness receipt")
    inventory = value["inventory"]
    validate_inventory(inventory)
    if value["source_identity"] != digest(inventory) or value["descriptors"] != descriptors(
        inventory
    ):
        raise ValueError("CI source handoff receipt identity changed")
    return value


def require_handoff(product, receipt=RECEIPT):
    product, receipt = ordinary_path(product), ordinary_path(receipt)

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("CI source handoff receipt has duplicate keys")
            result[key] = value
        return result

    with directory_fd(receipt.parent) as parent:
        mode = os.stat(receipt.name, dir_fd=parent, follow_symlinks=False)
        if mode.st_size > 8_000_000:
            raise ValueError("CI source handoff receipt exceeds its input budget")
        value = json.loads(read_regular(parent, receipt.name, mode), object_pairs_hook=unique_pairs)
    validate_receipt(value, product)
    require_exact_source(product, value["inventory"])
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", type=Path, default=PRODUCT)
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    args = parser.parse_args()
    require_handoff(args.product, args.receipt)
    print("Exact CI source inventory and descriptor binding verified; no source was modified.")


if __name__ == "__main__":
    main()
