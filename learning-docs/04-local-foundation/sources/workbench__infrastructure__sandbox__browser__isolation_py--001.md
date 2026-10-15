# workbench/infrastructure/sandbox/browser/isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance.capability_verification`、`workbench.filesystem`、`workbench.infrastructure.processes.tools`、`workbench.infrastructure.sandbox.browser.policy`、`workbench.planning.contracts`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `image_source_identity`（L107–L108）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha`。 返回路径：L108的`{name: sha(ROOT / name) for name in IMAGE_SOURCES}`。
- `bounded_json`（L111–L169）：接收`value`、`limit`。 源码说明：Prove the encoded size before allocating JSON or escaped strings.。 控制顺序：L167按`len(encoded) != used`分支；L168抛异常，停止当前正常路径。 调用`visit`、`json.dumps(value, ensure_ascii=True, allow_nan=False, separators=…`、`json.dumps`、`len`、`ValueError`。 返回路径：L169的`encoded`。
- `bounded_json.add`（L115–L119）：接收`size`。 控制顺序：L118按`used > limit`分支；L119抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_json.string`（L121–L137）：接收`value`。 控制顺序：L124按`len(value) > limit - used`分支；L125抛异常，停止当前正常路径；L127遍历`value`。 调用`len`、`ValueError`、`add`、`ord`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_json.visit`（L139–L163）：接收`item`、`depth`。 控制顺序：L140按`depth > 32`分支；L141抛异常，停止当前正常路径；L142按`isinstance(item, str)`分支；L144按`item is None or type(item) is bool`分支；L146按`type(item) in (int, float)`分支；L147按`type(item) is int and item.bit_length() > limit * 4`分支；L148抛异常，停止当前正常路径；L150按`isinstance(item, (list, tuple))`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`isinstance`、`string`、`type`、`add`、`item.bit_length`、`len`、`json.dumps`、`max`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bounded_browser_step`（L172–L195）：接收`step`、`variables`。 源码说明：Reject substitution expansion before constructing candidate strings.。 控制顺序：L175遍历`(("selector", 500), ("value", 10000))`；L178遍历`re.finditer(r"\$\{([a-z][a-z0-9_-]*)\}", template)`；L180按`name not in variables or type(variables[name]) not in (str, int, float, bool)`分支；L181抛异常，停止当前正常路径；L183按`not isinstance(replacement, str)`分支；L187按`used > limit`分支；L188抛异常，停止当前正常路径；L192按`used + len(tail) > limit`分支。后续分支沿下方源码相同行号继续阅读。 调用`step.model_dump`、`re.finditer`、`type`、`ValueError`、`isinstance`、`str`、`match.start`、`len`、`parts.extend`等。 返回路径：L195的`BrowserStep.model_validate(value).model_dump()`。
- `browser_contract`（L198–L217）：接收`request_id`、`selected`、`saved`。 控制顺序：L205遍历`selected`；L208按`used > MAX_CONTRACT`分支；L209抛异常，停止当前正常路径；L210遍历`scenario.browser`；L213按`used > MAX_CONTRACT`分支；L214抛异常，停止当前正常路径。 调用`len`、`bounded_json`、`bool`、`ValueError`、`bounded_browser_step`、`row["steps"].append`、`payload["scenarios"].append`。 返回路径：L217的`payload`。
- `_image_file_archive`（L220–L245）：接收`name`、`path`。 源码说明：Read a bounded raw tar from a stopped owned container; never extract it.。 控制顺序：L230在`True`成立时循环；L232按`not chunk`分支；L234按`len(chunk) > MAX_IMAGE_FILE * 2 - len(output)`分支；L235抛异常，停止当前正常路径；L237按`process.wait(timeout=_remaining(deadline, message))`分支；L238抛异常，停止当前正常路径；L242按`process.poll() is None`分支。 调用`subprocess.Popen`、`clean_env`、`time.monotonic`、`bytearray`、`_read_pipe`、`len`、`ValueError`、`output.extend`、`process.wait`等。 返回路径：L240的`bytes(output)`。
- `image_archive_digest`（L248–L267）：接收`raw`、`basename`。 控制顺序：L249按`len(raw) > MAX_IMAGE_FILE * 2`分支；L250抛异常，停止当前正常路径；L253按`len(members) != 1`分支；L254抛异常，停止当前正常路径；L256按`member.name != basename or not member.isfile() or member.issparse() or not 0 < member…`分支；L262抛异常，停止当前正常路径；L265按`len(body) != member.size`分支；L266抛异常，停止当前正常路径。 调用`len`、`ValueError`、`tarfile.open`、`io.BytesIO`、`archive.getmembers`、`member.isfile`、`member.issparse`、`archive.extractfile`、`source.read`等。 返回路径：L267的`hashlib.sha256(body).hexdigest()`。
- `require_image_sources`（L270–L279）：接收`name`。 控制顺序：L271按`not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name)`分支；L272抛异常，停止当前正常路径；L277按`actual != image_source_identity()`分支；L278抛异常，停止当前正常路径。 调用`re.fullmatch`、`ValueError`、`image_archive_digest`、`_image_file_archive`、`path.rsplit`、`IMAGE_SOURCES.items`、`image_source_identity`。 返回路径：L279的`actual`。
- `browser_source_identity`（L282–L283）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha`。 返回路径：L283的`{name: sha(ROOT / name) for name in BROWSER_SOURCES}`。
- `require_browser_acceptance`（L286–L336）：接收`image`。 控制顺序：L288按`BROWSER_ACCEPTANCE.stat().st_size > 100000`分支；L289抛异常，停止当前正常路径；L309按`not isinstance(record, dict) or set(record) != { "protocol", "passed", "image", "mock…`分支；L335抛异常，停止当前正常路径。 调用`browser_image_identity`、`BROWSER_ACCEPTANCE.stat`、`ValueError`、`json.loads`、`BROWSER_ACCEPTANCE.read_text`、`selected_policy`、`isinstance`、`set`、`record.get`等。 返回路径：L336的`image`。
- `browser_image_identity`（L339–L343）：接收`image`。 控制顺序：L341按`not re.fullmatch(r"sha256:[a-f0-9]{64}", image)`分支；L342抛异常，停止当前正常路径。 调用`os.environ.get`、`re.fullmatch`、`ValueError`。 返回路径：L343的`image`。
- `_remaining`（L346–L350）：接收`deadline`、`message`。 控制顺序：L348按`remaining <= 0`分支；L349抛异常，停止当前正常路径。 调用`time.monotonic`、`TimeoutError`。 返回路径：L350的`remaining`。
- `_pipe_pause`（L353–L354）：接收`deadline`、`message`。 调用`time.sleep`、`min`、`_remaining`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_read_pipe`（L357–L374）：接收`stream`、`deadline`、`message`。 源码说明：Read one bounded chunk or EOF, without socket-only Windows selectors. Python 3.14 supports nonblocking anonymous pipes on Windows and POSIX. Empty/full pipes raise BlockingIOError; only a successful e。 控制顺序：L366在`True`成立时循环。 调用`stream.fileno`、`os.set_blocking`、`_remaining`、`os.read`、`_pipe_pause`。 返回路径：L374的`chunk`。
- `_write_pipe`（L377–L392）：接收`stream`、`data`、`deadline`。 控制顺序：L382在`view`成立时循环；L388按`written`分支。 调用`stream.fileno`、`os.set_blocking`、`memoryview`、`_remaining`、`os.write`、`_pipe_pause`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `worker_command`（L395–L436）：接收`image`、`name`。 控制顺序：L396按`not re.fullmatch(r"sha256:[a-f0-9]{64}", image)`分支；L397抛异常，停止当前正常路径；L398按`not re.fullmatch(r"rnd-browser-[a-f0-9]{32}", name)`分支；L399抛异常，停止当前正常路径；L401按`policy is not None`分支。 调用`re.fullmatch`、`ValueError`、`selected_policy`、`runtime_identity`、`str`。 返回路径：L403的`[ *DOCKER, "create", "--name", name, "--pull=never", "--network=none", "--read-only", "--c…`。
- `apparmor_runtime_env`（L439–L445）：接收`value`。 调用`isinstance`、`all`、`item.startswith`。 返回路径：L440的`isinstance(value, list) and all(isinstance(item, str) for item in value) and [item for ite…`。
- `require_worker_inspection`（L448–L500）：接收`value`、`image`。 控制顺序：L449按`not isinstance(value, list) or len(value) != 1`分支；L450抛异常，停止当前正常路径；L466按`record.get("Image") != image or config.get("User") != "1000:1000" or any(host.get(k) …`分支；L490按`not security_options_match(host.get("SecurityOpt"))`分支；L492按`selected_policy() is not None`分支；L493按`record.get("AppArmorProfile") != "docker-default"`分支；L495按`not apparmor_runtime_env(config.get("Env"))`分支；L497抛异常，停止当前正常路径。 调用`isinstance`、`len`、`ValueError`、`record.get`、`config.get`、`any`、`host.get`、`expected.items`、`security_options_match`等。 返回路径：L500的`{"image": image, "network": "none", "bounded": True}`。
- `relay_request`（L503–L581）：接收`client`、`frame`、`deadline`。 源码说明：Candidate-controlled requests cannot select a host, token, or proxy.。 控制顺序：L505按`not isinstance(frame, dict) or set(frame) != { "type", "id", "method", "path", "heade…`分支；L513抛异常，停止当前正常路径；L514按`frame["type"] != "request" or type(frame["id"]) is not int or not 1 <= frame["id"] <=…`分支；L519抛异常，停止当前正常路径；L521按`not isinstance(path, str) or len(path) > 8192 or not path.startswith("/") or path.sta…`分支；L532抛异常，停止当前正常路径；L533按`frame["method"] not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}`分支；L534抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`set`、`ValueError`、`type`、`len`、`path.startswith`、`any`、`ord`、`urlsplit`等。 返回路径：L575的`{ "type": "response", "id": frame["id"], "status": response.status_code, "headers": output…`。
- `execute_worker`（L584–L687）：接收`payload`、`url`、`token`、`timeout`、`image`。 源码说明：Bound stdout before parsing; bound runtime independently of HTTP progress.。 控制顺序：L587按`origin.scheme != "http" or origin.path not in {"", "/"} or origin.query or origin.fra…`分支；L595抛异常，停止当前正常路径；L597按`not (origin.hostname == "127.0.0.1" or (origin.hostname or "").endswith(".localhost")…`分支；L598抛异常，停止当前正常路径；L610按`created.returncode`分支；L611抛异常，停止当前正常路径；L615按`inspected.returncode or len(inspected.stdout) > 100000`分支；L616抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`urlsplit`、`ValueError`、`(origin.hostname or "").endswith`、`bounded_json`、`uuid.uuid4`、`worker_command`、`time.monotonic`、`min`、`max`等。 返回路径：L670的`report`。
- `run_isolated_browser`（L690–L726）：接收`url`、`token`、`scenarios`、`saved`、`timeout`、`image`。 控制顺序：L692按`not selected`分支；L695按`not image or not shutil.which("docker")`分支；L696抛异常，停止当前正常路径；L703抛异常，停止当前正常路径；L710按`error or value is None`分支；L711抛异常，停止当前正常路径；L712按`value["passed"] is False`分支；L713抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`os.environ.get`、`shutil.which`、`BrowserFailure`、`uuid.uuid4`、`browser_contract`、`execute_worker`、`browser_report`、`sha`、`type`等。 返回路径：L693的`[]`；L726的`expected`。

</details>

**创建路径：** `workbench/infrastructure/sandbox/browser/isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L726。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28081`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/browser/isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ed1685918b43d8cf3d9e31151c7d9f4e9dcefea4af4543eb41e8aa9ec70c5a56"} -->
````python
# workbench/infrastructure/sandbox/browser/isolation.py
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
import shutil
import subprocess
import tarfile
import time
import uuid
from urllib.parse import urlsplit

import httpx

from workbench.acceptance.capability_verification import BrowserFailure, browser_report
from workbench.filesystem import sha
from workbench.infrastructure.processes.tools import clean_env
from workbench.infrastructure.sandbox.browser.policy import (
    POLICY_SOURCE,
    runtime_identity,
    security_options_match,
    selected_policy,
)
from workbench.planning.contracts import BrowserStep
from workbench.settings import ROOT

MAX_BODY = 4 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_REQUESTS = 256
MAX_FRAME = 6 * 1024 * 1024
MAX_CONTRACT = 1_000_000
MAX_IMAGE_FILE = 256 * 1024
PIPE_CHUNK = 65536
PIPE_POLL_INTERVAL = 0.001
DOCKER = ["docker", "--host", "unix:///var/run/docker.sock"]


BROWSER_SOURCES = (
    "workbench/infrastructure/sandbox/browser/policy.py",
    POLICY_SOURCE,
    "scripts/capability_browser_seccomp_probe.c",
    "scripts/capability_browser_apparmor.cjs",
    "workbench/infrastructure/sandbox/browser/isolation.py",
    "workbench/acceptance/capability_verification.py",
    "scripts/capability_browser.cjs",
    "scripts/capability_browser_worker.cjs",
    "scripts/capability_browser_network_probe.cjs",
    "scripts/ci_capability_browser_isolation.py",
    "scripts/browser_memory_observation.py",
    "tools/browser/Dockerfile",
    "tools/browser/seccomp.playwright-1.56.1.json",
    "workbench/__init__.py",
    "workbench/_compat/__init__.py",
    "workbench/_compat/aliases.py",
    "workbench/acceptance/__init__.py",
    "workbench/business/__init__.py",
    "workbench/business/modules/__init__.py",
    "workbench/capability_sandbox.py",
    "workbench/cli.py",
    "workbench/coding/__init__.py",
    "workbench/core/__init__.py",
    "workbench/daytona_worker.py",
    "workbench/delivery/__init__.py",
    "workbench/extensions/__init__.py",
    "workbench/generation/__init__.py",
    "workbench/generation/native/__init__.py",
    "workbench/infrastructure/__init__.py",
    "workbench/infrastructure/llm/__init__.py",
    "workbench/infrastructure/native/__init__.py",
    "workbench/infrastructure/persistence/__init__.py",
    "workbench/infrastructure/processes/__init__.py",
    "workbench/infrastructure/sandbox/__init__.py",
    "workbench/infrastructure/sandbox/browser/__init__.py",
    "workbench/infrastructure/sandbox/daytona/__init__.py",
    "workbench/interfaces/__init__.py",
    "workbench/knowledge_services/__init__.py",
    "workbench/models/__init__.py",
    "workbench/planning/__init__.py",
    "workbench/production/__init__.py",
    "workbench/projects/__init__.py",
    "workbench/requirements/__init__.py",
    "workbench/specifications/__init__.py",
    "workbench/specifications/openspec/__init__.py",
    "workbench/templates/__init__.py",
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
        message = "Browser image provenance read timed out"
        while True:
            chunk = _read_pipe(process.stdout, deadline, message)
            if not chunk:
                break
            if len(chunk) > MAX_IMAGE_FILE * 2 - len(output):
                raise ValueError("Browser image provenance archive too large")
            output.extend(chunk)
        if process.wait(timeout=_remaining(deadline, message)):
            raise ValueError("Browser image provenance unavailable")
        _remaining(deadline, message)
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


def _remaining(deadline, message):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError(message)
    return remaining


def _pipe_pause(deadline, message):
    time.sleep(min(PIPE_POLL_INTERVAL, _remaining(deadline, message)))


def _read_pipe(stream, deadline, message):
    """Read one bounded chunk or EOF, without socket-only Windows selectors.

    Python 3.14 supports nonblocking anonymous pipes on Windows and POSIX.
    Empty/full pipes raise BlockingIOError; only a successful empty read is EOF.
    No reader threads or extra handles outlive the owning process cleanup.
    """
    fd = stream.fileno()
    os.set_blocking(fd, False)
    while True:
        _remaining(deadline, message)
        try:
            chunk = os.read(fd, PIPE_CHUNK)
        except BlockingIOError:
            _pipe_pause(deadline, message)
            continue
        _remaining(deadline, message)
        return chunk


def _write_pipe(stream, data, deadline):
    fd = stream.fileno()
    os.set_blocking(fd, False)
    message = "Browser pipe deadline exceeded"
    view = memoryview(data)
    while view:
        _remaining(deadline, message)
        try:
            written = os.write(fd, view[:PIPE_CHUNK])
        except BlockingIOError:
            written = 0
        if written:
            view = view[written:]
        else:
            _pipe_pause(deadline, message)
    _remaining(deadline, message)


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
        _write_pipe(process.stdin, encoded, deadline)
        buffer = bytearray()
        total = count = 0
        report = None
        with httpx.Client(
            base_url=url,
            headers={"x-daytona-preview-token": token},
            follow_redirects=False,
            trust_env=False,
            timeout=5,
        ) as client:
            message = "Browser worker deadline exceeded"
            while True:
                chunk = _read_pipe(process.stdout, deadline, message)
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
            status = process.wait(timeout=_remaining(deadline, message))
            _remaining(deadline, message)
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
