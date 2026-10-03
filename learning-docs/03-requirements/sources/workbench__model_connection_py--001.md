# workbench/model_connection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_protocol`、`workbench.model_settings`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ConnectionTestRequest`（L34–L39）：继承`BaseModel`。声明的数据项为`stage`、`expected_revision`、`request_id`、`confirm_cost`；类型约束/数据库列参数以完整定义为准。
- `ProbeResponse`（L42–L44）：继承`BaseModel`。声明的数据项为`ok`；类型约束/数据库列参数以完整定义为准。
- `ConnectionTestBusy`（L47–L48）：继承`ModelSettingsError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ModelConnectionTester`（L51–L255）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ModelConnectionTester.__init__`（L52–L55）：接收`settings`、`transport`。 调用`Lock`、`OrderedDict`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ModelConnectionTester.test`（L57–L87）：接收`command`。 控制顺序：L60按`not self._lock.acquire(blocking=False)`分支；L61抛异常，停止当前正常路径；L65按`cached`分支；L66按`cached[0] != fingerprint`分支；L67抛异常，停止当前正常路径；L77按`configuration.revision != command.expected_revision`分支；L78抛异常，停止当前正常路径；L81抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`self._lock.acquire`、`ConnectionTestBusy`、`self._results.get`、`RevisionConflict`、`self.settings.data_dir.mkdir`、`FileLock`、`str`、`self.settings.model_configuration`、`self._probe`等。 返回路径：L68的`cached[1]`；L85的`result`。
- `ModelConnectionTester._probe`（L89–L255）：接收`configuration`、`stage`。 控制顺序：L124按`stage == "default"`分支；L181按`audited.error is not None`分支；L182抛异常，停止当前正常路径；L183抛异常，停止当前正常路径；L185按`response.get("parsing_error") is not None or not isinstance( response.get("parsed"), …`分支；L188抛异常，停止当前正常路径；L196按`exc.code == "truncated"`分支；L214按`status`分支。后续分支沿下方源码相同行号继续阅读。 调用`time.monotonic`、`uuid.uuid4`、`min`、`ModelProfile`、`configuration.default.model_dump`、`configuration.profile`、`profile.validate_endpoint`、`profile.model_copy`、`output_contract`等。 返回路径：L147的`finish( "configuration", "invalid_configuration", "请先补全并保存该连接的地址、模型和专用密钥", )`；L190的`finish( "completed", "connected", "连接成功，已收到并验证真实模型响应；本次测试不代表所有任务均可执行", )`；L197的`finish( "validation", "truncated", f"模型已响应，但超过本次测试的 {profile.max_output_tokens} token 输出上限…`。
- `ModelConnectionTester._probe.finish`（L102–L121）：接收`phase`、`code`、`message`、`retryable`。 调用`self.settings.redact_data`、`max`、`round`、`time.monotonic`、`logger.info`。 返回路径：L121的`receipt`。

</details>

**创建路径：** `workbench/model_connection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L255。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11000`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_connection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2138576ed0b0a145b3c0c6943378c1bcb2561252ba913906dd17f9d2794c14e9"} -->
````python
# workbench/model_connection.py
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
````
