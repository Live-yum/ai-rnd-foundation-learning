# tests/test_readonly_dependency_admission.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_capability_profile`、`workbench`、`workbench.capability_isolation`、`workbench.capability_verification`、`workbench.catalog`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `absent_after_delete`（L27–L31）：接收`events`、`identifier`。 控制顺序：L30断言`identifier == IDENTIFIER and events[-1] == "deleted"`；L31抛异常，停止当前正常路径。 调用`DaytonaNotFoundError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `product_plan`（L35–L37）：接收`tmp_path`。 调用`fixed_application`。 返回路径：L37的`product, fixed_application(product)`。
- `inspected`（L40–L50）：接收`record`。 调用`container_binding`。 返回路径：L41的`{ **container_binding(record), "profile": "fixed-authored-sqlite-v1", "sandbox_id": IDENTI…`。
- `test_direct_verify_rejects_before_container_creation`（L64–L96）：接收`product_plan`、`settings`、`tmp_path`、`mutation`。 控制顺序：L69按`mutation == "missing-profile"`分支；L71按`mutation == "descriptor-drift"`分支；L73按`mutation == "extra-descriptor"`分支；L75按`mutation == "wrong-image"`分支；L77按`mutation == "prepare-hook"`分支；L79按`mutation == "alternate-launcher"`分支；L96断言`json.loads(receipt_path.read_text())["passed"] is False`。 调用`profile_record`、`(product / "uv.lock").write_text`、`(product / "package.json").write_text`、`receipt_path.write_text`、`pytest.raises`、`sandbox._verify`、`plan.selection.model_dump`、`SimpleNamespace`、`pytest.fail`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspector_drift_rejects_before_source_upload`（L102–L142）：接收`product_plan`、`settings`、`tmp_path`、`field`。 控制顺序：L141断言`result["passed"] is False and result["cleanup"] == "deleted"`；L142断言`result["kind"] == "isolation_environment" and events == ["deleted"]`。 调用`profile_record`、`inspected`、`SimpleNamespace`、`events.append`、`absent_after_delete`、`sandbox._verify`、`plan.selection.model_dump`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspector_drift_rejects_before_source_upload.forbidden`（L117–L118）：接收`*a`、`**k`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_image_dependency_failure_precedes_any_product_command`（L156–L199）：接收`product_plan`、`settings`、`tmp_path`、`monkeypatch`、`field`。 控制顺序：L198断言`result["passed"] is False and result["cleanup"] == "deleted"`；L199断言`events == ["upload", "deleted"]`。 调用`profile_record`、`dependency_evidence`、`manifest`、`field.endswith`、`SimpleNamespace`、`events.append`、`monkeypatch.setattr`、`sandbox._verify`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_image_dependency_failure_precedes_any_product_command.forbidden`（L165–L166）：接收`*a`、`**k`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `complete_proof`（L202–L262）：接收`product`、`plan`。 调用`profile_record`、`digest`、`scenario.model_dump`、`manifest`、`plan.model_dump`、`inspected`、`sha`、`dict.fromkeys`、`dependency_evidence`等。 返回路径：L216的`{ "verifier": execution.VERIFIER, "passed": True, "cleanup": "deleted", "network_block_all…`。
- `complete_native_proof`（L265–L296）：接收`product`、`plan`。 控制顺序：L276遍历`( "preinstalled_dependencies", "restart_preinstalled_dependencies…`；L283遍历`("security_checks", "restart_security_checks")`；L295断言`require_evidence(proof, **bindings) is proof`。 调用`Selection`、`complete_proof`、`profile_record`、`inspected`、`container_binding`、`dict`、`dependency_evidence`、`manifest`、`dict.fromkeys`等。 返回路径：L296的`proof, bindings`。
- `test_native_delivery_binds_runtime_patch_at_initial_restart_and_final`（L308–L324）：接收`product_plan`、`field`、`mutation`。 控制顺序：L315按`mutation == "missing"`分支；L317按`mutation == "stale"`分支。 调用`complete_native_proof`、`copy.deepcopy`、`value.pop`、`value["runtime_patches"][0][ "relative_path" ].replace`、`pytest.raises`、`require_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_delivery_requires_both_complete_security_groups`（L329–L333）：接收`product_plan`、`field`、`replacement`。 调用`complete_native_proof`、`pytest.raises`、`require_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_native_security_flag_rejects_false_or_truthy_coercion`（L338–L344）：接收`product_plan`、`field`、`value`。 控制顺序：L340遍历`proof[field]`。 调用`complete_native_proof`、`copy.deepcopy`、`pytest.raises`、`require_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_delivery_rejects_missing_extra_or_stripped_security_evidence`（L347–L371）：接收`product_plan`。 控制顺序：L349遍历`("security_checks", "restart_security_checks")`；L350遍历`proof[field]`；L359遍历`( ("security_checks",), ("restart_security_checks",), ("security_…`；L365遍历`fields`。 调用`complete_native_proof`、`copy.deepcopy`、`pytest.raises`、`require_evidence`、`changed.pop`、`proof.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_old_or_unbound_dependency_evidence_never_passes`（L388–L425）：接收`product_plan`、`mutation`。 控制顺序：L399断言`require_evidence(proof, **bindings) is proof`；L400按`mutation == "v3"`分支；L402按`mutation == "absent"`分支；L404按`mutation == "restart-absent"`分支；L406按`mutation == "final-absent"`分支；L408按`mutation == "source-drift"`分支；L410按`mutation == "offline-install-only"`分支；L412按`mutation == "profile-image"`分支。后续分支沿下方源码相同行号继续阅读。 调用`complete_proof`、`dict`、`digest`、`manifest`、`plan.model_dump`、`plan.selection.model_dump`、`require_evidence`、`proof.pop`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dependency_receipt_flags_require_boolean_true`（L428–L443）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L431断言`execution.require_preinstalled_evidence( good, record["snapshot"]["dependency_manifes…`；L437遍历`good`。 调用`profile_record`、`dependency_evidence`、`execution.require_preinstalled_evidence`、`digest`、`copy.deepcopy`、`bad.pop`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_dependency_probes_do_not_replace_existing_security_checks`（L457–L491）：接收`product_plan`、`monkeypatch`、`missing`。 控制顺序：L465断言`len(expected) == 25`；L467按`missing`分支；L471按`missing`分支；L475断言`probe.run_security_probe( object(), plan, 10, {"resource_limits": True} ) == dict.fro…`；L481断言`len(native) == 40`；L482断言`native == (expected - {"all_tcp_destinations_denied"}) \| { "postgres_application_rol…`。 调用`compile`、`set`、`len`、`dict.fromkeys`、`checks.pop`、`monkeypatch.setattr`、`SimpleNamespace`、`json.dumps`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_readonly_dependency_admission.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L491。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17928`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_readonly_dependency_admission.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e8b7e274c11c889a9ca9e0e7e495761b21c9e7fa556c646168a7c07f9e9540f9"} -->
````python
# tests/test_readonly_dependency_admission.py
"""Fail-closed contract tests with synthetic images, never live certification."""

import copy
import json
from types import SimpleNamespace

import pytest
from capability_dependency_fixtures import container_binding, dependency_evidence, profile_record

from scripts.ci_capability_profile import fixed_application
from workbench import capability_execution as execution
from workbench import capability_sandbox as sandbox
from workbench.capability_isolation import (
    ISOLATION_FLAGS,
    ISOLATION_PROFILE,
    NATIVE_SHARED_MEMORY_EVIDENCE,
)
from workbench.capability_verification import CheckFailure, require_evidence
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.filesystem import manifest, sha
from workbench.settings import ROOT

IDENTIFIER = "00000000-0000-0000-0000-000000000001"


def absent_after_delete(events, identifier):
    from daytona.common.errors import DaytonaNotFoundError

    assert identifier == IDENTIFIER and events[-1] == "deleted"
    raise DaytonaNotFoundError("owned fixture absent after deletion")


@pytest.fixture
def product_plan(tmp_path):
    product = tmp_path / "product"
    return product, fixed_application(product)


def inspected(record):
    return {
        **container_binding(record),
        "profile": "fixed-authored-sqlite-v1",
        "sandbox_id": IDENTIFIER,
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-profile",
        "descriptor-drift",
        "extra-descriptor",
        "wrong-image",
        "prepare-hook",
        "alternate-launcher",
    ],
)
def test_direct_verify_rejects_before_container_creation(
    product_plan, settings, tmp_path, mutation
):
    product, plan = product_plan
    record = profile_record(product)
    if mutation == "missing-profile":
        record = None
    elif mutation == "descriptor-drift":
        (product / "uv.lock").write_text("unreviewed dependency")
    elif mutation == "extra-descriptor":
        (product / "package.json").write_text("{}")
    elif mutation == "wrong-image":
        record["snapshot"]["dependency_manifest"]["image_id"] = "sha256:" + "9" * 64
    elif mutation == "prepare-hook":
        plan.runtime.prepare[0].argv += ["--all-extras"]
    elif mutation == "alternate-launcher":
        plan.runtime.start.argv[0] = "python"
    receipt_path = tmp_path / "proof.json"
    receipt_path.write_text('{"passed":true,"verifier":"controller-http-contract-v3"}')
    with pytest.raises(CheckFailure):
        sandbox._verify(
            product,
            plan,
            plan.scenarios,
            settings,
            plan.selection.model_dump(),
            tmp_path / "proof.json",
            client=SimpleNamespace(create=lambda *a, **k: pytest.fail("Created before admission")),
            aggregate=True,
            profile_record=record,
        )

    assert json.loads(receipt_path.read_text())["passed"] is False


@pytest.mark.parametrize(
    "field", ["runner_image_id", "snapshot_image_id", "snapshot_digest", "dependency_manifest"]
)
def test_inspector_drift_rejects_before_source_upload(product_plan, settings, tmp_path, field):
    product, plan = product_plan
    record = profile_record(product)
    evidence = inspected(record)
    evidence[field] = (
        {}
        if field == "dependency_manifest"
        else (
            "registry:6000/rnd-python@sha256:" + "9" * 64
            if field == "snapshot_digest"
            else "sha256:" + "9" * 64
        )
    )
    events = []

    def forbidden(*a, **k):
        pytest.fail("Source touched before actual image admission")

    remote = SimpleNamespace(
        id=IDENTIFIER, fs=SimpleNamespace(create_folder=forbidden, upload_file=forbidden)
    )
    client = SimpleNamespace(
        create=lambda *a, **k: remote,
        delete=lambda *a, **k: events.append("deleted"),
        get=lambda identifier: absent_after_delete(events, identifier),
    )
    settings.daytona_snapshot = "owned-fixture"
    result = sandbox._verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "proof.json",
        client=client,
        aggregate=True,
        profile_record=record,
        control_observer=lambda _: evidence,
    )
    assert result["passed"] is False and result["cleanup"] == "deleted"
    assert result["kind"] == "isolation_environment" and events == ["deleted"]


