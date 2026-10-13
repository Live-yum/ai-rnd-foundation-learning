# tests/test_browser_memory_observation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `group`（L17–L31）：接收`root`、`identifier`、`layout`。 控制顺序：L24遍历`{ "memory.max": "805306368", "memory.current": "4096", "memory.pe…`。 调用`path.mkdir`、`{ "memory.max": "805306368", "memory.current": "4096", "memory.pe…`、`(path / name).write_text`。 返回路径：L31的`path`。
- `test_reads_only_exact_owned_group_and_bounded_numbers`（L36–L54）：接收`tmp_path`、`monkeypatch`、`layout`。 控制顺序：L43断言`identity`；L44断言`facts == { "memory_max": 805306368, "memory_unbounded": False, "memory_current": 4096…`；L51断言`{p.name: p.read_bytes() for p in owned.iterdir()} == before_bytes`；L52断言`"private" not in json.dumps(facts)`；L54断言`observe.read_cgroup(IDENTIFIER)[1]["memory_peak"] is None`。 调用`monkeypatch.setattr`、`group`、`(unrelated / "memory.max").write_text`、`p.read_bytes`、`owned.iterdir`、`observe.read_cgroup`、`json.dumps`、`(owned / "memory.peak").unlink`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bad_or_ambiguous_cgroup_reads_are_unavailable`（L61–L81）：接收`tmp_path`、`monkeypatch`、`fault`。 控制顺序：L64按`fault == "symlink"`分支；L67按`fault == "oversize"`分支；L69按`fault == "negative"`分支；L71按`fault == "missing"`分支；L73按`fault == "duplicate"`分支；L75按`fault == "two_groups"`分支；L81断言`observe.read_cgroup(IDENTIFIER) is None`。 调用`monkeypatch.setattr`、`group`、`(path / "memory.max").unlink`、`(path / "memory.max").symlink_to`、`(path / "memory.max").write_text`、`(path / "memory.current").write_text`、`(path / "memory.events.local").unlink`、`(path / "memory.events.local").write_text`、`(_ for _ in ()).throw`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_identity_never_reads_files_or_docker`（L85–L93）：接收`monkeypatch`、`identifier`。 控制顺序：L92断言`observe.read_cgroup(identifier) is None`；L93断言`observe.docker_events(["docker"], identifier, 1, 2) is None`。 调用`monkeypatch.setattr`、`pytest.fail`、`observe.read_cgroup`、`observe.docker_events`、`pytest.mark.parametrize`、`OTHER.upper`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_docker_events_have_exact_filters_and_no_private_output`（L99–L127）：接收`monkeypatch`、`identity`、`action`。 控制顺序：L122断言`value == ( [{"action": "oom", "time_nano": 100}] if identity == IDENTIFIER and action…`；L127断言`"private" not in json.dumps(value)`。 调用`monkeypatch.setattr`、`observe.docker_events`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_docker_events_have_exact_filters_and_no_private_output.run`（L100–L118）：接收`args`、`**kwargs`。 控制顺序：L101断言`args[:2] == ["docker", "events"]`；L102遍历`( "type=container", "container=" + IDENTIFIER, "event=oom", "even…`；L109断言`value in args`；L110断言`kwargs["timeout"] == 2`；L111断言`"logs" not in args and "exec" not in args`。 调用`SimpleNamespace`、`json.dumps( {"id": identity, "action": action, "time_nano": 100, …`、`json.dumps`。 返回路径：L112的`SimpleNamespace( returncode=0, stdout=json.dumps( {"id": identity, "action": action, "time…`。
- `test_missing_baseline_and_replaced_group_never_fabricate_delta`（L131–L148）：接收`tmp_path`、`monkeypatch`。 控制顺序：L137断言`observer.sample() is None`；L143断言`result["pre_start"] is None and result["pre_post_delta"] is None`；L144断言`result["observed_delta"] == {"max": 1, "oom": 1, "oom_kill": 1, "oom_group_kill": 0}`；L147断言`result["identity_changed"] is True`；L148断言`result["pre_post_delta"] is result["observed_delta"] is None`。 调用`monkeypatch.setattr`、`observe.MemoryObservation`、`observer.sample`、`group`、`(path / "memory.events.local").write_text`、`observer.finish`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mismatched_container_name_disables_all_observation`（L151–L158）：接收`monkeypatch`。 控制顺序：L158断言`observer.finish() == {"available": False}`。 调用`monkeypatch.setattr`、`pytest.fail`、`observe.MemoryObservation`、`observer.start`、`observer.finish`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_counter_reset_and_missing_sample_have_no_delta`（L161–L163）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L162断言`observe.counter_delta(None, None) is None`；L163断言`observe.counter_delta({"events_local": {"oom": 2}}, {"events_local": {"oom": 1}}) is …`。 调用`observe.counter_delta`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_observation_failure_cannot_replace_original_verdict`（L167–L188）：接收`monkeypatch`、`failure`。 控制顺序：L184抛异常，停止当前正常路径；L185断言`captured.value is original and facts == {"available": False}`；L188断言`facts == {"available": False}`。 调用`monkeypatch.setattr`、`RuntimeError`、`pytest.raises`、`observe.observe_memory`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_observation_failure_cannot_replace_original_verdict.Broken`（L168–L178）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_observation_failure_cannot_replace_original_verdict.Broken.__init__`（L169–L171）：接收`*args`。 控制顺序：L170按`failure == "constructor"`分支；L171抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_observation_failure_cannot_replace_original_verdict.Broken.start`（L173–L175）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L174按`failure == "start"`分支；L175抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_observation_failure_cannot_replace_original_verdict.Broken.finish`（L177–L178）：接收`**kwargs`。 控制顺序：L178抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_poll_has_finite_sampling_budget`（L191–L200）：接收`monkeypatch`。 控制顺序：L200断言`ticks == [0.1] * 300`。 调用`observe.MemoryObservation`、`SimpleNamespace`、`ticks.append`、`monkeypatch.setattr`、`observer.poll`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unconfirmed_stop_never_delays_cleanup_with_extra_reads_or_events`（L203–L220）：接收`monkeypatch`。 控制顺序：L216断言`observer.stop.is_set()`；L217断言`facts["available"] is False and facts["post_start_return"] is facts["docker_events"] …`；L220断言`facts["post_start_return_status"] == "termination_not_confirmed"`。 调用`observe.MemoryObservation`、`SimpleNamespace`、`pytest.fail`、`monkeypatch.setattr`、`observer.finish`、`observer.stop.is_set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_container_cgroup_lifecycle_explains_missing_endpoints_without_fabricating_oom`（L226–L279）：接收`tmp_path`、`monkeypatch`、`before_exists`、`removed_at_exit`。 控制顺序：L247按`path`分支；L257断言`observer.before_status == ("available" if before_exists else "group_absent")`；L258按`path is None`分支；L267按`removed_at_exit`分支；L270抛异常，停止当前正常路径；L271断言`captured.value is original`；L272断言`facts["pre_start_status"] == ("available" if before_exists else "group_absent")`；L273断言`facts["post_start_return_status"] == ("group_absent" if removed_at_exit else "availab…`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`SimpleNamespace`、`group`、`counters`、`observe.MemoryObservation`、`RuntimeError`、`pytest.raises`、`observe.observe_memory`、`observer.sample`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_container_cgroup_lifecycle_explains_missing_endpoints_without_fabricating_oom.counters`（L241–L244）：接收`path`、`maximum`。 调用`(path / "memory.events.local").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_sample_reasons_are_finite_without_exception_or_path_text`（L293–L312）：接收`tmp_path`、`monkeypatch`、`fault`、`expected`。 控制顺序：L297按`fault != "absent"`分支；L299按`fault == "missing_counter"`分支；L301按`fault == "bad_counter"`分支；L303按`fault == "ambiguous"`分支；L311断言`observe.read_cgroup_observation(IDENTIFIER) == (None, expected)`；L312断言`observe.read_cgroup(IDENTIFIER) is None`。 调用`monkeypatch.setattr`、`group`、`(path / "memory.current").unlink`、`(path / "memory.events.local").write_text`、`(_ for _ in ()).throw`、`PermissionError`、`observe.read_cgroup_observation`、`observe.read_cgroup`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_browser_memory_observation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L312。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12587`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_browser_memory_observation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "abc8819f87960da74d04081404193f8091984eef007a6c04965c80af713b16f9"} -->
````python
# tests/test_browser_memory_observation.py
"""Read-only fixtures only; these are not cgroup enforcement certification."""

import json
import shutil
import sys
from types import SimpleNamespace

import pytest

from scripts import browser_memory_observation as observe

IDENTIFIER = "a" * 64
OTHER = "b" * 64
LINUX_COUNTERS = pytest.mark.skipif(sys.platform != "linux", reason="Linux cgroup filesystem")


def group(root, identifier=IDENTIFIER, layout="systemd"):
    path = (
        root / "system.slice" / f"docker-{identifier}.scope"
        if layout == "systemd"
        else root / "docker" / identifier
    )
    path.mkdir(parents=True)
    for name, value in {
        "memory.max": "805306368",
        "memory.current": "4096",
        "memory.peak": "8192",
        "memory.events.local": "low 0\nhigh 0\nmax 2\noom 1\noom_kill 1\noom_group_kill 0\n",
    }.items():
        (path / name).write_text(value)
    return path


@pytest.mark.parametrize("layout", ["systemd", "cgroupfs"])
@LINUX_COUNTERS
def test_reads_only_exact_owned_group_and_bounded_numbers(tmp_path, monkeypatch, layout):
    monkeypatch.setattr(observe, "CGROUP_ROOT", tmp_path)
    owned = group(tmp_path, layout=layout)
    unrelated = group(tmp_path, OTHER, layout)
    (unrelated / "memory.max").write_text("private unrelated content")
    before_bytes = {p.name: p.read_bytes() for p in owned.iterdir()}
    identity, facts = observe.read_cgroup(IDENTIFIER)
    assert identity
    assert facts == {
        "memory_max": 805306368,
        "memory_unbounded": False,
        "memory_current": 4096,
        "memory_peak": 8192,
        "events_local": {"max": 2, "oom": 1, "oom_kill": 1, "oom_group_kill": 0},
    }
    assert {p.name: p.read_bytes() for p in owned.iterdir()} == before_bytes
    assert "private" not in json.dumps(facts)
    (owned / "memory.peak").unlink()
    assert observe.read_cgroup(IDENTIFIER)[1]["memory_peak"] is None


@pytest.mark.parametrize(
    "fault", ["symlink", "oversize", "negative", "missing", "duplicate", "denied", "two_groups"]
)
@LINUX_COUNTERS
def test_bad_or_ambiguous_cgroup_reads_are_unavailable(tmp_path, monkeypatch, fault):
    monkeypatch.setattr(observe, "CGROUP_ROOT", tmp_path)
    path = group(tmp_path)
    if fault == "symlink":
        (path / "memory.max").unlink()
        (path / "memory.max").symlink_to(tmp_path / "private")
    elif fault == "oversize":
        (path / "memory.max").write_text("9" * 5000)
    elif fault == "negative":
        (path / "memory.current").write_text("-1")
    elif fault == "missing":
        (path / "memory.events.local").unlink()
    elif fault == "duplicate":
        (path / "memory.events.local").write_text("max 0\noom 0\noom_kill 0\noom_kill 1")
    elif fault == "two_groups":
        group(tmp_path, layout="cgroupfs")
    else:
        monkeypatch.setattr(
            observe.os, "open", lambda *a, **k: (_ for _ in ()).throw(PermissionError())
        )
    assert observe.read_cgroup(IDENTIFIER) is None


@pytest.mark.parametrize("identifier", [None, "", "a" * 63, "../private", OTHER.upper()])
def test_invalid_identity_never_reads_files_or_docker(monkeypatch, identifier):
    monkeypatch.setattr(
        observe.os, "open", lambda *a, **k: pytest.fail("unexpected filesystem read")
    )
    monkeypatch.setattr(
        observe.subprocess, "run", lambda *a, **k: pytest.fail("unexpected Docker read")
    )
    assert observe.read_cgroup(identifier) is None
    assert observe.docker_events(["docker"], identifier, 1, 2) is None


@pytest.mark.parametrize(
    "identity,action", [(IDENTIFIER, "oom"), (OTHER, "oom"), (IDENTIFIER, "exec_start")]
)
def test_docker_events_have_exact_filters_and_no_private_output(monkeypatch, identity, action):
    def run(args, **kwargs):
        assert args[:2] == ["docker", "events"]
        for value in (
            "type=container",
            "container=" + IDENTIFIER,
            "event=oom",
            "event=kill",
            "event=die",
        ):
            assert value in args
        assert kwargs["timeout"] == 2
        assert "logs" not in args and "exec" not in args
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {"id": identity, "action": action, "time_nano": 100, "private": "never publish"}
            ).encode(),
            stderr=b"private",
        )

    monkeypatch.setattr(observe.subprocess, "run", run)
    value = observe.docker_events(["docker"], IDENTIFIER, 0, 1)
    assert value == (
        [{"action": "oom", "time_nano": 100}]
        if identity == IDENTIFIER and action == "oom"
        else None
    )
    assert "private" not in json.dumps(value)


