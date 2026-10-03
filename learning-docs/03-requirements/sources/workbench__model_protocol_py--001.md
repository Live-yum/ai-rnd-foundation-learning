# workbench/model_protocol.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**带着一个具体问题阅读：** 服务商原生结构化输出只是传输能力：协议层必须仍检查返回内容大小、JSON结构和本地schema。一个供应商声称strict并不能代替本地验证；不支持的响应形状应给出可脱敏诊断，而不是扫描任意文本直到拼出看似合格的对象。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `stream_wire_limit`（L19–L24）：接收`max_output_tokens`。 源码说明：SSE repeats metadata per token; bound framing separately from model text.。 调用`type`、`min`。 返回路径：L24的`min(MAX_STREAM_WIRE_BYTES, MAX_MODEL_CONTENT_BYTES + tokens * 1024)`。
- `OutputContract`（L28–L41）：继承`object`。声明的数据项为`provider`、`mode`、`reason`、`request_fields`；类型约束/数据库列参数以完整定义为准。
- `OutputContract.receipt`（L34–L41）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L35的`{ "provider": self.provider, "output_mode": self.mode, "format_reason": self.reason, "cont…`。
- `output_contract`（L44–L61）：接收`profile`、`schema`。 源码说明：Choose the integration, not model capabilities or a hand-built API schema.。 控制顺序：L47按`provider == "auto"`分支；L51按`profile.output_mode not in {"auto", "json_object"}`分支；L52抛异常，停止当前正常路径。 调用`{"api.deepseek.com": "deepseek", "api.openai.com": "openai"}.get`、`urlsplit`、`ValueError`、`OutputContract`。 返回路径：L53的`OutputContract( provider, "json_object", "langchain_json_mode", { "max_output_tokens": pro…`。
- `structured_model`（L65–L102）：接收`profile`、`schema`、`contract`、`http_client`、`streaming`。 源码说明：The official LangChain integration owns wire formatting and schema parsing. LangGraph nodes call this same Runnable for all four schema-driven stages. JSON mode preserves open dictionaries; local stri。 调用`httpx.AsyncClient`、`SyncOnlyTransport`、`model_class`、`model.with_structured_output`、`asyncio.get_running_loop`、`asyncio.run`、`async_client.aclose`、`ThreadPoolExecutor`、`executor.submit(asyncio.run, async_client.aclose()).result`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `SyncOnlyTransport`（L105–L107）：继承`httpx.AsyncBaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SyncOnlyTransport.handle_async_request`（L106–L107）：接收`request`。 控制顺序：L107抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedTransport`（L110–L213）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AuditedTransport.__init__`（L113–L123）：接收`contract`、`inner`、`observer`、`streaming`。 调用`httpx.HTTPTransport`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedTransport.handle_request`（L125–L209）：接收`request`。 控制顺序：L132抛异常，停止当前正常路径；L133按`200 <= response.status_code < 300 and response.headers.get("content-type", "").split(…`分支；L138按`self.observer`分支；L151遍历`response.iter_bytes()`；L153按`len(data) > MAX_MODEL_CONTENT_BYTES`分支；L154抛异常，停止当前正常路径；L155按`200 <= response.status_code < 300`分支；L159按`self.observer`分支。后续分支沿下方源码相同行号继续阅读。 调用`self.inner.handle_request`、`response.headers.get("content-type", "").split(";", 1)[0].strip()…`、`response.headers.get("content-type", "").split(";", 1)[0].strip`、`response.headers.get("content-type", "").split`、`response.headers.get`、`self.observer.mode`、`httpx.Response`、`response.headers.items`、`k.lower`等。 返回路径：L140的`httpx.Response( response.status_code, headers={ k: v for k, v in response.headers.items() …`；L209的`httpx.Response(response.status_code, headers=headers, content=bytes(data))`。
- `AuditedTransport.close`（L211–L213）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L212按`self.owned`分支。 调用`self.inner.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedEventStream`（L216–L363）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AuditedEventStream.__init__`（L219–L228）：接收`response`、`audit`。 调用`stream_wire_limit`、`audit.contract.request_fields.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedEventStream.__iter__`（L230–L260）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L234遍历`self.lines()`；L235按`line == ""`分支；L236按`not data`分支；L241按`len(payload.encode("utf-8")) > MAX_MODEL_CONTENT_BYTES`分支；L242抛异常，停止当前正常路径；L245按`self.done`分支；L247按`line.startswith("data:")`分支；L251按`data_bytes > MAX_MODEL_CONTENT_BYTES`分支。后续分支沿下方源码相同行号继续阅读。 调用`self.lines`、`"\n".join`、`len`、`payload.encode`、`OutputFailure`、`self.frame`、`("data: " + payload + "\n\n").encode`、`line.startswith`、`line[5:].removeprefix`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `AuditedEventStream.lines`（L262–L288）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L265遍历`self.response.iter_bytes()`；L267按`self.bytes_read > self.wire_limit`分支；L268抛异常，停止当前正常路径；L270在`True`成立时循环；L272按`not boundaries`分支；L275按`len(buffer[:index].encode("utf-8")) > MAX_MODEL_CONTENT_BYTES`分支；L276抛异常，停止当前正常路径；L277按`buffer[index] == "\r" and index == len(buffer) - 1`分支。后续分支沿下方源码相同行号继续阅读。 调用`codecs.getincrementaldecoder("utf-8")`、`codecs.getincrementaldecoder`、`self.response.iter_bytes`、`len`、`OutputFailure`、`decoder.decode`、`buffer.find`、`min`、`buffer[:index].encode`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `AuditedEventStream.frame`（L290–L359）：接收`payload`。 控制顺序：L291按`payload == "[DONE]"`分支；L305按`self.finish != "stop"`分支；L306抛异常，停止当前正常路径；L310按`not isinstance(value, dict) or value.get("error")`分支；L311抛异常，停止当前正常路径；L314按`choices == [] and isinstance(value.get("usage"), dict)`分支；L317按`not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict…`分支；L318抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`completion_content`、`"".join`、`OutputFailure`、`load_json`、`isinstance`、`value.get`、`len`、`choice.get`、`delta.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedEventStream.close`（L362–L363）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.response.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `OutputFailure`（L366–L371）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `OutputFailure.__init__`（L369–L371）：接收`code`、`message`、`retry`、`repair`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_json`（L374–L400）：接收`text`。 控制顺序：L400抛异常，停止当前正常路径。 调用`json.loads`、`ValueError`。 返回路径：L393的`json.loads( text, object_pairs_hook=unique_pairs, parse_constant=invalid_constant, parse_f…`。
- `load_json.unique_pairs`（L375–L381）：接收`pairs`。 控制顺序：L377遍历`pairs`；L378按`key in result`分支；L379抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L381的`result`。
- `load_json.invalid_constant`（L383–L384）：接收`_`。 控制顺序：L384抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_json.finite_float`（L386–L390）：接收`value`。 控制顺序：L388按`not math.isfinite(result)`分支；L389抛异常，停止当前正常路径。 调用`float`、`math.isfinite`、`ValueError`。 返回路径：L390的`result`。
- `completion_content`（L403–L448）：接收`envelope`、`contract`。 控制顺序：L404按`not isinstance(envelope, dict) or envelope.get("error")`分支；L405抛异常，停止当前正常路径；L407按`not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict…`分支；L408抛异常，停止当前正常路径；L411按`not isinstance(message, dict) or message.get("role", "assistant") != "assistant"`分支；L412抛异常，停止当前正常路径；L413按`message.get("refusal") is not None`分支；L414按`message["refusal"] != ""`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`envelope.get`、`OutputFailure`、`len`、`choice.get`、`message.get`、`content.strip`、`usage.items`、`type`。 返回路径：L448的`content, safe_usage, finish or "unknown"`。
- `validate_content`（L451–L458）：接收`content`、`schema`、`mode`。 控制顺序：L452按`mode != "json_object"`分支；L453抛异常，停止当前正常路径；L456按`not isinstance(value, dict)`分支；L457抛异常，停止当前正常路径。 调用`ValueError`、`load_json`、`isinstance`、`schema.model_validate_json`。 返回路径：L458的`schema.model_validate_json(content, strict=True)`。

</details>

**创建路径：** `workbench/model_protocol.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L458。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19503`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_protocol.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d49c15e6b26515c5a45e0b69a4cdc2fa7d9b5cba58751d228164b01b91e496c9"} -->
````python
# workbench/model_protocol.py
"""LangChain structured-output integration and provider-independent validation guards."""

import asyncio
import codecs
import json
import math
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

CONTRACT_VERSION = 2
MAX_MODEL_CONTENT_BYTES = 2_000_000
MAX_STREAM_WIRE_BYTES = 64_000_000


def stream_wire_limit(max_output_tokens):
    """SSE repeats metadata per token; bound framing separately from model text."""
    tokens = (
        max_output_tokens if type(max_output_tokens) is int and max_output_tokens > 0 else 16384
    )
    return min(MAX_STREAM_WIRE_BYTES, MAX_MODEL_CONTENT_BYTES + tokens * 1024)


@dataclass(frozen=True)
class OutputContract:
    provider: str
    mode: str
    reason: str
    request_fields: dict

    def receipt(self):
        return {
            "provider": self.provider,
            "output_mode": self.mode,
            "format_reason": self.reason,
            "contract_version": CONTRACT_VERSION,
            "structured_output": "langchain.with_structured_output",
        }


def output_contract(profile, schema):
    """Choose the integration, not model capabilities or a hand-built API schema."""
    provider = profile.provider
    if provider == "auto":
        provider = {"api.deepseek.com": "deepseek", "api.openai.com": "openai"}.get(
            urlsplit(profile.base_url).hostname, "compatible"
        )
    if profile.output_mode not in {"auto", "json_object"}:
        raise ValueError("当前统一结构化链使用 JSON mode；OUTPUT_MODE 应为 auto/json_object")
    return OutputContract(
        provider,
        "json_object",
        "langchain_json_mode",
        {
            "max_output_tokens": profile.max_output_tokens
            or (65536 if provider == "deepseek" else 16384)
        },
    )


@contextmanager
def structured_model(profile, schema, contract, http_client, *, streaming=False):
    """The official LangChain integration owns wire formatting and schema parsing.

    LangGraph nodes call this same Runnable for all four schema-driven stages.
    JSON mode preserves open dictionaries; local strict validation remains mandatory.
    """
    from langchain_deepseek import ChatDeepSeek
    from langchain_openai import ChatOpenAI

    # Integrations eagerly construct both SDK clients. Inject a network-disabled
    # async client too, and close it even when construction or invocation fails.
    async_client = httpx.AsyncClient(transport=SyncOnlyTransport(), trust_env=False)
    try:
        model_class = ChatDeepSeek if contract.provider == "deepseek" else ChatOpenAI
        model = model_class(
            model=profile.model,
            api_key=profile.api_key,
            base_url=profile.base_url,
            http_client=http_client,
            timeout=http_client.timeout,
            http_async_client=async_client,
            max_retries=0,
            streaming=streaming,
            use_responses_api=False,
            http_socket_options=(),
            cache=False,
            max_tokens=contract.request_fields["max_output_tokens"],
        )
        yield model.with_structured_output(schema, method="json_mode", include_raw=True)
    finally:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(async_client.aclose())
        else:
            # A synchronous node can also be called inside an existing event loop.
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(asyncio.run, async_client.aclose()).result()


class SyncOnlyTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request):
        raise RuntimeError("ModelGateway only permits its audited synchronous transport")


class AuditedTransport(httpx.BaseTransport):
    """Bound bytes and check response status before SDK/parser normalization loses evidence."""

    def __init__(self, contract, inner=None, *, observer=None, streaming=False):
        self.contract = contract
        self.owned = inner is None
        self.inner = inner if inner is not None else httpx.HTTPTransport(retries=0, trust_env=False)
        self.error = None
        self.content = None
        self.usage = {}
        self.finish = "unknown"
        self.observer = observer
        self.streaming = streaming
        self.stream_unsupported = False

    def handle_request(self, request):
        try:
            response = self.inner.handle_request(request)
        except OutputFailure as exc:
            # Preserve a trusted transport guard through SDK exception wrapping.
            # It must remain non-retryable and retain its static diagnostic code.
            self.error = exc
            raise
        if (
            200 <= response.status_code < 300
            and response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            == "text/event-stream"
        ):
            if self.observer:
                self.observer.mode("streaming")
            return httpx.Response(
                response.status_code,
                headers={
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() not in {"content-encoding", "content-length"}
                },
                stream=AuditedEventStream(response, self),
            )
        data = bytearray()
        try:
            for chunk in response.iter_bytes():
                data.extend(chunk)
                if len(data) > MAX_MODEL_CONTENT_BYTES:
                    raise OutputFailure("response_too_large", "模型响应过大")
            if 200 <= response.status_code < 300:
                self.content, self.usage, self.finish = completion_content(
                    load_json(data), self.contract
                )
                if self.observer:
                    self.observer.mode("non_streaming")
            elif response.status_code in {400, 422}:
                # Only explicit capability errors authorize a non-streaming retry.
                # Never expose or heuristically display raw provider error messages.
                try:
                    error = load_json(data).get("error", {})
                    self.stream_unsupported = isinstance(error, dict) and (
                        error.get("code")
                        in {"unsupported_stream", "stream_not_supported", "unsupported_streaming"}
                        or (
                            error.get("param") == "stream"
                            and error.get("code") == "unsupported_value"
                        )
                    )
                except ValueError, TypeError, AttributeError:
                    pass
        except (ValueError, TypeError) as exc:
            self.error = exc
            raise
        finally:
            response.close()
        headers = dict(response.headers)
        headers.pop("content-encoding", None)
        headers.pop("content-length", None)
        if self.streaming and 200 <= response.status_code < 300:
            # Some compatible endpoints ignore stream=true and return one JSON
            # completion. Adapt that single genuine result for the SDK; the UI
            # receives no pretend deltas and explicitly reports non_streaming.
            item = {
                "id": "completed-response",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "",
                "usage": self.usage,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": self.content,
                        },
                        "finish_reason": "stop",
                    }
                ],
            }
            data = (
                "data: " + json.dumps(item, ensure_ascii=False) + "\n\ndata: [DONE]\n\n"
            ).encode()
            headers["content-type"] = "text/event-stream"
        return httpx.Response(response.status_code, headers=headers, content=bytes(data))

    def close(self):
        if self.owned:
            self.inner.close()


