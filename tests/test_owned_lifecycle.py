"""Restart cannot pass by accidentally reusing an orphaned application server."""

import subprocess
from types import SimpleNamespace

import pytest

from workbench import owned_lifecycle as life


@pytest.mark.parametrize("running", [False, True])
def test_shutdown_drains_launcher_before_port_check(monkeypatch, running):
    events = []
    process = SimpleNamespace(
        pid=99, poll=lambda: None if running else 0, wait=lambda **kw: events.append("wait")
    )
    monkeypatch.setattr(
        life.os, "killpg", lambda pid, sig: events.append((pid, sig)), raising=False
    )

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def settimeout(self, value):
            assert value <= 1

        def connect_ex(self, address):
            events.append(address)
            return 111

    monkeypatch.setattr(life.socket, "socket", Connection)
    life.stop_native(process, [48080, 5173])
    assert events[-2:] == [("127.0.0.1", 48080), ("127.0.0.1", 5173)]
    if running:
        assert events[:2] == [(99, life.signal.SIGINT), "wait"]


def test_leftover_application_server_blocks_restart(monkeypatch):
    process = SimpleNamespace(poll=lambda: 0)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def settimeout(self, value):
            pass

        def connect_ex(self, address):
            return 0

    monkeypatch.setattr(life.socket, "socket", Connection)
    monkeypatch.setattr(life.time, "sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="left an application server"):
        life.stop_native(process, [48080])


def test_launcher_timeout_is_not_successful_cleanup(monkeypatch):
    def wait(**kwargs):
        raise subprocess.TimeoutExpired("launcher", 30)

    process = SimpleNamespace(pid=99, poll=lambda: None, wait=wait)
    killed = []
    monkeypatch.setattr(life.os, "killpg", lambda *args: None, raising=False)
    monkeypatch.setattr(life, "stop_process", lambda p: killed.append(p.pid))
    with pytest.raises(RuntimeError, match="did not drain"):
        life.stop_native(process, [48080])
    assert killed == [99]
