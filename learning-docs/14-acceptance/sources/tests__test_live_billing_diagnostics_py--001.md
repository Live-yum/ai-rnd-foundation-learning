# tests/test_live_billing_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.domain`、`workbench.llm`、`workbench.model_diagnostics`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `acceptance_main`（L21–L63）：接收`tmp_path`、`monkeypatch`。 源码说明：Exercise the real CLI authority/billing path without starting a model suite.。 控制顺序：L39遍历`environment.items()`。 调用`event.write_text`、`str`、`environment.items`、`monkeypatch.setenv`、`monkeypatch.setattr`、`SimpleNamespace`、`object`。 返回路径：L63的`invoke`。
- `acceptance_main.offline_suite`（L49–L51）：接收`settings`、`directory`、`binding`、`**kwargs`。 调用`calls.append`。 返回路径：L51的`{"passed": False, "real_model": False, "run_identity": binding}`。
- `acceptance_main.invoke`（L55–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L58断言`caught.value.code == 1`；L60断言`report["passed"] is False and report["real_model"] is False`。 调用`pytest.raises`、`acceptance.main`、`json.loads`、`(acceptance.REPORTS / "summary.json").read_text`。 返回路径：L61的`calls, report`。
- `test_declared_free_billing_reaches_suite_independently_of_ca`（L67–L82）：接收`acceptance_main`、`monkeypatch`、`ca_mode`。 控制顺序：L72断言`len(calls) == 1 and "controller_failure" not in report`；L73断言`calls[0] == { "ca_mode": ca_mode, "billing": { "mode": "declared_free", "attestation"…`。 调用`monkeypatch.setenv`、`acceptance_main`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_declared_free_billing_remains_bound_to_confirmation_and_endpoint`（L94–L101）：接收`acceptance_main`、`monkeypatch`、`ca_mode`、`key`、`value`。 控制顺序：L100断言`calls == []`；L101断言`report["controller_failure"]["error_type"] == "ValueError"`。 调用`monkeypatch.setenv`、`acceptance_main`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_system_ca_metered_mode_keeps_existing_unspecified_billing`（L104–L110）：接收`acceptance_main`、`monkeypatch`。 控制顺序：L109断言`calls == [{"ca_mode": "system", "billing": None}]`；L110断言`"controller_failure" not in report`。 调用`monkeypatch.setenv`、`monkeypatch.delenv`、`acceptance_main`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_ca_still_requires_explicit_declared_free_mode`（L113–L118）：接收`acceptance_main`、`monkeypatch`。 控制顺序：L117断言`calls == []`；L118断言`report["controller_failure"]["error_type"] == "ValueError"`。 调用`monkeypatch.setenv`、`acceptance_main`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gateway_persists_provider_phase_and_safe_connection_guidance`（L130–L167）：接收`store`、`kind`、`code`、`hint`、`streaming`。 控制顺序：L154断言`len(calls) == store.get_run(run)["model_calls"] == 1`；L160断言`len(failures) == (2 if streaming else 1)`；L161遍历`failures`；L163断言`diagnostic["code"] == code`；L164断言`diagnostic["phase"] == "provider_request"`；L165断言`hint in diagnostic["retry_hint"]`；L166断言`"Schema" not in diagnostic["retry_hint"]`；L167断言`secret not in str(caught.value) + json.dumps(failures)`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`、`new_run`、`pytest.raises`、`gateway.complete`、`len`、`store.get_run`、`store.events`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gateway_persists_provider_phase_and_safe_connection_guidance.handler`（L139–L148）：接收`request`。 控制顺序：L141按`kind == "proxy"`分支；L142抛异常，停止当前正常路径；L144抛异常，停止当前正常路径；L146按`kind == "proxy_certificate"`分支；L147抛异常，停止当前正常路径；L148抛异常，停止当前正常路径。 调用`calls.append`、`httpx.ProxyError`、`ssl.SSLCertVerificationError`、`httpx.ConnectError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_failure_phases_are_unchanged`（L180–L181）：接收`code`、`phase`。 控制顺序：L181断言`failure_diagnostic(code, trace_id="offline-trace")["phase"] == phase`。 调用`failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_live_billing_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L181。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6743`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_live_billing_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4e9f7ad86ad70f94100904ea3992544a98257b335d7232f8cb676c9cb00e7c8f"} -->
````python
# tests/test_live_billing_diagnostics.py
"""Offline regressions for billing evidence and persisted connection diagnostics."""

import json
import ssl
import sys
from types import SimpleNamespace

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from scripts import ci_template_projects as acceptance
from scripts import live_test_client as client
from workbench.domain import Requirement
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_diagnostics import failure_diagnostic


