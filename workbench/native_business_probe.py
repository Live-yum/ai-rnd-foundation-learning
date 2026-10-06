"""Executed native HTTP query, relation and append-only-history acceptance.

The oracle reads complete unfiltered manager rows, then independently applies the
approved grants and field predicates. It never derives expected results from the
query under test. Only counts and audit hashes leave this probe.
"""

from datetime import UTC, date, datetime

from workbench.business_probe import wire_name
from workbench.domain import digest

ACTORS = ("manager", "employee", "other_employee", "service", "other_service")


def refused(response, codes):
    try:
        code = response.json().get("code")
    except ValueError, AttributeError:
        code = None
    assert response.status_code in codes or (
        response.status_code == 200 and type(code) is int and code in codes
    ), "Native negative probe was accepted or failed for an unrelated reason"


class NativeOracle:
    def __init__(self, plan, manager, actors, records):
        self.plan, self.manager, self.records = plan, manager, records
        self.entities = {e.name: e for e in plan.entities}
        self.resources = {r.entity: r for r in plan.business.resources}
        self.grants = {(g.role, g.entity): g for g in plan.business.permissions}
        self.workflows = {w.entity: w for w in plan.business.workflows}
        self.relations = {(r.entity, r.field): r for r in plan.business.relations}
        state = manager.call(
            "GET", manager.prefix + ("/configuration" if manager.fastapi else "/me")
        )
        manager_id = state["actor"]["id"] if manager.fastapi else state["id"]
        self.actors = {"manager": (str(manager_id), manager), **actors}
        assert set(self.actors) == set(ACTORS), "Native execution requires all five real identities"
        self.controls = {}
        self.rows = {}
        for entity in self.entities:
            grant = self.grants.get(("manager", entity))
            assert grant and "read" in grant.actions and grant.scope == "all", (
                "Exact-set oracle requires an approved all-row manager read grant"
            )

    def normalized(self, row):
        fields = {f.name for e in self.entities.values() for f in e.fields}
        fields.update({"id", "created_by", "created_at", "updated_at", "archived_at"})
        return {
            name: row.get(wire_name(self.manager.template, name))
            for name in fields
            if wire_name(self.manager.template, name) in row
        }

    def all_rows(self, client, entity, **query):
        return [self.normalized(r) for r in client.all_rows(entity, **query)]

    def refresh(self, entity):
        self.rows[entity] = self.all_rows(self.manager, entity)
        return self.rows[entity]

    def allowed(self, label, entity, action, row=None):
        role = label.removeprefix("other_")
        grant = self.grants.get((role, entity))
        if not grant or action not in grant.actions:
            return False
        if row is None:
            return grant.scope == "all" or action == "create" and grant.scope == "own"
        if grant.scope == "all":
            return True
        field = "created_by" if grant.scope == "own" else self.resources[entity].assignee_field
        return str(row.get(field)) == self.actors[label][0]

    def row(self, entity, identifier):
        found = [r for r in self.refresh(entity) if str(r["id"]) == str(identifier)]
        assert len(found) == 1, "Owned native control disappeared"
        return found[0]

    def sample(self, entity, side=0, parent_values=None):
        values = {}
        workflow = self.workflows.get(entity)
        protected = {self.resources[entity].assignee_field}
        if workflow:
            protected.add(workflow.status_field)
            protected.update(t.set_timestamp for t in workflow.transitions)
        for index, field in enumerate(self.entities[entity].fields):
            if field.name in protected:
                continue
            relation = self.relations.get((entity, field.name))
            if relation:
                if relation.target_entity == "$users":
                    continue
                values[field.name] = (parent_values or {}).get(
                    field.name, self.records[relation.target_entity]
                )
            elif field.kind == "text":
                # The target-field marker is absent from every other searchable
                # field. Proper substrings distinguish icontains from equality.
                marker = "v" + digest([entity, field.name, side])[:14] + "z"
                if field.max_length < len(marker):
                    marker = chr(0x4E00 + index * 2 + side)
                values[field.name] = marker.ljust(max(1, field.min_length), "x")[: field.max_length]
            elif field.kind == "enum":
                values[field.name] = field.choices[min(side, len(field.choices) - 1)]
            elif field.kind == "boolean":
                values[field.name] = bool(side)
            elif field.kind == "integer":
                from templates.product.fields import integer_bounds

                low, high = integer_bounds(field.model_dump())
                values[field.name] = max(low, min(41 + side, high))
            elif field.kind == "date":
                values[field.name] = f"2098-02-0{side + 1}"
            elif field.kind == "datetime":
                # Future dates keep query controls out of due-notification tests.
                values[field.name] = f"2098-02-0{side + 1}T12:00:00Z"
        return values

    def seed_queries(self):
        for entity in self.entities:
            for label, (_, client) in self.actors.items():
                grant = self.grants.get((label.removeprefix("other_"), entity))
                if not grant or "read" not in grant.actions:
                    continue
                if grant.scope == "all" and label != "manager":
                    continue
                creator = label if grant.scope == "own" else "manager"
                if not self.allowed(creator, entity, "create"):
                    # Own/read-only means genuinely empty own data; never expand
                    # the Plan or forge created_by just to manufacture a fixture.
                    continue
                for side in (0, 1):
                    sample = self.sample(entity, side)
                    # Required parent reads also stay inside the creator's grant.
                    for relation in self.plan.business.relations:
                        if relation.entity != entity or relation.target_entity == "$users":
                            continue
                        target_rows = self.refresh(relation.target_entity)
                        candidates = [
                            r
                            for r in target_rows
                            if self.allowed(creator, relation.target_entity, "read", r)
                        ]
                        assert candidates, "Approved query creator has no readable relation target"
                        sample[relation.field] = str(candidates[0]["id"])
                    identifier = self.actors[creator][1].create(entity, sample)
                    row = self.row(entity, identifier)
                    if grant.scope == "assigned":
                        assigner = next(
                            (a for a in self.actors if self.allowed(a, entity, "assign", row)), None
                        )
                        assert assigner, "Assigned query fixture has no approved assigning actor"
                        self.actors[assigner][1].action(
                            entity, identifier, "assign", {"assignee": self.actors[label][0]}
                        )
                        row = self.row(entity, identifier)
                    workflow = self.workflows.get(entity)
                    if side and workflow:
                        transition = next(
                            (
                                t
                                for t in workflow.transitions
                                if row[workflow.status_field] in t.from_states
                            ),
                            None,
                        )
                        handler = next(
                            (
                                a
                                for a in self.actors
                                if transition
                                and a.removeprefix("other_") in transition.roles
                                and self.allowed(a, entity, "transition", row)
                            ),
                            None,
                        )
                        if handler:
                            self.actors[handler][1].action(
                                entity, identifier, "transition", {"transition": transition.name}
                            )
                            row = self.row(entity, identifier)
                    self.controls[entity, label, side] = row
            self.refresh(entity)

    def history_response(self, label, entity, identifier, method="GET", **kwargs):
        client = self.actors[label][1]
        route = (
            f"{client.prefix}/{entity}/{identifier}/history"
            if client.fastapi
            else client.prefix + "/history"
        )
        return client.http.request(
            method, route, params={"entity": entity, "id": identifier, "audit": "true"}, **kwargs
        )


