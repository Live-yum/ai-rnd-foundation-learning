"""Opt-in real provider acceptance; only allowlisted evidence leaves the isolated job.

No model fixtures, provider substitutions, secret discovery, or automatic scheduling.
The source files and databases produced during the run are deliberately not artifacts.
"""

import contextlib
import hashlib
import hmac
import json
import logging
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from pydantic import SecretStr

REPOSITORY = "Live-yum/ai-rnd-foundation-learning"
REFS = {"refs/heads/feat/real-model-acceptance"}
PUSH_MARKER = "test: run authorized real-model validation iteration"
ENDPOINT = "https://api.deepseek.com"
MODEL = "deepseek-flash"
MAX_WORKFLOW_CALLS = 16
MAX_COMPLETION_TOKENS = 4096
SMOKE_PAYLOAD = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    "thinking": {"type": "enabled"},
    "reasoning_effort": "high",
    "stream": False,
}
NEWS_REQUEST = (
    "泰拉瑞瑞亚游戏资讯。创建登录后逐用户隔离的个人资讯管理页面，手动录入，支持增删改查。"
    "本次验收的明确字段契约：实体 news；title 为必填文本，1至250字符，可关键词搜索；"
    "body 为必填文本，1至3000字符，也可关键词搜索；published_on 为必填真实日期，"
    "支持单日精确筛选和包含起止日的日期区间；category 为可选枚举，选项资讯、攻略、大神，"
    "可精确筛选。关键词、分类、日期条件必须可以组合，清除条件恢复完整列表。"
    "用户注册登录后只能访问自己的记录，跨用户读写拒绝。"
    "选择 python-basic、simple-admin、SQLite；未明确事项使用智能推荐。"
    "不要增加网站采集、匿名公众访问、支付或其他未要求功能。"
)


class SafeFailure(RuntimeError):
    """Only a code chosen by this harness and numeric HTTP status can be published."""

    def __init__(self, code, status=None, details=None):
        self.code, self.status, self.details = code, status, details
        super().__init__(code)


@dataclass(frozen=True)
class Config:
    base_url: str
    model: str
    key: SecretStr = field(repr=False)


def configuration(env):
    # Presence/match booleans distinguish missing injection from provider errors;
    # no credential value, length, fragment, hash, or raw configuration is exposed.
    names = ("BASE_URL", "MODE", "API_KEY")
    raw = {name: env.get(name, "") for name in names}
    values = {name: value.strip() if isinstance(value, str) else "" for name, value in raw.items()}
    checks = {
        "BASE_URL_present": bool(values["BASE_URL"]),
        "MODE_present": bool(values["MODE"]),
        "API_KEY_present": bool(values["API_KEY"]),
        "BASE_URL_matches_authorized_destination": values["BASE_URL"].rstrip("/") == ENDPOINT,
        "MODE_matches_authorized_model": values["MODE"] == MODEL,
    }
    for name in names:
        if not isinstance(raw[name], str):
            raise SafeFailure("invalid_configuration_type_" + name, details=checks)
        if not values[name]:
            raise SafeFailure("missing_configuration_" + name, details=checks)
    if not checks["BASE_URL_matches_authorized_destination"]:
        raise SafeFailure("configuration_destination_mismatch", details=checks)
    if not checks["MODE_matches_authorized_model"]:
        raise SafeFailure("configuration_model_mismatch", details=checks)
    return Config(values["BASE_URL"].rstrip("/"), values["MODE"], SecretStr(values["API_KEY"]))


def trusted_dispatch(env):
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_REPOSITORY") != REPOSITORY
        or env.get("GITHUB_REF") not in REFS
    ):
        raise SafeFailure("untrusted_dispatch")
    if env.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return
    if env.get("GITHUB_EVENT_NAME") == "push":
        try:
            event = json.loads(Path(env.get("GITHUB_EVENT_PATH", "")).read_text(encoding="utf-8"))
            if (
                event["head_commit"]["message"] == PUSH_MARKER
                and event["after"] == env.get("GITHUB_SHA")
                and event["head_commit"]["id"] == env.get("GITHUB_SHA")
                and bool(env.get("GITHUB_SHA"))
                and event["repository"]["full_name"] == REPOSITORY
            ):
                return
        except OSError, ValueError, KeyError, TypeError:
            pass
    raise SafeFailure("untrusted_dispatch")


