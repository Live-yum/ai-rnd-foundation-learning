"""Independent customer-service acceptance over real native HTTP authentication."""

import uuid

import httpx

from workbench.domain import digest
from workbench.native_checks import flatten, payload, record_id
from workbench.native_environment import login


def wire_name(template, name):
    if template == "fastapiadmin":
        return name
    first, *rest = name.split("_")
    return first + "".join(piece[:1].upper() + piece[1:] for piece in rest)


class BusinessClient:
    def __init__(self, template, base, token, targets):
        self.fastapi = template == "fastapiadmin"
        self.template = template
        self.prefix = "/business" if self.fastapi else "/admin-api/infra/rnd-business"
        self.targets = {t["entity"]: t for t in targets}
        self.http = httpx.Client(
            base_url=base,
            timeout=30,
            trust_env=False,
            headers={"Authorization": "Bearer " + token, "tenant-id": "1"},
        )

    def close(self):
        self.http.close()

    def call(self, method, path, **kwargs):
        return payload(self.http.request(method, path, **kwargs))

    def wire(self, data):
        return {wire_name(self.template, k): v for k, v in data.items()}

    def create(self, entity, data):
        route = (
            self.prefix + "/" + entity + "/create"
            if self.fastapi
            else self.targets[entity]["api"] + "/create"
        )
        value = self.call("POST", route, json=data if self.fastapi else self.wire(data))
        return str(value["id"] if isinstance(value, dict) else value)

    def rows(self, entity, **query):
        route = (
            self.prefix + "/" + entity + "/list" if self.fastapi else self.targets[entity]["list"]
        )
        value = self.call("GET", route, params=query)
        return value.get("items", value.get("list"))

    def action(self, entity, identifier, action, data):
        if self.fastapi:
            return self.call("POST", f"{self.prefix}/{entity}/{identifier}/{action}", json=data)
        value = {"entity": entity, "id": identifier, "action": action}
        value.update(
            {
                "assigneeId" if k == "assignee" else "note" if k == "text" else k: v
                for k, v in data.items()
            }
        )
        return self.call("POST", self.prefix + "/action", json=value)

    def history(self, entity, identifier, audit=False):
        route = (
            f"{self.prefix}/{entity}/{identifier}/history"
            if self.fastapi
            else self.prefix + "/history"
        )
        return self.call(
            "GET", route, params={"entity": entity, "id": identifier, "audit": str(audit).lower()}
        )

    def related(self, entity, identifier):
        route = (
            f"{self.prefix}/{entity}/{identifier}/related"
            if self.fastapi
            else self.prefix + "/related"
        )
        value = self.call("GET", route, params={"entity": entity, "id": identifier})
        if self.fastapi:
            return value
        return {
            group["entity"]: [entry["record"] for entry in group["records"]]
            for group in value["groups"]
        }

    def role(self, identifier, role):
        if self.fastapi:
            return self.call("PUT", f"{self.prefix}/users/{identifier}/role", json={"role": role})
        return self.call(
            "POST",
            self.prefix + "/roles",
            json={"userId": str(identifier), "role": role, "grant": True},
        )

    def inbox(self):
        return self.call("GET", self.prefix + ("/inbox" if self.fastapi else "/notifications"))

    def read_notice(self, identifier):
        if self.fastapi:
            return self.http.post(f"{self.prefix}/inbox/{identifier}/read", json={})
        return self.http.post(self.prefix + "/notifications/read", json={"id": identifier})


