# workbench/capability_verification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `CheckFailure`（L26–L27）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BrowserFailure`（L30–L35）：继承`CheckFailure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BrowserFailure.__init__`（L33–L35）：接收`diagnostic`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `browser_report`（L80–L138）：接收`raw`、`request_id`、`verifier_sha256`。 源码说明：Return a current, exact-protocol report or a static rejection category.。 控制顺序：L82按`len(raw) > 100000`分支；L88按`not isinstance(value, dict) or type(value.get("protocol")) is not int or value["proto…`分支；L94按`value.get("request_id") != request_id or value.get("verifier_sha256") != verifier_sha…`分支；L97按`value.get("passed") is True`分支；L98按`set(value) != fields \| {"checks"} or not isinstance(value["checks"], list)`分支；L102按`value.get("passed") is not False or set(value) != fields \| {"diagnostic"} or not isi…`分支。 调用`len`、`json.loads`、`isinstance`、`type`、`value.get`、`set`、`detail.get`、`any`。 返回路径：L83的`None, "report-too-large"`；L87的`None, "invalid-json"`；L93的`None, "invalid-schema"`。
- `preview_url`（L141–L154）：接收`value`、`sandbox_id`、`port`。 控制顺序：L143按`parsed.scheme not in {"http", "https"} or parsed.hostname != f"{port}-{sandbox_id}.pr…`分支；L153抛异常，停止当前正常路径。 调用`urlsplit`、`any`、`ord`、`CheckFailure`、`value.rstrip`。 返回路径：L154的`value.rstrip("/")`。
- `interpolate`（L157–L176）：接收`value`、`variables`、`path`。 控制顺序：L158按`isinstance(value, list)`分支；L160按`isinstance(value, dict)`分支；L162按`not isinstance(value, str)`分支；L165按`full and not path`分支；L166按`full[1] not in variables`分支；L167抛异常，停止当前正常路径。 调用`isinstance`、`interpolate`、`value.items`、`re.fullmatch`、`CheckFailure`、`re.sub`。 返回路径：L159的`[interpolate(v, variables) for v in value]`；L161的`{k: interpolate(v, variables) for k, v in value.items()}`；L163的`value`。
- `interpolate.replacement`（L170–L174）：接收`match`。 控制顺序：L171按`match[1] not in variables`分支；L172抛异常，停止当前正常路径。 调用`CheckFailure`、`str`、`quote`。 返回路径：L174的`quote(text, safe="") if path else text`。
- `values_at`（L179–L195）：接收`value`、`path`。 控制顺序：L180按`path == "$"`分支；L182按`not path.startswith("$.") or len(path) > 300`分支；L183抛异常，停止当前正常路径；L185遍历`path[2:].split(".")`；L187遍历`values`；L188按`part == "*" and isinstance(item, (dict, list))`分支；L190按`isinstance(item, dict) and part in item`分支；L192按`isinstance(item, list) and part.isdigit() and int(part) < len(item)`分支。 调用`path.startswith`、`len`、`CheckFailure`、`path[2:].split`、`isinstance`、`found.extend`、`item.values`、`found.append`、`part.isdigit`等。 返回路径：L181的`[value]`；L195的`values`。
- `json_equal`（L198–L209）：接收`left`、`right`。 控制顺序：L199按`type(left) is not type(right)`分支；L201按`isinstance(left, dict)`分支；L205按`isinstance(left, list)`分支。 调用`type`、`isinstance`、`left.keys`、`right.keys`、`all`、`json_equal`、`left.items`、`len`、`zip`。 返回路径：L200的`False`；L202的`left.keys() == right.keys() and all( json_equal(value, right[key]) for key, value in left.…`；L206的`len(left) == len(right) and all( json_equal(a, b) for a, b in zip(left, right, strict=True…`。
- `run_steps`（L212–L266）：接收`client`、`steps`、`variables`。 控制顺序：L214遍历`enumerate(steps)`；L228遍历`response.iter_bytes()`；L230按`len(raw) > 2_000_000`分支；L231抛异常，停止当前正常路径；L234抛异常，停止当前正常路径；L235按`status != step.status`分支；L236抛异常，停止当前正常路径；L238按`step.equals or step.absent or step.captures`分支。后续分支沿下方源码相同行号继续阅读。 调用`enumerate`、`interpolate`、`HttpStep.loopback_path`、`HttpStep.bounded_headers`、`time.monotonic`、`client.stream`、`bytearray`、`response.iter_bytes`、`raw.extend`等。 返回路径：L266的`receipts`。
- `run_scenarios`（L269–L295）：接收`client`、`scenarios`、`saved`、`after_restart`。 控制顺序：L272遍历`scenarios`；L276按`not steps`分支；L282抛异常，停止当前正常路径。 调用`client.cookies.clear`、`saved.setdefault`、`uuid.uuid4`、`run_steps`、`checks.append`、`digest`、`scenario.model_dump`。 返回路径：L295的`checks, saved`。
- `run_browser`（L298–L405）：接收`url`、`token`、`scenarios`、`saved`、`timeout`。 控制顺序：L300按`not selected`分支；L303按`not node`分支；L304抛异常，停止当前正常路径；L310抛异常，停止当前正常路径；L347抛异常，停止当前正常路径；L358按`prior and prior["passed"] is False`分支；L359抛异常，停止当前正常路径；L362抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`shutil.which`、`BrowserFailure`、`uuid.uuid4`、`sha`、`interpolate`、`step.model_dump`、`tempfile.TemporaryFile`、`subprocess.Popen`、`str`等。 返回路径：L301的`[]`；L405的`value["checks"]`。
- `require_evidence`（L408–L474）：接收`receipt`、`source_digest`、`plan_digest`、`scenarios`、`selection`、`database_tables`、`aggregate`。 控制顺序：L421按`receipt.get("passed") is not True or receipt.get("source_digest") != source_digest or…`分支；L434抛异常，停止当前正常路径；L435按`aggregate`分支；L438按`not required or restarted != required or receipt.get("restarted") is not True`分支；L439抛异常，停止当前正常路径；L443按`stack.get("selection") != selection or not stack.get("source_checks") or stack.get("l…`分支；L454抛异常，停止当前正常路径；L455按`aggregate`分支。后续分支沿下方源码相同行号继续阅读。 调用`require_container_evidence`、`receipt.get`、`require_isolation_evidence`、`digest`、`s.model_dump`、`c.get`、`len`、`any`、`s.get`等。 返回路径：L474的`receipt`。

