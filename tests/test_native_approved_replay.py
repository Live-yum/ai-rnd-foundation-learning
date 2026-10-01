"""Approved-plan provenance checks precede native generation; never a model substitute."""

import hashlib
import json
import re

import pytest

from scripts import ci_native_bundled as replay
from workbench.domain import Plan
from workbench.settings import ROOT


def test_exact_approved_yudao_replay_preserves_original_schema_and_bytes():
    record = replay.APPROVED_CUSTOMER_REPLAYS["yudao-1d7"]
    raw = (ROOT / record["path"]).read_bytes()
    assert len(raw) == 19534
    assert (
        hashlib.sha256(raw).hexdigest()
        == "16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5"
    )
    plan = replay.approved_customer_replay("yudao-1d7", "yudao-vben")
    assert plan == Plan.model_validate_json(raw)
    assert {entity.name for entity in plan.entities} == {"customers", "requests", "tasks"}
    assert {role.name for role in plan.business.roles} == {"manager", "service", "employee"}
    note = (ROOT / "tests/fixtures/customer_approved_replays/README.md").read_text(encoding="utf-8")
    assert "36795375784" in note and "1d7c70b03e63509830e97af9af398c0bd148902e" in note
    assert "never reads this fixture" in note


@pytest.mark.parametrize(
    "kind", ["digest", "oversize", "schema", "credential", "candidate_envelope"]
)
def test_approved_replay_rejects_untrusted_payload_before_generation(tmp_path, monkeypatch, kind):
    original = replay.APPROVED_CUSTOMER_REPLAYS["yudao-1d7"]
    data = json.loads((ROOT / original["path"]).read_text(encoding="utf-8"))
    if kind == "oversize":
        data["acceptance"] = ["x" * 140000]
    elif kind == "schema":
        data["entities"] = "not-an-entity-list"
    elif kind == "credential":
        data["acceptance"] = ["DATABASE_PASSWORD=secret-test-canary"]
    elif kind == "candidate_envelope":
        data = {
            "approval_status": "unapproved",
            "execution_authorized": False,
            "candidate_plan": data,
        }
    raw = json.dumps(data).encode()
    path = tmp_path / "fixture.json"
    path.write_bytes(raw)
    monkeypatch.setattr(replay, "ROOT", tmp_path)
    monkeypatch.setitem(
        replay.APPROVED_CUSTOMER_REPLAYS,
        "test",
        {
            "path": path.name,
            "template": "yudao-vben",
            "sha256": "0" * 64 if kind == "digest" else hashlib.sha256(raw).hexdigest(),
        },
    )
    with pytest.raises(ValueError) as caught:
        replay.approved_customer_replay("test", "yudao-vben")
    assert "secret-test-canary" not in str(caught.value)


def test_approved_replay_template_is_not_read_from_fixture():
    with pytest.raises(ValueError, match="template/path"):
        replay.approved_customer_replay("yudao-1d7", "fastapiadmin")


def test_replay_workflow_is_separate_and_has_unique_artifacts():
    source = (ROOT / ".github/workflows/customer-runtime.yml").read_text(encoding="utf-8")
    assert "--approved-replay yudao-1d7" in source
    assert "--spec examples/plans/customer-service.json" in source
    assert "native-runtime-${{ matrix.template }}-${{ matrix.case }}" in source
    assert source.count("case: canonical") == 2
    assert source.count("case: approved-1d7") == 1
    assert not re.search(r"^\s*(?:API_KEY|BASE_URL)\s*:", source, re.M)
    genuine = (ROOT / "scripts/ci_real_model.py").read_text(encoding="utf-8")
    assert "customer_approved_replays" not in genuine
    assert "approved_customer_replay" not in genuine
