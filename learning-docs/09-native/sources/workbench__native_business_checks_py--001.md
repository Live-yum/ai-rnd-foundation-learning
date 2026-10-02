# workbench/native_business_checks.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：用批准的正反例验证原生业务约束。** 实际发送新增和修改请求，区分业务拒绝、鉴权失败和服务错误；拒绝新增不能留下记录，拒绝修改不能改变旧值，合法操作仍须成功。不能仅断言HTTP不等于200。

**对应关系：** native_coding候选验证/原生整体验收 → 真实后端接口 → 保留业务证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `wire`（L6–L13）：接收`template`、`sample`。 调用`key`、`sample.items`。 返回路径：L11的`{ (name if template == "fastapiadmin" else key(name)): value for name, value in sample.ite…`。
- `wire.key`（L7–L9）：接收`name`。 调用`name.split`、`"".join`、`piece.title`。 返回路径：L9的`first + "".join(piece.title() for piece in rest)`。
- `successful`（L16–L17）：接收`response`。 调用`response.json().get`、`response.json`。 返回路径：L17的`response.is_success and response.json().get("code", 200) in {0, 200}`。
- `data`（L20–L24）：接收`response`。 控制顺序：L21按`not successful(response)`分支；L22抛异常，停止当前正常路径。 调用`successful`、`ValueError`、`str`、`response.json`、`body.get`。 返回路径：L24的`body.get("data", body)`。
- `check_business_examples`（L27–L128）：接收`template`、`base`、`token`、`targets`、`plan`。 源码说明：Reject creates/updates before persistence; never accept a server crash as validation.。 控制顺序：L37遍历`plan.get("custom_rules", [])`；L57遍历`accepted`；L60按`type(identifier) is not int or identifier <= 0`分支；L61抛异常，停止当前正常路径；L64按`any(actual.get(k) != v for k, v in sample.items())`分支；L65抛异常，停止当前正常路径；L68遍历`rejected`；L71按`successful(response)`分支。后续分支沿下方源码相同行号继续阅读。 调用`hasattr`、`plan.model_dump`、`httpx.Client`、`plan.get`、`next`、`wire`、`data`、`client.post`、`isinstance`等。 返回路径：L128的`result`。
- `check_business_examples.rows`（L44–L46）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`data`、`client.get`、`value.get`。 返回路径：L46的`value.get("items", value.get("list"))`。
- `check_business_examples.get`（L48–L54）：接收`identifier`。 调用`data`、`client.get`。 返回路径：L49的`data( client.get( api + (f"/detail/{identifier}" if fast else "/get"), params={} if fast e…`。

</details>

**创建路径：** `workbench/native_business_checks.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5988`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_business_checks.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9c693385054f732abedc324d8f5a0e7011cdecd3c96067ca85c4de50a0ae3b58"} -->
````python
# workbench/native_business_checks.py
"""Executable approved native business examples, reused by standalone delivery probes."""

import httpx


def wire(template, sample):
    def key(name):
        first, *rest = name.split("_")
        return first + "".join(piece.title() for piece in rest)

    return {
        (name if template == "fastapiadmin" else key(name)): value for name, value in sample.items()
    }


def successful(response):
    return response.is_success and response.json().get("code", 200) in {0, 200}


def data(response):
    if not successful(response):
        raise ValueError("Native rule positive example failed: HTTP " + str(response.status_code))
    body = response.json()
    return body.get("data", body)


def check_business_examples(template, base, token, targets, plan):
    """Reject creates/updates before persistence; never accept a server crash as validation."""
    plan = plan.model_dump() if hasattr(plan, "model_dump") else plan
    result = {"passed": False, "rules": []}
    with httpx.Client(
        base_url=base,
        trust_env=False,
        timeout=30,
        headers={"Authorization": "Bearer " + token, "tenant-id": "1"},
    ) as client:
        for rule in plan.get("custom_rules", []):
            target = next(t for t in targets if t["entity"] == rule["entity"])
            api, fast = target["api"], template == "fastapiadmin"
            accepted = [wire(template, row) for row in rule["accept_examples"]]
            rejected = [wire(template, row) for row in rule["reject_examples"]]
            identifiers = []

            def rows():
                value = data(client.get(target["list"], params={"pageSize": 100, "page_size": 100}))
                return value.get("items", value.get("list"))

            def get(identifier):
                return data(
                    client.get(
                        api + (f"/detail/{identifier}" if fast else "/get"),
                        params={} if fast else {"id": identifier},
                    )
                )

            try:
                for sample in accepted:
                    created = data(client.post(api + "/create", json=sample))
                    identifier = created["id"] if isinstance(created, dict) else created
                    if type(identifier) is not int or identifier <= 0:
                        raise ValueError("Native create returned no real record ID")
                    identifiers.append(identifier)
                    actual = get(identifier)
                    if any(actual.get(k) != v for k, v in sample.items()):
                        raise ValueError("Native rule accepted record changed")
                identifier = identifiers[0]
                baseline = get(identifier)
                for sample in rejected:
                    previous_ids = {row["id"] for row in rows()}
                    response = client.post(api + "/create", json=sample)
                    if successful(response):
                        accidental = data(response)
                        accidental = (
                            accidental["id"] if isinstance(accidental, dict) else accidental
                        )
                        if type(accidental) is int:
                            identifiers.append(accidental)
                    if successful(response) or response.status_code >= 500:
                        raise ValueError("Native rule negative create was accepted or crashed")
                    if response.status_code not in {200, 400, 422}:
                        raise ValueError("Native rule rejection was not a client validation result")
                    if "RND_BUSINESS_RULE" not in response.text:
                        raise ValueError("Negative example failed for an unrelated reason")
                    if {row["id"] for row in rows()} != previous_ids:
                        raise ValueError("Rejected create wrote a business record")
                    response = client.put(
                        api + (f"/update/{identifier}" if fast else "/update"),
                        json=sample if fast else {"id": identifier, **sample},
                    )
                    if (
                        successful(response)
                        or response.status_code >= 500
                        or "RND_BUSINESS_RULE" not in response.text
                    ):
                        raise ValueError("Native rule negative update was not validated")
                    if any(get(identifier).get(k) != v for k, v in baseline.items()):
                        raise ValueError("Rejected update changed the saved record")
                # Positive update must work too; the rule cannot simply disable editing.
                value = accepted[-1]
                data(
                    client.put(
                        api + (f"/update/{identifier}" if fast else "/update"),
                        json=value if fast else {"id": identifier, **value},
                    )
                )
                if any(get(identifier).get(k) != v for k, v in value.items()):
                    raise ValueError("Positive update did not persist")
                result["rules"].append(
                    {
                        "entity": rule["entity"],
                        "accepted": len(accepted),
                        "rejected_create": len(rejected),
                        "rejected_update": len(rejected),
                        "positive_update": True,
                        "rejected_writes_absent": True,
                    }
                )
            finally:
                for identifier in identifiers:
                    data(
                        client.request(
                            "DELETE",
                            api + "/delete",
                            **({"json": [identifier]} if fast else {"params": {"id": identifier}}),
                        )
                    )
    result["passed"] = True
    return result
````
