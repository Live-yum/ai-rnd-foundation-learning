"""Bounded, allow-listed native observations for independent model review.

This module does not run probes or turn capability declarations into evidence.
The caller first validates the unchanged source, approved plan and acceptance
file. Old boolean-only reports deliberately cannot satisfy business proof gates.
"""

import json
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictBool

from workbench.domain import Name, digest
from workbench.generator import PrerequisiteError

MAX_EVIDENCE_BYTES = 64_000
MAX_EXECUTION_BYTES = 128_000
MAX_ACCEPTANCE_BYTES = 8_000_000
PROJECTION_VERSION = 2
Count = Annotated[int, Field(strict=True, ge=0, le=1_000_000)]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Role = Literal["manager", "employee", "service"]
Actor = Literal["manager", "employee", "other_employee", "service", "other_service"]
Scope = Literal["all", "own", "assigned"]
MetricKind = Literal["count", "group_count", "time_count", "average_duration"]


def positive(value):
    if value is not True:
        raise ValueError("An executed assertion did not pass")
    return value


Passed = Annotated[StrictBool, AfterValidator(positive)]


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Reminder(Observation):
    entity: Name
    event: Literal["created", "assigned", "transitioned", "note_added", "due"]
    transition: Name | None
    recipient: Literal["creator", "assignee"]
    expected_count: Count
    observed_count: Count
    idempotent: Passed
    read_persisted: Passed
    foreign_read_denied: Passed
    outsider_count: Annotated[int, Field(strict=True, ge=0, le=0)]


class Bucket(Observation):
    key_sha256: Sha256
    count: Count


class MetricValue(Observation):
    value: Annotated[float | int, Field(ge=0, le=1e15)] | None
    samples: Count | None
    buckets: list[Bucket] = Field(max_length=64)


class Metric(Observation):
    name: Name
    role: Role
    actor: Actor
    scope: Scope
    kind: MetricKind
    visible_count: Count
    expected: MetricValue
    observed: MetricValue


class MetricDenial(Observation):
    role: Role
    actor: Actor
    observed_count: Annotated[int, Field(strict=True, ge=0, le=0)]


class Audit(Observation):
    entity: Name
    mutation: Literal["update", "delete"]
    transport: Literal["http", "database"]
    denied: Passed
    before_count: Count
    after_count: Count
    before_sha256: Sha256
    after_sha256: Sha256
    unchanged: Passed


class RelatedACL(Observation):
    parent_entity: Name
    child_entity: Name
    field: Name
    role: Role
    actor: Actor
    case: Literal["visible_parent", "foreign_parent"]
    expected_count: Count
    observed_count: Count
    record_set_equal: Passed
    parent_denied: StrictBool


class RelationWrite(Observation):
    entity: Name
    field: Name
    target_entity: Name | Literal["$users"]
    role: Role
    actor: Actor
    action: Literal["create", "update", "assign"]
    case: Literal[
        "visible_target",
        "foreign_target",
        "missing_target",
        "protected_field",
        "unauthorized_action",
    ]
    denied: StrictBool
    unchanged: StrictBool
    expected_count: Count
    observed_count: Count


class QueryCase(Observation):
    case: Literal["positive", "negative", "alternate", "combination"]
    expected_count: Count
    observed_count: Count
    expected_sha256: Sha256
    observed_sha256: Sha256
    record_set_equal: Passed


class FieldQuery(Observation):
    entity: Name
    field: Name
    kind: Literal["search", "exact", "date_range"]
    role: Role
    actor: Actor
    cases: list[QueryCase] = Field(min_length=2, max_length=4)


class ExecutionEvidence(Observation):
    version: Annotated[int, Field(strict=True, ge=1, le=1)]
    spec_digest: Sha256
    reminders: list[Reminder] = Field(max_length=120)
    metrics: list[Metric] = Field(max_length=160)
    metric_denials: list[MetricDenial] = Field(max_length=5)
    audit: list[Audit] = Field(max_length=24)
    related_acl: list[RelatedACL] = Field(max_length=128)
    relation_writes: list[RelationWrite] = Field(max_length=192)
    field_queries: list[FieldQuery] = Field(max_length=256)


class LoginShell(Observation):
    actor: Actor
    rendered: Passed
    native_shell_visible: Passed
    real_login: Passed
    native_menu_received: Passed


