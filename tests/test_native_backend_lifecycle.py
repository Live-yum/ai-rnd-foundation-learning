"""Real loopback/process regressions for owned native-backend restart readiness."""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from workbench import native_environment as native


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def test_occupied_native_port_never_starts_or_contacts_foreign_server(tmp_path, monkeypatch):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        monkeypatch.setattr(
            native.subprocess, "Popen", lambda *a, **k: pytest.fail("unowned port must not spawn")
        )
        monkeypatch.setattr(
            native.httpx,
            "Client",
            lambda *a, **k: pytest.fail("foreign listener must not receive probe"),
        )
        with pytest.raises(RuntimeError, match="already occupied"):
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": str(port)}, tmp_path / "report"
            ):
                pytest.fail("must not become ready")
        assert listener.fileno() >= 0


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/net/tcp").is_file(),
    reason="Linux /proc ownership diagnostics",
)
@pytest.mark.parametrize("descendant", [False, True])
@pytest.mark.parametrize("raise_inside", [False, True])
def test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group(
    tmp_path, monkeypatch, descendant, raise_inside
):
    port = free_port()
    requests = tmp_path / "requests.txt"
    server = tmp_path / "server.py"
    server.write_text(
        """import http.server,json,sys,time
from pathlib import Path
port=int(sys.argv[1]); requests=Path(sys.argv[2])
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  requests.write_text(requests.read_text()+'probe\\n' if requests.exists() else 'probe\\n')
  body=b'{"paths":{}}';self.send_response(200);self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
time.sleep(0.15)
http.server.HTTPServer(('127.0.0.1',port),Handler).serve_forever()
""",
        encoding="utf-8",
    )
    owner = tmp_path / "owner.py"
    owner.write_text(
        "import subprocess,sys\nchild=subprocess.Popen([sys.executable,*sys.argv[1:]])\nchild.wait()\n",
        encoding="utf-8",
    )
    original_popen = subprocess.Popen
    processes = []

    def start(command, **kwargs):
        actual = (
            [sys.executable, str(owner), str(server), str(port), str(requests)]
            if descendant
            else [sys.executable, str(server), str(port), str(requests)]
        )
        process = original_popen(actual, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(native.subprocess, "Popen", start)
    original_client = native.httpx.Client

    class OwnershipCheckedClient:
        def __init__(self, **kwargs):
            self.client = original_client(**kwargs)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.client.close()

        def get(self, url):
            # An HTTP request must never be the operation that discovers a
            # listener: the exact owned group must already own LISTEN first.
            state = native.backend_port_state(port, processes[-1].pid)
            assert state["observable"] and state["owned_listener"]
            return self.client.get(url)

    monkeypatch.setattr(native.httpx, "Client", OwnershipCheckedClient)
    for attempt in range(2):
        report = tmp_path / str(attempt)
        try:
            with native.running_backend(
                "fastapiadmin", tmp_path, {"SERVER_PORT": str(port)}, report
            ) as (url, path):
                assert url == f"http://127.0.0.1:{port}" and path == "/openapi.json"
                assert native.backend_port_state(port, processes[-1].pid)["owned_listener"]
                if raise_inside:
                    raise LookupError("test body failure")
        except LookupError:
            assert raise_inside
        lifecycle = json.loads((report / "backend-lifecycle.json").read_text(encoding="utf-8"))
        assert lifecycle["port"] == port and lifecycle["port_released"] is True
        assert lifecycle["port_state_before_cleanup"]["owned_listener"] is True
        assert lifecycle["returncode"] is not None
        assert native.loopback_port_bindable(port)
    assert requests.read_text(encoding="utf-8").splitlines() == ["probe", "probe"]


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc/net/tcp").is_file(),
    reason="Linux process-group orphan regression",
)
def test_exited_launcher_cannot_leave_its_owned_listener_behind(tmp_path, monkeypatch):
    port = free_port()
    server = "import socket,time; s=socket.socket();s.bind(('127.0.0.1',int(__import__('sys').argv[1])));s.listen();time.sleep(30)"
    launcher = (
        "import subprocess,sys; subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]])"
    )
    original = subprocess.Popen
    processes = []

    def start(command, **kwargs):
        process = original([sys.executable, "-c", launcher, server, str(port)], **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(native.subprocess, "Popen", start)
    with pytest.raises(RuntimeError, match="Native backend exited"):
        with native.running_backend(
            "fastapiadmin", tmp_path, {"SERVER_PORT": str(port)}, tmp_path / "report"
        ):
            pytest.fail("exited launcher must never be accepted")
    result = json.loads((tmp_path / "report/backend-lifecycle.json").read_text(encoding="utf-8"))
    assert result["port_state_before_cleanup"]["owned_group_pids"]
    assert result["port_released"] is True
    assert native.loopback_port_bindable(port)
