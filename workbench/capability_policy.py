"""Controller-owned scope policy, never supplied by a candidate or model plan.

Generic extensions use frozen, reviewed executable contracts. Registered compound
requests additionally retain authored semantic obligations; a bounded oracle
cannot grant completion of the original website.
"""

import re
import unicodedata

from scripts.extension_oracles import contest
from workbench.capability_verification import CheckFailure
from workbench.domain import digest

# Exact authored source excerpts, independent of planner wording and source IDs.
CONTEST_BINDINGS = {
    "支持队长创建队伍并生成邀请码，队员通过邀请码加入队伍（限制每支队伍的最大人数及跨校组队规则）。": (
        "team.capacity_atomic",
        "team.invitation_code_join",
    ),
    "匿名/盲审支持：自动隐藏学生姓名、学校等敏感信息，确保评审客观公正。": (
        "review.identity_blind",
    ),
    "多角色协同与权限控制：精准划分参赛学生、指导老师、评审专家和系统管理员的权限，确保数据安全与操作合规。": (
        "access.outsider_denied",
    ),
}


def canonical(value):
    return "".join(
        char for char in unicodedata.normalize("NFKC", value).casefold() if char.isalnum()
    )


def _contest_binding(messages):
    # Only a coherent human source can bind a domain oracle. Unrelated historical
    # keywords and standalone invitation systems must not acquire contest semantics.
    words = (
        "竞赛|赛事|contest|competition",
        "邀请码|邀请加入|邀请队员|invitecode|invitationcode",
        "盲审|匿名评审|匿名审稿|blindreview|anonymousreview",
    )
    bound_messages = set()
    ambiguous = False
    # ponytail: bounded negation grammar; unclear domain changes require independent review.
    for index, message in enumerate(messages):
        clauses = [canonical(part) for part in re.split(r"[。；;，,\n]", message)]
        negative = [
            any(
                re.search(
                    r"(?:不要|不需要|不做|不再|取消|去掉|移除|删除|without|no|not).{0,12}(?:"
                    + word
                    + ")|(?:"
                    + word
                    + r")(?:功能|模块|需求|网站|系统)?(?:取消|不做|不要|不需要)",
                    part,
                )
                for part in clauses
            )
            for word in words
        ]
        # Cancelling a deadline/field/display rule does not cancel the business.
        negative[0] = any(
            re.fullmatch(
                r"(?:请|现在)?(?:不要|不需要|不做|不再做?|取消|去掉|移除|删除|without|no|not)"
                r"(?:整个|全部)?(?:竞赛|赛事|contest|competition)(?:业务|模块|需求|网站|系统|功能)?(?:了|吧)?"
                r"|(?:竞赛|赛事|contest|competition)(?:业务|模块|需求|网站|系统|功能)?"
                r"(?:取消|不做|不要|不需要)(?:了|吧)?",
                part,
            )
            for part in clauses
        )
        text = canonical(message)
        positive = [
            bool(re.search(word, text)) and not neg
            for word, neg in zip(words, negative, strict=True)
        ]
        if negative[0]:
            bound_messages.clear()
            ambiguous = False
            continue
        if any(negative[1:]) and bound_messages:
            bound_messages.clear()
            ambiguous = True  # Changed compound scope needs its own reviewed contract.
        authored = sum(canonical(quote) in text for quote in CONTEST_BINDINGS)
        if (authored >= 2 and not any(negative)) or all(positive):
            bound_messages.add(index)
            ambiguous = False
        elif positive[0]:
            ambiguous = True
    registered = bool(bound_messages)
    ambiguous = ambiguous and not registered
    return bound_messages, ambiguous


def scope_policy(scope, selection):
    bound_messages, ambiguous = _contest_binding(scope["messages"])
    registered = bool(bound_messages)
    goals = []
    for row in scope["sources"]:
        semantics = ["original.full_source"]
        normalized = canonical(row["text"])
        for quote, predicates in CONTEST_BINDINGS.items():
            if row.get("message_index") in bound_messages and canonical(quote) in normalized:
                semantics.extend(predicates)
        for semantic in semantics:
            goals.append({"source_id": row["id"], "source_text": row["text"], "semantic": semantic})
    return {
        "version": 4,
        "source_digest": scope["source_digest"],
        "source_units_digest": digest(scope["sources"]),
        "selection": selection,
        "trusted_oracle": contest.CONTRACT_VERSION if registered else None,
        "oracle_source_ids": [
            row["id"] for row in scope["sources"] if row.get("message_index") in bound_messages
        ],
        "requires_explicit_review": ambiguous,
        "coverage_level": "bounded-business-slice"
        if registered
        else "unreviewed-business-scope"
        if ambiguous
        else "reviewed-executable-contract",
        "goals": goals,
    }


