"""Synthetic fixtures test proof validation; these are NOT native runtime receipts."""

import json
from copy import deepcopy

import pytest
from test_native_business_evidence import evidence as legacy_business_fixture
from test_native_managed import verified_fixture

from workbench.domain import Plan, digest
from workbench.generator import PrerequisiteError
from workbench.native_delivery import managed_verify
from workbench.native_evidence import (
    MAX_EVIDENCE_BYTES,
    native_review_evidence,
    validate_execution_evidence,
)
from workbench.settings import ROOT


def synthetic_observations(plan):
    """Explicit unit-only data, not a substitute for the HTTP probe producer."""
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    grants = {(p.role, p.entity): p for p in plan.business.permissions}
    result = {
        "version": 1,
        "spec_digest": digest(plan.model_dump()),
        "reminders": [
            {
                "entity": n.entity,
                "event": n.event,
                "transition": n.transition,
                "recipient": n.recipient,
                "expected_count": 1,
                "observed_count": 1,
                "idempotent": True,
                "read_persisted": True,
                "foreign_read_denied": True,
                "outsider_count": 0,
            }
            for n in plan.business.notifications
        ],
        "metrics": [],
        "metric_denials": [],
        "audit": [],
        "related_acl": [],
        "relation_writes": [],
        "field_queries": [],
    }
    for actor in actors:
        role = actor.removeprefix("other_")
        allowed = False
        for metric in plan.business.metrics:
            grant = grants.get((role, metric.entity))
            if not grant or "read_metrics" not in grant.actions:
                continue
            allowed = True
            value = {"value": None, "samples": None, "buckets": []}
            if metric.kind == "count":
                value["value"] = 2
            elif metric.kind == "average_duration":
                value["samples"] = 0
            else:
                value["buckets"] = [{"key_sha256": "1" * 64, "count": 2}]
            result["metrics"].append(
                {
                    "name": metric.name,
                    "role": role,
                    "actor": actor,
                    "scope": grant.scope,
                    "kind": metric.kind,
                    "visible_count": 2,
                    "expected": value,
                    "observed": deepcopy(value),
                }
            )
        if not allowed:
            result["metric_denials"].append({"role": role, "actor": actor, "observed_count": 0})
    for resource in plan.business.resources:
        for mutation in ("update", "delete"):
            result["audit"].append(
                {
                    "entity": resource.entity,
                    "mutation": mutation,
                    "transport": "http",
                    "denied": True,
                    "before_count": 3,
                    "after_count": 3,
                    "unchanged": True,
                    "before_sha256": "2" * 64,
                    "after_sha256": "2" * 64,
                }
            )
    for relation in plan.business.relations:
        if relation.target_entity != "$users":
            for actor in actors:
                role = actor.removeprefix("other_")
                parent_grant = grants.get((role, relation.target_entity))
                child_grant = grants.get((role, relation.entity))
                can_read = parent_grant and "read" in parent_grant.actions
                for case in ("visible_parent", "foreign_parent"):
                    if case == "visible_parent" and not can_read:
                        continue
                    if case == "foreign_parent" and can_read and parent_grant.scope == "all":
                        continue
                    count = int(
                        case == "visible_parent"
                        and child_grant is not None
                        and "read" in child_grant.actions
                    )
                    result["related_acl"].append(
                        {
                            "parent_entity": relation.target_entity,
                            "child_entity": relation.entity,
                            "field": relation.field,
                            "role": role,
                            "actor": actor,
                            "case": case,
                            "expected_count": count,
                            "observed_count": count,
                            "record_set_equal": True,
                            "parent_denied": case == "foreign_parent",
                        }
                    )
        for case in ("visible_target", "missing_target"):
            result["relation_writes"].append(
                {
                    "entity": relation.entity,
                    "field": relation.field,
                    "target_entity": relation.target_entity,
                    "role": "manager",
                    "actor": "manager",
                    "action": "assign" if relation.target_entity == "$users" else "create",
                    "case": case,
                    "denied": case == "missing_target",
                    "unchanged": case == "missing_target",
                    "expected_count": 1,
                    "observed_count": 1,
                }
            )
    for entity in plan.entities:
        for field in entity.fields:
            for enabled, kind in (
                (field.searchable, "search"),
                (field.filterable, "exact"),
                (field.date_range, "date_range"),
            ):
                if not enabled:
                    continue
                for role in ("manager", "employee", "service"):
                    grant = grants.get((role, entity.name))
                    if not grant or "read" not in grant.actions:
                        continue
                    result["field_queries"].append(
                        {
                            "entity": entity.name,
                            "field": field.name,
                            "kind": kind,
                            "role": role,
                            "actor": role,
                            "cases": [
                                {
                                    "case": case,
                                    "expected_count": count,
                                    "observed_count": count,
                                    "expected_sha256": digest([count]),
                                    "observed_sha256": digest([count]),
                                    "record_set_equal": True,
                                }
                                for case, count in (
                                    ("positive", 1),
                                    ("negative", 0),
                                    ("combination", 1),
                                )
                            ],
                        }
                    )
    return result


