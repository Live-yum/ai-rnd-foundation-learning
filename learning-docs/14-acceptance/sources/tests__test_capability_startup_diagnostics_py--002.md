# tests/test_capability_startup_diagnostics.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_capability_startup_diagnostics_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_sandbox`、`workbench.capability_startup_paths`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_terminal_suffixless_unknown_suppresses_prior_known_exception`（L911–L924）：接收`renderer`、`message`、`lowercase`。 控制顺序：L921断言`result["exception_type"] == "unknown"`；L922断言`result["failure_component"] == "unknown"`；L923断言`"PrivateFailure" not in json.dumps(result)`；L924断言`"private" not in json.dumps(result)`。 调用`privatefailure if lowercase else PrivateFailure`、`TypeError`、`startup_failure_diagnostic`、`renderer`、`json.dumps`、`pytest.mark.parametrize`、`rich_trace`、`"".join`、`traceback.format_exception`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_suffixless_unknown_suppresses_prior_known_exception.PrivateFailure`（L912–L913）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_terminal_suffixless_unknown_suppresses_prior_known_exception.privatefailure`（L915–L916）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_rich_console_modes_preserve_terminal_chain`（L931–L955）：接收`legacy_windows`、`panel`、`empty`、`terminal_kind`。 控制顺序：L946断言`len(output.encode()) < NATIVE_TAIL_LIMIT`；L947按`panel`分支；L949断言`left in output.splitlines()[-1] and right in output.splitlines()[-1]`；L951断言`result["exception_type"] == ("KeyError" if terminal_kind == "known" else "unknown")`；L952断言`result["failure_component"] == "unknown"`；L953断言`result["output_read_limit_reached"] is False`；L954断言`"PrivateFailure" not in json.dumps(result)`；L955断言`"private" not in json.dumps(result)`。 调用`exception`、`TypeError`、`rich_trace`、`len`、`output.encode`、`output.splitlines`、`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_console_modes_preserve_terminal_chain.PrivateFailure`（L934–L935）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_rich_console_modes_preserve_terminal_chain.privatefailure`（L937–L938）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_framework_prefix_never_authorizes_a_private_exception`（L968–L974）：接收`alias`。 控制顺序：L972断言`result["exception_type"] == "unknown"`；L973断言`"PrivateFailure" not in json.dumps(result)`；L974断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cut_unknown_name_cannot_become_a_known_empty_exception`（L978–L984）：接收`prefix`。 控制顺序：L983断言`result["output_read_limit_reached"] is True`；L984断言`result["exception_type"] == "unknown"`。 调用`len`、`(prefix + "TypeError").encode`、`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_bare_exception_newline_remains_known_at_exact_cap`（L987–L991）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L990断言`result["output_read_limit_reached"] is True`；L991断言`result["exception_type"] == "TypeError"`。 调用`startup_failure_diagnostic`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_interface_failure_requires_same_closed_info_block`（L1009–L1020）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1010断言`node_failure_facts(NODE_SYSTEM_ERROR) == { "error_code": "ERR_SYSTEM_ERROR", "errno":…`；L1019断言`node_failure_facts(colored_output) == node_failure_facts(NODE_SYSTEM_ERROR)`；L1020断言`"private" not in json.dumps(node_failure_facts(NODE_SYSTEM_ERROR))`。 调用`node_failure_facts`、`"\n".join`、`NODE_SYSTEM_ERROR.splitlines`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_missing_conflicting_or_unrelated_properties_stay_unknown`（L1035–L1039）：接收`old`、`new`。 控制顺序：L1037断言`result["component"] == "unknown" and result["syscall"] == "unknown"`；L1038断言`"private" not in json.dumps(result)`；L1039断言`"ERR_PRIVATE" not in json.dumps(result)`。 调用`node_failure_facts`、`NODE_SYSTEM_ERROR.replace`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_properties_cannot_cross_error_records_or_truncated_boundaries`（L1042–L1055）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1045遍历`( first + second, NODE_SYSTEM_ERROR + "Error: private-terminal\n …`；L1054断言`result["component"] == "unknown"`；L1055断言`"private" not in json.dumps(result)`。 调用`NODE_SYSTEM_ERROR.replace`、`NODE_SYSTEM_ERROR.index`、`node_failure_facts`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `node_error_fixture_script`（L1058–L1088）：接收`code`、`errno`、`logged`。 控制顺序：L1061按`code == "ERR_SYSTEM_ERROR"`分支。 调用`json.dumps`。 返回路径：L1084的`"Error.stackTraceLimit=1;const {codes,UVException}=require('internal/errors');" + construc…`。
- `test_actual_node_formatter_produces_only_verified_public_facts`（L1098–L1119）：接收`code`、`errno`、`logged`。 控制顺序：L1112断言`process.returncode == (0 if logged else 1)`；L1114断言`result["error_code"] == code and result["errno"] == errno`；L1115断言`result["syscall"] == ("uv_interface_addresses" if code == "ERR_SYSTEM_ERROR" else "op…`；L1116断言`result["component"] == ( "node-interface-enumeration" if code == "ERR_SYSTEM_ERROR" e…`；L1119断言`"private" not in json.dumps(result)`。 调用`node_error_fixture_script`、`subprocess.run`、`shutil.which`、`os.environ.items`、`node_failure_facts`、`json.dumps`、`pytest.mark.skipif`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_node_fixture_handles_windows_libuv_map`（L1130–L1171）：接收`code`、`errno`、`windows_errno`、`logged`。 控制顺序：L1164断言`process.returncode == (0 if logged else 1)`；L1165断言`json.loads(process.stdout) == {"old_code": "UNKNOWN", "host_errno": windows_errno}`；L1166断言`node_failure_facts(process.stderr) == { "error_code": code, "errno": errno, "syscall"…`。 调用`json.dumps`、`subprocess.run`、`shutil.which`、`node_error_fixture_script`、`os.environ.items`、`json.loads`、`node_failure_facts`、`pytest.mark.skipif`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_command_identity_cannot_issue_a_status_query`（L1176–L1185）：接收`value`、`field`。 控制顺序：L1182断言`startup_command_exit_facts(process, **identities, timeout=5) == { "command_exit_statu…`。 调用`SimpleNamespace`、`pytest.fail`、`startup_command_exit_facts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_node_suffixless_terminal_error_cannot_borrow_prior_component`（L1193–L1226）：接收`name`、`logged`。 控制顺序：L1216断言`process.returncode == (0 if logged else 1)`；L1217断言`"ERR_SYSTEM_ERROR" in process.stderr and name + ": private-sentinel" in process.stder…`；L1218断言`len(process.stderr.encode()) < NATIVE_TAIL_LIMIT`；L1220断言`result == { "error_code": "unknown", "errno": None, "syscall": "unknown", "component"…`；L1226断言`name not in json.dumps(result, ensure_ascii=False)`。 调用`json.dumps`、`subprocess.run`、`shutil.which`、`os.environ.items`、`len`、`process.stderr.encode`、`node_failure_facts`、`pytest.mark.skipif`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_unknown_or_partial_terminal_record_remains_conservative`（L1239–L1246）：接收`terminal`。 控制顺序：L1241断言`result == { "error_code": "unknown", "errno": None, "syscall": "unknown", "component"…`。 调用`node_failure_facts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_latest_known_record_and_raw_budget_do_not_borrow_other_records`（L1249–L1266）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1258断言`node_failure_facts(NODE_SYSTEM_ERROR + denied) == { "error_code": "EACCES", "errno": …`；L1264断言`node_failure_facts( NODE_SYSTEM_ERROR.ljust(NATIVE_TAIL_LIMIT) + "PrivateFailure: out…`。 调用`node_failure_facts`、`NODE_SYSTEM_ERROR.ljust`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_diagnostics.py`；**本文件共有 2 段**。本段覆盖源文件 L900–L1266。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14288`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_diagnostics.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "68bd86100a8b1dca6e50fc46712070e87813394d8655a6f1440ea95cec1fb1d0"} -->
````python
# tests/test_capability_startup_diagnostics.py
@pytest.mark.parametrize(
    "renderer",
    [
        rich_trace,
        lambda exc: rich_trace(exc, panel=True),
        lambda exc: "".join(traceback.format_exception(exc)),
    ],
    ids=["rich", "rich-panel", "plain"],
)
@pytest.mark.parametrize("message", [(), ("private-sentinel",)])
@pytest.mark.parametrize("lowercase", [False, True])
def test_terminal_suffixless_unknown_suppresses_prior_known_exception(renderer, message, lowercase):
    class PrivateFailure(Exception):
        pass

    class privatefailure(Exception):
        pass

    terminal = (privatefailure if lowercase else PrivateFailure)(*message)
    terminal.__cause__ = TypeError("private-primary")
    result = startup_failure_diagnostic(renderer(terminal), 502, "none")
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("legacy_windows", [False, True])
@pytest.mark.parametrize("panel", [False, True])
@pytest.mark.parametrize("empty", [False, True])
@pytest.mark.parametrize("terminal_kind", ["known", "private", "lowercase"])
def test_real_rich_console_modes_preserve_terminal_chain(
    legacy_windows, panel, empty, terminal_kind
):
    class PrivateFailure(Exception):
        pass

    class privatefailure(Exception):
        pass

    exception = {"known": KeyError, "private": PrivateFailure, "lowercase": privatefailure}[
        terminal_kind
    ]
    terminal = exception() if empty else exception("private-sentinel")
    terminal.__cause__ = TypeError("private-primary")
    output = rich_trace(terminal, panel=panel, legacy_windows=legacy_windows)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    if panel:
        left, right = ("└", "┘") if legacy_windows else ("╰", "╯")
        assert left in output.splitlines()[-1] and right in output.splitlines()[-1]
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == ("KeyError" if terminal_kind == "known" else "unknown")
    assert result["failure_component"] == "unknown"
    assert result["output_read_limit_reached"] is False
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "alias",
    [
        "private.MissingGreenlet",
        "private.PydanticUserError",
        "sqlalchemy.exc.PrivateFailure",
        "pydantic.errors.PrivateFailure",
        "pydantic_core._pydantic_core.PrivateFailure",
    ],
)
def test_framework_prefix_never_authorizes_a_private_exception(alias):
    result = startup_failure_diagnostic(
        "TypeError: private-first\n" + alias + ": private-last", 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert "PrivateFailure" not in json.dumps(result)
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("prefix", ["", "\x1b[31m", "TypeError: private-primary\n"])
def test_cut_unknown_name_cannot_become_a_known_empty_exception(prefix):
    limit = len((prefix + "TypeError").encode())
    result = startup_failure_diagnostic(
        prefix + "TypeErrorPrivate", 502, "none", output_limit=limit
    )
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "unknown"


def test_complete_bare_exception_newline_remains_known_at_exact_cap():
    output = "TypeError\n"
    result = startup_failure_diagnostic(output, 502, "none", output_limit=len(output))
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "TypeError"


NODE_SYSTEM_ERROR = """SystemError [ERR_SYSTEM_ERROR]: private-sentinel
    at private-location:1:1 {
  code: 'ERR_SYSTEM_ERROR',
  info: {
    errno: 1,
    code: 'Unknown system error 1',
    message: 'private-sentinel',
    syscall: 'uv_interface_addresses'
  },
  errno: [Getter/Setter],
  syscall: [Getter/Setter]
}
"""


def test_node_interface_failure_requires_same_closed_info_block():
    assert node_failure_facts(NODE_SYSTEM_ERROR) == {
        "error_code": "ERR_SYSTEM_ERROR",
        "errno": 1,
        "syscall": "uv_interface_addresses",
        "component": "node-interface-enumeration",
    }
    colored_output = "\n".join(
        "\x1b[31m" + line + "\x1b[0m" for line in NODE_SYSTEM_ERROR.splitlines()
    )
    assert node_failure_facts(colored_output) == node_failure_facts(NODE_SYSTEM_ERROR)
    assert "private" not in json.dumps(node_failure_facts(NODE_SYSTEM_ERROR))


@pytest.mark.parametrize(
    "old,new",
    [
        ("SystemError [ERR_SYSTEM_ERROR]", "PrivateError [ERR_PRIVATE]"),
        ("    errno: 1,", "    errno: -1,"),
        ("    errno: 1,", "    errno: 1,\n    errno: 13,"),
        ("    syscall: 'uv_interface_addresses'", "    syscall: 'private-sentinel'"),
        ("  info: {", "  private: {"),
        ("  },", ""),
        ("  code: 'ERR_SYSTEM_ERROR',", "  code: 'ERR_PRIVATE',"),
    ],
)
def test_node_missing_conflicting_or_unrelated_properties_stay_unknown(old, new):
    result = node_failure_facts(NODE_SYSTEM_ERROR.replace(old, new))
    assert result["component"] == "unknown" and result["syscall"] == "unknown"
    assert "private" not in json.dumps(result)
    assert "ERR_PRIVATE" not in json.dumps(result)


def test_node_properties_cannot_cross_error_records_or_truncated_boundaries():
    first = NODE_SYSTEM_ERROR.replace("    errno: 1,\n", "")
    second = NODE_SYSTEM_ERROR.replace("    syscall: 'uv_interface_addresses'\n", "")
    for text in (
        first + second,
        NODE_SYSTEM_ERROR + "Error: private-terminal\n    at private:1:1 {\n}\n",
        "\x1b[0m" * NATIVE_TAIL_LIMIT + NODE_SYSTEM_ERROR,
        NODE_SYSTEM_ERROR[: NODE_SYSTEM_ERROR.index("  info:")]
        + "}\n"
        + NODE_SYSTEM_ERROR[NODE_SYSTEM_ERROR.index("  info:") :],
    ):
        result = node_failure_facts(text)
        assert result["component"] == "unknown"
        assert "private" not in json.dumps(result)


def node_error_fixture_script(code, errno, logged):
    # Trusted Node's own formatter with synthetic context; no candidate imports,
    # kernel-error claim, permission changes, or filesystem/network operations.
    if code == "ERR_SYSTEM_ERROR":
        construct = "const e=new codes.ERR_SYSTEM_ERROR({errno:1,code:'Unknown system error 1',message:'Unknown system error 1',syscall:'uv_interface_addresses'});"
    else:
        # UVException ignores ctx.code and looks up ctx.errno in HOST libuv.
        # Construct with that host number, then render the synthetic Linux
        # container errno. Windows uses -4092/-4058/-4066, not -13/-2/-24.
        # Node v22.23.2: lib/internal/errors.js:598 and deps/uv/include/uv/errno.h.
        construct = (
            "const ctx="
            + json.dumps(
                {
                    "errno": errno,
                    "code": code,
                    "message": "private-sentinel",
                    "syscall": "open",
                    "path": "/private-sentinel",
                }
            )
            + ";const host=[...require('node:util').getSystemErrorMap()]"
            ".find(([,entry])=>entry[0]===ctx.code);"
            "if(!host)throw Error('owned errno lookup failed');"
            "const e=new UVException({...ctx,errno:host[0]});e.errno=ctx.errno;"
        )
    return (
        "Error.stackTraceLimit=1;const {codes,UVException}=require('internal/errors');"
        + construct
        + ("console.error(e);" if logged else "throw e;")
    )


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned formatter fixture"
)
@pytest.mark.parametrize(
    "code,errno", [("ERR_SYSTEM_ERROR", 1), ("EACCES", -13), ("ENOENT", -2), ("EMFILE", -24)]
)
@pytest.mark.parametrize("logged", [False, True])
def test_actual_node_formatter_produces_only_verified_public_facts(code, errno, logged):
    script = node_error_fixture_script(code, errno, logged)
    process = subprocess.run(
        [shutil.which("node"), "--expose-internals", "-e", script],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        },
    )
    assert process.returncode == (0 if logged else 1)
    result = node_failure_facts(process.stderr)
    assert result["error_code"] == code and result["errno"] == errno
    assert result["syscall"] == ("uv_interface_addresses" if code == "ERR_SYSTEM_ERROR" else "open")
    assert result["component"] == (
        "node-interface-enumeration" if code == "ERR_SYSTEM_ERROR" else "unknown"
    )
    assert "private" not in json.dumps(result)


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned formatter fixture"
)
@pytest.mark.parametrize(
    "code,errno,windows_errno",
    [("EACCES", -13, -4092), ("ENOENT", -2, -4058), ("EMFILE", -24, -4066)],
)
@pytest.mark.parametrize("logged", [False, True])
def test_real_node_fixture_handles_windows_libuv_map(code, errno, windows_errno, logged):
    # Inject the verified Windows map only into this owned child process. The
    # real UVException constructor and Node formatter remain unchanged.
    windows = (
        "const uv=require('internal/test/binding').internalBinding('uv');"
        "const windowsMap=new Map([[-4092,['EACCES','permission denied']],"
        "[-4058,['ENOENT','no such file or directory']],"
        "[-4066,['EMFILE','too many open files']]]);"
        "uv.getErrorMap=()=>new Map(windowsMap);uv.errmap=new Map(windowsMap);"
        "const before=new (require('internal/errors').UVException)("
        + json.dumps({"errno": errno, "code": code, "syscall": "open"})
        + ");process.stdout.write(JSON.stringify({old_code:before.code,host_errno:"
        "[...require('node:util').getSystemErrorMap()].find(([,entry])=>entry[0]==="
        + json.dumps(code)
        + ")[0]}));"
    )
    process = subprocess.run(
        [
            shutil.which("node"),
            "--no-warnings",
            "--expose-internals",
            "-e",
            windows + node_error_fixture_script(code, errno, logged),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        },
    )
    assert process.returncode == (0 if logged else 1)
    assert json.loads(process.stdout) == {"old_code": "UNKNOWN", "host_errno": windows_errno}
    assert node_failure_facts(process.stderr) == {
        "error_code": code,
        "errno": errno,
        "syscall": "open",
        "component": "unknown",
    }


@pytest.mark.parametrize("value", [None, True, "", [], "x" * 129])
@pytest.mark.parametrize("field", ["session", "command_id"])
def test_invalid_command_identity_cannot_issue_a_status_query(value, field):
    identities = {"session": "owned-session", "command_id": "owned-command"}
    identities[field] = value
    process = SimpleNamespace(
        get_session_command=lambda *a: pytest.fail("Invalid identity queried")
    )
    assert startup_command_exit_facts(process, **identities, timeout=5) == {
        "command_exit_status": "unknown",
        "command_exit_code": None,
    }


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned formatter fixture"
)
@pytest.mark.parametrize("name", ["PrivateFailure", "privatefailure", "私有错误"])
@pytest.mark.parametrize("logged", [False, True])
def test_actual_node_suffixless_terminal_error_cannot_borrow_prior_component(name, logged):
    script = (
        "Error.stackTraceLimit=1;const {codes}=require('internal/errors');"
        "console.error(new codes.ERR_SYSTEM_ERROR({errno:1,code:'Unknown system error 1',"
        "message:'Unknown system error 1',syscall:'uv_interface_addresses'}));"
        "const terminal=new Error('private-sentinel');terminal.name="
        + json.dumps(name)
        + ";"
        + ("console.error(terminal);" if logged else "throw terminal;")
    )
    process = subprocess.run(
        [shutil.which("node"), "--expose-internals", "-e", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        },
    )
    assert process.returncode == (0 if logged else 1)
    assert "ERR_SYSTEM_ERROR" in process.stderr and name + ": private-sentinel" in process.stderr
    assert len(process.stderr.encode()) < NATIVE_TAIL_LIMIT
    result = node_failure_facts(process.stderr)
    assert result == {
        "error_code": "unknown",
        "errno": None,
        "syscall": "unknown",
        "component": "unknown",
    }
    assert name not in json.dumps(result, ensure_ascii=False)


