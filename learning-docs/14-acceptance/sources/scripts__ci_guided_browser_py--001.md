# scripts/ci_guided_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台到资讯产品的浏览器验收协调。** 启动实际工作台与浏览器，显式模型夹具提供资讯需求，检查智能推荐和产物；随后访问真正生成的产品，不将静态HTML当成功。

**对应关系：** browser工作流 → guided_browser.cjs → 实际API/页面/独立交付。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.news_fixture`、`workbench.api`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `free_port`（L31–L34）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L34的`sock.getsockname()[1]`。
- `stream_packets`（L41–L56）：接收`value`、`model`。 源码说明：Real OpenAI wire protocol, including a JSON surrogate split between deltas.。 控制顺序：L51遍历`fragments`。 调用`json.dumps(value, ensure_ascii=False).replace`、`json.dumps`、`content.index`、`prefix.find`、`sorted`、`len`、`zip`、`_stream_packet`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_stream_packet`（L59–L73）：接收`model`、`delta`、`finish`。 调用`( "data: " + json.dumps( { "id": "explicit-fixture", "object": "c…`、`json.dumps`。 返回路径：L60的`( "data: " + json.dumps( { "id": "explicit-fixture", "object": "chat.completion.chunk", "c…`。
- `ui_build_snapshot`（L76–L81）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`str`、`path.relative_to`、`hashlib.sha256(path.read_bytes()).hexdigest`、`hashlib.sha256`、`path.read_bytes`、`sorted`、`(ROOT / "workbench/web").rglob`、`path.is_file`。 返回路径：L77的`{ str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in s…`。
- `main`（L84–L522）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L86断言`"workbench/web/index.html" in build_before and "workbench/web/app.js" in build_before`；L272遍历`range(100)`；L273按`server.started`分支；L277抛异常，停止当前正常路径；L311断言`first.returncode == 0`；L312断言`not failures`；L313断言`first_draft.is_set() and completed.is_set()`；L314断言`all(call["stream"] for call in calls)`。后续分支沿下方源码相同行号继续阅读。 调用`ui_build_snapshot`、`threading.Event`、`ThreadingHTTPServer`、`threading.Thread(target=provider.serve_forever, daemon=True).star…`、`threading.Thread`、`reports.mkdir`、`write_json`、`tempfile.TemporaryDirectory`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider`（L94–L236）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `main.Provider.log_message`（L95–L96）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider.do_GET`（L98–L109）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99按`self.path != "/fixture/status"`分支。 调用`self.send_error`、`self.json_response`、`first_draft.is_set`、`completed.is_set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider.json_response`（L111–L117）：接收`value`、`status`。 调用`json.dumps(value).encode`、`json.dumps`、`self.send_response`、`self.send_header`、`str`、`len`、`self.end_headers`、`self.wfile.write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider.do_POST`（L119–L132）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L120按`self.path == "/fixture/start"`分支；L124按`self.path == "/fixture/release"`分支；L132抛异常，停止当前正常路径。 调用`start_stream.set`、`self.json_response`、`release.set`、`self.model_response`、`failures.append`、`type`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider.model_response`（L134–L236）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L136断言`self.headers["Authorization"] == "Bearer " + FIXTURE_KEY`；L141按`model == "denied-fixture"`分支；L147按`model == "requirements-fixture"`分支；L148按`payload.get("autonomous")`分支；L155按`payload.get("original_request") == "交互选项验收"`分支；L181按`model == "planning-fixture"`分支；L184按`model == "review-fixture"`分支；L191抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`self.rfile.read`、`int`、`calls.append`、`body.get`、`len`、`self.json_response`、`payload.get`、`assert_resolution`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_guided_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L526。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21062`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_guided_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0442407cdc17b789b222565a4ca17d93f06f3846d49ab3433b6c0ffefc5da88a"} -->
````python
# scripts/ci_guided_browser.py
"""Real local HTTP and Chromium regression; model servers are explicit test fixtures only."""

import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import uvicorn

from scripts.news_fixture import (
    ORIGINAL_REQUEST,
    assert_approved,
    assert_resolution,
    news_requirement,
    news_spec,
)
from workbench.api import create_app
from workbench.filesystem import unpack, write_json
from workbench.settings import ROOT, Settings
from workbench.tools import clean_env, process_options, stop_process


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


STREAM_SUMMARY = "泰拉瑞瑞亚游戏资讯的登录后个人管理页面 🧪流式验收"
FIXTURE_KEY = "explicit-ci-only"