@LINUX_COUNTERS
def test_missing_baseline_and_replaced_group_never_fabricate_delta(tmp_path, monkeypatch):
    monkeypatch.setattr(observe, "CGROUP_ROOT", tmp_path)
    monkeypatch.setattr(observe, "docker_events", lambda *a: [])
    observer = observe.MemoryObservation(
        [{"Id": IDENTIFIER, "Name": "/owned"}], "owned", ["docker"]
    )
    assert observer.sample() is None
    path = group(tmp_path)
    observer.sample()
    (path / "memory.events.local").write_text("max 3\noom 2\noom_kill 2\noom_group_kill 0")
    observer.sample()
    result = observer.finish(stopped=True)
    assert result["pre_start"] is None and result["pre_post_delta"] is None
    assert result["observed_delta"] == {"max": 1, "oom": 1, "oom_kill": 1, "oom_group_kill": 0}
    observer.identity = (-1, -1)
    result = observer.finish(stopped=True)
    assert result["identity_changed"] is True
    assert result["pre_post_delta"] is result["observed_delta"] is None


def test_mismatched_container_name_disables_all_observation(monkeypatch):
    monkeypatch.setattr(observe, "read_cgroup", lambda *a: pytest.fail("unexpected read"))
    monkeypatch.setattr(observe, "docker_events", lambda *a: pytest.fail("unexpected event query"))
    observer = observe.MemoryObservation(
        [{"Id": IDENTIFIER, "Name": "/other"}], "owned", ["docker"]
    )
    observer.start()
    assert observer.finish() == {"available": False}


