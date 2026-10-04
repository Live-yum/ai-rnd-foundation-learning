# scripts/extension_oracles/contest.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.extension_oracles.contest；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `OracleFailure`（L41–L42）：继承`AssertionError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `require`（L45–L47）：接收`condition`、`message`。 控制顺序：L46按`not condition`分支；L47抛异常，停止当前正常路径。 调用`OracleFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Goal`（L51–L61）：继承`object`。声明的数据项为`source_id`、`source_text`、`semantic`；类型约束/数据库列参数以完整定义为准。
- `Goal.id`（L59–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`"\0".join`、`sha256(value.encode()).hexdigest`、`sha256`、`value.encode`。 返回路径：L61的`"goal-" + sha256(value.encode()).hexdigest()[:24]`。
- `coverage`（L64–L91）：接收`goals`、`witnesses`。 源码说明：No candidate-provided list of IDs or generic health result grants coverage.。 控制顺序：L73遍历`goals`。 调用`require`、`len`、`all`、`witnesses.get`、`rows.append`、`sha256(goal.source_text.encode()).hexdigest`、`sha256`、`goal.source_text.encode`、`by_source.setdefault(goal.source_id, []).append`等。 返回路径：L86的`{ "obligations": rows, "complete_source_ids": [key for key, values in by_source.items() if…`。
- `State`（L106–L114）：继承`object`。声明的数据项为`team_id`、`captain_id`、`member_id`、`invitations`、`name`、`submission_title`、`database_identity`、`process_generation`；类型约束/数据库列参数以完整定义为准。
- `_response`（L117–L121）：接收`http`、`actor`、`method`、`path`、`payload`、`statuses`。 调用`http`、`require`、`isinstance`。 返回路径：L121的`status, body`。
- `_id`（L124–L127）：接收`body`。 调用`body.get`、`require`、`type`。 返回路径：L127的`value`。
- `_identity`（L130–L134）：接收`probe`。 调用`probe`、`require`、`len`、`type`。 返回路径：L134的`rows[0]["database"], rows[0]["database_oid"]`。
- `_physical`（L137–L165）：接收`probe`、`state`。 调用`probe`、`require`、`len`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_access`（L168–L190）：接收`http`、`state`。 控制顺序：L179遍历`("outsider", "reviewer")`；L188遍历`("captain", "member_a", "member_b", "outsider", "anonymous")`。 调用`_response`、`require`、`detail.get`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `initial`（L193–L280）：接收`http`、`database_probe`、`actor_ids`、`process_generation`。 源码说明：Drive fresh authenticated HTTP + independently authenticated read-only SQL probes. http(actor, method, path, payload) -> (status, normalized JSON body). Each concurrent call MUST use an independent HT。 控制顺序：L225遍历`(300, 1, 300)`。 调用`require`、`set`、`all`、`type`、`actor_ids.values`、`len`、`bool`、`_identity`、`database_probe`等。 返回路径：L280的`state, {key: True for key in SEMANTICS[:5]}`。
- `initial.accept`（L251–L253）：接收`actor`。 调用`barrier.wait`、`http`。 返回路径：L253的`actor, http(actor, "POST", redeem, {"code": codes[0]})[0]`。
- `after_restart`（L283–L291）：接收`http`、`database_probe`、`state`、`process_generation`。 调用`require`、`bool`、`_identity`、`_physical`、`_access`。 返回路径：L291的`{"postgres.restart_retention": True}`。
- `fresh_database`（L294–L302）：接收`database_probe`、`previous_state`。 调用`require`、`_identity`、`database_probe`。 返回路径：L302的`{"postgres.fresh_database": True}`。
- `state_dict`（L305–L306）：接收`state`。 调用`asdict`。 返回路径：L306的`asdict(state)`。

</details>

**创建路径：** `scripts/extension_oracles/contest.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L306。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11525`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/extension_oracles/contest.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "363f2e846dcee1ae2853f1d032cced788ea1553eb1d089d2fc7ea2c6af172177"} -->
````python
# scripts/extension_oracles/contest.py
"""Trusted, authored contest oracle. Never copy this package into candidate workspaces.

The controller owns HTTP authentication, SQL execution and process lifecycle. This
module imports no candidate code and accepts no candidate-defined predicates/SQL.
Passing this bounded slice never proves the full original competition request.
"""

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from hashlib import sha256
from threading import Barrier
from time import sleep
from uuid import uuid4

CONTRACT_VERSION = "contest-business-v2"
SEMANTICS = (
    "team.capacity_atomic",
    "team.invitation_code_join",
    "review.identity_blind",
    "access.outsider_denied",
    "postgres.physical_rows",
    "postgres.restart_retention",
    "postgres.fresh_database",
)
REMAINING = (
    "original.full_source",
    "member_order_and_contribution",
    "cross_school_registration",
    "random_reviewer_assignment",
    "weighted_scoring",
    "teacher_confirmation",
    "concurrent_unique_registration_number",
    "email_delivery",
    "sms_delivery",
    "cloud_file_storage",
    "export",
)


class OracleFailure(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise OracleFailure(message)


@dataclass(frozen=True)
class Goal:
    """The reviewer binds an atomic predicate to exact, immutable original text."""

    source_id: str
    source_text: str
    semantic: str

    @property
    def id(self):
        value = "\0".join((CONTRACT_VERSION, self.source_id, self.source_text, self.semantic))
        return "goal-" + sha256(value.encode()).hexdigest()[:24]


def coverage(goals, witnesses):
    """No candidate-provided list of IDs or generic health result grants coverage."""
    require(len({goal.id for goal in goals}) == len(goals), "duplicate goal binding")
    require(
        all(g.semantic in SEMANTICS or g.semantic in REMAINING for g in goals),
        "unknown semantic obligation",
    )
    by_source = {}
    rows = []
    for goal in goals:
        # Only exact semantic assertion names produced by this trusted oracle count.
        verified = goal.semantic in SEMANTICS and witnesses.get(goal.semantic) is True
        rows.append(
            {
                "goal_id": goal.id,
                "source_id": goal.source_id,
                "source_sha256": sha256(goal.source_text.encode()).hexdigest(),
                "semantic": goal.semantic,
                "status": "verified" if verified else "remaining",
            }
        )
        by_source.setdefault(goal.source_id, []).append(verified)
    return {
        "obligations": rows,
        "complete_source_ids": [key for key, values in by_source.items() if all(values)],
        "remaining_obligations": list(REMAINING),
        "full_request_complete": False,
    }


TEAM_SQL = (
    "SELECT id, captain_id, capacity, name, submission_title FROM rnd_contest_team WHERE id = %s"
)
MEMBER_SQL = "SELECT user_id FROM rnd_contest_membership WHERE team_id = %s ORDER BY user_id"
INVITE_SQL = (
    "SELECT id, code_hash, status FROM rnd_contest_invitation WHERE team_id = %s ORDER BY id"
)
IDENTITY_SQL = "SELECT current_database() AS database, oid AS database_oid FROM pg_database WHERE datname = current_database()"
EMPTY_SQL = "SELECT count(*) AS count FROM rnd_contest_team"


@dataclass(frozen=True)
class State:
    team_id: int
    captain_id: int
    member_id: int
    invitations: tuple
    name: str
    submission_title: str
    database_identity: tuple
    process_generation: str


def _response(http, actor, method, path, payload=None, statuses=(200,)):
    status, body = http(actor, method, path, payload)
    require(status in statuses, f"{actor} {method} {path}: unexpected status {status}")
    require(isinstance(body, dict), f"{method} {path}: JSON object required")
    return status, body


def _id(body):
    value = body.get("id")
    require(type(value) is int and value > 0, "positive integer id required")
    return value


def _identity(probe):
    rows = probe(IDENTITY_SQL, ())
    require(len(rows) == 1, "PostgreSQL catalog identity missing")
    require(type(rows[0]["database_oid"]) is int, "physical PostgreSQL OID required")
    return rows[0]["database"], rows[0]["database_oid"]


def _physical(probe, state):
    teams = probe(TEAM_SQL, (state.team_id,))
    require(len(teams) == 1, "physical PostgreSQL team row missing")
    expected = {
        "id": state.team_id,
        "captain_id": state.captain_id,
        "capacity": 2,
        "name": state.name,
        "submission_title": state.submission_title,
    }
    require(teams[0] == expected, "physical PostgreSQL team row differs from submitted values")
    members = probe(MEMBER_SQL, (state.team_id,))
    require(
        sorted(row["user_id"] for row in members) == sorted([state.captain_id, state.member_id]),
        "physical membership must contain exactly captain and one accepted invitee",
    )
    invitations = probe(INVITE_SQL, (state.team_id,))
    require(len(invitations) == 3, "physical invitation rows missing")
    expected = {row[0]: row[1] for row in state.invitations}
    require(
        {row["id"]: row["code_hash"] for row in invitations} == expected,
        "physical invitation hashes differ from issued opaque codes",
    )
    status_by_id = {row["id"]: row["status"] for row in invitations}
    require(
        status_by_id[state.invitations[0][0]] == "active"
        and status_by_id[state.invitations[2][0]] == "revoked",
        "physical invitation lifecycle differs from revocation state",
    )


def _access(http, state):
    path = f"/rnd/contest/teams/{state.team_id}"
    _, detail = _response(http, "captain", "GET", path)
    require(
        detail.get("id") == state.team_id and detail.get("name") == state.name,
        "captain cannot read their persisted team",
    )
    require(
        sorted(detail.get("member_ids", [])) == sorted([state.captain_id, state.member_id]),
        "captain membership detail is incorrect",
    )
    for actor in ("outsider", "reviewer"):
        _response(http, actor, "GET", path, statuses=(403, 404))
    review = f"/rnd/contest/review/teams/{state.team_id}"
    _, blind = _response(http, "reviewer", "GET", review)
    # Strict allowlist rejects nested metadata, aliases, debug fields and name leaks.
    require(
        blind == {"id": state.team_id, "submission_title": state.submission_title},
        "reviewer projection leaks identity or loses the review submission",
    )
    for actor in ("captain", "member_a", "member_b", "outsider", "anonymous"):
        _response(http, actor, "GET", review, statuses=(401, 403, 404))
    _response(http, "anonymous", "GET", path, statuses=(401, 403, 404))


def initial(http, database_probe, actor_ids, process_generation):
    """Drive fresh authenticated HTTP + independently authenticated read-only SQL probes.

    http(actor, method, path, payload) -> (status, normalized JSON body).
    Each concurrent call MUST use an independent HTTP connection and native token.
    database_probe(sql, params) is controller-owned PostgreSQL, never an app endpoint.
    actor_ids contains five distinct synthetic native user IDs.
    """
    require(
        set(actor_ids) == {"captain", "member_a", "member_b", "outsider", "reviewer"},
        "exact synthetic actor set required",
    )
    require(all(type(v) is int and v > 0 for v in actor_ids.values()), "invalid native user IDs")
    require(len(set(actor_ids.values())) == 5, "actors must be distinct authenticated users")
    require(bool(process_generation), "trusted process generation required")
    identity = _identity(database_probe)
    require(database_probe(EMPTY_SQL, ()) == [{"count": 0}], "oracle requires a fresh business DB")
    nonce = uuid4().hex
    name, title = "private-team-" + nonce, "submission-" + nonce
    _, body = _response(
        http,
        "captain",
        "POST",
        "/rnd/contest/teams",
        {"name": name, "capacity": 2, "submission_title": title},
        (200, 201),
    )
    team_id = _id(body)
    invite_path = f"/rnd/contest/teams/{team_id}/invitations"
    _response(http, "outsider", "POST", invite_path, {"expires_in_seconds": 300}, (403, 404))
    invitations = []
    codes = []
    for expiry in (300, 1, 300):
        _, body = _response(
            http, "captain", "POST", invite_path, {"expires_in_seconds": expiry}, (200, 201)
        )
        code = body.get("code", "")
        require(
            isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_-]{32,128}", code),
            "invitation must expose an opaque URL-safe code of at least 32 characters",
        )
        codes.append(code)
        invitations.append((_id(body), sha256(code.encode()).hexdigest()))
    require(
        len(set(codes)) == 3 and len({row[0] for row in invitations}) == 3,
        "independently issued invitation codes and IDs must be distinct",
    )
    revoke = f"/rnd/contest/invitations/{invitations[2][0]}/revoke"
    _response(http, "outsider", "POST", revoke, {}, (403, 404))
    _response(http, "captain", "POST", revoke, {}, (200,))
    redeem = "/rnd/contest/invitations/redeem"
    _response(http, "outsider", "POST", redeem, {"code": uuid4().hex + uuid4().hex}, (404,))
    _response(http, "anonymous", "POST", redeem, {"code": codes[0]}, (401, 403))
    _response(http, "member_a", "POST", redeem, {"code": codes[2]}, (410,))
    sleep(1.2)
    _response(http, "member_a", "POST", redeem, {"code": codes[1]}, (410,))
    barrier = Barrier(2)

    def accept(actor):
        barrier.wait(timeout=10)
        return actor, http(actor, "POST", redeem, {"code": codes[0]})[0]

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(accept, ("member_a", "member_b")))
    winners = [actor for actor, status in results if status in (200, 201)]
    require(
        len(winners) == 1, "exactly one concurrent code redemption must succeed for the final slot"
    )
    require(
        all(status in (200, 201, 409) for _, status in results),
        "full team must reject the losing redemption with 409",
    )
    winner = winners[0]
    state = State(
        team_id,
        actor_ids["captain"],
        actor_ids[winner],
        tuple(invitations),
        name,
        title,
        identity,
        process_generation,
    )
    _physical(database_probe, state)
    _response(http, winner, "POST", redeem, {"code": codes[0]}, (200,))
    _physical(database_probe, state)
    _access(http, state)
    return state, {key: True for key in SEMANTICS[:5]}


def after_restart(http, database_probe, state, process_generation):
    require(
        bool(process_generation) and process_generation != state.process_generation,
        "restart must be observed by the trusted process supervisor",
    )
    require(_identity(database_probe) == state.database_identity, "restart switched PostgreSQL DB")
    _physical(database_probe, state)
    _access(http, state)
    return {"postgres.restart_retention": True}


def fresh_database(database_probe, previous_state):
    require(
        _identity(database_probe) != previous_state.database_identity,
        "fresh replay must use a distinct PostgreSQL database identity",
    )
    require(
        database_probe(EMPTY_SQL, ()) == [{"count": 0}], "prior business rows leaked into fresh DB"
    )
    return {"postgres.fresh_database": True}


def state_dict(state):
    return asdict(state)
````
