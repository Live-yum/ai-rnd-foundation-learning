# workbench/capability_execution.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.domain`、`workbench.errors`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `security_checks_for`（L135–L140）：接收`selection`。 控制顺序：L136按`selection.get("template") == "fastapiadmin"`分支。 调用`selection.get`、`set`。 返回路径：L137的`(set(SECURITY_CHECKS) - {"all_tcp_destinations_denied"}) \| set( NATIVE_SECURITY_CHECKS )`；L140的`set(SECURITY_CHECKS)`。
- `receipt_name`（L143–L148）：接收`selection`。 调用`selection.get`。 返回路径：L144的`"native-fastapiadmin-security-acceptance.json" if selection.get("template") == "fastapiadm…`。
- `verifier_identity`（L151–L152）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`digest`、`sha`。 返回路径：L152的`digest({name: sha(ROOT / name) for name in SOURCE_FILES})`。
- `profile_binding`（L155–L176）：接收`record`。 控制顺序：L159按`selected not in ( Selection(template="python-basic").model_dump(), Selection(template…`分支；L163抛异常，停止当前正常路径；L167按`dependency_profile["image_id"] != record["snapshot"]["image_id"]`分支；L168抛异常，停止当前正常路径。 调用`record.get`、`Selection().model_dump`、`Selection`、`Selection(template="python-basic").model_dump`、`Selection(template="fastapiadmin").model_dump`、`ValueError`、`require_dependency_manifest`。 返回路径：L169的`{ "recipe_identity": record["recipe_identity"], "runner_image_id": record["runner"]["image…`。
- `require_preinstalled_evidence`（L179–L215）：接收`value`、`expected`、`source_digest`。 源码说明：A verified image dependency tree is not a runtime installation receipt.。 控制顺序：L195按`not isinstance(expected, dict) or not isinstance(value, dict) or set(value) != keys o…`分支；L214抛异常，停止当前正常路径。 调用`isinstance`、`set`、`type`、`value.get`、`any`、`expected.get`、`re.fullmatch`、`str`、`ValueError`。 返回路径：L215的`value`。
- `require_profile_container_binding`（L218–L238）：接收`record`、`container`。 源码说明：Do not trust a matching descriptor unless the inspected image is pinned.。 控制顺序：L221按`not isinstance(container, dict) or any( container.get(key) != bound[key] for key in (…`分支；L225抛异常，停止当前正常路径；L226按`container.get("dependency_manifest") != bound["dependency_manifest"]`分支；L227抛异常，停止当前正常路径；L228按`record.get("selection", {}).get("template") == "fastapiadmin"`分支；L230按`container.get("profile") != "native-fastapiadmin-postgresql-v1" or type(shared) is no…`分支；L237抛异常，停止当前正常路径。 调用`profile_binding`、`isinstance`、`any`、`container.get`、`ValueError`、`record.get("selection", {}).get`、`record.get`、`type`。 返回路径：L238的`container`。
- `require_security_receipt`（L241–L284）：接收`value`、`record`、`browser_image`。 控制顺序：L259按`not isinstance(value, dict) or set(value) != expected or value.get("protocol") != PRO…`分支；L278抛异常，停止当前正常路径。 调用`record.get`、`Selection(template="python-basic").model_dump`、`Selection`、`security_checks_for`、`isinstance`、`set`、`value.get`、`verifier_identity`、`profile_binding`等。 返回路径：L284的`value`。
- `capability_execution_prerequisites`（L287–L342）：接收`settings`、`selection`。 源码说明：Read-only gate; never runs candidate code or calls a model. Return the exact verified profile directory/record. Missing conditions are recoverable execution blockers; callers must retain the plan and 。 控制顺序：L297按`not settings.capability_execution_enabled`分支；L298抛异常，停止当前正常路径；L302按`selected not in ( Selection(template="python-basic").model_dump(), Selection(template…`分支；L306抛异常，停止当前正常路径；L310按`settings.sandbox_provider != "daytona"`分支；L311抛异常，停止当前正常路径；L322按`directory.is_relative_to(runs)`分支；L323抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`UnsupportedScope`、`Selection.model_validate(selection).model_dump`、`Selection.model_validate`、`Selection(template="python-basic").model_dump`、`Selection`、`Selection(template="fastapiadmin").model_dump`、`require_browser_acceptance`、`Path(settings.capability_profile_directory).resolve`、`Path`等。 返回路径：L342的`directory, record`。

