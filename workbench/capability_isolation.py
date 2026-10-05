"""Disposable Linux identity and control-channel separation for module commands.

No operation here targets the host OS. All commands go through the owned
Daytona sandbox's control channel, before untrusted source is executed.
"""

import json
import re
import shlex
import uuid

from workbench.capability_verification import CheckFailure
from workbench.filesystem import sha
from workbench.settings import ROOT

PRODUCT = "/tmp/rnd-capability/product"
CONTROL = "/tmp/rnd-module-control"
APP_USER = "rnd-module"
APP_UID = 20000
GUARD = CONTROL + "/guard.py"
SYSTEM_PATH = "/usr/sbin:/usr/bin:/sbin:/bin"
# The daemon starts an outer shell before it evaluates our inner env -i command.
# Apply these through the SDK's envs protocol so locale and user startup hooks
# cannot contaminate machine-readable command output before that inner boundary.
# Global shell startup files remain part of the pinned trusted image; unexpected
# output still fails the strict whole-output identity check below.
CONTROL_SHELL_ENV = {
    "LC_ALL": "C",
    "LANG": "C",
    "BASH_ENV": "/dev/null",
    "ENV": "/dev/null",
    "ZDOTDIR": "/nonexistent",
}
ISOLATION_PROFILE = "module-linux-landlock-v1"
NATIVE_SHARED_MEMORY_EVIDENCE = {
    "profile": "native-private-shm-v1",
    "actual_mount_verified": True,
    "regular_files_only": True,
    "size_bytes": 64 * 1024 * 1024,
    "noexec": True,
    "nosuid": True,
    "nodev": True,
    "uid": 0,
    "gid": 0,
    "mode": 0o1777,
}
ISOLATION_FLAGS = (
    "no_new_privs",
    "capabilities_cleared",
    "supplementary_groups_cleared",
    "privilege_transitions_disabled",
    "trusted_tools_readonly",
    "private_control_unreadable",
    "private_database_unreadable",
    "daemon_tcp_denied",
    "unix_scope_restricted",
    "inherited_fds_closed",
    "standard_streams_detached",
    "no_controlling_terminal",
    "socket_filter_enforced",
)


def require_native_shared_memory_evidence(value):
    expected = NATIVE_SHARED_MEMORY_EVIDENCE
    if (
        type(value) is not dict
        or value.keys() != expected.keys()
        or any(
            type(value[key]) is not type(wanted) or value[key] != wanted
            for key, wanted in expected.items()
        )
    ):
        raise IsolationUnavailable("缺少原生共享内存实际挂载和普通文件范围的完整隔离回执")
    return value


def require_isolation_evidence(value, *, native_semaphore_storage=False):
    if (
        not isinstance(value, dict)
        or value.get("profile") != ISOLATION_PROFILE
        or type(value.get("application_uid")) is not int
        or value["application_uid"] != APP_UID
        or type(value.get("landlock_abi")) is not int
        or value["landlock_abi"] < 6
        or value.get("guard_sha256") != sha(ROOT / "scripts/capability_guard.py")
        or any(value.get(flag) is not True for flag in ISOLATION_FLAGS)
    ):
        raise IsolationUnavailable("缺少准确版本、完整必需字段或当前守卫摘要的执行隔离回执")
    if native_semaphore_storage:
        require_native_shared_memory_evidence(value.get("native_shared_memory"))
    elif "native_shared_memory" in value:
        raise IsolationUnavailable("普通执行配置不能带有原生共享内存写权限回执")
    return value


class IsolationUnavailable(CheckFailure):
    def __init__(self, message, *, evidence=None):
        super().__init__(message)
        self.evidence = evidence or {}


