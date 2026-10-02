# scripts/rebuild_learning_docs.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.rebuild_learning_docs；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `sha`（L24–L25）：接收`data`。 调用`hashlib.sha256(data).hexdigest`、`hashlib.sha256`。 返回路径：L25的`hashlib.sha256(data).hexdigest()`。
- `safe_path`（L28–L44）：接收`name`。 控制顺序：L29按`not isinstance(name, str)`分支；L30抛异常，停止当前正常路径；L32按`not name or path.is_absolute() or path.as_posix() != name or ".." in path.parts or ".…`分支；L43抛异常，停止当前正常路径。 调用`isinstance`、`ValueError`、`PurePosixPath`、`path.is_absolute`、`path.as_posix`、`any`、`ord`。 返回路径：L44的`path`。
- `comment_line`（L47–L59）：接收`name`、`language`。 控制顺序：L49按`language in {"html", "vue", "markdown", "xml"}`分支；L51按`language in {"javascript", "typescript", "java", "json", "jsonc"}`分支；L53按`language == "css"`分支；L55按`language == "sql"`分支；L57按`language == "ini"`分支。 调用`safe_path`。 返回路径：L50的`f"<!-- {name} -->"`；L52的`f"// {name}"`；L54的`f"/* {name} */"`。
- `annotation`（L62–L67）：接收`line`。 控制顺序：L63遍历`COMMENTS`；L64按`match := pattern.fullmatch(line)`分支；L67抛异常，停止当前正常路径。 调用`pattern.fullmatch`、`safe_path`、`ValueError`。 返回路径：L66的`match[1]`。
- `parse_document`（L70–L111）：接收`text`。 源码说明：Scan real top-level fences; nested source examples remain uninterpreted bytes.。 控制顺序：L74在`index < len(lines)`成立时循环；L77按`not match`分支；L78按`line.lstrip().startswith(MARKER)`分支；L83按`fence[0] == "`" and "`" in info`分支；L92在`index < len(lines) and not closing.fullmatch(lines[index].rstrip(…`成立时循环；L94按`index == len(lines)`分支；L95抛异常，停止当前正常路径；L97按`not body`分支。后续分支沿下方源码相同行号继续阅读。 调用`text.splitlines`、`len`、`lines[index].rstrip`、`OPEN.fullmatch`、`line.lstrip().startswith`、`line.lstrip`、`markers.append`、`match.groups`、`info.strip`等。 返回路径：L111的`records, markers`。
- `fences`（L114–L115）：接收`text`。 调用`parse_document`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `check_fences`（L118–L119）：接收`text`。 调用`sum`、`fences`。 返回路径：L119的`sum(1 for _ in fences(text))`。
- `regular_inside`（L122–L133）：接收`root`、`relative`。 控制顺序：L125按`root.is_symlink() or any(parent.is_symlink() for parent in root.absolute().parents)`分支；L126抛异常，停止当前正常路径；L127遍历`parts`；L129按`candidate.is_symlink()`分支；L130抛异常，停止当前正常路径；L131按`not candidate.is_file()`分支；L132抛异常，停止当前正常路径。 调用`safe_path`、`root.is_symlink`、`any`、`parent.is_symlink`、`root.absolute`、`ValueError`、`candidate.is_symlink`、`candidate.is_file`。 返回路径：L133的`candidate`。
- `read_manifest`（L136–L148）：接收`folder`。 控制顺序：L139按`not isinstance(document, dict) or type(document.get("format")) is not int or document…`分支；L145抛异常，停止当前正常路径；L146按`not document["files"]`分支；L147抛异常，停止当前正常路径。 调用`Path`、`json.loads`、`regular_inside(folder, "manifest.json").read_text`、`regular_inside`、`isinstance`、`type`、`document.get`、`ValueError`。 返回路径：L148的`document`。
- `read_bundle`（L151–L250）：接收`folder`。 控制顺序：L155遍历`document["files"]`；L156按`not isinstance(row, dict) or not {"path", "sha256", "bytes", "stage", "parts"} <= row…`分支；L160抛异常，停止当前正常路径；L161按`not isinstance(row["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]…`分支；L167抛异常，停止当前正常路径；L170按`name in rows or safe_path(name).parts[0] == LEDGER`分支；L171抛异常，停止当前正常路径；L172按`not isinstance(row["stage"], str) or not re.fullmatch( r"[0-9]{2}-[a-z0-9-]+", row["s…`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`read_manifest`、`set`、`isinstance`、`row.keys`、`ValueError`、`re.fullmatch`、`type`、`safe_path`等。 返回路径：L250的`rows`。
- `ensure_safe_target`（L253–L261）：接收`destination`、`name`。 控制顺序：L255遍历`safe_path(name).parts`；L257按`candidate.is_symlink()`分支；L258抛异常，停止当前正常路径；L259按`candidate != destination / name and candidate.exists() and not candidate.is_dir()`分支；L260抛异常，停止当前正常路径。 调用`safe_path`、`candidate.is_symlink`、`ValueError`、`candidate.exists`、`candidate.is_dir`。 返回路径：L261的`candidate`。
- `restore`（L264–L324）：接收`folder`、`destination`、`through`、`advance`。先验证所有源码块与目标路径，再向空目录写入；这一步本身不执行任何写出的项目代码。 控制顺序：L269按`through is not None`分支；L271按`len(matches) != 1`分支；L272抛异常，停止当前正常路径；L279按`destination.is_symlink() or (destination.exists() and not destination.is_dir())`分支；L280抛异常，停止当前正常路径；L282按`any(parent.is_symlink() for parent in destination.absolute().parents)`分支；L283抛异常，停止当前正常路径；L285按`destination.exists() and any(destination.iterdir())`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`read_bundle`、`read_manifest`、`len`、`ValueError`、`destination.is_symlink`、`destination.exists`、`destination.is_dir`、`any`等。 返回路径：L324的`len(selected)`。
- `main`（L327–L343）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L335按`args.check`分支；L337按`args.destination is None`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`Path(__file__).resolve`、`Path`、`parser.parse_args`、`print`、`len`、`read_bundle`、`parser.error`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/rebuild_learning_docs.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L347。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13973`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/rebuild_learning_docs.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "157a029a2305ad664e40990f9ad18a8e0da2db796e800c9998381f65d25b01e9"} -->
````python
# scripts/rebuild_learning_docs.py
"""Restore a staged textbook using only Python's standard library; never execute source."""

import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

MARKER = "<!-- learning-source: "
OPEN = re.compile(r"^( {0,3})(`{3,}|~{3,})([^\r\n]*)$")
COMMENTS = (
    re.compile(r"^# (.+)$"),
    re.compile(r"^// (.+)$"),
    re.compile(r"^-- (.+)$"),
    re.compile(r"^; (.+)$"),
    re.compile(r"^<!-- (.+) -->$"),
    re.compile(r"^/\* (.+) \*/$"),
)
LEDGER = ".learning-progress.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    if not isinstance(name, str):
        raise ValueError("Path must be a string")
    path = PurePosixPath(name)
    if (
        not name
        or path.is_absolute()
        or path.as_posix() != name
        or ".." in path.parts
        or ".git" in path.parts
        or ":" in name
        or "\\" in name
        or any(ord(char) < 32 for char in name)
        or name == "."
    ):
        raise ValueError("Unsafe relative path: " + name)
    return path


