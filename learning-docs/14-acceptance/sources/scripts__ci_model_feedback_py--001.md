# scripts/ci_model_feedback.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_model_feedback；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.llm`、`workbench.model_connection`、`workbench.model_protocol`、`workbench.model_settings`、`workbench.requirement_intent`、`workbench.runtime`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `SafeFailure`（L56–L60）：继承`OutputFailure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SafeFailure.__init__`（L59–L60）：接收`code`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Config`（L64–L76）：继承`object`。声明的数据项为`model`、`key`、`approved_max_cny`；类型约束/数据库列参数以完整定义为准。
- `Config.cost`（L69–L71）：接收`input_tokens`、`output_tokens`。 调用`Decimal`。 返回路径：L71的`(input_rate * input_tokens + output_rate * output_tokens) / Decimal(1_000_000)`。
- `Config.maximum_cost`（L73–L76）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.cost`。 返回路径：L74的`self.cost( MAX_CALLS * (2 * MAX_REQUEST_BYTES + 4096), PROBE_OUTPUT_TOKENS + 4 * TASK_OUTP…`。
- `configuration`（L79–L97）：接收`env`。 控制顺序：L80按`env.get("BASE_URL", "").strip().rstrip("/") != ENDPOINT`分支；L81抛异常，停止当前正常路径；L83按`model not in PRICES`分支；L84抛异常，停止当前正常路径；L86按`not key or any(ord(character) <= 32 for character in key)`分支；L87抛异常，停止当前正常路径；L91抛异常，停止当前正常路径；L92按`not approved.is_finite() or not 0 < approved <= MAX_APPROVED_CNY`分支。后续分支沿下方源码相同行号继续阅读。 调用`env.get("BASE_URL", "").strip().rstrip`、`env.get("BASE_URL", "").strip`、`env.get`、`SafeFailure`、`env.get("MODE", "").strip`、`env.get("API_KEY", "").strip`、`any`、`ord`、`Decimal`等。 返回路径：L97的`result`。
- `trusted_dispatch`（L100–L110）：接收`env`。 控制顺序：L101按`env.get("GITHUB_ACTIONS") != "true" or env.get("GITHUB_EVENT_NAME") != "workflow_disp…`分支；L110抛异常，停止当前正常路径。 调用`env.get`、`re.fullmatch`、`SafeFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `response_receipt`（L113–L148）：接收`status`、`data`。 控制顺序：L119遍历`data.splitlines()`；L120按`line.startswith(b"data:") and line[5:].strip() != b"[DONE]"`分支；L125遍历`envelopes`；L126按`not isinstance(envelope, dict)`分支；L129按`isinstance(usage, dict)`分支；L138按`isinstance(choices, list) and choices and isinstance(choices[0], dict)`分支；L140按`finish in { "stop", "length", "content_filter", "tool_calls", "insufficient_system_re…`分支。 调用`json.loads`、`data.splitlines`、`line.startswith`、`line[5:].strip`、`envelopes.append`、`isinstance`、`envelope.get`、`usage.items`、`type`等。 返回路径：L148的`receipt`。
- `BoundedFeedbackTransport`（L151–L289）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BoundedFeedbackTransport.__init__`（L154–L162）：接收`config`。 调用`httpx.HTTPTransport`、`Decimal`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedFeedbackTransport.handle_request`（L164–L194）：接收`request`。 控制顺序：L170按`len(self.receipts) > before`分支；L172抛异常，停止当前正常路径；L174按`len(self.receipts) > before`分支；L181抛异常，停止当前正常路径；L190按`len(self.receipts) > before`分支；L194抛异常，停止当前正常路径。 调用`len`、`self._handle_request`、`self.guard_failures.append`、`self.receipts[-1].update`、`isinstance`、`type`、`SafeFailure`。 返回路径：L167的`self._handle_request(request)`。
- `BoundedFeedbackTransport._handle_request`（L196–L283）：接收`request`。 控制顺序：L197按`request.method != "POST" or str(request.url) != ENDPOINT + "/chat/completions"`分支；L198抛异常，停止当前正常路径；L199按`self.phase not in PHASE_LIMITS or self.calls >= MAX_CALLS or self.phase_calls[self.ph…`分支；L204抛异常，停止当前正常路径；L206按`len(data) > MAX_REQUEST_BYTES`分支；L207抛异常，停止当前正常路径；L211抛异常，停止当前正常路径；L212按`not isinstance(body, dict) or body.get("model") != self.config.model`分支。后续分支沿下方源码相同行号继续阅读。 调用`str`、`SafeFailure`、`request.read`、`len`、`json.loads`、`isinstance`、`body.get`、`hmac.compare_digest`、`request.headers.get`等。 返回路径：L283的`httpx.Response(response.status_code, headers=headers, content=bytes(data))`。
- `BoundedFeedbackTransport.close`（L285–L286）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedFeedbackTransport.shutdown`（L288–L289）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.transport.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `safe_gate`（L292–L304）：接收`run`。 调用`run.get`、`pending.get`、`data.get`、`bool`、`len`、`requirement.get`。 返回路径：L296的`{ "status": run["status"], "gate_stage": pending.get("stage"), "can_approve": bool(pending…`。
- `failure_receipts`（L307–L337）：接收`store`、`run_id`。 控制顺序：L320遍历`reversed(events)`。 调用`store.tx`、`list`、`session.scalars`、`select(Event) .where(Event.run_id == run_id, Event.kind == "assis…`、`select(Event) .where`、`select`、`Event.id.desc`、`reversed`、`event.data.get`等。 返回路径：L337的`receipts`。
- `run_check`（L340–L452）：接收`config`、`transport`、`directory`。 控制顺序：L382按`not probe["ok"] and probe["code"] != "truncated"`分支；L403按`not gate or gate["stage"] not in {"requirements", "clarification"}`分支；L450按`run_id`分支。 调用`Settings`、`ModelSettingsRepository(settings).update`、`ModelSettingsRepository`、`config.key.get_secret_value`、`ModelConnectionTester(settings, transport).test`、`ModelConnectionTester`、`ConnectionTestRequest`、`str`、`uuid.uuid4`等。 返回路径：L384的`result`；L405的`result`；L448的`result`。
- `main`（L455–L504）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L487按`transport`分支；L497按`config`分支；L503按`not result["passed"]`分支；L504抛异常，停止当前正常路径。 调用`trusted_dispatch`、`configuration`、`os.environ.pop`、`result.update`、`str`、`config.maximum_cost`、`BoundedFeedbackTransport`、`tempfile.TemporaryDirectory`、`tempfile.TemporaryFile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_model_feedback.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L508。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19982`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_model_feedback.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "93b9135a0177e36d175b8d00ac74b33e6ded0bcdb4bfac0a72f940e5a74f141d"} -->
````python
# scripts/ci_model_feedback.py
"""Explicitly authorized, cost-bounded live model/settings + signup feedback check.

Only synthetic inputs are sent. The real Runtime, Store, ModelGateway and
connection tester remain unchanged; this transport enforces network/spend scope.
Never uploads raw responses, databases, prompts, credentials or generated files.
"""

import contextlib
import hmac
import json
import logging
import os
import re
import tempfile
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx
from pydantic import SecretStr
from sqlalchemy import func, select

from workbench.domain import Requirement
from workbench.llm import ModelGateway
from workbench.model_connection import ConnectionTestRequest, ModelConnectionTester
from workbench.model_protocol import OutputFailure, stream_wire_limit
from workbench.model_settings import ModelSettingsRepository
from workbench.requirement_intent import registration_scope
from workbench.runtime import Runtime
from workbench.settings import ROOT, Settings
from workbench.store import Approval, Event, Store

REPOSITORY = "Live-yum/ai-rnd-foundation-learning"
REFS = {"refs/heads/main", "refs/heads/fix/model-feedback-history"}
ENDPOINT = "https://api.deepseek.com"
ORIGINAL = "大学生计算机设计大赛报名网站"
ANSWER = "参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录"
MAX_CALLS = 5
MAX_REQUEST_BYTES = 65536
MAX_RESPONSE_BYTES = 2_000_000
TASK_OUTPUT_TOKENS = 8192
PROBE_OUTPUT_TOKENS = 128
PHASE_LIMITS = {"connection": 1, "initial_requirements": 2, "corrected_requirements": 2}
# Verified 2026-10-03, peak/cache-miss CNY per million tokens. Never substitute a
# model for an unavailable one. Unknown model IDs/prices fail before networking.
PRICE_SOURCE = "https://api-docs.deepseek.com/zh-cn/quick_start/pricing/"
PRICE_DATE = "2026-10-03"
PRICES = {
    "deepseek-flash": (Decimal("2"), Decimal("8")),
    "deepseek-v4-pro": (Decimal("9"), Decimal("27")),
}
MAX_APPROVED_CNY = Decimal("10")


class SafeFailure(OutputFailure):
    """Only harness-owned failure codes are public; never pass provider strings."""

    def __init__(self, code):
        super().__init__(code, code, retry=False)


@dataclass(frozen=True)
class Config:
    model: str
    key: SecretStr = field(repr=False)
    approved_max_cny: Decimal = MAX_APPROVED_CNY

    def cost(self, input_tokens, output_tokens):
        input_rate, output_rate = PRICES[self.model]
        return (input_rate * input_tokens + output_rate * output_tokens) / Decimal(1_000_000)

    def maximum_cost(self):
        return self.cost(
            MAX_CALLS * (2 * MAX_REQUEST_BYTES + 4096), PROBE_OUTPUT_TOKENS + 4 * TASK_OUTPUT_TOKENS
        )


def configuration(env):
    if env.get("BASE_URL", "").strip().rstrip("/") != ENDPOINT:
        raise SafeFailure("configuration_destination_mismatch")
    model = env.get("MODE", "").strip()
    if model not in PRICES:
        raise SafeFailure("configuration_model_or_price_unverified")
    key = env.get("API_KEY", "").strip()
    if not key or any(ord(character) <= 32 for character in key):
        raise SafeFailure("configuration_key_missing_or_invalid")
    try:
        approved = Decimal(env.get("APPROVED_MAX_CNY", "0"))
    except InvalidOperation, TypeError:
        raise SafeFailure("invalid_approved_budget") from None
    if not approved.is_finite() or not 0 < approved <= MAX_APPROVED_CNY:
        raise SafeFailure("invalid_approved_budget")
    result = Config(model, SecretStr(key), approved)
    if result.maximum_cost() > approved:
        raise SafeFailure("insufficient_preapproved_budget")
    return result


def trusted_dispatch(env):
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or env.get("GITHUB_REPOSITORY") != REPOSITORY
        or env.get("GITHUB_REF") not in REFS
        or env.get("GITHUB_RUN_ATTEMPT") != "1"
        or not re.fullmatch(r"[a-f0-9]{40}", env.get("GITHUB_SHA", ""))
        or env.get("REVIEWED_SHA") != env.get("GITHUB_SHA")
    ):
        raise SafeFailure("untrusted_dispatch_or_repeat_attempt")


