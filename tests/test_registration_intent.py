"""Deterministic scope choices and conservative, provenance-preserving compaction."""

import pytest
from conftest import requirement

from workbench.catalog import Selection
from workbench.clarification import render_answer
from workbench.domain import Requirement, digest
from workbench.requirement_coverage import reconcile
from workbench.requirement_intent import (
    ADMIN_SCOPE,
    AUTHENTICATED_SCOPE,
    admin_scope_correction,
    blocked_requirement,
    scope_conflicts,
)

ORIGINAL = "大学生计算机设计大赛报名网站"


@pytest.mark.parametrize("template", ["python-basic", "fastapiadmin", "yudao-vben"])
def test_ambiguous_registration_is_a_scope_question_not_anonymous_claim(template):
    capabilities = Selection(template=template).capabilities()
    conflict = scope_conflicts([ORIGINAL], capabilities)
    assert conflict[0]["code"] == "registration_entrypoint_unresolved"
    assert not conflict[0]["unsupported"]
    assert conflict[0]["source"] == {
        "section": "user_messages",
        "index": 0,
        "quote": ORIGINAL,
        "sha256": digest(ORIGINAL),
    }
    blocked = blocked_requirement({}, conflict, capabilities, [])
    assert blocked.summary == ORIGINAL and not blocked.ready
    assert blocked.unsupported == []
    assert len(blocked.question_items[0].options) == 3
    assert blocked.facts == {}


@pytest.mark.parametrize(
    "goal",
    [
        "账号注册和登录功能",
        "内部个人任务管理，用户注册账号并登录后管理自己的任务",
        "报名记录管理后台，仅管理员录入和维护报名记录",
        "比赛报名管理网站，只有管理员维护报名记录",
        "只做管理员后台，不需要报名网站",
        "参赛学生注册账号并登录后提交报名",
        AUTHENTICATED_SCOPE,
    ],
)
def test_supported_auth_and_admin_requests_are_not_public_requirements(goal):
    assert scope_conflicts([goal], Selection(template="fastapiadmin").capabilities()) == []


@pytest.mark.parametrize(
    "goal",
    [
        "大学生竞赛报名，学生无需登录提交报名",
        "大学生竞赛报名网站，支持匿名报名",
        "比赛要有独立公众报名页面",
        "给参赛者开发自定义公开报名门户",
    ],
)
def test_only_explicit_external_or_anonymous_portal_is_unsupported(goal):
    conflict = scope_conflicts([goal], Selection(template="fastapiadmin").capabilities())
    assert conflict[0]["code"] == "unsupported_registration_portal"
    assert conflict[0]["unsupported"] is True
    assert conflict[0]["source"]["quote"] == goal


@pytest.mark.parametrize(
    "answer", ["智能推荐", "按你的建议继续", "使用fastapiadmin模板", "队长统一提交"]
)
def test_recommendation_cannot_resolve_product_entrypoint(answer):
    capabilities = Selection(template="fastapiadmin").capabilities()
    assert scope_conflicts([ORIGINAL, answer], capabilities) == scope_conflicts(
        [ORIGINAL], capabilities
    )


@pytest.mark.parametrize(
    "answer",
    [
        "不要取消公开报名，改为仅管理员录入和维护报名记录",
        "取消公开报名网站，改为仅管理员录入和维护报名记录，但已注册学生也可提交报名",
        "取消匿名报名网站，改为仅管理员录入和维护报名记录，但也允许游客无需登录提交报名",
    ],
)
def test_mixed_or_negated_cancellation_is_not_admin_only_authorization(answer):
    assert not admin_scope_correction(answer)
    assert scope_conflicts([ORIGINAL, answer], Selection(template="fastapiadmin").capabilities())