def test_nonbusiness_native_plan_keeps_existing_managed_verification(tmp_path):
    destination, receipt, _ = verified_fixture(tmp_path)
    result = managed_verify(destination, receipt)
    assert result["passed"] is True
    projected = result["native_acceptance"]
    assert "original_installation" not in projected
    assert "fresh_database_installation" not in projected
    assert projected["source_digest"] == result["source_digest"]


@pytest.fixture
def detailed_fixture(tmp_path):
    report, receipt, spec_path = legacy_business_fixture(tmp_path)
    plan = Plan.model_validate_json(spec_path.read_text(encoding="utf-8"))
    report["template"] = receipt["template"]
    report["portable_restored"].update(
        {
            "passed": True,
            "fresh_database": True,
            "frontend_started": True,
            "installed_from_lock": True,
            "standalone_launcher": True,
            "archive_round_trip": True,
            "source_database_reused": False,
            "original_platform_imported": False,
            "model_required": False,
        }
    )
    proof = synthetic_observations(plan)
    report["business_contract"]["execution_evidence"] = proof
    report["portable_restored"]["business"]["execution_evidence"] = deepcopy(proof)
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["pages"].extend(
            login_shell_observation(actor) for actor in ("manager", "employee", "service")
        )
    return report, plan


def test_model_projection_preserves_executed_detail_and_all_bindings(detailed_fixture):
    report, plan = detailed_fixture
    files = {"start.py": "c" * 64, "deployment/workbench/business_probe.py": "b" * 64}
    result = native_review_evidence(report, plan, files, "a" * 64)
    assert result["source_digest"] == digest(files)
    assert result["spec_digest"] == digest(plan.model_dump())
    assert result["acceptance_sha256"] == "a" * 64
    assert result["reproduction_files"] == files
    assert result["original_installation"]["http"]["reminders"]
    assert result["fresh_database_installation"]["http"]["metrics"]
    assert result["original_installation"]["browser"]["checks"]
    assert result["deployment"]["fresh_database"] is True
    assert len(json.dumps(result).encode()) < MAX_EVIDENCE_BYTES


@pytest.mark.parametrize(
    "collection",
    [
        "reminders",
        "metrics",
        "metric_denials",
        "audit",
        "related_acl",
        "relation_writes",
        "field_queries",
    ],
)
@pytest.mark.parametrize("installation", ["original", "fresh"])
def test_every_required_executed_collection_fails_closed(
    detailed_fixture, collection, installation
):
    report, plan = detailed_fixture
    source = (
        report["business_contract"]
        if installation == "original"
        else report["portable_restored"]["business"]
    )
    source["execution_evidence"][collection] = []
    with pytest.raises(PrerequisiteError, match="执行证据"):
        native_review_evidence(report, plan, {}, "a" * 64)