class ContainerInspectionRejected(ValueError):
    """Trusted inspector rejection with bounded facts, never raw inspect output.

    Unknown exception text, Docker paths, environment and arbitrary network
    names are not diagnostic evidence. Revalidate on access as well as creation
    so callers cannot extend the receipt by mutating an exception's attributes.
    """

    _CATEGORIES = frozenset(
        {
            "sandbox_identity",
            "runner_unavailable",
            "runner_identity",
            "engine_seccomp",
            "container_identity",
            "sandbox_network",
            "runner_bridge",
            "container_policy",
            "tmpfs_mounts",
            "binary_mounts",
            "resource_limits",
            "shared_memory",
        }
    )
    _NUMBERS = frozenset(
        {
            "memory",
            "memory_swap",
            "cpu_period",
            "cpu_quota",
            "pids_limit",
            "network_count",
            "bridge_count",
            "mount_count",
        }
    )
    _FLAGS = frozenset(
        {
            "native_resources",
            "tmpfs_keys_match",
            "tmpfs_options_match",
            "runner_bridge_attached",
            "bridge_ipv6_disabled",
            "bridge_driver_matches",
            "bridge_subnets_match",
            "mount_types_match",
            "mount_destinations_match",
            "mount_sources_match",
            "mount_readonly_matches",
            "mount_writable_matches",
            "shared_memory_ipc_private",
            "shared_memory_size_match",
        }
    )
    _NETWORK_MODES = frozenset({"", "default", "bridge", "runner-bridge", "host", "none"})

    def __init__(self, message, *, category, facts=None):
        super().__init__(message)
        self._category = category
        self._facts = facts if type(facts) is dict else {}
        self._facts = ContainerInspectionRejected.diagnostic(self)

    def diagnostic(self):
        schema = ContainerInspectionRejected
        if type(self._category) is not str or self._category not in schema._CATEGORIES:
            return {}
        evidence = {"container_rejection": self._category}
        facts = self._facts if type(self._facts) is dict else {}
        for key in schema._NUMBERS | schema._FLAGS | {"network_mode"}:
            if key not in facts:
                continue
            value = facts[key]
            if key in schema._NUMBERS:
                value = value if type(value) is int and -(2**63) <= value < 2**63 else None
            elif key in schema._FLAGS:
                value = value if type(value) is bool else None
            else:
                value = value if type(value) is str and value in schema._NETWORK_MODES else "other"
            evidence[key] = value
        return evidence


def require_container_evidence(value, sandbox_id):
    profiles = {
        "fixed-authored-sqlite-v1": "rnd-python",
        "native-fastapiadmin-postgresql-v1": "rnd-native-fastapiadmin",
    }
    if (
        not isinstance(value, dict)
        or not isinstance(sandbox_id, str)
        or not re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", sandbox_id
        )
        or not isinstance(value.get("profile"), str)
        or value.get("profile") not in profiles
        or value.get("sandbox_id") != sandbox_id
        or value.get("control_user") != "0:0"
        or value.get("privileged") is not False
        or value.get("seccomp") != "docker-default"
        or value.get("seccomp_engine") != "builtin"
        or value.get("trusted_readonly_binary_mounts") is not True
        or any(
            not re.fullmatch(r"sha256:[a-f0-9]{64}", str(value.get(key, "")))
            for key in ("runner_image_id", "snapshot_image_id")
        )
        or not re.fullmatch(
            rf"registry:6000/{profiles.get(value.get('profile'), 'invalid')}@sha256:[a-f0-9]{{64}}",
            str(value.get("snapshot_digest", "")),
        )
    ):
        raise IsolationUnavailable("缺少当前独占容器的真实非特权/镜像/挂载检查回执")
    if value["profile"] == "native-fastapiadmin-postgresql-v1":
        shared = value.get("shared_memory")
        if (
            type(shared) is not dict
            or set(shared) != {"ipc_mode", "size_bytes"}
            or type(shared.get("ipc_mode")) is not str
            or shared["ipc_mode"] != "private"
            or type(shared.get("size_bytes")) is not int
            or shared["size_bytes"] != 64 * 1024 * 1024
        ):
            raise IsolationUnavailable("原生容器缺少私有64 MiB共享内存的独立检查回执")
    return value


def system_argv(argv):
    return ["/usr/bin/env", "-i", "PATH=" + SYSTEM_PATH, "LANG=C.UTF-8", "HOME=/nonexistent", *argv]


