# tests/test_business_browser_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_browser_failure_retains_only_allowlisted_operation_and_static_callsites`（L15–L44）：接收`name`、`operation`、`separator`。 控制顺序：L36断言`code == ("TimeoutError" if name == "TimeoutError" else "BusinessBrowserFailure")`；L38断言`report == { "source": "verify-business-browser.cjs", "operation": operation if operat…`；L43断言`len(result) < 400`；L44断言`not any(secret in result for secret in ("private-canary", "password", "token", "http:…`。 调用`subprocess.run( [shutil.which("node"), "-e", script, name, operat…`、`subprocess.run`、`shutil.which`、`result.split`、`json.loads`、`len`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_failure_codes_remain_specific_without_fake_callsites`（L47–L64）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L63断言`code == "business-browser-relation-list-label"`；L64断言`json.loads(encoded)["callsites"] == []`。 调用`subprocess.run( [ shutil.which("node"), "-e", "const {browserFail…`、`subprocess.run`、`shutil.which`、`result.split`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_browser_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L64。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2451`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_browser_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d09b7b758ad1d4c006519504f397fd589ccb60f4a8c375a154868321d0e432de"} -->
````python
# tests/test_business_browser_diagnostics.py
"""Bounded failure callsites without exposing real browser values or credentials."""

import json
import shutil
import subprocess

import pytest

from workbench.settings import ROOT


@pytest.mark.parametrize("separator", ["/", "\\"])
@pytest.mark.parametrize("name", ["TimeoutError", "Error with private-canary"])
@pytest.mark.parametrize("operation", ["locator.click", "page.goto", "unknown.private-canary"])
def test_browser_failure_retains_only_allowlisted_operation_and_static_callsites(
    name, operation, separator
):
    script = r"""
const {browserFailure}=require('./templates/product/verify-business-browser.cjs');
const [name,operation,separator]=process.argv.slice(1);
const message=operation+': Timeout; private-canary password token DOM http://private.invalid/';
const frame='    at caller ('+['private-canary','account','verify-business-browser.cjs:42:7)'].join(separator);
const result=browserFailure({name,message,stack:message+'\n'+Array(20).fill(frame).join('\n')});
console.log(result);
"""
    result = subprocess.run(
        [shutil.which("node"), "-e", script, name, operation, separator],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=20,
    ).stdout.strip()
    code, encoded = result.split(" ", 1)
    assert code == ("TimeoutError" if name == "TimeoutError" else "BusinessBrowserFailure")
    report = json.loads(encoded)
    assert report == {
        "source": "verify-business-browser.cjs",
        "operation": operation if operation != "unknown.private-canary" else None,
        "callsites": [{"line": 42, "column": 7}] * 5,
    }
    assert len(result) < 400
    assert not any(secret in result for secret in ("private-canary", "password", "token", "http:"))


def test_business_failure_codes_remain_specific_without_fake_callsites():
    result = subprocess.run(
        [
            shutil.which("node"),
            "-e",
            "const {browserFailure}=require('./templates/product/verify-business-browser.cjs');"
            "console.log(browserFailure({message:'business-browser-relation-list-label'}));",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=20,
    ).stdout.strip()
    code, encoded = result.split(" ", 1)
    assert code == "business-browser-relation-list-label"
    assert json.loads(encoded)["callsites"] == []
````