def response_receipt(status, data):
    receipt = {"http_status": status}
    try:
        envelopes = [json.loads(data)]
    except ValueError, UnicodeDecodeError:
        envelopes = []
        for line in data.splitlines():
            if line.startswith(b"data:") and line[5:].strip() != b"[DONE]":
                try:
                    envelopes.append(json.loads(line[5:].strip()))
                except ValueError, UnicodeDecodeError:
                    continue
    for envelope in envelopes:
        if not isinstance(envelope, dict):
            continue
        usage = envelope.get("usage")
        if isinstance(usage, dict):
            receipt["usage"] = {
                key: value
                for key, value in usage.items()
                if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
                and type(value) is int
                and 0 <= value <= 100_000_000
            }
        choices = envelope.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            finish = choices[0].get("finish_reason")
            if finish in {
                "stop",
                "length",
                "content_filter",
                "tool_calls",
                "insufficient_system_resource",
            }:
                receipt["finish_reason"] = finish
    return receipt


class BoundedFeedbackTransport(httpx.BaseTransport):
    """Every attempt reserves its worst-case cost *before* an actual HTTP request."""

    def __init__(self, config):
        self.config = config
        self.transport = httpx.HTTPTransport(retries=0, trust_env=False)
        self.phase = "connection"
        self.calls = 0
        self.phase_calls = {phase: 0 for phase in PHASE_LIMITS}
        self.reserved_cny = Decimal("0")
        self.receipts = []
        self.guard_failures = []

    def handle_request(self, request):
        before = len(self.receipts)
        try:
            return self._handle_request(request)
        except SafeFailure as exc:
            self.guard_failures.append({"code": exc.code, "call": self.calls})
            if len(self.receipts) > before:
                self.receipts[-1]["error_code"] = exc.code
            raise
        except httpx.HTTPError as exc:
            if len(self.receipts) > before:
                self.receipts[-1].update(
                    error_code="transport_timeout"
                    if isinstance(exc, httpx.TimeoutException)
                    else "transport_error",
                    exception_type=type(exc).__name__,
                )
            raise
        except Exception as exc:
            self.guard_failures.append(
                {
                    "code": "harness_internal_error",
                    "call": self.calls,
                    "exception_type": type(exc).__name__,
                }
            )
            if len(self.receipts) > before:
                self.receipts[-1].update(
                    error_code="harness_internal_error", exception_type=type(exc).__name__
                )
            raise SafeFailure("harness_internal_error") from None

    def _handle_request(self, request):
        if request.method != "POST" or str(request.url) != ENDPOINT + "/chat/completions":
            raise SafeFailure("request_destination_rejected")
        if (
            self.phase not in PHASE_LIMITS
            or self.calls >= MAX_CALLS
            or self.phase_calls[self.phase] >= PHASE_LIMITS[self.phase]
        ):
            raise SafeFailure("request_count_limit")
        data = request.read()
        if len(data) > MAX_REQUEST_BYTES:
            raise SafeFailure("request_byte_limit")
        try:
            body = json.loads(data)
        except ValueError:
            raise SafeFailure("request_not_json") from None
        if not isinstance(body, dict) or body.get("model") != self.config.model:
            raise SafeFailure("model_substitution_rejected")
        if not hmac.compare_digest(
            request.headers.get("Authorization", ""), "Bearer " + self.config.key.get_secret_value()
        ):
            raise SafeFailure("authorization_header_mismatch")
        if body.get("response_format") != {"type": "json_object"}:
            raise SafeFailure("structured_output_required")
        limit = PROBE_OUTPUT_TOKENS if self.phase == "connection" else TASK_OUTPUT_TOKENS
        output = body.get("max_tokens", body.get("max_completion_tokens"))
        if (
            type(output) is not int
            or not 1 <= output <= limit
            or ("max_tokens" in body and "max_completion_tokens" in body)
        ):
            raise SafeFailure("output_budget_missing_or_exceeded")
        # Two tokens per UTF-8 byte plus generous framing overhead is deliberately
        # much higher than normal BPE input tokenization. Include every JSON byte.
        input_bound = 2 * len(data) + 4096
        reserve = self.config.cost(input_bound, output)
        if self.reserved_cny + reserve > self.config.approved_max_cny:
            raise SafeFailure("monetary_budget_exceeded")
        self.reserved_cny += reserve
        self.calls += 1
        self.phase_calls[self.phase] += 1
        receipt = {
            "phase": self.phase,
            "call": self.calls,
            "input_token_bound": input_bound,
            "output_token_limit": output,
            "reserved_cny": str(reserve),
        }
        self.receipts.append(receipt)
        try:
            response = self.transport.handle_request(request)
        except httpx.HTTPError:
            receipt["transport_error"] = True
            raise
        streaming = (
            response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            == "text/event-stream"
        )
        byte_limit = stream_wire_limit(output) if streaming else MAX_RESPONSE_BYTES
        receipt.update(
            http_status=response.status_code,
            response_transport="sse" if streaming else "non_streaming",
            response_bytes=0,
            response_byte_limit=byte_limit,
        )
        data = bytearray()
        try:
            for chunk in response.iter_bytes():
                data.extend(chunk)
                receipt["response_bytes"] = len(data)
                if len(data) > byte_limit:
                    raise SafeFailure("stream_wire_limit" if streaming else "response_byte_limit")
        finally:
            response.close()
        receipt.update(response_receipt(response.status_code, bytes(data)))
        usage = receipt.get("usage", {})
        if "prompt_tokens" in usage and "completion_tokens" in usage:
            receipt["reported_cny"] = str(
                self.config.cost(usage["prompt_tokens"], usage["completion_tokens"])
            )
            if usage["prompt_tokens"] > input_bound or usage["completion_tokens"] > output:
                raise SafeFailure("provider_reported_usage_exceeds_reserved_bounds")
        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"content-encoding", "content-length"}
        }
        return httpx.Response(response.status_code, headers=headers, content=bytes(data))

    def close(self):
        pass  # Each production adapter closes its own Client; the harness owns this pool.

    def shutdown(self):
        self.transport.close()


