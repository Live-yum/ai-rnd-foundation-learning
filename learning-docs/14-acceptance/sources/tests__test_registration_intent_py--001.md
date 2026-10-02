# tests/test_registration_intent.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.clarification`、`workbench.domain`、`workbench.requirement_coverage`、`workbench.requirement_intent`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_ambiguous_registration_is_a_scope_question_not_anonymous_claim`（L22–L37）：接收`template`。 控制顺序：L25断言`conflict[0]["code"] == "registration_entrypoint_unresolved"`；L26断言`not conflict[0]["unsupported"]`；L27断言`conflict[0]["source"] == { "section": "user_messages", "index": 0, "quote": ORIGINAL,…`；L34断言`blocked.summary == ORIGINAL and not blocked.ready`；L35断言`blocked.unsupported == []`；L36断言`len(blocked.question_items[0].options) == 3`；L37断言`blocked.facts == {}`。 调用`Selection(template=template).capabilities`、`Selection`、`scope_conflicts`、`digest`、`blocked_requirement`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supported_auth_and_admin_requests_are_not_public_requirements`（L52–L53）：接收`goal`。 控制顺序：L53断言`scope_conflicts([goal], Selection(template="fastapiadmin").capabilities()) == []`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_external_or_anonymous_portal_is_unsupported`（L65–L69）：接收`goal`。 控制顺序：L67断言`conflict[0]["code"] == "unsupported_registration_portal"`；L68断言`conflict[0]["unsupported"] is True`；L69断言`conflict[0]["source"]["quote"] == goal`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recommendation_cannot_resolve_product_entrypoint`（L75–L79）：接收`answer`。 控制顺序：L77断言`scope_conflicts([ORIGINAL, answer], capabilities) == scope_conflicts( [ORIGINAL], cap…`。 调用`Selection(template="fastapiadmin").capabilities`、`Selection`、`scope_conflicts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mixed_or_negated_cancellation_is_not_admin_only_authorization`（L90–L92）：接收`answer`。 控制顺序：L91断言`not admin_scope_correction(answer)`；L92断言`scope_conflicts([ORIGINAL, answer], Selection(template="fastapiadmin").capabilities()…`。 调用`admin_scope_correction`、`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structured_scope_choice_uses_selected_option_not_question_or_other_options`（L99–L122）：接收`option`、`blocked`。 控制顺序：L112断言`bool(scope_conflicts([ORIGINAL, answer], capabilities)) is blocked`；L113按`blocked`分支；L121断言`recovered.summary == ORIGINAL`；L122断言`recovered.unsupported`。 调用`Selection(template="fastapiadmin").capabilities`、`Selection`、`scope_conflicts`、`blocked_requirement`、`render_answer`、`requirement.gate_dump`、`bool`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_declared_auth_mode_does_not_erase_explicit_anonymous_requirement`（L125–L130）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L130断言`scope_conflicts([original, AUTHENTICATED_SCOPE], capabilities)`。 调用`Selection(template="fastapiadmin").capabilities`、`Selection`、`scope_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_canonical_lists_only_merge_complete_equivalent_phrases_and_record_spellings`（L133–L157）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L151断言`result.users == ["团队队长（仅作为联系人）", "管理员", "团队队长（自行提交报名）"]`；L152断言`result.features == ["支持报名记录的增删改查", "队名最长100字符", "队名最长200字符"]`；L153断言`result.acceptance == ["对报名记录进行新增、查询、修改、删除", "仅能删除本人报名记录"]`；L154断言`any(item["duplicate"] == "团队队长（仅联系人）" for item in audit)`；L155断言`previous.model_dump() == original`；L156遍历`range(5)`；L157断言`reconcile(result.gate_dump(), candidate, []).gate_dump() == result.gate_dump()`。 调用`requirement().model_copy`、`requirement`、`previous.model_copy`、`previous.model_dump`、`reconcile`、`previous.gate_dump`、`any`、`range`、`reconcile(result.gate_dump(), candidate, []).gate_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_admin_scope_correction_removes_only_atomic_legacy_goal`（L160–L174）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L171断言`"提供" + ORIGINAL not in corrected.features`；L172断言`"报名网站及比赛结果公示" in corrected.features`；L174断言`"提供" + ORIGINAL in retained.features`。 调用`requirement().model_copy`、`requirement`、`before.model_dump`、`reconcile`、`before.gate_dump`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_internal_modes_do_not_need_external_portal_choice`（L185–L186）：接收`goal`。 控制顺序：L186断言`scope_conflicts([goal], Selection(template="fastapiadmin").capabilities()) == []`。 调用`scope_conflicts`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_negative_or_admin_only_submission_is_not_positive_entrant_intent`（L197–L203）：接收`feature`。 控制顺序：L203断言`analysis_intent_conflicts(candidate, [ORIGINAL, AUTHENTICATED_SCOPE])`。 调用`requirement().model_copy`、`requirement`、`analysis_intent_conflicts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `registration_plan`（L206–L246）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`。 返回路径：L209的`Plan.model_validate( { "title": ORIGINAL, "data_scope": "shared", "acceptance": [AUTHENTIC…`。
- `test_native_entrant_plan_needs_actual_registration_and_own_creation`（L252–L269）：接收`broken`。 控制顺序：L257断言`registration_plan_gaps(plan, [ORIGINAL, AUTHENTICATED_SCOPE], capabilities) == []`；L258按`broken == "no_business"`分支；L260按`broken == "read_only"`分支；L262按`broken == "all_rows"`分支；L264按`broken == "registration_disabled"`分支；L269断言`registration_plan_gaps(plan, [ORIGINAL, AUTHENTICATED_SCOPE], capabilities)`。 调用`registration_plan`、`Selection(template="fastapiadmin").capabilities`、`Selection`、`registration_plan_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_literal_prose_must_not_be_normalized_into_false_equivalence`（L272–L292）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L286断言`merged.features == [ "文件名必须是 file.", "选项标签为 Ａ", "文件名必须是 file", "选项标签为 A", ]`；L292断言`merged.users == ["Ａ组（仅联系人）", "A组（仅联系人）"]`。 调用`requirement().model_copy`、`requirement`、`reconcile`、`before.gate_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_old_positive_phrase_cannot_hide_new_contact_only_contradiction`（L295–L305）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L305断言`analysis_intent_conflicts(candidate, [ORIGINAL, AUTHENTICATED_SCOPE])`。 调用`requirement().model_copy`、`requirement`、`analysis_intent_conflicts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_registration_intent.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L305。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12441`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_registration_intent.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8358c8cbe876c1dfa0750ca1dc241244a5f183d7165403c85f2fc67d7861b7ca"} -->
````python
# tests/test_registration_intent.py
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
````
