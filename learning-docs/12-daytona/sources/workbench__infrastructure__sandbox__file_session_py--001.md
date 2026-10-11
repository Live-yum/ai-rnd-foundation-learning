# workbench/infrastructure/sandbox/file_session.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.errors`、`workbench.filesystem`、`workbench.infrastructure.sandbox.cleanup`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Session`（L23–L198）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Session.__init__`（L24–L81）：接收`settings`、`task`、`selection`、`product`、`deadline`、`path`、`binding`。 控制顺序：L25按`not 15 < deadline - time.monotonic() <= 180`分支；L26抛异常，停止当前正常路径；L81抛异常，停止当前正常路径。 调用`time.monotonic`、`UnsupportedScope`、`dict`、`uuid.uuid4`、`threading.Lock`、`threading.Event`、`queue.Queue`、`write_json`、`receipt`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.read`（L83–L111）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85在`True`成立时循环；L87按`not raw or len(raw) > LIMIT`分支；L88抛异常，停止当前正常路径；L90按`value.get("nonce") != self.binding["nonce"]`分支；L91抛异常，停止当前正常路径；L92按`value.get("event") == "created"`分支；L94按`self.closing or time.monotonic() >= self.work_end`分支；L96按`self.identifier is not None or value.get("name") != self.name or type(value.get("id")…`分支。后续分支沿下方源码相同行号继续阅读。 调用`self.process.stdout.readline`、`len`、`ValueError`、`json.loads`、`value.get`、`time.monotonic`、`type`、`write_json`、`receipt`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.send`（L113–L118）：接收`value`。 控制顺序：L115按`len(raw) > LIMIT or time.monotonic() >= self.work_end`分支；L116抛异常，停止当前正常路径。 调用`json.dumps(value).encode`、`json.dumps`、`len`、`time.monotonic`、`UnsupportedScope`、`self.process.stdin.write`、`self.process.stdin.flush`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.receive`（L120–L132）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L124抛异常，停止当前正常路径；L125按`self.closing or time.monotonic() >= self.work_end or value.get("error") or "result" n…`分支；L131抛异常，停止当前正常路径。 调用`self.answers.get`、`max`、`time.monotonic`、`UnsupportedScope`、`value.get`。 返回路径：L132的`value["result"]`。
- `Session.bind_candidate`（L134–L139）：接收`source`。 控制顺序：L136按`self.closing or time.monotonic() >= self.work_end`分支；L137抛异常，停止当前正常路径。 调用`time.monotonic`、`UnsupportedScope`、`write_json`、`receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.write`（L141–L143）：接收`edits`。 调用`self.send`、`edits.model_dump`、`self.receive`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.snapshot`（L145–L147）：接收`paths`。 调用`self.send`、`self.receive`。 返回路径：L147的`self.receive()`。
- `Session.watch`（L149–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L150按`not self.cancel.wait(max(0, self.work_end - time.monotonic()))`分支。 调用`self.cancel.wait`、`max`、`time.monotonic`、`self.finish`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Session.finish`（L156–L198）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L160按`owner`分支；L163按`self.process is not None`分支；L165按`os.name == "posix"`分支；L168按`self.process.poll() is None`分支；L173遍历`(self.process.stdin, self.process.stdout)`；L197按`not self.done.is_set() or self.error is not None`分支；L198抛异常，停止当前正常路径。 调用`self.cancel.set`、`os.killpg`、`self.process.poll`、`self.process.kill`、`self.process.wait`、`max`、`min`、`time.monotonic`、`pipe.close`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `supervised_environment`（L202–L209）：接收`settings`、`task`、`selection`、`product`、`deadline`、`cleanup_record`、`cleanup_binding`。 调用`Session`、`session.finish`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `main`（L212–L255）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L220按`len(body) > LIMIT`分支；L221抛异常，停止当前正常路径；L243在`True`成立时循环；L245按`not raw or len(raw) > LIMIT`分支；L246抛异常，停止当前正常路径；L248按`request["operation"] == "write"`分支；L251按`request["operation"] == "snapshot"`分支；L254抛异常，停止当前正常路径。 调用`install_loopback_guard`、`sys.stdin.buffer.readline`、`len`、`ValueError`、`json.loads`、`open`、`contextlib.redirect_stdout`、`_local_environment`、`Settings`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.emit`（L225–L227）：接收`value`。 调用`output.write`、`json.dumps`、`output.flush`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/infrastructure/sandbox/file_session.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L259。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10205`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/file_session.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a62506c220432ef25aa71f291c924f46b0506687760dd86e7124cab3d9a92615"} -->
````python
# workbench/infrastructure/sandbox/file_session.py
"""Parent-owned bounded file RPC; no SDK call can hold the controller past its deadline."""

