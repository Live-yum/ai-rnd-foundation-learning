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
        return response

    def close(self):
        # ModelGateway creates a Client per attempt; the owning harness closes the pool.
        pass

    def shutdown(self):
        self.transport.close()


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
    application = create_app(
        settings, gateway_factory=lambda store: ModelGateway(settings, store, transport)
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
            raise SafeFailure("workflow_not_ready", last)
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
            result["configuration_checks"] = exc.details
    except Exception:
        result.update(failure_phase=phase, failure_code="acceptance_execution_failed")
    finally:
        if transport:
            result["actual_http_calls"] = prior_calls + transport.calls
            result["provider_statuses"] = ([200] if prior_calls else []) + transport.statuses
            with contextlib.suppress(Exception):
                transport.shutdown()
        destination.mkdir(parents=True, exist_ok=True)
        summary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
