# scripts/template_acceptance_runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.template_acceptance_runtime；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.template_acceptance_cases`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `reference`（L33–L37）：接收`values`、`path`。 控制顺序：L35遍历`path.split(".")`。 调用`path.split`、`isinstance`、`int`、`copy.deepcopy`。 返回路径：L37的`copy.deepcopy(result)`。
- `resolve`（L40–L50）：接收`value`、`values`。 控制顺序：L41按`isinstance(value, dict)`分支；L43按`isinstance(value, list)`分支；L45按`not isinstance(value, str)`分支；L48按`match`分支。 调用`isinstance`、`resolve`、`value.items`、`REFERENCE.fullmatch`、`reference`、`match.group`、`REFERENCE.sub`、`str`。 返回路径：L42的`{key: resolve(item, values) for key, item in value.items()}`；L44的`[resolve(item, values) for item in value]`；L46的`value`。
- `check_json`（L53–L98）：接收`value`、`assertion`、`location`。 控制顺序：L54按`"where" in assertion`分支；L57按`assertion.get("one")`分支；L60遍历`assertion.get("path", [])`；L62按`"equals" in assertion`分支；L68按`"count" in assertion`分支；L74按`"ids" in assertion`分支；L81按`"contains" in assertion`分支；L88按`"gte" in assertion`分支。后续分支沿下方源码相同行号继续阅读。 调用`require`、`isinstance`、`same_obligation`、`assertion.get`、`len`、`json.dumps`、`sorted`、`any`、`type`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `LocalProduct`（L101–L232）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `LocalProduct.__init__`（L104–L111）：接收`case`、`product`、`python`、`directory`。 调用`Path`、`str`、`self.directory.mkdir`、`clean_env`、`secrets.token_urlsafe`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `LocalProduct.command`（L113–L124）：接收`args`、`stdin`。 调用`subprocess.run`、`require`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `LocalProduct.start`（L126–L161）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L153在`time.monotonic() < deadline`成立时循环；L156按`self.client.get("/health", timeout=1).status_code == 200`分支；L161抛异常，停止当前正常路径。 调用`socket.socket`、`listener.bind`、`listener.getsockname`、`subprocess.Popen`、`str`、`process_options`、`httpx.Client`、`time.monotonic`、`require`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `LocalProduct.stop`（L163–L169）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L164按`self.client`分支；L167按`self.process`分支。 调用`self.client.close`、`stop_process`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `LocalProduct.request`（L171–L184）：接收`actor`、`method`、`path`、`expected`、`location`、`**kwargs`。 调用`require`、`path.startswith`、`self.client.request`、`response.json`。 返回路径：L184的`response.json() if response.content else None`。
- `LocalProduct.__enter__`（L186–L229）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L190按`business`分支；L206遍历`self.case.actors.items()`；L209按`not business`分支；L214按`name != bootstrap`分支；L224按`business`分支；L229抛异常，停止当前正常路径。 调用`self.command`、`self.case.contract.get`、`next`、`self.case.actors.items`、`json.dumps`、`self.start`、`self.request`、`self.actors[name].update`、`self.stop`。 返回路径：L226的`self`。
- `LocalProduct.__exit__`（L231–L232）：接收`*args`。 调用`self.stop`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_scenario`（L235–L319）：接收`case`、`product`、`python`、`directory`、`screenshots`、`browser`。 源码说明：The browser=False switch is for explicit offline harness tests only.。 控制顺序：L240遍历`case.scenario`；L241按`block.get("restart")`分支；L244遍历`enumerate(block["requests"])`；L257遍历`step.get("assertions", [])`；L259按`"save" in step`分支；L265按`browser`分支。 调用`LocalProduct`、`block.get`、`app.stop`、`app.start`、`enumerate`、`str`、`copy.deepcopy`、`body.update`、`resolve`等。 返回路径：L313的`{ "passed": True, "checks": checks, "http_requests": app.http_calls, "restart": True, "bro…`。

</details>

**创建路径：** `scripts/template_acceptance_runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L319。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12337`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/template_acceptance_runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "98208beda48264bed8b653fd792182ac7fc3049fcbaffc8a56bd31b6f4d9fe29"} -->
````python
# scripts/template_acceptance_runtime.py
"""Run source-authored HTTP scenarios and Chromium views on a clean delivered product.

Cases contain only HTTP requests, JSON assertions, and UI expectations. No case can
execute commands, supply a Plan, replace a model response, or invent evidence.
"""

