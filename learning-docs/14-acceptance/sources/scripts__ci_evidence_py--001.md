# scripts/ci_evidence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_evidence；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `digest`（L33–L36）：接收`value`。 调用`hashlib.sha256( json.dumps(value, ensure_ascii=True, separators=(…`、`hashlib.sha256`、`json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_…`、`json.dumps`。 返回路径：L34的`hashlib.sha256( json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True…`。
- `write_json`（L39–L41）：接收`path`、`value`。 调用`path.parent.mkdir`、`path.write_text`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `read_json`（L44–L53）：接收`path`。 调用`json.loads`、`path.read_text`。 返回路径：L53的`json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)`。
- `read_json.unique`（L45–L51）：接收`pairs`。 控制顺序：L47遍历`pairs`；L48按`key in result`分支；L49抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L51的`result`。
- `run_binding`（L56–L69）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L65按`not re.fullmatch("[0-9a-f]{40}", result["head"]) or any( not re.fullmatch("[1-9][0-9]…`分支；L68抛异常，停止当前正常路径。 调用`os.environ.get`、`re.fullmatch`、`any`、`ValueError`。 返回路径：L69的`result`。
- `safe_name`（L72–L96）：接收`name`。 控制顺序：L73按`not isinstance(name, str) or not name or "\\" in name or ":" in name or any(ord(c) < …`分支；L81抛异常，停止当前正常路径；L83按`any( part in {"", ".", ".."} or part.lower() in FORBIDDEN or part.endswith((".", " ")…`分支；L91抛异常，停止当前正常路径；L92按`ntpath.isreserved(name)`分支；L93抛异常，停止当前正常路径；L94按`PurePosixPath(name).is_absolute()`分支；L95抛异常，停止当前正常路径。 调用`isinstance`、`any`、`ord`、`name.endswith`、`ValueError`、`name.split`、`part.lower`、`part.endswith`、`part.lower().startswith`等。 返回路径：L96的`name`。
- `regular_file`（L99–L111）：接收`root`、`name`。 控制顺序：L101按`root.is_symlink()`分支；L102抛异常，停止当前正常路径；L104遍历`(target, *target.parents)`；L105按`path == root`分支；L107按`path.is_symlink()`分支；L108抛异常，停止当前正常路径；L109按`not target.is_file() or target.stat().st_nlink != 1`分支；L110抛异常，停止当前正常路径。 调用`safe_name`、`root.is_symlink`、`ValueError`、`path.is_symlink`、`target.is_file`、`target.stat`。 返回路径：L111的`target`。
- `create_source_artifact`（L114–L141）：接收`root`、`names`、`output`、`binding`。 源码说明：Only an explicit verified source inventory may cross the clean-room boundary.。 控制顺序：L117按`not names or len(names) > MAX_FILES or len(set(names)) != len(names)`分支；L118抛异常，停止当前正常路径；L119按`len({name.casefold() for name in names}) != len(names)`分支；L120抛异常，停止当前正常路径；L122遍历`names`；L126按`total > MAX_BYTES`分支；L127抛异常，停止当前正常路径；L131遍历`rows`。 调用`sorted`、`len`、`set`、`ValueError`、`name.casefold`、`regular_file(root, name).read_bytes`、`regular_file`、`rows.append`、`hashlib.sha256(data).hexdigest`等。 返回路径：L141的`manifest`。
- `restore_source_artifact`（L144–L215）：接收`artifact`、`destination`、`binding`。 源码说明：Validate every path, size, byte and identity before creating destination files.。 控制顺序：L146按`any(path.is_symlink() for path in (destination, *destination.parents))`分支；L147抛异常，停止当前正常路径；L148按`destination.exists() or destination.is_symlink()`分支；L149抛异常，停止当前正常路径；L151按`not isinstance(manifest, dict) or type(manifest.get("version")) is not int or manifes…`分支；L157抛异常，停止当前正常路径；L159按`not isinstance(rows, list) or not rows or len(rows) > MAX_FILES or digest(rows) != ma…`分支；L165抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`any`、`path.is_symlink`、`ValueError`、`destination.exists`、`destination.is_symlink`、`read_json`、`isinstance`、`type`、`manifest.get`等。 返回路径：L215的`manifest`。

</details>

**创建路径：** `scripts/ci_evidence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L215。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7412`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_evidence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a2e6f622074371647ea7282219f38d422bfba6ac782d26b8fed4b00fcaf49df2"} -->
````python
# scripts/ci_evidence.py
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
````