def verify_audit_mutations(oracle, evidence):
    for entity, identifier in oracle.records.items():
        for method, mutation in (("PUT", "update"), ("DELETE", "delete")):
            before = oracle.manager.history(entity, identifier, True)
            assert before, "Audit mutation test requires a persisted existing event"
            # Address the actual, GET-verified history resource, including an
            # existing event ID. Do not invent an endpoint that never existed.
            response = oracle.history_response(
                "manager",
                entity,
                identifier,
                method,
                json={
                    "id": str(before[0]["id"]),
                    "event": "probe_changed",
                    "note": "probe_changed",
                },
            )
            refused(response, {403, 405})
            after = oracle.manager.history(entity, identifier, True)
            assert before == after, "Rejected audit mutation changed an existing event"
            evidence.append(
                {
                    "entity": entity,
                    "mutation": mutation,
                    "transport": "http",
                    "denied": True,
                    "before_count": len(before),
                    "after_count": len(after),
                    "unchanged": True,
                    "before_sha256": digest(before),
                    "after_sha256": digest(after),
                }
            )


def moment(value, kind):
    if kind == "date":
        return date.fromisoformat(str(value))
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    assert parsed.tzinfo is not None, "Native datetime response lost timezone"
    return parsed.astimezone(UTC)


def keyword(value):
    value = str(value or "")
    assert value, "Declared search field lacks a nonempty query control"
    return (value[1:-1] if len(value) > 2 else value[:1]).upper()


