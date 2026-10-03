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
ISOLATION_PROFILE = "module-linux-landlock-v1"
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
)


def require_isolation_evidence(value):
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
    return value


class IsolationUnavailable(CheckFailure):
    def __init__(self, message, *, evidence=None):
        super().__init__(message)
        self.evidence = evidence or {}


def require_container_evidence(value, sandbox_id):
    if (
        not isinstance(value, dict)
        or not isinstance(sandbox_id, str)
        or not re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", sandbox_id
        )
        or value.get("profile") != "fixed-authored-sqlite-v1"
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
            r"registry:6000/rnd-python@sha256:[a-f0-9]{64}", str(value.get("snapshot_digest", ""))
        )
    ):
        raise IsolationUnavailable("缺少当前独占容器的真实非特权/镜像/挂载检查回执")
    return value


def system_argv(argv):
    return ["/usr/bin/env", "-i", "PATH=" + SYSTEM_PATH, "LANG=C.UTF-8", "HOME=/nonexistent", *argv]


def control_exec(sandbox, argv, timeout):
    return sandbox.process.exec(shlex.join(system_argv(argv)), timeout=timeout)


def product_argv(plan, argv, database):
    ports = {plan.runtime.port}
    if ports & {2280, 55432}:
        raise IsolationUnavailable("产品端口与控制/数据库保留端口冲突")
    connect = "55432" if plan.selection.database == "postgresql" else ""
    environment = {
        "HOME": "/home/" + APP_USER,
        "PATH": "/opt/java/openjdk/bin:/usr/local/bin:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONUTF8": "1",
        "UV_CACHE_DIR": "/opt/rnd/uv-cache",
        "UV_PYTHON_INSTALL_DIR": "/opt/rnd/python",
        "UV_OFFLINE": "1",
        "UV_NO_PROGRESS": "1",
        "UV_LINK_MODE": "copy",
        "COREPACK_ENABLE_NETWORK": "0",
        **database,
    }
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
            str(plan.runtime.port),
            connect,
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


def read_command_output(sandbox, path, timeout, limit=8000):
    if not path.startswith(CONTROL + "/private/") or "/" in path.removeprefix(
        CONTROL + "/private/"
    ):
        raise IsolationUnavailable("执行输出路径不属于独立控制目录")
    result = control_exec(sandbox, ["/usr/bin/head", "-c", str(limit), path], timeout)
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


def prepare_identity(sandbox, plan, timeout):
    root = control_exec(sandbox, ["/usr/bin/id", "-u"], timeout)
    output = root.result.strip() if isinstance(root.result, str) else ""
    control_uid = int(output) if re.fullmatch(r"[0-9]{1,10}", output) else None
    identity_check = {
        "control_exec_exit_code": root.exit_code if type(root.exit_code) is int else None,
        "control_euid": control_uid,
    }
    if root.exit_code != 0 or control_uid != 0:
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
        ["/usr/bin/chown", "-R", APP_USER + ":" + APP_USER, PRODUCT, "/opt/rnd/uv-cache"],
    ]
    for argv in commands:
        if control_exec(sandbox, argv, timeout).exit_code != 0:
            raise IsolationUnavailable("隔离环境无法建立专用无权限执行身份，未执行生成源码")
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
    guarded = product_argv(plan, [], {})
    probe_argv = guarded[: guarded.index(GUARD) + 3] + ["--probe"]
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
        product_argv(plan, ["/usr/bin/python3", "-I", "-S", "-c", PROBE, *trusted], {}),
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
        }
    )
