"""Linux sandbox ownership checks for independent launcher shutdown and real restart."""

import os
import signal
import socket
import subprocess
import time

from workbench.tools import stop_process


def stop_native(process, ports):
    """Drain the independent launcher's ExitStack before claiming a real restart.

    Backend and frontend own separate sessions. Killing only the parent can leave
    them alive. A restart is allowed only after all owned server ports are closed.
    """
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGINT)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise RuntimeError("Standalone launcher did not drain its child processes") from None
    for attempt in range(40):
        listening = []
        for port in ports:
            with socket.socket() as connection:
                connection.settimeout(0.2)
                if connection.connect_ex(("127.0.0.1", port)) == 0:
                    listening.append(port)
        if not listening:
            return
        if attempt == 39:
            raise RuntimeError("Standalone shutdown left an application server listening")
        time.sleep(0.25)
