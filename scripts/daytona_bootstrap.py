"""Authenticate against local Dex, create a local API key and register a warm snapshot.

The password grant is restricted to the loopback-bound development installation.
It is not a recommendation for public OAuth deployments. Tokens are never printed.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from uuid import UUID

import httpx
from pydantic import SecretStr

from scripts.daytona_local import HOME, private_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings
from workbench.tools import ToolFailure, run_command

PERMISSIONS = ["write:sandboxes", "delete:sandboxes", "write:snapshots", "delete:snapshots"]


def bootstrap(directory=HOME):
    directory = Path(directory)
    destination = directory / "workbench.env"
    if destination.exists():
        raise ValueError("本机API配置已存在，拒绝再创建密钥或覆盖")
    credentials = json.loads((directory / "credentials.json").read_text(encoding="utf-8"))
    install_loopback_guard()
    with httpx.Client(timeout=20, follow_redirects=False, trust_env=False) as http:
        for attempt in range(90):
            try:
                ready = http.get("http://127.0.0.1:5556/dex/.well-known/openid-configuration")
                ready.raise_for_status()
                break
            except httpx.HTTPError, ValueError:
                if attempt == 89:
                    raise RuntimeError("本机Dex未就绪；没有联系任何云端身份服务") from None
                time.sleep(2)
        response = http.post(
            "http://127.0.0.1:5556/dex/token",
            data={
                "grant_type": "password",
                "client_id": "rnd-bootstrap",
                "client_secret": credentials["bootstrap_secret"],
                "username": credentials["email"],
                "password": credentials["password"],
                "scope": "openid profile email audience:server:client_id:daytona",
            },
        )
        response.raise_for_status()
        headers = {"Authorization": "Bearer " + response.json()["id_token"]}
        for attempt in range(120):
            try:
                response = http.get("http://127.0.0.1:3000/api/organizations", headers=headers)
                response.raise_for_status()
                organizations = response.json()
                if not organizations:
                    raise ValueError("本机用户尚未建立个人组织")
                break
            except httpx.HTTPError, ValueError:
                if attempt == 119:
                    raise RuntimeError("本机API/身份认证未就绪；请查看本机容器日志") from None
                time.sleep(2)
        personal = [item for item in organizations if item.get("personal")]
        if len(personal) != 1:
            raise ValueError("个人组织不唯一，拒绝猜测密钥所属组织")
        headers["X-Daytona-Organization-ID"] = personal[0]["id"]
        configure_personal_region(http, headers, personal[0])
        response = http.post(
            "http://127.0.0.1:3000/api/api-keys",
            headers=headers,
            json={"name": "rnd-local-verification", "permissions": PERMISSIONS},
        )
        response.raise_for_status()
        key = response.json()["value"]
    # Persist a newly created key immediately, even if a later snapshot operation fails.
    # All values originate from this dedicated local installation, never a hosted account.
    private_json(directory / "api-key.json", {"value": key, "organization_id": personal[0]["id"]})
    write_environment(destination, key, "")
    print("本机认证通过，API密钥只写入本机受限文件；没有模型调用。")


def configure_personal_region(http, headers, organization):
    """Select only our local region through the authenticated public API.

    The server's DEFAULT_REGION_ID creates a region, but does not assign it to
    each new personal organization. Snapshot creation requires both settings.
    """
    organization_id = str(UUID(organization["id"]))
    if organization.get("personal") is not True:
        raise ValueError("只允许初始化当前本机用户的个人组织")
    current = organization.get("defaultRegionId")
    if current not in (None, "", "local"):
        raise ValueError("个人组织已选择其他区域；拒绝静默覆盖")
    if current != "local":
        response = http.patch(
            f"http://127.0.0.1:3000/api/organizations/{organization_id}/default-region",
            headers=headers,
            json={"defaultRegionId": "local"},
        )
        response.raise_for_status()
    response = http.get("http://127.0.0.1:3000/api/organizations", headers=headers)
    response.raise_for_status()
    confirmed = [row for row in response.json() if row.get("id") == organization_id]
    if len(confirmed) != 1 or confirmed[0].get("defaultRegionId") != "local":
        raise ValueError("本机个人组织默认区域未保存；没有创建API密钥")


def write_environment(path, key, snapshot):
    if any(char in key + snapshot for char in "\n\r\"'"):
        raise ValueError("本机配置值包含不允许的字符")
    Path(path).write_text(
        "SANDBOX_PROVIDER=daytona\nDAYTONA_ALLOW_LOCAL_EXECUTION=true\n"
        "DAYTONA_API_URL=http://127.0.0.1:3000/api\nDAYTONA_TARGET=local\n"
        f"DAYTONA_API_KEY={key}\nDAYTONA_SNAPSHOT={snapshot}\nTOOL_TIMEOUT=300\n",
        encoding="utf-8",
    )
    if os.name != "nt":
        Path(path).chmod(0o600)


def snapshot(directory=HOME):
    """Bound setup, SDK calls and cleanup in addition to the SDK operation timeout."""
    run_command(
        [
            sys.executable,
            "-m",
            "scripts.daytona_bootstrap",
            "snapshot-worker",
            "--directory",
            str(Path(directory).resolve()),
        ],
        ROOT,
        timeout=720,
        heartbeat="Local snapshot registration",
    )
    print("本机快照已就绪；全部操作在限时本机进程内完成。")


def snapshot_named(service, name):
    """Resolve an exact name through the pinned SDK's paginated listing.

    In v0.190.0 get(name) forwards the name to a UUID-only API route. Never
    interpret that server error as a missing snapshot or create a duplicate.
    A bounded scan must finish before absence can be established.
    """
    found = None
    for page in range(1, 101):
        result = service.list(page=page, limit=100)
        if result.page != page or not 0 <= result.total_pages <= 100:
            raise ValueError("本机快照分页结果异常；拒绝猜测快照是否存在")
        for item in result.items:
            if item.name == name:
                if found is not None:
                    raise ValueError("存在多个同名本机快照；拒绝猜测或覆盖")
                found = item
        if page >= result.total_pages:
            return found
    raise ValueError("本机快照分页未完成；没有创建快照")


def wait_default_snapshot(service, image, timeout=300):
    """Wait for the server's automatic image warm-up before a private snapshot.

    The pinned server starts a general snapshot asynchronously after Runner
    health. Two snapshots of that same image otherwise race on its unique
    in-progress Runner job. Readiness is observed, never fabricated or retried
    by deleting a failed snapshot. Listing/authentication errors propagate.
    """
    deadline = time.monotonic() + timeout
    while True:
        existing = snapshot_named(service, image)
        if existing is not None:
            if existing.image_name != image:
                raise ValueError("默认快照镜像来源不符；没有创建私有快照")
            state = str(getattr(existing.state, "value", existing.state)).lower()
            if state == "active":
                return existing
            if state in {"error", "failed", "build_failed", "inactive", "removing"}:
                raise ValueError("默认快照构建失败或不可用；检查本机Runner，不重复创建")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("默认快照尚未就绪；没有创建私有快照或写入就绪回执")
        time.sleep(min(2, remaining))


def snapshot_resources(metadata):
    import re

    from workbench.daytona_profiles import profile_key

    profile = metadata.get("profile")
    if profile is None:
        if not re.fullmatch(r"registry:6000/rnd-python:[a-f0-9]{16}", metadata["image"]):
            raise ValueError("快照只能引用本机登记的预热镜像")
        return {"cpu": 1, "memory": 2, "disk": 5}, True
    profile_key(profile["template"], {"database": profile["database"]})
    if not re.fullmatch(r"[a-f0-9]{64}", profile.get("dependency_identity", "")):
        raise ValueError("快照缺少完整依赖身份")
    family = "rnd-" + profile["template"]
    stamp = metadata["source_hash"]
    if (
        not re.fullmatch(r"[a-f0-9]{16}", stamp)
        or metadata["image"] != "registry:6000/" + family + ":" + stamp
        or metadata["snapshot"] != family + "-" + stamp
    ):
        raise ValueError("本机矩阵快照来源或名称不符")
    expected = {"cpu": 2, "memory": 10 if profile["template"] == "yudao-vben" else 4, "disk": 30}
    if metadata.get("resources") != expected or metadata.get("wait_for_default") is not False:
        raise ValueError("本机快照资源必须匹配登记的技术栈")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", metadata.get("image_id", "")):
        raise ValueError("缺少本机不可变镜像身份")
    return expected, False


def snapshot_worker(directory=HOME):
    directory = Path(directory)
    metadata = json.loads((directory / "snapshot-image.json").read_text(encoding="utf-8"))
    resources, wait_default = snapshot_resources(metadata)
    install_loopback_guard()
    from daytona import CreateSnapshotParams, Resources

    key = json.loads((directory / "api-key.json").read_text(encoding="utf-8"))["value"]
    settings = Settings(_env_file=None, daytona_api_key=SecretStr(key), daytona_target="local")
    client = client_for(settings)
    try:
        existing = snapshot_named(client.snapshot, metadata["snapshot"])
        if existing is None:
            # API/Runner health alone does not imply snapshot warm-up is complete.
            started = time.monotonic()
            if wait_default:
                wait_default_snapshot(client.snapshot, metadata["image"])
            remaining = max(1, min(600, int(650 - (time.monotonic() - started))))
            existing = client.snapshot.create(
                CreateSnapshotParams(
                    name=metadata["snapshot"],
                    image=metadata["image"],
                    region_id="local",
                    resources=Resources(**resources),
                ),
                timeout=remaining,
            )
        if existing.name != metadata["snapshot"] or existing.image_name != metadata["image"]:
            raise ValueError("同名快照的镜像来源不符；拒绝复用或覆盖")
        if str(getattr(existing.state, "value", existing.state)).lower() != "active":
            raise ValueError("同名本机快照尚未就绪，请检查状态；不静默覆盖")
        write_environment(directory / "workbench.env", key, metadata["snapshot"])
        print("本机快照已就绪；沙箱关卡禁止外网并使用离线依赖。")
    finally:
        close_client(client)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["auth", "snapshot", "snapshot-worker"])
    parser.add_argument("--directory", type=Path, default=HOME)
    args = parser.parse_args()
    {"auth": bootstrap, "snapshot": snapshot, "snapshot-worker": snapshot_worker}[args.action](
        args.directory
    )


if __name__ == "__main__":
    try:
        main()
    except ToolFailure as error:
        directory = HOME
        if "--directory" in sys.argv:
            directory = Path(sys.argv[sys.argv.index("--directory") + 1])
        log = getattr(error, "log", str(error))
        for name in ("credentials.json", "api-key.json"):
            path = directory / name
            if path.exists():
                for value in json.loads(path.read_text(encoding="utf-8")).values():
                    if isinstance(value, str) and len(value) > 5:
                        log = log.replace(value, "[REDACTED]")
        print(log[-12000:])
        raise SystemExit("本机快照登记失败；未写入就绪回执") from None