import copy
import json
import os
import re
import secrets
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

import httpx

from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require,
    require_scenario_checks,
    same_obligation,
)
from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, stop_process

REFERENCE = re.compile(r"\$\{([a-zA-Z0-9_.]+)\}")


def reference(values, path):
    result = values
    for part in path.split("."):
        result = result[int(part)] if isinstance(result, list) else result[part]
    return copy.deepcopy(result)


def resolve(value, values):
    if isinstance(value, dict):
        return {key: resolve(item, values) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, values) for item in value]
    if not isinstance(value, str):
        return value
    match = REFERENCE.fullmatch(value)
    if match:
        return reference(values, match.group(1))
    return REFERENCE.sub(lambda match: str(reference(values, match.group(1))), value)


def check_json(value, assertion, location):
    if "where" in assertion:
        require(isinstance(value, list), "assertion_collection", location)
        value = [item for item in value if same_obligation(item, assertion["where"])]
    if assertion.get("one"):
        require(isinstance(value, list) and len(value) == 1, "assertion_one", location)
        value = value[0]
    for key in assertion.get("path", []):
        value = value[key]
    if "equals" in assertion:
        require(
            json.dumps(value, sort_keys=True) == json.dumps(assertion["equals"], sort_keys=True),
            "assertion_equals",
            location,
        )
    if "count" in assertion:
        require(
            isinstance(value, list) and len(value) == assertion["count"],
            "assertion_count",
            location,
        )
    if "ids" in assertion:
        require(
            isinstance(value, list)
            and sorted(item["id"] for item in value) == sorted(assertion["ids"]),
            "assertion_ids",
            location,
        )
    if "contains" in assertion:
        require(
            isinstance(value, list)
            and any(same_obligation(item, assertion["contains"]) for item in value),
            "assertion_contains",
            location,
        )
    if "gte" in assertion:
        require(
            type(value) in {int, float} and value >= assertion["gte"], "assertion_minimum", location
        )
    if assertion.get("timestamp"):
        require(
            isinstance(value, str)
            and datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None,
            "assertion_timestamp",
            location,
        )


