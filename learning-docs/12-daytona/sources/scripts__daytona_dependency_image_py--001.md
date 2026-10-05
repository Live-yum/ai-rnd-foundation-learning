# scripts/daytona_dependency_image.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_dependency_image；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_descriptor_roles`（L56–L73）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Data-only policy, mirrored by the isolated standalone build collector.。 返回路径：L58的`{ "runtime": [ "backend/pyproject.toml", "backend/uv.lock", "frontend/web/package.json", "…`。
- `native_runtime_patch_identity`（L76–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Reviewed physical patch identity; no runtime code loading or execution.。 返回路径：L78的`{ "id": "vite-preview-interface-eperm-v1", "package": "vite", "version": "7.3.3", "upstrea…`。
- `validate_runtime_patches`（L87–L118）：接收`patches`、`entries`。 源码说明：Bind the exact patch to its no-follow inventory and public Vite link.。 控制顺序：L90按`type(patches) is not list or len(patches) != 1 or type(patches[0]) is not dict or set…`分支；L99抛异常，停止当前正常路径；L104按`not isinstance(entry, dict) or entry.get("type") != "file" or entry.get("sha256") != …`分支；L112抛异常，停止当前正常路径；L114在`parent.is_relative_to(NATIVE_NODE_ROOT)`成立时循环；L116按`not isinstance(directory, dict) or directory.get("type") != "directory"`分支；L117抛异常，停止当前正常路径。 调用`native_runtime_patch_identity`、`type`、`len`、`set`、`any`、`patches[0].get`、`identity.items`、`VITE_PATCH_PATH.fullmatch`、`ValueError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `canonical`（L121–L122）：接收`value`。 调用`json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_a…`、`json.dumps`。 返回路径：L122的`json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()`。
- `digest`（L125–L126）：接收`value`。 调用`hashlib.sha256(canonical(value)).hexdigest`、`hashlib.sha256`、`canonical`。 返回路径：L126的`hashlib.sha256(canonical(value)).hexdigest()`。
- `file_hash`（L129–L133）：接收`fd`。 控制顺序：L131在`block := os.read(fd, 1024 * 1024)`成立时循环。 调用`hashlib.sha256`、`os.read`、`result.update`、`result.hexdigest`。 返回路径：L133的`result.hexdigest()`。
- `open_absolute`（L136–L153）：接收`path`、`directory`。 源码说明：Open each ancestor O_NOFOLLOW; a real directory is required throughout.。 控制顺序：L139按`not path.is_absolute() or ".." in path.parts`分支；L140抛异常，停止当前正常路径；L143遍历`enumerate(path.parts[1:])`；L145按`directory or index < len(path.parts) - 2`分支；L153抛异常，停止当前正常路径。 调用`Path`、`path.is_absolute`、`ValueError`、`os.open`、`enumerate`、`len`、`os.close`。 返回路径：L150的`fd`。
- `regular_bytes`（L156–L165）：接收`path`。 控制顺序：L160按`not stat.S_ISREG(info.st_mode) or info.st_nlink != 1`分支；L161抛异常，停止当前正常路径。 调用`open_absolute`、`os.fstat`、`stat.S_ISREG`、`ValueError`、`os.fdopen`、`os.dup`、`stream.read`、`os.close`。 返回路径：L163的`stream.read()`。
- `check_ancestors`（L168–L176）：接收`path`。 控制顺序：L169遍历`reversed(Path(path).parents)`；L173按`info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022`分支；L174抛异常，停止当前正常路径。 调用`reversed`、`Path`、`open_absolute`、`os.fstat`、`ValueError`、`os.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `inventory`（L179–L229）：接收`roots`、`readonly`。 源码说明：Inventory all entries using directory FDs; reject devices and hardlinks.。 控制顺序：L220遍历`roots`；L221按`readonly`分支。 调用`check_ancestors`、`open_absolute`、`Path`、`visit`、`str`、`os.close`、`validate_links`、`dict`、`sorted`等。 返回路径：L229的`dict(sorted(entries.items()))`。
- `inventory.visit`（L183–L218）：接收`parent`、`name`、`absolute`。 控制顺序：L187按`info.st_mode & 0o6000`分支；L188抛异常，停止当前正常路径；L189按`readonly and (info.st_uid != 0 or info.st_gid != 0)`分支；L190抛异常，停止当前正常路径；L191按`stat.S_ISLNK(info.st_mode)`分支；L192按`info.st_nlink != 1`分支；L193抛异常，停止当前正常路径；L196按`readonly and mode & 0o022`分支。后续分支沿下方源码相同行号继续阅读。 调用`os.stat`、`stat.S_IMODE`、`ValueError`、`stat.S_ISLNK`、`entry.update`、`os.readlink`、`stat.S_ISREG`、`stat.S_ISDIR`、`os.open`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_links`（L232–L258）：接收`entries`、`roots`。 控制顺序：L256遍历`entries.items()`；L257按`entry["type"] == "symlink"`分支。 调用`entries.items`、`resolve`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_links.permitted`（L233–L234）：接收`value`。 调用`any`、`value.startswith`。 返回路径：L234的`any(value == root or value.startswith(root + "/") for root in roots)`。
- `validate_links.resolve`（L236–L254）：接收`value`。 控制顺序：L237遍历`range(41)`；L238按`not permitted(value)`分支；L239抛异常，停止当前正常路径；L241遍历`range(2, len(parts) + 1)`；L244按`entry and entry["type"] == "symlink"`分支；L251按`value not in entries`分支；L252抛异常，停止当前正常路径；L254抛异常，停止当前正常路径。 调用`range`、`permitted`、`ValueError`、`value.split`、`len`、`"/".join`、`entries.get`、`posixpath.normpath`、`posixpath.join`等。 返回路径：L253的`value`。
- `seal`（L261–L299）：接收`roots`、`runtime_patches`。 源码说明：Run only after the builder exited, with no app process sharing this layer.。 控制顺序：L264按`NATIVE_NODE_ROOT in roots`分支；L293遍历`roots`。 调用`inventory`、`validate_runtime_patches`、`open_absolute`、`Path`、`visit`、`os.close`。 返回路径：L299的`inventory(roots)`。
- `seal.visit`（L267–L291）：接收`parent`、`name`。 控制顺序：L269按`stat.S_ISLNK(info.st_mode)`分支；L273按`stat.S_ISDIR(info.st_mode)`分支；L278按`(opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)`分支；L279抛异常，停止当前正常路径；L280按`stat.S_ISDIR(info.st_mode)`分支；L281遍历`sorted(os.listdir(fd))`；L283按`not stat.S_ISREG(info.st_mode) or info.st_nlink != 1`分支；L284抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`os.stat`、`stat.S_ISLNK`、`os.chown`、`stat.S_ISDIR`、`os.open`、`os.fstat`、`ValueError`、`sorted`、`os.listdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_manifest`（L302–L382）：接收`value`、`profile`。 控制顺序：L303按`not isinstance(value, dict) or set(value) != {"schema", "profiles"} or type(value.get…`分支；L313抛异常，停止当前正常路径；L332按`profile == "fastapiadmin"`分支；L334按`not isinstance(record, dict) or not required <= set(record) or set(record) - required…`分支；L347抛异常，停止当前正常路径；L348遍历`("original_descriptors", "normalized_descriptors")`；L350按`not isinstance(descriptors, dict) or not descriptors`分支；L351抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`set`、`type`、`value.get`、`ValueError`、`value["profiles"].get`、`required.update`、`record.get`、`HEX.fullmatch`等。 返回路径：L382的`record`。
- `inspect_manifest`（L385–L396）：接收`profile`、`path`、`verify_tree`。 控制顺序：L389按`verify_tree`分支；L392按`info.st_uid or info.st_gid or info.st_mode & 0o022`分支；L393抛异常，停止当前正常路径；L394按`inventory(record["roots"]) != record["entries"]`分支；L395抛异常，停止当前正常路径。 调用`regular_bytes`、`Path(path).absolute`、`Path`、`json.loads`、`validate_manifest`、`check_ancestors`、`Path(path).lstat`、`ValueError`、`inventory`。 返回路径：L396的`raw, record`。
- `receipt`（L399–L417）：接收`profile`、`product`、`path`。 控制顺序：L401按`product is not None`分支；L402遍历`record["original_descriptors"].items()`；L403按`hashlib.sha256(regular_bytes(Path(product).absolute() / name)).hexdigest() != expecte…`分支；L407抛异常，停止当前正常路径。 调用`inspect_manifest`、`record["original_descriptors"].items`、`hashlib.sha256(regular_bytes(Path(product).absolute() / name)).he…`、`hashlib.sha256`、`regular_bytes`、`Path(product).absolute`、`Path`、`ValueError`、`hashlib.sha256(raw).hexdigest`。 返回路径：L408的`{ "schema": 1, "profile": profile, "manifest_sha256": hashlib.sha256(raw).hexdigest(), "in…`。
- `create`（L420–L440）：接收`profile`、`inputs`、`path`。 控制顺序：L428按`profile == "fastapiadmin"`分支。 调用`Path(path).exists`、`Path`、`json.loads`、`Path(path).read_bytes`、`dict`、`record.update`、`inventory`、`digest`、`validate_manifest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L443–L489）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L453按`args.action == "seal-build-tools"`分支；L459按`args.action == "seal"`分支；L462按`args.action == "create"`分支；L464按`args.action == "verify-runtime"`分支；L465按`args.product is None`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`list`、`parser.parse_args`、`seal`、`Path("/opt/rnd/build-tools-manifest.json").write_bytes`、`Path`、`canonical`、`digest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_dependency_image.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L493。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19237`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_dependency_image.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f4e7f2fd6af02b846286f8f89f639d8717c2bc2406f8eeb712c790ba95c42360"} -->
````python
# scripts/daytona_dependency_image.py
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
NATIVE_NODE_ROOT = "/opt/rnd/runtime/fastapiadmin/frontend/node_modules"
VITE_PATCH_PATH = re.compile(
    r"\.pnpm/vite@7\.3\.3(?:_[A-Za-z0-9@+_.-]+)?/node_modules/vite/dist/node/chunks/config\.js"
)
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


def native_runtime_patch_identity():
    """Reviewed physical patch identity; no runtime code loading or execution."""
    return {
        "id": "vite-preview-interface-eperm-v1",
        "package": "vite",
        "version": "7.3.3",
        "upstream_sha256": "339ee4656b2ca976ca320b48cffba04361f91ad0899a32a1c60ba9b2910e772e",
        "patched_sha256": "8df548e7d1456f542321e05139faec50f23f15e64afc5a434c57583308bcc86e",
    }


def validate_runtime_patches(patches, entries):
    """Bind the exact patch to its no-follow inventory and public Vite link."""
    identity = native_runtime_patch_identity()
    if (
        type(patches) is not list
        or len(patches) != 1
        or type(patches[0]) is not dict
        or set(patches[0]) != {*identity, "relative_path"}
        or any(patches[0].get(key) != value for key, value in identity.items())
        or type(patches[0].get("relative_path")) is not str
        or not VITE_PATCH_PATH.fullmatch(patches[0]["relative_path"])
    ):
        raise ValueError("Missing or incompatible native runtime patch identity")
    relative = patches[0]["relative_path"]
    physical = NATIVE_NODE_ROOT + "/" + relative
    entry = entries.get(physical)
    vite = entries.get(NATIVE_NODE_ROOT + "/vite")
    if (
        not isinstance(entry, dict)
        or entry.get("type") != "file"
        or entry.get("sha256") != identity["patched_sha256"]
        or not isinstance(vite, dict)
        or vite.get("type") != "symlink"
        or vite.get("target") != relative.removesuffix("/dist/node/chunks/config.js")
    ):
        raise ValueError("Native runtime patch file or Vite link differs")
    parent = PurePosixPath(physical).parent
    while parent.is_relative_to(NATIVE_NODE_ROOT):
        directory = entries.get(str(parent))
        if not isinstance(directory, dict) or directory.get("type") != "directory":
            raise ValueError("Native runtime patch path is not a physical directory")
        parent = parent.parent


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


def seal(roots, *, runtime_patches=None):
    """Run only after the builder exited, with no app process sharing this layer."""
    entries = inventory(roots, readonly=False)
    if NATIVE_NODE_ROOT in roots:
        validate_runtime_patches(runtime_patches, entries)

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
        required.update({"descriptor_roles", "runtime_patches"})
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
        validate_runtime_patches(record["runtime_patches"], record["entries"])
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
        **({"runtime_patches": record["runtime_patches"]} if profile == "fastapiadmin" else {}),
    }


def create(profile, inputs, *, path=MANIFEST):
    value = (
        json.loads(Path(path).read_bytes())
        if Path(path).exists()
        else {"schema": 1, "profiles": {}}
    )
    record = dict(inputs)
    record.update(roots=ROOTS[profile], groups=GROUPS[profile])
    if profile == "fastapiadmin":
        # Validate builder-supplied identities against actual no-follow file
        # hashes before the first privileged ownership or permission change.
        record["entries"] = inventory(record["roots"], readonly=False)
        record["installed_tree_sha256"] = digest(record["entries"])
        value["profiles"][profile] = record
        validate_manifest(value, profile)
    record["entries"] = seal(record["roots"], runtime_patches=record.get("runtime_patches"))
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
        inputs = json.loads(regular_bytes(args.inputs.absolute())) if args.inputs else {}
        seal(ROOTS[args.profile], runtime_patches=inputs.get("runtime_patches"))
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
                        {
                            "descriptor_roles": record["descriptor_roles"],
                            "runtime_patches": record["runtime_patches"],
                        }
                        if args.profile == "fastapiadmin"
                        else {}
                    ),
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
````