def test_counter_reset_and_missing_sample_have_no_delta():
    assert observe.counter_delta(None, None) is None
    assert observe.counter_delta({"events_local": {"oom": 2}}, {"events_local": {"oom": 1}}) is None


@pytest.mark.parametrize("failure", ["constructor", "start", "finish"])
def test_observation_failure_cannot_replace_original_verdict(monkeypatch, failure):
    class Broken:
        def __init__(self, *args):
            if failure == "constructor":
                raise PermissionError("private permission failure")

        def start(self):
            if failure == "start":
                raise OSError("private unavailable counter")

        def finish(self, **kwargs):
            raise RuntimeError("private diagnostic error")

    monkeypatch.setattr(observe, "MemoryObservation", Broken)
    original = RuntimeError("original strict gate failure")
    with pytest.raises(RuntimeError) as captured:
        with observe.observe_memory([], "owned", ["docker"]) as facts:
            raise original
    assert captured.value is original and facts == {"available": False}
    with observe.observe_memory([], "owned", ["docker"]) as facts:
        pass  # A genuine success also stays successful if diagnostics are unavailable.
    assert facts == {"available": False}


def test_poll_has_finite_sampling_budget(monkeypatch):
    observer = observe.MemoryObservation(
        [{"Id": IDENTIFIER, "Name": "/owned"}], "owned", ["docker"]
    )
    ticks = []
    observer.stop = SimpleNamespace(wait=lambda delay: ticks.append(delay) or False)
    monkeypatch.setattr(observe.time, "monotonic", lambda: 0)
    monkeypatch.setattr(observer, "sample", lambda: None)
    observer.poll()
    assert ticks == [0.1] * 300