class BoundedRealTransport(httpx.BaseTransport):
    """Real HTTPS transport with one authorized destination and a hard call/token budget."""

    def __init__(self, config):
        self.config = config
        self.transport = httpx.HTTPTransport(retries=0)
        self.statuses = []
        self.calls = 0
        self.receipts = []
        self.current_schema = None
        self.current_stage = "smoke"

    def handle_request(self, request):
        if (
            request.method != "POST"
            or str(request.url) != self.config.base_url + "/chat/completions"
            or self.calls >= MAX_WORKFLOW_CALLS + 1
        ):
            raise SafeFailure("request_scope_or_budget")
        body = json.loads(request.read())
        if body.get("model") != self.config.model:
            raise SafeFailure("model_substitution_rejected")
        if not hmac.compare_digest(
            request.headers.get("Authorization", ""),
            "Bearer " + self.config.key.get_secret_value(),
        ):
            raise SafeFailure("unexpected_authorization_header")
        # Preserve the user's exact compatibility smoke payload, including reasoning flags.
        # Token budgeting applies only to the subsequent schema-driven acceptance workflow.
        if body != SMOKE_PAYLOAD:
            body["max_tokens"] = min(
                body.get("max_tokens", MAX_COMPLETION_TOKENS), MAX_COMPLETION_TOKENS
            )
        headers = dict(request.headers)
        headers.pop("content-length", None)
        bounded = httpx.Request(
            "POST", request.url, headers=headers, json=body, extensions=request.extensions
        )
        self.calls += 1
        response = self.transport.handle_request(bounded)
        self.statuses.append(response.status_code)
        body_bytes = bytearray()
        for chunk in response.iter_bytes():
            body_bytes.extend(chunk)
            if len(body_bytes) > 2_000_000:
                response.close()
                raise SafeFailure("provider_response_too_large", response.status_code)
        response.close()
        self.receipts.append(
            response_receipt(
                response.status_code, bytes(body_bytes), self.current_stage, self.current_schema
            )
        )
        response_headers = dict(response.headers)
        response_headers.pop("content-encoding", None)
        response_headers.pop("content-length", None)
        return httpx.Response(
            response.status_code, headers=response_headers, content=bytes(body_bytes)
        )

    def close(self):
        # ModelGateway creates a Client per attempt; the owning harness closes the pool.
        pass

    def shutdown(self):
        self.transport.close()


def response_receipt(status, data, stage, schema=None):
    from pydantic import ValidationError

    receipt = {"http_status": status, "stage": stage}
    try:
        envelope = json.loads(data)
        choice = envelope["choices"][0]
        reason = choice.get("finish_reason")
        receipt["finish_reason"] = (
            reason if reason in {"stop", "length", "content_filter", "tool_calls"} else "unknown"
        )
        content = choice["message"].get("content")
        receipt["content_present"] = isinstance(content, str) and bool(content.strip())
        receipt["reasoning_present"] = bool(choice["message"].get("reasoning_content"))
        receipt["usage"] = {
            key: value
            for key, value in envelope.get("usage", {}).items()
            if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
            and type(value) is int
            and 0 <= value <= 100_000_000
        }
        if schema is not None and isinstance(content, str):
            content = content.strip()
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            try:
                schema.model_validate_json(content)
                receipt["schema_valid"] = True
            except ValidationError as exc:
                receipt["schema_valid"] = False
                # Pydantic error types are library-defined codes, never model text or inputs.
                errors = exc.errors(include_input=False, include_url=False)
                receipt["schema_error_types"] = sorted({e["type"] for e in errors})
                names = set()

                def visit(node):
                    if isinstance(node, dict):
                        names.update(node.get("properties", {}))
                        for value in node.values():
                            visit(value)
                    elif isinstance(node, list):
                        for value in node:
                            visit(value)

                visit(schema.model_json_schema())
                receipt["schema_errors"] = [
                    {
                        "type": e["type"],
                        "field_path": [
                            part if type(part) is int or part in names else "additional_field"
                            for part in e["loc"]
                        ],
                    }
                    for e in errors[:20]
                ]
    except ValueError, KeyError, IndexError, TypeError:
        receipt["response_envelope_valid"] = False
    return receipt


