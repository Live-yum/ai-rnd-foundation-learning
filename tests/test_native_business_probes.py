"""Native wire-protocol probe tests, not receipts of a deployed native installation.

MockTransport independently implements the two route protocols. Mutation tests
prove that a successful HTTP response or true marker cannot substitute for the
observable database effects and exact query/ACL results.
"""

import json
from contextlib import contextmanager
from copy import deepcopy

import httpx
import pytest

from workbench.business_probe import BusinessClient, wire_name
from workbench.domain import Plan, digest
from workbench.native_business_probe import (
    NativeOracle,
    verify_audit_mutations,
    verify_field_queries,
    verify_native_execution,
    verify_related_acl,
    verify_relation_writes,
)
from workbench.settings import ROOT


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_shared_probe_sends_only_native_pagination_keys(template):
    seen = []
    client = BusinessClient(
        template,
        "http://127.0.0.1",
        "synthetic",
        [{"entity": "customers", "list": "/admin-api/infra/wb-customers/page"}],
    )
    client.http.close()
    client.http = httpx.Client(
        base_url="http://127.0.0.1",
        transport=httpx.MockTransport(
            lambda request: (
                seen.append(dict(request.url.params))
                or httpx.Response(
                    200,
                    json={
                        "code": 200 if template == "fastapiadmin" else 0,
                        "data": {"items": [], "list": []},
                    },
                )
            )
        ),
    )
    try:
        assert (
            client.rows("customers", q="keyword", page_size=100, pageSize=100, page=2, pageNo=2)
            == []
        )
        expected = {
            "q": "keyword",
            **(
                {"page_size": "100", "page": "2"}
                if template == "fastapiadmin"
                else {"pageSize": "100", "pageNo": "2"}
            ),
        }
        assert seen == [expected]
        with pytest.raises(ValueError, match="Conflicting native pagination"):
            client.rows("customers", page_size=10, pageSize=20)
        assert len(seen) == 1
    finally:
        client.close()


def plan_with_date():
    raw = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    raw["entities"][0]["fields"].append(
        {"name": "contact_date", "kind": "date", "date_range": True}
    )
    return Plan.model_validate(raw)


