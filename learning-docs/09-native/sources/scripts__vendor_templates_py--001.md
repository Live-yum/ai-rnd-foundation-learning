# scripts/vendor_templates.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：重建固定的第三方源码归档。** 按登记远端与提交取得公开依赖，保留许可证，排除密钥/缓存/数据库等不应打包内容，记录归档SHA与逐文件内容摘要。它不取得本平台骨架代码。

**对应关系：** 教材还原后--fetch → templates/vendor → workbench.vendor校验并解压。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fingerprint`（L66–L67）：接收`data`。 调用`hashlib.sha256(data).hexdigest`、`hashlib.sha256`。 返回路径：L67的`hashlib.sha256(data).hexdigest()`。
- `pack`（L70–L108）：接收`source`、`target`。 控制顺序：L72遍历`os.walk(source, followlinks=False)`；L74遍历`sorted(names)`；L77按`path.is_symlink() or not stat.S_ISREG(path.stat().st_mode)`分支；L78抛异常，停止当前正常路径；L79按`path.suffix.lower() in EXCLUDE_EXT or (name.startswith(".env") and not name.endswith(…`分支；L86按`path.stat().st_size > 32_000_000`分支；L87抛异常，停止当前正常路径；L92遍历`sorted(rows.items())`。 调用`os.walk`、`sorted`、`Path`、`path.relative_to(source).as_posix`、`path.relative_to`、`path.is_symlink`、`stat.S_ISREG`、`path.stat`、`ValueError`等。 返回路径：L103的`{ "archive_sha256": fingerprint(target.read_bytes()), "source_digest": source_digest, "fil…`。
- `build`（L111–L134）：接收`source_root`、`output`。 控制顺序：L113遍历`SOURCES`；L116按`"MIT" not in license_text`分支；L117抛异常，停止当前正常路径。 调用`(path / "LICENSE").read_text`、`ValueError`、`pack`、`(output / (source["name"] + ".LICENSE")).write_text`、`records.append`、`sorted`、`(output / "manifest.json").write_text`、`json.dumps`。 返回路径：L134的`manifest`。
- `main`（L137–L176）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L143按`args.fetch == bool(args.source_root)`分支；L147按`args.fetch`分支；L148遍历`SOURCES`；L165按`actual != row["sha"]`分支；L166抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`bool`、`parser.error`、`tempfile.TemporaryDirectory`、`Path`、`dest.mkdir`、`subprocess.run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/vendor_templates.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L180。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6150`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/vendor_templates.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7653f6e94d9552f4dd5c0b0228eb8b3fcaca09b5356301deb0bb313896e4240e"} -->
````python
# scripts/vendor_templates.py
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
                    ["git", "-C", str(dest), "config", "core.autocrlf", "false"], check=True
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
````
