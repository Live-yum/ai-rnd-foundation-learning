# scripts/ci_template_projects.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_template_projects；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.template_acceptance_cases`、`scripts.template_acceptance_runtime`、`workbench.domain`、`workbench.filesystem`、`workbench.llm`、`workbench.model_diagnostics`、`workbench.model_protocol`、`workbench.runtime`、`workbench.settings`、`workbench.store`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `trusted_event`（L51–L80）：接收`env`、`event`。 源码说明：Bind every receipt and every credential-bearing request to the checked-out head.。 控制顺序：L59按`env.get("GITHUB_EVENT_NAME") == "pull_request"`分支。 调用`require`、`env.get`、`bool`、`re.fullmatch`、`event.get`、`event.get("label", {}).get`、`pr.get("head", {}).get("repo", {}).get`、`pr.get("head", {}).get`、`pr.get`等。 返回路径：L74的`{ "repository": REPOSITORY, "head_sha": head, "run_id": env.get("GITHUB_RUN_ID", ""), "run…`。
- `acceptance_settings`（L83–L135）：接收`env`、`directory`。 控制顺序：L84遍历`("BASE_URL", "MODE", "API_KEY")`；L133遍历`STAGES`。 调用`require`、`isinstance`、`env.get`、`bool`、`env[name].strip`、`env["BASE_URL"].strip().rstrip`、`env["BASE_URL"].strip`、`env["MODE"].strip`、`SecretStr`等。 返回路径：L135的`settings`。
- `BoundedTransport`（L138–L229）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BoundedTransport.__init__`（L141–L146）：接收`settings`。 调用`httpx.HTTPTransport`、`Counter`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedTransport.handle_request`（L148–L223）：接收`request`。 控制顺序：L152按`not ( self.run_id and self.stage in MODEL_STAGES and request.method == "POST" and str…`分支；L169抛异常，停止当前正常路径；L177遍历`response.iter_bytes()`；L179按`len(payload) > 2_000_000`分支；L180抛异常，停止当前正常路径；L203按`self.schema is not None and response.status_code == 200`分支。 调用`json.loads`、`request.read`、`self.settings.model_for`、`str`、`body.get`、`all`、`type`、`hmac.compare_digest`、`request.headers.get`等。 返回路径：L223的`httpx.Response(response.status_code, headers=headers, content=bytes(payload))`。
- `BoundedTransport.close`（L225–L226）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedTransport.shutdown`（L228–L229）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.inner.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ObservedGateway`（L232–L254）：继承`ModelGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ObservedGateway.__init__`（L233–L235）：接收`settings`、`store`、`transport`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ObservedGateway.complete`（L237–L254）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 调用`key.split`、`self.traces.append`、`super().complete`、`super`。 返回路径：L254的`result`。
- `failure_events`（L257–L289）：接收`store`、`run_id`、`settings`。 源码说明：Keep bounded diagnostics already authored by the platform, never response text.。 控制顺序：L260遍历`range(4)`；L262按`not events`分支；L265遍历`events`；L266按`event["kind"] not in {"model_failure", "assistant_failed"}`分支；L271遍历`("stage", "code", "request_id", "response_id", "attempt")`；L273按`isinstance(value, str)`分支；L275按`type(value) is int`分支；L282按`len(json.dumps(details, ensure_ascii=False)) <= 3000`分支。后续分支沿下方源码相同行号继续阅读。 调用`range`、`store.events`、`settings.redact_data`、`data.get`、`diagnostic.get`、`isinstance`、`type`、`len`、`json.dumps`等。 返回路径：L286的`failures`；L289的`failures`。
- `verify_delivery`（L292–L340）：接收`case`、`run`、`settings`、`directory`。 调用`require`、`result.get`、`all`、`cleanroom.get`、`archive.is_file`、`sha`、`Path`、`unpack`、`manifest`等。 返回路径：L322的`{ "ready": True, "contract_preserved": True, "delivery_sha256": result["sha256"], "plan_sh…`。
- `aggregate`（L343–L368）：接收`cases`、`results`。 控制顺序：L344按`len(results) != len(cases) or {result.get("case") for result in results} != { case.id…`分支；L348遍历`cases`；L350按`not ( result.get("passed") is True and result.get("source_digest") == case.source_dig…`分支。 调用`len`、`result.get`、`next`、`item.get`、`type`、`set`、`result.get("cleanroom", {}).get`、`result.get("scenario", {}).get`、`result.get("scenario", {}).get("browser", {}).get`。 返回路径：L347的`False`；L367的`False`；L368的`True`。
- `run_suite`（L371–L491）：接收`settings`、`directory`、`binding`。 控制顺序：L426遍历`cases`；L428遍历`assignments.items()`；L430按`run_id in processed or run["status"] in {"QUEUED", "RUNNING"}`分支；L464按`run.get("error")`分支。 调用`suite_cases`、`len`、`REPORTS.mkdir`、`BoundedTransport`、`Store`、`store.migrate`、`store.create_batch`、`require`、`zip`等。 返回路径：L482的`summary`。
- `main`（L494–L552）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L502按`args.validate_fixtures`分支；L529按`binding and (REPORTS / "summary.json").is_file()`分支；L531按`saved.get("run_identity") == binding`分支；L552抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`suite_cases`、`print`、`json.dumps`、`json.loads`、`Path(os.environ["GITHUB_EVENT_PATH"]).read_text`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_template_projects.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L556。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`23179`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_template_projects.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4aa0f0ce86779f1d86f6ce410236191ab8cf06be7583a3f17e0207d909dcba8e"} -->
````python
# scripts/ci_template_projects.py
"""Bounded real-model batch acceptance for three independent project scenarios.

Only reviewed same-repository label events or manual dispatches can use secrets.
All three requirements enter the ordinary batch queue, LangGraph, LangChain,
approval, generation, browser, and clean-delivery gates. There is no fixture-model
mode, fixed-Plan fallback, automatic rerun, or success inferred from model prose.
"""

import argparse
import hmac
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import httpx
from pydantic import SecretStr, ValidationError

from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require,
    require_contract,
    suite_cases,
)
from scripts.template_acceptance_runtime import run_scenario
from workbench.domain import digest
from workbench.filesystem import manifest, sha, unpack, write_json
from workbench.llm import ModelGateway
from workbench.model_diagnostics import schema_diagnostics
from workbench.model_protocol import (
    OutputFailure,
    completion_content,
    output_contract,
    validate_content,
)
from workbench.runtime import Runtime
from workbench.settings import ROOT, STAGES, Settings
from workbench.store import Store
from workbench.verification import product_interpreter, require_browser_evidence

