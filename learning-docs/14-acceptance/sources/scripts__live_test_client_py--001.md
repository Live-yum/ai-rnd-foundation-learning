# scripts/live_test_client.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.live_test_client；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.model_diagnostics`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `phase_trace`（L31–L48）：接收`facts`、`started`、`previous`。 返回路径：L48的`trace`。
- `phase_trace.trace`（L32–L46）：接收`name`、`info`。 控制顺序：L38按`phase is not None and state in {"started", "complete", "failed"}`分支；L41按`state == "failed"`分支；L45按`previous is not None`分支。 调用`name.rpartition`、`HTTP_TRACE_NAMES.get`、`min`、`facts.setdefault`、`max`、`time.monotonic`、`previous`。 返回路径：L46的`previous(name, info)`。
- `zero_billing`（L51–L65）：接收`env`。 控制顺序：L52按`env.get("LIVE_BILLING_MODE", "metered") != "declared_free"`分支；L53抛异常，停止当前正常路径；L54按`env.get("LIVE_ZERO_BILLING_ACK") != "true" or env.get("BASE_URL", "").rstrip("/") != …`分支；L58抛异常，停止当前正常路径。 调用`env.get`、`ValueError`、`env.get("BASE_URL", "").rstrip`。 返回路径：L59的`{ "mode": "declared_free", "attestation": ATTESTATION, "endpoint": ENDPOINT, "source": "us…`。
- `test_context`（L68–L85）：接收`endpoint`、`mode`。 控制顺序：L69按`mode not in {"system", "caddy-ip"}`分支；L70抛异常，停止当前正常路径；L72按`mode == "caddy-ip"`分支；L73按`endpoint.rstrip("/") != ENDPOINT`分支；L74抛异常，停止当前正常路径；L76按`"PRIVATE KEY" in pem or not re.fullmatch( r"-----BEGIN CERTIFICATE-----\n[A-Za-z0-9+/…`分支；L79抛异常，停止当前正常路径；L80按`hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest() != FINGERPRINT`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`ssl.create_default_context`、`endpoint.rstrip`、`CA.read_text`、`re.fullmatch`、`hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest`、`hashlib.sha256`、`ssl.PEM_cert_to_DER_cert`、`context.load_verify_locations`。 返回路径：L85的`context`。
- `TestServiceTransport`（L88–L148）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `TestServiceTransport.__init__`（L91–L97）：接收`endpoint`、`mode`。 调用`endpoint.rstrip`、`httpx.HTTPTransport`、`test_context`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TestServiceTransport.handle_request`（L99–L145）：接收`request`。 控制顺序：L105按`not allowed`分支；L106抛异常，停止当前正常路径；L107按`request.method == "POST"`分支；L111按`request.method == "POST" and len(self.timings) < 32`分支；L124按`timing is not None`分支；L129按`timing is not None`分支；L131抛异常，停止当前正常路径；L135按`timing is not None`分支。后续分支沿下方源码相同行号继续阅读。 调用`str`、`ValueError`、`time.monotonic`、`len`、`request.extensions.get("timeout", {}).get`、`request.extensions.get`、`self.timings.append`、`phase_trace`、`self.inner.handle_request`等。 返回路径：L145的`response`。
- `TestServiceTransport.close`（L147–L148）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.inner.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TimedResponseStream`（L151–L171）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `TimedResponseStream.__init__`（L152–L153）：接收`inner`、`timing`、`started`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TimedResponseStream.finish`（L155–L157）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L156按`self.timing["elapsed_seconds"] is None`分支。 调用`max`、`time.monotonic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TimedResponseStream.__iter__`（L159–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L161遍历`self.inner`。 调用`len`、`self.finish`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `TimedResponseStream.close`（L167–L171）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.inner.close`、`self.finish`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `reviewed_head`（L174–L201）：接收`env`。 源码说明：Accept only the existing explicit dispatch or same-repository label scope.。 控制顺序：L176按`env.get("GITHUB_ACTIONS") != "true" or env.get("GITHUB_REPOSITORY") != "Live-yum/ai-r…`分支；L181抛异常，停止当前正常路径；L183按`event_name == "workflow_dispatch"`分支；L185按`event_name == "pull_request"`分支；L189按`not ( event.get("action") == "labeled" and event.get("label", {}).get("name") == "run…`分支；L196抛异常，停止当前正常路径；L198抛异常，停止当前正常路径；L199按`not re.fullmatch(r"[a-f0-9]{40}", head) or env.get("REVIEWED_SHA") != head`分支。后续分支沿下方源码相同行号继续阅读。 调用`env.get`、`ValueError`、`json.loads`、`Path(env["GITHUB_EVENT_PATH"]).read_text`、`Path`、`event.get`、`event.get("label", {}).get`、`pr.get("head", {}).get("repo", {}).get`、`pr.get("head", {}).get`等。 返回路径：L201的`head`。
- `probe`（L204–L232）：接收`env`。 控制顺序：L207按`not endpoint.startswith("https://")`分支；L208抛异常，停止当前正常路径；L222按`response.status_code not in {200, 401}`分支；L223抛异常，停止当前正常路径。 调用`reviewed_head`、`env.get("BASE_URL", "").rstrip`、`env.get`、`endpoint.startswith`、`ValueError`、`zero_billing`、`httpx.Client`、`TestServiceTransport`、`client.stream`。 返回路径：L224的`{ "strict_tls": True, "http_status": response.status_code, "authentication_sent": False, "…`。
- `main`（L235–L247）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L244抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.parse_args`、`probe`、`transport_failure`、`SystemExit`、`write_json`、`print`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/live_test_client.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L251。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9572`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/live_test_client.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1f7879ddcd85348c2ae35da1a690912d8ddc1d827e3aacc26334e5edae519a07"} -->
````python
# scripts/live_test_client.py
"""Explicit test-only trust for the user-owned service; never a system CA change."""