def control_exec(sandbox, argv, timeout):
    return sandbox.process.exec(
        shlex.join(system_argv(argv)), env=dict(CONTROL_SHELL_ENV), timeout=timeout
    )


def product_argv(plan, argv, database, *, native_semaphore_storage=False):
    # This keyword is supplied by the trusted container-admission path. Source
    # plans, environment variables and a connection to 55433 cannot opt in.
    if (
        type(native_semaphore_storage) is not bool
        or native_semaphore_storage
        and (
            getattr(plan.selection, "template", "") != "fastapiadmin"
            or plan.selection.database != "postgresql"
        )
    ):
        raise IsolationUnavailable("共享内存写权限仅用于独立核实的原生PostgreSQL执行配置")
    ports = {plan.runtime.port}
    if ports & {2280, 55432, 55433}:
        raise IsolationUnavailable("产品端口与控制/数据库保留端口冲突")
    connect = "55432" if plan.selection.database == "postgresql" else ""
    if getattr(plan.selection, "template", "") == "fastapiadmin":
        if plan.runtime.port == 5173:
            raise IsolationUnavailable("原生后端端口不能占用独立前端端口")
        ports.add(5173)
        connect = ",".join(str(value) for value in sorted({plan.runtime.port, 55432, 55433}))
    environment = {
        "HOME": "/tmp/rnd-capability/home",
        "PATH": "/opt/java/openjdk/bin:/usr/local/bin:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": "/tmp/rnd-capability/cache",
        "TMPDIR": "/tmp/rnd-capability/tmp",
        "UV_PYTHON_INSTALL_DIR": "/opt/rnd/python",
        "UV_OFFLINE": "1",
        "UV_NO_PROGRESS": "1",
        "UV_LINK_MODE": "copy",
        "COREPACK_ENABLE_NETWORK": "0",
        **database,
    }
    template = getattr(plan.selection, "template", "")
    if template in {"python-basic", "fastapiadmin"}:
        python_root = "/opt/rnd/runtime/" + (
            "fastapiadmin/backend/.venv" if template == "fastapiadmin" else "python-basic/.venv"
        )
        environment["VIRTUAL_ENV"] = python_root
        environment["PATH"] = python_root + "/bin:" + environment["PATH"]
        if template == "fastapiadmin":
            environment["PATH"] = (
                "/opt/rnd/runtime/fastapiadmin/frontend/node_modules/.bin:" + environment["PATH"]
            )
    return system_argv(
        [
            "/usr/bin/setsid",
            "--fork",
            "--wait",
            "/usr/bin/setpriv",
            "--reuid=" + APP_USER,
            "--regid=" + APP_USER,
            "--clear-groups",
            "--no-new-privs",
            "--bounding-set=-all",
            "--inh-caps=-all",
            "--ambient-caps=-all",
            "--",
            "/usr/bin/python3",
            "-I",
            "-S",
            GUARD,
            ",".join(str(value) for value in sorted(ports)),
            connect,
            *(["--native-shm"] if native_semaphore_storage else []),
            "--",
            "/usr/bin/env",
            "-i",
            *(key + "=" + value for key, value in environment.items()),
            *argv,
        ]
    )


def redirected_command(argv):
    """Dedicated data-only stdio; never share a privileged control terminal."""
    output = CONTROL + "/private/" + uuid.uuid4().hex + ".log"
    command = "exec " + shlex.join(argv) + " </dev/null >" + shlex.quote(output) + " 2>&1"
    return ["/bin/sh", "-c", command], output


def read_command_output(sandbox, path, timeout, limit=8000, *, tail=False):
    if not path.startswith(CONTROL + "/private/") or "/" in path.removeprefix(
        CONTROL + "/private/"
    ):
        raise IsolationUnavailable("执行输出路径不属于独立控制目录")
    if type(tail) is not bool or (tail and (type(limit) is not int or not 1 <= limit <= 8000)):
        raise IsolationUnavailable("启动失败输出尾部必须限制在 8000 字节以内")
    reader = "/usr/bin/tail" if tail else "/usr/bin/head"
    result = control_exec(sandbox, [reader, "-c", str(limit), path], timeout)
    if result.exit_code != 0:
        raise IsolationUnavailable("无法读取独立命令回执")
    return result.result or ""


