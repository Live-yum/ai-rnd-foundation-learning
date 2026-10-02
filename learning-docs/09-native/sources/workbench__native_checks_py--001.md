# workbench/native_checks.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：统一原生响应、菜单和权限断言。** 两套原生系统响应结构不同，payload/record_id等辅助函数统一读取方式。await_permission有明确超时，不用无限重试把失败伪装成通过；拒绝未认证和伪造令牌仍是必须验证的路径。

**对应关系：** native_acceptance/native_lab → native_checks → 原生HTTP。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `successful`（L11–L17）：接收`response`。 控制顺序：L12按`response.status_code not in (200, 201)`分支。 调用`response.json().get`、`response.json`。 返回路径：L13的`False`；L15的`response.json().get("code", 200) in (0, 200)`；L17的`False`。
- `payload`（L20–L26）：接收`response`。 控制顺序：L21按`not successful(response)`分支；L22抛异常，停止当前正常路径。 调用`successful`、`AssertionError`、`response.json`、`body.get`。 返回路径：L26的`body.get("data", body)`。
- `denied`（L29–L37）：接收`response`。 控制顺序：L34按`response.status_code not in (401, 403) and code not in (401, 403)`分支；L35抛异常，停止当前正常路径。 调用`response.json().get`、`response.json`、`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `flatten`（L40–L43）：接收`rows`。 控制顺序：L41遍历`rows`。 调用`flatten`、`item.get`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `record_id`（L46–L47）：接收`value`。 调用`isinstance`。 返回路径：L47的`value["id"] if isinstance(value, dict) else value`。
- `read_menu_ids`（L50–L64）：接收`rows`、`permission`。 控制顺序：L53按`not matching`分支；L54抛异常，停止当前正常路径；L56遍历`matching`；L58在`cursor`成立时循环；L59按`cursor["id"] in visited`分支；L60抛异常，停止当前正常路径。 调用`row.get`、`AssertionError`、`set`、`visited.add`、`selected.add`、`by_id.get`、`cursor.get`、`sorted`。 返回路径：L64的`sorted(selected)`。
- `await_permission`（L67–L81）：接收`client`、`path`、`headers`、`allowed`、`timeout`。 源码说明：YuDao has a 60-second permission cache. Observe convergence; never clear it.。 控制顺序：L70在`True`成立时循环；L73按`not accepted`分支；L75按`accepted is allowed`分支；L77按`time.monotonic() - started >= timeout`分支；L78抛异常，停止当前正常路径。 调用`time.monotonic`、`client.get`、`successful`、`denied`、`round`、`AssertionError`、`time.sleep`。 返回路径：L76的`round(time.monotonic() - started, 3)`。
- `check_native_permissions`（L84–L190）：接收`template`、`base_url`、`admin_token`。 控制顺序：L85按`urlsplit(base_url).hostname not in {"127.0.0.1", "localhost"}`分支；L86抛异常，停止当前正常路径；L112按`fastapi`分支；L126按`not fastapi`分支；L159断言`not before.get("menus")`；L165断言`after.get("menus")`。 调用`urlsplit`、`ValueError`、`httpx.Client`、`denied`、`client.get`、`payload`、`read_menu_ids`、`list`、`flatten`等。 返回路径：L177的`{ "grant_convergence_seconds": grant_seconds, "revoke_convergence_seconds": revoke_seconds…`。
- `check_native_permissions.assign`（L135–L153）：接收`menu_ids`。 控制顺序：L136按`fastapi`分支。 调用`client.put`、`client.post`、`payload`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/native_checks.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L190。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7344`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_checks.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c66b1085e05241b87d80cce74af50cb80df838dbe0a2534a471e8cfa74984236"} -->
````python
# workbench/native_checks.py
"""Exercise original native authorization; generated modules have independent acceptance checks."""

import time
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
        raise AssertionError(
            f"Native API failed: {response.request.method} {response.request.url.path} HTTP {response.status_code}"
        )
    body = response.json()
    return body.get("data", body)


def denied(response):
    try:
        code = response.json().get("code")
    except ValueError:
        code = None
    if response.status_code not in (401, 403) and code not in (401, 403):
        raise AssertionError(
            f"Expected authorization denial: {response.request.url.path}, HTTP {response.status_code}, code {code}"
        )


def flatten(rows):
    for item in rows:
        yield item
        yield from flatten(item.get("children") or [])


def record_id(value):
    return value["id"] if isinstance(value, dict) else value


def read_menu_ids(rows, permission):
    by_id = {row["id"]: row for row in rows}
    matching = [row for row in rows if row.get("permission") == permission]
    if not matching:
        raise AssertionError("Native read permission is absent from menu metadata")
    selected = set()
    for cursor in matching:
        visited = set()
        while cursor:
            if cursor["id"] in visited:
                raise AssertionError("Native menu parent cycle")
            visited.add(cursor["id"])
            selected.add(cursor["id"])
            cursor = by_id.get(cursor.get("parent_id", cursor.get("parentId")))
    return sorted(selected)


def await_permission(client, path, headers, allowed, timeout=75):
    """YuDao has a 60-second permission cache. Observe convergence; never clear it."""
    started = time.monotonic()
    while True:
        response = client.get(path, headers=headers)
        accepted = successful(response)
        if not accepted:
            denied(response)
        if accepted is allowed:
            return round(time.monotonic() - started, 3)
        if time.monotonic() - started >= timeout:
            raise AssertionError(
                "Native permission did not converge within its declared cache bound"
            )
        time.sleep(2)


def check_native_permissions(template, base_url, admin_token):
    if urlsplit(base_url).hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Native authorization tests require a loopback lab server")
    fastapi = template == "fastapiadmin"
    prefix = "" if fastapi else "/admin-api"
    listing = prefix + ("/system/user/list" if fastapi else "/system/user/page")
    info = prefix + ("/system/user/current/info" if fastapi else "/system/auth/get-permission-info")
    permission = "module_system:user:query" if fastapi else "system:user:query"
    with httpx.Client(
        base_url=base_url, trust_env=False, timeout=30, headers={"tenant-id": "1"}
    ) as client:
        denied(client.get(listing))
        denied(client.get(listing, headers={"Authorization": "Bearer test1"}))
        admin = {"Authorization": "Bearer " + admin_token}
        payload(client.get(listing, headers=admin))
        menus = payload(
            client.get(
                prefix + ("/system/menu/tree" if fastapi else "/system/menu/list"), headers=admin
            )
        )
        selected = read_menu_ids(list(flatten(menus)), permission)
        role_data = {"name": "Workbench reader", "code": "workbench_reader", "status": 0}
        role_data.update({"order": 1, "data_scope": 1} if fastapi else {"sort": 1})
        role_id = record_id(
            payload(client.post(prefix + "/system/role/create", json=role_data, headers=admin))
        )
        username, password = "workbenchreader", "NativeTest123!"
        user = {"username": username, "password": password}
        if fastapi:
            user.update(
                {
                    "name": "Workbench reader",
                    "is_superuser": False,
                    "role_ids": [role_id],
                    "status": 0,
                }
            )
        else:
            user.update({"nickname": "Workbench reader"})
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

        def assign(menu_ids):
            if fastapi:
                response = client.put(
                    "/system/role/permission",
                    json={
                        "role_ids": [role_id],
                        "menu_ids": menu_ids,
                        "data_scope": 1,
                        "dept_ids": [],
                    },
                    headers=admin,
                )
            else:
                response = client.post(
                    prefix + "/system/permission/assign-role-menu",
                    json={"roleId": role_id, "menuIds": menu_ids},
                    headers=admin,
                )
            payload(response)

        assign([])
        restricted = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        denied(client.get(listing, headers=restricted))
        before = payload(client.get(info, headers=restricted))
        assert not before.get("menus"), "Empty role unexpectedly receives native menus"
        assign(selected)
        reader = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        grant_seconds = await_permission(client, listing, reader, True) if not fastapi else 0
        payload(client.get(listing, headers=reader))
        after = payload(client.get(info, headers=reader))
        assert after.get("menus"), "Granted native page is absent from login/menu result"
        denied(
            client.post(
                prefix + "/system/role/create",
                json={**role_data, "code": "must_not_be_created"},
                headers=reader,
            )
        )
        assign([])
        revoked = {"Authorization": "Bearer " + login(template, base_url, username, password)}
        revoke_seconds = await_permission(client, listing, revoked, False) if not fastapi else 0
        denied(client.get(listing, headers=revoked))
    return {
        "grant_convergence_seconds": grant_seconds,
        "revoke_convergence_seconds": revoke_seconds,
        "upstream_permission_cache_seconds": 0 if fastapi else 60,
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
````
