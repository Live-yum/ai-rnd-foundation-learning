# scripts/capability_security_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_security_probe；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_execution`、`workbench.capability_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run_security_probe`（L90–L120）：接收`sandbox`、`plan`、`timeout`、`container_evidence`、`environment`。 控制顺序：L91按`not container_evidence.get("resource_limits")`分支；L92抛异常，停止当前正常路径；L94遍历`(CONTROL + "/private/security-sentinel", "/tmp/rnd-postgres/secur…`；L96按`result.exit_code != 0`分支；L97抛异常，停止当前正常路径；L108抛异常，停止当前正常路径；L110按`plan.selection.template == "fastapiadmin"`分支；L112按`result != 0 or not isinstance(checks, dict) or set(checks) != expected or any(value i…`分支。后续分支沿下方源码相同行号继续阅读。 调用`container_evidence.get`、`IsolationUnavailable`、`control_exec`、`run_guarded_control`、`product_argv`、`json.loads`、`set`、`expected.remove`、`isinstance`等。 返回路径：L120的`checks`。
- `security_probe_for_profile`（L123–L136）：接收`directory`、`record`。 返回路径：L136的`probe`。
- `security_probe_for_profile.probe`（L124–L134）：接收`sandbox`、`plan`、`timeout`、`container_evidence`、`environment`。 控制顺序：L126按`plan.selection.template == "fastapiadmin"`分支。 调用`run_security_probe`、`checks.update`、`verify_native_services`、`verify_native_planner_identity`、`verify_native_egress`。 返回路径：L134的`checks`。

</details>

**创建路径：** `scripts/capability_security_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L136。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6945`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_security_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5e43c3ac23bb76dd0e97dff5853d24fa0529ba7c15070a2c2e49f8cf9abad641"} -->
````python
# scripts/capability_security_probe.py
"""Bounded adversarial checks in the *real* disposable product identity.

No host execution fallback. Checks attempt denied operations and keep ordinary
product writes functional. Only booleans return; no private bytes are printed.
"""

import json

from workbench.capability_execution import SECURITY_CHECKS
from workbench.capability_isolation import (
    CONTROL,
    IsolationUnavailable,
    control_exec,
    product_argv,
    run_guarded_control,
)

