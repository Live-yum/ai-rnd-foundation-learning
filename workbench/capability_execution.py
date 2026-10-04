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
PROTOCOL = "custom-source-isolation-v1"
SOURCE_FILES = (
    "workbench/capability_browser_policy.py",
    "scripts/capability_browser_seccomp_probe.c",
    "tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json",
    "workbench/capability_execution.py",
    "workbench/capability_sandbox.py",
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
    "scripts/ci_native_capability_security.py",
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
)


NATIVE_SECURITY_CHECKS = (
    "postgres_application_role_restricted",
    "postgres_verifier_role_restricted",
    "postgres_planner_identity_restricted",
    "redis_owned_namespace_only",
    "private_redis_control_denied",
    "native_egress_denied_same_ports",
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
    return {
        "recipe_identity": record["recipe_identity"],
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "snapshot": record["snapshot"]["snapshot"],
    }


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
