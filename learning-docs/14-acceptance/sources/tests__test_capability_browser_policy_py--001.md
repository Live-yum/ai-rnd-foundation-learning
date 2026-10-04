# tests/test_capability_browser_policy.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_test_controller`（L17–L19）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fixture`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `approved`（L22–L30）：接收`monkeypatch`。 控制顺序：L23遍历`{ "CAPABILITY_BROWSER_APPROVED_POLICY": policy.POLICY_SHA256, "GI…`。 调用`{ "CAPABILITY_BROWSER_APPROVED_POLICY": policy.POLICY_SHA256, "GI…`、`monkeypatch.setenv`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `target`（L33–L56）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L34的`( { "Server": { "Version": "28.0.4", "Os": "linux", "Arch": "amd64", "KernelVersion": "6.1…`。
- `test_no_implicit_activation`（L59–L62）：接收`monkeypatch`。 控制顺序：L61断言`policy.selected_policy() is None`；L62断言`not any("seccomp=" in v for v in isolation.worker_command(IMAGE, NAME))`。 调用`monkeypatch.delenv`、`policy.selected_policy`、`any`、`isolation.worker_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_scope_rejects_before_create`（L76–L81）：接收`monkeypatch`、`key`、`value`。 调用`approved`、`monkeypatch.setenv`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`isolation.worker_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_policy_rejected`（L84–L91）：接收`monkeypatch`、`tmp_path`。 调用`approved`、`path.parent.mkdir`、`path.write_text`、`monkeypatch.setattr`、`pytest.raises`、`policy.selected_policy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_or_wrong_target_rejected`（L111–L116）：接收`section`、`key`、`value`。 调用`copy.deepcopy`、`target`、`pytest.raises`、`policy.validate_target`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_target_records_observed_versions`（L119–L122）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L121断言`got["policy_sha256"] == policy.POLICY_SHA256`；L122断言`got["runc"] == "1.2.5" and got["kernel"] == "6.17.0-1022-azure"`。 调用`policy.validate_target`、`target`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_command_requires_runtime_before_create`（L125–L132）：接收`monkeypatch`。 控制顺序：L130断言`seen == [IMAGE]`；L131断言`"--security-opt=seccomp=" + str(policy.selected_policy()) in args`；L132断言`"--network=none" in args and "--cap-drop=ALL" in args`。 调用`approved`、`monkeypatch.setattr`、`seen.append`、`isolation.worker_command`、`str`、`policy.selected_policy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspect_matches_inline_content_not_path_or_unconfined`（L135–L148）：接收`monkeypatch`。 控制顺序：L139断言`policy.security_options_match(good)`；L140遍历`( ["no-new-privileges:true"], good + ["apparmor=unconfined"], ["n…`；L146断言`not policy.security_options_match(bad)`；L148断言`not policy.security_options_match([good[0], "seccomp=" + json.dumps(content)])`。 调用`approved`、`json.loads`、`policy.selected_policy().read_bytes`、`policy.selected_policy`、`json.dumps`、`policy.security_options_match`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_requires_matching_compiler_provenance`（L151–L173）：接收`monkeypatch`、`tmp_path`。 控制顺序：L165断言`policy.runtime_identity(IMAGE)["libseccomp_observed_matching_build"] == "2.5.5"`。 调用`binary.write_bytes`、`monkeypatch.setattr`、`approved`、`iter`、`target`、`next`、`SimpleNamespace`、`policy.runtime_identity`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `worker_inspection`（L176–L205）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`policy.selected_policy().read_text`、`policy.selected_policy`。 返回路径：L177的`[ { "Image": IMAGE, "AppArmorProfile": "docker-default", "Config": {"User": "1000:1000", "…`。
- `test_effective_policy_and_outer_boundary_required`（L220–L227）：接收`monkeypatch`、`section`、`key`、`value`。 调用`approved`、`worker_inspection`、`isolation.require_worker_inspection`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `raw_proof`（L230–L251）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L232遍历`policy.RAW_CHECKS`。 调用`name.endswith`、`name.startswith`、`dict.fromkeys`。 返回路径：L244的`{ "protocol": "browser-seccomp-transport-v1", "architecture": "native-amd64", "expected_pr…`。
- `test_complete_raw_proof`（L254–L255）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L255断言`policy.require_raw_probe(raw_proof()) is True`。 调用`policy.require_raw_probe`、`raw_proof`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_raw_proof_rejected`（L270–L274）：接收`mutation`。 调用`raw_proof`、`mutation`、`pytest.raises`、`policy.require_raw_probe`、`pytest.mark.parametrize`、`r.update`、`r["checks"].pop`、`r["checks"].update`、`r["observations"]["mount_denied"].update`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_selected_receipt_requires_exact_runtime_and_raw_proof`（L277–L332）：接收`monkeypatch`、`tmp_path`。 控制顺序：L320断言`isolation.require_browser_acceptance(IMAGE) == IMAGE`；L321遍历`( lambda r: r.update(protocol="offline-browser-isolation-v2"), la…`。 调用`approved`、`policy.validate_target`、`target`、`monkeypatch.setattr`、`isolation.browser_source_identity`、`isolation.image_source_identity`、`dict.fromkeys`、`path.write_text`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_policy.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L332。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11606`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_policy.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "31e8b204a8cbe61164def1d65ea7fd0dba14c554fb83628a45b01d7675564b33"} -->
````python
# tests/test_capability_browser_policy.py
"""Approved Actions selector tests; no daemon or policy is executed."""

import copy
import json
from types import SimpleNamespace

import pytest

from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy

IMAGE = "sha256:" + "a" * 64
NAME = "rnd-browser-" + "b" * 32


@pytest.fixture(autouse=True)
def native_test_controller(monkeypatch):
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")


def approved(monkeypatch):
    for key, value in {
        "CAPABILITY_BROWSER_APPROVED_POLICY": policy.POLICY_SHA256,
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "Live-yum/ai-rnd-foundation-learning",
        "GITHUB_WORKFLOW": "Offline candidate browser isolation",
        "GITHUB_RUN_ID": "12345",
    }.items():
        monkeypatch.setenv(key, value)


def target():
    return (
        {
            "Server": {
                "Version": "28.0.4",
                "Os": "linux",
                "Arch": "amd64",
                "KernelVersion": "6.17.0-1022-azure",
                "Components": [
                    {"Name": "runc", "Version": "1.2.5", "Details": {"GitCommit": "abc123"}},
                    {"Name": "containerd", "Version": "1.7.25"},
                ],
            }
        },
        {
            "OSType": "linux",
            "Architecture": "x86_64",
            "DefaultRuntime": "runc",
            "Runtimes": {"runc": {"path": "runc"}},
            "DockerRootDir": "/var/lib/docker",
            "SecurityOptions": ["name=apparmor", "name=seccomp,profile=builtin"],
        },
        [{"Id": IMAGE, "Os": "linux", "Architecture": "amd64", "Config": {"User": "1000:1000"}}],
    )


def test_no_implicit_activation(monkeypatch):
    monkeypatch.delenv("CAPABILITY_BROWSER_APPROVED_POLICY", raising=False)
    assert policy.selected_policy() is None
    assert not any("seccomp=" in v for v in isolation.worker_command(IMAGE, NAME))


@pytest.mark.parametrize(
    "key,value",
    [
        ("CAPABILITY_BROWSER_APPROVED_POLICY", "/tmp/arbitrary.json"),
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_WORKFLOW", "Python 3.14 acceptance"),
        ("GITHUB_RUN_ID", ""),
        ("GITHUB_RUN_ID", "../1"),
    ],
)
def test_scope_rejects_before_create(monkeypatch, key, value):
    approved(monkeypatch)
    monkeypatch.setenv(key, value)
    monkeypatch.setattr(policy.subprocess, "run", lambda *a, **k: pytest.fail("subprocess reached"))
    with pytest.raises(ValueError):
        isolation.worker_command(IMAGE, NAME)


def test_changed_policy_rejected(monkeypatch, tmp_path):
    approved(monkeypatch)
    path = tmp_path / policy.POLICY_SOURCE
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    monkeypatch.setattr(policy, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="bytes changed"):
        policy.selected_policy()


@pytest.mark.parametrize(
    "section,key,value",
    [
        (0, "Version", "28.0.5"),
        (0, "Arch", "arm64"),
        (0, "Os", "windows"),
        (0, "KernelVersion", None),
        (0, "Components", []),
        (1, "DefaultRuntime", "other"),
        (1, "Architecture", "aarch64"),
        (1, "SecurityOptions", []),
        (1, "DockerRootDir", "/other"),
        (2, "Id", "sha256:" + "b" * 64),
        (2, "Architecture", "arm64"),
        (2, "Config", {"User": "0"}),
    ],
)
def test_unknown_or_wrong_target_rejected(section, key, value):
    values = copy.deepcopy(target())
    selected = values[0]["Server"] if section == 0 else values[1] if section == 1 else values[2][0]
    selected[key] = value
    with pytest.raises(ValueError):
        policy.validate_target(*values, IMAGE)


def test_target_records_observed_versions():
    got = policy.validate_target(*target(), IMAGE)
    assert got["policy_sha256"] == policy.POLICY_SHA256
    assert got["runc"] == "1.2.5" and got["kernel"] == "6.17.0-1022-azure"


def test_command_requires_runtime_before_create(monkeypatch):
    approved(monkeypatch)
    seen = []
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: seen.append(image))
    args = isolation.worker_command(IMAGE, NAME)
    assert seen == [IMAGE]
    assert "--security-opt=seccomp=" + str(policy.selected_policy()) in args
    assert "--network=none" in args and "--cap-drop=ALL" in args


def test_inspect_matches_inline_content_not_path_or_unconfined(monkeypatch):
    approved(monkeypatch)
    content = json.loads(policy.selected_policy().read_bytes())
    good = ["no-new-privileges:true", "apparmor=docker-default", "seccomp=" + json.dumps(content)]
    assert policy.security_options_match(good)
    for bad in (
        ["no-new-privileges:true"],
        good + ["apparmor=unconfined"],
        ["no-new-privileges:true", "seccomp=unconfined"],
        ["no-new-privileges:true", "seccomp=" + str(policy.selected_policy())],
    ):
        assert not policy.security_options_match(bad)
    content["defaultAction"] = "SCMP_ACT_ALLOW"
    assert not policy.security_options_match([good[0], "seccomp=" + json.dumps(content)])


def test_runtime_requires_matching_compiler_provenance(monkeypatch, tmp_path):
    binary = tmp_path / "runc"
    binary.write_bytes(b"synthetic-runc-build")
    monkeypatch.setattr(policy, "Path", lambda path: binary)
    approved(monkeypatch)
    values = iter(target())
    monkeypatch.setattr(policy, "_read_json", lambda args: next(values))
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=b"runc version 1.2.5\ncommit: abc123\nlibseccomp: 2.5.5\n"
        ),
    )
    assert policy.runtime_identity(IMAGE)["libseccomp_observed_matching_build"] == "2.5.5"
    values = iter(target())
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=b"runc version 1.3.0\n"),
    )
    with pytest.raises(ValueError, match="provenance mismatch"):
        policy.runtime_identity(IMAGE)


def worker_inspection():
    return [
        {
            "Image": IMAGE,
            "AppArmorProfile": "docker-default",
            "Config": {"User": "1000:1000", "Env": ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1"]},
            "Mounts": [],
            "HostConfig": {
                "NetworkMode": "none",
                "ReadonlyRootfs": True,
                "Privileged": False,
                "NanoCpus": 1000000000,
                "Memory": 805306368,
                "MemorySwap": 805306368,
                "PidsLimit": 128,
                "IpcMode": "private",
                "CgroupnsMode": "private",
                "ShmSize": 67108864,
                "CapDrop": ["ALL"],
                "CapAdd": [],
                "SecurityOpt": [
                    "no-new-privileges:true",
                    "apparmor=docker-default",
                    "seccomp=" + policy.selected_policy().read_text(),
                ],
                "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=134217728,mode=1777"},
                "LogConfig": {"Type": "none"},
            },
        }
    ]


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("record", "AppArmorProfile", "unconfined"),
        ("host", "CapAdd", ["SYS_ADMIN"]),
        ("host", "NetworkMode", "host"),
        ("host", "Privileged", True),
        ("host", "SecurityOpt", ["no-new-privileges:true"]),
        ("host", "Binds", ["/:/host"]),
        ("host", "PidMode", "host"),
    ],
)
def test_effective_policy_and_outer_boundary_required(monkeypatch, section, key, value):
    approved(monkeypatch)
    data = worker_inspection()
    isolation.require_worker_inspection(data, IMAGE)
    record = data[0] if section == "record" else data[0]["HostConfig"]
    record[key] = value
    with pytest.raises(ValueError):
        isolation.require_worker_inspection(data, IMAGE)


def raw_proof():
    observations = {}
    for name in policy.RAW_CHECKS:
        killed = name.endswith("_killed")
        error = 0 if name.startswith("native_") or killed else 38 if name == "clone3_enosys" else 1
        observations[name] = {
            "returned": not killed,
            "return": -error,
            "errno": error,
            "signal": 31 if killed else 0,
            "exit_status": 0 if "extra_" in name else -1,
            "setup_errno": 0,
            "timed_out": False,
        }
    return {
        "protocol": "browser-seccomp-transport-v1",
        "architecture": "native-amd64",
        "expected_profile_sha256": policy.POLICY_SHA256,
        "passed": True,
        "checks": dict.fromkeys(policy.RAW_CHECKS, True),
        "observations": observations,
    }


def test_complete_raw_proof():
    assert policy.require_raw_probe(raw_proof()) is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(passed=1),
        lambda r: r.update(expected_profile_sha256="wrong"),
        lambda r: r["checks"].pop("clone3_enosys"),
        lambda r: r["checks"].update(mount_denied=False),
        lambda r: r["checks"].update(mount_denied=1),
        lambda r: r["observations"]["mount_denied"].update(timed_out=True),
        lambda r: r["observations"].pop("mount_denied"),
    ],
)
def test_incomplete_raw_proof_rejected(mutation):
    data = raw_proof()
    mutation(data)
    with pytest.raises(ValueError):
        policy.require_raw_probe(data)


def test_selected_receipt_requires_exact_runtime_and_raw_proof(monkeypatch, tmp_path):
    approved(monkeypatch)
    runtime = policy.validate_target(*target(), IMAGE)
    runtime["libseccomp"] = "2.5.5"
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: runtime)
    path = tmp_path / "receipt.json"
    monkeypatch.setattr(isolation, "BROWSER_ACCEPTANCE", path)
    record = {
        "protocol": "offline-browser-isolation-v3",
        "passed": True,
        "image": IMAGE,
        "mocked": False,
        "runtime": runtime,
        "sources": isolation.browser_source_identity(),
        "image_sources": isolation.image_source_identity(),
        "checks": {
            "kernel_and_network": dict.fromkeys(
                [
                    "passed",
                    "kernel_resource_limits",
                    "network_none",
                    "tmpfs_exhaustion",
                    "pid_exhaustion",
                    "readonly_root",
                    "browser_build",
                    "apparmor_enforced",
                ],
                True,
            ),
            **dict.fromkeys(
                [
                    "positive",
                    "error",
                    "abuse",
                    "failure_cleanup",
                    "memory_exhaustion",
                    "raw_syscalls",
                ],
                True,
            ),
        },
    }
    path.write_text(json.dumps(record))
    assert isolation.require_browser_acceptance(IMAGE) == IMAGE
    for mutation in (
        lambda r: r.update(protocol="offline-browser-isolation-v2"),
        lambda r: r["runtime"].update(policy_sha256=None),
        lambda r: r["runtime"].update(kernel="other"),
        lambda r: r["checks"].pop("raw_syscalls"),
        lambda r: r["checks"].update(raw_syscalls=1),
    ):
        bad = copy.deepcopy(record)
        mutation(bad)
        path.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            isolation.require_browser_acceptance(IMAGE)
````
