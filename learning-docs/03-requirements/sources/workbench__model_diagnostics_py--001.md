# workbench/model_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `failure_diagnostic`（L4–L66）：接收`code`、`trace_id`、`attempt`、`details`。 控制顺序：L8按`code.startswith("http_") or code == "transport_error"`分支；L12按`code in {"http_401", "http_403"}`分支；L14按`code == "http_429"`分支；L16按`code in {"interrupted", "worker_interrupted", "abandoned_attempt"}`分支；L20按`code in {"refusal", "content_filter"}`分支；L23按`code == "unexpected_model_error"`分支；L27按`code == "invalid_json"`分支；L30按`code in { "length", "truncated", "response_too_large", "response_byte_limit", "stream…`分支。后续分支沿下方源码相同行号继续阅读。 调用`code.startswith`。 返回路径：L58的`{ "phase": phase, "code": code, "trace_id": trace_id, "attempt": attempt, "summary": summa…`。
- `schema_diagnostics`（L69–L122）：接收`exc`、`schema`。 源码说明：Only schema-owned path segments and validator type, never arbitrary model values. Pydantic root validator messages and extra-field locations can contain the raw response or credentials; neither is saf。 调用`set`、`collect`、`schema.model_json_schema`、`safe_message`、`error["type"].replace("_", "").isalnum`、`error["type"].replace`、`isinstance`、`exc.errors`。 返回路径：L112的`[ { "message": safe_message(error), "type": error["type"] if error["type"].replace("_", ""…`。
- `schema_diagnostics.collect`（L77–L84）：接收`node`。 控制顺序：L78按`isinstance(node, dict)`分支；L80遍历`node.values()`；L82按`isinstance(node, list)`分支；L83遍历`node`。 调用`isinstance`、`allowed.update`、`node.get`、`node.values`、`collect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `schema_diagnostics.safe_message`（L108–L110）：接收`error`。 调用`error["msg"].removeprefix`。 返回路径：L110的`value if value in safe_messages else "字段结构或类型不符合约定"`。

</details>

**创建路径：** `workbench/model_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L122。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5663`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6265d57aebcbbdddcc2ec5befffc4640912267183f1d632777e1b663c6889977"} -->
````python
# workbench/model_diagnostics.py
"""Safe actionable provider failures. Never persist provider bodies or input values."""


def failure_diagnostic(code, *, trace_id, attempt=None, details=None):
    phase = "response_validation"
    summary = "模型响应未通过结构校验，未生成可批准结果。"
    hint = "查看字段路径与错误类型；确认模型支持 JSON 结构化输出后，重试当前运行。无需重填已提交的回答。"
    if code.startswith("http_") or code == "transport_error":
        phase = "provider_request"
        summary = "模型请求失败，尚未取得有效响应。"
        hint = "先在模型与配置中测试该阶段连接，检查网络、服务额度与模型权限，再重试当前运行。"
        if code in {"http_401", "http_403"}:
            hint = "检查该阶段的密钥与模型访问权限，保存后测试连接；不要把密钥放入对话。"
        elif code == "http_429":
            hint = "检查服务商额度或限流状态，稍后手动重试当前运行。"
    elif code in {"interrupted", "worker_interrupted", "abandoned_attempt"}:
        phase = "response_stream"
        summary = "响应在完成前中断，已保留历史回答。"
        hint = "确认服务与网络恢复后，重试当前运行；不会把未完成响应当作已批准方案。"
    elif code in {"refusal", "content_filter"}:
        summary = "模型拒绝处理或触发内容过滤。"
        hint = "检查请求是否适合该服务；不要通过重试绕过服务商的安全限制。"
    elif code == "unexpected_model_error":
        phase = "model_execution"
        summary = "模型调用发生未预期错误，未生成可批准结果。"
        hint = "使用追踪 ID 定位服务端日志，检查模型适配器和配置；修复后重试当前运行。"
    elif code == "invalid_json":
        summary = "服务已响应，但返回内容不是可接受的完整 JSON 对象。"
        hint = "检查服务是否支持 JSON 对象输出；保留严格校验，调整模型或配置后重试当前运行。"
    elif code in {
        "length",
        "truncated",
        "response_too_large",
        "response_byte_limit",
        "stream_wire_limit",
    }:
        summary = "模型响应超过长度限制，无法作为完整结果。"
        hint = "检查模型输出限制与本轮范围，调整后重试；保留原始需求与已提交回答。"
        if code == "stream_wire_limit":
            phase = "response_stream"
            summary = "模型流的传输字节超过安全上限；正文与流式封装分别计量。"
    elif code in {
        "request_destination_rejected",
        "request_count_limit",
        "request_byte_limit",
        "request_not_json",
        "model_substitution_rejected",
        "authorization_header_mismatch",
        "structured_output_required",
        "output_budget_missing_or_exceeded",
        "monetary_budget_exceeded",
        "provider_reported_usage_exceeds_reserved_bounds",
        "harness_internal_error",
    }:
        phase = "request_guard"
        summary = "验收请求被安全或预算保护停止，未自动重试。"
        hint = "使用追踪 ID 和安全回执中的错误代码定位原因；重新实测前核对剩余预算与授权。"
    return {
        "phase": phase,
        "code": code,
        "trace_id": trace_id,
        "attempt": attempt,
        "summary": summary,
        "retry_hint": hint,
        "details": details or [],
    }


def schema_diagnostics(exc, schema):
    """Only schema-owned path segments and validator type, never arbitrary model values.

    Pydantic root validator messages and extra-field locations can contain the
    raw response or credentials; neither is safe to expose verbatim.
    """
    allowed = set()

    def collect(node):
        if isinstance(node, dict):
            allowed.update(node.get("properties", {}))
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)

    collect(schema.model_json_schema())
    safe_messages = {
        "字段清单不能包含重复名称",
        "文本问题不能包含选择项",
        "选择问题至少包含两个不同选项",
        "同一个问题的选项标识不能重复",
        "同一个问题的选项文字不能重复",
        "问题标识不能重复",
        "问题文字不能重复",
        "结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题",
        "同一实体不能重复声明字段清单",
        "最小长度不得大于最大长度",
        "枚举必须有不重复的选项",
        "只有 enum 类型可以声明 choices",
        "关键词搜索只能使用文本/枚举字段",
        "日期范围只支持 date 类型",
        "字段名属于保留名称",
        "字段名称必须唯一",
        "实体名称重复或为保留名称",
        "自定义规则引用未知实体",
    }

    def safe_message(error):
        value = error["msg"].removeprefix("Value error, ")
        return value if value in safe_messages else "字段结构或类型不符合约定"

    return [
        {
            "message": safe_message(error),
            "type": error["type"] if error["type"].replace("_", "").isalnum() else "validation",
            "path": [
                part if isinstance(part, int) or part in allowed else "[field]"
                for part in error["loc"][:20]
            ],
        }
        for error in exc.errors(include_input=False, include_url=False)[:30]
    ]
````
