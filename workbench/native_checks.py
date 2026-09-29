"""Exercise ORIGINAL native role APIs in the disposable lab, not generated business modules."""

from urllib.parse import urlsplit

import httpx

from workbench.native_environment import login


def successful(response):
    if response.status_code not in (200, 201):
        return False
    try:
        return response.json().get("code", 200) in (0, 200)
    except ValueError:
        return False


def payload(response):
    if not successful(response):
        # Do not put tokens, credentials or full login responses in public logs.
        raise AssertionError(f"Native API failed: {response.request.method} {response.request.url.path} HTTP {response.status_code}")
    body = response.json()
    return body.get("data", body)


def denied(response):
    try:
        code = response.json().get("code")
    except ValueError:
        code = None
    if response.status_code not in (401, 403) and code not in (401, 403):
        raise AssertionError(f"Expected authorization denial: {response.request.url.path}, HTTP {response.status_code}, code {code}")


def flatten(rows):
    for item in rows:
        yield item
        yield from flatten(item.get("children") or [])


def record_id(value):
    return value["id"] if isinstance(value, dict) else value


def check_native_permissions(template, base_url, admin_token):
    """Create only lab users/roles through real authorized APIs; never modify auth code."""
    if urlsplit(base_url).hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Native authorization tests are restricted to loopback lab servers")
    fastapi = template == "fastapiadmin"
    prefix = "" if fastapi else "/admin-api"
    listing = prefix + ("/system/user/list" if fastapi else "/system/user/page")
    info = prefix + ("/system/user/current/info" if fastapi else "/system/auth/get-permission-info")
    permission = "module_system:user:query" if fastapi else "system:user:query"
    with httpx.Client(base_url=base_url, trust_env=False, timeout=30, headers={"tenant-id": "1"}) as client:
        denied(client.get(listing))
        denied(client.get(listing, headers={"Authorization": "Bearer test1"}))
        admin = {"Authorization": "Bearer " + admin_token}
        payload(client.get(listing, headers=admin))
        menus = payload(client.get(prefix + ("/system/menu/tree" if fastapi else "/system/menu/list"), headers=admin))
        rows = list(flatten(menus))
        matching = [row for row in rows if row.get("permission") == permission]
        if len(matching) != 1:
            raise AssertionError("Native read permission was not uniquely present in menu metadata")
        by_id = {row["id"]: row for row in rows}
        selected = set()
        cursor = matching[0]
        while cursor:
            selected.add(cursor["id"])
            cursor = by_id.get(cursor.get("parent_id", cursor.get("parentId")))
        role_data = {"name": "Workbench reader", "code": "workbench_reader", "status": 0}
        role_data.update({"order": 1, "data_scope": 1} if fastapi else {"sort": 1})
        role_id = record_id(payload(client.post(prefix + "/system/role/create", json=role_data, headers=admin)))
        username, password = "workbenchreader", "NativeTest123!"
        user = {"username": username, "password": password}
        if fastapi:
            user.update({"name": "Workbench reader", "is_superuser": False, "role_ids": [role_id], "status": 0})
        else:
            user.update({"nickname": "Workbench reader"})
        user_id = record_id(payload(client.post(prefix + "/system/user/create", json=user, headers=admin)))
        if not fastapi:
            payload(client.post(prefix + "/system/permission/assign-user-role", json={"userId": user_id, "roleIds": [role_id]}, headers=admin))

        def assign(menu_ids):
            if fastapi:
                response = client.put("/system/role/permission", json={"role_ids": [role_id], "menu_ids": menu_ids, "data_scope": 1, "dept_ids": []}, headers=admin)
            else:
                response = client.post(prefix + "/system/permission/assign-role-menu", json={"roleId": role_id, "menuIds": menu_ids}, headers=admin)
            payload(response)

        # Do not assume newly created roles lack defaults: explicitly set the lab role to empty.
        assign([])
        restricted = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        denied(client.get(listing, headers=restricted))
        before = payload(client.get(info, headers=restricted))
        assert not before.get("menus"), "Empty role unexpectedly receives native menus"
        assign(sorted(selected))
        reader = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        payload(client.get(listing, headers=reader))
        after = payload(client.get(info, headers=reader))
        assert after.get("menus"), "Granted native page is absent from login/menu result"
        # A read-only role must still be unable to create roles.
        denied(client.post(prefix + "/system/role/create", json={**role_data, "code": "must_not_be_created"}, headers=reader))
        assign([])
        revoked = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        denied(client.get(listing, headers=revoked))
    return {
        "unauthenticated_denied": True,
        "mock_token_denied": True,
        "empty_role_denied": True,
        "granted_read_allowed": True,
        "menu_visibility_after_grant": True,
        "write_without_permission_denied": True,
        "revoked_read_denied": True,
        "scope": "upstream-native-system-user-page",
        "generated_modules_verified": False,
    }
