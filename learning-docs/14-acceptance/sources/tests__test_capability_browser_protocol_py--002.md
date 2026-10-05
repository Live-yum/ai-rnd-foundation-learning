# tests/test_capability_browser_protocol.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_capability_browser_protocol_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_security_facts_are_bounded_readonly_and_finite`（L892–L958）：接收`mode`。 控制顺序：L894按`not node`分支；L939断言`run.returncode == 0`；L943断言`len(data["reads"]) == 5`；L944断言`len(data["closed"]) == (0 if mode == "unavailable" else 5)`；L955按`mode != "valid"`分支；L958断言`facts == expected`。 调用`shutil.which`、`pytest.fail`、`SCRIPT.read_text`、`source.index`、`subprocess.run`、`json.dumps`、`assert_redacted`、`json.loads`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `launch_diagnostic`（L961–L972）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`diagnostic`、`dict.fromkeys`。 返回路径：L962的`diagnostic( phase="launch", error_code="sandbox-unavailable", error_type="Error", sandbox_…`。
- `test_launch_detail_rejects_missing_extra_unbounded_or_inconsistent_fields`（L994–L1002）：接收`mutation`。 控制顺序：L1001断言`result is None`；L1002断言`error == "invalid-diagnostic"`。 调用`launch_diagnostic`、`mutation`、`failed_report`、`verifier.browser_report`、`json.dumps(value).encode`、`json.dumps`、`hashlib.sha256(SCRIPT.read_bytes()).hexdigest`、`hashlib.sha256`、`SCRIPT.read_bytes`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_launch_detail_unknown_kernel_facts_never_make_failure_pass`（L1005–L1011）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1010断言`error is None`；L1011断言`result["passed"] is False`。 调用`failed_report`、`launch_diagnostic`、`verifier.browser_report`、`json.dumps(value).encode`、`json.dumps`、`hashlib.sha256(SCRIPT.read_bytes()).hexdigest`、`hashlib.sha256`、`SCRIPT.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_protocol.py`；**本文件共有 2 段**。本段覆盖源文件 L890–L1011。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4723`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_protocol.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "7165cd70b446cca9d6c54e6b39458ac1be95eb0f6b510abfb61a5243e55e0cde"} -->
````python
# tests/test_capability_browser_protocol.py
@pytest.mark.node_tools
@pytest.mark.parametrize("mode", ["valid", "unavailable", "oversized", "malformed"])
def test_security_facts_are_bounded_readonly_and_finite(mode):
    node = shutil.which("node")
    if not node:
        pytest.fail("Node is required to validate security diagnostics")
    source = SCRIPT.read_text()
    helper = source[
        source.index("function browserSecurityFacts()") : source.index("function rememberFailure")
    ]
    harness = r"""
const vm = require('node:vm')
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'))
const reads = [], closed = []
const status = 'NoNewPrivs:\t1\nSeccomp:\t2\nCapEff:\t0000000000000000\n'
const contents = {
  '/proc/self/status': status,
  '/proc/self/attr/current': 'docker-default (enforce)',
  '/sys/module/apparmor/parameters/enabled': 'Y',
  '/proc/sys/kernel/apparmor_restrict_unprivileged_userns': '1',
  '/proc/sys/kernel/unprivileged_userns_clone': '0',
}
const fs = {
  openSync: (path, flags) => {
    if (!(path in contents) || flags !== 'r') throw Error('unexpected read')
    reads.push(path)
    if (input.mode === 'unavailable') throw Error(input.secret)
    return path
  },
  readSync: (fd, buffer, offset, length, position) => {
    if (length !== 8193 || buffer.length !== 8193 || offset !== 0 || position !== 0) throw Error('unbounded read')
    const text = input.mode === 'oversized' ? 'x'.repeat(8193)
      : input.mode === 'malformed' ? input.secret : contents[fd]
    return buffer.write(text, 'ascii')
  },
  closeSync: fd => closed.push(fd),
}
const result = vm.runInNewContext(input.helper + '\nbrowserSecurityFacts()', {
  fs, Buffer, process: {getuid: () => 1000},
})
process.stdout.write(JSON.stringify({result, reads, closed}))
"""
    run = subprocess.run(
        [node, "-e", harness],
        input=json.dumps({"mode": mode, "helper": helper, "secret": SECRET_ERROR}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert run.returncode == 0, run.stderr
    assert_redacted(run.stdout)
    data = json.loads(run.stdout)
    facts = data["result"]
    assert len(data["reads"]) == 5
    assert len(data["closed"]) == (0 if mode == "unavailable" else 5)
    expected = {
        "uid_zero": False,
        "no_new_privileges": True,
        "seccomp_mode": 2,
        "effective_capabilities": False,
        "apparmor_profile": "docker-default",
        "apparmor_enabled": True,
        "apparmor_userns_restricted": True,
        "unprivileged_userns_enabled": False,
    }
    if mode != "valid":
        expected = {key: None for key in expected}
        expected.update(uid_zero=False, apparmor_profile="unknown")
    assert facts == expected


def launch_diagnostic():
    return diagnostic(
        phase="launch",
        error_code="sandbox-unavailable",
        error_type="Error",
        sandbox_reason="namespace-entry-failed",
        security_facts={
            **dict.fromkeys(verifier.BROWSER_SECURITY_FLAGS),
            "seccomp_mode": None,
            "apparmor_profile": "unknown",
        },
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(sandbox_reason=SECRET_ERROR),
        lambda d: d.update(sandbox_reason=[]),
        lambda d: d.update(sandbox_reason=None),
        lambda d: d.update(security_facts=[]),
        lambda d: d["security_facts"].update(uid_zero=1),
        lambda d: d["security_facts"].update(seccomp_mode=True),
        lambda d: d["security_facts"].update(seccomp_mode=3),
        lambda d: d["security_facts"].update(apparmor_profile=SECRET_ERROR),
        lambda d: d["security_facts"].update(apparmor_profile=[]),
        lambda d: d["security_facts"].update(raw=SECRET_ERROR),
        lambda d: d["security_facts"].pop("no_new_privileges"),
        lambda d: d.pop("sandbox_reason"),
        lambda d: d.update(error_code="operation-failed"),
        lambda d: d.update(phase="navigation"),
    ],
)
def test_launch_detail_rejects_missing_extra_unbounded_or_inconsistent_fields(mutation):
    detail = launch_diagnostic()
    mutation(detail)
    value = failed_report({"request_id": REQUEST_ID}, **detail)
    result, error = verifier.browser_report(
        json.dumps(value).encode(), REQUEST_ID, hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    )
    assert result is None
    assert error == "invalid-diagnostic"


def test_launch_detail_unknown_kernel_facts_never_make_failure_pass():
    value = failed_report({"request_id": REQUEST_ID}, **launch_diagnostic())
    result, error = verifier.browser_report(
        json.dumps(value).encode(), REQUEST_ID, hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    )
    assert error is None
    assert result["passed"] is False
````