import argparse
import hashlib
import json
import os
import re
import ssl
import time
from pathlib import Path

import httpx

from workbench.filesystem import write_json
from workbench.model_diagnostics import transport_failure
from workbench.settings import ROOT

ENDPOINT = "https://170.106.181.109:8317/v1"
CA = ROOT / "tests/resources/live-service/caddy-root.pem"
FINGERPRINT = "15db86a8d11566625d4220515991727c900e232e641d8e7fcb08b0b42d3079af"
ATTESTATION = "user-confirmed-no-charge-2026-10-11"
HTTP_TRACE_NAMES = {
    "connection.connect_tcp": "connect",
    "connection.start_tls": "tls",
    "http11.send_request_headers": "request_headers",
    "http11.send_request_body": "request_body",
    "http11.receive_response_headers": "response_headers",
}


def phase_trace(facts, started, previous):
    def trace(name, info):
        # httpcore info contains request headers and exception objects. Do not
        # inspect, copy, stringify or persist it. Only forward an existing hook.
        try:
            event, _, state = name.rpartition(".")
            phase = HTTP_TRACE_NAMES.get(event)
            if phase is not None and state in {"started", "complete", "failed"}:
                facts["event_count"] = min(64, facts["event_count"] + 1)
                facts.setdefault(f"{phase}_{state}_seconds", max(0, time.monotonic() - started))
                if state == "failed":
                    facts["failed_phase"] = phase
        except Exception:
            pass  # Optional diagnostics cannot replace any transport outcome.
        if previous is not None:
            return previous(name, info)

    return trace


def zero_billing(env):
    if env.get("LIVE_BILLING_MODE", "metered") != "declared_free":
        raise ValueError("explicit_zero_billing_mode_required")
    if (
        env.get("LIVE_ZERO_BILLING_ACK") != "true"
        or env.get("BASE_URL", "").rstrip("/") != ENDPOINT
    ):
        raise ValueError("zero_billing_confirmation_or_endpoint_missing")
    return {
        "mode": "declared_free",
        "attestation": ATTESTATION,
        "endpoint": ENDPOINT,
        "source": "user_declaration_not_provider_invoice",
        "maximum_cost_usd": 0,
    }


def test_context(endpoint, mode):
    if mode not in {"system", "caddy-ip"}:
        raise ValueError("unknown_test_ca_mode")
    context = ssl.create_default_context()
    if mode == "caddy-ip":
        if endpoint.rstrip("/") != ENDPOINT:
            raise ValueError("test_ca_endpoint_mismatch")
        pem = CA.read_text(encoding="ascii")
        if "PRIVATE KEY" in pem or not re.fullmatch(
            r"-----BEGIN CERTIFICATE-----\n[A-Za-z0-9+/=\r\n]+-----END CERTIFICATE-----\s*", pem
        ):
            raise ValueError("public_certificate_only")
        if hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest() != FINGERPRINT:
            raise ValueError("test_ca_fingerprint_mismatch")
        context.load_verify_locations(cadata=pem)
    if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
        raise ValueError("strict_tls_required")
    return context


