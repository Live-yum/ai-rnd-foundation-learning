# tests/test_native_registry.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_environment`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_pinned_registry_rewrite_preserves_versions_hashes_and_is_idempotent`（L10–L26）：接收`tmp_path`。 控制顺序：L14遍历`["pyproject.toml", "uv.lock"]`；L20断言`"pypi.tuna.tsinghua.edu.cn" not in after`；L21断言`"https://files.pythonhosted.org/packages/" in after`；L22断言`re.findall(r'(?:version\|hash) = "[^"]+"', before) == re.findall( r'(?:version\|hash)…`；L26断言`all(v["before_sha256"] == v["after_sha256"] for v in receipt.values())`。 调用`backend.mkdir`、`ZipFile`、`next`、`z.namelist`、`n.endswith`、`(backend / name).write_bytes`、`z.read`、`(backend / "uv.lock").read_text`、`prepare_fastapi_registry`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_registry.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L26。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1202`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_registry.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "06d6e3cd9b4d1e0e5d545da945174b4545218c13c2ecfc5cc0a4e4cdb3ac1630"} -->
````python
# tests/test_native_registry.py
"""Canonical package downloads preserve the pinned upstream lock exactly."""

import re
from zipfile import ZipFile

from workbench.native_environment import prepare_fastapi_registry
from workbench.settings import ROOT


def test_pinned_registry_rewrite_preserves_versions_hashes_and_is_idempotent(tmp_path):
    backend = tmp_path / "backend"
    backend.mkdir()
    with ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as z:
        for name in ["pyproject.toml", "uv.lock"]:
            source = next(n for n in z.namelist() if n.endswith("backend/" + name))
            (backend / name).write_bytes(z.read(source))
    before = (backend / "uv.lock").read_text(encoding="utf-8")
    prepare_fastapi_registry(backend, tmp_path / "reports")
    after = (backend / "uv.lock").read_text(encoding="utf-8")
    assert "pypi.tuna.tsinghua.edu.cn" not in after
    assert "https://files.pythonhosted.org/packages/" in after
    assert re.findall(r'(?:version|hash) = "[^"]+"', before) == re.findall(
        r'(?:version|hash) = "[^"]+"', after
    )
    receipt = prepare_fastapi_registry(backend, tmp_path / "reports")
    assert all(v["before_sha256"] == v["after_sha256"] for v in receipt.values())
````
