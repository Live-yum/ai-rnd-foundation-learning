"""Read-only process inventory regression; signal only our synthetic child.

Never execute the production UID-wide drain against the test host.
"""

import ast
import os
import pathlib
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest


@pytest.mark.skipif(sys.platform != "linux", reason="Linux thread-group /proc semantics")
def test_restart_inventory_sees_live_thread_under_zombie_group_leader(monkeypatch):
    from workbench import capability_sandbox

    scripts = []

    def capture(_sandbox, argv, _timeout):
        scripts.append(argv[argv.index("-c") + 1])
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(capability_sandbox, "control_exec", capture)
    capability_sandbox.restart_application_identity(None, 8123, 5)
    # Extract only the read-only inventory function, never the signal loop.
    tree = ast.parse(scripts[0])
    inventory = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "live"
    )
    namespace = {"pathlib": pathlib, "uid": os.getuid()}
    exec(
        compile(ast.Module(body=[inventory], type_ignores=[]), "<read-only-inventory>", "exec"),
        namespace,
    )

    source = (
        "import threading,time,ctypes; "
        "threading.Thread(target=lambda:time.sleep(30),daemon=True).start(); "
        "ctypes.CDLL(None).pthread_exit(None)"
    )
    child = subprocess.Popen([sys.executable, "-I", "-S", "-c", source])
    try:
        status_path = pathlib.Path("/proc") / str(child.pid) / "status"
        deadline = time.monotonic() + 5
        while True:
            status = dict(line.split(":", 1) for line in status_path.read_text().splitlines())
            if status["State"].strip().startswith("Z"):
                break
            assert time.monotonic() < deadline, "Synthetic main thread did not exit"
            time.sleep(0.01)
        tasks = list((status_path.parent / "task").glob("*/status"))
        assert len(tasks) >= 2
        assert child.pid in namespace["live"]()
        assert namespace["live"]().count(child.pid) == 1
    finally:
        child.kill()
        child.wait(timeout=5)