@pytest.mark.parametrize(
    "change",
    [
        "old_boolean_only",
        "wrong_plan",
        "duplicate",
        "partial",
        "coerced_boolean",
        "unknown_subject",
        "wrong_role",
        "wrong_scope",
        "wrong_count",
        "changed_audit",
    ],
)
def test_partial_and_forged_observations_are_rejected(detailed_fixture, change):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    if change == "old_boolean_only":
        report["business_contract"].pop("execution_evidence")
    elif change == "wrong_plan":
        proof["spec_digest"] = "b" * 64
    elif change == "duplicate":
        proof["reminders"].append(deepcopy(proof["reminders"][0]))
    elif change == "partial":
        proof["field_queries"].pop()
    elif change == "coerced_boolean":
        proof["audit"][0]["denied"] = 1
    elif change == "unknown_subject":
        proof["reminders"][0]["entity"] = "unapproved"
    elif change == "wrong_role":
        proof["metrics"][0]["role"] = "employee"
    elif change == "wrong_scope":
        proof["metrics"][0]["scope"] = "own"
    elif change == "wrong_count":
        proof["field_queries"][0]["cases"][0]["observed_count"] = 99
    elif change == "changed_audit":
        proof["audit"][0]["after_sha256"] = "3" * 64
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


@pytest.mark.parametrize("location", ["top", "business", "browser", "proof", "deployment"])
def test_secrets_never_enter_projection_or_errors(detailed_fixture, location):
    report, plan = detailed_fixture
    secret = "Bearer sk-test-private-value postgresql://private:password@database.invalid/db"
    if location == "top":
        report["provider_response"] = {"environment": secret}
    elif location == "business":
        report["business_contract"]["browser_actors"] = {"password": secret}
    elif location == "browser":
        report["business_browser"]["pages"][0]["native_theme_tokens"] = {"token": secret}
    elif location == "proof":
        report["business_contract"]["execution_evidence"]["raw_http"] = secret
    else:
        report["portable_restored"]["archive_round_trip"] = secret
    try:
        result = native_review_evidence(report, plan, {}, "a" * 64)
    except PrerequisiteError as error:
        assert secret not in str(error)
        assert location in {"proof", "deployment"}
    else:
        assert secret not in json.dumps(result)
        assert location in {"top", "business", "browser"}


def test_unrecognized_browser_check_is_not_forwarded_as_proof(detailed_fixture):
    report, plan = detailed_fixture
    report["business_browser"]["checks"].append("password=secret")
    with pytest.raises(PrerequisiteError) as error:
        native_review_evidence(report, plan, {}, "a" * 64)
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "1", -1, 10**20])
def test_metric_values_must_be_bounded_real_numbers(detailed_fixture, value):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    proof["metrics"][0]["observed"]["value"] = value
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_excessive_collection_cannot_expand_model_context(detailed_fixture):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    proof["reminders"] = proof["reminders"] * 100
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_managed_verify_forwards_bound_evidence_without_model_call(tmp_path):
    product, receipt, _ = verified_fixture(tmp_path)
    result = managed_verify(product, receipt)
    native = result["native_acceptance"]
    assert native["source_digest"] == result["source_digest"]
    assert native["acceptance_sha256"] == result["evidence_sha256"]
    assert native["spec_digest"] == receipt["spec_digest"]
    assert "original_installation" not in native  # Non-business fixture has no invented probes.


def test_realistic_customer_review_payload_has_room_for_all_evidence(detailed_fixture):
    from workbench.domain import ModelReview
    from workbench.flow import REVIEW

    report, plan = detailed_fixture
    # Exercise peer observations as well as role-level checks. This remains a
    # synthetic budget fixture, never an acceptance artifact.
    for business in (report["business_contract"], report["portable_restored"]["business"]):
        proof = business["execution_evidence"]
        for query in list(proof["field_queries"]):
            if query["role"] in {"employee", "service"}:
                peer = deepcopy(query)
                peer["actor"] = "other_" + query["role"]
                proof["field_queries"].append(peer)
    review = native_review_evidence(report, plan, {}, "a" * 64)
    payload = {
        "requirement": (ROOT / "examples/requirements/customer-service-contract.md").read_text(
            encoding="utf-8"
        ),
        "plan": plan.model_dump(),
        "independent_evidence": {"passed": True, "native_acceptance": review},
        "previous_review": {"uncovered_requirements": ["bounded previous finding"] * 7},
    }
    total = (
        len(json.dumps(payload, ensure_ascii=False))
        + len(REVIEW)
        + len(json.dumps(ModelReview.model_json_schema(), ensure_ascii=False))
    )
    assert total < 95_000  # Keep space for the gateway's system/repair scaffolding.
    proof = review["original_installation"]["http"]
    assert proof["field_query_case_columns"] == [
        "case",
        "expected_count",
        "observed_count",
        "record_set_equal",
    ]
    assert proof["field_queries"][0]["cases"][0] == ["positive", 1, 1, True]