def stream_packets(value, model):
    """Real OpenAI wire protocol, including a JSON surrogate split between deltas."""
    content = json.dumps(value, ensure_ascii=False).replace("🧪", r"\ud83e\uddea")
    # A partial JSON object has a usable draft well before its validation can finish.
    boundary = content.index('",', content.index(":") + 2) + 1
    prefix, tail = content[:boundary], content[boundary:]
    surrogate = prefix.find(r"\ud83e")
    cuts = sorted({0, 14, *([surrogate + 4, surrogate + 8] if surrogate >= 0 else []), len(prefix)})
    fragments = [prefix[a:b] for a, b in zip(cuts, cuts[1:]) if prefix[a:b]]
    yield False, _stream_packet(model, {"role": "assistant"})
    for fragment in fragments:
        yield False, _stream_packet(model, {"content": fragment})
    # The caller holds this boundary until the browser sees and acknowledges the draft.
    yield True, _stream_packet(model, {"content": tail})
    yield False, _stream_packet(model, {}, finish="stop")
    yield False, b"data: [DONE]\r\n\r\n"


def _stream_packet(model, delta, finish=None):
    return (
        "data: "
        + json.dumps(
            {
                "id": "explicit-fixture",
                "object": "chat.completion.chunk",
                "created": 1,
                "model": model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            },
            ensure_ascii=False,
        )
        + "\r\n\r\n"
    ).encode("utf-8")


def ui_build_snapshot():
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((ROOT / "workbench/web").rglob("*"))
        if path.is_file()
    }


