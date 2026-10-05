"""Peer lifecycle contract tests; these mocks do not certify actual egress."""

import json
from types import SimpleNamespace

import pytest

from scripts import capability_native_egress as probe
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection


def setup(monkeypatch, *, label="owned", denied=True):
    commands = []
    name = [""]
    monkeypatch.setattr(probe, "compose", lambda *a: "a" * 64)
    monkeypatch.setattr(probe, "product_argv", lambda plan, argv, env: argv)
    monkeypatch.setattr(
        probe,
        "run_guarded_control",
        lambda *a: (0 if denied else 1, json.dumps({"native_egress_denied_same_ports": denied})),
    )

    def docker(*args, **kwargs):
        commands.append(args)
        if "curl" in args:
            return "rnd-owned-egress-peer"
        tail = args[5:]
        if tail[0] == "run":
            name[0] = tail[tail.index("--name") + 1]
            return "b" * 64
        if tail[:2] == ("container", "inspect"):
            return json.dumps(
                [
                    {
                        "Id": "b" * 64,
                        "Name": "/" + name[0],
                        "Config": {"Labels": {"rnd-owned-sandbox": label}},
                        "Image": "sha256:" + "c" * 64,
                        "NetworkSettings": {
                            "Networks": {"runner-bridge": {"IPAddress": "172.20.0.42"}}
                        },
                    }
                ]
            )
        if tail[0] == "rm":
            return "b" * 64
        raise AssertionError(args)

    monkeypatch.setattr(probe.local, "docker", docker)
    return commands


def execute():
    return probe.verify_native_egress(
        None,
        {"snapshot": {"image_id": "sha256:" + "c" * 64}},
        SimpleNamespace(id="owned"),
        SimpleNamespace(
            selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(port=8000)
        ),
        30,
    )


def test_peer_is_bounded_unpublished_and_removed_after_positive_controls(monkeypatch):
    commands = setup(monkeypatch)
    assert execute() == {"native_egress_denied_same_ports": True}
    launch = next(c for c in commands if "run" in c)
    for flag in (
        "--read-only",
        "--cap-drop",
        "--security-opt",
        "--memory",
        "--memory-swap",
        "--cpus",
        "--pids-limit",
    ):
        assert flag in launch
    assert "--publish" not in launch and "-p" not in launch and "--privileged" not in launch
    assert sum("curl" in c for c in commands) == 6
    assert commands[-1][-3:] == ("rm", "--force", "b" * 64)


def test_failed_denial_still_removes_only_owned_peer(monkeypatch):
    commands = setup(monkeypatch, denied=False)
    with pytest.raises(CheckFailure, match="同端口"):
        execute()
    assert commands[-1][-3:] == ("rm", "--force", "b" * 64)


def test_identity_mismatch_never_removes_another_container(monkeypatch):
    commands = setup(monkeypatch, label="someone-else")
    with pytest.raises(CheckFailure, match="清理未确认"):
        execute()
    assert not any("rm" in c for c in commands)
