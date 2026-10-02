# tests/test_native_backend_lifecycle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `free_port`（L15–L18）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`listener.bind`、`listener.getsockname`。 返回路径：L18的`listener.getsockname()[1]`。
- `test_occupied_native_port_never_starts_or_contacts_foreign_server`（L21–L39）：接收`tmp_path`、`monkeypatch`。 控制顺序：L39断言`listener.fileno() >= 0`。 调用`socket.socket`、`listener.bind`、`listener.listen`、`listener.getsockname`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.running_backend`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group`（L48–L124）：接收`tmp_path`、`monkeypatch`、`descendant`、`raise_inside`。 控制顺序：L107遍历`range(2)`；L113断言`url == f"http://127.0.0.1:{port}" and path == "/openapi.json"`；L114断言`native.backend_port_state(port, processes[-1].pid)["owned_listener"]`；L115按`raise_inside`分支；L116抛异常，停止当前正常路径；L118断言`raise_inside`；L120断言`lifecycle["port"] == port and lifecycle["port_released"] is True`；L121断言`lifecycle["port_state_before_cleanup"]["owned_listener"] is True`。后续分支沿下方源码相同行号继续阅读。 调用`free_port`、`server.write_text`、`owner.write_text`、`monkeypatch.setattr`、`range`、`str`、`native.running_backend`、`native.backend_port_state`、`LookupError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.start`（L76–L84）：接收`command`、`**kwargs`。 调用`str`、`original_popen`、`processes.append`。 返回路径：L84的`process`。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.OwnershipCheckedClient`（L89–L104）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.OwnershipCheckedClient.__init__`（L90–L91）：接收`**kwargs`。 调用`original_client`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.OwnershipCheckedClient.__enter__`（L93–L94）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L94的`self`。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.OwnershipCheckedClient.__exit__`（L96–L97）：接收`*args`。 调用`self.client.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delayed_native_listener_restarts_on_same_port_and_cleans_owned_group.OwnershipCheckedClient.get`（L99–L104）：接收`url`。 控制顺序：L103断言`state["observable"] and state["owned_listener"]`。 调用`native.backend_port_state`、`self.client.get`。 返回路径：L104的`self.client.get(url)`。
- `test_exited_launcher_cannot_leave_its_owned_listener_behind`（L131–L154）：接收`tmp_path`、`monkeypatch`。 控制顺序：L152断言`result["port_state_before_cleanup"]["owned_group_pids"]`；L153断言`result["port_released"] is True`；L154断言`native.loopback_port_bindable(port)`。 调用`free_port`、`monkeypatch.setattr`、`pytest.raises`、`native.running_backend`、`str`、`pytest.fail`、`json.loads`、`(tmp_path / "report/backend-lifecycle.json").read_text`、`native.loopback_port_bindable`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exited_launcher_cannot_leave_its_owned_listener_behind.start`（L140–L143）：接收`command`、`**kwargs`。 调用`original`、`str`、`processes.append`。 返回路径：L143的`process`。

</details>

**创建路径：** `tests/test_native_backend_lifecycle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L154。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5966`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_backend_lifecycle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "af187431b1f66df396b6f552adf9fc1153bd0c148692caecfeb5de1738936422"} -->
````python
# tests/test_native_backend_lifecycle.py
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
````