def test_unconfirmed_stop_never_delays_cleanup_with_extra_reads_or_events(monkeypatch):
    observer = observe.MemoryObservation(
        [{"Id": IDENTIFIER, "Name": "/owned"}], "owned", ["docker"]
    )
    observer.thread = SimpleNamespace(join=lambda **k: pytest.fail("must not delay cleanup"))
    monkeypatch.setattr(observe, "read_cgroup", lambda *a: pytest.fail("extra read before cleanup"))
    monkeypatch.setattr(
        observe, "read_cgroup_observation", lambda *a: pytest.fail("extra read before cleanup")
    )
    monkeypatch.setattr(
        observe, "docker_events", lambda *a: pytest.fail("extra event query before cleanup")
    )
    facts = observer.finish(stopped=False)
    assert observer.stop.is_set()
    assert (
        facts["available"] is False and facts["post_start_return"] is facts["docker_events"] is None
    )
    assert facts["post_start_return_status"] == "termination_not_confirmed"


@pytest.mark.parametrize("before_exists", [False, True])
@pytest.mark.parametrize("removed_at_exit", [False, True])
@LINUX_COUNTERS
def test_container_cgroup_lifecycle_explains_missing_endpoints_without_fabricating_oom(
    tmp_path, monkeypatch, before_exists, removed_at_exit
):
    monkeypatch.setattr(observe, "CGROUP_ROOT", tmp_path)
    monkeypatch.setattr(observe, "docker_events", lambda *a: [{"action": "die", "time_nano": 10}])
    monkeypatch.setattr(
        observe.threading,
        "Thread",
        lambda **k: SimpleNamespace(
            start=lambda: None,
            join=lambda **k: None,
            is_alive=lambda: False,
        ),
    )

    def counters(path, maximum):
        (path / "memory.events.local").write_text(
            f"max {maximum}\noom 0\noom_kill 0\noom_group_kill 0\n"
        )

    path = group(tmp_path) if before_exists else None
    if path:
        counters(path, 0)
    observer = observe.MemoryObservation(
        [{"Id": IDENTIFIER, "Name": "/owned"}], "owned", ["docker"]
    )
    monkeypatch.setattr(observe, "MemoryObservation", lambda *a: observer)
    original = RuntimeError("original strict OOMKilled gate rejection")
    with pytest.raises(RuntimeError) as captured:
        with observe.observe_memory([], "owned", ["docker"]) as facts:
            # The sample preceding docker start cannot see an uncreated group.
            assert observer.before_status == ("available" if before_exists else "group_absent")
            if path is None:
                path = group(tmp_path)
                counters(path, 0)
            observer.sample()
            counters(path, 1)
            (path / "memory.peak").write_text("805306368")
            observer.sample()
            # Runtime teardown may remove the exact group before our inspect
            # and before the test harness's later docker rm cleanup.
            if removed_at_exit:
                shutil.rmtree(path)
            facts["container_stopped"] = True
            raise original
    assert captured.value is original
    assert facts["pre_start_status"] == ("available" if before_exists else "group_absent")
    assert facts["post_start_return_status"] == ("group_absent" if removed_at_exit else "available")
    assert facts["post_start_return_stage"] == "after_termination_inspect"
    assert (facts["pre_start"] is None) is (not before_exists)
    assert (facts["post_start_return"] is None) is removed_at_exit
    assert facts["observed_delta"] == {"max": 1, "oom": 0, "oom_kill": 0, "oom_group_kill": 0}
    assert (facts["pre_post_delta"] is not None) is (before_exists and not removed_at_exit)
    assert facts["last_observed"]["memory_peak"] == 805306368


@pytest.mark.parametrize(
    "fault,expected",
    [
        ("absent", "group_absent"),
        ("missing_counter", "counter_missing"),
        ("denied", "permission_denied"),
        ("bad_counter", "invalid_counter_or_path"),
        ("ambiguous", "ambiguous_layout"),
    ],
)
@LINUX_COUNTERS
def test_missing_sample_reasons_are_finite_without_exception_or_path_text(
    tmp_path, monkeypatch, fault, expected
):
    monkeypatch.setattr(observe, "CGROUP_ROOT", tmp_path)
    if fault != "absent":
        path = group(tmp_path)
        if fault == "missing_counter":
            (path / "memory.current").unlink()
        elif fault == "bad_counter":
            (path / "memory.events.local").write_text("private-path-secret")
        elif fault == "ambiguous":
            group(tmp_path, layout="cgroupfs")
        else:
            monkeypatch.setattr(
                observe.os,
                "open",
                lambda *a, **k: (_ for _ in ()).throw(PermissionError("private-path-secret")),
            )
    assert observe.read_cgroup_observation(IDENTIFIER) == (None, expected)
    assert observe.read_cgroup(IDENTIFIER) is None
````
