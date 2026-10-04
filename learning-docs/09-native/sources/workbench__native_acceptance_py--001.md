# workbench/native_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：实际调用生成后的业务接口。** sample_record为不同字段构造有效记录；generated_crud检查创建、读取、修改、删除和无效载荷，persistence检查重启后记录仍在，permissions实际授权及撤权，不只读取权限配置。

**对应关系：** native_lab → 后端HTTP/PG；test_native_baseline和native CI。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_checks`、`workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `wire_name`（L20–L24）：接收`template`、`name`。 控制顺序：L21按`template == "fastapiadmin"`分支。 调用`name.split`、`"".join`、`piece[:1].upper`。 返回路径：L22的`name`；L24的`first + "".join(piece[:1].upper() + piece[1:] for piece in rest)`。
- `sample_record`（L27–L44）：接收`entity`、`suffix`、`template`、`plan`。 控制顺序：L28按`plan is not None`分支；L32按`rule`分支。 调用`next`、`wire`、`wire_name`。 返回路径：L34的`wire(template, rule.accept_examples[index])`；L35的`{ wire_name(template, f.name): ( f"{entity.name}-{suffix}"[: f.max_length] if f.kind == "t…`。
- `invalid_record`（L47–L58）：接收`entity`、`data`、`template`。 源码说明：Exercise an existing constraint, never invent a required business field.。 控制顺序：L53按`required is not None`分支。 调用`dict`、`next`、`invalid.pop`、`wire_name`。 返回路径：L55的`invalid, "required"`；L58的`invalid, "type"`。
- `list_rows`（L61–L67）：接收`value`。 控制顺序：L62按`not isinstance(value, dict)`分支；L63抛异常，停止当前正常路径；L65按`not isinstance(rows, list)`分支；L66抛异常，停止当前正常路径。 调用`isinstance`、`AssertionError`、`value.get`。 返回路径：L67的`rows`。
- `generated_crud`（L70–L163）：接收`template`、`base_url`、`token`、`targets`、`plan`。 控制顺序：L77遍历`zip(targets, plan.entities, strict=True)`；L84断言`type(identifier) is int and identifier > 0`；L96遍历`data.items()`；L97断言`saved[key] == value`；L99按`fastapi`分支；L110遍历`changed.items()`；L111断言`updated[key] == value`；L113断言`any(row["id"] == identifier for row in rows)`。后续分支沿下方源码相同行号继续阅读。 调用`httpx.Client`、`zip`、`denied`、`client.get`、`sample_record`、`payload`、`client.post`、`record_id`、`type`等。 返回路径：L163的`results`。
- `generated_crud.get_item`（L86–L93）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87按`fastapi`分支。 调用`payload`、`client.get`。 返回路径：L88的`payload( client.get(target["api"] + f"/detail/{identifier}", headers=admin) )`；L91的`payload( client.get(target["api"] + "/get", params={"id": identifier}, headers=admin) )`。
- `check_generated_persistence`（L166–L178）：接收`template`、`base_url`、`token`、`targets`、`records`。 控制顺序：L173遍历`zip(targets, records, strict=True)`；L176遍历`record["persistent_data"].items()`；L177断言`saved[key] == value`。 调用`httpx.Client`、`zip`、`list_rows`、`payload`、`client.get`、`next`、`record["persistent_data"].items`、`len`。 返回路径：L178的`{"process_restart_preserves_records": True, "entity_count": len(records)}`。
- `generated_permissions`（L181–L331）：接收`template`、`base_url`、`token`、`targets`、`plan`。 源码说明：Grant/read/create/revoke using original role APIs, never by editing auth code.。 控制顺序：L201遍历`targets`；L203遍历`("query", "create", "update", "delete")`；L223按`not fastapi`分支；L261遍历`targets`；L263断言`not payload(client.get(info, headers=none)).get("menus")`；L266按`not fastapi`分支；L267遍历`targets`；L270断言`menus`。后续分支沿下方源码相同行号继续阅读。 调用`httpx.Client`、`list`、`flatten`、`payload`、`client.get`、`set`、`read_ids.update`、`read_menu_ids`、`full_ids.update`等。 返回路径：L318的`{ "owned_user_id": user_id, "owned_role_id": role_id, "attempt_id": attempt_id, "empty_rol…`。
- `generated_permissions.assign`（L232–L254）：接收`ids`。 控制顺序：L233按`fastapi`分支；L251按`fastapi`分支；L254断言`actual == set(ids)`。 调用`client.put`、`sorted`、`client.post`、`payload`、`client.get`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `generated_permissions.identity`（L256–L257）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`login`。 返回路径：L257的`{"Authorization": "Bearer " + login(template, base_url, username, password)}`。

</details>

**创建路径：** `workbench/native_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L331。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13597`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0acccbf3674fc8d1beb8ef99fccc0aff7b89cc2ec071662443d6bae1aeb4f228"} -->
````python
# workbench/native_acceptance.py
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


def invalid_record(entity, data, template):
    """Exercise an existing constraint, never invent a required business field."""
    invalid = dict(data)
    required = next(
        (field for field in entity.fields if field.required and field.kind != "boolean"), None
    )
    if required is not None:
        invalid.pop(wire_name(template, required.name))
        return invalid, "required"
    field = entity.fields[0]
    invalid[wire_name(template, field.name)] = {"invalid_scalar": True}
    return invalid, "type"


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
            invalid, validation_kind = invalid_record(entity, data, template)
            response = client.post(target["api"] + "/create", json=invalid, headers=admin)
            assert not successful(response) and response.status_code < 500
            assert response.status_code in (400, 422) or response.json().get("code") in (
                400,
                422,
            ), "Declared field validation must return a client validation error"
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
                (
                    str(sample[wire_name(template, f.name)])
                    for f in entity.fields
                    if f.kind == "text"
                ),
                "",
            )
            target["sample_record"] = {"id": persistent, **sample}
            results.append(
                {
                    "entity": entity.name,
                    "crud": True,
                    "required_field_rejected": validation_kind == "required",
                    "invalid_field_rejected": True,
                    "validation_kind": validation_kind,
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
````
