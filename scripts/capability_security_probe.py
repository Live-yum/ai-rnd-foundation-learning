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
fs=os.statvfs('/tmp');assert fs.f_flag & os.ST_NOEXEC
checks['tmpfs_noexec_enforced']=True
assert 0 < fs.f_blocks*fs.f_frsize <= (4294967296 if native else 1073741824)
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
manifest=pathlib.Path('/opt/rnd/runtime/dependency-manifest.json')
assert manifest.is_file() and not manifest.is_symlink()
with manifest.open('rb') as stream:assert stream.read(1)
roots=[pathlib.Path('/opt/rnd/runtime/fastapiadmin/backend/.venv' if native else '/opt/rnd/runtime/python-basic/.venv')]
if native:roots.append(pathlib.Path('/opt/rnd/runtime/fastapiadmin/frontend/node_modules'))
for root in roots:
 assert root.is_dir() and not root.is_symlink()
 assert os.access(root,os.R_OK|os.X_OK) and not os.access(root,os.W_OK)
 # No bytes of application or private data leave this product-identity probe.
 assert next(root.iterdir(),None) is not None
 denied('immutable_dependency_write_denied',lambda:open(root/'security-forbidden-write','wb'))
 denied('immutable_dependency_write_denied',lambda:open('/proc/self/root'+str(root/'security-forbidden-write'),'wb'))
denied('immutable_dependency_write_denied',lambda:open(manifest,'ab'))
checks['immutable_dependency_read_allowed']=True
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
