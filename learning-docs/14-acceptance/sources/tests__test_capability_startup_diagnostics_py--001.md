# tests/test_capability_startup_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_startup_hints_are_finite_even_for_secret_bearing_tracebacks`（L11–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L19断言`result == { "phase": "health_deadline", "http_status": 503, "http_error": "other", "o…`；L36断言`"secret" not in json.dumps(result)`；L37断言`len(json.dumps(result)) < 768`；L38断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nontext_startup_output_never_stringifies_candidate_data`（L42–L52）：接收`output`。 控制顺序：L44断言`result["output_readable"] is False`；L45断言`result["http_status"] is None`；L46断言`result["http_error"] == "other"`；L47断言`result["output_hints"] == []`；L48断言`result["startup_phase_hint"] == "unknown"`；L49断言`result["failure_component"] == "unknown"`；L50断言`result["exception_type"] == "unknown"`；L51断言`result["exception_errno"] is None`。后续分支沿下方源码相同行号继续阅读。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_public_module_names_can_be_reported`（L58–L65）：接收`module`。 控制顺序：L62断言`result["known_missing_modules"] == [module]`；L63断言`startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"]…`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_loader_failure_is_not_mislabeled_as_missing_module`（L68–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L75断言`result["output_hints"] == ["import-error", "native-library-mapping"]`；L76断言`result["tmpfs_noexec"] is True`；L77断言`"secret" not in json.dumps(result)`；L78断言`startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `colored`（L92–L93）：接收`text`。 调用`"\x1b[0m\x1b[38;2;1;2;3m".join`。 返回路径：L93的`"\x1b[31m" + "\x1b[0m\x1b[38;2;1;2;3m".join(text) + "\x1b[0m"`。
- `test_observed_sgr_can_split_exception_words_and_errno`（L96–L102）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99断言`result["exception_type"] == "FileNotFoundError"`；L100断言`result["exception_errno"] == 2`；L101断言`result["output_hints"] == ["missing-file"]`；L102断言`result["output_shapes"] == ["file-not-found-type", "ansi-control"]`。 调用`colored`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sgr_trace_retains_same_trace_association_with_later_cleanup`（L105–L114）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L112断言`result["failure_component"] == "multiprocessing-semaphore"`；L113断言`result["exception_type"] == "FileNotFoundError" and result["exception_errno"] == 2`；L114断言`"secret" not in json.dumps(result)`。 调用`"\n".join`、`SEMAPHORE_TRACE.splitlines`、`colored`、`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_oversize_and_non_sgr_sequences_are_not_interpreted`（L120–L124）：接收`prefix`。 控制顺序：L122断言`result["exception_type"] == "unknown"`；L123断言`result["failure_component"] == "unknown"`；L124断言`"private" not in json.dumps(result) and "secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stripped_control_bytes_do_not_create_a_larger_scan_window`（L127–L133）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L131断言`result["output_nonempty"] is True`；L132断言`result["exception_type"] == "unknown" and result["output_hints"] == []`；L133断言`result["output_shapes"] == ["ansi-control"]`。 调用`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sgr_from_another_trace_cannot_supply_a_semaphore_denial`（L136–L140）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L140断言`startup_failure_diagnostic(trace, 502, "none")["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace`、`"\n".join`、`(first + second).splitlines`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_semaphore_failure_requires_known_constructor_frames_and_denial`（L143–L151）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L145断言`result["failure_component"] == "multiprocessing-semaphore"`；L146断言`result["exception_type"] == "PermissionError"`；L147断言`result["exception_errno"] == 13`；L148断言`result["startup_phase_hint"] == "factory"`；L149断言`result["application_startup_reported"] is False`；L150断言`"secret" not in json.dumps(result)`；L151断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_or_unrelated_trace_does_not_claim_semaphore`（L166–L169）：接收`old`、`new`。 控制顺序：L168断言`result["failure_component"] == "unknown"`；L169断言`"private_constructor" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`SEMAPHORE_TRACE.replace`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_fixed_errno_values_are_emitted`（L173–L175）：接收`number`。 控制顺序：L175断言`result["exception_errno"] == number`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_errno_is_not_copied`（L179–L182）：接收`number`。 控制顺序：L181断言`result["exception_errno"] is None`；L182断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_unknown_error_does_not_hide_complete_earlier_trace`（L185–L192）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L189断言`result["exception_type"] == "unknown"`；L190断言`result["exception_errno"] is None`；L191断言`result["failure_component"] == "multiprocessing-semaphore"`；L192断言`"SecretError" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno`（L203–L216）：接收`separator`。 控制顺序：L212断言`result["failure_component"] == "multiprocessing-semaphore"`；L213断言`result["exception_type"] == "FileNotFoundError"`；L214断言`result["exception_errno"] == 2`；L215断言`result["output_hints"] == ["permission-denied", "missing-file"]`；L216断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrelated_permission_error_cannot_complete_a_constructor_trace`（L220–L229）：接收`header`。 控制顺序：L227断言`result["exception_type"] == "PermissionError"`；L228断言`result["exception_errno"] == 13`；L229断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_traceback_cannot_supply_a_semaphore_hint`（L232–L237）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L235遍历`(no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] p…`；L237断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.split`、`no_error.ljust`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_phase_is_only_a_fixed_hint`（L250–L253）：接收`output`、`phase`。 控制顺序：L252断言`result["startup_phase_hint"] == phase`；L253断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_outside_the_existing_output_bound_cannot_supply_a_hint`（L256–L261）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L258断言`result["failure_component"] == "unknown"`；L259断言`result["startup_phase_hint"] == "unknown"`；L260断言`result["exception_type"] == "unknown"`；L261断言`result["exception_errno"] is None`。 调用`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tail_traceback_preserves_final_error_without_joining_truncated_primary_trace`（L264–L279）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L276断言`result["failure_component"] == "unknown"`；L277断言`result["exception_type"] == "PermissionError"`；L278断言`result["exception_errno"] == 13`；L279断言`"secret" not in json.dumps(result)`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`primary.split`、`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_ascii_output_has_same_byte_budget_before_any_parsing`（L282–L288）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L284断言`result["failure_component"] == "unknown"`；L285断言`result["startup_phase_hint"] == "unknown"`；L286断言`result["exception_type"] == "unknown"`；L287断言`result["exception_errno"] is None`；L288断言`"汉" not in json.dumps(result, ensure_ascii=False)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_split_utf8_and_surrogate_data_never_escape_diagnostic`（L291–L297）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L295断言`result["exception_type"] == "PermissionError"`；L296断言`result["exception_errno"] == 13`；L297断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_command_exit_facts_use_status_only`（L304–L335）：接收`value`、`expected`、`monkeypatch`。 控制顺序：L330断言`startup_command_exit_status(process, "private-session", "private-command", 5) == expe…`；L334断言`seen == [5]`；L335断言`daytona_sessions._DEADLINE.get() is None`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`seen.append`、`daytona_sessions.harden_toolbox_transport`、`httpx.Client`、`Process`、`startup_command_exit_status`、`daytona_sessions._DEADLINE.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_command_exit_facts_use_status_only.get_command`（L321–L326）：接收`session_id`、`command_id`。 控制顺序：L322断言`session_id == "private-session" and command_id == "private-command"`。 调用`rest.request`、`Command.from_dict`。 返回路径：L324的`Command.from_dict( {"id": command_id, "command": "secret TOKEN=secret", "exitCode": value}…`。
- `test_pinned_sdk_null_or_omitted_exit_never_proves_running`（L339–L347）：接收`exit_present`。 控制顺序：L343按`exit_present`分支；L347断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`Command.from_dict`、`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_strict_exit_model_rejection_is_safe`（L351–L361）：接收`value`。 控制顺序：L361断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`pytest.raises`、`get_command`、`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_strict_exit_model_rejection_is_safe.get_command`（L355–L356）：接收`*args`。 调用`Command.from_dict`。 返回路径：L356的`Command.from_dict({"id": "fixture-command", "command": "secret", "exitCode": value})`。
- `test_malformed_exit_values_remain_unknown`（L365–L369）：接收`value`。 控制顺序：L369断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_different_command_remains_unknown`（L376–L378）：接收`command`。 控制顺序：L378断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline`（L381–L395）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L389遍历`(SimpleNamespace(), SimpleNamespace(get_session_command=unavailab…`；L390断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`；L393断言`daytona_sessions._DEADLINE.get() == 123`。 调用`daytona_sessions._DEADLINE.set`、`SimpleNamespace`、`startup_command_exit_status`、`daytona_sessions._DEADLINE.get`、`daytona_sessions._DEADLINE.reset`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline.unavailable`（L384–L385）：接收`*args`。 控制顺序：L385抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_command_status_classifier_cannot_disclose_arbitrary_values`（L399–L402）：接收`value`。 控制顺序：L401断言`result["command_exit_status"] == "unknown"`；L402断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L402。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16762`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9980b548241a09cfd17fdbee915a3ff6dcb03536ba2f26b66daa48773765d5e6"} -->
````python
# tests/test_capability_startup_diagnostics.py
"""Startup hints cannot become product acceptance or disclose candidate output."""

import json
from types import SimpleNamespace

import pytest

from workbench.capability_sandbox import startup_command_exit_status, startup_failure_diagnostic


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
        "output_shapes": [],
        "known_missing_modules": [],
        "startup_phase_hint": "unknown",
        "failure_component": "unknown",
        "exception_type": "PermissionError",
        "exception_errno": None,
        "application_startup_reported": True,
        "tmpfs_noexec": None,
        "command_exit_status": "unknown",
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


def colored(text):
    return "\x1b[31m" + "\x1b[0m\x1b[38;2;1;2;3m".join(text) + "\x1b[0m"


def test_observed_sgr_can_split_exception_words_and_errno():
    output = colored("FileNotFoundError: [Errno 2] No such file or directory")
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["missing-file"]
    assert result["output_shapes"] == ["file-not-found-type", "ansi-control"]


def test_sgr_trace_retains_same_trace_association_with_later_cleanup():
    # Ordinary per-line coloring stays comfortably within the original budget.
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in SEMAPHORE_TRACE.splitlines())
    trace += "\nTraceback (most recent call last):\n" + colored(
        "FileNotFoundError: [Errno 2] secret"
    )
    result = startup_failure_diagnostic(trace, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError" and result["exception_errno"] == 2
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "prefix", ["\x1b[", "\x1b[123", "\x1b[" + "1;" * 10000 + "m", "\x1b]0;private\x07"]
)
def test_incomplete_oversize_and_non_sgr_sequences_are_not_interpreted(prefix):
    result = startup_failure_diagnostic(prefix + "PermissionError: [Errno 13] secret", 502, "none")
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result) and "secret" not in json.dumps(result)


def test_stripped_control_bytes_do_not_create_a_larger_scan_window():
    result = startup_failure_diagnostic(
        "\x1b[0m" * 2000 + "PermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["output_nonempty"] is True
    assert result["exception_type"] == "unknown" and result["output_hints"] == []
    assert result["output_shapes"] == ["ansi-control"]


def test_sgr_from_another_trace_cannot_supply_a_semaphore_denial():
    first = SEMAPHORE_TRACE.replace("PermissionError: [Errno 13]", "FileNotFoundError: [Errno 2]")
    second = "Traceback (most recent call last):\nPermissionError: [Errno 13] secret"
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in (first + second).splitlines())
    assert startup_failure_diagnostic(trace, 502, "none")["failure_component"] == "unknown"


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


def test_tail_traceback_preserves_final_error_without_joining_truncated_primary_trace():
    primary = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    output = (
        primary.split("\n", 1)[1]
        + "\nDuring handling of the above exception, another exception occurred:\n\n"
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "PermissionError: [Errno 13] secret\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


def test_non_ascii_output_has_same_byte_budget_before_any_parsing():
    result = startup_failure_diagnostic("汉" * 2667 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert "汉" not in json.dumps(result, ensure_ascii=False)


def test_split_utf8_and_surrogate_data_never_escape_diagnostic():
    result = startup_failure_diagnostic(
        "\ufffd\udc80secret\nPermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "value,expected",
    [(0, "zero"), (1, "nonzero"), (137, "nonzero"), (255, "nonzero")],
)
def test_pinned_sdk_command_exit_facts_use_status_only(value, expected, monkeypatch):
    import httpx
    from daytona._sync.process import Process
    from daytona_toolbox_api_client.models.command import Command

    from workbench import daytona_sessions

    seen = []
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: 100)
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda *a, **k: seen.append(k["_request_timeout"]),
    )
    daytona_sessions.harden_toolbox_transport(
        SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest))
    )

    def get_command(*, session_id, command_id):
        assert session_id == "private-session" and command_id == "private-command"
        rest.request("GET", "local")
        return Command.from_dict(
            {"id": command_id, "command": "secret TOKEN=secret", "exitCode": value}
        )

    with httpx.Client(trust_env=False) as client:
        process = Process("python", SimpleNamespace(get_session_command=get_command), client)
        assert (
            startup_command_exit_status(process, "private-session", "private-command", 5)
            == expected
        )
    assert seen == [5]
    assert daytona_sessions._DEADLINE.get() is None


@pytest.mark.parametrize("exit_present", [False, True])
def test_pinned_sdk_null_or_omitted_exit_never_proves_running(exit_present):
    from daytona_toolbox_api_client.models.command import Command

    payload = {"id": "fixture-command", "command": "secret"}
    if exit_present:
        payload["exitCode"] = None
    command = Command.from_dict(payload)
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [True, False, "1", 1.0])
def test_pinned_sdk_strict_exit_model_rejection_is_safe(value):
    from daytona_toolbox_api_client.models.command import Command
    from pydantic import ValidationError

    def get_command(*args):
        return Command.from_dict({"id": "fixture-command", "command": "secret", "exitCode": value})

    with pytest.raises(ValidationError):
        get_command()
    process = SimpleNamespace(get_session_command=get_command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [None, True, False, "1", 1.0, [], {}, -1, 256, 10**100])
def test_malformed_exit_values_remain_unknown(value):
    process = SimpleNamespace(
        get_session_command=lambda *a: SimpleNamespace(id="fixture-command", exit_code=value)
    )
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize(
    "command",
    [None, SimpleNamespace(), SimpleNamespace(id="other-command", exit_code=1)],
)
def test_missing_or_different_command_remains_unknown(command):
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


def test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline():
    from workbench import daytona_sessions

    def unavailable(*args):
        raise RuntimeError("secret session, command and SDK body")

    token = daytona_sessions._DEADLINE.set(123)
    try:
        for process in (SimpleNamespace(), SimpleNamespace(get_session_command=unavailable)):
            assert (
                startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"
            )
            assert daytona_sessions._DEADLINE.get() == 123
    finally:
        daytona_sessions._DEADLINE.reset(token)


@pytest.mark.parametrize("value", [True, 1, [], {"secret": "secret"}, "running", "secret"])
def test_command_status_classifier_cannot_disclose_arbitrary_values(value):
    result = startup_failure_diagnostic("", 502, "none", command_exit_status=value)
    assert result["command_exit_status"] == "unknown"
    assert "secret" not in json.dumps(result)
````