@pytest.mark.parametrize(
    "field",
    [
        "manifest_sha256",
        "installed_tree_sha256",
        "descriptors_verified",
        "installed_tree_verified",
        "readonly_verified",
        "product_links_verified",
    ],
)
def test_image_dependency_failure_precedes_any_product_command(
    product_plan, settings, tmp_path, monkeypatch, field
):
    product, plan = product_plan
    record = profile_record(product)
    evidence = dependency_evidence(record["snapshot"]["dependency_manifest"], manifest(product))
    evidence[field] = "9" * 64 if field.endswith("sha256") else 1
    events = []

    def forbidden(*a, **k):
        pytest.fail("Candidate process ran before dependency proof")

    remote = SimpleNamespace(
        id=IDENTIFIER,
        fs=SimpleNamespace(
            create_folder=lambda *a: None, upload_file=lambda *a, **k: events.append("upload")
        ),
        process=SimpleNamespace(create_session=forbidden, execute_session_command=forbidden),
    )
    monkeypatch.setattr(sandbox, "control_exec", lambda *a: SimpleNamespace(exit_code=0))
    monkeypatch.setattr(sandbox, "prepare_identity", lambda *a: {})
    monkeypatch.setattr(
        "workbench.capability_dependencies.prepare_readonly_dependencies", lambda *a, **k: evidence
    )
    monkeypatch.setattr(sandbox, "prepare_database", forbidden)
    settings.daytona_snapshot = "owned-fixture"
    result = sandbox._verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "proof.json",
        client=SimpleNamespace(
            create=lambda *a, **k: remote,
            delete=lambda *a, **k: events.append("deleted"),
            get=lambda identifier: absent_after_delete(events, identifier),
        ),
        aggregate=True,
        profile_record=record,
        control_observer=lambda _: inspected(record),
    )
    assert result["passed"] is False and result["cleanup"] == "deleted"
    assert events == ["upload", "deleted"]


