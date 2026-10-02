# workbench/requirement_intent.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：保留原始报名目标并明确参与者入口。** 区分入口未定、登录后业务UI和显式匿名或独立公众门户；只接受用户明确取消自行报名后的管理员范围更正。原始消息是依据，模型重述或智能推荐不能授权缩减；阻塞恢复保留旧需求并提出明确选项；analysis_intent_conflicts拒绝丢失参与者，registration_plan_gaps核对真实报名实体、默认角色和create/read的own权限。

**对应关系：** 用户消息 → scope_conflicts → Workflow.capability_recovery → 当前能力澄清gate及Vue范围提示；已知选择不再消耗模型调用。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_canonical`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_answer_text`（L20–L23）：接收`text`。 调用`text.replace`。 返回路径：L23的`text.replace(SCOPE_QUESTION, "")`。
- `_positive_text`（L35–L45）：接收`text`。 调用`re.sub`。 返回路径：L39的`re.sub( r"(?:取消\|放弃\|不需要\|不要\|不允许\|禁止\|无需\|不做\|不再提供)" r"(?:匿名\|未登录\|无需登录\|独立公开\|独立公众\|独立对外…`。
- `_explicit_mode`（L48–L67）：接收`text`。 控制顺序：L50按`re.search( rf"(?:匿名\|{NO_LOGIN})[^。；;\n]{{0,24}}(?:报名\|提交)\|" r"(?:独立\|自定义)[^。；;\n]{0…`分支；L63按`auth and not re.search( r"(?:不得\|不能\|不允许\|禁止)[^，,。；;\n]{0,20}(?:提交\|报名)", auth.group(…`分支。 调用`_positive_text`、`re.search`、`auth.group`。 返回路径：L56的`"public_portal"`；L66的`"authenticated_business_ui"`；L67的`None`。
- `admin_scope_correction`（L70–L90）：接收`text`。 源码说明：Require explicit cancellation AND an unambiguous admin-only replacement.。 控制顺序：L73按`re.search(r"(?:不要\|不能\|不想\|不应\|并非\|不是\|不)\s*(?:取消\|放弃\|删除\|移除)", text)`分支；L81按`not cancellation or "报名" not in cancellation.group() or not admin`分支。 调用`_answer_text`、`re.search`、`cancellation.group`、`cancellation.end`、`_explicit_mode`。 返回路径：L74的`False`；L82的`False`；L86的`not _explicit_mode(remaining) and not re.search( rf"(?:{ACTORS})[^。；;\n]{{0,30}}(?:自行\|直接\…`。
- `registration_goal`（L93–L115）：接收`text`。 源码说明：Only an entrant product request, never ordinary account registration.。 控制顺序：L96按`admin_scope_correction(text)`分支；L98遍历`re.split(r"[。；;\n]", text)`；L99按`re.search(r"(?:不要\|不需要\|不做\|不提供\|取消)[^。；;]{0,24}报名", clause)`分支；L101按`re.search(r"(?:报名\|参赛注册)(?:网站\|站点\|门户\|页面\|入口)", clause)`分支；L102按`not re.search(r"(?:仅\|只)(?:做\|需\|要\|提供)?[^，,]{0,12}(?:管理端\|后台)", clause)`分支；L104按`re.search( rf"(?:{ACTORS})[^。；;]{{0,24}}(?:自行\|直接\|在线\|公开)[^。；;]{{0,12}}报名", clause )`分支；L108按`re.search( r"\b(?:event\|contest\|competition\|participant)\b.{0,40}" r"\b(?:registra…`分支。 调用`_answer_text`、`admin_scope_correction`、`re.split`、`re.search`。 返回路径：L97的`False`；L103的`True`；L107的`True`。
- `registration_scope`（L118–L150）：接收`human`。 源码说明：Keep unspecified, conflicting, authenticated and public scope separate.。 控制顺序：L121遍历`enumerate(human)`；L124按`admin_scope_correction(text)`分支；L128按`admin and mode`分支；L130按`index == 0 and admin`分支；L132按`active and active["mode"] == "public_portal" and mode == "authenticated_business_ui"`分支；L138按`not withdrawal or re.search(r"(?:不要\|不能\|不想\|不应\|不)\s*取消", text)`分支；L140按`mode is not None or (active is None and registration_goal(text))`分支。 调用`enumerate`、`_answer_text`、`_explicit_mode`、`admin_scope_correction`、`re.search`、`registration_goal`、`digest`。 返回路径：L150的`active`。
- `scope_conflicts`（L153–L196）：接收`human`、`capabilities`。 源码说明：Recommendations cannot decide away a consequential product entrypoint.。 控制顺序：L156按`active is None`分支；L159按`active["mode"] == "authenticated_business_ui" and modes.get("authenticated_business_u…`分支；L163按`public and modes.get("anonymous_submission") and modes.get("custom_public_portal")`分支。 调用`registration_scope`、`capabilities.get`、`modes.get`。 返回路径：L157的`[]`；L160的`[]`；L164的`[]`。
- `cancellable_registration_goal`（L199–L206）：接收`key`、`quote`。 源码说明：A narrow source-backed legacy goal removal, not a fuzzy feature deletion.。 调用`admin_scope_correction`、`bool`、`re.fullmatch`。 返回路径：L201的`admin_scope_correction(quote) and bool( re.fullmatch( r"(?:提供\|建设\|开发\|搭建\|实现)?[^\s，,；;。！？…`。
- `blocked_requirement`（L209–L249）：接收`previous`、`conflicts`、`capabilities`、`canonicalization`、`original_request`。 源码说明：Keep prior details auditable, restore goal, and expose the required choice.。 调用`Requirement.model_validate(previous).model_dump`、`Requirement.model_validate`、`Requirement( summary=source[:4000], users=[], data_scope=capabili…`、`Requirement`、`list`、`dict.fromkeys`、`canonicalize_requirement`。 返回路径：L249的`Requirement.model_validate(data)`。
- `reconcile_entrypoint`（L252–L301）：接收`previous`、`proposed`、`human`、`corrections`、`audit`。 源码说明：A fresh entrant choice supersedes legacy contact-only model assumptions. Only atomic actor/record-creation restrictions are replaced. Business fields, unrelated features, and compound prose are retain。 控制顺序：L260按`not active or active["mode"] != "authenticated_business_ui"`分支；L264按`revised is not None and raw in corrections`分支；L265遍历`("users", "features", "acceptance")`；L267遍历`revised[section]`；L284按`participant_contact or admin_creation`分支。 调用`registration_scope`、`Requirement.model_validate(previous).model_dump`、`Requirement.model_validate`、`bool`、`re.fullmatch`、`audit.append`、`kept.append`、`proposed.model_copy`。 返回路径：L261的`previous, proposed`；L301的`revised, proposed.model_copy(update={"summary": original[:4000]})`。
- `analysis_intent_conflicts`（L304–L382）：接收`candidate`、`human`、`cursor`。 控制顺序：L306按`not active or active["mode"] != "authenticated_business_ui"`分支；L346按`has_actor and has_submission and not contradictory_actor`分支。 调用`registration_scope`、`any`、`re.search`、`positive_submission`、`candidate.model_dump_json`。 返回路径：L307的`[]`；L347的`[]`；L349的`[ { "code": "registration_intent_conflict", "target": {"entity": None, "field": "registrat…`。
- `analysis_intent_conflicts.positive_submission`（L314–L329）：接收`text`。 控制顺序：L315遍历`re.split(r"[，,。；;\n]", text)`；L316按`not re.search( rf"(?:{participant}\|登录后\|自行)[^。；;]{{0,40}}(?:提交\|创建\|录入\|自行\|直接)(?:活动…`分支；L321按`re.search(r"管理员\|管理人员", clause) and not re.search(participant, clause)`分支；L323按`re.search( r"(?:不能\|不得\|禁止\|不允许\|不支持\|不可\|不\|无需)[^，,。；;]{0,15}(?:自行\|直接\|提交\|创建\|录入)"…`分支。 调用`re.split`、`re.search`。 返回路径：L328的`True`；L329的`False`。
- `registration_plan_gaps`（L385–L423）：接收`plan`、`human`、`capabilities`。 源码说明：Verify an executable entrant path, not merely registration-themed CRUD.。 控制顺序：L388按`not active or active["mode"] != "authenticated_business_ui"`分支；L399按`not targets`分支；L401按`capabilities["template"] == "python-basic" and plan.data_scope == "per_user" and plan…`分支；L408按`business is None`分支；L411按`"注册" in active["source"]["quote"] and not business.registration.enabled`分支；L414遍历`sorted(targets)`；L419按`grant is None or not {"create", "read"} <= set(grant.actions) or grant.scope != "own"`分支。 调用`registration_scope`、`re.search`、`reasons.append`、`sorted`、`next`、`set`。 返回路径：L389的`[]`；L400的`["参赛者自行报名缺少明确的报名记录实体，不能以无关管理实体替代"]`；L406的`[]`。

