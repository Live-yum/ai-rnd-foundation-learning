# workbench/capability_browser_isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_browser_policy`、`workbench.capability_contracts`、`workbench.capability_verification`、`workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `image_source_identity`（L72–L73）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha`。 返回路径：L73的`{name: sha(ROOT / name) for name in IMAGE_SOURCES}`。
- `bounded_json`（L76–L134）：接收`value`、`limit`。 源码说明：Prove the encoded size before allocating JSON or escaped strings.。 控制顺序：L132按`len(encoded) != used`分支；L133抛异常，停止当前正常路径。 调用`visit`、`json.dumps(value, ensure_ascii=True, allow_nan=False, separators=…`、`json.dumps`、`len`、`ValueError`。 返回路径：L134的`encoded`。
- `bounded_json.add`（L80–L84）：接收`size`。 控制顺序：L83按`used > limit`分支；L84抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_json.string`（L86–L102）：接收`value`。 控制顺序：L89按`len(value) > limit - used`分支；L90抛异常，停止当前正常路径；L92遍历`value`。 调用`len`、`ValueError`、`add`、`ord`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_json.visit`（L104–L128）：接收`item`、`depth`。 控制顺序：L105按`depth > 32`分支；L106抛异常，停止当前正常路径；L107按`isinstance(item, str)`分支；L109按`item is None or type(item) is bool`分支；L111按`type(item) in (int, float)`分支；L112按`type(item) is int and item.bit_length() > limit * 4`分支；L113抛异常，停止当前正常路径；L115按`isinstance(item, (list, tuple))`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`isinstance`、`string`、`type`、`add`、`item.bit_length`、`len`、`json.dumps`、`max`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_browser_step`（L137–L160）：接收`step`、`variables`。 源码说明：Reject substitution expansion before constructing candidate strings.。 控制顺序：L140遍历`(("selector", 500), ("value", 10000))`；L143遍历`re.finditer(r"\$\{([a-z][a-z0-9_-]*)\}", template)`；L145按`name not in variables or type(variables[name]) not in (str, int, float, bool)`分支；L146抛异常，停止当前正常路径；L148按`not isinstance(replacement, str)`分支；L152按`used > limit`分支；L153抛异常，停止当前正常路径；L157按`used + len(tail) > limit`分支。后续分支沿下方源码相同行号继续阅读。 调用`step.model_dump`、`re.finditer`、`type`、`ValueError`、`isinstance`、`str`、`match.start`、`len`、`parts.extend`等。 返回路径：L160的`BrowserStep.model_validate(value).model_dump()`。
- `browser_contract`（L163–L182）：接收`request_id`、`selected`、`saved`。 控制顺序：L170遍历`selected`；L173按`used > MAX_CONTRACT`分支；L174抛异常，停止当前正常路径；L175遍历`scenario.browser`；L178按`used > MAX_CONTRACT`分支；L179抛异常，停止当前正常路径。 调用`len`、`bounded_json`、`bool`、`ValueError`、`bounded_browser_step`、`row["steps"].append`、`payload["scenarios"].append`。 返回路径：L182的`payload`。
- `_image_file_archive`（L185–L215）：接收`name`、`path`。 源码说明：Read a bounded raw tar from a stopped owned container; never extract it.。 控制顺序：L196在`True`成立时循环；L198按`remaining <= 0`分支；L199抛异常，停止当前正常路径；L200按`not poll.select(min(remaining, 1))`分支；L203按`not chunk`分支；L205按`len(chunk) > MAX_IMAGE_FILE * 2 - len(output)`分支；L206抛异常，停止当前正常路径；L208按`process.wait(timeout=max(0.1, deadline - time.monotonic()))`分支。后续分支沿下方源码相同行号继续阅读。 调用`subprocess.Popen`、`clean_env`、`time.monotonic`、`bytearray`、`selectors.DefaultSelector`、`poll.register`、`TimeoutError`、`poll.select`、`min`等。 返回路径：L210的`bytes(output)`。
- `image_archive_digest`（L218–L237）：接收`raw`、`basename`。 控制顺序：L219按`len(raw) > MAX_IMAGE_FILE * 2`分支；L220抛异常，停止当前正常路径；L223按`len(members) != 1`分支；L224抛异常，停止当前正常路径；L226按`member.name != basename or not member.isfile() or member.issparse() or not 0 < member…`分支；L232抛异常，停止当前正常路径；L235按`len(body) != member.size`分支；L236抛异常，停止当前正常路径。 调用`len`、`ValueError`、`tarfile.open`、`io.BytesIO`、`archive.getmembers`、`member.isfile`、`member.issparse`、`archive.extractfile`、`source.read`等。 返回路径：L237的`hashlib.sha256(body).hexdigest()`。
- `require_image_sources`（L240–L249）：接收`name`。 控制顺序：L241按`not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name)`分支；L242抛异常，停止当前正常路径；L247按`actual != image_source_identity()`分支；L248抛异常，停止当前正常路径。 调用`re.fullmatch`、`ValueError`、`image_archive_digest`、`_image_file_archive`、`path.rsplit`、`IMAGE_SOURCES.items`、`image_source_identity`。 返回路径：L249的`actual`。
- `browser_source_identity`（L252–L253）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha`。 返回路径：L253的`{name: sha(ROOT / name) for name in BROWSER_SOURCES}`。
- `require_browser_acceptance`（L256–L306）：接收`image`。 控制顺序：L258按`BROWSER_ACCEPTANCE.stat().st_size > 100000`分支；L259抛异常，停止当前正常路径；L279按`not isinstance(record, dict) or set(record) != { "protocol", "passed", "image", "mock…`分支；L305抛异常，停止当前正常路径。 调用`browser_image_identity`、`BROWSER_ACCEPTANCE.stat`、`ValueError`、`json.loads`、`BROWSER_ACCEPTANCE.read_text`、`selected_policy`、`isinstance`、`set`、`record.get`等。 返回路径：L306的`image`。
- `browser_image_identity`（L309–L313）：接收`image`。 控制顺序：L311按`not re.fullmatch(r"sha256:[a-f0-9]{64}", image)`分支；L312抛异常，停止当前正常路径。 调用`os.environ.get`、`re.fullmatch`、`ValueError`。 返回路径：L313的`image`。
- `_write_pipe`（L316–L328）：接收`stream`、`data`、`deadline`。 控制顺序：L320在`view`成立时循环；L322按`remaining <= 0`分支；L323抛异常，停止当前正常路径；L324按`poll.select(min(remaining, 1))`分支。 调用`memoryview`、`selectors.DefaultSelector`、`poll.register`、`time.monotonic`、`TimeoutError`、`poll.select`、`min`、`os.write`、`stream.fileno`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `worker_command`（L331–L372）：接收`image`、`name`。 控制顺序：L332按`not re.fullmatch(r"sha256:[a-f0-9]{64}", image)`分支；L333抛异常，停止当前正常路径；L334按`not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name)`分支；L335抛异常，停止当前正常路径；L337按`policy is not None`分支。 调用`re.fullmatch`、`ValueError`、`selected_policy`、`runtime_identity`、`str`。 返回路径：L339的`[ *DOCKER, "create", "--name", name, "--pull=never", "--network=none", "--read-only", "--c…`。
- `apparmor_runtime_env`（L375–L381）：接收`value`。 调用`isinstance`、`all`、`item.startswith`。 返回路径：L376的`isinstance(value, list) and all(isinstance(item, str) for item in value) and [item for ite…`。
- `require_worker_inspection`（L384–L436）：接收`value`、`image`。 控制顺序：L385按`not isinstance(value, list) or len(value) != 1`分支；L386抛异常，停止当前正常路径；L402按`record.get("Image") != image or config.get("User") != "1000:1000" or any(host.get(k) …`分支；L426按`not security_options_match(host.get("SecurityOpt"))`分支；L428按`selected_policy() is not None`分支；L429按`record.get("AppArmorProfile") != "docker-default"`分支；L431按`not apparmor_runtime_env(config.get("Env"))`分支；L433抛异常，停止当前正常路径。 调用`isinstance`、`len`、`ValueError`、`record.get`、`config.get`、`any`、`host.get`、`expected.items`、`security_options_match`等。 返回路径：L436的`{"image": image, "network": "none", "bounded": True}`。
- `relay_request`（L439–L517）：接收`client`、`frame`、`deadline`。 源码说明：Candidate-controlled requests cannot select a host, token, or proxy.。 控制顺序：L441按`not isinstance(frame, dict) or set(frame) != { "type", "id", "method", "path", "heade…`分支；L449抛异常，停止当前正常路径；L450按`frame["type"] != "request" or type(frame["id"]) is not int or not 1 <= frame["id"] <=…`分支；L455抛异常，停止当前正常路径；L457按`not isinstance(path, str) or len(path) > 8192 or not path.startswith("/") or path.sta…`分支；L468抛异常，停止当前正常路径；L469按`frame["method"] not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}`分支；L470抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`set`、`ValueError`、`type`、`len`、`path.startswith`、`any`、`ord`、`urlsplit`等。 返回路径：L511的`{ "type": "response", "id": frame["id"], "status": response.status_code, "headers": output…`。
- `execute_worker`（L520–L631）：接收`payload`、`url`、`token`、`timeout`、`image`。 源码说明：Bound stdout before parsing; bound runtime independently of HTTP progress.。 控制顺序：L523按`origin.scheme != "http" or origin.path not in {"", "/"} or origin.query or origin.fra…`分支；L531抛异常，停止当前正常路径；L533按`not (origin.hostname == "127.0.0.1" or (origin.hostname or "").endswith(".localhost")…`分支；L534抛异常，停止当前正常路径；L546按`created.returncode`分支；L547抛异常，停止当前正常路径；L551按`inspected.returncode or len(inspected.stdout) > 100000`分支；L552抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`urlsplit`、`ValueError`、`(origin.hostname or "").endswith`、`bounded_json`、`uuid.uuid4`、`worker_command`、`time.monotonic`、`min`、`max`等。 返回路径：L614的`report`。
- `run_isolated_browser`（L634–L670）：接收`url`、`token`、`scenarios`、`saved`、`timeout`、`image`。 控制顺序：L636按`not selected`分支；L639按`not image or not shutil.which("docker")`分支；L640抛异常，停止当前正常路径；L647抛异常，停止当前正常路径；L654按`error or value is None`分支；L655抛异常，停止当前正常路径；L656按`value["passed"] is False`分支；L657抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`os.environ.get`、`shutil.which`、`BrowserFailure`、`uuid.uuid4`、`browser_contract`、`execute_worker`、`browser_report`、`sha`、`type`等。 返回路径：L637的`[]`；L670的`expected`。

