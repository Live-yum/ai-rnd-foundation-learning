# tests/test_capability_startup_paths.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `helpers`（L17–L27）：接收`loader`。 调用`ast.parse`、`ast.Module`、`isinstance`、`SimpleNamespace`、`vars`、`getattr`、`str`、`exec`、`compile`。 返回路径：L27的`scope`。
- `elf`（L30–L39）：接收`loader`。 调用`bytearray`、`struct.pack_into`、`len`。 返回路径：L39的`data`。
- `test_missing_regular_directory_and_dangling_link`（L42–L60）：接收`tmp_path`。 控制顺序：L46断言`inspect(str(path))["entry"] == "missing"`；L48断言`inspect(str(path))["target"] == "regular"`；L49断言`inspect(str(tmp_path))["target"] == "directory"`；L55断言`inspect(str(link))["entry"] == "symlink"`；L56断言`inspect(str(link))["target"] == "regular"`；L59断言`value["entry"] == "symlink" and value["target"] == "missing"`；L60断言`"private-sentinel" not in json.dumps(value)`。 调用`helpers`、`inspect`、`str`、`path.write_bytes`、`link.symlink_to`、`pytest.skip`、`path.unlink`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_dac_does_not_use_root_access`（L64–L73）：接收`tmp_path`。 控制顺序：L72断言`result["dac_read"] is False and result["dac_exec"] is False`；L73断言`file.read_bytes() == b"inert" if os.geteuid() == 0 else True`。 调用`base.mkdir`、`file.write_bytes`、`file.chmod`、`helpers(base / "loader")["inspect"]`、`helpers`、`str`、`os.geteuid`、`file.read_bytes`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_elf_header_reports_only_fixed_loader_state`（L77–L84）：接收`tmp_path`、`present`。 控制顺序：L79按`present`分支；L84断言`result == {"format": "elf", "loader": "present" if present else "missing"}`。 调用`loader.write_bytes`、`program.write_bytes`、`elf`、`helpers(loader)["executable_format"]`、`helpers`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_binary_and_shebang_never_expose_content`（L96–L101）：接收`tmp_path`、`data`、`kind`、`loader`。 控制顺序：L100断言`result == {"format": kind, "loader": loader}`；L101断言`"private" not in json.dumps(result)`。 调用`program.write_bytes`、`helpers(tmp_path / "loader")["executable_format"]`、`helpers`、`str`、`json.dumps`、`pytest.mark.parametrize`、`elf`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_elf_program_header_outside_read_budget_is_unknown`（L104–L112）：接收`tmp_path`。 控制顺序：L109断言`helpers(tmp_path / "loader")["executable_format"](str(program)) == { "format": "elf",…`。 调用`elf`、`bytearray`、`struct.pack_into`、`program.write_bytes`、`helpers(tmp_path / "loader")["executable_format"]`、`helpers`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fifo_is_never_read_and_descriptor_is_closed`（L116–L133）：接收`tmp_path`。 控制顺序：L130断言`scope["executable_format"](str(fifo)) == {"format": "unknown", "loader": "unknown"}`；L131断言`len(descriptors) == 1`。 调用`os.mkfifo`、`helpers`、`pytest.fail`、`scope["executable_format"]`、`str`、`len`、`pytest.raises`、`os.fstat`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fifo_is_never_read_and_descriptor_is_closed.open_fd`（L123–L126）：接收`*args`。 调用`opened`、`descriptors.append`。 返回路径：L126的`fd`。
- `receipt`（L136–L143）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L137的`{ "paths": { name: {"entry": "regular", "target": "regular", "dac_read": True, "dac_exec":…`。
- `test_controller_requests_only_fixed_program_and_bounds_output`（L146–L155）：接收`monkeypatch`。 控制顺序：L154断言`diagnostic.native_startup_paths(object(), 5) == {"status": "observed", **receipt()}`；L155断言`calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.PROBE], 5)]`。 调用`monkeypatch.setattr`、`diagnostic.native_startup_paths`、`object`、`receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_controller_requests_only_fixed_program_and_bounds_output.execute`（L149–L151）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`、`receipt`。 返回路径：L151的`SimpleNamespace(exit_code=0, result=json.dumps(receipt()))`。
- `test_malformed_receipt_is_unknown`（L171–L179）：接收`monkeypatch`、`mutate`。 控制顺序：L179断言`diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}`。 调用`copy.deepcopy`、`receipt`、`mutate`、`monkeypatch.setattr`、`SimpleNamespace`、`json.dumps`、`diagnostic.native_startup_paths`、`object`、`pytest.mark.parametrize`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_or_oversize_probe_never_serializes_output`（L185–L189）：接收`monkeypatch`、`code`、`output`。 控制顺序：L189断言`diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`diagnostic.native_startup_paths`、`object`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_output_format_classification_never_copies_content`（L213–L215）：接收`text`、`expected`。 控制顺序：L214断言`diagnostic.output_shapes(text) == expected`；L215断言`diagnostic.output_shapes("x" * 8000 + (text or "")) == []`。 调用`diagnostic.output_shapes`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_plan`（L218–L222）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`。 返回路径：L219的`SimpleNamespace( selection=SimpleNamespace(template="fastapiadmin", database="postgresql")…`。
- `smoke_checks`（L225–L226）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`dict.fromkeys`。 返回路径：L226的`dict.fromkeys(("version_matches", "executable_matches", "cwd_matches", "isolated"), True)`。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget`（L229–L269）：接收`monkeypatch`。 控制顺序：L268断言`result == {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}`；L269断言`"private-sentinel" not in json.dumps(result)`。 调用`monkeypatch.setattr`、`native_plan`、`diagnostic.product_argv`、`diagnostic.native_startup_smoke`、`object`、`smoke_checks`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget.execute`（L248–L258）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L249断言`timeout == 5`；L250断言`argv[:2] == ["/bin/sh", "-c"]`；L251断言`argv[2].startswith("cd /tmp/rnd-capability/product/backend && ")`；L253断言`inner[:2] == ["/bin/sh", "-c"]`；L255断言`launcher == ["exec", *expected]`；L256断言`"--native-shm" in launcher and "--reuid=rnd-module" in launcher`。 调用`argv[2].startswith`、`shlex.split`、`argv[2].split`、`inner[2].split`、`SimpleNamespace`。 返回路径：L258的`SimpleNamespace(exit_code=0)`。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget.read`（L260–L263）：接收`sandbox`、`path`、`timeout`、`limit`、`tail`。 控制顺序：L261断言`timeout == 1 and limit == 512 and tail is True`；L262断言`path.startswith("/tmp/rnd-module-control/private/")`。 调用`path.startswith`、`json.dumps`、`smoke_checks`。 返回路径：L263的`json.dumps(smoke_checks())`。
- `test_smoke_failure_and_corrupt_output_are_finite`（L284–L291）：接收`monkeypatch`、`code`、`output`、`expected`。 控制顺序：L290断言`result["exit_status"] == expected and result["checks"] is None`；L291断言`"private-sentinel" not in json.dumps(result)`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`diagnostic.native_startup_smoke`、`object`、`native_plan`、`json.dumps`、`pytest.mark.parametrize`、`smoke_checks`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_timeout_keeps_unknown_and_does_not_start_another_read`（L294–L308）：接收`monkeypatch`。 控制顺序：L306断言`diagnostic.native_startup_smoke( object(), native_plan(), {}, {"native_semaphore_stor…`。 调用`monkeypatch.setattr`、`pytest.fail`、`diagnostic.native_startup_smoke`、`object`、`native_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_timeout_keeps_unknown_and_does_not_start_another_read.execute`（L298–L300）：接收`*args`。 调用`SimpleNamespace`。 返回路径：L300的`SimpleNamespace(exit_code=0)`。
- `test_all_native_diagnostic_reads_fit_existing_byte_budget`（L311–L316）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L312断言`diagnostic.NATIVE_TAIL_LIMIT + diagnostic.PATH_OUTPUT_LIMIT + diagnostic.SMOKE_OUTPUT…`；L316断言`len(json.dumps(receipt()).encode()) < diagnostic.PATH_OUTPUT_LIMIT`。 调用`len`、`json.dumps(receipt()).encode`、`json.dumps`、`receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline`（L321–L374）：接收`monkeypatch`、`probe`、`fail`。 控制顺序：L365断言`len(requests) == (1 if probe == "metadata" or fail else 2)`；L366断言`len(transports) == len(requests)`；L367断言`_DEADLINE.get() == 999.0`；L368按`probe == "metadata"`分支；L369断言`result["status"] == ("unknown" if fail else "observed")`；L371断言`result["checks"] == (None if fail else smoke_checks())`；L372断言`"private-sentinel" not in json.dumps(result)`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`transports.append`、`harden_toolbox_transport`、`_DEADLINE.set`、`httpx.Client`、`Process`、`diagnostic.native_startup_paths`、`diagnostic.native_startup_smoke`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline.execute_command`（L338–L350）：接收`request`、`**kwargs`。 控制顺序：L340断言`type(request.timeout) is int and 1 <= request.timeout <= 5`；L341断言`_DEADLINE.get() == 15`；L346断言`0 < transports[-1] <= 15 - clock[0]`；L347按`fail`分支；L348抛异常，停止当前正常路径。 调用`requests.append`、`type`、`_DEADLINE.get`、`rest.request`、`RuntimeError`、`receipt`、`smoke_checks`、`SimpleNamespace`、`json.dumps`。 返回路径：L350的`SimpleNamespace(result=json.dumps(value), exit_code=0, additional_properties={})`。
- `test_actual_start_keeps_health_failure_and_closes_http`（L379–L480）：接收`monkeypatch`、`failure`、`native`。 控制顺序：L468断言`events == (["tail", "paths", "smoke", "closed"] if native else ["tail", "closed"])`；L469断言`state["command_exit_status"] == "nonzero"`；L470断言`state["command_exit_code"] == 2`；L471断言`state["output_raw_bytes"] == output_limit`；L472断言`state["output_read_limit_reached"] is True`；L473按`native`分支；L474断言`state["launch_paths"]["status"] == ("unknown" if failure == "paths" else "observed")`；L475断言`state["interpreter_probe"]["exit_status"] == ( "unknown" if failure == "smoke" else "…`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`next`、`ast.walk`、`ast.parse`、`source.read_text`、`isinstance`、`complete_native_plan`、`iter`、`SimpleNamespace`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_start_keeps_health_failure_and_closes_http.paths`（L401–L405）：接收`*args`。 控制顺序：L403按`failure == "paths"`分支；L404抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`、`receipt`。 返回路径：L405的`{"status": "observed", **receipt()}`。
- `test_actual_start_keeps_health_failure_and_closes_http.smoke`（L407–L411）：接收`*args`。 控制顺序：L409按`failure == "smoke"`分支；L410抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`、`smoke_checks`。 返回路径：L411的`{"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}`。
- `test_actual_start_keeps_health_failure_and_closes_http.read`（L419–L422）：接收`limit`、`tail`、`*args`。 控制顺序：L420断言`limit == output_limit and tail is True`。 调用`events.append`。 返回路径：L422的`output`。

</details>

**创建路径：** `tests/test_capability_startup_paths.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L480。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18793`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_paths.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b981f638afcf6426c71d1006048874bfb8f0fa3d15fb7713f34027fa2d4bc292"} -->
````python
# tests/test_capability_startup_paths.py
"""Finite metadata from real owned launch fixtures, without candidate execution."""

import ast
import copy
import json
import os
import shlex
import stat
import struct
from types import SimpleNamespace

import pytest

from workbench import capability_startup_paths as diagnostic


def helpers(loader):
    tree = ast.parse(diagnostic.PROBE)
    functions = ast.Module([node for node in tree.body if isinstance(node, ast.FunctionDef)], [])
    # Pure regular-file ELF parsing remains covered on Windows. Only this test
    # adapter supplies zero for an absent nonblocking flag; real FIFO handling
    # is separately POSIX-only and the production Linux probe is unchanged.
    probe_os = SimpleNamespace(**vars(os))
    probe_os.O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
    scope = {"os": probe_os, "stat": stat, "struct": struct, "paths": {"elf_loader": str(loader)}}
    exec(compile(functions, "trusted-probe-functions", "exec"), scope)
    return scope


def elf(loader=b"/lib64/ld-linux-x86-64.so.2\0"):
    data = bytearray(256)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", data, 32, 64)
    struct.pack_into("<HH", data, 54, 56, 1)
    struct.pack_into("<I", data, 64, 3)
    struct.pack_into("<Q", data, 72, 128)
    struct.pack_into("<Q", data, 96, len(loader))
    data[128 : 128 + len(loader)] = loader
    return data


def test_missing_regular_directory_and_dangling_link(tmp_path):
    scope = helpers(tmp_path / "loader")
    inspect = scope["inspect"]
    path = tmp_path / "private-sentinel"
    assert inspect(str(path))["entry"] == "missing"
    path.write_bytes(b"inert")
    assert inspect(str(path))["target"] == "regular"
    assert inspect(str(tmp_path))["target"] == "directory"
    link = tmp_path / "link"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("Creating symlinks requires platform support")
    assert inspect(str(link))["entry"] == "symlink"
    assert inspect(str(link))["target"] == "regular"
    path.unlink()
    value = inspect(str(link))
    assert value["entry"] == "symlink" and value["target"] == "missing"
    assert "private-sentinel" not in json.dumps(value)


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits and directory traversal")
def test_app_dac_does_not_use_root_access(tmp_path):
    # All existing ancestors have to permit UID 20000 traversal too.
    base = tmp_path / "directory"
    base.mkdir(mode=0o755)
    file = base / "program"
    file.write_bytes(b"inert")
    file.chmod(0o000)
    result = helpers(base / "loader")["inspect"](str(file))
    assert result["dac_read"] is False and result["dac_exec"] is False
    assert file.read_bytes() == b"inert" if os.geteuid() == 0 else True


@pytest.mark.parametrize("present", [True, False])
def test_real_elf_header_reports_only_fixed_loader_state(tmp_path, present):
    loader = tmp_path / "loader"
    if present:
        loader.write_bytes(b"inert")
    program = tmp_path / "program"
    program.write_bytes(elf())
    result = helpers(loader)["executable_format"](str(program))
    assert result == {"format": "elf", "loader": "present" if present else "missing"}


@pytest.mark.parametrize(
    "data,kind,loader",
    [
        (b"#!/private/secret\n", "script", "unknown"),
        (b"private-sentinel", "other", "unknown"),
        (elf(b"/private/secret\0"), "elf", "unexpected"),
        (b"\x7fELF", "elf", "unknown"),
    ],
)
def test_unknown_binary_and_shebang_never_expose_content(tmp_path, data, kind, loader):
    program = tmp_path / "program"
    program.write_bytes(data)
    result = helpers(tmp_path / "loader")["executable_format"](str(program))
    assert result == {"format": kind, "loader": loader}
    assert "private" not in json.dumps(result)


def test_elf_program_header_outside_read_budget_is_unknown(tmp_path):
    program = tmp_path / "program"
    data = elf() + bytearray(70000)
    struct.pack_into("<Q", data, 72, 66000)
    program.write_bytes(data)
    assert helpers(tmp_path / "loader")["executable_format"](str(program)) == {
        "format": "elf",
        "loader": "unknown",
    }


@pytest.mark.skipif(os.name != "posix", reason="Actual FIFO requires POSIX nonblocking open")
def test_fifo_is_never_read_and_descriptor_is_closed(tmp_path):
    fifo = tmp_path / "owned-fifo"
    os.mkfifo(fifo)
    scope = helpers(tmp_path / "loader")
    descriptors = []
    opened = scope["os"].open

    def open_fd(*args):
        fd = opened(*args)
        descriptors.append(fd)
        return fd

    scope["os"].open = open_fd
    scope["os"].read = lambda *a: pytest.fail("Non-regular contents must not be read")
    assert scope["executable_format"](str(fifo)) == {"format": "unknown", "loader": "unknown"}
    assert len(descriptors) == 1
    with pytest.raises(OSError):
        os.fstat(descriptors[0])


def receipt():
    return {
        "paths": {
            name: {"entry": "regular", "target": "regular", "dac_read": True, "dac_exec": False}
            for name in diagnostic.PATH_ROLES
        },
        "native_binary": {"format": "elf", "loader": "present"},
    }


def test_controller_requests_only_fixed_program_and_bounds_output(monkeypatch):
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append((argv, timeout))
        return SimpleNamespace(exit_code=0, result=json.dumps(receipt()))

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "observed", **receipt()}
    assert calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.PROBE], 5)]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(secret="private-sentinel"),
        lambda d: d["paths"].pop("native_python"),
        lambda d: d["paths"].update(secret=d["paths"]["env"]),
        lambda d: d["paths"]["env"].update(entry="private-sentinel"),
        lambda d: d["paths"]["env"].update(dac_read=1),
        lambda d: d["paths"]["env"].update(dac_exec="true"),
        lambda d: d["native_binary"].update(loader="private-sentinel"),
        lambda d: d.update(native_binary=[]),
    ],
)
def test_malformed_receipt_is_unknown(monkeypatch, mutate):
    value = copy.deepcopy(receipt())
    mutate(value)
    monkeypatch.setattr(
        diagnostic,
        "control_exec",
        lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(value)),
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "code,output", [(False, "{}"), (1, "private-sentinel"), (0, "x" * 2049), (0, "{"), (0, None)]
)
def test_failed_or_oversize_probe_never_serializes_output(monkeypatch, code, output):
    monkeypatch.setattr(
        diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code, result=output)
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("/usr/bin/env: '/private/secret': No such file or directory", ["env-launcher"]),
        ("/bin/sh: 1: cd: can't cd to /private/secret", ["shell-launcher"]),
        (
            "/private/secret: error while loading shared libraries: private.so: cannot open shared object file: No such file or directory",
            ["elf-loader", "shared-library-open"],
        ),
        (
            "2026-10-05 08:00:00.001 | ERROR    | app.core.discover:_build:44 - private-sentinel",
            ["vendor-loguru"],
        ),
        (
            "\x1b[31mFileNotFoundError: private-sentinel\x1b[0m",
            ["file-not-found-type", "ansi-control"],
        ),
        ("private-sentinel", []),
        (None, []),
    ],
)
def test_output_format_classification_never_copies_content(text, expected):
    assert diagnostic.output_shapes(text) == expected
    assert diagnostic.output_shapes("x" * 8000 + (text or "")) == []


