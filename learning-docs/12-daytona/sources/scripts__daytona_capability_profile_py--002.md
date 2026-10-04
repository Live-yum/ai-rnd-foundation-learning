# scripts/daytona_capability_profile.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__daytona_capability_profile_py--001.md)

**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_capability_profile；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_build`、`workbench.capability_isolation`、`workbench.local_only`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `inspect_created_sandbox`（L713–L940）：接收`directory`、`sandbox_id`、`require_resources`、`selection`。 源码说明：Inspect only the newly owned UUID inside the verified profile Runner. Upstream create.go names the Docker container sandboxDto.Id. No shell, caller-provided Docker options, executable, or general comm。 控制顺序：L722按`not isinstance(sandbox_id, str) or str(UUID(sandbox_id)) != sandbox_id`分支；L723抛异常，停止当前正常路径；L728按`native`分支；L733按`not re.fullmatch(r"[a-f0-9]{64}", runner_id)`分支；L734抛异常，停止当前正常路径；L739按`len(rows) != 1`分支；L740抛异常，停止当前正常路径；L745按`runner.get("Image") != record["runner"]["image_id"] or runner.get("State", {}).get("R…`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`str`、`UUID`、`ContainerInspectionRejected`、`require_profile`、`selection.get`、`require_native_profile`、`compose(directory, "ps", "--quiet", "runner").strip`、`compose`等。 返回路径：L940的`receipt`。
- `up`（L943–L981）：接收`directory`。 控制顺序：L955遍历`range(90)`；L962按`any(row.get("State") in {"exited", "dead", "removing"} for row in rows)`分支；L963抛异常，停止当前正常路径；L969按`ready == local.KEEP`分支；L971遍历`endpoints`；L979按`attempt < 89`分支；L981抛异常，停止当前正常路径。 调用`require_profile`、`compose`、`httpx.Client`、`range`、`raw.lstrip().startswith`、`raw.lstrip`、`json.loads`、`raw.splitlines`、`line.strip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L984–L997）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L989按`args.action == "prepare"`分支；L991按`args.action == "up"`分支；L993按`args.action == "check"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`prepare`、`up`、`require_profile`、`print`、`compose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_capability_profile.py`；**本文件共有 2 段**。本段覆盖源文件 L713–L1005。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12266`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_capability_profile.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "e42512ea28eb052ccfeba87d7b3f3cd36310177729c7b4f380c6a57b5d26fa9c"} -->
````python
# scripts/daytona_capability_profile.py
def inspect_created_sandbox(directory, sandbox_id, *, require_resources=False, selection=None):
    """Inspect only the newly owned UUID inside the verified profile Runner.

    Upstream create.go names the Docker container sandboxDto.Id. No shell,
    caller-provided Docker options, executable, or general command is accepted.
    The receipt contains no environment, paths, credentials, or user content.
    """
    from uuid import UUID

    if not isinstance(sandbox_id, str) or str(UUID(sandbox_id)) != sandbox_id:
        raise ContainerInspectionRejected(
            "Owned sandbox must have one canonical UUID", category="sandbox_identity"
        )
    record = require_profile(directory)
    native = selection is not None and selection.get("template") == "fastapiadmin"
    if native:
        from scripts.daytona_native_capability_profile import require_native_profile

        record = require_native_profile(directory)
    runner_id = compose(directory, "ps", "--quiet", "runner").strip()
    if not re.fullmatch(r"[a-f0-9]{64}", runner_id):
        raise ContainerInspectionRejected(
            "Profile requires exactly one running Runner container",
            category="runner_unavailable",
        )
    rows = json.loads(local.docker("container", "inspect", runner_id))
    if len(rows) != 1:
        raise ContainerInspectionRejected(
            "Profile Runner container identity is ambiguous", category="runner_identity"
        )
    runner = rows[0]
    labels = runner.get("Config", {}).get("Labels", {})
    if (
        runner.get("Image") != record["runner"]["image_id"]
        or runner.get("State", {}).get("Running") is not True
        or labels.get("com.docker.compose.project") != PROJECT
        or labels.get("com.docker.compose.service") != "runner"
        or "USE_SNAPSHOT_ENTRYPOINT=false" not in runner.get("Config", {}).get("Env", [])
        or runner.get("Config", {}).get("Entrypoint")
        != ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"]
        or runner.get("Config", {}).get("Cmd")
    ):
        raise ContainerInspectionRejected(
            "Running Runner does not match the owned profile",
            category="runner_identity",
        )
    security = json.loads(
        local.docker(
            "exec",
            runner_id,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "info",
            "--format",
            "{{json .SecurityOptions}}",
            timeout=30,
        )
    )
    if not isinstance(security, list) or "name=seccomp,profile=builtin" not in security:
        raise ContainerInspectionRejected(
            "Inner Docker must report its enabled built-in seccomp filter",
            category="engine_seccomp",
        )
    rows = json.loads(
        local.docker(
            "exec",
            runner_id,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "inspect",
            sandbox_id,
            timeout=30,
        )
    )
    if len(rows) != 1:
        raise ContainerInspectionRejected(
            "Owned application container identity is ambiguous",
            category="container_identity",
        )
    container = rows[0]
    config, host = container.get("Config", {}), container.get("HostConfig", {})
    if require_resources:
        networks = container.get("NetworkSettings", {}).get("Networks", {})
        if set(networks) != {"runner-bridge"} or host.get("NetworkMode") != "runner-bridge":
            raise ContainerInspectionRejected(
                "Custom source must have only the exact owned Runner bridge",
                category="sandbox_network",
                facts={
                    "network_mode": host.get("NetworkMode"),
                    "network_count": len(networks),
                    "runner_bridge_attached": "runner-bridge" in networks,
                },
            )
        bridge = json.loads(
            local.docker(
                "exec",
                runner_id,
                "docker",
                "--host",
                "unix:///var/run/docker.sock",
                "network",
                "inspect",
                "runner-bridge",
                timeout=30,
            )
        )
        if (
            len(bridge) != 1
            or bridge[0].get("EnableIPv6") is not False
            or bridge[0].get("Driver") != "bridge"
            or {item.get("Subnet") for item in bridge[0].get("IPAM", {}).get("Config", [])}
            != {local.RUNNER_BRIDGE_SUBNET}
        ):
            actual = bridge[0] if len(bridge) == 1 else {}
            ipam = actual.get("IPAM")
            subnets = ipam.get("Config") if isinstance(ipam, dict) else None
            raise ContainerInspectionRejected(
                "Runner bridge address/IPv6 policy differs from the reviewed profile",
                category="runner_bridge",
                facts={
                    "bridge_count": len(bridge),
                    "bridge_ipv6_disabled": actual.get("EnableIPv6") is False,
                    "bridge_driver_matches": actual.get("Driver") == "bridge",
                    "bridge_subnets_match": isinstance(subnets, list)
                    and bool(subnets)
                    and all(
                        isinstance(item, dict) and item.get("Subnet") == local.RUNNER_BRIDGE_SUBNET
                        for item in subnets
                    ),
                },
            )
    if (
        container.get("Name") != "/" + sandbox_id
        or container.get("Image") != record["snapshot"]["image_id"]
        or container.get("State", {}).get("Running") is not True
        or config.get("User") != "0:0"
        or config.get("WorkingDir") != CONTROL_WORKDIR
        or config.get("Entrypoint") != ["/usr/local/bin/daytona"]
        or config.get("Cmd")
        or host.get("Privileged") is not False
        or host.get("CapAdd")
        or host.get("SecurityOpt")
        or host.get("Devices")
        or host.get("DeviceRequests")
        or host.get("PidMode") not in (None, "")
        or host.get("IpcMode") not in (None, "", "private")
        or host.get("NetworkMode") in {"host", "none"}
    ):
        raise ContainerInspectionRejected(
            "Created application container does not match the unprivileged profile",
            category="container_policy",
        )
    expected = {
        "/usr/local/bin/daytona": "/usr/local/bin/.tmp/binaries/daemon-amd64",
        "/usr/local/lib/daytona-computer-use": "/usr/local/bin/.tmp/binaries/daytona-computer-use",
    }
    mounts = container.get("Mounts", [])
    if require_resources:
        tmpfs = [mount for mount in mounts if mount.get("Type") == "tmpfs"]
        if len(tmpfs) > 1 or any(
            mount.get("Destination") != "/tmp"
            or mount.get("RW") is not True
            or mount.get("Source") not in (None, "")
            for mount in tmpfs
        ):
            raise ContainerInspectionRejected(
                "Only the exact bounded application tmpfs is permitted",
                category="tmpfs_mounts",
                facts={
                    "mount_count": len(tmpfs),
                    "mount_destinations_match": all(m.get("Destination") == "/tmp" for m in tmpfs),
                    "mount_writable_matches": all(m.get("RW") is True for m in tmpfs),
                    "mount_sources_match": all(m.get("Source") in (None, "") for m in tmpfs),
                },
            )
        mounts = [mount for mount in mounts if mount.get("Type") != "tmpfs"]
    if (
        len(mounts) != len(expected)
        or any(
            mount.get("Type") != "bind"
            or mount.get("RW") is not False
            or expected.get(mount.get("Destination")) != mount.get("Source")
            for mount in mounts
        )
        or {mount.get("Destination") for mount in mounts} != set(expected)
    ):
        destinations = [m.get("Destination") for m in mounts if isinstance(m, dict)]
        raise ContainerInspectionRejected(
            "Application mounts must be only the two trusted read-only binaries",
            category="binary_mounts",
            facts={
                "mount_count": len(mounts),
                "mount_types_match": all(
                    isinstance(m, dict) and m.get("Type") == "bind" for m in mounts
                ),
                "mount_readonly_matches": all(
                    isinstance(m, dict) and m.get("RW") is False for m in mounts
                ),
                "mount_destinations_match": len(destinations) == len(mounts)
                and all(isinstance(value, str) for value in destinations)
                and set(destinations) == set(expected),
                "mount_sources_match": all(
                    isinstance(m, dict)
                    and isinstance(m.get("Destination"), str)
                    and expected.get(m["Destination"]) == m.get("Source")
                    for m in mounts
                ),
            },
        )
    receipt = {
        "profile": record["profile"],
        "sandbox_id": sandbox_id,
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "dependency_manifest": copy.deepcopy(record["snapshot"]["dependency_manifest"]),
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
    }
    if require_resources:
        receipt["resource_limits"] = require_execution_resources(host, native=native)
    return receipt


def up(directory=HOME):
    import httpx

    require_profile(directory)
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
            if any(row.get("State") in {"exited", "dead", "removing"} for row in rows):
                raise RuntimeError("Capability profile service exited before readiness")
            ready = {
                row["Service"]
                for row in rows
                if row.get("State") == "running" and row.get("Health", "") in {"", "healthy"}
            }
            if ready == local.KEEP:
                try:
                    for endpoint in endpoints:
                        client.get(endpoint).raise_for_status()
                    print(
                        "Dedicated capability API, Runner and local identity endpoints are ready."
                    )
                    return
                except httpx.HTTPError:
                    pass
            if attempt < 89:
                time.sleep(2)
    raise RuntimeError("Capability profile readiness timed out; no passing proof was produced")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "up", "check", "status", "down"])
    parser.add_argument("--directory", type=Path, default=HOME)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.directory)
    elif args.action == "up":
        up(args.directory)
    elif args.action == "check":
        require_profile(args.directory)
        print("Profile image and recipe identities match; application isolation is not yet proven.")
    else:
        print(compose(args.directory, *({"status": ["ps"], "down": ["down"]}[args.action])))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print((error.stderr or b"").decode("utf-8", errors="replace")[-12000:])
        raise
````
