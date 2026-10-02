"""Unit-only protocol/codec fixtures, never substitute for native Actions receipts."""

import json
from copy import deepcopy

import httpx
import pytest

from workbench.domain import Plan, digest
from workbench.settings import ROOT
from workbench.yudao_navigation_checks import (
    ACTORS,
    UNAVAILABLE_IDS,
    check_installed_navigation,
    decode_navigation,
    encode_navigation,
    expected_entities,
    expected_permissions,
    validate_navigation,
    validate_sidebar,
)


def synthetic_navigation(plan):
    rows, browser = [], []
    for actor in ACTORS:
        roots = ["/infra", "/system", "/workbench"] if actor == "manager" else ["/workbench"]
        entities = expected_entities(plan, actor)
        permissions = expected_permissions(plan, actor)
        rows.append(
            {
                "actor": actor,
                "expected_roots": roots,
                "observed_roots": roots,
                "expected_entities": entities,
                "observed_entities": entities,
                "auth_menu_count": len(roots) + len(entities),
                "direct_menu_count": 120,
                "auth_ids_sha256": digest(entities),
                "direct_ids_sha256": "a" * 64,
                "expected_permissions": permissions,
                "observed_permissions": permissions,
                "expected_permission_count": len(permissions),
                "observed_permission_count": len(permissions),
                "expected_permissions_sha256": digest(permissions),
                "observed_permissions_sha256": digest(permissions),
                "unsupported_count": 0,
                "direct_consistent": True,
                "acl_exact": True,
                "admin_api_denied": actor != "manager",
            }
        )
        browser.append(
            {
                "actor": actor,
                "expected_roots": roots,
                "observed_roots": roots,
                "expected_entities": entities,
                "observed_entities": entities,
                "rendered_entities": entities,
                "sidebar_link_count": len(entities) + 2,
                "unavailable_count": 0,
                "native_sidebar_inspected": True,
                "generated_links_visible": True,
            }
        )
    return {
        "version": 1,
        "spec_digest": digest(plan.model_dump()),
        "negative_get_ids": list(UNAVAILABLE_IDS),
        "negative_get_count": len(UNAVAILABLE_IDS),
        "positive_get_ids": [4, 19],
        "base_features": [
            {"name": name, "http_status": 200, "expected_minimum": 1, "observed_count": 1}
            for name in ("dictionary_types", "dictionary_data", "api_docs")
        ],
        "actors": rows,
    }, browser


@pytest.fixture
def plan():
    return Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )


def test_navigation_codec_is_lossless_named_and_bound_to_full_raw_hash(plan):
    http, browser = synthetic_navigation(plan)
    validate_navigation(http, plan)
    validate_sidebar(browser, plan)
    for raw, flag in ((http, False), (browser, True)):
        encoded = encode_navigation(raw, browser=flag)
        assert decode_navigation(encoded) == raw
        assert encoded["raw_sha256"] == digest(raw)
        assert "expected_entities" in encoded["columns"]
        assert "observed_entities" in encoded["columns"]
        assert len(json.dumps(encoded)) < len(json.dumps(raw))
        for alteration in ("hash", "value", "foreign_column", "bool_index", "extra"):
            broken = deepcopy(encoded)
            if alteration == "hash":
                broken["raw_sha256"] = "f" * 64
            elif alteration == "value":
                broken["values"][broken["rows"][0][0]] = "employee"
            elif alteration == "foreign_column":
                broken["columns"][0] = "untrusted"
            elif alteration == "bool_index":
                broken["rows"][0][0] = True
            else:
                broken["raw_secret"] = "not-allowed"
            with pytest.raises((ValueError, TypeError)):
                decode_navigation(broken)


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "foreign",
        "missing_actor",
        "extra",
        "unsupported",
        "changed_acl",
        "changed_permission",
        "numeric_true",
        "missing_direct_negative",
        "false_positive",
        "restart_changed",
    ],
)
def test_navigation_proof_rejects_missing_forged_foreign_and_tampered_values(plan, fault):
    proof, _ = synthetic_navigation(plan)
    if fault == "missing":
        proof = None
    elif fault == "foreign":
        proof["spec_digest"] = "0" * 64
    elif fault == "missing_actor":
        proof["actors"].pop()
    elif fault == "extra":
        proof["raw_http"] = "secret"
    elif fault == "unsupported":
        proof["actors"][0]["observed_roots"].append("/crm")
    elif fault == "changed_acl":
        proof["actors"][1]["observed_entities"] = []
    elif fault == "changed_permission":
        proof["actors"][1]["observed_permissions_sha256"] = "b" * 64
    elif fault == "numeric_true":
        proof["actors"][0]["acl_exact"] = 1
    elif fault == "missing_direct_negative":
        proof["negative_get_ids"].pop()
    elif fault == "false_positive":
        proof["positive_get_ids"] = []
    else:
        proof["actors"][1]["expected_permission_count"] += 1
    with pytest.raises((ValueError, TypeError)):
        validate_navigation(proof, plan)


