"""Build ordinary Git-tracked source archives. No submodules, LFS or runtime clone is needed."""

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    {
        "name": "fastapiadmin",
        "template": "fastapiadmin",
        "slot": "fastapiadmin",
        "url": "https://github.com/fastapiadmin/FastapiAdmin.git",
        "sha": "1cd12c726ad9032c17ef85ce805ce991be60fbdf",
    },
    {
        "name": "yudao-backend",
        "template": "yudao-vben",
        "slot": "backend",
        "url": "https://github.com/yudaocode/yudao-cloud-mini.git",
        "sha": "47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be",
    },
    {
        "name": "yudao-frontend",
        "template": "yudao-vben",
        "slot": "frontend",
        "url": "https://github.com/yudaocode/yudao-ui-admin-vben.git",
        "sha": "1b14e889f529e245fd620daa720dcea6de0cc5e7",
    },
]
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".data",
    "target",
    "dist",
    "logs",
}
EXCLUDE_EXT = {
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".ttc",
    ".eot",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".db",
    ".db-wal",
    ".db-shm",
}


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def pack(source, target):
    rows, excluded = {}, []
    for base, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for name in sorted(names):
            path = Path(base) / name
            relative = path.relative_to(source).as_posix()
            if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
                raise ValueError("Template source contains a non-regular file: " + relative)
            if (
                path.suffix.lower() in EXCLUDE_EXT
                or (name.startswith(".env") and not name.endswith(".example"))
                or name in {"access-token", "id_rsa", "id_ed25519", "credentials.json"}
            ):
                excluded.append(relative)
                continue
            if path.stat().st_size > 32_000_000:
                raise ValueError("Unexpected large source asset: " + relative)
            rows[relative] = path
    target.parent.mkdir(parents=True, exist_ok=True)
    hashes = {}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(rows.items()):
            data = path.read_bytes()
            hashes[name] = fingerprint(data)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    source_digest = fingerprint(
        json.dumps(hashes, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    )
    return {
        "archive_sha256": fingerprint(target.read_bytes()),
        "source_digest": source_digest,
        "files": len(rows),
        "excluded_files": excluded,
    }


def build(source_root, output):
    records = []
    for source in SOURCES:
        path = source_root / source["name"]
        license_text = (path / "LICENSE").read_text(encoding="utf-8")
        if "MIT" not in license_text:
            raise ValueError("Review upstream license before vendoring")
        archive = source["name"] + ".zip"
        facts = pack(path, output / archive)
        (output / (source["name"] + ".LICENSE")).write_text(
            license_text, encoding="utf-8", newline="\n"
        )
        records.append({**source, "archive": archive, "license": "MIT", **facts})
    manifest = {
        "format": 1,
        "storage": "ordinary-git-source-archives",
        "sources": records,
        "exclusions": sorted(EXCLUDE_DIRS | EXCLUDE_EXT),
        "note": "Source code, schemas and dependency locks are included. Build caches, runtime secrets and font binaries are not redistributed.",
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "templates/vendor")
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch == bool(args.source_root):
        parser.error("Select exactly one of --fetch or --source-root")
    with tempfile.TemporaryDirectory(prefix="native-vendor-") as temporary:
        root = args.source_root or Path(temporary)
        if args.fetch:
            for row in SOURCES:
                dest = root / row["name"]
                dest.mkdir()
                subprocess.run(["git", "init", "--quiet", "--template=", str(dest)], check=True)
                subprocess.run(
                    ["git", "-C", str(dest), "fetch", "--depth", "1", row["url"], row["sha"]],
                    check=True,
                )
                subprocess.run(
                    ["git", "-C", str(dest), "checkout", "--detach", "FETCH_HEAD"], check=True
                )
                actual = subprocess.check_output(
                    ["git", "-C", str(dest), "rev-parse", "HEAD"], text=True
                ).strip()
                if actual != row["sha"]:
                    raise ValueError("Wrong upstream commit")
        result = build(root, args.output)
        print(
            json.dumps(
                [
                    {k: s[k] for k in ("name", "sha", "files", "archive_sha256")}
                    for s in result["sources"]
                ],
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