PROBE = r"""
import ctypes,errno,json,os,pathlib,resource,socket,sys
native=sys.argv[1]=='fastapiadmin'
checks={}
def denied(name, operation):
    try:
        result=operation()
        if hasattr(result,'close'): result.close()
    except OSError as exc:
        assert exc.errno in (errno.EACCES,errno.EPERM), name
        checks[name]=True
        return
    raise AssertionError(name)
denied('private_control_read_denied',lambda:open('/tmp/rnd-module-control/private/security-sentinel','rb'))
denied('private_control_write_denied',lambda:open('/tmp/rnd-module-control/private/forged-receipt','wb'))
denied('private_database_read_denied',lambda:open('/tmp/rnd-postgres/security-sentinel','rb'))
denied('guard_write_denied',lambda:open('/tmp/rnd-module-control/guard.py','ab'))
denied('trusted_interpreter_write_denied',lambda:open('/usr/bin/python3','ab'))
for label,port in [('control_tcp_denied',2280),('undeclared_tcp_denied',2281)]:
    def connect():
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.settimeout(1);s.connect(('127.0.0.1',port))
    denied(label,connect)
denied('raw_socket_denied',lambda:socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP))
for family in (socket.AF_INET,socket.AF_INET6,socket.AF_PACKET):
 for kind in (socket.SOCK_DGRAM,socket.SOCK_RAW):
  for flags in (0,socket.SOCK_NONBLOCK,socket.SOCK_CLOEXEC,socket.SOCK_NONBLOCK|socket.SOCK_CLOEXEC):
   denied('socket_types_denied',lambda:socket.socket(family,kind|flags))
for kind in (socket.SOCK_DGRAM,socket.SOCK_SEQPACKET):
 for flags in (0,socket.SOCK_NONBLOCK|socket.SOCK_CLOEXEC):
  denied('socketpair_types_denied',lambda:socket.socketpair(socket.AF_UNIX,kind|flags))
for family,addresses in (() if native else ((socket.AF_INET,('127.0.0.1','192.0.2.1')),(socket.AF_INET6,('::1','2001:db8::1')))):
 for address in addresses:
  def forbidden_connect():
   with socket.socket(family,socket.SOCK_STREAM) as s:
    s.settimeout(1);s.connect((address,8123))
  denied('all_tcp_destinations_denied',forbidden_connect)
a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
a.send(b'probe');assert b.recv(5)==b'probe';a.close();b.close()
checks['unix_stream_pair_allowed']=True
libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
assert libc.syscall(425,0,0)==-1 and ctypes.get_errno()==errno.EPERM
checks['io_uring_denied']=True
denied('root_signal_denied',lambda:os.kill(1,0))
denied('privilege_transition_denied',lambda:os.setuid(0))
# The home is owned by the application, so this denial proves Landlock, rather
# than ordinary Unix ownership, keeps writes off the bounded tmpfs.
denied('filesystem_write_scope',lambda:open('/home/rnd-module/outside-tmpfs','wb'))
denied('proc_symlink_write_denied',lambda:open('/proc/self/root/home/rnd-module/outside-tmpfs','wb'))
mounts=[line.split() for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()]
matching=[row for row in mounts if row[4]=='/tmp' and row[row.index('-')+1]=='tmpfs']
assert len(matching)==1
fs=os.statvfs('/tmp');assert 0 < fs.f_blocks*fs.f_frsize <= (4294967296 if native else 1073741824)
checks['tmpfs_storage_bound']=True
cgroup=pathlib.Path('/sys/fs/cgroup')
assert 0 < int((cgroup/'memory.max').read_text()) <= (6 if native else 2)*1024**3
assert 0 < int((cgroup/'pids.max').read_text()) <= (384 if native else 256)
quota,period=(cgroup/'cpu.max').read_text().split();assert 0 < int(quota) <= int(period)*(2 if native else 1)
checks['kernel_cgroup_limits']=True
expected={'RLIMIT_CPU':300,'RLIMIT_FSIZE':32*1024*1024,'RLIMIT_NPROC':128,'RLIMIT_NOFILE':256,'RLIMIT_CORE':0}
if native:expected.update(RLIMIT_CPU=900,RLIMIT_FSIZE=128*1024*1024,RLIMIT_NPROC=256)
for name,ceiling in expected.items():
    soft,hard=resource.getrlimit(getattr(resource,name))
    assert 0 <= soft <= hard <= ceiling,(name,soft,hard)
checks['resource_limits_enforced']=True
p=pathlib.Path('/tmp/rnd-capability/tmp/security-writable')
p.write_text('bounded synthetic probe');assert p.read_text()=='bounded synthetic probe';p.unlink()
checks['ordinary_product_write_allowed']=True
print(json.dumps(checks,sort_keys=True))
"""


def run_security_probe(sandbox, plan, timeout, container_evidence, environment=None):
    if not container_evidence.get("resource_limits"):
        raise IsolationUnavailable("缺少实际CPU/内存/磁盘资源上限，未执行生成源码")
    # Created by the trusted controller under private root-owned directories.
    for path in (CONTROL + "/private/security-sentinel", "/tmp/rnd-postgres/security-sentinel"):
        result = control_exec(sandbox, ["/usr/bin/touch", path], timeout)
        if result.exit_code != 0:
            raise IsolationUnavailable("安全反例的私有哨兵创建失败")
    result, output = run_guarded_control(
        sandbox,
        product_argv(
            plan, ["/usr/bin/python3", "-I", "-S", "-c", PROBE, plan.selection.template], {}
        ),
        timeout,
    )
    try:
        checks = json.loads(output)
    except ValueError, TypeError:
        raise IsolationUnavailable("真实隔离安全反例没有有效回执") from None
    expected = set(SECURITY_CHECKS) - {"container_resource_limits"}
    if plan.selection.template == "fastapiadmin":
        expected.remove("all_tcp_destinations_denied")
    if (
        result != 0
        or not isinstance(checks, dict)
        or set(checks) != expected
        or any(value is not True for value in checks.values())
    ):
        raise IsolationUnavailable("真实隔离安全反例未全部通过，未执行生成源码")
    checks["container_resource_limits"] = True
    return checks


def security_probe_for_profile(directory, record):
    def probe(sandbox, plan, timeout, container_evidence, environment=None):
        checks = run_security_probe(sandbox, plan, timeout, container_evidence, environment)
        if plan.selection.template == "fastapiadmin":
            from scripts.capability_native_egress import verify_native_egress
            from scripts.capability_native_planner_probe import verify_native_planner_identity
            from workbench.capability_services import verify_native_services

            checks.update(verify_native_services(sandbox, plan, environment, timeout))
            checks.update(verify_native_planner_identity(sandbox, plan, environment, timeout))
            checks.update(verify_native_egress(directory, record, sandbox, plan, timeout))
        return checks

    return probe
````