@pytest.mark.parametrize(
    "fault", ["missing_actor", "unavailable", "not_rendered", "fake_flag", "foreign_root"]
)
def test_sidebar_proof_requires_real_positive_negative_and_acl_values(plan, fault):
    _, proof = synthetic_navigation(plan)
    if fault == "missing_actor":
        proof.pop()
    elif fault == "unavailable":
        proof[0]["unavailable_count"] = 1
    elif fault == "not_rendered":
        proof[0]["rendered_entities"] = []
    elif fault == "fake_flag":
        proof[0]["native_sidebar_inspected"] = 1
    else:
        proof[1]["observed_roots"] = ["/system", "/workbench"]
    with pytest.raises((ValueError, TypeError)):
        validate_sidebar(proof, plan)


def protocol_fixture(plan, fault):
    full = []

    def add(identifier, parent, kind, path="", component="", permission=""):
        full.append(
            {
                "id": identifier,
                "parentId": parent,
                "type": kind,
                "path": path,
                "component": component,
                "permission": permission,
                "status": 0,
            }
        )

    add(1, 0, 1, "/system")
    add(2, 0, 1, "/infra")
    add(1000, 0, 1, "/workbench")
    for identifier in (4, 5, 6, 9, 17, 18, 19, 20, 565):
        add(
            identifier,
            1 if identifier < 10 else 2,
            2,
            "installed",
            "system/user/index" if identifier < 10 else "infra/codegen/index",
        )
    targets = {entity.name: {"entity": entity.name} for entity in plan.entities}
    for index, entity in enumerate(plan.entities):
        identifier = 1100 + index * 10
        add(
            identifier,
            1000,
            2,
            "wb-" + entity.name,
            "infra/wb" + entity.name.replace("_", "") + "/index",
        )
        for offset, action in enumerate(("query", "create", "update", "delete")):
            add(
                identifier + offset + 1,
                identifier,
                3,
                permission="infra:wb-" + entity.name + ":" + action,
            )

    class Client:
        def __init__(self, actor):
            self.actor, self.targets, self.http = actor, targets, self

        def get(self, path, **kwargs):
            if path == "/doc.html":
                return httpx.Response(
                    200,
                    text="<html>Native resource fixture</html>",
                    headers={"content-type": "text/html"},
                    request=httpx.Request("GET", "http://127.0.0.1" + path),
                )
            if "/dict-" in path:
                return httpx.Response(
                    200,
                    json={
                        "code": 0,
                        "data": {"list": [{"id": 1}]} if path.endswith("/page") else [{"id": 1}],
                    },
                    request=httpx.Request("GET", "http://127.0.0.1" + path),
                )
            return httpx.Response(
                200,
                json={"code": 0 if fault == "admin_permission_leak" else 403},
                request=httpx.Request("GET", "http://127.0.0.1" + path),
            )

        def call(self, method, path, **kwargs):
            if path.endswith("/menu/list"):
                return full + (
                    [{"id": 480, "parentId": 0, "path": "/crm"}]
                    if fault == "unavailable_root"
                    else []
                )
            if path.endswith("/menu/get"):
                identifier = kwargs["params"]["id"]
                return next(
                    (row for row in full if row["id"] == identifier),
                    {"id": identifier} if fault == "direct_get_leak" else None,
                )
            if path.endswith("/list-all-simple"):
                return full + ([{"id": 480}] if fault == "simple_leak" else [])
            assert path.endswith("/get-permission-info")
            chosen = (
                full
                if self.actor == "manager"
                else [row for row in full if row["id"] == 1000 or row["id"] >= 1100]
            )
            permissions = (
                sorted({row["permission"] for row in full if row["permission"]})
                if self.actor == "manager"
                else expected_permissions(plan, self.actor)
            )
            entities = expected_entities(plan, self.actor)
            tree = []
            for row in chosen:
                if row["parentId"] != 0:
                    continue
                entry = {
                    **row,
                    "children": [
                        dict(child)
                        for child in chosen
                        if child["parentId"] == row["id"]
                        and child["type"] != 3
                        and (
                            row["id"] != 1000
                            or child["component"].split("/")[1][2:]
                            in [entity.replace("_", "") for entity in entities]
                        )
                    ],
                }
                tree.append(entry)
            if fault == "acl_leak" and self.actor != "manager":
                tree.append({"id": 1, "parentId": 0, "path": "/system"})
            if fault == "permission_leak" and self.actor != "manager":
                permissions.append("system:user:query")
            return {"menus": tree, "permissions": permissions}

    manager = Client("manager")
    actors = {actor: ("fixture", Client(actor)) for actor in ACTORS if actor != "manager"}
    return manager, actors