</details>

**创建路径：** `workbench/capability_browser_isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L670。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26289`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_browser_isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d318a6d1a0cde0fc0dbc15b938831a3bbad5ae29a7c913366cecface50999c24"} -->
````python
# workbench/capability_browser_isolation.py
"""Offline, bounded browser worker. Never falls back to host Chromium.

The only application transport is a controller-owned HTTP relay over stdio.
The worker image is administrator-selected by immutable digest, not plan data.
Live certification is a separate admission gate; unit tests cannot certify it.
"""

import base64
import hashlib
import io
import json
import os
import re
import selectors
import shutil
import subprocess
import tarfile
import time
import uuid
from urllib.parse import urlsplit

import httpx

from workbench.capability_browser_policy import (
    POLICY_SOURCE,
    runtime_identity,
    security_options_match,
    selected_policy,
)
from workbench.capability_contracts import BrowserStep
from workbench.capability_verification import BrowserFailure, browser_report
from workbench.filesystem import sha
from workbench.settings import ROOT
from workbench.tools import clean_env

MAX_BODY = 4 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_REQUESTS = 256
MAX_FRAME = 6 * 1024 * 1024
MAX_CONTRACT = 1_000_000
MAX_IMAGE_FILE = 256 * 1024
DOCKER = ["docker", "--host", "unix:///var/run/docker.sock"]