def register_fastapi_actor(base, username, password, targets):
    """Exercise the public native registration route without an administrator token."""
    with httpx.Client(base_url=base, timeout=30, trust_env=False) as public:
        registered = payload(
            public.post(
                "/system/user/register",
                json={
                    "username": username,
                    "password": password,
                    "name": "Synthetic employee",
                    # Native registration must not accept forged administrative claims.
                    "is_superuser": True,
                    "role_ids": [1],
                },
            )
        )
    identifier = str(record_id(registered))
    actor = BusinessClient(
        "fastapiadmin", base, login("fastapiadmin", base, username, password), targets
    )
    try:
        config = actor.call("GET", "/business/configuration")
        assert config["actor"] == {"id": identifier, "role": "employee"}
        assert config["can_manage_roles"] is False
        info = actor.call("GET", "/system/user/current/info")
        assert info.get("is_superuser") is False, "Public registration granted native administrator"
        assert info.get("menus"), "Default business role has no native menu"
        if targets:
            expected = {
                "module_rnd/" + grant["entity"] + "/index"
                for grant in config["permissions"]
                if "read" in grant["actions"]
            }
            actual = {
                (menu.get("component_path") or "").lstrip("/")
                for menu in flatten(info["menus"])
                if (menu.get("component_path") or "").lstrip("/").startswith("module_rnd/")
            }
            assert actual == expected, "Native business menus differ from approved read grants"
    except Exception:
        actor.close()
        raise
    return identifier, actor


def register_yudao_actor(base, username, password, targets):
    """Keep the native anonymous registration, validation and default membership."""
    with httpx.Client(
        base_url=base, timeout=30, trust_env=False, headers={"tenant-id": "1"}
    ) as public:
        registered = payload(
            public.post(
                "/admin-api/system/auth/register",
                json={
                    "username": username,
                    "password": password,
                    "nickname": "Synthetic employee",
                    "roleIds": [1],
                    "roles": ["super_admin"],
                },
            )
        )
    identifier = str(registered["userId"])
    actor = BusinessClient(
        "yudao-vben", base, login("yudao-vben", base, username, password), targets
    )
    try:
        membership = actor.call("GET", actor.prefix + "/me")
        assert membership["id"] == identifier
        assert membership["roles"] == ["employee"]
        info = actor.call("GET", "/admin-api/system/auth/get-permission-info")
        assert "super_admin" not in info.get("roles", [])
        assert "*:*:*" not in info.get("permissions", [])
        assert info.get("menus"), "Default business role has no native menu"
    except Exception:
        actor.close()
        raise
    return identifier, actor


