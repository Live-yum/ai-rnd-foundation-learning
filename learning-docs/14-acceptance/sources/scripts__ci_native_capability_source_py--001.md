# scripts/ci_native_capability_source.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_native_capability_source；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_dependency_build`、`scripts.daytona_native_capability_profile`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ordinary_path`（L28–L36）：接收`path`。 源码说明：Do not resolve away a linked root or any linked parent.。 控制顺序：L30按`".." in Path(path).parts`分支；L31抛异常，停止当前正常路径；L33遍历`[*reversed(path.parents), path]`；L34按`entry.is_symlink() or (hasattr(entry, "is_junction") and entry.is_junction())`分支；L35抛异常，停止当前正常路径。 调用`Path`、`ValueError`、`Path(path).absolute`、`reversed`、`entry.is_symlink`、`hasattr`、`entry.is_junction`。 返回路径：L36的`path`。
- `directory_fd`（L40–L58）：接收`path`、`create`。 源码说明：Open every ancestor without following links, including the root argument.。 控制顺序：L42按`not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")`分支；L43抛异常，停止当前正常路径；L47遍历`path.parts[1:]`；L48按`create`分支。 调用`hasattr`、`ValueError`、`ordinary_path`、`os.open`、`os.mkdir`、`os.close`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `file_identity`（L61–L70）：接收`value`。 返回路径：L62的`( value.st_dev, value.st_ino, value.st_mode, value.st_nlink, value.st_size, value.st_mtime…`。
- `read_regular`（L73–L93）：接收`directory`、`name`、`expected`。 控制顺序：L77按`not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > 32_000_0…`分支；L84抛异常，停止当前正常路径；L86按`len(data) != before.st_size or file_identity(os.fstat(source.fileno())) != file_ident…`分支；L92抛异常，停止当前正常路径。 调用`os.open`、`os.fdopen`、`os.fstat`、`source.fileno`、`stat.S_ISREG`、`file_identity`、`ValueError`、`source.read`、`len`等。 返回路径：L93的`data`。
- `validate_inventory`（L96–L126）：接收`inventory`。 控制顺序：L97按`type(inventory) is not dict or not inventory or len(inventory) > 10000`分支；L98抛异常，停止当前正常路径；L100遍历`inventory.items()`；L102按`path is None or not name or path.as_posix() != name or path.is_absolute() or ".." in …`分支；L120抛异常，停止当前正常路径；L124按`len(canonical_directories) != len(directories) or canonical_directories & canonical`分支；L125抛异常，停止当前正常路径。 调用`type`、`len`、`ValueError`、`set`、`inventory.items`、`PurePosixPath`、`path.as_posix`、`path.is_absolute`、`any`等。 返回路径：L126的`directories`。
- `require_exact_source`（L129–L166）：接收`product`、`inventory`。 源码说明：Inspect every physical entry; no ignore patterns or excluded subtrees.。 控制顺序：L133按`not product.is_dir()`分支；L134抛异常，停止当前正常路径；L141遍历`os.fwalk( ".", dir_fd=root, follow_symlinks=False, onerror=walk_e…`；L144遍历`sorted([*dirs, *names])`；L147按`stat.S_ISDIR(mode.st_mode)`分支；L148按`relative not in directories`分支；L149抛异常，停止当前正常路径；L153按`stat.S_ISREG(mode.st_mode) and mode.st_nlink == 1`分支。后续分支沿下方源码相同行号继续阅读。 调用`validate_inventory`、`ordinary_path`、`product.is_dir`、`ValueError`、`set`、`directory_fd`、`os.fwalk`、`sorted`、`(PurePosixPath(base) / name).as_posix`等。 返回路径：L166的`inventory`。
- `require_exact_source.walk_error`（L137–L138）：接收`error`。 控制顺序：L138抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `copy_exact_source`（L169–L194）：接收`source`、`destination`、`inventory`。 源码说明：A new physical copy of an independently verified clean source, never a filter.。 控制顺序：L173按`destination.is_relative_to(source) or source.is_relative_to(destination)`分支；L174抛异常，停止当前正常路径；L177遍历`sorted(inventory)`；L181按`hashlib.sha256(data).hexdigest() != inventory[name]`分支；L182抛异常，停止当前正常路径。 调用`ordinary_path`、`require_exact_source`、`destination.is_relative_to`、`source.is_relative_to`、`ValueError`、`directory_fd`、`os.mkdir`、`sorted`、`PurePosixPath`等。 返回路径：L194的`destination`。
- `descriptors`（L197–L202）：接收`inventory`。 控制顺序：L200按`set(observed) != set(DESCRIPTORS)`分支；L201抛异常，停止当前正常路径。 调用`inventory.items`、`Path`、`set`、`ValueError`。 返回路径：L202的`observed`。
- `run_identity`（L205–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Bind GitHub runs/attempts; local runs instead rely on fresh exclusive output.。 调用`os.environ.get`。 返回路径：L207的`{ name: os.environ.get(name, "") for name in ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_A…`。
- `SourceHandoff`（L213–L273）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SourceHandoff.__init__`（L214–L224）：接收`product`、`receipt`。 控制顺序：L216按`self.receipt.is_relative_to(self.product)`分支；L217抛异常，停止当前正常路径；L220按`self.product.exists()`分支；L221抛异常，停止当前正常路径。 调用`ordinary_path`、`self.receipt.is_relative_to`、`ValueError`、`write_json`、`self.product.exists`、`FileExistsError`、`run_identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `SourceHandoff.capture`（L226–L235）：接收`clean_product`、`inventory`、`archive_sha256`。 控制顺序：L227按`self.inventory is not None`分支；L228抛异常，停止当前正常路径；L229按`type(archive_sha256) is not str or not re.fullmatch(r"[a-f0-9]{64}", archive_sha256)`分支；L230抛异常，停止当前正常路径。 调用`ValueError`、`type`、`re.fullmatch`、`dict`、`descriptors`、`copy_exact_source`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `SourceHandoff.complete`（L237–L273）：接收`report`、`original_product`。 控制顺序：L240按`self.inventory is None or self.run != run_identity() or report.get("generated_runtime…`分支；L258抛异常，停止当前正常路径。 调用`report.get`、`restored.get`、`run_identity`、`any`、`type`、`re.fullmatch`、`manifest`、`ValueError`、`require_exact_source`等。 返回路径：L273的`value`。
- `validate_receipt`（L276–L310）：接收`value`、`product`。 控制顺序：L278按`type(value) is not dict or set(value) != { "schema", "passed", "provenance", "product…`分支；L303抛异常，停止当前正常路径；L306按`value["source_identity"] != digest(inventory) or value["descriptors"] != descriptors(…`分支；L309抛异常，停止当前正常路径。 调用`ordinary_path`、`type`、`set`、`value.get`、`str`、`run_identity`、`native_descriptor_roles`、`re.fullmatch`、`ValueError`等。 返回路径：L310的`value`。
- `require_handoff`（L313–L331）：接收`product`、`receipt`。 控制顺序：L326按`mode.st_size > 8_000_000`分支；L327抛异常，停止当前正常路径。 调用`ordinary_path`、`directory_fd`、`os.stat`、`ValueError`、`json.loads`、`read_regular`、`validate_receipt`、`require_exact_source`。 返回路径：L331的`value`。
- `require_handoff.unique_pairs`（L316–L322）：接收`pairs`。 控制顺序：L318遍历`pairs`；L319按`key in result`分支；L320抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L322的`result`。
- `main`（L334–L340）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`require_handoff`、`print`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_capability_source.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L344。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14207`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_capability_source.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8a5e04677e9bf426bd24928740fc590968a2454fb41832103e1b86cdf98ae720"} -->
````python
# scripts/ci_native_capability_source.py
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

from scripts.daytona_dependency_build import native_descriptor_roles
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
        raise ValueError("CI source handoff requires exactly the eleven native source descriptors")
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
            "descriptor_roles": native_descriptor_roles(),
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
            "descriptor_roles",
            "run",
        }
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or value.get("passed") is not True
        or value.get("provenance") != PROVENANCE
        or value.get("product") != str(product)
        or value.get("run") != run_identity()
        or value.get("descriptor_roles") != native_descriptor_roles()
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
````
