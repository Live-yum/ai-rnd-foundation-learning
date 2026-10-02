"""Signup lessons and restored real-browser evidence fail closed independently."""

import hashlib
import json

import pytest

from scripts import build_learning_docs as builder
from scripts import ci_learning_docs as acceptance
from scripts.handbook_notes import purpose
from scripts.rebuild_learning_docs import check_fences

PNG_BYTES = b"\x89PNG\r\n\x1a\nfixture-test-bytes"
BUNDLE_FILES = {
    "workbench/web/index.html": b"fixture HTML",
    "workbench/web/app.js": b"fixture Javascript",
    "workbench/web/style.css": b"fixture CSS",
}
SCREENSHOTS = [
    "scope-blocked.png",
    "scope-blocked-mobile.png",
    "scope-options-mobile.png",
    "scope-corrected.png",
]


def valid_summary():
    return {
        **dict.fromkeys(acceptance.SIGNUP_SCOPE_TRUE_FIELDS, True),
        "run_id": "same-fixture-run",
        "native_generation_attempted": False,
        "external_provider_calls": False,
        "fixture_mode": "in-process-requirement-gateway",
        "fixture_model_calls": [{"run_id": "same-fixture-run", "key": "requirement:3"}],
        "original_approval_count": 1,
        "recovered_approval_count": 1,
        "status": "WAITING_REQUIREMENTS",
        "errors": [],
        "screenshots": SCREENSHOTS,
        "ui_bundle_sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in BUNDLE_FILES.items()
        },
        "screenshot_sha256": dict.fromkeys(SCREENSHOTS, hashlib.sha256(PNG_BYTES).hexdigest()),
    }


def browser_files(destination, summary, *, missing_image=False):
    folder = destination / "reports/signup-scope-browser"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "browser.json").write_text(json.dumps(summary), encoding="utf-8")
    for name, data in BUNDLE_FILES.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for name in SCREENSHOTS:
        if not missing_image or name != "scope-corrected.png":
            (folder / name).write_bytes(PNG_BYTES)


def test_signup_cleanroom_driver_and_evidence_are_separate(tmp_path):
    destination, evidence = tmp_path / "student", tmp_path / "evidence/current"
    summary = valid_summary()
    commands = []

    def run(argv):
        commands.append(argv)
        browser_files(destination, summary)

    result = acceptance.verify_signup_scope_browser(destination, "student-python", run, evidence)
    assert result == summary
    assert commands == [["student-python", "-m", "scripts.ci_signup_scope_browser"]]
    assert json.loads((evidence / "browser.json").read_text(encoding="utf-8")) == summary
    assert (evidence / "scope-corrected.png").is_file()


@pytest.mark.parametrize("field", acceptance.SIGNUP_SCOPE_TRUE_FIELDS)
@pytest.mark.parametrize("bad", [False, None, 1, "true"])
def test_signup_evidence_requires_literal_success_for_every_claim(tmp_path, field, bad):
    destination = tmp_path / "student"
    summary = valid_summary()
    summary[field] = bad
    with pytest.raises(AssertionError, match="browser/recovery evidence"):
        acceptance.verify_signup_scope_browser(
            destination, "python", lambda _: browser_files(destination, summary), tmp_path / "out"
        )
    assert (tmp_path / "out/browser.json").is_file()


@pytest.mark.parametrize(
    "field,bad",
    [
        ("native_generation_attempted", True),
        ("native_generation_attempted", 0),
        ("external_provider_calls", True),
        ("external_provider_calls", None),
        ("fixture_mode", "real-model"),
        ("status", "READY"),
        ("errors", ["failed request"]),
        ("fixture_model_calls", []),
        ("fixture_model_calls", [{"run_id": "other-run"}]),
        ("fixture_model_calls", [{"run_id": "same-fixture-run"}] * 2),
        ("run_id", ""),
        ("original_approval_count", 0),
        ("recovered_approval_count", True),
        ("recovered_approval_count", 2),
        ("screenshots", []),
        ("screenshots", ["../unrelated.png"]),
        ("ui_bundle_sha256", {}),
        ("screenshot_sha256", {"scope-blocked.png": "wrong"}),
    ],
)
def test_signup_cleanroom_rejects_changed_scope_or_missing_contract(tmp_path, field, bad):
    destination = tmp_path / "student"
    summary = valid_summary()
    summary[field] = bad
    with pytest.raises(AssertionError):
        acceptance.verify_signup_scope_browser(
            destination, "python", lambda _: browser_files(destination, summary), tmp_path / "out"
        )