class TestServiceTransport(httpx.BaseTransport):
    """Restrict the scoped trust to two exact endpoints, with no redirects."""

    def __init__(self, endpoint, mode="system"):
        self.endpoint = endpoint.rstrip("/")
        self.inner = httpx.HTTPTransport(
            verify=test_context(self.endpoint, mode), retries=0, trust_env=False
        )
        self.calls = self.responses = 0
        self.timings = []

    def handle_request(self, request):
        allowed = (
            request.method == "GET"
            and str(request.url) == self.endpoint + "/models"
            and "authorization" not in request.headers
        ) or (request.method == "POST" and str(request.url) == self.endpoint + "/chat/completions")
        if not allowed:
            raise ValueError("test_transport_destination_rejected")
        if request.method == "POST":
            self.calls += 1
        timing = None
        started = time.monotonic()
        if request.method == "POST" and len(self.timings) < 32:
            timing = {
                "attempt": self.calls,
                "request_body_bytes": len(request.content),
                "read_timeout_seconds": request.extensions.get("timeout", {}).get("read"),
                "headers_seconds": None,
                "elapsed_seconds": None,
                "response_bytes": 0,
                "http_trace": {"event_count": 0, "failed_phase": None},
            }
            self.timings.append(timing)
        had_trace = "trace" in request.extensions
        previous_trace = request.extensions.get("trace")
        if timing is not None:
            request.extensions["trace"] = phase_trace(timing["http_trace"], started, previous_trace)
        try:
            response = self.inner.handle_request(request)
        except BaseException:
            if timing is not None:
                timing["elapsed_seconds"] = max(0, time.monotonic() - started)
            raise
        finally:
            # Trace only through the response-header boundary. Restore the
            # original hook before lazy body reads/close, including on failure.
            if timing is not None:
                if had_trace:
                    request.extensions["trace"] = previous_trace
                else:
                    request.extensions.pop("trace", None)
        if request.method == "POST":
            self.responses += 1
        if timing is not None:
            timing["headers_seconds"] = max(0, time.monotonic() - started)
            response.stream = TimedResponseStream(response.stream, timing, started)
        return response

    def close(self):
        self.inner.close()


class TimedResponseStream(httpx.SyncByteStream):
    def __init__(self, inner, timing, started):
        self.inner, self.timing, self.started = inner, timing, started

    def finish(self):
        if self.timing["elapsed_seconds"] is None:
            self.timing["elapsed_seconds"] = max(0, time.monotonic() - self.started)

    def __iter__(self):
        try:
            for chunk in self.inner:
                self.timing["response_bytes"] += len(chunk)
                yield chunk
        finally:
            self.finish()

    def close(self):
        try:
            self.inner.close()
        finally:
            self.finish()


def reviewed_head(env):
    """Accept only the existing explicit dispatch or same-repository label scope."""
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_REPOSITORY") != "Live-yum/ai-rnd-foundation-learning"
        or env.get("GITHUB_RUN_ATTEMPT") != "1"
    ):
        raise ValueError("reviewed_first_acceptance_event_required")
    event_name = env.get("GITHUB_EVENT_NAME")
    if event_name == "workflow_dispatch":
        head = env.get("GITHUB_SHA", "")
    elif event_name == "pull_request":
        head = env.get("ACCEPTANCE_HEAD_SHA", "")
        event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        pr = event.get("pull_request", {})
        if not (
            event.get("action") == "labeled"
            and event.get("label", {}).get("name") == "run-live-acceptance"
            and pr.get("head", {}).get("repo", {}).get("full_name") == env["GITHUB_REPOSITORY"]
            and pr.get("base", {}).get("repo", {}).get("full_name") == env["GITHUB_REPOSITORY"]
            and pr.get("head", {}).get("sha") == head
        ):
            raise ValueError("untrusted_pull_request")
    else:
        raise ValueError("reviewed_first_acceptance_event_required")
    if not re.fullmatch(r"[a-f0-9]{40}", head) or env.get("REVIEWED_SHA") != head:
        raise ValueError("reviewed_head_mismatch")
    return head


def probe(env):
    head = reviewed_head(env)
    endpoint = env.get("BASE_URL", "").rstrip("/")
    if not endpoint.startswith("https://"):
        raise ValueError("https_required")
    mode = env.get("LIVE_TEST_CA", "system")
    billing = (
        zero_billing(env)
        if mode == "caddy-ip" or env.get("LIVE_BILLING_MODE") == "declared_free"
        else {"mode": "metered"}
    )
    with httpx.Client(
        transport=TestServiceTransport(endpoint, mode),
        timeout=20,
        follow_redirects=False,
        trust_env=False,
    ) as client:
        with client.stream("GET", endpoint + "/models") as response:
            if response.status_code not in {200, 401}:
                raise ValueError("unauthenticated_service_probe_rejected")
            return {
                "strict_tls": True,
                "http_status": response.status_code,
                "authentication_sent": False,
                "head_sha": head,
                "ca_mode": mode,
                "ca_sha256": FINGERPRINT if mode == "caddy-ip" else None,
                "billing": billing,
            }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    receipt = {"strict_tls": False, "authentication_sent": False}
    try:
        receipt = probe(os.environ)
    except Exception as exc:
        diagnostic = transport_failure(exc)
        receipt["failure"] = diagnostic[0] if diagnostic else "strict_unauthenticated_probe_failed"
        raise SystemExit(1) from None
    finally:
        write_json(ROOT / "reports/live-tls.json", receipt)
        print(json.dumps(receipt))


if __name__ == "__main__":
    main()
````