</details>

**创建路径：** `workbench/requirement_intent.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L423。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19037`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_intent.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d37f7becd451ff2d9e9ea512aa3d4aa33fef3859e64989c6f25f4f99fb647c39"} -->
````python
# workbench/requirement_intent.py
"""Source-backed capability boundaries, independent of model scope rewording.

This intentionally recognizes a narrow product request, not every occurrence of
"registration". Account sign-up and administrative registration records are not
public entrant registration. Unknown prose remains for normal analysis.
"""

import re

from workbench.domain import Requirement, digest
from workbench.requirement_canonical import canonicalize_requirement

PUBLIC_REGISTRATION = "entrant-registration-entrypoint"
SCOPE_QUESTION = "参与者将通过哪种入口报名？"
ADMIN_SCOPE = "取消参赛者自行提交报名，改为仅管理员录入和维护报名记录"
PUBLIC_SCOPE = "需要独立公众报名页面或匿名报名提交，暂停生成并先扩展、验证此能力"
AUTHENTICATED_SCOPE = "参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录"


def _answer_text(text):
    # Structured answer history includes the question prompt, which is not a
    # user choice. Our neutral prompt carries no alternative's commitment.
    return text.replace(SCOPE_QUESTION, "")


ACTORS = r"参赛者|参赛学生|选手|队长|学生|团队|员工|成员|职工|用户|报名人"
ADMIN_ONLY = (
    r"(?:仅|只)(?:需|要|提供|做|允许|支持|保留|由)?(?:内部)?"
    r"(?:赛事管理人员|管理人员|管理员)(?:进行|来|负责|自行|手动)?"
    r"(?:录入|登记|维护|管理)"
)
NO_LOGIN = r"(?:无需|不用|不需要|不必)(?:注册(?:并)?)?登录|未登录"


