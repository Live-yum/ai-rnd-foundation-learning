# scripts/ci_live_modules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_live_modules；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.live_test_client`、`scripts.sla_fixture`、`workbench.filesystem`、`workbench.planning.feature_planner`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `failure_diagnostic`（L32–L79）：接收`exc`。 源码说明：Only fixed labels and trusted-code line numbers, never traceback text/locals.。 控制顺序：L72在`frame is not None`成立时循环；L74按`stage is not None`分支；L77按`type(exc) is ContainerInspectionRejected`分支。 调用`names.get`、`type`、`str`、`stages.items`、`trusted.get`、`result.update`、`ContainerInspectionRejected.diagnostic`。 返回路径：L79的`result`。
- `require`（L82–L84）：接收`condition`、`code`。 控制顺序：L83按`not condition`分支；L84抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `configuration`（L87–L140）：接收`env`。 源码说明：No secret access or network: validate the dispatch and conservative ceiling.。 控制顺序：L117按`billing == "declared_free"`分支；L127抛异常，停止当前正常路径。 调用`env.get`、`require`、`re.fullmatch`、`env.get("BASE_URL", "").strip().rstrip`、`env.get("BASE_URL", "").strip`、`urlsplit`、`bool`、`env.get("MODE", "").strip`、`Decimal`等。 返回路径：L128的`{ "head_sha": head, "scenario": SCENARIO, "billing": zero_billing(env) if billing == "decl…`。
- `acceptance_design`（L143–L185）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Keep trusted assertions outside model control, strengthen isolation and restart.。 控制顺序：L150遍历`scenarios`。 调用`design().model_dump`、`design`、`next`、`steps.index`、`steps.extend`、`scenario["after_restart"].append`、`FeatureDesign.model_validate`。 返回路径：L185的`FeatureDesign.model_validate(data)`。
- `live_settings`（L188–L224）：接收`env`、`config`、`directory`。 调用`require`、`bool`、`env.get("API_KEY", "").strip`、`env.get`、`Settings`、`env["BASE_URL"].strip().rstrip`、`env["BASE_URL"].strip`、`env["MODE"].strip`、`SecretStr`等。 返回路径：L197的`Settings( _env_file=HOME / "workbench.env", data_dir=directory / "platform", database_url=…`。
- `execute`（L227–L347）：接收`settings`、`directory`、`transport`、`progress`。 控制顺序：L268遍历`plan.tasks`；L343按`progress is not None and run_id`分支。 调用`acceptance_design`、`plan.selection.model_dump`、`require`、`worker_python().is_file`、`worker_python`、`capability_execution_prerequisites`、`Store`、`store.migrate`、`store.create_project`等。 返回路径：L328的`{ "real_model_calls": calls, "tokens_reserved": sum(b["tokens_reserved"] for b in budgets)…`。
- `main`（L350–L391）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L365按`not args.preflight`分支；L389抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`configuration`、`summary.update`、`tempfile.TemporaryDirectory`、`Path`、`TestServiceTransport`、`os.environ.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_live_modules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L395。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16403`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_live_modules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "980cce51364e43fe212574dfb781a32df7a620fd73924c7b624e763d33d121d4"} -->
````python
# scripts/ci_live_modules.py
"""Manual HTTPS executor acceptance; reviewed plans, real models, real isolation.

This is not live requirement planning or full LangGraph/Gate crash recovery.
No authored implementation, mock transport or local execution fallback is used.
"""

import argparse
import json
import os
import re
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

from scripts.live_test_client import TestServiceTransport, zero_billing
from scripts.sla_fixture import design
from workbench.filesystem import manifest, pack_source, unpack, write_json
from workbench.planning.feature_planner import FeatureDesign
from workbench.settings import ROOT

REPOSITORY = "Live-yum/ai-rnd-foundation-learning"
SCENARIO = "mini-swe-sla"
OUTPUT_TOKENS = 8192
CONTEXT_CHARS = 40000
STEPS_PER_TASK = 8
TOKENS_PER_TASK = 2_000_000
MODEL_CALLS = 32  # Two modules, eight steps each, at most two gateway attempts.
REPORT = ROOT / "reports/live-modules/summary.json"


