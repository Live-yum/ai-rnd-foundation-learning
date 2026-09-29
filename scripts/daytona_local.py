"""Install the pinned, development-only Daytona stack on this machine.

Only `prepare` and `images`/`snapshot-image` fetch public software dependencies.
Runtime API, authentication, storage, registry and execution remain local. No
Daytona account, Auth0 tenant, hosted runner or hosted telemetry is involved.
"""

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path

import yaml

from workbench.local_only import DAYTONA_SOURCE, DAYTONA_VERSION
from workbench.settings import ROOT
from workbench.tools import clean_env

HOME = ROOT / ".data/daytona-local"
PROJECT = "rnd-daytona-local"
KEEP = {"api", "proxy", "runner", "db", "redis", "dex", "registry", "minio", "maildev"}
IMAGES = {
    "api": f"ghcr.io/daytonaio/daytona-api:v{DAYTONA_VERSION}",
    "proxy": f"ghcr.io/daytonaio/daytona-proxy:v{DAYTONA_VERSION}",
    "runner": f"ghcr.io/daytonaio/daytona-runner:v{DAYTONA_VERSION}",
    "db": "postgres:18",
    "redis": "redis:7.4.2",
    "dex": "dexidp/dex:v2.42.0",
    "registry": "registry:2.8.2",
    "minio": "minio/minio:RELEASE.2025-04-22T22-12-26Z",
    "maildev": "maildev/maildev:2.2.1",
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


def render_compose(original, credentials, directory):
    """Transform upstream configuration; never execute instructions from its README."""
    config = copy.deepcopy(original)
    config["name"] = PROJECT
    config["services"] = {name: value for name, value in config["services"].items() if name in KEEP}
    if set(config["services"]) != KEEP:
        raise ValueError("固定Daytona源码的服务集合不符，拒绝套用不兼容配置")
    config["networks"] = {"daytona-network": {"driver": "bridge"}}
    for name, service in config["services"].items():
        service["image"] = IMAGES[name]
        service["restart"] = "no"
        service.pop("build", None)
        service["ports"] = ["127.0.0.1:" + str(port) for port in service.get("ports", [])]
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
        DEFAULT_REGION_ID="local",
        DEFAULT_REGION_NAME="Local computer",
        DEFAULT_RUNNER_NAME="local-docker",
        OIDC_MANAGEMENT_API_ENABLED="false",
        # Match Dex's signed issuer, but obtain JWKS via its private Docker hostname.
        PUBLIC_OIDC_DOMAIN="http://localhost:5556/dex",
        DEFAULT_SNAPSHOT="daytonaio/sandbox:0.5.0-slim",
    )
    config["services"]["proxy"]["environment"].update(PROXY_API_KEY=credentials["proxy_key"])
    config["services"]["runner"]["environment"].update(
        DAYTONA_RUNNER_TOKEN=credentials["runner_key"],
        AWS_SECRET_ACCESS_KEY=credentials["storage_password"],
        SSH_GATEWAY_ENABLE="false",
    )
    config["services"]["db"]["environment"]["POSTGRES_PASSWORD"] = credentials["database_password"]
    config["services"]["minio"]["environment"]["MINIO_ROOT_PASSWORD"] = credentials[
        "storage_password"
    ]
    config["services"]["dex"]["volumes"] = [
        str(Path(directory).resolve() / "dex.yaml") + ":/etc/dex/config.yaml:ro",
        "dex_db:/var/dex",
    ]
    # Do not persist unneeded optional SSH/observability services or their test keys.
    assert_local_compose(config)
    return config


def assert_local_compose(config):
    if set(config["services"]) != KEEP:
        raise ValueError("存在未登记服务")
    for name, service in config["services"].items():
        if service["image"] != IMAGES[name] and "@sha256:" not in service["image"]:
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
    result = {}
    for name, service in config["services"].items():
        docker("pull", service["image"])
        details = json.loads(docker("image", "inspect", service["image"]))[0]
        digests = details.get("RepoDigests") or []
        prefix = service["image"].rsplit(":", 1)[0] + "@sha256:"
        matching = [d for d in digests if d.startswith(prefix)]
        if not matching:
            raise ValueError("镜像没有匹配的仓库摘要，拒绝漂移：" + name)
        result[name] = {"tag": service["image"], "digest": matching[0]}
        service["image"] = matching[0]
    locked.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    if os.name != "nt":
        locked.chmod(0o600)
    private_json(directory / "images.lock.json", result)
    print("镜像下载并按实际sha256锁定；未使用latest回退。")


def compose(directory, *args, timeout=900):
    path = Path(directory) / "compose.lock.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert_local_compose(config)
    return docker("compose", "--project-name", PROJECT, "--file", str(path), *args, timeout=timeout)


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
    else:
        commands = {"up": ["up", "-d", "--pull", "never"], "status": ["ps"], "down": ["down"]}
        print(compose(args.directory, *commands[args.action]))
    # `down` deliberately omits -v; no command here deletes persistent user volumes.


if __name__ == "__main__":
    main()