def _positive_text(text):
    # Double negation is retention, never a cancellation quote. In particular,
    # 不需要登录/无需登录 is a positive no-login requirement, not a scope deletion.
    text = re.sub(r"(?:不要|不能|不想|不应)\s*取消", "保留", text)
    return re.sub(
        r"(?:取消|放弃|不需要|不要|不允许|禁止|无需|不做|不再提供)"
        r"(?:匿名|未登录|无需登录|独立公开|独立公众|独立对外|自定义公开|公开|公众|对外|参赛者自行)"
        r"[^，,。；;\n]{0,30}(?:报名|门户|页面|提交)",
        "",
        text,
    )


def _explicit_mode(text):
    positive = _positive_text(text)
    if re.search(
        rf"(?:匿名|{NO_LOGIN})[^。；;\n]{{0,24}}(?:报名|提交)|"
        r"(?:独立|自定义)[^。；;\n]{0,16}(?:公众|公开|对外)[^。；;\n]{0,12}(?:网站|页面|门户)|"
        r"(?:公众|公开|对外)[^。；;\n]{0,12}(?:独立|自定义)[^。；;\n]{0,12}(?:网站|页面|门户)",
        positive,
    ):
        return "public_portal"
    auth = re.search(
        rf"(?:{ACTORS})[^。；;\n]{{0,24}}登录[^。；;\n]{{0,40}}"
        r"(?:自行|直接|在线)?(?:提交)?(?:活动|赛事|比赛|竞赛|培训)?报名|"
        r"登录后[^。；;\n]{0,40}(?:自行|直接)(?:提交)?(?:活动|赛事|比赛|竞赛|培训)?报名",
        positive,
    )
    if auth and not re.search(
        r"(?:不得|不能|不允许|禁止)[^，,。；;\n]{0,20}(?:提交|报名)", auth.group()
    ):
        return "authenticated_business_ui"
    return None


