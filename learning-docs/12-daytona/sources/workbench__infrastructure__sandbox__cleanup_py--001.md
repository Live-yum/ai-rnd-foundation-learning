# workbench/infrastructure/sandbox/cleanup.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.errors`、`workbench.filesystem`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `failure_kind`（L30–L32）：接收`exc`。 调用`type`。 返回路径：L32的`name if name in FAILURE_KINDS else "other"`。
- `receipt`（L35–L42）：接收`binding`、`name`、`identifier`、`reason`。 返回路径：L36的`{ "binding": binding, "sandbox_name": name, "sandbox_id": identifier, "status": "pending" …`。
- `confirm_deleted`（L45–L61）：接收`client`、`target`、`deadline`、`timeout_cap`。 控制顺序：L49按`remaining <= 0`分支；L50抛异常，停止当前正常路径；L53在`time.monotonic() < deadline`成立时循环；L57按`time.monotonic() >= deadline`分支；L58抛异常，停止当前正常路径；L61抛异常，停止当前正常路径。 调用`min`、`time.monotonic`、`TimeoutError`、`client.delete`、`client.get`、`time.sleep`、`max`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `delete_owned`（L64–L123）：接收`settings`、`name`、`identifier`、`binding`、`path`、`deadline`。 控制顺序：L65按`not NAME.fullmatch(name)`分支；L66抛异常，停止当前正常路径；L98按`not process.returncode and len(output) <= 4096`分支；L100按`diagnostic.get("binding") == binding and diagnostic.get("deleted") is False and diagn…`分支；L107按`late or unresolved_create`分支；L108抛异常，停止当前正常路径；L109按`time.monotonic() >= end or process.returncode or len(output) > 4096`分支；L110抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`NAME.fullmatch`、`UnsupportedScope`、`time.monotonic`、`receipt`、`write_json`、`getattr`、`settings.daytona_api_key.get_secret_value`、`subprocess.Popen`、`clean_env`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `perform`（L126–L144）：接收`payload`。 控制顺序：L132按`not NAME.fullmatch(payload["name"])`分支；L133抛异常，停止当前正常路径；L137按`target.name != payload["name"] or ( payload["identifier"] is not None and target.id !…`分支；L140抛异常，停止当前正常路径。 调用`install_loopback_guard`、`NAME.fullmatch`、`ValueError`、`client_for`、`Settings`、`client.get`、`confirm_deleted`、`close_client`。 返回路径：L142的`{"binding": payload["binding"], "deleted": True}`。
- `main`（L147–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L152按`len(body) > 16384`分支；L153抛异常，停止当前正常路径。 调用`sys.stdin.buffer.read`、`len`、`ValueError`、`open`、`contextlib.redirect_stdout`、`json.loads`、`perform`、`failure_kind`、`print`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `public_receipt`（L168–L227）：接收`path`、`task`、`plan`。 控制顺序：L173按`path.stat().st_size > 4096`分支；L177按`set(bound) != {"task", "plan", "source", "nonce"} or bound["task"] != digest(task.mod…`分支；L207按`value.get("failure_phase") in PHASES and value.get("failure_kind") in FAILURE_KINDS`分支；L209按`value.get("cleanup_failure_kind") in FAILURE_KINDS`分支；L211按`value.get("supervision_failure_phase") in SUPERVISION_PHASES and value.get("supervisi…`分支。 调用`path.stat`、`json.loads`、`path.read_text`、`set`、`digest`、`task.model_dump`、`plan.model_dump`、`type`、`re.fullmatch`等。 返回路径：L174的`unknown`；L199的`unknown`；L219的`{ **extra, "status": value["status"], "reason": value["reason"], "binding": bound, "sandbo…`。
- `checkpoint_receipts`（L230–L274）：接收`workspace`、`task`、`plan`。 源码说明：Project at most eight owned checkpoint receipts before ephemeral source removal.。 控制顺序：L237遍历`range(1, 9)`；L240按`not path.exists()`分支；L244按`path.stat().st_size > 1_000_000`分支；L245抛异常，停止当前正常路径；L248按`type(bound["nonce"]) is not str or not re.fullmatch("[a-f0-9]{32}", bound["nonce"]) o…`分支；L259抛异常，停止当前正常路径。 调用`range`、`path.exists`、`path.stat`、`ValueError`、`json.loads`、`path.read_text`、`type`、`re.fullmatch`、`digest`等。 返回路径：L274的`result`。

</details>

