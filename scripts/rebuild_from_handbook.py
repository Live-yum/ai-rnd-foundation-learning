"""Restore source blocks to an EMPTY directory. Writes only; does not execute anything."""

import argparse
import hashlib
import re
from pathlib import Path, PurePosixPath

PATTERN = re.compile(
    r"<!-- source-file: (.+?) sha256: ([0-9a-f]{64}) -->\n(`{4,})[^\n]*\n(.*?)\n\3\n", re.S
)


def extract(text):
    result = {}
    for match in PATTERN.finditer(text):
        name, fingerprint, _, content = match.groups()
        path = PurePosixPath(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or ":" in name
            or "\\" in name
            or name in result
        ):
            raise ValueError("附录文件路径不安全或重复")
        # All committed sources use a final newline.
        content += "\n"
        if hashlib.sha256(content.encode()).hexdigest() != fingerprint:
            raise ValueError("源码块哈希不匹配: " + name)
        result[name] = content
    if not result:
        raise ValueError("没有找到完整源码块")
    return result


def restore(handbook, destination):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("目标必须是新的空目录，不覆盖已有项目")
    rows = extract(Path(handbook).read_text(encoding="utf-8"))
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in rows.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("handbook", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print("Restored files:", restore(args.handbook, args.destination))