def require(condition):
    if not condition:
        raise ValueError("Missing or inconsistent executed native proof")


def unique(items, key):
    identities = [key(item) for item in items]
    require(len(identities) == len(set(identities)))
    return set(identities)


def normalized_role(actor):
    return actor.removeprefix("other_")


def validate_execution_evidence(raw, plan):
    """Validate observations and coverage, never fill a missing probe with True."""
    proof = ExecutionEvidence.model_validate(raw)
    require(proof.spec_digest == digest(plan.model_dump()) and plan.business is not None)
    business = plan.business
    grants = {(p.role, p.entity): p for p in business.permissions}
    entities = {entity.name: entity for entity in plan.entities}
    for collection in (
        proof.metrics,
        proof.metric_denials,
        proof.related_acl,
        proof.relation_writes,
        proof.field_queries,
    ):
        for item in collection:
            require(item.role == normalized_role(item.actor))

    notices = {(n.entity, n.event, n.transition, n.recipient) for n in business.notifications}
    require(
        unique(proof.reminders, lambda n: (n.entity, n.event, n.transition, n.recipient)) == notices
    )
    for notice in proof.reminders:
        require(notice.expected_count == notice.observed_count == 1)

    metrics = {metric.name: metric for metric in business.metrics}
    metric_keys = unique(proof.metrics, lambda m: (m.name, m.actor))
    expected_metrics = set()
    for metric in business.metrics:
        for actor in ("manager", "employee", "other_employee", "service", "other_service"):
            role = normalized_role(actor)
            grant = grants.get((role, metric.entity))
            if grant and "read_metrics" in grant.actions:
                expected_metrics.add((metric.name, actor))
    require(metric_keys == expected_metrics)
    for observation in proof.metrics:
        metric = metrics[observation.name]
        grant = grants[(observation.role, metric.entity)]
        require(observation.kind == metric.kind and observation.scope == grant.scope)
        expected, observed = observation.expected, observation.observed
        require(expected.samples == observed.samples)
        require(
            unique(expected.buckets, lambda b: b.key_sha256)
            == unique(observed.buckets, lambda b: b.key_sha256)
        )
        require(
            {b.key_sha256: b.count for b in expected.buckets}
            == {b.key_sha256: b.count for b in observed.buckets}
        )
        if expected.value is None:
            require(observed.value is None)
        else:
            require(observed.value is not None and abs(expected.value - observed.value) < 0.01)
        if metric.kind == "count":
            require(type(expected.value) is int and type(observed.value) is int)
            require(not expected.buckets and expected.samples is None)
        elif metric.kind == "average_duration":
            require(expected.samples is not None and not expected.buckets)
            require((expected.value is None) == (expected.samples == 0))
        else:
            require(expected.value is None and expected.samples is None)
    expected_denials = {
        actor
        for actor in ("manager", "employee", "other_employee", "service", "other_service")
        if not any(
            p.role == normalized_role(actor) and "read_metrics" in p.actions
            for p in business.permissions
        )
    }
    require(unique(proof.metric_denials, lambda d: d.actor) == expected_denials)

    require(
        unique(proof.audit, lambda a: (a.entity, a.mutation))
        == {
            (resource.entity, mutation)
            for resource in business.resources
            for mutation in ("update", "delete")
        }
    )
    for audit in proof.audit:
        require(audit.before_count > 0 and audit.before_count == audit.after_count)
        require(audit.before_sha256 == audit.after_sha256)

    relations = {
        (r.target_entity, r.entity, r.field)
        for r in business.relations
        if r.target_entity != "$users"
    }
    related_keys = unique(
        proof.related_acl, lambda a: (a.parent_entity, a.child_entity, a.field, a.actor, a.case)
    )
    for observation in proof.related_acl:
        require(
            (observation.parent_entity, observation.child_entity, observation.field) in relations
        )
        require(observation.expected_count == observation.observed_count)
        parent_grant = grants.get((observation.role, observation.parent_entity))
        can_read = parent_grant is not None and "read" in parent_grant.actions
        if observation.case == "foreign_parent":
            require(not can_read or parent_grant.scope != "all")
            require(observation.parent_denied and observation.observed_count == 0)
        else:
            require(can_read and not observation.parent_denied)
        child_grant = grants.get((observation.role, observation.child_entity))
        if child_grant is None or "read" not in child_grant.actions:
            require(observation.observed_count == 0)
    for parent, child, field in relations:
        require((parent, child, field, "manager", "visible_parent") in related_keys)
        for role in ("employee", "service"):
            parent_grant, child_grant = grants.get((role, parent)), grants.get((role, child))
            if child_grant and "read" in child_grant.actions and child_grant.scope != "all":
                require(
                    any(
                        p == parent and c == child and f == field and normalized_role(a) == role
                        for p, c, f, a, _ in related_keys
                    )
                )
            if parent_grant and "read" in parent_grant.actions and parent_grant.scope != "all":
                require(
                    any(
                        p == parent
                        and c == child
                        and f == field
                        and normalized_role(a) == role
                        and case == "foreign_parent"
                        for p, c, f, a, case in related_keys
                    )
                )

    relation_keys = {(r.entity, r.field, r.target_entity) for r in business.relations}
    write_keys = unique(
        proof.relation_writes, lambda w: (w.entity, w.field, w.actor, w.action, w.case)
    )
    for observation in proof.relation_writes:
        require((observation.entity, observation.field, observation.target_entity) in relation_keys)
        require(observation.expected_count == observation.observed_count)
        require(not observation.denied or observation.unchanged)
        if observation.case in {
            "foreign_target",
            "missing_target",
            "protected_field",
            "unauthorized_action",
        }:
            require(observation.denied is True)
        else:
            require(observation.denied is False)
    for entity, field, _ in relation_keys:
        for case in ("visible_target", "missing_target"):
            require(any(e == entity and f == field and k == case for e, f, _, _, k in write_keys))

    query_keys = unique(proof.field_queries, lambda q: (q.entity, q.field, q.kind, q.actor))
    expected_queries = set()
    for entity in entities.values():
        fields = [
            (f.name, kind)
            for f in entity.fields
            for enabled, kind in (
                (f.searchable, "search"),
                (f.filterable, "exact"),
                (f.date_range, "date_range"),
            )
            if enabled
        ]
        for role in ("manager", "employee", "service"):
            grant = grants.get((role, entity.name))
            if grant and "read" in grant.actions:
                expected_queries.update((entity.name, name, kind, role) for name, kind in fields)
    covered_queries = {(e, f, k, normalized_role(a)) for e, f, k, a in query_keys}
    require(covered_queries == expected_queries)
    for query in proof.field_queries:
        cases = unique(query.cases, lambda c: c.case)
        require("positive" in cases and bool({"negative", "alternate"} & cases))
        positive_case = next(case for case in query.cases if case.case == "positive")
        for case in query.cases:
            require(case.expected_count == case.observed_count)
            require(case.expected_sha256 == case.observed_sha256)
            if case.case == "positive":
                require(case.observed_count > 0)
            if case.case == "negative":
                require(case.observed_count == 0)
            if case.case == "alternate":
                require(case.expected_sha256 != positive_case.expected_sha256)
    for entity, _, _, role in expected_queries:
        configured = {(f, k) for e, f, k, r in expected_queries if e == entity and r == role}
        filters = {field for field, kind in configured if kind != "search"}
        searches = {field for field, kind in configured if kind == "search"}
        # All searchable text fields share one q operand. Two such fields alone
        # do not provide two composable query operations.
        composable = len(filters) > 1 or any(a != b for a in searches for b in filters)
        if composable:
            require(
                any(
                    q.entity == entity
                    and q.role == role
                    and any(c.case == "combination" for c in q.cases)
                    for q in proof.field_queries
                )
            )
    result = proof.model_dump()
    require(len(json.dumps(result, separators=(",", ":")).encode()) <= MAX_EXECUTION_BYTES)
    return result