BROWSER_SOURCES = (
    "workbench/capability_browser_policy.py",
    POLICY_SOURCE,
    "scripts/capability_browser_seccomp_probe.c",
    "scripts/capability_browser_apparmor.cjs",
    "workbench/capability_browser_isolation.py",
    "workbench/capability_verification.py",
    "scripts/capability_browser.cjs",
    "scripts/capability_browser_worker.cjs",
    "scripts/capability_browser_network_probe.cjs",
    "scripts/ci_capability_browser_isolation.py",
    "tools/browser/Dockerfile",
    "tools/browser/seccomp.playwright-1.56.1.json",
)
BROWSER_ACCEPTANCE = ROOT / "reports/capability-browser-isolation.json"
IMAGE_SOURCES = {
    "scripts/capability_browser_apparmor.cjs": "/opt/verifier/capability_browser_apparmor.cjs",
    POLICY_SOURCE: "/opt/verifier/browser-seccomp-v2.json",
    "scripts/capability_browser_seccomp_probe.c": "/opt/verifier/capability_browser_seccomp_probe.c",
    "scripts/capability_browser.cjs": "/opt/verifier/capability_browser.cjs",
    "scripts/capability_browser_worker.cjs": "/opt/verifier/capability_browser_worker.cjs",
    "scripts/capability_browser_network_probe.cjs": "/opt/verifier/capability_browser_network_probe.cjs",
    "tools/browser/Dockerfile": "/opt/verifier/Dockerfile",
    "tools/browser/seccomp.playwright-1.56.1.json": "/opt/verifier/seccomp.playwright-1.56.1.json",
}


