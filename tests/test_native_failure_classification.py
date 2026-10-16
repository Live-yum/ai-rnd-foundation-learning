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


@pytest.mark.parametrize("browser_failure", [False, True])
def test_real_lab_failure_log_keeps_safe_check_identifier(tmp_path, monkeypatch, browser_failure):
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
        if browser_failure:
            from workbench.business.browser import require_business_browser

            native_lab._runtime_check(
                require_business_browser,
                {"template": "fastapiadmin", "passed": False, "errors": ["super-secret"]},
                plan,
                "fastapiadmin",
                check_id="customer-service-browser",
            )
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
    assert (
        "check_id=customer-service-browser" if browser_failure else "check_id=generated-crud"
    ) in log
    assert (
        "reason=browser_evidence_failed" if browser_failure else "reason=assertion_failed"
    ) in log
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


@pytest.mark.parametrize("kind", ["failed_report", "missing_role", "missing_journey"])
def test_trusted_business_browser_failures_are_runtime_validation(kind):
    from workbench.business.browser import require_business_browser

    report = {"template": "fastapiadmin", "passed": True, "errors": [], "checks": []}
    if kind == "failed_report":
        report["passed"] = False
        report["errors"] = ["Bearer secret-response"]
    if kind == "missing_journey":
        report["checks"] = [
            role + ":real_native_login_menu_shell" for role in ("manager", "service", "employee")
        ]
    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(
            require_business_browser,
            report,
            None,
            "fastapiadmin",
            check_id="customer-service-browser",
        )
    assert "reason=browser_evidence_failed" in str(failure.value)
    assert "secret-response" not in str(failure.value)


@pytest.mark.parametrize("kind", ["unknown_value", "permission", "identity"])
def test_browser_boundary_preserves_unknown_and_security_failures(kind):
    from workbench.business.browser import require_business_browser

    def check():
        if kind == "identity":
            require_business_browser({"template": "yudao-vben"}, None, "fastapiadmin")
        if kind == "permission":
            raise PermissionError("denied")
        raise ValueError("unknown security or malformed data error")

    with pytest.raises(PermissionError if kind == "permission" else ValueError) as failure:
        native_lab._runtime_check(check, check_id="customer-service-browser")
    assert not isinstance(failure.value, NativeValidationFailure)


def test_browser_failure_type_is_not_converted_at_other_boundaries():
    from workbench.business.browser import BusinessBrowserValidationFailure

    def check():
        raise BusinessBrowserValidationFailure("not the selected browser boundary")

    with pytest.raises(BusinessBrowserValidationFailure):
        native_lab._runtime_check(check, check_id="generated-crud")
