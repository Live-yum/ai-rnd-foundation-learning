# tests/test_daytona_sessions.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.daytona_sessions`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Process`（L11–L37）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Process.__init__`（L12–L15）：接收`statuses`、`failure`。 调用`iter`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Process.create_session`（L17–L18）：接收`session`。 调用`self.calls.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Process.execute_session_command`（L20–L26）：接收`session`、`request`、`**kwargs`。 控制顺序：L22断言`request.run_async is True`；L23断言`request.command == "cd '/tmp/a b' && python 'a;b.py'"`；L24按`self.failure`分支；L25抛异常，停止当前正常路径。 调用`self.calls.append`、`SimpleNamespace`。 返回路径：L26的`SimpleNamespace(cmd_id="cmd-1")`。
- `Process.get_session_command`（L28–L30）：接收`*args`。 调用`self.calls.append`、`SimpleNamespace`、`next`。 返回路径：L30的`SimpleNamespace(exit_code=next(self.statuses))`。
- `Process.get_session_command_logs`（L32–L34）：接收`*args`。 调用`self.calls.append`、`SimpleNamespace`。 返回路径：L34的`SimpleNamespace(output="actual command output")`。
- `Process.exec`（L36–L37）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_single_submission_polls_to_completion_and_records_identity`（L40–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L46断言`result.exit_code == 0`；L47断言`result.result == "actual command output"`；L48断言`process.calls == ["create", "submit", "poll", "poll", "poll", "logs"]`；L49断言`evidence["mode"] == "async-session"`；L50断言`evidence["session_id"].startswith("rnd-check-")`；L51断言`evidence["command_id"] == "cmd-1"`。 调用`Process`、`run_session_command`、`evidence["session_id"].startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lost_submission_never_falls_back_or_submits_twice`（L54–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L59断言`process.calls == ["create", "submit"]`；L60断言`evidence["session_id"]`；L61断言`"command_id" not in evidence`。 调用`Process`、`ConnectionError`、`pytest.raises`、`run_session_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_timeout_has_no_resubmission_or_log_fetch`（L64–L73）：接收`monkeypatch`。 控制顺序：L72断言`process.calls == ["create", "submit"]`；L73断言`daytona_sessions._DEADLINE.get() is None`。 调用`iter`、`monkeypatch.setattr`、`next`、`Process`、`pytest.raises`、`run_session_command`、`daytona_sessions._DEADLINE.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonzero_command_is_returned_without_retry`（L76–L79）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78断言`run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {}).exit_code == 9`；L79断言`process.calls == ["create", "submit", "poll", "logs"]`。 调用`Process`、`run_session_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_pinned_transport_does_not_replay_lost_post`（L82–L120）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L114断言`calls == ["server-executed"]`；L115断言`api.rest_client.pool_manager.connection_pool_kw["retries"].total == 0`。 调用`ThreadingHTTPServer`、`threading.Thread`、`worker.start`、`Configuration`、`RemoteDisconnectedRetry`、`ApiClient`、`SimpleNamespace`、`harden_toolbox_transport`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_pinned_transport_does_not_replay_lost_post.Handler`（L88–L96）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_pinned_transport_does_not_replay_lost_post.Handler.do_POST`（L89–L93）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.rfile.read`、`int`、`self.headers.get`、`calls.append`、`self.connection.shutdown`、`self.connection.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_pinned_transport_does_not_replay_lost_post.Handler.log_message`（L95–L96）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_timeouts_bounded_and_session_deadline_applies`（L123–L142）：接收`monkeypatch`。 控制顺序：L142断言`seen == [30, 120, 5, 5, 5]`。 调用`SimpleNamespace`、`seen.append`、`harden_toolbox_transport`、`rest.request`、`daytona_sessions._DEADLINE.set`、`monkeypatch.setattr`、`daytona_sessions._DEADLINE.reset`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_command_can_run_beyond_gateway_idle_budget_with_short_polls`（L145–L161）：接收`monkeypatch`。 控制顺序：L157断言`clock[0] == 400`；L158断言`result.exit_code == 0`；L159断言`process.calls.count("submit") == 1`；L160断言`process.calls.count("poll") == 5`；L161断言`process.calls.count("logs") == 1`。 调用`monkeypatch.setattr`、`clock.__setitem__`、`Process`、`run_session_command`、`process.calls.count`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_split_logs_are_preserved_and_bounded`（L164–L172）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L170断言`result.exit_code == 1`；L171断言`result.result.startswith("first\nerror")`；L172断言`len(result.result) == 8000`。 调用`Process`、`SimpleNamespace`、`run_session_command`、`result.result.startswith`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_sessions.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L172。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6390`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_sessions.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5d65c89f2c1c55b1c524c5fccbc1278d42fc2dc58d96d25bd1f1052ad7cd6bbd"} -->
````python
# tests/test_daytona_sessions.py
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

from workbench.daytona_sessions import harden_toolbox_transport, run_session_command


