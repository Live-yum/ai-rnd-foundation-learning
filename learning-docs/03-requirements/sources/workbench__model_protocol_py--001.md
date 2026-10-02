# workbench/model_protocol.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**带着一个具体问题阅读：** 服务商原生结构化输出只是传输能力：协议层必须仍检查返回内容大小、JSON结构和本地schema。一个供应商声称strict并不能代替本地验证；不支持的响应形状应给出可脱敏诊断，而不是扫描任意文本直到拼出看似合格的对象。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `OutputContract`（L17–L30）：继承`object`。声明的数据项为`provider`、`mode`、`reason`、`request_fields`；类型约束/数据库列参数以完整定义为准。
- `OutputContract.receipt`（L23–L30）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L24的`{ "provider": self.provider, "output_mode": self.mode, "format_reason": self.reason, "cont…`。
- `output_contract`（L33–L50）：接收`profile`、`schema`。 源码说明：Choose the integration, not model capabilities or a hand-built API schema.。 控制顺序：L36按`provider == "auto"`分支；L40按`profile.output_mode not in {"auto", "json_object"}`分支；L41抛异常，停止当前正常路径。 调用`{"api.deepseek.com": "deepseek", "api.openai.com": "openai"}.get`、`urlsplit`、`ValueError`、`OutputContract`。 返回路径：L42的`OutputContract( provider, "json_object", "langchain_json_mode", { "max_output_tokens": pro…`。
- `structured_model`（L54–L91）：接收`profile`、`schema`、`contract`、`http_client`。 源码说明：The official LangChain integration owns wire formatting and schema parsing. LangGraph nodes call this same Runnable for all four schema-driven stages. JSON mode preserves open dictionaries; local stri。 调用`httpx.AsyncClient`、`SyncOnlyTransport`、`model_class`、`model.with_structured_output`、`asyncio.get_running_loop`、`asyncio.run`、`async_client.aclose`、`ThreadPoolExecutor`、`executor.submit(asyncio.run, async_client.aclose()).result`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `SyncOnlyTransport`（L94–L96）：继承`httpx.AsyncBaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SyncOnlyTransport.handle_async_request`（L95–L96）：接收`request`。 控制顺序：L96抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedTransport`（L99–L135）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AuditedTransport.__init__`（L102–L109）：接收`contract`、`inner`。 调用`httpx.HTTPTransport`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AuditedTransport.handle_request`（L111–L131）：接收`request`。 控制顺序：L115遍历`response.iter_bytes()`；L117按`len(data) > 2_000_000`分支；L118抛异常，停止当前正常路径；L119按`200 <= response.status_code < 300`分支；L125抛异常，停止当前正常路径。 调用`self.inner.handle_request`、`bytearray`、`response.iter_bytes`、`data.extend`、`len`、`OutputFailure`、`completion_content`、`load_json`、`response.close`等。 返回路径：L131的`httpx.Response(response.status_code, headers=headers, content=bytes(data))`。
- `AuditedTransport.close`（L133–L135）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134按`self.owned`分支。 调用`self.inner.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `OutputFailure`（L138–L143）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `OutputFailure.__init__`（L141–L143）：接收`code`、`message`、`retry`、`repair`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_json`（L146–L172）：接收`text`。 控制顺序：L172抛异常，停止当前正常路径。 调用`json.loads`、`ValueError`。 返回路径：L165的`json.loads( text, object_pairs_hook=unique_pairs, parse_constant=invalid_constant, parse_f…`。
- `load_json.unique_pairs`（L147–L153）：接收`pairs`。 控制顺序：L149遍历`pairs`；L150按`key in result`分支；L151抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L153的`result`。
- `load_json.invalid_constant`（L155–L156）：接收`_`。 控制顺序：L156抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `load_json.finite_float`（L158–L162）：接收`value`。 控制顺序：L160按`not math.isfinite(result)`分支；L161抛异常，停止当前正常路径。 调用`float`、`math.isfinite`、`ValueError`。 返回路径：L162的`result`。
- `completion_content`（L175–L220）：接收`envelope`、`contract`。 控制顺序：L176按`not isinstance(envelope, dict) or envelope.get("error")`分支；L177抛异常，停止当前正常路径；L179按`not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict…`分支；L180抛异常，停止当前正常路径；L183按`not isinstance(message, dict) or message.get("role", "assistant") != "assistant"`分支；L184抛异常，停止当前正常路径；L185按`message.get("refusal") is not None`分支；L186按`message["refusal"] != ""`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`envelope.get`、`OutputFailure`、`len`、`choice.get`、`message.get`、`content.strip`、`usage.items`、`type`。 返回路径：L220的`content, safe_usage, finish or "unknown"`。
- `validate_content`（L223–L230）：接收`content`、`schema`、`mode`。 控制顺序：L224按`mode != "json_object"`分支；L225抛异常，停止当前正常路径；L228按`not isinstance(value, dict)`分支；L229抛异常，停止当前正常路径。 调用`ValueError`、`load_json`、`isinstance`、`schema.model_validate_json`。 返回路径：L230的`schema.model_validate_json(content, strict=True)`。

</details>

**创建路径：** `workbench/model_protocol.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L230。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8774`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_protocol.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "aa42ad468744e9c2ba6b74a3bb0386ea4dc9f6b95cb526eb928f34a84e052a6a"} -->
````python
# workbench/model_protocol.py
"""LangChain structured-output integration and provider-independent validation guards."""

import asyncio
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
def structured_model(profile, schema, contract, http_client):
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
            streaming=False,
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

    def __init__(self, contract, inner=None):
        self.contract = contract
        self.owned = inner is None
        self.inner = inner if inner is not None else httpx.HTTPTransport(retries=0, trust_env=False)
        self.error = None
        self.content = None
        self.usage = {}
        self.finish = "unknown"

    def handle_request(self, request):
        response = self.inner.handle_request(request)
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
        except (ValueError, TypeError) as exc:
            self.error = exc
            raise
        finally:
            response.close()
        headers = dict(response.headers)
        headers.pop("content-encoding", None)
        headers.pop("content-length", None)
        return httpx.Response(response.status_code, headers=headers, content=bytes(data))

    def close(self):
        if self.owned:
            self.inner.close()


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