def safe_gate(run):
    pending = run.get("pending") or {}
    data = pending.get("data") or {}
    requirement = data.get("requirement") or {}
    return {
        "status": run["status"],
        "gate_stage": pending.get("stage"),
        "can_approve": bool(pending.get("can_approve")),
        "questions": len(requirement.get("questions", [])),
        "unsupported": len(requirement.get("unsupported", [])),
        "analysis_diagnostics": len(data.get("analysis_diagnostics", [])),
        "capability_conflicts": len(data.get("capability_conflicts", [])),
    }


def failure_receipts(store, run_id):
    # Read only terminal diagnostic events, so a long delta stream cannot hide
    # the final failure beyond the general API's first 200-event page.
    with store.tx() as session:
        events = list(
            session.scalars(
                select(Event)
                .where(Event.run_id == run_id, Event.kind == "assistant_failed")
                .order_by(Event.id.desc())
                .limit(10)
            )
        )
        receipts = []
        for event in reversed(events):
            diagnostic = event.data.get("diagnostic") or {}
            # These fields are created by failure_diagnostic/schema_diagnostics,
            # whose path and message values are schema-owned, not provider text.
            receipts.append(
                {
                    **{
                        key: diagnostic[key]
                        for key in ("phase", "code", "trace_id", "attempt", "summary", "retry_hint")
                        if key in diagnostic
                    },
                    "details": [
                        {key: detail[key] for key in ("type", "path", "message") if key in detail}
                        for detail in diagnostic.get("details", [])[:30]
                    ],
                }
            )
        return receipts