import contextlib
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from workbench.errors import UnsupportedScope
from workbench.filesystem import write_json
from workbench.infrastructure.sandbox.cleanup import delete_owned, receipt
from workbench.tools import clean_env, process_options

LIMIT = 1_200_000


class Session:
    def __init__(self, settings, task, selection, product, deadline, path, binding):
        if not 15 < deadline - time.monotonic() <= 180:
            raise UnsupportedScope("File session requires the original bounded module deadline")
        self.deadline, self.work_end = deadline, deadline - 15
        self.settings, self.path, self.binding = settings, path, dict(binding)
        self.name = (
            ("rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-")
            + "agent-"
            + uuid.uuid4().hex
        )
        self.identifier = None
        self.lock, self.done, self.cancel = threading.Lock(), threading.Event(), threading.Event()
        self.closing, self.error = False, None
        self.answers = queue.Queue(maxsize=2)
        self.process = None
        write_json(path, receipt(self.binding, self.name, None, "create_unconfirmed"))
        keys = (
            "sandbox_provider",
            "daytona_allow_local_execution",
            "daytona_api_url",
            "daytona_snapshot",
            "daytona_snapshots",
            "daytona_target",
            "daytona_runtime_timeout",
            "tool_timeout",
            "capability_execution_enabled",
            "capability_browser_image",
        )
        config = {key: getattr(settings, key) for key in keys}
        config["capability_profile_directory"] = str(settings.capability_profile_directory)
        config["daytona_api_key"] = settings.daytona_api_key.get_secret_value()
        payload = {
            "settings": config,
            "task": task.model_dump(),
            "selection": selection,
            "product": str(Path(product).resolve()),
            "deadline": deadline,
            "name": self.name,
            "nonce": self.binding["nonce"],
        }
        try:
            self.process = subprocess.Popen(
                [sys.executable, "-m", __name__],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                env=clean_env(),
                **process_options(),
            )
            self.reader = threading.Thread(target=self.read, daemon=True)
            self.reader.start()
            self.watchdog = threading.Thread(target=self.watch, daemon=True)
            self.watchdog.start()
            self.send(payload)
            self.receive()
        except BaseException:
            self.finish()
            raise

    def read(self):
        try:
            while True:
                raw = self.process.stdout.readline(LIMIT + 1)
                if not raw or len(raw) > LIMIT:
                    raise ValueError("File worker protocol ended")
                value = json.loads(raw)
                if value.get("nonce") != self.binding["nonce"]:
                    raise ValueError("File worker session binding mismatch")
                if value.get("event") == "created":
                    with self.lock:
                        if self.closing or time.monotonic() >= self.work_end:
                            continue
                        if (
                            self.identifier is not None
                            or value.get("name") != self.name
                            or type(value.get("id")) is not str
                            or not 0 < len(value["id"]) <= 256
                        ):
                            raise ValueError("File worker identity mismatch")
                        self.identifier = value["id"]
                        write_json(self.path, receipt(self.binding, self.name, self.identifier))
                else:
                    self.answers.put(value, timeout=max(0.001, self.work_end - time.monotonic()))
        except Exception:
            try:
                self.answers.put_nowait({"error": True})
            except queue.Full:
                pass

    def send(self, value):
        raw = json.dumps(value).encode() + b"\n"
        if len(raw) > LIMIT or time.monotonic() >= self.work_end:
            raise UnsupportedScope("File RPC exceeds original budget")
        self.process.stdin.write(raw)
        self.process.stdin.flush()

    def receive(self):
        try:
            value = self.answers.get(timeout=max(0, self.work_end - time.monotonic()))
        except queue.Empty:
            raise UnsupportedScope("File SDK deadline exhausted") from None
        if (
            self.closing
            or time.monotonic() >= self.work_end
            or value.get("error")
            or "result" not in value
        ):
            raise UnsupportedScope("File SDK failed or returned after deadline")
        return value["result"]

    def bind_candidate(self, source):
        with self.lock:
            if self.closing or time.monotonic() >= self.work_end:
                raise UnsupportedScope("File session expired")
            self.binding = {**self.binding, "source": source}
            write_json(self.path, receipt(self.binding, self.name, self.identifier))

    def write(self, edits):
        self.send({"operation": "write", "edits": edits.model_dump()})
        self.receive()

    def snapshot(self, paths):
        self.send({"operation": "snapshot", "paths": paths})
        return self.receive()

    def watch(self):
        if not self.cancel.wait(max(0, self.work_end - time.monotonic())):
            try:
                self.finish()
            except UnsupportedScope:
                pass  # Parent RPC/finally observes the stored terminal error.

    def finish(self):
        with self.lock:
            owner = not self.closing
            self.closing = True
        if owner:
            self.cancel.set()
            try:
                if self.process is not None:
                    try:
                        if os.name == "posix":
                            # Kill the owned session before reaping its leader, including inspectors.
                            os.killpg(self.process.pid, signal.SIGKILL)
                        elif self.process.poll() is None:
                            self.process.kill()
                    except ProcessLookupError:
                        pass
                    self.process.wait(timeout=max(0.001, min(2, self.deadline - time.monotonic())))
                    for pipe in (self.process.stdin, self.process.stdout):
                        try:
                            pipe.close()
                        except OSError, ValueError:
                            pass  # The reaped worker owns no remaining SDK transport.
                delete_owned(
                    self.settings,
                    self.name,
                    self.identifier,
                    self.binding,
                    self.path,
                    self.deadline,
                )
            except BaseException as exc:
                self.error = exc
                write_json(
                    self.path,
                    receipt(self.binding, self.name, self.identifier, "deletion_unconfirmed"),
                )
            finally:
                self.done.set()
        else:
            # SDK work is killed at its deadline; allow only bounded child reaping here.
            self.done.wait(max(0, self.deadline - time.monotonic()) + 3)
        if not self.done.is_set() or self.error is not None:
            raise UnsupportedScope("File session cleanup unconfirmed; execution stopped")


