# workbench/capability_isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_verification`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `require_isolation_evidence`（L51–L63）：接收`value`。 控制顺序：L52按`not isinstance(value, dict) or value.get("profile") != ISOLATION_PROFILE or type(valu…`分支；L62抛异常，停止当前正常路径。 调用`isinstance`、`value.get`、`type`、`sha`、`any`、`IsolationUnavailable`。 返回路径：L63的`value`。
- `IsolationUnavailable`（L66–L69）：继承`CheckFailure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `IsolationUnavailable.__init__`（L67–L69）：接收`message`、`evidence`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_container_evidence`（L72–L95）：接收`value`、`sandbox_id`。 控制顺序：L73按`not isinstance(value, dict) or not isinstance(sandbox_id, str) or not re.fullmatch( r…`分支；L94抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`value.get`、`any`、`str`、`IsolationUnavailable`。 返回路径：L95的`value`。
- `system_argv`（L98–L99）：接收`argv`。 返回路径：L99的`["/usr/bin/env", "-i", "PATH=" + SYSTEM_PATH, "LANG=C.UTF-8", "HOME=/nonexistent", *argv]`。
- `control_exec`（L102–L105）：接收`sandbox`、`argv`、`timeout`。 调用`sandbox.process.exec`、`shlex.join`、`system_argv`、`dict`。 返回路径：L103的`sandbox.process.exec( shlex.join(system_argv(argv)), env=dict(CONTROL_SHELL_ENV), timeout=…`。
- `product_argv`（L108–L152）：接收`plan`、`argv`、`database`。 控制顺序：L110按`ports & {2280, 55432}`分支；L111抛异常，停止当前正常路径。 调用`IsolationUnavailable`、`system_argv`、`str`、`environment.items`。 返回路径：L126的`system_argv( [ "/usr/bin/setsid", "--fork", "--wait", "/usr/bin/setpriv", "--reuid=" + APP…`。
- `redirected_command`（L155–L159）：接收`argv`。 源码说明：Dedicated data-only stdio; never share a privileged control terminal.。 调用`uuid.uuid4`、`shlex.join`、`shlex.quote`。 返回路径：L159的`["/bin/sh", "-c", command], output`。
- `read_command_output`（L162–L170）：接收`sandbox`、`path`、`timeout`、`limit`。 控制顺序：L163按`not path.startswith(CONTROL + "/private/") or "/" in path.removeprefix( CONTROL + "/p…`分支；L166抛异常，停止当前正常路径；L168按`result.exit_code != 0`分支；L169抛异常，停止当前正常路径。 调用`path.startswith`、`path.removeprefix`、`IsolationUnavailable`、`control_exec`、`str`。 返回路径：L170的`result.result or ""`。
- `run_guarded_control`（L173–L176）：接收`sandbox`、`argv`、`timeout`。 调用`redirected_command`、`control_exec`、`read_command_output`。 返回路径：L176的`result.exit_code, read_command_output(sandbox, output, timeout)`。
- `prepare_identity`（L207–L318）：接收`sandbox`、`plan`、`timeout`。 控制顺序：L228按`type(root.exit_code) is not int or root.exit_code != 0 or control_uid != 0`分支；L229抛异常，停止当前正常路径；L249遍历`commands`；L250按`control_exec(sandbox, argv, timeout).exit_code != 0`分支；L251抛异常，停止当前正常路径；L255按`control_exec(sandbox, ["/usr/bin/chmod", "644", GUARD], timeout).exit_code`分支；L256抛异常，停止当前正常路径；L281抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`control_exec`、`isinstance`、`root.result.strip`、`re.fullmatch`、`int`、`type`、`len`、`output.lower`、`IsolationUnavailable`等。 返回路径：L310的`require_isolation_evidence( { **guard_receipt, **receipt, "profile": ISOLATION_PROFILE, "g…`。

</details>

**创建路径：** `workbench/capability_isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L318。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12382`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "707f2c1edae2fe13bfef78be265a4559006c5a45fc192903a774f20ae56c1379"} -->
````python
# workbench/capability_isolation.py
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
    return sandbox.process.exec(
        shlex.join(system_argv(argv)), env=dict(CONTROL_SHELL_ENV), timeout=timeout
    )


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
````
