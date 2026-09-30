"""The child guard is tested in a fresh interpreter; it never changes pytest's networking."""

import sys

import pytest

from workbench.settings import ROOT
from workbench.tools import run_command


@pytest.mark.parametrize(
    "operation",
    [
        "socket.getaddrinfo('example.com',443)",
        "socket.gethostbyname('localhost')",
        "socket.socket().connect(('127.0.0.1',80))",
        "socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b'x',('127.0.0.1',9))",
        "socket.socket().bind(('127.0.0.1',0))",
    ],
)
def test_aider_guard_blocks_dns_tcp_udp_and_listening(operation):
    runner = ROOT / "tools/aider/offline_runner.py"
    script = (
        f"import runpy,socket; ns=runpy.run_path({str(runner)!r},run_name='guard-test'); "
        "ns['install_offline_guard']()\n"
        f"try:\n {operation}\nexcept PermissionError as e:\n assert 'network access is disabled' in str(e)\n"
        "else:\n raise AssertionError('unguarded network operation')\n"
    )
    assert run_command([sys.executable, "-c", script], ROOT, 20)["returncode"] == 0
