# workbench/vendor.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：核验并展开固定第三方模板。** inventory读取随教材给出的来源清单；unpack_source核验归档和源码摘要后才展开。prepare为特定模板选对后端/前端归档。模板是第三方依赖，不要求初学者重新手写其数千文件。

**对应关系：** rnd init/native_prepare → vendor → 本机templates/vendor；test_vendor。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `inventory`（L20–L26）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L22按`not path.is_file()`分支；L23抛异常，停止当前正常路径。 调用`path.is_file`、`FileNotFoundError`、`json.loads`、`path.read_text`。 返回路径：L26的`json.loads(path.read_text(encoding="utf-8"))["sources"]`。
- `unpack_source`（L29–L66）：接收`settings`、`record`。 控制顺序：L31按`not archive.is_file() or sha(archive) != record["archive_sha256"]`分支；L32抛异常，停止当前正常路径；L38按`destination.exists()`分支；L39按`digest(manifest(destination)) != record["source_digest"]`分支；L40抛异常，停止当前正常路径；L47按`len(entries) > 25000 or sum(i.file_size for i in entries) > 300_000_000`分支；L48抛异常，停止当前正常路径；L50遍历`entries`。后续分支沿下方源码相同行号继续阅读。 调用`archive.is_file`、`sha`、`ValueError`、`settings.prepare`、`FileLock`、`str`、`destination.exists`、`digest`、`manifest`等。 返回路径：L66的`destination`。
- `prepare`（L69–L93）：接收`settings`、`template`。 控制顺序：L73按`not rows`分支；L74抛异常，停止当前正常路径；L76遍历`rows`。 调用`inventory`、`ValueError`、`unpack_source`、`str`、`build_index`、`write_json`、`receipts.append`。 返回路径：L93的`receipts`。

</details>

**创建路径：** `workbench/vendor.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L93。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3848`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/vendor.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a7c2d96ee2de466ce268a65f5e8ef46c079cdfe0c2603431a92a9d1e77da496d"} -->
````python
# workbench/vendor.py
"""Offline, checksum-verified source installation from archives already in the checkout."""

import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

from filelock import FileLock

from workbench.domain import digest
from workbench.filesystem import inside, manifest, secret_name, sha, write_json
from workbench.settings import ROOT

VENDOR = ROOT / "templates/vendor"


def inventory():
    path = VENDOR / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(
            "仓库缺少自带原生模板快照；请完整git clone本次PR，不需要额外git clone上游"
        )
    return json.loads(path.read_text(encoding="utf-8"))["sources"]


def unpack_source(settings, record):
    archive = VENDOR / record["archive"]
    if not archive.is_file() or sha(archive) != record["archive_sha256"]:
        raise ValueError("模板归档缺失或哈希错误：" + record["name"])
    destination = settings.data_dir / "bundled" / record["name"] / record["sha"]
    settings.prepare()
    with FileLock(
        str(settings.data_dir / "sources" / (record["name"] + "-bundle.lock")), timeout=60
    ):
        if destination.exists():
            if digest(manifest(destination)) != record["source_digest"]:
                raise ValueError("自带模板工作源已被修改；保留现场后重建快照副本，不覆盖你的修改")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="unpack-", dir=destination.parent) as temp:
                temp = Path(temp)
                with zipfile.ZipFile(archive) as z:
                    entries = z.infolist()
                    if len(entries) > 25000 or sum(i.file_size for i in entries) > 300_000_000:
                        raise ValueError("自带模板归档超过大小限制")
                    seen = set()
                    for item in entries:
                        path = inside(temp, item.filename)
                        if item.filename in seen or stat.S_ISLNK(item.external_attr >> 16):
                            raise ValueError("自带模板含重复路径或符号链接")
                        if secret_name(item.filename):
                            raise ValueError("自带模板不允许包含运行时密钥")
                        seen.add(item.filename)
                        if item.is_dir():
                            path.mkdir(parents=True, exist_ok=True)
                        else:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            with z.open(item) as src, path.open("wb") as out:
                                shutil.copyfileobj(src, out)
                if digest(manifest(temp)) != record["source_digest"]:
                    raise ValueError("模板解压后内容摘要不一致")
                os.replace(temp, destination)
        return destination


def prepare(settings, template):
    from workbench.knowledge import build_index

    rows = [r for r in inventory() if r["template"] == template]
    if not rows:
        raise ValueError("没有对应自带原生模板")
    receipts = []
    for row in rows:
        path = unpack_source(settings, row)
        receipt = {
            "template": template,
            "slot": row["slot"],
            "sha": row["sha"],
            "url": row["url"],
            "path": str(path),
            "dirty": False,
            "source": "bundled-offline",
            "source_digest": row["source_digest"],
        }
        build_index(
            path, settings.data_dir / "knowledge" / template / row["slot"] / row["sha"], row["sha"]
        )
        write_json(path.parent / "source-receipt.json", receipt)
        receipts.append(receipt)
    return receipts
````