def contract_snapshot(data, requirement=False):
    def identifier(value):
        return (
            value
            if isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", value)
            else "unrecognized"
        )

    def field_summary(value):
        result = {"name": identifier(value.get("field" if requirement else "name"))}
        for name in ("required", "searchable", "filterable", "date_range"):
            if type(value.get(name)) is bool:
                result[name] = value[name]
        for name in ("min_length", "max_length"):
            if type(value.get(name)) is int and 0 <= value[name] <= 20000:
                result[name] = value[name]
        if value.get("kind") in {"text", "integer", "boolean", "date", "enum"}:
            result["kind"] = value["kind"]
        if isinstance(value.get("choices"), list):
            result["choices_count"] = len(value["choices"])
        return result

    if requirement:
        return [field_summary(f) for f in data.get("field_requirements", [])[:128]]
    return [
        {
            "name": identifier(e.get("name")),
            "fields": [field_summary(f) for f in e.get("fields", [])],
        }
        for e in data.get("entities", [])[:8]
    ]


def safe_workflow_details(store, run_id, traces):
    details = {"model_stages": traces}
    if run_id:
        run = store.get_run(run_id)
        state = run.get("status")
        details["terminal_state"] = (
            state
            if state in {"READY", "SOURCE_READY", "FAILED", "BLOCKED", "PAUSED_LIMIT", "REJECTED"}
            else "not_terminal"
        )
        pending = run.get("pending") or {}
        stage = pending.get("stage")
        details["pending_stage"] = (
            stage if stage in {"clarification", "requirements", "design", "delivery"} else None
        )
        details["model_calls"] = run.get("model_calls", 0)
        requirement = (store.latest_revision(run_id, "requirements") or {}).get("requirement", {})
        plan = (store.latest_revision(run_id, "design") or {}).get("plan", {})
        details["valid_plan_present"] = bool(plan)
        details["plan_contract"] = contract_snapshot(plan)
        details["requirement_contract"] = contract_snapshot(requirement, requirement=True)
        error = run.get("error") or ""
        categories = {
            "model_schema_invalid": ("结构化契约",),
            "context_limit": ("上下文过大",),
            "provider_error": ("模型鉴权", "模型地址", "模型请求被拒绝", "模型服务超时"),
            "requirement_coverage": ("设计未覆盖", "已确认字段", "已确认条件", "覆盖不足"),
            "tool_failure": ("工具执行失败",),
            "browser_acceptance": ("浏览器", "browser"),
            "model_budget": ("调用次数", "模型调用预算"),
        }
        details["error_categories"] = [
            code for code, tokens in categories.items() if any(t in error for t in tokens)
        ]
        blocked = (pending.get("data") or {}).get("blocked", [])
        details["coverage_block_count"] = len(blocked) if isinstance(blocked, list) else 0
        paths = {f["name"] for e in details["plan_contract"] for f in e["fields"]}
        details["coverage_fields"] = (
            sorted(
                name
                for name in paths
                if name != "unrecognized"
                and any(name in reason for reason in blocked if isinstance(reason, str))
            )
            if isinstance(blocked, list)
            else []
        )
    return details


