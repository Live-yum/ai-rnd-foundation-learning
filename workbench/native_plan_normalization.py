"""Deterministic native storage names, separate from immutable approved intent.

Only identifiers change. No field, required constraint, enum value, permission,
example value or business scope is invented to accommodate a test harness.
"""

import re
from copy import deepcopy

from workbench.domain import Plan, Requirement

NATIVE_TEMPLATES = {"fastapiadmin", "yudao-vben"}


def reserved_native_names(template):
    if template not in NATIVE_TEMPLATES:
        return set()
    # Both adapters share downstream code generation guards. Preserve their
    # union even where a particular SQL table uses fewer audit columns.
    from workbench.native_coding import RESERVED as runtime_names
    from workbench.native_modules import RESERVED as audit_names

    return audit_names | runtime_names


def _replacement(entity, name, occupied):
    base = f"{entity}_{name}"[:40]
    candidate = base
    suffix = 2
    while candidate in occupied:
        ending = f"_{suffix}"
        candidate = base[: 40 - len(ending)] + ending
        suffix += 1
    return candidate


def _text_refs(text, mappings, entity=None):
    """Rewrite identifier references, never values in examples or enums."""
    replacements = {}
    for owner, fields in mappings.items():
        for source, target in fields.items():
            replacements[f"{owner}.{source}"] = f"{owner}.{target}"
    if entity is not None:
        replacements.update(mappings.get(entity, {}))
    else:
        for source in {name for fields in mappings.values() for name in fields}:
            targets = {fields[source] for fields in mappings.values() if source in fields}
            if len(targets) == 1:
                replacements[source] = next(iter(targets))
    if not replacements:
        return text
    pattern = (
        r"(?<![a-zA-Z0-9_.])(?:"
        + "|".join(re.escape(key) for key in sorted(replacements, key=len, reverse=True))
        + r")(?![a-zA-Z0-9_])"
    )
    return re.sub(pattern, lambda match: replacements[match.group()], text)


def _rename(data, mappings):
    data = deepcopy(data)
    for entity in data["entities"]:
        names = mappings.get(entity["name"], {})
        for field in entity["fields"]:
            field["name"] = names.get(field["name"], field["name"])
    for rule in data.get("custom_rules", []):
        names = mappings.get(rule["entity"], {})
        for key in ("accept_examples", "reject_examples"):
            rule[key] = [{names.get(k, k): v for k, v in sample.items()} for sample in rule[key]]
        rule["description"] = _text_refs(rule["description"], mappings, rule["entity"])
    data["acceptance"] = [_text_refs(text, mappings) for text in data["acceptance"]]
    business = data.get("business")
    if business:
        references = {
            "resources": ("assignee_field",),
            "relations": ("field",),
            "workflows": ("status_field",),
            "notifications": ("due_field",),
            "metrics": ("group_by", "start_field", "end_field", "time_field"),
        }
        for section, attributes in references.items():
            for item in business.get(section, []):
                names = mappings.get(item["entity"], {})
                for attribute in attributes:
                    if item.get(attribute) in names:
                        item[attribute] = names[item[attribute]]
                for transition in item.get("transitions", []):
                    if transition.get("set_timestamp") in names:
                        transition["set_timestamp"] = names[transition["set_timestamp"]]
                for predicate in item.get("filters", []):
                    predicate["field"] = names.get(predicate["field"], predicate["field"])
    return Plan.model_validate(data)


def source_plan(plan, normalization):
    """Project implementation names back to source names for obligation checks."""
    plan = Plan.model_validate(plan)
    mappings = {}
    reserved = reserved_native_names(normalization.get("template"))
    entities = {entity.name: {field.name for field in entity.fields} for entity in plan.entities}
    seen = set()
    for entry in normalization.get("field_mappings", []):
        entity, source, target = (entry[key] for key in ("entity", "source_field", "target_field"))
        fields = entities.get(entity, set())
        if (
            source not in reserved
            or target in reserved
            or target not in fields
            or source in fields
            or (entity, target) in seen
            or source in mappings.get(entity, {}).values()
        ):
            raise ValueError("原生字段映射无效；请重新生成设计并保留需求字段来源")
        seen.add((entity, target))
        mappings.setdefault(entity, {})[target] = source
    return _rename(plan.model_dump(), mappings)


def normalize_native_plan(plan, approved_requirement, template, *, prior_normalization=None):
    """Return a fresh Plan plus serializable source mapping and safe diagnostics."""
    plan = Plan.model_validate(plan)
    Requirement.model_validate(approved_requirement)  # Never mutate the approved input.
    if prior_normalization and prior_normalization.get("field_mappings"):
        # A new planner response may use source names, implementation names,
        # or omit a field (the coverage gate still detects that omission).
        fields = {entity.name: {field.name for field in entity.fields} for entity in plan.entities}
        retained = []
        for entry in prior_normalization["field_mappings"]:
            names = fields.get(entry["entity"], set())
            if entry["target_field"] in names:
                if entry["source_field"] in names:
                    raise ValueError("原生字段来源映射不唯一；请保留一个业务字段并重新生成设计")
                retained.append(entry)
        plan = source_plan(plan, {**prior_normalization, "field_mappings": retained})
    reserved = reserved_native_names(template)
    mappings = {}
    entries = []
    for entity in plan.entities:
        occupied = {field.name for field in entity.fields} | reserved
        for field in sorted(entity.fields, key=lambda field: field.name):
            if field.name not in reserved:
                continue
            target = _replacement(entity.name, field.name, occupied)
            occupied.add(target)
            mappings.setdefault(entity.name, {})[field.name] = target
            entries.append(
                {
                    "entity": entity.name,
                    "source_field": field.name,
                    "target_field": target,
                    "reason": "native_reserved_identifier",
                }
            )
    normalized = _rename(plan.model_dump(), mappings)
    report = {
        "version": 1,
        "template": template,
        "field_mappings": entries,
        "diagnostics": [
            {
                "code": "native_reserved_identifier",
                "entity": entry["entity"],
                "field": entry["source_field"],
                "implementation_field": entry["target_field"],
                "message": (
                    f"实体 {entry['entity']} 的字段 {entry['source_field']} 与原生框架保留字段冲突；"
                    f"存储名称映射为 {entry['target_field']}，业务含义和已确认约束保持不变。"
                ),
            }
            for entry in entries
        ],
    }
    return normalized, report
