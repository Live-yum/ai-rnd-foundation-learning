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
    source_file.write_text("value = 1\n", encoding="utf-8")
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
            source_file.write_text("corrupted\n", encoding="utf-8")
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
        native_lab._runtime_check(failed_check, check_id="generated-crud")


def test_runtime_check_diagnostic_is_bounded_and_does_not_copy_assertion_secrets():
    secret = "Bearer private-token https://user:password@host/" + "sensitive body" * 1000

    def failed_check():
        raise AssertionError(secret)

    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(failed_check, check_id="generated-permissions")
    text = str(failure.value)
    assert "check_id=generated-permissions" in text
    assert "reason=assertion_failed" in text
    assert len(text) < 160
    assert "private-token" not in text
    assert "password" not in text
    assert "sensitive" not in text


def test_real_lab_failure_log_keeps_safe_check_identifier(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "upstream.py").write_text("value = 1\n", encoding="utf-8")
    plan = Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )
    monkeypatch.setattr(native_lab, "prepare_fastapi_transactions", lambda *args: {})

    def failed_check():
        raise AssertionError("Bearer super-secret HTTP response private-body")

    def fail(*args):
        native_lab._runtime_check(failed_check, check_id="generated-crud")

    monkeypatch.setattr(native_lab, "bootstrap_database", fail)
    reports = tmp_path / "reports"
    with pytest.raises(NativeValidationFailure):
        native_lab._run_acceptance(
            "fastapiadmin",
            source,
            tmp_path / "product",
            None,
            "postgresql://localhost/test_codegen",
            reports,
            plan,
            backend_port=18001,
        )
    log = (reports / "failure.log").read_text(encoding="utf-8")
    assert "check_id=generated-crud" in log
    assert "reason=assertion_failed" in log
    assert "super-secret" not in log
    assert "private-body" not in log
    assert len(log) < 300


def test_runtime_failure_identifies_trusted_assertion_frame_without_payload():
    from workbench.acceptance.native_acceptance import list_rows

    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(list_rows, "private response body", check_id="generated-crud")
    text = str(failure.value)
    assert "source=workbench/acceptance/native_acceptance.py:" in text
    assert ":list_rows" in text
    assert "private response body" not in text
    assert len(text) < 300