def complete_proof(product, plan):
    record = profile_record(product)
    checks = [
        {
            "id": scenario.id,
            "phase": phase,
            "contract_sha256": digest(scenario.model_dump()),
            "passed": True,
            "steps": [{"passed": True}],
        }
        for scenario in plan.scenarios
        for phase in (("initial", "restart") if scenario.after_restart else ("initial",))
    ]
    dependency = record["snapshot"]["dependency_manifest"]
    return {
        "verifier": execution.VERIFIER,
        "passed": True,
        "cleanup": "deleted",
        "network_block_all": True,
        "credentials_uploaded": False,
        "source_digest": digest(manifest(product)),
        "plan_digest": digest(plan.model_dump()),
        "sandbox_id": IDENTIFIER,
        "container_isolation": inspected(record),
        "execution_isolation": {
            "profile": ISOLATION_PROFILE,
            "application_uid": 20000,
            "landlock_abi": 6,
            "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
            **dict.fromkeys(ISOLATION_FLAGS, True),
        },
        "dependency_profile": dependency,
        "preinstalled_dependencies": dependency_evidence(dependency, manifest(product)),
        "restart_preinstalled_dependencies": dependency_evidence(dependency, manifest(product)),
        "final_preinstalled_dependencies": dependency_evidence(dependency, manifest(product)),
        "checks": checks,
        "restarted": True,
        "stack": {
            "selection": plan.selection.model_dump(),
            "source_checks": ["fixture"],
            "launcher": "uvicorn",
        },
        "database": {
            "engine": "sqlite",
            "observed_writes": True,
            "baseline": {name: 0 for name in plan.runtime.database_tables},
            "after": {name: 1 for name in plan.runtime.database_tables},
            "after_restart": {name: 1 for name in plan.runtime.database_tables},
        },
        "browser": [
            {
                "id": scenario.id,
                "steps": len(scenario.browser),
                "passed": True,
                "real_browser": True,
                "browser_os_sandbox": True,
            }
            for scenario in plan.scenarios
            if scenario.browser
        ],
    }


