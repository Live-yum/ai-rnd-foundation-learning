# tests/test_capability_startup_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_startup_hints_are_finite_even_for_secret_bearing_tracebacks`（L10–L31）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L18断言`result == { "phase": "health_deadline", "http_status": 503, "http_error": "other", "o…`；L29断言`"secret" not in json.dumps(result)`；L30断言`len(json.dumps(result)) < 512`；L31断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nontext_startup_output_never_stringifies_candidate_data`（L35–L41）：接收`output`。 控制顺序：L37断言`result["output_readable"] is False`；L38断言`result["http_status"] is None`；L39断言`result["http_error"] == "other"`；L40断言`result["output_hints"] == []`；L41断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_public_module_names_can_be_reported`（L47–L54）：接收`module`。 控制顺序：L51断言`result["known_missing_modules"] == [module]`；L52断言`startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"]…`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_loader_failure_is_not_mislabeled_as_missing_module`（L57–L67）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L64断言`result["output_hints"] == ["import-error", "native-library-mapping"]`；L65断言`result["tmpfs_noexec"] is True`；L66断言`"secret" not in json.dumps(result)`；L67断言`startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L67。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2429`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "82d117c7d50732da5bf4c8eca7122ad81af2b1608a1635d181fc773b50204e78"} -->
````python
# tests/test_capability_startup_diagnostics.py
"""Startup hints cannot become product acceptance or disclose candidate output."""

import json

import pytest

from workbench.capability_sandbox import startup_failure_diagnostic


def test_startup_hints_are_finite_even_for_secret_bearing_tracebacks():
    result = startup_failure_diagnostic(
        "secret content /private/secret token=secret\n"
        "ModuleNotFoundError: No module named 'secret.module'\n"
        "PermissionError: secret path\nApplication startup complete",
        503,
        "secret transport error",
    )
    assert result == {
        "phase": "health_deadline",
        "http_status": 503,
        "http_error": "other",
        "output_readable": True,
        "output_nonempty": True,
        "output_hints": ["permission-denied", "missing-module"],
        "known_missing_modules": [],
        "application_startup_reported": True,
        "tmpfs_noexec": None,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 512
    assert "passed" not in result


@pytest.mark.parametrize("output", [None, [], {"secret": "private"}, True])
def test_nontext_startup_output_never_stringifies_candidate_data(output):
    result = startup_failure_diagnostic(output, True, [])
    assert result["output_readable"] is False
    assert result["http_status"] is None
    assert result["http_error"] == "other"
    assert result["output_hints"] == []
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "module", ["uvicorn", "fastapi", "sqlalchemy", "pydantic", "app", "access"]
)
def test_only_exact_public_module_names_can_be_reported(module):
    result = startup_failure_diagnostic(
        "ModuleNotFoundError: No module named '" + module + "'", 502, "none"
    )
    assert result["known_missing_modules"] == [module]
    assert (
        startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"] == []
    )


def test_native_loader_failure_is_not_mislabeled_as_missing_module():
    result = startup_failure_diagnostic(
        "ImportError: /private/secret: failed to map segment from shared object",
        502,
        "none",
        True,
    )
    assert result["output_hints"] == ["import-error", "native-library-mapping"]
    assert result["tmpfs_noexec"] is True
    assert "secret" not in json.dumps(result)
    assert startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None
````
