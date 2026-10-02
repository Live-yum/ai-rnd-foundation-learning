# tests/test_safety.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.coding`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.knowledge`、`workbench.rules`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_rule_sandbox_rejects`（L27–L29）：接收`source`。 调用`pytest.raises`、`Rules`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rule_validation`（L32–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Rules`、`rule.validate`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_path_boundary`（L42–L44）：接收`tmp_path`、`path`。 调用`pytest.raises`、`inside`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_zip_rejects`（L48–L54）：接收`tmp_path`、`path`。 调用`io.BytesIO`、`zipfile.ZipFile`、`z.writestr`、`archive.seek`、`pytest.raises`、`unpack`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_case_zip_rejected`（L57–L64）：接收`tmp_path`。 调用`io.BytesIO`、`zipfile.ZipFile`、`z.writestr`、`archive.seek`、`pytest.raises`、`unpack`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_not_indexed_cache_staleness`（L67–L79）：接收`tmp_path`。 控制顺序：L73断言`build_index(source, index)["parsed_python"] == 1`；L74断言`build_index(source, index)["reused"] == 1`；L75断言`".env" not in manifest(source)`；L76断言`"a.py" in context_for(source, index, ["a.py"])["files"]`。 调用`source.mkdir`、`(source / "a.py").write_text`、`(source / ".env").write_text`、`build_index`、`manifest`、`context_for`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_patch_and_template_tamper`（L82–L96）：接收`settings`、`plan`。 调用`generate_basic`、`pytest.raises`、`apply_patch`、`Patch`、`(product / "app.py").write_text`、`verify_basic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_safety.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L96。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3196`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_safety.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2149ef317bad3145258b40e60e31c32732d5c4761d9845542da760b801319e2b"} -->
````python
# tests/test_safety.py
import io
import zipfile

import pytest

from workbench.coding import apply_patch
from workbench.domain import Patch
from workbench.filesystem import inside, manifest, unpack
from workbench.generator import PrerequisiteError, generate_basic
from workbench.knowledge import build_index, context_for
from workbench.rules import Rules, UnsafeRule
from workbench.verification import verify_basic


@pytest.mark.parametrize(
    "source",
    [
        "import os",
        "def validate(entity, data):\n    import os",
        'def validate(entity, data):\n    open("x")',
        "def validate(entity, data):\n    while True: pass",
        "def validate(entity, data):\n    return data.__class__",
        "def validate(entity, data):\n    x = 1",
        'def validate(entity, data):\n    return eval("1")',
    ],
)
def test_rule_sandbox_rejects(source):
    with pytest.raises((UnsafeRule, SyntaxError)):
        Rules(source)


def test_rule_validation():
    rule = Rules(
        "def validate(entity, data):\n    if data.get('age', 0) < 18:\n        raise ValueError('adult only')\n"
    )
    rule.validate("user", {"age": 20})
    with pytest.raises(ValueError):
        rule.validate("user", {"age": 12})


@pytest.mark.parametrize("path", ["../x", "/etc/passwd", "C:/x", "..\\x", "file:stream"])
def test_path_boundary(tmp_path, path):
    with pytest.raises(ValueError):
        inside(tmp_path, path)


@pytest.mark.parametrize("path", ["../evil", ".env", "secret.key"])
def test_zip_rejects(tmp_path, path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(path, "x")
    archive.seek(0)
    with pytest.raises(ValueError):
        unpack(archive, tmp_path / "out")


def test_duplicate_case_zip_rejected(tmp_path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("a.txt", "one")
        z.writestr("A.txt", "two")
    archive.seek(0)
    with pytest.raises(ValueError):
        unpack(archive, tmp_path)


def test_secret_not_indexed_cache_staleness(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.py").write_text("def hello():\n    return 1\n", encoding="utf-8")
    (source / ".env").write_text("API_KEY=secret")
    index = tmp_path / "index"
    assert build_index(source, index)["parsed_python"] == 1
    assert build_index(source, index)["reused"] == 1
    assert ".env" not in manifest(source)
    assert "a.py" in context_for(source, index, ["a.py"])["files"]
    (source / "a.py").write_text("x = 2")
    with pytest.raises(ValueError):
        context_for(source, index, ["a.py"])


def test_stale_patch_and_template_tamper(settings, plan):
    product = settings.data_dir / "runs" / "test" / "product"
    generate_basic(plan, product)
    with pytest.raises(ValueError):
        apply_patch(
            product,
            Patch(
                path="custom_rules.py",
                before_sha256="0" * 64,
                content="def validate(entity, data):\n    pass\n",
            ),
        )
    (product / "app.py").write_text('print("fake success")')
    with pytest.raises(PrerequisiteError):
        verify_basic(plan, product, settings)
````