def admin_scope_correction(text):
    """Require explicit cancellation AND an unambiguous admin-only replacement."""
    text = _answer_text(text)
    if re.search(r"(?:不要|不能|不想|不应|并非|不是|不)\s*(?:取消|放弃|删除|移除)", text):
        return False
    cancellation = re.search(
        r"(?:取消|放弃|删除|移除|不再需要|不需要|不要|不做|不再提供|无需)\s*"
        r"(?:参赛者|参赛学生|学生|选手|队长|团队|公众|公开|匿名|在线|自行|直接|的|提交|报名|入口|页面|网站){1,12}",
        text,
    )
    admin = re.search(ADMIN_ONLY, text)
    if not cancellation or "报名" not in cancellation.group() or not admin:
        return False
    # Additional free text and selected options are one user message. A selected
    # admin-only option cannot swallow a contradictory custom entrant request.
    remaining = text[cancellation.end() :]
    return not _explicit_mode(remaining) and not re.search(
        rf"(?:{ACTORS})[^。；;\n]{{0,30}}(?:自行|直接|在线|提交)(?:活动)?报名|"
        r"(?:仍|还|同时|但是|但|也)[^。；;\n]{0,32}(?:报名网站|公开报名|提交报名|在线报名)",
        remaining,
    )


def registration_goal(text):
    """Only an entrant product request, never ordinary account registration."""
    text = _answer_text(text)
    if admin_scope_correction(text):
        return False
    for clause in re.split(r"[。；;\n]", text):
        if re.search(r"(?:不要|不需要|不做|不提供|取消)[^。；;]{0,24}报名", clause):
            continue
        if re.search(r"(?:报名|参赛注册)(?:网站|站点|门户|页面|入口)", clause):
            if not re.search(r"(?:仅|只)(?:做|需|要|提供)?[^，,]{0,12}(?:管理端|后台)", clause):
                return True
        if re.search(
            rf"(?:{ACTORS})[^。；;]{{0,24}}(?:自行|直接|在线|公开)[^。；;]{{0,12}}报名", clause
        ):
            return True
        if re.search(
            r"\b(?:event|contest|competition|participant)\b.{0,40}"
            r"\b(?:registration|sign[- ]?up)\b.{0,20}\b(?:site|website|portal|page)\b",
            clause,
            re.I,
        ):
            return True
    return False


def registration_scope(human):
    """Keep unspecified, conflicting, authenticated and public scope separate."""
    active = None
    for index, raw in enumerate(human):
        text = _answer_text(raw)
        mode = _explicit_mode(text) if active or "报名" in text else None
        if admin_scope_correction(text):
            active = None
            continue
        admin = re.search(ADMIN_ONLY, text)
        if admin and mode:
            mode = "conflicting"
        elif index == 0 and admin:
            continue
        if active and active["mode"] == "public_portal" and mode == "authenticated_business_ui":
            withdrawal = re.search(
                r"(?:取消|不需要|不要|不做|不再提供)(?:匿名|无需登录|独立公开|独立公众|公开|公众)"
                r"[^，,。；;\n]{0,24}(?:报名|提交|门户|页面)",
                text,
            )
            if not withdrawal or re.search(r"(?:不要|不能|不想|不应|不)\s*取消", text):
                continue
        if mode is not None or (active is None and registration_goal(text)):
            active = {
                "mode": mode or "unspecified",
                "source": {
                    "section": "user_messages",
                    "index": index,
                    "quote": raw,
                    "sha256": digest(raw),
                },
            }
    return active


def scope_conflicts(human, capabilities):
    """Recommendations cannot decide away a consequential product entrypoint."""
    active = registration_scope(human)
    if active is None:
        return []
    modes = capabilities.get("registration_modes", {})
    if active["mode"] == "authenticated_business_ui" and modes.get("authenticated_business_ui"):
        return []
    public = active["mode"] == "public_portal"
    contradictory = active["mode"] == "conflicting"
    if public and modes.get("anonymous_submission") and modes.get("custom_public_portal"):
        return []
    source = active["source"]
    message = (
        f"用户目标“{source['quote'][:200]}”明确要求独立公众报名入口或匿名提交；"
        f"当前模板 {capabilities['template']} 未提供该入口，不能以管理员代录替代"
        if public
        else (
            "同一回答同时选择仅管理员代录和参与者自行报名，范围互相冲突；请明确保留的操作入口"
            if contradictory
            else f"用户目标“{source['quote'][:200]}”是参赛报名网站，尚未明确报名入口；"
            "需要区分登录后的参赛者自行提交、独立公众页面与管理员代录，"
            "不能推定用户要求匿名访问，也不能默认缩减为管理员代录"
        )
    )
    return [
        {
            "code": "unsupported_registration_portal"
            if public
            else "registration_scope_conflict"
            if contradictory
            else "registration_entrypoint_unresolved",
            "capability": PUBLIC_REGISTRATION,
            "source": source,
            "template": capabilities["template"],
            "unsupported": public,
            "message": message,
            "alternatives": [
                AUTHENTICATED_SCOPE + "；沿用当前技术栈，设计须声明非管理员角色及本人记录权限",
                PUBLIC_SCOPE + "；当前没有已验证的独立公众报名模板可自动切换",
                "明确改变范围：“" + ADMIN_SCOPE + "”；继续使用当前已选技术栈",
            ],
        }
    ]


