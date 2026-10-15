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
