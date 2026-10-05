"""Bounded live evidence for the approved disposable native shared-memory root.

Commands run only through the real product guard. The low-level pair probe
receives two inspected, owned SDK sandboxes. The peer lifecycle creates and
deletes one same-profile SDK sandbox, then confirms physical removal. Neither
changes mounts or grants new resource limits. Only fixed booleans, finite
failure stages and validated owned cleanup identifiers leave the probes.
"""

import json
import re
import time
import uuid

from scripts import daytona_local as local
from scripts.daytona_capability_profile import (
    compose,
    inspect_created_sandbox,
    require_execution_resources,
)
from workbench.capability_execution import require_profile_container_binding
from workbench.capability_isolation import (
    PRODUCT,
    prepare_identity,
    product_argv,
    require_container_evidence,
    require_native_shared_memory_evidence,
    run_guarded_control,
)
from workbench.capability_verification import CheckFailure
from workbench.sandbox import params_for, snapshot_for

RUNTIME_CHECKS = (
    "native_shm_64mib_enforced",
    "native_shm_ordinary_files_allowed",
    "native_shm_spawn_pool_completed",
    "native_shm_spawn_pool_cleanup",
    "native_shm_noexec_enforced",
    "native_shm_forbidden_objects_denied",
    "native_shm_outside_writes_denied",
    "native_shm_probe_cleanup",
)
PAIR_CHECKS = (
    "native_shm_cross_container_invisible",
    "native_shm_cross_container_cleanup",
)
COMPLETE = "native-shm-probe-command-complete"
UUID_PATTERN = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
PRIMARY_STAGES = frozenset({"none", "create", "inspect", "prepare", "pair"})
CLEANUP_STAGES = frozenset({"recover", "identity", "delete", "physical-absence"})
FAILURE_STAGES = frozenset(
    {
        "initial",
        "ordinary",
        "pool",
        "pool-cleanup",
        "capacity",
        "noexec",
        "objects",
        "outside",
        "cleanup",
    }
)