def matches_query(definition, row, q="", filters=None):
    fields = {f.name: f for f in definition.fields}
    if q and not any(
        q.casefold() in str(row.get(f.name) or "").casefold()
        for f in fields.values()
        if f.searchable
    ):
        return False
    for name, value in (filters or {}).items():
        suffix = next((s for s in ("_from", "_to") if name.endswith(s)), "")
        field = fields[name[: -len(suffix)] if suffix else name]
        actual = row.get(field.name)
        if suffix:
            if actual is None:
                return False
            actual, bound = moment(actual, field.kind), moment(value, field.kind)
            if suffix == "_from" and actual < bound or suffix == "_to" and actual > bound:
                return False
        elif field.kind in {"date", "datetime"}:
            if actual is None or moment(actual, field.kind) != moment(value, field.kind):
                return False
        elif (
            str(actual).lower() != str(value).lower()
            if field.kind == "boolean"
            else actual != value
        ):
            return False
    return True


def verify_field_queries(oracle, evidence):
    for entity, definition in oracle.entities.items():
        all_rows = oracle.refresh(entity)
        fields = definition.fields
        configured = [
            (f, kind)
            for f in fields
            for kind, enabled in (
                ("search", f.searchable),
                ("exact", f.filterable),
                ("date_range", f.date_range),
            )
            if enabled
        ]
        for label, (_, client) in oracle.actors.items():
            role = label.removeprefix("other_")
            grant = oracle.grants.get((role, entity))
            if not grant or "read" not in grant.actions:
                continue
            visible = [r for r in all_rows if oracle.allowed(label, entity, "read", r)]
            positive = oracle.controls.get(
                (entity, label, 0), oracle.controls[entity, "manager", 0]
            )
            alternate = oracle.controls.get(
                (entity, label, 1), oracle.controls[entity, "manager", 1]
            )
            for field, kind in configured:
                name = field.name
                value, other = positive.get(name), alternate.get(name)
                if kind == "search":
                    term = keyword(value)
                    # Assert the positive fixture isolates this field, not merely
                    # an OR-search hit in a different field with identical text.
                    assert not any(
                        term.casefold() in str(positive.get(f.name) or "").casefold()
                        for f in fields
                        if f.searchable and f.name != name
                    ), "Native query control does not isolate declared search field"
                    pair = [{"q": term}, {"q": "nativeprobeabsent" + digest([entity, name])[:16]}]
                elif kind == "exact":
                    assert value is not None, "Declared exact filter lacks a control"
                    if other == value:
                        if field.kind == "enum":
                            other = next(
                                (choice for choice in field.choices if choice != value), value
                            )
                        elif field.kind == "text":
                            other = "nativeprobeabsent"
                        elif field.kind == "integer":
                            other = value + 1
                        elif field.kind == "boolean":
                            other = not value
                    pair = [{"filters": {name: value}}, {"filters": {name: other}}]
                else:
                    assert value is not None, "Declared date range lacks a legal populated control"
                    # The inclusive equal bounds prove both from and to. An
                    # earlier disjoint day detects silently ignored date filters.
                    missing = "1901-01-01" + ("T00:00:00Z" if field.kind == "datetime" else "")
                    pair = [
                        {"filters": {name + "_from": value, name + "_to": value}},
                        {"filters": {name + "_from": missing, name + "_to": missing}},
                    ]
                cases = [
                    ("positive", pair[0]),
                    ("alternate" if kind == "exact" else "negative", pair[1]),
                ]
                if kind == "date_range" and other is not None and other != value:
                    cases.append(
                        ("alternate", {"filters": {name + "_from": other, name + "_to": other}})
                    )
                if kind == "exact":
                    # Full legal enum values alone cannot distinguish equality
                    # from a buggy substring filter. Use a proper substring that
                    # is absent as an exact value when the domain permits one.
                    partial = None
                    if field.kind in {"text", "enum"} and len(str(value)) > 1:
                        partial = str(value)[:-1]
                    elif field.kind == "integer" and len(str(abs(value))) > 1:
                        partial = int(str(abs(value))[:-1])
                    if partial is not None and not any(r.get(name) == partial for r in all_rows):
                        cases.append(("negative", {"filters": {name: partial}}))
                # Cross a keyword hit with the alternate exact/range value.
                # Correct AND excludes the same positive row; ignoring either
                # operand or implementing OR is observable on the control pair.
                independent = next(
                    (f for f in fields if f.name != name and (f.filterable or f.date_range)), None
                )
                if kind == "search" and independent:
                    if independent.filterable:
                        extra = {independent.name: alternate.get(independent.name)}
                    else:
                        bound = alternate.get(independent.name)
                        extra = {independent.name + "_from": bound, independent.name + "_to": bound}
                    assert all(v is not None for v in extra.values()), (
                        "Combined query lacks a populated independent field"
                    )
                    cases.append(("combination", {"q": pair[0]["q"], "filters": extra}))
                elif kind != "search":
                    search_field = next(
                        (f for f in fields if f.searchable and f.name != name), None
                    )
                    if search_field:
                        cases.append(
                            (
                                "combination",
                                {"q": keyword(positive.get(search_field.name)), **pair[1]},
                            )
                        )
                    elif independent:
                        extra = (
                            {independent.name: alternate.get(independent.name)}
                            if independent.filterable
                            else {
                                independent.name + "_from": alternate.get(independent.name),
                                independent.name + "_to": alternate.get(independent.name),
                            }
                        )
                        cases.append(("combination", {"filters": {**pair[0]["filters"], **extra}}))
                observed_cases = []
                for case, query in cases:
                    expected = {
                        str(r["id"]) for r in visible if matches_query(definition, r, **query)
                    }
                    actual_rows = oracle.all_rows(client, entity, **query)
                    actual = {str(r["id"]) for r in actual_rows}
                    assert actual == expected and len(actual_rows) == len(expected), (
                        f"Native query matrix differs for {label}/{entity}/{name}/{kind}/{case}"
                    )
                    observed_cases.append(
                        {
                            "case": case,
                            "expected_count": len(expected),
                            "observed_count": len(actual_rows),
                            "record_set_equal": True,
                            "expected_sha256": digest(sorted(expected)),
                            "observed_sha256": digest(sorted(actual)),
                        }
                    )
                evidence.append(
                    {
                        "entity": entity,
                        "field": name,
                        "kind": kind,
                        "role": role,
                        "actor": label,
                        "cases": observed_cases,
                    }
                )


