# tests/test_native_failure_classification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance`、`workbench.core.contracts`、`workbench.delivery.recovery`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_lab_does_not_downgrade_unknown_or_integrity_failures`（L13–L56）：接收`tmp_path`、`monkeypatch`、`kind`。 控制顺序：L56断言`not isinstance(error.value, NativeValidationFailure)`。 调用`source.mkdir`、`source_file.write_text`、`Plan`、`monkeypatch.setattr`、`pytest.raises`、`native_lab._run_acceptance`、`isinstance`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_lab_does_not_downgrade_unknown_or_integrity_failures.fail`（L28–L35）：接收`*args`。 控制顺序：L29按`kind == "source_changed"`分支；L31按`kind == "plan_changed"`分支；L33按`kind == "permission"`分支；L34抛异常，停止当前正常路径；L35抛异常，停止当前正常路径。 调用`source_file.write_text`、`PermissionError`、`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_runtime_check_marks_validation_failed`（L59–L64）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`native_lab._runtime_check`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_runtime_check_marks_validation_failed.failed_check`（L60–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L61抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_failure_classification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L64。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2200`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_failure_classification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ae8610356b61360891882a97e509c9a5a8ab4305eb41250c9dc888a8ab60bcbf"} -->
````python
# tests/test_native_failure_classification.py
"""Exercise the real native lab wrapper, not a mocked delivery entry point."""

import pytest

pytest.importorskip("psycopg")

from workbench.acceptance import native_lab
from workbench.core.contracts import Plan
from workbench.delivery.recovery import NativeIntegrityError, NativeValidationFailure


@pytest.mark.parametrize("kind", ["unknown_assert", "permission", "source_changed", "plan_changed"])
def test_native_lab_does_not_downgrade_unknown_or_integrity_failures(tmp_path, monkeypatch, kind):
    source = tmp_path / "source"
    source.mkdir()
    source_file = source / "upstream.py"
    source_file.write_text("value = 1\n")
    plan = Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )
    monkeypatch.setattr(native_lab, "prepare_fastapi_transactions", lambda *args: {})

    def fail(*args):
        if kind == "source_changed":
            source_file.write_text("corrupted\n")
        if kind == "plan_changed":
            plan.title = "changed approval"
        if kind == "permission":
            raise PermissionError("denied")
        raise AssertionError("unclassified assertion before executable validation")

    monkeypatch.setattr(native_lab, "bootstrap_database", fail)
    expected = (
        NativeIntegrityError
        if kind in {"source_changed", "plan_changed"}
        else PermissionError
        if kind == "permission"
        else AssertionError
    )
    with pytest.raises(expected) as error:
        native_lab._run_acceptance(
            "fastapiadmin",
            source,
            tmp_path / "product",
            None,
            "postgresql://localhost/test_codegen",
            tmp_path / "reports",
            plan,
            backend_port=18001,
        )
    assert not isinstance(error.value, NativeValidationFailure)


def test_only_explicit_runtime_check_marks_validation_failed():
    def failed_check():
        raise AssertionError("HTTP acceptance mismatch")

    with pytest.raises(NativeValidationFailure):
        native_lab._runtime_check(failed_check)
````
