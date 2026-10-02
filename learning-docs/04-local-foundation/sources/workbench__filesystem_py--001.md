# workbench/filesystem.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：限定文件路径、归档成员和写入范围。** inside在读取或写入前确认路径属于工作目录；files过滤凭据和运行目录；manifest逐文件算SHA，防止源码改了却使用旧索引；unpack拒绝越界和特殊文件；atomic_text用临时文件完成替换。

**对应关系：** knowledge/retrieval/aider_tool/sandbox/打包共用；test_safety、test_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `secret_name`（L27–L46）：接收`path`。 调用`Path(path).name.lower`、`Path`、`name.startswith`、`name.endswith`。 返回路径：L29的`name == ".env" or (name.startswith(".env.") and not name.endswith(".example")) or name.sta…`。
- `inside`（L49–L61）：接收`root`、`relative`。 控制顺序：L52按`p.is_absolute() or ".." in p.parts or any(":" in part for part in p.parts)`分支；L53抛异常，停止当前正常路径；L56遍历`p.parts`；L58按`current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction())`分支；L59抛异常，停止当前正常路径。 调用`Path(root).resolve`、`Path`、`PurePosixPath`、`str(relative).replace`、`str`、`p.is_absolute`、`any`、`ValueError`、`root.joinpath`等。 返回路径：L61的`candidate`。
- `atomic_text`（L64–L76）：接收`path`、`content`。 控制顺序：L75按`os.path.exists(temporary)`分支。 调用`Path`、`path.parent.mkdir`、`tempfile.mkstemp`、`os.fdopen`、`f.write`、`f.flush`、`os.fsync`、`f.fileno`、`os.replace`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `write_json`（L79–L80）：接收`path`、`data`。 调用`atomic_text`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `sha`（L83–L85）：接收`path`。 调用`Path(path).open`、`Path`、`hashlib.file_digest(f, "sha256").hexdigest`、`hashlib.file_digest`。 返回路径：L85的`hashlib.file_digest(f, "sha256").hexdigest()`。
- `files`（L88–L103）：接收`root`。 控制顺序：L90遍历`os.walk(root, followlinks=False)`；L92遍历`dirs`；L94遍历`sorted(names)`；L97按`secret_name(relative) or name.startswith(".writing-")`分支；L99按`not stat.S_ISREG(path.stat().st_mode)`分支；L100抛异常，停止当前正常路径；L101按`path.stat().st_size > 32_000_000`分支；L102抛异常，停止当前正常路径。 调用`Path(root).resolve`、`Path`、`os.walk`、`sorted`、`inside`、`(Path(base) / directory).relative_to(root).as_posix`、`(Path(base) / directory).relative_to`、`(Path(base) / name).relative_to(root).as_posix`、`(Path(base) / name).relative_to`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `manifest`（L106–L107）：接收`root`。 调用`sha`、`files`。 返回路径：L107的`{name: sha(path) for name, path in files(root)}`。
- `archive_entry_limit`（L115–L124）：接收`template`。 源码说明：Caller-selected trusted template, never a value read from archive content. The pinned Yudao monorepo alone contains over 12,000 source files. Its source importer already uses a bounded 25,000-entry po。 控制顺序：L122按`template not in {None, "python-basic", "fastapiadmin", "yudao-vben"}`分支；L123抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L124的`25000 if template == "yudao-vben" else 10000`。
- `_archive_preflight`（L127–L164）：接收`z`、`destination`、`template`。 控制顺序：L131按`len(entries) > limit`分支；L132抛异常，停止当前正常路径；L133按`expanded > ARCHIVE_MAX_BYTES`分支；L134抛异常，停止当前正常路径；L139按`compressed > ARCHIVE_MAX_BYTES`分支；L140抛异常，停止当前正常路径；L142遍历`entries`；L145按`canonical in seen or stat.S_ISLNK(item.external_attr >> 16)`分支。后续分支沿下方源码相同行号继续阅读。 调用`z.infolist`、`archive_entry_limit`、`sum`、`len`、`ValueError`、`z.fp.tell`、`z.fp.seek`、`set`、`inside`等。 返回路径：L156的`entries, { "template": template or "generic", "entry_count": len(entries), "entry_limit": …`。
- `inspect_archive`（L167–L170）：接收`archive`、`destination`、`template`。 源码说明：Producer and consumer use the same bounded preflight, with no writes.。 调用`zipfile.ZipFile`、`_archive_preflight`。 返回路径：L170的`_archive_preflight(z, destination, template)[1]`。
- `pack_source`（L173–L189）：接收`source`、`archive`、`template`。 源码说明：Atomically package only distributable sources under the consumer policy.。 控制顺序：L176按`archive.resolve().is_relative_to(Path(source).resolve())`分支；L177抛异常，停止当前正常路径；L183遍历`files(source)`。 调用`Path`、`archive.resolve().is_relative_to`、`archive.resolve`、`Path(source).resolve`、`ValueError`、`tempfile.mkstemp`、`os.close`、`zipfile.ZipFile`、`files`等。 返回路径：L187的`report`。
- `unpack`（L192–L211）：接收`archive`、`destination`、`template`。 控制顺序：L196遍历`entries`；L198按`item.is_dir()`分支；L204在`block := src.read(1024 * 1024)`成立时循环；L206按`size > item.file_size`分支；L207抛异常，停止当前正常路径；L209按`size != item.file_size`分支；L210抛异常，停止当前正常路径。 调用`zipfile.ZipFile`、`_archive_preflight`、`inside`、`item.is_dir`、`path.mkdir`、`path.parent.mkdir`、`z.open`、`path.open`、`src.read`等。 返回路径：L211的`report`。

</details>

**创建路径：** `workbench/filesystem.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L211。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7652`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/filesystem.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "969e5f1184239abef61b57915fb6c7d746245631d25bcbf5db995b33c9f82790"} -->
````python
# workbench/filesystem.py
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
````
