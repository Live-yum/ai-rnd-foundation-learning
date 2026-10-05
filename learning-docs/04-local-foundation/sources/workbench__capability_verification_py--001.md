# workbench/capability_verification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `CheckFailure`（L27–L28）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BrowserFailure`（L31–L36）：继承`CheckFailure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BrowserFailure.__init__`（L34–L36）：接收`diagnostic`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `valid_browser_launch_detail`（L92–L111）：接收`detail`。 调用`detail.get`、`isinstance`、`set`、`all`、`type`。 返回路径：L95的`isinstance(facts, dict) and set(facts) == BROWSER_SECURITY_FLAGS \| {"seccomp_mode", "appa…`。
- `browser_report`（L114–L174）：接收`raw`、`request_id`、`verifier_sha256`。 源码说明：Return a current, exact-protocol report or a static rejection category.。 控制顺序：L116按`len(raw) > 100000`分支；L122按`not isinstance(value, dict) or type(value.get("protocol")) is not int or value["proto…`分支；L128按`value.get("request_id") != request_id or value.get("verifier_sha256") != verifier_sha…`分支；L131按`value.get("passed") is True`分支；L132按`set(value) != fields \| {"checks"} or not isinstance(value["checks"], list)`分支；L136按`value.get("passed") is not False or set(value) != fields \| {"diagnostic"} or not isi…`分支。 调用`len`、`json.loads`、`isinstance`、`type`、`value.get`、`set`、`detail.get`、`valid_browser_launch_detail`、`any`。 返回路径：L117的`None, "report-too-large"`；L121的`None, "invalid-json"`；L127的`None, "invalid-schema"`。
- `preview_url`（L177–L190）：接收`value`、`sandbox_id`、`port`。 控制顺序：L179按`parsed.scheme not in {"http", "https"} or parsed.hostname != f"{port}-{sandbox_id}.pr…`分支；L189抛异常，停止当前正常路径。 调用`urlsplit`、`any`、`ord`、`CheckFailure`、`value.rstrip`。 返回路径：L190的`value.rstrip("/")`。
- `capture_scalar_size`（L198–L219）：接收`value`。 控制顺序：L199按`type(value) is str`分支；L200按`len(value) > MAX_CAPTURE_VALUE_BYTES`分支；L201抛异常，停止当前正常路径；L205抛异常，停止当前正常路径；L206按`type(value) in (int, float, bool)`分支；L207按`type(value) is float and not math.isfinite(value)`分支；L208抛异常，停止当前正常路径；L209按`type(value) is int and value.bit_length() > MAX_CAPTURE_VALUE_BYTES * 4`分支。后续分支沿下方源码相同行号继续阅读。 调用`type`、`len`、`CheckFailure`、`value.encode`、`math.isfinite`、`value.bit_length`、`str`。 返回路径：L219的`size`。
- `CaptureBudget`（L222–L255）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `CaptureBudget.__init__`（L225–L228）：接收`saved`。 控制顺序：L227遍历`saved.items()`。 调用`saved.items`、`self.add_namespace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CaptureBudget.entry_size`（L231–L235）：接收`name`、`value`。 控制顺序：L232按`not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name)`分支；L233抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`CheckFailure`、`len`、`capture_scalar_size`。 返回路径：L235的`128 + len(name) + capture_scalar_size(value)`。
- `CaptureBudget.add_namespace`（L237–L247）：接收`name`、`variables`。 控制顺序：L238按`not isinstance(name, str) or len(name) > 64 or not isinstance(variables, dict)`分支；L239抛异常，停止当前正常路径；L241遍历`variables.items()`；L243按`self.used + cost > MAX_CAPTURE_STATE_BYTES`分支；L244抛异常，停止当前正常路径；L245按`self.used + cost > MAX_CAPTURE_STATE_BYTES`分支；L246抛异常，停止当前正常路径。 调用`isinstance`、`len`、`CheckFailure`、`variables.items`、`self.entry_size`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `CaptureBudget.store`（L249–L255）：接收`variables`、`name`、`value`。 控制顺序：L252按`self.used + cost - old > MAX_CAPTURE_STATE_BYTES`分支；L253抛异常，停止当前正常路径。 调用`self.entry_size`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `interpolate`（L258–L313）：接收`value`、`variables`、`path`。 调用`visit`。 返回路径：L313的`visit(value)`。
- `interpolate.account`（L261–L271）：接收`text`。 控制顺序：L263按`len(text) > remaining`分支；L264抛异常，停止当前正常路径；L268抛异常，停止当前正常路径；L269按`size > remaining`分支；L270抛异常，停止当前正常路径。 调用`len`、`CheckFailure`、`text.encode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `interpolate.captured`（L273–L278）：接收`name`。 控制顺序：L274按`name not in variables`分支；L275抛异常，停止当前正常路径。 调用`CheckFailure`、`capture_scalar_size`。 返回路径：L278的`value`。
- `interpolate.visit`（L280–L311）：接收`item`、`depth`。 控制顺序：L281按`depth > 32`分支；L282抛异常，停止当前正常路径；L284按`isinstance(item, list)`分支；L286按`isinstance(item, dict)`分支；L288遍历`item.items()`；L292按`not isinstance(item, str)`分支；L295按`full and not path`分支；L300遍历`re.finditer(r"\$\{([a-z][a-z0-9_-]*)\}", item)`。 调用`CheckFailure`、`account`、`isinstance`、`visit`、`item.items`、`re.fullmatch`、`captured`、`str`、`re.finditer`等。 返回路径：L285的`[visit(v, depth + 1) for v in item]`；L291的`result`；L293的`item`。
- `values_at`（L316–L332）：接收`value`、`path`。 控制顺序：L317按`path == "$"`分支；L319按`not path.startswith("$.") or len(path) > 300`分支；L320抛异常，停止当前正常路径；L322遍历`path[2:].split(".")`；L324遍历`values`；L325按`part == "*" and isinstance(item, (dict, list))`分支；L327按`isinstance(item, dict) and part in item`分支；L329按`isinstance(item, list) and part.isdigit() and int(part) < len(item)`分支。 调用`path.startswith`、`len`、`CheckFailure`、`path[2:].split`、`isinstance`、`found.extend`、`item.values`、`found.append`、`part.isdigit`等。 返回路径：L318的`[value]`；L332的`values`。
- `json_equal`（L335–L346）：接收`left`、`right`。 控制顺序：L336按`type(left) is not type(right)`分支；L338按`isinstance(left, dict)`分支；L342按`isinstance(left, list)`分支。 调用`type`、`isinstance`、`left.keys`、`right.keys`、`all`、`json_equal`、`left.items`、`len`、`zip`。 返回路径：L337的`False`；L339的`left.keys() == right.keys() and all( json_equal(value, right[key]) for key, value in left.…`；L343的`len(left) == len(right) and all( json_equal(a, b) for a, b in zip(left, right, strict=True…`。
- `http_phase_deadline`（L354–L360）：接收`steps`、`deadline`。 控制顺序：L355按`len(steps) > MAX_HTTP_PHASE_STEPS or sum(step.wait_ms for step in steps) > MAX_HTTP_P…`分支；L359抛异常，停止当前正常路径。 调用`len`、`sum`、`CheckFailure`、`time.monotonic`。 返回路径：L360的`time.monotonic() + MAX_HTTP_PHASE_SECONDS if deadline is None else deadline`。
- `run_steps`（L363–L455）：接收`client`、`steps`、`variables`、`capture_budget`、`deadline`。 控制顺序：L367遍历`enumerate(steps)`；L379按`started + wait >= deadline`分支；L380抛异常，停止当前正常路径；L381按`wait`分支；L384按`step.body is not None`分支；L386按`step.body_encoding == "form"`分支；L390抛异常，停止当前正常路径；L397按`remaining <= 0`分支。后续分支沿下方源码相同行号继续阅读。 调用`http_phase_deadline`、`CaptureBudget`、`enumerate`、`interpolate`、`HttpStep.loopback_path`、`HttpStep.bounded_headers`、`httpx.Headers`、`time.monotonic`、`CheckFailure`等。 返回路径：L455的`receipts`。
- `run_scenarios`（L458–L499）：接收`client`、`scenarios`、`saved`、`after_restart`。 控制顺序：L469遍历`scenarios`；L471按`scenario.id not in saved`分支；L478按`not steps`分支；L486抛异常，停止当前正常路径。 调用`http_phase_deadline`、`CaptureBudget`、`client.cookies.clear`、`uuid.uuid4`、`capture_budget.add_namespace`、`run_steps`、`checks.append`、`digest`、`scenario.model_dump`。 返回路径：L499的`checks, saved`。
- `run_browser`（L502–L609）：接收`url`、`token`、`scenarios`、`saved`、`timeout`。 控制顺序：L504按`not selected`分支；L507按`not node`分支；L508抛异常，停止当前正常路径；L514抛异常，停止当前正常路径；L551抛异常，停止当前正常路径；L562按`prior and prior["passed"] is False`分支；L563抛异常，停止当前正常路径；L566抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`shutil.which`、`BrowserFailure`、`uuid.uuid4`、`sha`、`interpolate`、`step.model_dump`、`tempfile.TemporaryFile`、`subprocess.Popen`、`str`等。 返回路径：L505的`[]`；L609的`value["checks"]`。
- `require_evidence`（L612–L733）：接收`receipt`、`source_digest`、`plan_digest`、`scenarios`、`selection`、`database_tables`、`aggregate`。 控制顺序：L631按`selection["template"] == "fastapiadmin" and container.get("profile") != ( "native-fas…`分支；L634抛异常，停止当前正常路径；L635按`not isinstance(dependency_profile, dict) or dependency_profile.get("profile") != sele…`分支；L641抛异常，停止当前正常路径；L653按`aggregate`分支；L660抛异常，停止当前正常路径；L665按`selection["template"] == "fastapiadmin"`分支；L667遍历`("security_checks", "restart_security_checks") if aggregate else …`。后续分支沿下方源码相同行号继续阅读。 调用`require_container_evidence`、`receipt.get`、`require_dependency_manifest`、`container.get`、`CheckFailure`、`isinstance`、`dependency_profile.get`、`require_preinstalled_evidence`、`require_isolation_evidence`等。 返回路径：L733的`receipt`。

</details>

**创建路径：** `workbench/capability_verification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L733。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28752`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_verification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "22e0e3908c3e4bee3a1562de338ad00902b71b9e42660ef0248fe2ee63d930cc"} -->
````python
# workbench/capability_verification.py
"""Independent HTTP checks run outside the generated application's sandbox.

Only request/expectation data comes from the reviewed plan. Generated test scripts
and reports are never imported or accepted as evidence by this verifier.
"""

import json
import math
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


BROWSER_SECURITY_FLAGS = {
    "uid_zero",
    "no_new_privileges",
    "effective_capabilities",
    "apparmor_enabled",
    "apparmor_userns_restricted",
    "unprivileged_userns_enabled",
}
BROWSER_SANDBOX_REASONS = {"root-launch", "namespace-entry-failed", "no-usable-sandbox"}


def valid_browser_launch_detail(detail):
    facts = detail.get("security_facts")
    reason = detail.get("sandbox_reason")
    return (
        isinstance(facts, dict)
        and set(facts) == BROWSER_SECURITY_FLAGS | {"seccomp_mode", "apparmor_profile"}
        and all(facts[key] is None or type(facts[key]) is bool for key in BROWSER_SECURITY_FLAGS)
        and (
            facts["seccomp_mode"] is None
            or (type(facts["seccomp_mode"]) is int and facts["seccomp_mode"] in {0, 1, 2})
        )
        and isinstance(facts["apparmor_profile"], str)
        and facts["apparmor_profile"]
        in {"docker-default", "unconfined", "other-enforced", "unknown"}
        and (
            isinstance(reason, str) and reason in BROWSER_SANDBOX_REASONS
            if detail.get("error_code") == "sandbox-unavailable"
            else reason is None
        )
    )


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
        | ({"sandbox_reason", "security_facts"} if detail.get("phase") == "launch" else set())
        or (detail.get("phase") == "launch" and not valid_browser_launch_detail(detail))
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


MAX_CAPTURE_VALUE_BYTES = 16384
MAX_CAPTURE_STATE_BYTES = 1_000_000
MAX_INTERPOLATED_BYTES = 1_000_000


def capture_scalar_size(value):
    if type(value) is str:
        if len(value) > MAX_CAPTURE_VALUE_BYTES:
            raise CheckFailure("验收捕获值超过单值预算")
        try:
            size = len(value.encode("utf-8"))
        except UnicodeError:
            raise CheckFailure("验收捕获值不是有效Unicode") from None
    elif type(value) in (int, float, bool):
        if type(value) is float and not math.isfinite(value):
            raise CheckFailure("验收捕获数值必须有限")
        if type(value) is int and value.bit_length() > MAX_CAPTURE_VALUE_BYTES * 4:
            raise CheckFailure("验收捕获值超过单值预算")
        try:
            size = len(str(value))
        except ValueError:
            raise CheckFailure("验收捕获值超过单值预算") from None
    else:
        raise CheckFailure("验收捕获值必须是单一标量")
    if size > MAX_CAPTURE_VALUE_BYTES:
        raise CheckFailure("验收捕获值超过单值预算")
    return size


class CaptureBudget:
    """Bound all retained scenarios; replacing a variable credits its old cost."""

    def __init__(self, saved):
        self.used = 0
        for name, variables in saved.items():
            self.add_namespace(name, variables)

    @staticmethod
    def entry_size(name, value):
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name):
            raise CheckFailure("验收捕获变量名无效")
        # Fixed overhead also bounds the number of tiny retained dictionary entries.
        return 128 + len(name) + capture_scalar_size(value)

    def add_namespace(self, name, variables):
        if not isinstance(name, str) or len(name) > 64 or not isinstance(variables, dict):
            raise CheckFailure("验收捕获状态格式无效")
        cost = 128 + len(name)
        for key, value in variables.items():
            cost += self.entry_size(key, value)
            if self.used + cost > MAX_CAPTURE_STATE_BYTES:
                raise CheckFailure("验收捕获状态超过总预算")
        if self.used + cost > MAX_CAPTURE_STATE_BYTES:
            raise CheckFailure("验收捕获状态超过总预算")
        self.used += cost

    def store(self, variables, name, value):
        cost = self.entry_size(name, value)
        old = self.entry_size(name, variables[name]) if name in variables else 0
        if self.used + cost - old > MAX_CAPTURE_STATE_BYTES:
            raise CheckFailure("验收捕获状态超过总预算")
        variables[name] = value
        self.used += cost - old


def interpolate(value, variables, *, path=False):
    remaining = MAX_INTERPOLATED_BYTES

    def account(text):
        nonlocal remaining
        if len(text) > remaining:
            raise CheckFailure("验收变量替换超过预算")
        try:
            size = len(text.encode("utf-8"))
        except UnicodeError:
            raise CheckFailure("验收变量替换不是有效Unicode") from None
        if size > remaining:
            raise CheckFailure("验收变量替换超过预算")
        remaining -= size

    def captured(name):
        if name not in variables:
            raise CheckFailure("验收引用尚未捕获的变量")
        value = variables[name]
        capture_scalar_size(value)
        return value

    def visit(item, depth=0):
        if depth > 32:
            raise CheckFailure("验收变量替换嵌套超过预算")
        account("x")  # Bound aggregate object/container count as well as strings.
        if isinstance(item, list):
            return [visit(v, depth + 1) for v in item]
        if isinstance(item, dict):
            result = {}
            for key, value in item.items():
                account(key)
                result[key] = visit(value, depth + 1)
            return result
        if not isinstance(item, str):
            return item
        full = re.fullmatch(r"\$\{([a-z][a-z0-9_-]*)\}", item)
        if full and not path:
            result = captured(full[1])
            account(str(result))
            return result
        parts, offset = [], 0
        for match in re.finditer(r"\$\{([a-z][a-z0-9_-]*)\}", item):
            literal = item[offset : match.start()]
            account(literal)
            replacement = str(captured(match[1]))
            replacement = quote(replacement, safe="") if path else replacement
            account(replacement)
            parts.extend((literal, replacement))
            offset = match.end()
        tail = item[offset:]
        account(tail)
        parts.append(tail)
        return "".join(parts)

    return visit(value)


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


MAX_HTTP_PHASE_SECONDS = 300
MAX_HTTP_PHASE_STEPS = 4096
MAX_HTTP_PHASE_WAIT_MS = 30_000


def http_phase_deadline(steps, deadline=None):
    if (
        len(steps) > MAX_HTTP_PHASE_STEPS
        or sum(step.wait_ms for step in steps) > MAX_HTTP_PHASE_WAIT_MS
    ):
        raise CheckFailure("验收HTTP步骤或等待总量超过预算")
    return time.monotonic() + MAX_HTTP_PHASE_SECONDS if deadline is None else deadline


def run_steps(client, steps, variables, *, capture_budget=None, deadline=None):
    deadline = http_phase_deadline(steps, deadline)
    capture_budget = CaptureBudget({"": variables}) if capture_budget is None else capture_budget
    receipts = []
    for index, step in enumerate(steps):
        path = interpolate(step.path, variables, path=True)
        HttpStep.loopback_path(path)
        headers = interpolate(step.headers, variables)
        HttpStep.bounded_headers(headers)
        # Candidate responses are untrusted. HTTPX's decoded iterator can
        # allocate an arbitrarily expanded compressed block before a caller's
        # byte-count check. Request identity and never invoke its decoders.
        headers = httpx.Headers(headers)
        headers["accept-encoding"] = "identity"
        started = time.monotonic()
        wait = step.wait_ms / 1000
        if started + wait >= deadline:
            raise CheckFailure("验收HTTP总期限不足，未开始下一请求")
        if wait:
            time.sleep(wait)
        request_body = {}
        if step.body is not None:
            body = interpolate(step.body, variables)
            if step.body_encoding == "form":
                try:
                    body = HttpStep.bounded_form(body)
                except ValueError, UnicodeError:
                    raise CheckFailure("form插值结果超过边界或不是字符串字段") from None
                request_body["data"] = body
                headers["content-type"] = "application/x-www-form-urlencoded"
            else:
                request_body["json"] = body
                headers["content-type"] = "application/json"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise CheckFailure("验收HTTP总期限已耗尽，未发送请求")
        try:
            with client.stream(
                step.method,
                path,
                headers=headers,
                timeout=min(15, remaining),
                **request_body,
            ) as response:
                if (
                    response.headers.get("content-encoding", "identity").strip().lower()
                    != "identity"
                ):
                    raise CheckFailure("验收HTTP响应必须使用未压缩的identity编码")
                raw = bytearray()
                for block in response.iter_raw():
                    if time.monotonic() >= deadline:
                        raise CheckFailure("验收HTTP总期限已耗尽")
                    if len(block) > 2_000_000 - len(raw):
                        raise CheckFailure("验收HTTP响应超过2MB预算")
                    raw.extend(block)
                status = response.status_code
                if time.monotonic() >= deadline:
                    raise CheckFailure("验收HTTP总期限已耗尽")
        except httpx.HTTPError:
            raise CheckFailure(f"第 {index + 1} 个验收请求传输失败") from None
        if status != step.status:
            raise CheckFailure(f"第 {index + 1} 个请求期望HTTP {step.status}，实际HTTP {status}")
        body = None
        if step.equals or step.absent or step.captures:
            try:
                body = json.loads(raw)
            except ValueError, UnicodeError, RecursionError:
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
            capture_budget.store(variables, name, found[0])
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
    deadline = http_phase_deadline(
        [
            step
            for scenario in scenarios
            for step in (scenario.after_restart if after_restart else scenario.steps)
        ]
    )
    saved = {} if saved is None else saved
    capture_budget = CaptureBudget(saved)
    checks = []
    for scenario in scenarios:
        client.cookies.clear()
        if scenario.id not in saved:
            variables = {"nonce": uuid.uuid4().hex}
            capture_budget.add_namespace(scenario.id, variables)
            saved[scenario.id] = variables
        else:
            variables = saved[scenario.id]
        steps = scenario.after_restart if after_restart else scenario.steps
        if not steps:
            continue
        try:
            executed = run_steps(
                client, steps, variables, capture_budget=capture_budget, deadline=deadline
            )
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
    from workbench.capability_dependencies import require_dependency_manifest
    from workbench.capability_execution import (
        VERIFIER,
        require_preinstalled_evidence,
        security_checks_for,
    )
    from workbench.capability_isolation import (
        require_container_evidence,
        require_isolation_evidence,
    )

    require_container_evidence(receipt.get("container_isolation"), receipt.get("sandbox_id"))
    dependency_profile = require_dependency_manifest(
        receipt.get("dependency_profile"), selection["template"]
    )
    container = receipt["container_isolation"]
    if selection["template"] == "fastapiadmin" and container.get("profile") != (
        "native-fastapiadmin-postgresql-v1"
    ):
        raise CheckFailure("原生证据未绑定专用私有共享内存容器")
    if (
        not isinstance(dependency_profile, dict)
        or dependency_profile.get("profile") != selection["template"]
        or dependency_profile.get("image_id") != container.get("snapshot_image_id")
        or container.get("dependency_manifest") != dependency_profile
    ):
        raise CheckFailure("只读依赖证明未绑定实际镜像和当前技术栈")
    try:
        require_preinstalled_evidence(
            receipt.get("preinstalled_dependencies"),
            dependency_profile,
            source_digest=source_digest,
        )
        require_preinstalled_evidence(
            receipt.get("final_preinstalled_dependencies"),
            dependency_profile,
            source_digest=source_digest,
        )
        if aggregate:
            require_preinstalled_evidence(
                receipt.get("restart_preinstalled_dependencies"),
                dependency_profile,
                source_digest=source_digest,
            )
    except ValueError:
        raise CheckFailure("缺少已验证的只读预装依赖证明，不能沿用安装回执") from None
    require_isolation_evidence(
        receipt.get("execution_isolation"),
        native_semaphore_storage=selection["template"] == "fastapiadmin",
    )
    if selection["template"] == "fastapiadmin":
        required_security = security_checks_for(selection)
        for field in (
            ("security_checks", "restart_security_checks") if aggregate else ("security_checks",)
        ):
            security = receipt.get(field)
            if (
                type(security) is not dict
                or set(security) != required_security
                or any(value is not True for value in security.values())
            ):
                raise CheckFailure("原生最终证据缺少完整的初始或重启隔离反例及清理证明")
    expected = {s.id: digest(s.model_dump()) for s in scenarios}
    checks = receipt.get("checks", [])
    actual = {c.get("id"): c.get("contract_sha256") for c in checks if c.get("phase") == "initial"}
    if (
        receipt.get("passed") is not True
        or receipt.get("source_digest") != source_digest
        or receipt.get("plan_digest") != plan_digest
        or receipt.get("verifier") != VERIFIER
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
