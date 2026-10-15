"""Explicit, read-only model catalog lookup using a saved or unsaved profile.

Only GET /models is sent. Drafts never enter credential storage, and use the same
destination/key binding checks as saved configuration. No inference or retries.
"""

import json
import time
import unicodedata
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from workbench.model_diagnostics import transport_failure
from workbench.model_settings import ModelSettingsError, ModelSettingsRepository, RevisionConflict
from workbench.settings import validate_model_url

DISCOVERY_TIMEOUT_SECONDS = 20
MAX_DISCOVERY_BYTES = 1024 * 1024
MAX_DISCOVERY_MODELS = 1000
MAX_MODEL_ID_LENGTH = 256


class ModelDiscoveryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    stage: Literal["default", "requirements", "planning", "coding", "review"]
    expected_revision: str = Field(min_length=1, max_length=64)
    # Keep draft credentials out of object representations. The repository merge
    # validates all fields/types with the operator's existing transport policy.
    profile: dict[str, Any] | None = Field(default=None, repr=False)


class DiscoveryInputError(ModelSettingsError):
    pass


class DiscoveryResponseError(ValueError):
    def __init__(self, code="invalid_response"):
        self.code = code


def _safe_catalog_trace(event, info):
    """Sanitize only this request's protocol diagnostics before httpcore logs.

    httpcore invokes the request-local trace extension before formatting DEBUG
    records. Completion/failure info is a separate diagnostics dictionary, so
    replacing its values cannot change response parsing or transport behavior.
    Never mutate started-event kwargs: those may also drive the operation.
    Keep event names, HTTP status and exception types useful for diagnosis,
    without retaining hostile reason phrases, headers or exception messages.
    """
    if event.endswith(".complete"):
        result = info.get("return_value")
        info.clear()
        if (
            event.endswith("receive_response_headers.complete")
            and isinstance(result, tuple)
            and len(result) >= 2
            and type(result[1]) is int
        ):
            info["http_status"] = result[1]
    elif event.endswith(".failed"):
        exception = info.get("exception")
        info.clear()
        info["error_type"] = type(exception).__name__


class _CatalogTransport(httpx.BaseTransport):
    def __init__(self, transport=None):
        self.transport = transport or httpx.HTTPTransport(verify=True, trust_env=False, retries=0)

    def handle_request(self, request):
        # A request-local callback avoids changing global logger levels/filters
        # and cannot suppress another thread's unrelated HTTP diagnostics.
        request.extensions["trace"] = _safe_catalog_trace
        response = self.transport.handle_request(request)
        # HTTPX logs these protocol fields at INFO. A hostile upstream can echo
        # Authorization in a custom reason phrase, so discard it before logging.
        response.extensions.pop("reason_phrase", None)
        if response.extensions.get("http_version") not in {
            None,
            b"HTTP/1.0",
            b"HTTP/1.1",
            b"HTTP/2",
            b"HTTP/3",
        }:
            response.extensions.pop("http_version", None)
        return response

    def close(self):
        self.transport.close()


def _model_ids(response, *, deadline, secrets):
    # Reject compression rather than allowing an encoded response to expand
    # beyond the byte budget before the HTTP client's decoder can be checked.
    if response.headers.get("content-encoding", "identity").strip().lower() != "identity":
        raise DiscoveryResponseError()
    length = response.headers.get("content-length")
    if length is not None:
        try:
            if not length.isascii() or not length.isdigit():
                raise ValueError
            size = int(length)
        except ValueError:
            raise DiscoveryResponseError() from None
        if size > MAX_DISCOVERY_BYTES:
            raise DiscoveryResponseError("response_too_large")
    chunks, size = [], 0
    for chunk in response.iter_bytes():
        if time.monotonic() > deadline:
            raise httpx.ReadTimeout("Model discovery deadline exceeded")
        size += len(chunk)
        if size > MAX_DISCOVERY_BYTES:
            raise DiscoveryResponseError("response_too_large")
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks))
    except ValueError, UnicodeDecodeError, RecursionError:
        raise DiscoveryResponseError() from None
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise DiscoveryResponseError()
    if len(payload["data"]) > MAX_DISCOVERY_MODELS:
        raise DiscoveryResponseError("response_too_large")
    models, seen = [], set()
    for row in payload["data"]:
        model = row.get("id") if isinstance(row, dict) else None
        if (
            not isinstance(model, str)
            or not model
            or len(model) > MAX_MODEL_ID_LENGTH
            or model != model.strip()
            or any(unicodedata.category(char).startswith("C") for char in model)
            or any(secret in model for secret in secrets)
        ):
            # Never offer a redacted/modified ID as a usable model. A provider
            # echoing any saved or draft secret makes its catalog invalid.
            raise DiscoveryResponseError()
        if model not in seen:
            models.append(model)
            seen.add(model)
    return models


