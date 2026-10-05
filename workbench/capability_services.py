"""Owned native test services, never credentials or databases from the host.

Every sandbox receives its own Redis instance/DB 0. The application ACL cannot
administer it, select another DB, or use the private control socket. This is an
instance namespace, not a claim that arbitrary existing Redis keys are scoped.
"""

import json
import secrets

from workbench.capability_isolation import (
    control_exec,
    product_argv,
    run_guarded_control,
    system_argv,
)
from workbench.capability_verification import CheckFailure

REDIS_PORT = 55433
REDIS_ROOT = "/tmp/rnd-redis"


def prepare_native_services(sandbox, plan, timeout):
    if plan.selection.template != "fastapiadmin":
        return {}
    application = secrets.token_hex(24)
    control = secrets.token_hex(24)
    session = secrets.token_hex(32)
    for argv in (
        ["/usr/bin/mkdir", "-p", REDIS_ROOT],
        ["/usr/bin/chown", "redis:redis", REDIS_ROOT],
        ["/usr/bin/chmod", "700", REDIS_ROOT],
    ):
        if control_exec(sandbox, argv, timeout).exit_code:
            raise CheckFailure("无法建立本次独立Redis私有目录")
    config = "\n".join(
        (
            "bind 127.0.0.1",
            f"port {REDIS_PORT}",
            "protected-mode yes",
            "databases 1",
            f"dir {REDIS_ROOT}",
            f"unixsocket {REDIS_ROOT}/control.sock",
            "unixsocketperm 700",
            f"pidfile {REDIS_ROOT}/redis.pid",
            f"logfile {REDIS_ROOT}/redis.log",
            "daemonize yes",
            'save ""',
            "appendonly no",
            "maxmemory 134217728",
            "maxmemory-policy noeviction",
            "user default off",
            f"user rnd_app on >{application} ~* &* +@read +@write +@connection +@transaction +@pubsub -@admin -@dangerous -select +eval +evalsha +script|load +scan +keys +info +dbsize",
            f"user rnd_control on >{control} ~* &* +@all",
            "",
        )
    )
    sandbox.fs.upload_file(config.encode(), REDIS_ROOT + "/redis.conf", timeout=timeout)
    # The control password is never placed on a process command line or in the
    # application environment. Only trusted root helpers can read this file.
    sandbox.fs.upload_file(
        json.dumps({"password": control, "sandbox_id": sandbox.id}).encode(),
        "/tmp/rnd-module-control/private/redis-control.json",
        timeout=timeout,
    )
    for argv in (
        ["/usr/bin/chmod", "600", "/tmp/rnd-module-control/private/redis-control.json"],
        ["/usr/bin/chown", "redis:redis", REDIS_ROOT + "/redis.conf"],
        ["/usr/bin/chmod", "600", REDIS_ROOT + "/redis.conf"],
        [
            "/usr/sbin/runuser",
            "-u",
            "redis",
            "--",
            *system_argv(["/usr/bin/redis-server", REDIS_ROOT + "/redis.conf"]),
        ],
    ):
        if control_exec(sandbox, argv, timeout).exit_code:
            raise CheckFailure("本次独立Redis启动或ACL配置失败")
    return {"redis_password": application, "session_key": session}