_BROWSER_CHECKS = {
    "manager:customers:native-query-and-exact-filter",
    "manager:customer_native_form_create",
    "manager:changed_value_edit",
    "employee:related_request_native_form_create",
    "manager:linked_task_and_native_assignment",
    "service:assigned_workflows_notes_timestamps",
    "manager:all_declared_native_metric_cards",
    "employee:own_record_history_acl_and_read_reminder",
    "other_employee:row_isolation",
    "other_service:row_isolation",
    "native-business-action:assign:",
    "native-business-action:transition:start",
    "native-business-action:transition:resolve",
    "native-business-action:add_note:",
    "manager:customers:requests:related-record-and-history",
    "manager:requests:tasks:related-record-and-history",
    "manager:real-native-echarts-metrics",
    *(
        f"{role}:{login}"
        for role in ("manager", "employee", "other_employee", "service", "other_service")
        for login in ("real_native_login_menu_shell", "native-login-and-tenant")
    ),
    *(
        f"{role}:{entity}:native-form-create"
        for role in ("manager", "employee", "service")
        for entity in ("customers", "requests", "tasks")
    ),
}


def browser_summary(report, plan):
    """Never forward arbitrary browser logs, URLs, usernames or theme strings."""
    require(report.get("passed") is True and report.get("spec_digest") == digest(plan.model_dump()))
    checks = report.get("checks")
    require(isinstance(checks, list) and len(checks) <= 256)
    require(all(isinstance(check, str) and check in _BROWSER_CHECKS for check in checks))
    pages = []
    login_shells = []
    names = {entity.name for entity in plan.entities}
    observations = report.get("pages")
    require(isinstance(observations, list) and len(observations) <= 32)
    for page in observations:
        require(isinstance(page, dict))
        if "entity" not in page:
            # FastapiAdmin records each real actor login before its entity-form
            # observations. A login shell is a separate executed proof type,
            # never a substitute for a missing entity page or an arbitrary log.
            require(report.get("template") == "fastapiadmin")
            require(
                set(page)
                == {
                    "role",
                    "route",
                    "rendered",
                    "native_shell_visible",
                    "native_component_family",
                    "native_theme_tokens",
                    "real_login",
                    "native_menu_received",
                }
            )
            shell = LoginShell.model_validate(
                {
                    "actor": page["role"],
                    **{key: page[key] for key in LoginShell.model_fields if key != "actor"},
                }
            )
            require(f"{shell.actor}:real_native_login_menu_shell" in checks)
            require(page["route"] in {f"/module_rnd/{name}" for name in names})
            require(page["native_component_family"] == "Fa/Element Plus")
            tokens = page["native_theme_tokens"]
            require(
                isinstance(tokens, dict)
                and all(
                    isinstance(tokens.get(key), str) and tokens[key].strip()
                    for key in ("--el-color-primary", "--el-font-size-base")
                )
            )
            login_shells.append(shell)
            continue
        require(page.get("entity") in names)
        pages.append(
            {
                "entity": page["entity"],
                **{
                    key: page.get(key) is True
                    for key in (
                        "native_shell_visible",
                        "native_form_components_visible",
                        "real_list_request",
                    )
                },
            }
        )
    login_actors = unique(login_shells, lambda shell: shell.actor)
    if report.get("template") == "fastapiadmin":
        # Each claimed executed login needs its actual typed shell observation.
        # Keeping a check marker cannot replace a deleted actor's proof page.
        suffix = ":real_native_login_menu_shell"
        require(
            login_actors
            == {check.removesuffix(suffix) for check in checks if check.endswith(suffix)}
        )
    require(
        {
            page["entity"]
            for page in pages
            if all(value is True for key, value in page.items() if key != "entity")
        }
        == names
    )
    from workbench.business_browser import query_journey_evidence

    return {
        "passed": True,
        "checks": sorted(set(checks)),
        "pages": pages,
        "login_shells": [shell.model_dump() for shell in login_shells],
        "query_journey": query_journey_evidence(report),
    }