class ModelDiscoverer:
    def __init__(self, settings, transport=None):
        self.settings, self.transport = settings, transport
        self.repository = ModelSettingsRepository(settings)

    def discover(self, command: ModelDiscoveryRequest):
        before = self.repository.snapshot()
        if before.revision != command.expected_revision:
            raise RevisionConflict("配置已被其他窗口修改；请重新加载后再获取模型")
        configuration = before
        if command.profile is not None:
            patch = (
                {"default": command.profile}
                if command.stage == "default"
                else {"stages": {command.stage: command.profile}}
            )
            try:
                configuration = self.repository._merge(before, patch)
            except ModelSettingsError as exc:
                raise DiscoveryInputError(str(exc)) from None

        result = {
            "ok": False,
            "stage": command.stage,
            "revision": before.revision,
            "scope": "model_discovery",
            "models": [],
            "attempts": 0,
        }

        def finish(code, message, **extra):
            # Neither endpoint, request draft, provider metadata/body nor an
            # exception string is ever included in this response.
            return {**result, "code": code, "message": message, **extra}

        try:
            profile = (
                configuration.default
                if command.stage == "default"
                else configuration.profile(command.stage)
            )
            endpoint = validate_model_url(
                profile.base_url,
                allow_insecure_http=self.settings.allow_insecure_model_http,
            )
            key = profile.api_key.get_secret_value()
            if not key:
                raise ValueError
        except ValueError:
            return finish("invalid_configuration", "请先填写该连接的 API 根地址和专用 API Key")

        secrets = set(self.settings.redaction_secrets())
        for snapshot in (before, configuration):
            secrets.update(
                profile.api_key.get_secret_value()
                for profile in (snapshot.default, *snapshot.stages.values())
                if profile.api_key.get_secret_value()
            )
        if any(secret in endpoint for secret in secrets):
            return finish("invalid_configuration", "API 根地址中不能包含 API Key")
        timeout = min(self.settings.llm_timeout, DISCOVERY_TIMEOUT_SECONDS)
        try:
            # TLS validation remains enabled, including local HTTPS endpoints.
            # Redirects, environment proxies and transport retries are disabled.
            with httpx.Client(
                timeout=timeout,
                transport=_CatalogTransport(self.transport),
                verify=True,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                result["attempts"] = 1
                deadline = time.monotonic() + timeout
                with client.stream(
                    "GET",
                    endpoint + "/models",
                    headers={
                        "authorization": "Bearer " + key,
                        "accept": "application/json",
                        "accept-encoding": "identity",
                    },
                ) as response:
                    if response.status_code != 200:
                        code, message = {
                            401: (
                                "authentication_failed",
                                "服务拒绝身份验证；请检查该地址的 API Key",
                            ),
                            403: (
                                "permission_denied",
                                "服务拒绝读取模型列表；请检查访问策略和权限",
                            ),
                            404: (
                                "discovery_unsupported",
                                "服务未提供模型列表接口；可手动填写模型 ID",
                            ),
                            405: (
                                "discovery_unsupported",
                                "服务未提供模型列表接口；可手动填写模型 ID",
                            ),
                            408: ("timeout", "获取模型列表超时；可稍后手动重试"),
                            429: ("rate_limited", "服务限流或额度不足；可稍后手动重试"),
                        }.get(
                            response.status_code,
                            (
                                "http_error",
                                "服务未返回可用模型列表；请检查服务状态或手动填写模型 ID",
                            ),
                        )
                        return finish(code, message, http_status=response.status_code)
                    models = _model_ids(response, deadline=deadline, secrets=secrets)
            return finish(
                "models_discovered",
                "已获取模型 ID；列表不代表模型权限或推理兼容性已验证"
                if models
                else "服务返回的模型列表为空；可手动填写模型 ID",
                ok=True,
                models=models,
            )
        except DiscoveryResponseError as exc:
            return finish(
                exc.code,
                "模型列表超过安全大小限制；请手动填写模型 ID"
                if exc.code == "response_too_large"
                else "服务返回的模型列表格式无效；可手动填写模型 ID",
            )
        except httpx.HTTPError as exc:
            if diagnostic := transport_failure(exc):
                return finish(*diagnostic)
            if isinstance(exc, httpx.TimeoutException):
                return finish("timeout", "获取模型列表超时；可稍后手动重试")
            if isinstance(exc, httpx.ConnectError):
                return finish("connection_failed", "无法连接模型服务；请检查地址、网络和 TLS 证书")
            return finish("transport_error", "获取模型列表时连接中断；可稍后手动重试")
        except Exception:
            return finish("internal_error", "模型列表获取未完成；可手动填写模型 ID")
