# tests/test_capability_browser_preflight.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `setup_report`（L13–L19）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`monkeypatch.setenv`。 返回路径：L19的`tmp_path / "reports/capability-browser-preflight.json"`。
- `test_selected_probe_is_mandatory_even_if_bundled_browser_passes`（L23–L49）：接收`setup_report`、`monkeypatch`、`selected_passes`。 控制顺序：L37按`selected_passes`分支；L43断言`result["passed"] is selected_passes`；L44断言`result["product_acceptance"] is False`；L45断言`result["channel"] == "chrome"`；L46断言`[channel for channel, _ in calls] == ["", "chrome"]`；L47断言`preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "chrome"`。 调用`monkeypatch.setattr`、`preflight.main`、`pytest.raises`、`json.loads`、`setup_report.read_text`、`urlopen`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_selected_probe_is_mandatory_even_if_bundled_browser_passes.probe`（L28–L34）：接收`url`。 控制顺序：L30断言`response.status == 200`；L31断言`b'id="check"' in response.read()`。 调用`urlopen`、`response.read`、`calls.append`。 返回路径：L34的`{"passed": selected_passes if channel == "chrome" else True}`。
- `test_bundled_failure_cannot_hide_selected_success`（L52–L63）：接收`setup_report`、`monkeypatch`。 控制顺序：L61断言`result["passed"] is True`；L62断言`result["bundled_probe"]["passed"] is False`；L63断言`result["selected_probe"]["passed"] is True`。 调用`monkeypatch.setattr`、`preflight.main`、`json.loads`、`setup_report.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bundled_failure_cannot_hide_selected_success.probe`（L53–L56）：接收`url`。 控制顺序：L54按`preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == ""`分支。 返回路径：L55的`{"passed": False, "browser_diagnostic": {"error_code": "sandbox-unavailable"}}`；L56的`{"passed": True}`。
- `test_probe_preserves_safe_browser_failure_without_raw_infrastructure_errors`（L66–L85）：接收`monkeypatch`。 控制顺序：L73断言`preflight.probe("http://127.0.0.1:1") == { "passed": False, "browser_diagnostic": dia…`；L82断言`preflight.probe("http://127.0.0.1:1") == { "passed": False, "error_code": "preflight-…`。 调用`monkeypatch.setattr`、`preflight.probe`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_preserves_safe_browser_failure_without_raw_infrastructure_errors.fail`（L69–L70）：接收`*args`。 控制顺序：L70抛异常，停止当前正常路径。 调用`BrowserFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_preserves_safe_browser_failure_without_raw_infrastructure_errors.infrastructure_failure`（L78–L79）：接收`*args`。 控制顺序：L79抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chrome_version_output_is_bounded_and_allowlisted`（L89–L99）：接收`monkeypatch`、`version`。 控制顺序：L97断言`preflight.installed_chrome_version() == ( "141.0.7390.37" if version == "141.0.7390.3…`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`version.encode`、`preflight.installed_chrome_version`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_profile_failure_label_does_not_bypass_or_replace_strict_validation`（L103–L128）：接收`monkeypatch`、`valid_diagnostic`。 控制顺序：L126断言`"private-credential" not in str(failure.value)`；L127断言`calls == [(proof, {"aggregate": True, "source_digest": "current-source"})]`；L128断言`proof["passed"] is False`。 调用`monkeypatch.setattr`、`pytest.raises`、`profile.require_profile_evidence`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_profile_failure_label_does_not_bypass_or_replace_strict_validation.reject`（L118–L120）：接收`receipt`、`**bindings`。 控制顺序：L120抛异常，停止当前正常路径。 调用`calls.append`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_preflight.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4893`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_preflight.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "654f04d832b9869a7014d4a2fd43a47d74a6da9fa4c67bede3267254cfe2bf8c"} -->
````python
# tests/test_capability_browser_preflight.py
"""Preflight failure/cleanup contracts; unit fixtures are not browser evidence."""

import json
from urllib.request import urlopen

import pytest

from scripts import ci_capability_browser_preflight as preflight
from workbench.capability_verification import BrowserFailure


@pytest.fixture
def setup_report(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight, "ROOT", tmp_path)
    monkeypatch.setattr(preflight, "sha", lambda path: "a" * 64)
    monkeypatch.setattr(preflight, "installed_chrome_version", lambda: "141.0.7390.37")
    monkeypatch.setattr(preflight, "readonly_host_facts", lambda: {"apparmor_enabled": "Y"})
    monkeypatch.setenv("PRODUCT_VERIFY_BROWSER_CHANNEL", "chrome")
    return tmp_path / "reports/capability-browser-preflight.json"


@pytest.mark.parametrize("selected_passes", [True, False])
def test_selected_probe_is_mandatory_even_if_bundled_browser_passes(
    setup_report, monkeypatch, selected_passes
):
    calls = []

    def probe(url):
        with urlopen(url, timeout=2) as response:
            assert response.status == 200
            assert b'id="check"' in response.read()
        channel = preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"]
        calls.append((channel, url))
        return {"passed": selected_passes if channel == "chrome" else True}

    monkeypatch.setattr(preflight, "probe", probe)
    if selected_passes:
        preflight.main()
    else:
        with pytest.raises(SystemExit, match="preflight FAILED"):
            preflight.main()
    result = json.loads(setup_report.read_text())
    assert result["passed"] is selected_passes
    assert result["product_acceptance"] is False
    assert result["channel"] == "chrome"
    assert [channel for channel, _ in calls] == ["", "chrome"]
    assert preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "chrome"
    with pytest.raises(OSError):
        urlopen(calls[-1][1], timeout=2)


def test_bundled_failure_cannot_hide_selected_success(setup_report, monkeypatch):
    def probe(url):
        if preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "":
            return {"passed": False, "browser_diagnostic": {"error_code": "sandbox-unavailable"}}
        return {"passed": True}

    monkeypatch.setattr(preflight, "probe", probe)
    preflight.main()
    result = json.loads(setup_report.read_text())
    assert result["passed"] is True
    assert result["bundled_probe"]["passed"] is False
    assert result["selected_probe"]["passed"] is True


def test_probe_preserves_safe_browser_failure_without_raw_infrastructure_errors(monkeypatch):
    diagnostic = {"phase": "launch", "error_code": "sandbox-unavailable"}

    def fail(*args):
        raise BrowserFailure(diagnostic)

    monkeypatch.setattr(preflight, "run_browser", fail)
    assert preflight.probe("http://127.0.0.1:1") == {
        "passed": False,
        "browser_diagnostic": diagnostic,
    }

    def infrastructure_failure(*args):
        raise OSError("private-path-and-credential-do-not-print")

    monkeypatch.setattr(preflight, "run_browser", infrastructure_failure)
    assert preflight.probe("http://127.0.0.1:1") == {
        "passed": False,
        "error_code": "preflight-infrastructure",
    }


@pytest.mark.parametrize("version", ["141.0.7390.37\n", "private-token", "141.0.7390.37\nsecret"])
def test_chrome_version_output_is_bounded_and_allowlisted(monkeypatch, version):
    from types import SimpleNamespace

    monkeypatch.setattr(
        preflight.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=version.encode()),
    )
    assert preflight.installed_chrome_version() == (
        "141.0.7390.37" if version == "141.0.7390.37\n" else None
    )


@pytest.mark.parametrize("valid_diagnostic", [True, False])
def test_profile_failure_label_does_not_bypass_or_replace_strict_validation(
    monkeypatch, valid_diagnostic
):
    from scripts import ci_capability_profile as profile
    from workbench.capability_verification import CheckFailure

    calls = []
    proof = {
        "passed": False,
        "browser_diagnostic": {
            "phase": "launch" if valid_diagnostic else "private-credential",
            "error_code": "sandbox-unavailable",
        },
    }

    def reject(receipt, **bindings):
        calls.append((receipt, bindings))
        raise CheckFailure("strict-contract-rejected")

    monkeypatch.setattr(profile, "require_evidence", reject)
    message = "launch/sandbox-unavailable" if valid_diagnostic else "strict-contract-rejected"
    with pytest.raises(CheckFailure, match=message) as failure:
        profile.require_profile_evidence(proof, aggregate=True, source_digest="current-source")
    assert "private-credential" not in str(failure.value)
    assert calls == [(proof, {"aggregate": True, "source_digest": "current-source"})]
    assert proof["passed"] is False
````