PROBE = r"""
import concurrent.futures,errno,gc,json,multiprocessing,os,re,socket,stat,subprocess,sys
from multiprocessing import resource_tracker
SHM='/dev/shm'
LIMIT=64*1024*1024
phase='initial'
checks={}
baseline=None
paths=[]
pool=None
failed=None
def denied(operation):
 try:
  value=operation()
  if hasattr(value,'close'):value.close()
 except OSError as exc:
  assert exc.errno in (errno.EACCES,errno.EPERM)
  return
 raise AssertionError
def create(path,data=b''):
 fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_RDWR|os.O_NOFOLLOW,0o600)
 try:
  if data:assert os.write(fd,data)==len(data)
 finally:os.close(fd)
def cleanup():
 # Remove only the random names checked absent before this attempt.
 for path in paths:
  try:
   mode=os.lstat(path).st_mode
   if stat.S_ISDIR(mode):os.rmdir(path)
   else:os.unlink(path)
  except FileNotFoundError:pass
 assert all(not os.path.lexists(path) for path in paths)
 assert baseline is None or set(os.listdir(SHM))==baseline
def unix_socket(path):
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stream:stream.bind(path)
def execute_file(path):
 child=subprocess.Popen([path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:child.communicate(timeout=2)
 finally:
  if child.poll() is None:child.kill();child.communicate(timeout=1)
def stop_pool():
 global pool
 if pool is not None:
  # Only children of this single authored probe process are eligible.
  for child in multiprocessing.active_children():
   child.terminate();child.join(timeout=1)
   if child.is_alive():child.kill();child.join(timeout=1)
  pool.shutdown(wait=True,cancel_futures=True)
  pool=None
 gc.collect()
 resource_tracker._resource_tracker._stop()
 assert not multiprocessing.active_children()
 assert resource_tracker._resource_tracker._pid is None
try:
 nonce=sys.argv[1]
 assert re.fullmatch('[a-f0-9]{32}',nonce)
 assert os.getuid()==20000 and os.geteuid()==20000
 baseline=set(os.listdir(SHM))
 names=['ordinary','linked','renamed','capacity','exec','directory','symlink','device','block','fifo','socket']
 targets={name:SHM+'/rnd-shm-'+nonce+'-'+name for name in names}
 assert all(not os.path.lexists(path) for path in targets.values())
 paths=list(targets.values())
 fs=os.statvfs(SHM)
 assert fs.f_blocks*fs.f_frsize==LIMIT
 assert fs.f_flag & os.ST_NOEXEC and fs.f_flag & os.ST_NOSUID and fs.f_flag & os.ST_NODEV
 phase='ordinary'
 create(targets['ordinary'],b'owned-shm-probe')
 with open(targets['ordinary'],'r+b') as stream:
  assert stream.read()==b'owned-shm-probe'
  stream.seek(0);stream.write(b'updated');stream.truncate()
 with open(targets['ordinary'],'rb') as stream:assert stream.read()==b'updated'
 os.link(targets['ordinary'],targets['linked'])
 os.rename(targets['linked'],targets['renamed'])
 os.unlink(targets['ordinary'])
 with open(targets['renamed'],'rb') as stream:assert stream.read()==b'updated'
 os.unlink(targets['renamed'])
 checks['native_shm_ordinary_files_allowed']=True
 phase='pool'
 before_pool=set(os.listdir(SHM))
 pool=concurrent.futures.ProcessPoolExecutor(max_workers=1,mp_context=multiprocessing.get_context('spawn'))
 assert pool.submit(pow,6,2).result(timeout=8)==36
 worker=pool.submit(os.getpid).result(timeout=8)
 assert type(worker) is int and worker>0 and worker!=os.getpid()
 checks['native_shm_spawn_pool_completed']=True
 phase='pool-cleanup'
 pool.shutdown(wait=True,cancel_futures=True)
 pool=None
 stop_pool()
 assert set(os.listdir(SHM))==before_pool
 checks['native_shm_spawn_pool_cleanup']=True
 phase='capacity'
 before_capacity=os.statvfs(SHM)
 available=before_capacity.f_bavail*before_capacity.f_frsize
 assert 0<available<=LIMIT
 fd=os.open(targets['capacity'],os.O_CREAT|os.O_EXCL|os.O_RDWR|os.O_NOFOLLOW,0o600)
 try:
  # Allocate real tmpfs pages, then require the next page to fail at the
  # filesystem bound. The approved native RLIMIT_FSIZE is larger than 64MiB.
  os.posix_fallocate(fd,0,available)
  assert os.statvfs(SHM).f_bavail==0
  try:os.pwrite(fd,b'x',available)
  except OSError as exc:assert exc.errno==errno.ENOSPC
  else:raise AssertionError
  assert os.fstat(fd).st_size==available
 finally:os.close(fd);os.unlink(targets['capacity'])
 assert os.statvfs(SHM).f_bavail>=before_capacity.f_bavail
 checks['native_shm_64mib_enforced']=True
 phase='noexec'
 create(targets['exec'],b'#!/bin/sh\nexit 0\n')
 os.chmod(targets['exec'],0o700)
 denied(lambda:execute_file(targets['exec']))
 os.unlink(targets['exec'])
 checks['native_shm_noexec_enforced']=True
 phase='objects'
 denied(lambda:os.mkdir(targets['directory'],0o700))
 denied(lambda:os.symlink('ordinary',targets['symlink']))
 denied(lambda:os.mknod(targets['device'],stat.S_IFCHR|0o600,os.makedev(1,3)))
 denied(lambda:os.mknod(targets['block'],stat.S_IFBLK|0o600,os.makedev(7,0)))
 denied(lambda:os.mkfifo(targets['fifo'],0o600))
 denied(lambda:unix_socket(targets['socket']))
 checks['native_shm_forbidden_objects_denied']=True
 phase='outside'
 outside='/home/rnd-module/rnd-shm-'+nonce+'-outside'
 assert not os.path.lexists(outside)
 paths.append(outside)
 denied(lambda:open(outside,'xb'))
 denied(lambda:open('/proc/self/root'+outside,'xb'))
 escape='/tmp/rnd-capability/tmp/rnd-shm-'+nonce+'-escape'
 assert not os.path.lexists(escape)
 paths.append(escape)
 os.symlink(outside,escape)
 denied(lambda:open(escape,'xb'))
 os.unlink(escape)
 checks['native_shm_outside_writes_denied']=True
except BaseException:
 failed=phase
finally:
 try:
  stop_pool()
  cleanup()
 except BaseException:failed='cleanup'
if failed is not None:
 print(json.dumps({'passed':False,'stage':failed},sort_keys=True))
 raise SystemExit(1)
checks['native_shm_probe_cleanup']=True
print(json.dumps(checks,sort_keys=True))
"""

