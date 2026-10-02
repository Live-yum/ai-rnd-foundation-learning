# tests/test_native_transaction.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_compatibility`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_generated_transaction_scope_is_recorded`（L10–L27）：接收`tmp_path`。 控制顺序：L22断言`'scope="function"' in text`；L23断言`'Security(AuthPermission(["module_rnd:device:create"]))' in text`；L24断言`receipt["before_sha256"] != receipt["after_sha256"]`；L25断言`receipt["dependencies"] == 1`。 调用`file.write_text`、`commit_before_response`、`file.read_text`、`ast.parse`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tool_failure_retains_end_of_large_log`（L30–L42）：接收`tmp_path`。 控制顺序：L40断言`error.value.log.startswith("start")`；L41断言`"specific failure" in error.value.log`；L42断言`len(error.value.log) < 65000`。 调用`pytest.raises`、`run_command`、`error.value.log.startswith`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_preserves_diagnostics`（L45–L53）：接收`tmp_path`。 控制顺序：L52断言`error.value.timed_out is True`；L53断言`"before timeout" in error.value.log`。 调用`pytest.raises`、`run_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_updates_exercise_integer_and_boolean_changes`（L56–L66）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L63断言`initial["name"] != changed["name"]`；L64断言`initial["quantity"] != changed["quantity"]`；L65断言`initial["active"] is True`；L66断言`changed["active"] is False`。 调用`acceptance_spec`、`sample_record`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_role_and_codegen_both_commit_before_their_success_response`（L69–L91）：接收`tmp_path`。 控制顺序：L79遍历`paths`；L84断言`[r["path"] for r in receipts] == paths`；L85断言`all(r["before_sha256"] != r["after_sha256"] for r in receipts)`；L86遍历`paths`；L88断言`actual == source.replace( "Depends(db_getter)", 'Depends(db_getter, scope="function")…`。 调用`path.parent.mkdir`、`path.write_text`、`prepare_fastapi_transactions`、`all`、`(tmp_path / relative).read_text`、`source.replace`、`ast.parse`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_transaction.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L91。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3232`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_transaction.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f12ff3d14b6f5bfb49e9bfe681dfd6169c00f68e875bbe171299a3616398a990"} -->
````python
# tests/test_native_transaction.py
import ast
import sys

import pytest

from workbench.native_compatibility import commit_before_response, prepare_fastapi_transactions
from workbench.tools import ToolFailure, run_command


def test_generated_transaction_scope_is_recorded(tmp_path):
    file = tmp_path / "controller.py"
    file.write_text(
        """from fastapi import Depends, Security
async def create(auth=Security(AuthPermission(["module_rnd:device:create"])), db=Depends(db_getter)):
    return await service.create(db)
""",
        encoding="utf-8",
    )
    receipt = commit_before_response(file)
    text = file.read_text(encoding="utf-8")
    ast.parse(text)
    assert 'scope="function"' in text
    assert 'Security(AuthPermission(["module_rnd:device:create"]))' in text
    assert receipt["before_sha256"] != receipt["after_sha256"]
    assert receipt["dependencies"] == 1
    with pytest.raises(ValueError):
        commit_before_response(file)


def test_tool_failure_retains_end_of_large_log(tmp_path):
    with pytest.raises(ToolFailure) as error:
        run_command(
            [
                sys.executable,
                "-c",
                "print('start');print('x'*80000);print('specific failure');raise SystemExit(9)",
            ],
            tmp_path,
        )
    assert error.value.log.startswith("start")
    assert "specific failure" in error.value.log
    assert len(error.value.log) < 65000


def test_timeout_preserves_diagnostics(tmp_path):
    with pytest.raises(ToolFailure) as error:
        run_command(
            [sys.executable, "-u", "-c", "import time;print('before timeout');time.sleep(10)"],
            tmp_path,
            timeout=0.5,
        )
    assert error.value.timed_out is True
    assert "before timeout" in error.value.log


def test_updates_exercise_integer_and_boolean_changes():
    from scripts.ci_native_generated import acceptance_spec
    from workbench.native_acceptance import sample_record

    entity = acceptance_spec().entities[0]
    initial = sample_record(entity)
    changed = sample_record(entity, "updated")
    assert initial["name"] != changed["name"]
    assert initial["quantity"] != changed["quantity"]
    assert initial["active"] is True
    assert changed["active"] is False


def test_native_role_and_codegen_both_commit_before_their_success_response(tmp_path):
    paths = [
        "app/modules/system/role/controller.py",
        "app/modules/generator/gencode/controller.py",
    ]
    source = (
        "from fastapi import Depends, Security\n"
        "async def operation(auth=Security(native_auth), db=Depends(db_getter)):\n"
        "    return await native_service(db)\n"
    )
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(source, encoding="utf-8")
    receipts = prepare_fastapi_transactions(tmp_path)
    assert [r["path"] for r in receipts] == paths
    assert all(r["before_sha256"] != r["after_sha256"] for r in receipts)
    for relative in paths:
        actual = (tmp_path / relative).read_text(encoding="utf-8")
        assert actual == source.replace(
            "Depends(db_getter)", 'Depends(db_getter, scope="function")'
        )
        ast.parse(actual)
````
