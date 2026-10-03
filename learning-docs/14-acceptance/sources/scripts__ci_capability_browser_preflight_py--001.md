# scripts/ci_capability_browser_preflight.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_capability_browser_preflight；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_verification`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `FixturePage`（L29–L38）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `FixturePage.do_GET`（L30–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.send_response`、`self.send_header`、`str`、`len`、`self.end_headers`、`self.wfile.write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `FixturePage.log_message`（L37–L38）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `readonly_host_facts`（L41–L53）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L43遍历`{ "apparmor_enabled": "/sys/module/apparmor/parameters/enabled", …`。 调用`{ "apparmor_enabled": "/sys/module/apparmor/parameters/enabled", …`、`Path(filename).read_text(encoding="ascii").strip`、`Path(filename).read_text`、`Path`。 返回路径：L53的`facts`。
- `probe`（L56–L74）：接收`url`。 调用`SimpleNamespace`、`BrowserStep`、`run_browser`。 返回路径：L69的`{"passed": False, "browser_diagnostic": exc.diagnostic}`；L73的`{"passed": False, "error_code": "preflight-infrastructure"}`；L74的`{"passed": True, "checks": checks}`。
- `installed_chrome_version`（L77–L90）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L86按`result.returncode == 0 and re.fullmatch(r"[0-9]{1,4}(?:\.[0-9]{1,4}){3}", value)`分支。 调用`subprocess.run`、`clean_env`、`result.stdout.decode("ascii").strip`、`result.stdout.decode`、`re.fullmatch`。 返回路径：L87的`value`；L90的`None`。
- `main`（L93–L131）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L112按`channel == "chrome"`分支；L127按`not report["passed"]`分支；L128抛异常，停止当前正常路径。 调用`os.environ.get`、`installed_chrome_version`、`sha`、`readonly_host_facts`、`write_json`、`ThreadingHTTPServer`、`threading.Thread`、`thread.start`、`probe`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_capability_browser_preflight.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L135。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5237`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_capability_browser_preflight.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "796452a13f2c4c1742587c5c6d59e45ad9921e3e98d2f3a1852c2859ec3a8bd8"} -->
````python
# scripts/ci_capability_browser_preflight.py
"""Real sandboxed controller-browser readiness, never product acceptance.

Run before building Daytona. Only a synthetic loopback page is served; no
application source, credentials, model, AppArmor policy or sysctl is changed.
The same trusted driver, pinned Playwright, channel and sandbox settings as the
product verifier must pass. A bundled-browser failure is retained separately
for diagnosis when the explicitly selected system Chrome passes.
"""

import os
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from workbench.capability_contracts import BrowserStep
from workbench.capability_verification import BrowserFailure, run_browser
from workbench.filesystem import sha, write_json
from workbench.settings import ROOT
from workbench.tools import clean_env

PAGE = b"""<!doctype html><meta charset="utf-8"><title>Browser readiness</title>
<button id="check" onclick="document.querySelector('#result').textContent='Ready'">Check</button>
<p id="result">Waiting</p>"""


class FixturePage(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, *args):
        pass


def readonly_host_facts():
    facts = {}
    for name, filename in {
        "apparmor_enabled": "/sys/module/apparmor/parameters/enabled",
        "apparmor_restrict_unprivileged_userns": "/proc/sys/kernel/apparmor_restrict_unprivileged_userns",
        "unprivileged_userns_clone": "/proc/sys/kernel/unprivileged_userns_clone",
    }.items():
        try:
            value = Path(filename).read_text(encoding="ascii").strip()
        except OSError, UnicodeError:
            value = None
        facts[name] = value if value in {"0", "1", "Y", "N"} else None
    return facts


def probe(url):
    scenario = SimpleNamespace(
        id="controller-browser-readiness",
        browser=[
            BrowserStep(action="open", value="/"),
            BrowserStep(action="text", selector="#result", value="Waiting"),
            BrowserStep(action="click", selector="#check"),
            BrowserStep(action="text", selector="#result", value="Ready"),
        ],
    )
    try:
        checks = run_browser(url, "synthetic-readiness-token", [scenario], {scenario.id: {}}, 60)
    except BrowserFailure as exc:
        return {"passed": False, "browser_diagnostic": exc.diagnostic}
    except Exception:
        # An unexpected infrastructure exception must not leak environment or
        # subprocess text, and must never turn into a passing readiness result.
        return {"passed": False, "error_code": "preflight-infrastructure"}
    return {"passed": True, "checks": checks}


def installed_chrome_version():
    try:
        result = subprocess.run(
            ["/usr/bin/google-chrome", "--product-version"],
            capture_output=True,
            timeout=10,
            env=clean_env(),
        )
        value = result.stdout.decode("ascii").strip()
        if result.returncode == 0 and re.fullmatch(r"[0-9]{1,4}(?:\.[0-9]{1,4}){3}", value):
            return value
    except OSError, UnicodeError, subprocess.TimeoutExpired:
        pass
    return None


def main():
    channel = os.environ.get("PRODUCT_VERIFY_BROWSER_CHANNEL", "")
    report = {
        "passed": False,
        "scope": "controller-browser-readiness-only",
        "product_acceptance": False,
        "channel": channel if channel in {"", "chrome"} else "rejected",
        "playwright_version": "1.56.1",
        "chrome_version": installed_chrome_version() if channel == "chrome" else None,
        "browser_verifier_sha256": sha(ROOT / "scripts/capability_browser.cjs"),
        "host_facts": readonly_host_facts(),
    }
    report_path = ROOT / "reports/capability-browser-preflight.json"
    write_json(report_path, report)
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixturePage)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        if channel == "chrome":
            # Observe the old bundled launch separately. This result never
            # satisfies the mandatory probe for the explicitly chosen channel.
            os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] = ""
            try:
                report["bundled_probe"] = probe(url)
            finally:
                os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] = channel
        report["selected_probe"] = probe(url)
        report["passed"] = report["selected_probe"]["passed"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        write_json(report_path, report)
    if not report["passed"]:
        raise SystemExit(
            "Sandboxed browser preflight FAILED; see capability-browser-preflight.json"
        )
    print("Sandboxed controller browser readiness PASS; product acceptance is still required.")


if __name__ == "__main__":
    main()
````
