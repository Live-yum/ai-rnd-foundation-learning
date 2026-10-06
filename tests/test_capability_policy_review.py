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


@pytest.mark.parametrize(
    "text",
    [
        "用户通过邀请码加入普通团队。",
        "论文系统提供匿名评审与邀请码。",
        "不需要竞赛、邀请码和盲审，只做客户管理。",
        "竞赛不做邀请码和盲审。",
    ],
)
def test_unrelated_or_negated_keywords_do_not_bind_contest(text):
    assert policy_for(text)["trusted_oracle"] is None


@pytest.mark.parametrize(
    "messages,registered",
    [
        (["创建竞赛网站。", "另一个客服系统使用邀请码。", "论文库支持盲审。"], False),
        (["竞赛网站支持邀请码和盲审。", "取消竞赛，改成客户管理。"], False),
        (["竞赛网站支持邀请码和盲审。", "取消盲审。"], False),
        (["竞赛网站支持邀请码和盲审。", "竞赛取消了，只做客服。"], False),
        (["竞赛网站支持邀请码和盲审。", "盲审功能取消。"], False),
        (["竞赛网站支持邀请码和盲审。", "继续"], True),
    ],
)
def test_binding_tracks_coherent_active_human_sources(messages, registered):
    current = {
        "messages": messages,
        "source_digest": digest(messages),
        "sources": scope_sources(messages),
    }
    selected = scope_policy(current, Selection().model_dump())
    assert bool(selected["trusted_oracle"]) is registered
    assert bool(selected["oracle_source_ids"]) is registered
    assert selected["source_units_digest"] == digest(current["sources"])


@pytest.mark.parametrize(
    "change",
    [
        "取消竞赛报名截止时间限制。",
        "不要在竞赛页面显示学生姓名。",
    ],
)
def test_local_contest_changes_cannot_cancel_business_oracle(change):
    messages = ["竞赛网站支持邀请码和盲审。", change]
    current = {
        "messages": messages,
        "source_digest": digest(messages),
        "sources": scope_sources(messages),
    }
    selected = scope_policy(current, Selection().model_dump())
    assert selected["trusted_oracle"] == contest.CONTRACT_VERSION
    assert selected["oracle_source_ids"] == [current["sources"][0]["id"]]
    assert len(selected["goals"]) == 2
    assert selected["source_units_digest"] == digest(current["sources"])


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
