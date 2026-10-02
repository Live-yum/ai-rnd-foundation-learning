# scripts/daytona_local.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：安装和管理本机Daytona开发服务。** prepare取得固定资源与随机本机配置，images构建并锁定镜像，up验证锁后启动，status读取状态；snapshot-image预热产品依赖。每一步分开执行，失败不跳下一步。

**对应关系：** 终端明确命令 → 本机Docker/Compose → .data/daytona-local配置与锁。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_build`、`scripts.daytona_gateway`、`workbench.local_only`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `private_json`（L59–L63）：接收`path`、`data`。 控制顺序：L62按`os.name != "nt"`分支。 调用`Path`、`path.write_text`、`json.dumps`、`path.chmod`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `command`（L66–L77）：接收`argv`、`cwd`、`timeout`。 源码说明：Never forward a model key, proxy, remote Docker context or shell string.。 调用`subprocess.run`、`clean_env`、`result.stdout.decode("utf-8", errors="replace").strip`、`result.stdout.decode`。 返回路径：L77的`result.stdout.decode("utf-8", errors="replace").strip()`。
- `docker`（L80–L83）：接收`timeout`、`*args`。 调用`command`。 返回路径：L83的`command(["docker", "--host", host, *args], timeout=timeout)`。
- `environment`（L86–L90）：接收`service`。 控制顺序：L88按`isinstance(original, list)`分支。 调用`service.get`、`isinstance`、`dict`、`item.split`。 返回路径：L89的`dict(item.split("=", 1) for item in original)`；L90的`dict(original)`。
- `gateway_service`（L93–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Only this fixed byte-forwarder has a publishing network; backends have none.。 调用`str`。 返回路径：L95的`{ "image": IMAGES["gateway"], "command": ["python", "-I", "/opt/rnd/gateway.py"], "user": …`。
- `render_compose`（L110–L191）：接收`original`、`credentials`、`directory`。 源码说明：Transform upstream configuration; never execute instructions from its README.。 控制顺序：L117按`set(config["services"]) != UPSTREAM_SERVICES`分支；L118抛异常，停止当前正常路径；L120遍历`config["services"].items()`；L124按`name != "runner"`分支；L132遍历`tuple(env)`；L133按`any(word in key for word in ("POSTHOG", "SENTRY", "ANALYTICS", "OTEL", "SSH_"))`分支。 调用`copy.deepcopy`、`config["services"].items`、`set`、`ValueError`、`service.pop`、`service.get`、`environment`、`tuple`、`any`等。 返回路径：L191的`config`。
- `assert_local_compose`（L194–L254）：接收`config`。 控制顺序：L196按`control_plane.get("internal") is not True`分支；L197抛异常，停止当前正常路径；L200按`not isinstance(ranges, list) or len(ranges) != 1 or not isinstance(ranges[0], dict) o…`分支；L206抛异常，停止当前正常路径；L210抛异常，停止当前正常路径；L211按`subnet.version != 4 or not subnet.is_private or subnet.overlaps(ipaddress.ip_network(…`分支；L216抛异常，停止当前正常路径；L217按`config.get("networks") != NETWORKS`分支。后续分支沿下方源码相同行号继续阅读。 调用`config.get("networks", {}).get`、`config.get`、`control_plane.get`、`ValueError`、`isinstance`、`ipam.get`、`len`、`ranges[0].get`、`ipaddress.ip_network`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare`（L257–L335）：接收`directory`。 控制顺序：L259按`directory.exists() and any(directory.iterdir())`分支；L260抛异常，停止当前正常路径；L262按`os.name != "nt"`分支；L279按`command(["git", "rev-parse", "HEAD"], cwd=source) != DAYTONA_SOURCE`分支；L280抛异常，停止当前正常路径；L320遍历`(("compose.yaml", config), ("dex.yaml", dex))`；L323按`os.name != "nt"`分支。 调用`Path(directory).resolve`、`Path`、`directory.exists`、`any`、`directory.iterdir`、`ValueError`、`directory.mkdir`、`directory.chmod`、`source.mkdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `images`（L338–L366）：接收`directory`。先在本机从固定源码或校验后的同版本发布文件构建Daytona，再锁定Image ID；其他基础依赖记录Registry摘要。启动对照两份锁且禁止自动拉取替代版本。 控制顺序：L343按`locked.exists()`分支；L344抛异常，停止当前正常路径；L347遍历`config["services"].items()`；L348按`name in BUILT`分支；L355按`not matching`分支；L356抛异常，停止当前正常路径；L360遍历`BUILT`；L363按`os.name != "nt"`分支。 调用`Path`、`yaml.safe_load`、`(directory / "compose.yaml").read_text`、`assert_local_compose`、`locked.exists`、`ValueError`、`config["services"].items`、`docker`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `compose`（L369–L379）：接收`directory`、`timeout`、`*args`。 控制顺序：L374遍历`config["services"].items()`；L377按`service["image"] != expected or record["tag"] != IMAGES[name]`分支；L378抛异常，停止当前正常路径。 调用`Path`、`yaml.safe_load`、`path.read_text`、`assert_local_compose`、`json.loads`、`(Path(directory) / "images.lock.json").read_text`、`config["services"].items`、`record.get`、`ValueError`等。 返回路径：L379的`docker("compose", "--project-name", PROJECT, "--file", str(path), *args, timeout=timeout)`。
- `snapshot_stamp`（L382–L387）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`hashlib.sha256( (ROOT / "tools/daytona/Dockerfile").read_bytes() …`、`hashlib.sha256`、`(ROOT / "tools/daytona/Dockerfile").read_bytes`、`(ROOT / "templates/product/uv.lock").read_bytes`、`(ROOT / "templates/product/pyproject.toml").read_bytes`。 返回路径：L383的`hashlib.sha256( (ROOT / "tools/daytona/Dockerfile").read_bytes() + (ROOT / "templates/prod…`。
- `wait_for_registry`（L390–L407）：不接收显式业务参数，从已配置对象/模块读取依赖。检测宿主机127.0.0.1上的真实Registry响应，而不是只检查容器存在；限时重试失败即停止，不上传到云端仓库。 源码说明：Check real host-loopback reachability, not merely a running container state.。 控制顺序：L395遍历`range(30)`；L399按`response.json() != {}`分支；L400抛异常，停止当前正常路径；L403按`attempt == 29`分支；L404抛异常，停止当前正常路径。 调用`httpx.Client`、`range`、`client.get`、`response.raise_for_status`、`response.json`、`ValueError`、`RuntimeError`、`time.sleep`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `snapshot_image`（L410–L440）：接收`directory`。构建上下文只有Dockerfile与产品依赖文件，不含模型Key、平台源码或用户数据库。镜像进入本机Registry供本机Runner读取。 控制顺序：L415遍历`("pyproject.toml", "uv.lock")`；L424按`stamp != snapshot_stamp()`分支；L425抛异常，停止当前正常路径。 调用`Path`、`context.mkdir`、`shutil.copyfile`、`hashlib.sha256( b"".join( (context / name).read_bytes() for name …`、`hashlib.sha256`、`b"".join`、`(context / name).read_bytes`、`snapshot_stamp`、`ValueError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `up`（L443–L482）：接收`directory`。 源码说明：A started container is not a ready API; reject early exits before authentication.。 控制顺序：L455遍历`range(90)`；L465按`dead`分支；L466抛异常，停止当前正常路径；L472按`running == KEEP`分支；L474遍历`endpoints`；L480按`attempt != 89`分支；L482抛异常，停止当前正常路径。 调用`compose`、`httpx.Client`、`range`、`raw.lstrip().startswith`、`raw.lstrip`、`json.loads`、`raw.splitlines`、`line.strip`、`row.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L485–L502）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L492按`args.action == "prepare"`分支；L494按`args.action == "images"`分支；L496按`args.action == "snapshot-image"`分支；L498按`args.action == "up"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`prepare`、`images`、`snapshot_image`、`up`、`print`、`compose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_local.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L520。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21665`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_local.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "637be560a398469d0913d58f9c4c08c060d3d38d247cc275e2627706c373483c"} -->
````python
# scripts/daytona_local.py
"""Install the pinned, development-only Daytona stack on this machine.

Only `prepare` and `images`/`snapshot-image` fetch public software dependencies.
Runtime API, authentication, storage, registry and execution remain local. No
Daytona account, Auth0 tenant, hosted runner or hosted telemetry is involved.
"""

import argparse
import copy
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import shutil
import subprocess
import time
from pathlib import Path

import yaml

from scripts.daytona_build import BUILT, build_images, local_tag
from scripts.daytona_gateway import TARGETS
from workbench.local_only import DAYTONA_SOURCE, DAYTONA_VERSION
from workbench.settings import ROOT
from workbench.tools import clean_env

HOME = ROOT / ".data/daytona-local"
PROJECT = "rnd-daytona-local"
UPSTREAM_SERVICES = {"api", "proxy", "runner", "db", "redis", "dex", "registry", "minio", "maildev"}
KEEP = UPSTREAM_SERVICES | {"gateway"}
# Pinned DAYTONA_SOURCE 01c502bb1f1ff8f2885d0cd490e043736083dca8:
# apps/runner/pkg/docker/client.go fixes the isolated runner-bridge to this /16.
# Keep the outer DinD control plane disjoint; dynamic Docker allocation can choose
# the same subnet and send daemon readiness probes down the wrong interface.
RUNNER_BRIDGE_SUBNET = "172.20.0.0/16"
CONTROL_PLANE_SUBNET = "172.30.240.0/24"
NETWORKS = {
    "daytona-network": {
        "driver": "bridge",
        "internal": True,
        "ipam": {"config": [{"subnet": CONTROL_PLANE_SUBNET}]},
    },
    "loopback-entry": {"driver": "bridge", "internal": False},
}
IMAGES = {
    **{name: local_tag(name) for name in BUILT},
    "db": "postgres:18",
    "redis": "redis:7.4.2",
    "dex": "dexidp/dex:v2.42.0",
    "registry": "registry:2.8.2",
    "maildev": "maildev/maildev:2.2.1",
    "gateway": "python:3.14.7-slim",
}


def private_json(path, data):
    path = Path(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)


def command(argv, *, cwd=ROOT, timeout=900):
    """Never forward a model key, proxy, remote Docker context or shell string."""
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=clean_env(),
        timeout=timeout,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8", errors="replace").strip()


def docker(*args, timeout=900):
    # Explicit local daemon: a saved remote Docker context cannot change execution location.
    host = "npipe:////./pipe/docker_engine" if os.name == "nt" else "unix:///var/run/docker.sock"
    return command(["docker", "--host", host, *args], timeout=timeout)


def environment(service):
    original = service.get("environment", {})
    if isinstance(original, list):
        return dict(item.split("=", 1) for item in original)
    return dict(original)


def gateway_service():
    """Only this fixed byte-forwarder has a publishing network; backends have none."""
    return {
        "image": IMAGES["gateway"],
        "command": ["python", "-I", "/opt/rnd/gateway.py"],
        "user": "65534:65534",
        "read_only": True,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "restart": "no",
        "networks": ["daytona-network", "loopback-entry"],
        "ports": [f"127.0.0.1:{port}:{port}" for port in TARGETS],
        "volumes": [str(ROOT / "scripts/daytona_gateway.py") + ":/opt/rnd/gateway.py:ro"],
        "environment": {"OTEL_ENABLED": "false", "DO_NOT_TRACK": "1", "OTEL_SDK_DISABLED": "true"},
    }


def render_compose(original, credentials, directory):
    """Transform upstream configuration; never execute instructions from its README."""
    config = copy.deepcopy(original)
    config["name"] = PROJECT
    config["services"] = {
        name: value for name, value in config["services"].items() if name in UPSTREAM_SERVICES
    }
    if set(config["services"]) != UPSTREAM_SERVICES:
        raise ValueError("固定Daytona源码的服务集合不符，拒绝套用不兼容配置")
    config["networks"] = copy.deepcopy(NETWORKS)
    for name, service in config["services"].items():
        service["image"] = IMAGES[name]
        service["restart"] = "no"
        service.pop("build", None)
        if name != "runner":
            service.pop("privileged", None)
        service.pop("ports", None)
        service["networks"] = ["daytona-network"]
        service["depends_on"] = [n for n in service.get("depends_on", []) if n in KEEP]
        env = environment(service)
        # Disable both backend and browser telemetry. Empty keys alone are insufficient
        # for a frontend baked into an image, so the local API returns no telemetry config.
        for key in tuple(env):
            if any(word in key for word in ("POSTHOG", "SENTRY", "ANALYTICS", "OTEL", "SSH_")):
                env.pop(key)
        env.update(
            OTEL_ENABLED="false",
            POSTHOG_API_KEY="",
            POSTHOG_HOST="",
            DO_NOT_TRACK="1",
            OTEL_SDK_DISABLED="true",
        )
        service["environment"] = env
    api = config["services"]["api"]["environment"]
    api.update(
        ENCRYPTION_KEY=credentials["encryption_key"],
        ENCRYPTION_SALT=credentials["salt"],
        DB_PASSWORD=credentials["database_password"],
        S3_SECRET_KEY=credentials["storage_password"],
        PROXY_API_KEY=credentials["proxy_key"],
        DEFAULT_RUNNER_API_KEY=credentials["runner_key"],
        HEALTH_CHECK_API_KEY=credentials["health_key"],
        # v0.190.0's API-key strategy requires this value even when the optional
        # SSH service is absent. Derive a distinct, stable local sentinel; do
        # not reuse a proxy/health key or re-enable any SSH service or URL.
        SSH_GATEWAY_API_KEY=hmac.new(
            credentials["admin_key"].encode(), b"rnd-local-unused-ssh-gateway", hashlib.sha256
        ).hexdigest(),
        ADMIN_API_KEY=credentials["admin_key"],
        DEFAULT_REGION_ID="local",
        DEFAULT_REGION_NAME="local-computer",
        DEFAULT_RUNNER_NAME="local-docker",
        OIDC_MANAGEMENT_API_ENABLED="false",
        # Match Dex's signed issuer, but obtain JWKS via its private Docker hostname.
        PUBLIC_OIDC_DOMAIN="http://localhost:5556/dex",
        DEFAULT_SNAPSHOT="registry:6000/rnd-python:" + snapshot_stamp(),
    )
    config["services"]["proxy"]["environment"].update(PROXY_API_KEY=credentials["proxy_key"])
    config["services"]["runner"]["environment"].update(
        DAYTONA_RUNNER_TOKEN=credentials["runner_key"],
        AWS_SECRET_ACCESS_KEY=credentials["storage_password"],
        SSH_GATEWAY_ENABLE="false",
        INITIALIZE_DAEMON_TELEMETRY="false",
    )
    config["services"]["db"]["environment"]["POSTGRES_PASSWORD"] = credentials["database_password"]
    config["services"]["minio"]["environment"]["MINIO_ROOT_PASSWORD"] = credentials[
        "storage_password"
    ]
    # A host-owned 0600 credential file must work for any developer UID.
    # This non-privileged container has only its config and its own data volume.
    config["services"]["dex"]["user"] = "0:0"
    config["services"]["dex"]["security_opt"] = ["no-new-privileges:true"]
    config["services"]["minio"]["environment"]["MINIO_IDENTITY_STS_EXPIRY"] = "24h"
    config["services"]["minio"]["environment"]["MINIO_UPDATE"] = "off"
    config["services"]["dex"]["volumes"] = [
        str(Path(directory).resolve() / "dex.yaml") + ":/etc/dex/config.yaml:ro",
        "dex_db:/var/dex",
    ]
    config["services"]["gateway"] = gateway_service()
    # Do not persist unneeded optional SSH/observability services or their test keys.
    assert_local_compose(config)
    return config


def assert_local_compose(config):
    control_plane = config.get("networks", {}).get("daytona-network", {})
    if control_plane.get("internal") is not True:
        raise ValueError("Daytona运行网络必须禁止外部出口")
    ipam = control_plane.get("ipam")
    ranges = ipam.get("config") if isinstance(ipam, dict) else None
    if (
        not isinstance(ranges, list)
        or len(ranges) != 1
        or not isinstance(ranges[0], dict)
        or not isinstance(ranges[0].get("subnet"), str)
    ):
        raise ValueError("Daytona控制网络必须固定不重叠的私有子网；不自动选择或重试")
    try:
        subnet = ipaddress.ip_network(ranges[0]["subnet"])
    except ValueError:
        raise ValueError("Daytona控制网络子网无效；不自动选择或重试") from None
    if (
        subnet.version != 4
        or not subnet.is_private
        or subnet.overlaps(ipaddress.ip_network(RUNNER_BRIDGE_SUBNET))
    ):
        raise ValueError("Daytona控制网络不能与固定runner-bridge子网重叠；不改变隔离设置")
    if config.get("networks") != NETWORKS:
        raise ValueError("仅允许固定内部网络和本机入口网络")
    if set(config["services"]) != KEEP:
        raise ValueError("存在未登记服务")
    region_name = environment(config["services"]["api"]).get("DEFAULT_REGION_NAME")
    if region_name is not None and not re.fullmatch(r"[a-zA-Z0-9_.-]{2,255}", region_name):
        raise ValueError("本机区域名称不能包含空格，必须满足固定上游约束")
    gateway = dict(config["services"]["gateway"])
    gateway.pop("image", None)
    expected_gateway = gateway_service()
    expected_gateway.pop("image")
    if gateway != expected_gateway:
        raise ValueError("本机入口配置不匹配；不能添加代理目标、可写文件或权限")
    for name, service in config["services"].items():
        if name != "gateway" and (
            service.get("ports") or service.get("networks") != ["daytona-network"]
        ):
            raise ValueError("后端只能连接内部网络，不能直接发布端口")
        image = service["image"]
        pinned = (
            re.fullmatch(r"sha256:[0-9a-f]{64}", image)
            if name in BUILT
            else re.fullmatch(
                re.escape(IMAGES[name].rsplit(":", 1)[0]) + r"@sha256:[0-9a-f]{64}", image
            )
        )
        if image != IMAGES[name] and not pinned:
            raise ValueError("镜像未固定")
        if any(not str(port).startswith("127.0.0.1:") for port in service.get("ports", [])):
            raise ValueError("服务端口不能暴露到局域网/公网")
        env = environment(service)
        for key, value in env.items():
            if isinstance(value, str) and (
                "https://" in value or "cloudfront.net" in value or "auth0.com" in value
            ):
                raise ValueError("本地服务配置含外部服务地址：" + key)
        if env.get("OTEL_ENABLED") != "false" or env.get("POSTHOG_API_KEY"):
            raise ValueError("遥测必须关闭")


def prepare(directory=HOME):
    directory = Path(directory).resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Daytona目录非空；不覆盖配置、密码或数据。使用status/up继续。")
    directory.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        directory.chmod(0o700)
    source = directory / "upstream"
    source.mkdir()
    command(["git", "init", "--template=", "."], cwd=source)
    command(
        [
            "git",
            "fetch",
            "--depth",
            "1",
            "https://github.com/daytonaio/daytona.git",
            DAYTONA_SOURCE,
        ],
        cwd=source,
    )
    command(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=source)
    if command(["git", "rev-parse", "HEAD"], cwd=source) != DAYTONA_SOURCE:
        raise ValueError("Daytona源码SHA不匹配")
    import bcrypt

    credentials = {
        k: secrets.token_hex(24)
        for k in (
            "password",
            "encryption_key",
            "salt",
            "database_password",
            "storage_password",
            "proxy_key",
            "runner_key",
            "health_key",
            "admin_key",
            "bootstrap_secret",
        )
    }
    credentials["email"] = "student@rnd.invalid"
    original = yaml.safe_load((source / "docker/docker-compose.yaml").read_text(encoding="utf-8"))
    config = render_compose(original, credentials, directory)
    dex = yaml.safe_load((source / "docker/dex/config.yaml").read_text(encoding="utf-8"))
    dex["staticPasswords"] = [
        {
            "email": credentials["email"],
            "username": "student",
            "userID": "rnd-local-student",
            "hash": bcrypt.hashpw(credentials["password"].encode(), bcrypt.gensalt()).decode(),
        }
    ]
    dex["staticClients"][0]["trustedPeers"] = ["rnd-bootstrap"]
    dex["staticClients"].append(
        {
            "id": "rnd-bootstrap",
            "name": "Local setup only",
            "secret": credentials["bootstrap_secret"],
            "redirectURIs": ["http://localhost:3009/callback"],
        }
    )
    dex["oauth2"] = {"passwordConnector": "local"}
    for name, data in (("compose.yaml", config), ("dex.yaml", dex)):
        path = directory / name
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        if os.name != "nt":
            path.chmod(0o600)
    private_json(directory / "credentials.json", credentials)
    private_json(
        directory / "installation.json",
        {
            "source_sha": DAYTONA_SOURCE,
            "release": "v" + DAYTONA_VERSION,
            "deployment": "local-development-only",
            "cloud_account": False,
        },
    )
    print("本机配置已生成；密码保存在本机 credentials.json，不会显示或提交到Git。")


def images(directory=HOME):
    directory = Path(directory)
    config = yaml.safe_load((directory / "compose.yaml").read_text(encoding="utf-8"))
    assert_local_compose(config)
    locked = directory / "compose.lock.yaml"
    if locked.exists():
        raise ValueError("镜像已锁定；不自动更新镜像或重写摘要")
    # Resolve installation dependencies before the expensive local source builds.
    result = {}
    for name, service in config["services"].items():
        if name in BUILT:
            continue
        docker("pull", service["image"])
        details = json.loads(docker("image", "inspect", service["image"]))[0]
        digests = details.get("RepoDigests") or []
        prefix = service["image"].rsplit(":", 1)[0] + "@sha256:"
        matching = [d for d in digests if d.startswith(prefix)]
        if not matching:
            raise ValueError("镜像没有匹配的仓库摘要，拒绝漂移：" + name)
        result[name] = {"tag": service["image"], "digest": matching[0]}
        service["image"] = matching[0]
    result.update(build_images(directory, command, docker))
    for name in BUILT:
        config["services"][name]["image"] = result[name]["image_id"]
    locked.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    if os.name != "nt":
        locked.chmod(0o600)
    private_json(directory / "images.lock.json", result)
    print("固定源码API/Proxy及校验后的Runner已在本机构建；镜像按实际sha256锁定。")


def compose(directory, *args, timeout=900):
    path = Path(directory) / "compose.lock.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert_local_compose(config)
    records = json.loads((Path(directory) / "images.lock.json").read_text(encoding="utf-8"))
    for name, service in config["services"].items():
        record = records[name]
        expected = record.get("image_id") if name in BUILT else record.get("digest")
        if service["image"] != expected or record["tag"] != IMAGES[name]:
            raise ValueError("本机镜像锁与Compose不一致：" + name)
    return docker("compose", "--project-name", PROJECT, "--file", str(path), *args, timeout=timeout)


def snapshot_stamp():
    return hashlib.sha256(
        (ROOT / "tools/daytona/Dockerfile").read_bytes()
        + (ROOT / "templates/product/uv.lock").read_bytes()
        + (ROOT / "templates/product/pyproject.toml").read_bytes()
    ).hexdigest()[:16]


def wait_for_registry():
    """Check real host-loopback reachability, not merely a running container state."""
    import httpx

    with httpx.Client(timeout=3, trust_env=False, follow_redirects=False) as client:
        for attempt in range(30):
            try:
                response = client.get("http://127.0.0.1:6000/v2/")
                response.raise_for_status()
                if response.json() != {}:
                    raise ValueError("Unexpected local registry response")
                return
            except httpx.HTTPError, ValueError:
                if attempt == 29:
                    raise RuntimeError(
                        "本机Registry不可达；检查gateway与registry日志，不切换云服务"
                    ) from None
                time.sleep(1)


def snapshot_image(directory=HOME):
    # Use a minimal build context: the platform, .env and user data cannot reach docker build.
    directory = Path(directory)
    context = directory / "snapshot-context"
    context.mkdir(exist_ok=True)
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / "templates/product" / name, context / name)
    shutil.copyfile(ROOT / "tools/daytona/Dockerfile", context / "Dockerfile")
    stamp = hashlib.sha256(
        b"".join(
            (context / name).read_bytes() for name in ("Dockerfile", "uv.lock", "pyproject.toml")
        )
    ).hexdigest()[:16]
    local_image = "127.0.0.1:6000/rnd-python:" + stamp
    if stamp != snapshot_stamp():
        raise ValueError("快照构建上下文与固定输入不一致")
    # Start ONLY the private registry. Build and publish before starting the control plane.
    compose(directory, "up", "-d", "--pull", "never", "registry", "gateway")
    wait_for_registry()
    docker("build", "--tag", local_image, str(context), timeout=1800)
    docker("push", local_image)
    # The runner's own Docker daemon resolves `registry` on the local Compose network.
    private_json(
        directory / "snapshot-image.json",
        {
            "image": "registry:6000/rnd-python:" + stamp,
            "snapshot": "rnd-python-" + stamp,
            "source_hash": stamp,
        },
    )
    print("Python3.14与锁定依赖已预热到本机镜像；沙箱验收使用offline安装。")


def up(directory=HOME):
    """A started container is not a ready API; reject early exits before authentication."""
    import httpx

    compose(directory, "up", "-d", "--pull", "never")
    endpoints = [
        "http://127.0.0.1:3000/api/config",
        "http://127.0.0.1:3003/",
        "http://127.0.0.1:5556/dex/.well-known/openid-configuration",
        "http://127.0.0.1:6000/v2/",
    ]
    with httpx.Client(timeout=3, trust_env=False, follow_redirects=False) as client:
        for attempt in range(90):
            raw = compose(directory, "ps", "--all", "--format", "json")
            rows = (
                json.loads(raw)
                if raw.lstrip().startswith("[")
                else [json.loads(line) for line in raw.splitlines() if line.strip()]
            )
            dead = [
                row["Service"] for row in rows if row.get("State") in {"exited", "dead", "removing"}
            ]
            if dead:
                raise RuntimeError("本机服务已退出，不能继续认证：" + ", ".join(sorted(dead)))
            running = {
                row["Service"]
                for row in rows
                if row.get("State") == "running" and row.get("Health", "") in {"", "healthy"}
            }
            if running == KEEP:
                try:
                    for endpoint in endpoints:
                        client.get(endpoint).raise_for_status()
                    print("本机服务、API、Runner与身份端点全部就绪；可以进入认证。")
                    return
                except httpx.HTTPError:
                    pass
            if attempt != 89:
                time.sleep(2)
    raise RuntimeError("本机服务健康检查超时；检查容器日志，未声明安装成功")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["prepare", "images", "up", "status", "down", "snapshot-image"]
    )
    parser.add_argument("--directory", type=Path, default=HOME)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.directory)
    elif args.action == "images":
        images(args.directory)
    elif args.action == "snapshot-image":
        snapshot_image(args.directory)
    elif args.action == "up":
        up(args.directory)
    else:
        commands = {"status": ["ps"], "down": ["down"]}
        print(compose(args.directory, *commands[args.action]))
    # `down` deliberately omits -v; no command here deletes persistent user volumes.


if __name__ == "__main__":
    from workbench.tools import ToolFailure

    try:
        main()
    except ToolFailure as error:
        print(
            getattr(error, "log", str(error))[-12000:]
        )  # Only public installation inputs; no runtime credentials.
        raise
    except subprocess.CalledProcessError as error:
        # Avoid a bare exit status hiding the actual installation failure.
        text = (error.stderr or b"").decode("utf-8", errors="replace")
        print(text[-12000:])
        raise
````
