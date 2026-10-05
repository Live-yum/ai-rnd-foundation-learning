# tests/test_capability_startup_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_startup_hints_are_finite_even_for_secret_bearing_tracebacks`（L10–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L18断言`result == { "phase": "health_deadline", "http_status": 503, "http_error": "other", "o…`；L33断言`"secret" not in json.dumps(result)`；L34断言`len(json.dumps(result)) < 768`；L35断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nontext_startup_output_never_stringifies_candidate_data`（L39–L49）：接收`output`。 控制顺序：L41断言`result["output_readable"] is False`；L42断言`result["http_status"] is None`；L43断言`result["http_error"] == "other"`；L44断言`result["output_hints"] == []`；L45断言`result["startup_phase_hint"] == "unknown"`；L46断言`result["failure_component"] == "unknown"`；L47断言`result["exception_type"] == "unknown"`；L48断言`result["exception_errno"] is None`。后续分支沿下方源码相同行号继续阅读。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_public_module_names_can_be_reported`（L55–L62）：接收`module`。 控制顺序：L59断言`result["known_missing_modules"] == [module]`；L60断言`startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"]…`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_loader_failure_is_not_mislabeled_as_missing_module`（L65–L75）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L72断言`result["output_hints"] == ["import-error", "native-library-mapping"]`；L73断言`result["tmpfs_noexec"] is True`；L74断言`"secret" not in json.dumps(result)`；L75断言`startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_semaphore_failure_requires_known_constructor_frames_and_denial`（L89–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L91断言`result["failure_component"] == "multiprocessing-semaphore"`；L92断言`result["exception_type"] == "PermissionError"`；L93断言`result["exception_errno"] == 13`；L94断言`result["startup_phase_hint"] == "factory"`；L95断言`result["application_startup_reported"] is False`；L96断言`"secret" not in json.dumps(result)`；L97断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_or_unrelated_trace_does_not_claim_semaphore`（L112–L115）：接收`old`、`new`。 控制顺序：L114断言`result["failure_component"] == "unknown"`；L115断言`"private_constructor" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`SEMAPHORE_TRACE.replace`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_fixed_errno_values_are_emitted`（L119–L121）：接收`number`。 控制顺序：L121断言`result["exception_errno"] == number`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_errno_is_not_copied`（L125–L128）：接收`number`。 控制顺序：L127断言`result["exception_errno"] is None`；L128断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_unknown_error_does_not_hide_complete_earlier_trace`（L131–L138）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L135断言`result["exception_type"] == "unknown"`；L136断言`result["exception_errno"] is None`；L137断言`result["failure_component"] == "multiprocessing-semaphore"`；L138断言`"SecretError" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno`（L149–L162）：接收`separator`。 控制顺序：L158断言`result["failure_component"] == "multiprocessing-semaphore"`；L159断言`result["exception_type"] == "FileNotFoundError"`；L160断言`result["exception_errno"] == 2`；L161断言`result["output_hints"] == ["permission-denied", "missing-file"]`；L162断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrelated_permission_error_cannot_complete_a_constructor_trace`（L166–L175）：接收`header`。 控制顺序：L173断言`result["exception_type"] == "PermissionError"`；L174断言`result["exception_errno"] == 13`；L175断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_traceback_cannot_supply_a_semaphore_hint`（L178–L183）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L181遍历`(no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] p…`；L183断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.split`、`no_error.ljust`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_phase_is_only_a_fixed_hint`（L196–L199）：接收`output`、`phase`。 控制顺序：L198断言`result["startup_phase_hint"] == phase`；L199断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_outside_the_existing_output_bound_cannot_supply_a_hint`（L202–L207）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L204断言`result["failure_component"] == "unknown"`；L205断言`result["startup_phase_hint"] == "unknown"`；L206断言`result["exception_type"] == "unknown"`；L207断言`result["exception_errno"] is None`。 调用`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L207。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8376`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3dbde794ee5e68b63a5717e2f48e43534c8b145f72d7704d728fb9e9836f43c1"} -->
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
        "startup_phase_hint": "unknown",
        "failure_component": "unknown",
        "exception_type": "PermissionError",
        "exception_errno": None,
        "application_startup_reported": True,
        "tmpfs_noexec": None,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 768
    assert "passed" not in result


