"""Candidate editing must not mutate baselines or execute product code."""

import pytest

from workbench.capability_contracts import CapabilityEdits, CapabilityTask
from workbench.capability_editing import apply_candidate
from workbench.filesystem import sha


def task(files):
    return CapabilityTask(
        id="team",
        title="Team rules",
        requirements=["source-0-0"],
        files=files,
        contract="Cross-record bounded team module",
        scenarios=["teams"],
    )


def edits(path, before=None, content="raise RuntimeError('never import generated code')\n"):
    return CapabilityEdits(
        explanation="test fixture",
        files=[{"path": path, "before_sha256": before, "content": content}],
    )


def test_candidate_is_separate_and_replay_is_hash_bound(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original\n")
    before = sha(product / "app.py")
    value = edits("app.py", before)
    candidate = tmp_path / "candidate"
    receipt = apply_candidate(
        product, value, task(["app.py"]), {"template": "python-basic"}, candidate
    )
    assert receipt["host_execution"] is False
    assert (product / "app.py").read_text() == "original\n"
    assert "never import" in (candidate / "app.py").read_text()
    assert (
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)
        == receipt
    )
    (candidate / "app.py").write_text("tampered")
    with pytest.raises(ValueError, match="身份"):
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)


@pytest.mark.parametrize(
    "path",
    [
        "pyproject.toml",
        "verify.py",
        "workbench/flow.py",
        "deployment/run.py",
        "start.py",
        "package.json",
    ],
)
def test_protected_paths_cannot_be_approved_by_model(tmp_path, path):
    product = tmp_path / "product"
    product.mkdir()
    with pytest.raises(ValueError):
        apply_candidate(
            product, edits(path), task([path]), {"template": "python-basic"}, tmp_path / "candidate"
        )
    assert not (tmp_path / "candidate").exists()


def test_stale_and_extra_edits_fail_before_copy(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original")
    with pytest.raises(ValueError, match="前像"):
        apply_candidate(
            product,
            edits("app.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )
    with pytest.raises(ValueError, match="全部文件"):
        apply_candidate(
            product,
            edits("extra.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )
