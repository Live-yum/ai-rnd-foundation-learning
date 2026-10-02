# scripts/rebuild_from_handbook.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从一本书还原安全的新项目。** extract先验证全部标记、路径和SHA；截图严格解码Base64后验证原始字节，再由restore写入新的空目录。任一源码或资源块残缺就不动目标；不运行提取出的程序或下载依赖。

**对应关系：** 书中独立bootstrap或本脚本 → 完整自有源码和真实截图 → ci_handbook。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `extract`（L17–L61）：接收`text`。 控制顺序：L19遍历`PATTERN.finditer(text)`；L22按`path.is_absolute() or ".." in path.parts or ":" in name or "\\" in name or name in re…`分支；L33抛异常，停止当前正常路径；L34按`encoding == "base64"`分支；L38抛异常，停止当前正常路径；L39按`hashlib.sha256(restored).hexdigest() != fingerprint`分支；L40抛异常，停止当前正常路径；L54按`restored is None`分支。后续分支沿下方源码相同行号继续阅读。 调用`PATTERN.finditer`、`match.groups`、`PurePosixPath`、`path.is_absolute`、`path.as_posix`、`any`、`ord`、`ValueError`、`base64.b64decode`等。 返回路径：L61的`result`。
- `restore`（L64–L77）：接收`handbook`、`destination`。先验证所有源码块与目标路径，再向空目录写入；这一步本身不执行任何写出的项目代码。 控制顺序：L66按`destination.is_symlink() or (destination.exists() and any(destination.iterdir()))`分支；L67抛异常，停止当前正常路径；L70遍历`rows.items()`；L73按`isinstance(content, bytes)`分支。 调用`Path`、`destination.is_symlink`、`destination.exists`、`any`、`destination.iterdir`、`ValueError`、`extract`、`Path(handbook).read_text`、`destination.mkdir`等。 返回路径：L77的`len(rows)`。

</details>

**创建路径：** `scripts/rebuild_from_handbook.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L85。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3156`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/rebuild_from_handbook.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f4de746b16d2de91095db3137d26f4255f398645a58b5826dacec0189d6b6d57"} -->
````python
# scripts/rebuild_from_handbook.py
"""Restore source blocks to an EMPTY directory. Writes only; does not execute anything."""

import argparse
import base64
import binascii
import hashlib
import re
from pathlib import Path, PurePosixPath

PATTERN = re.compile(
    r"^<!-- source-file: ([^\r\n]+) sha256: ([0-9a-f]{64})(?: encoding: (base64))? -->\n"
    r"(`{4,})[^\n]*\n(.*?)\n\4\n",
    re.S | re.M,
)


def extract(text):
    result = {}
    for match in PATTERN.finditer(text):
        name, fingerprint, encoding, _, content = match.groups()
        path = PurePosixPath(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or ":" in name
            or "\\" in name
            or name in result
            or not path.parts
            or path.as_posix() != name
            or ".git" in path.parts
            or any(ord(char) < 32 for char in name)
        ):
            raise ValueError("附录文件路径不安全或重复")
        if encoding == "base64":
            try:
                restored = base64.b64decode(content.replace("\n", ""), validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ValueError("二进制块编码不合法: " + name) from exc
            if hashlib.sha256(restored).hexdigest() != fingerprint:
                raise ValueError("二进制块哈希不匹配: " + name)
            result[name] = restored
            continue
        # The final fence separator can be a source newline or an added one.
        # Recover only the exact form authorized by the original source SHA.
        candidates = (content + "\n", content)
        restored = next(
            (
                value
                for value in candidates
                if hashlib.sha256(value.encode()).hexdigest() == fingerprint
            ),
            None,
        )
        if restored is None:
            raise ValueError("源码块哈希不匹配: " + name)
        result[name] = restored
    if not result:
        raise ValueError("没有找到完整源码块")
    if len(result) != len(re.findall(r"^<!-- source-file: ", text, re.M)):
        raise ValueError("源码块不完整，拒绝写入残缺项目")
    return result


def restore(handbook, destination):
    destination = Path(destination)
    if destination.is_symlink() or (destination.exists() and any(destination.iterdir())):
        raise ValueError("目标必须是新的空目录，不覆盖已有项目")
    rows = extract(Path(handbook).read_text(encoding="utf-8"))
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in rows.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("handbook", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print("Restored files:", restore(args.handbook, args.destination))
````
