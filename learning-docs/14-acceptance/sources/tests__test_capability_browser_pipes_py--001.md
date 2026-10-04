# tests/test_capability_browser_pipes.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `no_pipe_selectors`（L22–L33）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fixture`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `no_pipe_selectors.unavailable`（L25–L26）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `no_pipe_selectors.no_threads`（L30–L31）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `child_processes`（L37–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L51遍历`processes`；L52按`process.poll() is None`分支；L55遍历`(process.stdin, process.stdout, process.stderr)`；L56按`stream is not None`分支；L58断言`not set(threading.enumerate()) - before`。 调用`set`、`threading.enumerate`、`process.poll`、`process.kill`、`process.wait`、`stream.close`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `child_processes.launch`（L42–L48）：接收`script`、`**kwargs`。 调用`real_popen`、`processes.append`。 返回路径：L48的`process`。
- `read_all`（L61–L65）：接收`stream`、`deadline`。 控制顺序：L63在`chunk := isolation._read_pipe(stream, deadline, "test pipe deadli…`成立时循环。 调用`bytearray`、`isolation._read_pipe`、`output.extend`、`bytes`。 返回路径：L65的`bytes(output)`。
- `test_real_pipe_transfers_large_binary_payload_and_eof`（L68–L82）：接收`child_processes`。 控制顺序：L81断言`read_all(process.stdout, deadline) == hashlib.sha256(body).digest()`；L82断言`process.wait(timeout=5) == 0`。 调用`bytes`、`range`、`launch`、`time.monotonic`、`isolation._write_pipe`、`process.stdin.close`、`read_all`、`hashlib.sha256(body).digest`、`hashlib.sha256`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_unresponsive_pipe_honors_deadline`（L86–L102）：接收`child_processes`、`direction`。 控制顺序：L97按`direction == "write"`分支；L101断言`time.monotonic() - started < 2`；L102断言`process.poll() is None`。 调用`launch`、`time.monotonic`、`pytest.raises`、`isolation._write_pipe`、`isolation._read_pipe`、`process.poll`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_closed_read_end_is_broken_pipe_not_timeout`（L105–L113）：接收`child_processes`。 控制顺序：L110断言`process.wait(timeout=5) == 0`；L113断言`isolation._read_pipe(process.stdout, time.monotonic() + 5, "deadline") == b""`。 调用`launch`、`process.wait`、`pytest.raises`、`isolation._write_pipe`、`time.monotonic`、`isolation._read_pipe`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `simulated_pipes`（L117–L151）：接收`monkeypatch`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`state.modes.append`。 返回路径：L151的`state, SimpleNamespace(fileno=lambda: 17)`。
- `simulated_pipes.sleep`（L120–L123）：接收`seconds`。 控制顺序：L121断言`0 < seconds <= isolation.PIPE_POLL_INTERVAL`。 调用`state.sleeps.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `simulated_pipes.operation`（L125–L129）：接收`events`。 控制顺序：L127按`isinstance(event, Exception)`分支；L128抛异常，停止当前正常路径。 调用`events.pop`、`isinstance`。 返回路径：L129的`event`。
- `simulated_pipes.read`（L131–L133）：接收`fd`、`size`。 控制顺序：L132断言`fd == 17 and size == isolation.PIPE_CHUNK`。 调用`operation`。 返回路径：L133的`operation(state.reads)`。
- `simulated_pipes.write`（L135–L138）：接收`fd`、`data`。 控制顺序：L136断言`fd == 17 and 0 < len(data) <= isolation.PIPE_CHUNK`。 调用`len`、`state.attempts.append`、`bytes`、`operation`。 返回路径：L138的`operation(state.writes)`。
- `test_simulated_windows_partial_zero_and_full_pipe_writes`（L154–L160）：接收`simulated_pipes`。 控制顺序：L158断言`state.modes == [(17, False)]`；L159断言`state.attempts == [b"abcdef", b"cdef", b"cdef", b"cdef", b"def"]`；L160断言`len(state.sleeps) == 2`。 调用`BlockingIOError`、`isolation._write_pipe`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_simulated_windows_empty_pipe_is_not_eof`（L163–L169）：接收`simulated_pipes`。 控制顺序：L166断言`isolation._read_pipe(stream, 101, "deadline") == b"partial"`；L167断言`isolation._read_pipe(stream, 101, "deadline") == b""`；L168断言`state.modes == [(17, False), (17, False)]`；L169断言`len(state.sleeps) == 1`。 调用`BlockingIOError`、`isolation._read_pipe`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_simulated_blocked_pipe_never_extends_absolute_deadline`（L173–L184）：接收`simulated_pipes`、`direction`。 控制顺序：L179按`direction == "read"`分支；L183断言`state.now == deadline`；L184断言`sum(state.sleeps) == pytest.approx(0.025)`。 调用`BlockingIOError`、`pytest.raises`、`isolation._read_pipe`、`isolation._write_pipe`、`sum`、`pytest.approx`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_simulated_expired_deadline_does_not_attempt_io`（L188–L195）：接收`simulated_pipes`、`direction`。 控制顺序：L191按`direction == "read"`分支；L195断言`state.attempts == state.sleeps == []`。 调用`pytest.raises`、`isolation._read_pipe`、`isolation._write_pipe`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_simulated_real_pipe_errors_propagate`（L200–L210）：接收`simulated_pipes`、`direction`、`code`。 控制顺序：L205按`direction == "read"`分支；L209断言`raised.value is error`；L210断言`not state.sleeps`。 调用`OSError`、`pytest.raises`、`isolation._read_pipe`、`isolation._write_pipe`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `setup_worker`（L213–L225）：接收`monkeypatch`、`child_processes`、`script`。 调用`monkeypatch.setattr`、`launch`。 返回路径：L225的`calls, processes`。
- `setup_worker.run`（L217–L219）：接收`args`、`**kwargs`。 调用`calls.append`、`SimpleNamespace`。 返回路径：L219的`SimpleNamespace(returncode=0, stdout=b"[{}]")`。
- `assert_worker_cleaned`（L228–L236）：接收`calls`、`processes`。 控制顺序：L229断言`len(processes) == 1`；L230断言`processes[0].poll() is not None`；L231断言`processes[0].stdin.closed and processes[0].stdout.closed`；L234断言`len(creates) == len(removes) == 1`；L236断言`removes[0] == [*isolation.DOCKER, "rm", "-f", name]`。 调用`len`、`processes[0].poll`、`creates[0].index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_success_with_large_bidirectional_frames`（L239–L275）：接收`monkeypatch`、`child_processes`。 控制顺序：L271断言`status == 0`；L272断言`json.loads(report) == {"digest": hashlib.sha256(bytes(range(256)) * 8192).hexdigest()…`；L273断言`len(relayed) == 1`；L274断言`all("controller-only-token" not in str(args) for args in calls)`。 调用`setup_worker`、`monkeypatch.setattr`、`isolation.execute_worker`、`json.loads`、`hashlib.sha256(bytes(range(256)) * 8192).hexdigest`、`hashlib.sha256`、`bytes`、`range`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_success_with_large_bidirectional_frames.relay`（L261–L265）：接收`client`、`frame`、`deadline`。本机入口只按固定端口选择内部服务，逐字节转发并保留半关闭语义；不解析用户传入URL、目标地址或模型密钥，超时与退出时关闭两侧连接。 控制顺序：L262断言`client.headers["x-daytona-preview-token"] == "controller-only-token"`；L263断言`deadline > time.monotonic()`。 调用`time.monotonic`、`relayed.append`。 返回路径：L265的`{"type": "response", "id": 1, "body": frame["body"]}, 4 * 1024 * 1024`。
- `test_real_worker_pipe_failures_cleanup`（L298–L305）：接收`monkeypatch`、`child_processes`、`mode`、`script`、`error`、`message`。 调用`setup_worker`、`pytest.raises`、`isolation.execute_worker`、`assert_worker_cleaned`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_provenance_pipe_bounds_and_cleanup`（L309–L340）：接收`monkeypatch`、`child_processes`、`mode`。 控制顺序：L320按`mode == "timeout"`分支；L329按`mode == "success"`分支；L330断言`isolation._image_file_archive(NAME, "/source") == bytes(range(256)) * 1000`；L339断言`len(processes) == 1`；L340断言`processes[0].poll() is not None and processes[0].stdout.closed`。 调用`monkeypatch.setattr`、`launch`、`isolation._image_file_archive`、`bytes`、`range`、`pytest.raises`、`len`、`processes[0].poll`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_provenance_pipe_bounds_and_cleanup.read`（L324–L326）：接收`stream`、`deadline`、`message`。 调用`deadlines.append`、`real_read`、`min`、`time.monotonic`。 返回路径：L326的`real_read(stream, min(deadline, time.monotonic() + 0.1), message)`。
- `test_read_and_write_requests_are_chunk_bounded`（L343–L349）：接收`simulated_pipes`。 控制顺序：L348断言`b"".join(state.attempts) == body`；L349断言`max(map(len, state.attempts)) == isolation.PIPE_CHUNK`。 调用`isolation._write_pipe`、`b"".join`、`max`、`map`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_progress_does_not_reset_or_overrun_absolute_deadline`（L353–L374）：接收`monkeypatch`、`simulated_pipes`、`direction`。 控制顺序：L370按`direction == "read"`分支；L374断言`state.sleeps == []`。 调用`monkeypatch.setattr`、`pytest.raises`、`isolation._read_pipe`、`isolation._write_pipe`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_progress_does_not_reset_or_overrun_absolute_deadline.slow_read`（L359–L361）：接收`fd`、`size`。 返回路径：L361的`b"arrived too late"`。
- `test_progress_does_not_reset_or_overrun_absolute_deadline.slow_write`（L363–L365）：接收`fd`、`data`。 调用`len`。 返回路径：L365的`len(data)`。
- `test_real_blocked_reply_uses_original_deadline_and_cleans_up`（L377–L397）：接收`monkeypatch`、`child_processes`。 控制顺序：L396断言`len(deadlines) == 2 and deadlines[0] == deadlines[1]`。 调用`setup_worker`、`monkeypatch.setattr`、`pytest.raises`、`isolation.execute_worker`、`len`、`assert_worker_cleaned`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_blocked_reply_uses_original_deadline_and_cleans_up.write`（L389–L391）：接收`stream`、`data`、`deadline`。 调用`deadlines.append`、`real_write`。 返回路径：L391的`real_write(stream, data, deadline)`。
- `test_final_process_wait_never_adds_minimum_grace`（L401–L436）：接收`monkeypatch`、`operation`。 控制顺序：L427按`operation == "worker"`分支；L428断言`isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE) == ( …`；L432断言`state.closed == ["stdin", "stdout"]`；L434断言`isolation._image_file_archive(NAME, "/source") == b""`；L435断言`state.closed == ["stdout"]`；L436断言`state.waits == pytest.approx([0.025, 5])`。 调用`SimpleNamespace`、`state.closed.append`、`state.waits.append`、`monkeypatch.setattr`、`isolation.execute_worker`、`isolation._image_file_archive`、`pytest.approx`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_final_process_wait_never_adds_minimum_grace.read`（L422–L424）：接收`stream`、`deadline`、`message`。 调用`frames.pop`。 返回路径：L424的`frames.pop(0) if operation == "worker" else b""`。
- `test_real_eof_before_exit_still_times_out_and_cleans_up`（L439–L448）：接收`monkeypatch`、`child_processes`。 调用`setup_worker`、`pytest.raises`、`isolation.execute_worker`、`assert_worker_cleaned`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_pipes.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L448。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17119`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_pipes.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b6befcfbdedd2fc2dcc8c70cf8701bab35faf03606713406878792e67b4bdcff"} -->
````python
# tests/test_capability_browser_pipes.py
"""Portable real pipes and simulated Windows backpressure; no Docker certification."""

import errno
import hashlib
import json
import selectors
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

import pytest

from workbench import capability_browser_isolation as isolation

IMAGE = "sha256:" + "a" * 64
NAME = "rnd-browser-" + "b" * 32


@pytest.fixture(autouse=True)
def no_pipe_selectors(monkeypatch):
    # Windows select accepts sockets only. Exercise every path with selectors
    # forbidden, including success: converting WinError to a failure cannot pass.
    def unavailable(*args, **kwargs):
        pytest.fail("Anonymous pipes must not use Windows socket-only selectors")

    monkeypatch.setattr(selectors, "DefaultSelector", unavailable)

    def no_threads(*args, **kwargs):
        pytest.fail("Bounded pipe I/O must not create uncancellable helper threads")

    monkeypatch.setattr(threading.Thread, "start", no_threads)


@pytest.fixture
def child_processes():
    before = set(threading.enumerate())
    processes = []
    real_popen = subprocess.Popen

    def launch(script, **kwargs):
        process = real_popen(
            [sys.executable, "-I", "-S", "-c", script],
            **kwargs,
        )
        processes.append(process)
        return process

    yield launch, processes
    for process in processes:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()
    assert not set(threading.enumerate()) - before


def read_all(stream, deadline):
    output = bytearray()
    while chunk := isolation._read_pipe(stream, deadline, "test pipe deadline"):
        output.extend(chunk)
    return bytes(output)


def test_real_pipe_transfers_large_binary_payload_and_eof(child_processes):
    launch, _ = child_processes
    body = bytes(range(256)) * 8192
    process = launch(
        "import hashlib,sys; data=sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(hashlib.sha256(data).digest()); sys.stdout.flush()",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    isolation._write_pipe(process.stdin, body, deadline)
    process.stdin.close()
    assert read_all(process.stdout, deadline) == hashlib.sha256(body).digest()
    assert process.wait(timeout=5) == 0


@pytest.mark.parametrize("direction", ["read", "write"])
def test_real_unresponsive_pipe_honors_deadline(child_processes, direction):
    launch, _ = child_processes
    process = launch(
        "import time; time.sleep(30)",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    started = time.monotonic()
    deadline = started + 0.15
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "write":
            isolation._write_pipe(process.stdin, b"x" * 2_000_000, deadline)
        else:
            isolation._read_pipe(process.stdout, deadline, "test read deadline")
    assert time.monotonic() - started < 2
    assert process.poll() is None


def test_real_closed_read_end_is_broken_pipe_not_timeout(child_processes):
    launch, _ = child_processes
    process = launch(
        "pass", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    assert process.wait(timeout=5) == 0
    with pytest.raises(BrokenPipeError):
        isolation._write_pipe(process.stdin, b"not delivered", time.monotonic() + 5)
    assert isolation._read_pipe(process.stdout, time.monotonic() + 5, "deadline") == b""


@pytest.fixture
def simulated_pipes(monkeypatch):
    state = SimpleNamespace(now=100.0, sleeps=[], modes=[], reads=[], writes=[])

    def sleep(seconds):
        assert 0 < seconds <= isolation.PIPE_POLL_INTERVAL
        state.sleeps.append(seconds)
        state.now += seconds

    def operation(events):
        event = events.pop(0)
        if isinstance(event, Exception):
            raise event
        return event

    def read(fd, size):
        assert fd == 17 and size == isolation.PIPE_CHUNK
        return operation(state.reads)

    def write(fd, data):
        assert fd == 17 and 0 < len(data) <= isolation.PIPE_CHUNK
        state.attempts.append(bytes(data))
        return operation(state.writes)

    state.attempts = []
    monkeypatch.setattr(
        isolation, "time", SimpleNamespace(monotonic=lambda: state.now, sleep=sleep)
    )
    monkeypatch.setattr(
        isolation,
        "os",
        SimpleNamespace(
            set_blocking=lambda fd, flag: state.modes.append((fd, flag)), read=read, write=write
        ),
    )
    return state, SimpleNamespace(fileno=lambda: 17)


def test_simulated_windows_partial_zero_and_full_pipe_writes(simulated_pipes):
    state, stream = simulated_pipes
    state.writes = [2, 0, BlockingIOError(errno.EAGAIN, "full pipe"), 1, 3]
    isolation._write_pipe(stream, b"abcdef", 101)
    assert state.modes == [(17, False)]
    assert state.attempts == [b"abcdef", b"cdef", b"cdef", b"cdef", b"def"]
    assert len(state.sleeps) == 2


def test_simulated_windows_empty_pipe_is_not_eof(simulated_pipes):
    state, stream = simulated_pipes
    state.reads = [BlockingIOError(errno.EAGAIN, "empty pipe"), b"partial", b""]
    assert isolation._read_pipe(stream, 101, "deadline") == b"partial"
    assert isolation._read_pipe(stream, 101, "deadline") == b""
    assert state.modes == [(17, False), (17, False)]
    assert len(state.sleeps) == 1


@pytest.mark.parametrize("direction", ["read", "write", "zero-write"])
def test_simulated_blocked_pipe_never_extends_absolute_deadline(simulated_pipes, direction):
    state, stream = simulated_pipes
    state.reads = [BlockingIOError(errno.EAGAIN, "empty")] * 40
    state.writes = [0 if direction == "zero-write" else BlockingIOError(errno.EAGAIN, "full")] * 40
    deadline = state.now + 0.025
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, deadline, "deadline")
        else:
            isolation._write_pipe(stream, b"x", deadline)
    assert state.now == deadline
    assert sum(state.sleeps) == pytest.approx(0.025)


@pytest.mark.parametrize("direction", ["read", "write"])
def test_simulated_expired_deadline_does_not_attempt_io(simulated_pipes, direction):
    state, stream = simulated_pipes
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, state.now, "deadline")
        else:
            isolation._write_pipe(stream, b"x", state.now)
    assert state.attempts == state.sleeps == []


@pytest.mark.parametrize("direction", ["read", "write"])
@pytest.mark.parametrize("code", [errno.EBADF, errno.EIO, errno.EPIPE])
def test_simulated_real_pipe_errors_propagate(simulated_pipes, direction, code):
    state, stream = simulated_pipes
    error = OSError(code, "genuine pipe failure")
    state.reads = state.writes = [error]
    with pytest.raises(OSError) as raised:
        if direction == "read":
            isolation._read_pipe(stream, 101, "deadline")
        else:
            isolation._write_pipe(stream, b"x", 101)
    assert raised.value is error
    assert not state.sleeps


def setup_worker(monkeypatch, child_processes, script):
    launch, processes = child_processes
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout=b"[{}]")

    monkeypatch.setattr(isolation.subprocess, "run", run)
    monkeypatch.setattr(isolation.subprocess, "Popen", lambda args, **kw: launch(script, **kw))
    monkeypatch.setattr(isolation, "require_worker_inspection", lambda *args: {})
    monkeypatch.setattr(isolation, "require_image_sources", lambda *args: {})
    return calls, processes


def assert_worker_cleaned(calls, processes):
    assert len(processes) == 1
    assert processes[0].poll() is not None
    assert processes[0].stdin.closed and processes[0].stdout.closed
    creates = [args for args in calls if "create" in args]
    removes = [args for args in calls if "rm" in args]
    assert len(creates) == len(removes) == 1
    name = creates[0][creates[0].index("--name") + 1]
    assert removes[0] == [*isolation.DOCKER, "rm", "-f", name]


def test_real_worker_success_with_large_bidirectional_frames(monkeypatch, child_processes):
    script = """
import base64, hashlib, json, sys
request = json.loads(sys.stdin.buffer.readline())
assert request['token'] == ''
assert request['url'] == 'http://127.0.0.1:18080'
assert len(request['padding']) == 800000
body = bytes(range(256)) * 8192
frame = {'type':'request', 'id':1, 'method':'POST', 'path':'/large',
         'headers':{}, 'body':base64.b64encode(body).decode()}
sys.stdout.write(json.dumps(frame) + '\\n')
sys.stdout.flush()
response = json.loads(sys.stdin.buffer.readline())
assert response['id'] == 1
assert base64.b64decode(response['body']) == body
report = {'digest':hashlib.sha256(body).hexdigest()}
sys.stdout.write(json.dumps({'type':'report', 'report':report, 'exit_code':0}) + '\\n')
sys.stdout.flush()
"""
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    relayed = []

    def relay(client, frame, *, deadline):
        assert client.headers["x-daytona-preview-token"] == "controller-only-token"
        assert deadline > time.monotonic()
        relayed.append(frame)
        return {"type": "response", "id": 1, "body": frame["body"]}, 4 * 1024 * 1024

    monkeypatch.setattr(isolation, "relay_request", relay)
    report, status = isolation.execute_worker(
        {"padding": "x" * 800000}, "http://127.0.0.1:3456", "controller-only-token", 15, image=IMAGE
    )
    assert status == 0
    assert json.loads(report) == {"digest": hashlib.sha256(bytes(range(256)) * 8192).hexdigest()}
    assert len(relayed) == 1
    assert all("controller-only-token" not in str(args) for args in calls)
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize(
    ("mode", "script", "error", "message"),
    [
        ("blocked-input", "import time; time.sleep(30)", TimeoutError, "pipe deadline"),
        ("eof", "import sys; sys.stdin.readline()", ValueError, "Incomplete"),
        (
            "partial-eof",
            "import sys; sys.stdin.readline(); sys.stdout.write('{'); sys.stdout.flush()",
            ValueError,
            "Incomplete",
        ),
        (
            "partial-stall",
            "import sys,time; sys.stdin.readline(); sys.stdout.write('{'); "
            "sys.stdout.flush(); time.sleep(30)",
            TimeoutError,
            "worker deadline",
        ),
    ],
)
def test_real_worker_pipe_failures_cleanup(
    monkeypatch, child_processes, mode, script, error, message
):
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    payload = {"padding": "x" * 800000} if mode == "blocked-input" else {}
    with pytest.raises(error, match=message):
        isolation.execute_worker(payload, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize("mode", ["success", "oversized", "nonzero", "timeout"])
def test_real_provenance_pipe_bounds_and_cleanup(monkeypatch, child_processes, mode):
    launch, processes = child_processes
    scripts = {
        "success": "import sys; sys.stdout.buffer.write(bytes(range(256))*1000)",
        "oversized": "import sys; sys.stdout.buffer.write(b'x'*600000); sys.stdout.flush()",
        "nonzero": "import sys; sys.stdout.write('partial'); sys.exit(2)",
        "timeout": "import time; time.sleep(30)",
    }
    monkeypatch.setattr(
        isolation.subprocess, "Popen", lambda args, **kw: launch(scripts[mode], **kw)
    )
    if mode == "timeout":
        real_read = isolation._read_pipe
        deadlines = []

        def read(stream, deadline, message):
            deadlines.append(deadline)
            return real_read(stream, min(deadline, time.monotonic() + 0.1), message)

        monkeypatch.setattr(isolation, "_read_pipe", read)
    if mode == "success":
        assert isolation._image_file_archive(NAME, "/source") == bytes(range(256)) * 1000
    else:
        error, message = {
            "oversized": (ValueError, "too large"),
            "nonzero": (ValueError, "unavailable"),
            "timeout": (TimeoutError, "timed out"),
        }[mode]
        with pytest.raises(error, match=message):
            isolation._image_file_archive(NAME, "/source")
    assert len(processes) == 1
    assert processes[0].poll() is not None and processes[0].stdout.closed


def test_read_and_write_requests_are_chunk_bounded(simulated_pipes):
    state, stream = simulated_pipes
    body = b"x" * (2 * isolation.PIPE_CHUNK + 7)
    state.writes = [isolation.PIPE_CHUNK, isolation.PIPE_CHUNK, 7]
    isolation._write_pipe(stream, body, 101)
    assert b"".join(state.attempts) == body
    assert max(map(len, state.attempts)) == isolation.PIPE_CHUNK


@pytest.mark.parametrize("direction", ["read", "write"])
def test_progress_does_not_reset_or_overrun_absolute_deadline(
    monkeypatch, simulated_pipes, direction
):
    state, stream = simulated_pipes
    deadline = state.now + 0.01

    def slow_read(fd, size):
        state.now = deadline
        return b"arrived too late"

    def slow_write(fd, data):
        state.now = deadline
        return len(data)

    monkeypatch.setattr(isolation.os, "read", slow_read)
    monkeypatch.setattr(isolation.os, "write", slow_write)
    with pytest.raises(TimeoutError, match="deadline"):
        if direction == "read":
            isolation._read_pipe(stream, deadline, "deadline")
        else:
            isolation._write_pipe(stream, b"sent too late", deadline)
    assert state.sleeps == []


def test_real_blocked_reply_uses_original_deadline_and_cleans_up(monkeypatch, child_processes):
    script = (
        "import sys,time; sys.stdin.readline(); "
        'print(\'{"type":"request","id":1}\', flush=True); time.sleep(30)'
    )
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    monkeypatch.setattr(
        isolation, "relay_request", lambda *a, **k: ({"body": "x" * 900000}, 900000)
    )
    deadlines = []
    real_write = isolation._write_pipe

    def write(stream, data, deadline):
        deadlines.append(deadline)
        return real_write(stream, data, deadline)

    monkeypatch.setattr(isolation, "_write_pipe", write)
    with pytest.raises(TimeoutError, match="pipe deadline"):
        isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert len(deadlines) == 2 and deadlines[0] == deadlines[1]
    assert_worker_cleaned(calls, processes)


@pytest.mark.parametrize("operation", ["worker", "provenance"])
def test_final_process_wait_never_adds_minimum_grace(monkeypatch, operation):
    state = SimpleNamespace(now=100.0, waits=[], closed=[])
    streams = {
        name: SimpleNamespace(close=lambda name=name: state.closed.append(name))
        for name in ("stdin", "stdout")
    }
    process = SimpleNamespace(
        **streams,
        poll=lambda: 0,
        wait=lambda *, timeout: state.waits.append(timeout) or 0,
    )
    monkeypatch.setattr(isolation, "time", SimpleNamespace(monotonic=lambda: state.now))
    monkeypatch.setattr(isolation.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(
        isolation.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=b"[{}]")
    )
    monkeypatch.setattr(isolation, "require_worker_inspection", lambda *a: {})
    monkeypatch.setattr(isolation, "require_image_sources", lambda *a: {})
    monkeypatch.setattr(isolation, "_write_pipe", lambda *a: None)
    frames = [b'{"type":"report","report":{},"exit_code":0}\n', b""]

    def read(stream, deadline, message):
        state.now = deadline - 0.025
        return frames.pop(0) if operation == "worker" else b""

    monkeypatch.setattr(isolation, "_read_pipe", read)
    if operation == "worker":
        assert isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE) == (
            b"{}",
            0,
        )
        assert state.closed == ["stdin", "stdout"]
    else:
        assert isolation._image_file_archive(NAME, "/source") == b""
        assert state.closed == ["stdout"]
    assert state.waits == pytest.approx([0.025, 5])


def test_real_eof_before_exit_still_times_out_and_cleans_up(monkeypatch, child_processes):
    script = (
        "import os,sys,time; sys.stdin.readline(); "
        'print(\'{"type":"report","report":{},"exit_code":0}\', flush=True); '
        "os.close(sys.stdout.fileno()); time.sleep(30)"
    )
    calls, processes = setup_worker(monkeypatch, child_processes, script)
    with pytest.raises(subprocess.TimeoutExpired):
        isolation.execute_worker({}, "http://127.0.0.1:3456", "secret", 1, image=IMAGE)
    assert_worker_cleaned(calls, processes)
````
