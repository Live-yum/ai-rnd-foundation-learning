"""Independent read-only HTTP oracles for the pinned mini backend and approved ACL.

No generated capability manifest is consulted. This tests actual authenticated
menu APIs, including negative item reads, and is reused after process restart.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from workbench.domain import Name, digest
from workbench.native_checks import denied, flatten, payload

ACTORS = ("manager", "employee", "other_employee", "service", "other_service")
# Original pinned seed IDs: absent module roots and optional external services.
# These are test targets, never a product-side label/ID filtering policy.
UNAVAILABLE_IDS = (
    14,
    16,
    85,
    114,
    148,
    207,
    272,
    373,
    449,
    480,
    597,
    791,
    860,
    959,
    1348,
    1418,
    1476,
    1637,
    1894,
    8000,
    8200,
)
ACTION_PERMISSION = {
    "read": "query",
    "read_history": "query",
    "read_audit": "query",
    "read_metrics": "query",
    "create": "create",
    "update": "update",
    "assign": "update",
    "transition": "update",
    "add_note": "update",
    "archive": "delete",
}


def expected_entities(plan, actor):
    return sorted(
        p.entity
        for p in plan.business.permissions
        if p.role == actor.removeprefix("other_") and "read" in p.actions
    )


def expected_permissions(plan, actor):
    return sorted(
        {
            "infra:wb-" + p.entity.replace("_", "-") + ":" + ACTION_PERMISSION[action]
            for p in plan.business.permissions
            if p.role == actor.removeprefix("other_")
            for action in p.actions
        }
    )


def check_installed_navigation(plan, manager, actors):
    targets = manager.targets
    component_entities = {"infra/wb" + name.replace("_", "") + "/index": name for name in targets}
    full = manager.call("GET", "/admin-api/system/menu/list")
    full_by_id = {row["id"]: row for row in full}
    assert len(full_by_id) == len(full) and full, (
        "Native menu API duplicated or omitted installed rows"
    )
    assert {row["path"] for row in full if row["parentId"] == 0} == {
        "/system",
        "/infra",
        "/workbench",
    }, "Admin menu API exposed unavailable module or lost installed roots"
    assert {4, 5, 6, 9, 17, 18, 19, 20, 565} <= set(full_by_id), (
        "Legitimate installed system/infra pages disappeared"
    )
    assert not set(UNAVAILABLE_IDS) & set(full_by_id), (
        "Unavailable native module/service is exposed"
    )
    for identifier in UNAVAILABLE_IDS:
        assert (
            manager.call("GET", "/admin-api/system/menu/get", params={"id": identifier}) is None
        ), "Unsupported direct menu GET leaked metadata"
    for identifier in (4, 19):
        assert (
            manager.call("GET", "/admin-api/system/menu/get", params={"id": identifier})["id"]
            == identifier
        ), "Installed direct menu GET disappeared"
    base_features = []
    for name, path, query in (
        ("dictionary_types", "/admin-api/system/dict-type/page", {"pageNo": 1, "pageSize": 1}),
        ("dictionary_data", "/admin-api/system/dict-data/simple-list", {}),
    ):
        response = manager.http.get(path, params=query)
        value = payload(response)
        rows = value["list"] if isinstance(value, dict) else value
        assert response.status_code == 200 and isinstance(rows, list) and rows, (
            "Installed Dictionary API did not execute"
        )
        base_features.append(
            {
                "name": name,
                "http_status": response.status_code,
                "expected_minimum": 1,
                "observed_count": len(rows),
            }
        )
    docs = manager.http.get("/doc.html")
    assert (
        docs.status_code == 200 and "text/html" in docs.headers.get("content-type", "").lower()
    ), "Installed native API documentation resource is unavailable"
    assert "<html" in docs.text.lower(), "Native API documentation resource was not HTML"
    base_features.append(
        {
            "name": "api_docs",
            "http_status": docs.status_code,
            "expected_minimum": 1,
            "observed_count": 1,
        }
    )

    def enabled(row):
        seen = set()
        while row:
            if row["id"] in seen or row.get("status") != 0:
                return False
            seen.add(row["id"])
            if row["parentId"] == 0:
                return True
            row = full_by_id.get(row["parentId"])
        return False

    expected_simple = {row["id"] for row in full if enabled(row)}
    proofs = []
    for actor, client in [
        ("manager", manager),
        *((label, actors[label][1]) for label in ACTORS if label != "manager"),
    ]:
        info = client.call("GET", "/admin-api/system/auth/get-permission-info")
        menus = list(flatten(info["menus"]))
        ids = {row["id"] for row in menus}
        assert len(ids) == len(menus) and ids <= set(full_by_id), (
            "Auth menus disagree with installed direct menu API"
        )
        roots = sorted(row["path"] for row in info["menus"])
        expected_roots = (
            ["/infra", "/system", "/workbench"] if actor == "manager" else ["/workbench"]
        )
        assert roots == expected_roots, "Role menu contains unavailable or ungranted native module"
        entities = sorted(
            component_entities[row["component"].removesuffix(".vue")]
            for row in menus
            if (row.get("component") or "").removesuffix(".vue") in component_entities
        )
        expected = expected_entities(plan, actor)
        assert entities == expected, "Native Workbench menu differs from approved role read grants"
        simple = client.call("GET", "/admin-api/system/menu/list-all-simple")
        simple_ids = {row["id"] for row in simple}
        assert len(simple_ids) == len(simple) and simple_ids == expected_simple, (
            "Direct simple-menu API differs from installed enabled menu metadata"
        )
        permission_values = sorted(value for value in info["permissions"] if value)
        if actor == "manager":
            expected_values = sorted(
                {
                    row["permission"]
                    for row in full
                    if row["id"] in expected_simple and row.get("permission")
                }
            )
        else:
            expected_values = expected_permissions(plan, actor)
            denied(client.http.get("/admin-api/system/menu/list"))
            denied(client.http.get("/admin-api/system/menu/get", params={"id": 4}))
        assert permission_values == expected_values, (
            "Native permission set expanded or dropped approved grants"
        )
        proofs.append(
            {
                "actor": actor,
                "expected_roots": expected_roots,
                "observed_roots": roots,
                "expected_entities": expected,
                "observed_entities": entities,
                "auth_menu_count": len(ids),
                "direct_menu_count": len(simple_ids),
                "auth_ids_sha256": digest(sorted(ids)),
                "direct_ids_sha256": digest(sorted(simple_ids)),
                "expected_permissions": expected_values,
                "observed_permissions": permission_values,
                "expected_permission_count": len(expected_values),
                "observed_permission_count": len(permission_values),
                "expected_permissions_sha256": digest(expected_values),
                "observed_permissions_sha256": digest(permission_values),
                "unsupported_count": len(set(UNAVAILABLE_IDS) & (ids | simple_ids)),
                "direct_consistent": True,
                "acl_exact": True,
                "admin_api_denied": actor != "manager",
            }
        )
    return {
        "version": 1,
        "spec_digest": digest(plan.model_dump()),
        "negative_get_ids": list(UNAVAILABLE_IDS),
        "negative_get_count": len(UNAVAILABLE_IDS),
        "positive_get_ids": [4, 19],
        "base_features": base_features,
        "actors": proofs,
    }


def check_navigation_restart(template, base, token, targets, scenario, plan):
    from workbench.business_probe import BusinessClient
    from workbench.native_environment import login

    manager = BusinessClient(template, base, token, targets)
    actors = {}
    try:
        for actor in ACTORS:
            if actor == "manager":
                continue
            identity = scenario["browser_actors"][actor]
            actor_token = login(template, base, identity["username"], "BusinessTest123!")
            actors[actor] = (identity["id"], BusinessClient(template, base, actor_token, targets))
        observed = check_installed_navigation(plan, manager, actors)
        assert observed == scenario["installed_navigation"], (
            "Native menu/ACL APIs changed across process restart"
        )
        return observed
    finally:
        manager.close()
        for _, client in actors.values():
            client.close()


# Typed observations stay here so the self-contained launcher can enforce the same
# proof contract without importing the original development platform.
NavActor = Literal["manager", "employee", "other_employee", "service", "other_service"]
NavRoot = Literal["/infra", "/system", "/workbench"]
NavCount = Annotated[int, Field(strict=True, ge=0, le=10000)]
NavHash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class NavigationObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class NavigationActor(NavigationObservation):
    actor: NavActor
    expected_roots: list[NavRoot] = Field(min_length=1, max_length=3)
    observed_roots: list[NavRoot] = Field(min_length=1, max_length=3)
    expected_entities: list[Name] = Field(min_length=1, max_length=16)
    observed_entities: list[Name] = Field(min_length=1, max_length=16)
    auth_menu_count: NavCount
    direct_menu_count: NavCount
    auth_ids_sha256: NavHash
    direct_ids_sha256: NavHash
    expected_permissions: list[
        Annotated[
            str, Field(pattern=r"^(system|infra):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$", max_length=100)
        ]
    ] = Field(max_length=512)
    observed_permissions: list[
        Annotated[
            str, Field(pattern=r"^(system|infra):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$", max_length=100)
        ]
    ] = Field(max_length=512)
    expected_permission_count: NavCount
    observed_permission_count: NavCount
    expected_permissions_sha256: NavHash
    observed_permissions_sha256: NavHash
    unsupported_count: NavCount
    direct_consistent: StrictBool
    acl_exact: StrictBool
    admin_api_denied: StrictBool


class NavigationProof(NavigationObservation):
    version: Annotated[int, Field(strict=True, ge=1, le=1)]
    spec_digest: NavHash
    negative_get_ids: list[Annotated[int, Field(strict=True, gt=0)]] = Field(max_length=32)
    negative_get_count: NavCount
    positive_get_ids: list[Annotated[int, Field(strict=True, gt=0)]] = Field(max_length=8)
    base_features: list["BaseFeatureObservation"] = Field(min_length=3, max_length=3)
    actors: list[NavigationActor] = Field(min_length=5, max_length=5)


class BaseFeatureObservation(NavigationObservation):
    name: Literal["dictionary_types", "dictionary_data", "api_docs"]
    http_status: Annotated[int, Field(strict=True, ge=200, le=200)]
    expected_minimum: Annotated[int, Field(strict=True, ge=1, le=1)]
    observed_count: NavCount


class SidebarObservation(NavigationObservation):
    actor: NavActor
    expected_roots: list[NavRoot] = Field(min_length=1, max_length=3)
    observed_roots: list[NavRoot] = Field(min_length=1, max_length=3)
    expected_entities: list[Name] = Field(min_length=1, max_length=16)
    observed_entities: list[Name] = Field(min_length=1, max_length=16)
    rendered_entities: list[Name] = Field(min_length=1, max_length=16)
    sidebar_link_count: NavCount
    unavailable_count: NavCount
    native_sidebar_inspected: StrictBool
    generated_links_visible: StrictBool


def _require(condition):
    if not condition:
        raise ValueError("Missing or inconsistent installed native navigation proof")


def _validate_role(row, plan):
    roots = ["/infra", "/system", "/workbench"] if row.actor == "manager" else ["/workbench"]
    entities = expected_entities(plan, row.actor)
    _require(row.expected_roots == row.observed_roots == roots)
    _require(row.expected_entities == row.observed_entities == entities)


def validate_navigation(raw, plan):
    proof = NavigationProof.model_validate(raw)
    _require(proof.spec_digest == digest(plan.model_dump()))
    _require(proof.negative_get_ids == list(UNAVAILABLE_IDS))
    _require(proof.negative_get_count == len(UNAVAILABLE_IDS) and proof.positive_get_ids == [4, 19])
    _require({row.actor for row in proof.actors} == set(ACTORS))
    _require(
        {row.name for row in proof.base_features}
        == {"dictionary_types", "dictionary_data", "api_docs"}
    )
    _require(all(row.observed_count >= row.expected_minimum for row in proof.base_features))
    for row in proof.actors:
        _validate_role(row, plan)
        _require(row.auth_menu_count >= len(row.observed_roots) + len(row.observed_entities))
        _require(row.direct_menu_count >= row.auth_menu_count and row.unsupported_count == 0)
        _require(row.direct_consistent is True and row.acl_exact is True)
        _require(row.admin_api_denied is (row.actor != "manager"))
        _require(
            row.expected_permissions
            == row.observed_permissions
            == sorted(set(row.observed_permissions))
        )
        _require(
            row.expected_permission_count
            == row.observed_permission_count
            == len(row.observed_permissions)
            > 0
        )
        _require(row.expected_permissions_sha256 == digest(row.expected_permissions))
        _require(row.observed_permissions_sha256 == digest(row.observed_permissions))
        _require(row.expected_permissions_sha256 == row.observed_permissions_sha256)
        if row.actor != "manager":
            values = expected_permissions(plan, row.actor)
            _require(row.expected_permissions == values)
            _require(row.expected_permission_count == len(values))
            _require(row.expected_permissions_sha256 == digest(values))
    _require(len({row.direct_ids_sha256 for row in proof.actors}) == 1)
    _require(len({row.direct_menu_count for row in proof.actors}) == 1)
    return proof.model_dump()


def validate_sidebar(raw, plan):
    _require(isinstance(raw, list) and len(raw) == len(ACTORS))
    rows = [SidebarObservation.model_validate(row) for row in raw]
    _require({row.actor for row in rows} == set(ACTORS))
    for row in rows:
        _validate_role(row, plan)
        _require(row.rendered_entities == row.expected_entities)
        _require(
            row.sidebar_link_count >= len(row.rendered_entities) and row.unavailable_count == 0
        )
        _require(row.native_sidebar_inspected is True and row.generated_links_visible is True)
    return [row.model_dump() for row in rows]


def encode_navigation(raw, *, browser=False):
    """Lossless dictionary/table encoding; all validated values and their hash survive."""
    import json

    columns = list(SidebarObservation.model_fields if browser else NavigationActor.model_fields)
    values, indexes, rows = [], {}, []
    for observation in raw if browser else raw["actors"]:
        row = []
        for column in columns:
            value = observation[column]
            key = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            if key not in indexes:
                indexes[key] = len(values)
                values.append(value)
            row.append(indexes[key])
        rows.append(row)
    return {
        "codec_version": 1,
        "browser": browser,
        "raw_sha256": digest(raw),
        "columns": columns,
        "values": values,
        "rows": rows,
        "metadata": {}
        if browser
        else {key: value for key, value in raw.items() if key != "actors"},
    }


def decode_navigation(encoded):
    schema = SidebarObservation if encoded.get("browser") is True else NavigationActor
    _require(encoded.get("codec_version") == 1 and type(encoded.get("browser")) is bool)
    _require(
        set(encoded)
        == {"codec_version", "browser", "raw_sha256", "columns", "values", "rows", "metadata"}
    )
    _require(encoded["columns"] == list(schema.model_fields))
    _require(isinstance(encoded["values"], list) and len(encoded["values"]) <= 128)
    _require(isinstance(encoded["rows"], list) and len(encoded["rows"]) == len(ACTORS))
    rows = []
    for row in encoded["rows"]:
        _require(len(row) == len(encoded["columns"]))
        _require(all(type(index) is int and 0 <= index < len(encoded["values"]) for index in row))
        rows.append(
            schema.model_validate(
                dict(
                    zip(
                        encoded["columns"], (encoded["values"][index] for index in row), strict=True
                    )
                )
            ).model_dump()
        )
    if encoded["browser"]:
        _require(encoded["metadata"] == {})
        raw = rows
    else:
        raw = NavigationProof.model_validate({**encoded["metadata"], "actors": rows}).model_dump()
    _require(digest(raw) == encoded["raw_sha256"])
    return raw


def encode_observation_rows(raw, columns):
    """Versioned lossless outer-row compaction, preserving every existing value."""
    _require(isinstance(raw, list) and all(set(row) == set(columns) for row in raw))
    return {
        "codec_version": 1,
        "columns": columns,
        "raw_sha256": digest(raw),
        "rows": [[row[column] for column in columns] for row in raw],
    }


def decode_observation_rows(encoded, columns):
    _require(set(encoded) == {"codec_version", "columns", "raw_sha256", "rows"})
    _require(encoded["codec_version"] == 1 and type(encoded["codec_version"]) is int)
    _require(encoded["columns"] == columns and isinstance(encoded["rows"], list))
    _require(len(encoded["rows"]) <= 512)
    _require(all(isinstance(row, list) and len(row) == len(columns) for row in encoded["rows"]))
    rows = [dict(zip(columns, row, strict=True)) for row in encoded["rows"]]
    _require(digest(rows) == encoded["raw_sha256"])
    return rows
