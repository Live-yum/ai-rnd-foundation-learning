"""Zero-model CI must pass production projection, not stop at a boolean acceptance."""

import json

import pytest

from scripts import ci_native_bundled as gate
from workbench.domain import digest
from workbench.filesystem import manifest, sha, write_json
from workbench.generator import PrerequisiteError


@pytest.fixture
def execution(tmp_path, monkeypatch):
    # This fixture tests gate wiring only. Real producer/projector validation is
    # covered separately and the Actions replay requires actual native execution.
    plan = gate.approved_customer_replay("fastapi-0e8", "fastapiadmin")
    reports, product = tmp_path / "reports", tmp_path / "product"
    product.mkdir()
    (product / "start.py").write_text("# generated product\n", encoding="utf-8")
    report = {
        "template": "fastapiadmin",
        "spec_digest": digest(plan.model_dump()),
        **dict.fromkeys(
            (
                "generated_runtime_verified",
                "native_codegen",
                "automatic_mount",
                "menu_and_permissions",
                "real_crud",
                "restart_persistence",
                "frontend_build",
                "frontend_typecheck",
                "real_browser",
                "source_unmodified",
            ),
            True,
        ),
        "portable_restored": {
            **dict.fromkeys(
                (
                    "passed",
                    "fresh_database",
                    "frontend_started",
                    "installed_from_lock",
                    "standalone_launcher",
                    "restart",
                ),
                True,
            ),
            **dict.fromkeys(
                ("source_database_reused", "original_platform_imported", "model_required"), False
            ),
        },
    }
    write_json(reports / "acceptance.json", report)
    write_json(reports / "approved-spec.json", plan.model_dump())
    calls = []

    def style(saved, receipt, files):
        assert saved == report
        assert receipt == {"template": "fastapiadmin", "spec_digest": digest(plan.model_dump())}
        assert files == manifest(product)
        calls.append("style")

    def business(saved, receipt, spec_path):
        assert saved == report
        assert spec_path == reports / "approved-spec.json"
        calls.append("business")

    def projection(saved, actual_plan, files, evidence_sha256):
        assert saved == report
        assert actual_plan == plan
        assert files == manifest(product)
        assert evidence_sha256 == sha(reports / "acceptance.json")
        calls.append("projection")
        return {"version": 2, "test_wiring_only": True}

    monkeypatch.setattr(gate, "require_native_style", style)
    monkeypatch.setattr(gate, "require_native_business", business)
    monkeypatch.setattr(gate, "native_review_evidence", projection)
    return plan, product, reports, report, calls


def invoke(execution):
    plan, product, reports, report, _ = execution
    return gate.verify_review_projection("fastapiadmin", plan, product, reports, report)


def status(execution):
    return json.loads((execution[2] / "review-projection-status.json").read_text(encoding="utf-8"))


def test_gate_calls_strict_production_checks_with_actual_saved_hash_and_sources(execution):
    result = invoke(execution)
    assert execution[4] == ["style", "business", "projection"]
    assert result == {"version": 2, "test_wiring_only": True}
    assert status(execution)["passed"] is True
    assert status(execution)["phase"] == "complete"
    assert status(execution)["model_calls"] == 0
    assert status(execution)["source_digest"] == digest(manifest(execution[1]))


@pytest.mark.parametrize("kind", ["missing", "oversize", "different", "foreign", "template"])
def test_gate_rejects_unbound_artifact_before_projector(execution, monkeypatch, kind):
    path = execution[2] / "acceptance.json"
    if kind == "missing":
        path.unlink()
    elif kind == "oversize":
        monkeypatch.setattr(gate, "MAX_ACCEPTANCE_BYTES", 1)
    elif kind == "different":
        write_json(path, {**execution[3], "forged": True})
    else:
        key, value = ("spec_digest", "0" * 64) if kind == "foreign" else ("template", "yudao-vben")
        execution[3][key] = value
        write_json(path, execution[3])
    with pytest.raises((ValueError, OSError)):
        invoke(execution)
    assert execution[4] == []
    assert status(execution)["passed"] is False
    assert status(execution)["phase"] == "saved-execution-evidence"


