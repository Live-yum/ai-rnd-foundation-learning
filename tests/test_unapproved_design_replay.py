"""Failure diagnostics preserve exact contracts without conferring execution approval."""

import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from scripts.ci_real_model import (
    MAX_REPLAY_PLAN_BYTES,
    DiagnosticTextBudget,
    preserve_unapproved_design_contract,
)
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT


class ContractStore:
    def __init__(self):
        self.run = {"status": "BLOCKED", "template": "yudao-vben"}
        self.requirement = Requirement(
            summary="客户服务",
            users=["管理人员", "服务人员"],
            data_scope="shared",
            features=[],
            acceptance=[],
            facts={
                "metrics": [
                    {
                        "name": "requests_total",
                        "entity": "requests",
                        "role_scope": ["manager", "service"],
                    }
                ]
            },
        ).model_dump()
        self.plan = json.loads(
            (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
        )
        self.calls = []

    def get_run(self, run_id):
        self.calls.append(("get_run", run_id))
        return deepcopy(self.run)

    def latest_revision(self, run_id, stage):
        self.calls.append(("latest_revision", run_id, stage))
        return (
            {"requirement": deepcopy(self.requirement)}
            if stage == "requirements"
            else {"plan": deepcopy(self.plan)}
        )


def save(store, path, secret="exact-key-canary"):
    return preserve_unapproved_design_contract(
        store, "synthetic-run", path, DiagnosticTextBudget(secrets=(secret,), limit=0)
    )


def test_failure_contract_is_exact_bounded_and_not_a_generation_input(tmp_path):
    store = ContractStore()
    original = deepcopy(store.requirement), deepcopy(store.plan), deepcopy(store.run)
    path = tmp_path / "unapproved-design-contract.json"
    receipt = save(store, path)
    assert receipt["status"] == "saved" and receipt["execution_authorized"] is False
    assert receipt["bytes"] <= MAX_REPLAY_PLAN_BYTES
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["approval_status"] == "unapproved"
    assert payload["purpose"] == "offline_contract_validation_only"
    assert payload["execution_authorized"] is False
    assert payload["requirement"] == Requirement.model_validate(store.requirement).model_dump()
    assert payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()
    with pytest.raises(ValidationError):
        Plan.model_validate(payload)
    assert (store.requirement, store.plan, store.run) == original
    assert all(call[0] in {"get_run", "latest_revision"} for call in store.calls)


@pytest.mark.parametrize("state", ["READY", "SOURCE_READY", "WAITING_DESIGN", "RUNNING"])
def test_nonfailure_cannot_write_unapproved_contract(tmp_path, state):
    store = ContractStore()
    store.run["status"] = state
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "not_failure"}
    assert not target.exists()


@pytest.mark.parametrize("state", ["READY", "SOURCE_READY"])
def test_outer_acceptance_failure_retains_exact_contract_without_execution_approval(
    tmp_path, state
):
    store = ContractStore()
    store.run["status"] = state
    target = tmp_path / "unapproved-design-contract.json"
    receipt = preserve_unapproved_design_contract(
        store, "synthetic-run", target, DiagnosticTextBudget(), acceptance_failed=True
    )
    assert receipt["status"] == "saved"
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["execution_authorized"] is False
    assert payload["requirement"] == store.requirement
    assert payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()
    with pytest.raises(ValidationError):
        Plan.model_validate(payload)


@pytest.mark.parametrize("flag", [False, "true", 1, None])
def test_outer_failure_flag_cannot_be_coerced(tmp_path, flag):
    store = ContractStore()
    store.run["status"] = "READY"
    target = tmp_path / "unapproved-design-contract.json"
    assert preserve_unapproved_design_contract(
        store, "synthetic-run", target, DiagnosticTextBudget(), acceptance_failed=flag
    ) == {"status": "not_failure"}
    assert not target.exists()


def test_ready_outer_failure_still_rejects_secrets(tmp_path):
    store = ContractStore()
    store.run["status"] = "READY"
    store.requirement["facts"]["example"] = "exact-key-canary"
    target = tmp_path / "unapproved-design-contract.json"
    assert preserve_unapproved_design_contract(
        store,
        "synthetic-run",
        target,
        DiagnosticTextBudget(secrets=("exact-key-canary",)),
        acceptance_failed=True,
    ) == {"status": "secret_scan_rejected"}
    assert not target.exists()


@pytest.mark.parametrize(
    "secret",
    [
        "exact-key-canary",
        "Authorization: Bearer opaque-token",
        "password=hidden-value",
        "https://user:hidden-value@example.invalid",
        "sk-credentialcanary12345",
    ],
)
def test_both_contract_strings_and_structural_secrets_are_rejected(tmp_path, secret):
    store = ContractStore()
    store.requirement["facts"]["description"] = secret
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "secret_scan_rejected"}
    assert not target.exists()
    store.requirement["facts"] = {"configuration": {"password": "hidden-value"}}
    assert save(store, target) == {"status": "secret_scan_rejected"}
    assert not target.exists()


@pytest.mark.parametrize("which", ["requirement", "plan"])
def test_malformed_normalized_schema_is_rejected(tmp_path, which):
    store = ContractStore()
    getattr(store, which)["provider_headers"] = {"x": "not selected"}
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "invalid_schema"}
    assert not target.exists()


def test_oversized_contract_is_rejected_without_truncating_or_persisting(tmp_path):
    store = ContractStore()
    store.requirement["facts"]["large"] = "A" * (MAX_REPLAY_PLAN_BYTES + 1)
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "size_limit"}
    assert not target.exists()


def test_out_of_scope_or_missing_contract_never_uses_other_data(tmp_path):
    store = ContractStore()
    target = tmp_path / "unapproved-design-contract.json"
    store.run["template"] = "unrelated"
    assert save(store, target) == {"status": "outside_customer_scope"}
    store.run["template"] = "python-basic"
    store.plan = None
    assert save(store, target) == {"status": "unavailable"}
    assert not target.exists()


def test_artifact_is_failure_only_with_distinct_nonexecutable_path():
    source = (ROOT / ".github/workflows/native-probe.yml").read_text(encoding="utf-8")
    section = source.split("- name: Retain unapproved normalized design", 1)[1].split("- name:", 1)[
        0
    ]
    assert "if: failure()" in section
    assert "path: reports/real-model/unapproved-design-contract.json" in section
    assert "retention-days: 7" in section
    assert "run:" not in section
