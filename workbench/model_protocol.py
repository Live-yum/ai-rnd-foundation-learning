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
        response = self.inner.handle_request(request)
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
                if len(data) > 2_000_000:
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

    def __iter__(self):
        data = []
        try:
            for line in self.lines():
                if line == "":
                    if not data:
                        continue
                    payload = "\n".join(data)
                    data = []
                    self.frame(payload)
                    yield ("data: " + payload + "\n\n").encode("utf-8")
                    if self.done:
                        return
                elif line.startswith("data:"):
                    data.append(line[5:].removeprefix(" "))
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
            if self.bytes_read > 2_000_000:
                raise OutputFailure("response_too_large", "模型响应过大")
            buffer += decoder.decode(chunk)
            while True:
                boundaries = [p for p in (buffer.find("\r"), buffer.find("\n")) if p >= 0]
                if not boundaries:
                    break
                index = min(boundaries)
                if buffer[index] == "\r" and index == len(buffer) - 1:
                    break  # CRLF may be split between provider byte chunks.
                end = index + (2 if buffer[index : index + 2] == "\r\n" else 1)
                yield buffer[:index]
                buffer = buffer[end:]
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
