# scripts/browser_memory_observation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.browser_memory_observation；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_number`（L19–L25）：接收`value`。 控制顺序：L20按`not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,19}", value)`分支；L21抛异常，停止当前正常路径；L23按`result > 2**63 - 1`分支；L24抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`ValueError`、`int`。 返回路径：L25的`result`。
- `_text`（L28–L38）：接收`directory`、`name`。 控制顺序：L31按`not stat.S_ISREG(os.fstat(fd).st_mode)`分支；L32抛异常，停止当前正常路径；L34按`len(raw) > 4096`分支；L35抛异常，停止当前正常路径。 调用`os.open`、`stat.S_ISREG`、`os.fstat`、`ValueError`、`os.read`、`len`、`raw.decode("ascii").strip`、`raw.decode`、`os.close`。 返回路径：L36的`raw.decode("ascii").strip()`。
- `read_cgroup`（L41–L83）：接收`container_id`。 源码说明：Only the two exact Docker cgroup layouts; no process or parent-group scan.。 控制顺序：L43按`type(container_id) is not str or not re.fullmatch(r"[a-f0-9]{64}", container_id)`分支；L45按`not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")`分支；L48遍历`(("system.slice", f"docker-{container_id}.scope"), ("docker", con…`；L53遍历`parts`；L68遍历`_text(fd, "memory.events.local").splitlines()`；L70按`key in COUNTERS`分支；L71按`key in counters`分支；L72抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`type`、`re.fullmatch`、`hasattr`、`os.open`、`opened.append`、`os.fstat`、`_text`、`_number`、`_text(fd, "memory.events.local").splitlines`等。 返回路径：L44的`None`；L46的`None`；L83的`found[0] if len(found) == 1 else None`。
- `counter_delta`（L86–L92）：接收`before`、`after`。 控制顺序：L87按`before is None or after is None`分支；L90按`a.keys() != b.keys() or any(b[key] < a[key] for key in a)`分支。 调用`a.keys`、`b.keys`、`any`。 返回路径：L88的`None`；L91的`None`；L92的`{key: b[key] - a[key] for key in a}`。
- `docker_events`（L95–L139）：接收`docker`、`container_id`、`since`、`until`。 控制顺序：L96按`type(container_id) is not str or not re.fullmatch(r"[a-f0-9]{64}", container_id)`分支；L123按`result.returncode or len(result.stdout) > 8192`分支；L126遍历`result.stdout.splitlines()`；L128按`type(item) is not dict or item.get("id") != container_id or item.get("action") not in…`分支；L137按`len(events) > 16`分支。 调用`type`、`re.fullmatch`、`subprocess.run`、`str`、`clean_env`、`len`、`result.stdout.splitlines`、`json.loads`、`item.get`等。 返回路径：L97的`None`；L124的`None`；L135的`None`。
- `observe_memory`（L143–L160）：接收`inspection`、`name`、`docker`。 控制顺序：L157按`observer is not None`分支。 调用`MemoryObservation`、`observer.start`、`facts.update`、`observer.finish`、`facts.get`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `MemoryObservation`（L163–L253）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `MemoryObservation.__init__`（L164–L177）：接收`inspection`、`name`、`docker`。 调用`type`、`len`、`row.get`、`re.fullmatch`、`threading.Event`、`time.time`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryObservation.sample`（L179–L192）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L181按`observed is None`分支；L184按`self.identity is not None and self.identity != identity`分支；L189按`self.first is None`分支。 调用`read_cgroup`。 返回路径：L182的`None`；L186的`None`；L192的`values`。
- `MemoryObservation.start`（L194–L202）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L195按`self.container_id is None`分支。 调用`self.sample`、`threading.Thread`、`self.thread.start`、`self.stop.set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryObservation.poll`（L204–L212）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L207遍历`range(300)`；L208按`self.stop.wait(0.1) or time.monotonic() >= deadline`分支。 调用`time.monotonic`、`range`、`self.stop.wait`、`self.sample`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `MemoryObservation.finish`（L214–L253）：接收`stopped`。 控制顺序：L216按`self.container_id is None`分支；L219按`stopped and self.thread is not None`分支；L221按`self.thread.is_alive()`分支。 调用`self.stop.set`、`self.thread.join`、`self.thread.is_alive`、`self.sample`、`time.time`、`docker_events`、`counter_delta`。 返回路径：L217的`{"available": False}`；L222的`{"available": False, "container_id": self.container_id}`；L235的`{ "available": self.samples > 0 or events is not None, "container_id": self.container_id, …`。

</details>

**创建路径：** `scripts/browser_memory_observation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L253。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8859`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/browser_memory_observation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3d282f5cefc34c1c460d10847135f3850e417f89287545dc177b77e605b645e7"} -->
````python
# scripts/browser_memory_observation.py
"""Optional, read-only facts for one owned memory probe; never acceptance evidence."""

import json
import os
import re
import stat
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from workbench.tools import clean_env

CGROUP_ROOT = Path("/sys/fs/cgroup")
COUNTERS = ("max", "oom", "oom_kill", "oom_group_kill")


def _number(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,19}", value):
        raise ValueError("Invalid finite counter")
    result = int(value)
    if result > 2**63 - 1:
        raise ValueError("Counter exceeds bound")
    return result


def _text(directory, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("Not a regular cgroup counter")
        raw = os.read(fd, 4097)
        if len(raw) > 4096:
            raise ValueError("Counter exceeds byte bound")
        return raw.decode("ascii").strip()
    finally:
        os.close(fd)


def read_cgroup(container_id):
    """Only the two exact Docker cgroup layouts; no process or parent-group scan."""
    if type(container_id) is not str or not re.fullmatch(r"[a-f0-9]{64}", container_id):
        return None
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        return None
    found = []
    for parts in (("system.slice", f"docker-{container_id}.scope"), ("docker", container_id)):
        opened = []
        try:
            fd = os.open(CGROUP_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            opened.append(fd)
            for part in parts:
                fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                opened.append(fd)
            identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
            limit = _text(fd, "memory.max")
            values = {
                "memory_max": None if limit == "max" else _number(limit),
                "memory_unbounded": limit == "max",
                "memory_current": _number(_text(fd, "memory.current")),
            }
            try:
                values["memory_peak"] = _number(_text(fd, "memory.peak"))
            except FileNotFoundError:
                values["memory_peak"] = None
            counters = {}
            for line in _text(fd, "memory.events.local").splitlines():
                key, value = line.split()
                if key in COUNTERS:
                    if key in counters:
                        raise ValueError("Duplicate counter")
                    counters[key] = _number(value)
            if not {"max", "oom", "oom_kill"} <= counters.keys():
                raise ValueError("Missing counters")
            values["events_local"] = counters
            found.append((identity, values))
        except OSError, ValueError:
            pass
        finally:
            for fd in reversed(opened):
                os.close(fd)
    return found[0] if len(found) == 1 else None


def counter_delta(before, after):
    if before is None or after is None:
        return None
    a, b = before["events_local"], after["events_local"]
    if a.keys() != b.keys() or any(b[key] < a[key] for key in a):
        return None
    return {key: b[key] - a[key] for key in a}


def docker_events(docker, container_id, since, until):
    if type(container_id) is not str or not re.fullmatch(r"[a-f0-9]{64}", container_id):
        return None
    result = subprocess.run(
        [
            *docker,
            "events",
            "--since",
            str(since),
            "--until",
            str(until),
            "--filter",
            "type=container",
            "--filter",
            "container=" + container_id,
            "--filter",
            "event=oom",
            "--filter",
            "event=kill",
            "--filter",
            "event=die",
            "--format",
            '{"action":{{json .Action}},"id":{{json .Actor.ID}},"time_nano":{{json .TimeNano}}}',
        ],
        capture_output=True,
        timeout=2,
        env=clean_env(),
    )
    if result.returncode or len(result.stdout) > 8192:
        return None
    events = []
    for line in result.stdout.splitlines():
        item = json.loads(line)
        if (
            type(item) is not dict
            or item.get("id") != container_id
            or item.get("action") not in {"oom", "kill", "die"}
            or type(item.get("time_nano")) is not int
            or not 0 <= item["time_nano"] <= 2**63 - 1
        ):
            return None
        events.append({"action": item["action"], "time_nano": item["time_nano"]})
        if len(events) > 16:
            return None
    return events


@contextmanager
def observe_memory(inspection, name, docker):
    facts = {"available": False}
    observer = None
    try:
        observer = MemoryObservation(inspection, name, docker)
        observer.start()
    except Exception:
        pass
    try:
        yield facts
    finally:
        # Runs after the original inspect/acceptance decision, so diagnostics
        # cannot delay that inspection or replace its original result/error.
        try:
            if observer is not None:
                facts.update(observer.finish(stopped=facts.get("container_stopped") is True))
        except Exception:
            pass


class MemoryObservation:
    def __init__(self, inspection, name, docker):
        row = inspection[0] if type(inspection) is list and len(inspection) == 1 else {}
        value = row.get("Id") if type(row) is dict and row.get("Name") == "/" + name else None
        self.container_id = (
            value if type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) else None
        )
        self.docker = docker
        self.stop = threading.Event()
        self.thread = None
        self.identity = None
        self.identity_changed = False
        self.before = self.first = self.last = None
        self.samples = 0
        self.since = time.time()

    def sample(self):
        observed = read_cgroup(self.container_id)
        if observed is None:
            return None
        identity, values = observed
        if self.identity is not None and self.identity != identity:
            self.identity_changed = True
            return None
        self.identity = identity
        self.samples += 1
        if self.first is None:
            self.first = values
        self.last = values
        return values

    def start(self):
        if self.container_id is None:
            return
        try:
            self.before = self.sample()
            self.thread = threading.Thread(target=self.poll, daemon=True)
            self.thread.start()
        except Exception:
            self.stop.set()

    def poll(self):
        deadline = time.monotonic() + 30
        try:
            for _ in range(300):
                if self.stop.wait(0.1) or time.monotonic() >= deadline:
                    return
                self.sample()
        except Exception:
            return

    def finish(self, *, stopped=False):
        self.stop.set()
        if self.container_id is None:
            return {"available": False}
        try:
            if stopped and self.thread is not None:
                self.thread.join(timeout=0.5)
                if self.thread.is_alive():
                    return {"available": False, "container_id": self.container_id}
            # Never delay cleanup with joins, extra reads or Docker queries
            # when the original inspection has not confirmed termination.
            after = self.sample() if stopped else None
            until = time.time()
            try:
                events = (
                    docker_events(self.docker, self.container_id, self.since, until)
                    if stopped
                    else None
                )
            except Exception:
                events = None
            return {
                "available": self.samples > 0 or events is not None,
                "container_id": self.container_id,
                "identity_changed": self.identity_changed,
                "sample_count": self.samples,
                "pre_start": self.before,
                "post_start_return": after,
                "first_observed": self.first,
                "last_observed": self.last,
                "pre_post_delta": None
                if self.identity_changed
                else counter_delta(self.before, after),
                "observed_delta": None
                if self.identity_changed
                else counter_delta(self.first, self.last),
                "docker_events": events,
            }
        except Exception:
            return {"available": False, "container_id": self.container_id}
````
