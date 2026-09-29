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