def complete_native_proof(product, plan):
    plan.selection = Selection(template="fastapiadmin")
    proof = complete_proof(product, plan)
    record = profile_record(template="fastapiadmin")
    dependency = record["snapshot"]["dependency_manifest"]
    proof["container_isolation"] = {
        **inspected(record),
        **container_binding(record),
    }
    proof["execution_isolation"]["native_shared_memory"] = dict(NATIVE_SHARED_MEMORY_EVIDENCE)
    proof["dependency_profile"] = dependency
    for field in (
        "preinstalled_dependencies",
        "restart_preinstalled_dependencies",
        "final_preinstalled_dependencies",
    ):
        proof[field] = dependency_evidence(dependency, manifest(product))
    proof["database"]["engine"] = "postgresql"
    for field in ("security_checks", "restart_security_checks"):
        proof[field] = dict.fromkeys(
            execution.security_checks_for(plan.selection.model_dump()), True
        )
    bindings = dict(
        source_digest=digest(manifest(product)),
        plan_digest=digest(plan.model_dump()),
        scenarios=plan.scenarios,
        selection=plan.selection.model_dump(),
        database_tables=plan.runtime.database_tables,
        aggregate=True,
    )
    assert require_evidence(proof, **bindings) is proof
    return proof, bindings


@pytest.mark.parametrize(
    "field",
    [
        "preinstalled_dependencies",
        "restart_preinstalled_dependencies",
        "final_preinstalled_dependencies",
    ],
)
@pytest.mark.parametrize("mutation", ["missing", "stale", "changed-physical-path"])
def test_native_delivery_binds_runtime_patch_at_initial_restart_and_final(
    product_plan, field, mutation
):
    proof, bindings = complete_native_proof(*product_plan)
    # These compact fixtures share the profile's list; separate the receipt first.
    proof[field] = copy.deepcopy(proof[field])
    value = proof[field]
    if mutation == "missing":
        value.pop("runtime_patches")
    elif mutation == "stale":
        value["runtime_patches"][0]["id"] = "old"
    else:
        value["runtime_patches"][0]["relative_path"] = value["runtime_patches"][0][
            "relative_path"
        ].replace("vite@7.3.3/", "vite@7.3.3_jiti@2.6.1/")
    with pytest.raises(CheckFailure, match="依赖"):
        require_evidence(proof, **bindings)