def customer_service_acceptance(template, base, token, targets, plan):
    """Use synthetic owned accounts/records; do not alter any pre-existing user."""
    names = {entity.name for entity in plan.entities}
    if names != {"customers", "requests", "tasks"} or plan.business is None:
        raise ValueError(
            "Customer-service acceptance requires the declared three-resource contract"
        )
    manager = BusinessClient(template, base, token, targets)
    clients = [manager]
    attempt = uuid.uuid4().hex[:10]
    actors = {}
    browser_actors = {}
    try:
        state_response = manager.http.get(
            manager.prefix + ("/configuration" if manager.fastapi else "/meta"),
            params={"entity": "customers"},
        )
        try:
            state = payload(state_response)
        except ValueError, AssertionError:
            state = {"bootstrapRequired": True}
        if state.get("bootstrapRequired"):
            manager.call("POST", manager.prefix + "/bootstrap", json={})
        for label, role in [
            ("employee", "employee"),
            ("other_employee", "employee"),
            ("service", "service"),
            ("other_service", "service"),
        ]:
            username = "rnd" + attempt + label.replace("_", "")[:5]
            # Distinct test identities remain under native account/password validation.
            username += str(len(actors))
            password = "BusinessTest123!"
            body = {"username": username, "password": password}
            body.update(
                {"name": "Synthetic " + label, "is_superuser": False, "role_ids": [], "status": 0}
                if manager.fastapi
                else {"nickname": "Synthetic " + label}
            )
            prefix = "" if manager.fastapi else "/admin-api"
            if label == "employee":
                register = register_fastapi_actor if manager.fastapi else register_yudao_actor
                identifier, actor = register(base, username, password, targets)
            else:
                identifier = record_id(
                    manager.call("POST", prefix + "/system/user/create", json=body)
                )
                manager.role(identifier, role)
                actor = BusinessClient(
                    template, base, login(template, base, username, password), targets
                )
            clients.append(actor)
            actors[label] = (str(identifier), actor)
            browser_actors[label] = {"username": username, "id": str(identifier), "role": role}
        employee = actors["employee"][1]
        outsider = actors["other_employee"][1]
        service = actors["service"][1]
        customer = manager.create(
            "customers",
            {
                "name": "Synthetic " + attempt,
                "organization": "Example team",
                "contact": "synthetic@example.invalid",
                "category": "企业",
            },
        )
        assert any(str(r["id"]) == customer for r in employee.rows("customers", q=attempt))
        request = employee.create(
            "requests",
            {
                "title": "Synthetic consultation " + attempt,
                "detail": "Need assistance",
                "customer_id": customer,
                "priority": "普通",
                "due_at": "2020-01-01T00:00:00Z",
            },
        )
        # Distinct categories and an unresolved request make the required metric
        # meanings observably different from each other on the live database.
        other_customer = manager.create(
            "customers", {"name": "Comparison " + attempt, "category": "个人"}
        )
        other_request = outsider.create(
            "requests",
            {
                "title": "Unresolved comparison " + attempt,
                "detail": "Control row for scoped operational metrics",
                "customer_id": other_customer,
                "priority": "紧急",
            },
        )
        manager.action(
            "requests", other_request, "assign", {"assignee": actors["other_service"][0]}
        )
        assert not any(str(r["id"]) == request for r in outsider.rows("requests"))
        assert not any(str(r["id"]) == request for r in service.rows("requests"))

        def checked_action(entity, identifier, creator, action, data, transition=None):
            return verify_event_reminders(
                plan,
                entity,
                identifier,
                {"assign": "assigned", "add_note": "note_added", "transition": "transitioned"}[
                    action
                ],
                {"creator": creator, "assignee": service},
                [outsider, actors["other_service"][1]],
                lambda: (manager if action == "assign" else service).action(
                    entity, identifier, action, data
                ),
                transition,
            )

        checked_action("requests", request, employee, "assign", {"assignee": actors["service"][0]})
        assert any(str(r["id"]) == request for r in service.rows("requests"))
        assert not any(str(r["id"]) == request for r in actors["other_service"][1].rows("requests"))
        checked_action(
            "requests", request, employee, "add_note", {"text": "Investigated synthetic request"}
        )
        checked_action(
            "requests", request, employee, "transition", {"transition": "start"}, "start"
        )
        task = manager.create(
            "tasks",
            {
                "title": "Follow-up " + attempt,
                "detail": "Synthetic collaboration",
                "request_id": request,
                "due_at": "2020-01-01T00:00:00Z",
            },
        )
        checked_action("tasks", task, manager, "assign", {"assignee": actors["service"][0]})
        verify_reminders(
            plan,
            [("requests", request, employee, service), ("tasks", task, manager, service)],
            [outsider, actors["other_service"][1]],
        )
        checked_action("tasks", task, manager, "transition", {"transition": "start"}, "start")
        checked_action("tasks", task, manager, "add_note", {"text": "Follow-up complete"})
        checked_action("tasks", task, manager, "transition", {"transition": "resolve"}, "resolve")
        assert any(
            str(row["id"]) == request
            for row in manager.related("customers", customer).get("requests", [])
        ), "Customer service history missing"
        assert any(
            str(row["id"]) == task for row in manager.related("requests", request).get("tasks", [])
        ), "Request collaboration history missing"
        assert not any(
            str(row["id"]) == request
            for row in outsider.related("customers", customer).get("requests", [])
        ), "Related history leaked another employee request"
        checked_action(
            "requests", request, employee, "transition", {"transition": "resolve"}, "resolve"
        )
        verify_handling_history(plan, manager, service, employee, outsider, "requests", request)
        inbox = employee.inbox()
        assert any(
            str(row["record_id"]) == request and notice_event(row) == "transitioned"
            for row in inbox
        ), "Resolution reminder missing"
        metrics = verify_scoped_metrics(manager, plan, "manager")
        verify_scoped_metrics(service, plan, "service")
        verify_scoped_metrics(actors["other_service"][1], plan, "service")
        assert employee.call("GET", employee.prefix + "/metrics") == [], (
            "Employee must not access team metrics"
        )
        assert {item.name for item in plan.business.metrics} <= {item["name"] for item in metrics}
        return {
            "passed": True,
            "spec_digest": digest(plan.model_dump()),
            "real_native_auth": True,
            "public_native_registration": True,
            "three_roles": True,
            "relations": True,
            "related_history": True,
            "assignment": True,
            "transitions": True,
            "handling_history": True,
            "audit": True,
            "in_app_reminders": True,
            "due_reminders": True,
            "note_reminders": True,
            "status_change_reminders": True,
            "reminder_read_isolation": True,
            "metrics": True,
            "row_isolation": True,
            "records": {"customers": customer, "requests": request, "tasks": task},
            "synthetic_accounts": len(actors),
            "attempt": attempt,
            "browser_actors": browser_actors,
            "targets": targets,
        }
    finally:
        for client in clients:
            client.close()