def execution_summary(raw, plan):
    proof = validate_execution_evidence(raw, plan)
    proof["execution_sha256"] = digest(proof)
    # Keep the raw observation schema's version unchanged. The separately
    # versioned projection uses ordered rows paired with named column maps.
    proof["projection_version"] = PROJECTION_VERSION
    # The full acceptance artifact retains both hashes for each query. Validate
    # them before compacting repetitive cases with an explicit shared column map;
    # preserve expected/actual counts and the actually executed set-equality test.
    columns = ["case", "expected_count", "observed_count", "record_set_equal"]
    proof["field_query_case_columns"] = columns
    for query in proof["field_queries"]:
        query["cases"] = [[case[column] for column in columns] for case in query["cases"]]
    # The full per-actor relation and ACL matrices repeat the same keys in every
    # row, in both installations. Encode all validated values with explicit
    # column maps so a valid approved Plan fits the unchanged model-context bound.
    # Hashing above still binds the complete uncompressed executed proof.
    for collection, schema, key in (
        ("relation_writes", RelationWrite, "relation_write_columns"),
        ("related_acl", RelatedACL, "related_acl_columns"),
    ):
        columns = list(schema.model_fields)
        proof[key] = columns
        proof[collection] = [[row[column] for column in columns] for row in proof[collection]]
    return proof


