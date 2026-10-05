"""Data-only, no-follow dependency inventory and runtime verification (stdlib only).

The manifest is sealed into the image. Its SHA-256 and immutable Docker image ID
are bound externally by the controller profile, avoiding an impossible self-ID.
Never imports a candidate module, executes a dependency, or follows links to chown.
"""

import argparse
import hashlib
import json
import os
import posixpath
import re
import stat
from pathlib import Path, PurePosixPath

MANIFEST = Path("/opt/rnd/runtime/dependency-manifest.json")
HEX = re.compile(r"[a-f0-9]{64}")
ROOTS = {
    "python-basic": [
        "/opt/rnd/runtime/python-basic/.venv",
        "/opt/rnd/python",
        "/usr/local/bin/node",
        "/opt/rnd/browser",
        "/opt/rnd/browsers",
    ],
    "fastapiadmin": [
        "/opt/rnd/runtime/fastapiadmin/backend/.venv",
        "/opt/rnd/runtime/fastapiadmin/frontend/node_modules",
        "/opt/rnd/python",
        "/usr/local/bin/node",
        "/opt/rnd/harness/.venv",
        "/opt/rnd/browser",
        "/opt/rnd/browsers",
    ],
}
GROUPS = {
    "python-basic": {"python": ["--no-dev"], "extras": []},
    "fastapiadmin": {
        "python": ["default-groups"],
        "extras": [],
        "node": ["dependencies", "devDependencies", "optionalDependencies"],
        "harness": {
            "python": ["default-groups"],
            "extras": ["postgres", "daytona"],
            "install_project": False,
        },
    },
}


def native_descriptor_roles():
    """Data-only policy, mirrored by the isolated standalone build collector."""
    return {
        "runtime": [
            "backend/pyproject.toml",
            "backend/uv.lock",
            "frontend/web/package.json",
            "frontend/web/pnpm-lock.yaml",
        ],
        "portable_launcher": ["deployment/pyproject.toml", "deployment/uv.lock"],
        "auxiliary_source": [
            "frontend/app/package.json",
            "frontend/app/pnpm-lock.yaml",
            "frontend/app/src/uni_modules/mp-html/package.json",
            "frontend/docs/package.json",
            "frontend/docs/pnpm-lock.yaml",
        ],
    }


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(fd):
    result = hashlib.sha256()
    while block := os.read(fd, 1024 * 1024):
        result.update(block)
    return result.hexdigest()