def run_check(config, transport, directory):
    settings = Settings(
        data_dir=directory / "private",
        base_url="",
        api_key="",
        model="",
        install_products=False,
        enable_coding=False,
        max_model_calls=4,
        max_rounds=2,
        max_output_tokens=TASK_OUTPUT_TOKENS,
        llm_timeout=90,
        _env_file=None,
    )
    # Exercise saved configuration, not an environment-only shortcut.
    saved = ModelSettingsRepository(settings).update(
        {
            "expected_revision": "0",
            "default": {
                "base_url": ENDPOINT,
                "model": config.model,
                "api_key": config.key.get_secret_value(),
                "provider": "deepseek",
                "output_mode": "json_object",
                "max_output_tokens": TASK_OUTPUT_TOKENS,
            },
        }
    )
    probe = ModelConnectionTester(settings, transport).test(
        ConnectionTestRequest(
            stage="requirements",
            expected_revision=saved["revision"],
            request_id=str(uuid.uuid4()),
            confirm_cost=True,
        )
    )
    result = {
        "connection": {
            name: probe[name]
            for name in ("ok", "phase", "code", "trace_id", "attempts", "revision", "retryable")
        }
    }
    if not probe["ok"] and probe["code"] != "truncated":
        result["passed"] = False
        return result
    store = Store(settings)
    store.migrate()
    run_id = None
    try:
        project = store.create_project("合成报名反馈验收", str(uuid.uuid4()))
        run_id = store.create_run(
            project["id"],
            {"requirement": ORIGINAL, "template": "fastapiadmin", "intelligent": False},
            str(uuid.uuid4()),
        )["run_id"]
        with Runtime(
            settings, store, ModelGateway(settings, store, transport, streaming=True)
        ) as worker:
            transport.phase = "initial_requirements"
            worker.tick()
            initial = store.get_run(run_id)
            result["initial"] = safe_gate(initial)
            gate = initial.get("pending")
            if not gate or gate["stage"] not in {"requirements", "clarification"}:
                result["passed"] = False
                return result
            store.submit(
                run_id,
                {
                    "gate_id": gate["gate_id"],
                    "action": "answer" if gate["stage"] == "clarification" else "revise",
                    "text": ANSWER,
                },
                str(uuid.uuid4()),
            )
            transport.phase = "corrected_requirements"
            worker.tick()
            corrected = store.get_run(run_id)
            result["corrected"] = safe_gate(corrected)
            messages = [
                message["content"]
                for message in store.messages(run_id)
                if message["role"] == "user"
            ]
            result["answer_preserved"] = messages == [ORIGINAL, ANSWER]
            result["scope_preserved"] = (
                registration_scope(messages)["mode"] == "authenticated_business_ui"
            )
            pending = corrected.get("pending") or {}
            requirement = pending.get("data", {}).get("requirement")
            result["requirement_valid"] = bool(
                requirement and isinstance(Requirement.model_validate(requirement), Requirement)
            )
            with store.tx() as session:
                result["approvals"] = session.scalar(select(func.count()).select_from(Approval))
            result["generation_absent"] = not (
                settings.data_dir / "runs" / run_id / "product"
            ).exists()
            result["passed"] = bool(
                probe["ok"]
                and result["answer_preserved"]
                and result["scope_preserved"]
                and result["requirement_valid"]
                and result["approvals"] == 0
                and result["generation_absent"]
                and corrected["status"] == "WAITING_REQUIREMENTS"
                and pending.get("can_approve")
            )
            return result
    finally:
        if run_id:
            result["model_failures"] = failure_receipts(store, run_id)
        store.engine.dispose()