**创建路径：** `workbench/infrastructure/sandbox/cleanup.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L278。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10374`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/cleanup.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3e06492d07abe222df05ae1772c1102bebd2877ac45e8cb60619a6f99512d3bc"} -->
````python
# workbench/infrastructure/sandbox/cleanup.py
"""Owned coding-sandbox deletion; the parent alone publishes terminal cleanup state."""

import json
import re
import subprocess
import sys
import time

from workbench.errors import UnsupportedScope
from workbench.filesystem import write_json
from workbench.tools import clean_env, process_options

NAME = re.compile(r"rnd-source-(?:native-)?agent-[a-f0-9]{32}")


FAILURE_KINDS = {
    "PrerequisiteError",
    "UnsupportedScope",
    "ValueError",
    "TimeoutError",
    "DaytonaNotFoundError",
    "DaytonaTimeoutError",
    "DaytonaAuthorizationError",
    "DaytonaAuthenticationError",
    "DaytonaError",
    "other",
}


def failure_kind(exc):
    name = type(exc).__name__
    return name if name in FAILURE_KINDS else "other"


def receipt(binding, name, identifier, reason="pending"):
    return {
        "binding": binding,
        "sandbox_name": name,
        "sandbox_id": identifier,
        "status": "pending" if reason == "pending" else "unconfirmed",
        "reason": reason,
    }


def confirm_deleted(client, target, deadline, timeout_cap):
    from daytona.common.errors import DaytonaNotFoundError

    remaining = min(timeout_cap, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError("Cleanup deadline")
    identifier = target.id
    client.delete(target, timeout=remaining)
    while time.monotonic() < deadline:
        try:
            client.get(identifier)
        except DaytonaNotFoundError:
            if time.monotonic() >= deadline:
                raise TimeoutError("Deletion confirmation arrived after deadline") from None
            return
        time.sleep(min(0.05, max(0, deadline - time.monotonic())))
    raise TimeoutError("Deletion not confirmed absent")


def delete_owned(settings, name, identifier, binding, path, deadline):
    if not NAME.fullmatch(name):
        raise UnsupportedScope("Cleanup ownership name rejected")
    late = time.monotonic() >= deadline
    unresolved_create = identifier is None
    value = receipt(
        binding,
        name,
        identifier,
        "module_deadline" if late else "create_unconfirmed" if unresolved_create else "pending",
    )
    write_json(path, value)
    end = time.monotonic() + 1 if late else deadline
    payload = {
        "name": name,
        "identifier": identifier,
        "binding": binding,
        "deadline": end,
        "settings": {key: getattr(settings, key) for key in ("daytona_api_url", "daytona_target")},
    }
    payload["settings"]["daytona_api_key"] = settings.daytona_api_key.get_secret_value()
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "workbench.infrastructure.sandbox.cleanup"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=clean_env(),
            **process_options(),
        )
        output, _ = process.communicate(
            json.dumps(payload).encode(), timeout=max(0, end - time.monotonic())
        )
        if not process.returncode and len(output) <= 4096:
            diagnostic = json.loads(output)
            if (
                diagnostic.get("binding") == binding
                and diagnostic.get("deleted") is False
                and diagnostic.get("failure_kind") in FAILURE_KINDS
            ):
                value["cleanup_failure_kind"] = diagnostic["failure_kind"]
                write_json(path, value)
        if late or unresolved_create:
            raise UnsupportedScope("Terminated cleanup state cannot be upgraded by a late result")
        if time.monotonic() >= end or process.returncode or len(output) > 4096:
            raise UnsupportedScope("Cleanup result missing or late")
        result = json.loads(output)
        if result != {"binding": binding, "deleted": True}:
            raise UnsupportedScope("Cleanup acknowledgement binding rejected")
        value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)
    except BaseException:
        if value["status"] == "pending":
            value.update(status="unconfirmed", reason="deletion_unconfirmed")
            write_json(path, value)
        if process is not None and process.poll() is None:
            process.kill()  # no SDK callback or late child can write this parent-owned journal
            process.wait(timeout=2)
        raise


def perform(payload):
    from workbench.local_only import install_loopback_guard
    from workbench.sandbox import client_for, close_client
    from workbench.settings import Settings

    install_loopback_guard()
    if not NAME.fullmatch(payload["name"]):
        raise ValueError("Unowned cleanup target")
    client = client_for(Settings(_env_file=None, **payload["settings"]))
    try:
        target = client.get(payload["identifier"] or payload["name"])
        if target.name != payload["name"] or (
            payload["identifier"] is not None and target.id != payload["identifier"]
        ):
            raise ValueError("Cleanup identity mismatch")
        confirm_deleted(client, target, payload["deadline"], 120)
        return {"binding": payload["binding"], "deleted": True}
    finally:
        close_client(client)