</details>

**创建路径：** `workbench/capability_execution.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L342。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13780`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_execution.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "004341f311763ac83a54de89d5974659682ebb7da81b63ad9929e7ba47cfaec1"} -->
````python
# workbench/capability_execution.py
"""Fail-closed admission for reviewed custom-source execution.

An opt-in flag and a successful authored app are not security acceptance. The
controller requires a separately produced live adversarial receipt, bound to
the current verifier sources and exact local profile images. Generated source
never receives this file or its directory. This is a local trust boundary, not
a signature or a claim of protection from a malicious host administrator.
"""

import json
import re
import subprocess
from pathlib import Path

from workbench.catalog import Selection
from workbench.domain import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import sha
from workbench.settings import ROOT

RECEIPT = "capability-security-acceptance.json"
PROTOCOL = "custom-source-isolation-v2"
VERIFIER = "controller-http-contract-v4"
SOURCE_FILES = (
    "scripts/capability_browser_apparmor.cjs",
    "workbench/capability_browser_policy.py",
    "scripts/capability_browser_seccomp_probe.c",
    "tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json",
    "workbench/capability_execution.py",
    "workbench/capability_dependencies.py",
    "workbench/daytona_profiles.py",
    "scripts/daytona_dependency_image.py",
    "scripts/daytona_dependency_build.py",
    "scripts/daytona_dependency_build.lock.json",
    "tools/daytona/capability-snapshot.Dockerfile",
    "tools/daytona/capability-native-snapshot.Dockerfile",
    "workbench/capability_sandbox.py",
    "workbench/capability_startup_paths.py",
    "workbench/capability_isolation.py",
    "workbench/capability_stack.py",
    "workbench/capability_verification.py",
    "workbench/daytona_sessions.py",
    "workbench/sandbox.py",
    "workbench/filesystem.py",
    "workbench/local_only.py",
    "workbench/tools.py",
    "workbench/capability_contracts.py",
    "workbench/capability_policy.py",
    "workbench/capability_editing.py",
    "workbench/orchestration.py",
    "workbench/flow.py",
    "workbench/runtime.py",
    "workbench/store.py",
    "workbench/catalog.py",
    "workbench/settings.py",
    "workbench/capability_services.py",
    "workbench/capability_native_runtime.py",
    "scripts/capability_native_egress.py",
    "scripts/capability_native_planner_probe.py",
    "scripts/capability_native_shm_probe.py",
    "scripts/ci_native_capability_security.py",
    "scripts/ci_native_capability_source.py",
    "scripts/ci_native_tools.py",
    "workbench/native_lab.py",
    "workbench/portable.py",
    "scripts/ci_contest_capability.py",
    "scripts/extension_oracles/contest.py",
    "workbench/capability_contest_oracle.py",
    "tools/browser/seccomp.playwright-1.56.1.json",
    "scripts/daytona_native_capability_profile.py",
    "workbench/capability_browser_isolation.py",
    "scripts/capability_browser_worker.cjs",
    "scripts/capability_browser_network_probe.cjs",
    "scripts/ci_capability_browser_isolation.py",
    "tools/browser/Dockerfile",
    "pyproject.toml",
    "uv.lock",
    "scripts/capability_guard.py",
    "scripts/capability_security_probe.py",
    "scripts/ci_capability_security.py",
    "scripts/ci_capability_profile.py",
    "scripts/capability_fixture.py",
    "scripts/capability_browser.cjs",
    "scripts/daytona_capability_profile.py",
)
SECURITY_CHECKS = (
    "private_control_read_denied",
    "private_control_write_denied",
    "private_database_read_denied",
    "guard_write_denied",
    "trusted_interpreter_write_denied",
    "control_tcp_denied",
    "undeclared_tcp_denied",
    "raw_socket_denied",
    "root_signal_denied",
    "privilege_transition_denied",
    "resource_limits_enforced",
    "ordinary_product_write_allowed",
    "container_resource_limits",
    "tmpfs_storage_bound",
    "filesystem_write_scope",
    "proc_symlink_write_denied",
    "kernel_cgroup_limits",
    "socket_types_denied",
    "socketpair_types_denied",
    "all_tcp_destinations_denied",
    "unix_stream_pair_allowed",
    "io_uring_denied",
    "immutable_dependency_read_allowed",
    "immutable_dependency_write_denied",
    "tmpfs_noexec_enforced",
)