def test_alternate_query_requires_a_distinct_exact_result_set(detailed_fixture):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    query = proof["field_queries"][0]
    query["cases"][1].update(case="alternate", expected_count=1, observed_count=1)
    validate_execution_evidence(proof, plan)
    query["cases"][1]["expected_sha256"] = query["cases"][0]["expected_sha256"]
    query["cases"][1]["observed_sha256"] = query["cases"][0]["observed_sha256"]
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_multiple_searchable_fields_do_not_invent_a_second_q_operand(detailed_fixture):
    _, plan = detailed_fixture
    plan = plan.model_copy(deep=True)
    for field in next(e for e in plan.entities if e.name == "tasks").fields:
        field.filterable = False
        field.date_range = False
    proof = synthetic_observations(plan)
    for query in proof["field_queries"]:
        if query["entity"] == "tasks":
            query["cases"] = [case for case in query["cases"] if case["case"] != "combination"]
    validate_execution_evidence(proof, plan)
    # Independent q + category criteria still require a real combined query.
    for query in proof["field_queries"]:
        if query["entity"] == "customers":
            query["cases"] = [case for case in query["cases"] if case["case"] != "combination"]
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_model_review_receives_full_bound_projection_with_mock_only(detailed_fixture, settings):
    from workbench.domain import ModelReview
    from workbench.flow import Workflow

    report, plan = detailed_fixture
    projection = native_review_evidence(report, plan, {}, "a" * 64)
    settings.model_review = True
    observed = []

    class MockReviewer:
        def complete(self, run, key, instruction, payload, schema):
            observed.append(payload["independent_evidence"]["native_acceptance"])
            return ModelReview(summary="Synthetic transport test only")

    Workflow(settings, None, MockReviewer()).model_review(
        {
            "run_id": "mock-review",
            "attempt": 0,
            "plan": plan.model_dump(),
            "requirement": {},
            "verification": {"passed": True, "native_acceptance": projection},
        }
    )
    assert observed == [projection]


def test_oversized_acceptance_is_rejected_before_hashing(tmp_path, monkeypatch):
    import workbench.native_delivery as delivery

    product, receipt, report = verified_fixture(tmp_path)
    monkeypatch.setattr(delivery, "MAX_ACCEPTANCE_BYTES", report.stat().st_size - 1)
    monkeypatch.setattr(delivery, "sha", lambda *_: pytest.fail("Oversized report was read"))
    with pytest.raises(PrerequisiteError, match="大小"):
        managed_verify(product, receipt)


def login_shell_observation(actor="manager"):
    """Unit fixture matching the executed Fastapi browser producer's shell shape."""
    return {
        "role": actor,
        "route": "/module_rnd/customers",
        "rendered": True,
        "native_shell_visible": True,
        "native_component_family": "Fa/Element Plus",
        "native_theme_tokens": {"--el-color-primary": "#5D87FF", "--el-font-size-base": "14px"},
        "real_login": True,
        "native_menu_received": True,
    }


def test_fastapi_login_shells_are_distinct_from_entity_form_observations(detailed_fixture):
    report, plan = detailed_fixture
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
        browser["pages"].extend(login_shell_observation(actor) for actor in actors)
        browser["checks"].extend(f"{actor}:real_native_login_menu_shell" for actor in actors)
    original = deepcopy(report)
    projection = native_review_evidence(report, plan, {}, "a" * 64)
    for installation in ("original_installation", "fresh_database_installation"):
        browser = projection[installation]["browser"]
        assert {page["entity"] for page in browser["pages"]} == {e.name for e in plan.entities}
        assert browser["login_shells"] == [
            {
                "actor": actor,
                "rendered": True,
                "native_shell_visible": True,
                "real_login": True,
                "native_menu_received": True,
            }
            for actor in actors
        ]
        assert "route" not in json.dumps(browser)
        assert "#5D87FF" not in json.dumps(browser)
    assert report == original