def verify_related_acl(oracle, evidence):
    for relation in oracle.plan.business.relations:
        if relation.target_entity == "$users":
            continue
        parent, child = relation.target_entity, relation.entity
        parents, children = oracle.refresh(parent), oracle.refresh(child)
        for label, (_, client) in oracle.actors.items():
            visible = [r for r in parents if oracle.allowed(label, parent, "read", r)]
            foreign = [r for r in parents if not oracle.allowed(label, parent, "read", r)]
            for case, candidates in (("visible_parent", visible), ("foreign_parent", foreign)):
                if not candidates:
                    continue
                # Prefer a populated parent, including hidden children, so an
                # empty unrelated parent cannot stand in for row isolation.
                target = max(
                    candidates,
                    key=lambda p: sum(str(r.get(relation.field)) == str(p["id"]) for r in children),
                )
                identifier = str(target["id"])
                if case == "foreign_parent":
                    route = (
                        f"{client.prefix}/{parent}/{identifier}/related"
                        if client.fastapi
                        else client.prefix + "/related"
                    )
                    response = client.http.get(route, params={"entity": parent, "id": identifier})
                    refused(response, {403, 404})
                    expected_count = observed_count = 0
                else:
                    expected = {
                        str(r["id"])
                        for r in children
                        if str(r.get(relation.field)) == identifier
                        and oracle.allowed(label, child, "read", r)
                    }
                    result = client.related(parent, identifier).get(child, [])
                    actual = {str(r["id"]) for r in result}
                    assert actual == expected and len(result) == len(expected), (
                        "Related native records differ from approved child row scope"
                    )
                    expected_count, observed_count = len(expected), len(result)
                evidence.append(
                    {
                        "parent_entity": parent,
                        "child_entity": child,
                        "field": relation.field,
                        "role": label.removeprefix("other_"),
                        "actor": label,
                        "case": case,
                        "expected_count": expected_count,
                        "observed_count": observed_count,
                        "record_set_equal": True,
                        "parent_denied": case == "foreign_parent",
                    }
                )