@pytest.fixture
def acceptance_main(tmp_path, monkeypatch):
    """Exercise the real CLI authority/billing path without starting a model suite."""
    event = tmp_path / "event.json"
    event.write_text("{}", encoding="utf-8")
    environment = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": acceptance.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_EVENT_PATH": str(event),
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "ACCEPTANCE_HEAD_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "BASE_URL": client.ENDPOINT,
        "LIVE_TEST_CA": "system",
        "LIVE_BILLING_MODE": "declared_free",
        "LIVE_ZERO_BILLING_ACK": "true",
    }
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", ["ci_template_projects"])
    monkeypatch.setattr(acceptance, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(
        acceptance.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout="a" * 40)
    )
    monkeypatch.setattr(acceptance, "acceptance_settings", lambda *args: object())
    calls = []

    def offline_suite(settings, directory, binding, **kwargs):
        calls.append(kwargs)
        return {"passed": False, "real_model": False, "run_identity": binding}

    monkeypatch.setattr(acceptance, "run_suite", offline_suite)

    def invoke():
        with pytest.raises(SystemExit) as caught:
            acceptance.main()
        assert caught.value.code == 1  # The offline substitute never claims live success.
        report = json.loads((acceptance.REPORTS / "summary.json").read_text(encoding="utf-8"))
        assert report["passed"] is False and report["real_model"] is False
        return calls, report

    return invoke


@pytest.mark.parametrize("ca_mode", ["system", "caddy-ip"])
def test_declared_free_billing_reaches_suite_independently_of_ca(
    acceptance_main, monkeypatch, ca_mode
):
    monkeypatch.setenv("LIVE_TEST_CA", ca_mode)
    calls, report = acceptance_main()
    assert len(calls) == 1 and "controller_failure" not in report
    assert calls[0] == {
        "ca_mode": ca_mode,
        "billing": {
            "mode": "declared_free",
            "attestation": client.ATTESTATION,
            "endpoint": client.ENDPOINT,
            "source": "user_declaration_not_provider_invoice",
            "maximum_cost_usd": 0,
        },
    }


@pytest.mark.parametrize("ca_mode", ["system", "caddy-ip"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("LIVE_ZERO_BILLING_ACK", "false"),
        ("LIVE_ZERO_BILLING_ACK", ""),
        ("BASE_URL", "https://other.test/v1"),
    ],
)
def test_declared_free_billing_remains_bound_to_confirmation_and_endpoint(
    acceptance_main, monkeypatch, ca_mode, key, value
):
    monkeypatch.setenv("LIVE_TEST_CA", ca_mode)
    monkeypatch.setenv(key, value)
    calls, report = acceptance_main()
    assert calls == []
    assert report["controller_failure"]["error_type"] == "ValueError"


def test_system_ca_metered_mode_keeps_existing_unspecified_billing(acceptance_main, monkeypatch):
    monkeypatch.setenv("LIVE_BILLING_MODE", "metered")
    monkeypatch.setenv("BASE_URL", "https://other.test/v1")
    monkeypatch.delenv("LIVE_ZERO_BILLING_ACK")
    calls, report = acceptance_main()
    assert calls == [{"ca_mode": "system", "billing": None}]
    assert "controller_failure" not in report


def test_private_ca_still_requires_explicit_declared_free_mode(acceptance_main, monkeypatch):
    monkeypatch.setenv("LIVE_TEST_CA", "caddy-ip")
    monkeypatch.setenv("LIVE_BILLING_MODE", "metered")
    calls, report = acceptance_main()
    assert calls == []
    assert report["controller_failure"]["error_type"] == "ValueError"


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    "kind,code,hint",
    [
        ("proxy", "proxy_connection_failed", "代理访问策略"),
        ("certificate", "tls_certificate_verification_failed", "不能关闭校验"),
        ("proxy_certificate", "tls_certificate_verification_failed", "不能关闭校验"),
    ],
)
def test_gateway_persists_provider_phase_and_safe_connection_guidance(
    store, kind, code, hint, streaming
):
    calls = []
    secret = "private-provider-error-canary"
    store.settings.base_url = "https://example.test/v1"
    store.settings.model = "test-model"
    store.settings.api_key = SecretStr(secret)

    def handler(request):
        calls.append(request)
        if kind == "proxy":
            raise httpx.ProxyError("403 " + secret, request=request)
        try:
            raise ssl.SSLCertVerificationError(1, secret)
        except ssl.SSLCertVerificationError as cause:
            if kind == "proxy_certificate":
                raise httpx.ProxyError(secret, request=request) from cause
            raise httpx.ConnectError(secret, request=request) from cause

    gateway = ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=streaming)
    run = new_run(store)
    with pytest.raises(ModelFailure) as caught:
        gateway.complete(run, "requirement:1", "offline test", {}, Requirement)
    assert len(calls) == store.get_run(run)["model_calls"] == 1
    failures = [
        event
        for event in store.events(run)
        if event["kind"] in {"model_failure", "assistant_failed"}
    ]
    assert len(failures) == (2 if streaming else 1)
    for event in failures:
        diagnostic = event["data"]["diagnostic"]
        assert diagnostic["code"] == code
        assert diagnostic["phase"] == "provider_request"
        assert hint in diagnostic["retry_hint"]
        assert "Schema" not in diagnostic["retry_hint"]
    assert secret not in str(caught.value) + json.dumps(failures)


@pytest.mark.parametrize(
    "code,phase",
    [
        ("transport_error", "provider_request"),
        ("http_401", "provider_request"),
        ("http_429", "provider_request"),
        ("invalid_json", "response_validation"),
        ("native_schema_violation", "response_validation"),
    ],
)
def test_existing_failure_phases_are_unchanged(code, phase):
    assert failure_diagnostic(code, trace_id="offline-trace")["phase"] == phase
````
