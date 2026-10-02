# tests/test_business_screenshots.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `png`（L11–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`chunk`、`struct.pack`、`zlib.compress`。 返回路径：L20的`b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) + chun…`。
- `png.chunk`（L12–L18）：接收`kind`、`data`。 调用`struct.pack`、`len`、`zlib.crc32`。 返回路径：L13的`struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0…`。
- `verifier`（L28–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Path`、`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`。 返回路径：L33的`module`。
- `entry`（L36–L43）：接收`**changes`。 返回路径：L37的`{ "file": "manager--customers--list.png", "role": "manager", "entity": "customers", "view"…`。
- `test_only_listed_bounded_pngs_can_be_exported`（L46–L53）：接收`tmp_path`。 控制顺序：L51断言`records[0]["bytes"] == len(value)`；L52断言`len(records[0]["sha256"]) == 64`；L53断言`not any(str(tmp_path) in str(v) for v in records[0].values())`。 调用`verifier`、`png`、`(tmp_path / entry()["file"]).write_bytes`、`entry`、`module.validate_screenshots`、`len`、`any`、`str`、`records[0].values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_rejects_unknown_views_paths_and_secret_fields`（L69–L71）：接收`tmp_path`、`change`。 调用`pytest.raises`、`verifier().validate_screenshots`、`verifier`、`entry`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_rejects_symlink_and_unlisted_sidecar`（L74–L83）：接收`tmp_path`。 调用`verifier`、`target.write_bytes`、`png`、`(tmp_path / entry()["file"]).symlink_to`、`entry`、`pytest.skip`、`pytest.raises`、`module.validate_screenshots`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_rejects_non_png_duplicate_and_unrequested_files`（L86–L99）：接收`tmp_path`。 调用`verifier`、`entry`、`path.write_text`、`pytest.raises`、`module.validate_screenshots`、`path.write_bytes`、`png`、`(tmp_path / "private.json").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_rejects_limits`（L102–L114）：接收`tmp_path`、`monkeypatch`。 调用`verifier`、`entry`、`path.write_bytes`、`png`、`pytest.raises`、`module.validate_screenshots`、`monkeypatch.setattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_png_header_cannot_disguise_text_or_trailing_credentials`（L117–L122）：接收`tmp_path`。 控制顺序：L119遍历`[b"\x89PNG\r\n\x1a\nnot-an-image", png() + b"private-sidecar"]`。 调用`entry`、`png`、`path.write_bytes`、`pytest.raises`、`verifier().validate_screenshots`、`verifier`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requested_screenshot_output_cannot_silently_be_empty`（L125–L128）：接收`tmp_path`。 控制顺序：L126断言`verifier().validate_screenshots(None, []) == []`。 调用`verifier().validate_screenshots`、`verifier`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_screenshots.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4233`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_screenshots.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "56750d5f4146c62f1156ed1ebccaa1d8e0a38054cabdda6795893273fb001c14"} -->
````python
# tests/test_business_screenshots.py
"""Bounded synthetic-product PNG evidence; no credentials or arbitrary file exports."""

import importlib.util
import struct
import zlib
from pathlib import Path

import pytest


def png():
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\xff"))
        + chunk(b"IEND", b"")
    )


def verifier():
    path = Path(__file__).parents[1] / "templates/product/verify_business.py"
    spec = importlib.util.spec_from_file_location("business_screenshot_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry(**changes):
    return {
        "file": "manager--customers--list.png",
        "role": "manager",
        "entity": "customers",
        "view": "list",
        **changes,
    }


def test_only_listed_bounded_pngs_can_be_exported(tmp_path):
    module = verifier()
    value = png()
    (tmp_path / entry()["file"]).write_bytes(value)
    records = module.validate_screenshots(tmp_path, [entry()])
    assert records[0]["bytes"] == len(value)
    assert len(records[0]["sha256"]) == 64
    assert not any(str(tmp_path) in str(v) for v in records[0].values())


@pytest.mark.parametrize(
    "change",
    [
        {"file": "../secret.png"},
        {"file": "credentials.json"},
        {"role": "../manager"},
        {"entity": "../../private"},
        {"view": "login"},
        {"view": "platform"},
        {"view": ["list"]},
        {"token": "not-allowed"},
    ],
)
def test_manifest_rejects_unknown_views_paths_and_secret_fields(tmp_path, change):
    with pytest.raises(ValueError):
        verifier().validate_screenshots(tmp_path, [entry(**change)])


def test_manifest_rejects_symlink_and_unlisted_sidecar(tmp_path):
    module = verifier()
    target = tmp_path / "real.png"
    target.write_bytes(png())
    try:
        (tmp_path / entry()["file"]).symlink_to(target)
    except OSError:
        pytest.skip("Symlinks not available on this runner")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_manifest_rejects_non_png_duplicate_and_unrequested_files(tmp_path):
    module = verifier()
    path = tmp_path / entry()["file"]
    path.write_text("synthetic credential sidecar", encoding="utf-8")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])
    path.write_bytes(png())
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry(), entry()])
    with pytest.raises(ValueError):
        module.validate_screenshots(None, [entry()])
    (tmp_path / "private.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_manifest_rejects_limits(tmp_path, monkeypatch):
    module = verifier()
    path = tmp_path / entry()["file"]
    path.write_bytes(png())
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()] * 49)
    monkeypatch.setattr(module, "SCREENSHOT_FILE_BYTES", 7)
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])
    monkeypatch.setattr(module, "SCREENSHOT_FILE_BYTES", 99)
    monkeypatch.setattr(module, "SCREENSHOT_TOTAL_BYTES", 7)
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_png_header_cannot_disguise_text_or_trailing_credentials(tmp_path):
    path = tmp_path / entry()["file"]
    for payload in [b"\x89PNG\r\n\x1a\nnot-an-image", png() + b"private-sidecar"]:
        path.write_bytes(payload)
        with pytest.raises(ValueError):
            verifier().validate_screenshots(tmp_path, [entry()])


def test_requested_screenshot_output_cannot_silently_be_empty(tmp_path):
    assert verifier().validate_screenshots(None, []) == []
    with pytest.raises(ValueError):
        verifier().validate_screenshots(tmp_path, [])
````