@pytest.mark.parametrize(
    "option,blocked",
    [("authenticated_entry", False), ("admin_only", False), ("public_portal", True)],
)
def test_structured_scope_choice_uses_selected_option_not_question_or_other_options(
    option, blocked
):
    capabilities = Selection(template="fastapiadmin").capabilities()
    conflict = scope_conflicts([ORIGINAL], capabilities)
    requirement = blocked_requirement({}, conflict, capabilities, [])
    answer = render_answer(
        {"stage": "clarification", "data": {"requirement": requirement.gate_dump()}},
        {
            "text": "",
            "answers": [{"question_id": "registration_scope", "option_ids": [option], "text": ""}],
        },
    )
    assert bool(scope_conflicts([ORIGINAL, answer], capabilities)) is blocked
    if blocked:
        recovered = blocked_requirement(
            requirement.gate_dump(),
            scope_conflicts([ORIGINAL, answer], capabilities),
            capabilities,
            [],
            original_request=ORIGINAL,
        )
        assert recovered.summary == ORIGINAL
        assert recovered.unsupported


def test_declared_auth_mode_does_not_erase_explicit_anonymous_requirement():
    capabilities = Selection(template="fastapiadmin").capabilities()
    # Merely adding an authenticated flow is not permission to drop the original
    # anonymous flow; it requires explicit cancellation of that obligation.
    original = "比赛报名网站必须支持匿名报名"
    assert scope_conflicts([original, AUTHENTICATED_SCOPE], capabilities)


def test_canonical_lists_only_merge_complete_equivalent_phrases_and_record_spellings():
    previous = requirement().model_copy(
        update={
            "users": ["团队队长（仅作为联系人）", "管理员"],
            "features": ["支持报名记录的增删改查", "报名记录支持增删改查", "队名最长100字符"],
            "acceptance": ["对报名记录进行新增、查询、修改、删除"],
        }
    )
    candidate = previous.model_copy(
        update={
            "users": ["团队队长（仅联系人）", "团队队长（自行提交报名）"],
            "features": ["对报名记录进行新增、查询、修改、删除", "队名最长200字符"],
            "acceptance": ["支持报名记录的增删改查", "仅能删除本人报名记录"],
        }
    )
    original = previous.model_dump()
    audit = []
    result = reconcile(previous.gate_dump(), candidate, [], canonicalization=audit)
    assert result.users == ["团队队长（仅作为联系人）", "管理员", "团队队长（自行提交报名）"]
    assert result.features == ["支持报名记录的增删改查", "队名最长100字符", "队名最长200字符"]
    assert result.acceptance == ["对报名记录进行新增、查询、修改、删除", "仅能删除本人报名记录"]
    assert any(item["duplicate"] == "团队队长（仅联系人）" for item in audit)
    assert previous.model_dump() == original
    for _ in range(5):
        assert reconcile(result.gate_dump(), candidate, []).gate_dump() == result.gate_dump()


def test_explicit_admin_scope_correction_removes_only_atomic_legacy_goal():
    before = requirement().model_copy(
        update={"features": ["提供" + ORIGINAL, "报名网站及比赛结果公示"]}
    )
    proposed = before.model_dump()
    proposed["features"] = ["管理员维护报名记录"]
    proposed["changes"] = [
        {"section": "features", "key": old, "replacement": None, "source_quote": ADMIN_SCOPE}
        for old in before.features
    ]
    corrected = reconcile(before.gate_dump(), Requirement.model_validate(proposed), [ADMIN_SCOPE])
    assert "提供" + ORIGINAL not in corrected.features
    assert "报名网站及比赛结果公示" in corrected.features
    retained = reconcile(before.gate_dump(), Requirement.model_validate(proposed), ["智能推荐"])
    assert "提供" + ORIGINAL in retained.features


@pytest.mark.parametrize(
    "goal",
    [
        "内部员工登录后在现有业务界面自行报名，只维护本人记录",
        "公司内部培训报名网站，员工登录后提交报名",
        "仅管理员录入和维护报名网站",
    ],
)
def test_explicit_internal_modes_do_not_need_external_portal_choice(goal):
    assert scope_conflicts([goal], Selection(template="fastapiadmin").capabilities()) == []