def native_plan():
    return SimpleNamespace(
        selection=SimpleNamespace(template="fastapiadmin", database="postgresql"),
        runtime=SimpleNamespace(port=8123),
    )


def smoke_checks():
    return dict.fromkeys(("version_matches", "executable_matches", "cwd_matches", "isolated"), True)


def test_smoke_uses_original_guard_and_env_with_shared_five_second_budget(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    plan = native_plan()
    database = {"DATABASE_PASSWORD": "private-sentinel"}
    identity = {"native_semaphore_storage": True}
    expected = diagnostic.product_argv(
        plan,
        [
            "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python",
            "-I",
            "-S",
            "-c",
            diagnostic.SMOKE,
        ],
        database,
        **identity,
    )

    def execute(sandbox, argv, timeout):
        assert timeout == 5
        assert argv[:2] == ["/bin/sh", "-c"]
        assert argv[2].startswith("cd /tmp/rnd-capability/product/backend && ")
        inner = shlex.split(argv[2].split(" && ", 1)[1])
        assert inner[:2] == ["/bin/sh", "-c"]
        launcher = shlex.split(inner[2].split(" </dev/null ", 1)[0])
        assert launcher == ["exec", *expected]
        assert "--native-shm" in launcher and "--reuid=rnd-module" in launcher
        clock[0] = 4
        return SimpleNamespace(exit_code=0)

    def read(sandbox, path, timeout, limit, tail):
        assert timeout == 1 and limit == 512 and tail is True
        assert path.startswith("/tmp/rnd-module-control/private/")
        return json.dumps(smoke_checks())

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(diagnostic, "read_command_output", read)
    result = diagnostic.native_startup_smoke(object(), plan, database, identity, 99)
    assert result == {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "code,output,expected",
    [
        (127, "/usr/bin/env: private-sentinel: No such file or directory", "nonzero"),
        (0, '{"version_matches":true,"version_matches":false}', "zero"),
        (False, "private-sentinel", "unknown"),
        (0, "private-sentinel", "zero"),
        (0, "x" * 513, "zero"),
        (0, json.dumps({**smoke_checks(), "isolated": 1}), "zero"),
        (0, json.dumps({**smoke_checks(), "secret": "private-sentinel"}), "zero"),
    ],
)
def test_smoke_failure_and_corrupt_output_are_finite(monkeypatch, code, output, expected):
    monkeypatch.setattr(diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code))
    monkeypatch.setattr(diagnostic, "read_command_output", lambda *a, **k: output)
    result = diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    )
    assert result["exit_status"] == expected and result["checks"] is None
    assert "private-sentinel" not in json.dumps(result)


