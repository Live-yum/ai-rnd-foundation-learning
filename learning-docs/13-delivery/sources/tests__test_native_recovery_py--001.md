# tests/test_native_recovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`workbench.filesystem`、`workbench.generator`、`workbench.native_recovery`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `checkpoint`（L11–L20）：接收`tmp_path`。 调用`atomic_text`、`acceptance_spec`、`identity`、`save`。 返回路径：L20的`path, expected, product, source, plan, url`。
- `test_recovery_retains_files_targets_and_excludes_credentials`（L23–L28）：接收`tmp_path`。 控制顺序：L26断言`state["targets"] == [{"entity": "device"}]`；L27断言`(product / "app.py").read_text() == "generated"`；L28断言`"never-store-me" not in path.read_text()`。 调用`checkpoint`、`load`、`(product / "app.py").read_text`、`path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_recovery_fail_closed`（L32–L52）：接收`tmp_path`、`change`。 控制顺序：L34按`change == "files"`分支；L36按`change == "source"`分支；L39按`change == "database"`分支；L43按`change == "plan"`分支；L45按`change == "unsafe"`分支；L52断言`(product / "app.py").read_bytes() == before`。 调用`checkpoint`、`atomic_text`、`identity`、`url.replace`、`save`、`path.unlink`、`(product / "app.py").read_bytes`、`pytest.raises`、`load`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verified_customization_reuse_requires_unchanged_code`（L55–L82）：接收`tmp_path`。 控制顺序：L64断言`verified_native_customization(plan, product, reports) is False`；L79断言`verified_native_customization(plan, product, reports) is True`。 调用`acceptance_spec`、`atomic_text`、`verified_native_customization`、`write_json`、`digest`、`plan.model_dump`、`sha`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_recovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L82。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3428`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_recovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f665c7f83a94e586a55e1f1bdd1f149f702fa994c0492dc79ae8187a0acd7f0a"} -->
````python
# tests/test_native_recovery.py
"""Recovery refuses changed source/plan/database and never resets retained state."""

import pytest

from scripts.ci_native_generated import acceptance_spec
from workbench.filesystem import atomic_text
from workbench.generator import PrerequisiteError
from workbench.native_recovery import identity, load, save


def checkpoint(tmp_path):
    source, product = tmp_path / "source", tmp_path / "product"
    atomic_text(source / "app.py", "upstream")
    atomic_text(product / "app.py", "generated")
    plan = acceptance_spec()
    url = "postgresql+psycopg://native:never-store-me@127.0.0.1:5432/test_codegen"
    expected = identity("fastapiadmin", plan, url, source, None)
    path = tmp_path / "recovery.json"
    save(path, expected, product, [{"entity": "device"}], resumable=True, stage="generated")
    return path, expected, product, source, plan, url


def test_recovery_retains_files_targets_and_excludes_credentials(tmp_path):
    path, expected, product, *_ = checkpoint(tmp_path)
    state = load(path, expected, product)
    assert state["targets"] == [{"entity": "device"}]
    assert (product / "app.py").read_text() == "generated"
    assert "never-store-me" not in path.read_text()


@pytest.mark.parametrize("change", ["files", "source", "database", "plan", "unsafe", "missing"])
def test_native_recovery_fail_closed(tmp_path, change):
    path, expected, product, source, plan, url = checkpoint(tmp_path)
    if change == "files":
        atomic_text(product / "app.py", "user edits")
    elif change == "source":
        atomic_text(source / "app.py", "other upstream")
        expected = identity("fastapiadmin", plan, url, source, None)
    elif change == "database":
        expected = identity(
            "fastapiadmin", plan, url.replace("test_codegen", "other_codegen"), source, None
        )
    elif change == "plan":
        expected = {**expected, "spec_digest": "changed"}
    elif change == "unsafe":
        save(path, expected, product, [], resumable=False, stage="native-generation")
    else:
        path.unlink()
    before = (product / "app.py").read_bytes()
    with pytest.raises(PrerequisiteError):
        load(path, expected, product)
    assert (product / "app.py").read_bytes() == before


def test_verified_customization_reuse_requires_unchanged_code(tmp_path):
    from workbench.domain import digest
    from workbench.filesystem import sha, write_json
    from workbench.native_coding import verified_native_customization
    from workbench.native_recovery import NativeIntegrityError

    plan = acceptance_spec()
    product, reports = tmp_path / "product", tmp_path / "reports"
    atomic_text(product / "rule.py", "safe rule")
    assert verified_native_customization(plan, product, reports) is False
    write_json(
        reports / "native-coding.json",
        {
            "passed": True,
            "plop": {"spec_digest": digest(plan.model_dump())},
            "edit": {
                "verified": True,
                "frontend_build": True,
                "frontend_typecheck": True,
                "real_browser": True,
                "after": {"rule.py": sha(product / "rule.py")},
            },
        },
    )
    assert verified_native_customization(plan, product, reports) is True
    atomic_text(product / "rule.py", "external edits")
    with pytest.raises(NativeIntegrityError):
        verified_native_customization(plan, product, reports)
````
