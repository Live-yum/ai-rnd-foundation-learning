# workbench/models/discovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.models.diagnostics`、`workbench.models.settings`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_representations`（L27–L43）：接收`value`。 源码说明：Inspect literal and successively decoded text, never only the last form. Keeping intermediate forms matters when a credential itself contains an escape sequence. These decoders shorten changed input, 。 控制顺序：L35在`True`成立时循环；L37遍历`(html.unescape, unquote)`；L39按`decoded != value`分支；L42按`value == previous`分支。 调用`decode`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_short_symbol`（L46–L49）：接收`secret`。 调用`len`、`secret.isascii`、`secret.isalnum`。 返回路径：L49的`0 < len(secret) < 8 and secret.isascii() and secret.isalnum()`。
- `_credential_token`（L52–L61）：接收`value`、`secret`。 控制顺序：L54在`start >= 0`成立时循环；L56按`(start == 0 or not value[start - 1].isalnum()) and ( end == len(value) or not value[e…`分支。 调用`value.find`、`len`、`value[start - 1].isalnum`、`value[end].isalnum`。 返回路径：L59的`True`；L61的`False`。
- `_contains_credential`（L64–L90）：接收`value`、`secrets`、`hostname`。 源码说明：Conservative disclosure screening, not proof of arbitrary echo absence. A short symbol inside a word cannot be distinguished from a coincidence (key 'api', model 'rapid'). The narrow lexical exception。 控制顺序：L71遍历`_representations(value)`；L72遍历`secrets`；L73按`not secret`分支；L75按`not _short_symbol(secret)`分支；L76按`secret in representation`分支；L84按`any( not (hostname and representation == value and part == secret) and _credential_to…`分支。 调用`_representations`、`_short_symbol`、`representation.split`、`any`、`_credential_token`。 返回路径：L77的`True`；L89的`True`；L90的`False`。
- `_endpoint_contains_credential`（L93–L104）：接收`endpoint`、`secrets`。 控制顺序：L96按`_contains_credential(endpoint, [key for key in secrets if not _short_symbol(key)])`分支。 调用`_contains_credential`、`_short_symbol`、`urlsplit`、`parsed.netloc.rsplit`。 返回路径：L97的`True`；L102的`_contains_credential(authority, short, hostname=True) or _contains_credential( parsed.path…`。
- `ModelDiscoveryRequest`（L107–L113）：继承`BaseModel`。声明的数据项为`stage`、`expected_revision`、`profile`；类型约束/数据库列参数以完整定义为准。
- `DiscoveryInputError`（L116–L117）：继承`ModelSettingsError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DiscoveryResponseError`（L120–L122）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DiscoveryResponseError.__init__`（L121–L122）：接收`code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_safe_catalog_trace`（L125–L148）：接收`event`、`info`。 源码说明：Sanitize only this request's protocol diagnostics before httpcore logs. httpcore invokes the request-local trace extension before formatting DEBUG records. Completion/failure info is a separate diagno。 控制顺序：L135按`event.endswith(".complete")`分支；L138按`event.endswith("receive_response_headers.complete") and isinstance(result, tuple) and…`分支；L145按`event.endswith(".failed")`分支。 调用`event.endswith`、`info.get`、`info.clear`、`isinstance`、`len`、`type`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_CatalogTransport`（L151–L174）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `_CatalogTransport.__init__`（L152–L153）：接收`transport`。 调用`httpx.HTTPTransport`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_CatalogTransport.handle_request`（L155–L171）：接收`request`。 控制顺序：L163按`response.extensions.get("http_version") not in { None, b"HTTP/1.0", b"HTTP/1.1", b"HT…`分支。 调用`self.transport.handle_request`、`response.extensions.pop`、`response.extensions.get`。 返回路径：L171的`response`。
- `_CatalogTransport.close`（L173–L174）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.transport.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_model_ids`（L177–L225）：接收`response`、`deadline`、`secrets`。 控制顺序：L180按`response.headers.get("content-encoding", "identity").strip().lower() != "identity"`分支；L181抛异常，停止当前正常路径；L183按`length is not None`分支；L185按`not length.isascii() or not length.isdigit()`分支；L186抛异常，停止当前正常路径；L189抛异常，停止当前正常路径；L190按`size > MAX_DISCOVERY_BYTES`分支；L191抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`response.headers.get("content-encoding", "identity").strip().lowe…`、`response.headers.get("content-encoding", "identity").strip`、`response.headers.get`、`DiscoveryResponseError`、`length.isascii`、`length.isdigit`、`int`、`response.iter_bytes`、`time.monotonic`等。 返回路径：L225的`models`。
- `ModelDiscoverer`（L228–L363）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ModelDiscoverer.__init__`（L229–L231）：接收`settings`、`transport`。 调用`ModelSettingsRepository`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ModelDiscoverer.discover`（L233–L363）：接收`command`。 控制顺序：L235按`before.revision != command.expected_revision`分支；L236抛异常，停止当前正常路径；L238按`command.profile is not None`分支；L247抛异常，停止当前正常路径；L274按`not key`分支；L275抛异常，停止当前正常路径；L280遍历`(before, configuration)`；L286按`_endpoint_contains_credential(endpoint, secrets)`分支。后续分支沿下方源码相同行号继续阅读。 调用`self.repository.snapshot`、`RevisionConflict`、`self.repository._merge`、`DiscoveryInputError`、`str`、`configuration.profile`、`validate_model_url`、`profile.api_key.get_secret_value`、`finish`等。 返回路径：L277的`finish("invalid_configuration", "请先填写该连接的 API 根地址和专用 API Key")`；L287的`finish("invalid_configuration", "API 根地址中不能包含 API Key")`；L337的`finish(code, message, http_status=response.status_code)`。
- `ModelDiscoverer.discover.finish`（L258–L261）：接收`code`、`message`、`**extra`。 返回路径：L261的`{**result, "code": code, "message": message, **extra}`。

</details>

**创建路径：** `workbench/models/discovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L363。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15526`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/models/discovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "740d58c801ee249194efe7e042551a6d7579ba6ab34a4e2de83067260612ad0a"} -->
````python
# workbench/models/discovery.py
"""Explicit, read-only model catalog lookup using a saved or unsaved profile.

Only GET /models is sent. Drafts never enter credential storage, and use the same
destination/key binding checks as saved configuration. No inference or retries.
"""

import html
import json
import time
import unicodedata
from typing import Any, Literal
from urllib.parse import unquote, urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from workbench.models.diagnostics import transport_failure
from workbench.models.settings import ModelSettingsError, ModelSettingsRepository, RevisionConflict
from workbench.settings import validate_model_url

DISCOVERY_TIMEOUT_SECONDS = 20
MAX_DISCOVERY_BYTES = 1024 * 1024
MAX_DISCOVERY_MODELS = 1000
MAX_MODEL_ID_LENGTH = 256


def _representations(value):
    """Inspect literal and successively decoded text, never only the last form.

    Keeping intermediate forms matters when a credential itself contains an
    escape sequence. These decoders shorten changed input, bounding the loop by
    the already limited URL/model length. JSON escapes are decoded by json.loads.
    """
    yield value
    while True:
        previous = value
        for decode in (html.unescape, unquote):
            decoded = decode(value)
            if decoded != value:
                yield decoded
                value = decoded
        if value == previous:
            return


def _short_symbol(secret):
    # This is a narrow lexical exception, not a minimum credential length or an
    # entropy claim. Longer or punctuation-bearing keys retain substring checks.
    return 0 < len(secret) < 8 and secret.isascii() and secret.isalnum()


def _credential_token(value, secret):
    start = value.find(secret)
    while start >= 0:
        end = start + len(secret)
        if (start == 0 or not value[start - 1].isalnum()) and (
            end == len(value) or not value[end].isalnum()
        ):
            return True
        start = value.find(secret, start + 1)
    return False


def _contains_credential(value, secrets, *, hostname=False):
    """Conservative disclosure screening, not proof of arbitrary echo absence.

    A short symbol inside a word cannot be distinguished from a coincidence
    (key 'api', model 'rapid'). The narrow lexical exception permits that case;
    exact/delimited echoes remain blocked even when they might be legitimate IDs.
    """
    for representation in _representations(value):
        for secret in secrets:
            if not secret:
                continue
            if not _short_symbol(secret):
                if secret in representation:
                    return True
                continue
            # A short key can coincide with a public destination label such as
            # api.example. Do not treat that label (or 'api' inside 'rapid') as
            # evidence of credential embedding. A decorated echo-api label is
            # still rejected, as are exact/delimited keys in paths/model IDs.
            parts = representation.split(".") if hostname else (representation,)
            if any(
                not (hostname and representation == value and part == secret)
                and _credential_token(part, secret)
                for part in parts
            ):
                return True
    return False


def _endpoint_contains_credential(endpoint, secrets):
    # Long/structured credentials remain forbidden anywhere, including authority
    # and encoded forms. Short symbols use URL syntax rather than raw substring.
    if _contains_credential(endpoint, [key for key in secrets if not _short_symbol(key)]):
        return True
    parsed = urlsplit(endpoint)
    short = [key for key in secrets if _short_symbol(key)]
    # Preserve case: urlsplit.hostname lowercases DNS names while keys do not.
    authority = parsed.netloc.rsplit(":", 1)[0] if parsed.port else parsed.netloc
    return _contains_credential(authority, short, hostname=True) or _contains_credential(
        parsed.path, short
    )


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
            or _contains_credential(model, secrets)
        ):
            # Never offer a redacted/modified ID as a usable model. A provider
            # containing a screened saved/draft credential makes it invalid.
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
        if _endpoint_contains_credential(endpoint, secrets):
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
````