def verify_relation_writes(oracle, evidence):
    missing = "2147483646"

    def probe(relation, label, action, case, target, denied, identifier=None):
        entity, client = relation.entity, oracle.actors[label][1]
        before_rows = oracle.refresh(entity)
        before_audit = oracle.manager.history(entity, identifier, True) if identifier else None
        if action == "create":
            data = {**oracle.sample(entity), relation.field: target}
            response = client.create_response(entity, data)
        else:
            data = {"assignee": target} if action == "assign" else {relation.field: target}
            response = client.action_response(entity, identifier, action, data)
        if denied:
            refused(response, {400, 403, 404, 422})
            after_rows = oracle.refresh(entity)
            assert before_rows == after_rows, "Rejected relation write changed native rows"
            if identifier:
                assert oracle.manager.history(entity, identifier, True) == before_audit, (
                    "Rejected relation write changed native audit"
                )
            expected_count = observed_count = 0
        else:
            from workbench.native_checks import payload, record_id

            returned = payload(response)
            changed_id = str(record_id(returned)) if action == "create" else identifier
            persisted = oracle.row(entity, changed_id)
            assert str(persisted.get(relation.field)) == str(target), (
                "Authorized native relation write did not persist requested target"
            )
            expected_count = observed_count = 1
            if action == "create":
                assert len(oracle.rows[entity]) == len(before_rows) + 1
            else:
                assert len(oracle.manager.history(entity, identifier, True)) > len(before_audit), (
                    "Authorized relation write omitted audit"
                )
        evidence.append(
            {
                "entity": entity,
                "field": relation.field,
                "target_entity": relation.target_entity,
                "role": label.removeprefix("other_"),
                "actor": label,
                "action": action,
                "case": case,
                "denied": denied,
                "unchanged": denied,
                "expected_count": expected_count,
                "observed_count": observed_count,
            }
        )

    for relation in oracle.plan.business.relations:
        entity = relation.entity
        baseline = oracle.row(entity, oracle.controls[entity, "manager", 0]["id"])
        targets = (
            [] if relation.target_entity == "$users" else oracle.refresh(relation.target_entity)
        )
        assert all(str(r["id"]) != missing for r in targets), (
            "Missing-target sentinel collides with native row"
        )
        eligible = next(
            (
                label
                for label in oracle.actors
                if (g := oracle.grants.get((label.removeprefix("other_"), entity)))
                and "read" in g.actions
                and g.scope in {"all", "assigned"}
            ),
            None,
        )
        for label in oracle.actors:
            # Every attempted mutation addresses a newly owned test fixture.
            control = oracle.controls.get((entity, label, 0), baseline)
            owned = oracle.row(entity, control["id"])
            identifier = str(owned["id"])
            if relation.target_entity == "$users":
                assert eligible, "No approved readable relation assignee"
                recipient_grant = oracle.grants.get((label.removeprefix("other_"), entity))
                recipient = (
                    label
                    if recipient_grant
                    and "read" in recipient_grant.actions
                    and recipient_grant.scope in {"all", "assigned"}
                    else eligible
                )
                target = oracle.actors[recipient][0]
                if oracle.allowed(label, entity, "assign", owned):
                    original = owned.get(relation.field)
                    probe(relation, label, "assign", "visible_target", target, False, identifier)
                    probe(relation, label, "assign", "missing_target", missing, True, identifier)
                    if original is not None:
                        oracle.manager.action(
                            entity, identifier, "assign", {"assignee": str(original)}
                        )
                else:
                    probe(
                        relation, label, "assign", "unauthorized_action", target, True, identifier
                    )
                for action in ("create", "update"):
                    permitted = oracle.allowed(
                        label, entity, action, None if action == "create" else owned
                    )
                    protected_target = target
                    if action == "update":
                        current = oracle.row(entity, identifier).get(relation.field)
                        protected_target = next(
                            (
                                identity
                                for actor, (identity, _) in oracle.actors.items()
                                if identity != str(current)
                                and (
                                    grant := oracle.grants.get(
                                        (actor.removeprefix("other_"), entity)
                                    )
                                )
                                and "read" in grant.actions
                                and grant.scope in {"all", "assigned"}
                            ),
                            None,
                        )
                        assert protected_target, (
                            "Protected relation probe needs a different valid assignee"
                        )
                    probe(
                        relation,
                        label,
                        action,
                        "protected_field" if permitted else "unauthorized_action",
                        protected_target,
                        True,
                        identifier if action == "update" else None,
                    )
                continue
            readable = [
                r for r in targets if oracle.allowed(label, relation.target_entity, "read", r)
            ]
            readable.sort(key=lambda r: str(r["id"]) == str(owned.get(relation.field)))
            visible_target = str((readable or targets)[0]["id"])
            for action in ("create", "update"):
                permitted = oracle.allowed(
                    label, entity, action, None if action == "create" else owned
                )
                if not permitted:
                    probe(
                        relation,
                        label,
                        action,
                        "unauthorized_action",
                        visible_target,
                        True,
                        identifier if action == "update" else None,
                    )
                    continue
                if readable:
                    probe(
                        relation,
                        label,
                        action,
                        "visible_target",
                        visible_target,
                        False,
                        identifier if action == "update" else None,
                    )
                    probe(
                        relation,
                        label,
                        action,
                        "missing_target",
                        missing,
                        True,
                        identifier if action == "update" else None,
                    )
                foreign = next(
                    (
                        r
                        for r in targets
                        if not oracle.allowed(label, relation.target_entity, "read", r)
                    ),
                    None,
                )
                if foreign:
                    probe(
                        relation,
                        label,
                        action,
                        "foreign_target",
                        str(foreign["id"]),
                        True,
                        identifier if action == "update" else None,
                    )


def verify_native_execution(plan, manager, actors, records, evidence):
    identity = digest(plan.model_dump())
    oracle = NativeOracle(plan, manager, actors, records)
    verify_audit_mutations(oracle, evidence["audit"])
    oracle.seed_queries()
    verify_field_queries(oracle, evidence["field_queries"])
    verify_related_acl(oracle, evidence["related_acl"])
    verify_relation_writes(oracle, evidence["relation_writes"])
    assert digest(plan.model_dump()) == identity, "Native probe modified approved business Plan"
