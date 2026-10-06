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
