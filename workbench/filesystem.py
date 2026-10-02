"""File boundaries, atomic writes, deterministic hashes, and safe ZIP extraction."""

import hashlib
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".data",
    ".deployment",
    ".continue",
    "target",
    "dist",
    "logs",
}


def secret_name(path):
    name = Path(path).name.lower()
    return (
        name == ".env"
        or (name.startswith(".env.") and not name.endswith(".example"))
        or name.startswith(".aider.")
        or name.endswith(
            (".sqlite3", ".sqlite", ".pem", ".key", ".p12", ".pfx", ".db", ".db-wal", ".db-shm")
        )
        or name
        in {
            "access-token",
            "id_rsa",
            "id_ed25519",
            "credentials.json",
            ".pypirc",
            ".netrc",
            ".git-credentials",
        }
    )


def inside(root, relative):
    root = Path(root).resolve()
    p = PurePosixPath(str(relative).replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or any(":" in part for part in p.parts):
        raise ValueError("文件路径越界")
    candidate = root.joinpath(*p.parts)
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("不接受符号链接或 Windows junction")
    candidate.resolve().relative_to(root)
    return candidate


def atomic_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, data):
    atomic_text(path, json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def files(root):
    root = Path(root).resolve()
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for directory in dirs:
            inside(root, (Path(base) / directory).relative_to(root).as_posix())
        for name in sorted(names):
            relative = (Path(base) / name).relative_to(root).as_posix()
            path = inside(root, relative)
            if secret_name(relative) or name.startswith(".writing-"):
                continue
            if not stat.S_ISREG(path.stat().st_mode):
                raise ValueError("只允许普通文件")
            if path.stat().st_size > 32_000_000:
                raise ValueError(f"文件超过 32 MB 限制: {relative}")
            yield relative, path


def manifest(root):
    return {name: sha(path) for name, path in files(root)}


ARCHIVE_MAX_BYTES = 200_000_000
ARCHIVE_MAX_FILE_BYTES = 32_000_000
ARCHIVE_MAX_RATIO = 200


def archive_entry_limit(template=None):
    """Caller-selected trusted template, never a value read from archive content.

    The pinned Yudao monorepo alone contains over 12,000 source files. Its
    source importer already uses a bounded 25,000-entry policy. Keep the
    generic/Python/Fastapi ceiling and every template's byte budget unchanged.
    """
    if template not in {None, "python-basic", "fastapiadmin", "yudao-vben"}:
        raise ValueError("未知压缩包模板")
    return 25000 if template == "yudao-vben" else 10000


def _archive_preflight(z, destination, template):
    entries = z.infolist()
    limit = archive_entry_limit(template)
    expanded = sum(item.file_size for item in entries)
    if len(entries) > limit:
        raise ValueError(f"压缩包条目数量超过限制: {len(entries)} > {limit}")
    if expanded > ARCHIVE_MAX_BYTES:
        raise ValueError(f"压缩包解压字节数超过限制: {expanded} > {ARCHIVE_MAX_BYTES}")
    position = z.fp.tell()
    z.fp.seek(0, os.SEEK_END)
    compressed = z.fp.tell()
    z.fp.seek(position)
    if compressed > ARCHIVE_MAX_BYTES:
        raise ValueError("压缩包文件字节数超过限制")
    seen = set()
    for item in entries:
        path = inside(destination, item.filename)
        canonical = path.relative_to(Path(destination).resolve()).as_posix().casefold()
        if canonical in seen or stat.S_ISLNK(item.external_attr >> 16):
            raise ValueError("压缩包含重复路径或符号链接")
        seen.add(canonical)
        if secret_name(item.filename):
            raise ValueError("压缩包含密钥或数据库文件")
        if item.file_size > ARCHIVE_MAX_FILE_BYTES:
            raise ValueError("压缩包单文件字节数超过限制")
        if item.file_size > max(1, item.compress_size) * ARCHIVE_MAX_RATIO:
            raise ValueError("压缩包压缩比超过限制")
        if item.flag_bits & 1:
            raise ValueError("不接受加密压缩包")
    return entries, {
        "template": template or "generic",
        "entry_count": len(entries),
        "entry_limit": limit,
        "uncompressed_bytes": expanded,
        "compressed_bytes": compressed,
        "byte_limit": ARCHIVE_MAX_BYTES,
        "compression_ratio_limit": ARCHIVE_MAX_RATIO,
    }


def inspect_archive(archive, destination, *, template=None):
    """Producer and consumer use the same bounded preflight, with no writes."""
    with zipfile.ZipFile(archive) as z:
        return _archive_preflight(z, destination, template)[1]


def pack_source(source, archive, *, template=None):
    """Atomically package only distributable sources under the consumer policy."""
    archive = Path(archive)
    if archive.resolve().is_relative_to(Path(source).resolve()):
        raise ValueError("交付压缩包不能写入待打包源码目录")
    fd, name = tempfile.mkstemp(prefix=archive.name + "-", suffix=".tmp", dir=archive.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as z:
            for name, path in files(source):
                z.write(path, name)
        report = inspect_archive(temporary, source, template=template)
        os.replace(temporary, archive)
        return report
    finally:
        temporary.unlink(missing_ok=True)


def unpack(archive, destination, *, template=None):
    with zipfile.ZipFile(archive) as z:
        entries, report = _archive_preflight(z, destination, template)
        # Validate the complete archive before creating even its first file.
        for item in entries:
            path = inside(destination, item.filename)
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item) as src, path.open("wb") as dst:
                    size = 0
                    while block := src.read(1024 * 1024):
                        size += len(block)
                        if size > item.file_size:
                            raise ValueError("压缩包实际解压字节数与声明不符")
                        dst.write(block)
                    if size != item.file_size:
                        raise ValueError("压缩包实际解压字节数与声明不符")
        return report