def smoke(config, transport):
    """A single bounded genuine request. Provider error bodies are never emitted."""
    try:
        with httpx.Client(
            transport=transport, timeout=120, follow_redirects=False, trust_env=False
        ) as client:
            with client.stream(
                "POST",
                config.base_url + "/chat/completions",
                headers={"Authorization": "Bearer " + config.key.get_secret_value()},
                json=SMOKE_PAYLOAD,
            ) as response:
                status = response.status_code
                if status != 200:
                    code = "model_unavailable" if status == 404 else "provider_rejected"
                    raise SafeFailure(code, status)
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > 131072:
                        raise SafeFailure("smoke_response_too_large", status)
        content = json.loads(data)["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise SafeFailure("invalid_smoke_response", status)
    except httpx.HTTPError:
        raise SafeFailure("provider_transport_failure") from None
    except ValueError, KeyError, IndexError, TypeError:
        raise SafeFailure("invalid_smoke_response") from None
    return {"passed": True, "http_status": status, "actual_provider_request": True}


BROWSER_DRIVER = r"""
const fs = require('node:fs');
const [file, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(file, 'utf8'));
async function main() {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  const errors=[];
  page.on('pageerror', () => errors.push('page_error'));
  try {
    await page.goto(cfg.platform);
    await page.locator('#token').fill(cfg.token);
    await page.locator('#connect button').click();
    await page.locator('#template').selectOption('python-basic');
    await page.locator('#frontend').selectOption('simple-admin');
    await page.locator('#database').selectOption('sqlite');
    await page.locator('#choose').click();
    await page.locator('#project-title').fill('Real-model Terraria acceptance');
    await page.locator('#requirement').fill(cfg.requirement);
    // Exactly one initial delegation, no subsequent approval or retry clicks.
    await page.locator('#initial-smart').check();
    await page.locator('#new-run button').click();
    await page.waitForFunction(() => ['READY','SOURCE_READY','FAILED','BLOCKED','PAUSED_LIMIT','REJECTED']
      .some(s=>document.querySelector('#status').textContent === '状态：'+s), null, {timeout:1500000});
    const state=(await page.locator('#status').innerText()).replace('状态：','');
    const runId=(await page.locator('#run-title').innerText()).split(' ').at(-1);
    fs.writeFileSync(cfg.result, JSON.stringify({state,run_id:runId,page_errors:errors.length}));
    if(state!=='READY' || errors.length) throw new Error('workflow_not_ready');
    const download=page.waitForEvent('download');
    await page.locator('#download').click();
    await (await download).saveAs(cfg.download);
  } finally { await browser.close(); }
}
main().catch(()=> { console.error('real-model browser acceptance did not complete'); process.exitCode=1; });
"""


def require_news_spec(spec):
    try:
        assert spec["data_scope"] == "per_user" and not spec["unsupported"]
        assert len(spec["entities"]) == 1
        entity = spec["entities"][0]
        assert entity["name"] == "news"
        fields = {item["name"]: item for item in entity["fields"]}
        assert set(fields) == {"title", "body", "published_on", "category"}
        for name, length in (("title", 250), ("body", 3000)):
            f = fields[name]
            assert f["kind"] == "text" and f["required"] is True
            assert f["max_length"] == length and f["min_length"] == 1
            assert f["searchable"] is True
        date = fields["published_on"]
        assert date["kind"] == "date" and date["required"] is True
        assert date["filterable"] is True and date["date_range"] is True
        category = fields["category"]
        assert category["kind"] == "enum" and category["required"] is False
        assert set(category["choices"]) == {"资讯", "攻略", "大神"}
        assert category["filterable"] is True
    except KeyError, TypeError, AssertionError:
        raise SafeFailure("explicit_news_obligation_not_preserved") from None


def acceptance_settings(config, directory):
    from workbench.settings import STAGES, Settings

    return Settings(
        data_dir=directory / "private-platform",
        database_url="",
        checkpoint_url="",
        base_url=config.base_url,
        api_key=config.key,
        MODE=config.model,
        **{
            stage + suffix: value
            for stage in STAGES
            for suffix, value in (
                ("_base_url", config.base_url),
                ("_api_key", config.key),
                ("_model", config.model),
            )
        },
        install_products=True,
        tool_timeout=600,
        model_review=True,
        llm_timeout=90,
        max_model_calls=MAX_WORKFLOW_CALLS,
        max_rounds=5,
        max_repair_attempts=1,
        coding_engine="bounded",
        repo_map_provider="symbols",
        retrieval_engine="local",
        embedding_enabled=False,
        sandbox_provider="local",
        _env_file=None,
    )


def run_acceptance(config, transport, directory):
    import uvicorn
    from workbench.api import create_app
    from workbench.filesystem import unpack, write_json
    from workbench.llm import ModelGateway
    from workbench.settings import ROOT
    from workbench.tools import clean_env
    from workbench.verification import product_interpreter, require_browser_evidence, run_probe

    settings = acceptance_settings(config, directory)
    traces = []

    class ObservedGateway(ModelGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            stage = key.split(":")[0]
            stage = (
                stage
                if stage in {"requirement", "recommend", "plan", "coding", "review"}
                else "unknown"
            )
            transport.current_schema, transport.current_stage = schema, stage
            trace = {"stage": stage, "completed": False}
            traces.append(trace)
            value = super().complete(run_id, key, instruction, payload, schema)
            trace["completed"] = True
            for name in (
                "questions",
                "unsupported",
                "uncovered_requirements",
                "field_requirements",
            ):
                if hasattr(value, name):
                    trace[name + "_count"] = len(getattr(value, name))
            return value

    application = create_app(
        settings, gateway_factory=lambda store: ObservedGateway(settings, store, transport)
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            application, host="127.0.0.1", port=port, log_level="critical", access_log=False
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        for _ in range(150):
            if server.started:
                break
            time.sleep(0.1)
        else:
            raise SafeFailure("platform_start_failed")
        driver = directory / "browser.cjs"
        driver.write_text(BROWSER_DRIVER, encoding="utf-8")
        result_path, archive = directory / "browser-result.json", directory / "download.zip"
        cfg = directory / "browser-private.json"
        write_json(
            cfg,
            {
                "platform": f"http://127.0.0.1:{port}",
                "token": application.state.token,
                "requirement": NEWS_REQUEST,
                "download": str(archive),
                "result": str(result_path),
            },
        )
        module = os.environ.get(
            "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
        )
        process = subprocess.run(
            ["node", str(driver), str(cfg), module],
            cwd=ROOT,
            env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
            capture_output=True,
            timeout=1560,
            check=False,
        )
        if process.returncode or not result_path.is_file():
            last = next((s for s in reversed(transport.statuses) if s >= 400), None)
            run_id = None
            if result_path.is_file():
                run_id = json.loads(result_path.read_text(encoding="utf-8")).get("run_id")
            raise SafeFailure(
                "workflow_not_ready",
                last,
                safe_workflow_details(application.state.store, run_id, traces),
            )
        browser = json.loads(result_path.read_text(encoding="utf-8"))
        run = application.state.store.get_run(browser["run_id"])
        if run["status"] != "READY" or not run["auto_mode"] or not archive.is_file():
            raise SafeFailure("delivery_not_ready")
        if hashlib.sha256(archive.read_bytes()).hexdigest() != run["result"]["sha256"]:
            raise SafeFailure("download_integrity_failed")
        product = directory / "downloaded-product"
        unpack(archive, product)
        require_news_spec(json.loads((product / "approved-spec.json").read_text(encoding="utf-8")))
        if not run["result"]["cleanroom"].get("passed"):
            raise SafeFailure("pipeline_cleanroom_failed")
        require_browser_evidence(product, run["result"]["cleanroom"])
        # A fresh environment and database validate the bytes actually downloaded through the UI.
        python = product_interpreter(product, settings)
        probe = directory / "downloaded-product-verification.json"
        run_probe(product, python, probe, settings)
        evidence = json.loads(probe.read_text(encoding="utf-8"))
        require_browser_evidence(product, evidence)
        if evidence.get("passed") is not True or evidence.get("restart") is not True:
            raise SafeFailure("downloaded_cleanroom_failed")
        return {
            "passed": True,
            "real_model": True,
            "single_initial_smart_consent": True,
            "explicit_news_obligations_preserved": True,
            "ready": True,
            "ui_download": True,
            "download_hash_matches": True,
            "independent_database": True,
            "real_browser": True,
            "restart": True,
            "model_calls": run["model_calls"],
            "page_errors": browser["page_errors"],
            "aider_edit": "not_exercised",
            "continue_native_index": "not_exercised",
            "daytona": "not_exercised",
            "old_blocked_recovery": "not_exercised_in_real_run",
        }
    finally:
        server.should_exit = True
        thread.join(timeout=120)


def verified_smoke_receipt(path, config, env):
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["passed"] is True and saved["acceptance_scope"] == "smoke_only"
        assert saved["smoke"] == {
            "passed": True,
            "http_status": 200,
            "actual_provider_request": True,
        }
        assert saved["actual_http_calls"] == 1 and saved["provider_statuses"] == [200]
        assert saved["model"] == config.model and saved["endpoint"] == config.base_url
        assert saved["run_identity"] == [
            env.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
        ]
        return saved["smoke"]
    except OSError, ValueError, KeyError, AssertionError, TypeError:
        raise SafeFailure("missing_matching_successful_smoke") from None


def main():
    import argparse

    from workbench.settings import ROOT

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "full"], required=True)
    mode = parser.parse_args().phase
    destination = ROOT / "reports/real-model"
    summary = destination / "summary.json"
    result = {
        "passed": False,
        "real_provider_attempted": False,
        "acceptance_scope": "smoke_only" if mode == "smoke" else "full_workflow",
    }
    transport = None
    config = None
    phase = "configuration"
    prior_calls = 0
    try:
        trusted_dispatch(os.environ)
        config = configuration(os.environ)
        # Never inherit the provider credential into browser/uv/product child processes.
        os.environ.pop("API_KEY", None)
        result.update(
            model=config.model,
            endpoint=config.base_url,
            run_identity=[
                os.environ.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
            ],
        )
        if mode == "full":
            result["smoke"] = verified_smoke_receipt(summary, config, os.environ)
            prior_calls = 1
        transport = BoundedRealTransport(config)
        with tempfile.TemporaryDirectory(prefix="rnd-real-model-") as private:
            # Suppress raw application/provider tracebacks and model-generated text.
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as quiet:
                logging.disable(logging.CRITICAL)
                with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                    result["real_provider_attempted"] = True
                    if mode == "smoke":
                        phase = "smoke"
                        result["smoke"] = smoke(config, transport)
                    else:
                        phase = "workflow"
                        result["workflow"] = run_acceptance(config, transport, Path(private))
        result["passed"] = True
    except SafeFailure as exc:
        result.update(failure_phase=phase, failure_code=exc.code)
        if exc.status is not None:
            result["provider_status"] = exc.status
        if exc.details is not None:
            result["configuration_checks" if "configuration" in exc.code else "failure_details"] = (
                exc.details
            )
    except Exception:
        result.update(failure_phase=phase, failure_code="acceptance_execution_failed")
    finally:
        if transport:
            result["actual_http_calls"] = prior_calls + transport.calls
            result["provider_statuses"] = ([200] if prior_calls else []) + transport.statuses
            result["provider_receipts"] = transport.receipts
            with contextlib.suppress(Exception):
                transport.shutdown()
        destination.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(result, indent=2)
        if config is not None:
            rendered = rendered.replace(config.key.get_secret_value(), "[REDACTED]")
        summary.write_text(rendered, encoding="utf-8")
    print(rendered)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