def failure_diagnostic(exc):
    """Only fixed labels and trusted-code line numbers, never traceback text/locals."""
    from workbench.capability_isolation import ContainerInspectionRejected

    stages = {
        "scripts/ci_live_modules.py": "acceptance_controller",
        "workbench/coding/mini_swe.py": "agent_controller",
        "workbench/infrastructure/sandbox/coding.py": "coding_sandbox",
        "workbench/capability_execution.py": "isolation_admission",
        "scripts/daytona_capability_profile.py": "container_inspection",
        "workbench/capability_isolation.py": "container_evidence",
        "workbench/infrastructure/llm/gateway.py": "model_gateway",
        "workbench/coding/candidates.py": "candidate_application",
        "workbench/production/candidates.py": "product_ledger",
        "workbench/capability_sandbox.py": "independent_verification",
    }
    # Membership produces a fixed value; unknown/provider-defined names are suppressed.
    names = {
        name: name
        for name in (
            "ValueError",
            "TypeError",
            "KeyError",
            "RuntimeError",
            "OSError",
            "FileNotFoundError",
            "PermissionError",
            "TimeoutError",
            "ValidationError",
            "UnsupportedScope",
            "ModelFailure",
            "IsolationUnavailable",
            "ContainerInspectionRejected",
            "DaytonaError",
            "DaytonaNotFoundError",
        )
    }
    result = {"exception_type": names.get(type(exc).__name__, "other"), "stage": "other"}
    trusted = {str(ROOT / path): stage for path, stage in stages.items()}
    frame = exc.__traceback__
    while frame is not None:
        stage = trusted.get(frame.tb_frame.f_code.co_filename)
        if stage is not None:
            result.update(stage=stage, trusted_source_line=frame.tb_lineno)
        frame = frame.tb_next
    if type(exc) is ContainerInspectionRejected:
        result["container"] = ContainerInspectionRejected.diagnostic(exc)
    return result


def require(condition, code):
    if not condition:
        raise ValueError(code)


def configuration(env):
    """No secret access or network: validate the dispatch and conservative ceiling."""
    head = env.get("GITHUB_SHA", "")
    require(
        env.get("GITHUB_ACTIONS") == "true"
        and env.get("GITHUB_REPOSITORY") == REPOSITORY
        and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        and env.get("GITHUB_RUN_ATTEMPT") == "1"
        and re.fullmatch(r"[a-f0-9]{40}", head)
        and env.get("REVIEWED_SHA") == head
        and env.get("LIVE_SCENARIO") == SCENARIO,
        "reviewed_first_manual_dispatch_required",
    )
    endpoint = env.get("BASE_URL", "").strip().rstrip("/")
    url = urlsplit(endpoint)
    require(
        url.scheme == "https"
        and url.hostname
        and not url.username
        and not url.password
        and not url.query
        and not url.fragment,
        "https_endpoint_required",
    )
    require(bool(env.get("MODE", "").strip()), "model_required")
    billing = env.get("LIVE_BILLING_MODE", "metered")
    require(billing in {"metered", "declared_free"}, "unknown_billing_mode")
    try:
        cost = Decimal(env.get("LIVE_MAX_COST_USD", "0"))
        price = Decimal(env.get("LIVE_USD_PER_MILLION_TOKENS", "0"))
        if billing == "declared_free":
            zero_billing(env)
            require(cost == price == 0, "zero_billing_requires_zero_prices")
        else:
            require(cost.is_finite() and 0 < cost <= 10, "cost_ceiling_required")
            require(price.is_finite() and 0 < price <= 10000, "conservative_tariff_required")
        # Each module needs at least an edit and a submit. Reserve both gateway attempts.
        minimum = Decimal(2 * 2 * (4 * CONTEXT_CHARS + OUTPUT_TOKENS)) * price / 1_000_000
        require(cost / 2 >= minimum, "budget_cannot_cover_two_turns_per_module")
    except InvalidOperation:
        raise ValueError("invalid_cost_configuration") from None
    return {
        "head_sha": head,
        "scenario": SCENARIO,
        "billing": zero_billing(env) if billing == "declared_free" else {"mode": "metered"},
        "max_cost_usd": float(cost),
        "usd_per_million_tokens": float(price),
        "max_model_calls": MODEL_CALLS,
        "max_output_tokens": OUTPUT_TOKENS,
        "max_steps_per_module": STEPS_PER_TASK,
        "max_tokens_total": TOKENS_PER_TASK * 2,
        "max_seconds_per_module": 180,
        "job_timeout_minutes": 90,
    }


