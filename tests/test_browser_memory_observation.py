"""Read-only fixtures only; these are not cgroup enforcement certification."""

import json
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
        observe, "docker_events", lambda *a: pytest.fail("extra event query before cleanup")
    )
    facts = observer.finish(stopped=False)
    assert observer.stop.is_set()
    assert (
        facts["available"] is False and facts["post_start_return"] is facts["docker_events"] is None
    )
