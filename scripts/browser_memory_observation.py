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
    return read_cgroup_observation(container_id)[0]


def read_cgroup_observation(container_id):
    """Classify the same bounded reads, without extra probes or exception text."""
    if type(container_id) is not str or not re.fullmatch(r"[a-f0-9]{64}", container_id):
        return None, "invalid_identity"
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        return None, "unsupported_host"
    found = []
    unavailable = []
    for parts in (("system.slice", f"docker-{container_id}.scope"), ("docker", container_id)):
        opened = []
        stage = "group"
        try:
            fd = os.open(CGROUP_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            opened.append(fd)
            for part in parts:
                fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                opened.append(fd)
            identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
            stage = "counters"
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
        except PermissionError:
            unavailable.append("permission_denied")
        except FileNotFoundError:
            unavailable.append("group_absent" if stage == "group" else "counter_missing")
        except OSError, ValueError:
            unavailable.append("invalid_counter_or_path")
        finally:
            for fd in reversed(opened):
                os.close(fd)
    if len(found) == 1:
        return found[0], "available"
    if len(found) > 1:
        return None, "ambiguous_layout"
    for reason in (
        "permission_denied",
        "invalid_counter_or_path",
        "counter_missing",
        "group_absent",
    ):
        if reason in unavailable:
            return None, reason
    return None, "unavailable"


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
        self.before_status = self.last_read_status = "not_sampled"
        self.samples = 0
        self.since = time.time()

    def sample(self):
        observed, self.last_read_status = read_cgroup_observation(self.container_id)
        if observed is None:
            return None
        identity, values = observed
        if self.identity is not None and self.identity != identity:
            self.identity_changed = True
            self.last_read_status = "identity_changed"
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
            self.before_status = self.last_read_status
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
            after_status = self.last_read_status if stopped else "termination_not_confirmed"
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
                "pre_start_status": self.before_status,
                "post_start_return": after,
                "post_start_return_status": after_status,
                # Legacy key retained; this read follows the original state
                # inspection and thread join, not the start command return.
                "post_start_return_stage": "after_termination_inspect"
                if stopped
                else "not_sampled",
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