def cancellable_registration_goal(key, quote):
    """A narrow source-backed legacy goal removal, not a fuzzy feature deletion."""
    return admin_scope_correction(quote) and bool(
        re.fullmatch(
            r"(?:提供|建设|开发|搭建|实现)?[^\s，,；;。！？!?与及和]{1,100}报名(?:网站|页面|入口)",
            key,
        )
    )


def blocked_requirement(
    previous, conflicts, capabilities, canonicalization, *, original_request=""
):
    """Keep prior details auditable, restore goal, and expose the required choice."""
    source = original_request or conflicts[0]["source"]["quote"]
    data = (
        Requirement.model_validate(previous).model_dump()
        if previous
        else Requirement(
            summary=source[:4000],
            users=[],
            data_scope=capabilities["scope"],
            features=[source[:8000]],
            acceptance=[],
        ).model_dump()
    )
    # A model-only administrative reinterpretation must not become the headline.
    # Existing details remain visible and are not mistaken for scope approval.
    data["summary"] = source[:4000]
    data["unsupported"] = [item["message"] for item in conflicts if item["unsupported"]]
    data["questions"] = [SCOPE_QUESTION]
    data["question_items"] = [
        {
            "id": "registration_scope",
            "prompt": SCOPE_QUESTION,
            "kind": "single",
            "options": [
                {"id": "authenticated_entry", "label": AUTHENTICATED_SCOPE},
                {"id": "public_portal", "label": PUBLIC_SCOPE},
                {"id": "admin_only", "label": ADMIN_SCOPE},
            ],
            "required": True,
            "allow_other": True,
        }
    ]
    data["recommendations"] = conflicts[0]["alternatives"]
    warning = "管理端代录仅为待确认的范围变更；智能推荐不代表用户已取消参赛者报名目标"
    data["assumptions"] = list(dict.fromkeys([warning, *data["assumptions"]]))
    data["changes"] = []
    canonicalize_requirement(data, canonicalization)
    return Requirement.model_validate(data)


def reconcile_entrypoint(previous, proposed, human, corrections, audit):
    """A fresh entrant choice supersedes legacy contact-only model assumptions.

    Only atomic actor/record-creation restrictions are replaced. Business fields,
    unrelated features, and compound prose are retained for explicit analysis.
    The original checkpoint and every removed spelling stay in the ledger.
    """
    active = registration_scope(human)
    if not active or active["mode"] != "authenticated_business_ui":
        return previous, proposed
    raw = active["source"]["quote"]
    revised = Requirement.model_validate(previous).model_dump() if previous else None
    if revised is not None and raw in corrections:
        for section in ("users", "features", "acceptance"):
            kept = []
            for text in revised[section]:
                participant_contact = section == "users" and bool(
                    re.fullmatch(
                        r"(?:参赛者|参赛学生|学生|选手|队长|团队队长|员工|成员|职工|用户|报名人)"
                        r"[（(]?(?:仅作为|仅为|仅|只作为)?(?:报名)?联系人"
                        r"(?:[，,]?(?:不直接操作系统|不登录系统|不自行提交报名))?[）)]?",
                        text,
                    )
                )
                admin_creation = bool(
                    re.fullmatch(
                        r"(?:报名(?:信息|记录)?(?:默认)?(?:仅|只)(?:能|可|允许)?由"
                        r"(?:赛事管理人员|管理员)(?:录入|创建|提交)|"
                        r"(?:仅|只)(?:允许)?(?:赛事管理人员|管理员)(?:录入|创建|提交)报名(?:信息|记录)?)",
                        text,
                    )
                )
                if participant_contact or admin_creation:
                    audit.append(
                        {
                            "section": section,
                            "key": text,
                            "replacement": None,
                            "source_quote": raw,
                            "source": active["source"],
                            "reason": "explicit_authenticated_entrant_choice",
                        }
                    )
                else:
                    kept.append(text)
            revised[section] = kept
    # The headline retains the actual product goal after an explicit entrypoint
    # choice; actor/feature omissions still become deterministic diagnostics.
    original = human[0] if human else proposed.summary
    return revised, proposed.model_copy(update={"summary": original[:4000]})