def image_source_identity():
    return {name: sha(ROOT / name) for name in IMAGE_SOURCES}


def bounded_json(value, limit):
    """Prove the encoded size before allocating JSON or escaped strings."""
    used = 0

    def add(size):
        nonlocal used
        used += size
        if used > limit:
            raise ValueError("Browser JSON budget exceeded")

    def string(value):
        # Every character costs at least one byte. Reject large captures before
        # traversing or escaping them; ensure_ascii matches the encoder below.
        if len(value) > limit - used:
            raise ValueError("Browser JSON budget exceeded")
        add(2)
        for char in value:
            code = ord(char)
            add(
                2
                if char in '\\"\b\f\n\r\t'
                else 1
                if 32 <= code < 127
                else 6
                if code <= 65535
                else 12
            )

    def visit(item, depth=0):
        if depth > 32:
            raise ValueError("Browser JSON nesting exceeded")
        if isinstance(item, str):
            string(item)
        elif item is None or type(item) is bool:
            add(4 if item is None or item is True else 5)
        elif type(item) in (int, float):
            if type(item) is int and item.bit_length() > limit * 4:
                raise ValueError("Browser JSON number budget exceeded")
            add(len(json.dumps(item, allow_nan=False)))
        elif isinstance(item, (list, tuple)):
            add(2 + max(0, len(item) - 1))
            for child in item:
                visit(child, depth + 1)
        elif isinstance(item, dict):
            add(2 + max(0, len(item) - 1))
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError("Browser JSON keys must be strings")
                string(key)
                add(1)
                visit(child, depth + 1)
        else:
            raise ValueError("Invalid browser JSON value")

    visit(value)
    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()
    if len(encoded) != used:
        raise ValueError("Browser JSON size proof mismatch")
    return encoded


def bounded_browser_step(step, variables):
    """Reject substitution expansion before constructing candidate strings."""
    value = step.model_dump()
    for field, limit in (("selector", 500), ("value", 10000)):
        template = value[field]
        parts, used, offset = [], 0, 0
        for match in re.finditer(r"\$\{([a-z][a-z0-9_-]*)\}", template):
            name = match[1]
            if name not in variables or type(variables[name]) not in (str, int, float, bool):
                raise ValueError("Invalid browser capture")
            replacement = variables[name]
            if not isinstance(replacement, str):
                replacement = str(replacement)
            literal = template[offset : match.start()]
            used += len(literal) + len(replacement)
            if used > limit:
                raise ValueError("Browser substitution budget exceeded")
            parts.extend((literal, replacement))
            offset = match.end()
        tail = template[offset:]
        if used + len(tail) > limit:
            raise ValueError("Browser substitution budget exceeded")
        value[field] = "".join([*parts, tail])
    return BrowserStep.model_validate(value).model_dump()


