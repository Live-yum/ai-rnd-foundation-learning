"""Bounded, resumable application pause inside an already isolated sandbox.

The controller sends this trusted stdlib-only source to the sandbox's root
control interpreter. It is never imported from the candidate product. Signals
target only its dedicated application identity, through pinned pidfds. The
reader is a separately bounded child so a failed SQLite read cannot strand the
application in a stopped state. Container deletion remains the outer fail-safe
if the supervisor itself is forcibly killed.
"""

import os
import pathlib
import signal
import subprocess
import sys
import time

APP_UID = 20000
MAX_TASKS = 4096
GONE_PROCESS = (FileNotFoundError, ProcessLookupError)


def task_inventory(uid=APP_UID):
    """Include live worker threads even when their group leader is a zombie."""
    paths = list(pathlib.Path("/proc").glob("[0-9]*/task/[0-9]*/status"))
    if len(paths) > MAX_TASKS:
        raise RuntimeError("Application task inventory budget exceeded")
    tasks = {}
    for path in paths:
        try:
            fields = dict(line.split(":", 1) for line in path.read_text().splitlines())
            uids = tuple(int(value) for value in fields["Uid"].split())
            state = fields["State"].split()[0]
            if uid not in uids or state in {"Z", "X"}:
                continue
            # Start time plus monotonic scheduling counters bind each stopped
            # thread. Rechecking these after the read detects even a cooperating
            # sibling's SIGCONT/write/SIGSTOP race that ended stopped again.
            start = int(path.with_name("stat").read_text().rsplit(")", 1)[1].split()[19])
            tasks[int(fields["Tgid"]), int(fields["Pid"])] = (
                state,
                uids,
                start,
                int(fields["voluntary_ctxt_switches"]),
                int(fields["nonvoluntary_ctxt_switches"]),
            )
        except GONE_PROCESS:
            pass
    return tasks


class ApplicationPause:
    def __init__(self, deadline, *, uid=APP_UID):
        self.deadline = deadline
        self.uid = uid
        self.handles = {}
        self.baseline = None

    def _stop(self, pid):
        if pid not in self.handles:
            fd = os.pidfd_open(pid)
            try:
                fields = dict(
                    line.split(":", 1)
                    for line in pathlib.Path("/proc", str(pid), "status").read_text().splitlines()
                )
                if self.uid not in [int(value) for value in fields["Uid"].split()]:
                    raise RuntimeError("Application identity changed during pause")
            except BaseException:
                os.close(fd)
                raise
            self.handles[pid] = fd
        signal.pidfd_send_signal(self.handles[pid], signal.SIGSTOP)

    def __enter__(self):
        try:
            previous = None
            while time.monotonic() < self.deadline:
                current = task_inventory(self.uid)
                if not current:
                    raise RuntimeError("No live application identity to pause")
                if all(value[0] == "T" for value in current.values()) and current == previous:
                    self.baseline = current
                    return self
                for pid in {pid for pid, _ in current}:
                    try:
                        self._stop(pid)
                    except GONE_PROCESS:
                        pass
                previous = current
                time.sleep(0.01)
            raise TimeoutError("Application did not reach stable quiescence")
        except BaseException:
            self.resume()
            raise

    def verify(self):
        if self.baseline is None or task_inventory(self.uid) != self.baseline:
            raise RuntimeError("Application ran or changed during physical observation")

    def resume(self):
        failed = False
        for fd in self.handles.values():
            try:
                signal.pidfd_send_signal(fd, signal.SIGCONT)
            except ProcessLookupError:
                pass
            except OSError:
                failed = True
            finally:
                os.close(fd)
        self.handles.clear()
        if failed:
            raise RuntimeError("Application resume was not confirmed")

    def __exit__(self, *exc):
        self.resume()


def supervise(argv, budget):
    if not 0 < budget <= 12:
        raise ValueError("Invalid quiescence deadline")
    end = time.monotonic() + budget
    with ApplicationPause(min(end, time.monotonic() + 3)) as pause:
        remaining = end - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Physical observation deadline expired")
        result = subprocess.run(
            argv,
            capture_output=True,
            timeout=min(remaining, 5),
            check=False,
        )
        pause.verify()
        if result.returncode or len(result.stdout) > 65536:
            raise RuntimeError("Physical reader failed")
    # No successful receipt escapes until all pinned process groups were resumed.
    return result.stdout


def main():
    def interrupted(signum, frame):
        raise TimeoutError("Physical observation interrupted")

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    # Only a random root-private request path crosses the process boundary.
    # The reader opens it after ApplicationPause succeeds; no challenge/key/
    # expected value is ever exposed through argv or the inherited environment.
    budget = float(sys.argv[2])
    output = supervise([sys.executable, "-I", "-S", "-c", sys.argv[3], sys.argv[1]], budget)
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