REPOSITORY = "Live-yum/ai-rnd-foundation-learning"
MAX_MODEL_CALLS = 12
MAX_OUTPUT_TOKENS = 16384
REPORTS = ROOT / "reports/template-project-acceptance"
MODEL_STAGES = {"requirement", "recommend", "plan", "coding", "review"}


def trusted_event(env, event):
    """Bind every receipt and every credential-bearing request to the checked-out head."""
    require(
        env.get("GITHUB_ACTIONS") == "true" and env.get("GITHUB_REPOSITORY") == REPOSITORY,
        "untrusted_runner",
    )
    head = env.get("ACCEPTANCE_HEAD_SHA", "")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", head)), "invalid_head_sha")
    if env.get("GITHUB_EVENT_NAME") == "pull_request":
        pr = event.get("pull_request", {})
        require(
            event.get("action") == "labeled"
            and event.get("label", {}).get("name") == "run-live-acceptance"
            and pr.get("head", {}).get("repo", {}).get("full_name") == REPOSITORY
            and pr.get("base", {}).get("repo", {}).get("full_name") == REPOSITORY
            and pr.get("head", {}).get("sha") == head,
            "untrusted_pull_request",
        )
    else:
        require(
            env.get("GITHUB_EVENT_NAME") == "workflow_dispatch" and env.get("GITHUB_SHA") == head,
            "untrusted_dispatch",
        )
    return {
        "repository": REPOSITORY,
        "head_sha": head,
        "run_id": env.get("GITHUB_RUN_ID", ""),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT", ""),
        "event": env["GITHUB_EVENT_NAME"],
    }


