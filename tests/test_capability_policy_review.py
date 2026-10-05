"""Independent data-only regressions; these do not certify live execution."""

from copy import deepcopy

import pytest

from scripts.capability_fixture import GOAL, make_plan
from scripts.extension_oracles import contest
from workbench.capability_contracts import CapabilityPlan, scope_sources
from workbench.capability_policy import CONTEST_BINDINGS, contract_errors, scope_policy
from workbench.catalog import Selection
from workbench.domain import digest


def policy_for(text):
    messages = [text]
    scope = {
        "messages": messages,
        "source_digest": digest(messages),
        "sources": scope_sources(messages),
    }
    original = deepcopy(scope)
    policy = scope_policy(scope, Selection(template="fastapiadmin").model_dump())
    assert scope == original, "Policy matching must preserve exact original source evidence"
    assert policy["source_units_digest"] == digest(scope["sources"])
    return policy


@pytest.mark.parametrize("style", ["bullets", "numbered", "wrapped", "punctuation"])
def test_formatting_cannot_downgrade_registered_business_oracle(style):
    lines = list(CONTEST_BINDINGS)
    if style == "bullets":
        lines = ["- " + line for line in lines]
    elif style == "numbered":
        lines = [f"{index + 1}. {line}" for index, line in enumerate(lines)]
    elif style == "wrapped":
        lines = [line[:12] + "\n" + line[12:] for line in lines]
    else:
        lines = [line.replace("。", ";").replace("：", ":") for line in lines]
    assert policy_for("\n".join(lines))["trusted_oracle"] == contest.CONTRACT_VERSION


def make_contract():
    return make_plan(
        {
            "source_units": scope_sources([GOAL]),
            "source_digest": digest([GOAL]),
            "selection": Selection().model_dump(),
        }
    ).model_dump()


@pytest.mark.parametrize("positive", [{"absent": ["$.business"]}, {"equals": {"$.ok": True}}])
def test_empty_or_status_envelope_is_not_business_acceptance(positive):
    raw = make_contract()
    for scenario in raw["scenarios"]:
        scenario["steps"] = [
            {"method": "POST", "path": "/probe", "status": 200, **positive},
            {"path": "/nonexistent", "status": 404},
        ]
        scenario["after_restart"] = [{"path": "/probe", "status": 200, **positive}]
    assert contract_errors(CapabilityPlan.model_validate(raw))


def test_failed_read_after_restart_cannot_count_as_persistence():
    raw = make_contract()
    for scenario in raw["scenarios"]:
        scenario["after_restart"] = [
            {"path": "/entries/${entry}", "status": 404, "equals": {"$.detail": "not found"}}
        ]
    assert any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))


def test_unrelated_restart_resource_cannot_borrow_written_value():
    raw = make_contract()
    for scenario in raw["scenarios"]:
        for step in scenario["after_restart"]:
            if step["status"] == 200:
                step["path"] = "/unrelated-static"
    assert any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))
