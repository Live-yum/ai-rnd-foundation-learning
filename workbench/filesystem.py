"""File boundaries, atomic writes, deterministic hashes, and safe ZIP extraction."""
import hashlib
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

EXCLUDED_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", ".data", "target", "dist"}


def secret_name(path):
    name = Path(path).name.lower()
    return (name == ".env" or (name.startswith(".env.") and not name.endswith(".example"))
            or name.endswith((".pem", ".key", ".p12", ".pfx", ".db", ".db-wal", ".db-shm"))
            or name in {"access-token", "id_rsa", "id_ed25519", "credentials.json"})


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
            if path.stat().st_size > 5_000_000:
                raise ValueError(f"文件超过 5 MB 限制: {relative}")
            yield relative, path


def manifest(root):
    return {name: sha(path) for name, path in files(root)}


def unpack(archive, destination):
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        if len(entries) > 10000 or sum(e.file_size for e in entries) > 200_000_000:
            raise ValueError("压缩包解压后超过限制")
        seen = set()
        for item in entries:
            path = inside(destination, item.filename)
            if item.filename in seen or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("压缩包含重复路径或符号链接")
            seen.add(item.filename)
            if secret_name(item.filename):
                raise ValueError("压缩包含密钥或数据库文件")
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item) as src, path.open("wb") as dst:
                    import shutil
                    shutil.copyfileobj(src, dst)