@pytest.mark.parametrize("field", ["security_checks", "restart_security_checks"])
@pytest.mark.parametrize("replacement", [None, {}, [], True, "complete"])
def test_native_delivery_requires_both_complete_security_groups(product_plan, field, replacement):
    proof, bindings = complete_native_proof(*product_plan)
    proof[field] = replacement
    with pytest.raises(CheckFailure, match="隔离反例及清理"):
        require_evidence(proof, **bindings)


@pytest.mark.parametrize("field", ["security_checks", "restart_security_checks"])
@pytest.mark.parametrize("value", [False, 1, 0, None, "true", [], {}])
def test_every_native_security_flag_rejects_false_or_truthy_coercion(product_plan, field, value):
    proof, bindings = complete_native_proof(*product_plan)
    for key in proof[field]:
        changed = copy.deepcopy(proof)
        changed[field][key] = value
        with pytest.raises(CheckFailure, match="隔离反例及清理"):
            require_evidence(changed, **bindings)


def test_native_delivery_rejects_missing_extra_or_stripped_security_evidence(product_plan):
    proof, bindings = complete_native_proof(*product_plan)
    for field in ("security_checks", "restart_security_checks"):
        for key in proof[field]:
            changed = copy.deepcopy(proof)
            del changed[field][key]
            with pytest.raises(CheckFailure, match="隔离反例及清理"):
                require_evidence(changed, **bindings)
        changed = copy.deepcopy(proof)
        changed[field]["extra"] = True
        with pytest.raises(CheckFailure, match="隔离反例及清理"):
            require_evidence(changed, **bindings)
    for fields in (
        ("security_checks",),
        ("restart_security_checks",),
        ("security_checks", "restart_security_checks"),
    ):
        changed = copy.deepcopy(proof)
        for field in fields:
            changed.pop(field)
        with pytest.raises(CheckFailure, match="隔离反例及清理"):
            require_evidence(changed, **bindings)
    proof.update(security_checks={}, restart_security_checks={})
    with pytest.raises(CheckFailure, match="隔离反例及清理"):
        require_evidence(proof, **bindings)


