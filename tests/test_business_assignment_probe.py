"""MockTransport unit tests for native probes; these are not live native evidence.

Plan variations exist only in these isolated tests. The production HTTP probe
must never substitute or mutate the approved Plan to obtain a positive branch.
"""

import json
from contextlib import contextmanager
from copy import deepcopy

import httpx
import pytest

from workbench import business_probe as probe
from workbench.domain import Plan, digest
from workbench.settings import ROOT


@contextmanager
def assignment_case(template, read_scope=None, assign_scope=None, violation=None):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    if read_scope:
        plan.business.permissions.append(
            type(plan.business.permissions[0])(
                role="employee", entity="tasks", actions=["read"], scope=read_scope
            )
        )
    if assign_scope:
        role, scope = assign_scope
        grant = next(
            item
            for item in plan.business.permissions
            if item.entity == "requests" and item.role == role
        )
        grant.actions.append("assign")
        grant.scope = scope
    original = plan.model_dump()
    fastapi = template == "fastapiadmin"
    prefix = "/business" if fastapi else "/admin-api/infra/rnd-business"
    targets = [
        {"entity": name, "api": f"/admin-api/infra/{name}", "list": f"/admin-api/infra/{name}/page"}
        for name in ("requests", "tasks")
    ]
    identities = {
        "manager": ("20", "manager"),
        "employee": ("21", "employee"),
        "other_employee": ("22", "employee"),
        "service": ("23", "service"),
        "other_service": ("24", "service"),
    }
    records = {
        "requests": {"id": "11", "title": "Request", "created_by": "21", "assignee_id": "23"},
        "tasks": {"id": "12", "title": "Task", "created_by": "20", "assignee_id": "23"},
    }
    histories = {name: [{"id": "1", "event": "created"}] for name in records}
    notices = {label: [] for label in identities}
    calls = []

    def permission(role, entity):
        return next(
            (p for p in plan.business.permissions if p.role == role and p.entity == entity), None
        )

    def permitted(grant, user, record):
        if grant is None:
            return False
        return (
            grant.scope == "all"
            or grant.scope == "own"
            and record["created_by"] == user
            or grant.scope == "assigned"
            and record["assignee_id"] == user
        )

    def answer(data=None, code=None):
        if code:
            return httpx.Response(code if fastapi else 200, json={"code": code})
        return httpx.Response(200, json={"code": 200 if fastapi else 0, "data": data})

    def handler(request):
        label = request.headers["Authorization"].removeprefix("Bearer ")
        user, role = identities[label]
        path = request.url.path
        body = json.loads(request.content) if request.content else {}
        calls.append((label, request.method, path, deepcopy(body)))
        if request.method == "GET" and path.endswith(("/inbox", "/notifications")):
            return answer(notices[label])
        entity = next((name for name in records if f"/{name}/" in path), None)
        entity = entity or request.url.params.get("entity") or body.get("entity")
        if request.method == "GET" and path.endswith("/history"):
            assert role == "manager" and request.url.params["audit"] == "true"
            return answer(histories[entity])
        record = records[entity]
        grant = permission(role, entity)
        if request.method == "GET":
            readable = grant is not None and "read" in grant.actions
            scoped = permitted(grant, user, record)
            row = {probe.wire_name(template, key): value for key, value in record.items()}
            if path.endswith(("/list", "/page")):
                if not readable:
                    return answer(code=403)
                if (
                    violation == "peer_list_leak"
                    and label == "other_employee"
                    and entity == "tasks"
                ):
                    scoped = True
                return answer({"items" if fastapi else "list": [row] if scoped else []})
            assert path.endswith(("/get", "/related"))
            if violation == "peer_detail_leak" and label == "other_employee":
                scoped = True
            return answer(row) if readable and scoped else answer(code=404 if fastapi else 403)
        action = path.rsplit("/", 1)[-1] if fastapi else body.get("action", "update")
        if action == "update" and not fastapi:
            assert request.method == "PUT" and set(body) == {"id", "title"}
        elif not fastapi:
            assert request.method == "POST" and path == prefix + "/action"
            expected = {
                "entity",
                "id",
                "action",
                "assigneeId" if action == "assign" else "transition",
            }
            assert set(body) == expected, (
                "Native action body must reach the intended permission gate"
            )
        else:
            assert request.method == "POST"
            assert path == f"{prefix}/{entity}/{record['id']}/{action}"
            assert set(body) == {
                "assignee" if action == "assign" else action if action == "transition" else "title"
            }
        recipient = body.get("assignee" if fastapi else "assigneeId")
        error = None
        if grant is None or action not in grant.actions:
            if violation not in {"unauthorized_actor", "readonly_mutation"}:
                error = 403
        elif not permitted(grant, user, record) and violation != "foreign_row":
            error = 404 if fastapi else 403
        if error is None and action == "assign":
            recipient_role = next(r for i, r in identities.values() if i == recipient)
            recipient_grant = permission(recipient_role, entity)
            eligible = (
                recipient_grant is not None
                and "read" in recipient_grant.actions
                and recipient_grant.scope in {"assigned", "all"}
            )
            if not eligible and violation != "ineligible_assignee":
                error = 422 if fastapi else 400
        if error is not None:
            if violation == "server_error":
                return answer(code=500)
            if violation == "unrelated_denial":
                return answer(code=401)
            if violation == "denial_row_write":
                record["title"] += " changed"
            if violation == "denial_audit_write":
                histories[entity].append({"id": "rogue", "event": "assigned"})
            if violation == "denial_notice_write":
                notices["manager"].append(
                    {"id": "rogue", "entity": entity, "record_id": record["id"]}
                )
            return answer(code=error)
        if action == "assign":
            if (
                violation == "restore_failure"
                and record["assignee_id"] == "21"
                and recipient == "23"
            ):
                return answer(code=400)
            if not (violation == "positive_not_persisted" and recipient == "21"):
                record["assignee_id"] = recipient
        histories[entity].append({"id": str(len(histories[entity]) + 1), "event": action})
        return answer({probe.wire_name(template, key): value for key, value in record.items()})

    clients = {}
    for label in identities:
        client = probe.BusinessClient(template, "http://127.0.0.1", label, targets)
        client.http.close()
        client.http = httpx.Client(
            base_url="http://127.0.0.1",
            headers={"Authorization": "Bearer " + label},
            transport=httpx.MockTransport(handler),
        )
        clients[label] = client
    actors = {
        label: (identities[label][0], client)
        for label, client in clients.items()
        if label != "manager"
    }
    args = (plan, clients["manager"], actors, {name: row["id"] for name, row in records.items()})
    try:
        yield args, records, calls
        assert plan.model_dump() == original, (
            "Even isolated probe execution must preserve its input Plan"
        )
    finally:
        for client in clients.values():
            client.close()