@contextlib.contextmanager
def supervised_environment(
    settings, task, selection, product, *, deadline, cleanup_record, cleanup_binding
):
    session = Session(settings, task, selection, product, deadline, cleanup_record, cleanup_binding)
    try:
        yield session
    finally:
        session.finish()


def main():
    from workbench.infrastructure.sandbox.coding import _local_environment
    from workbench.local_only import install_loopback_guard
    from workbench.planning.contracts import CapabilityEdits, CapabilityTaskV2
    from workbench.settings import Settings

    install_loopback_guard()
    body = sys.stdin.buffer.readline(LIMIT + 1)
    if len(body) > LIMIT:
        raise ValueError("File worker payload too large")
    payload = json.loads(body)
    output = sys.stdout

    def emit(value):
        output.write(json.dumps({"nonce": payload["nonce"], **value}) + "\n")
        output.flush()

    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        with _local_environment(
            Settings(_env_file=None, **payload["settings"]),
            CapabilityTaskV2.model_validate(payload["task"]),
            payload["selection"],
            Path(payload["product"]),
            deadline=payload["deadline"],
            owned_name=payload["name"],
            external_cleanup=True,
            on_created=lambda name, identifier: emit(
                {"event": "created", "name": name, "id": identifier}
            ),
        ) as files:
            emit({"result": True})
            while True:
                raw = sys.stdin.buffer.readline(LIMIT + 1)
                if not raw or len(raw) > LIMIT:
                    raise ValueError("File worker request ended")
                request = json.loads(raw)
                if request["operation"] == "write":
                    files.write(CapabilityEdits.model_validate(request["edits"]))
                    result = True
                elif request["operation"] == "snapshot":
                    result = files.snapshot(request["paths"])
                else:
                    raise ValueError("Unknown file-only operation")
                emit({"result": result})


if __name__ == "__main__":
    main()
````