def browser_contract(request_id, selected, saved):
    payload = {"request_id": request_id, "scenarios": []}
    # Include transport-only fields in the cumulative proof, although only the
    # worker launcher adds them to the actual request.
    used = len(
        bounded_json({**payload, "url": "http://127.0.0.1:18080", "token": ""}, MAX_CONTRACT)
    )
    for scenario in selected:
        row = {"id": scenario.id, "steps": []}
        used += len(bounded_json(row, MAX_CONTRACT)) + bool(payload["scenarios"])
        if used > MAX_CONTRACT:
            raise ValueError("Browser contract budget exceeded")
        for step in scenario.browser:
            bounded = bounded_browser_step(step, saved[scenario.id])
            used += len(bounded_json(bounded, MAX_CONTRACT)) + bool(row["steps"])
            if used > MAX_CONTRACT:
                raise ValueError("Browser contract budget exceeded")
            row["steps"].append(bounded)
        payload["scenarios"].append(row)
    return payload


def _image_file_archive(name, path):
    """Read a bounded raw tar from a stopped owned container; never extract it."""
    command = [*DOCKER, "cp", name + ":" + path, "-"]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=clean_env()
    )
    deadline = time.monotonic() + 10
    output = bytearray()
    try:
        with selectors.DefaultSelector() as poll:
            poll.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Browser image provenance read timed out")
                if not poll.select(min(remaining, 1)):
                    continue
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    break
                if len(chunk) > MAX_IMAGE_FILE * 2 - len(output):
                    raise ValueError("Browser image provenance archive too large")
                output.extend(chunk)
        if process.wait(timeout=max(0.1, deadline - time.monotonic())):
            raise ValueError("Browser image provenance unavailable")
        return bytes(output)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        process.stdout.close()


def image_archive_digest(raw, basename):
    if len(raw) > MAX_IMAGE_FILE * 2:
        raise ValueError("Browser image provenance archive too large")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        members = archive.getmembers()
        if len(members) != 1:
            raise ValueError("Browser image source is not one regular file")
        member = members[0]
        if (
            member.name != basename
            or not member.isfile()
            or member.issparse()
            or not 0 < member.size <= MAX_IMAGE_FILE
        ):
            raise ValueError("Invalid browser image source member")
        with archive.extractfile(member) as source:
            body = source.read(MAX_IMAGE_FILE + 1)
        if len(body) != member.size:
            raise ValueError("Truncated browser image source")
        return hashlib.sha256(body).hexdigest()


def require_image_sources(name):
    if not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name):
        raise ValueError("Invalid browser worker identity")
    actual = {
        source: image_archive_digest(_image_file_archive(name, path), path.rsplit("/", 1)[1])
        for source, path in IMAGE_SOURCES.items()
    }
    if actual != image_source_identity():
        raise ValueError("Browser image contains stale verifier sources")
    return actual


def browser_source_identity():
    return {name: sha(ROOT / name) for name in BROWSER_SOURCES}


def require_browser_acceptance(image=None):
    image = browser_image_identity() if image is None else browser_image_identity(image)
    if BROWSER_ACCEPTANCE.stat().st_size > 100000:
        raise ValueError("Browser acceptance receipt too large")
    record = json.loads(BROWSER_ACCEPTANCE.read_text(encoding="utf-8"))
    expected_checks = {
        "kernel_and_network": {
            "passed": True,
            "kernel_resource_limits": True,
            "network_none": True,
            "tmpfs_exhaustion": True,
            "pid_exhaustion": True,
            "readonly_root": True,
            "browser_build": True,
            **({"apparmor_enforced": True} if selected_policy() is not None else {}),
        },
        "positive": True,
        "error": True,
        "abuse": True,
        "failure_cleanup": True,
        "memory_exhaustion": True,
        **({"raw_syscalls": True} if selected_policy() is not None else {}),
    }
    if (
        not isinstance(record, dict)
        or set(record)
        != {
            "protocol",
            "passed",
            "image",
            "mocked",
            "sources",
            "image_sources",
            "checks",
            "runtime",
        }
        or record.get("protocol") != "offline-browser-isolation-v3"
        or record.get("passed") is not True
        or record.get("mocked") is not False
        or record.get("image") != image
        or record.get("runtime") != runtime_identity(image)
        or record.get("sources") != browser_source_identity()
        or record.get("image_sources") != image_source_identity()
        or record.get("checks") != expected_checks
        or any(
            type(v) is not bool for k, v in record["checks"].items() if k != "kernel_and_network"
        )
        or any(type(v) is not bool for v in record["checks"]["kernel_and_network"].values())
    ):
        raise ValueError("Live browser acceptance missing, stale, or incomplete")
    return image