@pytest.mark.parametrize(
    "step", ["require_native_style", "require_native_business", "native_review_evidence"]
)
def test_failure_retains_actual_report_and_safe_phase_without_stale_pass(
    execution, monkeypatch, step
):
    path = execution[2] / "acceptance.json"
    before = path.read_bytes()
    write_json(execution[2] / "review-projection.json", {"stale": True})

    def fail(*args):
        raise ValueError("secret-test-canary")

    monkeypatch.setattr(gate, step, fail)
    with pytest.raises(ValueError):
        invoke(execution)
    assert path.read_bytes() == before
    assert not (execution[2] / "review-projection.json").exists()
    current = status(execution)
    assert current["passed"] is False
    assert current["phase"] == (
        "production-review-projection"
        if step == "native_review_evidence"
        else "native-style-and-business"
    )
    assert "secret-test-canary" not in json.dumps(current)


@pytest.mark.parametrize("kind", ["source", "acceptance"])
def test_gate_rejects_changes_during_projection(execution, monkeypatch, kind):
    def mutate(*args):
        if kind == "source":
            (execution[1] / "start.py").write_text("# tampered\n", encoding="utf-8")
        else:
            write_json(execution[2] / "acceptance.json", {"tampered": True})
        return {"version": 2}

    monkeypatch.setattr(gate, "native_review_evidence", mutate)
    with pytest.raises(ValueError, match="changed during projection"):
        invoke(execution)
    assert status(execution)["passed"] is False
    assert not (execution[2] / "review-projection.json").exists()


def test_main_never_stops_after_run_acceptance():
    import inspect

    source = inspect.getsource(gate.main)
    assert "report = run_acceptance(" in source
    assert "verify_review_projection(args.template, plan, output, reports, report)" in source


@pytest.mark.parametrize(
    "location,key,required",
    [
        *[
            ("original", key, True)
            for key in (
                "generated_runtime_verified",
                "native_codegen",
                "automatic_mount",
                "menu_and_permissions",
                "real_crud",
                "restart_persistence",
                "frontend_build",
                "frontend_typecheck",
                "real_browser",
                "source_unmodified",
            )
        ],
        *[
            ("restored", key, True)
            for key in (
                "passed",
                "fresh_database",
                "frontend_started",
                "installed_from_lock",
                "standalone_launcher",
                "restart",
            )
        ],
        *[
            ("restored", key, False)
            for key in ("source_database_reused", "original_platform_imported", "model_required")
        ],
    ],
)
@pytest.mark.parametrize("mutation", ["opposite", "missing", "number"])
def test_shared_production_runtime_gates_cannot_be_bypassed(
    execution, location, key, required, mutation
):
    report = execution[3]
    target = report if location == "original" else report["portable_restored"]
    if mutation == "missing":
        target.pop(key)
    else:
        target[key] = not required if mutation == "opposite" else int(required)
    write_json(execution[2] / "acceptance.json", report)
    with pytest.raises(PrerequisiteError):
        invoke(execution)
    assert execution[4] == []
    assert status(execution)["phase"] == "native-runtime-deployment"
    assert status(execution)["passed"] is False


def test_parse_and_hash_are_bound_to_the_same_read_bytes(execution, monkeypatch):
    path = execution[2] / "acceptance.json"
    original_sha = sha(path)
    loads = gate.json.loads
    observed = []

    def swap_after_read(raw):
        value = loads(raw)
        write_json(path, {"changed_between_read_and_hash": True})
        return value

    def projection(saved, plan, files, evidence_sha256):
        observed.append(evidence_sha256)
        assert evidence_sha256 == original_sha
        return {"version": 2}

    monkeypatch.setattr(gate.json, "loads", swap_after_read)
    monkeypatch.setattr(gate, "native_review_evidence", projection)
    with pytest.raises(ValueError, match="changed during projection"):
        invoke(execution)
    assert observed == [original_sha]
    monkeypatch.setattr(gate.json, "loads", loads)
    assert status(execution)["passed"] is False
