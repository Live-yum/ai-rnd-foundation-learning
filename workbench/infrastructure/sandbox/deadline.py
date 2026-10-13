"""Deadline for a dedicated verifier process, independent of SDK SIGALRM timers."""

import math
import os
import signal
import threading
import time


class CheckpointExpired(BaseException):
    """Escape SDK Exception handlers into owned cleanup; never business feedback."""


class CheckpointDeadline:
    def __init__(self, deadline):
        if (
            type(deadline) not in (int, float)
            or not math.isfinite(deadline)
            or not 10 < deadline - time.monotonic() <= 180
            or not hasattr(signal, "SIGUSR1")
            or threading.current_thread() is not threading.main_thread()
        ):
            raise ValueError("Checkpoint requires a dedicated POSIX process and cleanup reserve")
        self.deadline = deadline
        self.cleanup = False
        self.closed = False
        self.wake = threading.Event()

    def enter_cleanup(self):
        self.cleanup = True
        self.wake.set()

    def expire(self, signum, frame):
        if self.closed:
            return
        end = self.deadline if self.cleanup else self.deadline - 10
        if time.monotonic() < end:
            return  # A queued soft signal cannot interrupt an already-started cleanup.
        if self.cleanup:
            self.closed = True
        self.enter_cleanup()
        raise CheckpointExpired("Checkpoint deadline exhausted")

    def watch(self):
        while not self.closed:
            end = self.deadline if self.cleanup else self.deadline - 10
            if self.wake.wait(max(0, end - time.monotonic())):
                self.wake.clear()
                continue
            if not self.closed:
                os.kill(os.getpid(), signal.SIGUSR1)
            self.wake.wait(0.01)

    def __enter__(self):
        self.previous = signal.signal(signal.SIGUSR1, self.expire)
        self.thread = threading.Thread(target=self.watch, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.closed = True
        self.wake.set()
        self.thread.join(timeout=0.2)
        signal.signal(signal.SIGUSR1, self.previous)
