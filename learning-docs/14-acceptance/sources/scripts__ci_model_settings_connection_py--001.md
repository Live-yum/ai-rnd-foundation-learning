# scripts/ci_model_settings_connection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_model_settings_connection；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_connection`、`workbench.model_discovery`、`workbench.model_settings`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `BoundedTransport`（L51–L71）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BoundedTransport.__init__`（L54–L57）：接收`endpoint`、`inner`。 调用`httpx.HTTPTransport`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedTransport.handle_request`（L59–L67）：接收`request`。 控制顺序：L64按`kind is None or self.counts[kind] >= 1`分支；L65抛异常，停止当前正常路径。 调用`{ ("POST", self.endpoint + "/chat/completions"): "inference", ("G…`、`str`、`httpx.RequestError`、`self.inner.handle_request`。 返回路径：L67的`self.inner.handle_request(request)`。
- `BoundedTransport.close`（L69–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `safe_result`（L74–L83）：接收`result`。 控制顺序：L81按`type(status) is int and 100 <= status <= 599`分支。 调用`result.get`、`type`。 返回路径：L83的`safe`。
- `acceptance`（L86–L178）：接收`values`、`transport`、`discover`。 控制顺序：L94按`any(not values.get(key, "").strip() for key in ("BASE_URL", "API_KEY", "MODE"))`分支；L97按`urlsplit(values["BASE_URL"].strip()).scheme != "https"`分支；L100按`values["API_KEY"] in endpoint`分支；L112遍历`("BASE_URL", "API_KEY", "MODE")`；L128按`response.status_code != 200`分支；L131按`not public["ready"] or public["default"]["api_key"] != "configured"`分支；L143按`response.status_code != 200`分支；L147按`not saved["ready"] or configuration.default.base_url != endpoint or configuration.def…`分支。后续分支沿下方源码相同行号继续阅读。 调用`any`、`values.get(key, "").strip`、`values.get`、`urlsplit`、`values["BASE_URL"].strip`、`validate_model_url`、`BoundedTransport`、`tempfile.TemporaryDirectory`、`Path`等。 返回路径：L95的`{**receipt, "code": "missing_configuration"}`；L98的`{**receipt, "code": "https_required"}`；L101的`{**receipt, "code": "invalid_configuration"}`。
- `acceptance.auth`（L120–L122）：接收`request`。用本机Dex真实签发的JWT访问本机API创建密钥，不伪造token，也不向云身份服务注册账号。 控制顺序：L121按`request.headers.get("authorization") != "Bearer " + token`分支；L122抛异常，停止当前正常路径。 调用`request.headers.get`、`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L181–L189）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`logging.disable`、`acceptance`、`os.environ.get`、`REPORT.parent.mkdir`、`REPORT.write_text`、`json.dumps`、`print`。 返回路径：L189的`0 if result["code"] == "passed" else 1`。

</details>

**创建路径：** `scripts/ci_model_settings_connection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L193。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7471`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_model_settings_connection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9becc004e5067cd2a2937f85cd6357332012dd2726b063483c8dc4c7970b84f1"} -->
````python
# scripts/ci_model_settings_connection.py
"""One authorized .env/settings/probe acceptance; never a generation workload.

Only static classifications and request counts leave this process. Temporary
credentials are removed on exit; no raw settings, responses or URLs are logged.
"""

import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import httpx
from dotenv import set_key
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from workbench.model_connection import ConnectionTestRequest, ModelConnectionTester
from workbench.model_discovery import ModelDiscoverer, ModelDiscoveryRequest
from workbench.model_settings import register_model_settings_routes
from workbench.settings import Settings, validate_model_url

REPORT = Path("reports/model-settings-connection/summary.json")
CODES = {
    "connected",
    "invalid_configuration",
    "truncated",
    "invalid_response",
    "authentication_failed",
    "permission_denied",
    "model_or_endpoint_not_found",
    "timeout",
    "rate_limited",
    "connection_failed",
    "transport_error",
    "internal_error",
    "tls_certificate_verification_failed",
    "proxy_connection_failed",
    "dns_error",
    "models_discovered",
    "discovery_unsupported",
    "http_error",
    "response_too_large",
    "redirect_blocked",
}


class BoundedTransport(httpx.BaseTransport):
    """Enforce exact destinations and at most one request of each approved kind."""

    def __init__(self, endpoint, *, inner=None):
        self.endpoint = endpoint
        self.inner = inner or httpx.HTTPTransport(verify=True, trust_env=False, retries=0)
        self.counts = {"inference": 0, "catalog": 0}

    def handle_request(self, request):
        kind = {
            ("POST", self.endpoint + "/chat/completions"): "inference",
            ("GET", self.endpoint + "/models"): "catalog",
        }.get((request.method, str(request.url)))
        if kind is None or self.counts[kind] >= 1:
            raise httpx.RequestError("acceptance_scope_blocked", request=request)
        self.counts[kind] += 1
        return self.inner.handle_request(request)

    def close(self):
        # The two existing clients share one bounded transport; owner closes it.
        pass


def safe_result(result):
    code = result.get("code")
    safe = {
        "ok": result.get("ok") is True,
        "code": code if code in CODES else "other_failure",
    }
    status = result.get("http_status")
    if type(status) is int and 100 <= status <= 599:
        safe["http_status"] = status
    return safe


def acceptance(values, *, transport=None, discover=False):
    receipt = {
        "scope": "env_settings_default_probe",
        "real_service": transport is None,
        "code": "not_started",
        "inference_requests": 0,
        "catalog_requests": 0,
    }
    if any(not values.get(key, "").strip() for key in ("BASE_URL", "API_KEY", "MODE")):
        return {**receipt, "code": "missing_configuration"}
    try:
        if urlsplit(values["BASE_URL"].strip()).scheme != "https":
            return {**receipt, "code": "https_required"}
        endpoint = validate_model_url(values["BASE_URL"].strip())
        if values["API_KEY"] in endpoint:
            return {**receipt, "code": "invalid_configuration"}
    except ValueError:
        return {**receipt, "code": "invalid_configuration"}

    bounded = BoundedTransport(endpoint, inner=transport)
    try:
        with tempfile.TemporaryDirectory(prefix="settings-connection-") as directory:
            root = Path(directory)
            root.chmod(0o700)
            dotenv = root / ".env"
            dotenv.touch(mode=0o600)
            for name in ("BASE_URL", "API_KEY", "MODE"):
                set_key(dotenv, name, values[name])
            # Prevent process variables from masking the .env initialization.
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings(_env_file=dotenv, data_dir=root / "data", llm_timeout=20)
            token = uuid.uuid4().hex
            app = FastAPI()

            def auth(request: Request):
                if request.headers.get("authorization") != "Bearer " + token:
                    raise HTTPException(401)

            register_model_settings_routes(app, settings, auth)
            with TestClient(app) as client:
                client.headers["authorization"] = "Bearer " + token
                response = client.get("/settings/models")
                if response.status_code != 200:
                    return {**receipt, "code": "settings_read_failed"}
                public = response.json()
                if not public["ready"] or public["default"]["api_key"] != "configured":
                    return {**receipt, "code": "env_initialization_failed"}
                response = client.put(
                    "/settings/models",
                    json={
                        "expected_revision": public["revision"],
                        "default": {
                            "base_url": public["default"]["base_url"],
                            "model": public["default"]["model"],
                        },
                    },
                )
                if response.status_code != 200:
                    return {**receipt, "code": "same_endpoint_save_failed"}
                saved = response.json()
                configuration = settings.model_configuration()
                if (
                    not saved["ready"]
                    or configuration.default.base_url != endpoint
                    or configuration.default.api_key.get_secret_value() != values["API_KEY"]
                ):
                    return {**receipt, "code": "saved_configuration_mismatch"}
                receipt["settings_lifecycle"] = "passed"
                if discover:
                    result = ModelDiscoverer(settings, bounded).discover(
                        ModelDiscoveryRequest(stage="default", expected_revision=saved["revision"])
                    )
                    receipt["catalog"] = safe_result(result)
                result = ModelConnectionTester(settings, bounded).test(
                    ConnectionTestRequest(
                        stage="default",
                        expected_revision=saved["revision"],
                        request_id=str(uuid.uuid4()),
                        confirm_cost=True,
                    )
                )
                receipt["probe"] = safe_result(result)
                receipt["code"] = "passed" if result["ok"] else "probe_failed"
    except Exception:
        # Never print exception text, settings, response bodies, model IDs or URLs.
        receipt["code"] = "acceptance_internal_failure"
    finally:
        bounded.inner.close()
        receipt.update(
            inference_requests=bounded.counts["inference"],
            catalog_requests=bounded.counts["catalog"],
        )
    return receipt


def main():
    logging.disable(logging.CRITICAL)
    result = acceptance(
        {key: os.environ.get(key, "") for key in ("BASE_URL", "API_KEY", "MODE")}, discover=True
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["code"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
````