@pytest.mark.parametrize(
    "feature",
    [
        "参赛者不得自行提交报名",
        "参赛者不能创建报名，由管理员代录",
        "管理员自行提交报名，参赛者仅是联系人",
    ],
)
def test_negative_or_admin_only_submission_is_not_positive_entrant_intent(feature):
    from workbench.requirement_intent import analysis_intent_conflicts

    candidate = requirement().model_copy(
        update={"users": ["参赛者", "管理员"], "features": [feature], "acceptance": [feature]}
    )
    assert analysis_intent_conflicts(candidate, [ORIGINAL, AUTHENTICATED_SCOPE])


def registration_plan():
    from workbench.domain import Plan

    return Plan.model_validate(
        {
            "title": ORIGINAL,
            "data_scope": "shared",
            "acceptance": [AUTHENTICATED_SCOPE],
            "entities": [
                {
                    "name": "registration",
                    "description": "比赛报名",
                    "fields": [{"name": "team_name", "kind": "text", "required": True}],
                }
            ],
            "business": {
                "roles": [
                    {"name": "entrant", "label": "参赛者"},
                    {"name": "organizer", "label": "赛事管理员"},
                ],
                "registration": {"enabled": True, "default_role": "entrant"},
                "bootstrap_role": "organizer",
                "role_admin_roles": ["organizer"],
                "resources": [{"entity": "registration"}],
                "permissions": [
                    {
                        "role": "entrant",
                        "entity": "registration",
                        "actions": ["create", "read", "update"],
                        "scope": "own",
                    },
                    {
                        "role": "organizer",
                        "entity": "registration",
                        "actions": ["create", "read", "update"],
                        "scope": "all",
                    },
                ],
            },
        }
    )


@pytest.mark.parametrize(
    "broken", ["no_business", "read_only", "all_rows", "registration_disabled", "unrelated_entity"]
)
def test_native_entrant_plan_needs_actual_registration_and_own_creation(broken):
    from workbench.requirement_intent import registration_plan_gaps

    plan = registration_plan()
    capabilities = Selection(template="fastapiadmin").capabilities()
    assert registration_plan_gaps(plan, [ORIGINAL, AUTHENTICATED_SCOPE], capabilities) == []
    if broken == "no_business":
        plan.business = None
    elif broken == "read_only":
        plan.business.permissions[0].actions = ["read"]
    elif broken == "all_rows":
        plan.business.permissions[0].scope = "all"
    elif broken == "registration_disabled":
        plan.business.registration.enabled = False
    else:
        plan.entities[0].name = "task"
        plan.entities[0].description = "任务"
    assert registration_plan_gaps(plan, [ORIGINAL, AUTHENTICATED_SCOPE], capabilities)


def test_unknown_literal_prose_must_not_be_normalized_into_false_equivalence():
    before = requirement().model_copy(
        update={
            "features": ["文件名必须是 file.", "选项标签为 Ａ"],
            "users": ["Ａ组（仅联系人）"],
        }
    )
    candidate = requirement().model_copy(
        update={
            "features": ["文件名必须是 file", "选项标签为 A"],
            "users": ["A组（仅联系人）"],
        }
    )
    merged = reconcile(before.gate_dump(), candidate, [])
    assert merged.features == [
        "文件名必须是 file.",
        "选项标签为 Ａ",
        "文件名必须是 file",
        "选项标签为 A",
    ]
    assert merged.users == ["Ａ组（仅联系人）", "A组（仅联系人）"]


def test_old_positive_phrase_cannot_hide_new_contact_only_contradiction():
    from workbench.requirement_intent import analysis_intent_conflicts

    candidate = requirement().model_copy(
        update={
            "users": ["参赛者", "队长（仅联系人）", "管理员"],
            "features": [AUTHENTICATED_SCOPE, "参赛者不得自行提交报名"],
            "acceptance": [AUTHENTICATED_SCOPE],
        }
    )
    assert analysis_intent_conflicts(candidate, [ORIGINAL, AUTHENTICATED_SCOPE])
