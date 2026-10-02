# tests/test_native_delivery_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product_reports`（L14–L18）：接收`tmp_path`。 调用`reports.mkdir`。 返回路径：L18的`product, reports`。
- `test_failed_delivery_captures_only_safe_structured_lifecycle_and_redacted_logs`（L21–L98）：接收`tmp_path`。 控制顺序：L65遍历`("credentials.json", "services.env", "portable-start.json", "othe…`；L69断言`result["affects_acceptance"] is False`；L70断言`result["failure_phase"] == "backend-readiness"`；L71断言`result["backend"]["startup_attempt"] == 2`；L72断言`result["backend"]["port"] == 48080 and result["backend"]["pid"] == 731`；L73断言`result["backend"]["returncode"] == 42`；L74断言`result["backend"]["port_state_before_cleanup"]["local_port_state_counts"] == {"06": 2…`；L75断言`set(result["logs"]) == set(portable.DIAGNOSTIC_LOGS)`。后续分支沿下方源码相同行号继续阅读。 调用`product_reports`、`write_json`、`atomic_text`、`portable.capture_native_delivery_failure`、`set`、`json.dumps`、`json.loads`、`(tmp_path / "out/portable-failure-diagnostics.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_log_tails_have_per_file_and_shared_byte_budgets`（L101–L111）：接收`tmp_path`。 控制顺序：L103遍历`portable.DIAGNOSTIC_LOGS`；L107断言`all(len(row.get("text", "").encode("utf-8")) <= 65536 for row in rows)`；L108断言`sum(len(row.get("text", "").encode("utf-8")) for row in rows) <= 262144`；L109断言`result["logs"]["backend-runtime.log"]["text"].endswith("final failure\n")`；L110断言`result["logs"]["backend-runtime.log"]["truncated"] is True`；L111断言`any(row["status"] == "budget-exhausted" for row in rows)`。 调用`product_reports`、`atomic_text`、`portable.capture_native_delivery_failure`、`result["logs"].values`、`all`、`len`、`row.get("text", "").encode`、`row.get`、`sum`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_first_line_is_discarded_and_redaction_precedes_output_clipping`（L114–L125）：接收`tmp_path`。 控制顺序：L123断言`"partial-private-tail" not in body and "secret" not in body`；L124断言`result["logs"]["backend-runtime.log"]["text"].endswith("last failure\n")`；L125断言`"[REDACTED]" in result["logs"]["frontend-runtime.log"]["text"]`。 调用`product_reports`、`atomic_text`、`portable.capture_native_delivery_failure`、`json.dumps`、`result["logs"]["backend-runtime.log"]["text"].endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_known_database_secret_cannot_leak_at_a_read_or_output_boundary`（L129–L138）：接收`tmp_path`、`boundary`。 控制顺序：L137断言`"ssword" not in captured and secret not in captured`；L138断言`result["logs"]["backend-runtime.log"]["truncated"] is True`。 调用`product_reports`、`len`、`atomic_text`、`portable.capture_native_delivery_failure`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_serialized_receipt_is_bounded_with_control_character_heavy_logs`（L141–L152）：接收`tmp_path`。 控制顺序：L143遍历`portable.DIAGNOSTIC_LOGS`；L147断言`receipt.stat().st_size <= portable.DIAGNOSTIC_RECEIPT_BYTES`；L149断言`sum(len(row.get("text", "").encode("utf-8")) for row in result["logs"].values()) <= p…`。 调用`product_reports`、`atomic_text`、`portable.capture_native_delivery_failure`、`receipt.stat`、`json.loads`、`receipt.read_text`、`sum`、`len`、`row.get("text", "").encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostics_never_follow_leaf_or_parent_symlinks`（L156–L171）：接收`tmp_path`、`parent`。 控制顺序：L162按`parent`分支；L170断言`result["logs"]["backend-runtime.log"]["status"] == "unavailable"`；L171断言`"private-symlink-target" not in json.dumps(result)`。 调用`product_reports`、`external.mkdir`、`atomic_text`、`source.rmdir`、`source.symlink_to`、`(source / "backend-runtime.log").symlink_to`、`pytest.skip`、`portable.capture_native_delivery_failure`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostics_reject_special_files_without_opening_them`（L175–L179）：接收`tmp_path`。 控制顺序：L179断言`result["logs"]["backend-runtime.log"]["status"] == "unavailable"`。 调用`product_reports`、`os.mkfifo`、`portable.capture_native_delivery_failure`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lifecycle_invalid_or_oversized_data_cannot_prevent_log_retention`（L183–L189）：接收`tmp_path`、`value`。 控制顺序：L188断言`result["logs"]["backend-runtime.log"]["text"] == "actual child failure"`；L189断言`result["failure_phase"] == "standalone-launcher"`。 调用`product_reports`、`atomic_text`、`portable.capture_native_delivery_failure`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db`（L195–L283）：接收`tmp_path`、`monkeypatch`、`mode`。 控制顺序：L246按`mode == "diagnostic-io-failure"`分支；L254按`mode == "success"`分支；L256断言`result["archive_round_trip"] is True`；L257断言`not (output / "portable-failure-diagnostics.json").exists()`；L261按`mode != "invalid-receipt"`分支；L262断言`raised.value is failure`；L263断言`not (output / "portable-start.json").exists()`；L264按`mode != "diagnostic-io-failure"`分支。后续分支沿下方源码相同行号继续阅读。 调用`product.mkdir`、`atomic_text`、`monkeypatch.setattr`、`Connection`、`tools.ToolFailure`、`portable.verify_native_delivery`、`(output / "portable-failure-diagnostics.json").exists`、`pytest.raises`、`(output / "portable-start.json").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.Connection`（L203–L211）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.Connection.__enter__`（L204–L205）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L205的`self`。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.Connection.__exit__`（L207–L208）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.Connection.execute`（L210–L211）：接收`statement`。 调用`operations.append`、`statement.as_string`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.run`（L218–L243）：接收`command`、`cwd`、`timeout`、`env`、`**kwargs`。 控制顺序：L220断言`env["NATIVE_DELIVERY_DATABASE_URL"] != URL`；L221断言`command[-1] == "--check" and timeout == 2100`；L233按`mode in {"process-failure", "diagnostic-io-failure"}`分支；L234抛异常，停止当前正常路径。 调用`copies.append`、`atomic_text`、`write_json`。 返回路径：L243的`{"log": "explicit fake successful console"}`。
- `test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db.unavailable`（L248–L250）：接收`*args`、`**kwargs`。 控制顺序：L249断言`copies[-1].is_dir()`；L250抛异常，停止当前正常路径。 调用`copies[-1].is_dir`、`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_delivery_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L283。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12229`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_delivery_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ff89d24e677f2011ecc865db807f5ee9acbeba74bb9e53207ad330da8cc3795e"} -->
````python
# tests/test_native_delivery_diagnostics.py
"""Portable failure evidence survives cleanup without exporting runtime secrets."""

import json
import os

import pytest

from workbench import portable, tools
from workbench.filesystem import atomic_text, write_json

URL = "postgresql+psycopg://fixture:db-p%40ssword@127.0.0.1/fixture_codegen"


def product_reports(tmp_path):
    product = tmp_path / "product"
    reports = product / ".deployment/reports"
    reports.mkdir(parents=True)
    return product, reports


def test_failed_delivery_captures_only_safe_structured_lifecycle_and_redacted_logs(tmp_path):
    product, source = product_reports(tmp_path)
    write_json(
        source / "backend-lifecycle.json",
        {
            "port": 48080,
            "pid": 731,
            "startup_attempt": 2,
            "runtime_log_start_bytes": 2345,
            "returncode": 42,
            "returncode_before_cleanup": 42,
            "owned_process_group": True,
            "started": True,
            "port_released": False,
            "phase": "backend-cleanup",
            "failure": {
                "phase": "backend-readiness",
                "type": "RuntimeError",
                "message": "private-message",
            },
            "cleanup_failure": {"type": "RuntimeError", "message": "private-cleanup"},
            "environment": {"SECRET": "private-environment"},
            "port_state_before_cleanup": {
                "observable": True,
                "listening": False,
                "owned_listener": False,
                "owned_group_pids": [731],
                "owned_listener_pids": [],
                "owned_socket_pids": [731],
                "local_port_state_counts": {"06": 2},
                "command": "private-command",
                "address": "private-address",
            },
        },
    )
    atomic_text(
        source / "backend-runtime.log",
        "FAILED on second startup\n"
        + URL
        + "\ndb-p@ssword db-p%40ssword password=plain-private "
        + 'NATIVE_DB_PASSWORD=env-private {"accessToken":"json-private"} '
        + "Authorization: Bearer bearer-private Basic basic-private "
        + "jdbc:postgresql://user:url-private@127.0.0.1/db\n",
    )
    for name in ("credentials.json", "services.env", "portable-start.json", "other.log"):
        atomic_text(source / name, "never-export-runtime-data")
    atomic_text(product / ".deployment/services.json", "never-export-service-credentials")
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    assert result["affects_acceptance"] is False
    assert result["failure_phase"] == "backend-readiness"
    assert result["backend"]["startup_attempt"] == 2
    assert result["backend"]["port"] == 48080 and result["backend"]["pid"] == 731
    assert result["backend"]["returncode"] == 42
    assert result["backend"]["port_state_before_cleanup"]["local_port_state_counts"] == {"06": 2}
    assert set(result["logs"]) == set(portable.DIAGNOSTIC_LOGS)
    body = json.dumps(result)
    for secret in (
        "db-p@ssword",
        "db-p%40ssword",
        "plain-private",
        "env-private",
        "json-private",
        "bearer-private",
        "basic-private",
        "url-private",
        "private-message",
        "private-cleanup",
        "private-environment",
        "private-command",
        "private-address",
        "never-export",
    ):
        assert secret not in body
    assert "FAILED on second startup" in body
    assert (
        json.loads((tmp_path / "out/portable-failure-diagnostics.json").read_text(encoding="utf-8"))
        == result
    )


def test_diagnostic_log_tails_have_per_file_and_shared_byte_budgets(tmp_path):
    product, source = product_reports(tmp_path)
    for name in portable.DIAGNOSTIC_LOGS:
        atomic_text(source / name, "bounded normal line\n" * 40000 + "final failure\n")
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    rows = result["logs"].values()
    assert all(len(row.get("text", "").encode("utf-8")) <= 65536 for row in rows)
    assert sum(len(row.get("text", "").encode("utf-8")) for row in rows) <= 262144
    assert result["logs"]["backend-runtime.log"]["text"].endswith("final failure\n")
    assert result["logs"]["backend-runtime.log"]["truncated"] is True
    assert any(row["status"] == "budget-exhausted" for row in rows)


def test_partial_first_line_is_discarded_and_redaction_precedes_output_clipping(tmp_path):
    product, source = product_reports(tmp_path)
    atomic_text(
        source / "backend-runtime.log",
        "first" * 70000 + "partial-private-tail\n" + "safe\n" * 100 + "last failure\n",
    )
    atomic_text(source / "frontend-runtime.log", 'password="' + "secret" * 14000 + '"\nlast\n')
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    body = json.dumps(result)
    assert "partial-private-tail" not in body and "secret" not in body
    assert result["logs"]["backend-runtime.log"]["text"].endswith("last failure\n")
    assert "[REDACTED]" in result["logs"]["frontend-runtime.log"]["text"]


@pytest.mark.parametrize("boundary", ["read", "output"])
def test_known_database_secret_cannot_leak_at_a_read_or_output_boundary(tmp_path, boundary):
    product, source = product_reports(tmp_path)
    secret = "db-p@ssword"
    budget = portable.DIAGNOSTIC_READ_BYTES if boundary == "read" else portable.DIAGNOSTIC_LOG_BYTES
    text = "preamble\n" + secret + "\n" + "z" * (budget - len(secret) + 3)
    atomic_text(source / "backend-runtime.log", text)
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    captured = result["logs"]["backend-runtime.log"]["text"]
    assert "ssword" not in captured and secret not in captured
    assert result["logs"]["backend-runtime.log"]["truncated"] is True


def test_serialized_receipt_is_bounded_with_control_character_heavy_logs(tmp_path):
    product, source = product_reports(tmp_path)
    for name in portable.DIAGNOSTIC_LOGS:
        atomic_text(source / name, "\x00\x01\x02\x03\x04\x05\n" * 40000)
    portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    receipt = tmp_path / "out/portable-failure-diagnostics.json"
    assert receipt.stat().st_size <= portable.DIAGNOSTIC_RECEIPT_BYTES
    result = json.loads(receipt.read_text(encoding="utf-8"))
    assert (
        sum(len(row.get("text", "").encode("utf-8")) for row in result["logs"].values())
        <= portable.DIAGNOSTIC_TOTAL_BYTES
    )


@pytest.mark.parametrize("parent", [False, True])
def test_diagnostics_never_follow_leaf_or_parent_symlinks(tmp_path, parent):
    product, source = product_reports(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    atomic_text(external / "backend-runtime.log", "private-symlink-target")
    try:
        if parent:
            source.rmdir()
            source.symlink_to(external, target_is_directory=True)
        else:
            (source / "backend-runtime.log").symlink_to(external / "backend-runtime.log")
    except OSError:
        pytest.skip("Host does not permit creating test symlinks")
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    assert result["logs"]["backend-runtime.log"]["status"] == "unavailable"
    assert "private-symlink-target" not in json.dumps(result)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX special-file regression")
def test_diagnostics_reject_special_files_without_opening_them(tmp_path):
    product, source = product_reports(tmp_path)
    os.mkfifo(source / "backend-runtime.log")
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    assert result["logs"]["backend-runtime.log"]["status"] == "unavailable"


@pytest.mark.parametrize("value", ["{" * 16385, "not JSON", "[]", '{"phase":[]}'])
def test_lifecycle_invalid_or_oversized_data_cannot_prevent_log_retention(tmp_path, value):
    product, source = product_reports(tmp_path)
    atomic_text(source / "backend-lifecycle.json", value)
    atomic_text(source / "backend-runtime.log", "actual child failure")
    result = portable.capture_native_delivery_failure(product, tmp_path / "out", URL)
    assert result["logs"]["backend-runtime.log"]["text"] == "actual child failure"
    assert result["failure_phase"] == "standalone-launcher"


@pytest.mark.parametrize(
    "mode", ["process-failure", "invalid-receipt", "success", "diagnostic-io-failure"]
)
def test_verification_preserves_failure_before_temp_cleanup_and_drops_only_owned_db(
    tmp_path, monkeypatch, mode
):
    product = tmp_path / "source"
    product.mkdir()
    atomic_text(product / "start.py", "# Explicit fake child for evidence unit regression\n")
    operations, copies = [], []

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, statement):
            operations.append(statement.as_string())

    monkeypatch.setattr(portable.psycopg, "connect", lambda *a, **kw: Connection())
    failure = tools.ToolFailure("original child failed")
    failure.log = "console password=console-private\n"
    failure.returncode, failure.timed_out = 1, False

    def run(command, cwd, timeout, env, **kwargs):
        copies.append(cwd)
        assert env["NATIVE_DELIVERY_DATABASE_URL"] != URL
        assert command[-1] == "--check" and timeout == 2100
        atomic_text(cwd / ".deployment/reports/backend-runtime.log", "actual child failure")
        write_json(
            cwd / ".deployment/reports/backend-lifecycle.json",
            {
                "pid": 912,
                "port": 48080,
                "startup_attempt": 2,
                "returncode": 42,
                "failure": {"phase": "backend-readiness", "type": "RuntimeError"},
            },
        )
        if mode in {"process-failure", "diagnostic-io-failure"}:
            raise failure
        write_json(
            cwd / ".deployment/reports/portable-start.json",
            {
                "passed": True,
                "frontend_started": mode == "success",
                "restart": True,
            },
        )
        return {"log": "explicit fake successful console"}

    monkeypatch.setattr(tools, "run_command", run)
    if mode == "diagnostic-io-failure":

        def unavailable(*args, **kwargs):
            assert copies[-1].is_dir()
            raise OSError("private diagnostic exception")

        monkeypatch.setattr(portable, "capture_native_delivery_failure", unavailable)
    output = tmp_path / "out"
    if mode == "success":
        result = portable.verify_native_delivery(product, URL, output, template="yudao-vben")
        assert result["archive_round_trip"] is True
        assert not (output / "portable-failure-diagnostics.json").exists()
    else:
        with pytest.raises((tools.ToolFailure, ValueError)) as raised:
            portable.verify_native_delivery(product, URL, output, template="yudao-vben")
        if mode != "invalid-receipt":
            assert raised.value is failure
        assert not (output / "portable-start.json").exists()
        if mode != "diagnostic-io-failure":
            result = json.loads(
                (output / "portable-failure-diagnostics.json").read_text(encoding="utf-8")
            )
            assert result["failure_phase"] == "backend-readiness"
            assert result["logs"]["backend-runtime.log"]["text"] == "actual child failure"
            if mode == "process-failure":
                assert result["launcher_failure"] == {
                    "type": "ToolFailure",
                    "returncode": 1,
                    "timed_out": False,
                }
        else:
            assert "Could not retain" in str(failure.__notes__)
            assert "private diagnostic" not in str(failure.__notes__)
    assert len(copies) == 1 and not copies[0].exists()
    assert len(operations) == 2
    assert operations[0].startswith('CREATE DATABASE "restore_')
    assert operations[1].startswith('DROP DATABASE "restore_')
    assert "console-private" not in (output / "portable-start.log").read_text(encoding="utf-8")
````