def by_case(proof):
    return {(item["entity"], item["case"]): item for item in proof["checks"]}


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_canonical_plan_exercises_target_and_actor_denials_without_invented_grants(template):
    with assignment_case(template) as (args, records, calls):
        proof = probe.verify_assignment_boundaries(*args)
        checks = by_case(proof)
        assert proof["spec_digest"] == digest(args[0].model_dump())
        assert checks["requests", "own_only_assignee_denied"]["status"] == "exercised"
        assert checks["tasks", "no_read_assignee_denied"]["status"] == "exercised"
        for entity in records:
            assert checks[entity, "unauthorized_actor_denied"]["status"] == "exercised"
            assert checks[entity, "foreign_row_denied"]["status"] == "absent"
            assert checks[entity, "read_only_recipient_accepted"]["status"] == "absent"
        assert sum(method == "POST" for _, method, _, _ in calls) == 4
        assert len(proof["checks"]) == 10


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("scope", ["assigned", "all"])
def test_approved_read_only_recipient_is_assignable_without_acquiring_mutation_power(
    template, scope
):
    with assignment_case(template, read_scope=scope) as (args, records, calls):
        checks = by_case(probe.verify_assignment_boundaries(*args))
        positive = checks["tasks", "read_only_recipient_accepted"]
        assert positive["status"] == "exercised" and positive["assignee_scope"] == scope
        assert positive["persisted_and_recipient_readable"]
        assert positive["original_assignee_restored"] and records["tasks"]["assignee_id"] == "23"
        for action in ("assign", "update", "transition"):
            assert checks["tasks", f"read_only_recipient_{action}_denied"]["status"] == "exercised"
        assert positive["peer_isolation"]["status"] == (
            "exercised" if scope == "assigned" else "absent"
        )
        if scope == "assigned":
            assert positive["peer_isolation"]["record_endpoint"] == (
                "related" if template == "fastapiadmin" else "get"
            )
        if template == "yudao-vben":
            assert any(
                method == "PUT" and path.endswith("/tasks/update") for _, method, path, _ in calls
            )


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("role,scope", [("employee", "own"), ("service", "assigned")])
def test_foreign_row_denial_is_exercised_only_with_an_existing_restricted_assign_grant(
    template, role, scope
):
    with assignment_case(template, assign_scope=(role, scope)) as (args, _, calls):
        checks = by_case(probe.verify_assignment_boundaries(*args))
        assert checks["requests", "foreign_row_denied"]["status"] == "exercised"
        assert checks["requests", "foreign_row_denied"]["actor_role"] == role
        assert any(label == "other_" + role and method == "POST" for label, method, _, _ in calls)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "violation",
    [
        "ineligible_assignee",
        "unauthorized_actor",
        "server_error",
        "unrelated_denial",
        "denial_row_write",
        "denial_audit_write",
        "denial_notice_write",
    ],
)
def test_http_faults_cannot_be_reported_as_assignment_boundary_proof(template, violation):
    with assignment_case(template, violation=violation) as (args, _, _):
        with pytest.raises(AssertionError):
            probe.verify_assignment_boundaries(*args)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "violation",
    [
        "positive_not_persisted",
        "readonly_mutation",
        "peer_list_leak",
        "peer_detail_leak",
        "restore_failure",
    ],
)
def test_positive_assignment_requires_persistence_least_privilege_isolation_and_restoration(
    template, violation
):
    with assignment_case(template, read_scope="assigned", violation=violation) as (args, _, _):
        with pytest.raises(AssertionError):
            probe.verify_assignment_boundaries(*args)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_approved_restricted_assign_cannot_escape_its_row_scope(template):
    with assignment_case(
        template, assign_scope=("service", "assigned"), violation="foreign_row"
    ) as (args, _, _):
        with pytest.raises(AssertionError, match="foreign_row_denied"):
            probe.verify_assignment_boundaries(*args)
