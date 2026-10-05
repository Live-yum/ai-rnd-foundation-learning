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