class Process:
    def __init__(self, statuses=(None, None, 0), failure=None):
        self.statuses = iter(statuses)
        self.calls = []
        self.failure = failure

    def create_session(self, session):
        self.calls.append("create")

    def execute_session_command(self, session, request, **kwargs):
        self.calls.append("submit")
        assert request.run_async is True
        assert request.command == "cd '/tmp/a b' && python 'a;b.py'"
        if self.failure:
            raise self.failure
        return SimpleNamespace(cmd_id="cmd-1")

    def get_session_command(self, *args):
        self.calls.append("poll")
        return SimpleNamespace(exit_code=next(self.statuses))

    def get_session_command_logs(self, *args):
        self.calls.append("logs")
        return SimpleNamespace(output="actual command output")

    def exec(self, *args, **kwargs):
        pytest.fail("Synchronous fallback would repeat the mutation")


def test_single_submission_polls_to_completion_and_records_identity():
    process = Process()
    evidence = {}
    result = run_session_command(
        process, ["python", "a;b.py"], "/tmp/a b", 10, evidence, poll_seconds=0
    )
    assert result.exit_code == 0
    assert result.result == "actual command output"
    assert process.calls == ["create", "submit", "poll", "poll", "poll", "logs"]
    assert evidence["mode"] == "async-session"
    assert evidence["session_id"].startswith("rnd-check-")
    assert evidence["command_id"] == "cmd-1"


def test_lost_submission_never_falls_back_or_submits_twice():
    process = Process(failure=ConnectionError("response lost after server execution"))
    evidence = {}
    with pytest.raises(ConnectionError):
        run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, evidence)
    assert process.calls == ["create", "submit"]
    assert evidence["session_id"]
    assert "command_id" not in evidence


def test_timeout_has_no_resubmission_or_log_fetch(monkeypatch):
    from workbench import daytona_sessions

    ticks = iter([0, 0, 0, 0, 11])
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: next(ticks))
    process = Process()
    with pytest.raises(TimeoutError):
        run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {})
    assert process.calls == ["create", "submit"]
    assert daytona_sessions._DEADLINE.get() is None


def test_nonzero_command_is_returned_without_retry():
    process = Process(statuses=[9])
    assert run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {}).exit_code == 9
    assert process.calls == ["create", "submit", "poll", "logs"]


def test_real_pinned_transport_does_not_replay_lost_post():
    from daytona.internal.urllib3_retry import RemoteDisconnectedRetry
    from daytona_toolbox_api_client import ApiClient, Configuration

    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            calls.append("server-executed")
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    config = Configuration()
    config.retries = RemoteDisconnectedRetry(total=3)
    api = ApiClient(config)
    client = SimpleNamespace(_toolbox_api_client=api)
    harden_toolbox_transport(client)
    try:
        with pytest.raises(Exception):
            api.rest_client.request(
                "POST",
                f"http://127.0.0.1:{server.server_port}/execute",
                headers={"Content-Type": "application/json"},
                body={},
            )
        assert calls == ["server-executed"]
        assert api.rest_client.pool_manager.connection_pool_kw["retries"].total == 0
    finally:
        api.rest_client.pool_manager.clear()
        server.shutdown()
        server.server_close()
        worker.join()


def test_missing_timeouts_bounded_and_session_deadline_applies(monkeypatch):
    from workbench import daytona_sessions

    seen = []
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda *args, **kwargs: seen.append(kwargs["_request_timeout"]),
    )
    harden_toolbox_transport(SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest)))
    rest.request("GET", "local")
    rest.request("POST", "local", _request_timeout=120)
    token = daytona_sessions._DEADLINE.set(105)
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: 100)
    try:
        rest.request("GET", "local")
        rest.request("POST", "local", _request_timeout=20)
        rest.request("GET", "local", _request_timeout=(None, None))
    finally:
        daytona_sessions._DEADLINE.reset(token)
    assert seen == [30, 120, 5, 5, 5]


def test_command_can_run_beyond_gateway_idle_budget_with_short_polls(monkeypatch):
    from workbench import daytona_sessions

    clock = [0.0]
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        daytona_sessions.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    process = Process(statuses=[None, None, None, None, 0])
    result = run_session_command(
        process, ["python", "a;b.py"], "/tmp/a b", 1000, {}, poll_seconds=100
    )
    assert clock[0] == 400
    assert result.exit_code == 0
    assert process.calls.count("submit") == 1
    assert process.calls.count("poll") == 5
    assert process.calls.count("logs") == 1


def test_split_logs_are_preserved_and_bounded():
    process = Process(statuses=[1])
    process.get_session_command_logs = lambda *args: SimpleNamespace(
        output=None, stdout="first\n", stderr="error" + "x" * 9000
    )
    result = run_session_command(process, ["python", "a;b.py"], "/tmp/a b", 10, {})
    assert result.exit_code == 1
    assert result.result.startswith("first\nerror")
    assert len(result.result) == 8000
````
