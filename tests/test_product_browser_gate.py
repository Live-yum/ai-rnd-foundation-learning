"""Browser evidence is mandatory for each generated UI and its clean-room delivery."""

import json

import pytest

from workbench.filesystem import write_json
from workbench.generator import PrerequisiteError, generate_basic
from workbench.verification import package_basic, require_browser_evidence, verify_basic


def product(tmp_path, plan, frontend="simple-admin"):
    path = tmp_path / "product"
    generate_basic(plan, path, {"template": "python-basic", "frontend": frontend})
    return path


@pytest.mark.parametrize(
    "browser",
    [
        None,
        {},
        {"passed": True},
        {
            "passed": True,
            "real_browser": True,
            "applicable": True,
            "entities": ["task"],
            "checks": [],
            "errors": [],
        },
    ],
)
def test_ui_never_accepts_missing_partial_browser_report(tmp_path, plan, browser):
    target = product(tmp_path, plan)
    with pytest.raises(PrerequisiteError, match="浏览器"):
        require_browser_evidence(target, {"passed": True, "browser": browser})


def test_api_only_has_no_fabricated_browser_success(tmp_path, plan):
    target = product(tmp_path, plan, "api-only")
    require_browser_evidence(target, {"passed": True})


def test_ui_rejects_older_http_only_runtime_receipt(tmp_path, plan, settings, monkeypatch):
    target = product(tmp_path, plan)

    def old_probe(product, python, report_path, settings):
        write_json(report_path, {"passed": True, "restart": True, "http": True})
        return {"returncode": 0}

    monkeypatch.setattr("workbench.verification.run_probe", old_probe)
    with pytest.raises(PrerequisiteError, match="浏览器"):
        verify_basic(plan, target, settings)
    assert not (tmp_path / "verification.json").exists()


def test_real_browser_spec_and_cleanroom_gate(tmp_path, settings):
    # Real browser, real generated product, no model and no patched evidence.
    from scripts.news_fixture import news_spec
    from workbench.domain import Plan

    plan = Plan.model_validate(news_spec())
    target = product(tmp_path, plan)
    report = verify_basic(plan, target, settings)
    assert report["passed"] is True, report
    assert report["browser"]["real_browser"] is True
    delivery = package_basic(plan, target, settings, report)
    assert delivery["cleanroom"]["browser"]["real_browser"] is True
    assert delivery["cleanroom"]["browser"]["entities"] == [e.name for e in plan.entities]
    saved = json.loads((tmp_path / "verification.json").read_text(encoding="utf-8"))
    assert saved["browser"]["errors"] == []


def test_missing_browser_is_environment_blocker_not_auto_repair(
    tmp_path, plan, settings, monkeypatch
):
    target = product(tmp_path, plan)
    monkeypatch.setenv("PRODUCT_VERIFY_PLAYWRIGHT", str(tmp_path / "absent-playwright"))
    with pytest.raises(PrerequisiteError, match="Playwright"):
        verify_basic(plan, target, settings)
    assert not (tmp_path / "verification.json").exists()
    assert not (tmp_path / "delivery.zip").exists()


def test_real_browser_rejects_broken_generated_search_ui(tmp_path, settings):
    from scripts.news_fixture import news_spec
    from workbench.domain import Plan
    from workbench.tools import ToolFailure
    from workbench.verification import run_probe

    plan = Plan.model_validate(news_spec())
    target = product(tmp_path, plan)
    ui = target / "web/app.js"
    original = ui.read_text(encoding="utf-8")
    broken = original.replace(
        "if (value) query.set(key, value);", "if (value && key !== 'q') query.set(key, value);"
    )
    assert broken != original
    ui.write_text(broken, encoding="utf-8")
    report_path = tmp_path / "broken-browser.json"
    # Probe directly to prove the browser itself detects a broken UI. The normal
    # gate additionally rejects this mutation against the generation manifest.
    import sys

    with pytest.raises(ToolFailure):
        run_probe(target, sys.executable, report_path, settings)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is False
    assert "browser acceptance failed" in report["message"]


def test_optional_text_omitted_in_approved_rule_sample_still_checks_limits(
    tmp_path, plan, settings
):
    from workbench.domain import Plan

    data = plan.model_dump()
    data["entities"][0]["fields"].append(
        {"name": "notes", "kind": "text", "required": False, "max_length": 30}
    )
    data["custom_rules"] = [
        {
            "description": "priority cannot be negative",
            "entity": "task",
            "accept_examples": [{"title": "allowed", "priority": 1, "done": False}],
            "reject_examples": [{"title": "rejected", "priority": -1, "done": False}],
        }
    ]
    plan = Plan.model_validate(data)
    target = product(tmp_path, plan)
    (target / "custom_rules.py").write_text(
        "def validate(entity, data):\n"
        "    if entity == 'task' and data['priority'] < 0:\n"
        "        raise ValueError('priority cannot be negative')\n"
    )
    report = verify_basic(plan, target, settings)
    assert report["passed"] is True, report
    assert "browser-overlength-rejected:task.notes" in report["browser"]["checks"]
