"""The same independent native HTTP probe is included in delivered runtime tools."""

import httpx


def payload(response):
    if not response.is_success:
        raise ValueError(f"原生交付接口 HTTP {response.status_code}")
    body = response.json()
    if body.get("code", 200) not in {0, 200}:
        raise ValueError("原生交付接口业务操作失败")
    return body.get("data", body)


def check_restored_product(template, base, token, targets, plan):
    fastapi = template == "fastapiadmin"
    prefix = "" if fastapi else "/admin-api"
    with httpx.Client(
        base_url=base,
        timeout=30,
        trust_env=False,
        headers={"Authorization": "Bearer " + token, "tenant-id": "1"},
    ) as client:
        info = payload(
            client.get(
                prefix
                + ("/system/user/current/info" if fastapi else "/system/auth/get-permission-info")
            )
        )
        menus = str(info.get("menus", []))
        checked = []
        for target, entity in zip(targets, plan["entities"], strict=True):
            marker = (
                "module_rnd/" + entity["name"]
                if fastapi
                else "infra/wb" + entity["name"].replace("_", "")
            )
            if marker not in menus:
                raise ValueError("新数据库未恢复生成业务菜单")
            body = {}
            for field in entity["fields"]:
                parts = field["name"].split("_")
                name = (
                    field["name"] if fastapi else parts[0] + "".join(p.title() for p in parts[1:])
                )
                body[name] = {
                    "text": "restored-product"[: field["max_length"]],
                    "integer": 0,
                    "boolean": False,
                }[field["kind"]]
            from workbench.native_business_checks import wire

            rule = next(
                (r for r in plan.get("custom_rules", []) if r["entity"] == entity["name"]), None
            )
            if rule:
                body = wire(template, rule["accept_examples"][0])
            created = payload(client.post(target["api"] + "/create", json=body))
            identifier = created["id"] if isinstance(created, dict) else created
            got = payload(
                client.get(
                    target["api"] + (f"/detail/{identifier}" if fastapi else "/get"),
                    params={} if fastapi else {"id": identifier},
                )
            )
            if any(got.get(key) != value for key, value in body.items()):
                raise ValueError("新数据库中的CRUD值不一致")
            if fastapi:
                payload(client.request("DELETE", target["api"] + "/delete", json=[identifier]))
            else:
                payload(client.delete(target["api"] + "/delete", params={"id": identifier}))
            checked.append(
                {
                    "entity": entity["name"],
                    "menu_restored": True,
                    "create_read_delete": True,
                    "zero_false_preserved": True,
                }
            )
    from workbench.native_business_checks import check_business_examples

    business = check_business_examples(template, base, token, targets, plan)
    return {
        "passed": True,
        "fresh_database": True,
        "entities": checked,
        "model_required": False,
        "business_rules": business,
    }
