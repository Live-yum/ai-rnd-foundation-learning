# workbench/daytona_sessions.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：长时间沙箱检查的单次异步提交。** 建立独立会话并仅提交一次异步命令，按总期限用有界GET轮询，终止后读一次日志。传输层关闭透明重试，单请求最多30秒；提交响应丢失立即失败，不能用同步exec重放。

**对应关系：** sandbox非SQLite矩阵命令 → run_session_command → mode/session/command回执 → 可信运行报告与自有沙箱清理。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `harden_toolbox_transport`（L19–L59）：接收`client`。 源码说明：Configure the pinned SDK before its first toolbox request. Public session helpers omit timeouts for creation, status and logs. Bound their shared generated REST transport as well as the outer worker d。 调用`Retry`、`frozenset`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `harden_toolbox_transport.request`（L41–L57）：接收`method`、`url`、`*args`、`**kwargs`。 控制顺序：L45按`deadline is None and previous is not None`分支；L48按`deadline is not None`分支；L50按`remaining <= 0`分支；L51抛异常，停止当前正常路径；L52按`isinstance(previous, (int, float))`分支；L54按`isinstance(previous, tuple)`分支。 调用`kwargs.get`、`_DEADLINE.get`、`original`、`min`、`time.monotonic`、`TimeoutError`、`isinstance`。 返回路径：L46的`original(method, url, *args, **kwargs)`；L57的`original(method, url, *args, **kwargs)`。
- `run_session_command`（L62–L108）：接收`process`、`argv`、`cwd`、`timeout`、`evidence`、`poll_seconds`。 源码说明：Submit once, poll bounded GETs, then fetch logs once; never exec fallback. The caller owns the sandbox and deletes it in finally, including ambiguous submission failure. Session identifiers remain in 。 控制顺序：L90按`not isinstance(command_id, str) or not command_id`分支；L91抛异常，停止当前正常路径；L93在`True`成立时循环；L97按`command.exit_code is not None`分支；L98按`type(command.exit_code) is not int`分支；L99抛异常，停止当前正常路径；L103按`output is None`分支。 调用`time.monotonic`、`_DEADLINE.set`、`evidence.update`、`uuid.uuid4`、`check_deadline`、`process.create_session`、`process.execute_session_command`、`SessionExecuteRequest`、`shlex.quote`等。 返回路径：L105的`SimpleNamespace(exit_code=command.exit_code, result=output[:8000])`。
- `run_session_command.check_deadline`（L74–L76）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L75按`time.monotonic() >= deadline`分支；L76抛异常，停止当前正常路径。 调用`time.monotonic`、`TimeoutError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/daytona_sessions.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L108。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4316`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/daytona_sessions.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bcd30bbddd2a08009368e23f7d18b710dbebba9de89cad015341df560c95f27f"} -->
````python
# workbench/daytona_sessions.py
"""Bounded, single-submission commands for pinned local Daytona 0.190.0.

A synchronous exec POST can outlive the loopback gateway's idle budget. Never
retry that mutation: a lost response does not prove that execution never began.
"""

import shlex
import time
import uuid
from contextvars import ContextVar
from types import SimpleNamespace

from urllib3.util.retry import Retry

_DEADLINE = ContextVar("daytona_command_deadline", default=None)
REQUEST_SECONDS = 30.0


def harden_toolbox_transport(client):
    """Configure the pinned SDK before its first toolbox request.

    Public session helpers omit timeouts for creation, status and logs. Bound
    their shared generated REST transport as well as the outer worker deadline.
    No HTTP operation is transparently retried, especially mutating POSTs.
    """
    rest = client._toolbox_api_client.rest_client
    manager = rest.pool_manager
    retries = Retry(
        total=0,
        connect=0,
        read=0,
        redirect=0,
        status=0,
        other=0,
        allowed_methods=frozenset({"GET", "HEAD"}),
        raise_on_status=False,
    )
    manager.connection_pool_kw["retries"] = retries
    original = rest.request

    def request(method, url, *args, **kwargs):
        previous = kwargs.get("_request_timeout")
        deadline = _DEADLINE.get()
        # Preserve explicit existing short-exec/upload budgets outside sessions.
        if deadline is None and previous is not None:
            return original(method, url, *args, **kwargs)
        remaining = REQUEST_SECONDS
        if deadline is not None:
            remaining = min(remaining, deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Daytona session command deadline exceeded")
        if isinstance(previous, (int, float)):
            remaining = min(remaining, previous)
        elif isinstance(previous, tuple):
            remaining = min([remaining, *(value for value in previous if value is not None)])
        kwargs["_request_timeout"] = remaining
        return original(method, url, *args, **kwargs)

    rest.request = request


def run_session_command(process, argv, cwd, timeout, evidence, *, poll_seconds=1.0):
    """Submit once, poll bounded GETs, then fetch logs once; never exec fallback.

    The caller owns the sandbox and deletes it in finally, including ambiguous
    submission failure. Session identifiers remain in the failure receipt.
    """
    from daytona import SessionExecuteRequest

    deadline = time.monotonic() + timeout
    token = _DEADLINE.set(deadline)
    evidence.update(mode="async-session", session_id="rnd-check-" + uuid.uuid4().hex)

    def check_deadline():
        if time.monotonic() >= deadline:
            raise TimeoutError("Daytona session command deadline exceeded")

    try:
        check_deadline()
        process.create_session(evidence["session_id"])
        check_deadline()
        response = process.execute_session_command(
            evidence["session_id"],
            SessionExecuteRequest(
                command="cd " + shlex.quote(cwd) + " && " + shlex.join(argv), run_async=True
            ),
            timeout=min(REQUEST_SECONDS, max(0.001, deadline - time.monotonic())),
        )
        command_id = response.cmd_id
        if not isinstance(command_id, str) or not command_id:
            raise ValueError("Daytona async submission returned no command ID")
        evidence["command_id"] = command_id
        while True:
            check_deadline()
            command = process.get_session_command(evidence["session_id"], command_id)
            check_deadline()
            if command.exit_code is not None:
                if type(command.exit_code) is not int:
                    raise ValueError("Daytona command returned invalid exit code")
                logs = process.get_session_command_logs(evidence["session_id"], command_id)
                check_deadline()
                output = logs.output
                if output is None:
                    output = (logs.stdout or "")[:8000] + (logs.stderr or "")[:8000]
                return SimpleNamespace(exit_code=command.exit_code, result=output[:8000])
            time.sleep(min(poll_seconds, max(0, deadline - time.monotonic())))
    finally:
        _DEADLINE.reset(token)
````