def acceptance_settings(env, directory):
    for name in ("BASE_URL", "MODE", "API_KEY"):
        require(
            isinstance(env.get(name), str) and bool(env[name].strip()),
            "missing_configuration",
            name,
        )
    url, model, key = (
        env["BASE_URL"].strip().rstrip("/"),
        env["MODE"].strip(),
        SecretStr(env["API_KEY"].strip()),
    )
    settings = Settings(
        data_dir=Path(directory) / "platform",
        database_url="",
        checkpoint_url="",
        base_url=url,
        MODE=model,
        api_key=key,
        provider="compatible",
        output_mode="json_object",
        max_output_tokens=MAX_OUTPUT_TOKENS,
        allow_insecure_model_http=env.get("ALLOW_INSECURE_MODEL_HTTP", "").lower() == "true",
        **{
            stage + suffix: value
            for stage in STAGES
            for suffix, value in (
                ("_base_url", "" if stage == "review" else url),
                ("_model", "" if stage == "review" else model),
                ("_api_key", SecretStr("") if stage == "review" else key),
                ("_provider", "compatible"),
                ("_output_mode", "json_object"),
                ("_max_output_tokens", MAX_OUTPUT_TOKENS),
            )
        },
        install_products=True,
        model_review=False,
        tool_timeout=900,
        llm_timeout=180,
        max_model_calls=MAX_MODEL_CALLS,
        max_rounds=5,
        max_repair_attempts=1,
        max_context_chars=160000,
        coding_engine="bounded",
        repo_map_provider="symbols",
        retrieval_engine="local",
        embedding_enabled=False,
        sandbox_provider="local",
        _env_file=None,
    )
    for stage in STAGES:
        settings.model_for(stage).validate_endpoint()
    return settings


class BoundedTransport(httpx.BaseTransport):
    """Count actual provider requests, including failures, without retaining their text."""

    def __init__(self, settings):
        self.settings = settings
        self.inner = httpx.HTTPTransport(retries=0, trust_env=False)
        self.run_id, self.stage, self.schema = None, None, None
        self.calls = Counter()
        self.receipts = []

    def handle_request(self, request):
        body = json.loads(request.read())
        profile = self.settings.model_for("planning")
        tokens = [body[key] for key in ("max_tokens", "max_completion_tokens") if key in body]
        if not (
            self.run_id
            and self.stage in MODEL_STAGES
            and request.method == "POST"
            and str(request.url) == profile.base_url + "/chat/completions"
            and body.get("model") == profile.model
            and body.get("response_format") == {"type": "json_object"}
            and body.get("stream", False) is False
            and tokens
            and all(type(value) is int and 0 < value <= MAX_OUTPUT_TOKENS for value in tokens)
            and hmac.compare_digest(
                request.headers.get("Authorization", ""),
                "Bearer " + profile.api_key.get_secret_value(),
            )
            and self.calls[self.run_id] < MAX_MODEL_CALLS
            and sum(self.calls.values()) < MAX_MODEL_CALLS * 3
        ):
            raise OutputFailure("acceptance_request_scope", "验收模型请求超出明确配置或预算")
        self.calls[self.run_id] += 1
        receipt = {"run_id": self.run_id, "stage": self.stage, "http_status": None}
        self.receipts.append(receipt)
        response = self.inner.handle_request(request)
        receipt["http_status"] = response.status_code
        payload = bytearray()
        try:
            for chunk in response.iter_bytes():
                payload.extend(chunk)
                if len(payload) > 2_000_000:
                    raise OutputFailure("acceptance_response_limit", "模型响应超过验收字节上限")
        finally:
            response.close()
        try:
            envelope = json.loads(payload)
            usage = envelope.get("usage", {})
            receipt["usage"] = (
                {
                    key: value
                    for key, value in usage.items()
                    if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
                    and type(value) is int
                    and 0 <= value <= 100_000_000
                }
                if isinstance(usage, dict)
                else {}
            )
            reason = envelope["choices"][0].get("finish_reason")
            receipt["finish_reason"] = (
                reason
                if reason in {"stop", "length", "content_filter", "tool_calls"}
                else "unknown"
            )
            if self.schema is not None and response.status_code == 200:
                contract = output_contract(profile, self.schema)
                try:
                    content, _, _ = completion_content(envelope, contract)
                    validate_content(content, self.schema, mode=contract.mode)
                    receipt["schema_valid"] = True
                except ValidationError as error:
                    receipt.update(schema_valid=False, validation_code="schema_validation")
                    receipt["schema_diagnostics"] = schema_diagnostics(error, self.schema)[:8]
                except OutputFailure as error:
                    receipt.update(schema_valid=False, validation_code=error.code)
                except ValueError, KeyError, IndexError, AttributeError, TypeError:
                    receipt.update(schema_valid=False, validation_code="invalid_json")
        except ValueError, KeyError, IndexError, AttributeError, TypeError:
            receipt["envelope_valid"] = False
        headers = {
            key: value
            for key, value in response.headers.items()
            if key not in {"content-encoding", "content-length"}
        }
        return httpx.Response(response.status_code, headers=headers, content=bytes(payload))

    def close(self):
        pass  # Model clients share this suite-owned pool.

    def shutdown(self):
        self.inner.close()