def run_guarded_control(sandbox, argv, timeout):
    command, output = redirected_command(argv)
    result = control_exec(sandbox, command, timeout)
    return result.exit_code, read_command_output(sandbox, output, timeout)


PROBE = r"""
import json,os,pathlib,stat,sys
status=dict(line.split(':',1) for line in pathlib.Path('/proc/self/status').read_text().splitlines())
assert os.getuid()==20000 and os.geteuid()==20000
assert not os.getgroups() and status['NoNewPrivs'].strip()=='1'
assert pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[4]=='0'
assert all(int(status[name].strip(),16)==0 for name in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
for raw in sys.argv[1:]:
    path=pathlib.Path(raw).resolve()
    assert path.exists() and not os.access(path,os.W_OK)
    while str(path) != '/':
        parent=path.parent
        if os.access(parent,os.W_OK):
            assert parent.stat().st_mode & stat.S_ISVTX and path.stat().st_uid != os.getuid()
        path=parent
assert not os.access('/tmp/rnd-module-control/private',os.R_OK)
assert not os.access('/tmp/rnd-postgres',os.R_OK)
# A filesystem Unix control socket accessible to this UID is not an accepted profile.
for line in pathlib.Path('/proc/net/unix').read_text().splitlines()[1:]:
    fields=line.split()
    if len(fields)>7 and fields[7].startswith('/'):
        p=pathlib.Path(fields[7])
        if p.exists() and p.stat().st_uid != os.getuid():
            assert not os.access(p,os.W_OK)
print(json.dumps({'application_uid':os.getuid(),'no_new_privs':True,'capabilities_cleared':True,'supplementary_groups_cleared':True,'privilege_transitions_disabled':True,'trusted_tools_readonly':True,'private_control_unreadable':True,'private_database_unreadable':True,'daemon_tcp_denied':True,'unix_scope_restricted':True,'no_controlling_terminal':True}))
"""


