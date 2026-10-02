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
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, stop_process


class CheckFailure(ValueError):
    pass


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
        raise CheckFailure("浏览器验收需要已安装的Node与固定Playwright，不能跳过前端验证")
    payload = {
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
        process = subprocess.Popen(
            [node, str(ROOT / "scripts/capability_browser.cjs")],
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
                }
            ),
        )
        try:
            process.communicate(json.dumps(payload).encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise CheckFailure("真实浏览器验收超时，已终止验收进程组") from None
        if process.returncode:
            raise CheckFailure("真实浏览器场景未通过；缺少工具或页面交互断言失败，未跳过")
        output.seek(0)
        raw = output.read(100001)
    if len(raw) > 100000:
        raise CheckFailure("浏览器验收报告过大")
    try:
        value = json.loads(raw)
    except ValueError, UnicodeError:
        raise CheckFailure("浏览器验收缺少有效报告") from None
    if value.get("passed") is not True:
        raise CheckFailure("浏览器验收失败")
    return value["checks"]


def require_evidence(
    receipt, *, source_digest, plan_digest, scenarios, selection, database_tables, aggregate=False
):
    from workbench.capability_isolation import require_isolation_evidence

    require_isolation_evidence(receipt.get("execution_isolation"))
    expected = {s.id: digest(s.model_dump()) for s in scenarios}
    checks = receipt.get("checks", [])
    actual = {c.get("id"): c.get("contract_sha256") for c in checks if c.get("phase") == "initial"}
    if (
        receipt.get("passed") is not True
        or receipt.get("source_digest") != source_digest
        or receipt.get("plan_digest") != plan_digest
        or receipt.get("verifier") != "controller-http-contract-v2"
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
