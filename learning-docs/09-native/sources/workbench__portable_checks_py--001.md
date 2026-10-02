# workbench/portable_checks.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立原生产品的业务复验。** check_restored_product对新数据库启动后的产品执行实际认证和CRUD断言，输入来自产品随包规格。它不能依赖工作台的运行对象，否则在用户独立解压后就失效。

**对应关系：** templates/deployment/start.py复制的helper → 产品后端HTTP。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot_business_records`（L6–L28）：接收`template`、`base`、`token`、`targets`、`scenario`。 源码说明：Hash the exact records created by the independent installation over native HTTP.。 控制顺序：L12按`not isinstance(records, dict) or set(records) != {target["entity"] for target in targ…`分支；L13抛异常，停止当前正常路径；L17遍历`records.items()`；L23按`len(matches) != 1`分支；L24抛异常，停止当前正常路径。 调用`scenario.get`、`isinstance`、`set`、`ValueError`、`BusinessClient`、`records.items`、`client.rows`、`str`、`len`等。 返回路径：L26的`result`。
- `require_preserved_business_records`（L31–L33）：接收`before`、`after`。 控制顺序：L32按`not before or before != after`分支；L33抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `payload`（L36–L42）：接收`response`。 控制顺序：L37按`not response.is_success`分支；L38抛异常，停止当前正常路径；L40按`body.get("code", 200) not in {0, 200}`分支；L41抛异常，停止当前正常路径。 调用`ValueError`、`response.json`、`body.get`。 返回路径：L42的`body.get("data", body)`。
- `check_restored_product`（L45–L127）：接收`template`、`base`、`token`、`targets`、`plan`。 控制顺序：L46按`plan.get("business")`分支；L70遍历`zip(targets, plan["entities"], strict=True)`；L76按`marker not in menus`分支；L77抛异常，停止当前正常路径；L79遍历`entity["fields"]`；L94按`rule`分支；L104按`any(got.get(key) != value for key, value in body.items())`分支；L105抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`plan.get`、`customer_service_acceptance`、`Plan.model_validate`、`httpx.Client`、`payload`、`client.get`、`str`、`info.get`、`zip`等。 返回路径：L53的`{"passed": True, "fresh_database": True, "model_required": False, "business": result}`；L121的`{ "passed": True, "fresh_database": True, "entities": checked, "model_required": False, "b…`。

</details>

**创建路径：** `workbench/portable_checks.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L127。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5123`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/portable_checks.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4ce3893293f2582c78edd04b9cea7e2bfaa245f2fe4bbe4ab1b62098c7245bdb"} -->
````python
# workbench/portable_checks.py
"""The same independent native HTTP probe is included in delivered runtime tools."""

import httpx


def snapshot_business_records(template, base, token, targets, scenario):
    """Hash the exact records created by the independent installation over native HTTP."""
    from workbench.business_probe import BusinessClient
    from workbench.domain import digest

    records = scenario.get("records")
    if not isinstance(records, dict) or set(records) != {target["entity"] for target in targets}:
        raise ValueError("Independent restart has no complete business record identity")
    client = BusinessClient(template, base, token, targets)
    try:
        result = {}
        for entity, identifier in records.items():
            matches = [
                row
                for row in client.rows(entity, page_size=100, pageSize=100)
                if str(row["id"]) == identifier
            ]
            if len(matches) != 1:
                raise ValueError("Independent restart lost the original business record: " + entity)
            result[entity] = {"id": identifier, "sha256": digest(matches[0])}
        return result
    finally:
        client.close()


def require_preserved_business_records(before, after):
    if not before or before != after:
        raise ValueError("Independent restart changed or lost previously created business records")


def payload(response):
    if not response.is_success:
        raise ValueError(f"原生交付接口 HTTP {response.status_code}")
    body = response.json()
    if body.get("code", 200) not in {0, 200}:
        raise ValueError("原生交付接口业务操作失败")
    return body.get("data", body)


def check_restored_product(template, base, token, targets, plan):
    if plan.get("business"):
        from workbench.business_probe import customer_service_acceptance
        from workbench.domain import Plan

        result = customer_service_acceptance(
            template, base, token, targets, Plan.model_validate(plan)
        )
        return {"passed": True, "fresh_database": True, "model_required": False, "business": result}
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
````
