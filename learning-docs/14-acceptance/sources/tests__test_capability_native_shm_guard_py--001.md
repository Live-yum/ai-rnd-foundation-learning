# tests/test_capability_native_shm_guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `owned_shm`（L15–L83）：接收`tmp_path`、`monkeypatch`。 源码说明：Substitute metadata only; this does not attest a tmpfs or private IPC.。 调用`device.mkdir`、`(device / "shm").mkdir`、`SimpleNamespace`、`monkeypatch.setattr`、`original_statvfs`。 返回路径：L83的`state`。
- `owned_shm.opened`（L36–L40）：接收`path`、`flags`、`*args`、`**kwargs`。 控制顺序：L38按`path == "shm"`分支。 调用`original_open`、`descriptors.append`。 返回路径：L40的`descriptor`。
- `owned_shm.entry`（L42–L55）：接收`descriptor`。 控制顺序：L44按`descriptor not in descriptors`分支。 调用`original_fstat`、`SimpleNamespace`。 返回路径：L45的`actual`；L46的`SimpleNamespace( **{ "st_dev": actual.st_dev, "st_ino": actual.st_ino, "st_mode": stat.S_I…`。
- `owned_shm.read`（L57–L69）：接收`path`。 控制顺序：L58按`path.startswith("/proc/self/fdinfo/")`分支；L60按`path == "/proc/self/mountinfo"`分支；L62按`state.mountinfo is not None`分支。 调用`path.startswith`、`original_fstat`、`os.major`、`os.minor`、`original_read`。 返回路径：L59的`state.fdinfo`；L63的`state.mountinfo`；L65的`f"42 1 {os.major(actual.st_dev)}:{os.minor(actual.st_dev)} / /dev/shm " "rw,nosuid,nodev,n…`。
- `assert_rejected`（L86–L92）：接收`fixture`。 控制顺序：L89遍历`fixture.descriptors`；L92断言`caught.value.errno == errno.EBADF`。 调用`pytest.raises`、`guard.open_verified_native_shm`、`fixture.original_fstat`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_metadata_fixture_matches_required_mount`（L95–L103）：接收`owned_shm`。 控制顺序：L98断言`owned_shm.original_fstat(descriptor).st_ino == (owned_shm.device / "shm").stat().st_i…`；L101断言`owned_shm.reads == 2`。 调用`guard.open_verified_native_shm`、`owned_shm.original_fstat`、`(owned_shm.device / "shm").stat`、`os.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_rejects_wrong_ownership_and_type`（L117–L119）：接收`owned_shm`、`field`、`value`。 调用`assert_rejected`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_rejects_wrong_actual_size_or_flags`（L135–L137）：接收`owned_shm`、`field`、`value`。 调用`assert_rejected`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_rejects_malformed_wrong_or_ambiguous_mount`（L160–L167）：接收`owned_shm`、`change`。 调用`(owned_shm.device / "shm").stat`、`os.major`、`os.minor`、`change`、`assert_rejected`、`pytest.mark.parametrize`、`line.replace`、`line.replace("42 1 ", "43 1 ").replace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_binds_descriptor_device_to_mountinfo`（L170–L172）：接收`owned_shm`。 调用`assert_rejected`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_requires_unique_descriptor_mount_id`（L176–L178）：接收`owned_shm`、`fdinfo`。 调用`assert_rejected`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_opens_each_component_without_following_symlinks`（L182–L191）：接收`owned_shm`、`tmp_path`、`parent`。 控制顺序：L186按`parent`分支；L191断言`list(target.iterdir()) == []`。 调用`target.mkdir`、`(path / "shm").rmdir`、`path.rmdir`、`path.symlink_to`、`assert_rejected`、`list`、`target.iterdir`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_mount_identity_must_stay_fixed_until_rule_add`（L194–L204）：接收`owned_shm`、`monkeypatch`。 调用`monkeypatch.setattr`、`assert_rejected`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shm_mount_identity_must_stay_fixed_until_rule_add.changed`（L198–L201）：接收`descriptor`。 调用`original`、`identities.append`、`len`。 返回路径：L201的`identity if len(identities) == 1 else (*identity, "changed")`。
- `test_native_shm_rights_are_only_regular_file_operations`（L207–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L208断言`guard.NATIVE_SHM_ACCESS == sum(1 << bit for bit in (1, 5, 8, 13, 14))`；L209断言`guard.NATIVE_SHM_ACCESS & sum(1 << bit for bit in (0, 4, 6, 7, 9, 10, 11, 12)) == 0`；L210断言`guard.NATIVE_SHM_EVIDENCE == isolation.NATIVE_SHARED_MEMORY_EVIDENCE`。 调用`sum`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `plan`（L213–L217）：接收`template`、`database`。 调用`SimpleNamespace`。 返回路径：L214的`SimpleNamespace( selection=SimpleNamespace(template=template, database=database), runtime=…`。
- `test_native_shm_flag_requires_explicit_trusted_launch_keyword`（L220–L230）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L223断言`"55433" in ordinary[ordinary.index(isolation.GUARD) + 2]`；L224断言`"--native-shm" not in ordinary`；L225断言`native == ordinary[: ordinary.index(isolation.GUARD) + 3] + ["--native-shm"] + ordina…`。 调用`isolation.product_argv`、`plan`、`ordinary.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_native_launch_cannot_receive_shared_memory_permission`（L242–L246）：接收`template`、`database`、`enabled`。 调用`pytest.raises`、`isolation.product_argv`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shared_memory_receipt_requires_exact_typed_finite_fields`（L249–L263）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L251断言`isolation.require_native_shared_memory_evidence(value) == value`；L252遍历`value.items()`；L253遍历`[None, str(wanted), not wanted if type(wanted) is bool else True]`；L254按`type(replacement) is type(wanted) and replacement == wanted`分支。 调用`dict`、`isolation.require_native_shared_memory_evidence`、`value.items`、`str`、`type`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_guard_flag_controls_only_explicit_filesystem_extension`（L268–L303）：接收`monkeypatch`、`capsys`、`native`、`probe`。 源码说明：Launcher parser unit test; all security calls are replaced, never executed.。 控制顺序：L292断言`len(calls) == 1`；L293断言`calls[0][2]["native_semaphore_storage"] is native`；L294断言`calls[0][2]["filesystem"] is (not probe or native)`；L295断言`resources == [{"native": True}]`；L296按`probe`分支；L300断言`("native_shared_memory" in receipt) is native`；L301断言`executed == []`；L303断言`executed[0][:2] == ("/bin/true", ["/bin/true", "--native-shm"])`。 调用`monkeypatch.setattr`、`resources.append`、`executed.append`、`guard.main`、`len`、`json.loads`、`capsys.readouterr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_guard_flag_controls_only_explicit_filesystem_extension.restrict`（L272–L276）：接收`bind_ports`、`connect_ports`、`**kwargs`。 控制顺序：L274按`kwargs["native_semaphore_storage"]`分支。 调用`calls.append`、`kwargs.copy`、`dict`。 返回路径：L276的`6`。
- `test_guard_rejects_malformed_flag_before_security_setup`（L315–L323）：接收`monkeypatch`、`command`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`guard.main`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_container_receipt`（L326–L339）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L327的`{ "profile": "native-fastapiadmin-postgresql-v1", "sandbox_id": "00000000-0000-0000-0000-0…`。
- `test_native_container_receipt_requires_private_bounded_shared_memory`（L357–L363）：接收`shared_memory`。 控制顺序：L359断言`isolation.require_container_evidence(valid, valid["sandbox_id"]) == valid`。 调用`native_container_receipt`、`isolation.require_container_evidence`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_isolation_evidence_binds_native_extension_to_selected_launch_profile`（L366–L383）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L378断言`isolation.require_isolation_evidence(ordinary) == ordinary`；L379断言`isolation.require_isolation_evidence(native, native_semaphore_storage=True) == native`。 调用`sha`、`dict.fromkeys`、`dict`、`isolation.require_isolation_evidence`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_shm_guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L383。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14234`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_shm_guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f40c08f35ccd6a511729c7ac8b94d3a38a726ccbbdfca9c3a530737bed43f94e"} -->
````python
# tests/test_capability_native_shm_guard.py
"""Owned-directory unit fixtures; real native mount acceptance is mandatory in CI."""

import errno
import os
import stat
from types import SimpleNamespace

import pytest

from scripts import capability_guard as guard
from workbench import capability_isolation as isolation


@pytest.fixture
def owned_shm(tmp_path, monkeypatch):
    """Substitute metadata only; this does not attest a tmpfs or private IPC."""
    device = tmp_path / "dev"
    device.mkdir()
    (device / "shm").mkdir()
    original_open, original_fstat = os.open, os.fstat
    original_statvfs, original_read = os.fstatvfs, guard._read_proc
    descriptors = []
    state = SimpleNamespace(
        device=device,
        entry={},
        filesystem={
            "f_frsize": 4096,
            "f_blocks": 16384,
            "f_flag": os.ST_NOEXEC | os.ST_NOSUID | os.ST_NODEV,
        },
        fdinfo="mnt_id:\t42\n",
        mountinfo=None,
        reads=0,
    )

    def opened(path, flags, *args, **kwargs):
        descriptor = original_open(device if path == "/dev" else path, flags, *args, **kwargs)
        if path == "shm":
            descriptors.append(descriptor)
        return descriptor

    def entry(descriptor):
        actual = original_fstat(descriptor)
        if descriptor not in descriptors:
            return actual
        return SimpleNamespace(
            **{
                "st_dev": actual.st_dev,
                "st_ino": actual.st_ino,
                "st_mode": stat.S_IFDIR | 0o1777,
                "st_uid": 0,
                "st_gid": 0,
                **state.entry,
            }
        )

    def read(path):
        if path.startswith("/proc/self/fdinfo/"):
            return state.fdinfo
        if path == "/proc/self/mountinfo":
            state.reads += 1
            if state.mountinfo is not None:
                return state.mountinfo
            actual = original_fstat(descriptors[-1])
            return (
                f"42 1 {os.major(actual.st_dev)}:{os.minor(actual.st_dev)} / /dev/shm "
                "rw,nosuid,nodev,noexec,relatime - tmpfs shm rw,size=65536k\n"
            )
        return original_read(path)

    state.original_fstat = original_fstat
    state.descriptors = descriptors
    monkeypatch.setattr(guard.os, "open", opened)
    monkeypatch.setattr(guard.os, "fstat", entry)
    monkeypatch.setattr(
        guard.os,
        "fstatvfs",
        lambda fd: (
            SimpleNamespace(**state.filesystem) if fd in descriptors else original_statvfs(fd)
        ),
    )
    monkeypatch.setattr(guard, "_read_proc", read)
    return state


def assert_rejected(fixture):
    with pytest.raises((RuntimeError, OSError)):
        guard.open_verified_native_shm()
    for descriptor in fixture.descriptors:
        with pytest.raises(OSError) as caught:
            fixture.original_fstat(descriptor)
        assert caught.value.errno == errno.EBADF


def test_owned_metadata_fixture_matches_required_mount(owned_shm):
    descriptor = guard.open_verified_native_shm()
    try:
        assert (
            owned_shm.original_fstat(descriptor).st_ino == (owned_shm.device / "shm").stat().st_ino
        )
        assert owned_shm.reads == 2
    finally:
        os.close(descriptor)


@pytest.mark.parametrize(
    "field,value",
    [
        ("st_uid", 1),
        ("st_gid", 1),
        ("st_mode", stat.S_IFDIR | 0o777),
        ("st_mode", stat.S_IFDIR | 0o1770),
        ("st_mode", stat.S_IFREG | 0o1777),
        ("st_mode", stat.S_IFLNK | 0o1777),
    ],
)
def test_native_shm_rejects_wrong_ownership_and_type(owned_shm, field, value):
    owned_shm.entry[field] = value
    assert_rejected(owned_shm)


@pytest.mark.parametrize(
    "field,value",
    [
        ("f_frsize", 0),
        ("f_blocks", 0),
        ("f_blocks", 16383),
        ("f_blocks", 16385),
        ("f_flag", os.ST_NOSUID | os.ST_NODEV),
        ("f_flag", os.ST_NOEXEC | os.ST_NODEV),
        ("f_flag", os.ST_NOEXEC | os.ST_NOSUID),
        ("f_flag", os.ST_NOEXEC | os.ST_NOSUID | os.ST_NODEV | os.ST_RDONLY),
    ],
)
def test_native_shm_rejects_wrong_actual_size_or_flags(owned_shm, field, value):
    owned_shm.filesystem[field] = value
    assert_rejected(owned_shm)


@pytest.mark.parametrize(
    "change",
    [
        lambda line: line.replace("/ /dev/shm", "/subdirectory /dev/shm"),
        lambda line: line.replace("/dev/shm", "/other"),
        lambda line: line.replace("tmpfs shm", "ext4 shm"),
        lambda line: line.replace("rw,nosuid", "ro,nosuid"),
        lambda line: line.replace("nosuid,", ""),
        lambda line: line.replace("nodev,", ""),
        lambda line: line.replace("noexec,", ""),
        lambda line: line.replace(" - ", " shared:9 - "),
        lambda line: line.replace(" - ", " master:9 - "),
        lambda line: line.replace(" - ", " propagate_from:9 - "),
        lambda line: line.replace("shm rw,", "shm ro,"),
        lambda line: line + line.replace("42 1 ", "43 1 "),
        lambda line: line + line.replace("42 1 ", "43 1 ").replace("/dev/shm", "/dev/shm/nested"),
        lambda line: line.replace(" - ", " malformed "),
        lambda line: "malformed\n" + line,
    ],
)
def test_native_shm_rejects_malformed_wrong_or_ambiguous_mount(owned_shm, change):
    raw_device = (owned_shm.device / "shm").stat().st_dev
    line = (
        f"42 1 {os.major(raw_device)}:{os.minor(raw_device)} / /dev/shm "
        "rw,nosuid,nodev,noexec,relatime - tmpfs shm rw,size=65536k\n"
    )
    owned_shm.mountinfo = change(line)
    assert_rejected(owned_shm)


def test_native_shm_binds_descriptor_device_to_mountinfo(owned_shm):
    owned_shm.mountinfo = "42 1 999:999 / /dev/shm rw,nosuid,nodev,noexec - tmpfs shm rw\n"
    assert_rejected(owned_shm)


@pytest.mark.parametrize("fdinfo", ["", "mnt_id: 0\n", "mnt_id: x\n", "mnt_id: 42\nmnt_id: 42\n"])
def test_native_shm_requires_unique_descriptor_mount_id(owned_shm, fdinfo):
    owned_shm.fdinfo = fdinfo
    assert_rejected(owned_shm)


@pytest.mark.parametrize("parent", [False, True])
def test_native_shm_opens_each_component_without_following_symlinks(owned_shm, tmp_path, parent):
    target = tmp_path / "outside"
    target.mkdir()
    path = owned_shm.device if parent else owned_shm.device / "shm"
    if parent:
        (path / "shm").rmdir()
    path.rmdir()
    path.symlink_to(target, target_is_directory=True)
    assert_rejected(owned_shm)
    assert list(target.iterdir()) == []


def test_native_shm_mount_identity_must_stay_fixed_until_rule_add(owned_shm, monkeypatch):
    original = guard._native_shm_mount_identity
    identities = []

    def changed(descriptor):
        identity = original(descriptor)
        identities.append(identity)
        return identity if len(identities) == 1 else (*identity, "changed")

    monkeypatch.setattr(guard, "_native_shm_mount_identity", changed)
    assert_rejected(owned_shm)


def test_native_shm_rights_are_only_regular_file_operations():
    assert guard.NATIVE_SHM_ACCESS == sum(1 << bit for bit in (1, 5, 8, 13, 14))
    assert guard.NATIVE_SHM_ACCESS & sum(1 << bit for bit in (0, 4, 6, 7, 9, 10, 11, 12)) == 0
    assert guard.NATIVE_SHM_EVIDENCE == isolation.NATIVE_SHARED_MEMORY_EVIDENCE


def plan(template="fastapiadmin", database="postgresql"):
    return SimpleNamespace(
        selection=SimpleNamespace(template=template, database=database),
        runtime=SimpleNamespace(port=8123),
    )


def test_native_shm_flag_requires_explicit_trusted_launch_keyword():
    ordinary = isolation.product_argv(plan(), ["/bin/true"], {})
    native = isolation.product_argv(plan(), ["/bin/true"], {}, native_semaphore_storage=True)
    assert "55433" in ordinary[ordinary.index(isolation.GUARD) + 2]
    assert "--native-shm" not in ordinary
    assert (
        native
        == ordinary[: ordinary.index(isolation.GUARD) + 3]
        + ["--native-shm"]
        + ordinary[ordinary.index(isolation.GUARD) + 3 :]
    )


@pytest.mark.parametrize(
    "template,database,enabled",
    [
        ("python-basic", "sqlite", True),
        ("python-basic", "postgresql", True),
        ("fastapiadmin", "sqlite", True),
        ("fastapiadmin", "postgresql", 1),
    ],
)
def test_non_native_launch_cannot_receive_shared_memory_permission(template, database, enabled):
    with pytest.raises(isolation.IsolationUnavailable):
        isolation.product_argv(
            plan(template, database), ["/bin/true"], {}, native_semaphore_storage=enabled
        )


def test_native_shared_memory_receipt_requires_exact_typed_finite_fields():
    value = dict(isolation.NATIVE_SHARED_MEMORY_EVIDENCE)
    assert isolation.require_native_shared_memory_evidence(value) == value
    for key, wanted in value.items():
        for replacement in [None, str(wanted), not wanted if type(wanted) is bool else True]:
            if type(replacement) is type(wanted) and replacement == wanted:
                continue
            with pytest.raises(isolation.IsolationUnavailable):
                isolation.require_native_shared_memory_evidence({**value, key: replacement})
        with pytest.raises(isolation.IsolationUnavailable):
            isolation.require_native_shared_memory_evidence(
                {k: v for k, v in value.items() if k != key}
            )
    with pytest.raises(isolation.IsolationUnavailable):
        isolation.require_native_shared_memory_evidence({**value, "source": "private-path"})


@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("probe", [False, True])
def test_guard_flag_controls_only_explicit_filesystem_extension(monkeypatch, capsys, native, probe):
    """Launcher parser unit test; all security calls are replaced, never executed."""
    calls = []

    def restrict(bind_ports, connect_ports, **kwargs):
        calls.append((bind_ports, connect_ports, kwargs.copy()))
        if kwargs["native_semaphore_storage"]:
            kwargs["evidence"]["native_shared_memory"] = dict(guard.NATIVE_SHM_EVIDENCE)
        return 6

    resources = []
    executed = []
    monkeypatch.setattr(guard, "restrict_tcp", restrict)
    monkeypatch.setattr(guard, "restrict_resources", lambda **kw: resources.append(kw))
    monkeypatch.setattr(guard, "restrict_sockets", lambda **kw: {"major": 2, "minor": 5})
    monkeypatch.setattr(guard, "daemon_denied", lambda: None)
    monkeypatch.setattr(guard.os, "execvpe", lambda *args: executed.append(args))
    command = ["--probe"] if probe else ["--", "/bin/true", "--native-shm"]
    monkeypatch.setattr(
        guard.sys,
        "argv",
        ["guard.py", "8123", "55433", *(["--native-shm"] if native else []), *command],
    )
    guard.main()
    assert len(calls) == 1
    assert calls[0][2]["native_semaphore_storage"] is native
    assert calls[0][2]["filesystem"] is (not probe or native)
    assert resources == [{"native": True}], "Preexisting limits must remain unchanged"
    if probe:
        import json

        receipt = json.loads(capsys.readouterr().out)
        assert ("native_shared_memory" in receipt) is native
        assert executed == []
    else:
        assert executed[0][:2] == ("/bin/true", ["/bin/true", "--native-shm"])


@pytest.mark.parametrize(
    "command",
    [
        ["--native-shm"],
        ["--native-shm", "--native-shm", "--probe"],
        ["--native-shm", "--"],
        ["--probe", "extra"],
    ],
)
def test_guard_rejects_malformed_flag_before_security_setup(monkeypatch, command):
    monkeypatch.setattr(guard.sys, "argv", ["guard.py", "8123", "55433", *command])
    monkeypatch.setattr(
        guard,
        "restrict_tcp",
        lambda *a, **k: pytest.fail("Malformed command reached security setup"),
    )
    with pytest.raises(RuntimeError, match="separator"):
        guard.main()


def native_container_receipt():
    return {
        "profile": "native-fastapiadmin-postgresql-v1",
        "sandbox_id": "00000000-0000-0000-0000-000000000001",
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
        "runner_image_id": "sha256:" + "0" * 64,
        "snapshot_image_id": "sha256:" + "1" * 64,
        "snapshot_digest": "registry:6000/rnd-native-fastapiadmin@sha256:" + "2" * 64,
        "shared_memory": {"ipc_mode": "private", "size_bytes": 67108864},
    }


@pytest.mark.parametrize(
    "shared_memory",
    [
        None,
        {},
        {"ipc_mode": "private"},
        {"size_bytes": 67108864},
        {"ipc_mode": "host", "size_bytes": 67108864},
        {"ipc_mode": "container:other", "size_bytes": 67108864},
        {"ipc_mode": "private", "size_bytes": True},
        {"ipc_mode": "private", "size_bytes": "67108864"},
        {"ipc_mode": "private", "size_bytes": 67108865},
        {"ipc_mode": "private", "size_bytes": 67108864, "extra": True},
    ],
)
def test_native_container_receipt_requires_private_bounded_shared_memory(shared_memory):
    valid = native_container_receipt()
    assert isolation.require_container_evidence(valid, valid["sandbox_id"]) == valid
    with pytest.raises(isolation.IsolationUnavailable):
        isolation.require_container_evidence(
            {**valid, "shared_memory": shared_memory}, valid["sandbox_id"]
        )


def test_isolation_evidence_binds_native_extension_to_selected_launch_profile():
    from workbench.filesystem import sha
    from workbench.settings import ROOT

    ordinary = {
        "profile": isolation.ISOLATION_PROFILE,
        "application_uid": isolation.APP_UID,
        "landlock_abi": 6,
        "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
        **dict.fromkeys(isolation.ISOLATION_FLAGS, True),
    }
    native = {**ordinary, "native_shared_memory": dict(isolation.NATIVE_SHARED_MEMORY_EVIDENCE)}
    assert isolation.require_isolation_evidence(ordinary) == ordinary
    assert isolation.require_isolation_evidence(native, native_semaphore_storage=True) == native
    with pytest.raises(isolation.IsolationUnavailable):
        isolation.require_isolation_evidence(ordinary, native_semaphore_storage=True)
    with pytest.raises(isolation.IsolationUnavailable):
        isolation.require_isolation_evidence(native)
````