@pytest.mark.parametrize("output", [None, [], {"secret": "private"}, True])
def test_nontext_startup_output_never_stringifies_candidate_data(output):
    result = startup_failure_diagnostic(output, True, [])
    assert result["output_readable"] is False
    assert result["http_status"] is None
    assert result["http_error"] == "other"
    assert result["output_hints"] == []
    assert result["startup_phase_hint"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
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


SEMAPHORE_TRACE = """Traceback (most recent call last):
  File "/private/secret/backend/app/__init__.py", line 146, in create_app
    register_routers(app)
  File "/private/secret/python/concurrent/futures/process.py", line 731, in __init__
    self._call_queue = _SafeQueue(
  File "/private/secret/python/multiprocessing/synchronize.py", line 57, in __init__
    sl = self._semlock = _multiprocessing.SemLock(
PermissionError: [Errno 13] Permission denied: '/private/secret'
"""


def test_semaphore_failure_requires_known_constructor_frames_and_denial():
    result = startup_failure_diagnostic(SEMAPHORE_TRACE, 502, "none", True)
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["startup_phase_hint"] == "factory"
    assert result["application_startup_reported"] is False
    assert "secret" not in json.dumps(result)
    assert "passed" not in result


@pytest.mark.parametrize(
    "old,new",
    [
        ("concurrent/futures/process.py", "private/secret.py"),
        ("multiprocessing/synchronize.py", "private/secret.py"),
        ("_multiprocessing.SemLock(", "private_constructor("),
        ("in __init__", "in private_constructor"),
        ("PermissionError", "FileNotFoundError"),
        ("[Errno 13]", "[Errno 2]"),
        ("[Errno 13]", "[Errno 9999999999]"),
    ],
)
def test_partial_or_unrelated_trace_does_not_claim_semaphore(old, new):
    result = startup_failure_diagnostic(SEMAPHORE_TRACE.replace(old, new), 502, "none")
    assert result["failure_component"] == "unknown"
    assert "private_constructor" not in json.dumps(result)


@pytest.mark.parametrize("number", [1, 2, 13, 28, 30])
def test_only_fixed_errno_values_are_emitted(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] == number


@pytest.mark.parametrize("number", [0, -1, 5, 42, 9999999999999999999999999999])
def test_unknown_errno_is_not_copied(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] is None
    assert "secret" not in json.dumps(result)


def test_terminal_unknown_error_does_not_hide_complete_earlier_trace():
    result = startup_failure_diagnostic(
        SEMAPHORE_TRACE + "\nprivate.SecretError: [Errno 13] secret\n", 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert "SecretError" not in json.dumps(result)


@pytest.mark.parametrize(
    "separator",
    [
        "\n",
        "\nDuring handling of the above exception, another exception occurred:\n\n",
        "\nThe above exception was the direct cause of the following exception:\n\n",
    ],
)
def test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno(separator):
    output = (
        SEMAPHORE_TRACE
        + separator
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "FileNotFoundError: [Errno 2] No such file or directory: '/private/secret'\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["permission-denied", "missing-file"]
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize("header", ["", "Traceback (most recent call last):\n"])
def test_unrelated_permission_error_cannot_complete_a_constructor_trace(header):
    unrelated = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    result = startup_failure_diagnostic(
        unrelated + "\n" + header + "PermissionError: [Errno 13] private\n", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["failure_component"] == "unknown"


def test_incomplete_traceback_cannot_supply_a_semaphore_hint():
    no_header = SEMAPHORE_TRACE.split("\n", 1)[1]
    no_error = SEMAPHORE_TRACE.split("PermissionError:", 1)[0]
    for output in (no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] private"):
        result = startup_failure_diagnostic(output, 502, "none")
        assert result["failure_component"] == "unknown"


@pytest.mark.parametrize(
    "output,phase",
    [
        ('  File "/secret/uvicorn/importer.py", line 10, in import_from_string\n', "import"),
        (SEMAPHORE_TRACE, "factory"),
        ("INFO:     Waiting for application startup.\n" + SEMAPHORE_TRACE, "lifespan"),
        ("ERROR:    Application startup failed. Exiting.", "lifespan"),
        ("private-phase secret", "unknown"),
    ],
)
def test_startup_phase_is_only_a_fixed_hint(output, phase):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["startup_phase_hint"] == phase
    assert "secret" not in json.dumps(result)


def test_context_outside_the_existing_output_bound_cannot_supply_a_hint():
    result = startup_failure_diagnostic("x" * 8000 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
````