</details>

**创建路径：** `workbench/capability_verification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L474。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18118`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_verification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "791adcd6a6ba87c62c3adec0c487995e9b20e860b86a5d9e3ebce54387121bf6"} -->
````python
# workbench/capability_verification.py
"""Independent HTTP checks run outside the generated application's sandbox.

Only request/expectation data comes from the reviewed plan. Generated test scripts
and reports are never imported or accepted as evidence by this verifier.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from urllib.parse import quote, urlsplit

import httpx

from workbench.capability_contracts import HttpStep
from workbench.domain import digest
from workbench.filesystem import sha
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, stop_process


class CheckFailure(ValueError):
    pass


class BrowserFailure(CheckFailure):
    """Only bounded, allowlisted diagnostics cross the browser process boundary."""

    def __init__(self, diagnostic):
        super().__init__("真实浏览器场景未通过；查看安全阶段诊断，未跳过")
        self.diagnostic = diagnostic


BROWSER_PHASES = {
    "contract",
    "tool",
    "launch",
    "context",
    "routing",
    "page",
    "navigation",
    "action",
    "assertion",
    "application",
    "context-close",
    "browser-close",
}
BROWSER_ERROR_CODES = {
    "operation-failed",
    "timeout",
    "tool-version",
    "browser-channel-rejected",
    "contract-too-large",
    "origin-rejected",
    "action-rejected",
    "application-error",
    "tool-missing",
    "sandbox-unavailable",
    "browser-missing",
    "browser-dependency",
    "name-resolution",
    "connection-refused",
    "navigation-network",
}
BROWSER_ACTIONS = {"viewport", "open", "fill", "click", "visible", "hidden", "text", None}
BROWSER_ERROR_TYPES = {
    "Error",
    "TypeError",
    "SyntaxError",
    "ReferenceError",
    "TimeoutError",
    "Other",
}


def browser_report(raw, request_id, verifier_sha256):
    """Return a current, exact-protocol report or a static rejection category."""
    if len(raw) > 100000:
        return None, "report-too-large"
    try:
        value = json.loads(raw)
    except ValueError, UnicodeError, RecursionError:
        return None, "invalid-json"
    if (
        not isinstance(value, dict)
        or type(value.get("protocol")) is not int
        or value["protocol"] != 1
    ):
        return None, "invalid-schema"
    if value.get("request_id") != request_id or value.get("verifier_sha256") != verifier_sha256:
        return None, "wrong-verifier-or-request"
    fields = {"protocol", "request_id", "verifier_sha256", "passed"}
    if value.get("passed") is True:
        if set(value) != fields | {"checks"} or not isinstance(value["checks"], list):
            return None, "invalid-schema"
        return value, None
    detail = value.get("diagnostic")
    if (
        value.get("passed") is not False
        or set(value) != fields | {"diagnostic"}
        or not isinstance(detail, dict)
        or set(detail)
        != {
            "phase",
            "error_code",
            "error_type",
            "scenario_index",
            "step_index",
            "action",
            "navigation_status",
        }
        or not isinstance(detail.get("phase"), str)
        or detail["phase"] not in BROWSER_PHASES
        or not isinstance(detail.get("error_code"), str)
        or detail["error_code"] not in BROWSER_ERROR_CODES
        or not isinstance(detail.get("error_type"), str)
        or detail["error_type"] not in BROWSER_ERROR_TYPES
        or (detail.get("action") is not None and not isinstance(detail["action"], str))
        or detail["action"] not in BROWSER_ACTIONS
        or any(
            detail[key] is not None
            and (type(detail[key]) is not int or not 0 <= detail[key] <= 10000)
            for key in ("scenario_index", "step_index")
        )
        or (
            detail["navigation_status"] is not None
            and (
                type(detail["navigation_status"]) is not int
                or not 100 <= detail["navigation_status"] <= 599
            )
        )
    ):
        return None, "invalid-diagnostic"
    return value, None


def preview_url(value, sandbox_id, port):
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname != f"{port}-{sandbox_id}.proxy.localhost"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
        or any(ord(c) <= 32 for c in value)
    ):
        raise CheckFailure("自定义验收只接受当前沙箱端口的本机私有预览地址")
    return value.rstrip("/")


def interpolate(value, variables, *, path=False):
    if isinstance(value, list):
        return [interpolate(v, variables) for v in value]
    if isinstance(value, dict):
        return {k: interpolate(v, variables) for k, v in value.items()}
    if not isinstance(value, str):
        return value
    full = re.fullmatch(r"\$\{([a-z][a-z0-9_-]*)\}", value)
    if full and not path:
        if full[1] not in variables:
            raise CheckFailure("验收引用尚未捕获的变量")
        return variables[full[1]]

    def replacement(match):
        if match[1] not in variables:
            raise CheckFailure("验收引用尚未捕获的变量")
        text = str(variables[match[1]])
        return quote(text, safe="") if path else text

    return re.sub(r"\$\{([a-z][a-z0-9_-]*)\}", replacement, value)


def values_at(value, path):
    if path == "$":
        return [value]
    if not path.startswith("$.") or len(path) > 300:
        raise CheckFailure("验收JSON路径无效")
    values = [value]
    for part in path[2:].split("."):
        found = []
        for item in values:
            if part == "*" and isinstance(item, (dict, list)):
                found.extend(item.values() if isinstance(item, dict) else item)
            elif isinstance(item, dict) and part in item:
                found.append(item[part])
            elif isinstance(item, list) and part.isdigit() and int(part) < len(item):
                found.append(item[int(part)])
        values = found
    return values


def json_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            json_equal(value, right[key]) for key, value in left.items()
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            json_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return left == right


def run_steps(client, steps, variables):
    receipts = []
    for index, step in enumerate(steps):
        path = interpolate(step.path, variables, path=True)
        HttpStep.loopback_path(path)
        headers = interpolate(step.headers, variables)
        HttpStep.bounded_headers(headers)
        started = time.monotonic()
        try:
            with client.stream(
                step.method,
                path,
                headers=headers,
                **({"json": interpolate(step.body, variables)} if step.body is not None else {}),
            ) as response:
                raw = bytearray()
                for block in response.iter_bytes():
                    raw.extend(block)
                    if len(raw) > 2_000_000:
                        raise CheckFailure("验收HTTP响应超过2MB预算")
                status = response.status_code
        except httpx.HTTPError:
            raise CheckFailure(f"第 {index + 1} 个验收请求传输失败") from None
        if status != step.status:
            raise CheckFailure(f"第 {index + 1} 个请求期望HTTP {step.status}，实际HTTP {status}")
        body = None
        if step.equals or step.absent or step.captures:
            try:
                body = json.loads(raw)
            except ValueError, UnicodeError:
                raise CheckFailure(f"第 {index + 1} 个请求缺少约定JSON响应") from None
        for pointer, expected in step.equals.items():
            actual = values_at(body, pointer)
            if not actual or any(
                not json_equal(v, interpolate(expected, variables)) for v in actual
            ):
                raise CheckFailure(f"第 {index + 1} 个请求的已批准JSON断言未通过")
        if any(values_at(body, pointer) for pointer in step.absent):
            raise CheckFailure(f"第 {index + 1} 个请求暴露了契约禁止返回的字段")
        for name, pointer in step.captures.items():
            found = values_at(body, pointer)
            if len(found) != 1 or not isinstance(found[0], (str, int, float, bool)):
                raise CheckFailure(f"第 {index + 1} 个请求缺少单一捕获值")
            variables[name] = found[0]
        receipts.append(
            {
                "step": index + 1,
                "method": step.method,
                "status": status,
                "assertions": len(step.equals) + len(step.absent),
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "passed": True,
            }
        )
    return receipts


def run_scenarios(client, scenarios, *, saved=None, after_restart=False):
    saved = {} if saved is None else saved
    checks = []
    for scenario in scenarios:
        client.cookies.clear()
        variables = saved.setdefault(scenario.id, {"nonce": uuid.uuid4().hex})
        steps = scenario.after_restart if after_restart else scenario.steps
        if not steps:
            continue
        try:
            executed = run_steps(client, steps, variables)
        except CheckFailure as exc:
            exc.scenario_id = scenario.id
            raise
        checks.append(
            {
                "id": scenario.id,
                "contract_sha256": digest(scenario.model_dump()),
                "requirements": scenario.requirements,
                "evidence": scenario.evidence,
                "external_service": scenario.external_service,
                "phase": "restart" if after_restart else "initial",
                "steps": executed,
                "passed": True,
            }
        )
    return checks, saved


def run_browser(url, token, scenarios, saved, timeout):
    selected = [s for s in scenarios if s.browser]
    if not selected:
        return []
    node = shutil.which("node")
    if not node:
        raise BrowserFailure({"phase": "python-spawn", "error_code": "node-missing"})
    request_id = uuid.uuid4().hex
    script = ROOT / "scripts/capability_browser.cjs"
    try:
        verifier_sha256 = sha(script)
    except OSError:
        raise BrowserFailure(
            {"phase": "python-spawn", "error_code": "verifier-unavailable"}
        ) from None
    payload = {
        "request_id": request_id,
        "url": url,
        "token": token,
        "scenarios": [
            {
                "id": s.id,
                "steps": [interpolate(step.model_dump(), saved[s.id]) for step in s.browser],
            }
            for s in selected
        ],
    }
    with tempfile.TemporaryFile() as output:
        try:
            process = subprocess.Popen(
                [node, str(script)],
                stdin=subprocess.PIPE,
                stdout=output,
                stderr=subprocess.STDOUT,
                **process_options(),
                env=clean_env(
                    {
                        "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get(
                            "PRODUCT_VERIFY_PLAYWRIGHT",
                            str(ROOT / ".native/browser/node_modules/playwright"),
                        ),
                        "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
                        "PRODUCT_VERIFY_BROWSER_CHANNEL": os.environ.get(
                            "PRODUCT_VERIFY_BROWSER_CHANNEL", ""
                        ),
                    }
                ),
            )
        except OSError:
            raise BrowserFailure({"phase": "python-spawn", "error_code": "spawn-failed"}) from None
        try:
            process.communicate(json.dumps(payload).encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            cleanup = "stopped"
            try:
                stop_process(process)
            except Exception:
                cleanup = "failed"
            output.seek(0)
            prior, _ = browser_report(output.read(100001), request_id, verifier_sha256)
            if prior and prior["passed"] is False:
                raise BrowserFailure(
                    {**prior["diagnostic"], "termination": "python-timeout", "cleanup": cleanup}
                ) from None
            raise BrowserFailure(
                {"phase": "python-timeout", "error_code": "timeout", "cleanup": cleanup}
            ) from None
        output.seek(0)
        raw = output.read(100001)
    value, report_error = browser_report(raw, request_id, verifier_sha256)
    status = process.returncode if type(process.returncode) is int else None
    if report_error:
        raise BrowserFailure(
            {
                "phase": "python-exit" if status else "python-report",
                "error_code": "nonzero-exit" if status else "invalid-report",
                "exit_code": status,
                "report_error": report_error,
            }
        )
    if value["passed"] is False:
        raise BrowserFailure({**value["diagnostic"], "exit_code": status})
    if status != 0:
        raise BrowserFailure(
            {"phase": "python-exit", "error_code": "success-with-invalid-exit", "exit_code": status}
        )
    expected = {scenario.id: len(scenario.browser) for scenario in selected}
    checks = value["checks"]
    seen = set()
    for check in checks:
        if (
            not isinstance(check, dict)
            or set(check) != {"id", "passed", "steps", "real_browser", "browser_os_sandbox"}
            or not isinstance(check.get("id"), str)
            or check["id"] not in expected
            or check["id"] in seen
            or type(check.get("steps")) is not int
            or check["steps"] != expected[check["id"]]
            or any(
                check.get(flag) is not True
                for flag in ("passed", "real_browser", "browser_os_sandbox")
            )
        ):
            raise BrowserFailure({"phase": "python-report", "error_code": "invalid-checks"})
        seen.add(check["id"])
    if seen != set(expected):
        raise BrowserFailure({"phase": "python-report", "error_code": "invalid-checks"})
    return value["checks"]


def require_evidence(
    receipt, *, source_digest, plan_digest, scenarios, selection, database_tables, aggregate=False
):
    from workbench.capability_isolation import (
        require_container_evidence,
        require_isolation_evidence,
    )

    require_container_evidence(receipt.get("container_isolation"), receipt.get("sandbox_id"))
    require_isolation_evidence(receipt.get("execution_isolation"))
    expected = {s.id: digest(s.model_dump()) for s in scenarios}
    checks = receipt.get("checks", [])
    actual = {c.get("id"): c.get("contract_sha256") for c in checks if c.get("phase") == "initial"}
    if (
        receipt.get("passed") is not True
        or receipt.get("source_digest") != source_digest
        or receipt.get("plan_digest") != plan_digest
        or receipt.get("verifier") != "controller-http-contract-v3"
        or receipt.get("network_block_all") is not True
        or receipt.get("credentials_uploaded") is not False
        or receipt.get("cleanup") != "deleted"
        or actual != expected
        or len(actual) != len([c for c in checks if c.get("phase") == "initial"])
        or any(c.get("passed") is not True or not c.get("steps") for c in checks)
        or any(s.get("passed") is not True for c in checks for s in c.get("steps", []))
    ):
        raise CheckFailure("独立验收证据不完整或与当前源码、计划和场景不一致")
    if aggregate:
        restarted = {c.get("id") for c in checks if c.get("phase") == "restart"}
        required = {s.id for s in scenarios if s.after_restart}
        if not required or restarted != required or receipt.get("restarted") is not True:
            raise CheckFailure("最终汇总缺少独立重启后的持久化验收")
    stack = receipt.get("stack", {})
    database = receipt.get("database", {})
    before, after = database.get("baseline", {}), database.get("after", {})
    if (
        stack.get("selection") != selection
        or not stack.get("source_checks")
        or stack.get("launcher") != ("java" if selection["backend"] == "yudao-java" else "uvicorn")
        or database.get("engine") != selection["database"]
        or database.get("observed_writes") is not True
        or set(before) != set(database_tables)
        or set(after) != set(database_tables)
        or any(type(value) is not int or value < 0 for value in [*before.values(), *after.values()])
        or not any(after[name] > before[name] for name in before)
    ):
        raise CheckFailure("技术栈或独立物理数据库写入证据缺失，不能采用模型自报完成")
    if aggregate:
        restarted = database.get("after_restart", {})
        if set(restarted) != set(after) or any(
            type(restarted[name]) is not int or restarted[name] < after[name] for name in after
        ):
            raise CheckFailure("物理数据库重启证据不完整")
    browser_expected = {s.id: len(s.browser) for s in scenarios if s.browser}
    browser = receipt.get("browser", [])
    if (
        {check.get("id"): check.get("steps") for check in browser} != browser_expected
        or len(browser) != len(browser_expected)
        or any(
            check.get("passed") is not True
            or check.get("real_browser") is not True
            or check.get("browser_os_sandbox") is not True
            for check in browser
        )
    ):
        raise CheckFailure("缺少准确计划的真实浏览器验收证据")
    return receipt
````