@pytest.mark.parametrize(
    "mutation",
    [
        "v3",
        "absent",
        "restart-absent",
        "final-absent",
        "source-drift",
        "offline-install-only",
        "profile-image",
        "profile-descriptors",
        "extra-proof-field",
    ],
)
def test_old_or_unbound_dependency_evidence_never_passes(product_plan, mutation):
    product, plan = product_plan
    proof = complete_proof(product, plan)
    bindings = dict(
        source_digest=digest(manifest(product)),
        plan_digest=digest(plan.model_dump()),
        scenarios=plan.scenarios,
        selection=plan.selection.model_dump(),
        database_tables=plan.runtime.database_tables,
        aggregate=True,
    )
    assert require_evidence(proof, **bindings) is proof
    if mutation == "v3":
        proof["verifier"] = "controller-http-contract-v3"
    elif mutation == "absent":
        proof.pop("preinstalled_dependencies")
    elif mutation == "restart-absent":
        proof.pop("restart_preinstalled_dependencies")
    elif mutation == "final-absent":
        proof.pop("final_preinstalled_dependencies")
    elif mutation == "source-drift":
        proof["preinstalled_dependencies"]["source_inventory_sha256"] = "0" * 64
    elif mutation == "offline-install-only":
        proof["preinstalled_dependencies"] = {"offline_install": True}
    elif mutation == "profile-image":
        proof["dependency_profile"] = {
            **proof["dependency_profile"],
            "image_id": "sha256:" + "0" * 64,
        }
    elif mutation == "profile-descriptors":
        proof["dependency_profile"] = {
            **proof["dependency_profile"],
            "original_descriptors": {"extra/package.json": "0" * 64},
        }
    else:
        proof["preinstalled_dependencies"]["installed_at_runtime"] = True
    with pytest.raises(CheckFailure):
        require_evidence(proof, **bindings)


def test_dependency_receipt_flags_require_boolean_true():
    record = profile_record()
    good = dependency_evidence(record["snapshot"]["dependency_manifest"])
    assert (
        execution.require_preinstalled_evidence(
            good, record["snapshot"]["dependency_manifest"], source_digest=digest({})
        )
        is good
    )
    for field in good:
        bad = copy.deepcopy(good)
        bad.pop(field)
        with pytest.raises(ValueError):
            execution.require_preinstalled_evidence(
                bad, record["snapshot"]["dependency_manifest"], source_digest=digest({})
            )


@pytest.mark.parametrize(
    "missing",
    [
        None,
        "immutable_dependency_read_allowed",
        "immutable_dependency_write_denied",
        "tmpfs_noexec_enforced",
        "private_control_read_denied",
        "io_uring_denied",
    ],
)
def test_new_dependency_probes_do_not_replace_existing_security_checks(
    product_plan, monkeypatch, missing
):
    from scripts import capability_security_probe as probe

    _, plan = product_plan
    compile(probe.PROBE, "<product-security-probe>", "exec")
    expected = set(execution.SECURITY_CHECKS)
    assert len(expected) == 25
    checks = dict.fromkeys(expected - {"container_resource_limits"}, True)
    if missing:
        checks.pop(missing)
    monkeypatch.setattr(probe, "control_exec", lambda *a: SimpleNamespace(exit_code=0))
    monkeypatch.setattr(probe, "run_guarded_control", lambda *a: (0, json.dumps(checks)))
    if missing:
        with pytest.raises(CheckFailure):
            probe.run_security_probe(object(), plan, 10, {"resource_limits": True})
    else:
        assert probe.run_security_probe(
            object(), plan, 10, {"resource_limits": True}
        ) == dict.fromkeys(expected, True)
        from scripts.capability_native_shm_probe import RUNTIME_CHECKS

        native = execution.security_checks_for({"template": "fastapiadmin"})
        assert len(native) == 40
        assert native == (expected - {"all_tcp_destinations_denied"}) | {
            "postgres_application_role_restricted",
            "postgres_verifier_role_restricted",
            "postgres_planner_identity_restricted",
            "redis_owned_namespace_only",
            "private_redis_control_denied",
            "native_egress_denied_same_ports",
            "cross_container_shm_private",
            "peer_cleanup",
        } | set(RUNTIME_CHECKS)
````
