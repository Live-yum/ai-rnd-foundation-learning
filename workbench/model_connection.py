"""One explicit, bounded connection probe against a saved immutable model profile.

Uses the production structured-output adapter, but never creates a run, sends user
content, retries automatically, or treats format validation as a successful call.
"""

import logging
import time
import uuid
from collections import OrderedDict
from threading import Lock
from typing import Literal

import httpx
from filelock import FileLock, Timeout
from openai import APIConnectionError, APIError, APITimeoutError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from workbench.model_protocol import (
    AuditedTransport,
    OutputFailure,
    output_contract,
    structured_model,
    validate_content,
)
from workbench.model_settings import ModelSettingsError, RevisionConflict
from workbench.settings import ModelProfile

TEST_MAX_TOKENS = 128
TEST_TIMEOUT_SECONDS = 20
logger = logging.getLogger(__name__)


class ConnectionTestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    stage: Literal["default", "requirements", "planning", "coding", "review"]
    expected_revision: str = Field(min_length=1, max_length=64)
    request_id: str = Field(min_length=36, max_length=36, pattern=r"^[a-f0-9-]{36}$")
    confirm_cost: Literal[True]


class ProbeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    ok: Literal[True]


class ConnectionTestBusy(ModelSettingsError):
    pass


class ModelConnectionTester:
    def __init__(self, settings, transport=None):
        self.settings, self.transport = settings, transport
        self._lock = Lock()
        self._results = OrderedDict()

    def test(self, command: ConnectionTestRequest):
        # A second click/tab cannot overlap a paid probe. The file lock also
        # covers independent API processes sharing the same settings directory.
        if not self._lock.acquire(blocking=False):
            raise ConnectionTestBusy("连接测试正在进行；请等待结果，不要重复发起")
        try:
            cached = self._results.get(command.request_id)
            fingerprint = (command.stage, command.expected_revision)
            if cached:
                if cached[0] != fingerprint:
                    raise RevisionConflict("测试请求标识已用于其他配置；请重新发起测试")
                return cached[1]
            self.settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            try:
                with FileLock(
                    str(self.settings.data_dir / "model-connection-test.lock"),
                    timeout=0,
                    mode=0o600,
                ):
                    configuration = self.settings.model_configuration()
                    if configuration.revision != command.expected_revision:
                        raise RevisionConflict("配置已被其他窗口修改；请重新加载后再测试")
                    result = self._probe(configuration, command.stage)
            except Timeout:
                raise ConnectionTestBusy("连接测试正在进行；请等待结果，不要重复发起") from None
            self._results[command.request_id] = (fingerprint, result)
            while len(self._results) > 64:
                self._results.popitem(last=False)
            return result
        finally:
            self._lock.release()

    def _probe(self, configuration, stage):
        started = time.monotonic()
        result = {
            "ok": False,
            "stage": stage,
            "revision": configuration.revision,
            "trace_id": uuid.uuid4().hex,
            "scope": "structured_connection_probe",
            "attempts": 0,
            "max_output_tokens": TEST_MAX_TOKENS,
            "timeout_seconds": min(self.settings.llm_timeout, TEST_TIMEOUT_SECONDS),
        }

        def finish(phase, code, message, retryable=False):
            receipt = self.settings.redact_data(
                {
                    **result,
                    "phase": phase,
                    "code": code,
                    "message": message,
                    "retryable": retryable,
                    "elapsed_ms": max(0, round((time.monotonic() - started) * 1000)),
                }
            )
            logger.info(
                "model_connection_test trace=%s stage=%s phase=%s code=%s attempts=%s",
                receipt["trace_id"],
                receipt["stage"],
                receipt["phase"],
                receipt["code"],
                receipt["attempts"],
            )
            return receipt

        try:
            if stage == "default":
                profile = ModelProfile(
                    stage="default",
                    **{
                        **configuration.default.model_dump(),
                        "provider": configuration.default.provider or "auto",
                        "output_mode": configuration.default.output_mode or "auto",
                    },
                )
            else:
                profile = configuration.profile(stage)
            profile.validate_endpoint()
            # Keep provider/URL/model/key/output mode from exactly one revision.
            # Only cap the test's output budget; do not modify saved settings.
            profile = profile.model_copy(
                update={
                    "max_output_tokens": min(
                        profile.max_output_tokens or TEST_MAX_TOKENS, TEST_MAX_TOKENS
                    )
                }
            )
            contract = output_contract(profile, ProbeResponse)
        except ValueError:
            return finish(
                "configuration",
                "invalid_configuration",
                "请先补全并保存该连接的地址、模型和专用密钥",
            )

        result.update(
            endpoint=profile.base_url,
            model=profile.model,
            max_output_tokens=profile.max_output_tokens,
            **contract.receipt(),
        )
        try:
            audited = AuditedTransport(contract, self.transport)
            with httpx.Client(
                timeout=result["timeout_seconds"],
                transport=audited,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                with structured_model(profile, ProbeResponse, contract, client) as structured:
                    result["attempts"] = 1
                    try:
                        response = structured.invoke(
                            [
                                {
                                    "role": "system",
                                    "content": 'Connection test. Return only the JSON object {"ok":true}.',
                                },
                                {"role": "user", "content": 'Return {"ok":true}.'},
                            ],
                            config={"callbacks": []},
                        )
                    except Exception:
                        if audited.error is not None:
                            raise audited.error from None
                        raise
            validate_content(audited.content, ProbeResponse, mode=contract.mode)
            if response.get("parsing_error") is not None or not isinstance(
                response.get("parsed"), ProbeResponse
            ):
                raise ValueError("invalid_probe_response")
            result.update(ok=True, usage=audited.usage)
            return finish(
                "completed",
                "connected",
                "连接成功，已收到并验证真实模型响应；本次测试不代表所有任务均可执行",
            )
        except OutputFailure as exc:
            if exc.code == "truncated":
                return finish(
                    "validation",
                    "truncated",
                    f"模型已响应，但超过本次测试的 {profile.max_output_tokens} token 输出上限，未完成校验；"
                    "推理模型可能需要更高测试预算，这不等于地址或密钥无效",
                )
            return finish("validation", exc.code, str(exc), exc.retry)
        except ValidationError, ValueError, TypeError, KeyError, IndexError:
            return finish(
                "validation",
                "invalid_response",
                "服务已响应，但内容未通过 JSON 结构校验；请检查输出协议与模型兼容性",
            )
        except (httpx.HTTPError, APIError) as exc:
            status = getattr(exc, "status_code", None) or getattr(
                getattr(exc, "response", None), "status_code", None
            )
            if status:
                result["http_status"] = status
                code, message, retryable = {
                    401: (
                        "authentication_failed",
                        "服务拒绝身份验证；请检查该地址的 API Key",
                        False,
                    ),
                    403: (
                        "permission_denied",
                        "该账号无权调用此模型；请检查模型权限和服务区域",
                        False,
                    ),
                    404: (
                        "model_or_endpoint_not_found",
                        "模型或接口不存在；请检查模型 ID 与 API 根地址",
                        False,
                    ),
                    408: ("timeout", "模型服务请求超时；可稍后手动重试", True),
                    429: ("rate_limited", "模型服务限流或额度不足；请检查配额后手动重试", True),
                }.get(
                    status,
                    (
                        "http_" + str(status),
                        "模型服务拒绝请求；请检查服务状态、模型与协议设置",
                        status >= 500,
                    ),
                )
                return finish("request", code, message, retryable)
            if isinstance(exc, (httpx.TimeoutException, APITimeoutError)):
                return finish("request", "timeout", "连接或模型响应超时；可稍后手动重试", True)
            if isinstance(exc, (httpx.ConnectError, APIConnectionError)):
                return finish(
                    "request",
                    "connection_failed",
                    "无法连接模型服务；请检查地址、网络和 TLS 证书",
                    True,
                )
            return finish("request", "transport_error", "模型连接中断；可检查网络后手动重试", True)
        except Exception:
            # Never surface SDK exception strings, response bodies or credentials.
            return finish("request", "internal_error", "连接测试未完成；请根据追踪编号排查服务日志")
