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