def open_absolute(path, *, directory=False):
    """Open each ancestor O_NOFOLLOW; a real directory is required throughout."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Dependency path must be absolute and normalized")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for index, part in enumerate(path.parts[1:]):
            flags = os.O_RDONLY | os.O_NOFOLLOW
            if directory or index < len(path.parts) - 2:
                flags |= os.O_DIRECTORY
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def regular_bytes(path):
    fd = open_absolute(path)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Descriptor/manifest is not an independent regular file")
        with os.fdopen(os.dup(fd), "rb") as stream:
            return stream.read()
    finally:
        os.close(fd)


def check_ancestors(path):
    for parent in reversed(Path(path).parents):
        fd = open_absolute(parent, directory=True)
        try:
            info = os.fstat(fd)
            if info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
                raise ValueError("Dependency ancestor is application-writable")
        finally:
            os.close(fd)


def inventory(roots, *, readonly=True):
    """Inventory all entries using directory FDs; reject devices and hardlinks."""
    entries = {}

    def visit(parent, name, absolute):
        info = os.stat(name, dir_fd=parent, follow_symlinks=False)
        mode = stat.S_IMODE(info.st_mode)
        entry = {"mode": mode, "uid": info.st_uid, "gid": info.st_gid}
        if info.st_mode & 0o6000:
            raise ValueError("Set-ID dependency entry rejected")
        if readonly and (info.st_uid != 0 or info.st_gid != 0):
            raise ValueError("Dependency must be root-owned")
        if stat.S_ISLNK(info.st_mode):
            if info.st_nlink != 1:
                raise ValueError("Hardlinked dependency symlink rejected")
            entry.update(type="symlink", target=os.readlink(name, dir_fd=parent))
        else:
            if readonly and mode & 0o022:
                raise ValueError("Dependency is application-writable")
            if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise ValueError("Special dependency entry rejected")
            flags = os.O_RDONLY | os.O_NOFOLLOW
            if stat.S_ISDIR(info.st_mode):
                flags |= os.O_DIRECTORY
            fd = os.open(name, flags, dir_fd=parent)
            try:
                opened = os.fstat(fd)
                if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise ValueError("Dependency changed during inventory")
                if stat.S_ISREG(info.st_mode):
                    if info.st_nlink != 1:
                        raise ValueError("Hardlinked dependency file rejected")
                    entry.update(type="file", size=info.st_size, sha256=file_hash(fd))
                else:
                    entry.update(type="directory")
                    for child in sorted(os.listdir(fd)):
                        visit(fd, child, absolute + "/" + child)
            finally:
                os.close(fd)
        entries[absolute] = entry

    for root in roots:
        if readonly:
            check_ancestors(root)
        parent = open_absolute(Path(root).parent, directory=True)
        try:
            visit(parent, Path(root).name, str(root))
        finally:
            os.close(parent)
    validate_links(entries, roots)
    return dict(sorted(entries.items()))


def validate_links(entries, roots):
    def permitted(value):
        return any(value == root or value.startswith(root + "/") for root in roots)

    def resolve(value):
        for _ in range(41):
            if not permitted(value):
                raise ValueError("Dependency symlink escapes the complete image graph")
            parts = value.split("/")
            for index in range(2, len(parts) + 1):
                prefix = "/".join(parts[:index])
                entry = entries.get(prefix)
                if entry and entry["type"] == "symlink":
                    target = entry["target"]
                    value = posixpath.normpath(
                        posixpath.join(posixpath.dirname(prefix), target, *parts[index:])
                    )
                    break
            else:
                if value not in entries:
                    raise ValueError("Dependency link target is missing")
                return value
        raise ValueError("Cyclic dependency symlink rejected")

    for path, entry in entries.items():
        if entry["type"] == "symlink":
            resolve(path)


def seal(roots):
    """Run only after the builder exited, with no app process sharing this layer."""
    inventory(roots, readonly=False)

    def visit(parent, name):
        info = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            os.chown(name, 0, 0, dir_fd=parent, follow_symlinks=False)
            return
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if stat.S_ISDIR(info.st_mode):
            flags |= os.O_DIRECTORY
        fd = os.open(name, flags, dir_fd=parent)
        try:
            opened = os.fstat(fd)
            if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError("Dependency changed during sealing")
            if stat.S_ISDIR(info.st_mode):
                for child in sorted(os.listdir(fd)):
                    visit(fd, child)
            elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Unsafe entry during dependency sealing")
            os.fchown(fd, 0, 0)
            mode = (stat.S_IMODE(info.st_mode) & ~0o222) | 0o444
            if stat.S_ISDIR(info.st_mode) or info.st_mode & 0o111:
                mode |= 0o111
            os.fchmod(fd, mode)
        finally:
            os.close(fd)

    for root in roots:
        parent = open_absolute(Path(root).parent, directory=True)
        try:
            visit(parent, Path(root).name)
        finally:
            os.close(parent)
    return inventory(roots)


def validate_manifest(value, profile):
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "profiles"}
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or not isinstance(profile, str)
        or profile not in ROOTS
        or not isinstance(value.get("profiles"), dict)
        or set(value["profiles"]) - set(ROOTS)
    ):
        raise ValueError("Unsupported dependency manifest")
    record = value["profiles"].get(profile)
    required = {
        "roots",
        "groups",
        "recipe_identity",
        "platform",
        "original_descriptors",
        "normalized_descriptors",
        "entries",
        "installed_tree_sha256",
    }
    optional = {
        "toolchain",
        "source_builds",
        "build_tool_artifacts",
        "build_tool_installed_sha256",
        "harness_descriptors",
    }
    if profile == "fastapiadmin":
        required.add("descriptor_roles")
    if (
        not isinstance(record, dict)
        or not required <= set(record)
        or set(record) - required - optional
        or record.get("roots") != ROOTS[profile]
        or record.get("groups") != GROUPS[profile]
        or not isinstance(record.get("recipe_identity"), str)
        or not HEX.fullmatch(record["recipe_identity"])
        or record.get("platform") != {"os": "linux", "architecture": "amd64", "python": "3.14.7"}
        or not isinstance(record.get("entries"), dict)
        or not isinstance(record.get("installed_tree_sha256"), str)
        or record["installed_tree_sha256"] != digest(record["entries"])
    ):
        raise ValueError("Dependency profile, groups, platform or tree identity mismatch")
    for group in ("original_descriptors", "normalized_descriptors"):
        descriptors = record.get(group)
        if not isinstance(descriptors, dict) or not descriptors:
            raise ValueError("Unsafe dependency descriptor identity")
        for name, value_hash in descriptors.items():
            if (
                not isinstance(name, str)
                or not name
                or "\\" in name
                or ":" in name
                or "\x00" in name
                or name.startswith("/")
                or ".." in PurePosixPath(name).parts
                or PurePosixPath(name).as_posix() != name
                or name == "."
                or not isinstance(value_hash, str)
                or not HEX.fullmatch(value_hash)
            ):
                raise ValueError("Unsafe dependency descriptor identity")
    if set(record["original_descriptors"]) != set(record["normalized_descriptors"]):
        raise ValueError("Normalized descriptor membership differs")
    if profile == "fastapiadmin":
        roles = native_descriptor_roles()
        if (
            record["descriptor_roles"] != roles
            or set(record["original_descriptors"])
            != {name for paths in roles.values() for name in paths}
            or any(
                record["original_descriptors"][name] != record["normalized_descriptors"][name]
                for name in [*roles["portable_launcher"], *roles["auxiliary_source"]]
            )
        ):
            raise ValueError("Native source descriptor roles or immutable source hashes differ")
    return record


def inspect_manifest(profile, *, path=MANIFEST, verify_tree=True):
    raw = regular_bytes(Path(path).absolute())
    document = json.loads(raw)
    record = validate_manifest(document, profile)
    if verify_tree:
        check_ancestors(path)
        info = Path(path).lstat()
        if info.st_uid or info.st_gid or info.st_mode & 0o022:
            raise ValueError("Dependency manifest is application-writable")
        if inventory(record["roots"]) != record["entries"]:
            raise ValueError("Installed dependency graph changed")
    return raw, record


def receipt(profile, *, product=None, path=MANIFEST):
    raw, record = inspect_manifest(profile, path=path)
    if product is not None:
        for name, expected in record["original_descriptors"].items():
            if (
                hashlib.sha256(regular_bytes(Path(product).absolute() / name)).hexdigest()
                != expected
            ):
                raise ValueError("Candidate dependency descriptor changed")
    return {
        "schema": 1,
        "profile": profile,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "installed_tree_sha256": record["installed_tree_sha256"],
        "descriptors_verified": product is not None,
        "installed_tree_verified": True,
        "readonly_verified": True,
    }


def create(profile, inputs, *, path=MANIFEST):
    value = (
        json.loads(Path(path).read_bytes())
        if Path(path).exists()
        else {"schema": 1, "profiles": {}}
    )
    record = dict(inputs)
    record.update(roots=ROOTS[profile], groups=GROUPS[profile])
    record["entries"] = seal(record["roots"])
    record["installed_tree_sha256"] = digest(record["entries"])
    value["profiles"][profile] = record
    validate_manifest(value, profile)
    Path(path).write_bytes(canonical(value) + b"\n")
    os.chmod(path, 0o444)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["seal", "seal-build-tools", "create", "inspect", "verify-runtime"],
    )
    parser.add_argument("--profile", choices=list(ROOTS), required=True)
    parser.add_argument("--product", type=Path)
    parser.add_argument("--inputs", type=Path)
    args = parser.parse_args()
    if args.action == "seal-build-tools":
        entries = seal(["/opt/rnd/build-tools", "/opt/rnd/python"])
        Path("/opt/rnd/build-tools-manifest.json").write_bytes(
            canonical({"installed_tree_sha256": digest(entries)})
        )
        os.chmod("/opt/rnd/build-tools-manifest.json", 0o444)
    elif args.action == "seal":
        seal(ROOTS[args.profile])
    elif args.action == "create":
        create(args.profile, json.loads(regular_bytes(args.inputs.absolute())))
    elif args.action == "verify-runtime":
        if args.product is None:
            parser.error("--product is required for runtime verification")
        print(json.dumps(receipt(args.profile, product=args.product), sort_keys=True))
    else:
        raw, record = inspect_manifest(args.profile)
        print(
            json.dumps(
                {
                    "schema": 1,
                    "profile": args.profile,
                    "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                    "installed_tree_sha256": record["installed_tree_sha256"],
                    "original_descriptors": record["original_descriptors"],
                    **(
                        {"descriptor_roles": record["descriptor_roles"]}
                        if args.profile == "fastapiadmin"
                        else {}
                    ),
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