class LocalProduct:
    """Own one fresh database and real product process, never the platform's database."""

    def __init__(self, case, product, python, directory):
        self.case, self.product, self.python = case, Path(product), str(python)
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.env = clean_env({"PRODUCT_DATA_DIR": str(self.directory / "database")})
        self.password = secrets.token_urlsafe(24)
        self.actors, self.process, self.client = {}, None, None
        self.http_calls = 0

    def command(self, args, *, stdin=None):
        result = subprocess.run(
            [self.python, *args],
            cwd=self.product,
            env=self.env,
            input=stdin,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=90,
        )
        require(result.returncode == 0, "product_command_failed")

    def start(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.process = subprocess.Popen(
            [
                self.python,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "critical",
            ],
            cwd=self.product,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **process_options(),
        )
        self.client = httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=20, trust_env=False, follow_redirects=False
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            require(self.process.poll() is None, "product_start_failed")
            try:
                if self.client.get("/health", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        raise AcceptanceFailure("product_start_timeout")

    def stop(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.process:
            stop_process(self.process)
            self.process = None

    def request(self, actor, method, path, *, expected=200, location="setup", **kwargs):
        require(method in {"GET", "POST", "PUT", "DELETE"}, "request_method")
        require(
            path.startswith(("/api/", "/business/", "/auth/")) and ".." not in path, "request_path"
        )
        headers = {"Authorization": "Bearer " + self.actors[actor]["token"]} if actor else {}
        response = self.client.request(method, path, headers=headers, **kwargs)
        self.http_calls += 1
        require(
            response.status_code == expected,
            "http_status_mismatch",
            f"{location}/expected_{expected}/actual_{response.status_code}",
        )
        return response.json() if response.content else None

    def __enter__(self):
        try:
            self.command(["manage.py", "init"])
            business = self.case.contract.get("business")
            if business:
                bootstrap = next(
                    name
                    for name, item in self.case.actors.items()
                    if item["role"] == business["bootstrap_role"]
                )
                self.command(
                    [
                        "-c",
                        "import sys,json,getpass; data=json.load(sys.stdin); getpass.getpass=lambda _:data['password']; import manage; manage.bootstrap_admin(data['username'])",
                    ],
                    stdin=json.dumps(
                        {"username": "acceptance_" + bootstrap, "password": self.password}
                    ),
                )
            self.start()
            for name, definition in self.case.actors.items():
                credentials = {"username": "acceptance_" + name, "password": self.password}
                identity = {"username": credentials["username"], **definition}
                if not business:
                    auth = self.request(
                        None, "POST", "/auth/register", json=credentials, expected=201
                    )
                else:
                    if name != bootstrap:
                        identity = self.request(
                            bootstrap,
                            "POST",
                            "/business/users",
                            json={**credentials, **definition},
                            expected=201,
                        )
                    auth = self.request(None, "POST", "/auth/login", json=credentials)
                self.actors[name] = {**identity, "token": auth["access_token"]}
                if business:
                    self.actors[name].update(self.request(name, "GET", "/business/me"))
            return self
        except BaseException:
            self.stop()
            raise

    def __exit__(self, *args):
        self.stop()


def run_scenario(case, product, python, directory, screenshots, *, browser=True):
    """The browser=False switch is for explicit offline harness tests only."""
    checks = []
    with LocalProduct(case, product, python, directory) as app:
        values = {"actors": app.actors}
        for block in case.scenario:
            if block.get("restart"):
                app.stop()
                app.start()
            for index, step in enumerate(block["requests"]):
                location = block["id"] + "/" + str(index)
                body = copy.deepcopy(case.fixtures[step["fixture"]]) if "fixture" in step else {}
                body.update(resolve(step.get("json", {}), values))
                response = app.request(
                    step["actor"],
                    step["method"],
                    resolve(step["path"], values),
                    expected=step["status"],
                    location=location,
                    **({"json": body} if "fixture" in step or "json" in step else {}),
                    **({"params": resolve(step["params"], values)} if "params" in step else {}),
                )
                for assertion in step.get("assertions", []):
                    check_json(response, resolve(assertion, values), location)
                if "save" in step:
                    require(step["save"] not in values, "duplicate_saved_response", location)
                    values[step["save"]] = response
            checks.append(block["id"])
        require_scenario_checks(case, checks)
        browser_report = {"passed": False, "real_browser": False, "scope": "offline_http_test_only"}
        if browser:
            module = os.environ.get(
                "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
            )
            require(Path(module).is_dir(), "browser_tooling_missing")
            screenshots = Path(screenshots)
            screenshots.mkdir(parents=True, exist_ok=True)
            cfg, output = (
                Path(directory) / "browser-input.json",
                Path(directory) / "browser-output.json",
            )
            write_json(
                cfg,
                {
                    "case": case.identity,
                    "url": str(app.client.base_url),
                    "actors": {
                        name: {"username": item["username"]} for name, item in app.actors.items()
                    },
                    "password": app.password,
                    "spec": json.loads(
                        (Path(product) / "approved-spec.json").read_text(encoding="utf-8")
                    ),
                    "views": resolve(list(case.browser), values),
                    "screenshots": str(screenshots),
                    "output": str(output),
                },
            )
            result = subprocess.run(
                ["node", str(ROOT / "scripts/template_acceptance_browser.cjs"), str(cfg), module],
                cwd=ROOT,
                env=clean_env(
                    {"PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0")}
                ),
                capture_output=True,
                timeout=240,
            )
            require(result.returncode == 0 and output.is_file(), "scenario_browser_failed")
            browser_report = json.loads(output.read_text(encoding="utf-8"))
            require(
                browser_report.get("passed") is True and browser_report.get("real_browser") is True,
                "scenario_browser_evidence",
            )
            require(
                browser_report.get("views") == len(case.browser)
                and browser_report.get("errors") == [],
                "scenario_browser_incomplete",
            )
        return {
            "passed": True,
            "checks": checks,
            "http_requests": app.http_calls,
            "restart": True,
            "browser": browser_report,
        }
````