def acceptance_design():
    """Keep trusted assertions outside model control, strengthen isolation and restart."""
    data = design().model_dump()
    data["implementation"]["runtime"]["prepare"] = [
        {"argv": ["uv", "sync", "--locked", "--offline", "--no-dev", "--python", "3.14"]}
    ]
    scenarios = data["implementation"]["scenarios"]
    for scenario in scenarios:
        steps = scenario["steps"]
        create = next(step for step in steps if step["path"] == "/api/tickets")
        position = steps.index(create) + 1
        variants = [
            {**create, "body": {**create["body"], "status": "resolved"}},
            {**create, "body": {**create["body"], "due_at": "2099-01-01T00:00:00Z"}},
        ]
        steps[position:position] = variants
        register = steps[0]
        outsider = {
            **register,
            "body": {**register["body"], "username": scenario["id"] + "-outsider-${nonce}"},
            "captures": {"outsider": "$.access_token"},
        }
        isolated = {
            "path": "/sla/summary",
            "headers": {"Authorization": "Bearer ${outsider}"},
            "status": 200,
            "equals": {"$.overdue": 0, "$.urgent_overdue": 0},
        }
        steps.extend([outsider, isolated, {"path": "/sla/summary", "status": 401}])
        steps.extend(
            [
                {
                    "method": "POST",
                    "path": "/api/customers",
                    "headers": create["headers"],
                    "body": {"name": "保留基础客户"},
                    "status": 201,
                },
                {"path": "/api/customers", "headers": create["headers"], "status": 200},
            ]
        )
        scenario["after_restart"].append(isolated)
    return FeatureDesign.model_validate(data)


def live_settings(env, config, directory):
    from pydantic import SecretStr

    from scripts.daytona_capability_profile import HOME
    from workbench.settings import Settings

    require(bool(env.get("API_KEY", "").strip()), "model_key_required")
    # The local service's generated file supplies only its own Daytona configuration.
    # Every provider field for the tested coding stage is explicitly pinned here.
    return Settings(
        _env_file=HOME / "workbench.env",
        data_dir=directory / "platform",
        database_url="",
        checkpoint_url="",
        coding_base_url=env["BASE_URL"].strip().rstrip("/"),
        coding_model=env["MODE"].strip(),
        coding_api_key=SecretStr(env["API_KEY"].strip()),
        coding_provider="compatible",
        coding_output_mode="json_object",
        coding_max_output_tokens=OUTPUT_TOKENS,
        allow_insecure_model_http=False,
        mini_swe_enabled=True,
        mini_swe_billing_mode=config["billing"]["mode"],
        mini_swe_zero_billing_ack=config["billing"]["mode"] == "declared_free",
        mini_swe_zero_billing_endpoint=config["billing"].get("endpoint", ""),
        mini_swe_max_tokens=TOKENS_PER_TASK,
        mini_swe_max_cost_usd=config["max_cost_usd"] / 2,
        mini_swe_usd_per_million_tokens=config["usd_per_million_tokens"],
        mini_swe_timeout=180,
        max_model_calls=MODEL_CALLS,
        max_context_chars=CONTEXT_CHARS,
        llm_timeout=60,
        tool_timeout=120,
        daytona_runtime_timeout=600,
        capability_execution_enabled=True,
        capability_profile_directory=HOME,
    )