@pytest.mark.parametrize(
    "terminal",
    [
        "PrivateFailure: private-sentinel\n",
        "PrivateFailure:",
        "PrivateFailure: " + "x" * NATIVE_TAIL_LIMIT,
        "Private" + "x" * 256 + ": private-sentinel\n",
        "private-terminal-text\n",
    ],
)
def test_node_unknown_or_partial_terminal_record_remains_conservative(terminal):
    result = node_failure_facts(NODE_SYSTEM_ERROR + terminal)
    assert result == {
        "error_code": "unknown",
        "errno": None,
        "syscall": "unknown",
        "component": "unknown",
    }


def test_node_latest_known_record_and_raw_budget_do_not_borrow_other_records():
    denied = """Error: EACCES: private-sentinel
    at private-location:1:1 {
  errno: -13,
  syscall: 'open',
  code: 'EACCES',
  path: '/private-sentinel'
}
"""
    assert node_failure_facts(NODE_SYSTEM_ERROR + denied) == {
        "error_code": "EACCES",
        "errno": -13,
        "syscall": "open",
        "component": "unknown",
    }
    assert node_failure_facts(
        NODE_SYSTEM_ERROR.ljust(NATIVE_TAIL_LIMIT) + "PrivateFailure: outside-budget"
    ) == node_failure_facts(NODE_SYSTEM_ERROR)
````
