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
        create=lambda *a, **k: remote, delete=lambda *a, **k: events.append("deleted")
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
            create=lambda *a, **k: remote, delete=lambda *a, **k: events.append("deleted")
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
