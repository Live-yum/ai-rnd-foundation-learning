"""Local tool policy. Chat model endpoints are deliberately not subject to it.

The socket guard is installed only in the dedicated Daytona child process. It
is a defence against SDK redirects/telemetry, not an OS sandbox for hostile code.
"""

import ipaddress
import os
import socket
import sys
from urllib.parse import urlsplit, urlunsplit

DAYTONA_VERSION = "0.190.0"
DAYTONA_SOURCE = "01c502bb1f1ff8f2885d0cd490e043736083dca8"
TELEMETRY_OFF = {
    "LANGSMITH_TRACING": "false",
    "LANGCHAIN_TRACING_V2": "false",
    "LANGCHAIN_TRACING": "false",
    "LANGSMITH_OTEL_ENABLED": "false",
    "DAYTONA_OTEL_ENABLED": "false",
    "DAYTONA_EXPERIMENTAL_OTEL_ENABLED": "false",
    "OTEL_SDK_DISABLED": "true",
    "AIDER_ANALYTICS": "false",
    "DO_NOT_TRACK": "1",
}


def local_http_url(value: str, purpose: str = "工具") -> str:
    """Validate before sending any bytes; normalise localhost without DNS lookup."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or "\\" in value
        or any(ord(char) <= 32 for char in value)
    ):
        raise ValueError(
            f"{purpose}只允许本机回环 HTTP(S) 地址，不允许云端、局域网、凭据或查询参数"
        )
    host = "[::1]" if parsed.hostname == "::1" else "127.0.0.1"
    port = parsed.port  # Invalid/overflowing ports must also fail before a request.
    if port == 0:
        raise ValueError(f"{purpose}端口必须大于0")
    return urlunsplit((parsed.scheme, host + (f":{port}" if port else ""), parsed.path, "", ""))


def local_database_url(value: str) -> str:
    """For the control/checkpoint databases; reject driver query overrides too."""
    if not value:
        return value
    from sqlalchemy.engine import make_url

    parsed = make_url(value)
    if parsed.get_backend_name() == "sqlite":
        if parsed.host or parsed.query or (parsed.database or "").startswith(("//", "\\\\")):
            raise ValueError("SQLite必须是本机文件，不能使用网络共享或URI覆盖参数")
    elif parsed.get_backend_name() == "postgresql":
        if parsed.host not in {"127.0.0.1", "localhost", "::1"} or parsed.query:
            raise ValueError("PostgreSQL必须在本机；不接受service、hostaddr等连接覆盖参数")
        parsed = parsed.set(host="127.0.0.1" if parsed.host == "localhost" else parsed.host)
    else:
        raise ValueError("控制数据库只支持本机SQLite或PostgreSQL")
    return parsed.render_as_string(hide_password=False)


def disable_telemetry() -> None:
    """Do not let inherited development environment turn on hosted tracing."""
    os.environ.update(TELEMETRY_OFF)


def install_loopback_guard() -> None:
    """Dedicated child only: block non-loopback connections and external DNS.

    Daytona's local proxy uses <port>-<sandbox>.proxy.localhost. Resolve that
    exact suffix to loopback ourselves; never trust an external DNS answer.
    """
    disable_telemetry()
    original = socket.getaddrinfo

    def is_local(host):
        if isinstance(host, bytes):
            host = host.decode("ascii")
        if host == "localhost" or (isinstance(host, str) and host.endswith(".proxy.localhost")):
            return True
        if host == "proxy.localhost":
            return True
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError, TypeError:
            return False

    def resolve(host, *args, **kwargs):
        if not is_local(host):
            raise ValueError("Daytona本地客户端拒绝解析非本机地址")
        if isinstance(host, bytes):
            host = host.decode("ascii")
        if host == "localhost" or host == "proxy.localhost" or host.endswith(".proxy.localhost"):
            host = "127.0.0.1"
        return original(host, *args, **kwargs)

    def audit(event, args):
        if event == "socket.getaddrinfo" and not is_local(args[0]):
            raise ValueError("Daytona本地客户端拒绝外部DNS")
        if event in {"socket.connect", "socket.sendto"}:
            sock, address = args[0], args[-1]
            if sock.family in {socket.AF_INET, socket.AF_INET6}:
                if not isinstance(address, tuple) or not is_local(address[0]):
                    raise ValueError("Daytona本地客户端拒绝非回环网络连接")

    socket.getaddrinfo = resolve
    sys.addaudithook(audit)


def local_docker_command(argv):
    """Registered Docker tools cannot follow a saved cloud/remote Docker context."""
    from pathlib import Path

    if Path(argv[0]).stem.lower() != "docker":
        return argv
    if any(
        arg in {"--context", "-c", "--host", "-H"} or arg.startswith(("--context=", "--host="))
        for arg in argv[1:]
    ):
        raise ValueError("Docker工具不接受远程context/host覆盖")
    endpoint = (
        "npipe:////./pipe/docker_engine" if os.name == "nt" else "unix:///var/run/docker.sock"
    )
    return [argv[0], "--host", endpoint, *argv[1:]]
