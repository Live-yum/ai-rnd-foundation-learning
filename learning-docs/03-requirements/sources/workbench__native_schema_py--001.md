# workbench/native_schema.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `NativeSchema`（L20–L92）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `NativeSchema.__init__`（L21–L57）：接收`profile`、`schema`、`settings`、`key`、`payload`、`streaming`。 控制顺序：L24按`streaming or profile.provider != "compatible" or profile.max_output_tokens != 8192 or…`分支；L35抛异常，停止当前正常路径；L37按`any(version(name) != pinned for name, pinned in SDK_VERSIONS.items())`分支；L38抛异常，停止当前正常路径；L47抛异常，停止当前正常路径。 调用`key.startswith`、`issubclass`、`payload.get("task", {}).get`、`payload.get`、`OutputFailure`、`any`、`version`、`SDK_VERSIONS.items`、`to_strict_json_schema`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NativeSchema.check_request`（L59–L82）：接收`request`。 控制顺序：L62按`len(data) > self.input_bytes`分支；L63抛异常，停止当前正常路径；L65按`request.method != "POST" or str(request.url) != self.url or set(body) != {"model", "m…`分支；L79抛异常，停止当前正常路径；L81抛异常，停止当前正常路径。 调用`request.read`、`len`、`load_json`、`str`、`set`、`type`、`json.dumps`、`request.extensions.get`、`dict.fromkeys`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NativeSchema.check_content`（L84–L92）：接收`content`。 控制顺序：L89抛异常，停止当前正常路径。 调用`self.validator.validate`、`load_json`、`OutputFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_receipt`（L95–L102）：接收`native`、`status`。 调用`type`。 返回路径：L96的`{ "native_strict_requested": True, "native_request_verified": native.request_verified if n…`。

</details>

**创建路径：** `workbench/native_schema.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L102。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4306`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_schema.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7eea12882612a372f58c7a5964febaca4a1ab0bc5626182c3db1a298e15e818c"} -->
````python
# workbench/native_schema.py
"""Opt-in mini-SWE wire contract for the reviewed, locked SDK combination."""

import json
from importlib.metadata import version

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from workbench.model_protocol import OutputFailure, load_json

SDK_VERSIONS = {
    "langchain-openai": "1.6.7",
    "openai": "3.22.1",
    "pydantic": "2.13.5",
    "httpx": "0.28.1",
    "jsonschema": "4.26.0",
}


class NativeSchema:
    def __init__(self, profile, schema, settings, *, key, payload, streaming):
        from workbench.coding.ports import AgentTurn

        if (
            streaming
            or profile.provider != "compatible"
            or profile.max_output_tokens != 8192
            or settings.max_context_chars > 40000
            or settings.llm_timeout > 60
            or not key.startswith("coding:mini_swe:")
            or not issubclass(schema, AgentTurn)
            or schema.__name__ != "ApprovedAgentTurn"
            or payload.get("task", {}).get("id") not in {"sla-api", "sla-dashboard"}
        ):
            raise OutputFailure("native_scope_rejected", "原生 strict 仅限批准的 mini-swe-sla 契约")
        try:
            if any(version(name) != pinned for name, pinned in SDK_VERSIONS.items()):
                raise ValueError
            # This private SDK transformation is version-bound and checked again
            # against the actual serialized HTTP request before it can leave.
            from openai.lib._pydantic import to_strict_json_schema

            self.schema = to_strict_json_schema(schema)
            Draft202012Validator.check_schema(self.schema)
            self.validator = Draft202012Validator(self.schema)
        except Exception:
            raise OutputFailure("native_sdk_unsupported", "原生 strict SDK/Schema 不兼容") from None
        self.response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "strict": True, "schema": self.schema},
        }
        self.url = profile.base_url.rstrip("/") + "/chat/completions"
        self.model = profile.model
        self.input_bytes = 4 * settings.max_context_chars
        self.timeout = settings.llm_timeout
        self.request_verified = False
        self.local_conformant = None

    def check_request(self, request):
        try:
            data = request.read()
            if len(data) > self.input_bytes:
                raise ValueError
            body = load_json(data)
            if (
                request.method != "POST"
                or str(request.url) != self.url
                or set(body)
                != {"model", "messages", "stream", "max_completion_tokens", "response_format"}
                or body["model"] != self.model
                or body["stream"] is not False
                or type(body["max_completion_tokens"]) is not int
                or body["max_completion_tokens"] != 8192
                or json.dumps(body["response_format"], sort_keys=True)
                != json.dumps(self.response_format, sort_keys=True)
                or request.extensions.get("timeout")
                != dict.fromkeys(("connect", "read", "write", "pool"), self.timeout)
            ):
                raise ValueError
        except ValueError, TypeError, KeyError:
            raise OutputFailure("native_request_mismatch", "原生 strict 出站契约不匹配") from None
        self.request_verified = True

    def check_content(self, content):
        self.local_conformant = False
        try:
            self.validator.validate(load_json(content))
        except ValueError, TypeError, ValidationError, RecursionError:
            raise OutputFailure(
                "native_schema_violation", "响应违反所请求的 strict Schema"
            ) from None
        self.local_conformant = True


def native_receipt(native=None, *, status=None):
    return {
        "native_strict_requested": True,
        "native_request_verified": native.request_verified if native is not None else False,
        "native_local_conformant": native.local_conformant if native is not None else None,
        "native_provider_enforcement": "unknown",
        "native_http_status": status if type(status) is int and 100 <= status <= 599 else None,
    }
````