NATIVE_SECURITY_CHECKS = (
    "postgres_application_role_restricted",
    "postgres_verifier_role_restricted",
    "postgres_planner_identity_restricted",
    "redis_owned_namespace_only",
    "private_redis_control_denied",
    "native_egress_denied_same_ports",
    "native_shm_64mib_enforced",
    "native_shm_ordinary_files_allowed",
    "native_shm_spawn_pool_completed",
    "native_shm_spawn_pool_cleanup",
    "native_shm_noexec_enforced",
    "native_shm_forbidden_objects_denied",
    "native_shm_outside_writes_denied",
    "native_shm_probe_cleanup",
    "cross_container_shm_private",
    "peer_cleanup",
)


def security_checks_for(selection):
    if selection.get("template") == "fastapiadmin":
        return (set(SECURITY_CHECKS) - {"all_tcp_destinations_denied"}) | set(
            NATIVE_SECURITY_CHECKS
        )
    return set(SECURITY_CHECKS)


def receipt_name(selection):
    return (
        "native-fastapiadmin-security-acceptance.json"
        if selection.get("template") == "fastapiadmin"
        else RECEIPT
    )


def verifier_identity():
    return digest({name: sha(ROOT / name) for name in SOURCE_FILES})


def profile_binding(record):
    from workbench.capability_dependencies import require_dependency_manifest

    selected = record.get("selection", Selection().model_dump())
    if selected not in (
        Selection(template="python-basic").model_dump(),
        Selection(template="fastapiadmin").model_dump(),
    ):
        raise ValueError("No immutable dependency profile for the selected source stack")
    dependency_profile = require_dependency_manifest(
        record["snapshot"]["dependency_manifest"], selected["template"]
    )
    if dependency_profile["image_id"] != record["snapshot"]["image_id"]:
        raise ValueError("Immutable dependency provenance is bound to a different image")
    return {
        "recipe_identity": record["recipe_identity"],
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "snapshot": record["snapshot"]["snapshot"],
        "dependency_manifest": dependency_profile,
    }


def require_preinstalled_evidence(value, expected, *, source_digest):
    """A verified image dependency tree is not a runtime installation receipt."""
    flags = {
        "descriptors_verified",
        "installed_tree_verified",
        "readonly_verified",
        "product_links_verified",
        "source_inventory_verified",
    }
    keys = {
        "schema",
        "profile",
        "manifest_sha256",
        "installed_tree_sha256",
        "source_inventory_sha256",
    } | flags
    if (
        not isinstance(expected, dict)
        or not isinstance(value, dict)
        or set(value) != keys
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or value.get("profile") not in {"python-basic", "fastapiadmin"}
        or any(
            value.get(key) != expected.get(key)
            for key in keys - flags - {"source_inventory_sha256"}
        )
        or any(
            not re.fullmatch(r"[a-f0-9]{64}", str(value.get(key, "")))
            for key in ("manifest_sha256", "installed_tree_sha256")
        )
        or not re.fullmatch(r"[a-f0-9]{64}", str(source_digest))
        or value.get("source_inventory_sha256") != source_digest
        or any(value.get(key) is not True for key in flags)
    ):
        raise ValueError("Missing, stale or incompatible verified preinstalled dependency proof")
    return value


def require_profile_container_binding(record, container):
    """Do not trust a matching descriptor unless the inspected image is pinned."""
    bound = profile_binding(record)
    if not isinstance(container, dict) or any(
        container.get(key) != bound[key]
        for key in ("runner_image_id", "snapshot_image_id", "snapshot_digest")
    ):
        raise ValueError("Inspected container does not match the admitted dependency image")
    if container.get("dependency_manifest") != bound["dependency_manifest"]:
        raise ValueError("Inspector is missing exact immutable dependency provenance")
    if record.get("selection", {}).get("template") == "fastapiadmin":
        shared = container.get("shared_memory")
        if (
            container.get("profile") != "native-fastapiadmin-postgresql-v1"
            or type(shared) is not dict
            or shared != {"ipc_mode": "private", "size_bytes": 67108864}
            or type(shared["ipc_mode"]) is not str
            or type(shared["size_bytes"]) is not int
        ):
            raise ValueError("Native image admission requires its exact private shared memory")
    return container