def prepare_identity(sandbox, plan, timeout, *, native_semaphore_storage=False):
    root = control_exec(sandbox, ["/usr/bin/id", "-u"], timeout)
    output = root.result.strip() if isinstance(root.result, str) else ""
    control_uid = int(output) if re.fullmatch(r"[0-9]{1,10}", output) else None
    identity_check = {
        "control_exec_exit_code": root.exit_code if type(root.exit_code) is int else None,
        "control_euid": control_uid,
        "control_result_type": "string"
        if isinstance(root.result, str)
        else "null"
        if root.result is None
        else "other",
        "control_result_chars": len(root.result) if isinstance(root.result, str) else None,
        "control_output_shape": "decimal"
        if control_uid is not None
        else "empty"
        if not output
        else "locale-warning"
        if "setlocale" in output.lower()
        else "other",
    }
    if type(root.exit_code) is not int or root.exit_code != 0 or control_uid != 0:
        raise IsolationUnavailable("缺少受控隔离身份，未执行生成源码", evidence=identity_check)
    commands = [
        ["/usr/sbin/groupadd", "--gid", str(APP_UID), APP_USER],
        [
            "/usr/sbin/useradd",
            "--uid",
            str(APP_UID),
            "--gid",
            APP_USER,
            "--create-home",
            "--shell",
            "/usr/sbin/nologin",
            APP_USER,
        ],
        ["/usr/bin/mkdir", "-p", CONTROL + "/private", "/tmp/rnd-postgres"],
        ["/usr/bin/chmod", "700", CONTROL + "/private", "/tmp/rnd-postgres"],
        ["/usr/bin/chmod", "755", CONTROL],
        ["/usr/bin/chmod", "711", "/tmp/rnd-capability"],
        [
            "/usr/bin/mkdir",
            "-p",
            "/tmp/rnd-capability/home",
            "/tmp/rnd-capability/tmp",
            "/tmp/rnd-capability/cache",
        ],
    ]
    for argv in commands:
        if control_exec(sandbox, argv, timeout).exit_code != 0:
            raise IsolationUnavailable("隔离环境无法建立专用无权限执行身份，未执行生成源码")
    # Never recursively chown through candidate links, including during initial
    # identity setup. Preflight the entire extracted tree before any mutation.
    ownership = r"""
import os,pathlib,stat
roots=[pathlib.Path('/tmp/rnd-capability')/name for name in ('product','home','tmp','cache')]
entries=[]
for root in roots:
 assert root.is_dir() and not root.is_symlink()
 entries.append(root)
 for directory,dirs,names in os.walk(root,followlinks=False):
  for name in [*dirs,*names]:
   p=pathlib.Path(directory)/name;entry=p.lstat()
   assert not stat.S_ISLNK(entry.st_mode)
   assert stat.S_ISDIR(entry.st_mode) or (stat.S_ISREG(entry.st_mode) and entry.st_nlink==1)
   entries.append(p)
for path in entries:os.chown(path,20000,20000,follow_symlinks=False)
"""
    if control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", ownership], timeout).exit_code:
        raise IsolationUnavailable("隔离源码包含链接或特殊文件，未执行生成源码")
    sandbox.fs.upload_file(
        (ROOT / "scripts/capability_guard.py").read_bytes(), GUARD, timeout=timeout
    )
    if control_exec(sandbox, ["/usr/bin/chmod", "644", GUARD], timeout).exit_code:
        raise IsolationUnavailable("可信执行守卫无法设为只读")
    trusted = [
        "/usr/bin/python3",
        "/usr/bin/env",
        "/usr/bin/setpriv",
        "/usr/bin/setsid",
        "/usr/bin/head",
        "/bin/sh",
        GUARD,
    ]
    # Include the system interpreter's complete stdlib search roots, without site hooks.
    result = control_exec(
        sandbox,
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            "import json,sys;print(json.dumps([p for p in sys.path if p]))",
        ],
        timeout,
    )
    try:
        trusted.extend(path for path in json.loads(result.result) if not path.endswith(".zip"))
    except ValueError, TypeError:
        raise IsolationUnavailable("系统解释器环境无法核实") from None
    if plan.selection.database == "postgresql":
        trusted.extend(["/usr/lib/postgresql/17/bin/psql", "/usr/lib/postgresql/17/bin/postgres"])
    guarded = product_argv(plan, [], {}, native_semaphore_storage=native_semaphore_storage)
    probe_argv = guarded[: guarded.index(GUARD) + 3 + int(native_semaphore_storage)] + ["--probe"]
    probe_status, probe_output = run_guarded_control(sandbox, probe_argv, timeout)
    try:
        guard_receipt = json.loads(probe_output)
    except ValueError, TypeError:
        raise IsolationUnavailable("内核守卫未返回完整回执；未执行生成源码") from None
    if (
        probe_status != 0
        or type(guard_receipt.get("landlock_abi")) is not int
        or guard_receipt["landlock_abi"] < 6
    ):
        raise IsolationUnavailable("内核缺少所需Landlock ABI6隔离，未执行生成源码")
    identity_status, identity_output = run_guarded_control(
        sandbox,
        product_argv(
            plan,
            ["/usr/bin/python3", "-I", "-S", "-c", PROBE, *trusted],
            {},
            native_semaphore_storage=native_semaphore_storage,
        ),
        timeout,
    )
    if identity_status != 0:
        raise IsolationUnavailable(
            "生成程序身份/内核守卫/控制端口/可信工具隔离未通过，未执行生成源码"
        )
    try:
        receipt = json.loads(identity_output)
    except ValueError, TypeError:
        raise IsolationUnavailable("执行隔离缺少可信运行回执") from None
    return require_isolation_evidence(
        {
            **guard_receipt,
            **receipt,
            "profile": ISOLATION_PROFILE,
            "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
            **identity_check,
        },
        native_semaphore_storage=native_semaphore_storage,
    )