@pytest.mark.parametrize("installation", ["original", "fresh"])
@pytest.mark.parametrize(
    "change",
    [
        "unknown_actor",
        "unknown_shape",
        "missing_login",
        "failed_login",
        "coerced_login",
        "unapproved_route",
        "wrong_family",
        "missing_theme",
        "missing_check",
        "duplicate_actor",
        "entity_disguised_as_shell",
        "missing_entity",
        "failed_entity",
    ],
)
def test_shell_acceptance_cannot_hide_invalid_or_missing_page_proof(
    detailed_fixture, installation, change
):
    report, plan = detailed_fixture
    browser = (
        report["business_browser"]
        if installation == "original"
        else report["portable_restored"]["browser"]
    )
    shell = next(page for page in browser["pages"] if page.get("role") == "manager")
    if change == "unknown_actor":
        shell["role"] = "secret-private-role"
    elif change == "unknown_shape":
        shell["arbitrary_page"] = "secret-private-value"
    elif change == "missing_login":
        shell.pop("real_login")
    elif change == "failed_login":
        shell["real_login"] = False
    elif change == "coerced_login":
        shell["real_login"] = 1
    elif change == "unapproved_route":
        shell["route"] = "/secret-private-route"
    elif change == "wrong_family":
        shell["native_component_family"] = "generic"
    elif change == "missing_theme":
        shell["native_theme_tokens"] = {}
    elif change == "missing_check":
        browser["checks"].remove("manager:real_native_login_menu_shell")
    elif change == "duplicate_actor":
        browser["pages"].append(deepcopy(shell))
    elif change == "entity_disguised_as_shell":
        browser["pages"][0].pop("entity")
    elif change == "missing_entity":
        browser["pages"].pop(0)
    elif change == "failed_entity":
        browser["pages"][0]["real_list_request"] = False
    with pytest.raises(PrerequisiteError) as error:
        native_review_evidence(report, plan, {}, "a" * 64)
    assert "secret-private" not in str(error.value)


@pytest.mark.parametrize("installation", ["original", "fresh"])
@pytest.mark.parametrize("missing", ["manager", "employee", "service", "all", "extra_check"])
def test_every_fastapi_login_check_requires_its_typed_shell_observation(
    detailed_fixture, installation, missing
):
    report, plan = detailed_fixture
    browser = (
        report["business_browser"]
        if installation == "original"
        else report["portable_restored"]["browser"]
    )
    if missing == "extra_check":
        browser["checks"].append("other_service:real_native_login_menu_shell")
    else:
        browser["pages"] = [
            page
            for page in browser["pages"]
            if "entity" in page or missing != "all" and page.get("role") != missing
        ]
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_lower_level_projection_does_not_invent_unclaimed_logins(detailed_fixture):
    report, plan = detailed_fixture
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["checks"] = [
            check
            for check in browser["checks"]
            if not check.endswith(":real_native_login_menu_shell")
        ]
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
    projected = native_review_evidence(report, plan, {}, "a" * 64)
    assert projected["original_installation"]["browser"]["login_shells"] == []
    assert projected["fresh_database_installation"]["browser"]["login_shells"] == []
    # Production's preceding business gate still requires genuine login checks.
    from workbench.business_browser import require_business_browser

    with pytest.raises(ValueError, match="real role login"):
        require_business_browser(report["business_browser"], plan, "fastapiadmin")


def test_relation_column_projection_is_lossless_and_hashes_complete_proof(detailed_fixture):
    from workbench.native_evidence import RelatedACL, RelationWrite, execution_summary

    report, plan = detailed_fixture
    raw = report["business_contract"]["execution_evidence"]
    original = deepcopy(raw)
    compact = execution_summary(raw, plan)
    assert compact["execution_sha256"] == digest(raw)
    assert compact["version"] == raw["version"] == 1
    assert compact["projection_version"] == 2
    for collection, schema, key in (
        ("relation_writes", RelationWrite, "relation_write_columns"),
        ("related_acl", RelatedACL, "related_acl_columns"),
    ):
        assert compact[key] == list(schema.model_fields)
        expanded = [dict(zip(compact[key], row, strict=True)) for row in compact[collection]]
        assert expanded == raw[collection]
    assert raw == original