def test_smoke_timeout_keeps_unknown_and_does_not_start_another_read(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])

    def execute(*args):
        clock[0] = 5.1
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(
        diagnostic, "read_command_output", lambda *a, **k: pytest.fail("Deadline exceeded")
    )
    assert diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    ) == {"exit_status": "zero", "output_shapes": [], "checks": None}


def test_all_native_diagnostic_reads_fit_existing_byte_budget():
    assert (
        diagnostic.NATIVE_TAIL_LIMIT + diagnostic.PATH_OUTPUT_LIMIT + diagnostic.SMOKE_OUTPUT_LIMIT
        == 8000
    )
    assert len(json.dumps(receipt()).encode()) < diagnostic.PATH_OUTPUT_LIMIT


@pytest.mark.parametrize("probe", ["metadata", "smoke"])
@pytest.mark.parametrize("fail", [False, True])
def test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline(
    monkeypatch, probe, fail
):
    import httpx
    from daytona._sync.process import Process

    from workbench.daytona_sessions import _DEADLINE, harden_toolbox_transport

    clock = [10.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    requests, transports = [], []
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda method, url, **kwargs: transports.append(kwargs["_request_timeout"]),
    )
    harden_toolbox_transport(SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest)))

    def execute_command(*, request, **kwargs):
        requests.append(request)
        assert type(request.timeout) is int and 1 <= request.timeout <= 5
        assert _DEADLINE.get() == 15
        clock[0] += 1.25
        # Exercise the actual SDK-selected larger HTTP budget through the real
        # hardened transport. The absolute deadline must win over that budget.
        rest.request("POST", "https://owned.invalid", **kwargs)
        assert 0 < transports[-1] <= 15 - clock[0]
        if fail:
            raise RuntimeError("private-sentinel")
        value = receipt() if probe == "metadata" else smoke_checks()
        return SimpleNamespace(result=json.dumps(value), exit_code=0, additional_properties={})

    outer = _DEADLINE.set(999.0)
    try:
        with httpx.Client(trust_env=False) as client:
            sandbox = SimpleNamespace(
                process=Process("python", SimpleNamespace(execute_command=execute_command), client)
            )
            result = (
                diagnostic.native_startup_paths(sandbox, 5)
                if probe == "metadata"
                else diagnostic.native_startup_smoke(
                    sandbox, native_plan(), {}, {"native_semaphore_storage": True}, 5
                )
            )
        assert len(requests) == (1 if probe == "metadata" or fail else 2)
        assert len(transports) == len(requests)
        assert _DEADLINE.get() == 999.0
        if probe == "metadata":
            assert result["status"] == ("unknown" if fail else "observed")
        else:
            assert result["checks"] == (None if fail else smoke_checks())
        assert "private-sentinel" not in json.dumps(result)
    finally:
        _DEADLINE.reset(outer)