@contextmanager
def protocol(template, fault=None, plan=None):
    plan = plan or plan_with_date()
    fastapi = template == "fastapiadmin"
    identities = {
        "manager": "20",
        "employee": "21",
        "other_employee": "22",
        "service": "23",
        "other_service": "24",
    }
    grants = {(p.role, p.entity): p for p in plan.business.permissions}
    definitions = {e.name: e for e in plan.entities}
    resources = {r.entity: r for r in plan.business.resources}
    workflows = {w.entity: w for w in plan.business.workflows}
    relations = {(r.entity, r.field): r for r in plan.business.relations}
    rows = {entity: [] for entity in definitions}
    audits = {}
    calls = []
    counter = 100

    def allow(label, entity, action, row=None):
        grant = grants.get((label.removeprefix("other_"), entity))
        if not grant or action not in grant.actions:
            return False
        if grant.scope == "all":
            return True
        if row is None:
            return action == "create" and grant.scope == "own"
        field = "created_by" if grant.scope == "own" else resources[entity].assignee_field
        return str(row.get(field)) == identities[label]

    def answer(data=None, code=None):
        return httpx.Response(
            code if fastapi and code else 200,
            json={"code": code or (200 if fastapi else 0), "data": data},
        )

    def encode(row):
        return {wire_name(template, key): value for key, value in deepcopy(row).items()}

    def decode(entity, body):
        inverse = {wire_name(template, f.name): f.name for f in definitions[entity].fields}
        return {inverse.get(key, key): value for key, value in body.items()}

    def lookup(entity, identifier):
        return next((r for r in rows[entity] if str(r["id"]) == str(identifier)), None)

    def validate(label, entity, body, row=None):
        protected = {resources[entity].assignee_field}
        if entity in workflows:
            protected.add(workflows[entity].status_field)
            protected.update(t.set_timestamp for t in workflows[entity].transitions)
        if (
            any(body[field] != (row or {}).get(field) for field in protected.intersection(body))
            and fault != "protected_write"
        ):
            return 422
        for field, value in body.items():
            relation = relations.get((entity, field))
            if relation and relation.target_entity != "$users":
                target = lookup(relation.target_entity, value)
                if target is None and fault != "missing_target":
                    return 400
                if (
                    target
                    and not allow(label, relation.target_entity, "read", target)
                    and fault != "foreign_target"
                ):
                    return 403
        return None

    def add_audit(entity, identifier, event):
        audits.setdefault((entity, str(identifier)), []).append(
            {
                "id": str(sum(map(len, audits.values())) + 1),
                "event": event,
                "after": deepcopy(lookup(entity, identifier)),
            }
        )

    def select(entity, label, query):
        if fastapi:
            filters = json.loads(query.get("filters", "{}"))
        else:
            inverse = {wire_name(template, f.name): f.name for f in definitions[entity].fields}
            filters = {}
            for key, value in query.items():
                if key in {"q", "pageNo", "pageSize"}:
                    continue
                suffix = "_from" if key.endswith("_from") else "_to" if key.endswith("_to") else ""
                plain = key[: -len(suffix)] if suffix else key
                assert plain in inverse, "Probe sent a non-native query field"
                filters[inverse[plain] + suffix] = value
        fields = {f.name: f for f in definitions[entity].fields}
        result = []
        for row in rows[entity]:
            if not allow(label, entity, "read", row) and not (
                fault == "query_scope" and query.get("q")
            ):
                continue
            needle = query.get("q", "").casefold()
            searched = [f.name for f in fields.values() if f.searchable]
            if fault and fault.startswith("search_field:"):
                searched.remove(fault.split(":", 1)[1]) if fault.split(":", 1)[
                    1
                ] in searched else None
            search = not needle or any(
                needle == str(row.get(name) or "").casefold()
                if fault == "search_equality"
                else needle in str(row.get(name) or "").casefold()
                for name in searched
            )
            predicates = []
            for key, expected in filters.items():
                suffix = "_from" if key.endswith("_from") else "_to" if key.endswith("_to") else ""
                name = key[: -len(suffix)] if suffix else key
                actual = row.get(name)
                if fault == "ignore_filter" or fault == "ignore_combination" and needle:
                    continue
                if suffix:
                    if (
                        fault == "ignore_date"
                        or fault == "ignore_from"
                        and suffix == "_from"
                        or fault == "ignore_to"
                        and suffix == "_to"
                    ):
                        continue
                    predicates.append(
                        actual is not None
                        and (actual >= expected if suffix == "_from" else actual <= expected)
                    )
                else:
                    predicates.append(
                        str(expected) in str(actual)
                        if fault == "substring_exact"
                        else str(actual) == str(expected)
                    )
            include = search and all(predicates)
            if fault == "combination_or" and needle and filters:
                include = search or all(predicates)
            if include:
                result.append(encode(row))
        return result

    def handler(request):
        nonlocal counter
        label = request.headers["Authorization"].removeprefix("Bearer ")
        path, query = request.url.path, dict(request.url.params)
        body = json.loads(request.content) if request.content else {}
        calls.append((label, request.method, path, deepcopy(query), deepcopy(body)))
        if path.endswith(("/configuration", "/me")):
            return answer(
                {"actor": {"id": identities[label], "role": label}}
                if fastapi
                else {"id": identities[label]}
            )
        if path.endswith("/metrics"):
            namespace = {}
            exec(
                compile(
                    (ROOT / "templates/business/common/policy.py").read_text(encoding="utf-8"),
                    "native-policy.py",
                    "exec",
                ),
                namespace,
            )
            policy = namespace["Policy"](plan.model_dump())
            values = []
            for metric in plan.business.metrics:
                grant = grants.get((label.removeprefix("other_"), metric.entity))
                if grant and "read_metrics" in grant.actions:
                    visible = [
                        row
                        for row in rows[metric.entity]
                        if allow(label, metric.entity, "read_metrics", row)
                    ]
                    values.append(
                        {"name": metric.name, "value": policy.metric(visible, metric.model_dump())}
                    )
            return answer(values)
        entity = (
            next((name for name in definitions if f"/{name}/" in path), None)
            or query.get("entity")
            or body.get("entity")
        )
        identifier = query.get("id") or body.get("id")
        if fastapi and entity:
            tail = path.split("/" + entity + "/", 1)[1].split("/")
            if len(tail) > 1:
                identifier = tail[0]
        if path.endswith("/history"):
            existing = audits.get((entity, str(identifier)), [])
            if request.method != "GET":
                if fault == "audit_changed":
                    existing[0]["event"] = "changed"
                if fault == "audit_accepted":
                    return answer(True)
                return answer(code=405)
            assert allow(label, entity, "read_audit", lookup(entity, identifier))
            return answer(deepcopy(existing))
        if path.endswith(("/list", "/page")):
            if not any(
                p.role == label.removeprefix("other_")
                and p.entity == entity
                and "read" in p.actions
                for p in plan.business.permissions
            ):
                return answer(code=403)
            result = select(entity, label, query)
            page = int(query.get("page", query.get("pageNo", 1)))
            size = int(query.get("page_size", query.get("pageSize", 100)))
            assert size == 100
            return answer(
                {
                    "items" if fastapi else "list": result[(page - 1) * size : page * size],
                    "total": len(result),
                }
            )
        if path.endswith("/related"):
            parent = lookup(entity, identifier)
            if not allow(label, entity, "read", parent) and fault != "foreign_parent":
                return answer(code=403)
            result = {}
            for relation in plan.business.relations:
                if relation.target_entity != entity:
                    continue
                child_rows = [
                    encode(r)
                    for r in rows[relation.entity]
                    if str(r.get(relation.field)) == str(identifier)
                    and (allow(label, relation.entity, "read", r) or fault == "related_scope")
                ]
                result[relation.entity] = child_rows
            return answer(
                result
                if fastapi
                else {
                    "groups": [
                        {"entity": name, "records": [{"record": r} for r in values]}
                        for name, values in result.items()
                    ]
                }
            )
        creating = path.endswith("/create")
        action = (
            "create"
            if creating
            else path.rsplit("/", 1)[-1]
            if fastapi or path.endswith("/update")
            else body["action"]
        )
        row = None if creating else lookup(entity, identifier)
        if not allow(label, entity, action, row) and fault != "unauthorized_write":
            return answer(code=403)
        data = decode(entity, body)
        if action in {"create", "update"}:
            error = validate(label, entity, data, row)
            if error:
                return answer(code=error)
            data.pop("id", None)
            if creating:
                counter += 1
                row = {
                    "id": str(counter),
                    "created_by": identities[label],
                    "created_at": "2026-10-01T00:00:00Z",
                    **data,
                }
                if entity in workflows:
                    row[workflows[entity].status_field] = workflows[entity].initial
                row.setdefault(resources[entity].assignee_field, None) if resources[
                    entity
                ].assignee_field else None
                rows[entity].append(row)
                identifier = row["id"]
            else:
                row.update(data)
        elif action == "assign":
            assignee = body.get("assignee", body.get("assigneeId"))
            recipient = next((a for a, value in identities.items() if value == assignee), None)
            grant = grants.get((recipient.removeprefix("other_"), entity)) if recipient else None
            if not grant or "read" not in grant.actions or grant.scope not in {"all", "assigned"}:
                return answer(code=422)
            row[resources[entity].assignee_field] = assignee
        elif action == "transition":
            transition = next(
                t for t in workflows[entity].transitions if t.name == data["transition"]
            )
            assert row[workflows[entity].status_field] in transition.from_states
            row[workflows[entity].status_field] = transition.to_state
            if transition.set_timestamp:
                row[transition.set_timestamp] = "2026-10-01T00:01:00Z"
        add_audit(entity, identifier, action)
        return answer(encode(row) if fastapi or not creating else identifier)

    targets = [
        {"entity": e, "api": "/admin-api/infra/" + e, "list": "/admin-api/infra/" + e + "/page"}
        for e in definitions
    ]
    clients = {}
    for label in identities:
        client = BusinessClient(template, "http://127.0.0.1", label, targets)
        client.http.close()
        client.http = httpx.Client(
            base_url="http://127.0.0.1",
            headers={"Authorization": "Bearer " + label},
            transport=httpx.MockTransport(handler),
        )
        clients[label] = client
    manager = clients["manager"]
    actors = {
        label: (identities[label], client)
        for label, client in clients.items()
        if label != "manager"
    }
    records = {}
    oracle = NativeOracle(plan, manager, actors, records)
    # All baseline rows are synthetic and created through the same native routes.
    for entity in definitions:
        records[entity] = manager.create(entity, oracle.sample(entity))
    try:
        yield oracle, calls, rows, audits
    finally:
        for client in clients.values():
            client.close()


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_native_probes_execute_all_fields_roles_relations_and_actual_audit_mutations(template):
    with protocol(template) as (oracle, calls, _, _):
        evidence = {key: [] for key in ("audit", "field_queries", "related_acl", "relation_writes")}
        verify_native_execution(
            oracle.plan,
            oracle.manager,
            {k: v for k, v in oracle.actors.items() if k != "manager"},
            oracle.records,
            evidence,
        )
        assert len(evidence["audit"]) == 6
        assert all(p["before_sha256"] == p["after_sha256"] for p in evidence["audit"])
        assert {p["kind"] for p in evidence["field_queries"]} == {"search", "exact", "date_range"}
        assert {p["actor"] for p in evidence["field_queries"]} == set(oracle.actors)
        assert {p["case"] for p in evidence["relation_writes"]} >= {
            "visible_target",
            "missing_target",
            "protected_field",
            "unauthorized_action",
            "foreign_target",
        }
        assert all(
            c["expected_count"] == c["observed_count"]
            and c["expected_sha256"] == c["observed_sha256"]
            for p in evidence["field_queries"]
            for c in p["cases"]
        )
        assert (
            sum(
                method in {"PUT", "DELETE"} and path.endswith("/history")
                for _, method, path, _, _ in calls
            )
            == 6
        )
        assert "Bearer" not in json.dumps(evidence) and "params" not in json.dumps(evidence)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "fault",
    [
        "ignore_filter",
        "ignore_combination",
        "combination_or",
        "query_scope",
        "search_equality",
        "ignore_date",
        "ignore_from",
        "ignore_to",
        "search_field:organization",
        "search_field:detail",
    ],
)
def test_query_mutations_are_detected_by_actual_native_protocol_results(template, fault):
    with protocol(template, fault) as (oracle, _, _, _):
        oracle.seed_queries()
        with pytest.raises(AssertionError, match="Native query matrix differs"):
            verify_field_queries(oracle, [])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("fault", ["audit_accepted", "audit_changed"])
