# tests/test_vendor.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.vendor`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_an_ordinary_checkout_contains_actual_native_code_archives`（L11–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L13断言`{r["name"] for r in rows} == {"fastapiadmin", "yudao-backend", "yudao-frontend"}`；L14遍历`rows`；L16断言`archive.is_file() and hashlib.sha256(archive.read_bytes()).hexdigest() == item["archi…`；L21断言`"LICENSE" in z.namelist()`；L22断言`len(z.namelist()) == item["files"]`；L23断言`not any( n.endswith((".ttf", ".otf", ".woff", ".woff2", ".pem", ".key")) for n in z.n…`；L27断言`any(n.endswith((".py", ".java", ".vue")) for n in z.namelist())`。 调用`inventory`、`archive.is_file`、`hashlib.sha256(archive.read_bytes()).hexdigest`、`hashlib.sha256`、`archive.read_bytes`、`zipfile.ZipFile`、`z.namelist`、`len`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_offline_unpack_is_reusable_and_detects_source_changes`（L30–L37）：接收`settings`。 控制顺序：L33断言`digest(manifest(dest)) == item["source_digest"]`；L34断言`unpack_source(settings, item) == dest`。 调用`next`、`inventory`、`unpack_source`、`digest`、`manifest`、`(dest / "LICENSE").write_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_vendor.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L37。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1403`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_vendor.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b1a4d29427eea4f67b0657977581acea499eeabfaa1ad67fc2469c68dbf68365"} -->
````python
# tests/test_vendor.py
import hashlib
import zipfile

import pytest

from workbench.domain import digest
from workbench.filesystem import manifest
from workbench.vendor import VENDOR, inventory, unpack_source


def test_an_ordinary_checkout_contains_actual_native_code_archives():
    rows = inventory()
    assert {r["name"] for r in rows} == {"fastapiadmin", "yudao-backend", "yudao-frontend"}
    for item in rows:
        archive = VENDOR / item["archive"]
        assert (
            archive.is_file()
            and hashlib.sha256(archive.read_bytes()).hexdigest() == item["archive_sha256"]
        )
        with zipfile.ZipFile(archive) as z:
            assert "LICENSE" in z.namelist()
            assert len(z.namelist()) == item["files"]
            assert not any(
                n.endswith((".ttf", ".otf", ".woff", ".woff2", ".pem", ".key"))
                for n in z.namelist()
            )
            assert any(n.endswith((".py", ".java", ".vue")) for n in z.namelist())


def test_offline_unpack_is_reusable_and_detects_source_changes(settings):
    item = next(r for r in inventory() if r["name"] == "fastapiadmin")
    dest = unpack_source(settings, item)
    assert digest(manifest(dest)) == item["source_digest"]
    assert unpack_source(settings, item) == dest
    (dest / "LICENSE").write_text("changed")
    with pytest.raises(ValueError, match="修改"):
        unpack_source(settings, item)
````