@pytest.mark.parametrize("failure", [None, "paths", "smoke"])
@pytest.mark.parametrize("native", [False, True])
def test_actual_start_keeps_health_failure_and_closes_http(monkeypatch, failure, native):
    import uuid
    from pathlib import Path

    from daytona import SessionExecuteRequest
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_dependencies import readonly_start_command
    from workbench.capability_sandbox import startup_failure_diagnostic
    from workbench.capability_verification import CheckFailure

    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    start = next(
        n
        for n in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
        if isinstance(n, ast.FunctionDef) and n.name == "start"
    )
    events = []
    plan = complete_native_plan()
    clock = iter((0, plan.runtime.startup_seconds + 1))
    client = SimpleNamespace(close=lambda: events.append("closed"))

    def paths(*args):
        events.append("paths")
        if failure == "paths":
            raise RuntimeError("private-sentinel")
        return {"status": "observed", **receipt()}

    def smoke(*args):
        events.append("smoke")
        if failure == "smoke":
            raise RuntimeError("private-sentinel")
        return {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}

    monkeypatch.setattr(diagnostic, "native_startup_paths", paths)
    monkeypatch.setattr(diagnostic, "native_startup_smoke", smoke)

    output_limit = diagnostic.NATIVE_TAIL_LIMIT if native else 8000
    output = "/usr/bin/env: private-sentinel: No such file or directory".ljust(output_limit)

    def read(*args, limit, tail):
        assert limit == output_limit and tail is True
        events.append("tail")
        return output

    state = {}
    process = SimpleNamespace(
        create_session=lambda *a: None,
        execute_session_command=lambda *a, **k: SimpleNamespace(cmd_id="owned"),
    )
    scope = {
        "readonly_start_command": readonly_start_command,
        "require_preinstalled_evidence": lambda *a, **k: None,
        "verify_readonly_dependencies": lambda *a, **k: {},
        "dependency_profile": {},
        "before": {},
        "receipt": {"source_digest": "bound"},
        "plan": plan,
        "settings": SimpleNamespace(tool_timeout=20),
        "sandbox": SimpleNamespace(
            id="owned",
            process=process,
            get_preview_link=lambda *a: SimpleNamespace(url="owned", token="private-sentinel"),
        ),
        "uuid": uuid,
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "product_argv": diagnostic.product_argv,
        "redirected_command": diagnostic.redirected_command,
        "SessionExecuteRequest": SessionExecuteRequest,
        "REMOTE": "/tmp/rnd-capability",
        "shlex": shlex,
        "preview_url": lambda *a: "http://owned.invalid",
        "httpx": SimpleNamespace(Client=lambda **k: client),
        "time": SimpleNamespace(monotonic=lambda: next(clock)),
        "read_command_output": read,
        "control_exec": lambda *a: SimpleNamespace(exit_code=0, result="1"),
        "startup_failure_diagnostic": startup_failure_diagnostic,
        "startup_command_exit_facts": lambda *a: {
            "command_exit_status": "nonzero",
            "command_exit_code": 2,
        },
        "native": native,
        "CheckFailure": CheckFailure,
    }
    exec(compile(ast.Module([start], []), "actual-start-function", "exec"), scope)
    with pytest.raises(CheckFailure, match="健康检查"):
        scope["start"]()
    state = scope["receipt"]["startup_diagnostic"]
    assert events == (["tail", "paths", "smoke", "closed"] if native else ["tail", "closed"])
    assert state["command_exit_status"] == "nonzero"
    assert state["command_exit_code"] == 2
    assert state["output_raw_bytes"] == output_limit
    assert state["output_read_limit_reached"] is True
    if native:
        assert state["launch_paths"]["status"] == ("unknown" if failure == "paths" else "observed")
        assert state["interpreter_probe"]["exit_status"] == (
            "unknown" if failure == "smoke" else "zero"
        )
    else:
        assert "launch_paths" not in state and "interpreter_probe" not in state
    assert "private-sentinel" not in json.dumps(state)
````
