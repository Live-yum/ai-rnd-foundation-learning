# tests/test_live_test_client.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `env`（L12–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L13的`{ "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": live.REPOSITORY, "GITHUB_EVENT_NAME": "wo…`。
- `test_public_pinned_ca_keeps_hostname_and_certificate_verification`（L31–L34）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L33断言`context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED`；L34断言`"PRIVATE KEY" not in client.CA.read_text()`。 调用`client.test_context`、`client.CA.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_ca_never_applies_to_other_destinations`（L47–L49）：接收`endpoint`。 调用`pytest.raises`、`client.test_context`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tampered_certificate_is_rejected_before_trust`（L52–L57）：接收`tmp_path`、`monkeypatch`。 调用`path.write_text`、`client.CA.read_text().replace`、`client.CA.read_text`、`monkeypatch.setattr`、`pytest.raises`、`client.test_context`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_free_mode_is_explicit_zero_and_still_bounded`（L60–L65）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L62断言`config["max_cost_usd"] == config["usd_per_million_tokens"] == 0`；L63断言`config["billing"]["attestation"] == client.ATTESTATION`；L64断言`config["max_model_calls"] == 32 and config["max_output_tokens"] == 8192`；L65断言`config["max_tokens_total"] == 4_000_000`。 调用`live.configuration`、`env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_free_mode_cannot_silently_replace_paid_budget`（L79–L81）：接收`key`、`value`。 调用`pytest.raises`、`live.configuration`、`env`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_is_strict_unauthenticated_and_does_not_follow_redirects`（L85–L107）：接收`monkeypatch`、`status`、`success`。 控制顺序：L102按`success`分支；L103断言`client.probe({**env(), "API_KEY": "never-send-this"})["strict_tls"]`；L107断言`len(requests) == 1`。 调用`monkeypatch.setattr`、`client.probe`、`env`、`pytest.raises`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_is_strict_unauthenticated_and_does_not_follow_redirects.factory`（L90–L99）：接收`**kwargs`。 控制顺序：L91断言`kwargs["verify"].check_hostname`；L92断言`kwargs["verify"].verify_mode == ssl.CERT_REQUIRED`。 调用`httpx.MockTransport`。 返回路径：L99的`httpx.MockTransport(handle)`。
- `test_probe_is_strict_unauthenticated_and_does_not_follow_redirects.factory.handle`（L94–L97）：接收`request`。 控制顺序：L96断言`"authorization" not in request.headers`。 调用`requests.append`、`httpx.Response`。 返回路径：L97的`httpx.Response(status, headers={"location": "https://other.test/v1"})`。
- `test_scoped_transport_refuses_cross_host_and_authenticated_probe`（L110–L123）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L113遍历`[ httpx.Request("POST", "https://other.test/v1/chat/completions")…`；L121断言`transport.calls == 0`。 调用`client.TestServiceTransport`、`httpx.Request`、`pytest.raises`、`transport.handle_request`、`transport.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_platform_free_mode_needs_attested_exact_endpoint`（L135–L176）：接收`settings`、`tmp_path`、`monkeypatch`、`ack`、`endpoint`、`cost`、`price`、`accepted`。 控制顺序：L172按`accepted`分支；L173断言`invoke() == "offline-authority-checked"`。 调用`settings.model_copy`、`monkeypatch.setattr`、`design`、`invoke`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_platform_free_mode_needs_attested_exact_endpoint.invoke`（L160–L170）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`mini_swe.run_agent`、`ModelGateway`。 返回路径：L161的`mini_swe.run_agent( settings, ModelGateway(settings, None), "offline", plan.tasks[0], plan…`。
- `test_transport_timings_preserve_response_and_timeout_semantics`（L180–L235）：接收`monkeypatch`、`failure`。 控制顺序：L213按`failure`分支；L217断言`http.post(client.ENDPOINT + "/chat/completions", content=b"private-request").content …`；L221断言`transport.calls == 1 and transport.responses == (0 if failure == "headers" else 1)`；L223断言`data == [ { "attempt": 1, "request_body_bytes": 15, "read_timeout_seconds": 7, "heade…`；L234断言`bool(closed) is (failure != "headers")`；L235断言`"private" not in json.dumps(data)`。 调用`monkeypatch.setattr`、`type`、`staticmethod`、`httpx.MockTransport`、`client.TestServiceTransport`、`httpx.Client`、`pytest.raises`、`http.post`、`timing_receipts`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_timings_preserve_response_and_timeout_semantics.Body`（L191–L201）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_transport_timings_preserve_response_and_timeout_semantics.Body.__iter__`（L192–L198）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L196按`failure == "body"`分支；L197抛异常，停止当前正常路径。 调用`httpx.ReadTimeout`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_transport_timings_preserve_response_and_timeout_semantics.Body.close`（L200–L201）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`closed.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_timings_preserve_response_and_timeout_semantics.request`（L203–L208）：接收`req`。 控制顺序：L204断言`req.extensions["timeout"]["read"] == 7`；L206按`failure == "headers"`分支；L207抛异常，停止当前正常路径。 调用`httpx.ReadTimeout`、`httpx.Response`、`Body`。 返回路径：L208的`httpx.Response(200, stream=Body())`。
- `test_timing_projection_rejects_non_numeric_data_and_limits_inventory`（L238–L249）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L243遍历`((False, TURN_FIELDS, 8), (True, ATTEMPT_FIELDS, 32))`；L244遍历`("private-text", True, -1, float("nan"), float("inf"), 10**1000, …`；L247断言`len(result) == limit`；L248断言`all(value is None for row in result for value in row.values())`；L249断言`"private" not in json.dumps(result)`。 调用`float`、`dict.fromkeys`、`timing_receipts`、`len`、`all`、`row.values`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_live_test_client.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L249。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8814`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_live_test_client.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0ed08af58e8d98f769fad40183e69f9b821b778cf690ec8905c60d62681d7e2e"} -->
````python
# tests/test_live_test_client.py
"""Offline trust scope, no-charge attestation and bounded client contracts."""

import ssl

import httpx
import pytest

from scripts import ci_live_modules as live
from scripts import live_test_client as client


def env():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": live.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "LIVE_SCENARIO": "mini-swe-sla",
        "BASE_URL": client.ENDPOINT,
        "MODE": "offline",
        "LIVE_TEST_CA": "caddy-ip",
        "LIVE_BILLING_MODE": "declared_free",
        "LIVE_ZERO_BILLING_ACK": "true",
        "LIVE_MAX_COST_USD": "0",
        "LIVE_USD_PER_MILLION_TOKENS": "0",
    }


def test_public_pinned_ca_keeps_hostname_and_certificate_verification():
    context = client.test_context(client.ENDPOINT, "caddy-ip")
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    assert "PRIVATE KEY" not in client.CA.read_text()


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://170.106.181.109:8317/v1",
        "https://170.106.181.109/v1",
        "https://example.test:8317/v1",
        client.ENDPOINT + "?other",
        client.ENDPOINT + "/models",
    ],
)
def test_private_ca_never_applies_to_other_destinations(endpoint):
    with pytest.raises(ValueError, match="endpoint"):
        client.test_context(endpoint, "caddy-ip")


def test_tampered_certificate_is_rejected_before_trust(tmp_path, monkeypatch):
    path = tmp_path / "ca.pem"
    path.write_text(client.CA.read_text().replace("MI", "MJ", 1))
    monkeypatch.setattr(client, "CA", path)
    with pytest.raises(ValueError, match="fingerprint"):
        client.test_context(client.ENDPOINT, "caddy-ip")


def test_free_mode_is_explicit_zero_and_still_bounded():
    config = live.configuration(env())
    assert config["max_cost_usd"] == config["usd_per_million_tokens"] == 0
    assert config["billing"]["attestation"] == client.ATTESTATION
    assert config["max_model_calls"] == 32 and config["max_output_tokens"] == 8192
    assert config["max_tokens_total"] == 4_000_000


@pytest.mark.parametrize(
    "key,value",
    [
        ("LIVE_ZERO_BILLING_ACK", "false"),
        ("LIVE_BILLING_MODE", "metered"),
        ("LIVE_BILLING_MODE", "unknown"),
        ("BASE_URL", "https://other.test/v1"),
        ("LIVE_MAX_COST_USD", "10"),
        ("LIVE_USD_PER_MILLION_TOKENS", "1"),
    ],
)
def test_free_mode_cannot_silently_replace_paid_budget(key, value):
    with pytest.raises(ValueError):
        live.configuration({**env(), key: value})


@pytest.mark.parametrize("status,success", [(200, True), (401, True), (403, False), (302, False)])
def test_probe_is_strict_unauthenticated_and_does_not_follow_redirects(
    monkeypatch, status, success
):
    requests = []

    def factory(**kwargs):
        assert kwargs["verify"].check_hostname
        assert kwargs["verify"].verify_mode == ssl.CERT_REQUIRED

        def handle(request):
            requests.append(request)
            assert "authorization" not in request.headers
            return httpx.Response(status, headers={"location": "https://other.test/v1"})

        return httpx.MockTransport(handle)

    monkeypatch.setattr(client.httpx, "HTTPTransport", factory)
    if success:
        assert client.probe({**env(), "API_KEY": "never-send-this"})["strict_tls"]
    else:
        with pytest.raises(ValueError):
            client.probe(env())
    assert len(requests) == 1


def test_scoped_transport_refuses_cross_host_and_authenticated_probe():
    transport = client.TestServiceTransport(client.ENDPOINT, "caddy-ip")
    try:
        for request in [
            httpx.Request("POST", "https://other.test/v1/chat/completions"),
            httpx.Request(
                "GET", client.ENDPOINT + "/models", headers={"Authorization": "not-real"}
            ),
        ]:
            with pytest.raises(ValueError, match="destination"):
                transport.handle_request(request)
        assert transport.calls == 0
    finally:
        transport.close()


@pytest.mark.parametrize(
    "ack,endpoint,cost,price,accepted",
    [
        (True, client.ENDPOINT, 0, 0, True),
        (False, client.ENDPOINT, 0, 0, False),
        (True, "https://other.test/v1", 0, 0, False),
        (True, client.ENDPOINT, 1, 0, False),
    ],
)
def test_platform_free_mode_needs_attested_exact_endpoint(
    settings, tmp_path, monkeypatch, ack, endpoint, cost, price, accepted
):
    from scripts.sla_fixture import design
    from workbench.coding import mini_swe
    from workbench.errors import UnsupportedScope
    from workbench.llm import ModelGateway

    settings = settings.model_copy(
        update={
            "mini_swe_enabled": True,
            "base_url": client.ENDPOINT,
            "model": "offline",
            "max_output_tokens": 8192,
            "mini_swe_billing_mode": "declared_free",
            "mini_swe_zero_billing_ack": ack,
            "mini_swe_zero_billing_endpoint": endpoint,
            "mini_swe_max_cost_usd": cost,
            "mini_swe_usd_per_million_tokens": price,
        }
    )
    monkeypatch.setattr(mini_swe, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(mini_swe, "_run", lambda *args: ("offline-authority-checked", {}))
    plan = design().implementation

    def invoke():
        return mini_swe.run_agent(
            settings,
            ModelGateway(settings, None),
            "offline",
            plan.tasks[0],
            plan,
            tmp_path,
            tmp_path / "worker",
            {},
        )

    if accepted:
        assert invoke() == "offline-authority-checked"
    else:
        with pytest.raises(UnsupportedScope):
            invoke()


@pytest.mark.parametrize("failure", [None, "headers", "body"])
def test_transport_timings_preserve_response_and_timeout_semantics(monkeypatch, failure):
    import json

    from workbench.coding.timing import http_trace_receipt, timing_receipts

    clock = [10.0]
    monkeypatch.setattr(
        client, "time", type("Clock", (), {"monotonic": staticmethod(lambda: clock[0])})
    )
    closed = []

    class Body(httpx.SyncByteStream):
        def __iter__(self):
            clock[0] += 2
            yield b"private-model-text"
            clock[0] += 3
            if failure == "body":
                raise httpx.ReadTimeout("private-server-detail")
            yield b"done"

        def close(self):
            closed.append(True)

    def request(req):
        assert req.extensions["timeout"]["read"] == 7
        clock[0] += 4
        if failure == "headers":
            raise httpx.ReadTimeout("private-server-detail")
        return httpx.Response(200, stream=Body())

    monkeypatch.setattr(client.httpx, "HTTPTransport", lambda **kw: httpx.MockTransport(request))
    transport = client.TestServiceTransport(client.ENDPOINT)
    with httpx.Client(transport=transport, timeout=7, trust_env=False) as http:
        if failure:
            with pytest.raises(httpx.ReadTimeout):
                http.post(client.ENDPOINT + "/chat/completions", content=b"private-request")
        else:
            assert (
                http.post(client.ENDPOINT + "/chat/completions", content=b"private-request").content
                == b"private-model-textdone"
            )
    assert transport.calls == 1 and transport.responses == (0 if failure == "headers" else 1)
    data = timing_receipts(transport.timings, attempts=True)
    assert data == [
        {
            "attempt": 1,
            "request_body_bytes": 15,
            "read_timeout_seconds": 7,
            "headers_seconds": None if failure == "headers" else 4,
            "elapsed_seconds": 4 if failure == "headers" else 9,
            "response_bytes": 0 if failure == "headers" else 18 if failure == "body" else 22,
            "http_trace": http_trace_receipt({"event_count": 0}),
        }
    ]
    assert bool(closed) is (failure != "headers")
    assert "private" not in json.dumps(data)


def test_timing_projection_rejects_non_numeric_data_and_limits_inventory():
    import json

    from workbench.coding.timing import ATTEMPT_FIELDS, TURN_FIELDS, timing_receipts

    for attempts, fields, limit in ((False, TURN_FIELDS, 8), (True, ATTEMPT_FIELDS, 32)):
        for poison in ("private-text", True, -1, float("nan"), float("inf"), 10**1000, {}, []):
            values = [{**dict.fromkeys(fields, poison), "raw": "private-key"}] * 40
            result = timing_receipts(values, attempts=attempts)
            assert len(result) == limit
            assert all(value is None for row in result for value in row.values())
            assert "private" not in json.dumps(result)
````
