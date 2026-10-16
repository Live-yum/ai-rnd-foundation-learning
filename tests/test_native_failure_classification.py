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


@pytest.mark.parametrize(
    "check_id", ["installed-navigation-restart", "independent-native-delivery"]
)
@pytest.mark.parametrize("kind", ["known", "value", "permission", "assertion"])
def test_late_boundaries_accept_only_selected_failures(check_id, kind):
    from workbench.delivery.portable import PortableValidationFailure

    error_type = {
        "known": PortableValidationFailure
        if check_id == "independent-native-delivery"
        else AssertionError,
        "value": ValueError,
        "permission": PermissionError,
        "assertion": AssertionError,
    }[kind]

    def check():
        raise error_type("Bearer raw-secret-response")

    recognized = kind == "known" or (
        kind == "assertion" and check_id == "installed-navigation-restart"
    )
    with pytest.raises(NativeValidationFailure if recognized else error_type) as raised:
        native_lab._runtime_check(check, check_id=check_id)
    if recognized:
        assert check_id in str(raised.value)
        assert "raw-secret" not in str(raised.value)
    else:
        assert not isinstance(raised.value, NativeValidationFailure)


@pytest.mark.parametrize("stage", ["navigation", "portable"])
@pytest.mark.parametrize("failure", ["known", "unknown", "permission", "source", "plan"])
def test_real_late_callsite_preserves_checkpoint_and_integrity(
    tmp_path, monkeypatch, stage, failure
):
    import json
    from contextlib import nullcontext
    from types import SimpleNamespace

    from workbench.acceptance import yudao_navigation
    from workbench.business import probe
    from workbench.delivery.portable import PortableValidationFailure

    source = tmp_path / "source"
    source.mkdir()
    original = source / "original.py"
    original.write_text("original\n", encoding="utf-8")
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    output = tmp_path / "product/backend"
    output.mkdir(parents=True)
    (output / "generated.py").write_text("generated\n", encoding="utf-8")
    (output.parent / "frontend-product").mkdir()
    plan = SimpleNamespace(
        title="Approved",
        custom_rules=[],
        business=stage == "navigation",
        entities=[SimpleNamespace(name="task", fields=[])],
    )
    plan.model_dump = lambda: {"title": plan.title}
    monkeypatch.setattr(native_lab.native_recovery, "load", lambda *args: {"targets": [{}]})
    monkeypatch.setattr(native_lab, "native_environment", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        native_lab, "running_backend", lambda *args: nullcontext(("http://localhost", {}))
    )
    monkeypatch.setattr(
        native_lab, "frontend_preview", lambda *args: nullcontext("http://localhost")
    )
    for name in ("install_backend", "build_frontend", "generated_browser"):
        monkeypatch.setattr(native_lab, name, lambda *args, **kwargs: None)
    for name in (
        "frontend_environment",
        "verify_native_style",
        "generated_crud",
        "generated_permissions",
        "check_generated_persistence",
        "build_native_delivery",
    ):
        monkeypatch.setattr(native_lab, name, lambda *args, **kwargs: {})
    monkeypatch.setattr(native_lab, "login", lambda *args: "fixture")
    monkeypatch.setattr(probe, "customer_service_acceptance", lambda *args: {"records": {}})
    monkeypatch.setattr(probe, "BusinessClient", lambda *args: SimpleNamespace(close=lambda: None))

    def fail(*args, **kwargs):
        if failure == "source":
            original.write_text("changed\n", encoding="utf-8")
        if failure == "plan":
            plan.title = "Changed"
        if failure == "permission":
            raise PermissionError("denied")
        if failure == "unknown":
            raise ValueError("unclassified")
        raise (AssertionError if stage == "navigation" else PortableValidationFailure)("raw-secret")

    monkeypatch.setattr(
        yudao_navigation if stage == "navigation" else native_lab,
        "check_navigation_restart" if stage == "navigation" else "verify_native_delivery",
        fail,
    )
    reports = tmp_path / "reports"
    expected = (
        NativeIntegrityError
        if failure in {"source", "plan"}
        else PermissionError
        if failure == "permission"
        else ValueError
        if failure == "unknown"
        else NativeValidationFailure
    )
    with pytest.raises(expected) as raised:
        native_lab._run_acceptance(
            "yudao-vben",
            source,
            output,
            frontend,
            "postgresql://localhost/test_codegen",
            reports,
            plan,
            backend_port=18001,
        )
    if failure == "known":
        checkpoint = json.loads((reports / "recovery.json").read_text(encoding="utf-8"))
        assert checkpoint["stage"] == "validation-interrupted"
        assert checkpoint["resumable"] is True
        assert "raw-secret" not in (reports / "failure.log").read_text(encoding="utf-8")
    else:
        assert not isinstance(raised.value, NativeValidationFailure)


@pytest.mark.parametrize(
    "failure",
    [
        "passed",
        "frontend_started",
        "restart",
        "restart_preserved_records",
        "json",
        "value",
        "assertion",
        "permission",
        "zip",
        "source",
    ],
)
def test_real_portable_receipt_boundary_is_narrow(tmp_path, monkeypatch, failure):
    from contextlib import nullcontext
    from types import SimpleNamespace

    from workbench import filesystem
    from workbench.delivery import portable
    from workbench.infrastructure.processes import tools

    product = tmp_path / "product"
    product.mkdir()
    filesystem.atomic_text(product / "start.py", "# fixture\n")
    monkeypatch.setattr(
        portable.psycopg,
        "connect",
        lambda *args, **kwargs: nullcontext(SimpleNamespace(execute=lambda *args: None)),
    )
    if failure == "zip":
        monkeypatch.setattr(filesystem, "unpack", lambda *args, **kwargs: {})

    def run(command, cwd, *args, **kwargs):
        errors = {"value": ValueError, "assertion": AssertionError, "permission": PermissionError}
        if failure in errors:
            raise errors[failure]("raw-secret")
        if failure == "source":
            filesystem.atomic_text(product / "start.py", "changed\n")
        target = cwd / ".deployment/reports/portable-start.json"
        if failure == "json":
            filesystem.atomic_text(target, "{invalid raw-secret")
        else:
            result = {
                "passed": True,
                "frontend_started": True,
                "restart": True,
                "business": True,
                "restart_preserved_records": True,
            }
            if failure in result:
                result[failure] = False
            filesystem.write_json(target, result)
        return {"log": "fixture"}

    monkeypatch.setattr(tools, "run_command", run)
    recognized = failure in {"passed", "frontend_started", "restart", "restart_preserved_records"}
    expected = (
        NativeValidationFailure
        if recognized
        else PermissionError
        if failure == "permission"
        else AssertionError
        if failure == "assertion"
        else ValueError
    )
    with pytest.raises(expected) as raised:
        native_lab._runtime_check(
            portable.verify_native_delivery,
            product,
            "postgresql://localhost/test_codegen",
            tmp_path / "reports",
            template="fastapiadmin",
            source_handoff=lambda *args: None,
            check_id="independent-native-delivery",
        )
    if recognized:
        assert "portable_evidence_failed" in str(raised.value)
        assert "raw-secret" not in str(raised.value)
    else:
        assert not isinstance(raised.value, NativeValidationFailure)