def main():
    result = {
        "passed": False,
        "scope": "connection_and_signup_requirements_only",
        "price_source": PRICE_SOURCE,
        "price_verified_at": PRICE_DATE,
    }
    config, transport = None, None
    try:
        trusted_dispatch(os.environ)
        config = configuration(os.environ)
        os.environ.pop("API_KEY", None)
        result.update(
            model=config.model,
            endpoint=ENDPOINT,
            commit=os.environ["GITHUB_SHA"],
            approved_max_cny=str(config.approved_max_cny),
            maximum_reserved_cny=str(config.maximum_cost()),
        )
        transport = BoundedFeedbackTransport(config)
        with (
            tempfile.TemporaryDirectory(prefix="model-feedback-") as directory,
            tempfile.TemporaryFile(mode="w+", encoding="utf-8") as quiet,
        ):
            logging.disable(logging.CRITICAL)
            with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                result.update(run_check(config, transport, Path(directory)))
    except SafeFailure as exc:
        result["failure_code"] = str(exc)
    except Exception as exc:
        result.update(failure_code="execution_failed", exception_type=type(exc).__name__)
    finally:
        if transport:
            result.update(
                actual_http_calls=transport.calls,
                phase_calls=transport.phase_calls,
                reserved_cny=str(transport.reserved_cny),
                requests=transport.receipts,
                guard_failures=transport.guard_failures,
            )
            transport.shutdown()
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if config:
            rendered = rendered.replace(config.key.get_secret_value(), "[redacted]")
        destination = ROOT / "reports/model-feedback/summary.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
````