def browser_image_identity(image=None):
    image = os.environ.get("CAPABILITY_BROWSER_IMAGE", "") if image is None else image
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image):
        raise ValueError("Immutable browser image ID required")
    return image


def _write_pipe(stream, data, deadline):
    view = memoryview(data)
    with selectors.DefaultSelector() as poll:
        poll.register(stream, selectors.EVENT_WRITE)
        while view:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Browser pipe deadline exceeded")
            if poll.select(min(remaining, 1)):
                try:
                    view = view[os.write(stream.fileno(), view) :]
                except BlockingIOError:
                    pass


def worker_command(image, name):
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image):
        raise ValueError("Immutable browser image ID required")
    if not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name):
        raise ValueError("Invalid worker identity")
    policy = selected_policy()
    if policy is not None:
        runtime_identity(image)
    return [
        *DOCKER,
        "create",
        "--name",
        name,
        "--pull=never",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges:true",
        *(
            [
                "--security-opt=seccomp=" + str(policy),
                "--security-opt=apparmor=docker-default",
                "--env=CAPABILITY_BROWSER_REQUIRE_APPARMOR=1",
            ]
            if policy is not None
            else []
        ),
        "--user=1000:1000",
        "--cpus=1",
        "--memory=768m",
        "--memory-swap=768m",
        "--pids-limit=128",
        "--ulimit=nofile=256:256",
        "--ulimit=core=0:0",
        "--tmpfs=/tmp:rw,nosuid,nodev,noexec,size=134217728,mode=1777",
        "--shm-size=64m",
        "--ipc=private",
        "--cgroupns=private",
        "--log-driver=none",
        "-i",
        image,
    ]


def apparmor_runtime_env(value):
    return (
        isinstance(value, list)
        and all(isinstance(item, str) for item in value)
        and [item for item in value if item.startswith("CAPABILITY_BROWSER_REQUIRE_APPARMOR=")]
        == ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1"]
    )


def require_worker_inspection(value, image):
    if not isinstance(value, list) or len(value) != 1:
        raise ValueError("Missing worker inspection")
    record = value[0]
    host = record.get("HostConfig", {})
    config = record.get("Config", {})
    expected = {
        "NetworkMode": "none",
        "ReadonlyRootfs": True,
        "Privileged": False,
        "NanoCpus": 1000000000,
        "Memory": 805306368,
        "MemorySwap": 805306368,
        "PidsLimit": 128,
        "IpcMode": "private",
        "CgroupnsMode": "private",
        "ShmSize": 67108864,
    }
    if (
        record.get("Image") != image
        or config.get("User") != "1000:1000"
        or any(host.get(k) != v for k, v in expected.items())
        or host.get("CapDrop") != ["ALL"]
        or host.get("CapAdd")
        or not security_options_match(host.get("SecurityOpt"))
        or (
            selected_policy() is not None
            and (
                record.get("AppArmorProfile") != "docker-default"
                or not apparmor_runtime_env(config.get("Env"))
            )
        )
        or host.get("Binds")
        or host.get("PortBindings")
        or host.get("Devices")
        or host.get("PidMode")
        or host.get("UTSMode")
        or host.get("Tmpfs") != {"/tmp": "rw,nosuid,nodev,noexec,size=134217728,mode=1777"}
        or host.get("LogConfig", {}).get("Type") != "none"
        or any(m.get("Type") != "tmpfs" for m in record.get("Mounts", []))
    ):
        mismatches = []
        if not security_options_match(host.get("SecurityOpt")):
            mismatches.append("security-options")
        if selected_policy() is not None:
            if record.get("AppArmorProfile") != "docker-default":
                mismatches.append("apparmor-config")
            if not apparmor_runtime_env(config.get("Env")):
                mismatches.append("apparmor-runtime-guard")
        raise ValueError(
            "Browser worker isolation mismatch: " + ",".join(mismatches or ["outer-boundary"])
        )
    return {"image": image, "network": "none", "bounded": True}