def contract_errors(plan):
    """A source reference/health endpoint alone is never business acceptance.

    This structural minimum cannot prove arbitrary natural-language semantics;
    the frozen design review remains responsible for the contract's relevance.
    """
    errors = []
    ignored = {plan.runtime.health_path, "/health", "/ready", "/openapi.json"}
    envelope = {"ok", "success", "status", "status_code", "code", "msg", "message"}

    def positive(step):
        return (
            200 <= step.status < 300
            and step.path.split("?", 1)[0] not in ignored
            and any(
                key.rsplit(".", 1)[-1] not in envelope and value is not None
                for key, value in step.equals.items()
            )
        )

    persisted = set()
    owners = {
        id(step): (scenario.id, position)
        for scenario in plan.scenarios
        for position, step in enumerate(scenario.steps)
    }
    for task in plan.tasks:
        scenarios = [s for s in plan.scenarios if s.id in task.scenarios]
        for source in task.requirements:
            steps = [
                step
                for s in scenarios
                if source in s.requirements
                for step in s.steps
                if step.path.split("?", 1)[0] not in ignored
            ]
            writes = [
                step
                for step in steps
                if step.method != "GET" and positive(step) and step.body is not None
            ]
            reads = [step for step in steps if step.method == "GET" and positive(step)]
            linked = []
            for write in writes:
                for read in reads:
                    if (
                        owners[id(write)][0] == owners[id(read)][0]
                        and owners[id(write)][1] < owners[id(read)][1]
                        and any("${" + name + "}" in read.path for name in write.captures)
                    ):
                        linked.extend(
                            (owners[id(read)][0], read.path, key, digest(value))
                            for key, value in read.equals.items()
                            if value is not None
                            and key.rsplit(".", 1)[-1] not in envelope
                            and value in write.equals.values()
                        )
            if not linked:
                errors.append(
                    f"来源 {source} 缺少独立业务写入与绑定读回值断言，健康检查或ID引用不能证明实现"
                )
            persisted.update(linked)
            paths = {step.path.split("?", 1)[0] for step in [*writes, *reads]}
            if not any(
                step.status in {401, 403} and step.path.split("?", 1)[0] in paths for step in steps
            ):
                errors.append(f"来源 {source} 缺少相同业务资源的权限边界断言")
            if not any(
                step.status in {400, 409, 422} and step.path.split("?", 1)[0] in paths
                for step in steps
            ):
                errors.append(f"来源 {source} 缺少相同业务资源的业务负例断言")
    if not any(
        positive(step)
        and step.method == "GET"
        and any(
            (scenario.id, step.path, key, digest(value)) in persisted
            for key, value in step.equals.items()
        )
        for scenario in plan.scenarios
        for step in scenario.after_restart
    ):
        errors.append("缺少重启后的同一业务值断言")
    return list(dict.fromkeys(errors))


def business_coverage(policy, proof):
    if policy["requires_explicit_review"]:
        raise CheckFailure("原始业务范围匹配不明确，需要独立验收策略审阅，不能降级通用验收")
    if policy["trusted_oracle"] is None:
        rows = [
            {
                "goal_id": "goal-" + digest({"protocol": "original-source-v1", **goal})[:24],
                "source_id": goal["source_id"],
                "source_sha256": digest(goal["source_text"]),
                "semantic": goal["semantic"],
                "status": "remaining",
            }
            for goal in policy["goals"]
        ]
        return {
            "obligations": rows,
            "complete_source_ids": [],
            "remaining_source_ids": sorted({row["source_id"] for row in rows}),
            "remaining_obligations": [row["goal_id"] for row in rows],
            "coverage_level": policy["coverage_level"],
            "full_request_complete": False,
            "source_units_digest": policy["source_units_digest"],
            "natural_language_semantics_proven": False,
        }
    business = proof.get("business_oracle", {})
    if not isinstance(business, dict) or not isinstance(business.get("witnesses"), dict):
        raise CheckFailure("独立业务oracle报告结构无效")
    if (
        business.get("protocol") != policy["trusted_oracle"]
        or set(business.get("witnesses", {})) != set(contest.SEMANTICS)
        or any(value is not True for value in business.get("witnesses", {}).values())
        or business.get("full_request_complete") is not False
        or business.get("remaining_obligations") != list(contest.REMAINING)
        or any(
            business.get(key) is not True
            for key in ("fresh_replay", "same_cluster", "distinct_database_oid")
        )
    ):
        raise CheckFailure("缺少当前原始范围绑定的独立业务oracle证据")
    result = contest.coverage(
        [contest.Goal(**goal) for goal in policy["goals"]], business["witnesses"]
    )
    return {
        **result,
        "coverage_level": policy["coverage_level"],
        "source_units_digest": policy["source_units_digest"],
    }
