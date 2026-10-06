# workbench/capability_policy.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.extension_oracles`、`workbench.capability_verification`、`workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `canonical`（L30–L33）：接收`value`。 调用`"".join`、`unicodedata.normalize("NFKC", value).casefold`、`unicodedata.normalize`、`char.isalnum`。 返回路径：L31的`"".join( char for char in unicodedata.normalize("NFKC", value).casefold() if char.isalnum(…`。
- `_contest_binding`（L36–L94）：接收`messages`。 控制顺序：L47遍历`enumerate(messages)`；L79按`negative[0]`分支；L83按`any(negative[1:]) and bound_messages`分支；L87按`(authored >= 2 and not any(negative)) or all(positive)`分支；L90按`positive[0]`分支。 调用`set`、`enumerate`、`canonical`、`re.split`、`any`、`re.search`、`re.fullmatch`、`bool`、`zip`等。 返回路径：L94的`bound_messages, ambiguous`。
- `scope_policy`（L97–L125）：接收`scope`、`selection`。 控制顺序：L101遍历`scope["sources"]`；L104遍历`CONTEST_BINDINGS.items()`；L105按`row.get("message_index") in bound_messages and canonical(quote) in normalized`分支；L107遍历`semantics`。 调用`_contest_binding`、`bool`、`canonical`、`CONTEST_BINDINGS.items`、`row.get`、`semantics.extend`、`goals.append`、`digest`。 返回路径：L109的`{ "version": 4, "source_digest": scope["source_digest"], "source_units_digest": digest(sco…`。
- `contract_errors`（L128–L211）：接收`plan`。 源码说明：A source reference/health endpoint alone is never business acceptance. This structural minimum cannot prove arbitrary natural-language semantics; the frozen design review remains responsible for the c。 控制顺序：L154遍历`plan.tasks`；L156遍历`task.requirements`；L171遍历`writes`；L172遍历`reads`；L173按`owners[id(write)][0] == owners[id(read)][0] and owners[id(write)][1] < owners[id(read…`分支；L185按`not linked`分支；L191按`not any( step.status in {401, 403} and step.path.split("?", 1)[0] in paths for step i…`分支；L195按`not any( step.status in {400, 409, 422} and step.path.split("?", 1)[0] in paths for s…`分支。后续分支沿下方源码相同行号继续阅读。 调用`set`、`id`、`enumerate`、`step.path.split`、`positive`、`any`、`linked.extend`、`digest`、`read.equals.items`等。 返回路径：L211的`list(dict.fromkeys(errors))`。
- `contract_errors.positive`（L138–L146）：接收`step`。 调用`step.path.split`、`any`、`key.rsplit`、`step.equals.items`。 返回路径：L139的`200 <= step.status < 300 and step.path.split("?", 1)[0] not in ignored and any( key.rsplit…`。
- `business_coverage`（L214–L260）：接收`policy`、`proof`。 控制顺序：L215按`policy["requires_explicit_review"]`分支；L216抛异常，停止当前正常路径；L217按`policy["trusted_oracle"] is None`分支；L239按`not isinstance(business, dict) or not isinstance(business.get("witnesses"), dict)`分支；L240抛异常，停止当前正常路径；L241按`business.get("protocol") != policy["trusted_oracle"] or set(business.get("witnesses",…`分支；L252抛异常，停止当前正常路径。 调用`CheckFailure`、`digest`、`sorted`、`proof.get`、`isinstance`、`business.get`、`set`、`any`、`business.get("witnesses", {}).values`等。 返回路径：L228的`{ "obligations": rows, "complete_source_ids": [], "remaining_source_ids": sorted({row["sou…`；L256的`{ **result, "coverage_level": policy["coverage_level"], "source_units_digest": policy["sou…`。

</details>

**创建路径：** `workbench/capability_policy.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L260。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10983`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_policy.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a63c124257d8302f890b749e7594770f4b53e84938ca1b7a1e5687959a166b61"} -->
````python
# workbench/capability_policy.py
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
````
