import httpx
import pytest

from workbench import business_probe as probe


@pytest.mark.parametrize(
    "violation",
    [None, "role", "identity", "global_admin", "menus", "menu_scope", "registration_denied"],
)
def test_public_registration_is_anonymous_and_requires_native_default_role(monkeypatch, violation):
    original_client = httpx.Client
    clients, registered, logins = [], [], []

    def handler(request):
        if request.url.path == "/system/user/register":
            assert "authorization" not in request.headers
            import json

            body = json.loads(request.content)
            assert body["is_superuser"] is True and body["role_ids"] == [1]
            registered.append(True)
            if violation == "registration_denied":
                return httpx.Response(409, json={"code": 409})
            data = {"id": 8}
        elif request.url.path == "/business/configuration":
            assert request.headers["Authorization"] == "Bearer synthetic-test-token"
            data = {
                "actor": {
                    "id": "9" if violation == "identity" else "8",
                    "role": "manager" if violation == "role" else "employee",
                },
                "can_manage_roles": False,
                "permissions": [{"entity": "customers", "actions": ["read"]}],
            }
        else:
            assert request.url.path == "/system/user/current/info"
            data = {
                "is_superuser": violation == "global_admin",
                "menus": []
                if violation == "menus"
                else [{"id": 10, "component_path": "module_rnd/customers/index"}],
            }
            if violation == "menu_scope":
                data["menus"].append({"id": 11, "component_path": "module_rnd/tasks/index"})
        return httpx.Response(200, json={"code": 200, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    def login(*args):
        logins.append(args)
        return "synthetic-test-token"

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", login)
    if violation:
        with pytest.raises(AssertionError):
            probe.register_fastapi_actor(
                "http://127.0.0.1",
                "syntheticuser",
                "SyntheticPass123!",
                [{"entity": "customers"}, {"entity": "tasks"}],
            )
        assert all(client.is_closed for client in clients)
    else:
        identifier, actor = probe.register_fastapi_actor(
            "http://127.0.0.1",
            "syntheticuser",
            "SyntheticPass123!",
            [{"entity": "customers"}, {"entity": "tasks"}],
        )
        assert identifier == "8"
        actor.close()
    assert registered == [True]
    assert len(logins) == (0 if violation == "registration_denied" else 1)


@pytest.mark.parametrize(
    "violation",
    [None, "role", "identity", "global_admin", "permissions", "menus", "registration_denied"],
)
def test_yudao_registration_requires_native_anonymous_default_membership(monkeypatch, violation):
    import json

    original_client = httpx.Client
    clients = []

    def handler(request):
        if request.url.path == "/admin-api/system/auth/register":
            assert "authorization" not in request.headers
            assert request.headers["tenant-id"] == "1"
            body = json.loads(request.content)
            assert body["roleIds"] == [1] and body["roles"] == ["super_admin"]
            if violation == "registration_denied":
                return httpx.Response(200, json={"code": 403})
            data = {"userId": 8}
        elif request.url.path.endswith("/me"):
            data = {
                "id": "9" if violation == "identity" else "8",
                "roles": ["manager" if violation == "role" else "employee"],
            }
        else:
            assert request.url.path == "/admin-api/system/auth/get-permission-info"
            data = {
                "roles": ["super_admin"] if violation == "global_admin" else ["rnd_employee"],
                "permissions": ["*:*:*"] if violation == "permissions" else ["infra:rnd:query"],
                "menus": [] if violation == "menus" else [{"id": 20}],
            }
        return httpx.Response(200, json={"code": 0, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", lambda *args: "synthetic-test-token")
    if violation:
        with pytest.raises(AssertionError):
            probe.register_yudao_actor("http://127.0.0.1", "syntheticuser", "Synthetic123!", [])
    else:
        identifier, actor = probe.register_yudao_actor(
            "http://127.0.0.1", "syntheticuser", "Synthetic123!", []
        )
        assert identifier == "8"
        actor.close()
    assert all(client.is_closed for client in clients)


def reminder_case(template, violation=None):
    import json

    from workbench.domain import Plan
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    fastapi = template == "fastapiadmin"
    store = []

    class Client:
        def __init__(self, role):
            self.role = role

        def inbox(self):
            return [row for recipient, row in store if recipient is self]

        def read_notice(self, identifier):
            matches = [
                row for recipient, row in store if row["id"] == identifier and recipient is self
            ]
            if not matches and violation != "wrong_recipient":
                code = 403
            else:
                code = 200 if fastapi else 0
                if matches and violation != "unread":
                    matches[0].update(
                        {"read": True} if fastapi else {"read_at": "2026-09-30T00:00:00Z"}
                    )
            return httpx.Response(
                200,
                json={"code": code, "data": True},
                request=httpx.Request("POST", "http://127.0.0.1/read"),
            )

    creator, assignee, outsider = [Client(role) for role in ["creator", "assignee", "outsider"]]
    recipients = {"creator": creator, "assignee": assignee}

    def emit(entity, identifier, event, transition=None):
        expected = probe.reminder_recipients(plan, entity, event, recipients, transition)
        for recipient in expected:
            if violation in {"missing_due", "missing"} and (
                event == "due" or violation == "missing"
            ):
                continue
            for _ in range(
                2
                if violation == "duplicated_due" and event == "due" or violation == "duplicated"
                else 1
            ):
                row = {"id": str(len(store) + 1), "entity": entity, "record_id": identifier}
                row.update(
                    {"event": event, "read": False}
                    if fastapi
                    else {"message": f"{entity} #{identifier} {event}", "read_at": None}
                )
                store.append((outsider if violation == "misrouted" else recipient, row))
        return "action result"

    return plan, recipients, outsider, emit


@pytest.mark.parametrize(
    "violation", [None, "missing_due", "duplicated_due", "unread", "wrong_recipient", "misrouted"]
)
@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("recipient", ["creator", "assignee"])
def test_assignment_due_idempotency_and_read_recipient_are_required(template, violation, recipient):
    plan, recipients, outsider, emit = reminder_case(template, violation)
    for notice in plan.business.notifications:
        if notice.event in {"assigned", "due"}:
            notice.recipient = recipient
    records = []
    for entity, identifier in [("requests", "2"), ("tasks", "3")]:
        records.append((entity, identifier, recipients["creator"], recipients["assignee"]))
        for event in ["assigned", "due"]:
            emit(entity, identifier, event)
    if violation:
        with pytest.raises(AssertionError):
            probe.verify_reminders(plan, records, [outsider])
    else:
        probe.verify_reminders(plan, records, [outsider])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "event,transition",
    [("note_added", None), ("transitioned", "start"), ("transitioned", "resolve")],
)
@pytest.mark.parametrize("recipient", ["creator", "assignee"])
@pytest.mark.parametrize(
    "violation", [None, "missing", "duplicated", "misrouted", "unread", "wrong_recipient"]
)
def test_each_note_or_transition_requires_its_own_persisted_routed_reminder(
    template, event, transition, recipient, violation
):
    plan, recipients, outsider, emit = reminder_case(template, violation)
    for notice in plan.business.notifications:
        if (notice.entity, notice.event, notice.transition) == ("requests", event, transition):
            notice.recipient = recipient
    # Pre-existing notifications cannot stand in for a missing current event.
    emit("requests", "2", event, transition)

    def action():
        return emit("requests", "2", event, transition)

    args = (plan, "requests", "2", event, recipients, [outsider], action, transition)
    if violation:
        with pytest.raises(AssertionError):
            probe.verify_event_reminders(*args)
    else:
        assert probe.verify_event_reminders(*args) == "action result"


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("employee_grant", [False, True])
@pytest.mark.parametrize(
    "violation", [None, "service_history", "manager_audit", "employee_history", "outsider_history"]
)
def test_handling_history_uses_required_service_grant_and_exact_employee_permissions(
    template, employee_grant, violation
):
    import json

    from workbench.domain import Plan
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    permission = next(
        grant
        for grant in plan.business.permissions
        if grant.role == "employee" and grant.entity == "requests"
    )
    if not employee_grant:
        permission.actions.remove("read_history")
    fastapi = template == "fastapiadmin"
    calls = []
    clients = []

    def client(role):
        def handler(request):
            calls.append((role, request.url))
            expected = (
                "/business/requests/2/history"
                if fastapi
                else "/admin-api/infra/rnd-business/history"
            )
            assert request.url.path == expected
            if not fastapi:
                assert (
                    request.url.params["entity"] == "requests" and request.url.params["id"] == "2"
                )
            if role == "manager":
                assert request.url.params["audit"] == "true"
            permitted = role in {"manager", "service"} or role == "employee" and employee_grant
            if role == "employee" and not employee_grant and violation == "employee_history":
                permitted = True
            if role == "outsider" and violation == "outsider_history":
                permitted = True
            if not permitted:
                return httpx.Response(403 if fastapi else 200, json={"code": 403})
            count = 4
            if violation == {
                "service": "service_history",
                "manager": "manager_audit",
                "employee": "employee_history",
            }.get(role):
                count = 3
            return httpx.Response(
                200,
                json={
                    "code": 200 if fastapi else 0,
                    "data": [{"id": str(i)} for i in range(count)],
                },
            )

        actor = object.__new__(probe.BusinessClient)
        actor.fastapi = fastapi
        actor.prefix = "/business" if fastapi else "/admin-api/infra/rnd-business"
        actor.http = httpx.Client(
            base_url="http://127.0.0.1", transport=httpx.MockTransport(handler)
        )
        clients.append(actor)
        return actor

    manager, service, employee, outsider = [
        client(role) for role in ["manager", "service", "employee", "outsider"]
    ]
    try:
        if violation:
            with pytest.raises(AssertionError):
                probe.verify_handling_history(
                    plan, manager, service, employee, outsider, "requests", "2"
                )
        else:
            probe.verify_handling_history(
                plan, manager, service, employee, outsider, "requests", "2"
            )
            assert {role for role, _ in calls} == {"manager", "service", "employee", "outsider"}
    finally:
        for actor in clients:
            actor.close()
