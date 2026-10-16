"""Exercise the real native lab wrapper, not a mocked delivery entry point."""

import pytest

pytest.importorskip("psycopg")

from workbench.acceptance import native_lab
from workbench.core.contracts import Plan
from workbench.delivery.recovery import NativeIntegrityError, NativeValidationFailure


@pytest.mark.parametrize("kind", ["unknown_assert", "permission", "source_changed", "plan_changed"])
def test_native_lab_does_not_downgrade_unknown_or_integrity_failures(tmp_path, monkeypatch, kind):
    source = tmp_path / "source"
    source.mkdir()
    source_file = source / "upstream.py"
    source_file.write_text("value = 1\n")
    plan = Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )
    monkeypatch.setattr(native_lab, "prepare_fastapi_transactions", lambda *args: {})

    def fail(*args):
        if kind == "source_changed":
            source_file.write_text("corrupted\n")
        if kind == "plan_changed":
            plan.title = "changed approval"
        if kind == "permission":
            raise PermissionError("denied")
        raise AssertionError("unclassified assertion before executable validation")

    monkeypatch.setattr(native_lab, "bootstrap_database", fail)
    expected = (
        NativeIntegrityError
        if kind in {"source_changed", "plan_changed"}
        else PermissionError
        if kind == "permission"
        else AssertionError
    )
    with pytest.raises(expected) as error:
        native_lab._run_acceptance(
            "fastapiadmin",
            source,
            tmp_path / "product",
            None,
            "postgresql://localhost/test_codegen",
            tmp_path / "reports",
            plan,
            backend_port=18001,
        )
    assert not isinstance(error.value, NativeValidationFailure)


def test_only_explicit_runtime_check_marks_validation_failed():
    def failed_check():
        raise AssertionError("HTTP acceptance mismatch")

    with pytest.raises(NativeValidationFailure):
        native_lab._runtime_check(failed_check)
