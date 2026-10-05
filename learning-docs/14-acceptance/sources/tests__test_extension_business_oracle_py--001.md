# tests/test_extension_business_oracle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.extension_oracles.contest`、`workbench.capability_contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `SimulatedCandidate`（L32–L125）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SimulatedCandidate.__init__`（L35–L41）：接收`fault`。 调用`Lock`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `SimulatedCandidate.http`（L43–L45）：接收`actor`、`method`、`path`、`payload`。 调用`self._http`。 返回路径：L45的`self._http(actor, method, path, payload)`。
- `SimulatedCandidate._http`（L47–L105）：接收`actor`、`method`、`path`、`payload`。 控制顺序：L48按`self.fault == "health_only"`分支；L50按`method == "POST" and path.endswith("/teams")`分支；L54按`method == "POST" and path.endswith("/invitations")`分支；L55按`actor != "captain"`分支；L66按`method == "POST" and path.endswith("/revoke")`分支；L67按`actor != "captain" and self.fault != "revoke_bypass"`分支；L70按`self.fault != "ignore_revocation"`分支；L73按`method == "POST" and path.endswith("/redeem")`分支。后续分支沿下方源码相同行号继续阅读。 调用`path.endswith`、`uuid4`、`len`、`sha256(code.encode()).hexdigest`、`sha256`、`code.encode`、`monotonic`、`self.invites.append`、`int`等。 返回路径：L49的`200, {"ok": True}`；L53的`201, {"id": 1}`；L56的`403, {}`。
- `SimulatedCandidate.probe`（L107–L125）：接收`sql`、`params`。 控制顺序：L108按`sql == IDENTITY_SQL`分支；L110按`sql == EMPTY_SQL`分支；L112按`sql == TEAM_SQL`分支；L113按`self.fault == "no_physical_write" or self.team is None`分支；L116按`self.fault == "wrong_physical_value"`分支；L119按`sql == MEMBER_SQL`分支；L121按`sql == INVITE_SQL`分支；L125抛异常，停止当前正常路径。 调用`dict`、`int`、`deepcopy`、`sorted`、`AssertionError`。 返回路径：L109的`[dict(self.database)]`；L111的`[{"count": int(self.team is not None)}]`；L114的`[]`。
- `test_authored_simulation_accepts_correct_bounded_behavior`（L128–L137）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L131断言`witnesses == {key: True for key in SEMANTICS[:5]}`；L132断言`after_restart(candidate.http, candidate.probe, state, "process-2") == { "postgres.res…`；L137断言`fresh_database(other.probe, state) == {"postgres.fresh_database": True}`。 调用`SimulatedCandidate`、`initial`、`after_restart`、`fresh_database`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_oracle_rejects_adversarial_candidate`（L158–L161）：接收`fault`。 调用`SimulatedCandidate`、`pytest.raises`、`initial`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supervisor_must_observe_restart_and_same_database`（L164–L171）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimulatedCandidate`、`initial`、`pytest.raises`、`after_restart`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restart_rejects_disappeared_physical_rows`（L174–L179）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimulatedCandidate`、`initial`、`pytest.raises`、`after_restart`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fresh_database_rejects_reuse_and_contamination`（L182–L189）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimulatedCandidate`、`initial`、`pytest.raises`、`fresh_database`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_or_missing_native_actor_identity_is_rejected`（L192–L195）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimulatedCandidate`、`pytest.raises`、`initial`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frozen_original_goal_ids_and_remaining_scope_cannot_be_health_covered`（L198–L221）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L201断言`fixture["source_units"] == scope_sources([fixture["requirement_text"]])`；L205断言`[goal.id for goal in goals] == [row["goal_id"] for row in fixture["goals"]]`；L206断言`{g.source_id for g in goals} == {s["id"] for s in fixture["source_units"]}`；L208断言`all(row["status"] == "remaining" for row in report["obligations"])`；L210断言`len([r for r in report["obligations"] if r["status"] == "verified"]) == 4`；L211断言`not report["complete_source_ids"]`；L212断言`not report["full_request_complete"]`；L213遍历`( "email_delivery", "sms_delivery", "cloud_file_storage", "export…`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`json.loads`、`path.read_text`、`scope_sources`、`Goal`、`coverage`、`all`、`dict.fromkeys`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_goal_identity_changes_if_source_or_semantic_changes`（L224–L227）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L226断言`goal.id != Goal("source-0-1", "加权评分", "review.identity_blind").id`；L227断言`goal.id != Goal("source-0-1", "匿名/盲审支持", "weighted_scoring").id`。 调用`Goal`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_extension_business_oracle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L227。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_extension_business_oracle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c72b3464a477a4989858514dcebc193732aabd8c3fe1a8606e4dd06c282c2e9b"} -->
````python
# tests/test_extension_business_oracle.py
"""Authored adversarial simulations of the trusted oracle; NOT native/live acceptance."""

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from threading import Lock
from time import monotonic
from uuid import uuid4

import pytest

from scripts.extension_oracles.contest import (
    EMPTY_SQL,
    IDENTITY_SQL,
    INVITE_SQL,
    MEMBER_SQL,
    SEMANTICS,
    TEAM_SQL,
    Goal,
    OracleFailure,
    after_restart,
    coverage,
    fresh_database,
    initial,
)
from workbench.capability_contracts import scope_sources

ACTORS = {"captain": 10, "member_a": 21, "member_b": 22, "outsider": 30, "reviewer": 40}


class SimulatedCandidate:
    """Deliberately independent tiny state machine, with selectable product faults."""

    def __init__(self, fault=None):
        self.fault = fault
        self.team = None
        self.members = []
        self.invites = []
        self.lock = Lock()
        self.database = {"database": "test_owned", "database_oid": 1234}

    def http(self, actor, method, path, payload):
        with self.lock:
            return self._http(actor, method, path, payload)

    def _http(self, actor, method, path, payload):
        if self.fault == "health_only":
            return 200, {"ok": True}
        if method == "POST" and path.endswith("/teams"):
            self.team = {"id": 1, "captain_id": ACTORS[actor], **payload}
            self.members = [ACTORS[actor]]
            return 201, {"id": 1}
        if method == "POST" and path.endswith("/invitations"):
            if actor != "captain":
                return 403, {}
            code = uuid4().hex + uuid4().hex
            invitation = {
                "id": len(self.invites) + 1,
                "code_hash": sha256(code.encode()).hexdigest(),
                "status": "active",
                "expires": monotonic() + payload["expires_in_seconds"],
            }
            self.invites.append(invitation)
            return 201, {"id": invitation["id"], "code": code}
        if method == "POST" and path.endswith("/revoke"):
            if actor != "captain" and self.fault != "revoke_bypass":
                return 403, {}
            invite = self.invites[int(path.split("/")[-2]) - 1]
            if self.fault != "ignore_revocation":
                invite["status"] = "revoked"
            return 200, {}
        if method == "POST" and path.endswith("/redeem"):
            if actor == "anonymous":
                return 401, {}
            digest = sha256(payload["code"].encode()).hexdigest()
            invite = next((row for row in self.invites if row["code_hash"] == digest), None)
            if invite is None:
                return (200 if self.fault == "accept_unknown_code" else 404), {}
            if invite["status"] == "revoked":
                return 410, {}
            if invite["expires"] < monotonic() and self.fault != "ignore_expiry":
                return 410, {}
            if ACTORS[actor] in self.members:
                if self.fault == "duplicate_membership":
                    self.members.append(ACTORS[actor])
                return 200, {}
            if len(self.members) >= 2 and self.fault != "concurrent_overfill":
                return 409, {}
            self.members.append(ACTORS[actor])
            return 200, {}
        if method == "GET" and "/review/" in path:
            if actor != "reviewer" and self.fault != "review_role_bypass":
                return 403, {}
            result = {"id": 1, "submission_title": self.team["submission_title"]}
            if self.fault == "identity_leak":
                result["metadata"] = {"identity": {"school": "Synthetic School"}}
            if self.fault == "identity_value_leak":
                result["submission_title"] += self.team["name"]
            return 200, result
        if method == "GET":
            if actor != "captain" and self.fault != "outsider_read":
                return 403, {}
            return 200, {**self.team, "member_ids": list(self.members)}
        return 404, {}

    def probe(self, sql, params):
        if sql == IDENTITY_SQL:
            return [dict(self.database)]
        if sql == EMPTY_SQL:
            return [{"count": int(self.team is not None)}]
        if sql == TEAM_SQL:
            if self.fault == "no_physical_write" or self.team is None:
                return []
            row = deepcopy(self.team)
            if self.fault == "wrong_physical_value":
                row["submission_title"] = "not the submitted value"
            return [row]
        if sql == MEMBER_SQL:
            return [{"user_id": value} for value in sorted(self.members)]
        if sql == INVITE_SQL:
            return [
                {key: row[key] for key in ("id", "code_hash", "status")} for row in self.invites
            ]
        raise AssertionError("unrecognized trusted SQL")


def test_authored_simulation_accepts_correct_bounded_behavior():
    candidate = SimulatedCandidate()
    state, witnesses = initial(candidate.http, candidate.probe, ACTORS, "process-1")
    assert witnesses == {key: True for key in SEMANTICS[:5]}
    assert after_restart(candidate.http, candidate.probe, state, "process-2") == {
        "postgres.restart_retention": True
    }
    other = SimulatedCandidate()
    other.database["database_oid"] = 5678
    assert fresh_database(other.probe, state) == {"postgres.fresh_database": True}


@pytest.mark.parametrize(
    "fault",
    [
        "health_only",
        "concurrent_overfill",
        "revoke_bypass",
        "ignore_revocation",
        "ignore_expiry",
        "accept_unknown_code",
        "duplicate_membership",
        "identity_leak",
        "identity_value_leak",
        "review_role_bypass",
        "outsider_read",
        "no_physical_write",
        "wrong_physical_value",
    ],
)
def test_independent_oracle_rejects_adversarial_candidate(fault):
    candidate = SimulatedCandidate(fault)
    with pytest.raises(OracleFailure):
        initial(candidate.http, candidate.probe, ACTORS, "process-1")


def test_supervisor_must_observe_restart_and_same_database():
    candidate = SimulatedCandidate()
    state, _ = initial(candidate.http, candidate.probe, ACTORS, "process-1")
    with pytest.raises(OracleFailure, match="trusted process"):
        after_restart(candidate.http, candidate.probe, state, "process-1")
    candidate.database["database_oid"] = 9999
    with pytest.raises(OracleFailure, match="switched PostgreSQL"):
        after_restart(candidate.http, candidate.probe, state, "process-2")


def test_restart_rejects_disappeared_physical_rows():
    candidate = SimulatedCandidate()
    state, _ = initial(candidate.http, candidate.probe, ACTORS, "process-1")
    candidate.team = None
    with pytest.raises(OracleFailure, match="physical PostgreSQL team row missing"):
        after_restart(candidate.http, candidate.probe, state, "process-2")


def test_fresh_database_rejects_reuse_and_contamination():
    candidate = SimulatedCandidate()
    state, _ = initial(candidate.http, candidate.probe, ACTORS, "process-1")
    with pytest.raises(OracleFailure, match="distinct PostgreSQL"):
        fresh_database(candidate.probe, state)
    candidate.database["database_oid"] = 9999
    with pytest.raises(OracleFailure, match="prior business rows leaked"):
        fresh_database(candidate.probe, state)


def test_duplicate_or_missing_native_actor_identity_is_rejected():
    candidate = SimulatedCandidate()
    with pytest.raises(OracleFailure, match="distinct"):
        initial(candidate.http, candidate.probe, {**ACTORS, "outsider": 10}, "process-1")


def test_frozen_original_goal_ids_and_remaining_scope_cannot_be_health_covered():
    path = Path(__file__).parent / "fixtures/contest_oracle/original_requirement.json"
    fixture = json.loads(path.read_text())
    assert fixture["source_units"] == scope_sources([fixture["requirement_text"]])
    goals = [
        Goal(row["source_id"], row["source_text"], row["semantic"]) for row in fixture["goals"]
    ]
    assert [goal.id for goal in goals] == [row["goal_id"] for row in fixture["goals"]]
    assert {g.source_id for g in goals} == {s["id"] for s in fixture["source_units"]}
    report = coverage(goals, {"health": True, **{goal.id: True for goal in goals}})
    assert all(row["status"] == "remaining" for row in report["obligations"])
    report = coverage(goals, dict.fromkeys(SEMANTICS, True))
    assert len([r for r in report["obligations"] if r["status"] == "verified"]) == 4
    assert not report["complete_source_ids"]
    assert not report["full_request_complete"]
    for obligation in (
        "email_delivery",
        "sms_delivery",
        "cloud_file_storage",
        "export",
        "random_reviewer_assignment",
        "weighted_scoring",
    ):
        assert obligation in report["remaining_obligations"]


def test_goal_identity_changes_if_source_or_semantic_changes():
    goal = Goal("source-0-1", "匿名/盲审支持", "review.identity_blind")
    assert goal.id != Goal("source-0-1", "加权评分", "review.identity_blind").id
    assert goal.id != Goal("source-0-1", "匿名/盲审支持", "weighted_scoring").id
````
