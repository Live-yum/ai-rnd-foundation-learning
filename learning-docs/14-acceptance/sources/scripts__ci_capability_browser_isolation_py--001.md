# scripts/ci_capability_browser_isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_capability_browser_isolation；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_browser_isolation`、`workbench.capability_contracts`、`workbench.capability_verification`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Page`（L26–L40）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Page.do_GET`（L27–L37）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pages.get`、`self.send_response`、`self.send_header`、`self.end_headers`、`self.wfile.write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Page.log_message`（L39–L40）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run`（L43–L47）：接收`args`、`timeout`。 控制顺序：L45按`value.returncode or len(value.stdout) > 100000`分支；L46抛异常，停止当前正常路径。 调用`subprocess.run`、`clean_env`、`len`、`RuntimeError`。 返回路径：L47的`value.stdout`。
- `main`（L50–L134）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87按`state.get("OOMKilled") is not True or state.get("Running") is not False`分支；L88抛异常，停止当前正常路径；L91遍历`("positive", "error", "abuse")`；L94按`mode == "positive"`分支；L108按`mode != "positive"`分支；L109抛异常，停止当前正常路径；L112按`mode == "positive"`分支；L114抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`browser_image_identity`、`browser_source_identity`、`write_json`、`uuid.uuid4`、`ThreadingHTTPServer`、`threading.Thread`、`thread.start`、`worker_command`、`command.append`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_capability_browser_isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L138。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5766`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_capability_browser_isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "57bd904fda8a3202360aadbe81b5070ba2db16a5a5b95361ff02ca56d0205fed"} -->
````python
# scripts/ci_capability_browser_isolation.py
"""Live Docker-only browser gate; never certifies from mocks or host Chromium."""

import json
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

from workbench.capability_browser_isolation import (
    DOCKER,
    browser_image_identity,
    browser_source_identity,
    require_image_sources,
    require_worker_inspection,
    run_isolated_browser,
    worker_command,
)
from workbench.capability_contracts import BrowserStep
from workbench.capability_verification import BrowserFailure
from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import clean_env


class Page(BaseHTTPRequestHandler):
    def do_GET(self):
        pages = {
            "/": b'<button id="go" onclick="document.querySelector(\'#value\').textContent=\'ok\'">Go</button><p id="value">waiting</p>',
            "/error": b'<script>throw new Error("candidate error")</script><p id="value">error</p>',
            "/abuse": b"<script>while(true){}</script>",
        }
        value = pages.get(self.path, b"missing")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(value)

    def log_message(self, *args):
        pass


def run(args, timeout=30):
    value = subprocess.run(args, capture_output=True, timeout=timeout, env=clean_env())
    if value.returncode or len(value.stdout) > 100000:
        raise RuntimeError("Live browser infrastructure probe failed")
    return value.stdout


def main():
    image = browser_image_identity()
    report = {
        "protocol": "offline-browser-isolation-v2",
        "passed": False,
        "image": image,
        "mocked": False,
        "sources": browser_source_identity(),
        "image_sources": {},
        "checks": {},
    }
    output = ROOT / "reports/capability-browser-isolation.json"
    write_json(output, report)
    name = "rnd-browser-" + uuid.uuid4().hex
    server = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        command = worker_command(image, name)
        command[-1:-1] = ["--entrypoint=node"]
        command.append("/opt/verifier/capability_browser_network_probe.cjs")
        run(command)
        require_worker_inspection(json.loads(run([*DOCKER, "inspect", name])), image)
        report["image_sources"] = require_image_sources(name)
        report["checks"]["kernel_and_network"] = json.loads(run([*DOCKER, "start", "-a", name]))
        run([*DOCKER, "rm", "-f", name])
        # A separate owned worker must be killed by its memory cgroup, not by
        # a JavaScript heap ceiling, and its descendants must still be removed.
        oom_command = worker_command(image, name)
        oom_command[-1:-1] = ["--entrypoint=node"]
        oom_command.extend(["-e", "const a=[];while(true)a.push(Buffer.alloc(16*1024*1024,255))"])
        run(oom_command)
        require_worker_inspection(json.loads(run([*DOCKER, "inspect", name])), image)
        subprocess.run(
            [*DOCKER, "start", "-a", name], capture_output=True, timeout=30, env=clean_env()
        )
        state = json.loads(run([*DOCKER, "inspect", name]))[0]["State"]
        if state.get("OOMKilled") is not True or state.get("Running") is not False:
            raise RuntimeError("Memory cgroup did not stop abusive worker")
        run([*DOCKER, "rm", "-f", name])
        report["checks"]["memory_exhaustion"] = True
        for mode in ("positive", "error", "abuse"):
            path = "/" if mode == "positive" else "/" + mode
            steps = [BrowserStep(action="open", value=path)]
            if mode == "positive":
                steps += [
                    BrowserStep(action="click", selector="#go"),
                    BrowserStep(action="text", selector="#value", value="ok"),
                ]
            scenario = SimpleNamespace(id=mode, browser=steps)
            try:
                checks = run_isolated_browser(
                    f"http://127.0.0.1:{server.server_port}",
                    "synthetic-token",
                    [scenario],
                    {mode: {}},
                    10 if mode == "abuse" else 60,
                )
                if mode != "positive":
                    raise RuntimeError("Hostile browser unexpectedly passed")
                report["checks"][mode] = bool(checks)
            except BrowserFailure as exc:
                if mode == "positive":
                    report["diagnostic"] = exc.diagnostic
                    raise
                if mode == "error" and exc.diagnostic.get("error_code") != "application-error":
                    raise RuntimeError("Unexpected browser error classification") from None
                if mode == "abuse" and exc.diagnostic.get("error_type") != "TimeoutError":
                    raise RuntimeError("Resource-abuse deadline was not observed") from None
                # Failure alone is insufficient: all owned containers must be gone.
                report["checks"][mode] = True
        remaining = run(
            [*DOCKER, "ps", "-a", "--filter", "name=^/rnd-browser-", "--format", "{{.Names}}"]
        )
        if remaining.strip():
            raise RuntimeError("Browser failure left a container")
        report["checks"]["failure_cleanup"] = True
        report["passed"] = True
    finally:
        subprocess.run(
            [*DOCKER, "rm", "-f", name], capture_output=True, timeout=15, env=clean_env()
        )
        server.shutdown()
        server.server_close()
        write_json(output, report)


if __name__ == "__main__":
    main()
````
