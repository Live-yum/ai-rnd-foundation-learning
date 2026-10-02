# scripts/ci_guided_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台到资讯产品的浏览器验收协调。** 启动实际工作台与浏览器，显式模型夹具提供资讯需求，检查智能推荐和产物；随后访问真正生成的产品，不将静态HTML当成功。

**对应关系：** browser工作流 → guided_browser.cjs → 实际API/页面/独立交付。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.news_fixture`、`workbench.api`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `free_port`（L29–L32）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L32的`sock.getsockname()[1]`。
- `main`（L35–L232）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L107遍历`range(100)`；L108按`server.started`分支；L112抛异常，停止当前正常路径；L139断言`first.returncode == 0`；L142断言`run["status"] == "READY" and run["auto_mode"]`；L143断言`run["options"]["frontend"] == "simple-admin" and run["options"]["database"] == "sqlit…`；L147断言`{c["model"] for c in calls} == { "requirements-fixture", "planning-fixture", "review-…`；L185遍历`range(100)`。后续分支沿下方源码相同行号继续阅读。 调用`ThreadingHTTPServer`、`threading.Thread(target=provider.serve_forever, daemon=True).star…`、`threading.Thread`、`reports.mkdir`、`tempfile.TemporaryDirectory`、`Path`、`free_port`、`Settings`、`create_app`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider`（L38–L81）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `main.Provider.log_message`（L39–L40）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.Provider.do_POST`（L42–L81）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44断言`self.headers["Authorization"] == "Bearer explicit-ci-only"`；L48按`model == "requirements-fixture"`分支；L49按`payload.get("autonomous")`分支；L52按`model == "planning-fixture"`分支；L55按`model == "review-fixture"`分支；L62抛异常，停止当前正常路径。 调用`json.loads`、`self.rfile.read`、`int`、`calls.append`、`payload.get`、`assert_resolution`、`news_requirement`、`assert_approved`、`news_spec`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_guided_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L236。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8592`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_guided_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "40533481b935aa69dbcfaa51d578f0cbec61ff1eb1272c2c45cba26fd74da03b"} -->
````python
# scripts/ci_guided_browser.py
"""Real local HTTP and Chromium regression; model servers are explicit test fixtures only."""

import json
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


def main():
    calls = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.headers["Authorization"] == "Bearer explicit-ci-only"
            model = body["model"]
            payload = json.loads(body["messages"][1]["content"])
            calls.append({"model": model, "path": self.path})
            if model == "requirements-fixture":
                if payload.get("autonomous"):
                    assert_resolution(payload)
                value = news_requirement(payload.get("autonomous", False))
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
    with tempfile.TemporaryDirectory(prefix="guided-browser-") as directory:
        directory = Path(directory)
        port = free_port()
        settings = Settings(
            data_dir=directory / "platform",
            base_url=f"http://127.0.0.1:{provider.server_port}/v1",
            api_key="explicit-ci-only",
            MODE="requirements-fixture",
            PLANNING_MODE="planning-fixture",
            REVIEW_MODE="review-fixture",
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
        browser = ROOT / ".native/browser/node_modules/playwright"
        evidence = directory / "browser-input.json"
        config = {
            "requirement": ORIGINAL_REQUEST,
            "platform": f"http://127.0.0.1:{port}",
            "token": application.state.token,
            "output": str(directory / "download.zip"),
            "reports": str(reports),
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
                env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
                text=True,
                capture_output=True,
                timeout=150,
            )
            (reports / "workbench.log").write_text(first.stdout + first.stderr, encoding="utf-8")
            assert first.returncode == 0, first.stderr
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
            product = directory / "product"
            unpack(directory / "download.zip", product)
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
                    env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
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
            write_json(
                reports / "summary.json",
                {
                    "passed": True,
                    "model_mode": "explicit-local-http-fixtures",
                    "model_calls": calls,
                    "real_browser": True,
                    "smart_without_further_questions": True,
                    "generated_news_search_filter": True,
                    "reported_boundary_list_regression": True,
                    "explicit_facts_preserved": True,
                },
            )
        finally:
            server.should_exit = True
            thread.join(timeout=30)
            provider.shutdown()
            provider.server_close()


if __name__ == "__main__":
    main()
````