def main():
    build_before = ui_build_snapshot()
    assert "workbench/web/index.html" in build_before and "workbench/web/app.js" in build_before
    calls = []
    release = threading.Event()
    start_stream = threading.Event()
    first_draft = threading.Event()
    completed = threading.Event()
    failures = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return

        def do_GET(self):
            if self.path != "/fixture/status":
                self.send_error(404)
                return
            self.json_response(
                {
                    "draft_sent": first_draft.is_set(),
                    "completed": completed.is_set(),
                    "calls": calls,
                    "failures": failures,
                }
            )

        def json_response(self, value, status=200):
            encoded = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_POST(self):
            if self.path == "/fixture/start":
                start_stream.set()
                self.json_response({"started": True})
                return
            if self.path == "/fixture/release":
                release.set()
                self.json_response({"released": True})
                return
            try:
                self.model_response()
            except Exception as exc:
                failures.append(type(exc).__name__ + ": " + str(exc))
                raise

        def model_response(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.headers["Authorization"] == "Bearer " + FIXTURE_KEY
            model = body["model"]
            payload = json.loads(body["messages"][1]["content"])
            calls.append({"model": model, "path": self.path, "stream": body.get("stream", False)})
            first = len(calls) == 1
            if model == "denied-fixture":
                self.json_response(
                    {"error": {"code": "invalid_api_key", "message": "Explicit local test denial"}},
                    status=401,
                )
                return
            if model == "requirements-fixture":
                if payload.get("autonomous"):
                    assert_resolution(payload)
                value = news_requirement(
                    payload.get("autonomous", False)
                    or payload.get("original_request") == "人工审批验收"
                )
                value["summary"] = STREAM_SUMMARY
                if payload.get("original_request") == "交互选项验收":
                    value["questions"] = ["这次采用哪种使用方式？", "需要哪些筛选方式？"]
                    value["question_items"] = [
                        {
                            "id": "audience",
                            "prompt": value["questions"][0],
                            "kind": "single",
                            "required": True,
                            "allow_other": True,
                            "options": [
                                {"id": "personal", "label": "个人管理"},
                                {"id": "shared", "label": "团队共用"},
                            ],
                        },
                        {
                            "id": "filters",
                            "prompt": value["questions"][1],
                            "kind": "multiple",
                            "required": True,
                            "allow_other": True,
                            "options": [
                                {"id": "search", "label": "搜索"},
                                {"id": "date", "label": "日期筛选"},
                            ],
                        },
                    ]
            elif model == "planning-fixture":
                assert_approved(payload)
                value = news_spec()
            elif model == "review-fixture":
                value = {
                    "summary": "根据真实测试报告审阅",
                    "observations": [],
                    "uncovered_requirements": [],
                }
            else:
                raise AssertionError("Unexpected model stage for deterministic CRUD: " + model)
            if body.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                if first and not start_stream.wait(60):
                    raise TimeoutError("Browser never attached to the real SSE endpoint")
                for boundary, packet in stream_packets(value, model):
                    if boundary and first:
                        first_draft.set()
                        if not release.wait(60):
                            raise TimeoutError(
                                "Browser never observed the unfinished provider draft"
                            )
                    # Deliberate writes inside UTF-8 codepoints and SSE/JSON boundaries.
                    offset = 0
                    for size in (1, 7, 2, 13, 3, 5, 11) * (len(packet) // 42 + 1):
                        if offset >= len(packet):
                            break
                        self.wfile.write(packet[offset : offset + size])
                        self.wfile.flush()
                        offset += size
                    time.sleep(0.015)
                if first:
                    completed.set()
                return
            encoded = json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(value, ensure_ascii=False),
                            }
                        }
                    ],
                    "usage": {"total_tokens": 50},
                },
                ensure_ascii=False,
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    provider = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=provider.serve_forever, daemon=True).start()
    reports = ROOT / "reports/guided-browser"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "ui-build-start.json", build_before)
    with tempfile.TemporaryDirectory(prefix="guided-browser-") as directory:
        directory = Path(directory)
        port = free_port()
        settings = Settings(
            data_dir=directory / "platform",
            base_url=f"http://127.0.0.1:{provider.server_port}/v1",
            api_key=FIXTURE_KEY,
            MODE="requirements-fixture",
            requirements_model="requirements-fixture",
            planning_model="planning-fixture",
            coding_model="coding-fixture",
            review_model="review-fixture",
            **{
                stage + "_base_url": ""
                for stage in ("requirements", "planning", "coding", "review")
            },
            **{
                stage + "_api_key": "" for stage in ("requirements", "planning", "coding", "review")
            },
            install_products=False,
            retrieval_engine="continue",
            _env_file=None,
        )
        application = create_app(settings)
        server = uvicorn.Server(
            uvicorn.Config(application, host="127.0.0.1", port=port, log_level="error")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        for _ in range(100):
            if server.started:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("Platform did not start")
        browser = Path(
            os.getenv("PRODUCT_VERIFY_PLAYWRIGHT", ROOT / ".native/browser/node_modules/playwright")
        )
        browser_env = clean_env(
            {"PLAYWRIGHT_BROWSERS_PATH": os.getenv("PLAYWRIGHT_BROWSERS_PATH", "0")}
        )
        evidence = directory / "browser-input.json"
        config = {
            "requirement": ORIGINAL_REQUEST,
            "platform": f"http://127.0.0.1:{port}",
            "token": application.state.token,
            "output": str(directory / "download.zip"),
            "reports": str(reports),
            "fixture": f"http://127.0.0.1:{provider.server_port}",
            "stream_summary": STREAM_SUMMARY,
        }
        write_json(evidence, config)
        try:
            first = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/guided_browser.cjs"),
                    "workbench",
                    str(evidence),
                    str(browser),
                ],
                cwd=ROOT,
                env=browser_env,
                text=True,
                capture_output=True,
                timeout=150,
            )
            (reports / "workbench.log").write_text(first.stdout + first.stderr, encoding="utf-8")
            assert first.returncode == 0, first.stdout + first.stderr
            assert not failures, failures
            assert first_draft.is_set() and completed.is_set()
            assert all(call["stream"] for call in calls), (
                "Runtime must request genuine provider SSE"
            )
            outcome = json.loads((reports / "workbench.json").read_text())
            run = application.state.store.get_run(outcome["run_id"])
            assert run["status"] == "READY" and run["auto_mode"]
            assert (
                run["options"]["frontend"] == "simple-admin"
                and run["options"]["database"] == "sqlite"
            )
            assert {c["model"] for c in calls} == {
                "requirements-fixture",
                "planning-fixture",
                "review-fixture",
            }
            manual = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/guided_browser.cjs"),
                    "manual",
                    str(evidence),
                    str(browser),
                ],
                cwd=ROOT,
                env=browser_env,
                text=True,
                capture_output=True,
                timeout=120,
            )
            (reports / "manual.log").write_text(manual.stdout + manual.stderr, encoding="utf-8")
            assert manual.returncode == 0, manual.stdout + manual.stderr
            assert not failures, failures
            recovery = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/guided_browser.cjs"),
                    "recovery",
                    str(evidence),
                    str(browser),
                ],
                cwd=ROOT,
                env=browser_env,
                text=True,
                capture_output=True,
                timeout=120,
            )
            (reports / "recovery.log").write_text(
                recovery.stdout + recovery.stderr, encoding="utf-8"
            )
            assert recovery.returncode == 0, recovery.stdout + recovery.stderr
            assert not failures, failures
            interaction = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/guided_browser.cjs"),
                    "interaction",
                    str(evidence),
                    str(browser),
                ],
                cwd=ROOT,
                env=browser_env,
                text=True,
                capture_output=True,
                timeout=120,
            )
            (reports / "interaction.log").write_text(
                interaction.stdout + interaction.stderr, encoding="utf-8"
            )
            assert interaction.returncode == 0, interaction.stdout + interaction.stderr
            assert not failures, failures
            public_evidence = json.dumps(
                {
                    "events": application.state.store.events(outcome["run_id"]),
                    "transcript": application.state.store.transcript(outcome["run_id"]),
                },
                ensure_ascii=False,
            )
            assert FIXTURE_KEY not in public_evidence
            assert application.state.token not in public_evidence
            product = directory / "product"
            unpack(directory / "download.zip", product)
            for product_file in product.rglob("*"):
                if product_file.is_file():
                    data = product_file.read_bytes()
                    assert FIXTURE_KEY.encode() not in data, product_file
                    assert application.state.token.encode() not in data, product_file
            env = clean_env({"PRODUCT_DATA_DIR": str(directory / "product-data")})
            subprocess.run(
                [sys.executable, "manage.py", "init"],
                cwd=product,
                env=env,
                check=True,
                capture_output=True,
                timeout=60,
            )
            product_port = free_port()
            config["product"] = f"http://127.0.0.1:{product_port}"
            write_json(evidence, config)
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(product_port),
                    "--no-access-log",
                ],
                cwd=product,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **process_options(),
            )
            try:
                for _ in range(100):
                    try:
                        if (
                            httpx.get(config["product"] + "/health", trust_env=False).status_code
                            == 200
                        ):
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.1)
                second = subprocess.run(
                    [
                        "node",
                        str(ROOT / "scripts/guided_browser.cjs"),
                        "product",
                        str(evidence),
                        str(browser),
                    ],
                    cwd=ROOT,
                    env=browser_env,
                    text=True,
                    capture_output=True,
                    timeout=120,
                )
                (reports / "product.log").write_text(
                    second.stdout + second.stderr, encoding="utf-8"
                )
                assert second.returncode == 0, second.stderr
            finally:
                stop_process(process)
            build_after = ui_build_snapshot()
            assert build_after == build_before, (
                "UI bundle changed during browser acceptance; rerun against one stable build"
            )
            write_json(
                reports / "screenshot-manifest.json",
                {
                    "ui_build_sha256": build_after,
                    "stable_bundle_throughout": True,
                    "evidence": "Real Chromium against local FastAPI and explicit deterministic HTTP model fixtures; no live or paid provider calls",
                    "screen_capture": "Desktop 1440x1100 and mobile 390x844; transition animations disabled only while capturing",
                    "screenshots": [
                        {
                            "file": image.name,
                            "scope": "generated product"
                            if image.name.startswith("news-")
                            else "Vue workbench",
                        }
                        for image in sorted(reports.glob("*.png"))
                        if "failure" not in image.name
                    ],
                    "regressions": [
                        "live Unicode SSE",
                        "replay and deduplication",
                        "manual and delegated approval gates",
                        "stale 409 re-review",
                        "keyboard and IME",
                        "secret-safe model settings",
                        "generated CRUD search and dates",
                    ],
                },
            )
            write_json(
                reports / "summary.json",
                {
                    "passed": True,
                    "model_mode": "explicit-local-http-fixtures",
                    "ui_build_sha256": build_after,
                    "stable_bundle_throughout": True,
                    "model_calls": calls,
                    "real_browser": True,
                    "actual_incremental_sse": True,
                    "first_delta_before_provider_complete": True,
                    "unicode_split_replay_dedupe": True,
                    "concurrent_stale_gate_rereview": True,
                    "explicit_manual_gates_and_delivery_lock": True,
                    "failed_provider_same_run_retry": True,
                    "desktop_and_mobile_screenshots": True,
                    "secret_safe_settings": True,
                    "smart_without_further_questions": True,
                    "generated_news_search_filter": True,
                    "reported_boundary_list_regression": True,
                    "explicit_facts_preserved": True,
                },
            )
        finally:
            start_stream.set()
            release.set()
            server.should_exit = True
            thread.join(timeout=30)
            provider.shutdown()
            provider.server_close()


if __name__ == "__main__":
    main()
````