# This command intentionally carries no arbitrary path, content, or output.
# Both sandboxes see the same random names but must see only their own contents.
MARKER = r"""
import os,re,stat,sys
SHM='/dev/shm'
try:
 operation,nonce,side=sys.argv[1:]
 assert re.fullmatch('[a-f0-9]{32}',nonce) and side in ('first','second')
 paths={name:SHM+'/rnd-shm-pair-'+nonce+'-'+name for name in ('first','second','shared')}
 own=paths[side]
 other=paths['second' if side=='first' else 'first']
 def absent(path):assert not os.path.lexists(path)
 def read(path):
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   info=os.fstat(fd)
   assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and info.st_nlink==1
   assert os.read(fd,32)==side.encode()
  finally:os.close(fd)
 if operation=='empty':
  for path in paths.values():absent(path)
 elif operation=='create':
  absent(other)
  for path in (own,paths['shared']):
   fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   try:assert os.write(fd,side.encode())==len(side)
   finally:os.close(fd)
 elif operation=='verify':
  absent(other);read(own);read(paths['shared'])
 elif operation=='cleanup':
  for path in paths.values():
   try:os.unlink(path)
   except FileNotFoundError:pass
  for path in paths.values():absent(path)
 else:raise AssertionError
except BaseException:raise SystemExit(1) from None
print('native-shm-probe-command-complete')
"""


def _native(plan):
    if plan.selection.template != "fastapiadmin" or plan.selection.database != "postgresql":
        raise CheckFailure("共享内存探针只允许已批准的一次性原生profile")


def verify_native_shm(sandbox, plan, timeout):
    """Exercise real spawn workers, tmpfs exhaustion, and denial under the guard."""
    _native(plan)
    try:
        status, output = run_guarded_control(
            sandbox,
            product_argv(
                plan,
                ["/usr/bin/python3", "-I", "-S", "-c", PROBE, uuid.uuid4().hex],
                {},
                native_semaphore_storage=True,
            ),
            min(timeout, 45),
        )
        checks = json.loads(output)
    except Exception:
        raise CheckFailure("原生共享内存安全反例未返回有效回执（stage=unknown）") from None
    if (
        status == 0
        and isinstance(checks, dict)
        and set(checks) == set(RUNTIME_CHECKS)
        and all(value is True for value in checks.values())
    ):
        return checks
    stage = "unknown"
    if (
        status != 0
        and isinstance(checks, dict)
        and set(checks) == {"passed", "stage"}
        and checks["passed"] is False
        and isinstance(checks["stage"], str)
        and checks["stage"] in FAILURE_STAGES
    ):
        stage = checks["stage"]
    raise CheckFailure(f"原生共享内存安全反例未全部通过（stage={stage}）")


