import json
from pathlib import Path

import pytest

from workbench.aider_tools import Edit, Edits, apply_edits, proposed_content
from workbench.filesystem import atomic_text, sha
from workbench.generator import generate_basic
from workbench.tools import ToolFailure

BEFORE = "def validate(entity, data):\n    return None\n"
AFTER = "def validate(entity, data):\n    if entity == 'task' and data['priority'] < 0:\n        raise ValueError('priority')\n    return None\n"


def proposal(path):
    return Edits(
        before_sha256=sha(path),
        edits=[Edit(search="    return None\n", replace=AFTER.split("\n", 1)[1])],
        explanation="Approved nonnegative priority rule",
    )


@pytest.mark.parametrize(
    "edit",
    [
        Edit(search="missing\n", replace=""),
        Edit(search="    return None\n", replace="    return None\n"),
        Edit(search="    return None\n", replace="<<<<<<< SEARCH\n"),
        Edit(search="    return None\n", replace="    import os\n"),
    ],
)
def test_untrusted_edit_rejected(edit):
    with pytest.raises(ValueError):
        proposed_content(BEFORE, Edits(before_sha256="0" * 64, edits=[edit], explanation="test"))


def test_transaction_and_replay_have_real_rollback_bundle(tmp_path, settings, plan, monkeypatch):
    product = tmp_path / "product"
    generate_basic(plan, product)
    atomic_text(product / "custom_rules.py", BEFORE)
    change = proposal(product / "custom_rules.py")

    def fake_worker(operation, source, argument, output, timeout):
        # Only this protocol test substitutes Aider. ci_toolchain runs the actual installed CLI.
        assert operation == "apply"
        assert "<<<<<<< SEARCH" in Path(argument).read_text(encoding="utf-8")
        atomic_text(Path(source) / "custom_rules.py", AFTER)
        atomic_text(output, "{}")

    monkeypatch.setattr("workbench.aider_tools.worker", fake_worker)
    receipt = apply_edits(product, change, settings, 0)
    assert receipt["before_commit"] != receipt["after_commit"]
    assert sha(tmp_path / receipt["bundle"]) == receipt["bundle_sha256"]
    assert receipt["model_calls_by_aider"] == 0
    assert apply_edits(product, change, settings, 0)["replayed"] is True
    assert (product / "custom_rules.py").read_text(encoding="utf-8") == AFTER
    assert not (product / ".git").exists()
    assert json.loads((tmp_path / "aider-0.json").read_text())["proposal_digest"]


@pytest.mark.parametrize("mode", ["failure", "wrong", "extra"])
def test_worker_failures_never_modify_product(tmp_path, settings, plan, monkeypatch, mode):
    product = tmp_path / "product"
    generate_basic(plan, product)
    atomic_text(product / "custom_rules.py", BEFORE)
    change = proposal(product / "custom_rules.py")

    def fake_worker(operation, source, argument, output, timeout):
        if mode == "failure":
            raise ToolFailure("injected tool failure")
        atomic_text(Path(source) / "custom_rules.py", "wrong" if mode == "wrong" else AFTER)
        if mode == "extra":
            atomic_text(Path(source) / "unexpected.py", "bad")

    monkeypatch.setattr("workbench.aider_tools.worker", fake_worker)
    with pytest.raises((ValueError, ToolFailure)):
        apply_edits(product, change, settings, 0)
    assert (product / "custom_rules.py").read_text(encoding="utf-8") == BEFORE


def test_stale_sha_is_rejected_before_tool(tmp_path, settings, monkeypatch):
    product = tmp_path / "product"
    product.mkdir()
    atomic_text(product / "custom_rules.py", BEFORE)
    change = proposal(product / "custom_rules.py")
    atomic_text(product / "custom_rules.py", AFTER)
    monkeypatch.setattr(
        "workbench.aider_tools.worker", lambda *a: pytest.fail("must not invoke tool")
    )
    with pytest.raises(ValueError, match="过期"):
        apply_edits(product, change, settings, 0)