class AuditedEventStream(httpx.SyncByteStream):
    """Audit each provider SSE frame before it reaches the SDK or UI projection."""

    def __init__(self, response, audit):
        self.response, self.audit = response, audit
        self.content = []
        self.usage = {}
        self.finish = None
        self.done = False
        self.bytes_read = 0
        self.frames = 0
        self.content_bytes = 0
        self.wire_limit = stream_wire_limit(audit.contract.request_fields.get("max_output_tokens"))

    def __iter__(self):
        data = []
        data_bytes = 0
        try:
            for line in self.lines():
                if line == "":
                    if not data:
                        continue
                    payload = "\n".join(data)
                    data = []
                    data_bytes = 0
                    if len(payload.encode("utf-8")) > MAX_MODEL_CONTENT_BYTES:
                        raise OutputFailure("response_too_large", "模型流的单个消息过大")
                    self.frame(payload)
                    yield ("data: " + payload + "\n\n").encode("utf-8")
                    if self.done:
                        return
                elif line.startswith("data:"):
                    part = line[5:].removeprefix(" ")
                    data_bytes += len(part.encode("utf-8")) + bool(data)
                    data.append(part)
                    if data_bytes > MAX_MODEL_CONTENT_BYTES:
                        raise OutputFailure("response_too_large", "模型流的单个消息过大")
                # Comments and unknown SSE fields are intentionally ignored.
            if not self.done:
                raise OutputFailure("interrupted", "模型流在完整结束前断开", retry=True)
        except (ValueError, TypeError, httpx.HTTPError) as exc:
            self.audit.error = exc
            raise
        finally:
            self.response.close()

    def lines(self):
        decoder = codecs.getincrementaldecoder("utf-8")()
        buffer = ""
        for chunk in self.response.iter_bytes():
            self.bytes_read += len(chunk)
            if self.bytes_read > self.wire_limit:
                raise OutputFailure("stream_wire_limit", "模型流传输字节超过安全上限")
            buffer += decoder.decode(chunk)
            while True:
                boundaries = [p for p in (buffer.find("\r"), buffer.find("\n")) if p >= 0]
                if not boundaries:
                    break
                index = min(boundaries)
                if len(buffer[:index].encode("utf-8")) > MAX_MODEL_CONTENT_BYTES:
                    raise OutputFailure("response_too_large", "模型流的单行消息过大")
                if buffer[index] == "\r" and index == len(buffer) - 1:
                    break  # CRLF may be split between provider byte chunks.
                end = index + (2 if buffer[index : index + 2] == "\r\n" else 1)
                yield buffer[:index]
                buffer = buffer[end:]
            if len(buffer.encode("utf-8")) > MAX_MODEL_CONTENT_BYTES:
                raise OutputFailure("response_too_large", "模型响应过大：流中存在未结束消息")
        buffer += decoder.decode(b"", final=True)
        if buffer.endswith("\r"):
            yield buffer[:-1]
        elif buffer:
            yield buffer

    def frame(self, payload):
        if payload == "[DONE]":
            self.audit.content, self.audit.usage, self.audit.finish = completion_content(
                {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "".join(self.content)},
                            "finish_reason": self.finish,
                        }
                    ],
                    "usage": self.usage,
                },
                self.audit.contract,
            )
            # Streaming always requires affirmative completion, even compatible endpoints.
            if self.finish != "stop":
                raise OutputFailure("invalid_finish_reason", "模型流没有确认完整结束", retry=True)
            self.done = True
            return
        value = load_json(payload)
        if not isinstance(value, dict) or value.get("error"):
            raise OutputFailure("invalid_envelope", "模型服务返回无效响应信封", retry=True)
        self.frames += 1
        choices = value.get("choices")
        if choices == [] and isinstance(value.get("usage"), dict):
            self.usage = value["usage"]
            return
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise OutputFailure("invalid_choices", "模型响应缺少唯一选择", retry=True)
        choice = choices[0]
        delta = choice.get("delta")
        if choice.get("index", 0) != 0 or not isinstance(delta, dict):
            raise OutputFailure("invalid_message", "模型流消息结构无效", retry=True)
        if delta.get("role", "assistant") != "assistant":
            raise OutputFailure("invalid_message", "模型流消息角色无效", retry=True)
        if delta.get("refusal") not in (None, ""):
            raise OutputFailure("refusal", "模型拒绝本次请求；未尝试绕过拒绝")
        if delta.get("tool_calls") or delta.get("function_call"):
            raise OutputFailure("unexpected_tool_call", "本阶段不接受模型工具调用")
        finish = choice.get("finish_reason")
        if finish is not None:
            # Reuse the nonstream guards before making any content visible.
            completion_content(
                {"choices": [{"message": {"content": "{}"}, "finish_reason": finish}]},
                self.audit.contract,
            )
            if self.finish is not None:
                raise OutputFailure("invalid_finish_reason", "模型流重复结束", retry=True)
            self.finish = finish
        fragment = delta.get("content")
        if fragment is not None and not isinstance(fragment, str):
            raise OutputFailure("invalid_message", "模型流内容结构无效", retry=True)
        for key in ("reasoning_content", "reasoning"):
            if delta.get(key) is not None and not isinstance(delta[key], str):
                raise OutputFailure("invalid_message", "模型流推理字段结构无效")
        self.content_bytes += sum(
            len(delta[key].encode("utf-8"))
            for key in ("content", "reasoning_content", "reasoning")
            if isinstance(delta.get(key), str)
        )
        if self.content_bytes > MAX_MODEL_CONTENT_BYTES:
            raise OutputFailure("response_too_large", "模型响应正文过大")
        if fragment:
            if self.finish is not None and finish is None:
                raise OutputFailure("invalid_finish_reason", "模型流结束后仍有内容", retry=True)
            self.content.append(fragment)
            if self.audit.observer:
                self.audit.observer.content(fragment)
        if isinstance(value.get("usage"), dict):
            self.usage = value["usage"]
        # reasoning_content, reasoning and other internal fields are never projected.

    def close(self):
        self.response.close()


