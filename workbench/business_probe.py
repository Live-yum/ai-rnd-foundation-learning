"""Independent customer-service acceptance over real native HTTP authentication."""

import hashlib
import json
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

    def create_response(self, entity, data):
        route = (
            self.prefix + "/" + entity + "/create"
            if self.fastapi
            else self.targets[entity]["api"] + "/create"
        )
        return self.http.post(route, json=data if self.fastapi else self.wire(data))

    def create(self, entity, data):
        value = payload(self.create_response(entity, data))
        return str(value["id"] if isinstance(value, dict) else value)

    def rows(self, entity, **query):
        # Shared probes used to supply both dialects and rely on a server
        # silently ignoring foreign keys. Send only this native API's keys.
        for aliases, native in (
            (("page_size", "pageSize"), "page_size" if self.fastapi else "pageSize"),
            (("page", "pageNo"), "page" if self.fastapi else "pageNo"),
        ):
            supplied = [query.pop(key) for key in aliases if key in query]
            if supplied:
                if len({str(value) for value in supplied}) != 1:
                    raise ValueError("Conflicting native pagination aliases")
                query[native] = supplied[0]
        route = (
            self.prefix + "/" + entity + "/list" if self.fastapi else self.targets[entity]["list"]
        )
        value = self.call("GET", route, params=query)
        return value.get("items", value.get("list"))

    def all_rows(self, entity, *, q="", filters=None):
        """Read the complete bounded result; a first page is never an exact-set oracle."""
        route = (
            self.prefix + "/" + entity + "/list" if self.fastapi else self.targets[entity]["list"]
        )
        filters = filters or {}
        query = {"q": q} if q else {}
        if self.fastapi:
            query["filters"] = json.dumps(filters, ensure_ascii=False)
        else:
            for name, value in filters.items():
                suffix = next((s for s in ("_from", "_to") if name.endswith(s)), "")
                field = name[: -len(suffix)] if suffix else name
                query[wire_name(self.template, field) + suffix] = (
                    str(value).lower() if type(value) is bool else value
                )
        rows, total = [], None
        for page in range(1, 102):
            pagination = (
                {"page": page, "page_size": 100}
                if self.fastapi
                else {"pageNo": page, "pageSize": 100}
            )
            result = self.call("GET", route, params={**query, **pagination})
            batch = result.get("items", result.get("list"))
            count = result.get("total")
            assert isinstance(batch, list) and type(count) is int and 0 <= count <= 10000, (
                "Native list omitted bounded total/rows"
            )
            if total is None:
                total = count
            assert count == total, "Native list changed during exact-set pagination"
            rows.extend(batch)
            assert len(rows) <= total and len({str(r["id"]) for r in rows}) == len(rows), (
                "Native pagination duplicated or overcounted rows"
            )
            if len(rows) == total:
                return rows
            assert len(batch) == 100, "Native list silently truncated an exact-set result"
        raise AssertionError("Native list exceeded explicit 10000-row bound")

    def action(self, entity, identifier, action, data):
        return payload(self.action_response(entity, identifier, action, data))

    def action_response(self, entity, identifier, action, data):
        """Keep the real native response available for negative authorization probes."""
        if self.fastapi:
            return self.http.post(f"{self.prefix}/{entity}/{identifier}/{action}", json=data)
        if action == "update":
            return self.http.put(
                self.targets[entity]["api"] + "/update", json={"id": identifier, **self.wire(data)}
            )
        value = {"entity": entity, "id": identifier, "action": action}
        value.update(
            {
                "assigneeId" if k == "assignee" else "note" if k == "text" else k: v
                for k, v in data.items()
            }
        )
        return self.http.post(self.prefix + "/action", json=value)

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
    execution_evidence = {
        "version": 1,
        "spec_digest": digest(plan.model_dump()),
        "reminders": [],
        "metrics": [],
        "metric_denials": [],
        "audit": [],
        "related_acl": [],
        "relation_writes": [],
        "field_queries": [],
    }
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
                execution_evidence["reminders"],
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
            execution_evidence["reminders"],
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
        metrics = verify_scoped_metrics(manager, plan, "manager", "manager", execution_evidence)
        for label, (_, client) in actors.items():
            verify_scoped_metrics(
                client, plan, label.removeprefix("other_"), label, execution_evidence
            )
        assert {item.name for item in plan.business.metrics} <= {item["name"] for item in metrics}
        verify_created_reminders(
            plan,
            [
                ("customers", customer, manager),
                ("requests", request, employee),
                ("tasks", task, manager),
            ],
            clients,
            execution_evidence["reminders"],
        )
        assignment_boundaries = verify_assignment_boundaries(
            plan, manager, actors, {"requests": request, "tasks": task}
        )
        from workbench.native_business_probe import verify_native_execution

        verify_native_execution(
            plan,
            manager,
            actors,
            {
                "customers": customer,
                "requests": request,
                "tasks": task,
            },
            execution_evidence,
        )
        navigation = None
        if template == "yudao-vben":
            from workbench.yudao_navigation_checks import check_installed_navigation

            navigation = check_installed_navigation(plan, manager, actors)
        return {
            "passed": True,
            "execution_evidence": execution_evidence,
            "installed_navigation": navigation,
            "spec_digest": digest(plan.model_dump()),
            "real_native_auth": True,
            "public_native_registration": True,
            "three_roles": True,
            "relations": True,
            "related_history": True,
            "assignment": True,
            "assignment_boundaries": assignment_boundaries,
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


def verify_assignment_boundaries(plan, manager, actors, records):
    """Exercise only existing actors and grants from this exact approved Plan.

    Run after reminder cardinality checks: the conditional positive assignment is
    restored, but its legitimate audit/notification events must remain persisted.
    """
    approved_digest = digest(plan.model_dump())
    grants = {(p.role, p.entity): p for p in plan.business.permissions}
    roster = [
        (label, label.removeprefix("other_"), str(identifier), client)
        for label, (identifier, client) in actors.items()
    ]
    clients = [manager, *(actor[3] for actor in roster)]
    checks = []
    mutations = {"create", "update", "archive", "assign", "transition", "add_note"}

    def read_grant(role, entity):
        grant = grants.get((role, entity))
        return grant if grant and "read" in grant.actions else None

    def row(client, entity, identifier):
        found = [
            item
            for item in client.rows(entity, page_size=100, pageSize=100)
            if str(item["id"]) == str(identifier)
        ]
        assert len(found) == 1, "Assigned record missing from authorized HTTP rows"
        return found[0]

    def visible(grant, actor_id, record, assignee_field):
        if grant is None:
            return False
        return (
            grant.scope == "all"
            or str(
                record.get(
                    wire_name(manager.template, "created_by")
                    if grant.scope == "own"
                    else assignee_field
                )
            )
            == actor_id
        )

    def snapshot(entity, identifier):
        return {
            "row": row(manager, entity, identifier),
            "audit": manager.history(entity, identifier, True),
            "notifications": [
                [
                    notice
                    for notice in client.inbox()
                    if notice["entity"] == entity and str(notice["record_id"]) == str(identifier)
                ]
                for client in clients
            ],
        }

    def absent(entity, case, reason):
        checks.append({"entity": entity, "case": case, "status": "absent", "reason": reason})

    def rejected(entity, identifier, case, actor, recipient, statuses, action="assign", data=None):
        before = snapshot(entity, identifier)
        response = actor[3].action_response(
            entity, identifier, action, {"assignee": recipient[2]} if data is None else data
        )
        try:
            code = response.json().get("code")
        except ValueError, AttributeError:
            code = None
        # Native application codes are bounded integers. Never echo arbitrary
        # response strings, bodies, headers, or credentials in failure reports.
        if type(code) is not int or not -(2**31) <= code < 2**31:
            code = None
        assert response.status_code in statuses or (
            response.status_code == 200 and code in statuses
        ), (
            f"{case}: native assignment was accepted, crashed, or failed for an unrelated reason "
            f"(entity={entity}, http_status={response.status_code}, response_code={code})"
        )
        after = snapshot(entity, identifier)
        assert after == before, f"{case}: rejected assignment changed row, audit, or notifications"
        checks.append(
            {
                "entity": entity,
                "case": case,
                "status": "exercised",
                "action": action,
                "actor_role": actor[1],
                **(
                    {
                        "assignee_role": next(
                            item[1]
                            for item in roster
                            if item[2] == str(recipient[2] if data is None else data["assignee"])
                        )
                    }
                    if action == "assign"
                    else {}
                ),
                "http_status": response.status_code,
                "response_code": code,
                "row_audit_notifications_unchanged": True,
            }
        )

    for entity, identifier in records.items():
        resource = next(item for item in plan.business.resources if item.entity == entity)
        assignee_field = wire_name(manager.template, resource.assignee_field)
        baseline = row(manager, entity, identifier)
        assigning_actor = ("manager", "manager", "", manager)
        eligible = [
            actor
            for actor in roster
            if (grant := read_grant(actor[1], entity)) and grant.scope in {"assigned", "all"}
        ]
        assert eligible, "No existing approved assignee for assignment boundary probes"
        for case, candidates in (
            (
                "own_only_assignee_denied",
                [
                    actor
                    for actor in roster
                    if (grant := read_grant(actor[1], entity)) and grant.scope == "own"
                ],
            ),
            (
                "no_read_assignee_denied",
                [actor for actor in roster if read_grant(actor[1], entity) is None],
            ),
        ):
            if candidates:
                rejected(entity, identifier, case, assigning_actor, candidates[0], {400, 422})
            else:
                absent(entity, case, "No existing actor has this approved read-permission boundary")

        unauthorized = [
            actor
            for actor in roster
            if not (grant := grants.get((actor[1], entity))) or "assign" not in grant.actions
        ]
        if unauthorized:
            # Prefer a visible row, so denial proves the action gate independently
            # of the row-scope gate whenever the approved actors allow it.
            unauthorized.sort(
                key=lambda actor: (
                    not visible(read_grant(actor[1], entity), actor[2], baseline, assignee_field)
                )
            )
            rejected(
                entity, identifier, "unauthorized_actor_denied", unauthorized[0], eligible[0], {403}
            )
        else:
            absent(entity, "unauthorized_actor_denied", "Every existing actor has approved assign")

        foreign = [
            actor
            for actor in roster
            if (grant := grants.get((actor[1], entity)))
            and "assign" in grant.actions
            and grant.scope in {"own", "assigned"}
            and not visible(grant, actor[2], baseline, assignee_field)
        ]
        if foreign:
            rejected(entity, identifier, "foreign_row_denied", foreign[0], eligible[0], {403, 404})
        else:
            absent(
                entity,
                "foreign_row_denied",
                "No existing approved own/assigned assign actor is outside this row's scope",
            )

        readonly = [
            actor
            for actor in eligible
            if not mutations.intersection(grants[actor[1], entity].actions)
        ]
        if not readonly:
            absent(
                entity,
                "read_only_recipient_accepted",
                "No existing actor has approved read-only assigned/all permission",
            )
            continue
        recipient = readonly[0]
        original_assignee = baseline[assignee_field]
        assert original_assignee is not None, (
            "Assignment restoration requires the existing assignee"
        )
        manager.action(entity, identifier, "assign", {"assignee": recipient[2]})
        try:
            assert str(row(manager, entity, identifier)[assignee_field]) == recipient[2], (
                "Read-only recipient assignment did not persist"
            )
            assert str(row(recipient[3], entity, identifier)[assignee_field]) == recipient[2], (
                "Read-only assigned/all recipient cannot read their assigned row"
            )
            workflow = next(item for item in plan.business.workflows if item.entity == entity)
            for action, data in (
                ("assign", {"assignee": original_assignee}),
                ("update", {"title": baseline["title"]}),
                ("transition", {"transition": workflow.transitions[0].name}),
            ):
                rejected(
                    entity,
                    identifier,
                    "read_only_recipient_" + action + "_denied",
                    recipient,
                    recipient,
                    {403},
                    action,
                    data,
                )
            peers = [actor for actor in roster if actor[1] == recipient[1] and actor != recipient]
            isolation = {
                "status": "absent",
                "reason": "Approved all scope allows peer reads or no same-role peer exists",
            }
            if peers and grants[recipient[1], entity].scope == "assigned":
                peer = peers[0][3]
                assert not any(
                    str(item["id"]) == str(identifier)
                    for item in peer.rows(entity, page_size=100, pageSize=100)
                ), "Read-only assignment leaked into another actor's assigned list"
                if peer.fastapi:
                    # Fastapi detail uses list-row data plus the related endpoint;
                    # there is no independent business detail GET route.
                    response = peer.http.get(f"{peer.prefix}/{entity}/{identifier}/related")
                    endpoint = "related"
                else:
                    response = peer.http.get(
                        peer.targets[entity]["api"] + "/get", params={"id": identifier}
                    )
                    endpoint = "get"
                assert response.status_code in {403, 404} or (
                    response.status_code == 200 and response.json().get("code") in {403, 404}
                ), "Read-only assignment leaked through direct record access"
                isolation = {
                    "status": "exercised",
                    "list_denied": True,
                    "record_endpoint": endpoint,
                }
        finally:
            manager.action(entity, identifier, "assign", {"assignee": str(original_assignee)})
        assert str(row(manager, entity, identifier)[assignee_field]) == str(original_assignee), (
            "Original assignee was not restored for subsequent native browser acceptance"
        )
        checks.append(
            {
                "entity": entity,
                "case": "read_only_recipient_accepted",
                "status": "exercised",
                "actor_role": "manager",
                "assignee_role": recipient[1],
                "assignee_scope": grants[recipient[1], entity].scope,
                "persisted_and_recipient_readable": True,
                "original_assignee_restored": True,
                "peer_isolation": isolation,
            }
        )
    assert digest(plan.model_dump()) == approved_digest, (
        "Assignment probe changed the approved Plan"
    )
    return {"version": 1, "spec_digest": approved_digest, "checks": checks}


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
    plan, entity, identifier, event, recipients, outsiders, action, transition=None, evidence=None
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
    if evidence is not None:
        for notice in plan.business.notifications:
            if (notice.entity, notice.event, notice.transition) == (entity, event, transition):
                recipient = recipients[notice.recipient]
                added = set(record_notices(recipient, entity, identifier, event)) - set(
                    before[recipient]
                )
                append_reminder_evidence(evidence, notice, len(added))
    return result


def verify_created_reminders(plan, records, clients, evidence):
    """Creation receipts inspect only freshly created owned IDs and their inboxes."""
    for entity, identifier, creator in records:
        rules = [
            n for n in plan.business.notifications if n.entity == entity and n.event == "created"
        ]
        if not rules:
            continue
        # Native creation deliberately clears assignee; a created-to-assignee rule
        # cannot demonstrate delivery without a real recipient and stays blocked.
        assert all(n.recipient == "creator" for n in rules), (
            "Created reminder has no recipient before the separate assignment action"
        )
        for client in set(clients):
            notices = record_notices(client, entity, identifier, "created")
            assert len(notices) == int(client is creator), (
                "Creation reminder was omitted or misrouted"
            )
            assert record_notices(client, entity, identifier, "created") == notices, (
                "Creation reminder duplicated on read"
            )
            for notice_id in notices:
                payload(client.read_notice(notice_id))
                updated = record_notices(client, entity, identifier, "created")[notice_id]
                assert updated.get("read") is True or updated.get("read_at") is not None
                for other in set(clients) - {client}:
                    response = other.read_notice(notice_id)
                    assert response.status_code in {401, 403, 404} or response.json().get(
                        "code"
                    ) in {401, 403, 404}, "Creation reminder read state leaked"
        for notice in rules:
            append_reminder_evidence(
                evidence, notice, len(record_notices(creator, entity, identifier, "created"))
            )


def append_reminder_evidence(evidence, notice, observed):
    key = {
        "entity": notice.entity,
        "event": notice.event,
        "transition": notice.transition,
        "recipient": notice.recipient,
    }
    found = next((item for item in evidence if all(item[k] == v for k, v in key.items())), None)
    if found is None:
        evidence.append(
            {
                **key,
                "expected_count": 1,
                "observed_count": observed,
                "idempotent": True,
                "read_persisted": True,
                "foreign_read_denied": True,
                "outsider_count": 0,
            }
        )
    else:
        found["expected_count"] += 1
        found["observed_count"] += observed


def verify_reminders(plan, records, outsiders, evidence=None):
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
            if evidence is not None and event == "due":
                for notice in plan.business.notifications:
                    if (notice.entity, notice.event) == (entity, event):
                        observed = len(
                            record_notices(recipients[notice.recipient], entity, identifier, event)
                        )
                        append_reminder_evidence(evidence, notice, observed)


def verify_scoped_metrics(client, plan, role="manager", actor=None, evidence=None):
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
    if not expected and evidence is not None:
        evidence["metric_denials"].append(
            {"role": role, "actor": actor or role, "observed_count": len(results)}
        )
    for metric in plan.business.metrics:
        if metric.name not in by_name:
            continue
        rows = (
            client.all_rows(metric.entity)
            if hasattr(client, "all_rows")
            else client.rows(metric.entity, page_size=100, pageSize=100)
        )
        visible_count = len(rows)

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
        expected_value = {"value": None, "samples": None, "buckets": []}
        observed_value = dict(expected_value)
        if metric.kind == "count":
            assert type(result["value"]) is int and result["value"] == len(rows), (
                "Metric count differs from authorized rows"
            )
            expected_value["value"] = len(rows)
            observed_value["value"] = result["value"]
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
            expected_value.update(
                value=sum(samples) / len(samples) if samples else None, samples=len(samples)
            )
            observed_value.update(value=result["value"], samples=result["samples"])
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

            def bounded_buckets(values):
                return sorted(
                    [
                        {"key_sha256": hashlib.sha256(key.encode()).hexdigest(), "count": count}
                        for key, count in values.items()
                    ],
                    key=lambda item: item["key_sha256"],
                )

            expected_value["buckets"] = bounded_buckets(counts)
            observed_value["buckets"] = bounded_buckets(actual)
        if evidence is not None:
            scope = next(
                p.scope
                for p in plan.business.permissions
                if p.role == role and p.entity == metric.entity and "read_metrics" in p.actions
            )
            evidence["metrics"].append(
                {
                    "name": metric.name,
                    "role": role,
                    "actor": actor or role,
                    "scope": scope,
                    "kind": metric.kind,
                    "visible_count": visible_count,
                    "expected": expected_value,
                    "observed": observed_value,
                }
            )
    return results
