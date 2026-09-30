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

import httpx
from pydantic import SecretStr

from scripts.daytona_local import HOME, private_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for
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
    """Bound the whole operation: this fixed SDK does not enforce create(timeout)."""
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


def snapshot_worker(directory=HOME):
    directory = Path(directory)
    metadata = json.loads((directory / "snapshot-image.json").read_text(encoding="utf-8"))
    if not metadata["image"].startswith("registry:6000/rnd-python:"):
        raise ValueError("快照只能引用本机登记的预热镜像")
    install_loopback_guard()
    from daytona import CreateSnapshotParams, Resources
    from daytona.common.errors import DaytonaNotFoundError

    key = json.loads((directory / "api-key.json").read_text(encoding="utf-8"))["value"]
    settings = Settings(_env_file=None, daytona_api_key=SecretStr(key), daytona_target="local")
    client = client_for(settings)
    try:
        try:
            existing = client.snapshot.get(metadata["snapshot"])
            if str(existing.state).lower() != "active":
                raise ValueError("已存在同名但未就绪的本机快照，请检查状态；不静默覆盖")
        except DaytonaNotFoundError:
            client.snapshot.create(
                CreateSnapshotParams(
                    name=metadata["snapshot"],
                    image=metadata["image"],
                    region_id="local",
                    resources=Resources(cpu=1, memory=2, disk=5),
                ),
                timeout=600,
            )
        write_environment(directory / "workbench.env", key, metadata["snapshot"])
        print("本机快照已就绪；沙箱关卡禁止外网并使用离线依赖。")
    finally:
        client.close()


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
        log = error.log
        for name in ("credentials.json", "api-key.json"):
            path = directory / name
            if path.exists():
                for value in json.loads(path.read_text(encoding="utf-8")).values():
                    if isinstance(value, str) and len(value) > 5:
                        log = log.replace(value, "[REDACTED]")
        print(log[-12000:])
        raise SystemExit("本机快照登记失败；未写入就绪回执") from None
