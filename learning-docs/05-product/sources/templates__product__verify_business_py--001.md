# templates/product/verify_business.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](templates__product__verify_business_py--002.md)

**作用：独立基础产品的组成文件。** 独立客服HTTP/浏览器验收器：新建自有数据库和三角色合成账号，验证关系、指派、流程、记录、提醒、统计、拒绝路径及重启；截图仅限有界命名PNG，不导出密码或运行数据库。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `check`（L22–L24）：接收`condition`、`message`。 控制顺序：L23按`not condition`分支；L24抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_query_matrix`（L27–L307）：接收`spec`、`actors`、`rows`、`samples`、`create_roles`、`request`、`allowed`。 源码说明：Exact query expectations come from owned API writes, never query responses.。 控制顺序：L46遍历`spec["entities"]`；L50按`not searchable and not filterable`分支；L54按`workflow`分支；L63遍历`actors.items()`；L64按`not allowed(role, entity, "read")`分支；L67按`scope == "own" and not allowed(role, entity, "create")`分支；L72遍历`(0, 1)`；L74遍历`enumerate(fields)`。后续分支沿下方源码相同行号继续阅读。 调用`workflows.get`、`resources[entity].get`、`protected.add`、`protected.update`、`t.get`、`actors.items`、`allowed`、`dict`、`enumerate`等。 返回路径：L307的`cases, evidence`。
- `verify_query_matrix.wire`（L36–L37）：接收`value`。 调用`type`、`str(value).lower`、`str`。 返回路径：L37的`str(value).lower() if type(value) is bool else str(value)`。
- `verify_query_matrix.keyword`（L39–L44）：接收`value`。 调用`str`、`len`、`term[:200].upper`。 返回路径：L44的`term[:200].upper()`。
- `verify_query_matrix.matches`（L159–L169）：接收`row`、`params`。 控制顺序：L161按`q and not any(q in str(row.get(f["name"]) or "").casefold() for f in searchable)`分支。 调用`params.get("q", "").strip().casefold`、`params.get("q", "").strip`、`params.get`、`any`、`str(row.get(f["name"]) or "").casefold`、`str`、`row.get`、`all`、`wire`等。 返回路径：L162的`False`；L163的`all( wire(row.get(f["name"])) == value for key, value in params.items() if key.startswith(…`。
- `verify_field_constraints`（L310–L372）：接收`client`、`actor`、`entity`、`fields`、`sample`、`row`、`protected`、`can_update`。 源码说明：Reject concrete invalid requests through the generated server, not metadata alone.。 控制顺序：L316遍历`fields`；L319按`name in protected`分支；L323按`can_update`分支；L334按`field["required"]`分支；L340按`kind in {"text", "enum"}`分支；L342按`kind == "text"`分支；L345按`field.get("min_length", 0) > 0`分支；L348按`kind == "enum"`分支。后续分支沿下方源码相同行号继续阅读。 调用`client.get(route, headers=headers, params={"limit": 100}).json`、`client.get`、`client.post`、`check`、`client.put`、`evidence.append`、`sample.items`、`invalid.append`、`field.get`等。 返回路径：L372的`evidence`。
- `verify_audit_immutability`（L375–L423）：接收`client`、`actor`、`entity`、`row`、`actor_ids`。 控制顺序：L382遍历`original`；L407遍历`(route, route + "/" + original[0]["id"])`；L408遍历`("PUT", "PATCH", "DELETE")`。 调用`client.get`、`check`、`response.json`、`bool`、`entry.keys`、`all`、`isinstance`、`entry.get`、`datetime.fromisoformat`等。 返回路径：L416的`original, { "entity": entity, "entries_checked": len(original), "action_actor_timestamp": …`。
- `NotificationEvidence`（L426–L513）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `NotificationEvidence.__init__`（L429–L435）：接收`business`。 调用`Counter`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NotificationEvidence.recipient`（L437–L443）：接收`rule`、`row`。 调用`row.get`。 返回路径：L443的`row.get(field)`。
- `NotificationEvidence.event`（L445–L456）：接收`entity`、`row`、`event`、`transition`。 控制顺序：L447遍历`enumerate(self.rules)`；L448按`rule["entity"] != entity or rule["event"] != event`分支；L450按`event == "transitioned" and rule["transition"] != transition`分支；L453按`recipient`分支。 调用`set`、`enumerate`、`self.recipient`、`self.covered.add`、`recipients.add`、`self.expected.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NotificationEvidence.due`（L458–L483）：接收`rows`、`actor`、`allowed`。 控制顺序：L460遍历`enumerate(self.rules)`；L461按`rule["event"] != "due"`分支；L464遍历`rows[entity]`；L466按`not value or row.get("archived_at") or self.recipient(rule, row) != actor["id"] or no…`分支；L475按`workflow and row[workflow["status_field"]] not in { state for t in workflow["transiti…`分支；L481按`key not in self.due_seen`分支。 调用`datetime.now`、`enumerate`、`row.get`、`self.recipient`、`allowed`、`datetime.fromisoformat`、`value.replace`、`self.workflows.get`、`self.covered.add`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NotificationEvidence.inbox`（L485–L507）：接收`actor`、`notices`、`event`。 调用`check`、`len`、`all`、`Counter`、`self.expected.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NotificationEvidence.complete`（L509–L513）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`check`、`set`、`range`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_png`（L522–L581）：接收`payload`。 控制顺序：L539在`offset < len(payload)`成立时循环；L548按`header is None`分支；L551按`kind == b"IHDR"`分支；L552抛异常，停止当前正常路径；L553按`kind == b"IDAT"`分支；L555按`kind == b"IEND"`分支；L574抛异常，停止当前正常路径。 调用`check`、`payload.startswith`、`len`、`struct.unpack`、`zlib.crc32`、`ValueError`、`compressed.append`、`{0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get`、`zlib.decompressobj`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_screenshots`（L584–L632）：接收`directory`、`entries`。 源码说明：Only bounded, named PNGs from the owned synthetic-product directory escape.。 控制顺序：L590按`directory is None`分支；L596遍历`entries`。 调用`check`、`isinstance`、`len`、`bool`、`Path(directory).resolve`、`Path`、`set`、`entry.get`、`re.fullmatch`等。 返回路径：L592的`[]`；L632的`result`。
- `verify_business`（L635–L1723）：接收`product`、`python`、`stop`、`browser_error`、`screenshot_dir`。 控制顺序：L638按`screenshot_dir is not None`分支；L703按`selection["database"] == "postgresql"`分支；L827遍历`business["roles"]`；L843按`business["registration"]["enabled"]`分支；L867在`pending`成立时循环；L869遍历`list(pending)`；L875按`any(r["target_entity"] not in base for r in relations)`分支；L899按`workflow`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path(product).resolve`、`Path`、`Path(screenshot_dir).absolute`、`check`、`target.is_symlink`、`hasattr`、`target.is_junction`、`target.resolve().is_relative_to`、`target.resolve`等。 返回路径：L1707的`{ "passed": True, "http": True, "restart": True, "database": "real-isolated-" + selection[…`。

</details>

**创建路径：** `templates/product/verify_business.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L678。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`29684`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/verify_business.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "d98e1f664f09bf8314416e6e4807f1d8c3ea9df3c107209ef3603e752cf490c1"} -->
````python
# templates/product/verify_business.py
"""Independent HTTP/browser business verification against a new owned database."""

import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify_query_matrix(spec, actors, rows, samples, create_roles, request, allowed):
    """Exact query expectations come from owned API writes, never query responses."""
    business = spec["business"]
    grants = {(p["role"], p["entity"]): p for p in business["permissions"]}
    resources = {r["entity"]: r for r in business["resources"]}
    workflows = {w["entity"]: w for w in business["workflows"]}
    relations = {(r["entity"], r["field"]): r for r in business["relations"]}
    cases, evidence = [], []

    def wire(value):
        return str(value).lower() if type(value) is bool else str(value)

    def keyword(value):
        text = str(value or "")
        # A proper substring distinguishes keyword search from full-value
        # equality. One-character domains have no shorter nonempty query.
        term = text[1:-1] if len(text) > 2 else text[:1]
        return term[:200].upper()

    for definition in spec["entities"]:
        entity, fields = definition["name"], definition["fields"]
        searchable = [f for f in fields if f["searchable"]]
        filterable = [f for f in fields if f["filterable"]]
        if not searchable and not filterable:
            continue
        workflow = workflows.get(entity)
        protected = {resources[entity].get("assignee_field")}
        if workflow:
            protected.add(workflow["status_field"])
            protected.update(t.get("set_timestamp") for t in workflow["transitions"])
        due_fields = {
            n["due_field"]
            for n in business["notifications"]
            if n["entity"] == entity and n["event"] == "due"
        }
        controls = {}
        for role, actor in actors.items():
            if not allowed(role, entity, "read"):
                continue
            scope = grants[role, entity]["scope"]
            if scope == "own" and not allowed(role, entity, "create"):
                # An approved own/read-only role can legitimately have no owned
                # records. Do not manufacture extra create or ownership rights.
                continue
            creator = actor if scope == "own" else actors[create_roles[entity]]
            for side in (0, 1):
                sample = dict(samples[entity])
                for field_index, field in enumerate(fields):
                    name, kind = field["name"], field["kind"]
                    if name in protected or (entity, name) in relations:
                        continue
                    if name in due_fields:
                        sample[name] = f"2099-01-0{side + 1}T00:00:00Z"
                    elif field["searchable"] or field["filterable"]:
                        if kind == "text":
                            marker = (
                                "q"
                                + str(side)
                                + hashlib.sha256(f"{entity}/{name}".encode()).hexdigest()[:8]
                            )
                            if field["max_length"] < len(marker):
                                # Truncating the same q0 prefix would correlate
                                # short fields and lose independent field proof.
                                marker = chr(0x4E00 + field_index * 2 + side)
                            sample[name] = marker.ljust(max(1, field.get("min_length", 0)), "z")[
                                : field["max_length"]
                            ]
                        elif kind == "enum":
                            sample[name] = field["choices"][min(side, len(field["choices"]) - 1)]
                        elif kind == "integer":
                            sample[name] = 41 + side
                        elif kind == "boolean":
                            sample[name] = bool(side)
                        elif kind == "date":
                            sample[name] = f"2026-02-0{side + 1}"
                        elif kind == "datetime":
                            sample[name] = f"2026-02-0{side + 1}T00:00:00Z"
                row = request("POST", "/api/" + entity, creator, status=201, json=sample)
                rows[entity].append(row)
                if scope == "assigned":
                    assigner = next(
                        (
                            a
                            for a in actors.values()
                            if allowed(a["role"], entity, "assign", row, a["id"])
                        ),
                        None,
                    )
                    check(assigner is not None, "Query controls need an approved assignment actor")
                    row.update(
                        request(
                            "POST",
                            f"/api/{entity}/{row['id']}/assign",
                            assigner,
                            json={"user_id": actor["id"]},
                        )
                    )
                if (
                    side
                    and workflow
                    and any(f["name"] == workflow["status_field"] for f in searchable + filterable)
                ):
                    transition = next(
                        (
                            t
                            for t in workflow["transitions"]
                            if row[workflow["status_field"]] in t["from_states"]
                        ),
                        None,
                    )
                    if transition:
                        handler = next(
                            (
                                a
                                for a in actors.values()
                                if a["role"] in transition["roles"]
                                and allowed(a["role"], entity, "transition", row, a["id"])
                            ),
                            None,
                        )
                        if handler:
                            row.update(
                                request(
                                    "POST",
                                    f"/api/{entity}/{row['id']}/transition",
                                    handler,
                                    json={"transition": transition["name"]},
                                )
                            )
                controls[role, side] = row
        check(len(rows[entity]) <= 100, "Query control rows exceed explicit 100-record bound")

        def matches(row, params):
            q = params.get("q", "").strip().casefold()
            if q and not any(q in str(row.get(f["name"]) or "").casefold() for f in searchable):
                return False
            return all(
                wire(row.get(f["name"])) == value
                for key, value in params.items()
                if key.startswith("filter_")
                for f in filterable
                if key == "filter_" + f["name"]
            )

        first = next(iter(controls.values()), rows[entity][0])
        other = next((row for (role, side), row in controls.items() if side), first)
        for role, actor in actors.items():
            if not allowed(role, entity, "read"):
                continue
            scope = grants[role, entity]["scope"]
            visible = [r for r in rows[entity] if allowed(role, entity, "read", r, actor["id"])]
            positive = controls.get((role, 0), first)
            alternate = controls.get((role, 1), other)
            matrix = [(f, "keyword", None) for f in searchable] + [
                (f, "exact_filter", None) for f in filterable
            ]
            matrix += (
                [(f, "combined", searchable[0]["name"]) for f in filterable] if searchable else []
            )
            for field, kind, keyword_field in matrix:
                name = field["name"]
                if kind == "keyword":
                    term = keyword(positive.get(name))
                    check(bool(term), f"Query keyword control is empty: {entity}.{name}")
                    pair = [
                        ("match", {"q": term}),
                        (
                            "miss",
                            {
                                "q": "qnever"
                                + hashlib.sha256(f"{entity}/{name}".encode()).hexdigest()[:12]
                            },
                        ),
                    ]
                else:
                    value, alternative = positive.get(name), alternate.get(name)
                    if value == alternative:
                        if field["kind"] == "enum":
                            alternative = next((v for v in field["choices"] if v != value), value)
                        elif field["kind"] == "text":
                            alternative = "query-value-not-present"
                        elif field["kind"] == "boolean":
                            alternative = not value
                        elif field["kind"] == "integer":
                            alternative = int(value or 0) + 1
                    check(
                        value is not None and alternative is not None,
                        f"Query filter control is empty: {entity}.{name}",
                    )
                    anchor = {"q": keyword(positive.get(keyword_field))} if keyword_field else {}
                    pair = [
                        ("match", {**anchor, "filter_" + name: wire(value)}),
                        ("other", {**anchor, "filter_" + name: wire(alternative)}),
                    ]
                counts, excluded, foreign, isolated = [], 0, 0, 0
                for variant, params in pair:
                    expected = {r["id"] for r in visible if matches(r, params)}
                    all_matches = {r["id"] for r in rows[entity] if matches(r, params)}
                    isolated_count = (
                        sum(
                            r["id"] in expected
                            and params["q"].casefold() in str(r.get(name) or "").casefold()
                            and not any(
                                params["q"].casefold() in str(r.get(f["name"]) or "").casefold()
                                for f in searchable
                                if f["name"] != name
                            )
                            for r in visible
                        )
                        if kind == "keyword" and variant == "match"
                        else 0
                    )
                    actual = request(
                        "GET", "/api/" + entity, actor, params={**params, "limit": 100}
                    )
                    check(
                        isinstance(actual, list)
                        and {r["id"] for r in actual} == expected
                        and len(actual) == len(expected),
                        f"Query matrix differs for {role}/{entity}/{name}/{kind}/{variant}",
                    )
                    cases.append(
                        {
                            "role": role,
                            "entity": entity,
                            "field": name,
                            "kind": kind,
                            "variant": variant,
                            "keyword_field": keyword_field,
                            "params": params,
                            "expected_ids": sorted(expected),
                            "total_count": len(visible),
                            "foreign_count": len(all_matches - expected),
                            "isolated_count": isolated_count,
                        }
                    )
                    counts.append(len(expected))
                    excluded += len(visible) - len(expected)
                    foreign += len(all_matches - expected)
                    isolated += isolated_count
                evidence.append(
                    {
                        "role": role,
                        "entity": entity,
                        "field": name,
                        "kind": kind,
                        "keyword_field": keyword_field,
                        "scope": scope,
                        "cases": 2,
                        "positive_matches": counts[0],
                        "other_matches": counts[1],
                        "excluded_records": excluded,
                        "foreign_matches": foreign,
                        "isolated_matches": isolated,
                        "exact_results": True,
                        "role_scope": True,
                    }
                )
        for field in searchable:
            check(
                any(
                    p["entity"] == entity
                    and p["field"] == field["name"]
                    and p["kind"] == "keyword"
                    and p["isolated_matches"] > 0
                    for p in evidence
                ),
                f"Keyword field lacks an isolated positive control: {entity}.{field['name']}",
            )
        for field in filterable:
            check(
                any(
                    p["entity"] == entity
                    and p["field"] == field["name"]
                    and p["kind"] == "exact_filter"
                    and p["positive_matches"] > 0
                    for p in evidence
                ),
                f"Filter lacks a positive control: {entity}.{field['name']}",
            )
    return cases, evidence


def verify_field_constraints(client, actor, entity, fields, sample, row, protected, can_update):
    """Reject concrete invalid requests through the generated server, not metadata alone."""
    headers = {"Authorization": "Bearer " + actor["token"]}
    route = "/api/" + entity
    before = client.get(route, headers=headers, params={"limit": 100}).json()
    evidence = []
    for field in fields:
        name, kind = field["name"], field["kind"]
        proof = {"entity": entity, "field": name, "kind": kind, "required": field["required"]}
        if name in protected:
            response = client.post(route, headers=headers, json={**sample, name: "forged"})
            check(response.status_code == 422, f"Protected create field accepted: {entity}.{name}")
            proof["protected_create_rejected"] = True
            if can_update:
                response = client.put(
                    route + "/" + row["id"], headers=headers, json={name: "forged"}
                )
                check(
                    response.status_code == 422, f"Protected update field accepted: {entity}.{name}"
                )
                proof["protected_update_rejected"] = True
            evidence.append(proof)
            continue
        invalid = []
        if field["required"]:
            missing = {key: value for key, value in sample.items() if key != name}
            response = client.post(route, headers=headers, json=missing)
            check(response.status_code == 422, f"Missing required field accepted: {entity}.{name}")
            proof["missing_required_rejected"] = True
            invalid.append(("null_rejected", None))
            if kind in {"text", "enum"}:
                invalid.append(("blank_rejected", ""))
        if kind == "text":
            invalid.append(("over_max_length_rejected", "x" * (field["max_length"] + 1)))
            proof["max_length"] = field["max_length"]
            if field.get("min_length", 0) > 0:
                invalid.append(("under_min_length_rejected", "x" * (field["min_length"] - 1)))
                proof["min_length"] = field["min_length"]
        if kind == "enum":
            invalid_choice = next(
                char * max(1, field.get("min_length", 0))
                for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                if char * max(1, field.get("min_length", 0)) not in field["choices"]
            )
            invalid.append(("invalid_enum_rejected", invalid_choice))
            proof["declared_choices"] = len(field["choices"])
        if kind == "datetime":
            invalid.append(("invalid_timestamp_rejected", "not-a-timestamp"))
        for check_name, value in invalid:
            response = client.post(route, headers=headers, json={**sample, name: value})
            check(response.status_code == 422, f"{check_name} failed for {entity}.{name}")
            proof[check_name] = True
            if can_update:
                response = client.put(route + "/" + row["id"], headers=headers, json={name: value})
                check(
                    response.status_code == 422, f"Update {check_name} failed for {entity}.{name}"
                )
        if invalid and can_update:
            proof["invalid_updates_rejected"] = len(invalid)
        evidence.append(proof)
    after = client.get(route, headers=headers, params={"limit": 100}).json()
    check(before == after, "Rejected field input changed stored records")
    return evidence


def verify_audit_immutability(client, actor, entity, row, actor_ids):
    headers = {"Authorization": "Bearer " + actor["token"]}
    route = f"/api/{entity}/{row['id']}/history"
    response = client.get(route, headers=headers)
    check(response.status_code == 200, "Audit history unavailable")
    original = response.json()
    check(bool(original), "Audit history is empty")
    for entry in original:
        check(
            {"before", "after"} <= entry.keys()
            and all(
                entry[key] is None or isinstance(entry[key], dict) for key in ("before", "after")
            ),
            "Audit snapshots unavailable",
        )
        check(
            entry.get("id") and entry.get("action") and entry.get("actor_id") in actor_ids,
            "Audit action/actor missing",
        )
        check(bool(entry.get("created_at")), "Audit timestamp missing")
        check(
            datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00")).tzinfo is not None,
            "Audit timestamp is not timezone-aware",
        )
    forged = {
        "action": "forged",
        "actor_id": "forged",
        "created_at": "2000-01-01T00:00:00Z",
        "before": {},
        "after": {},
    }
    attempts = 0
    for path in (route, route + "/" + original[0]["id"]):
        for method in ("PUT", "PATCH", "DELETE"):
            denied = client.request(method, path, headers=headers, json=forged)
            check(denied.status_code in {403, 404, 405}, "Audit mutation/deletion route accepted")
            check(
                client.get(route, headers=headers).json() == original,
                "Audit changed after rejected mutation",
            )
            attempts += 1
    return original, {
        "entity": entity,
        "entries_checked": len(original),
        "action_actor_timestamp": True,
        "mutation_delete_attempts_rejected": attempts,
        "surface": "http_history_collection_and_entry",
        "unchanged_after_attempts": True,
    }


class NotificationEvidence:
    """Expected reminders come from successful actions and the approved contract."""

    def __init__(self, business):
        self.rules = business["notifications"]
        self.resources = {r["entity"]: r for r in business["resources"]}
        self.workflows = {w["entity"]: w for w in business["workflows"]}
        self.expected = Counter()
        self.covered = set()
        self.due_seen = set()

    def recipient(self, rule, row):
        field = (
            "created_by"
            if rule["recipient"] == "creator"
            else self.resources[rule["entity"]]["assignee_field"]
        )
        return row.get(field)

    def event(self, entity, row, event, transition=None):
        recipients = set()
        for index, rule in enumerate(self.rules):
            if rule["entity"] != entity or rule["event"] != event:
                continue
            if event == "transitioned" and rule["transition"] != transition:
                continue
            recipient = self.recipient(rule, row)
            if recipient:
                self.covered.add(index)
                recipients.add(recipient)
        self.expected.update((recipient, entity, row["id"], event) for recipient in recipients)

    def due(self, rows, actor, allowed):
        now = datetime.now(timezone.utc)
        for index, rule in enumerate(self.rules):
            if rule["event"] != "due":
                continue
            entity, field = rule["entity"], rule["due_field"]
            for row in rows[entity]:
                value = row.get(field)
                if (
                    not value
                    or row.get("archived_at")
                    or self.recipient(rule, row) != actor["id"]
                    or not allowed(actor["role"], entity, "read", row, actor["id"])
                    or datetime.fromisoformat(value.replace("Z", "+00:00")) > now
                ):
                    continue
                workflow = self.workflows.get(entity)
                if workflow and row[workflow["status_field"]] not in {
                    state for t in workflow["transitions"] for state in t["from_states"]
                }:
                    continue
                self.covered.add(index)
                key = (actor["id"], entity, row["id"], field, value)
                if key not in self.due_seen:
                    self.due_seen.add(key)
                    self.expected[actor["id"], entity, row["id"], "due"] += 1

    def inbox(self, actor, notices, event=None):
        check(
            len({n["id"] for n in notices}) == len(notices),
            "Duplicate notification identifiers",
        )
        check(
            all(n["recipient_id"] == actor["id"] for n in notices),
            "Notification recipient leak",
        )
        actual = Counter(
            (n["recipient_id"], n["entity"], n["record_id"], n["event"])
            for n in notices
            if event is None or n["event"] == event
        )
        expected = Counter(
            {
                k: v
                for k, v in self.expected.items()
                if k[0] == actor["id"] and (event is None or k[3] == event)
            }
        )
        check(actual == expected, "Missing, duplicated or unexpected declared notifications")
        check(all(n["created_at"] for n in notices), "Notification timestamp missing")

    def complete(self):
        check(
            self.covered == set(range(len(self.rules))),
            "Declared notification rule was not exercised by the approved workflow",
        )


SCREENSHOT_VIEWS = {"list", "form", "relations", "workflow", "reminders", "dashboard"}
SCREENSHOT_LIMIT = 48
SCREENSHOT_FILE_BYTES = 5 * 1024 * 1024
SCREENSHOT_TOTAL_BYTES = 40 * 1024 * 1024


def validate_png(payload):
    check(payload.startswith(b"\x89PNG\r\n\x1a\n"), "Screenshot must be PNG")
    offset, header, compressed, ended = 8, None, [], False
    safe_chunks = {
        b"IHDR",
        b"PLTE",
        b"IDAT",
        b"IEND",
        b"sRGB",
        b"gAMA",
        b"cHRM",
        b"iCCP",
        b"pHYs",
        b"sBIT",
        b"bKGD",
        b"tRNS",
    }
    while offset < len(payload):
        check(offset + 12 <= len(payload), "Truncated PNG")
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        kind = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        check(end <= len(payload) and kind in safe_chunks, "Invalid PNG chunk")
        data = payload[offset + 8 : offset + 8 + length]
        checksum = struct.unpack(">I", payload[end - 4 : end])[0]
        check(zlib.crc32(kind + data) & 0xFFFFFFFF == checksum, "Invalid PNG checksum")
        if header is None:
            check(kind == b"IHDR" and length == 13, "Invalid PNG header")
            header = struct.unpack(">IIBBBBB", data)
        elif kind == b"IHDR":
            raise ValueError("Duplicate PNG header")
        if kind == b"IDAT":
            compressed.append(data)
        if kind == b"IEND":
            check(length == 0 and end == len(payload), "PNG has trailing data")
            ended = True
        offset = end
    check(header is not None and ended and compressed, "Incomplete PNG")
    width, height, depth, color, compression, filtering, interlace = header
    check(
        0 < width * height <= 16 * 1024 * 1024 and compression == filtering == interlace == 0,
        "Unsupported or excessive PNG dimensions",
    )
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    check(channels is not None and depth in {1, 2, 4, 8, 16}, "Unsupported PNG pixels")
    row_bytes = (width * channels * depth + 7) // 8 + 1
    expected = row_bytes * height
    check(expected <= 64 * 1024 * 1024, "PNG decompression limit exceeded")
    decoder = zlib.decompressobj()
    try:
        pixels = decoder.decompress(b"".join(compressed), expected + 1)
    except zlib.error:
        raise ValueError("Invalid PNG compressed data") from None
    check(
        decoder.eof and not decoder.unused_data and len(pixels) == expected,
        "Invalid PNG image data",
    )
    check(
        all(pixels[index] <= 4 for index in range(0, len(pixels), row_bytes)), "Invalid PNG filter"
    )


def validate_screenshots(directory, entries):
    """Only bounded, named PNGs from the owned synthetic-product directory escape."""
    check(
        isinstance(entries, list) and len(entries) <= SCREENSHOT_LIMIT,
        "Invalid screenshot manifest",
    )
    if directory is None:
        check(not entries, "Screenshots were not requested")
        return []
    check(bool(entries), "Requested screenshots were not captured")
    root = Path(directory).resolve()
    seen, result, total = set(), [], 0
    for entry in entries:
        check(
            isinstance(entry, dict) and set(entry) == {"file", "role", "entity", "view"},
            "Invalid screenshot entry",
        )
        name, role, entity, view = (entry.get(key) for key in ("file", "role", "entity", "view"))
        check(
            isinstance(role, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", role),
            "Invalid screenshot role",
        )
        check(
            entity is None
            or isinstance(entity, str)
            and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", entity),
            "Invalid screenshot entity",
        )
        check(isinstance(view, str) and view in SCREENSHOT_VIEWS, "Invalid screenshot view")
        expected = f"{role}--{entity or 'overview'}--{view}.png"
        check(name == expected and name not in seen, "Invalid or duplicate screenshot filename")
        path = root / name
        check(
            not path.is_symlink() and path.is_file() and path.resolve().parent == root,
            "Screenshot file escaped owned directory",
        )
        size = path.stat().st_size
        check(0 < size <= SCREENSHOT_FILE_BYTES, "Screenshot exceeds file limit")
        total += size
        check(total <= SCREENSHOT_TOTAL_BYTES, "Screenshots exceed total limit")
        payload = path.read_bytes()
        validate_png(payload)
        seen.add(name)
        result.append({**entry, "bytes": size, "sha256": hashlib.sha256(payload).hexdigest()})
    check(
        {path.name for path in root.iterdir()} == seen,
        "Unlisted screenshot artifacts are forbidden",
    )
    return result


def verify_business(product, python, stop, browser_error, screenshot_dir=None):
    product = Path(product).resolve()
    screenshot_target = None
    if screenshot_dir is not None:
        target = Path(screenshot_dir).absolute()
        check(
            not target.is_symlink()
            and not (hasattr(target, "is_junction") and target.is_junction()),
            "Screenshot directory cannot be a link",
        )
        check(
            not target.resolve().is_relative_to(product),
            "Screenshot evidence must be outside immutable product source",
        )
        target.mkdir(parents=True, exist_ok=True, mode=0o700)
        check(not any(target.iterdir()), "Screenshot output directory must be empty")
        screenshot_target = target.resolve()
    spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
    selection = json.loads((product / "selection.json").read_text(encoding="utf-8"))
    business = spec["business"]
    digest = hashlib.sha256(
        json.dumps(spec, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    grants = {(g["role"], g["entity"]): g for g in business["permissions"]}
    resources = {r["entity"]: r for r in business["resources"]}
    workflows = {w["entity"]: w for w in business["workflows"]}
    fields = {e["name"]: e["fields"] for e in spec["entities"]}
    checks = []
    notification_evidence = NotificationEvidence(business)
    persisted_notifications = {}
    persisted_audit = {}
    evidence = {
        "version": 1,
        "field_validation": [],
        "related_views": [],
        "relation_labels": [],
        "datetime_policy": [],
        "due_notifications": [],
        "audit_immutability": [],
        "query_matrix": [],
    }
    related_expectations, relation_labels = [], []
    password = secrets.token_urlsafe(24)

````