def assert_history_denied(client, entity, identifier):
    # Both native wire protocols must deny the API call, not merely hide its UI.
    forbidden = (
        client.http.get(f"{client.prefix}/{entity}/{identifier}/history")
        if client.fastapi
        else client.http.get(
            client.prefix + "/history", params={"entity": entity, "id": identifier}
        )
    )
    if forbidden.status_code not in {401, 403, 404}:
        try:
            refused_code = forbidden.json().get("code")
        except ValueError:
            refused_code = None
        assert refused_code in {401, 403, 404}, "Unpermitted actor read handling history"


def verify_handling_history(plan, manager, service, employee, outsider, entity, identifier):
    # The public contract guarantees assigned service history and manager audit.
    # An employee's read grant does not implicitly grant read_history.
    history = service.history(entity, identifier)
    assert len(history) >= 4, "Handling timeline omitted actions"
    audit = manager.history(entity, identifier, True)
    assert len(audit) >= len(history), "Audit trail omitted history"
    employee_history = any(
        grant.role == "employee" and grant.entity == entity and "read_history" in grant.actions
        for grant in plan.business.permissions
    )
    if employee_history:
        assert len(employee.history(entity, identifier)) >= len(history), (
            "Employee handling history omitted permitted actions"
        )
    else:
        assert_history_denied(employee, entity, identifier)
    assert_history_denied(outsider, entity, identifier)


def notice_event(row):
    return row.get("event") or row.get("message", "").rsplit(" ", 1)[-1]


def record_notices(client, entity, identifier, event):
    return {
        str(row["id"]): row
        for row in client.inbox()
        if row["entity"] == entity
        and str(row["record_id"]) == str(identifier)
        and notice_event(row) == event
    }


def reminder_recipients(plan, entity, event, recipients, transition=None):
    # Only resolve→request creator is fixed by the public contract. All other
    # recipients come from the approved plan, not an implicit test preference.
    return {
        recipients[notice.recipient]
        for notice in plan.business.notifications
        if notice.entity == entity and notice.event == event and notice.transition == transition
    }


def verify_event_reminders(
    plan, entity, identifier, event, recipients, outsiders, action, transition=None
):
    """Prove every declared notification comes from this action to its intended inbox."""
    expected = reminder_recipients(plan, entity, event, recipients, transition)
    clients = set(recipients.values()) | set(outsiders)
    before = {client: record_notices(client, entity, identifier, event) for client in clients}
    result = action()
    for client in clients:
        after = record_notices(client, entity, identifier, event)
        added = set(after) - set(before[client])
        assert len(added) == int(client in expected), (
            f"{entity} {event} {transition or ''} reminder missing, duplicated or misrouted"
        )
        assert set(record_notices(client, entity, identifier, event)) == set(after), (
            "Reading reminders generated duplicate notifications"
        )
        for notice_id in added:
            payload(client.read_notice(notice_id))
            updated = record_notices(client, entity, identifier, event)[notice_id]
            assert updated.get("read") is True or updated.get("read_at") is not None, (
                "Read state not persisted"
            )
            for other in clients - {client}:
                forbidden = other.read_notice(notice_id)
                assert forbidden.status_code in {401, 403, 404} or forbidden.json().get("code") in {
                    401,
                    403,
                    404,
                }, "Other recipient changed reminder read state"
    return result