class OutputFailure(ValueError):
    """Safe static diagnostic; never use provider text as an exception message."""

    def __init__(self, code, message, *, retry=False, repair=False):
        self.code, self.retry, self.repair = code, retry, repair
        super().__init__(message)


def load_json(text):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError("non_finite_json_number")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("non_finite_json_number")
        return result

    try:
        return json.loads(
            text,
            object_pairs_hook=unique_pairs,
            parse_constant=invalid_constant,
            parse_float=finite_float,
        )
    except RecursionError:
        raise ValueError("json_nesting_limit") from None


def completion_content(envelope, contract):
    if not isinstance(envelope, dict) or envelope.get("error"):
        raise OutputFailure("invalid_envelope", "模型服务返回无效响应信封", retry=True)
    choices = envelope.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        raise OutputFailure("invalid_choices", "模型响应缺少唯一选择", retry=True)
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict) or message.get("role", "assistant") != "assistant":
        raise OutputFailure("invalid_message", "模型响应消息结构无效", retry=True)
    if message.get("refusal") is not None:
        if message["refusal"] != "":
            raise OutputFailure("refusal", "模型拒绝本次请求；未尝试绕过拒绝")
    finish = choice.get("finish_reason")
    if finish == "length":
        raise OutputFailure(
            "truncated", "模型输出被截断；检查 MAX_OUTPUT_TOKENS 和上下文长度后重试"
        )
    if finish == "content_filter":
        raise OutputFailure("content_filter", "模型内容过滤阻止本次响应；未尝试绕过过滤")
    if finish in {"insufficient_system_resource", "aborted"}:
        raise OutputFailure("interrupted", "模型生成中断", retry=True)
    if (
        finish in {"tool_calls", "function_call"}
        or message.get("tool_calls")
        or message.get("function_call")
    ):
        raise OutputFailure("unexpected_tool_call", "本阶段不接受模型工具调用")
    # Legacy compatible endpoints sometimes omit this field. Reviewed providers cannot.
    if finish != "stop" and not (finish is None and contract.provider == "compatible"):
        raise OutputFailure("invalid_finish_reason", "模型响应没有确认完整结束", retry=True)
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise OutputFailure(
            "empty_content", "模型未返回可验证的 JSON 内容", retry=True, repair=True
        )
    usage = envelope.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    safe_usage = {
        k: v
        for k, v in usage.items()
        if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
        and type(v) is int
        and 0 <= v <= 100_000_000
    }
    return content, safe_usage, finish or "unknown"


def validate_content(content, schema, *, mode):
    if mode != "json_object":
        raise ValueError("unsupported_output_validation_mode")
    # Pydantic's JSON parser accepts duplicate keys/nonfinite numbers; reject them first.
    value = load_json(content)
    if not isinstance(value, dict):
        raise ValueError("response_must_be_json_object")
    return schema.model_validate_json(content, strict=True)
````
