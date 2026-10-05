"""Linux-only stdlib child supervisor; no project/runtime imports or global settings.

An independent process-local subreaper keeps even double-forked descendants owned
until cleanup. It launches exactly one supplied argv, never a shell command.
"""

import ctypes
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
        return int(fields[1]), fields[19]
    except OSError, ValueError, IndexError:
        return None


def descendants():
    root = os.getpid()
    snapshot = {}
    for path in Path("/proc").iterdir():
        if path.name.isdecimal() and (value := identity(int(path.name))):
            snapshot[int(path.name)] = value
    owned = {root}
    while children := {
        pid for pid, value in snapshot.items() if value[0] in owned and pid not in owned
    }:
        owned.update(children)
    return {pid: snapshot[pid][1] for pid in owned if pid != root}


def cleanup():
    deadline = time.monotonic() + 10
    while True:
        # Every adopted child belongs to this dedicated supervisor's only target.
        # Keep start identity checks even though PID recycling is unlikely here.
        for pid, started in descendants().items():
            current = identity(pid)
            if current is not None and current[1] == started:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                return
            if pid == 0:
                break
        if time.monotonic() >= deadline:
            raise RuntimeError("Owned supervisor descendants did not exit")
        time.sleep(0.01)


def main(argv):
    if sys.platform != "linux" or not argv:
        raise RuntimeError("The subreaper supervisor requires Linux and an explicit argv")
    libc = ctypes.CDLL(None, use_errno=True)
    # PR_SET_CHILD_SUBREAPER applies only to this disposable process, not its
    # parent, other jobs, host policy, credentials, or future processes.
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "Cannot establish owned child supervision")
    child = None
    try:
        child = subprocess.Popen(argv)
        returncode = child.wait()
    finally:
        cleanup()
    if returncode < 0:
        if -returncode not in {signal.SIGKILL, signal.SIGSTOP}:
            signal.signal(-returncode, signal.SIG_DFL)
        os.kill(os.getpid(), -returncode)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