def execute(settings, directory, *, transport=None, progress=None):
    from workbench.capability_consumer import prepare_consumer, require_consumer_evidence
    from workbench.capability_execution import capability_execution_prerequisites
    from workbench.capability_sandbox import verify_capabilities
    from workbench.coding.candidates import apply_candidate
    from workbench.coding.mini_swe import run_agent, worker_python
    from workbench.generator import generate_basic
    from workbench.llm import ModelGateway
    from workbench.production.candidates import ProductLedger
    from workbench.store import Store

    selected = acceptance_design()
    plan = selected.implementation
    selection = plan.selection.model_dump()
    require(worker_python().is_file(), "locked_worker_required")
    # Same-job real security/browser/profile proof must exist before any paid request.
    capability_execution_prerequisites(settings, selection)
    store = Store(settings)
    run_id = None
    try:
        store.migrate()
        project = store.create_project("Reviewed SLA module acceptance", "live-sla")
        run_id = store.create_run(
            project["id"],
            {
                "requirement": plan.summary,
                "allow_custom_extensions": True,
                "module_executor": "mini_swe",
            },
            "live-sla-run",
        )["run_id"]
        gateway = ModelGateway(settings, store, transport)
        base = directory / "baseline"
        generate_basic(selected.baseline, base, selection)
        prepare_consumer(base, plan)
        frozen_base = manifest(base)
        ledger_path = directory / "ledger"
        ledger = ProductLedger(ledger_path, plan)
        ledger.baseline(base)
        product = base
        budgets = []
        for task in plan.tasks:
            before = manifest(product)
            workspace = directory / (task.id + "-worker")
            edits = run_agent(
                settings,
                gateway,
                run_id,
                task,
                plan,
                product,
                workspace,
                {
                    "baseline": selected.baseline.model_dump(),
                    "interfaces": {
                        "api": "/sla/summary returns overdue and urgent_overdue for the authenticated owner only",
                        "dashboard": "/sla-dashboard uses #username, #password, #login, #load and #result; result text: 逾期 1；紧急逾期 1",
                        "preserve": "Keep existing customers/tickets CRUD and authentication; exclude resolved and future tickets",
                    },
                },
            )
            candidate = directory / (task.id + "-candidate")
            apply_candidate(product, edits, task, selection, candidate)
            proof = verify_capabilities(
                candidate,
                plan,
                [s for s in plan.scenarios if s.id in task.scenarios],
                settings,
                aggregate=False,
                selection=selection,
            )
            promoted = ledger.promote(candidate, task, proof, before)
            # Reopen durable state and replay promotion; this is ledger recovery only.
            calls = store.get_run(run_id)["model_calls"]
            ledger = ProductLedger(ledger_path, plan)
            require(ledger.baseline(base) == promoted, "ledger_reopen_failed")
            require(
                ledger.promote(candidate, task, proof, before) == promoted,
                "promotion_replay_failed",
            )
            require(store.get_run(run_id)["model_calls"] == calls, "recovery_recalled_model")
            budgets.append(json.loads((workspace / "agent-budget.json").read_text()))
            product = candidate
        archive = directory / "delivery.zip"
        pack_source(product, archive, template="python-basic")
        clean = directory / "fresh-consumer"
        unpack(archive, clean, template="python-basic")
        require(manifest(clean) == manifest(product), "zip_source_mismatch")
        proof = verify_capabilities(
            clean,
            plan,
            plan.scenarios,
            settings,
            aggregate=True,
            selection=selection,
        )
        require_consumer_evidence(clean, plan, proof)
        ledger.verified(clean, proof)
        require(manifest(base) == frozen_base, "baseline_changed")
        calls = store.get_run(run_id)["model_calls"]
        require(0 < calls <= MODEL_CALLS, "real_calls_required")
        return {
            "real_model_calls": calls,
            "tokens_reserved": sum(b["tokens_reserved"] for b in budgets),
            "cost_reserved_usd": sum(b["cost_reserved_usd"] for b in budgets),
            "independent_product_acceptance": True,
            "zip_new_directory": True,
            "consumer_cold_start_and_restart": True,
            "ledger_reopen_and_idempotent_replay": True,
            "full_workflow_crash_recovery": False,
            "live_planning_and_approval": False,
            "source_digest": proof["source_digest"],
            "plan_digest": proof["plan_digest"],
            "cleanup": proof["cleanup"],
        }
    finally:
        if progress is not None and run_id:
            progress["model_call_reservations"] = store.get_run(run_id)["model_calls"]
            progress["model_http_attempts"] = transport.calls if transport else 0
            progress["model_http_responses"] = transport.responses if transport else 0
        store.engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    summary = {
        "passed": False,
        "real_model_acceptance": False,
        "scenario": SCENARIO,
        "phase": "configuration",
        "model_http_attempts": 0,
        "model_http_responses": 0,
    }
    try:
        config = configuration(os.environ)
        summary.update(configuration_valid=True, limits=config, phase="preflight")
        if not args.preflight:
            summary["phase"] = "execution"
            with tempfile.TemporaryDirectory(prefix="rnd-live-modules-") as temporary:
                directory = Path(temporary)
                transport = TestServiceTransport(
                    os.environ["BASE_URL"], os.environ.get("LIVE_TEST_CA", "system")
                )
                try:
                    summary.update(
                        execute(
                            live_settings(os.environ, config, directory),
                            directory,
                            transport=transport,
                            progress=summary,
                        )
                    )
                finally:
                    transport.close()
                summary.update(passed=True, real_model_acceptance=True, phase="completed")
    except Exception as exc:
        # Never publish raw provider/SDK errors, generated code, prompts or credentials.
        summary.update(passed=False, real_model_acceptance=False)
        summary["failure"] = "configuration_or_execution_rejected"
        summary["failure_diagnostic"] = failure_diagnostic(exc)
        raise SystemExit(1) from None
    finally:
        write_json(REPORT, summary)


if __name__ == "__main__":
    main()
````