def main():
    import contextlib
    import os

    body = sys.stdin.buffer.read(16385)
    if len(body) > 16384:
        raise ValueError("Cleanup request too large")
    # SDK output is not protocol data and must not escape to the parent.
    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        payload = json.loads(body)
        try:
            result = perform(payload)
        except Exception as exc:
            result = {
                "binding": payload["binding"],
                "deleted": False,
                "failure_kind": failure_kind(exc),
            }
    print(json.dumps(result))


def public_receipt(path, task, plan):
    from workbench.core.contracts import digest

    unknown = {"status": "unconfirmed", "reason": "invalid_or_missing"}
    try:
        if path.stat().st_size > 4096:
            return unknown
        value = json.loads(path.read_text())
        bound = value["binding"]
        if (
            set(bound) != {"task", "plan", "source", "nonce"}
            or bound["task"] != digest(task.model_dump())
            or bound["plan"] != digest(plan.model_dump())
            or type(bound["source"]) is not str
            or not re.fullmatch("[a-f0-9]{64}", bound["source"])
            or type(bound["nonce"]) is not str
            or not re.fullmatch("[a-f0-9]{32}", bound["nonce"])
            or type(value["sandbox_name"]) is not str
            or not NAME.fullmatch(value["sandbox_name"])
            or value["status"] not in ("pending", "unconfirmed", "deleted")
            or value["reason"]
            not in (
                "pending",
                "confirmed_absent",
                "module_deadline",
                "create_unconfirmed",
                "deletion_unconfirmed",
                "transport_cleanup",
            )
            or (value["status"] == "deleted" and value["reason"] != "confirmed_absent")
        ):
            return unknown
        extra = {}
        from workbench.infrastructure.sandbox.file_session import (
            PHASES,
            SUPERVISION_KINDS,
            SUPERVISION_PHASES,
        )

        if value.get("failure_phase") in PHASES and value.get("failure_kind") in FAILURE_KINDS:
            extra.update(failure_phase=value["failure_phase"], failure_kind=value["failure_kind"])
        if value.get("cleanup_failure_kind") in FAILURE_KINDS:
            extra["cleanup_failure_kind"] = value["cleanup_failure_kind"]
        if (
            value.get("supervision_failure_phase") in SUPERVISION_PHASES
            and value.get("supervision_failure_kind") in SUPERVISION_KINDS
        ):
            extra.update(
                supervision_failure_phase=value["supervision_failure_phase"],
                supervision_failure_kind=value["supervision_failure_kind"],
            )
        return {
            **extra,
            "status": value["status"],
            "reason": value["reason"],
            "binding": bound,
            "sandbox_name": value["sandbox_name"],
        }
    except OSError, ValueError, TypeError, KeyError:
        return unknown


def checkpoint_receipts(workspace, task, plan):
    """Project at most eight owned checkpoint receipts before ephemeral source removal."""
    from workbench.capability_diagnostics import node_diagnostic
    from workbench.core.contracts import digest
    from workbench.filesystem import manifest

    result = []
    for step in range(1, 9):
        candidate = workspace / f"step-{step}"
        path = workspace / f"step-{step}-node-verification.json"
        if not path.exists():
            continue
        item = {"step": step, "cleanup": "unconfirmed", "binding_valid": False}
        try:
            if path.stat().st_size > 1_000_000:
                raise ValueError("Oversized checkpoint receipt")
            value = json.loads(path.read_text())
            bound = value["checkpoint"]
            if (
                type(bound["nonce"]) is not str
                or not re.fullmatch("[a-f0-9]{32}", bound["nonce"])
                or bound["task"] != digest(task.model_dump())
                or value["plan_digest"] != digest(plan.model_dump())
                or value["source_digest"] != digest(manifest(candidate))
                or type(value["sandbox_name"]) is not str
                or not re.fullmatch(
                    r"rnd-(?:source-(?:native-)?|capability-)[a-f0-9]{32}", value["sandbox_name"]
                )
            ):
                raise ValueError("Checkpoint binding rejected")
            item.update(node_diagnostic(candidate, aggregate=False))
            item.update(
                binding_valid=True,
                sandbox_name=value["sandbox_name"],
                binding={
                    "task": bound["task"],
                    "plan": value["plan_digest"],
                    "source": value["source_digest"],
                    "nonce": bound["nonce"],
                },
            )
        except OSError, ValueError, TypeError, KeyError:
            pass
        result.append(item)
    return result


if __name__ == "__main__":
    main()
````
