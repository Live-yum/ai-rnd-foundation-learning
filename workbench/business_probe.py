"""Independent customer-service acceptance over real native HTTP authentication."""

import uuid

import httpx

from workbench.native_checks import payload, record_id
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

    def role(self, identifier, role):
        if self.fastapi:
            return self.call("PUT", f"{self.prefix}/users/{identifier}/role", json={"role": role})
        return self.call(
            "POST",
            self.prefix + "/roles",
            json={"userId": str(identifier), "role": role, "grant": True},
        )


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
            identifier = record_id(manager.call("POST", prefix + "/system/user/create", json=body))
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
        assert not any(str(r["id"]) == request for r in outsider.rows("requests"))
        assert not any(str(r["id"]) == request for r in service.rows("requests"))
        manager.action("requests", request, "assign", {"assignee": actors["service"][0]})
        assert any(str(r["id"]) == request for r in service.rows("requests"))
        assert not any(str(r["id"]) == request for r in actors["other_service"][1].rows("requests"))
        service.action("requests", request, "add_note", {"text": "Investigated synthetic request"})
        service.action("requests", request, "transition", {"transition": "start"})
        task = manager.create(
            "tasks",
            {
                "title": "Follow-up " + attempt,
                "detail": "Synthetic collaboration",
                "request_id": request,
                "due_at": "2020-01-01T00:00:00Z",
            },
        )
        manager.action("tasks", task, "assign", {"assignee": actors["service"][0]})
        service.action("tasks", task, "transition", {"transition": "start"})
        service.action("tasks", task, "add_note", {"text": "Follow-up complete"})
        service.action("tasks", task, "transition", {"transition": "resolve"})
        service.action("requests", request, "transition", {"transition": "resolve"})
        history = employee.history("requests", request)
        assert len(history) >= 4, "Handling timeline omitted actions"
        audit = manager.history("requests", request, True)
        assert len(audit) >= len(history), "Audit trail omitted history"
        inbox = employee.call(
            "GET", employee.prefix + ("/inbox" if employee.fastapi else "/notifications")
        )
        assert any(str(row["record_id"]) == request for row in inbox), "Resolution reminder missing"
        metrics = manager.call("GET", manager.prefix + "/metrics")
        assert {item.name for item in plan.business.metrics} <= {item["name"] for item in metrics}
        # Authorization must be enforced on the API, not merely hidden in native UI.
        forbidden = (
            outsider.http.get(
                outsider.prefix + "/history", params={"entity": "requests", "id": request}
            )
            if not outsider.fastapi
            else outsider.http.get(f"{outsider.prefix}/requests/{request}/history")
        )
        if forbidden.status_code not in {401, 403, 404}:
            try:
                refused_code = forbidden.json().get("code")
            except ValueError:
                refused_code = None
            assert refused_code in {401, 403, 404}, "Outsider read another employee history"
        return {
            "passed": True,
            "real_native_auth": True,
            "three_roles": True,
            "relations": True,
            "assignment": True,
            "transitions": True,
            "handling_history": True,
            "audit": True,
            "in_app_reminders": True,
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