def test_audit_success_or_denial_with_changed_history_is_not_immutable_proof(template, fault):
    with protocol(template, fault) as (oracle, _, _, _):
        with pytest.raises(AssertionError):
            verify_audit_mutations(oracle, [])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("fault", ["related_scope", "foreign_parent"])
def test_related_acl_rejects_hidden_children_and_inaccessible_parent_reads(template, fault):
    with protocol(template, fault) as (oracle, _, _, _):
        oracle.seed_queries()
        with pytest.raises(AssertionError):
            verify_related_acl(oracle, [])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "fault", ["missing_target", "foreign_target", "protected_write", "unauthorized_write"]
)
def test_relation_write_failures_cannot_be_hidden_by_boolean_markers(template, fault):
    with protocol(template, fault) as (oracle, _, _, _):
        oracle.seed_queries()
        with pytest.raises(AssertionError):
            verify_relation_writes(oracle, [])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_exact_filters_reject_substring_implementation(template):
    with protocol(template, "substring_exact") as (oracle, _, _, _):
        oracle.seed_queries()
        with pytest.raises(AssertionError, match="/exact/negative"):
            verify_field_queries(oracle, [])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "fault", [None, "duplicate", "truncated", "changed_total", "missing_total"]
)
def test_native_query_client_requires_complete_stable_pagination(template, fault):
    client = BusinessClient(
        template,
        "http://127.0.0.1",
        "synthetic",
        [{"entity": "customers", "list": "/admin-api/infra/customers/page"}],
    )
    client.http.close()
    requested = []

    def handler(request):
        query = dict(request.url.params)
        requested.append(query)
        fastapi = template == "fastapiadmin"
        page = int(query["page" if fastapi else "pageNo"])
        if fastapi:
            assert json.loads(query["filters"]) == {
                "contact_date_from": "2098-02-01",
                "category": "企业",
            }
        else:
            assert query["contactDate_from"] == "2098-02-01" and query["category"] == "企业"
        assert query["q"] == "NEEDLE"
        if fault == "duplicate" and page > 1:
            page = 1
        rows = [{"id": str(i)} for i in range((page - 1) * 100, min(page * 100, 235))]
        if fault == "truncated":
            rows = rows[:50]
        body = {
            "items" if fastapi else "list": rows,
            "total": 236 if fault == "changed_total" and page > 1 else 235,
        }
        if fault == "missing_total":
            body.pop("total")
        return httpx.Response(200, json={"code": 200 if fastapi else 0, "data": body})

    client.http = httpx.Client(base_url="http://127.0.0.1", transport=httpx.MockTransport(handler))
    try:
        if fault:
            with pytest.raises(AssertionError):
                client.all_rows(
                    "customers",
                    q="NEEDLE",
                    filters={"contact_date_from": "2098-02-01", "category": "企业"},
                )
        else:
            assert (
                len(
                    client.all_rows(
                        "customers",
                        q="NEEDLE",
                        filters={"contact_date_from": "2098-02-01", "category": "企业"},
                    )
                )
                == 235
            )
            assert len(requested) == 3
    finally:
        client.close()