@pytest.mark.parametrize("collection", ["relation_writes", "related_acl"])
def test_invalid_relation_observation_is_rejected_before_compaction(detailed_fixture, collection):
    report, plan = detailed_fixture
    report["business_contract"]["execution_evidence"][collection][0]["observed_count"] += 1
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_exact_approved_fastapi_plan_protocol_projection_fits_unchanged_budget(detailed_fixture):
    """Protocol mocks exercise producer cardinality, not native runtime acceptance."""
    import hashlib

    from test_native_business_probes import protocol

    from workbench.business_probe import verify_scoped_metrics
    from workbench.domain import ModelReview
    from workbench.flow import REVIEW
    from workbench.native_business_probe import verify_native_execution

    path = ROOT / "tests/fixtures/customer_approved_replays/fastapi-0e8.json"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4"
    )
    plan = Plan.model_validate_json(raw)
    before = plan.model_dump()
    proof = synthetic_observations(plan)
    for key, value in proof.items():
        if isinstance(value, list) and key != "reminders":
            proof[key] = []
    with protocol("fastapiadmin", plan=plan) as (oracle, _, _, _):
        verify_native_execution(
            plan,
            oracle.manager,
            {actor: value for actor, value in oracle.actors.items() if actor != "manager"},
            oracle.records,
            proof,
        )
        for actor, (_, client) in oracle.actors.items():
            verify_scoped_metrics(client, plan, actor.removeprefix("other_"), actor, proof)
    assert len(proof["relation_writes"]) == 64
    assert len(proof["field_queries"]) == 49
    assert validate_execution_evidence(proof, plan) == proof
    report, _ = detailed_fixture
    report["spec_digest"] = digest(plan.model_dump())
    for business in (report["business_contract"], report["portable_restored"]["business"]):
        business["execution_evidence"] = deepcopy(proof)
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["spec_digest"] = report["spec_digest"]
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
        browser["pages"].extend(login_shell_observation(actor) for actor in actors)
        browser["checks"].extend(f"{actor}:real_native_login_menu_shell" for actor in actors)
    files = {"start.py": "b" * 64, "deployment/workbench/business_probe.py": "c" * 64}
    projected = native_review_evidence(report, plan, files, "a" * 64)
    assert projected["version"] == 2
    assert MAX_EVIDENCE_BYTES == 64_000
    assert len(json.dumps(projected, separators=(",", ":")).encode()) < MAX_EVIDENCE_BYTES
    assert projected["source_digest"] == digest(files)
    assert projected["acceptance_sha256"] == "a" * 64
    for installation in ("original_installation", "fresh_database_installation"):
        assert projected[installation]["http"]["execution_sha256"] == digest(proof)
    uncompressed = deepcopy(projected)
    for installation in ("original_installation", "fresh_database_installation"):
        http = uncompressed[installation]["http"]
        for collection, key in (
            ("relation_writes", "relation_write_columns"),
            ("related_acl", "related_acl_columns"),
        ):
            columns = http.pop(key)
            http[collection] = [dict(zip(columns, row, strict=True)) for row in http[collection]]
    assert len(json.dumps(uncompressed, separators=(",", ":")).encode()) > MAX_EVIDENCE_BYTES
    payload = {
        "requirement": (ROOT / "examples/requirements/customer-service-contract.md").read_text(
            encoding="utf-8"
        ),
        "plan": plan.model_dump(),
        "independent_evidence": {"passed": True, "native_acceptance": projected},
        "previous_review": {"uncovered_requirements": ["bounded previous finding"] * 7},
    }
    size = (
        len(json.dumps(payload, ensure_ascii=False))
        + len(REVIEW)
        + len(json.dumps(ModelReview.model_json_schema(), ensure_ascii=False))
    )
    assert size < 95_000
    assert plan.model_dump() == before
