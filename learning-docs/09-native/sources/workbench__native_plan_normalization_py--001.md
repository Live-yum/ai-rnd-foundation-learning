# workbench/native_plan_normalization.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `reserved_native_names`（L15–L23）：接收`template`。 控制顺序：L16按`template not in NATIVE_TEMPLATES`分支。 调用`set`。 返回路径：L17的`set()`；L23的`audit_names \| runtime_names`。
- `_replacement`（L26–L34）：接收`entity`、`name`、`occupied`。 控制顺序：L30在`candidate in occupied`成立时循环。 调用`len`。 返回路径：L34的`candidate`。
- `_text_refs`（L37–L57）：接收`text`、`mappings`、`entity`。 源码说明：Rewrite identifier references, never values in examples or enums.。 控制顺序：L40遍历`mappings.items()`；L41遍历`fields.items()`；L43按`entity is not None`分支；L46遍历`{name for fields in mappings.values() for name in fields}`；L48按`len(targets) == 1`分支；L50按`not replacements`分支。 调用`mappings.items`、`fields.items`、`replacements.update`、`mappings.get`、`mappings.values`、`len`、`next`、`iter`、`"\|".join`等。 返回路径：L51的`text`；L57的`re.sub(pattern, lambda match: replacements[match.group()], text)`。
- `_rename`（L60–L92）：接收`data`、`mappings`。 控制顺序：L62遍历`data["entities"]`；L64遍历`entity["fields"]`；L66遍历`data.get("custom_rules", [])`；L68遍历`("accept_examples", "reject_examples")`；L73按`business`分支；L81遍历`references.items()`；L82遍历`business.get(section, [])`；L84遍历`attributes`。后续分支沿下方源码相同行号继续阅读。 调用`deepcopy`、`mappings.get`、`names.get`、`data.get`、`sample.items`、`_text_refs`、`references.items`、`business.get`、`item.get`等。 返回路径：L92的`Plan.model_validate(data)`。
- `source_plan`（L95–L116）：接收`plan`、`normalization`。 源码说明：Project implementation names back to source names for obligation checks.。 控制顺序：L102遍历`normalization.get("field_mappings", [])`；L105按`source not in reserved or target in reserved or target not in fields or source in fie…`分支；L113抛异常，停止当前正常路径。 调用`Plan.model_validate`、`reserved_native_names`、`normalization.get`、`set`、`entities.get`、`mappings.get(entity, {}).values`、`mappings.get`、`ValueError`、`seen.add`等。 返回路径：L116的`_rename(plan.model_dump(), mappings)`。
- `normalize_native_plan`（L119–L173）：接收`plan`、`approved_requirement`、`template`、`prior_normalization`。 源码说明：Return a fresh Plan plus serializable source mapping and safe diagnostics.。 控制顺序：L123按`prior_normalization and prior_normalization.get("field_mappings")`分支；L128遍历`prior_normalization["field_mappings"]`；L130按`entry["target_field"] in names`分支；L131按`entry["source_field"] in names`分支；L132抛异常，停止当前正常路径；L138遍历`plan.entities`；L140遍历`sorted(entity.fields, key=lambda field: field.name)`；L141按`field.name not in reserved`分支。 调用`Plan.model_validate`、`Requirement.model_validate`、`prior_normalization.get`、`fields.get`、`set`、`ValueError`、`retained.append`、`source_plan`、`reserved_native_names`等。 返回路径：L173的`normalized, report`。

</details>

**创建路径：** `workbench/native_plan_normalization.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L173。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7507`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_plan_normalization.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "eeefc28d1022a590a9992a1ed1d97f7e11c56dd9f7d268e720bc86cf263bbb76"} -->
````python
# workbench/native_plan_normalization.py
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
````