def test_signup_cleanroom_requires_all_screenshot_files(tmp_path):
    destination = tmp_path / "student"
    with pytest.raises(AssertionError, match="all desktop/mobile PNG"):
        acceptance.verify_signup_scope_browser(
            destination,
            "python",
            lambda _: browser_files(destination, valid_summary(), missing_image=True),
            tmp_path / "out",
        )


def test_signup_cleanroom_preserves_failure_and_never_merges_previous_success(tmp_path):
    destination = tmp_path / "student"
    previous = tmp_path / "evidence/previous"
    previous.mkdir(parents=True)
    (previous / "browser.json").write_text('{"passed":true}', encoding="utf-8")
    evidence = tmp_path / "evidence/current"

    def run(_):
        folder = destination / "reports/signup-scope-browser"
        folder.mkdir(parents=True)
        (folder / "browser.log").write_text("current failure: 中文诊断", encoding="utf-8")
        raise RuntimeError("Chromium failed")

    with pytest.raises(RuntimeError, match="Chromium failed"):
        acceptance.verify_signup_scope_browser(destination, "python", run, evidence)
    assert (evidence / "browser.log").read_text(encoding="utf-8") == "current failure: 中文诊断"
    assert not (evidence / "browser.json").exists()
    assert (previous / "browser.json").read_text(encoding="utf-8") == '{"passed":true}'


@pytest.mark.parametrize("reuse", ["source", "destination"])
def test_signup_cleanroom_refuses_preexisting_evidence_before_running(tmp_path, reuse):
    destination, evidence = tmp_path / "student", tmp_path / "evidence"
    if reuse == "source":
        browser_files(destination, valid_summary())
    else:
        evidence.mkdir()
    commands = []
    with pytest.raises((FileExistsError, AssertionError)):
        acceptance.verify_signup_scope_browser(destination, "python", commands.append, evidence)
    assert commands == []


def test_signup_teaching_source_assignment_and_lessons_match_current_boundaries():
    for name in ("requirement_intent", "requirement_canonical"):
        assert builder.stage_for(f"workbench/{name}.py") == 3
        assert "项目根配置" not in purpose(f"workbench/{name}.py")[0]
    for name in ("ci_signup_scope_browser.py", "signup_scope_browser.cjs"):
        assert builder.stage_for(f"scripts/{name}") == 14
        assert "浏览器" in purpose(f"scripts/{name}")[0]
    stages = builder.read_content()
    assert "uv sync --locked --extra postgres" in stages[0]["body"]
    assert "不能因为框架能注册账号" in stages[3]["body"]
    assert "Workflow.capability_recovery" in stages[7]["body"]
    assert "capability_conflicts" in stages[8]["body"]
    assert "副作用" in stages[9]["body"]
    assert "uv run python -m scripts.ci_signup_scope_browser" in stages[14]["body"]
    assert "reports/learning-docs-signup-scope-browser/" in stages[14]["body"]
    assert "进程内需求网关夹具" in stages[14]["body"]
    assert all(check_fences(stage["body"]) >= 0 for stage in stages)


@pytest.mark.parametrize("damage", ["asset", "extra_asset", "screenshot"])
def test_signup_cleanroom_rejects_artifact_changes_after_report(tmp_path, damage):
    destination = tmp_path / "student"

    def run(_):
        browser_files(destination, valid_summary())
        if damage == "asset":
            (destination / "workbench/web/app.js").write_bytes(b"changed")
        elif damage == "extra_asset":
            (destination / "workbench/web/unreported.js").write_bytes(b"extra")
        else:
            (destination / "reports/signup-scope-browser/scope-corrected.png").write_bytes(
                PNG_BYTES + b"changed"
            )

    with pytest.raises(AssertionError, match="must bind"):
        acceptance.verify_signup_scope_browser(destination, "python", run, tmp_path / "out")
