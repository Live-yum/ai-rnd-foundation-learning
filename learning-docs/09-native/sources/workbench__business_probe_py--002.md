# workbench/business_probe.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__business_probe_py--001.md) · 

**作用：三角色实际原生HTTP验收。** 使用明确合成账号和业务记录，通过原生登录取得身份，检查关联、分配、转换、历史、审计、提醒和统计，另以无权用户验证后端拒绝；不把隐藏按钮当权限证明。

**对应关系：** native_lab/独立恢复 → customer_service_acceptance → business.json及临时浏览器场景。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.native_checks`、`workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `verify_created_reminders`（L867–L900）：接收`plan`、`records`、`clients`、`evidence`。 源码说明：Creation receipts inspect only freshly created owned IDs and their inboxes.。 控制顺序：L869遍历`records`；L873按`not rules`分支；L877断言`all(n.recipient == "creator" for n in rules)`；L880遍历`set(clients)`；L882断言`len(notices) == int(client is creator)`；L885断言`record_notices(client, entity, identifier, "created") == notices`；L888遍历`notices`；L891断言`updated.get("read") is True or updated.get("read_at") is not None`。后续分支沿下方源码相同行号继续阅读。 调用`all`、`set`、`record_notices`、`len`、`int`、`payload`、`client.read_notice`、`updated.get`、`other.read_notice`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `append_reminder_evidence`（L903–L925）：接收`evidence`、`notice`、`observed`。 控制顺序：L911按`found is None`分支。 调用`next`、`all`、`key.items`、`evidence.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_reminders`（L928–L966）：接收`plan`、`records`、`outsiders`、`evidence`。 源码说明：Check assignment/due routing, idempotency and recipient-private read persistence.。 控制顺序：L930遍历`records`；L933遍历`("assigned", "due")`；L935遍历`clients`；L937断言`len(notices) == int(client in expected)`；L940断言`set(record_notices(client, entity, identifier, event)) == set(notices)`；L943按`not notices`分支；L948断言`updated.get("read") is True or updated.get("read_at") is not None`；L951遍历`clients - {client}`。后续分支沿下方源码相同行号继续阅读。 调用`set`、`recipients.values`、`reminder_recipients`、`record_notices`、`len`、`int`、`next`、`iter`、`notices.values`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_scoped_metrics`（L969–L1102）：接收`client`、`plan`、`role`、`actor`、`evidence`。 源码说明：Compare HTTP aggregates with independently counted visible rows, including values.。 控制顺序：L984断言`set(by_name) == expected and len(by_name) == len(results)`；L987按`not expected and evidence is not None`分支；L991遍历`plan.business.metrics`；L992按`metric.name not in by_name`分支；L1029按`isinstance(result.get("value"), dict)`分支；L1033按`metric.kind == "count"`分支；L1034断言`type(result["value"]) is int and result["value"] == len(rows)`；L1039按`metric.kind == "average_duration"`分支。后续分支沿下方源码相同行号继续阅读。 调用`client.call`、`any`、`set`、`len`、`evidence["metric_denials"].append`、`hasattr`、`client.all_rows`、`client.rows`、`matches`等。 返回路径：L1102的`results`。
- `verify_scoped_metrics.value`（L1001–L1002）：接收`row`、`field`。 调用`row.get`、`wire_name`。 返回路径：L1002的`row.get(wire_name(client.template, field))`。
- `verify_scoped_metrics.moment`（L1004–L1010）：接收`value`。 调用`datetime.fromisoformat`、`str(value).replace`、`str`、`parsed.replace`、`parsed.astimezone`。 返回路径：L1006的`parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezo…`。
- `verify_scoped_metrics.matches`（L1012–L1025）：接收`row`。 控制顺序：L1013遍历`metric.filters`；L1015按`rule.op == "eq" and actual != rule.value`分支；L1017按`rule.op == "ne" and actual == rule.value`分支；L1019按`rule.op == "in" and actual not in rule.value`分支；L1021按`rule.op == "gte" and (actual is None or actual < rule.value)`分支；L1023按`rule.op == "lte" and (actual is None or actual > rule.value)`分支。 调用`value`。 返回路径：L1016的`False`；L1018的`False`；L1020的`False`。
- `verify_scoped_metrics.bounded_buckets`（L1073–L1080）：接收`values`。 调用`sorted`、`hashlib.sha256(key.encode()).hexdigest`、`hashlib.sha256`、`key.encode`、`values.items`。 返回路径：L1074的`sorted( [ {"key_sha256": hashlib.sha256(key.encode()).hexdigest(), "count": count} for key…`。

</details>

**创建路径：** `workbench/business_probe.py`；**本文件共有 2 段**。本段覆盖源文件 L867–L1102。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10424`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_probe.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "c5035b24e32d07c065a66dd66c31e59e0bf2c0ebe8f36b4f88a9f12de9c6d461"} -->
````python
# workbench/business_probe.py
def verify_created_reminders(plan, records, clients, evidence):
    """Creation receipts inspect only freshly created owned IDs and their inboxes."""
    for entity, identifier, creator in records:
        rules = [
            n for n in plan.business.notifications if n.entity == entity and n.event == "created"
        ]
        if not rules:
            continue
        # Native creation deliberately clears assignee; a created-to-assignee rule
        # cannot demonstrate delivery without a real recipient and stays blocked.
        assert all(n.recipient == "creator" for n in rules), (
            "Created reminder has no recipient before the separate assignment action"
        )
        for client in set(clients):
            notices = record_notices(client, entity, identifier, "created")
            assert len(notices) == int(client is creator), (
                "Creation reminder was omitted or misrouted"
            )
            assert record_notices(client, entity, identifier, "created") == notices, (
                "Creation reminder duplicated on read"
            )
            for notice_id in notices:
                payload(client.read_notice(notice_id))
                updated = record_notices(client, entity, identifier, "created")[notice_id]
                assert updated.get("read") is True or updated.get("read_at") is not None
                for other in set(clients) - {client}:
                    response = other.read_notice(notice_id)
                    assert response.status_code in {401, 403, 404} or response.json().get(
                        "code"
                    ) in {401, 403, 404}, "Creation reminder read state leaked"
        for notice in rules:
            append_reminder_evidence(
                evidence, notice, len(record_notices(creator, entity, identifier, "created"))
            )


def append_reminder_evidence(evidence, notice, observed):
    key = {
        "entity": notice.entity,
        "event": notice.event,
        "transition": notice.transition,
        "recipient": notice.recipient,
    }
    found = next((item for item in evidence if all(item[k] == v for k, v in key.items())), None)
    if found is None:
        evidence.append(
            {
                **key,
                "expected_count": 1,
                "observed_count": observed,
                "idempotent": True,
                "read_persisted": True,
                "foreign_read_denied": True,
                "outsider_count": 0,
            }
        )
    else:
        found["expected_count"] += 1
        found["observed_count"] += observed


def verify_reminders(plan, records, outsiders, evidence=None):
    """Check assignment/due routing, idempotency and recipient-private read persistence."""
    for entity, identifier, creator, assignee in records:
        recipients = {"creator": creator, "assignee": assignee}
        clients = set(recipients.values()) | set(outsiders)
        for event in ("assigned", "due"):
            expected = reminder_recipients(plan, entity, event, recipients)
            for client in clients:
                notices = record_notices(client, entity, identifier, event)
                assert len(notices) == int(client in expected), (
                    f"{entity} {event} reminder missing, duplicated or misrouted"
                )
                assert set(record_notices(client, entity, identifier, event)) == set(notices), (
                    "Reading reminders generated duplicate notifications"
                )
                if not notices:
                    continue
                notice = next(iter(notices.values()))
                payload(client.read_notice(notice["id"]))
                updated = record_notices(client, entity, identifier, event)[str(notice["id"])]
                assert updated.get("read") is True or updated.get("read_at") is not None, (
                    "Read state not persisted"
                )
                for other in clients - {client}:
                    forbidden = other.read_notice(notice["id"])
                    assert forbidden.status_code in {401, 403, 404} or forbidden.json().get(
                        "code"
                    ) in {
                        401,
                        403,
                        404,
                    }, "Other recipient changed reminder read state"
            if evidence is not None and event == "due":
                for notice in plan.business.notifications:
                    if (notice.entity, notice.event) == (entity, event):
                        observed = len(
                            record_notices(recipients[notice.recipient], entity, identifier, event)
                        )
                        append_reminder_evidence(evidence, notice, observed)


def verify_scoped_metrics(client, plan, role="manager", actor=None, evidence=None):
    """Compare HTTP aggregates with independently counted visible rows, including values."""
    from collections import Counter
    from datetime import datetime, timezone

    results = client.call("GET", client.prefix + "/metrics")
    by_name = {item["name"]: item for item in results}
    expected = {
        metric.name
        for metric in plan.business.metrics
        if any(
            grant.role == role and grant.entity == metric.entity and "read_metrics" in grant.actions
            for grant in plan.business.permissions
        )
    }
    assert set(by_name) == expected and len(by_name) == len(results), (
        "Metric set differs from the role's approved permissions"
    )
    if not expected and evidence is not None:
        evidence["metric_denials"].append(
            {"role": role, "actor": actor or role, "observed_count": len(results)}
        )
    for metric in plan.business.metrics:
        if metric.name not in by_name:
            continue
        rows = (
            client.all_rows(metric.entity)
            if hasattr(client, "all_rows")
            else client.rows(metric.entity, page_size=100, pageSize=100)
        )
        visible_count = len(rows)

        def value(row, field):
            return row.get(wire_name(client.template, field))

        def moment(value):
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return (
                parsed.replace(tzinfo=timezone.utc)
                if parsed.tzinfo is None
                else parsed.astimezone(timezone.utc)
            )

        def matches(row):
            for rule in metric.filters:
                actual = value(row, rule.field)
                if rule.op == "eq" and actual != rule.value:
                    return False
                if rule.op == "ne" and actual == rule.value:
                    return False
                if rule.op == "in" and actual not in rule.value:
                    return False
                if rule.op == "gte" and (actual is None or actual < rule.value):
                    return False
                if rule.op == "lte" and (actual is None or actual > rule.value):
                    return False
            return True

        rows = [row for row in rows if matches(row)]
        result = by_name[metric.name]
        if isinstance(result.get("value"), dict):
            result = result["value"]
        expected_value = {"value": None, "samples": None, "buckets": []}
        observed_value = dict(expected_value)
        if metric.kind == "count":
            assert type(result["value"]) is int and result["value"] == len(rows), (
                "Metric count differs from authorized rows"
            )
            expected_value["value"] = len(rows)
            observed_value["value"] = result["value"]
        elif metric.kind == "average_duration":
            samples = [
                (
                    moment(value(row, metric.end_field)) - moment(value(row, metric.start_field))
                ).total_seconds()
                for row in rows
                if value(row, metric.end_field) and value(row, metric.start_field)
            ]
            assert type(result["samples"]) is int and result["samples"] == len(samples)
            if samples:
                assert abs(result["value"] - sum(samples) / len(samples)) < 0.01
            else:
                assert result["value"] is None
            expected_value.update(
                value=sum(samples) / len(samples) if samples else None, samples=len(samples)
            )
            observed_value.update(value=result["value"], samples=result["samples"])
        else:
            counts = Counter(
                str(value(row, metric.group_by))
                if metric.kind == "group_count"
                else moment(value(row, metric.time_field)).date().isoformat()
                for row in rows
            )
            actual = result.get("buckets")
            if actual is None:
                actual = {
                    str(group.get("key", group.get("day"))): group["count"]
                    for group in result["groups"]
                }
            assert all(type(value) is int for value in actual.values()) and actual == dict(
                counts
            ), "Metric buckets differ from authorized rows"

            def bounded_buckets(values):
                return sorted(
                    [
                        {"key_sha256": hashlib.sha256(key.encode()).hexdigest(), "count": count}
                        for key, count in values.items()
                    ],
                    key=lambda item: item["key_sha256"],
                )

            expected_value["buckets"] = bounded_buckets(counts)
            observed_value["buckets"] = bounded_buckets(actual)
        if evidence is not None:
            scope = next(
                p.scope
                for p in plan.business.permissions
                if p.role == role and p.entity == metric.entity and "read_metrics" in p.actions
            )
            evidence["metrics"].append(
                {
                    "name": metric.name,
                    "role": role,
                    "actor": actor or role,
                    "scope": scope,
                    "kind": metric.kind,
                    "visible_count": visible_count,
                    "expected": expected_value,
                    "observed": observed_value,
                }
            )
    return results
````