class ObservedGateway(ModelGateway):
    def __init__(self, settings, store, transport):
        super().__init__(settings, store, transport)
        self.traces = []

    def complete(self, run_id, key, instruction, payload, schema):
        stage = key.split(":", 1)[0]
        self.transport.run_id, self.transport.stage, self.transport.schema = run_id, stage, schema
        trace = {
            "run_id": run_id,
            # Autonomous requirement analysis uses the real recommend:N request key.
            # Keep that wire-stage in transport receipts, and normalize the logical gate.
            "stage": "requirement"
            if stage == "recommend"
            else stage
            if stage in MODEL_STAGES
            else "unknown",
            "validated": False,
        }
        self.traces.append(trace)
        result = super().complete(run_id, key, instruction, payload, schema)
        trace["validated"] = True
        return result


def failure_events(store, run_id, settings):
    """Keep bounded diagnostics already authored by the platform, never response text."""
    failures, after, used = [], 0, 0
    for _ in range(4):
        events = store.events(run_id, after=after)
        if not events:
            break
        after = events[-1]["id"]
        for event in events:
            if event["kind"] not in {"model_failure", "assistant_failed"}:
                continue
            data = settings.redact_data(event["data"])
            diagnostic = data.get("diagnostic", {})
            item = {"kind": event["kind"]}
            for key in ("stage", "code", "request_id", "response_id", "attempt"):
                value = data.get(key, diagnostic.get(key))
                if isinstance(value, str):
                    item[key] = value[:100]
                elif type(value) is int:
                    item[key] = value
            details = [
                {key: detail[key] for key in ("type", "path", "constraints") if key in detail}
                for detail in diagnostic.get("details", [])[:8]
                if isinstance(detail, dict)
            ]
            if len(json.dumps(details, ensure_ascii=False)) <= 3000:
                item["details"] = details
            size = len(json.dumps(item, ensure_ascii=False))
            if used + size > 12000 or len(failures) >= MAX_MODEL_CALLS * 2:
                return failures
            failures.append(item)
            used += size
    return failures