@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "unavailable_root",
        "direct_get_leak",
        "simple_leak",
        "acl_leak",
        "permission_leak",
        "admin_permission_leak",
    ],
)
def test_actual_http_probe_rejects_unavailable_menu_and_acl_faults(plan, fault):
    manager, actors = protocol_fixture(plan, fault)
    if fault == "none":
        validate_navigation(check_installed_navigation(plan, manager, actors), plan)
    else:
        with pytest.raises(AssertionError):
            check_installed_navigation(plan, manager, actors)


def projection_fixture(tmp_path):
    from test_native_business_evidence import evidence
    from test_native_review_evidence import synthetic_observations

    report, receipt, spec = evidence(tmp_path, "yudao-vben")
    plan = Plan.model_validate_json(spec.read_text(encoding="utf-8"))
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
    raw = synthetic_observations(plan)
    for business in (report["business_contract"], report["portable_restored"]["business"]):
        business["execution_evidence"] = deepcopy(raw)
    return report, plan


def test_production_projection_roundtrips_all_navigation_and_existing_collection_values(tmp_path):
    from workbench.native_evidence import Metric, execution_summary, native_review_evidence
    from workbench.yudao_navigation_checks import decode_observation_rows

    report, plan = projection_fixture(tmp_path)
    result = native_review_evidence(report, plan, {}, "f" * 64)
    assert result["acceptance_sha256"] == "f" * 64
    assert len(result["installed_navigation_proofs"]) == 2
    for label, business, browser in (
        ("original_installation", report["business_contract"], report["business_browser"]),
        (
            "fresh_database_installation",
            report["portable_restored"]["business"],
            report["portable_restored"]["browser"],
        ),
    ):
        refs = result[label]["navigation"]
        for key in ("http", "restart_http"):
            assert (
                decode_navigation(result["installed_navigation_proofs"][refs[key]])
                == business["installed_navigation"]
            )
        assert (
            decode_navigation(result["installed_navigation_proofs"][refs["browser"]])
            == browser["installed_navigation"]
        )
        prior = execution_summary(business["execution_evidence"], plan)
        assert prior["execution_sha256"] == result[label]["http"]["execution_sha256"]
        for collection, columns in (
            ("metrics", list(Metric.model_fields)),
            ("field_queries", ["entity", "field", "kind", "role", "actor", "cases"]),
        ):
            encoded = result[label]["http"][collection]
            assert decode_observation_rows(encoded, columns) == prior[collection]
            broken = deepcopy(encoded)
            broken["rows"][0][0] = "tampered"
            with pytest.raises(ValueError):
                decode_observation_rows(broken, columns)