def comment_line(name, language):
    safe_path(name)
    if language in {"html", "vue", "markdown", "xml"}:
        return f"<!-- {name} -->"
    if language in {"javascript", "typescript", "java", "json", "jsonc"}:
        return f"// {name}"
    if language == "css":
        return f"/* {name} */"
    if language == "sql":
        return f"-- {name}"
    if language == "ini":
        return f"; {name}"
    return f"# {name}"


def annotation(line):
    for pattern in COMMENTS:
        if match := pattern.fullmatch(line):
            safe_path(match[1])
            return match[1]
    raise ValueError("Every fenced block must start with a relative-path comment")


def parse_document(text):
    """Scan real top-level fences; nested source examples remain uninterpreted bytes."""
    lines = text.splitlines(keepends=True)
    index, records, markers = 0, [], []
    while index < len(lines):
        line = lines[index].rstrip("\r\n")
        match = OPEN.fullmatch(line)
        if not match:
            if line.lstrip().startswith(MARKER):
                markers.append(line)
            index += 1
            continue
        indentation, fence, info = match.groups()
        if fence[0] == "`" and "`" in info:
            # CommonMark forbids backticks in a backtick-fence info string.
            index += 1
            continue
        language = info.strip().split()[0] if info.strip() else ""
        opening = index
        index += 1
        start = index
        closing = re.compile(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$")
        while index < len(lines) and not closing.fullmatch(lines[index].rstrip("\r\n")):
            index += 1
        if index == len(lines):
            raise ValueError("Unclosed Markdown fence")
        body = "".join(lines[start:index])
        if not body:
            raise ValueError("A fenced block has no path annotation")
        first, separator, rest = body.partition("\n")
        if not separator:
            raise ValueError("A fenced block has no content separator")
        first = first.rstrip("\r")
        if indentation:
            first = first[min(len(first) - len(first.lstrip(" ")), len(indentation)) :]
        name = annotation(first)
        if first != comment_line(name, language):
            raise ValueError("Wrong comment syntax for fenced language: " + language)
        previous = lines[opening - 1].rstrip("\r\n") if opening else ""
        records.append((previous, language, name, rest))
        index += 1
    return records, markers


def fences(text):
    yield from parse_document(text)[0]


def check_fences(text):
    return sum(1 for _ in fences(text))


def regular_inside(root, relative):
    parts = safe_path(relative).parts
    candidate = root
    if root.is_symlink() or any(parent.is_symlink() for parent in root.absolute().parents):
        raise ValueError("Symlink root or ancestor is forbidden")
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("Symlink path is forbidden: " + relative)
    if not candidate.is_file():
        raise ValueError("Missing regular file: " + relative)
    return candidate


def read_manifest(folder):
    folder = Path(folder)
    document = json.loads(regular_inside(folder, "manifest.json").read_text(encoding="utf-8"))
    if (
        not isinstance(document, dict)
        or type(document.get("format")) is not int
        or document["format"] != 1
        or not isinstance(document.get("files"), list)
    ):
        raise ValueError("Unsupported learning manifest")
    if not document["files"]:
        raise ValueError("Empty learning manifest")
    return document


def read_bundle(folder):
    folder = Path(folder)
    document = read_manifest(folder)
    rows, documents = {}, set()
    for row in document["files"]:
        if (
            not isinstance(row, dict)
            or not {"path", "sha256", "bytes", "stage", "parts"} <= row.keys()
        ):
            raise ValueError("Incomplete source manifest row")
        if (
            not isinstance(row["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
            or type(row["bytes"]) is not int
            or row["bytes"] < 0
        ):
            raise ValueError("Invalid source hash or byte count")
        name = row["path"]
        safe_path(name)
        if name in rows or safe_path(name).parts[0] == LEDGER:
            raise ValueError("Duplicate or reserved source path: " + name)
        if not isinstance(row["stage"], str) or not re.fullmatch(
            r"[0-9]{2}-[a-z0-9-]+", row["stage"]
        ):
            raise ValueError("Invalid stage")
        if not isinstance(row["parts"], list) or not row["parts"]:
            raise ValueError("Missing source parts: " + name)
        chunks = []
        for number, relative in enumerate(row["parts"], 1):
            document_path = safe_path(relative)
            if (
                document_path.parts[:2] != (row["stage"], "sources")
                or document_path.suffix != ".md"
            ):
                raise ValueError("Source document is outside its declared stage")
            if relative in documents:
                raise ValueError("Duplicate source document: " + relative)
            documents.add(relative)
            text = regular_inside(folder, relative).read_bytes().decode("utf-8")
            all_records, markers = parse_document(text)
            records = [item for item in all_records if item[0].startswith(MARKER)]
            if len(records) != 1 or len(markers) != 1:
                raise ValueError("Missing or duplicate source record: " + relative)
            marker, language, annotated, payload = records[0]
            if not marker.endswith(" -->"):
                raise ValueError("Malformed source marker")
            meta = json.loads(marker[len(MARKER) : -4])
            if (
                not isinstance(meta, dict)
                or meta.get("path") != name
                or annotated != name
                or type(meta.get("part")) is not int
                or type(meta.get("parts")) is not int
                or meta.get("part") != number
                or meta.get("parts") != len(row["parts"])
                or meta.get("encoding") not in ("utf-8", "base64")
            ):
                raise ValueError("Source chunk identity mismatch: " + relative)
            if meta["encoding"] == "base64":
                if language != "base64":
                    raise ValueError("Binary source has wrong language")
                try:
                    chunk = base64.b64decode(payload.replace("\n", ""), validate=True)
                except (ValueError, binascii.Error) as exc:
                    raise ValueError("Invalid base64: " + name) from exc
                candidates = [chunk]
            else:
                candidates = [payload.encode("utf-8")]
                if payload.endswith("\n"):
                    candidates.append(payload[:-1].encode("utf-8"))
            matches = [data for data in candidates if sha(data) == meta.get("sha256")]
            if not matches:
                raise ValueError("Source chunk hash mismatch: " + relative)
            chunks.append(matches[0])
        data = b"".join(chunks)
        if len(data) != row.get("bytes") or sha(data) != row.get("sha256"):
            raise ValueError("Whole source hash mismatch: " + name)
        rows[name] = data
    # No file can also be a directory. Preflight the entire edition, including
    # later stages, so conflicts never cause a partial restore.
    for name in rows:
        if any(parent.as_posix() in rows for parent in PurePosixPath(name).parents):
            raise ValueError("Source file is also an ancestor directory: " + name)
    # Reject an omitted source page even if its manifest row was removed.
    actual = {
        path.relative_to(folder).as_posix()
        for path in folder.glob("*/sources/**/*.md")
        if path.is_file()
    }
    if actual != documents:
        raise ValueError("Source document inventory mismatch")
    for path in folder.rglob("*.md"):
        if path.is_symlink():
            raise ValueError("Symlink Markdown is forbidden")
        relative = path.relative_to(folder).as_posix()
        text = regular_inside(folder, relative).read_bytes().decode("utf-8")
        _, markers = parse_document(text)
        if relative not in documents and markers:
            raise ValueError("Unlisted source marker: " + relative)
    return rows


def ensure_safe_target(destination, name):
    candidate = destination
    for part in safe_path(name).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("Refuse target symlink: " + name)
        if candidate != destination / name and candidate.exists() and not candidate.is_dir():
            raise ValueError("Target parent is not a directory: " + name)
    return candidate


def restore(folder, destination, through=None, advance=False):
    folder, destination = Path(folder), Path(destination)
    rows = read_bundle(folder)  # Fully validate every stage before writing anything.
    document = read_manifest(folder)
    stages = {row["stage"] for row in document["files"]}
    if through is not None:
        matches = [stage for stage in stages if stage == through or stage[:2] == through]
        if len(matches) != 1:
            raise ValueError("Unknown or ambiguous stage: " + through)
        through = matches[0]
    selected = {
        row["path"]: rows[row["path"]]
        for row in document["files"]
        if through is None or row["stage"] <= through
    }
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise ValueError("Destination must be a real directory")
    # Refuse symlink ancestors even when the final leaf does not yet exist.
    if any(parent.is_symlink() for parent in destination.absolute().parents):
        raise ValueError("Destination has a symlink ancestor")
    previous = {}
    if destination.exists() and any(destination.iterdir()):
        if not advance:
            raise ValueError(
                "Destination must be empty; use --advance for a verified earlier stage"
            )
        ledger = json.loads(regular_inside(destination, LEDGER).read_text(encoding="utf-8"))
        if (
            not isinstance(ledger, dict)
            or type(ledger.get("format")) is not int
            or ledger.get("format") != 1
            or not isinstance(ledger.get("files"), dict)
        ):
            raise ValueError("Invalid progress ledger")
        previous = ledger["files"]
        for name, digest in previous.items():
            if name not in rows or sha(rows[name]) != digest:
                raise ValueError("Ledger does not belong to this edition: " + name)
            if sha(regular_inside(destination, name).read_bytes()) != digest:
                raise ValueError("A previously restored file changed: " + name)
        if not set(previous).issubset(selected):
            raise ValueError("Cannot move backwards to an earlier stage")
    for name, data in selected.items():
        target = ensure_safe_target(destination, name)
        if target.exists() and (not target.is_file() or target.read_bytes() != data):
            raise ValueError("Refuse to overwrite existing source: " + name)
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in selected.items():
        target = ensure_safe_target(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (destination / LEDGER).write_text(
        json.dumps(
            {"format": 1, "files": {name: sha(data) for name, data in selected.items()}},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return len(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, nargs="?")
    parser.add_argument("--docs", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--through", help="Include all stages through this number or full stage ID")
    parser.add_argument("--advance", action="store_true")
    parser.add_argument("--check", action="store_true", help="Validate only; never write source")
    args = parser.parse_args()
    if args.check:
        print("Validated source files:", len(read_bundle(args.docs)))
    elif args.destination is None:
        parser.error("Provide a new empty destination or --check")
    else:
        print(
            "Restored source files:",
            restore(args.docs, args.destination, args.through, args.advance),
        )


if __name__ == "__main__":
    main()
````