def verify_delivery(case, run, settings, directory):
    result = run["result"]
    require(run["status"] == "READY", "workflow_not_ready")
    require(
        result.get("validation_level") == "runtime" and result.get("isolated_dependencies") is True,
        "delivery_not_isolated",
    )
    cleanroom = result.get("cleanroom", {})
    require(
        all(cleanroom.get(key) is True for key in ("passed", "http", "restart")),
        "cleanroom_incomplete",
    )
    archive = settings.data_dir / "runs" / run["id"] / "delivery.zip"
    require(archive.is_file() and sha(archive) == result["sha256"], "delivery_digest")
    product = Path(directory) / case.identity / "delivered-product"
    unpack(archive, product, template="python-basic")
    require(manifest(product) == result["files"], "delivered_source_mismatch")
    spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
    plan = require_contract(case, spec)
    require_browser_evidence(product, cleanroom)
    require(cleanroom.get("browser", {}).get("real_browser") is True, "cleanroom_browser_missing")
    python = product_interpreter(product, settings)
    scenario = run_scenario(
        case, product, python, Path(directory) / case.identity / "scenario", REPORTS / "screenshots"
    )
    require(manifest(product) == result["files"], "scenario_changed_delivered_source")
    require(
        scenario["browser"]["real_browser"] is True and scenario["browser"]["passed"] is True,
        "scenario_browser_missing",
    )
    return {
        "ready": True,
        "contract_preserved": True,
        "delivery_sha256": result["sha256"],
        "plan_sha256": digest(plan.model_dump(mode="json")),
        "entities": len(plan.entities),
        "roles": len(plan.business.roles) if plan.business else 1,
        "workflows": len(plan.business.workflows) if plan.business else 0,
        "relations": len(plan.business.relations) if plan.business else 0,
        "metrics": len(plan.business.metrics) if plan.business else 0,
        "cleanroom": {
            "passed": True,
            "http": True,
            "real_browser": True,
            "restart": True,
            "isolated_dependencies": True,
        },
        "scenario": scenario,
    }


def aggregate(cases, results):
    if len(results) != len(cases) or {result.get("case") for result in results} != {
        case.identity for case in cases
    }:
        return False
    for case in cases:
        result = next(item for item in results if item.get("case") == case.identity)
        if not (
            result.get("passed") is True
            and result.get("source_digest") == case.source_digest
            and result.get("ready") is True
            and result.get("contract_preserved") is True
            and type(result.get("model_calls")) is int
            and 2 <= result["model_calls"] <= MAX_MODEL_CALLS
            and result.get("provider_http_calls") == result["model_calls"]
            and {"requirement", "plan"} <= set(result.get("completed_model_stages", []))
            and result.get("cleanroom", {}).get("passed") is True
            and result.get("cleanroom", {}).get("real_browser") is True
            and result.get("scenario", {}).get("passed") is True
            and result.get("scenario", {}).get("restart") is True
            and set(result.get("scenario", {}).get("checks", [])) == set(case.expected_checks)
            and result.get("scenario", {}).get("browser", {}).get("passed") is True
            and result.get("scenario", {}).get("browser", {}).get("real_browser") is True
        ):
            return False
    return True


