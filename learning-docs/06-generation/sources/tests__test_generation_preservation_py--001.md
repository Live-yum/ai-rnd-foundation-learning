# tests/test_generation_preservation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot`（L11–L14）：接收`root`。 调用`str`、`path.relative_to`、`path.read_bytes`、`root.rglob`、`path.is_file`。 返回路径：L12的`{ str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_fi…`。
- `existing`（L17–L26）：接收`tmp_path`、`plan`。 调用`generate_basic`、`(product / ".data").mkdir`、`(product / ".data/product.db").write_bytes`、`(product / ".data/deployment.env").write_bytes`、`(product / "user-notes.txt").write_text`、`(product / ".env").write_bytes`、`(product / "user_module.py").write_bytes`。 返回路径：L26的`product, receipt`。
- `test_existing_generation_without_matching_receipt_preserves_every_byte`（L45–L76）：接收`tmp_path`、`plan`、`failure`。 控制顺序：L48按`failure in {"missing", "receipt_directory"}`分支；L50按`failure == "receipt_directory"`分支；L52按`failure == "malformed"`分支；L54按`failure == "invalid_utf8"`分支；L58按`failure == "null"`分支；L60按`failure == "list"`分支；L62按`failure == "partial"`分支；L64按`failure == "spec"`分支。后续分支沿下方源码相同行号继续阅读。 调用`existing`、`path.unlink`、`path.mkdir`、`path.write_text`、`path.write_bytes`、`digest`、`value.pop`、`json.dumps`、`snapshot`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_design_cannot_reset_existing_product`（L79–L85）：接收`tmp_path`、`plan`。 控制顺序：L85断言`snapshot(tmp_path) == before`。 调用`existing`、`snapshot`、`plan.model_copy`、`pytest.raises`、`generate_basic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matching_generation_is_idempotent_and_preserves_user_data`（L88–L92）：接收`tmp_path`、`plan`。 控制顺序：L91断言`generate_basic(plan, product) == receipt`；L92断言`snapshot(tmp_path) == before`。 调用`existing`、`snapshot`、`generate_basic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_existing_empty_directory_is_not_adopted`（L95–L100）：接收`tmp_path`、`plan`。 控制顺序：L100断言`product.is_dir() and list(product.iterdir()) == []`。 调用`product.mkdir`、`pytest.raises`、`generate_basic`、`product.is_dir`、`list`、`product.iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_non_directory_is_not_removed`（L103–L108）：接收`tmp_path`、`plan`。 控制顺序：L108断言`product.read_bytes() == b"user-file"`。 调用`product.write_bytes`、`pytest.raises`、`generate_basic`、`product.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_generation_preservation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L108。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3694`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_generation_preservation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d60fe978bc9800432c0639d1db0031cd7a0674817d301bb32974b24abb610a92"} -->
````python
# tests/test_generation_preservation.py
"""Generator retries must not remove product databases, credentials or user files."""

import json

import pytest

from workbench.domain import digest
from workbench.generator import PrerequisiteError, generate_basic


def snapshot(root):
    return {
        str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }


def existing(tmp_path, plan):
    product = tmp_path / "product"
    receipt = generate_basic(plan, product)
    (product / ".data").mkdir()
    (product / ".data/product.db").write_bytes(b"user-owned-database-sentinel\x00\xff")
    (product / ".data/deployment.env").write_bytes(b"test-only-local-data")
    (product / "user-notes.txt").write_text("用户保存的内容", encoding="utf-8")
    (product / ".env").write_bytes(b"USER_SETTING=test-only-sentinel\n")
    (product / "user_module.py").write_bytes(b"# user-maintained code\nvalue = 42\n")
    return product, receipt


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "malformed",
        "invalid_utf8",
        "null",
        "list",
        "partial",
        "spec",
        "selection",
        "missing_files",
        "empty_files",
        "receipt_directory",
    ],
)
def test_existing_generation_without_matching_receipt_preserves_every_byte(tmp_path, plan, failure):
    product, receipt = existing(tmp_path, plan)
    path = tmp_path / "generation.json"
    if failure in {"missing", "receipt_directory"}:
        path.unlink()
        if failure == "receipt_directory":
            path.mkdir()
    elif failure == "malformed":
        path.write_text("{broken", encoding="utf-8")
    elif failure == "invalid_utf8":
        path.write_bytes(b"\xff\xfeinvalid")
    else:
        value = receipt
        if failure == "null":
            value = None
        elif failure == "list":
            value = []
        elif failure == "partial":
            value = {}
        elif failure == "spec":
            value["spec_digest"] = digest({"other": "design"})
        elif failure == "selection":
            value["selection"]["database"] = "postgresql"
        elif failure == "missing_files":
            value.pop("files")
        elif failure == "empty_files":
            value["files"] = {}
        path.write_text(json.dumps(value), encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert snapshot(tmp_path) == before


def test_changed_design_cannot_reset_existing_product(tmp_path, plan):
    product, _ = existing(tmp_path, plan)
    before = snapshot(tmp_path)
    changed = plan.model_copy(update={"title": plan.title + " changed"})
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(changed, product)
    assert snapshot(tmp_path) == before


def test_matching_generation_is_idempotent_and_preserves_user_data(tmp_path, plan):
    product, receipt = existing(tmp_path, plan)
    before = snapshot(tmp_path)
    assert generate_basic(plan, product) == receipt
    assert snapshot(tmp_path) == before


def test_unknown_existing_empty_directory_is_not_adopted(tmp_path, plan):
    product = tmp_path / "product"
    product.mkdir()
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert product.is_dir() and list(product.iterdir()) == []


def test_existing_non_directory_is_not_removed(tmp_path, plan):
    product = tmp_path / "product"
    product.write_bytes(b"user-file")
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert product.read_bytes() == b"user-file"
````
