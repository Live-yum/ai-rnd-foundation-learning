# templates/business/common/policy.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：三个模板共享的有限业务策略解释器。** Policy按批准合同查角色、资源、权限与状态转换，校验受控字段并计算登记指标；只处理数据和规则，不持有数据库连接或外部网络权限。

**对应关系：** Plan.business → business_python/fastapiadmin复制策略 → 各自事务运行时；Yudao以审查过的Java实现相同合同。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `PolicyError`（L7–L8）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `utc`（L11–L19）：接收`value`。 控制顺序：L17按`parsed.tzinfo is None`分支；L18抛异常，停止当前正常路径。 调用`datetime.now`、`datetime.fromisoformat`、`value.replace`、`PolicyError`、`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds"…`、`parsed.astimezone(timezone.utc).isoformat`、`parsed.astimezone`。 返回路径：L19的`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")`。
- `Policy`（L22–L201）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Policy.__init__`（L23–L35）：接收`spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Policy.resource`（L37–L40）：接收`entity`。 控制顺序：L38按`entity not in self.resources`分支；L39抛异常，停止当前正常路径。 调用`PolicyError`。 返回路径：L40的`self.resources[entity]`。
- `Policy.grant`（L42–L47）：接收`role`、`entity`、`action`。 控制顺序：L45按`grant is None or action not in grant["actions"]`分支；L46抛异常，停止当前正常路径。 调用`self.resource`、`self.permissions.get`、`PolicyError`。 返回路径：L47的`grant`。
- `Policy.visible`（L49–L54）：接收`actor`、`row`、`entity`、`action`。 控制顺序：L51按`grant["scope"] == "all"`分支。 调用`self.grant`、`self.resource`、`str`、`row.get`。 返回路径：L52的`True`；L54的`str(row.get(key)) == str(actor["id"])`。
- `Policy.workflow`（L56–L57）：接收`entity`。 调用`self.workflows.get`。 返回路径：L57的`self.workflows.get(entity)`。
- `Policy.transition`（L59–L71）：接收`role`、`entity`、`name`、`state`。 控制顺序：L65按`transition is None or role not in transition["roles"] or state not in transition["fro…`分支；L70抛异常，停止当前正常路径。 调用`self.grant`、`self.workflow`、`next`、`(workflow or {}).get`、`PolicyError`。 返回路径：L71的`transition`。
- `Policy.protected`（L73–L86）：接收`entity`。 控制顺序：L76按`resource.get("assignee_field")`分支；L79按`workflow`分支。 调用`self.resource`、`resource.get`、`fields.add`、`self.workflow`、`fields.update`、`item.get`。 返回路径：L86的`fields`。
- `Policy.validate_fields`（L88–L123）：接收`entity`、`data`。 控制顺序：L90按`set(data) - set(fields)`分支；L91抛异常，停止当前正常路径；L93遍历`fields.items()`；L95按`value is None`分支；L96按`field["required"]`分支；L97抛异常，停止当前正常路径；L102按`type(value) is not expected`分支；L103抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`set`、`PolicyError`、`fields.items`、`data.get`、`{"integer": int, "boolean": bool}.get`、`type`、`isinstance`、`value.strip`、`max`等。 返回路径：L123的`result`。
- `Policy.metric`（L125–L201）：接收`rows`、`metric`。 控制顺序：L164按`kind == "count"`分支；L166按`kind == "average_duration"`分支；L168遍历`rows`；L170按`start and end`分支；L175按`seconds >= 0`分支；L183按`kind == "group_count"`分支；L192按`kind == "time_count"`分支；L201抛异常，停止当前正常路径。 调用`matches`、`len`、`row.get`、`( datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.f…`、`datetime.fromisoformat`、`end.replace`、`start.replace`、`durations.append`、`sum`等。 返回路径：L165的`{"kind": kind, "value": len(rows)}`；L177的`{ "kind": kind, "value": sum(durations) / len(durations) if durations else None, "samples"…`；L185的`{ "kind": kind, "groups": [ {"key": key, "count": value} for key, value in sorted(groups.i…`。
- `Policy.metric.matches`（L126–L160）：接收`row`。 控制顺序：L127遍历`metric.get("filters", [])`；L141按`predicate["field"] in {"created_at", "updated_at", "archived_at"}`分支；L143按`kind == "datetime"`分支；L152按`op == "eq" and actual != expected or op == "ne" and actual == expected`分支；L154按`op == "in" and actual not in expected`分支；L156按`op in {"gte", "lte"} and ( actual is None or (actual < expected if op == "gte" else a…`分支。 调用`metric.get`、`row.get`、`next`、`utc`。 返回路径：L153的`False`；L155的`False`；L159的`False`。

</details>

**创建路径：** `templates/business/common/policy.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L201。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8198`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/common/policy.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ba5404d84b49cea256ab5cf493433959fc2bfe330246b85565558c144e13454c"} -->
````python
# templates/business/common/policy.py
"""Portable approved-business semantics; no database, network, or platform imports."""

from collections import Counter
from datetime import date, datetime, timezone


class PolicyError(ValueError):
    pass


def utc(value=None):
    parsed = (
        datetime.now(timezone.utc)
        if value is None
        else datetime.fromisoformat(value.replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        raise PolicyError("Timestamp requires timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class Policy:
    def __init__(self, spec):
        self.spec = spec
        self.business = spec["business"]
        self.entities = {item["name"]: item for item in spec["entities"]}
        self.resources = {item["entity"]: item for item in self.business["resources"]}
        self.roles = {item["name"] for item in self.business["roles"]}
        self.permissions = {
            (item["role"], item["entity"]): item for item in self.business["permissions"]
        }
        self.workflows = {item["entity"]: item for item in self.business["workflows"]}
        self.relations = {
            (item["entity"], item["field"]): item for item in self.business["relations"]
        }

    def resource(self, entity):
        if entity not in self.resources:
            raise PolicyError("Unknown resource")
        return self.resources[entity]

    def grant(self, role, entity, action):
        self.resource(entity)
        grant = self.permissions.get((role, entity))
        if grant is None or action not in grant["actions"]:
            raise PolicyError("Action is not permitted")
        return grant

    def visible(self, actor, row, entity, action="read"):
        grant = self.grant(actor["role"], entity, action)
        if grant["scope"] == "all":
            return True
        key = "created_by" if grant["scope"] == "own" else self.resource(entity)["assignee_field"]
        return str(row.get(key)) == str(actor["id"])

    def workflow(self, entity):
        return self.workflows.get(entity)

    def transition(self, role, entity, name, state):
        self.grant(role, entity, "transition")
        workflow = self.workflow(entity)
        transition = next(
            (item for item in (workflow or {}).get("transitions", []) if item["name"] == name), None
        )
        if (
            transition is None
            or role not in transition["roles"]
            or state not in transition["from_states"]
        ):
            raise PolicyError("Transition is not allowed from current state")
        return transition

    def protected(self, entity):
        fields = {"id", "owner_id", "created_by", "created_at", "updated_at", "archived_at"}
        resource = self.resource(entity)
        if resource.get("assignee_field"):
            fields.add(resource["assignee_field"])
        workflow = self.workflow(entity)
        if workflow:
            fields.add(workflow["status_field"])
            fields.update(
                item["set_timestamp"]
                for item in workflow["transitions"]
                if item.get("set_timestamp")
            )
        return fields

    def validate_fields(self, entity, data):
        fields = {item["name"]: item for item in self.entities[entity]["fields"]}
        if set(data) - set(fields):
            raise PolicyError("Unknown or immutable input field")
        result = {}
        for name, field in fields.items():
            value = data.get(name)
            if value is None:
                if field["required"]:
                    raise PolicyError("Missing required field: " + name)
                result[name] = None
                continue
            kind = "text" if (entity, name) in self.relations else field["kind"]
            expected = {"integer": int, "boolean": bool}.get(kind, str)
            if type(value) is not expected:
                raise PolicyError("Invalid field type: " + name)
            if isinstance(value, str):
                value = value.strip()
            if (
                kind in {"text", "enum"}
                and not max(1 if field["required"] else 0, field.get("min_length", 0))
                <= len(value)
                <= field["max_length"]
            ):
                raise PolicyError("Invalid field length: " + name)
            if kind == "enum" and value not in field["choices"]:
                raise PolicyError("Invalid enum value: " + name)
            if kind == "integer" and not -(2**63) <= value < 2**63:
                raise PolicyError("Integer outside supported range")
            if kind == "date":
                if date.fromisoformat(value).isoformat() != value:
                    raise PolicyError("Date must use YYYY-MM-DD")
            if kind == "datetime":
                value = utc(value)
            result[name] = value
        return result

    def metric(self, rows, metric):
        def matches(row):
            for predicate in metric.get("filters", []):
                actual, expected, op = (
                    row.get(predicate["field"]),
                    predicate["value"],
                    predicate["op"],
                )
                kind = next(
                    (
                        item["kind"]
                        for item in self.entities[metric["entity"]]["fields"]
                        if item["name"] == predicate["field"]
                    ),
                    None,
                )
                if predicate["field"] in {"created_at", "updated_at", "archived_at"}:
                    kind = "datetime"
                if kind == "datetime":
                    actual = utc(actual) if actual is not None else None
                    expected = (
                        [utc(value) if value is not None else None for value in expected]
                        if op == "in"
                        else utc(expected)
                        if expected is not None
                        else None
                    )
                if op == "eq" and actual != expected or op == "ne" and actual == expected:
                    return False
                if op == "in" and actual not in expected:
                    return False
                if op in {"gte", "lte"} and (
                    actual is None or (actual < expected if op == "gte" else actual > expected)
                ):
                    return False
            return True

        rows = [row for row in rows if matches(row)]
        kind = metric["kind"]
        if kind == "count":
            return {"kind": kind, "value": len(rows)}
        if kind == "average_duration":
            durations = []
            for row in rows:
                start, end = row.get(metric["start_field"]), row.get(metric["end_field"])
                if start and end:
                    seconds = (
                        datetime.fromisoformat(end.replace("Z", "+00:00"))
                        - datetime.fromisoformat(start.replace("Z", "+00:00"))
                    ).total_seconds()
                    if seconds >= 0:
                        durations.append(seconds)
            return {
                "kind": kind,
                "value": sum(durations) / len(durations) if durations else None,
                "samples": len(durations),
                "unit": "seconds",
            }
        if kind == "group_count":
            groups = Counter(row.get(metric["group_by"]) for row in rows)
            return {
                "kind": kind,
                "groups": [
                    {"key": key, "count": value}
                    for key, value in sorted(groups.items(), key=lambda item: str(item[0]))
                ],
            }
        if kind == "time_count":
            groups = Counter(
                utc(row[metric["time_field"]])[:10] for row in rows if row.get(metric["time_field"])
            )
            return {
                "kind": kind,
                "groups": [{"day": key, "count": value} for key, value in sorted(groups.items())],
                "timezone": "UTC",
            }
        raise PolicyError("Unknown metric kind")
````