NATIVE_SERVICE_PROBE = r"""
import json,os,socket,subprocess
checks={}
environment={'PATH':'/usr/bin:/bin','PGPASSWORD':os.environ['DATABASE_PASSWORD']}
base=['/usr/lib/postgresql/17/bin/psql','-X','-w','-h','127.0.0.1','-p','55432','-U','rnd_app','-d','rnd_product','-At','-v','ON_ERROR_STOP=1','-c']
safe=subprocess.run(base+['SELECT current_user; SELECT rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls FROM pg_catalog.pg_roles WHERE rolname=current_user'],env=environment,capture_output=True,timeout=5)
assert safe.returncode==0 and safe.stdout.strip()==b'rnd_app\nf'
for query in ('SET ROLE postgres','SET ROLE rnd_verify',"COPY (SELECT 1) TO PROGRAM 'true'", "SELECT pg_read_file('/tmp/rnd-module-control/private/redis-control.json')"):
 assert subprocess.run(base+[query],env=environment,capture_output=True,timeout=5).returncode!=0
outside=list(base);outside[outside.index('rnd_product')]='postgres'
assert subprocess.run(outside+['SELECT 1'],env=environment,capture_output=True,timeout=5).returncode!=0
checks['postgres_application_role_restricted']=True
with socket.create_connection(('127.0.0.1',55433),timeout=3) as connection:
 stream=connection.makefile('rb',buffering=0)
 def command(*args):
  encoded=[str(arg).encode() for arg in args]
  connection.sendall(b'*'+str(len(encoded)).encode()+b'\r\n'+b''.join(b'$'+str(len(v)).encode()+b'\r\n'+v+b'\r\n' for v in encoded))
  line=stream.readline(1025)
  assert len(line)<=1024 and line.endswith(b'\r\n')
  return line
 assert command('AUTH','rnd_app',os.environ['REDIS_PASSWORD'])==b'+OK\r\n'
 assert command('SET','__rnd_security_probe','owned')==b'+OK\r\n'
 assert command('DEL','__rnd_security_probe')==b':1\r\n'
 for args in (('CONFIG','GET','dir'),('ACL','LIST'),('SELECT','1'),('FLUSHALL',),('REPLICAOF','127.0.0.1','1')):
  assert command(*args).startswith(b'-NOPERM')
checks['redis_owned_namespace_only']=True
checks['private_redis_control_denied']=False
try:open('/tmp/rnd-redis/redis.conf','rb')
except PermissionError:checks['private_redis_control_denied']=True
assert checks['private_redis_control_denied']
print(json.dumps(checks))
"""


def verify_native_services(sandbox, plan, environment, timeout):
    if plan.selection.template != "fastapiadmin":
        return {}
    status, output = run_guarded_control(
        sandbox,
        product_argv(
            plan, ["/usr/bin/python3", "-I", "-S", "-c", NATIVE_SERVICE_PROBE], environment
        ),
        timeout,
    )
    try:
        checks = json.loads(output)
    except ValueError, TypeError:
        raise CheckFailure("原生服务身份探针未返回有效回执") from None
    expected = {
        "postgres_application_role_restricted",
        "redis_owned_namespace_only",
        "private_redis_control_denied",
    }
    if (
        status != 0
        or not isinstance(checks, dict)
        or set(checks) != expected
        or any(v is not True for v in checks.values())
    ):
        raise CheckFailure("原生数据库/Redis权限边界未通过，未执行候选源码")
    from workbench.capability_stack import pg_verifier_argv

    safe_query = "SELECT current_user,session_user,rolsuper,rolcreaterole,rolcreatedb,rolreplication,rolbypassrls FROM pg_catalog.pg_roles WHERE rolname=current_user"
    result = control_exec(sandbox, pg_verifier_argv(safe_query), min(timeout, 10))
    if result.exit_code or result.result.strip() != "rnd_verify|rnd_verify|f|f|f|f|f":
        raise CheckFailure("数据库验证器没有使用独立低权限认证")
    for query in (
        "SET ROLE postgres",
        "SET ROLE rnd_app",
        "CREATE TABLE public.verifier_must_not_write(id int)",
        "SELECT pg_catalog.pg_read_file('/tmp/rnd-module-control/private/postgres-verifier.json')",
    ):
        if control_exec(sandbox, pg_verifier_argv(query), min(timeout, 10)).exit_code == 0:
            raise CheckFailure("独立数据库验证身份有多余权限")
    checks["postgres_verifier_role_restricted"] = True
    return checks


REDIS_RESET = r"""
import json,pathlib,socket,sys
p=pathlib.Path('/tmp/rnd-module-control/private/redis-control.json')
assert p.stat().st_uid==0 and p.stat().st_mode&0o077==0 and p.stat().st_size<1024
control=json.loads(p.read_text());assert control['sandbox_id']==sys.argv[1]
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
 connection.settimeout(3);connection.connect('/tmp/rnd-redis/control.sock')
 stream=connection.makefile('rb',buffering=0)
 def command(*args):
  encoded=[str(a).encode() for a in args]
  connection.sendall(b'*'+str(len(encoded)).encode()+b'\r\n'+b''.join(b'$'+str(len(v)).encode()+b'\r\n'+v+b'\r\n' for v in encoded))
  assert stream.readline(1024)==b'+OK\r\n'
 command('AUTH','rnd_control',control['password'])
 command('FLUSHDB','SYNC')
"""


def reset_owned_native_cache(sandbox, timeout):
    result = control_exec(
        sandbox, ["/usr/bin/python3", "-I", "-S", "-c", REDIS_RESET, sandbox.id], min(timeout, 10)
    )
    if result.exit_code:
        raise CheckFailure("本次独立Redis缓存重建未确认，不能报告新库复测通过")