def native_review_evidence(report, plan, files, evidence_sha256):
    """Produce model-safe evidence only after mandatory proof checks succeed."""
    try:
        require(report.get("spec_digest") == digest(plan.model_dump()))
        require(report.get("template") in {"fastapiadmin", "yudao-vben"})
        restored = report["portable_restored"]
        deployment = {}
        for key in (
            "passed",
            "fresh_database",
            "frontend_started",
            "installed_from_lock",
            "standalone_launcher",
            "restart",
            "source_database_reused",
            "original_platform_imported",
            "model_required",
            "archive_round_trip",
            "restart_preserved_records",
        ):
            value = restored.get(key)
            require(value is None or type(value) is bool)
            deployment[key] = value
        if plan.business:
            require(deployment["archive_round_trip"] is True)
            require(deployment["restart_preserved_records"] is True)
        result = {
            "version": PROJECTION_VERSION,
            "spec_digest": digest(plan.model_dump()),
            "source_digest": digest(files),
            "acceptance_sha256": evidence_sha256,
            "template": report["template"],
            "deployment": deployment,
            "reproduction_files": {
                name: files[name]
                for name in (
                    "start.py",
                    "START_HERE.md",
                    "deployment/run.py",
                    "deployment/pyproject.toml",
                    "deployment/uv.lock",
                    "deployment/business-browser.cjs",
                    "deployment/workbench/business_probe.py",
                    "deployment/workbench/native_business_probe.py",
                )
                if name in files
            },
        }
        if plan.business:
            result["original_installation"] = {
                "http": execution_summary(
                    report["business_contract"].get("execution_evidence"), plan
                ),
                "browser": browser_summary(report["business_browser"], plan),
            }
            result["fresh_database_installation"] = {
                "http": execution_summary(
                    report["portable_restored"]["business"].get("execution_evidence"), plan
                ),
                "browser": browser_summary(report["portable_restored"]["browser"], plan),
            }
            if report["template"] == "yudao-vben":
                from workbench.yudao_navigation_checks import (
                    encode_navigation,
                    encode_observation_rows,
                    validate_navigation,
                    validate_sidebar,
                )

                # Deduplicate only byte-identical validated observations. Each
                # installation and restart retains an explicit pool reference;
                # the versioned named-column codec preserves every raw value.
                pool = []
                result["installed_navigation_proofs"] = pool

                def retain(value, browser=False):
                    encoded = encode_navigation(value, browser=browser)
                    if encoded not in pool:
                        pool.append(encoded)
                    return pool.index(encoded)

                for label, business, browser in (
                    (
                        "original_installation",
                        report["business_contract"],
                        report["business_browser"],
                    ),
                    ("fresh_database_installation", restored["business"], restored["browser"]),
                ):
                    first = validate_navigation(business.get("installed_navigation"), plan)
                    restarted = validate_navigation(
                        business.get("installed_navigation_restart"), plan
                    )
                    require(first == restarted)
                    sidebar = validate_sidebar(browser.get("installed_navigation"), plan)
                    result[label]["navigation"] = {
                        "http": retain(first),
                        "restart_http": retain(restarted),
                        "browser": retain(sidebar, browser=True),
                    }
                    # This optional collection codec has its own explicit
                    # version and hashes. The raw execution schema is unchanged.
                    for collection, columns in (
                        ("metrics", list(Metric.model_fields)),
                        ("field_queries", ["entity", "field", "kind", "role", "actor", "cases"]),
                    ):
                        result[label]["http"][collection] = encode_observation_rows(
                            result[label]["http"][collection], columns
                        )
        require(len(json.dumps(result, separators=(",", ":")).encode()) <= MAX_EVIDENCE_BYTES)
        return result
    except ValueError, TypeError, KeyError, AttributeError:
        # Pydantic exceptions can echo rejected inputs, which may contain secrets.
        raise PrerequisiteError(
            "原生执行证据缺失、越界或与批准设计不匹配；必须重新执行细项验收，不能使用旧布尔回执"
        ) from None
