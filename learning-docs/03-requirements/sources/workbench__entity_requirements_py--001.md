# workbench/entity_requirements.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：用户明确封闭的实体与字段清单。** 普通项目默认允许扩展；只有明确封闭的批准清单才禁止额外实体或字段。逐实体比较计划并报告缺失、额外字段与来源编号，不直接修改模型计划。模型遗漏清单不构成撤销批准，修正需可追溯的用户原文。

**对应关系：** Requirement.entity_requirements/additional_entities → coverage_gaps → 设计门与下一轮精准修复反馈。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `entity_gaps`（L4–L53）：接收`requirement`、`plan`、`diagnostics`。 控制顺序：L7按`not requirement.additional_entities`分支；L10按`extra_entities`分支；L12按`diagnostics is not None`分支；L24遍历`enumerate(requirement.entity_requirements)`；L30按`entity is not None and not missing and not extra`分支；L36按`diagnostics is not None`分支。 调用`sorted`、`set`、`gaps.append`、`diagnostics.append`、`enumerate`、`entities.get`。 返回路径：L53的`gaps`。

</details>

**创建路径：** `workbench/entity_requirements.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L53。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2570`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/entity_requirements.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "47adafbcdcf6f286d0ad9c58cd3f94b56f92540b96110f7bd96506cafc5bec46"} -->
````python
# workbench/entity_requirements.py
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
````