@pytest.mark.parametrize(
    "fault", [None, "ignore_filter", "search_equality", "query_scope", "ignore_date"]
)
def test_real_fastapi_native_sql_source_is_checked_by_the_query_oracle(fault):
    """Run shipped native rows/scope functions against real SQLAlchemy SQLite.

    Authentication/install/browser are deliberately outside this isolated source
    test. Native integration receipts still require the complete installed apps.
    """
    import ast
    import asyncio
    from datetime import UTC, date, datetime

    from fastapi import HTTPException
    from sqlalchemy import (
        Boolean,
        Column,
        Date,
        DateTime,
        Integer,
        String,
        create_engine,
        or_,
        select,
    )
    from sqlalchemy.orm import Session, declarative_base

    runtime = (ROOT / "templates/business/fastapiadmin/runtime.py").read_text(encoding="utf-8")
    if fault == "ignore_filter":
        before, after = "statement = statement.where(column == value)", "statement = statement"
    elif fault == "search_equality":
        before, after = ".icontains(query, autoescape=True)", ".ilike(query)"
    elif fault == "query_scope":
        before, after = (
            "scope(who, entity, action), model.is_deleted.is_(archived)",
            "(model.id > 0 if query else scope(who, entity, action)), model.is_deleted.is_(archived)",
        )
    elif fault == "ignore_date":
        before, after = (
            'statement = statement.where(column >= bound if suffix == "from" else column <= bound)',
            "statement = statement",
        )
    if fault:
        assert before in runtime
        runtime = runtime.replace(before, after)
    names = {"fail", "identifier", "date_value", "instant", "grant", "scope", "rows"}
    tree = ast.parse(runtime)
    tree.body = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names
    ]
    policy_namespace = {}
    exec(
        compile(
            (ROOT / "templates/business/common/policy.py").read_text(encoding="utf-8"),
            "native-policy.py",
            "exec",
        ),
        policy_namespace,
    )

    with protocol("fastapiadmin") as (oracle, _, _, _):
        oracle.seed_queries()
        base = declarative_base()
        models = {}
        for entity, definition in oracle.entities.items():
            attrs = {
                "__tablename__": entity,
                "id": Column(Integer, primary_key=True),
                "created_id": Column(Integer),
                "is_deleted": Column(Boolean, default=False),
            }
            for field in definition.fields:
                kind = {
                    "integer": Integer,
                    "date": Date,
                    "datetime": DateTime,
                    "boolean": Boolean,
                }.get(field.kind, String)
                attrs[field.name] = Column(kind)
            models[entity] = type(entity.title(), (base,), attrs)
        engine = create_engine("sqlite://")
        base.metadata.create_all(engine)
        namespace = {
            "HTTPException": HTTPException,
            "datetime": datetime,
            "date": date,
            "UTC": UTC,
            "select": select,
            "or_": or_,
            "POLICY": policy_namespace["Policy"](oracle.plan.model_dump()),
            "PolicyError": policy_namespace["PolicyError"],
            "MODELS": models,
            "ENTITIES": {e.name: e.model_dump() for e in oracle.plan.entities},
            "SPEC": oracle.plan.business.model_dump(),
        }
        exec(compile(tree, "native-runtime-query.py", "exec"), namespace)
        with Session(engine) as db:
            for entity, definition in oracle.entities.items():
                for row in oracle.rows[entity]:
                    values = {
                        "id": int(row["id"]),
                        "created_id": int(row["created_by"]),
                        "is_deleted": False,
                    }
                    for field in definition.fields:
                        value = row.get(field.name)
                        if value is not None and field.kind in {"date", "datetime"}:
                            value = (
                                date.fromisoformat(value)
                                if field.kind == "date"
                                else datetime.fromisoformat(value.replace("Z", "+00:00"))
                            )
                        values[field.name] = value
                    db.add(models[entity](**values))
            db.commit()

            class AsyncSessionAdapter:
                async def scalars(self, query):
                    return db.scalars(query)

            def sql_rows(client, entity, **query):
                label = next(name for name, (_, actor) in oracle.actors.items() if actor is client)
                who = {"id": oracle.actors[label][0], "role": label.removeprefix("other_")}
                result = asyncio.run(
                    namespace["rows"](
                        AsyncSessionAdapter(),
                        who,
                        entity,
                        query=query.get("q", ""),
                        filters=query.get("filters"),
                    )
                )
                records = []
                for row in result:
                    record = {"id": str(row.id), "created_by": str(row.created_id)}
                    for field in oracle.entities[entity].fields:
                        value = getattr(row, field.name)
                        record[field.name] = (
                            value.isoformat() if isinstance(value, (date, datetime)) else value
                        )
                    records.append(record)
                return records

            oracle.all_rows = sql_rows
            if fault:
                with pytest.raises(AssertionError, match="Native query matrix differs"):
                    verify_field_queries(oracle, [])
            else:
                proof = []
                verify_field_queries(oracle, proof)
                assert len(proof) == 54
        engine.dispose()


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_full_executed_probe_collections_satisfy_the_strict_native_review_contract(template):
    from test_business_probe import reminder_case

    from workbench.business_probe import verify_event_reminders, verify_scoped_metrics
    from workbench.native_evidence import validate_execution_evidence

    with protocol(template) as (oracle, _, _, _):
        proof = {
            "version": 1,
            "spec_digest": digest(oracle.plan.model_dump()),
            **{
                key: []
                for key in (
                    "reminders",
                    "metrics",
                    "metric_denials",
                    "audit",
                    "field_queries",
                    "related_acl",
                    "relation_writes",
                )
            },
        }
        original = deepcopy(oracle.plan.model_dump())
        verify_native_execution(
            oracle.plan,
            oracle.manager,
            {k: v for k, v in oracle.actors.items() if k != "manager"},
            oracle.records,
            proof,
        )
        for label, (_, client) in oracle.actors.items():
            verify_scoped_metrics(client, oracle.plan, label.removeprefix("other_"), label, proof)
        for notice in oracle.plan.business.notifications:
            reminder_plan, recipients, outsider, emit = reminder_case(template)
            verify_event_reminders(
                reminder_plan,
                notice.entity,
                "owned-control",
                notice.event,
                recipients,
                [outsider],
                lambda: emit(notice.entity, "owned-control", notice.event, notice.transition),
                notice.transition,
                proof["reminders"],
            )
        assert validate_execution_evidence(proof, oracle.plan) == proof
        assert oracle.plan.model_dump() == original
        assert {row["actor"] for row in proof["metric_denials"]} == {"employee", "other_employee"}
        assert all(
            row["expected_count"] == row["observed_count"] == 1 for row in proof["reminders"]
        )
        assert all(
            row["expected"]["value"] is None and row["expected"]["samples"] == 0
            for row in proof["metrics"]
            if row["kind"] == "average_duration"
        )