def require_security_receipt(value, record, *, browser_image=None):
    selection = record.get("selection", Selection(template="python-basic").model_dump())
    checks = security_checks_for(selection)
    expected = {
        "protocol",
        "passed",
        "verifier_identity",
        "profile",
        "selection",
        "checks",
        "positive_product",
        "cleanup",
        "paid_model_calls",
        "restart_kind",
        "browser_image",
        "preinstalled_dependencies",
        "positive_source_digest",
    }
    if (
        not isinstance(value, dict)
        or set(value) != expected
        or value.get("protocol") != PROTOCOL
        or value.get("passed") is not True
        or value.get("verifier_identity") != verifier_identity()
        or value.get("profile") != profile_binding(record)
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", str(value.get("browser_image", "")))
        or (browser_image is not None and value.get("browser_image") != browser_image)
        or value.get("selection") != selection
        or not isinstance(value.get("checks"), dict)
        or set(value["checks"]) != checks
        or any(value["checks"].get(key) is not True for key in checks)
        or value.get("positive_product") is not True
        or value.get("restart_kind") != "application_process"
        or value.get("cleanup") != "deleted"
        or type(value.get("paid_model_calls")) is not int
        or value["paid_model_calls"] != 0
    ):
        raise ValueError("Live isolation receipt is missing, stale, incomplete or incompatible")
    require_preinstalled_evidence(
        value["preinstalled_dependencies"],
        record["snapshot"]["dependency_manifest"],
        source_digest=value["positive_source_digest"],
    )
    return value


def capability_execution_prerequisites(settings, selection):
    """Read-only gate; never runs candidate code or calls a model.

    Return the exact verified profile directory/record. Missing conditions are
    recoverable execution blockers; callers must retain the plan and candidate.
    """
    from scripts.daytona_capability_profile import require_profile
    from workbench.generator import PrerequisiteError
    from workbench.sandbox import snapshot_for, validate_configuration

    if not settings.capability_execution_enabled:
        raise UnsupportedScope(
            "自定义候选已保存，隔离执行尚未显式启用；保留同一运行，完成环境验收后可继续。"
        )
    selected = Selection.model_validate(selection).model_dump()
    if selected not in (
        Selection(template="python-basic").model_dump(),
        Selection(template="fastapiadmin").model_dump(),
    ):
        raise UnsupportedScope(
            "自定义候选已保留原技术栈；该原生框架/数据库尚无通过真实隔离验收的执行profile，"
            "只暂停执行，不切换SQLite、不删除业务功能。"
        )
    if settings.sandbox_provider != "daytona":
        raise UnsupportedScope(
            "自定义候选已保存，等待已验收的本机Daytona隔离环境；不会在平台宿主执行。"
        )
    try:
        from workbench.capability_browser_isolation import require_browser_acceptance

        browser_image = require_browser_acceptance(settings.capability_browser_image)
        directory = Path(settings.capability_profile_directory).resolve()
        # The controller configuration can select its owned installation, never
        # a product directory supplied through plan/runtime fields.
        runs = (settings.data_dir / "runs").resolve()
        if directory.is_relative_to(runs):
            raise ValueError("Profile cannot be stored in a generated run workspace")
        validate_configuration(settings, selected["template"], selected)
        snapshot = snapshot_for(settings, selected["template"], selected)
        if selected["template"] == "fastapiadmin":
            from scripts.daytona_native_capability_profile import require_native_profile

            record = require_native_profile(directory, snapshot)
        else:
            record = require_profile(directory, snapshot)
        path = directory / receipt_name(selected)
        if path.is_symlink() or path.stat().st_size > 16384:
            raise ValueError("Invalid security receipt file")
        value = json.loads(path.read_text(encoding="utf-8"))
        require_security_receipt(value, record, browser_image=browser_image)
    except OSError, ValueError, TypeError, KeyError, PrerequisiteError, subprocess.SubprocessError:
        raise UnsupportedScope(
            "自定义候选已保存；当前守卫、验证器与镜像缺少匹配的真实安全正反例验收。"
            "请完成独立隔离验收后重试同一运行，不能用固定应用或模拟测试回执替代。"
        ) from None
    return directory, record
````