def analysis_intent_conflicts(candidate, human, *, cursor=0):
    active = registration_scope(human)
    if not active or active["mode"] != "authenticated_business_ui":
        return []
    participant = r"参赛者|参赛学生|学生|选手|队长|团队|员工|成员|职工|用户|报名人"
    has_actor = any(
        re.search(participant, text) and not re.search(r"仅.*联系人|不.*(?:操作|提交)", text)
        for text in candidate.users
    )

    def positive_submission(text):
        for clause in re.split(r"[，,。；;\n]", text):
            if not re.search(
                rf"(?:{participant}|登录后|自行)[^。；;]{{0,40}}(?:提交|创建|录入|自行|直接)(?:活动|赛事|比赛|竞赛|培训)?报名",
                clause,
            ):
                continue
            if re.search(r"管理员|管理人员", clause) and not re.search(participant, clause):
                continue
            if re.search(
                r"(?:不能|不得|禁止|不允许|不支持|不可|不|无需)[^，,。；;]{0,15}(?:自行|直接|提交|创建|录入)",
                clause,
            ):
                continue
            return True
        return False

    has_submission = any(
        positive_submission(text) for text in [*candidate.features, *candidate.acceptance]
    )
    contradictory_actor = any(
        re.search(participant, text)
        and (
            re.search(r"仅(?:作为|为)?(?:报名)?联系人", text)
            or re.search(
                rf"(?:{participant})[^，,。；;]{{0,24}}(?:不能|不得|禁止|不允许|不支持|不可)"
                r"(?:自行|直接)?(?:提交|创建|录入)(?:活动|赛事|比赛|竞赛|培训)?报名",
                text,
            )
        )
        for text in [*candidate.users, *candidate.features, *candidate.acceptance]
    )
    if has_actor and has_submission and not contradictory_actor:
        return []
    source = active["source"]
    return [
        {
            "code": "registration_intent_conflict",
            "target": {"entity": None, "field": "registration_entrypoint"},
            "attribute": "authenticated_entrant_submission",
            "message": "需求分析遗漏已明确的参赛者登录后自行报名；不能改成管理员代录或仅联系人",
            "sources": [
                {
                    "source": {"section": "user_messages", "index": source["index"]},
                    "expected": "authenticated_entrant_submission",
                    "origin": "user_input",
                    "text": source["quote"],
                    "user_sources": [
                        {
                            "user_message_index": source["index"],
                            "sha256": source["sha256"],
                            "fresh": source["index"] >= cursor,
                        }
                    ],
                },
                {
                    "source": {"section": "analysis", "index": 0},
                    "expected": {
                        "participant_role": has_actor,
                        "entrant_submission": has_submission,
                        "contradictory_actor_restriction": contradictory_actor,
                    },
                    "origin": "model_analysis",
                    "text": candidate.model_dump_json(),
                    "user_sources": [],
                },
            ],
        }
    ]


def registration_plan_gaps(plan, human, capabilities):
    """Verify an executable entrant path, not merely registration-themed CRUD."""
    active = registration_scope(human)
    if not active or active["mode"] != "authenticated_business_ui":
        return []
    targets = {
        entity.name
        for entity in plan.entities
        if re.search(
            r"报名|\b(?:registration|enrollment|entry|application)\b",
            entity.name + " " + entity.description,
            re.I,
        )
    }
    if not targets:
        return ["参赛者自行报名缺少明确的报名记录实体，不能以无关管理实体替代"]
    if (
        capabilities["template"] == "python-basic"
        and plan.data_scope == "per_user"
        and plan.business is None
    ):
        return []  # Built-in login/CRUD enforces owner_id on every record.
    business = plan.business
    if business is None:
        return ["参赛者自行报名需要可执行的 business 角色与本人记录权限，管理员 CRUD 不满足此要求"]
    reasons = []
    if "注册" in active["source"]["quote"] and not business.registration.enabled:
        reasons.append("参赛者明确需要注册账号，business.registration.enabled 必须为 true")
    role = business.registration.default_role
    for entity in sorted(targets):
        grant = next(
            (item for item in business.permissions if item.role == role and item.entity == entity),
            None,
        )
        if grant is None or not {"create", "read"} <= set(grant.actions) or grant.scope != "own":
            reasons.append(
                f"报名实体 {entity} 必须为默认参赛角色 {role} 声明 create/read 及 own 行权限，不能由管理员代录或授权查看他人报名"
            )
    return reasons
````
