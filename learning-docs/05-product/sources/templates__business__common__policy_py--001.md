# templates/business/common/policy.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：三个模板共享的有限业务策略解释器。** Policy按批准合同查角色、资源、权限与状态转换，校验受控字段并计算登记指标；只处理数据和规则，不持有数据库连接或外部网络权限。

**对应关系：** Plan.business → business_python/fastapiadmin复制策略 → 各自事务运行时；Yudao以审查过的Java实现相同合同。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `validate_scalar_constraints`（L10–L26）：接收`kind`、`field`、`value`。 控制顺序：L11按`kind == "integer"`分支；L12按`not -(2**31) <= value < 2**31`分支；L13抛异常，停止当前正常路径；L14遍历`( ("minimum", lambda limit: value < limit), ("maximum", lambda li…`；L20按`field.get(attribute) is not None and invalid(field[attribute])`分支；L21抛异常，停止当前正常路径；L22按`kind == "text" and field.get("pattern") is not None`分支；L26抛异常，停止当前正常路径。 调用`PolicyError`、`field.get`、`invalid`、`TypeAdapter(Annotated[str, Field(pattern=field["pattern"])]).vali…`、`TypeAdapter`、`Field`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `PolicyError`（L29–L30）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `utc`（L33–L41）：接收`value`。 控制顺序：L39按`parsed.tzinfo is None`分支；L40抛异常，停止当前正常路径。 调用`datetime.now`、`datetime.fromisoformat`、`value.replace`、`PolicyError`、`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds"…`、`parsed.astimezone(timezone.utc).isoformat`、`parsed.astimezone`。 返回路径：L41的`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")`。
- `Policy`（L44–L222）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Policy.__init__`（L45–L57）：接收`spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Policy.resource`（L59–L62）：接收`entity`。 控制顺序：L60按`entity not in self.resources`分支；L61抛异常，停止当前正常路径。 调用`PolicyError`。 返回路径：L62的`self.resources[entity]`。
- `Policy.grant`（L64–L69）：接收`role`、`entity`、`action`。 控制顺序：L67按`grant is None or action not in grant["actions"]`分支；L68抛异常，停止当前正常路径。 调用`self.resource`、`self.permissions.get`、`PolicyError`。 返回路径：L69的`grant`。
- `Policy.visible`（L71–L76）：接收`actor`、`row`、`entity`、`action`。 控制顺序：L73按`grant["scope"] == "all"`分支。 调用`self.grant`、`self.resource`、`str`、`row.get`。 返回路径：L74的`True`；L76的`str(row.get(key)) == str(actor["id"])`。
- `Policy.workflow`（L78–L79）：接收`entity`。 调用`self.workflows.get`。 返回路径：L79的`self.workflows.get(entity)`。
- `Policy.transition`（L81–L93）：接收`role`、`entity`、`name`、`state`。 控制顺序：L87按`transition is None or role not in transition["roles"] or state not in transition["fro…`分支；L92抛异常，停止当前正常路径。 调用`self.grant`、`self.workflow`、`next`、`(workflow or {}).get`、`PolicyError`。 返回路径：L93的`transition`。
- `Policy.protected`（L95–L108）：接收`entity`。 控制顺序：L98按`resource.get("assignee_field")`分支；L101按`workflow`分支。 调用`self.resource`、`resource.get`、`fields.add`、`self.workflow`、`fields.update`、`item.get`。 返回路径：L108的`fields`。
- `Policy.validate_fields`（L110–L144）：接收`entity`、`data`。 控制顺序：L112按`set(data) - set(fields)`分支；L113抛异常，停止当前正常路径；L115遍历`fields.items()`；L117按`value is None`分支；L118按`field["required"]`分支；L119抛异常，停止当前正常路径；L124按`type(value) is not expected`分支；L125抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`set`、`PolicyError`、`fields.items`、`data.get`、`{"integer": int, "boolean": bool}.get`、`type`、`isinstance`、`value.strip`、`max`等。 返回路径：L144的`result`。
- `Policy.metric`（L146–L222）：接收`rows`、`metric`。 控制顺序：L185按`kind == "count"`分支；L187按`kind == "average_duration"`分支；L189遍历`rows`；L191按`start and end`分支；L196按`seconds >= 0`分支；L204按`kind == "group_count"`分支；L213按`kind == "time_count"`分支；L222抛异常，停止当前正常路径。 调用`matches`、`len`、`row.get`、`( datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.f…`、`datetime.fromisoformat`、`end.replace`、`start.replace`、`durations.append`、`sum`等。 返回路径：L186的`{"kind": kind, "value": len(rows)}`；L198的`{ "kind": kind, "value": sum(durations) / len(durations) if durations else None, "samples"…`；L206的`{ "kind": kind, "groups": [ {"key": key, "count": value} for key, value in sorted(groups.i…`。
- `Policy.metric.matches`（L147–L181）：接收`row`。 控制顺序：L148遍历`metric.get("filters", [])`；L162按`predicate["field"] in {"created_at", "updated_at", "archived_at"}`分支；L164按`kind == "datetime"`分支；L173按`op == "eq" and actual != expected or op == "ne" and actual == expected`分支；L175按`op == "in" and actual not in expected`分支；L177按`op in {"gte", "lte"} and ( actual is None or (actual < expected if op == "gte" else a…`分支。 调用`metric.get`、`row.get`、`next`、`utc`。 返回路径：L174的`False`；L176的`False`；L180的`False`。

</details>

**创建路径：** `templates/business/common/policy.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L222。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9119`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/common/policy.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d771f433a9210b01bdf129362e55f90fbaa35e05c709bb75fd3f55ace1a8e18c"} -->
````python
# templates/business/common/policy.py
"""Portable approved-business semantics; no database, network, or platform imports."""

from collections import Counter
from datetime import date, datetime, timezone
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError


def validate_scalar_constraints(kind, field, value):
    if kind == "integer":
        if not -(2**31) <= value < 2**31:
            raise PolicyError("Integer outside supported range")
        for attribute, invalid in (
            ("minimum", lambda limit: value < limit),
            ("maximum", lambda limit: value > limit),
            ("exclusive_minimum", lambda limit: value <= limit),
            ("exclusive_maximum", lambda limit: value >= limit),
        ):
            if field.get(attribute) is not None and invalid(field[attribute]):
                raise PolicyError("Integer violates approved constraint")
    if kind == "text" and field.get("pattern") is not None:
        try:
            TypeAdapter(Annotated[str, Field(pattern=field["pattern"])]).validate_python(value)
        except ValidationError as error:
            raise PolicyError("Text violates approved pattern") from error


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
            validate_scalar_constraints(kind, field, value)
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