@pytest.mark.parametrize("location", ["original", "fresh", "restart", "browser"])
@pytest.mark.parametrize("fault", ["missing", "foreign", "altered"])
def test_production_projection_requires_current_bound_navigation(tmp_path, location, fault):
    from workbench.generator import PrerequisiteError
    from workbench.native_evidence import native_review_evidence

    report, plan = projection_fixture(tmp_path)
    if location == "browser":
        report["business_browser"]["installed_navigation"][0]["rendered_entities"] = []
    else:
        parent = (
            report["business_contract"]
            if location != "fresh"
            else report["portable_restored"]["business"]
        )
        key = "installed_navigation_restart" if location == "restart" else "installed_navigation"
        if fault == "missing":
            parent.pop(key)
        elif fault == "foreign":
            parent[key]["spec_digest"] = "1" * 64
        else:
            parent[key]["actors"][0]["unsupported_count"] = 1
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "f" * 64)


def test_raw_acceptance_hash_binds_navigation_changes_before_projection(tmp_path):
    from test_native_managed import verified_fixture

    from workbench.generator import PrerequisiteError
    from workbench.native_delivery import managed_verify

    product, receipt, _ = verified_fixture(tmp_path)
    path = product.parent / "native-evidence/acceptance.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["installed_navigation"] = {"tampered": True}
    path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(PrerequisiteError, match="丢失或已改变"):
        managed_verify(product, receipt)


@pytest.mark.parametrize("approved", [False, True])
def test_full_yudao_protocol_projection_with_actual_permission_values_fits_unchanged_budget(
    tmp_path, approved
):
    from test_native_business_probes import protocol
    from test_native_review_evidence import synthetic_observations
    from test_yudao_installed_navigation import source_capabilities

    from workbench.business_probe import verify_scoped_metrics
    from workbench.native_business_probe import verify_native_execution
    from workbench.native_evidence import MAX_EVIDENCE_BYTES, native_review_evidence

    report, plan = projection_fixture(tmp_path)
    if approved:
        plan = Plan.model_validate_json(
            (ROOT / "tests/fixtures/customer_approved_replays/yudao-1d7.json").read_text(
                encoding="utf-8"
            )
        )
    proof = synthetic_observations(plan)
    for key, value in proof.items():
        if isinstance(value, list) and key != "reminders":
            proof[key] = []
    with protocol("yudao-vben", plan=plan) as (oracle, _, _, _):
        verify_native_execution(
            plan,
            oracle.manager,
            {actor: value for actor, value in oracle.actors.items() if actor != "manager"},
            oracle.records,
            proof,
        )
        for actor, (_, client) in oracle.actors.items():
            verify_scoped_metrics(client, plan, actor.removeprefix("other_"), actor, proof)
    navigation, browser = synthetic_navigation(plan)
    permissions = sorted(
        source_capabilities()[2] | set(navigation["actors"][0]["expected_permissions"])
    )
    row = navigation["actors"][0]
    for key in ("expected_permissions", "observed_permissions"):
        row[key] = permissions
    for key in ("expected_permission_count", "observed_permission_count"):
        row[key] = len(permissions)
    for key in ("expected_permissions_sha256", "observed_permissions_sha256"):
        row[key] = digest(permissions)
    report["spec_digest"] = digest(plan.model_dump())
    for contract in (report["business_contract"], report["portable_restored"]["business"]):
        contract["execution_evidence"] = deepcopy(proof)
        contract["installed_navigation"] = deepcopy(navigation)
        contract["installed_navigation_restart"] = deepcopy(navigation)
    for ui in (report["business_browser"], report["portable_restored"]["browser"]):
        ui["spec_digest"] = report["spec_digest"]
        ui["installed_navigation"] = deepcopy(browser)
    files = {"start.py": "b" * 64, "deployment/workbench/business_probe.py": "c" * 64}
    projected = native_review_evidence(report, plan, files, "d" * 64)
    assert MAX_EVIDENCE_BYTES == 64_000
    assert len(json.dumps(projected, separators=(",", ":")).encode()) <= MAX_EVIDENCE_BYTES
    assert projected["source_digest"] == digest(files)
    for label in ("original_installation", "fresh_database_installation"):
        assert projected[label]["http"]["execution_sha256"] == digest(proof)
        raw = decode_navigation(
            projected["installed_navigation_proofs"][projected[label]["navigation"]["http"]]
        )
        assert raw == navigation and raw["actors"][0]["observed_permissions"] == permissions
