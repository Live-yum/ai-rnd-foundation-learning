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
        *(["--security-opt=seccomp=" + str(policy)] if policy is not None else []),
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
        or (selected_policy() is not None and record.get("AppArmorProfile") != "docker-default")
        or host.get("Binds")
        or host.get("PortBindings")
        or host.get("Devices")
        or host.get("PidMode")
        or host.get("UTSMode")
        or host.get("Tmpfs") != {"/tmp": "rw,nosuid,nodev,noexec,size=134217728,mode=1777"}
        or host.get("LogConfig", {}).get("Type") != "none"
        or any(m.get("Type") != "tmpfs" for m in record.get("Mounts", []))
    ):
        raise ValueError("Browser worker isolation mismatch")
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
