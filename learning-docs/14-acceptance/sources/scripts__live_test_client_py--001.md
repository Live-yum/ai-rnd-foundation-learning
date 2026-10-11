# scripts/live_test_client.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.live_test_client；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.model_diagnostics`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `zero_billing`（L22–L36）：接收`env`。 控制顺序：L23按`env.get("LIVE_BILLING_MODE", "metered") != "declared_free"`分支；L24抛异常，停止当前正常路径；L25按`env.get("LIVE_ZERO_BILLING_ACK") != "true" or env.get("BASE_URL", "").rstrip("/") != …`分支；L29抛异常，停止当前正常路径。 调用`env.get`、`ValueError`、`env.get("BASE_URL", "").rstrip`。 返回路径：L30的`{ "mode": "declared_free", "attestation": ATTESTATION, "endpoint": ENDPOINT, "source": "us…`。
- `test_context`（L39–L56）：接收`endpoint`、`mode`。 控制顺序：L40按`mode not in {"system", "caddy-ip"}`分支；L41抛异常，停止当前正常路径；L43按`mode == "caddy-ip"`分支；L44按`endpoint.rstrip("/") != ENDPOINT`分支；L45抛异常，停止当前正常路径；L47按`"PRIVATE KEY" in pem or not re.fullmatch( r"-----BEGIN CERTIFICATE-----\n[A-Za-z0-9+/…`分支；L50抛异常，停止当前正常路径；L51按`hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest() != FINGERPRINT`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`ssl.create_default_context`、`endpoint.rstrip`、`CA.read_text`、`re.fullmatch`、`hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest`、`hashlib.sha256`、`ssl.PEM_cert_to_DER_cert`、`context.load_verify_locations`。 返回路径：L56的`context`。
- `TestServiceTransport`（L59–L85）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `TestServiceTransport.__init__`（L62–L67）：接收`endpoint`、`mode`。 调用`endpoint.rstrip`、`httpx.HTTPTransport`、`test_context`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TestServiceTransport.handle_request`（L69–L82）：接收`request`。 控制顺序：L75按`not allowed`分支；L76抛异常，停止当前正常路径；L77按`request.method == "POST"`分支；L80按`request.method == "POST"`分支。 调用`str`、`ValueError`、`self.inner.handle_request`。 返回路径：L82的`response`。
- `TestServiceTransport.close`（L84–L85）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.inner.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `probe`（L88–L124）：接收`env`。 控制顺序：L89按`env.get("GITHUB_ACTIONS") != "true" or env.get("GITHUB_REPOSITORY") != "Live-yum/ai-r…`分支；L97抛异常，停止当前正常路径；L99按`not endpoint.startswith("https://")`分支；L100抛异常，停止当前正常路径；L114按`response.status_code not in {200, 401}`分支；L115抛异常，停止当前正常路径。 调用`env.get`、`re.fullmatch`、`ValueError`、`env.get("BASE_URL", "").rstrip`、`endpoint.startswith`、`zero_billing`、`httpx.Client`、`TestServiceTransport`、`client.stream`。 返回路径：L116的`{ "strict_tls": True, "http_status": response.status_code, "authentication_sent": False, "…`。
- `main`（L127–L139）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L136抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.parse_args`、`probe`、`transport_failure`、`SystemExit`、`write_json`、`print`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/live_test_client.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L143。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5196`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/live_test_client.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4faf3123c96e89a20920ac9e4faf780ed2bd2d026f3056102babd1f218694b24"} -->
````python
# scripts/live_test_client.py
"""Explicit test-only trust for the user-owned service; never a system CA change."""

import argparse
import hashlib
import json
import os
import re
import ssl

import httpx

from workbench.filesystem import write_json
from workbench.model_diagnostics import transport_failure
from workbench.settings import ROOT

ENDPOINT = "https://170.106.181.109:8317/v1"
CA = ROOT / "tests/resources/live-service/caddy-root.pem"
FINGERPRINT = "15db86a8d11566625d4220515991727c900e232e641d8e7fcb08b0b42d3079af"
ATTESTATION = "user-confirmed-no-charge-2026-10-11"


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
        response = self.inner.handle_request(request)
        if request.method == "POST":
            self.responses += 1
        return response

    def close(self):
        self.inner.close()


def probe(env):
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_REPOSITORY") != "Live-yum/ai-rnd-foundation-learning"
        or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or env.get("GITHUB_RUN_ATTEMPT") != "1"
        or not re.fullmatch(r"[a-f0-9]{40}", env.get("GITHUB_SHA", ""))
        or env.get("REVIEWED_SHA") != env.get("GITHUB_SHA")
    ):
        raise ValueError("reviewed_first_manual_dispatch_required")
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
                "head_sha": env["GITHUB_SHA"],
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