def verify_native_shm_isolation(first, second, plan, timeout):
    """Two designated disposable SDK sandboxes must not share either marker.

    The caller must inspect and prepare both sandboxes with the approved native
    profile first, and must delete both through its existing mandatory lifecycle.
    This function certifies marker cleanup; it does not certify container removal.
    """
    _native(plan)
    first_id, second_id = getattr(first, "id", None), getattr(second, "id", None)
    if (
        not isinstance(first_id, str)
        or not first_id
        or not isinstance(second_id, str)
        or not second_id
        or first_id == second_id
    ):
        raise CheckFailure("共享内存隔离验证必须使用两个不同的本次独占沙箱")
    nonce = uuid.uuid4().hex
    owned = []
    phase = "initial"
    primary = "none"

    def command(sandbox, side, operation):
        status, output = run_guarded_control(
            sandbox,
            product_argv(
                plan,
                ["/usr/bin/python3", "-I", "-S", "-c", MARKER, operation, nonce, side],
                {},
                native_semaphore_storage=True,
            ),
            min(timeout, 15),
        )
        return status == 0 and output.strip() == COMPLETE

    try:
        for sandbox, side in ((first, "first"), (second, "second")):
            phase = side + "-empty"
            if not command(sandbox, side, "empty"):
                raise ValueError
            owned.append((sandbox, side))
        phase = "first-create"
        if not command(first, "first", "create"):
            raise ValueError
        phase = "second-empty"
        if not command(second, "second", "empty"):
            raise ValueError
        phase = "second-create"
        if not command(second, "second", "create"):
            raise ValueError
        for sandbox, side in owned:
            phase = side + "-verify"
            if not command(sandbox, side, "verify"):
                raise ValueError
    except Exception:
        primary = phase
        raise CheckFailure(f"两个原生沙箱的共享内存隔离未确认（stage={phase}）") from None
    finally:
        cleaned = True
        for sandbox, side in owned:
            try:
                if not command(sandbox, side, "cleanup"):
                    cleaned = False
            except Exception:
                cleaned = False
        if not cleaned:
            raise CheckFailure(
                f"本次共享内存隔离探针清理未确认（primary={primary}; cleanup=failed）"
            ) from None
    return dict.fromkeys(PAIR_CHECKS, True)


def _peer_identity(sandbox, name, nonce, first_id):
    """Only this request's uniquely labelled SDK object may be deleted."""
    identifier = getattr(sandbox, "id", None)
    if (
        not isinstance(identifier, str)
        or not re.fullmatch(UUID_PATTERN, identifier)
        or identifier == first_id
        or getattr(sandbox, "name", None) != name
        or not isinstance(getattr(sandbox, "labels", None), dict)
        or sandbox.labels.get("rnd-shm-probe") != nonce
    ):
        raise CheckFailure("共享内存探针对端身份不属于本次创建，未读取或删除其他沙箱")
    return identifier


def _require_peer_absent(directory, identifier, timeout):
    """Read only the exact owned UUID in the existing profile's Docker daemon."""
    if not isinstance(identifier, str) or not re.fullmatch(UUID_PATTERN, identifier):
        raise ValueError
    deadline = time.monotonic() + min(timeout, 30)
    runner = compose(directory, "ps", "--quiet", "runner", timeout=min(timeout, 10)).strip()
    if not re.fullmatch(r"[a-f0-9]{64}", runner):
        raise ValueError
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError
        # Upstream names the actual Docker container sandboxDto.Id, not its
        # friendly SDK name. An empty exact-name listing proves physical removal.
        output = local.docker(
            "exec",
            runner,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "ls",
            "--all",
            "--quiet",
            "--no-trunc",
            "--filter",
            "name=^/" + identifier + "$",
            timeout=min(remaining, 15),
        )
        if isinstance(output, str) and not output.strip():
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError
        time.sleep(min(0.2, remaining))


class NativeShmCleanupFailure(CheckFailure):
    """Keep only controller-generated recovery identifiers for the operator."""

    def __init__(self, name, identifier, primary, cleanup):
        super().__init__(f"本次共享内存对端清理未确认（primary={primary}; cleanup=failed）")
        self.diagnostic = {
            "peer_name": name,
            "peer_id": identifier,
            "primary_stage": primary,
            "cleanup_stage": cleanup,
            "cleanup": "unconfirmed",
        }


def native_shm_cleanup_diagnostic(error):
    """Never serialize an arbitrary exception, traceback, peer object or label."""
    if type(error) is not NativeShmCleanupFailure:
        return {}
    value = getattr(error, "diagnostic", None)
    if (
        type(value) is not dict
        or set(value) != {"peer_name", "peer_id", "primary_stage", "cleanup_stage", "cleanup"}
        or not isinstance(value["peer_name"], str)
        or not re.fullmatch(r"rnd-source-native-shm-peer-[a-f0-9]{32}", value["peer_name"])
        or (
            value["peer_id"] is not None
            and (
                not isinstance(value["peer_id"], str)
                or not re.fullmatch(UUID_PATTERN, value["peer_id"])
            )
        )
        or not isinstance(value["primary_stage"], str)
        or value["primary_stage"] not in PRIMARY_STAGES
        or not isinstance(value["cleanup_stage"], str)
        or value["cleanup_stage"] not in CLEANUP_STAGES
        or value["cleanup"] != "unconfirmed"
    ):
        return {}
    return dict(value)