def run_suite(settings, directory, binding):
    cases = suite_cases()
    summary = {
        "version": 1,
        "passed": False,
        "real_model": False,
        "run_identity": binding,
        "selection": {"template": "python-basic", "frontend": "simple-admin", "database": "sqlite"},
        "endpoint": settings.base_url,
        "model": settings.model,
        "budget": {
            "max_model_calls_per_case": MAX_MODEL_CALLS,
            "max_model_calls_total": MAX_MODEL_CALLS * len(cases),
            "max_output_tokens_per_call": MAX_OUTPUT_TOKENS,
        },
        "scope": "Six-entity business complexity; not production load or native-template acceptance",
        "native_templates_exercised": [],
        "model_review_exercised": False,
        "cases": [],
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    transport = BoundedTransport(settings)
    store = Store(settings)
    try:
        store.migrate()
        batch_input = {
            "items": [
                {
                    "title": case.title,
                    "requirement": case.requirement,
                    "template": "python-basic",
                    "selection": summary["selection"],
                    "intelligent": True,
                    "allow_custom_extensions": False,
                }
                for case in cases
            ]
        }
        batch = store.create_batch(batch_input, "live-three-projects")
        require(len(batch["items"]) == len(cases), "batch_incomplete")
        assignments = {
            item["run_id"]: case for item, case in zip(batch["items"], cases, strict=True)
        }
        require(len(assignments) == len(cases), "batch_duplicate_run")
        require(
            store.create_batch(batch_input, "live-three-projects") == batch, "batch_not_idempotent"
        )
        summary["batch"] = {
            "created_projects": len(cases),
            "distinct_runs": len(assignments),
            "idempotent_replay": True,
        }
        gateway = ObservedGateway(settings, store, transport)
        processed = set()
        with Runtime(settings, store, gateway) as worker:
            for _ in cases:
                require(worker.tick(), "batch_queue_stopped")
                for run_id, case in assignments.items():
                    run = store.get_run(run_id)
                    if run_id in processed or run["status"] in {"QUEUED", "RUNNING"}:
                        continue
                    print(
                        f"Verifying {case.identity}: workflow={run['status']}, provider_calls={transport.calls[run_id]}",
                        flush=True,
                    )
                    receipt = {
                        "case": case.identity,
                        "size": case.size,
                        "title": case.title,
                        "source_digest": case.source_digest,
                        "passed": False,
                        "workflow_status": run["status"],
                        "model_calls": run["model_calls"],
                        "provider_http_calls": transport.calls[run_id],
                        "completed_model_stages": sorted(
                            {
                                trace["stage"]
                                for trace in gateway.traces
                                if trace["run_id"] == run_id and trace["validated"]
                            }
                        ),
                    }
                    try:
                        receipt.update(verify_delivery(case, run, settings, directory))
                        receipt["passed"] = True
                    except Exception as error:
                        receipt["failure"] = {
                            "code": error.code
                            if isinstance(error, AcceptanceFailure)
                            else "acceptance_execution_failed",
                            "path": error.path if isinstance(error, AcceptanceFailure) else "",
                            "error_type": type(error).__name__,
                        }
                        if run.get("error"):
                            receipt["failure"]["workflow_error"] = settings.redact(run["error"])[
                                :2000
                            ]
                    receipt["provider_receipts"] = [
                        {key: value for key, value in item.items() if key != "run_id"}
                        for item in transport.receipts
                        if item["run_id"] == run_id
                    ]
                    receipt["model_failures"] = failure_events(store, run_id, settings)
                    receipt = settings.redact_data(receipt)
                    print(json.dumps(receipt, ensure_ascii=False), flush=True)
                    summary["cases"].append(receipt)
                    processed.add(run_id)
                    write_json(REPORTS / (case.identity + ".json"), receipt)
                    write_json(REPORTS / "summary.json", summary)
        summary["passed"] = aggregate(cases, summary["cases"])
        summary["actual_model_calls"] = sum(transport.calls.values())
        return summary
    finally:
        summary["actual_model_calls"] = sum(transport.calls.values())
        summary["real_model"] = bool(summary["actual_model_calls"])
        summary["model_review_exercised"] = any(
            item["stage"] == "review" for item in transport.receipts
        )
        write_json(REPORTS / "summary.json", summary)
        store.engine.dispose()
        transport.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--validate-fixtures",
        action="store_true",
        help="Validate case structure without model calls or generating a product",
    )
    args = parser.parse_args()
    if args.validate_fixtures:
        cases = suite_cases()
        print(
            json.dumps(
                {
                    "fixture_validation": True,
                    "cases": [case.identity for case in cases],
                    "real_model_executed": False,
                }
            )
        )
        return
    summary = {"version": 1, "passed": False, "real_model": False}
    binding = None
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        binding = trusted_event(os.environ, event)
        checkout = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        require(checkout == binding["head_sha"], "checkout_head_mismatch")
        with tempfile.TemporaryDirectory(prefix="rnd-three-projects-") as temporary:
            settings = acceptance_settings(os.environ, Path(temporary))
            write_json(REPORTS / "summary.json", {**summary, "run_identity": binding})
            summary = run_suite(settings, Path(temporary), binding)
    except Exception as error:
        # If execution already wrote per-case evidence, preserve it on controller failure.
        if binding and (REPORTS / "summary.json").is_file():
            saved = json.loads((REPORTS / "summary.json").read_text(encoding="utf-8"))
            if saved.get("run_identity") == binding:
                summary = saved
        summary.update(
            passed=False,
            controller_failure={
                "code": error.code
                if isinstance(error, AcceptanceFailure)
                else "configuration_or_controller_failure",
                "error_type": type(error).__name__,
            },
        )
    write_json(REPORTS / "summary.json", summary)
    print(
        json.dumps(
            {
                "passed": summary["passed"],
                "cases_completed": len(summary.get("cases", [])),
                "actual_model_calls": summary.get("actual_model_calls", 0),
            }
        )
    )
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
````
