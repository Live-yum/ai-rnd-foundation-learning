"""Enforce explicit entity field inventories before generation, never trim a Plan."""


def entity_gaps(requirement, plan, *, diagnostics=None):
    gaps = []
    entities = {entity.name: entity for entity in plan.entities}
    if not requirement.additional_entities:
        expected_entities = sorted(item.entity for item in requirement.entity_requirements)
        extra_entities = sorted(set(entities) - set(expected_entities))
        if extra_entities:
            gaps.append(f"设计包含封闭实体清单以外的实体：{extra_entities}")
            if diagnostics is not None:
                diagnostics.append(
                    {
                        "code": "entity_set",
                        "source": {"section": "entity_requirements"},
                        "targets": [{"entity": name, "field": None} for name in extra_entities],
                        "attribute": "entities",
                        "expected": expected_entities,
                        "actual": sorted(entities),
                        "source_markers": ["explicit_entity_inventory"],
                    }
                )
    for index, obligation in enumerate(requirement.entity_requirements):
        entity = entities.get(obligation.entity)
        actual = sorted(field.name for field in entity.fields) if entity else []
        expected = sorted(obligation.fields)
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected)) if not obligation.additional_fields else []
        if entity is not None and not missing and not extra:
            continue
        code = "missing_entity" if entity is None else "entity_field_set"
        gaps.append(
            f"实体 {obligation.entity} 的已确认字段清单不一致：缺失 {missing}，额外 {extra}"
        )
        if diagnostics is not None:
            diagnostics.append(
                {
                    "code": code,
                    "source": {"section": "entity_requirements", "index": index},
                    "targets": [
                        {"entity": obligation.entity, "field": name} for name in missing + extra
                    ],
                    "attribute": "fields",
                    "expected": expected,
                    "actual": actual,
                    "missing": missing,
                    "extra": extra,
                    "additional_fields": obligation.additional_fields,
                    "source_markers": ["explicit_field_inventory"],
                }
            )
    return gaps
