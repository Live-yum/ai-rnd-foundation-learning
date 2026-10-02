"""Missing acceptance evidence must never become READY, even with green unit tests."""

import json

import pytest
from conftest import FixtureGateway, new_run
from test_native_managed import verified_fixture

from workbench.domain import ModelReview
from workbench.errors import UnsupportedScope
from workbench.filesystem import sha, write_json
from workbench.flow import Workflow
from workbench.generator import PrerequisiteError
from workbench.native_delivery import managed_verify
from workbench.runtime import Runtime


def test_explicit_review_gap_blocks_smart_delivery(settings, store, plan):
    settings.model_review = True

    class Reviewer(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is ModelReview:
                assert payload["independent_evidence"]["passed"] is True
                return ModelReview(
                    summary="发现缺口，不能交付",
                    uncovered_requirements=["已批准的组合筛选尚未实现"],
                )
            return super().complete(run, key, instruction, payload, schema)

    run = new_run(store)
    store.set_automation(run, True, "one-consent")
    with Runtime(settings, store, Reviewer(plan)) as worker:
        worker.tick()
    current = store.get_run(run)
    assert current["status"] == "BLOCKED", current
    assert "组合筛选" in current["error"]
    assert current["pending"] is None
    root = settings.data_dir / "runs" / run
    assert not (root / "delivery.zip").exists()
    assert not (root / "delivery.json").exists()
    report = json.loads((root / "model-review.json").read_text(encoding="utf-8"))
    assert report["delivery_clearance"] is False
    assert report["uncovered_requirements"] == ["已批准的组合筛选尚未实现"]
    assert len(store.messages(run)) == 1
    settings.model_review = False
    store.retry(run, "cannot-waive-review")
    with Runtime(settings, store, Reviewer(plan)) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "BLOCKED"
    assert not (root / "delivery.zip").exists()


def test_package_rechecks_review_from_older_checkpoint(settings, store, monkeypatch):
    import workbench.flow as flow

    def must_not_package(*args, **kwargs):
        pytest.fail("A saved review with missing requirements must not reach packaging")

    monkeypatch.setattr(flow, "package_basic", must_not_package)
    workflow = Workflow(settings, store, None)
    with pytest.raises(UnsupportedScope, match="审阅"):
        workflow.package(
            {
                "run_id": "saved-review",
                "template": "python-basic",
                "model_review": {
                    "enabled": True,
                    "uncovered_requirements": ["未实现已批准功能"],
                },
            }
        )


@pytest.mark.parametrize(
    "field",
    [
        "passed",
        "fresh_database",
        "frontend_started",
        "installed_from_lock",
        "standalone_launcher",
        "restart",
    ],
)
@pytest.mark.parametrize("value", [False, None, "true", 1])
def test_native_requires_exact_positive_restore_evidence(tmp_path, field, value):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data.setdefault("portable_restored", {})[field] = value
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize(
    "field", ["source_database_reused", "original_platform_imported", "model_required"]
)
@pytest.mark.parametrize("value", [True, None, "false", 0])
def test_native_cannot_depend_on_generation_environment(tmp_path, field, value):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data.setdefault("portable_restored", {})[field] = value
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize("restored", [None, {}, True, {"passed": True}])
def test_native_rejects_absent_or_partial_restore_report(tmp_path, restored):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data["portable_restored"] = restored
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "partial",
        "template",
        "family",
        "passed",
        "truthy_passed",
        "shell",
        "truthy_shell",
        "substitution",
        "falsey_substitution",
        "protected",
        "digest",
        "pages",
        "page_hash",
        "page_path",
        "components",
        "entities",
        "wrong_components",
        "unhashable_path",
    ],
)
def test_native_style_receipt_cannot_be_skipped_or_forged(tmp_path, change):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    style = data["native_style"]
    if change == "missing":
        data.pop("native_style")
    elif change == "partial":
        data["native_style"] = {"passed": True}
    elif change == "template":
        style["template"] = "yudao-vben"
    elif change == "family":
        style["ui_family"] = "simple-admin"
    elif change in {"passed", "truthy_passed"}:
        style["passed"] = False if change == "passed" else 1
    elif change in {"shell", "truthy_shell"}:
        style["shell_and_theme_unchanged"] = False if change == "shell" else "true"
    elif change in {"substitution", "falsey_substitution"}:
        style["generic_frontend_substitution"] = True if change == "substitution" else 0
    elif change == "protected":
        style["protected_files"] = {}
    elif change == "digest":
        style["protected_source_digest"] = "0" * 64
    elif change == "pages":
        style["generated_pages"] = []
    elif change == "page_hash":
        style["generated_pages"][0]["sha256"] = "0" * 64
    elif change == "page_path":
        style["generated_pages"][0]["path"] = "../../unrelated.vue"
    elif change == "components":
        style["generated_pages"][0]["native_components"] = []
    elif change == "entities":
        data["entities"] = []
    elif change == "wrong_components":
        style["generated_pages"][0]["native_components"] = ["GenericTable"]
    elif change == "unhashable_path":
        style["generated_pages"][0]["path"] = []
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="原生UI"):
        managed_verify(product, receipt)
    assert not (product.parent / "verification.json").exists()
