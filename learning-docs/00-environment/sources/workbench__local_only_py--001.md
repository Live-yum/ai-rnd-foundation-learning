# workbench/local_only.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工具的本机运行边界。** 地址先校验再创建客户端；localhost规范成回环IP，数据库URL拒绝能覆盖主机的查询参数。Docker命令显式指定本机套接字，Daytona子进程同时限制DNS和连接目标。此处不限制用户明确配置的大模型服务。

**对应关系：** settings → tools/retrieval/daytona_worker；test_local_only验证拒绝路径。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `local_http_url`（L28–L48）：接收`value`、`purpose`。这是纯校验函数：输入字符串，输出规范化本机URL；不满足合同直接抛异常，不发起网络请求。 源码说明：Validate before sending any bytes; normalise localhost without DNS lookup.。 控制顺序：L31按`parsed.scheme not in {"http", "https"} or parsed.hostname not in {"127.0.0.1", "local…`分支；L41抛异常，停止当前正常路径；L46按`port == 0`分支；L47抛异常，停止当前正常路径。 调用`urlsplit`、`any`、`ord`、`ValueError`、`urlunsplit`。 返回路径：L48的`urlunsplit((parsed.scheme, host + (f":{port}" if port else ""), parsed.path, "", ""))`。
- `local_database_url`（L51–L67）：接收`value`。在数据库引擎建立前完成校验，避免驱动查询参数把看似本机的URL转到别处。 源码说明：For the control/checkpoint databases; reject driver query overrides too.。 控制顺序：L53按`not value`分支；L58按`parsed.get_backend_name() == "sqlite"`分支；L59按`parsed.host or parsed.query or (parsed.database or "").startswith(("//", "\\\\"))`分支；L60抛异常，停止当前正常路径；L61按`parsed.get_backend_name() == "postgresql"`分支；L62按`parsed.host not in {"127.0.0.1", "localhost", "::1"} or parsed.query`分支；L63抛异常，停止当前正常路径；L66抛异常，停止当前正常路径。 调用`make_url`、`parsed.get_backend_name`、`(parsed.database or "").startswith`、`ValueError`、`parsed.set`、`parsed.render_as_string`。 返回路径：L54的`value`；L67的`parsed.render_as_string(hide_password=False)`。
- `disable_telemetry`（L70–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Do not let inherited development environment turn on hosted tracing.。 调用`os.environ.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_loopback_guard`（L75–L115）：不接收显式业务参数，从已配置对象/模块读取依赖。先保存原DNS函数再包装它，并安装连接审计；只应在专用SDK进程执行，不能封住平台合法的大模型请求。 源码说明：Dedicated child only: block non-loopback connections and external DNS. Daytona's local proxy uses <port>-<sandbox>.proxy.localhost. Resolve that exact suffix to loopback ourselves; never trust an exte。 调用`disable_telemetry`、`sys.addaudithook`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_loopback_guard.is_local`（L84–L94）：接收`host`。 控制顺序：L85按`isinstance(host, bytes)`分支；L87按`host == "localhost" or (isinstance(host, str) and host.endswith(".proxy.localhost"))`分支；L89按`host == "proxy.localhost"`分支。 调用`isinstance`、`host.decode`、`host.endswith`、`ipaddress.ip_address`。 返回路径：L88的`True`；L90的`True`；L92的`ipaddress.ip_address(host).is_loopback`。
- `install_loopback_guard.resolve`（L96–L103）：接收`host`、`*args`、`**kwargs`。 控制顺序：L97按`not is_local(host)`分支；L98抛异常，停止当前正常路径；L99按`isinstance(host, bytes)`分支；L101按`host == "localhost" or host == "proxy.localhost" or host.endswith(".proxy.localhost")`分支。 调用`is_local`、`ValueError`、`isinstance`、`host.decode`、`host.endswith`、`original`。 返回路径：L103的`original(host, *args, **kwargs)`。
- `install_loopback_guard.audit`（L105–L112）：接收`event`、`args`。 控制顺序：L106按`event == "socket.getaddrinfo" and not is_local(args[0])`分支；L107抛异常，停止当前正常路径；L108按`event in {"socket.connect", "socket.sendto"}`分支；L110按`sock.family in {socket.AF_INET, socket.AF_INET6}`分支；L111按`not isinstance(address, tuple) or not is_local(address[0])`分支；L112抛异常，停止当前正常路径。 调用`is_local`、`ValueError`、`isinstance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `local_docker_command`（L118–L132）：接收`argv`。 源码说明：Registered Docker tools cannot follow a saved cloud/remote Docker context.。 控制顺序：L122按`Path(argv[0]).stem.lower() != "docker"`分支；L124按`any( arg in {"--context", "-c", "--host", "-H"} or arg.startswith(("--context=", "--h…`分支；L128抛异常，停止当前正常路径。 调用`Path(argv[0]).stem.lower`、`Path`、`any`、`arg.startswith`、`ValueError`。 返回路径：L123的`argv`；L132的`[argv[0], "--host", endpoint, *argv[1:]]`。

</details>

**创建路径：** `workbench/local_only.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L132。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/local_only.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "33aaf900346916934459fbacb3e926aae40b86c565d1b3e92e4d4179a86d3e95"} -->
````python
# workbench/local_only.py
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
````