def _require_native_resources(value):
    keys = {"cpu_period", "cpu_quota", "memory", "memory_swap", "tmpfs_bytes", "pids"}
    if (
        type(value) is not dict
        or set(value) != keys
        or any(type(v) is not int for v in value.values())
    ):
        raise ValueError
    checked = require_execution_resources(
        {
            "CpuPeriod": value["cpu_period"],
            "CpuQuota": value["cpu_quota"],
            "Memory": value["memory"],
            "MemorySwap": value["memory_swap"],
            "PidsLimit": value["pids"],
            "Tmpfs": {"/tmp": f"rw,nosuid,nodev,size={value['tmpfs_bytes']},mode=1777"},
        },
        native=True,
    )
    if checked != value:
        raise ValueError


def verify_native_shm_peer(client, settings, directory, record, first, plan, timeout):
    """Create one owned same-profile peer; certify isolation only after deletion.

    Initial admission is rechecked before resource creation. A failed create is
    recovered by its exact random SDK name and label, never by a global list.
    There is no host mount, direct Docker mutation, candidate upload, or cleanup fallback.
    """
    _native(plan)
    if (
        client is None
        or settings is None
        or getattr(settings, "sandbox_provider", None) != "daytona"
    ):
        raise CheckFailure("共享内存对端验证缺少已批准的本机SDK执行环境")
    selected = plan.selection.model_dump()
    phase = "admission"
    try:
        if (
            record.get("selection") != selected
            or snapshot_for(settings, selected["template"], selected)
            != record["snapshot"]["snapshot"]
        ):
            raise ValueError

        def inspect(sandbox):
            sandbox.refresh_data()
            if sandbox.network_block_all is not True or sandbox.public is not False:
                raise ValueError
            evidence = require_container_evidence(
                inspect_created_sandbox(
                    directory, sandbox.id, require_resources=True, selection=selected
                ),
                sandbox.id,
            )
            if evidence.get("profile") != "native-fastapiadmin-postgresql-v1":
                raise ValueError
            _require_native_resources(evidence.get("resource_limits"))
            require_profile_container_binding(record, evidence)

        inspect(first)
        nonce = uuid.uuid4().hex
        name = "rnd-source-native-shm-peer-" + nonce
        parameters = params_for(settings, name, selected["template"], selected)
        if (
            parameters.snapshot != record["snapshot"]["snapshot"]
            or parameters.network_block_all is not True
            or parameters.public is not False
        ):
            raise ValueError
        parameters.os_user = "root"
        parameters.labels = {**parameters.labels, "rnd-shm-probe": nonce}
    except Exception:
        raise CheckFailure("共享内存对端创建前的原生隔离绑定无效（stage=admission）") from None

    peer = None
    primary = "none"
    try:
        phase = "create"
        peer = client.create(parameters, timeout=timeout)
        _peer_identity(peer, name, nonce, first.id)
        phase = "inspect"
        inspect(peer)
        phase = "prepare"
        peer.fs.create_folder("/tmp/rnd-capability", "711")
        peer.fs.create_folder(PRODUCT, "700")
        identity = prepare_identity(peer, plan, timeout, native_semaphore_storage=True)
        require_native_shared_memory_evidence(identity.get("native_shared_memory"))
        phase = "pair"
        pair = verify_native_shm_isolation(first, peer, plan, timeout)
        if pair != dict.fromkeys(PAIR_CHECKS, True):
            raise ValueError
    except Exception:
        primary = phase
        raise CheckFailure(f"原生共享内存对端验证未完成（stage={phase}）") from None
    finally:
        identifier = None
        cleanup_stage = "recover"
        try:
            if peer is None:
                peer = client.get(name)
            cleanup_stage = "identity"
            identifier = _peer_identity(peer, name, nonce, first.id)
            cleanup_stage = "delete"
            client.delete(peer, timeout=timeout)
            cleanup_stage = "physical-absence"
            _require_peer_absent(directory, identifier, timeout)
        except Exception:
            raise NativeShmCleanupFailure(name, identifier, primary, cleanup_stage) from None
    return {"cross_container_shm_private": True, "peer_cleanup": True}
