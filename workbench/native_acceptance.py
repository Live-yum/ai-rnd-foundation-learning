"""Independent HTTP checks for the ACTUAL generated modules and native RBAC APIs."""

import time
import uuid

import httpx

from workbench.native_checks import (
    await_permission,
    denied,
    flatten,
    payload,
    read_menu_ids,
    record_id,
    successful,
)
from workbench.native_environment import login


def wire_name(template, name):
    if template == "fastapiadmin":
        return name
    first, *rest = name.split("_")
    return first + "".join(piece[:1].upper() + piece[1:] for piece in rest)


def sample_record(entity, suffix="original", template="fastapiadmin", plan=None):
    if plan is not None:
        from workbench.native_business_checks import wire

        rule = next((r for r in plan.custom_rules if r.entity == entity.name), None)
        if rule:
            index = -1 if suffix == "updated" else 0
            return wire(template, rule.accept_examples[index])
    return {
        wire_name(template, f.name): (
            f"{entity.name}-{suffix}"[: f.max_length]
            if f.kind == "text"
            else (11 if suffix == "updated" else 7)
            if f.kind == "integer"
            else suffix != "updated"
        )
        for f in entity.fields
    }


def list_rows(value):
    if not isinstance(value, dict):
        raise AssertionError("Generated paginated API returned no pagination object")
    rows = value.get("items", value.get("list"))
    if not isinstance(rows, list):
        raise AssertionError("Generated paginated API omitted rows")
    return rows


def generated_crud(template, base_url, token, targets, plan):
    fastapi = template == "fastapiadmin"
    results = []
    with httpx.Client(
        base_url=base_url, timeout=30, trust_env=False, headers={"tenant-id": "1"}
    ) as client:
        admin = {"Authorization": "Bearer " + token}
        for target, entity in zip(targets, plan.entities, strict=True):
            listing = target["list"]
            denied(client.get(listing))
            denied(client.get(listing, headers={"Authorization": "Bearer test1"}))
            data = sample_record(entity, template=template, plan=plan)
            created = payload(client.post(target["api"] + "/create", json=data, headers=admin))
            identifier = record_id(created)
            assert type(identifier) is int and identifier > 0

            def get_item():
                if fastapi:
                    return payload(
                        client.get(target["api"] + f"/detail/{identifier}", headers=admin)
                    )
                return payload(
                    client.get(target["api"] + "/get", params={"id": identifier}, headers=admin)
                )

            saved = get_item()
            for key, value in data.items():
                assert saved[key] == value, f"Create/read mismatch for {key}"
            changed = sample_record(entity, "updated", template, plan)
            if fastapi:
                payload(
                    client.put(target["api"] + f"/update/{identifier}", json=changed, headers=admin)
                )
            else:
                payload(
                    client.put(
                        target["api"] + "/update", json={"id": identifier, **changed}, headers=admin
                    )
                )
            updated = get_item()
            for key, value in changed.items():
                assert updated[key] == value, f"Update/read mismatch for {key}"
            rows = list_rows(payload(client.get(listing, headers=admin)))
            assert any(row["id"] == identifier for row in rows)
            invalid = dict(data)
            required = next(f for f in entity.fields if f.required and f.kind != "boolean")
            invalid.pop(wire_name(template, required.name))
            response = client.post(target["api"] + "/create", json=invalid, headers=admin)
            assert not successful(response) and response.status_code < 500
            assert response.status_code in (400, 422) or response.json().get("code") in (
                400,
                422,
            ), "Required-field validation must return a client validation error"
            if fastapi:
                payload(
                    client.request(
                        "DELETE", target["api"] + "/delete", json=[identifier], headers=admin
                    )
                )
            else:
                payload(
                    client.delete(
                        target["api"] + "/delete", params={"id": identifier}, headers=admin
                    )
                )
            rows = list_rows(payload(client.get(listing, headers=admin)))
            assert not any(row["id"] == identifier for row in rows), (
                "Delete did not remove business item"
            )
            sample = sample_record(entity, "persistent", template, plan)
            persistent = record_id(
                payload(client.post(target["api"] + "/create", json=sample, headers=admin))
            )
            target["sample"] = next(
                str(sample[wire_name(template, f.name)]) for f in entity.fields if f.kind == "text"
            )
            results.append(
                {
                    "entity": entity.name,
                    "crud": True,
                    "required_field_rejected": True,
                    "persistent_id": persistent,
                    "persistent_data": sample,
                    "unauthenticated_denied": True,
                    "mock_token_denied": True,
                }
            )
    return results


def check_generated_persistence(template, base_url, token, targets, records):
    with httpx.Client(
        base_url=base_url,
        trust_env=False,
        timeout=30,
        headers={"Authorization": "Bearer " + token, "tenant-id": "1"},
    ) as client:
        for target, record in zip(targets, records, strict=True):
            rows = list_rows(payload(client.get(target["list"])))
            saved = next(row for row in rows if row["id"] == record["persistent_id"])
            for key, value in record["persistent_data"].items():
                assert saved[key] == value, "Native persistence changed across process restart"
    return {"process_restart_preserves_records": True, "entity_count": len(records)}