def relay_request(client, frame, *, deadline=None):
    """Candidate-controlled requests cannot select a host, token, or proxy."""
    if not isinstance(frame, dict) or set(frame) != {
        "type",
        "id",
        "method",
        "path",
        "headers",
        "body",
    }:
        raise ValueError("Invalid relay request")
    if (
        frame["type"] != "request"
        or type(frame["id"]) is not int
        or not 1 <= frame["id"] <= MAX_REQUESTS
    ):
        raise ValueError("Invalid relay identity")
    path = frame["path"]
    if (
        not isinstance(path, str)
        or len(path) > 8192
        or not path.startswith("/")
        or path.startswith("//")
        or "\\" in path
        or any(ord(c) < 32 for c in path)
        or urlsplit(path).netloc
        or urlsplit(path).scheme
        or urlsplit(path).fragment
    ):
        raise ValueError("Invalid relay path")
    if frame["method"] not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}:
        raise ValueError("Invalid relay method")
    headers = frame["headers"]
    allowed = {"accept", "content-type", "cookie", "authorization", "x-csrf-token"}
    if (
        not isinstance(headers, dict)
        or len(headers) > len(allowed)
        or any(
            k not in allowed or not isinstance(v, str) or len(v) > 8192 or "\r" in v or "\n" in v
            for k, v in headers.items()
        )
    ):
        raise ValueError("Invalid relay headers")
    if not isinstance(frame["body"], str) or len(frame["body"]) > ((MAX_BODY + 2) // 3) * 4:
        raise ValueError("Relay request budget exceeded")
    body = base64.b64decode(frame["body"], validate=True)
    if len(body) > MAX_BODY:
        raise ValueError("Relay request budget exceeded")
    # Browser contexts own cookies; never reuse the relay client cookie jar.
    client.cookies.clear()
    with client.stream(
        frame["method"], path, headers={**headers, "accept-encoding": "identity"}, content=body
    ) as response:
        if response.headers.get("content-encoding", "identity").lower() != "identity":
            raise ValueError("Compressed relay response rejected")
        chunks = bytearray()
        for chunk in response.iter_raw():
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("Browser relay deadline exceeded")
            if len(chunk) > MAX_BODY - len(chunks):
                raise ValueError("Relay response budget exceeded")
            chunks.extend(chunk)
        # Never follow redirects or hand an absolute redirect to the browser.
        if 300 <= response.status_code < 400:
            raise ValueError("Relay redirects rejected")
        output_headers = [
            (k, v)
            for k, v in response.headers.multi_items()
            if k.lower() in {"content-type", "set-cookie", "cache-control"}
        ]
        if sum(len(k) + len(v) for k, v in output_headers) > 32768:
            raise ValueError("Relay header budget exceeded")
        return {
            "type": "response",
            "id": frame["id"],
            "status": response.status_code,
            "headers": output_headers,
            "body": base64.b64encode(chunks).decode(),
        }, len(body) + len(chunks)


def execute_worker(payload, url, token, timeout, *, image):
    """Bound stdout before parsing; bound runtime independently of HTTP progress."""
    origin = urlsplit(url)
    if (
        origin.scheme != "http"
        or origin.path not in {"", "/"}
        or origin.query
        or origin.fragment
        or origin.username
        or origin.password
    ):
        raise ValueError("Invalid application origin")
    # Existing preview_url validates the exact sandbox preview before this call.
    if not (origin.hostname == "127.0.0.1" or (origin.hostname or "").endswith(".localhost")):
        raise ValueError("Only validated local preview origins are allowed")
    # No credentials enter the container. Prove this bound before creating it
    # or allocating the complete encoded request.
    request = {**payload, "url": "http://127.0.0.1:18080", "token": ""}
    encoded = bounded_json(request, MAX_CONTRACT - 1) + b"\n"
    name = "rnd-browser-" + uuid.uuid4().hex
    command = worker_command(image, name)
    process = None
    deadline = time.monotonic() + min(max(timeout, 1), 180)
    cleanup = False
    try:
        created = subprocess.run(command, capture_output=True, timeout=15, env=clean_env())
        if created.returncode:
            raise ValueError("Browser worker creation failed")
        inspected = subprocess.run(
            [*DOCKER, "inspect", name], capture_output=True, timeout=10, env=clean_env()
        )
        if inspected.returncode or len(inspected.stdout) > 100000:
            raise ValueError("Browser worker inspection failed")
        require_worker_inspection(json.loads(inspected.stdout), image)
        require_image_sources(name)
        process = subprocess.Popen(
            [*DOCKER, "start", "-a", "-i", name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=clean_env(),
        )
        os.set_blocking(process.stdin.fileno(), False)
        _write_pipe(process.stdin, encoded, deadline)
        buffer = bytearray()
        total = count = 0
        report = None
        with (
            selectors.DefaultSelector() as poll,
            httpx.Client(
                base_url=url,
                headers={"x-daytona-preview-token": token},
                follow_redirects=False,
                trust_env=False,
                timeout=5,
            ) as client,
        ):
            poll.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Browser worker deadline exceeded")
                if not poll.select(min(remaining, 1)):
                    continue
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    break
                buffer.extend(chunk)
                if len(buffer) > MAX_FRAME:
                    raise ValueError("Browser frame budget exceeded")
                while b"\n" in buffer:
                    raw, _, rest = buffer.partition(b"\n")
                    buffer = bytearray(rest)
                    frame = json.loads(raw)
                    if frame.get("type") == "report":
                        if report is not None or set(frame) != {"type", "report", "exit_code"}:
                            raise ValueError("Invalid worker report")
                        report = (bounded_json(frame["report"], 100000), frame["exit_code"])
                        continue
                    if report is not None:
                        raise ValueError("Request after browser report")
                    count += 1
                    if count > MAX_REQUESTS or frame.get("id") != count:
                        raise ValueError("Browser request budget exceeded")
                    response, size = relay_request(client, frame, deadline=deadline)
                    total += size
                    if total > MAX_TOTAL:
                        raise ValueError("Browser transfer budget exceeded")
                    _write_pipe(
                        process.stdin, bounded_json(response, MAX_FRAME - 1) + b"\n", deadline
                    )
            status = process.wait(timeout=max(0.1, deadline - time.monotonic()))
        if buffer or report is None or status != 0:
            raise ValueError("Incomplete browser worker report")
        return report
    finally:
        # Removing the owned container kills every browser descendant, including
        # orphan renderers. A killed Docker client alone is not cleanup evidence.
        try:
            result = subprocess.run(
                [*DOCKER, "rm", "-f", name], capture_output=True, timeout=15, env=clean_env()
            )
            cleanup = result.returncode == 0
        finally:
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                process.stdin.close()
                process.stdout.close()
        if not cleanup:
            raise RuntimeError("Browser worker cleanup unconfirmed")


def run_isolated_browser(url, token, scenarios, saved, timeout, *, image=None):
    selected = [s for s in scenarios if s.browser]
    if not selected:
        return []
    image = os.environ.get("CAPABILITY_BROWSER_IMAGE", "") if image is None else image
    if not image or not shutil.which("docker"):
        raise BrowserFailure({"phase": "python-spawn", "error_code": "isolation-unavailable"})
    request_id = uuid.uuid4().hex
    try:
        payload = browser_contract(request_id, selected, saved)
        raw, status = execute_worker(payload, url, token, timeout, image=image)
        value, error = browser_report(raw, request_id, sha(ROOT / "scripts/capability_browser.cjs"))
    except Exception as exc:
        raise BrowserFailure(
            {
                "phase": "python-exit",
                "error_code": "isolation-worker-failed",
                "error_type": type(exc).__name__,
            }
        ) from None
    if error or value is None:
        raise BrowserFailure({"phase": "python-report", "error_code": "invalid-report"})
    if value["passed"] is False:
        raise BrowserFailure(value["diagnostic"])
    expected = [
        {
            "id": s.id,
            "passed": True,
            "steps": len(s.browser),
            "real_browser": True,
            "browser_os_sandbox": True,
        }
        for s in selected
    ]
    if type(status) is not int or status != 0 or value["checks"] != expected:
        raise BrowserFailure({"phase": "python-report", "error_code": "invalid-checks"})
    return expected
````
