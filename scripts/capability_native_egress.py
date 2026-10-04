"""Actual same-port egress denial against our own temporary inner-Docker peer.

No public service or host networking change. A trusted Runner must reach the
synthetic peer immediately before and after the application identity cannot.
Only the uniquely named, labelled peer created here is removed.
"""

import ipaddress
import json
import re
import time
import uuid

from scripts import daytona_local as local
from scripts.daytona_capability_profile import compose
from workbench.capability_isolation import product_argv, run_guarded_control
from workbench.capability_verification import CheckFailure

SERVER = r"""
import http.server,sys,threading,time
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  body=b'rnd-owned-egress-peer';self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
for port in map(int,sys.argv[1:]):
 server=http.server.ThreadingHTTPServer(('0.0.0.0',port),Handler)
 threading.Thread(target=server.serve_forever,daemon=True).start()
time.sleep(90)
"""

DENY = r"""
import errno,json,socket,sys
address=sys.argv[1]
for port in map(int,sys.argv[2:]):
 for family,target in ((socket.AF_INET,address),(socket.AF_INET6,'::ffff:'+address)):
  try:
   with socket.socket(family,socket.SOCK_STREAM) as connection:
    connection.settimeout(1);connection.connect((target,port))
  except OSError as exc:
   assert isinstance(exc,TimeoutError) or exc.errno in (errno.EACCES,errno.EPERM,errno.EHOSTUNREACH,errno.ENETUNREACH,errno.ECONNREFUSED,errno.EAFNOSUPPORT)
  else:raise AssertionError('Same approved port reachable outside this sandbox')
print(json.dumps({'native_egress_denied_same_ports':True}))
"""


def verify_native_egress(directory, record, sandbox, plan, timeout):
    if plan.selection.template != "fastapiadmin":
        raise CheckFailure("外部同端口探针仅用于已声明原生profile")
    ports = sorted({plan.runtime.port, 55432, 55433})
    if any(not 1024 <= port <= 65535 or port == 2280 for port in ports):
        raise CheckFailure("原生同端口探针端口无效")
    runner = compose(directory, "ps", "--quiet", "runner").strip()
    if not re.fullmatch(r"[a-f0-9]{64}", runner):
        raise CheckFailure("原生出口验证缺少唯一Runner")
    name = "rnd-egress-" + uuid.uuid4().hex
    identifier = None
    created = False

    def docker(*args, limit=30):
        return local.docker(
            "exec",
            runner,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            *args,
            timeout=min(timeout, limit),
        )

    def inspect():
        rows = json.loads(docker("container", "inspect", name))
        if len(rows) != 1:
            raise CheckFailure("本次出口探针身份不唯一")
        row = rows[0]
        labels = row.get("Config", {}).get("Labels", {})
        if row.get("Name") != "/" + name or labels.get("rnd-owned-sandbox") != sandbox.id:
            raise CheckFailure("出口探针不属于本次沙箱，不读取或删除其他容器")
        if row.get("Image") != record["snapshot"]["image_id"]:
            raise CheckFailure("出口探针镜像身份不匹配")
        return row

    def reachable(address):
        for port in ports:
            value = local.docker(
                "exec",
                runner,
                "curl",
                "--noproxy",
                "*",
                "--fail",
                "--silent",
                "--max-time",
                "3",
                f"http://{address}:{port}/",
                timeout=min(timeout, 5),
            )
            if value.strip() != "rnd-owned-egress-peer":
                raise CheckFailure("可信控制端无法确认出口探针仍可达")

    try:
        # Mark the attempt before POST-like Docker run; an uncertain response
        # still uses the exact owned name+label for bounded cleanup, never retry.
        created = True
        identifier = docker(
            "run",
            "--detach",
            "--name",
            name,
            "--label",
            "rnd-owned-sandbox=" + sandbox.id,
            "--network",
            "runner-bridge",
            "--user",
            "65534:65534",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--memory",
            "64m",
            "--memory-swap",
            "64m",
            "--cpus",
            "0.25",
            "--pids-limit",
            "16",
            "--entrypoint",
            "/usr/bin/python3",
            record["snapshot"]["image_id"],
            "-I",
            "-S",
            "-c",
            SERVER,
            *(str(port) for port in ports),
        ).strip()
        if not re.fullmatch(r"[a-f0-9]{64}", identifier):
            raise CheckFailure("出口探针创建结果不确定，不重发创建请求")
        row = inspect()
        if row["Id"] != identifier:
            raise CheckFailure("出口探针返回身份不一致")
        network = row.get("NetworkSettings", {}).get("Networks", {})
        if set(network) != {"runner-bridge"}:
            raise CheckFailure("出口探针使用了未批准网络")
        address = network["runner-bridge"].get("IPAddress", "")
        if ipaddress.ip_address(address) not in ipaddress.ip_network(local.RUNNER_BRIDGE_SUBNET):
            raise CheckFailure("出口探针地址不在本次内部Runner网络")
        deadline = time.monotonic() + 8
        while True:
            try:
                reachable(address)
                break
            except Exception:
                if time.monotonic() >= deadline:
                    raise CheckFailure("出口正向对照服务未就绪，不能证明出口已阻断") from None
                time.sleep(0.2)
        status, output = run_guarded_control(
            sandbox,
            product_argv(
                plan,
                [
                    "/usr/bin/python3",
                    "-I",
                    "-S",
                    "-c",
                    DENY,
                    address,
                    *(str(port) for port in ports),
                ],
                {},
            ),
            min(timeout, 15),
        )
        reachable(address)
        if status != 0 or json.loads(output) != {"native_egress_denied_same_ports": True}:
            raise CheckFailure("候选身份可以访问本沙箱外的同端口服务，禁止执行源码")
        return {"native_egress_denied_same_ports": True}
    finally:
        if created:
            try:
                row = inspect()
                current = row.get("Id", "")
                if not re.fullmatch(r"[a-f0-9]{64}", current):
                    raise ValueError("Invalid cleanup identity")
                docker("rm", "--force", current)
            except Exception:
                raise CheckFailure("本次出口探针清理未确认，已阻止交付：" + name) from None