def generated_permissions(template, base_url, token, targets, plan):
    """Grant/read/create/revoke using original role APIs, never by editing auth code."""
    fastapi = template == "fastapiadmin"
    prefix = "" if fastapi else "/admin-api"
    info = prefix + ("/system/user/current/info" if fastapi else "/system/auth/get-permission-info")
    admin = {"Authorization": "Bearer " + token}
    with httpx.Client(
        base_url=base_url, trust_env=False, timeout=30, headers={"tenant-id": "1"}
    ) as client:
        rows = list(
            flatten(
                payload(
                    client.get(
                        prefix + ("/system/menu/tree" if fastapi else "/system/menu/list"),
                        headers=admin,
                    )
                )
            )
        )
        read_ids, full_ids = set(), set()
        for target in targets:
            read_ids.update(read_menu_ids(rows, target["permission"] + ":query"))
            for operation in ("query", "create", "update", "delete"):
                full_ids.update(read_menu_ids(rows, target["permission"] + ":" + operation))
        # A retry never adopts, deletes or changes an unrelated existing account.
        # Each disposable acceptance attempt owns a new bounded identifier.
        attempt_id = uuid.uuid4().hex[:12]
        role = {"name": "RND reader " + attempt_id, "code": "rnd_" + attempt_id, "status": 0}
        role.update({"order": 1, "data_scope": 3} if fastapi else {"sort": 1})
        role_id = record_id(
            payload(client.post(prefix + "/system/role/create", json=role, headers=admin))
        )
        username, password = "rnd" + attempt_id, "NativeTest123!"
        user = {"username": username, "password": password}
        user.update(
            {"name": "Generated reader", "is_superuser": False, "role_ids": [role_id], "status": 0}
            if fastapi
            else {"nickname": "Generated reader"}
        )
        user_id = record_id(
            payload(client.post(prefix + "/system/user/create", json=user, headers=admin))
        )
        if not fastapi:
            payload(
                client.post(
                    prefix + "/system/permission/assign-user-role",
                    json={"userId": user_id, "roleIds": [role_id]},
                    headers=admin,
                )
            )

        def assign(ids):
            if fastapi:
                response = client.put(
                    "/system/role/permission",
                    json={
                        "role_ids": [role_id],
                        "menu_ids": sorted(ids),
                        "data_scope": 3,
                        "dept_ids": [],
                    },
                    headers=admin,
                )
            else:
                response = client.post(
                    prefix + "/system/permission/assign-role-menu",
                    json={"roleId": role_id, "menuIds": sorted(ids)},
                    headers=admin,
                )
            payload(response)
            if fastapi:
                assigned = payload(client.get(f"/system/role/detail/{role_id}", headers=admin))
                actual = {menu["id"] for menu in assigned["menus"]}
                assert actual == set(ids), "Native role menu assignment was not committed"

        def identity():
            return {"Authorization": "Bearer " + login(template, base_url, username, password)}

        assign([])
        none = identity()
        for target in targets:
            denied(client.get(target["list"], headers=none))
        assert not payload(client.get(info, headers=none)).get("menus")
        assign(read_ids)
        reader = identity()
        if not fastapi:
            for target in targets:
                await_permission(client, target["list"], reader, True)
        menus = list(flatten(payload(client.get(info, headers=reader))["menus"]))
        assert menus, "No native menus for granted generated module"
        for target, entity in zip(targets, plan.entities, strict=True):
            assert list_rows(payload(client.get(target["list"], headers=reader))), (
                "Reader cannot see shared sample"
            )
            marker = (
                ("module_rnd/" + entity.name)
                if fastapi
                else ("infra/wb" + entity.name.replace("_", ""))
            )
            assert marker in str(menus), "Generated page is absent from native menus"
            denied(
                client.post(
                    target["api"] + "/create",
                    json=sample_record(entity, template=template, plan=plan),
                    headers=reader,
                )
            )
        assign(full_ids)
        writer = identity()
        if fastapi:
            snapshot = payload(client.get(info, headers=writer))
            permissions = {menu.get("permission") for menu in flatten(snapshot.get("menus", []))}
            expected = {target["permission"] + ":create" for target in targets}
            assert expected <= permissions, (
                "Fresh native login did not receive granted CREATE permissions: "
                + str(sorted(expected - permissions))
            )
        if not fastapi:
            time.sleep(
                61
            )  # Native CREATE decisions are cached for one minute; do not bypass the cache.
        for target, entity in zip(targets, plan.entities, strict=True):
            payload(
                client.post(
                    target["api"] + "/create",
                    json=sample_record(entity, "writer", template, plan),
                    headers=writer,
                )
            )
        assign([])
        revoked = identity()
        if not fastapi:
            for target in targets:
                await_permission(client, target["list"], revoked, False)
        for target in targets:
            denied(client.get(target["list"], headers=revoked))
        assert not payload(client.get(info, headers=revoked)).get("menus")
    return {
        "owned_user_id": user_id,
        "owned_role_id": role_id,
        "attempt_id": attempt_id,
        "empty_role_denied": True,
        "read_grant_allowed": True,
        "generated_pages_visible": True,
        "write_without_permission_denied": True,
        "write_grant_allowed": True,
        "revoke_denied": True,
        "native_auth_unmodified": True,
        "upstream_permission_cache_seconds": 0 if fastapi else 60,
        "entity_count": len(targets),
    }