def verify_reminders(plan, records, outsiders):
    """Check assignment/due routing, idempotency and recipient-private read persistence."""
    for entity, identifier, creator, assignee in records:
        recipients = {"creator": creator, "assignee": assignee}
        clients = set(recipients.values()) | set(outsiders)
        for event in ("assigned", "due"):
            expected = reminder_recipients(plan, entity, event, recipients)
            for client in clients:
                notices = record_notices(client, entity, identifier, event)
                assert len(notices) == int(client in expected), (
                    f"{entity} {event} reminder missing, duplicated or misrouted"
                )
                assert set(record_notices(client, entity, identifier, event)) == set(notices), (
                    "Reading reminders generated duplicate notifications"
                )
                if not notices:
                    continue
                notice = next(iter(notices.values()))
                payload(client.read_notice(notice["id"]))
                updated = record_notices(client, entity, identifier, event)[str(notice["id"])]
                assert updated.get("read") is True or updated.get("read_at") is not None, (
                    "Read state not persisted"
                )
                for other in clients - {client}:
                    forbidden = other.read_notice(notice["id"])
                    assert forbidden.status_code in {401, 403, 404} or forbidden.json().get(
                        "code"
                    ) in {
                        401,
                        403,
                        404,
                    }, "Other recipient changed reminder read state"


def verify_scoped_metrics(client, plan, role="manager"):
    """Compare HTTP aggregates with independently counted visible rows, including values."""
    from collections import Counter
    from datetime import datetime, timezone

    results = client.call("GET", client.prefix + "/metrics")
    by_name = {item["name"]: item for item in results}
    expected = {
        metric.name
        for metric in plan.business.metrics
        if any(
            grant.role == role and grant.entity == metric.entity and "read_metrics" in grant.actions
            for grant in plan.business.permissions
        )
    }
    assert set(by_name) == expected and len(by_name) == len(results), (
        "Metric set differs from the role's approved permissions"
    )
    for metric in plan.business.metrics:
        if metric.name not in by_name:
            continue
        rows = client.rows(metric.entity, page_size=100, pageSize=100)

        def value(row, field):
            return row.get(wire_name(client.template, field))

        def moment(value):
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return (
                parsed.replace(tzinfo=timezone.utc)
                if parsed.tzinfo is None
                else parsed.astimezone(timezone.utc)
            )

        def matches(row):
            for rule in metric.filters:
                actual = value(row, rule.field)
                if rule.op == "eq" and actual != rule.value:
                    return False
                if rule.op == "ne" and actual == rule.value:
                    return False
                if rule.op == "in" and actual not in rule.value:
                    return False
                if rule.op == "gte" and (actual is None or actual < rule.value):
                    return False
                if rule.op == "lte" and (actual is None or actual > rule.value):
                    return False
            return True

        rows = [row for row in rows if matches(row)]
        result = by_name[metric.name]
        if isinstance(result.get("value"), dict):
            result = result["value"]
        if metric.kind == "count":
            assert type(result["value"]) is int and result["value"] == len(rows), (
                "Metric count differs from authorized rows"
            )
        elif metric.kind == "average_duration":
            samples = [
                (
                    moment(value(row, metric.end_field)) - moment(value(row, metric.start_field))
                ).total_seconds()
                for row in rows
                if value(row, metric.end_field) and value(row, metric.start_field)
            ]
            assert type(result["samples"]) is int and result["samples"] == len(samples)
            if samples:
                assert abs(result["value"] - sum(samples) / len(samples)) < 0.01
            else:
                assert result["value"] is None
        else:
            counts = Counter(
                str(value(row, metric.group_by))
                if metric.kind == "group_count"
                else moment(value(row, metric.time_field)).date().isoformat()
                for row in rows
            )
            actual = result.get("buckets")
            if actual is None:
                actual = {
                    str(group.get("key", group.get("day"))): group["count"]
                    for group in result["groups"]
                }
            assert all(type(value) is int for value in actual.values()) and actual == dict(
                counts
            ), "Metric buckets differ from authorized rows"
    return results
